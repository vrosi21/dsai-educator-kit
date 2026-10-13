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

`compare` says what one version of a course does to another: which files are new, which
are gone, how many lines each file gained, and which lines it lost or had rewritten, with
the ids that disappear. A hand-in may do all of that; what it removes is shown to the
person first, who has to say that it is meant (desk/handins.py).

`version_of` is a fingerprint of a course's files. It is how the site knows whether a
hand-in was built on the version it has, or on an older one.

Nothing here imports Django: the kit runs this very file (see export_authoring).
"""

import difflib
import hashlib
import io
import json
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

# A note the site may put into a zip it gives out, beside the course's own files: which
# hand-in this is and what it was built on. Never part of the course.
NOTE = ".handin.json"
# In a YAML file, the line that gives an item its id.
ID_LINE = re.compile(r"^\s*(?:-\s+)?id:\s*[\"']?([A-Za-z0-9][A-Za-z0-9_.-]*)")

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


def pack(folder, note=None):
    """The course in `folder` as the bytes of a zip file. `note` (a dict) is added as a
    small file of its own beside the course's."""
    folder = Path(folder)
    return pack_files(folder.name, files_of(folder), note)


def pack_files(slug, files, note=None):
    """The same from files already in memory: {name inside the course: bytes}."""
    buffer = io.BytesIO()
    entries = dict(files)
    if note is not None:
        entries[NOTE] = json.dumps(note, indent=2).encode()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries):
            # A fixed date: the same files give the same zip, whoever packs them and when.
            info = zipfile.ZipInfo(f"{slug}/{name}", date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, entries[name])
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
        if inner.as_posix() not in ("course.yaml", NOTE):
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


def check(files, max_total=MAX_TOTAL):
    """The rules of `inspect` and `read` for a course that is already in memory
    ({name inside the course: bytes}), as an editor on the site makes one: only
    course.yaml and files under content/, only the kinds of file a course is made of,
    nothing hidden, nothing oversized, no image that carries a script."""
    if "course.yaml" not in files:
        raise HandInError("the course has no course.yaml")
    total = 0
    for name, data in files.items():
        path = PurePosixPath(name)
        plain = name == path.as_posix() and not path.is_absolute()
        if not plain or "\\" in name or ":" in name or ".." in path.parts:
            raise HandInError(f"`{name}` is not a path inside a course folder")
        if name != "course.yaml":
            if path.parts[0] != "content" or len(path.parts) < 2:
                raise HandInError(f"`{name}` is neither course.yaml nor under content/")
            if path.suffix.lower() not in SUFFIXES:
                raise HandInError(f"`{name}` is not a kind of file a course is made of")
            if any(part.startswith((".", "_")) for part in path.parts):
                raise HandInError(f"`{name}` is hidden: the site would never read it")
        if len(data) > MAX_FILE:
            raise HandInError(f"`{name}` is larger than {MAX_FILE // 1024 // 1024} MB")
        if name.lower().endswith(".svg") and SVG_ACTIVE.search(data):
            raise HandInError(f"`{name}` is an image that carries a script")
        total += len(data)
    if len(files) > MAX_FILES or total > max_total:
        raise HandInError("this is too large to be one course")


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

    Returns (course slug, {name inside the course: bytes}); raises HandInError. A note
    from the site, if the zip carries one, is left out: see `unzip_with_note`.
    """
    slug, files, _note = unzip_with_note(source, max_total)
    return slug, files


def unzip_with_note(source, max_total=MAX_TOTAL):
    """The same, and the note as a dict ({} when there is none or it cannot be read)."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    try:
        with zipfile.ZipFile(source) as archive:
            slug, members = inspect(archive, max_total)
            files = {name: read(archive, info) for name, info in members.items()}
    except zipfile.BadZipFile as error:
        raise HandInError("this is not a zip file") from error
    try:
        note = json.loads(files.pop(NOTE, b"{}"))
    except ValueError:
        note = {}
    return slug, files, note if isinstance(note, dict) else {}


def version_of(files):
    """A fingerprint of a course's files ({name: bytes}): the same for the same files
    wherever they are, and different as soon as a byte of one changes."""
    digest = hashlib.sha256()
    for name in sorted(files):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(files[name])
        digest.update(b"\0")
    return digest.hexdigest()


def content_version(folder):
    """The fingerprint of the course in `folder`."""
    return version_of(files_of(folder))


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


def _differences(old, new):
    """How `new` differs from `old`, both lists of lines: the lines of `old` that are
    gone or rewritten as (line number, text), and how many lines `new` gained."""
    gone, gained = [], 0
    for tag, a, b, c, d in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag in ("delete", "replace"):
            gone += [(number + 1, old[number]) for number in range(a, b)]
        if tag in ("insert", "replace"):
            gained += d - c
    return gone, gained


