# DSAI Vault educator kit

You are an educator: a student who writes one course of [DSAI Vault](https://dsai3.pages.dev),
the study site of the Data Science and AI programme, for everyone else. This folder is your
toolbox. It has the instructions your AI assistant follows, the format of the files, and
three small tools.

You do not need to know programming. You need to follow the steps below once, and after
that the work is a loop of five commands. Everything you type is written out here, ready
to copy.

**This repository holds no course.** It is the same for every educator. Your course comes
from the site: you download it, work on it in this folder on your own computer, and hand
the result back on the site.

## The short version

```
1. Download your course from the site          (Educators -> your course)
2. uv run tools/unpack.py ~/Downloads/rl.zip    put it into this folder
3. Put the lecture slides in courses/rl/source/
4. Tell your AI assistant:  Update the CMS for this course: rl
5. Read what it wrote. Check it against the lecture.
6. uv run tools/pack.py rl                      make one zip
7. Hand that zip in on the site                 (Educators -> your course -> Hand in)
```

In all examples the course is `rl`. Use your own course's short name: the last word of
its address on the site (`dsai3.pages.dev/courses/rl/`).

> **Important: material from an earlier year goes in its own folder.**
> If you write from last year's slides, homework or past papers, do not mix them with
> this year's. Put them in a folder named after their year, for example
> `courses/rl/source/2025-26/`. Your assistant then knows that it is older material and
> writes it up as that year's. Mixed in, last year's exam dates and rules end up on the
> site as if they were this year's. More under [step 4 of the set-up](#once-set-up).

## Words you will meet

- **Terminal**: the window where you type commands. On Windows it is called *Terminal* or
  *PowerShell*, on a Mac *Terminal*. You type a line and press Enter.
- **Folder**: the same thing as a directory. `courses/rl/source/` means: the folder
  `source`, inside `rl`, inside `courses`, inside this kit.
- **Clone**: download a copy of this kit to your computer, with git.
- **git**: a program that remembers versions of files. Here it runs only on your
  computer. More about that [below](#git-here-is-local-a-commit-is-not-an-upload).
- **uv**: a program that runs the three tools. It fetches what they need by itself.
- **AI assistant**: a program like Claude Code, Cursor, Codex or Gemini CLI that can read
  and write files in a folder on your computer. A chat in a browser tab cannot do that.

## What is in this folder

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

You never need to edit anything except what is inside `courses/`.

## Once: set up

### A. Install two programs

**git**

- Windows: download and run the installer from <https://git-scm.com/downloads>. Keep
  every setting it suggests.
- Mac: open Terminal and type `xcode-select --install`.
- Linux: `sudo apt install git` (or your system's own way).

**uv**

- Windows: open PowerShell and paste

  ```
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

- Mac and Linux: open Terminal and paste

  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

Close the terminal and open a new one. Then check that both are there. Each line should
answer with a version number:

```
git --version
uv --version
```

If one says "not found" or "not recognized", close the terminal, open a new one and try
again. If it still does, install that program once more.

You also need an AI assistant that works in a folder (see [the words](#words-you-will-meet)).

### B. Get the kit and your course

Open a terminal in the folder where you keep your study things (Documents is fine). On
Windows: open that folder in File Explorer, right-click an empty spot, choose **Open in
Terminal**. On a Mac: open Terminal and type `cd Documents`.

1. **Clone the kit**, go into it, and switch uploading off, so that your course can never
   end up in a public place by accident. Three lines, one after the other:

   ```
   git clone https://github.com/vrosi21/dsai-educator-kit.git
   cd dsai-educator-kit
   git remote set-url --push origin no-pushing
   ```

   You now have a folder `dsai-educator-kit`. **Every command from here on is typed
   inside that folder.** When you open a new terminal later, go into it first
   (`cd Documents/dsai-educator-kit`), or open the folder and choose **Open in Terminal**.

2. **Download your course.** Sign in on the site, open **Educators**, and on your course
   press **Download the course files**. You get `rl.zip` in your Downloads folder: the
   course exactly as the site has it. A course nobody has written yet is just one small
   file, `course.yaml`.

3. **Unpack it into the kit.**

   ```
   uv run tools/unpack.py ~/Downloads/rl.zip
   ```

   `~/Downloads/rl.zip` means "the file rl.zip in my Downloads folder". If the tool says
   it cannot find the file, type `uv run tools/unpack.py ` (with the space) and then drag
   the zip file from your Downloads folder into the terminal window: that pastes where it
   is. Press Enter.

   The first time, uv fetches a few things; that takes a minute. When it is done the
   course is in `courses/rl/`, and the tool says `Committed in your copy`. That is a
   bookmark on your computer, uploaded nowhere. It is your starting point.

4. **Add the material.** Put the lecture slides, labs, homework and past papers into
   `courses/rl/source/`. Make folders inside it as you like; `lectures/`, `labs/`,
   `homework/` and `exams/` are the usual ones. This folder stays on your computer: git
   ignores it and the tools never pack it. The material belongs to the lecturers.

   > **Important: material from an earlier year** (last year's slides, homework, past
   > papers) goes in a folder of its own, named after that year:
   >
   > ```
   > courses/rl/source/2025-26/
   > ```
   >
   > Write the year as the site does: two years with a dash, `2025-26`. That folder is how
   > your assistant knows the material is not this year's. It then writes it up as that
   > year's, says so in the text, and does not pass off last year's dates, exam format or
   > coursework as the current ones. This year's material stays outside that folder.

## Every time: write, check, hand in

Open a terminal in the kit's folder first.

1. **Update the kit**, so your assistant works from the latest instructions:

   ```
   git pull
   ```

   It never changes your course. The site tells you when there is a new version: under
   the bell at the top, and on the Educators page.

2. **Let your assistant write.** Open the kit's folder in your AI assistant and tell it:

   ```
   Update the CMS for this course: rl
   ```

   It reads `AGENTS.md`, learns the format from `docs/`, finds what in `source/` has not
   been written up, writes it, and checks its own work. To do one piece at a time, name
   it: `Update the CMS for this course: rl. Only lecture 3.` In Claude Code the same
   thing is the command `/update-cms rl`.

3. **Check what it wrote.** This is your part and the reason the role exists. Read the
   notes against the slides. Work through a few cards and at least one solution by hand.
   An assistant writes mistakes as confidently as it writes everything else. To see every
   line that is new or changed:

   ```
   git diff
   ```

   (Press `q` to leave that view.)

4. **Pack it.**

   ```
   uv run tools/pack.py rl
   ```

   It checks the course once more and writes one file into the folder `out/`, named like
   `rl-<date>-<time>.zip`: your `course.yaml` and `content/`, nothing from `source/`. If
   it says `Not packed`, it lists what is wrong, file by file. Copy that list to your
   assistant, let it fix the files, and pack again.

5. **Hand it in.** On the site: **Educators**, open your course, choose that zip, press
   **Hand in**. The site checks it in full. If it passes it is live at once and becomes a
   step in the course's history there. If it removes or rewrites anything, the site first
   shows you what, and takes it in when you tick the box and hand it in again.

6. **Note it down, on your computer.** Your copy and the site now agree. Tell git that
   this is your new starting point. Two lines:

   ```
   git add -A courses/rl
   git commit -m "rl: handed in"
   ```

   This uploads nothing; the hand-in in step 5 was the only upload there is. It is a
   bookmark in your own copy, so that the next `git diff` shows only what you do from
   here on.

## Git here is local: a commit is not an upload

Above you met `git commit`, and below you will meet `git stash`. **Neither sends anything
anywhere.** A commit is git remembering a version inside your own copy of the kit, on your
computer. Uploading would be `git push`, which you switched off in the set-up, and which
this repository would refuse anyway: only its owner can write to it.

Your course reaches the site in exactly one way: the zip you hand in there.

So why use git at all? It does two jobs well. `git diff` shows precisely what you, or
your assistant, changed. And when someone else has changed your course in the meantime,
git can put your work on top of theirs.

The rule for git in this folder is simple: **a commit is a bookmark for a version the
site has.** `tools/unpack.py` makes one when you bring the site's version in; you make one
after a hand-in was taken in. Work that is not handed in yet stays uncommitted, which is
exactly what `git diff` shows and what `git stash` can set aside.

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
your course's page there each step has **Download the course as it was after this step**;
to go back to it, unpack that zip and hand it in. Your own newest hand-in can simply be
taken back there. And your own copy has every version in git.

**Not what is the owner's.** In `course.yaml` the `topics` and the `description` are
yours. Title, code, year and whether the course is open are not, and a topic's id stays
as it is.

## If the site says the course has changed

Another educator of your course handed something in, or the owner published a change,
after you took your copy. Taking your zip in would undo their work, so it is refused. The
site tells you when that happens: under the bell, and on your course's page under
**Your copy**. Put your work on top of the latest version. Download the course files
again on the site, then type these four lines, one after the other:

```
git stash
uv run tools/unpack.py ~/Downloads/rl.zip
git stash pop
uv run tools/pack.py rl
```

The first sets your work aside, the second brings in the site's version, the third puts
your work back on top, the fourth checks and packs again.

Usually git fits the two together by itself. Where both changed the same place it marks
the file: both versions are in it between `<<<<<<<` and `>>>>>>>`. The easy way out is to
tell your assistant: *Resolve the merge conflicts in courses/rl. Keep what the site has
unless my change replaces it.* Then pack and hand in the new zip.

## The check

```
uv run tools/check.py rl
uv run tools/check.py --status rl
```

The first checks the structure of your files with the site's own code. The second also
lists what in `source/` has not been written up yet. Links between files and maths are
checked by the site itself when you hand in; if it finds something, it shows you the
report to give to your assistant.

Without uv: `pip install pyyaml pydantic`, then `python tools/check.py rl`.

## When something goes wrong

| What you see | What to do |
|---|---|
| `git` or `uv`: "not found", "not recognized" | Close the terminal and open a new one. Still there: install that program again (set-up, part A). |
| "there is no such file" for the zip | Type the command up to the file name, then drag the zip into the terminal window. |
| "there is no course folder courses/rl" | You are not in the kit's folder, or the course is not unpacked yet. Go into `dsai-educator-kit`, then run `tools/unpack.py`. |
| `unpack.py` says a folder "has work that is not committed" | You have work that was not handed in. Follow [If the site says the course has changed](#if-the-site-says-the-course-has-changed). |
| `pack.py` says `Not packed` | It lists the files and lines. Give that list to your assistant, let it fix them, pack again. |
| The site refuses a hand-in | The page says why, in the same file-and-line form. Give it to your assistant. If it says the course has changed, see that section above. |
| The site shows what a hand-in removes | Read the list. If you meant it, tick the box and hand in again. If not, your assistant removed something it should not have: ask it to put it back. |
| Stuck in a screen full of text after `git diff` | Press `q`. |

Anything else: **Ask or report** on the site, or ask your assistant. It can read this file.

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
