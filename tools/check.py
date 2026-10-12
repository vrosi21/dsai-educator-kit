# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "pydantic>=2.7"]
# ///
"""Check course files before handing them in.

    uv run tools/check.py rl            one course (the folder courses/rl)
    uv run tools/check.py               every course in courses/
    uv run tools/check.py --status rl   what it contains, and what is left to write

Without uv: `pip install pyyaml pydantic`, then `python tools/check.py ...`.

This runs the first half of the site's own importer, and it is the very same code: the
folder `tools/rules/` is copied from the application. It checks

- that every file sits where the site looks for it and has a usable name,
- that every YAML file and every front matter parses, with the house rules (no tabs, no
  duplicate keys, no backslash inside double quotes),
- every field of every file against the format: unknown fields, missing fields, wrong
  types, values that are not allowed,
- that every id is used once in the course and every `topic` exists in course.yaml.

It does not check the things that need the whole site: links between files
(`lecture:03-search`), the Markdown of the text itself, and whether the maths typesets.
Those are checked when the content is loaded into the site, which the person who runs
it does before anything goes live. A course that passes here can still come back with a
problem of that kind.

Every problem is printed as `file:line  field`, a message, and usually a `->` line saying
how to fix it. The exit status is 1 when any course has an error.
"""

import argparse
import difflib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# Where course folders are kept in the kit. Git ignores everything in it.
COURSES = ROOT / "courses"
sys.path.insert(0, str(HERE))

from rules.discover import clashes, course_folders, discover  # noqa: E402
from rules.load import load_bundle  # noqa: E402
from rules.report import Report  # noqa: E402
from rules.yamlio import dotted  # noqa: E402

VALID = "structure is valid (links between files and maths are checked by the site)"


def cross_check(bundle, report):
    """Ids are used once in the course; topics exist. The same rules as the site's importer."""
    topics = [topic.id for topic in bundle.course.spec.topics]
    claimed = {}

    def error(parsed, path, message, hint=""):
        line = parsed.loaded.line(path)
        report.error(parsed.rel, message, line=line, where=dotted(path), hint=hint)

    def claim(item_id, parsed, path):
        here = f"{parsed.rel}:{parsed.loaded.line(path)}"
        if item_id in claimed:
            error(
                parsed,
                path,
                f"id `{item_id}` is already used at {claimed[item_id]}",
                "every id must be unique in the course; give the newer item a new id",
            )
        else:
            claimed[item_id] = here

    def missing(parsed, path, what, name, known, fallback=""):
        # Worded as the importer words it, with the same "did you mean".
        close = difflib.get_close_matches(name, [str(k) for k in known], n=3, cutoff=0.5)
        hint = "did you mean " + ", ".join(f"`{c}`" for c in close) + "?" if close else fallback
        error(parsed, path, f"no {what} named `{name}` in this course", hint)

    def topic(parsed, path, value):
        if value and value not in topics:
            missing(parsed, path, "topic", value, topics, "topics are declared in course.yaml")

    seen = set()
    for i, one in enumerate(bundle.course.spec.topics):
        if one.id in seen:
            error(bundle.course, ("topics", i, "id"), f"topic `{one.id}` appears twice")
        seen.add(one.id)

    for docs in bundle.documents.values():
        for doc in docs.values():
            for i, value in enumerate(doc.spec.topics):
                topic(doc, ("topics", i), value)

    for slug, deck in bundle.decks.items():
        if slug == "review":
            report.error(
                deck.rel,
                "a deck cannot be called `review`: that address is the all-cards page",
                hint="rename the file",
            )
        topic(deck, ("topic",), deck.spec.topic)
        lectures = bundle.documents.get("lecture", {})
        if deck.spec.lecture and deck.spec.lecture not in lectures:
            missing(deck, ("lecture",), "lecture", deck.spec.lecture, lectures)
        for i, card in enumerate(deck.spec.cards):
            claim(card.id, deck, ("cards", i, "id"))
            topic(deck, ("cards", i, "topic"), card.topic)
            if card.hook:
                claim(f"{card.id}-hook", deck, ("cards", i, "hook"))

    def questions(parsed):
        for i, question in enumerate(parsed.spec.questions):
            claim(question.id, parsed, ("questions", i, "id"))
            topic(parsed, ("questions", i, "topic"), question.topic)

    for problem_set in bundle.problem_sets.values():
        topic(problem_set, ("topic",), problem_set.spec.topic)
        questions(problem_set)
    for paper in bundle.papers.values():
        questions(paper)
    for assessment in bundle.assessments.values():
        for i, value in enumerate(assessment.spec.scope.topics):
            topic(assessment, ("scope", "topics", i), value)
        for i, weight in enumerate(assessment.spec.weights):
            topic(assessment, ("weights", i, "topic"), weight.topic)

    if bundle.formulas:
        for s, section in enumerate(bundle.formulas.spec.sections):
            topic(bundle.formulas, ("sections", s, "topic"), section.topic)
            for r, row in enumerate(section.rows):
                claim(row.id, bundle.formulas, ("sections", s, "rows", r, "id"))
    if bundle.glossary:
        terms = bundle.glossary.spec.terms
        for i, term in enumerate(terms):
            claim(term.id, bundle.glossary, ("terms", i, "id"))
            topic(bundle.glossary, ("terms", i, "topic"), term.topic)
        known = {term.id for term in terms}
        for i, term in enumerate(terms):
            for j, other in enumerate(term.see):
                if other not in known:
                    missing(bundle.glossary, ("terms", i, "see", j), "glossary term", other, known)
    if bundle.hooks:
        for i, hook in enumerate(bundle.hooks.spec.hooks):
            claim(hook.id, bundle.hooks, ("hooks", i, "id"))
            topic(bundle.hooks, ("hooks", i, "topic"), hook.topic)
    for palace in bundle.palaces.values():
        topic(palace, ("topic",), palace.spec.topic)
        local = set()
        for i, locus in enumerate(palace.spec.loci):
            if locus.id in local:
                error(palace, ("loci", i, "id"), f"stop `{locus.id}` appears twice in this palace")
            local.add(locus.id)


