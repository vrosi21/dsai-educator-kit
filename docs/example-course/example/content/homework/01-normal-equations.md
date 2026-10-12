---
title: Normal equations by hand
number: 1
due: 2026-10-20
topics: [lsq]
summary: Two short exercises on forming and solving the normal equations, with worked solutions.
status: draft
---

## Exercise 1

Fit $\hat y = w_0 + w_1 x$ to the points $(0, 1)$, $(1, 2)$, $(2, 4)$.

:::solution
$X^\top X = \begin{pmatrix} 3 & 3 \\ 3 & 5 \end{pmatrix}$ and
$X^\top y = \begin{pmatrix} 7 \\ 10 \end{pmatrix}$.
Subtracting the equations gives $2 w_1 = 3$, so $w_1 = \tfrac{3}{2}$ and
$w_0 = \tfrac{1}{3}\big(7 - \tfrac{9}{2}\big) = \tfrac{5}{6}$.

**Answer:** $\hat y = \tfrac{5}{6} + \tfrac{3}{2} x$.
:::

## Exercise 2

Show that the residual vector $r = y - Xw^\star$ of a least-squares fit is orthogonal to
every column of $X$.

:::solution
The normal equations say $X^\top X w^\star = X^\top y$, that is
$X^\top (y - X w^\star) = 0$. The left side is $X^\top r$, whose entries are the inner
products of $r$ with the columns of $X$. All of them are zero.

With an intercept column of ones this includes $\sum_i r_i = 0$: the residuals of a
least-squares line always sum to zero.
:::
