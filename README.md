# DSAI Vault educator kit

Everything you need to write a course for [DSAI Vault](https://dsai3.pages.dev), the study
site for the Data Science and AI programme: the format, the instructions your AI assistant
follows, and two small tools. An educator is a student who writes one course for everyone
else.

**This repository holds no course content.** It is the same for every educator. Your
course lives inside your copy of it, in `courses/`, a folder git ignores: nothing you
write there is ever committed, pushed or seen by another educator, and updating the kit
never touches it.

```
AGENTS.md            the instructions your AI assistant follows (CLAUDE.md points to it)
.claude/skills/      the same as a command for Claude Code: /update-cms rl
docs/                how content is written: the guide, every field, an example course
tools/check.py       checks your course
tools/pack.py        packs your course into the one file you hand in
courses/             YOUR course goes here. Ignored by git.
out/                 the files pack.py makes. Ignored by git.
```

## Once: set up

1. **Get the kit.** `git clone` this repository. You only ever read from it.
2. **Get your course.** Sign in on the site, open **Educators**, and under your course
   press **Download the course files**. Unpack the zip into `courses/`, so that you have
   `courses/rl/course.yaml` (with your course's name in place of `rl`). A course nobody
   has written yet is just that one file; one that already has content comes with it.
3. **Add the material.** Put the lecture slides, labs, homework and past papers into
   `courses/rl/source/` (`lectures/`, `labs/`, `homework/`, `exams/`). They stay on your
   computer. They are never packed and never uploaded: they belong to the lecturers.
4. **Install [uv](https://docs.astral.sh/uv/)**, which runs the tools and fetches what
   they need by itself. Or, without it: `pip install pyyaml pydantic`.

## Every time: write, check, hand in

1. **Update the kit**, so your assistant works from the latest instructions and format:

   ```
   git pull
   ```

   Your `courses/` folder is not part of the repository, so this can never conflict with
   your work or change it.
2. **Let your assistant write.** Open this folder in an AI assistant that can read and
   write files on your computer, and tell it:

   ```
   Update the CMS for this course: rl
   ```

   It reads `AGENTS.md`, learns the format from `docs/`, finds what in `source/` has not
   been written up, writes it, and checks its own work. To do one piece at a time, name
   it: `Update the CMS for this course: rl. Only lecture 3.` In Claude Code the same
   thing is the command `/update-cms rl`.
3. **Check what it wrote.** This is your part and the reason the role exists. Read the
   notes against the slides. Work through a few cards and at least one solution by hand.
   An assistant writes mistakes as confidently as it writes everything else.
4. **Pack it.**

   ```
   uv run tools/pack.py rl
   ```

   It checks the course once more and writes `out/rl-<date>-<time>.zip`: your
   `course.yaml` and `content/`, nothing from `source/`.
5. **Hand in that file** to the person who runs the site, the way they asked you to. They
   take it in, the site checks it fully, and it goes live when they publish. If the site
   finds something the check here could not see, you get the report back, in the same
   `file:line` form, to give to your assistant.

Each hand-in is your whole course as it is now, so keep your `courses/` folder: it is the
working copy of your course, and the next hand-in starts from it. On a new computer,
download the course files from the site again; they are what is live.

By hand, without an assistant, it is the same loop: read `docs/AUTHORING.md`, write the
files, check, pack.

## The check

```
uv run tools/check.py rl
uv run tools/check.py --status rl
```

The first checks the structure of your files with the site's own code. The second also
lists what in `source/` has not been written up yet. Links between files and maths are
checked by the site itself when your hand-in is taken in.

## What you may change

Everything under your course's `content/`, and in its `course.yaml` the `topics` and the
`description`. The rest of `course.yaml` (title, code, year, whether the course is open)
belongs to the person who runs the site; a hand-in that changes it is refused. Ids and
file names are permanent once they are live: students' progress is stored under them.

## What never leaves your computer

- Anything under a `source/` folder.
- Scans, photos or copies of slides, handouts and papers, also inside `content/`. Write
  your own summary; draw your own figure.

Do not commit or push in this repository, and never force-add (`git add -f`) anything
under `courses/` or `out/`.

## Whose it is

Course material belongs to the lecturers and the faculty. What you write are study
summaries of it. What you hand in is shown to everyone who uses the site, and the person
who runs the site may edit or remove it.

Everything in this repository is a copy made from the site's own code, where it is tested
together with what it describes. Found a mistake in the instructions or the format? Use
**Ask or report** on the site.
