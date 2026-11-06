# The minimal exact towers: the Sierpinski gasket, the slit triangle, and the Fano tower

Status: Proved

Ticket `EXACT-TOWERS-20261029-001B`, 2026-10-29.

## Standard statement

**Setting.**
- **The gadget.** Let G be an exact gadget of a knot K (`EXACT-TOWERS-20261029-001A`):
  - m copies, h hidden variables and factor c;
  - relation R, a placement of K;
  - legs on three distinct copies, pairwise at one distance s.
- **Distance.** Two variables are adjacent when they share a copy.
- **The tower.** T₀ is one copy of R on three *corners*. T_k comes from T_{k−1} by replacing every copy with a copy of G, with fresh
  hidden variables, aligned so that its relation is that copy's constraint.

**Theorem 1 (structure of an exact tower).**
- **(i) Size.** T_k has m^k copies and 3 + h(m^k − 1)/(m − 1) variables.
- **(ii) The law.** The relation of T_k on its corners is R. Every allowed corner tuple has exactly c^((m^k − 1)/(m − 1))
  extensions, and every excluded one has none. So the corner law of a uniformly random solution is uniform on R at every level.
- **(iii) Distances.** For variables u, v of T_{k−1}, their distance in T_k is s times their distance in T_{k−1}. So the corners are
  pairwise at distance s^k. Suppose also:
  - every variable of G is within s of each leg;
  - every copy of G holds a variable within s − 1 of each leg.

  Then every variable of T_k is within s^k of each corner. The ball of radius s^j around a corner then holds exactly
  3 + h(m^j − 1)/(m − 1) variables, so the growth exponent is log m / log s.
- **(iv) Finite ramification.** T_k has a tree decomposition of width h + 2. Every sub-tower is cut off from the rest by its three
  corners.

**Theorem 2 (softening is unstable).** Give every copy weight 1 on its allowed tuples and weight r on its excluded ones.
- Every allowed leg tuple of G gets total weight c + O(r).
- Every excluded one gets at least 3c·r + O(r²).
- So to first order the excluded weight grows at least threefold per level, and the hard law is a repelling fixed point.

**Theorem 3 (the three minimal towers).**

| tower | copies m | hidden h | distance s | factor c | variables of T_k | growth exponent | softened map r ↦ r′ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| parity, triangle | 3 | 3 | 2 | 2 | (3^(k+1) + 3)/2 | log₂ 3 ≈ 1.585 | r(r² + 3)/(3r² + 1) |
| twisted not-all-equal, punctured tetrahedron | 4 | 3 | 2 | 2 | 4^k + 2 | 2 | 4r/(1 + r)² |
| not-all-equal, punctured Fano plane | 7 | 6 | 3 | 5 | 7^k + 2 | log₃ 7 ≈ 1.771 | r·N(r)/D(r), below |

Here N(r) = r⁶ + 7r³ + 21r + 35 and D(r) = r⁶ + r⁵ + 2r⁴ + 9r³ + 20r² + 26r + 5.
- **Instability.** In all three the multiplier at r = 0 is exactly m, and 0 < r < r′ < 1 for 0 < r < 1. So every softened tower
  flows to the free law, uniform on all eight corner tuples.
- **Corner information.** It is the same at every level, at distance s^k:
  - for parity, two corners share 0 bits and the three share a total correlation of 1 bit;
  - for the two not-all-equal towers, two corners share 5/3 − log₂ 3 ≈ 0.082 bits and the total correlation is 2 − log₂ 3 ≈ 0.415
    bits.

## Nearest known result

- **The Sierpinski gasket.** The parity tower's graphs are the Sierpinski gasket graphs, with (3^(k+1) + 3)/2 vertices and
  similarity dimension log₂ 3. Classical.
- **The Sierpinski tetrahedron.** Four pieces at half scale, dimension 2. The tetrahedral tower here is a different object with the
  same exponent: the midpoint subdivision of a triangle in which neighbouring sub-triangles do not share their midpoints.
- **Finitely ramified fractals.**
  - Gefen, Mandelbrot and Aharony (1980): spin models on finitely ramified fractals have no order above zero temperature. Exact
    decimation on such lattices is standard.
  - Theorem 2 is the hard-constraint version, with an explicit lower bound on the multiplier.
- **Bounded treewidth.** Post-critically finite self-similar graphs have bounded treewidth (for example arXiv 2011.02735, Schreier
  graphs of contracting groups).
- **The Fano tower.** Not found by name in a bounded search.
- **Classification.** Known with delta. The fractals and the absence of order above zero temperature are classical. The delta is that
  these towers are each law's smallest exact self-reproduction (`EXACT-TOWERS-20261029-001A`, `HUB-SURVIVORS-20261029-001B`), and
  the explicit softened maps.

