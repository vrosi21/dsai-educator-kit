# Writing course content

This guide is for whoever turns raw course material into what the site shows: usually an AI
agent working in this repository. Read it fully before writing a first file. The per-type
pages in [content-types/](content-types/) go deeper; load only the ones you need.

## The job

A course is a folder under `courses/`. Its `source/` holds the raw material (slides, lab
sheets, past papers). You read that material and write Markdown and YAML files under
`content/`. A command validates those files and loads them into the site.

```
courses/<course>/
  course.yaml        you write: what the course is, its list of topics
  source/            you READ ONLY: slides, labs, homework, past papers
  content/           you write: everything the site shows
```

**The one rule.** In a content session you create and edit files only under
`courses/<course>/content/` and `courses/<course>/course.yaml`. Never edit anything under
`source/`. Never edit Python, templates, CSS or JavaScript: if the site cannot display
something you need, say so in your report instead of changing code.

## The loop

Run every command from the repository root.

1. **See what exists and what is missing.**
   ```
   uv run python manage.py content_status <course>
   ```
   It lists what the course already contains and, under "not written up yet", the files in
   `source/` that no document refers to. Those are your work list.
2. **Read the sources completely.** Every page of a PDF, every cell of a notebook. Do not
   write from a skim, a table of contents or the file name.
3. **Write or update files** under `content/`. Update in place; do not rewrite files you
   were not asked to change.
4. **Validate.**
   ```
   uv run python manage.py sync_content <course> --check
   ```
   Every problem is reported as `file:line  field`, a message, and usually a `->` line
   saying how to fix it. Fix and re-run until it prints `valid`.
5. **Load it.**
   ```
   uv run python manage.py sync_content <course>
   ```
