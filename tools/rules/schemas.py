# Copied from the site's code by `manage.py export_authoring`. Do not edit here.
"""The file contract: the exact shape of every file a content author writes.

These Pydantic models are the single source of truth. `sync_content` validates against them,
and `export_schemas` turns them into docs/schemas/*.json and docs/content-types/fields.md, so
the documentation cannot drift from what the importer accepts. Each field's `description`
and each model's docstring is written for the author and is printed in those docs.

Anything typed `Markdown` is rendered by ingest/markdown.py (maths, callouts, links, code).
Anything typed `Line` is a short plain-text label.
"""

import datetime as dt
import difflib
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be empty")
    return value


# Not stripped: leading lines are kept so reported line numbers match the file.
Markdown = Annotated[str, AfterValidator(_not_blank)]
Line = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Id = Annotated[str, StringConstraints(pattern=SLUG_PATTERN, max_length=64)]

ItemId = Annotated[Id, Field(description="Unique in the whole course, and permanent.")]
TopicRef = Annotated[Id | None, Field(description="`id` of a topic declared in course.yaml.")]
Refs = Annotated[
    list[str],
    Field(description="Links to other content, e.g. `card:fisher-01`, `lecture:05-features`."),
]


class Spec(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


# ---------------------------------------------------------------- course.yaml


class TopicSpec(Spec):
    id: Id = Field(description="Permanent id, e.g. `ch5` or `bayes`.")
    title: Line = Field(description="Full name of the chapter or unit.")
    short: Line | None = Field(None, description="Shorter label for chips; defaults to title.")


class CourseFile(Spec):
    """What the course is, and its list of topics."""

    title: Line = Field(description="Full course name.")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)] = (
        Field(description="Short code shown on the course card, e.g. `MLPR`.")
    )
    year: str = Field("", description='Academic year in quotes, e.g. "2026-27".')
    series: Id | None = Field(
        None,
        description="Only when this folder is another year of a course that already has a "
        "folder: the name of that first folder, e.g. `mlpr`. Folders sharing a `series` are "
        "one course in different years: the dashboard opens the latest, and the course page "
        "offers every year at the top.",
    )
    semester: int | None = Field(
        None,
        ge=1,
        le=12,
        description="Which semester of the programme the course belongs to, e.g. `5`. "
        "The dashboard groups courses by it.",
    )
    status: Literal["active", "archived"] = Field(
        "active",
        description="`archived` is a finished course: it is left out of Next up and of the "
        "landing page, and without a `semester` it folds away at the bottom of the dashboard.",
    )
    enabled: bool = Field(
        True,
        description="`false` keeps the course out of sight until the owner switches it on "
        "(here, or in the admin). For a course nobody has reached yet.",
    )
    has_educator: bool = Field(
        False,
        description="`true` says someone is writing this course. While it has no content its "
        "page then says the content is on its way, instead of asking for an educator.",
    )
    hue: int = Field(250, ge=0, le=359, description="Colour of the course, 0-359 on the hue wheel.")
    order: int = Field(0, ge=0, description="Position among courses of the same semester.")
    description: str = Field("", description="One or two sentences shown under the title.")
    topics: list[TopicSpec] = Field(
        default_factory=list,
        description="Chapters or units, in teaching order. Everything else refers to these.",
    )

    @field_validator("semester", mode="before")
    @classmethod
    def _season_is_not_a_semester(cls, value):
        # Until October 2026 this field held a season. Files written then still say
        # `winter`, `summer` or "", and must keep loading: read them as "not given".
        return None if value in ("", "winter", "summer") else value


# ------------------------------------------- lectures / labs / homework / guides


class DocMeta(Spec):
    """The front matter of a Markdown document. The text follows the closing `---`."""

    title: Line = Field(description="Page title. Do not repeat it as a heading in the text.")
    number: int | None = Field(
        None,
        ge=0,
        le=999,
        description="Lecture/lab/homework number. Defaults to the digits the file name opens with.",
    )
    date: dt.date | None = Field(None, description="When it was held.")
    due: dt.date | None = Field(None, description="Deadline (labs, homework).")
    topics: list[Id] = Field(default_factory=list, description="Topic ids this document covers.")
    summary: str = Field("", description="One or two plain sentences shown in lists.")
    takeaways: list[Markdown] = Field(
        default_factory=list, description="3-6 things to remember; shown above the text."
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Files under source/ this was written from, e.g. `lectures/L05.pdf`.",
    )
    status: Literal["draft", "complete"] = Field(
        "complete", description="`draft` is shown as a label; the page is still visible."
    )


# ----------------------------------------------------------------------- decks


class StepSpec(Spec):
    do: Markdown = Field(description="What you write at this step.")
    why: Markdown | None = Field(None, description="Why that step is allowed.")


