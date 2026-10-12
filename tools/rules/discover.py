# Copied from the site's code by `manage.py export_authoring`. Do not edit here.
"""Find courses on disk, and sort one course's files by what they are.

A file's meaning comes only from where it sits, so authors never declare a type:

    <course>/course.yaml
    <course>/content/lectures|labs|homework|guides/<name>.md
    <course>/content/decks/<deck>.yaml
    <course>/content/problems/<set>.yaml
    <course>/content/exams/<assessment>/assessment.yaml  +  <paper>.yaml
    <course>/content/reference/formulas.yaml | glossary.yaml | cheatsheet.md
    <course>/content/memory/hooks.yaml  |  memory/palaces/<palace>.yaml

A course folder sits directly in the courses folder, or one level down inside a folder that
only groups courses (`semester-5/rl/`). Grouping is for the people who keep the files: a
course's address is its own folder's name wherever it sits, and the site never sees the
group.
"""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .schemas import SLUG_PATTERN

# Bump when rendering changes in a way that should re-import unchanged files.
PIPELINE_VERSION = "3"

SLUG = re.compile(SLUG_PATTERN)
YAML_SUFFIXES = {".yaml", ".yml"}
DOCUMENT_DIRS = {"lectures": "lecture", "labs": "lab", "homework": "homework", "guides": "guide"}
SOURCE_DIRS = ["lectures", "labs", "homework", "exams", "misc"]


@dataclass
class AssessmentFiles:
    assessment: Path | None = None
    papers: list[Path] = field(default_factory=list)


@dataclass
class CourseFiles:
    root: Path
    slug: str
    course: Path
    documents: dict[str, list[Path]] = field(default_factory=dict)  # kind -> files
    decks: list[Path] = field(default_factory=list)
    problem_sets: list[Path] = field(default_factory=list)
    assessments: dict[str, AssessmentFiles] = field(default_factory=dict)
    formulas: Path | None = None
    glossary: Path | None = None
    cheatsheet: Path | None = None
    hooks: Path | None = None
    palaces: list[Path] = field(default_factory=list)

    @property
    def content(self):
        return self.root / "content"

    def rel(self, path):
        return Path(path).relative_to(self.root).as_posix()


def _folders(directory):
    return sorted(
        child
        for child in directory.iterdir()
        if child.is_dir() and not child.name.startswith(("_", "."))
    )


def course_folders(root):
    """Every course folder in one root: directly in it, or inside a grouping folder.

    A folder with a course.yaml is a course. Any other folder is looked into once, for
    courses grouped under it; that is as deep as the search goes.
    """
    root = Path(root)
    if not root.is_dir():
        return
    for child in _folders(root):
        if (child / "course.yaml").is_file():
            yield child
        else:
            for inner in _folders(child):
                if (inner / "course.yaml").is_file():
                    yield inner


def find_courses(roots):
    """Course folders under the given roots, by slug. The first root to define a slug wins."""
    found = {}
    for root in roots:
        for folder in course_folders(root):
            found.setdefault(folder.name, folder)
    return found


def clashes(roots):
    """Slugs that two folders of the same root claim, with those folders.

    A course is addressed by its folder's name, so `semester-4/cda` and `semester-5/cda`
    would be one course in two places. (The same slug in two different roots is not a
    clash: the first root wins, which is how the example course steps aside.)
    """
    found = {}
    for root in roots:
        seen = {}
        for folder in course_folders(root):
            seen.setdefault(folder.name, []).append(folder)
        found.update({slug: folders for slug, folders in seen.items() if len(folders) > 1})
    return found


def find_course(slug, roots):
    return find_courses(roots).get(slug)


def _ignored(path):
    return path.name.startswith(("_", ".")) or path.name.lower() == "readme.md"


def _files(directory, suffixes):
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir() if p.is_file() and p.suffix in suffixes and not _ignored(p)
    )


def discover(course_dir, report):
    course_dir = Path(course_dir)
    files = CourseFiles(root=course_dir, slug=course_dir.name, course=course_dir / "course.yaml")
    if not SLUG.match(files.slug):
        report.error(
            "course.yaml",
            f"the folder name `{files.slug}` cannot be used as a course address",
            hint="rename the folder using lowercase letters, digits and hyphens",
        )
    content = files.content
    if not content.is_dir():
        return files

    known = set()

    def take(paths):
        known.update(paths)
        for path in paths:
            if not SLUG.match(path.stem):
                report.error(
                    files.rel(path),
                    f"the file name `{path.stem}` cannot be used as an address",
                    hint="rename it using lowercase letters, digits and hyphens, e.g. 05-fisher",
                )
        return list(paths)

    for directory, kind in DOCUMENT_DIRS.items():
        files.documents[kind] = take(_files(content / directory, {".md"}))
    files.decks = take(_files(content / "decks", YAML_SUFFIXES))
    files.problem_sets = take(_files(content / "problems", YAML_SUFFIXES))
    files.palaces = take(_files(content / "memory" / "palaces", YAML_SUFFIXES))

    exams = content / "exams"
    if exams.is_dir():
        for folder in sorted(p for p in exams.iterdir() if p.is_dir() and not _ignored(p)):
            if folder.name == "assets":
                continue
            entry = AssessmentFiles()
            for path in _files(folder, YAML_SUFFIXES):
                if path.stem == "assessment":
                    entry.assessment = path
                    known.add(path)
                else:
                    entry.papers += take([path])
            if not SLUG.match(folder.name):
                report.error(
                    files.rel(folder),
                    f"the folder name `{folder.name}` cannot be used as an address",
                    hint="rename it using lowercase letters, digits and hyphens, e.g. midterm",
                )
            if entry.assessment is None:
                report.error(
                    files.rel(folder),
                    "this exam folder has no assessment.yaml",
                    hint="every folder under content/exams/ needs an assessment.yaml",
                )
            files.assessments[folder.name] = entry

    def single(directory, stem, suffixes):
        for path in _files(content / directory, suffixes):
            if path.stem == stem:
                known.add(path)
                return path
        return None

    files.formulas = single("reference", "formulas", YAML_SUFFIXES)
    files.glossary = single("reference", "glossary", YAML_SUFFIXES)
    files.cheatsheet = single("reference", "cheatsheet", {".md"})
    files.hooks = single("memory", "hooks", YAML_SUFFIXES)

    for path in sorted(content.rglob("*")):
        if not path.is_file() or path in known or _ignored(path):
            continue
        if "assets" in path.relative_to(content).parts[:-1]:
            continue  # images referenced from Markdown
        report.warn(
            files.rel(path),
            "this file is not in a place the site reads, so it is ignored",
            hint="see docs/AUTHORING.md for the folder layout",
        )
    return files


def content_hash(course_dir):
    """Fingerprint of everything that affects what the site shows for this course."""
    course_dir = Path(course_dir)
    digest = hashlib.sha256(PIPELINE_VERSION.encode())
    paths = [course_dir / "course.yaml"]
    content = course_dir / "content"
    if content.is_dir():
        paths += sorted(p for p in content.rglob("*") if p.is_file())
    for path in paths:
        if path.is_file():
            digest.update(path.relative_to(course_dir).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def newest_mtime(course_dir):
    course_dir = Path(course_dir)
    paths = [course_dir / "course.yaml"]
    content = course_dir / "content"
    if content.is_dir():
        paths += [p for p in content.rglob("*") if p.is_file()]
    return max((p.stat().st_mtime for p in paths if p.is_file()), default=0)
