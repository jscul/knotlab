# Star knots stop being native at the freezing threshold of the tree

Status: Proved

Ticket `FREEZING-KNOTS-20261020-001B`, 2026-10-20. It uses the experiment
`FREEZING-KNOTS-20261020-001A-E001` ("A" below), which calibrates finite
planted graphs against the tree. It applies the source-aware reading adopted
on 2026-10-20 (`docs/FOUNDATIONAL_THESIS.md`, "Source condition for infinite
systems").

## Standard statement

Colour the d-regular tree with q colours by the broadcast process. The root
gets a uniform colour. Each child gets a uniform colour among the q − 1
colours that differ from its parent's.

The broadcast colouring is the uniform proper colouring of every finite
subtree. It is also the local limit of planted colourings of random d-regular
graphs. Call a vertex **frozen** if no proper colouring that differs from the
broadcast colouring at finitely many vertices recolours it. We show:

1. **Frozen branches.** A vertex is frozen exactly when, for every other
   colour, some neighbour of that colour is frozen within its own branch. A
   branch freezes its root with probability p*, the largest fixed point in
   [0, 1] of an explicit polynomial Φ.
2. **The star relation.** On q neighbours of a vertex, the relation over all
   proper colourings is "not all q colours used". It is constrained as a
   whole, yet unconstrained once any one neighbour is forgotten, at every
   degree d ≥ q.
3. **Nativity.** All q of those neighbours can be recoloured by finite changes
   with probability (1 − p*)^q (1 − ζ) + (1 − μ)^q ζ, with explicit μ and ζ.
   This equals 1 exactly when p* = 0.
4. **Thresholds.** p* = 0 for d below 6, 10 and 15 when q = 3, 4 and 5. At
   those degrees, p* ≥ 449/500, 427/500 and 219/250, and the probability in 3
   is below 0.0011, 0.00046 and 0.00003.

## Nearest known results

- **The frozen-field recursion.** This is the hard-field, or warning
  propagation, recursion of the cavity method. It locates freezing (rigidity,
  naive reconstruction) of colourings on trees and random graphs: Mézard and
  Montanari, *Information, Physics, and Computation*; Semerjian (2008);
  Zdeborová and Krzakala (2007).
- **Frozen vertices of typical colourings.** Molloy proved the freezing
  threshold for k ≥ 14 colours on Erdős–Rényi graphs. Achlioptas and
  Coja-Oghlan proved rigidity for large k.
- **Local convergence of planted models** to the broadcast colouring (standard;
  calibrated here by A).

**Classification: known with a delta.**
- Theorem 1 is the classical recursion.
- The thresholds in Theorem 4 are its naive-reconstruction values on regular
  trees. I did not compare them against a published table.
- The delta is the star-knot reading:
  - Theorem 2 shows the source-blind knot exists at every degree.
  - Theorem 3 gives its nativity formula.
  - Theorem 4 bounds that nativity at the threshold.

## Setting

- **The tree and its colouring.** T_d is the d-regular tree, q ≥ 3 colours,
  and σ is the broadcast colouring. For a vertex v and a neighbour w, the
  **branch** of w is the component of T_d − v that contains w.
- **Frozen within a branch.** w is frozen within its branch if no proper
  colouring of the branch that differs from σ at finitely many of its vertices
  recolours w. v's colour plays no role here.
- **Coverage polynomials.** C(need, k; p) is the probability that k children,
  each frozen with probability p and coloured uniformly among q − 1 colours,
  cover `need` given colours:

  C(need, k; p) = Σ_{j=0}^{need} (−1)^j C(need, j) (1 − j p/(q − 1))^k.

  Then:
  - Φ(p) = C(q − 1, d − 1; p);
  - Ψ(p) = C(q − 1, d; p);
  - μ = C(q − 2, d − 1; p*);
  - ζ = C(q − 1, d − q; p*), with ζ = 0 when d − q < q − 1.
- **The star knot.** Take q neighbours a₁, …, a_q of a vertex z. Under the
  source-aware reading, the star knot on them is **native** at σ when each a_i
  is recoloured by some finite change.

## Statements

**Theorem 1 (frozen branches).**
- **(a)** v is frozen if and only if every colour c ≠ σ(v) is carried by a
  neighbour that is frozen within its branch.
- **(b)** The same holds within a branch, with the root's children in place of
  the neighbours.
- **(c)** Let p_L be the probability that a branch root is forced by the colours
  at depth L below it, with p_0 = 1. Then p_L = Φ(p_{L−1}), and p_L decreases
  to p*, the largest fixed point of Φ in [0, 1].
  - A branch root is frozen with probability p*.
  - A vertex is frozen with probability Ψ(p*).

**Theorem 2 (the star knot exists at every degree).** For d ≥ q, the relation
on q neighbours of a vertex, over all proper colourings of T_d, is "not all q
colours used". It passes K1–K3.

**Theorem 3 (nativity of the star knot).** The star knot is native at σ with
probability

s = (1 − p*)^q (1 − ζ) + (1 − μ)^q ζ.

In particular, s = 1 exactly when p* = 0.

**Theorem 4 (thresholds).** Let d_f(3) = 6, d_f(4) = 10 and d_f(5) = 15.
- For d < d_f(q): p* = 0 and s = 1.
- For d ≥ d_f(q): p* ≥ r_q, with r_3 = 449/500, r_4 = 427/500 and
  r_5 = 219/250, and s ≤ max((1 − r_q)^q, (1 − μ(r_q))^q). That bound is below
  0.0011, 0.00046 and 0.00003 for q = 3, 4 and 5.

At d_f the jump is discontinuous: p* goes from 0 to about 0.90, 0.85 and 0.88.

**Answer to the epic's question.**
- Under the source-aware reading, star knots stop being native exactly at the
  freezing threshold, abruptly.
- The source-blind knot is present at every degree.
- The native-knot threshold is the freezing threshold itself, and s is a
  function of branch freezing. So in the terms of the 2026-10-20
  recommendation, native-knot density restates frozen-variable density.

## Proofs

**Proof of Theorem 1.**
- **(a), "if".** A finite change of T_d restricts, on each branch, to a finite
  proper change of that branch. So the frozen neighbours keep their colours,
  which cover every c ≠ σ(v), and v keeps σ(v).
- **(a), "only if".** Suppose some c ≠ σ(v) is carried by no frozen neighbour.
  - Each neighbour w with σ(w) = c is not frozen within its branch. So a finite
    change of its branch moves w to a colour other than c.
  - Apply these changes; they act on disjoint branches. Then give v colour c.
  - Neighbours that had colour c no longer do, and the other neighbours never
    did. The result is a finite proper change that recolours v.
- **(b)** The same argument, inside the branch.
- **(c) The recursion.** Let F_L(w) be the event that w is forced in its branch
  truncated at depth L, with depth L fixed.
  - **Monotone in depth.** F_{L+1} ⊆ F_L, since a deeper truncation leaves
    more vertices free.
  - **Limit.** Being frozen within the branch is the intersection of the F_L:
    every finite change lies within some depth.
  - **One step.** By (b) applied to the truncation, F_L(w) holds exactly when
    every colour c ≠ σ(w) is carried by a child u with F_{L−1}(u).
  - **Independence.** Under the broadcast law, the pairs (σ(u), F_{L−1}(u)) are
    independent over the children. Each σ(u) is uniform among the q − 1 colours
    other than σ(w). F_{L−1}(u) has probability p_{L−1} and is independent of
    σ(u), because permuting colours preserves the law and the event.
  - **Inclusion and exclusion over the missing colours** gives
    p_L = Φ(p_{L−1}).
- **(c) The limit.**
  - Φ is increasing: by coupling, raising p only adds frozen children.
  - So p_L decreases from p_0 = 1. Its limit is a fixed point, and it bounds
    every fixed point f from above, since p_L ≥ f by induction.
  - Continuity along decreasing events gives probability p* for frozen
    branches. Applying (a) with d neighbours gives Ψ(p*). ∎

**Proof of Theorem 2.**
- **Every tuple occurs.** Any proper colouring of a vertex and some of its
  neighbours extends outward over T_d, because each new vertex has one coloured
  neighbour. A tuple that misses some colour m is realized by giving z colour
  m.
- **No other tuple occurs.** A tuple using all q colours would leave z no
  colour.
- **K1–K3.**
  - K1: the q! tuples that use all colours are excluded.
  - K2: forgetting one neighbour, the other q − 1 miss some colour m. Give z
    colour m and give the forgotten neighbour any other colour.
  - K3: the relation is nonempty. ∎

**Proof of Theorem 3.** Write X_i for the colours of a_i's outer children that
are frozen within their branches.
- **Each member.** By Theorem 1(a) at a_i, a_i is frozen exactly when X_i,
  together with σ(z) whenever z is frozen in its branch away from a_i, covers
  every colour other than σ(a_i). By Theorem 1(b) at z, z is frozen there
  exactly when every colour c ≠ σ(z) is carried by some a_j, j ≠ i, that is
  frozen within its outer branch. Call that event Z_{−i}.
- **Two events per member.**
  - O_i is the event that X_i covers [q] ∖ {σ(a_i)}.
  - M_i is the event that X_i covers [q] ∖ {σ(a_i), σ(z)}.

  Then a_i is frozen exactly when O_i holds, or M_i and Z_{−i} both hold.
- **The star.** If no star member satisfies O_i, then Z_{−i} = Z: the non-star
  neighbours satisfying O_j cover [q] ∖ {σ(z)}. So the star is native exactly
  when every O_i fails and either Z fails or every M_i fails.
- **Probabilities.**
  - The branches are disjoint, and given σ(z) the members' colours are
    independent and uniform.
  - So O_i has probability p* (Theorem 1 with d − 1 children), M_i has
    probability μ, and Z has probability ζ.
  - These events are independent across members and of Z.
  - Since O_i ⊆ M_i, the event "neither O_i nor M_i" has probability 1 − μ.
- **The formula.** Summing over Z and not Z gives s.
- **s = 1 exactly when p* = 0.** If p* = 0, then μ = ζ = 0 (q ≥ 3), so s = 1.
  If p* > 0, then s ≤ 1 − P(O₁) < 1. ∎

**Proof of Theorem 4.**
- **Monotone in d.** Φ_d(p) ≤ Φ_{d+1}(p): by coupling, an extra child only
  adds coverage.
- **Below the threshold.** Φ(0) = 0, so Φ(p) − p = p·h(p) for a polynomial h.
  - For d = d_f − 1, `check.py` certifies h < 0 on [0, 1] with exact Bernstein
    coefficients, subdividing at midpoints where needed.
  - Then Φ(p) < p on (0, 1], so p* = 0. Smaller d follows by monotonicity.
- **At the threshold.** For d = d_f, the rational r_q satisfies
  Φ(r_q) ≥ r_q.
  - By induction p_L ≥ r_q, because Φ is increasing and p_0 = 1. So p* ≥ r_q.
  - Larger d follows by monotonicity.
- **The bound on s.**
  - μ is increasing in p, so μ ≥ μ(r_q).
  - Then s ≤ max((1 − p*)^q, (1 − μ)^q) ≤ max((1 − r_q)^q, (1 − μ(r_q))^q).
  - The right side only decreases as d grows. ∎

## Checks

`check.py` works in exact arithmetic. It rewrites `result.json` and replays
it.
- **Thresholds.**
  - Bernstein certificates of h < 0 hold for (q, d) = (3, 5), (4, 9) and
    (5, 14).
  - Rational witnesses hold at the thresholds: 449/500, 427/500 and 219/250.
  - Monotonicity in d holds on a grid around each threshold.
  - The star bounds are 0.00106, 0.000454 and 0.0000293.
- **Star relation.** It passes K1–K3 for q = 3, 4 and 5, with 21, 232 and 3005
  tuples. Every tuple extends.
- **Formula against A.** The formula reproduces the 21 rows of A's tree table.
- **The jump.** s = 1 below each threshold. At the threshold s = 0.00043,
  0.00022 and 0.000014.

**Controls**, each rejected:
- a witness one degree below the threshold: none exists for any q;
- a certificate of h < 0 at the threshold degree: fails for every q;
- adding the all-colour tuples: K1 fails.

**From A, finite planted graphs.**
- The frozen fractions of vertices and the native fractions of star knots
  match the tree's exact values at every measured radius, within about 0.01.
- In small graphs (n ≤ 36), the star relation over all colourings is the knot
  at degrees 3 and 4. At degree 5 and above it collapses, because those graphs
  have only 6 to 102 colourings.

## What this does not show

- **Planted (broadcast) worlds only.** Nothing is claimed for uniformly random
  colourings of random graphs beyond the regime where they match planted ones.
  For small q these thresholds may lie at or beyond the degree where random
  regular graphs stop being q-colourable.
- **Classical substance.** The recursion and the thresholds are classical. The
  contribution is the knot reading, together with the conclusion that, as a
  threshold, native-knot density restates freezing.
- **No algorithmic or hardness claim.**
