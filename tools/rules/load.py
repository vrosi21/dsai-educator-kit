# Copied from the site's code by `manage.py export_authoring`. Do not edit here.
"""Read every file of one course and validate it against the contract in schemas.py."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from . import schemas
from .yamlio import Loaded, dotted, load_yaml, split_front_matter


@dataclass
class Parsed:
    """One file that passed validation."""

    path: Path
    rel: str  # path relative to the course folder, for messages
    slug: str  # file name without extension
    spec: Any  # the validated Pydantic model
    loaded: Loaded  # line numbers of every field
    body: str = ""  # Markdown after the front matter
    body_line: int = 1


@dataclass
class Bundle:
    files: Any
    course: Parsed
    documents: dict[str, dict[str, Parsed]] = field(default_factory=dict)  # kind -> slug -> file
    decks: dict[str, Parsed] = field(default_factory=dict)
    problem_sets: dict[str, Parsed] = field(default_factory=dict)
    assessments: dict[str, Parsed] = field(default_factory=dict)
    papers: dict[tuple[str, str], Parsed] = field(default_factory=dict)  # (exam, paper) -> file
    formulas: Parsed | None = None
    glossary: Parsed | None = None
    hooks: Parsed | None = None
    cheatsheet: Parsed | None = None
    palaces: dict[str, Parsed] = field(default_factory=dict)


def _read(path, rel, report):
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        report.error(rel, "the file is not UTF-8 text", hint="re-save it with UTF-8 encoding")
    except OSError as exc:
        report.error(rel, f"cannot read the file: {exc}")
    return None


def _validate(model, loaded, rel, report):
    if not isinstance(loaded.data, dict):
        report.error(
            rel,
            "the file is empty" if loaded.data is None else "the file must be `key: value` pairs",
            hint=f"see docs/content-types/ for the fields of a {model.__name__}",
        )
        return None
    try:
        return model.model_validate(loaded.data)
    except ValidationError as exc:
        for error in exc.errors():
            path = tuple(p for p in error["loc"] if isinstance(p, (str, int)))
            message, hint = schemas.explain(error, typed=loaded.raw.get(path))
            report.error(rel, message, line=loaded.line(path), where=dotted(path), hint=hint)
        return None


def load_yaml_file(path, model, files, report):
    rel = files.rel(path)
    text = _read(path, rel, report)
    if text is None:
        return None
    loaded = load_yaml(text, file=rel, report=report)
    if loaded is None:
        return None
    spec = _validate(model, loaded, rel, report)
    if spec is None:
        return None
    return Parsed(path=path, rel=rel, slug=path.stem, spec=spec, loaded=loaded)


def load_markdown_file(path, files, report):
    rel = files.rel(path)
    text = _read(path, rel, report)
    if text is None:
        return None
    front, body, body_line = split_front_matter(text)
    if front is None:
        report.error(
            rel,
            "the file must start with front matter",
            line=1,
            hint="begin with a line `---`, then `title: …`, then a closing `---`",
        )
        return None
    loaded = load_yaml(front, file=rel, report=report, line_offset=1)
    if loaded is None:
        return None
    spec = _validate(schemas.DocMeta, loaded, rel, report)
    if spec is None:
        return None
    return Parsed(
        path=path, rel=rel, slug=path.stem, spec=spec, loaded=loaded, body=body, body_line=body_line
    )


def load_bundle(files, report):
    """Parse all files. Problems go to `report`; files that fail are simply left out, so one
    run lists every error in the course rather than stopping at the first."""
    course = load_yaml_file(files.course, schemas.CourseFile, files, report)
    if course is None:
        return None
    bundle = Bundle(files=files, course=course)

    def many(paths, model):
        loaded = (load_yaml_file(path, model, files, report) for path in paths)
        return {item.slug: item for item in loaded if item is not None}

    for kind, paths in files.documents.items():
        docs = (load_markdown_file(path, files, report) for path in paths)
        bundle.documents[kind] = {doc.slug: doc for doc in docs if doc is not None}
    bundle.decks = many(files.decks, schemas.DeckFile)
    bundle.problem_sets = many(files.problem_sets, schemas.ProblemSetFile)
    bundle.palaces = many(files.palaces, schemas.PalaceFile)

    for slug, entry in files.assessments.items():
        if entry.assessment is not None:
            parsed = load_yaml_file(entry.assessment, schemas.AssessmentFile, files, report)
            if parsed is not None:
                parsed.slug = slug
                bundle.assessments[slug] = parsed
        for path in entry.papers:
            parsed = load_yaml_file(path, schemas.PaperFile, files, report)
            if parsed is not None:
                bundle.papers[(slug, parsed.slug)] = parsed

    if files.formulas:
        bundle.formulas = load_yaml_file(files.formulas, schemas.FormulasFile, files, report)
    if files.glossary:
        bundle.glossary = load_yaml_file(files.glossary, schemas.GlossaryFile, files, report)
    if files.hooks:
        bundle.hooks = load_yaml_file(files.hooks, schemas.HooksFile, files, report)
    if files.cheatsheet:
        bundle.cheatsheet = load_markdown_file(files.cheatsheet, files, report)
    return bundle
