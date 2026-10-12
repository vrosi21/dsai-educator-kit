# Memory: hooks and palaces

Aids for the things that will not stay put: which term goes in the denominator, the order of
six steps, a list of conditions. They are scaffolding. The student uses them to get the real
thing out under pressure, then writes the real thing.

Write them sparingly, and only for material that is genuinely hard to hold. A hook for
something obvious is noise.

## Hooks

A hook is a mnemonic. There are two places to write one.

**On a flashcard**, when it helps recall that card's answer:

```yaml
  - id: lsq-normal
    q: |-
      State the normal equations.
    a: |-
      $$X^\top X\, w = X^\top y$$
    hook: |-
      Hit both sides with $X^\top$.
```

It is shown after the answer is revealed, and it appears on the course's Memory page as
well. Do not repeat it in `hooks.yaml`.

**In `content/memory/hooks.yaml`**, when it is not tied to one card. Fields:
[fields.md#hooks](fields.md#hooks). Example:
[hooks.yaml](../example-course/example/content/memory/hooks.yaml).

```yaml
hooks:
  - id: h-singular
    for: What makes the normal equations singular
    kind: acronym
    topic: lsq
    hook: |-
      **DFC**: Duplicate, Fewer, Constant.
    explain: |-
      A **D**uplicated feature column, **F**ewer data points than parameters, or a
      **C**onstant feature beside the intercept.
    refs: ["card:lsq-unique"]
```

- **`for`** names what the hook brings back. On the Memory page the student can cover this
  side, read the hook, and try to say what it stands for.
- **`hook`** is the mnemonic itself: short enough to recall whole.
- **`explain`** maps each piece of the hook onto the real thing. Without it a hook is a
  riddle.
- **`kind`** names the technique:

| `kind` | What it is | Good for |
|---|---|---|
| `phrase` | A short saying that encodes the shape of a result | Which way a ratio points, where a term sits |
| `acronym` | Initial letters | Short unordered lists |
| `image` | One vivid picture | A single relationship or contrast |
| `story` | A few linked events | Short ordered sequences, cause and effect |
| `rhyme` | Rhyme or rhythm | Rules with a fixed wording |
| `peg` | Items hung on a known sequence (one-bun, two-shoe) | Numbered lists |

What makes a good hook:

- It encodes **structure**, not content: which symbol is squared, which side the transpose
  is on, what order the passes go in.
- It is specific to the thing. "Remember the formula carefully" is not a hook.
- It is concrete and a little odd. Odd is memorable.
- It is true. A hook that misleads in an edge case does more harm than none.

## Memory palaces

A palace stores an **ordered** list along a route the student knows well: one stop per item,
one vivid scene per stop. Use it for procedures and fixed sequences of four to ten items.
For single facts, use flashcards.

File: `content/memory/palaces/<name>.yaml`. Fields: [fields.md#palace](fields.md#palace).
Example: [gd-loop.yaml](../example-course/example/content/memory/palaces/gd-loop.yaml).

```yaml
title: One gradient-descent step, on the way to class
topic: gd
encodes: |-
  The four things that happen, in order, in every iteration of gradient descent.
intro: |-
  The route is the walk from your front door to the lecture hall.

loci:
  - id: door
    place: Front door
    image: |-
      The door is plastered with a giant sticky note showing your current guess, the
      numbers of $w$ dripping wet ink.
    means: |-
      **Start from the current parameters** $w^{(t)}$.
  - id: bus-stop
    place: Bus stop
    image: |-
      Every passenger holds up a card with how late the bus is for *them*.
    means: |-
      **Compute the residual term** $Xw - y$.
    refs: ["term:g-residual"]
```

On the page the student first sees the whole route, then walks it from memory: at each stop
they recall the image, then what it means, then grade themselves.

- **Route:** generic places everyone has (front door, stairs, bus stop, a bridge, the
  lecture hall), in an order that could really be walked. The student will map them onto
  their own. Describe the route once in `intro`.
- **`place`** is two or three words.
- **`image`** is a scene, not a label: something happening, exaggerated, involving the
  senses, and connected to the idea by a visible link (the tilting bridge is the gradient).
  One or two sentences.
- **`means`** states the item exactly, with the formula if there is one. Start with the
  item in bold.
- **One item per stop.** If an item needs two scenes it is two items.
- Stop ids need only be unique within the palace.
- `refs` link a stop to the card, formula or term it stands for.