class CardSpec(Spec):
    """One flashcard. Its shape decides its kind:
    `q` + `a` is a basic card, `q` + `steps` a derivation, `cloze` a fill-in-the-blanks card."""

    id: ItemId
    q: Markdown | None = Field(None, description="The prompt.")
    a: Markdown | None = Field(None, description="The answer exactly as you would write it.")
    note: Markdown | None = Field(None, description="Commentary: why, context, common traps.")
    hook: Markdown | None = Field(None, description="A mnemonic for this card.")
    steps: list[StepSpec] | None = Field(None, description="Revealed one at a time.")
    cloze: Markdown | None = Field(None, description="A sentence with {{blanks}} to recall.")
    hy: bool = Field(False, description="High-yield: likely to be examined.")
    topic: TopicRef = None

    @property
    def kind(self):
        if self.cloze is not None:
            return "cloze"
        return "steps" if self.steps is not None else "basic"

    @model_validator(mode="after")
    def _shape(self):
        if self.cloze is not None:
            if self.q is not None or self.steps is not None:
                raise ValueError("a cloze card uses `cloze` instead of `q`/`steps`; remove them")
            if "{{" not in self.cloze or "}}" not in self.cloze:
                raise ValueError("`cloze` has no {{blank}}; wrap the words to recall in {{ }}")
        elif self.steps is not None:
            if self.q is None:
                raise ValueError("a card with `steps` needs a `q` (the thing to derive)")
            if len(self.steps) < 2:
                raise ValueError("`steps` needs at least 2 steps; use `a` for a short answer")
        elif self.q is None or self.a is None:
            raise ValueError("a card needs `q` and `a` (or `q` and `steps`, or `cloze`)")
        return self


class DeckFile(Spec):
    """A deck of flashcards. One file is one deck."""

    title: Line = Field(description="Name of the deck.")
    description: str = Field("", description="One sentence shown on the decks page.")
    topic: Annotated[Id | None, Field(description="Topic of every card that sets none.")] = None
    lecture: Id | None = Field(
        None, description="File name (without .md) of the lecture this deck drills."
    )
    cards: list[CardSpec] = Field(min_length=1, description="In the order they should be met.")


# ----------------------------------------------------- questions (sets, papers)


class ChoiceSpec(Spec):
    text: Markdown = Field(description="One answer option.")
    correct: bool = Field(False, description="Set to `true` on the right option(s).")
    why: Markdown | None = Field(None, description="Shown after answering.")


class PartSpec(Spec):
    q: Markdown = Field(description="The sub-question.")
    solution: Markdown | None = Field(None, description="Worked solution of this part.")
    points: float | None = Field(None, ge=0)
    label: Line | None = Field(None, description="Defaults to (a), (b), (c)…")


class QuestionSpec(Spec):
    """One question. `open` questions are worked on paper and need a solution; the other
    types are answered on the page and marked automatically."""

    id: ItemId
    type: Literal["open", "mcq", "multi", "tf"] = Field(
        "open",
        description="`mcq` one right choice, `multi` several, `tf` true/false.",
    )
    title: Line | None = Field(None, description="Short name; defaults to `Question N`.")
    points: float | None = Field(None, ge=0, description="Defaults to the sum of its parts.")
    topic: TopicRef = None
    q: Markdown = Field(description="The question as set.")
    parts: list[PartSpec] | None = Field(None, description="Sub-questions (a), (b)…")
    choices: list[ChoiceSpec] | None = Field(None, description="For `mcq` and `multi`.")
    correct: bool | None = Field(None, description="For `tf`: is the statement true?")
    solution: Markdown | None = Field(None, description="Full worked solution.")
    steps: list[StepSpec] | None = Field(None, description="Solution revealed step by step.")
    answer: Markdown | None = Field(None, description="The final answer on its own.")
    source: Markdown | None = Field(None, description="Where it came from, or how reconstructed.")

    @model_validator(mode="after")
    def _shape(self):
        if self.type in ("mcq", "multi"):
            if not self.choices or len(self.choices) < 2:
                raise ValueError(f"a `{self.type}` question needs at least 2 `choices`")
            right = sum(choice.correct for choice in self.choices)
            if self.type == "mcq" and right != 1:
                raise ValueError(
                    "an `mcq` question needs exactly one choice with `correct: true` "
                    "(use `type: multi` when several are right)"
                )
            if self.type == "multi" and right < 1:
                raise ValueError("a `multi` question needs at least one `correct: true` choice")
            if self.correct is not None:
                raise ValueError("`correct` on the question is for `type: tf`; mark the choice")
        elif self.type == "tf":
            if self.correct is None:
                raise ValueError("a `tf` question needs `correct: true` or `correct: false`")
            if self.choices is not None:
                raise ValueError("a `tf` question has no `choices`")
        else:
            if self.choices is not None or self.correct is not None:
                raise ValueError("`choices` / `correct` need `type: mcq`, `multi` or `tf`")
            parts_solved = bool(self.parts) and all(part.solution for part in self.parts)
            if not (self.solution or self.steps or self.answer or parts_solved):
                raise ValueError(
                    "an open question needs a `solution` (or `steps`, or `answer`, "
                    "or a `solution` on every part)"
                )
        return self


