# Copied from the site's code by `manage.py export_authoring`. Do not edit here.
"""One course as one zip file: how course files travel between the site and an educator.

    <course>.zip
      <course>/course.yaml
      <course>/content/**

Two directions use the same shape. An educator downloads the files of their course from
the site and unpacks them into their copy of the educator kit; when they have written
something, the kit packs the course again and they hand that file in.

A zip that comes back was made on someone else's computer, so nothing in it is trusted:
`inspect` refuses anything that is not plainly a course (a path that climbs out of its
folder, a link, a kind of file the site does not use, something too large), and
`protected_changes` says whether the parts of course.yaml that are not the educator's to
change were changed. Raw material (`source/`) is never packed and never accepted.

A hand-in may only add: new files, and new lines anywhere in the files that are there.
`compare` is that rule. Every line a file has now must still be in it, in the same order;
whatever fails that is listed, line by line. The same test answers a second question: has
the course moved on since this person took their copy? Then their copy lacks lines the
course now has, which looks exactly like a removal, and is refused the same way.

Nothing here imports Django: the kit runs this very file (see export_authoring).
"""

import difflib
import hashlib
import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

# What a course is made of. Anything else in a content folder is left behind.
SUFFIXES = {".md", ".yaml", ".yml", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
# Of those, the ones that are text and are compared line by line. An image either is the
# same image or it is not.
TEXT = {".md", ".yaml", ".yml"}
MAX_FILES = 2000
MAX_FILE = 10 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024

# course.yaml fields that belong to the person who runs the site.
PROTECTED = [
    "title",
    "code",
    "year",
    "series",
    "semester",
    "status",
    "enabled",
    "has_educator",
    "hue",
    "order",
]
# An SVG is a document that can carry a script. One that does is refused.
SVG_ACTIVE = re.compile(rb"<script|javascript:|\son\w+\s*=|<foreignObject", re.IGNORECASE)


class HandInError(ValueError):
    """The zip is not something that can be taken in. The message says why."""


def course_files(folder):
    """The files of one course that travel: course.yaml and what the site reads under
    content/. Yields (path, name inside the course folder)."""
    folder = Path(folder)
    yield folder / "course.yaml", "course.yaml"
    content = folder / "content"
    if not content.is_dir():
        return
    for path in sorted(content.rglob("*")):
        relative = path.relative_to(folder)
        hidden = any(part.startswith((".", "_")) for part in relative.parts)
        if path.is_file() and not hidden and path.suffix.lower() in SUFFIXES:
            yield path, relative.as_posix()


def pack(folder):
    """The course in `folder` as the bytes of a zip file."""
    folder = Path(folder)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, name in course_files(folder):
            # A fixed date: the same files give the same zip, whoever packs them and when.
            info = zipfile.ZipInfo(f"{folder.name}/{name}", date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue()


def inspect(archive, max_total=MAX_TOTAL):
    """Check an open ZipFile. Returns (course slug, {name inside the course: ZipInfo}).

    Raises HandInError for anything that is not plainly one course.
    """
    members, slugs, total = {}, set(), 0
    for info in archive.infolist():
        name = info.filename
        if info.is_dir():
            continue
        path = PurePosixPath(name)
        if "\\" in name or path.is_absolute() or ".." in path.parts or ":" in name:
            raise HandInError(f"`{name}` is not a path inside a course folder")
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise HandInError(f"`{name}` is a link, not a file")
        if len(path.parts) < 2:
            raise HandInError(f"`{name}` is outside the course folder")
        slugs.add(path.parts[0])
        inner = PurePosixPath(*path.parts[1:])
        if inner.as_posix() != "course.yaml":
            if inner.parts[0] != "content" or len(inner.parts) < 2:
                raise HandInError(
                    f"`{name}` is neither course.yaml nor under content/ "
                    "(raw material under source/ is never handed in)"
                )
            if path.suffix.lower() not in SUFFIXES:
                raise HandInError(f"`{name}` is not a kind of file a course is made of")
        if info.file_size > MAX_FILE:
            raise HandInError(f"`{name}` is larger than {MAX_FILE // 1024 // 1024} MB")
        total += info.file_size
        members[inner.as_posix()] = info
    if len(slugs) != 1:
        raise HandInError("the zip must hold exactly one course folder")
    if "course.yaml" not in members:
        raise HandInError("the zip has no course.yaml")
    if len(members) > MAX_FILES or total > max_total:
        raise HandInError("the zip is too large to be one course")
    return slugs.pop(), members


def read(archive, info):
    """One file out of the zip, never more of it than it claimed to hold."""
    with archive.open(info) as handle:
        data = handle.read(MAX_FILE + 1)
    if len(data) > MAX_FILE:
        raise HandInError(f"`{info.filename}` is larger than it says")
    if info.filename.lower().endswith(".svg") and SVG_ACTIVE.search(data):
        raise HandInError(f"`{info.filename}` is an image that carries a script")
    return data


def protected_changes(before, after):
    """What a handed-in course.yaml changed that is not the educator's to change.

    Both arguments are the text of a course.yaml. Returns a list of sentences; empty
    means only topics and the description differ, which is allowed.
    """
    try:
        old, new = yaml.safe_load(before) or {}, yaml.safe_load(after) or {}
    except yaml.YAMLError as error:
        return [f"course.yaml cannot be read: {error}"]
    if not isinstance(old, dict) or not isinstance(new, dict):
        return ["course.yaml must be `key: value` pairs"]
    changes = [
        f"`{field}` was {old.get(field)!r} and is now {new.get(field)!r}"
        for field in PROTECTED
        if old.get(field) != new.get(field)
    ]

    def ids(data):
        topics = data.get("topics") or []
        return [t.get("id") for t in topics if isinstance(t, dict)]

    gone = [topic for topic in ids(old) if topic not in ids(new)]
    if gone:
        changes.append("topics removed or renamed: " + ", ".join(map(str, gone)))
    return changes


def unzip(source, max_total=MAX_TOTAL):
    """Open a zip (a path, a file, or bytes) and read the course in it.

    Returns (course slug, {name inside the course: bytes}); raises HandInError.
    """
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    try:
        with zipfile.ZipFile(source) as archive:
            slug, members = inspect(archive, max_total)
            return slug, {name: read(archive, info) for name, info in members.items()}
    except zipfile.BadZipFile as error:
        raise HandInError("this is not a zip file") from error


def content_version(folder):
    """A fingerprint of the travelling files of the course in `folder`: the same for the
    same files wherever they sit, and different as soon as a byte of one changes."""
    digest = hashlib.sha256()
    for path, name in course_files(folder):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def files_of(folder):
    """The travelling files of the course in `folder`: {name inside the course: bytes}."""
    return {name: path.read_bytes() for path, name in course_files(folder)}


def _lines(data):
    """A text file as the lines that count: without line endings, trailing spaces and
    blank lines at the end, so that a file saved on Windows equals the one saved on a Mac."""
    lines = [line.rstrip() for line in data.decode("utf-8").splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _kept(old, new):
    """Whether every line of `old` is still in `new`, in the same order."""
    rest = iter(new)
    return all(line in rest for line in old)


def _lost(old, new, limit=6):
    """The lines of `old` that are gone from `new` or were rewritten: (line number, text)."""
    gone = []
    for tag, start, end, _, _ in difflib.SequenceMatcher(
        None, old, new, autojunk=False
    ).get_opcodes():
        if tag in ("delete", "replace"):
            gone += [(number + 1, old[number]) for number in range(start, end) if old[number]]
    return gone[:limit], len(gone)


@dataclass
class Change:
    """What one version of a course adds to another, and what it would take away."""

    added: list = field(default_factory=list)  # names of new files
    grown: dict = field(default_factory=dict)  # name -> number of lines added
    problems: list = field(default_factory=list)  # sentences; empty means it only adds

    @property
    def ok(self):
        return not self.problems

    @property
    def lines(self):
        return sum(self.grown.values())

    def __str__(self):
        files = f"{len(self.added)} new file{'s' * (len(self.added) != 1)}"
        return f"{files}, {self.lines} line{'s' * (self.lines != 1)} added to existing files"


def compare(old, new):
    """What `new` adds to `old`, both {name: bytes}, under the rule that nothing may go.

    course.yaml is left to `protected_changes`: its description may be reworded.
    """
    change = Change(added=sorted(set(new) - set(old)))
    for name in sorted(old):
        if name == "course.yaml":
            if name in new and old[name] != new[name]:
                grew = len(_text(new[name]) or []) - len(_text(old[name]) or [])
                change.grown[name] = max(0, grew)
            continue
        if name not in new:
            change.problems.append(f"{name}: the file is missing")
        elif PurePosixPath(name).suffix.lower() not in TEXT:
            if old[name] != new[name]:
                change.problems.append(f"{name}: the image was replaced by another")
        else:
            before, after = _text(old[name]), _text(new[name])
            if before is None or after is None:
                change.problems.append(f"{name}: the file is not UTF-8 text")
            elif _kept(before, after):
                if len(after) > len(before):
                    change.grown[name] = len(after) - len(before)
            else:
                shown, count = _lost(before, after)
                more = f" (and {count - len(shown)} more)" if count > len(shown) else ""
                change.problems.append(
                    f"{name}: {count} line{'s' * (count != 1)} removed or rewritten{more}"
                )
                change.problems += [f"    line {number}: {text[:110]}" for number, text in shown]
    return change


def _text(data):
    try:
        return _lines(data)
    except UnicodeDecodeError:
        return None


def extends(old, new, name):
    """Whether `new` keeps everything of `old` (the bytes of one file called `name`):
    for text every line in order, for an image the very same bytes."""
    if PurePosixPath(name).suffix.lower() not in TEXT:
        return old == new
    before, after = _text(old), _text(new)
    return before is not None and after is not None and _kept(before, after)


def topic_ids(course_yaml):
    """The topic ids in the text of a course.yaml; [] if it cannot be read."""
    try:
        data = yaml.safe_load(course_yaml) or {}
    except yaml.YAMLError:
        return []
    topics = data.get("topics") if isinstance(data, dict) else None
    return [topic.get("id") for topic in topics or [] if isinstance(topic, dict)]


def holds(course, snapshot):
    """Whether `course` already has everything in `snapshot` (both {name: bytes}): every
    file, every line, every topic. That is when a hand-in has become part of the files it
    was handed in to."""
    without_yaml = {name: data for name, data in snapshot.items() if name != "course.yaml"}
    if not compare(without_yaml, course).ok or "course.yaml" not in course:
        return False

    def ids(data):
        return set(topic_ids(data.decode("utf-8", errors="replace")))

    return ids(snapshot.get("course.yaml", b"")) <= ids(course["course.yaml"])
