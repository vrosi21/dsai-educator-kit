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

Nothing here imports Django: the kit runs this very file (see export_authoring).
"""

import io
import re
import zipfile
from pathlib import Path, PurePosixPath

import yaml

# What a course is made of. Anything else in a content folder is left behind.
SUFFIXES = {".md", ".yaml", ".yml", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
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


def inspect(archive):
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
    if len(members) > MAX_FILES or total > MAX_TOTAL:
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
