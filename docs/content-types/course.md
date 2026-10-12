# course.yaml

One per course, at the top of the course's folder (`courses/<course>/course.yaml`, or
`courses/semester-5/<course>/course.yaml` where courses are grouped by semester). It
names the course and lists its topics.
Fields: [fields.md#course](fields.md#course). Example:
[example-course/example/course.yaml](../example-course/example/course.yaml).

```yaml
title: Reinforcement Learning
code: RL
year: "2026-27"          # quoted: an unquoted 2026-27 is fine too, but a bare 2026 is a number
# series: rl             # only for another year of an existing course, see below
semester: 5              # semester of the programme, 1-12 | leave out
status: active           # active | archived (a finished course)
enabled: true            # false: hidden from students until it is opened in the admin
has_educator: false      # true: someone is writing it
hue: 150                 # the course's colour, 0-359 on the hue wheel
order: 4                 # position among courses of the same semester
description: Markov decision processes, dynamic programming, TD learning and policy gradients.

topics:
  - id: mdp
    title: Markov decision processes
    short: MDPs
  - id: dp
    title: Dynamic programming
```

## Where the course shows on the dashboard

The dashboard has one section per semester of the programme, titled the way the
faculty writes it (`semester: 5` is shown as Semester V). Sections that still hold an
active course come first, the latest semester on top; a semester whose courses are
all archived follows.

- A course **without** `semester` is listed under its `year` while it is active, and
  in the folded Archived section once it is archived.
- `status: archived` means finished. The course stays readable in its semester, but
  Next up stops suggesting it and the landing page does not list it.
- `order` sorts courses inside a section.

## Open or closed, and who writes it

Two fields say where a course stands. Both are starting points: the person who runs the
site can switch either one in the admin, and a switch set there wins over the file until
it is cleared.

- `enabled: false` keeps the course out of sight: it is not on the dashboard, not in the
  list to choose from, not in search, and its address answers "no such page". Use it for
  a course nobody has reached yet. Left out, a course is open.
- `has_educator: true` says someone is writing the course. It only matters while the
  course has no content: its page then says the content is on its way. With
  `has_educator: false` (or left out) the page says nobody is writing it yet and offers
  to apply to become its educator. Once an application is accepted the page stops
  asking, whatever the file says.

Do not change either field as part of writing content. They are decisions of the person
who runs the site.

## Another year of the same course

One folder is one course in one academic year. When a course is taught again and its
material changes, do not overwrite the old folder: people's progress is tied to it.
Create a second folder and tell it which course it continues:

```
manage.py startcourse mlpr-2026 --title "Machine Learning and Pattern Recognition" \
    --code MLPR --year 2026-27 --semester 4 --series mlpr
```

which writes `series: mlpr` into the new `course.yaml`. `series` is the name of the
first year's folder; that folder itself needs no change.

- The dashboard and the navigation show one entry for the course and open the
  **latest** year (`year` decides, so write it the same way everywhere: `"2026-27"`).
- The course page shows every year at the top, newest first, and switches between
  them. A course with one year shows that one.
- Each year has its own ids, its own content and its own progress. Nothing is shared
  or copied between years; copy the files you want to keep and edit them.

## Topics

Topics are the backbone of a course. Lectures, cards, questions, formula sections, glossary
terms, hooks and palaces point at topic ids, and an exam's scope is a set of topics.

- **Order** them as they are taught. The order is used wherever topics are listed.
- **Granularity:** a topic is a chapter or a week, not a single idea. Aim for 5 to 12.
  If the course follows a textbook, its chapters are usually the right topics.
- **`short`** is an optional label for chips where the full title is too long.
- **Ids are permanent.** Choose something that will still be right if the title is reworded:
  `mdp`, `ch5`, `week3`.

Add topics as the course progresses. An id must exist here before anything refers to it.

## Colour

`hue` is the only styling a course has; the whole palette (surfaces, chips, the course card)
is computed from it. Keep courses of the same year at least 40 apart so they are easy to
tell apart: 25 red, 60 amber, 100 lime, 150 green, 200 teal, 240 blue, 285 violet, 330 pink.
