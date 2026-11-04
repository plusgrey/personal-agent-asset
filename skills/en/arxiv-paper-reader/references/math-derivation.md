# Mathematical Derivation Guidelines

Goal: a reader with an undergraduate mathematics background should be able to follow every derivation from beginning to end **without consulting the paper or external references**.

## 1. Establish the Setup Before Deriving

- **Goal**: State exactly what is to be proved or derived as a concrete equation or inequality.
- **Assumptions**: List assumptions used, such as the Markov property, Gaussianity, independent and identically distributed samples, or parameter sharing.
- **Notation**: Define any symbols the paper leaves undefined or that could be confused with one another.

## 2. Justify Every Step

Perform only one kind of transformation per step and put its justification in `\tag{}` or beside/below the equation. Example:

$$
\begin{aligned}
\log p_\theta(x_0)
&= \log \int p_\theta(x_{0:T})\,dx_{1:T}
  && \text{(marginalization)} \\
&= \log \int q(x_{1:T}\mid x_0)\,\frac{p_\theta(x_{0:T})}{q(x_{1:T}\mid x_0)}\,dx_{1:T}
  && \text{(multiply and divide by the same distribution } q\text{)} \\
&= \log \mathbb{E}_{q(x_{1:T}\mid x_0)}\!\left[\frac{p_\theta(x_{0:T})}{q(x_{1:T}\mid x_0)}\right]
  && \text{(definition of expectation)} \\
&\ge \mathbb{E}_{q(x_{1:T}\mid x_0)}\!\left[\log \frac{p_\theta(x_{0:T})}{q(x_{1:T}\mid x_0)}\right]
  && \text{(Jensen's inequality; }\log\text{ is concave)}
\end{aligned}
$$

Common justifications include marginalization, Bayes' rule, the chain rule, the Markov property, linearity of expectation, completing the square, closed forms for products/quotients of Gaussians, treating terms independent of $\theta$ as constants, change of variables (state the transformation and Jacobian), integration by parts, reparameterization, Jensen's inequality, Cauchy–Schwarz, and Tweedie's formula.

## 3. Fill In Omitted Steps

- Whenever the paper says "it is easy to see," "clearly," "after a straightforward calculation," or "it can be shown," **expand the missing steps**.
- Mark reconstructed material with a `> Reconstruction:` blockquote or "(omitted in the paper)" so it is distinguishable from the paper's text.
- If the paper contains a notation error, omits an assumption, or drops a constant, flag it with `> **Caution:**`.

## 4. Secondary Results

**Definition**: A result used as a tool in the derivation but not contributed by the paper, including inequalities, identities, classical lemmas, and distributional properties.
Examples include Jensen's inequality, non-negativity of KL divergence (Gibbs' inequality), the closed-form KL divergence between two Gaussians, Gaussian conjugacy, the reparameterization trick, Tweedie's formula, the Fokker–Planck equation, Girsanov's theorem, calculus of variations, Cauchy–Schwarz, Hölder's inequality, Fenchel duality, and Stein's identity.

**Format**: Insert the following fixed-format block at the **first point of use**:

```markdown
> **Secondary result: Jensen's inequality**
>
> **Statement**: If $f$ is concave, then $f(\mathbb{E}[X]) \ge \mathbb{E}[f(X)]$; the inequality is reversed for a convex function.
> Equality holds if and only if $X$ is almost surely constant or $f$ is linear over the range of $X$.
>
> **Intuition**: A concave function lies above its chords; applying the function after averaging gives a value no smaller than averaging after applying the function.
>
> **Proof sketch**: Take a supporting line of the concave function at $\mu = \mathbb{E}[X]$:
> $f(x) \le f(\mu) + f'(\mu)(x-\mu)$. Taking expectations makes the second term on the right zero.
>
> **Role in this paper**: Because $\log$ is concave, this changes $\log \mathbb{E}_q[\cdot]$ into
> $\mathbb{E}_q[\log \cdot]$, yielding the tractable lower bound called the ELBO. Equality holds exactly when
> $q(x_{1:T}\mid x_0) = p_\theta(x_{1:T}\mid x_0)$, so the gap between the ELBO and the true log-likelihood is precisely a KL divergence.
```

**Requirements**:
- Include all four items: statement, intuition, proof or proof sketch, and role in this paper. The final item must be specific: identify the step and say exactly what is transformed into what.
- Give a complete proof when it is short. For a long proof (such as Girsanov's theorem), provide a proof sketch and a reference.
- Introduce a result only at its first occurrence. At later uses, write, for example, "(by Jensen's inequality from §3.1)."
- If a secondary result itself depends on another result, one nested explanation is acceptable. Do not recurse indefinitely; elementary calculus and linear algebra need no introduction.

## 5. End Each Derivation with a Takeaway

End every derivation block with a **Takeaway** covering:
- The conclusion in one sentence.
- Its role in the method, for example, "This step decomposes the ELBO into $T$ independently optimizable KL terms."
- Any approximation or cost, for example, "Dropping the weighting coefficients is an empirical choice; strictly speaking, the resulting objective is no longer the ELBO."

## 6. Notation and Formatting

- Keep notation consistent throughout; explain any departure from the paper's notation.
- Use `$...$` for inline equations, `$$...$$` for display equations, and `aligned` for multiline derivations.
- Avoid macros supported by only some renderers, such as `\bm` and `\coloneqq`; use `\boldsymbol` and `:=` instead.