class ProblemSetFile(Spec):
    """A practice set: questions with worked solutions, no clock."""

    title: Line = Field(description="Name of the set.")
    topic: Annotated[Id | None, Field(description="Topic of every question that sets none.")] = None
    instructions: Markdown | None = Field(None, description="Shown above the questions.")
    questions: list[QuestionSpec] = Field(min_length=1)


class MarkingSpec(Spec):
    negative: float = Field(
        0, ge=0, description="Points lost for a wrong mcq/multi/tf answer, e.g. 0.2."
    )


class PaperFile(Spec):
    """A past paper or a mock exam. It belongs to the exam whose folder it is in."""

    title: Line = Field(description="Name of the paper.")
    kind: Literal["past", "mock"] = Field(
        description="`past` opens worked; `mock` opens ready to sit against the clock."
    )
    date: dt.date | None = Field(None, description="When the paper was sat.")
    duration: int | None = Field(None, ge=1, le=600, description="Minutes allowed.")
    marking: MarkingSpec = Field(default_factory=MarkingSpec)
    instructions: Markdown | None = Field(None, description="The rubric printed on the paper.")
    questions: list[QuestionSpec] = Field(min_length=1)


# ----------------------------------------------------------------- assessments


class ScopeSpec(Spec):
    lectures: list[int] = Field(
        default_factory=list,
        description="Lecture numbers covered. Their topics are included automatically.",
    )
    topics: list[Id] = Field(default_factory=list, description="Further topic ids covered.")


class WeightSpec(Spec):
    topic: Id = Field(description="A topic id.")
    weight: int = Field(ge=1, le=5, description="1 = barely examined, 5 = carries the paper.")
    note: Markdown | None = Field(None, description="The evidence, e.g. which question asks it.")


class TaskSpec(Spec):
    tag: Line | None = Field(None, description="Short label: Cards, Practice, Read, Why first…")
    text: Markdown = Field(description="What to do, concretely.")
    links: Refs = Field(default_factory=list)


class PhaseSpec(Spec):
    label: Line = Field(description="`Phase 1`, `Day 2`, `Morning of`…")
    minutes: int | None = Field(None, ge=1, description="Roughly how long it takes.")
    title: Line = Field(description="What this block achieves.")
    why: Markdown | None = Field(None, description="Why it comes at this point.")
    tasks: list[TaskSpec] = Field(default_factory=list)


class PlanSpec(Spec):
    intro: Markdown | None = Field(None, description="One paragraph on how the plan is built.")
    phases: list[PhaseSpec] = Field(default_factory=list, description="In the order to do them.")
    skip: Markdown | None = Field(None, description="What to leave out on purpose, and why.")


class PredictionSpec(Spec):
    q: Markdown = Field(description="A question likely to appear.")
    why: Markdown | None = Field(None, description="The evidence: past papers, emphasis in class.")
    likelihood: Literal["high", "medium", "low"] = "medium"
    refs: Refs = Field(default_factory=list)


class AssessmentFile(Spec):
    """One exam to prepare for. Its page shows every card, problem, formula and hook whose
    topic is in scope, so list only what cannot be derived. Leave `scope` and `includes`
    empty to cover the whole course."""

    title: Line = Field(description="Name of the exam.")
    kind: Literal["midterm", "final", "comprehensive", "quiz", "oral", "project", "other"]
    date: dt.date | None = Field(None, description="Exam day; drives the countdown.")
    scope: ScopeSpec = Field(default_factory=ScopeSpec)
    includes: list[Id] = Field(
        default_factory=list,
        description="Other exams (folder names) whose scope this one also covers.",
    )
    format: Markdown | None = Field(None, description="Duration, structure, aids, marking.")
    weights: list[WeightSpec] = Field(
        default_factory=list, description="How much of the paper each topic carries."
    )
    plan: PlanSpec | None = None
    predictions: list[PredictionSpec] = Field(default_factory=list)


# ------------------------------------------------------------------- reference


class FormulaRowSpec(Spec):
    id: ItemId
    name: Line = Field(description="What you would call it when asked to write it down.")
    formula: Markdown = Field(description="Usually one display equation: `$$ … $$`.")
    note: Markdown | None = Field(None, description="Symbols, conditions, when it applies.")


