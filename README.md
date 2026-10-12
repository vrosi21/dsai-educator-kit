# DSAI Vault educator kit

Everything you need to write a course for [DSAI Vault](https://dsai3.pages.dev), the study
site for the Data Science and AI programme: the instructions your AI assistant follows,
the format of every content file, and three small tools. An educator is a student who
writes one course for everyone else.

**This repository holds no course.** It is the same for every educator. Your course comes
from the site: you download its files, put them into your copy of this kit, add to them,
and hand the result back on the site. Git keeps track of your course in your copy, on your
computer only. Nothing you write is ever pushed here.

```
AGENTS.md            the instructions your AI assistant follows (CLAUDE.md points to it)
.claude/skills/      the same as a command for Claude Code: /update-cms rl
docs/                how content is written: the guide, every field, an example course
tools/unpack.py      puts the site's version of your course into courses/
tools/check.py       checks your course
tools/pack.py        packs your course into the one file you hand in
courses/             YOUR course goes here
VERSION, CHANGELOG.md   which version of the kit this is, and what changed
```

In the examples the course is `rl`. Use your own course's short name, the one in its
address on the site.

## Git here is local: a commit is not an upload

Below you will meet `git commit` and `git stash`. **Neither sends anything anywhere.** A
commit is git remembering a version inside your own copy of the kit, on your computer.
Uploading would be `git push`, which you switch off in the first step of the set-up, and
which this repository would refuse anyway: only its owner can write to it.

Your course reaches the site in exactly one way: the zip you hand in there.

So why use git at all? Because it does two jobs well. `git diff` shows precisely what
you, or your assistant, changed. And when someone else has changed your course in the
meantime, git can put your work on top of theirs. Both need git to know your course,
which is all that committing it means here.

## Once: set up

You need [git](https://git-scm.com/downloads), [uv](https://docs.astral.sh/uv/) (it runs
the tools and fetches what they need), and an AI assistant that can read and write files
on your computer.

1. **Clone the kit**, and switch pushing off so that your course can never end up in a
   public place by accident:

   ```
   git clone https://github.com/vrosi21/dsai-educator-kit.git
   cd dsai-educator-kit
   git remote set-url --push origin no-pushing
   ```

2. **Download your course.** Sign in on the site, open **Educators**, and under your course
   press **Download the course files**. You get `rl.zip`: the course exactly as the site
   has it. A course nobody has written yet is just its `course.yaml`.
3. **Unpack it into the kit.**

   ```
   uv run tools/unpack.py ~/Downloads/rl.zip
   ```

   The course is now in `courses/rl/`, and the tool has committed that state in your
   copy: a bookmark on your computer, uploaded nowhere. It is your starting point: from
   here on `git diff` shows exactly what you changed.
4. **Add the material.** Put the lecture slides, labs, homework and past papers into
   `courses/rl/source/` (`lectures/`, `labs/`, `homework/`, `exams/`). Git ignores that
   folder and the tools never pack it. It belongs to the lecturers and stays with you.

## Every time: write, check, hand in

1. **Update the kit**, so your assistant works from the latest instructions and format:

   ```
   git pull
   ```

   It never changes your course. The site tells you when there is a new version:
   under the bell at the top, and on the Educators page.
2. **Let your assistant write.** Open this folder in it and tell it:

   ```
   Update the CMS for this course: rl
   ```

   It reads `AGENTS.md`, learns the format from `docs/`, finds what in `source/` has not
   been written up, writes it, and checks its own work. To do one piece at a time, name
   it: `Update the CMS for this course: rl. Only lecture 3.` In Claude Code the same
   thing is the command `/update-cms rl`.
3. **Check what it wrote.** This is your part and the reason the role exists. Read the
   notes against the slides. Work through a few cards and at least one solution by hand.
   `git diff` shows every line that is new. An assistant writes mistakes as confidently
   as it writes everything else.
4. **Pack it.**

   ```
   uv run tools/pack.py rl
   ```

   It checks the course once more and writes `out/rl-<date>-<time>.zip`: your
   `course.yaml` and `content/`, nothing from `source/`.
5. **Hand it in.** On the site: Educators, your course, choose that zip, **Hand in**. The
   site checks it in full. If it passes it is live at once and becomes a step in the
   course's history there. If it removes or rewrites anything, the site first shows you
   what, and takes it in when you confirm.
6. **Note it down, on your computer.** Your copy and the site now agree. Tell git that
   this is your new starting point:

   ```
   git add -A courses/rl
   git commit -m "rl: handed in"
   ```

   This uploads nothing; the hand-in in step 5 already did the only upload there is. It
   is a bookmark in your own copy, so that the next `git diff` shows only what you do
   from here on.

So the rule for git in this folder is simple: **a commit is a bookmark for a version
the site has.** `tools/unpack.py` makes one when you bring the site's version in; you
make one after a hand-in was taken in. Work that is not handed in yet stays uncommitted,
which is exactly what `git diff` shows and what `git stash` can set aside.

## What a hand-in may do

**Add, change and remove.** The course is yours to write: a new lecture, more cards, a
corrected answer, a deck taken apart and put together better.

**Removing has to be meant.** A hand-in that removes or rewrites anything is first shown
back to you on the site: which files, which lines, which ids. It is taken in when you
tick **It may change and remove what is there** and hand it in again. That is there to
catch a slip, such as an assistant tidying up where it should not have. Mind the ids
above all: each card, question, formula and term has one, and what students have marked
is stored under it. Correct an item in place and keep its id; an id that disappears takes
their progress on it along.

**Nothing is lost.** The site keeps the whole course as it stood after every hand-in. On
the Educators page each step of your course has **Download the course as it was after
this step**; to go back to it, unpack that zip and hand it in. Your own newest hand-in
can simply be taken back there. And your own copy has every version in git.

**Not what is the owner's.** In `course.yaml` the `topics` and the `description` are
yours. Title, code, year and whether the course is open are not, and a topic's id stays
as it is.

## If the site says the course has changed

Another educator of your course handed something in, or the owner published a change,
after you took your copy. Taking your zip in would undo their work, so it is refused. The
bell at the top of the site tells you when that happens. Put your work on top of the
latest version:

```
git stash                                    set your work aside
                                             (download the course files again, on the site)
uv run tools/unpack.py ~/Downloads/rl.zip    bring in the site's version
git stash pop                                put your work back on top
uv run tools/pack.py rl                      check and pack again
```

Usually git fits the two together by itself. Where both changed the same place it marks
the file: both versions are in it between `<<<<<<<` and `>>>>>>>`. Decide what stays and
delete the markers, or tell your assistant: *Resolve the merge conflicts in courses/rl.
Keep what the site has unless my change replaces it.* Then hand in the new zip.

## The check

```
uv run tools/check.py rl
uv run tools/check.py --status rl
```

The first checks the structure of your files with the site's own code. The second also
lists what in `source/` has not been written up yet. Links between files and maths are
checked by the site itself when you hand in; if it finds something, it shows you the
report, in the same `file:line` form, to give to your assistant.

Without uv: `pip install pyyaml pydantic`, then `python tools/check.py rl`.

## What never leaves your computer

- Anything under a `source/` folder.
- Scans, photos or copies of slides, handouts and papers, also inside `content/`. Write
  your own summary; draw your own figure.
- Your copy of this kit with your course in it. Do not push it anywhere public and do
  not fork this repository publicly with a course inside. If you want a backup, use a
  private repository of your own.

## Whose it is

Course material belongs to the lecturers and the faculty. What you write are study
summaries of it. What you hand in is shown to everyone who uses the site, and the person
who runs the site may edit or remove it.

Everything in this repository is a copy made from the site's own code, where it is tested
together with what it describes. Found a mistake in the instructions or the format? Use
**Ask or report** on the site.
