---
title: Fit a line two ways
number: 1
date: 2026-10-14
due: 2026-10-21
topics: [lsq, gd]
summary: Generate noisy points, fit them with the normal equations and with gradient descent, and check the two agree.
---

## Goal

Confirm numerically that gradient descent converges to the closed-form least-squares
solution, and see what happens when the learning rate is too large.

## Task 1: data

Draw 50 points from $y = 1 + 2x + \varepsilon$ with $\varepsilon \sim \mathcal{N}(0, 0.5^2)$.

```python
import numpy as np

rng = np.random.default_rng(0)
x = rng.uniform(0, 4, size=50)
y = 1 + 2 * x + rng.normal(0, 0.5, size=50)
X = np.column_stack([np.ones_like(x), x])   # design matrix: rows (1, x_i)
```

## Task 2: closed form

```python
w_exact, *_ = np.linalg.lstsq(X, y, rcond=None)
```

The result is close to $(1, 2)$ but not equal to it: the noise moves the best-fitting line.

## Task 3: gradient descent

Reuse `gradient_descent` from [](lecture:02-gradient-descent) and compare.

```python
w_gd = gradient_descent(X, y, eta=0.05, steps=2000)
print(np.abs(w_gd - w_exact).max())   # below 1e-10
```

:::warning
With `eta=0.2` the loss explodes on this data. The bound from the lecture is
$\eta < 2 / \lambda_{\max}\!\big(\tfrac{2}{n} X^\top X\big)$, which here is about $0.16$.
:::

## What to hand in

- [x] The two parameter vectors and their largest difference.
- [x] A plot of the loss against the step number for $\eta = 0.01$, $0.05$ and $0.2$.
- [ ] Optional: repeat with a duplicated feature column and explain what `lstsq` returns.
