# DSAI Vault educator kit: instructions for an AI assistant

DSAI Vault is a study site for the Data Science and AI programme. Its courses are written
by students, called educators. This repository is their kit: the format, the instructions
you are reading, and the tools. The person you are working for writes one course. Its
files are in `courses/<course>/` on this computer, and you write them from the raw
material in that course's `source/` folder.

You are most likely here because someone told you:

```
Update the CMS for this course: rl
```

That means: follow the procedure below for exactly that one course, the folder
`courses/rl`. If they named a lecture or a file, do that part; if they did not, the work
list in step 2 tells you what is missing.

## The layout

```
courses/rl/           one course. Everything in courses/ is ignored by git.
  course.yaml         what the course is, and its list of topics
  source/             raw material: slides, labs, homework, past papers. READ ONLY.
  content/            what the site shows. This is where you write.
docs/                 the format: how content files are written. Read it, never edit it.
tools/                check.py and pack.py. Never edit them.
out/                  the zip files pack.py makes. Ignored by git.
```

This repository carries no course content and never will: `courses/` and `out/` are
ignored, so nothing written there is ever committed or pushed. If `courses/` has no folder
for the course, stop and ask the person to download their course's files from the site
(the Educators page) and unpack them there. If the course's `source/` is empty, stop and
ask them to put the lecture material there: there is nothing to write from.

## Rules that are never broken

1. **One course per task.** Create and edit files only in that course's `content/` folder,
   and in its `course.yaml` only as rule 4 allows. Leave every other course, `docs/`,
   `tools/` and every other file of this repository exactly as it is.
2. **`source/` is read-only and stays where it is.** The slides and papers belong to the
   lecturers. Do not copy their pages, scans or figures into `content/`; write your own
   summary in your own words. A diagram you draw yourself or a plot you generate is fine.
3. **Ids and file names are permanent.** Every card, question, formula, term and hook has
   an `id`, and a document's file name is its address. Each student's progress is stored
   under them. Never rename, renumber or reuse one. To improve an item, edit it in place.
4. **`course.yaml` is mostly not yours.** You may add `topics` (and reword a topic's
   `title`), and write the `description`. Do not change `title`, `code`, `year`, `series`,
   `semester`, `status`, `enabled`, `has_educator`, `hue` or `order`, and never change or
   remove a topic's `id`. A hand-in that changes any of them is refused as a whole.
5. **Write what the source supports.** If you add something that is not in the material
   (an extra example, background the slides assume), say so in your report. Never invent
   exam dates, weights, or what "will be on the exam".
6. **Never use git on course files.** Do not `git add -f` anything under `courses/` or
   `out/`, and do not commit or push in this repository at all: it is read-only for
   educators, and it is updated with `git pull`.
7. **Do not pack or hand in unless you are asked.** The person checks what you wrote
   against the lecture first. That check is theirs and cannot be skipped.

## The procedure

1. **Learn the format.** Read `docs/AUTHORING.md` completely. Then read the page under
   `docs/content-types/` for each kind of file you are about to write, and nothing you do
   not need. `docs/example-course/example/` is a complete, valid course that uses every
   feature once: copy its shapes.

   That guide was written for the site's own repository, so its paths and commands differ
   here. The course is in `courses/<course>/` of this kit. Where it says
   `manage.py content_status <course>`, run step 2 below. Where it says
   `manage.py sync_content <course> --check`, run step 5 below. Loading into the site and
   `publish` are not part of your work: the person who runs the site does both.

2. **See what exists and what is missing.**
   ```
   uv run tools/check.py --status rl
   ```
   It prints what the course contains and, under "not written up yet", the files in
   `source/` that no document names in its `sources:` field. That is the work list.
3. **Read the sources completely.** Every page of a PDF, every cell of a notebook. Do not
   write from a skim, a table of contents or a file name. If you cannot read a file (a
   scan without text, a format you cannot open), say so in the report; do not guess its
   contents.
4. **Write or update the files** under `content/`. Update in place; leave alone what you
   were not asked to change. Add a topic to `course.yaml` before the first file refers to
   it. Name the source files a document was written from in its `sources:` field: that is
   how step 2 knows the material is covered.

   For one lecture this usually means its notes (`content/lectures/NN-name.md`), a deck of
   flashcards (`content/decks/`), and, where the course has exercises, problems with
   worked solutions (`content/problems/`), plus new rows for the formula sheet and the
   glossary. `docs/AUTHORING.md` has a playbook for each type of course and the quality bar
   every file must meet.
5. **Check.**
   ```
   uv run tools/check.py rl
   ```
   Every problem is reported as `file:line  field`, a message, and usually a `->` line
   saying how to fix it. Fix and re-run until it says the structure is valid.
6. **Report** to the person, in this order: the files you created and the files you
   changed; what in `source/` you could not read; anything you wrote that is not in the
   source; and what they should look at first when they check your work (derivations,
   numbers, anything you were unsure about).

Without `uv`: `pip install pyyaml pydantic` once, then `python tools/check.py ...`.

## What the check covers

`tools/check.py` is the first half of the site's own importer, the same code. It catches
files in the wrong place, YAML that does not parse, unknown or missing fields, wrong
types, an id used twice, and a `topic` that `course.yaml` does not declare.

It cannot see what needs the whole site: links between files (`lecture:03-search`,
`card:mdp-01`), the Markdown inside your text, and whether the maths typesets. So be
exact there:

- A link names something that exists, spelled as its file name or id is spelled.
- Maths is LaTeX between `$…$` or `$$…$$`, with every brace and environment closed.
- In YAML, prose and maths go in block scalars (`|-`). A double-quoted string with a
  backslash in it is an error: `"\theta"` is a TAB followed by `heta`.

Those are checked when the hand-in is taken in by the site. If something fails there the
person is sent the report, in the same `file:line` form, for you to fix.

## Handing it in (only when asked)

```
uv run tools/pack.py rl
```

It runs the check again and, if the course is valid, writes `out/rl-<date>-<time>.zip`:
the course's `course.yaml` and its `content/`, and nothing from `source/`. Tell the person
where the file is. Sending it is theirs to do.
