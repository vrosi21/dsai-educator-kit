---
title: Gradient descent
number: 2
date: 2026-10-12
topics: [gd]
summary: Reach the least-squares minimum by repeatedly stepping against the gradient, and see what the learning rate does.
takeaways:
  # A colon followed by a space needs quotes. Single quotes keep backslashes literal.
  - 'One step: $w \leftarrow w - \eta\, \nabla L(w)$.'
  - For the mean squared loss the gradient is $\frac{2}{n} X^\top (Xw - y)$.
  - Too large a learning rate diverges; too small a one crawls.
status: complete
---

## The idea

The gradient $\nabla L(w)$ points in the direction in which $L$ grows fastest. Moving a
small distance the other way must reduce the loss, as long as the step is small enough:

$$w^{(t+1)} = w^{(t)} - \eta\, \nabla L\big(w^{(t)}\big).$$

The step size $\eta > 0$ is the **learning rate**. Nothing here is specific to lines: the
same loop trains any model whose loss has a gradient.

## Gradient of the least-squares loss

With the mean squared loss $L(w) = \frac{1}{n} \lVert y - Xw \rVert^2$,

$$\nabla L(w) = \frac{2}{n} X^\top (Xw - y).$$

:::tip
$Xw - y$ is just minus the residual vector. Compute it once per step and reuse it for both
the loss and the gradient.
:::

## One step by hand

Take the data of [](lecture:01-least-squares): rows $(1,0)$, $(1,1)$, $(1,2)$ and
$y = (1, 3, 5)^\top$. Start at $w^{(0)} = (0, 0)^\top$ with $\eta = 0.1$.

:::example
$Xw^{(0)} - y = (-1, -3, -5)^\top$, so

$$\nabla L = \tfrac{2}{3} X^\top (Xw - y) = \tfrac{2}{3} \begin{pmatrix} -9 \\ -13 \end{pmatrix} = \begin{pmatrix} -6 \\ -26/3 \end{pmatrix},$$

and the first step lands on

$$w^{(1)} = \begin{pmatrix} 0 \\ 0 \end{pmatrix} - 0.1 \begin{pmatrix} -6 \\ -26/3 \end{pmatrix} = \begin{pmatrix} 0.6 \\ 0.867 \end{pmatrix}.$$

Both parameters moved towards the true values $(1, 2)$.
:::

## Choosing the learning rate

For this loss the Hessian is the constant matrix $H = \frac{2}{n} X^\top X$. Gradient descent
converges for every starting point exactly when

$$0 < \eta < \frac{2}{\lambda_{\max}(H)} .$$

:::warning
Above that bound each step overshoots by more than it corrects and the loss grows without
limit. A loss that rises from one iteration to the next means the rate is too large.
:::

## In code

```python
def gradient_descent(X, y, eta=0.1, steps=500):
    n, d = X.shape
    w = np.zeros(d)
    for _ in range(steps):
        residual = X @ w - y
        w -= eta * (2 / n) * (X.T @ residual)
    return w
```

On the three points above this returns $(1.000, 2.000)$ to three decimals after 500 steps.

:::recall Why can gradient descent not get stuck in a bad local minimum here?
The least-squares loss is convex: it has no local minima other than the global one.
:::

Compare the two approaches in [](guide:choosing-a-method).
