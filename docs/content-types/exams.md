# Exams

Each exam to prepare for gets a folder under `content/exams/` holding an `assessment.yaml`
and, optionally, papers:

```
content/exams/
  midterm/
    assessment.yaml        the exam: scope, format, plan, predictions
    past-2025.yaml         a past paper   (see questions.md)
    mock-1.yaml            a mock exam    (see questions.md)
  final/
    assessment.yaml
  comprehensive/
    assessment.yaml
```

The folder name is the exam's address (`exam:midterm`). Fields:
[fields.md#assessment](fields.md#assessment). Examples:
[midterm](../example-course/example/content/exams/midterm/assessment.yaml) (everything),
[final](../example-course/example/content/exams/final/assessment.yaml) (the minimum),
[comprehensive](../example-course/example/content/exams/comprehensive/assessment.yaml)
(built from the other two).

## The idea: write the scope, get the rest

An exam's page gathers, by itself, every flashcard, practice set, formula section, glossary
term and hook whose **topic** is in the exam's scope. It offers "drill the weak cards in
scope" and shows how much of the scope is solid. None of that is written by hand.

So the first job is the scope, and it only works if cards, questions and formula sections
carry the right topics.

```yaml
title: Midterm
kind: midterm            # midterm | final | comprehensive | quiz | oral | project | other
date: 2026-11-20         # optional; drives the countdown and the "next up" suggestion
scope:
  lectures: [1, 2, 3, 4, 5, 6]     # lecture numbers; their topics are included
  topics: [revision]               # further topics, if any
```

- `scope.lectures` is the usual way: the exam covers the topics of those lectures.
- Leave `scope` out entirely and the exam covers the whole course.
- **A comprehensive exam** covers what the partial exams cover. Give it
  `includes: [midterm, final]` (folder names) instead of repeating their scope.

That alone is a useful exam page. Everything below is optional and should be written only
when there is something true to say.

## `format`

Duration, number and kind of questions, what is allowed, how it is marked (including
negative marking). Two to four sentences. Source it from the syllabus or the lecturer.

## `weights`

How much of the paper each topic carries, 1 to 5, with the evidence.

```yaml
weights:
  - topic: lsq
    weight: 5
    note: |-
      The whole paper. Both past sittings asked for the derivation and one numeric fit.
```

Write weights only from evidence: past papers, a stated exam structure, repeated emphasis in
lectures. Without evidence, leave them out; an invented weighting is worse than none.

## `plan`

A sequence of phases that tells the student what to do next, so that they never have to
decide. It is the most valuable thing on the page and the easiest to write badly.

```yaml
plan:
  intro: |-
    Two short blocks. The first one is the exam; the second is insurance.
  phases:
    - label: Phase 1
      minutes: 50
      title: The derivation and one fit, until they are automatic
      why: |-
        Those two questions carried 70% of the marks on the last paper.
      tasks:
        - tag: Cards
          text: |-
            Run the least-squares deck. Say the *why* of each step out loud.
          links: ["deck:least-squares", "card:lsq-derive"]
        - tag: Practice
          text: |-
            Problem 1 on paper, solution closed.
          links: ["problems:fitting-practice#fit-p1"]
  skip: |-
    Gradient descent is **not** examined until the final. Leave lecture 2 alone this week.
```

Rules for a good plan:

- **Order by marks per minute, not by lecture number.** What the paper certainly asks and
  the student can certainly learn comes first.
- **Every phase has a `why`** that cites the evidence.
- **Every task is concrete and ends in a link:** a deck (with a `?filter=` where it helps),
  a card, a problem, a paper. "Revise chapter 4" is not a task.
- **Phases are sized in minutes** (25 to 90), with realistic totals.
- **Put a timed sitting of a past paper near the end,** then a phase for the cards it
  exposed (`cards?filter=weak`).
- **`skip` says what to leave out on purpose** and why. A student short of time needs this
  more than anything else.
- Labels are free: `Phase 1`, `Day 2`, `Evening before`, `Morning of`.

Each phase has a tick box on the page; the next unticked phase is what the dashboard
suggests when the exam is within three weeks.

## `predictions`

Questions likely to appear, each with its evidence and a likelihood.

```yaml
predictions:
  - q: |-
      Derive the normal equations from $L(w) = \lVert y - Xw \rVert^2$.
    why: |-
      Asked in both past sittings, word for word.
    likelihood: high          # high | medium | low
    refs: ["card:lsq-derive", "lecture:01-least-squares#the-normal-equations"]
```

Predict only from evidence, and state it in `why`. `refs` point at where the answer is
practised or explained. Five good predictions beat twenty guesses.

## Typical set-ups

- **Two partial exams and a comprehensive one:** `midterm` (first half), `final` (second
  half, `kind: final`), `comprehensive` with `includes: [midterm, final]`.
- **One final exam:** a single folder, no `scope`.
- **Oral exam or project defence:** `kind: oral` / `project`; `predictions` are the likely
  questions, and a deck holds the rehearsed answers.
- **Weekly quizzes:** one folder per quiz with `kind: quiz` and `scope.lectures: [n]`, or
  none at all if a deck per lecture is enough.