## Proof of Theorem 1

**(i) Size.** Each level multiplies the copies by m and adds h variables per replaced copy:
V_k = V_{k−1} + h·m^(k−1), with V₀ = 3. ∎

**(ii) The law.** By Theorem 1 of ticket A, replacing every copy of T_{k−1} by G gives each solution of T_{k−1} exactly
c^(m^(k−1)) extensions, and no other assignment any. So the corner relation of T_k is that of T_{k−1}, and the number of extensions
of each allowed corner tuple is multiplied by c^(m^(k−1)). Inductively the relation is R and the count is
c^(1 + m + … + m^(k−1)). ∎

**(iii) Distances.**
- **Distances scale by s.** Take u, v in T_{k−1}.
  - *At most s times.* Each adjacency of T_{k−1} lies in a copy C. In the gadget replacing C, the two variables are legs at
    distance s.
  - *At least s times.* Cut a shortest path of T_k at the variables of T_{k−1} it visits. The interior of each replacing gadget
    meets the rest only at its legs. So each piece runs inside one gadget, between two of its legs, which were adjacent in
    T_{k−1}, and has length at least s.
  - So the distance in T_k is s times the distance in T_{k−1}.
- **Eccentricity.** Suppose the two conditions hold. Prove by induction on k, for a fixed corner o, two statements:
  - (a) every variable of T_k is within s^k of o;
  - (b) every copy of T_k holds a variable within s^k − 1 of o.

  Both hold for T₀. For T_{k+1}, take a copy C of T_k, and let ℓ be its variable nearest to o, so that d(ℓ, o) ≤ s^k − 1 by (b).
  - *(a) for k + 1.* A variable x of C's gadget has d(x, o) ≤ d_G(x, ℓ) + s·d_{T_k}(ℓ, o) ≤ s + s(s^k − 1) = s^(k+1).
  - *(b) for k + 1.* Each copy of C's gadget holds a variable y with d_G(y, ℓ) ≤ s − 1. Then
    d(y, o) ≤ s − 1 + s(s^k − 1) = s^(k+1) − 1.
- **Balls.** Let A_j be the level-j sub-tower containing a corner a.
  - Its variables are within s^j of a, by the eccentricity bound applied to A_j.
  - Every other variable is reached through A_j's other two corners, which lie at distance s^j, so it is further away.
  - So the ball of radius s^j is A_j, with 3 + h(m^j − 1)/(m − 1) variables. ∎

**(iv) Finite ramification.**
- **The tree.** Its nodes are the copies that were replaced at some level. The bag of a node is the copy's three variables together
  with the h hidden variables its gadget introduced. A node's parent is the node whose gadget created it. Each copy of T_k lies
  inside the bag of its parent. Bags have h + 3 variables.
- **Connected occurrences.**
  - A hidden variable occurs in the bag of the node that introduced it, and in the bags of those of its children that contain it.
  - Below each such child, a leg lies in exactly one copy of the next gadget. So the variable occurs along a single downward path.
  - The occurrences therefore form a subtree, and this is a tree decomposition of width h + 2.
- **Cuts.** The variables introduced at or below a node occur only in copies descending from it. So deleting the node's three
  corners cuts them off. ∎

## Proof of Theorem 2

Let W_t(r) be the sum over hidden assignments of r^(number of violated copies), for a leg tuple t.
- **Allowed tuples.** W_t(0) = c.
- **Excluded tuples.** W_t(0) = 0, and the linear coefficient is the number of extensions of t that violate exactly one copy.
  Lemma 4 of ticket A gives at least 3c of them.
- **The ratio.** It is at least 3r + O(r²).

The three minimal gadgets keep the weights two-valued, as Theorem 3 shows. For a general gadget the first-order bound applies to the
smallest excluded weight against the largest allowed weight. ∎

## Proof of Theorem 3

- **The gadgets.** The triangle has copies (a, d, e), (b, d, f) and (c, e, f), each parity. The punctured tetrahedron and the
  punctured Fano plane are as in ticket A.
- **The conditions of Theorem 1(iii).** Check 1 confirms for each gadget:
  - the factors;
  - the legs on distinct copies at distance s;
  - every variable within s of each leg;
  - every copy holding a variable within s − 1 of each leg.
