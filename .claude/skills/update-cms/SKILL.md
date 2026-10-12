---
name: update-cms
description: Write new content for one DSAI Vault course from the raw material in its source folder. Use when asked to "update the CMS for this course", to write up a lecture, or to make cards, problems or exam prep for a course in courses/.
---

# Update the CMS for a course

The course to work on is given with the command (`/update-cms rl`) or in the request. Its
folder is `courses/<course>/` in this repository. If no course was named and `courses/`
holds exactly one, use that one; otherwise ask which.

Follow `AGENTS.md` at the top of this repository, all of it: the rules that are never
broken, then the procedure, step by step. In short:

1. Read `docs/AUTHORING.md`, and the pages under `docs/content-types/` you need.
2. `uv run tools/check.py --status <course>` for the list of what is not written up yet.
3. Read the sources completely.
4. Add files, and add lines to files, under the course's `content/` only. Never delete,
   reword or reorder a line that is already committed: the site takes additions only.
5. `uv run tools/check.py <course>` until the structure is valid, and
   `git diff --stat -- courses/<course>` shows insertions only.
6. Report: what you wrote, what you could not read, what is not from the source, what on
   the site you think is wrong, what to check first.

Do not commit, pack or hand in unless asked. Never push.