def counts(bundle):
    documents = {kind: len(docs) for kind, docs in bundle.documents.items()}
    questions = sum(len(p.spec.questions) for p in bundle.problem_sets.values())
    questions += sum(len(p.spec.questions) for p in bundle.papers.values())
    cards = [card for deck in bundle.decks.values() for card in deck.spec.cards]
    # A hook written on a card is a hook too, as on the site.
    hooks = len(bundle.hooks.spec.hooks) if bundle.hooks else 0
    hooks += sum(1 for card in cards if card.hook)
    return {
        "lectures": documents.get("lecture", 0),
        "labs": documents.get("lab", 0),
        "homework": documents.get("homework", 0),
        "guides": documents.get("guide", 0),
        "decks": len(bundle.decks),
        "cards": len(cards),
        "problem sets": len(bundle.problem_sets),
        "exams": len(bundle.assessments),
        "papers": len(bundle.papers),
        "questions": questions,
        "formulas": sum(len(s.rows) for s in bundle.formulas.spec.sections)
        if bundle.formulas
        else 0,
        "terms": len(bundle.glossary.spec.terms) if bundle.glossary else 0,
        "hooks": hooks,
        "palaces": len(bundle.palaces),
    }


def check(folder):
    """Run the checks on one course folder. Returns (report, bundle or None)."""
    report = Report(course=folder.name)
    files = discover(folder, report)
    bundle = load_bundle(files, report)
    if bundle is not None:
        cross_check(bundle, report)
        report.counts = counts(bundle)
    report.status = VALID if report.ok else "FAILED"
    return report, bundle


def find(name):
    """The course folder meant by `name`: a course's name (`rl`) or a path to its folder."""
    wanted = Path(name).name
    for folder in course_folders(COURSES):
        if folder.name == wanted:
            return folder
    return None


def status(folder, bundle):
    """What is left to write: files under source/ that no document names in `sources:`."""
    source = folder / "source"
    if not source.is_dir():
        return ["  no source/ folder here: put the lecture slides, labs and papers in one"]
    files = sorted(
        path.relative_to(source).as_posix()
        for path in source.rglob("*")
        if path.is_file() and not path.name.startswith(".") and path.name.lower() != "readme.md"
    )
    if not files:
        return ["  source/ is empty: add lecture slides, labs, homework there"]
    covered = set()
    if bundle is not None:
        for docs in bundle.documents.values():
            for doc in docs.values():
                covered.update(doc.spec.sources)
    pending = [name for name in files if name not in covered]
    lines = [f"  source files: {len(files)}, referenced by content: {len(files) - len(pending)}"]
    if pending:
        lines.append(f"  not written up yet ({len(pending)}):")
        lines += [f"    {name}" for name in pending]
    return lines


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # never let a stray character abort the report
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Check course files before handing them in.")
    parser.add_argument("courses", nargs="*", help="Course folders (default: every course).")
    parser.add_argument("--status", action="store_true", help="Also list what is left to write.")
    options = parser.parse_args(argv)

    folders = []
    for name in options.courses:
        folder = find(name)
        if folder is None:
            print(f"{name}: there is no course folder courses/{name} with a course.yaml")
            print("  -> download your course's files from the site (Educators page) and")
            print("     unpack them into courses/")
            return 1
        folders.append(folder)
    folders = folders or list(course_folders(COURSES))

    failed = 0
    for slug, twice in clashes([COURSES]).items():
        places = " and ".join(folder.relative_to(ROOT).as_posix() for folder in twice)
        print(f"{slug}: FAILED\n  ERROR   two folders are named `{slug}`: {places}")
        print("          -> a course's address is its folder's name, so it must be unique")
        failed += 1
    for folder in folders:
        report, bundle = check(folder)
        print(report.format())
        if options.status:
            print("\n".join(status(folder, bundle)))
        failed += not report.ok
    if not folders:
        print("No course in courses/ yet. Download your course's files from the site")
        print("(Educators page) and unpack them there.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
