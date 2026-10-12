# Questions: problem sets, past papers, mock exams

All three are lists of questions in the same format. The folder decides what the list is:

| File | What | Opens as |
|---|---|---|
| `content/problems/<set>.yaml` | Practice set | Worked solutions on demand, no clock |
| `content/exams/<exam>/<paper>.yaml` with `kind: past` | A paper that was really set | Study mode; can also be sat |
| `content/exams/<exam>/<paper>.yaml` with `kind: mock` | A paper you assembled | Sit mode: clock, hidden solutions, marking |

Fields: [problem-set](fields.md#problem-set), [paper](fields.md#paper),
[QuestionSpec](fields.md#questionspec). Examples:
[fitting-practice.yaml](../example-course/example/content/problems/fitting-practice.yaml),
[past-2025.yaml](../example-course/example/content/exams/midterm/past-2025.yaml),
[mock-1.yaml](../example-course/example/content/exams/midterm/mock-1.yaml).

A paper must sit in an exam folder that has an `assessment.yaml` (see [exams](exams.md)).

## A problem set

```yaml
title: Fitting practice
instructions: |-
  Work each problem on paper before opening the solution.

questions:
  - id: fit-p1
    title: Normal equations with numbers
    topic: lsq
    points: 10
    q: |-
      Fit $\hat y = w_0 + w_1 x$ to the points $(0, 1)$, $(1, 2)$, $(2, 4)$.
    parts:
      - q: |-
          Write down $X^\top X$ and $X^\top y$.
        points: 3
        solution: |-
          Rows of $X$ are $(1,0)$, $(1,1)$, $(1,2)$, so …
    answer: |-
      $\hat y = \tfrac{5}{6} + \tfrac{3}{2}x$
```

## A paper

```yaml
title: Mock midterm 1
kind: mock               # past | mock
duration: 30             # minutes
marking:
  negative: 0.5          # points lost per wrong choice answer; leave out for none
instructions: |-
  Thirty minutes. A wrong answer to a choice question costs half a point.
questions:
  - …
```

For a past paper add `date:` (when it was sat).

## Question types

`type` defaults to `open`.

**`open`**: worked on paper. It needs at least one of:

- `solution`: the full worked solution;
- `steps`: the solution as a list of `do` / `why` steps, revealed one at a time. Use it for
  procedures the student should be able to reproduce (this is the "drill" format);
- `parts`, each with its own `solution`, for questions with (a), (b), (c);
- `answer`: just the final answer, for short questions.

`answer` can accompany any of the others; it is shown in a "Answer" block and is what the
student checks first.

**`mcq`**: exactly one choice has `correct: true`.

```yaml
  - id: fit-p3
    type: mcq
    points: 2
    q: |-
      Gradient descent is run with a learning rate slightly **above** the bound. What happens?
    choices:
      - text: It converges, only more slowly.
        why: Slow convergence is the symptom of a rate that is too small.
      - text: The loss grows without bound.
        correct: true
```

**`multi`**: one or more choices are correct; the student must select exactly those.

**`tf`**: a statement, with `correct: true` or `correct: false` on the question itself.

`why` on a choice is shown after answering. Write it for the tempting wrong options: it is
where the learning happens.

## Points and marking

- `points` on a question; if it has `parts` with points and no `points` of its own, the
  parts are summed.
- In sit mode, choice questions are marked automatically: full points when right, minus
  `marking.negative` when wrong, zero when left blank. The student then reads each solution
  and awards points on the open questions.
- Give every question of a paper `points`, as on the real paper.

## What makes a good question

- **Shape it like the exam.** If past papers give a covariance matrix and ask for a
  direction, write that, with different numbers.
- **Choose numbers that work out.** Small integers, determinants that divide.
  Solve the problem yourself before writing it down.
- **A solution is a derivation, not a result.** Show every line a marker would expect,
  name the rule used at each step, and end with the answer stated plainly.
- **Say what the result means** when it has a meaning ("so the fitted line passes through
  the mean of the data").
- **One idea per question** in practice sets; papers can combine.
- **Distractors come from real mistakes:** the sign error, the wrong denominator, the
  neighbouring formula. Never use "all of the above".

## Past papers

- Transcribe every question exactly as set, including point values.
- If you are working from a photo or from memory, record that in the question's `source`
  field, and state any assumption ("the matrix in part (b) was illegible; solved with the
  standard pair from lecture 5").
- Write solutions to the standard of a model answer.
- Give each paper its `date`. File name: `past-2025-06.yaml`.

## Mock exams

- Build them only when there is evidence of the real format (a past paper, a stated
  structure). Match its length, section order and marking.
- Draw on the whole scope, weighted like the real paper.
- Do not reuse the past paper's own questions: reuse its shapes with new numbers.

## Ids

Every question id is unique in the whole course, across all sets and papers:
`fit-p1`, `mid25-q1`, `mock1-q3`. Keep them when you edit a question.