6. **Report** (see [What to report](#what-to-report)).

That is where a content session ends. The site you just updated is the local one.

**Putting it on the live site** is a separate step, taken only when the owner asks:

```
uv run --env-file .env python manage.py publish
```

It validates every course, sends the course files (never `source/`) to the server, and the
server loads them and prints its own report. You do not connect to the server yourself and
you never write to a database, local or live: files are the only way in. If `publish`
reports errors, fix the files and run it again; the live site is unchanged until it
succeeds. More in [DEPLOYMENT.md](DEPLOYMENT.md#publishing-course-content).

A new course starts with
`uv run python manage.py startcourse <slug> --title "…" --code X --year "2026-27"`.

**Where a course folder sits.** Directly in `courses/`, or one level down in a folder
that groups courses by semester (`courses/semester-5/rl/`). The grouping is only for
finding things: a course's address is its own folder's name either way, and that name
must be unique across all of them. Wherever these pages write `courses/<course>/`, read
"the course's folder".

## Where things go

A file's meaning comes only from its location. You never declare a type.

| Path under `content/` | What it is | Page |
|---|---|---|
| `lectures/NN-name.md` | Notes for one lecture | [documents](content-types/documents.md) |
| `labs/NN-name.md` | A lab: tasks, walkthrough, what to hand in | [documents](content-types/documents.md) |
| `homework/NN-name.md` | A homework: exercises and solutions | [documents](content-types/documents.md) |
| `guides/name.md` | A topic guide that cuts across lectures | [documents](content-types/documents.md) |
| `decks/name.yaml` | A deck of flashcards | [decks](content-types/decks.md) |
| `problems/name.yaml` | A practice problem set | [questions](content-types/questions.md) |
| `exams/<exam>/assessment.yaml` | One exam: scope, format, plan, predictions | [exams](content-types/exams.md) |
| `exams/<exam>/name.yaml` | A past paper or mock exam for that exam | [questions](content-types/questions.md) |
| `reference/formulas.yaml` | The formula sheet | [reference](content-types/reference.md) |
| `reference/glossary.yaml` | Definitions | [reference](content-types/reference.md) |
| `reference/cheatsheet.md` | One printable page | [reference](content-types/reference.md) |
| `memory/hooks.yaml` | Mnemonics | [memory](content-types/memory.md) |
| `memory/palaces/name.yaml` | A memory palace | [memory](content-types/memory.md) |

Images go in a folder named `assets/` next to the file that uses them.

File names are addresses: lowercase letters, digits and hyphens only (`05-fisher-pca.md`).
Every field of every file is listed in [content-types/fields.md](content-types/fields.md).
A complete, valid course that uses every feature is in
[example-course/example/](example-course/example/): copy its shapes.

## Nothing is mandatory

Every content type is optional and the site shows only what exists. Write what helps for
this course and this exam. As a starting point:

| Course is mostly… | Write first | Usually skip |
|---|---|---|
| **Maths, derivations** (analysis, optimisation, probability) | Lecture notes with `definition` / `theorem` / `proof` callouts; decks with many `steps` cards; problem sets with step-through solutions; formula sheet | Glossary, palaces |
| **Theory, concepts** (ethics, methodology, surveys) | Lecture notes; glossary; decks of basic and `cloze` cards; hooks and palaces for lists; mock exams with choice questions | Formula sheet, step-through problems |
| **Coding, labs** (applied ML, robotics software) | Lab pages with full code; decks whose answers are code; "write it from memory" problems | Palaces |
| **Seminar, project** (papers, presentations) | Guides (one per paper or theme); a deck of likely defence questions; an `oral` or `project` exam with predictions | Formula sheet, mock papers |

Exam material depends on what is known about the exam: a plan and predictions need past
papers or explicit hints from the lecturer. Without evidence, write neither.

## Topics come first

`course.yaml` lists the course's topics (chapters or units) in teaching order. Almost
everything else carries a topic id. That is what lets an exam say "I cover lectures 1 to 6"
and have its page collect the matching cards, problems, formulas and hooks automatically.

- Add a topic to `course.yaml` before using its id anywhere.
- Keep topics coarse: 5 to 12 per course, matching chapters or weeks, not individual ideas.
- A topic id is permanent, like every id.

## Ids are permanent

Cards, questions, formula rows, glossary terms and hooks each have an `id`. The learner's
progress is stored under that id.

- An id is lowercase letters, digits and single hyphens: `fisher-01`, `f-normal`, `mid25-q2`.
- **Unique across the whole course**, not just within its file.
- **Never rename an id, and never reuse one for different content.** Renaming silently
  throws away the learner's grade for that item.
- To improve an item, edit its text and keep its id. To retire one, delete it.
- Suggested prefixes: cards `<topic>-…`, formulas `f-…`, glossary `g-…`, hooks `h-…`,
  questions `<set>-q1` or `<set>-p1`.

File names behave the same way for documents: renaming `03-bayes.md` changes its address
and loses every reader's rating of it. Moving a card to another deck file is safe.

## Linking

Never write a site URL or a relative file path. Link with a reference; sync turns it into
the real address and fails if the target does not exist.

| Write | Links to |
|---|---|
| `lecture:05-fisher-pca` · `lab:02-knn` · `hw:01-sets` · `guide:pca-vs-fisher` | A document, by file name. Add `#heading-id` for a section |
| `deck:ch5-fisher` | A deck. Optional `?filter=` `due` `weak` `unseen` `missed` `shaky` `solid` `key` `steps` `cloze` |
| `card:fisher-01` | One flashcard |
| `problems:fitting-practice` · `problems:fitting-practice#fit-p1` | A problem set, or one question in it |
| `paper:midterm/past-2025` | A paper: exam folder, slash, file name. Optional `?mode=sit` |
| `exam:midterm` | An exam's page |
| `formula:f-normal` · `term:g-residual` · `hook:h-rate` · `palace:gd-loop` · `topic:lsq` | That item |
| `cards` · `cards?filter=weak` · `problems` · `exams` · `formulas` · `glossary` · `cheatsheet` · `memory` · `course` | A whole section |
| `source:lectures/L05.pdf` | A raw file (works only on the local site) |

In Markdown: `[the derivation](card:lsq-derive)`. With empty brackets the link text becomes
the target's own title: `[](lecture:02-gradient-descent)`. In YAML `links:` and `refs:`
lists, write the bare reference: `["deck:ch5-fisher", "card:fisher-01"]`.

External links are ordinary Markdown with a full address: `[KaTeX](https://katex.org)`.

## Markdown

Standard Markdown (CommonMark) with tables, plus the following.

**Headings.** In documents start at `##`; the page title comes from `title` in the front
matter. `#` is an error. Use `##` for sections and `###` for subsections: they form the
page's table of contents.

**Maths** is LaTeX, typeset by KaTeX.

- Inline `$x^2$`. Display on its own line(s): `$$ … $$`.
- Multi-line: `$$\begin{aligned} a &= b \\ &= c \end{aligned}$$`.
- A `$` touching a digit is not maths (`5$x$` fails): put the number inside, `$5x$`.
- Money is written `\$5`.
- Not available: `\label`, `\ref`, `\eqref`, `\newcommand`, `\usepackage`. Number an
  equation with `\tag{1}` if you must.
- Every formula is parsed by KaTeX during sync; a typo such as `\fraq` is reported with
  its line.

**Callouts** set a block apart. The name is lowercase; a title after it is optional.

```
:::definition Residual
The residual of point $i$ is $r_i = y_i - \hat y_i$.
:::
```

| Name | Use it for |
|---|---|
| `definition` | A term being defined |
| `theorem` | A statement that is proved or quoted |
| `proof` | Its proof (collapsed until opened) |
| `example` | A worked example |
| `paper` | "Write this on paper": the exam-ready wording of an answer |
| `note` | A side remark |
| `tip` | A shortcut or good habit |
| `warning` | Something that goes wrong in practice |
| `pitfall` | A mistake people make in exams |
| `recall` | A question to answer before reading on; the title is the question, the body the answer (collapsed) |
| `solution` | A solution inside a homework or lab page (collapsed) |

Do not nest callouts.

**Code** goes in fenced blocks with a language (` ```python `); it is syntax-highlighted.
Inline code uses backticks.

**Images.** `![What the picture shows](assets/boundary.svg)`, with the path relative to the
file. Formats: svg, png, jpg, webp, gif. The text in brackets is read by screen readers and
shown if the image fails, so describe the picture. Add `{.adapt}` after a black-on-clear
line drawing so it is inverted in dark mode: `![…](assets/x.svg){.adapt}`.

**Not allowed.** Raw HTML (`<br>`, `<sub>`, `<div>`): it would be shown as text, so it is
an error. Use Markdown and LaTeX instead (`$x_i$`, not `x<sub>i</sub>`).

Text is not "smartened": `(c)` stays `(c)`, and file names such as `train.py` are not
turned into links.

## YAML

- Two spaces per level. No tabs.
- Put anything with Markdown, maths or more than a few words in a **block scalar**:
  ```yaml
  a: |-
    $$X^\top X\, w = X^\top y$$
  ```
  Inside a block scalar every character is literal, so LaTeX needs no escaping.
- **Never put a backslash inside double quotes.** YAML reads `"\theta"` as a TAB followed
  by `heta` and `"\frac"` as a form feed followed by `rac`. Sync rejects it.
- A short value can be written plainly (`title: Least squares`) unless it contains `: `
  (colon and space) or ` #`, or starts with a symbol such as `[ { * & ! | > ' " % @` or a
  backtick. Then use single quotes, where backslashes are literal:
  `- 'One step: $w \leftarrow w - \eta g$'`.
- `yes`, `no`, `on`, `off`, `true`, `false`, `null`, numbers and dates are not text. Quote
  them when you mean text: `title: "2026"`, `term: "On"`.
- No anchors or aliases (`&name`, `*name`), no duplicate keys, no fields that are not in
  [fields.md](content-types/fields.md).

## Quality bar

The reader is a student preparing for an exam, studying alone, often at night.

**Be faithful to the source.**
- Everything you write must be supported by the course material. When you add something
  from general knowledge (an intuition, a worked example the slides lack), that is welcome,
  but say so in a `note` callout: "Not in the slides: …".
- Cite where things come from, in passing: "(slide 14)", "(lab 3, task 2)".
- Use the lecturer's notation and names. If the slides write $\Sigma_W$, do not switch to
  $S_w$.
- If a source is unreadable, ambiguous or contradicts another, do not guess silently. Write
  what you assumed in a `note` callout or a question's `source` field, and list it in your
  report.
- Do not copy long passages verbatim. Explain in your own words.

**Explain, do not list.**
- Define every symbol the first time it appears.
- Give the reason a step is allowed, not only the step.
- Prefer one worked example with real numbers over a paragraph of description.

**Write for retrieval.** Reading feels like learning and mostly is not. Each lecture note
should end up paired with cards and, where it applies, problems.

**Do not use the phrasing of chatbots.** No "Let's dive in", "It's important to note",
"In conclusion". No emoji. Plain, direct sentences.

Type-specific standards (what makes a good card, a good solution, a good plan) are on the
per-type pages.

## Reading the source material

- **Slides (PDF):** read every page. Slides are terse; reconstruct the argument that
  connects them. Diagrams often carry the content: describe what they show.
- **Notebooks:** read the code and the outputs. Keep the code that teaches something; drop
  boilerplate.
- **Past papers and photos of papers:** transcribe each question exactly. Where a part is
  illegible, say so in the question's `source` field rather than inventing it.
- **Your own earlier files:** when new material arrives, extend the existing notes and decks
  instead of creating parallel ones.

`sources:` in a document's front matter lists the files it was written from, as paths under
`source/` (`lectures/L05.pdf`). `content_status` uses that to tell what is still unwritten.

**Material from an earlier year.** A course folder is one academic year, the `year` in its
`course.yaml`. Material from another year of the same course is kept apart in
`source/<year>/`, for example `source/2025-26/`, and is named with that folder in
`sources:` (`2025-26/HW2.pdf`). Say which year it is from wherever the reader meets it
(the text, a past paper's title and `date`, a question's `source`), and never present its
dates, exam format, weights or staff as this year's. Where the two years differ, this
year's material is what the course says.

## When sync reports a problem

| Message contains | What happened | Fix |
|---|---|---|
| `double-quoted text contains a backslash` | LaTeX inside `"…"` | Use a block scalar `\|-` |
| `not valid YAML` | Indentation, or an unquoted value containing `: ` | Check the line above; quote or use a block scalar |
| `unknown field` | Misspelt or invented field | Use the name it suggests, or see fields.md |
| `must be text, but YAML read` | A number, date or `yes`/`no` where text was meant | Quote it |
| `id … is already used at` | Two items share an id | Give the newer one a new id |
| `no topic named` | Topic not declared | Add it to `course.yaml`, or fix the spelling |
| `no … named … in this course` | A link points at something that does not exist | Fix the reference; the hint lists near matches |
| `is not a link the site understands` | A file path or bare word used as a link | Use a reference from [Linking](#linking) |
| `raw HTML` | An HTML tag in Markdown | Use Markdown or LaTeX |
| ``a `#` heading`` | `#` in a document | Start at `##` |
| `is not a callout the site knows` | Unknown `:::name` | Use a name from the table above |
| `maths: …` | LaTeX that KaTeX cannot parse | The hint shows the formula; fix the command or the braces |
| `image not found` | Wrong path | Paths are relative to the file: `assets/name.svg` |
| ``a `$` was left as plain text`` (warning) | An unmatched `$`, or a `$` next to a digit | Fix the delimiters, or write `\$` for money |

Warnings do not block the sync. Errors do, for that course only; the site keeps showing the
last valid version.

## What to report

End a content session with a short report:

1. **Written:** files created and files changed, one line each.
2. **Counts:** from the last `sync_content` output.
3. **Assumed or unreadable:** every place you could not follow the source exactly.
4. **Not done:** source files still unwritten (`content_status` lists them), and anything
   the site could not express.
5. **Published or not:** say plainly whether the live site has these changes. Unless you
   were asked to run `publish` and it succeeded, it does not.
