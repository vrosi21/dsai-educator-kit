# Decks and flashcards

A deck is one YAML file in `content/decks/`. Fields: [fields.md#deck](fields.md#deck).
Examples: [least-squares.yaml](../example-course/example/content/decks/least-squares.yaml),
[gradient-descent.yaml](../example-course/example/content/decks/gradient-descent.yaml).

One deck per lecture or per topic works well. Name the file after it: `ch5-fisher.yaml`.

```yaml
title: Least squares
topic: lsq                    # every card gets this topic unless it sets its own
lecture: 01-least-squares     # optional: the lecture this deck drills

cards:
  - id: lsq-normal
    hy: true
    q: |-
      State the normal equations.
    a: |-
      $$X^\top X\, w = X^\top y$$
    note: |-
      Solve this system; do not invert $X^\top X$.
    hook: |-
      Hit both sides with $X^\top$.
```

## Three kinds of card

The fields you use decide the kind.

**Basic: `q` + `a`.** A prompt and the answer. Most cards.

**Derivation: `q` + `steps`.** For anything done in a fixed sequence: a proof, a
computation, an algorithm run by hand. Each press reveals one step.

```yaml
  - id: lsq-derive
    q: |-
      Derive the normal equations from the loss $L(w) = \lVert y - Xw \rVert^2$.
    steps:
      - do: |-
          Write the norm as an inner product: $L(w) = (y - Xw)^\top (y - Xw)$.
        why: |-
          $\lVert v \rVert^2 = v^\top v$. This turns the loss into something you can expand.
      - do: |-
          Set the gradient to zero: $X^\top X\, w = X^\top y$.
        why: |-
          $L$ is convex, so a stationary point is a global minimum.
    a: |-
      The result is a square $d \times d$ system, however many data points there are.
```

`do` is what you would write on paper at that step; `why` is the justification a marker
looks for. At least two steps. `a` is optional and shown at the end (a result, a check).

**Cloze: `cloze`.** A sentence with blanks. Good for definitions and statements whose exact
wording matters.

```yaml
  - id: gd-rate
    cloze: |-
      If the learning rate is too {{large}} the iterates {{diverge}}; if it is too
      {{small}} convergence is {{slow}}.
```

Wrap each thing to recall in `{{ }}`. A whole formula can be a blank: `{{$r_i = y_i - \hat y_i$}}`.
A blank cannot start or end inside `$ … $`.

## Fields on any card

- **`id`**: unique in the course, permanent. See [Ids](../AUTHORING.md#ids-are-permanent).
- **`a`**: the answer as you would write it in the exam. It is shown in a block labelled
  "Write this". Keep explanation out of it.
- **`note`**: everything else: why it is true, when it applies, the trap. Shown under the
  answer.
- **`hook`**: a mnemonic for this card. It also appears on the course's Memory page.
- **`hy: true`**: high-yield. Reserve it for what is very likely examined (it was on a past
  paper, the lecturer said so). If more than a third of a deck is marked, the mark means
  nothing.
- **`topic`**: only when a card belongs to a different topic than its deck.

## What makes a good card

- **One thing per card.** If the answer has three independent parts, write three cards, or
  one cloze with three blanks. A card you can only half-answer cannot be graded honestly.
- **The prompt must be answerable aloud.** "Fisher's criterion" is not a prompt.
  "State Fisher's criterion and say what each term measures" is.
- **Ask for what the exam asks for:** state, derive, compute, compare, explain why, spot the
  error. Check the past papers for the verbs.
- **Answers are short and exact.** A formula, a sentence, a short list. If it runs past five
  lines it is a derivation (`steps`) or belongs in the notes.
- **Cover the why, not only the what.** For each key result, a second card asking why it
  holds or when it fails.
- **Compute something.** In a mathematical course at least a quarter of the cards should
  make the student produce a number or an expression.
- **No trivia, no trick questions, no "which slide said…".**

A lecture usually yields 8 to 20 cards. Order them as a learner should meet them: definitions
before the results that use them.

## Changing a deck later

Edit a card's text freely; keep its `id`. Add new cards with new ids. Delete cards that are
wrong. Do not renumber or "tidy" ids: the student's grades are stored under them.