def _ids(files):
    """The ids given in the YAML content files of a course ({name: bytes})."""
    found = set()
    for name, data in files.items():
        if name != "course.yaml" and PurePosixPath(name).suffix.lower() in (".yaml", ".yml"):
            for line in _text(data) or []:
                match = ID_LINE.match(line)
                if match:
                    found.add(match.group(1))
    return found


@dataclass
class Change:
    """What one version of a course does to another."""

    added: list = field(default_factory=list)  # names of new files
    removed: list = field(default_factory=list)  # names of files that are gone
    swapped: list = field(default_factory=list)  # images replaced by another
    grown: dict = field(default_factory=dict)  # name -> lines added
    shrunk: dict = field(default_factory=dict)  # name -> lines removed or rewritten
    ids: list = field(default_factory=list)  # ids that disappear from the course
    lost: list = field(default_factory=list)  # what goes, as sentences for showing

    @property
    def only_adds(self):
        return not (self.removed or self.swapped or self.shrunk)

    @property
    def empty(self):
        return self.only_adds and not (self.added or self.grown)

    @property
    def lines_added(self):
        return sum(self.grown.values())

    @property
    def lines_removed(self):
        return sum(self.shrunk.values())

    def __str__(self):
        return summary(len(self.added), self.lines_added, self.lines_removed, len(self.removed))


def summary(new_files, lines_added, lines_removed=0, files_removed=0):
    """One line saying what a hand-in did, e.g. "1 new file, 12 lines added"."""

    def count(number, one, many=None):
        return f"{number} {one if number == 1 else many or one + 's'}"

    parts = []
    if new_files:
        parts.append(count(new_files, "new file"))
    if lines_added:
        parts.append(f"{count(lines_added, 'line')} added")
    if lines_removed:
        parts.append(f"{count(lines_removed, 'line')} removed or rewritten")
    if files_removed:
        parts.append(f"{count(files_removed, 'file')} removed")
    return ", ".join(parts) or "course.yaml changed"


def compare(old, new, shown=6):
    """What `new` does to `old`, both {name: bytes}.

    Nothing is forbidden here. `Change.only_adds` says whether everything that was
    there is still there (every file, and every line of every text file in the same
    order); if not, `Change.lost` lists what goes. course.yaml is left to
    `protected_changes`: only its growth is counted.
    """
    change = Change(added=sorted(set(new) - set(old)))
    for name in sorted(old):
        is_text = PurePosixPath(name).suffix.lower() in TEXT
        if name == "course.yaml":
            if name in new and old[name] != new[name]:
                grew = len(_text(new[name]) or []) - len(_text(old[name]) or [])
                change.grown[name] = max(0, grew)
        elif name not in new:
            change.removed.append(name)
            change.lost.append(f"{name}: the whole file")
        elif not is_text:
            if old[name] != new[name]:
                change.swapped.append(name)
                change.lost.append(f"{name}: the image, replaced by another")
        elif old[name] != new[name]:
            before, after = _text(old[name]), _text(new[name])
            if before is None or after is None:
                change.shrunk[name] = len(before or [])
                change.lost.append(f"{name}: the file is no longer UTF-8 text")
            elif _kept(before, after):
                if len(after) > len(before):
                    change.grown[name] = len(after) - len(before)
            else:
                gone, gained = _differences(before, after)
                change.shrunk[name] = len(gone)
                if gained:
                    change.grown[name] = gained
                count = len(gone)
                more = f" (and {count - shown} more)" if count > shown else ""
                change.lost.append(
                    f"{name}: {count} line{'s' * (count != 1)} removed or rewritten{more}"
                )
                change.lost += [f"    line {n}: {line[:110]}" for n, line in gone[:shown] if line]
    change.ids = sorted(_ids(old) - _ids(new))
    if change.ids:
        listed = ", ".join(change.ids[:12]) + (" ..." if len(change.ids) > 12 else "")
        change.lost.append(
            f"{len(change.ids)} id{'s' * (len(change.ids) != 1)} disappear, and with them "
            f"what students have marked on them: {listed}"
        )
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


def series_of(course_yaml):
    """The course a course.yaml (bytes) says it is another year of, or ""."""
    try:
        data = yaml.safe_load(course_yaml.decode("utf-8", errors="replace"))
    except yaml.YAMLError:
        return ""
    series = data.get("series") if isinstance(data, dict) else None
    return series if isinstance(series, str) else ""


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
    if not compare(without_yaml, course).only_adds or "course.yaml" not in course:
        return False

    def ids(data):
        return set(topic_ids(data.decode("utf-8", errors="replace")))

    return ids(snapshot.get("course.yaml", b"")) <= ids(course["course.yaml"])