- **Sizes and exponents.** These follow from Theorem 1.
- **The softened maps.** Enumerating hidden assignments by their number of violations gives two weight polynomials, one shared by all
  allowed tuples and one by all excluded ones (check 5). The map is their ratio. Writing r′ = n(r)/d(r), the identities

  - triangle: n − r·d = 4r(1 − r)(1 + r) and d − n = 2(1 − r)³;
  - tetrahedron: n − r·d = 2r(1 − r)(r + 3) and d − n = 2(1 − r)²;
  - Fano: n − r·d = r(1 − r)(r + 3)(r³ + 5r + 10) and d − n = (1 − r)³(1 + r)(r³ + r² + r + 5)

  have positive cofactors on (0, 1). They give r < r′ < 1 there.
- **The limit.** Since r′ > r, the iterates increase. Their limit is a fixed point in (0, 1], and the only one is 1.
- **The multiplier.** It is the ratio of the linear coefficient of the excluded weight to c: 6/2, 8/2 and 35/5.
- **The information values** are those of the uniform law on the relation, constant in k by Theorem 1(ii). ∎

## Reading

- **What the towers are.**
  - *Parity.* Its tower is the Sierpinski gasket.
  - *Twisted not-all-equal.* Its tower subdivides a triangle into four at each level, three corners and a middle one, as in the
    plane, but neighbouring sub-triangles keep their own midpoints. It grows like the plane, with exponent 2, yet three points cut
    off any sub-triangle. In the triangular grid, where midpoints are shared, they do not (check 6).
  - *Not-all-equal.* Its tower repeats the Fano plane: seven cells per cell, any two sharing at most one point, exponent log₃ 7.
- **Space from logic.**
  - Each law's smallest exact self-reproduction builds a definite hierarchical space with a definite growth exponent. Nothing is
    drawn in advance.
  - But every such space is finitely ramified: bounded treewidth, three-point cuts at every scale. No exact tower is a lattice, and
    none is two- or three-dimensional in the sense of separation, whatever its growth exponent.
- **Universally influential cycles.**
  - At the hard law, corners at distance s^k are exactly as correlated as at distance 1.
  - That influence is fragile. Any softening grows m-fold per level, at least threefold in general. The law therefore survives only
    up to the scale whose sub-tower holds about 1/r copies: correlation length ξ with ξ^(log m / log s) ≈ 1/r.
  - This is the classical picture for finitely ramified fractals, here with exact maps.
- **Possible and typical.** The canonical knot test reads the set of allowed states. That set is the knot at every level of every
  rebuilding tower. The counted law is a branch-internal measure, and it agrees with the set-level law at every scale exactly for
  the exact towers.
  - A rebuilding gadget that is not exact keeps the relation but moves the counted law. For "x or (y ≠ z)" (check 6) the corner law
    concentrates on the two tuples far from both excluded tuples.
  - Those two tuples form the decomposable relation x = 1, y ≠ z.

## Checks

`check.py` (standard library) on `tower_lib.py`, with `result.json`:
- **0.** The dependency artifacts are bound by hash.
- **1.** The three gadgets: knot relations, uniform counts, legs on distinct copies at one distance, and the two conditions of
  Theorem 1(iii).
- **2.** Towers to levels 6, 5 and 4:
  - copies and variables;
  - corner distances s^k and eccentricities s^k;
  - ball sizes 3 + h(m^j − 1)/(m − 1).
- **3.** Exact counts by variable elimination on the whole tower to levels 4, 3 and 3: c^((m^k − 1)/(m − 1)) on every allowed tuple,
  zero elsewhere. Also the information values.
- **4.** The hierarchy's tree decomposition (cover, connected occurrences, width h + 2) and the three-corner cuts at every node.
- **5.** The softened weight polynomials, the factorizations, sampled positivity, the multiplier m, and float trajectories from 0.001.
- **6.** Controls:
  - the four-copy "x or (y ≠ z)" gadget is rebuilding but not exact, and its corner law changes from level 1 to level 2;
  - in the triangular grid of side 4, deleting the corners of a corner sub-triangle does not cut it off;
  - a Fano gadget with one line moved is not exact.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 | Substitution with private hidden variables; distance scaling; hierarchy bags | Elementary; the fractals are classical |
| Theorem 2 | Lemma 4 of ticket A (a knot's excluded tuples are isolated) | Hard-constraint analogue of a classical fact |
| Theorem 3 | The three smallest exact gadgets and their weight polynomials | Explicit maps new here; the gasket classical |
| The selection | Each law's smallest exact self-reproduction (ticket A; `HUB-SURVIVORS-20261029-001B`) | From the program |

## What this does not show

- Anything about substitutions in which neighbouring copies share hidden variables. Those are the only route to towers that are not
  finitely ramified.
- The softened flow of gadgets that are not symmetric, beyond the first-order bound.
- That the drift of "x or (y ≠ z)" holds for all its rebuilding gadgets. One gadget is followed over four levels in scoping.
