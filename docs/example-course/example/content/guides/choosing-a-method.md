---
title: Closed form or gradient descent?
topics: [lsq, gd]
summary: When to solve the normal equations directly and when to iterate. A guide cuts across lectures; this one compares lectures 1 and 2.
---

## Short answer

Use the closed form whenever the problem fits in memory. Iterate when it does not, or when
the model is not linear in its parameters and no closed form exists.

## Side by side

| | Normal equations | Gradient descent |
|---|---|---|
| Result | Exact in one solve | Approximate, improves each step |
| Cost | About $n d^2 + d^3$ | About $n d$ per step |
| Tuning | None | Learning rate, number of steps |
| Breaks when | $X^\top X$ is singular | Rate above $2 / \lambda_{\max}(H)$ |
| Generalises to | Linear models only | Any differentiable loss |

Here $n$ is the number of data points and $d$ the number of parameters.

## How an exam asks this

:::paper
"Compare" questions want both sides and a condition. A complete answer names the cost of
each method, says when each fails, and ends with a rule for choosing.
:::

Terms used above: [](term:g-design-matrix), [](term:g-learning-rate). The formulas are
collected on [the sheet](formulas).
