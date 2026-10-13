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
courses/rl/           one course, as downloaded from the site and added to here
  course.yaml         what the course is, and its list of topics
  source/             raw material: slides, labs, homework, past papers. READ ONLY.
    2025-26/          material from an EARLIER year, in a folder named after that year
  content/            what the site shows. This is where you write.
docs/                 the format: how content files are written. Read it, never edit it.
tools/                unpack.py, check.py and pack.py. Never edit them.
out/                  the zip files pack.py makes. Ignored by git.
```

The repository this was cloned from carries no course. The course was downloaded from the
site and unpacked here with `tools/unpack.py`, which committed it: **in this folder a
commit is a bookmark for a version of the course that the site has.** Commits here are
local. Nothing is ever pushed: from this folder the course reaches the site only as the zip the person
hands in. Everything written since the last commit is uncommitted, so
`git diff -- courses/rl` is exactly the work that has not been handed in.

If `courses/` has no folder for the course, stop and ask the person to download their
course's files from the site (the Educators page) and run `uv run tools/unpack.py` on the
zip. If the course's `source/` is empty, stop and ask them to put the lecture material
there: there is nothing to write from.

## Rules that are never broken

1. **One course per task.** Create and edit files only in that course's `content/` folder,
   and in its `course.yaml` only as rule 5 allows. Leave every other course, `docs/`,
   `tools/` and every other file of this repository exactly as it is.
2. **Change what is there only on purpose.** The course is the educator's to write: you
   may add, correct and remove. But nothing that is committed changes by accident. Update
   a file in place; do not reformat, reorder, re-indent or "tidy" lines you were not asked
   to touch, and never delete an item or a file unless the person asked for that. Before
   you finish, read `git diff -- courses/<course>`: every removed line (`-`) must be one
   you meant to remove. The site shows the person each line and id a hand-in takes away
   and asks them to confirm it, so name every removal and rewrite in your report first.
3. **`source/` is read-only and stays where it is.** The slides and papers belong to the
   lecturers. Do not copy their pages, scans or figures into `content/`; write your own
   summary in your own words. A diagram you draw yourself or a plot you generate is fine.
4. **Ids and file names are permanent.** Every card, question, formula, term and hook has
   an `id`, and a document's file name is its address. Each student's progress is stored
   under them. Never rename, renumber or reuse one. To improve an item, edit it in place
   and keep its id; an id that disappears takes the students' progress on it along.
5. **`course.yaml` is mostly not yours.** You may add `topics`, and write the
   `description`. Do not change `title`, `code`, `year`, `series`, `semester`, `status`,
   `enabled`, `has_educator`, `hue` or `order`, and never change or remove a topic's `id`.
6. **Write what the source supports.** If you add something that is not in the material
   (an extra example, background the slides assume), say so in your report. Never invent
   exam dates, weights, or what "will be on the exam".
7. **Git: only what this file says.** Do not commit the person's work in progress, and
   never push, force-add anything under `source/`, or change the remote. Commits are made
   by `tools/unpack.py` (a version from the site) and by the person after the site has
   taken a hand-in. The one time you use git yourself is the procedure "The course
   changed on the site", below, when asked.
8. **Do not pack or hand in unless you are asked.** The person checks what you wrote
   against the lecture first. That check is theirs and cannot be skipped.
9. **An earlier year stays an earlier year.** Material in a folder named after a year
   (`source/2025-26/`) is from that year of the course, not from the one you are writing.
   Never present it as current: see "Material from an earlier year", just below.
10. **What was made on the site stays as it is.** The person can also change the course in
    the site's own editor. What arrives from there is part of the course like anything
    else: files written in a plainer layout than yours, and images named by a string of
    hex digits (`assets/3f9c2ab04d17e6a1.webp`). Do not re-lay those files out and do not
    rename, convert or remove those images or the lines that show them (rule 2).

## Material from an earlier year

The course you write is one academic year: the `year` in its `course.yaml`. Material from
another year of the same course (last year's slides, homework sheets, past papers) is
kept apart, in a folder under `source/` named after the year it is from:

```
courses/rl/source/2025-26/
```

That folder is how you know. If the person hands you earlier material that sits loose
among this year's, ask them to move it into such a folder first; you do not move files in
`source/`. When you write from it:

- Name it in `sources:` with its folder, like any other source: `2025-26/HW2.pdf`.
- Say which year it is from, where the reader meets it: in the text ("from 2025-26"), in
  a past paper's title and `date`, in a question's `source` field.
- Never present its dates, exam format, weights, staff or coursework as this year's.
  Where this year's material says something else, this year's is what the course says,
  and the difference is worth a sentence.
- Do not write this year's lecture notes from last year's slides when this year's exist.
  If only the earlier year has a lecture, write it and say so at the top of the note.

## The procedure

1. **Learn the format.** Read `docs/AUTHORING.md` completely. Then read the page under
   `docs/content-types/` for each kind of file you are about to write, and nothing you do
   not need. `docs/example-course/example/` is a complete, valid course that uses every
   feature once: copy its shapes.

   That guide was written for the site's own repository, so its paths and commands differ
   here. The course is in `courses/<course>/` of this kit. Where it says
   `manage.py content_status <course>`, run step 2 below. Where it says
   `manage.py sync_content <course> --check`, run step 5 below. Loading into the site and
   `publish` are not part of your work.

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
4. **Write or update the files** under `content/`. Update in place; leave alone what
   you were not asked to change. Add a topic to `course.yaml` before the first file
   refers to it. Name the source files a document was written from in its `sources:`
   field: that is how step 2 knows the material is covered.

   For one lecture this usually means its notes (`content/lectures/NN-name.md`), a deck of
   flashcards (`content/decks/`), and, where the course has exercises, problems with
   worked solutions (`content/problems/`), plus new rows for the formula sheet and the
   glossary. `docs/AUTHORING.md` has a playbook for each type of course and the quality bar
   every file must meet.
5. **Check.**
   ```
   uv run tools/check.py rl
   git diff --stat -- courses/rl
   ```
   Every problem the check finds is reported as `file:line  field`, a message, and usually
   a `->` line saying how to fix it. Fix and re-run until it says the structure is valid.
   Then read the diff itself for removed lines: each must be one you meant.
6. **Report** to the person, in this order: the files you created and the files you
   changed; **everything you removed or rewrote, and why**; what in `source/` you could
   not read; anything you wrote that is not in the source; anything already there that
   you think is wrong but were not asked to change; and what they should look at first
   when they check your work.

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

The site checks those when the person hands in. If it refuses, it shows them a report in
the same `file:line` form; they give it to you, you fix what it names, and they pack
again.

## Handing it in (only when asked)

```
uv run tools/pack.py rl
```

It runs the check again and, if the course is valid, writes `out/rl-<date>-<time>.zip`:
the course's `course.yaml` and its `content/`, and nothing from `source/`. Tell the person
where the file is, and what in it removes or rewrites something that is on the site.
Uploading it on the site's Educators page is theirs to do; if it takes anything away, the
site shows them what and they confirm with a tick. When the site has taken it in, they
record it: `git add -A courses/rl` and `git commit -m "rl: handed in"`. Do that for them
only if they ask.

## The course changed on the site (only when asked)

The site refuses a hand-in built on an older version of the course than it has: someone
changed the course in the meantime, with a hand-in or in the site's own editor (it may
have been this person). The person downloads the course files again
and asks you to bring their work on top. With the new zip at, say, `~/Downloads/rl.zip`:

```
git stash
uv run tools/unpack.py ~/Downloads/rl.zip
git stash pop
```

`git stash` sets the uncommitted work aside, `unpack.py` brings in and commits the site's
version, `git stash pop` puts the work back on top. If git reports conflicts, open each
marked file: between `<<<<<<<` and `>>>>>>>` are the two versions. Where they are
different things (two new cards, say), keep both, the site's first. Where they are two
versions of the same thing, keep the site's unless the person's change was meant to
replace it; if you cannot tell, keep both and say so. Never drop what someone else added
just to make the conflict go away. Delete the marker lines, run the check, read
`git diff -- courses/rl`, and tell the person what you merged and what you chose.

`unpack.py` says so when the site's version no longer has lines that the last commit
had: someone removed them on the site, which is fine, or work was committed here without
being handed in, which is then still in git's history. Pass that note on to the person.