class FormulaSectionSpec(Spec):
    title: Line = Field(description="Heading of the group.")
    topic: Annotated[
        Id | None,
        Field(description="Topic id. Exams covering it show this section."),
    ] = None
    rows: list[FormulaRowSpec] = Field(min_length=1)


class FormulasFile(Spec):
    """The formula sheet: what you may have to write from memory, grouped."""

    sections: list[FormulaSectionSpec] = Field(min_length=1)


class TermSpec(Spec):
    id: ItemId
    term: Line = Field(description="The word or phrase being defined.")
    definition: Markdown = Field(description="A definition you could write in an exam.")
    topic: TopicRef = None
    see: list[Id] = Field(default_factory=list, description="Ids of related terms.")


class GlossaryFile(Spec):
    """Definitions, one per term. Shown in alphabetical order."""

    terms: list[TermSpec] = Field(min_length=1)


# ---------------------------------------------------------------------- memory


class HookSpec(Spec):
    id: ItemId
    target: Line = Field(alias="for", description="What the hook brings back.")
    kind: Literal["phrase", "acronym", "image", "story", "rhyme", "peg"] = Field(
        "phrase", description="The technique, shown as a label."
    )
    hook: Markdown = Field(description="The mnemonic itself.")
    explain: Markdown | None = Field(None, description="How the hook maps onto the real thing.")
    topic: TopicRef = None
    refs: Refs = Field(default_factory=list)


class HooksFile(Spec):
    """Mnemonics that are not tied to one flashcard. (A `hook` written on a card appears on
    the Memory page as well; do not repeat it here.)"""

    hooks: list[HookSpec] = Field(min_length=1)


class LocusSpec(Spec):
    id: Id = Field(description="Unique within this palace.")
    place: Line = Field(description="The stop on the route, e.g. `Front door`.")
    image: Markdown = Field(description="The vivid scene placed there.")
    means: Markdown = Field(description="What the scene stands for.")
    refs: Refs = Field(default_factory=list)


class PalaceFile(Spec):
    """A memory palace: an ordered list stored along a route the learner knows well."""

    title: Line = Field(description="Name of the palace.")
    topic: TopicRef = None
    encodes: Markdown | None = Field(None, description="What ordered material this stores.")
    intro: Markdown | None = Field(None, description="The route, described once.")
    loci: list[LocusSpec] = Field(min_length=2, description="The stops, in walking order.")


# Name -> model, for export_schemas and the docs.
SCHEMAS = {
    "course": CourseFile,
    "document": DocMeta,
    "deck": DeckFile,
    "problem-set": ProblemSetFile,
    "paper": PaperFile,
    "assessment": AssessmentFile,
    "formulas": FormulasFile,
    "glossary": GlossaryFile,
    "hooks": HooksFile,
    "palace": PalaceFile,
}


def _all_field_names():
    names, pending, seen = set(), [Spec], set()
    while pending:
        model = pending.pop()
        if model in seen:
            continue
        seen.add(model)
        pending.extend(model.__subclasses__())
        for name, info in model.model_fields.items():
            names.add(info.alias or name)
    return sorted(names)


FIELD_NAMES = _all_field_names()

_YAML_TYPE_NAMES = {"bool": "true/false", "int": "number", "float": "number", "date": "date"}


def explain(error, typed=None):
    """Turn one Pydantic error into (message, hint) an author can act on.

    `typed` is the value as it appears in the file, when it differs from what YAML made of it."""
    kind = error["type"]
    location = error["loc"]
    field = next((part for part in reversed(location) if isinstance(part, str)), "")
    given = error.get("input")

    if kind == "missing":
        return f"`{field}` is required", ""
    if kind == "extra_forbidden":
        close = difflib.get_close_matches(field, FIELD_NAMES, n=1, cutoff=0.6)
        hint = f"did you mean `{close[0]}`?" if close else "remove it or check the field name"
        return f"unknown field `{field}`", hint
    if kind == "string_type":
        seen = _YAML_TYPE_NAMES.get(type(given).__name__, type(given).__name__)
        if given is None:
            return f"`{field}` is empty", "give it a value or remove the line"
        shown = typed if typed is not None else given
        return (
            f"`{field}` must be text, but YAML read `{shown}` as a {seen}",
            f'wrap it in quotes: "{shown}"',
        )
    if kind == "string_pattern_mismatch":
        return (
            f"`{given}` is not a valid id or name",
            "use lowercase letters, digits and single hyphens, e.g. fisher-01",
        )
    if kind == "value_error":
        return error["msg"].removeprefix("Value error, "), ""
    if kind == "too_short":
        return f"`{field}` is empty; it needs at least one entry", ""
    return f"`{field}`: {error['msg']}" if field else error["msg"], ""
