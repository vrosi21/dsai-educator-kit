# Reference: formula sheet, glossary, cheat sheet

Three optional files under `content/reference/`. Each page has a **cover and recall** mode:
the answers are hidden, the student says them, then clicks to check. Write them with that
use in mind.

## Formula sheet: `formulas.yaml`

Fields: [fields.md#formulas](fields.md#formulas). Example:
[formulas.yaml](../example-course/example/content/reference/formulas.yaml).

```yaml
sections:
  - title: Least squares
    topic: lsq
    rows:
      - id: f-normal
        name: Normal equations
        formula: |-
          $$X^\top X\, w = X^\top y$$
        note: |-
          Unique solution when the columns of $X$ are linearly independent.
```

- **What belongs:** everything the student may have to write from memory. Not derivations
  (those are `steps` cards) and not explanations (those are notes).
- **`name`** is what the formula would be called in a question: "Normal equations",
  "Mahalanobis distance". In cover mode only the name is visible, so it must identify the
  formula without giving it away.
- **`formula`** is normally a single display equation.
- **`note`** defines the symbols and states conditions. Keep it to a line or two.
- **One section per topic, with `topic` set.** An exam page then links to exactly the
  sections in its scope.
- Ids: `f-…`, unique in the course, permanent.

## Glossary: `glossary.yaml`

Fields: [fields.md#glossary](fields.md#glossary). Example:
[glossary.yaml](../example-course/example/content/reference/glossary.yaml).

```yaml
terms:
  - id: g-residual
    term: Residual
    topic: lsq
    definition: |-
      The difference $r_i = y_i - \hat y_i$ between an observed target and the model's
      prediction for the same input.
    see: [g-design-matrix]
```

- Most useful in theory-heavy courses where exams ask "define" and "distinguish".
- A definition is one to three sentences that could be written in an exam as they stand.
  Say what the thing is before saying what it is for.
- Do not define a term using itself, or using another term that is not in the glossary.
- `see` lists the ids of related terms.
- The page sorts terms alphabetically; file order does not matter.
- Ids: `g-…`.

## Cheat sheet: `cheatsheet.md`

A Markdown document (front matter needs only `title`) laid out in two columns and built to
be printed. Example:
[cheatsheet.md](../example-course/example/content/reference/cheatsheet.md).

- One page. If it does not fit on one printed page it is not a cheat sheet.
- Short `##` sections of bullet points and small tables. No prose paragraphs, no callouts.
- It summarises; it does not introduce anything that is not in the notes.
- Write it late, once the course's shape is known. It is the last thing read before an exam.
