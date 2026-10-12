---
title: Cheat sheet
summary: Everything from both lectures on one printable page.
---

## Least squares

- Model $\hat y = Xw$, loss $L(w) = \lVert y - Xw \rVert^2$.
- Minimiser solves $X^\top X\, w = X^\top y$.
- Unique when the columns of $X$ are independent.
- Residuals satisfy $X^\top r = 0$; with an intercept, $\sum_i r_i = 0$.

## Gradient descent

- Step $w \leftarrow w - \eta\, \nabla L(w)$.
- Mean squared loss: $\nabla L(w) = \frac{2}{n} X^\top (Xw - y)$.
- Converges for $0 < \eta < 2 / \lambda_{\max}(H)$.

## Choosing

| Situation | Use |
|---|---|
| Fits in memory, linear model | Normal equations (`np.linalg.lstsq`) |
| Too large, or not linear | Gradient descent |
