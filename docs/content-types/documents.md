# Documents: lectures, labs, homework, guides

A document is a Markdown file with a short YAML header (front matter). The folder decides
its kind:

| Folder | Kind | Write one when |
|---|---|---|
| `content/lectures/` | Lecture notes | A lecture has been given; one file per lecture |
| `content/labs/` | Lab | There is a lab sheet or notebook to work through |
| `content/homework/` | Homework | An assignment has been set (and, later, solved) |
| `content/guides/` | Guide | A subject needs explaining across lectures: a comparison, a method, a "how to answer this kind of question" |

Front matter fields: [fields.md#document](fields.md#document). Examples:
[lecture](../example-course/example/content/lectures/01-least-squares.md),
[lab](../example-course/example/content/labs/01-fit-a-line.md),
[homework](../example-course/example/content/homework/01-normal-equations.md),
[guide](../example-course/example/content/guides/choosing-a-method.md).

## Shape

```markdown
---
title: Least squares
number: 1
date: 2026-10-05
topics: [lsq]
summary: Fit a line by minimising squared residuals. The normal equations give the answer in closed form.
takeaways:
  - The loss is the sum of squared residuals, $L(w) = \lVert y - Xw \rVert^2$.
  - Setting the gradient to zero gives the normal equations $X^\top X\, w = X^\top y$.
sources:
  - lectures/L01_least_squares.pdf
---

## The model

We predict a target $y$ from one feature $x$ …
```

- **File name:** `NN-short-name.md` for lectures, labs and homework, where `NN` is the
  number (`05-fisher-pca.md`). Guides have no number (`pca-vs-fisher.md`).
- **`title`** is the page title. Do not repeat it as a heading.
- **`summary`** is plain text (no Markdown), one or two sentences, shown in lists.
- **`takeaways`** are 3 to 6 statements, each a full sentence, shown in a box above the
  text under "If you remember nothing else". Maths is allowed. If a takeaway contains `: `
  wrap it in single quotes.
- **`sources`** lists the raw files the page was written from, relative to `source/`.
- **`due`** (labs, homework) shows a deadline. **`status: draft`** marks unfinished pages.

## Lecture notes

The aim is a page the student can learn from without the slides.

A structure that works:

1. **Where this fits.** One short paragraph: what problem the lecture solves, what it builds
   on.
2. **The ideas, in the lecture's order.** One `##` section per idea. Definitions in
   `definition` callouts, results in `theorem`, their proofs in `proof` (collapsed, so the
   page stays readable).
3. **A worked example** with concrete numbers for anything computational.
4. **What an exam wants**, in `paper` callouts: the wording you would actually write.
5. **Where next:** links to the deck and problems for this lecture.

Standards:

- Define every symbol at first use, in the sentence where it appears.
- Reconstruct the argument between slides. If slide 12 states a result and slide 13 uses it,
  the notes say why it holds.
- Keep the lecturer's notation.
- Cite as you go: "(slide 14)".
- Use `pitfall` for mistakes the lecturer warned about and `recall` to make the reader stop
  and answer before reading on. Two or three `recall` blocks per lecture is plenty.
- Length follows the material. A 40-slide lecture is usually 600 to 1500 words of notes plus
  maths. Do not pad.

## Labs

- State the goal, then one `##` section per task, in the sheet's order.
- Show complete, runnable code for each task, with the output that matters described in
  words.
- Explain choices (why this learning rate, why this split), not syntax.
- End with what has to be handed in, as a task list (`- [ ]`).

## Homework

- Reproduce each exercise as set.
- Put each solution in a `:::solution` callout so it stays closed until opened.
- End every solution with the answer stated plainly (`**Answer:** …`).
- Before the deadline, a homework page may hold only the exercises (`status: draft`).

## Guides

A guide answers a question the lectures answer only in pieces. Good subjects: "PCA or
Fisher?", "How to read a QQ plot", "Every derivation that reuses the same trick". Use
tables for comparisons, and link to the lectures, cards and formulas it draws on.
