# A linear law is frozen everywhere or nowhere

Status: Proved

Ticket `FROZEN-WORLDS-20261020-001B`, 2026-10-20. It builds on
`HOLES-AT-INFINITY-20261020-001C-P001` (Theorem 2: every open parity of a
linear law is loop-supplied or end-supplied).

## Standard statement

Take a countable system of linear equations over GF(2), each on finitely many
variables, with each variable in finitely many equations.

1. Whether some solution can be changed in finitely many variables so as to
   change a given parity does not depend on the solution. It holds exactly
   when a finitely supported solution of the homogeneous system changes that
   parity.
2. Let F be a finite set of at least three variables. The projection of the
   solutions onto F is constrained as a whole but unconstrained after
   forgetting any one variable exactly when:
   - the parity of F is constant on the solutions; and
   - no proper nonempty subset of F has constant parity.
3. Take a translation-invariant system on Z^d with n variables per site,
   written as a matrix over the Laurent polynomial ring
   R = F₂[u₁^{±1}, …, u_d^{±1}]. Three conditions are equivalent:
   - finitely supported homogeneous solutions exist;
   - the matrix has rank below n over the field of fractions;
   - the solution space has positive topological entropy.

## Nearest known results

- **Algebraic dynamics.**
  - Schmidt, *Dynamical Systems of Algebraic Origin* (1995).
  - Kitchens and Schmidt on Markov subgroups of (Z/2)^{Z²}.
  - Lind and Schmidt, *Homoclinic points of algebraic Z^d-actions* (1999):
    for expansive actions, homoclinic points exist exactly when the entropy is
    positive.
  - Lind, Schmidt and Ward (1990) on entropy.
  - Ledrappier's example (1978).
- **Coding theory.** The minimal supports of the dual code are the circuits
  of the dual matroid.

**Classification: known with a delta.**
- Statements 1 and 3 are classical in substance, and statement 2 is the
  standard description of minimal dual codewords.
- The delta is the reading through K1–K3 and the source-aware reading: which
  laws have knots, which of those knots are native, and that this is decided
  by the law and not by the world.

## Setting

- **The law.** A linear law Φ is a system Σ_{v∈S_j} x_v = b_j over GF(2), with
  finite S_j and each variable in finitely many S_j.
  - K is the homogeneous solution group, and K_fin its finitely supported
    elements: the law's finite moves.
  - Sol = x₀ + K, assumed nonempty.
- **Worlds and nativity.** A world is a solution. A parity p_F is native at a
  world s if some solution s′, differing from s in finitely many variables,
  has p_F(s′) ≠ p_F(s).
- **Knots.**
  - Under the source-aware reading
    (`research/HOLES-AT-INFINITY-20261020-001/canonical_correction_request.md`,
    reading B), a K1–K3 knot on F is native at s when each variable of F is
    native at s.
  - A parity is fixed if it is constant on Sol.

## Statements

**Theorem 1 (nativity is the same at every world).** p_F is native at s if
and only if some k ∈ K_fin has p_F(k) = 1. This does not depend on s. So a
linear law is either frozen at every world (K_fin = 0), or has the same finite
moves at every world.

**Theorem 2 (the knots of a linear law).** Let F be finite with |F| ≥ 3.
- The projection R_F of Sol onto F passes K1–K3 (with any variable as
  contact) if and only if p_F is fixed and no p_G with ∅ ≠ G ⊊ F is fixed. In
  that case R_F is the hyperplane p_F = constant.
- Such a knot is native, at every world by Theorem 1, if and only if every
  variable of F lies in the support of some finite move.
- In particular, a frozen law has no native knot, however many knots the
  relation-level test finds.

**Theorem 3 (native loops, rank and entropy on Z^d).** Let a law on Z^d have
n variable types per site and m equation types, written as a matrix A ∈ R^{m×n}.
The following are equivalent:
1. K_fin ≠ 0: the law has native loops;
2. rank A < n over Frac(R);
3. the topological entropy h(K) is positive (and so is h(Sol) when Sol is
   nonempty).

If they fail, the law is frozen at every world.

**Examples on Z².** All four laws are computed by `check.py`.

| Law | Types | Equations | Rank | Finite moves | Entropy | Knots near the origin (K1–K3) | Native knots |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tseitin: vertex parity on edges | 2 | 1 | 1 | yes: unit squares | positive | 13 (vertex stars and other minimal cuts) | all 13 |
| Gauge: plaquette parity on edges | 2 | 1 | 1 | yes: vertex stars | positive | 13 | all 13 |
| Ledrappier: triangle parity on sites | 1 | 1 | 1 | none | zero | 12 (triangles and others) | none |
| Tseitin and gauge together | 2 | 2 | 2 | none | zero | 97 | none |

Each of Tseitin's and the gauge law's finite moves violates the other's
equations, so together they are frozen. A finite edge set that is both a cycle
and a cocycle of Z² is empty.

## Proofs

**Proof of Theorem 1.**
- If s and s′ are solutions differing in finitely many variables, then
  s′ − s ∈ K_fin.
- Conversely, s + k is a solution for every k ∈ K_fin.
- p_F(s′) − p_F(s) = p_F(s′ − s). ∎

**Proof of Theorem 2.**
- **R_F is the hyperplane.** R_F is an affine subspace of GF(2)^F.
  - K2 makes every projection that forgets one variable full, so
    dim R_F ≥ |F| − 1.
  - K1 makes R_F proper, so R_F is a hyperplane {p_G = c} for a unique nonempty
    G ⊆ F.
  - If G ≠ F, forgetting a variable outside G leaves that constraint, against
    K2. So G = F: p_F is fixed.
  - Every other fixed parity on F would cut R_F further. So no proper nonempty
    subset of F has a fixed parity.
- **The converse.** Suppose p_F is fixed and no proper nonempty subset of F
  has a fixed parity.
  - The functionals constant on R_F are then exactly 0 and p_F, so R_F is that
    hyperplane, and K1 and K3 hold.
  - A projection forgetting v has no non-zero constant functional, since any
    such functional would be a fixed parity on a proper subset. So it is full,
    and K2 holds.
- **Nativity** is Theorem 1 applied to each single variable. ∎

**Proof of Theorem 3.** Identify finitely supported configurations with R^n.
Applying the law to them is multiplication by a matrix Ã over R; Ã is A with
the exponents of each entry negated, which has the same rank.

- **1 ⟺ 2.** K_fin = ker Ã on R^n. A non-zero kernel vector over Frac(R)
  becomes one over R after clearing denominators.
- **2 ⟹ 3.**
  - Take a non-zero g ∈ K_fin, and let k exceed the diameter of its support.
  - The translates of g by kZ^d have disjoint supports, and every finite sum of
    them lies in K.
  - So the projection of K onto a box of side N has at least
    2^{(⌊N/k⌋−1)^d} elements, and h(K) ≥ k^{−d} > 0.
- **3 ⟹ 2.** We prove the contrapositive.
  - **Reduction to one equation.** If rank A = n, choose n rows whose minor
    δ = det M is non-zero. Then adj(M)·M = δ·I as operators on all
    configurations, since polynomial operators compose. So every x ∈ K has
    δ·x_i = 0 for each type i.
  - **The equation δ·y = 0 has zero entropy.**
    - Choose an integer linear functional ℓ that is injective on the finite
      support of δ, with ℓ-largest point a*.
    - The equation at each site expresses y(q) as the sum of y at the points
      q − a* + a, for a in the support with a ≠ a*. All of these have smaller ℓ
      and lie within distance D = diam supp δ of q.
    - So y on a box B_N is determined by y on the shell B_{N+D} ∖ B_N, which
      has O(D·N^{d−1}) sites.
    - The number of patterns on B_N is therefore 2^{O(N^{d−1})}, and
      h(X_δ) = 0.
  - **Conclusion.** h(K) ≤ n·h(X_δ) = 0, and Sol, a coset of K, has the same
    entropy. ∎

**The combined law is frozen.**
- Let x be finite, with even degree at every vertex and even around every unit
  square. Since H¹(Z²; F₂) = 0, the second condition makes x the coboundary δf
  of a vertex function f.
- f is constant off a finite set, and we may take that constant to be 0. The
  first condition then says that every vertex has an even number of
  neighbours where f = 1.
- At the top row of the support of f, a vertex just above a support vertex w
  has exactly one such neighbour, namely w. Its other neighbours lie above,
  beside or below it and are outside the support. That contradicts evenness,
  so f = 0.
- This agrees with rank 2 = n in Theorem 3.

## Checks

`check.py` rewrites `result.json` and replays it. It covers eleven laws on Z²:
- the four above;
- the gauge law with a shifted copy of its equation, a control with rank 1 and
  two equations;
- six seeded random laws.

The results:
- **Generic rank.** The modulus x³¹ + x³ + 1 is verified to be irreducible.
  Ranks were computed at five random points of GF(2^31) each.
- **Rank against finite moves.** The rank deficit equals the existence of
  finite moves in boxes of radius 3 and 4, for all eleven laws:
  - with a deficit, 15–16 moves at radius 3 and 35–36 at radius 4;
  - without one, none.
- **Entropy on boxes of radius 2, 3 and 4.**
  - With a deficit, the lower bound from finite moves grows quadratically
    (16, 36, 64).
  - Without one, there are no finite moves, and the upper bound grows linearly,
    for example 9, 13, 17 for Ledrappier.
- **Knots.** Every subset of the variables in the 3×3 window was checked.
  - knotlab accepted every minimal fixed support it checked: 13, 13, 12 and 40
    of the 97.
  - It rejected all 17 non-minimal fixed supports checked.
  - Native knots: all 13 for Tseitin and for the gauge law; none for Ledrappier
    or the combined law.
- **World-independence.** Which window variables a change inside the box can
  flip was solved separately at two random worlds for each of five laws, with
  identical answers.

**Controls**, each rejected:
- the generic rank evaluated at u = v = 1, where the combined law's entries
  vanish: rank 0, which contradicts its lack of finite moves;
- nativity read from boundary-supported solutions: 12 spurious native knots
  for Ledrappier;
- the same world-independence procedure on a non-linear law, 3-colourings of a
  5×5 box: the centre can be flipped at the flat world but not at the plane
  world.

## What this does not show

- **Classical substance.** Statements 1 and 3 are classical, and 2 is
  standard. The contribution is the reading: under the source-aware reading,
  linear laws split into those whose knots are native at every world and
  frozen laws whose knots never are. The source-blind reading cannot tell them
  apart.
- **Non-linear laws** are not covered. There nativity can depend on the world
  (ticket C).
- **Nothing here is spatial or metric.** Entropy measures how many solutions
  there are, not space.
