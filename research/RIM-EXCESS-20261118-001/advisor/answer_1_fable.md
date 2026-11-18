<!-- modelUsage: claude-fable-5-2 -->

**Caveat on my reading.** I worked from the statement alone and nothing below was computed. I assumed members are lattice vertices, edges are oriented counter-clockwise around up triangles (so e1, e2, e3 circulate an up triangle), and "lone" means a vertex in exactly one triangle. If that is wrong, Q1 stands and Q2–Q3 need re-reading.

## 1. Checks

**Lemma P is correct.** Two remarks:
- At m = 3 the step "B − s must not be tight" is not Prop 3 (pairs are never tight). It still holds because the pair sum 3 − delta_s equals D(p,n) + D(n,p) = 3s(p,n) ≥ 3, forcing delta_s ≤ 0. Say so explicitly.
- The same argument gives more: removing any r members (leaving at least 3) saves at most 3(r−1). That is the full induced-order bond condition and a free pruning rule.

**Corollary is correct** but is arithmetic: m = s+2+e and W = 3(m−2). It needs one unstated line: B has a tight order on all m members, because a tight order on fewer would make an (m−1)-subset constrained. It also re-proves Theorem 7, since W ≥ D(x,z) + D(z,x) = 3s.

**Lemma C is correct, and can be sharpened.** If the arcs weigh a1 and a2, then (a1 − D(x,z)) + (a2 − D(z,x)) = 3e exactly, with both terms non-negative multiples of 3. So e splits as e' + e'', with x→z arc members having detour ≤ 3e' and the others ≤ 3e''. At e = 0 every member is on a geodesic.

**Gap in the algorithm.** "No tight proper sub-collection" must be tested in all cyclic orders of the sub-collection, not only the order induced from the polygon. Nothing in Lemma P shows a subset tight in a foreign order is tight in the induced one. If the code checks induced orders only, it can accept a non-bond and return b too small; it can never return b too large. Either check all orders or prove an uncrossing lemma. Also state the stopping rule for unbonded pairs.

## 2. Why lone, opposite, facing

**Lone + opposite forces a figure-eight (I believe this is a proof).**
- A geodesic walk can pass a lone up vertex x only as w→x→u, with the interior on its left; a lone down vertex z only with the interior on its right.
- So the boundary order is u, u', w', w, with the x→z arc joining u to w' and the z→x arc joining u' to w. These are interleaved, so in a disc the arcs share a vertex y. Two lone vertices of the same class are not interleaved.
- Split the polygon at y into loops through x (m1 members, weight W1) and z (m2, W2).
  - If y is a member, counting shows one loop is a tight proper sub-collection, a contradiction.
  - So y is not a member, and non-tightness of both loops forces W_i = 3(m_i − 1). Each loop plus y is exactly tight, with y on geodesics.
- Hence every bond through an opposite lone pair is (C1 ∪ C2) − y, with C1 ∋ x,y and C2 ∋ z,y tight and meeting only in y. Then e = e1 + e2 + [s(x,y) + s(y,z) − s(x,z)], where e_i is loop i's weight over its round trip, in units of 3.
- Conversely, two tight sets sharing exactly one point always glue to a tight set. So this is where b can break the triangle inequality: the glued set is constrained but its bond may drop x or z.

**Facing (heuristic, valid where patch D equals free-lattice D).**
- In coordinates (i,j) with e1 = (1,0) and −e3 = (0,1), I get lattice D(v) = max(i+2j, i−j, −2i−j).
- A closed tour then weighs at least 3k, where k is the side of the smallest enclosing up triangle, for one orientation. I proved that orientation; the down-triangle bound for the other I checked only on examples.
- So m points are tight iff they fit in an up or down triangle of side m−2, and a bond needs at least two members on each side of that triangle (a corner counts twice).
- For a facing pair with x = (0,0) and z = (a,b), z is the only parallelogram vertex on the antidiagonal i+j = s. So S − z fits a triangle of side s−1 and is tight: no bond in a pure parallelogram.
- A non-lone z in a disc always has a neighbour on that antidiagonal, which supplies the second point at excess 0.

**Reason to doubt.** The facing half uses the lattice metric. In non-convex patches D is longer, tight sets are rarer, and I have no proof that a non-lone pair cannot gain excess. I would put the claim at about 80% for 11–12 knots.

## 3. Does excess grow?

I cannot prove a bound and cannot certify a family. I lean slightly towards unbounded, but weakly.

**Mechanism.** On any patch, a bond of excess e through x, z fits in a lattice triangle of side s+e. In the convex idealisation it also needs a second patch vertex q on z's antidiagonal (or x's). If the nearest such q sits at offset T > b along it, then e ≥ T − b.

**Candidate family.**
- Take a 2×1 parallelogram with x = (0,0), z = (2,1), s = 3.
- Attach along edge (1,0)–(2,0) a one-triangle-wide band running down-right between antidiagonals i+j = 1 and i+j = 2, about 2t triangles long.
- Add one cap triangle at the far end touching i+j = 3.
- The band stays strictly between the two antidiagonals, so neither flank is touched. By my count this is about 5+2t knots.

**What could go wrong.** The band is non-convex, so the patch metric may leave the pair unbonded. Or a bond may use non-convexity to avoid q, and excess stays small. Since t = 1, 2 lie inside your exhaustive ≤10 range, where the maximum excess is 1, at least one of these happens at small t.

**Cheapest discriminator.**
1. Look up the t = 1, 2 discs in the existing tables.
2. Run the polygon search on the single corner pair for t = 3..10, and with a 2×2 or 3×2 body. Each is one pair on one patch.
3. Read the outcome: unbonded throughout, excess growing with t, or saturating at 2.
4. On the referee's excess-2 examples, extract y, e1, e2, the detour, and the antidiagonal offset of the nearest patch vertex. That tests the mechanism at no cost.
5. If you hill-climb again, climb on that offset subject to "bonded", not on excess, which is flat.

## 4. Predictions to freeze

| Check | Prediction | Confidence |
|---|---|---|
| Lemma P, all bonds, discs ≤ 9 | Zero violations; a failure means a code or definition mismatch | 99% |
| Polygon search vs brute force, ≤ 9 | Exact match; any mismatch has search b < brute b (see the order gap) | 90% |
| Excess only on lone opposite facing, 11 and 12 knots | Holds; same for unbonded pairs | 80% |
| Largest excess on 12-knot discs | Exactly 2 | 90% |
| Random patches to 40 knots | Max excess 2; reaching 3 about 10%; says little about Q3 | — |

Extra falsifiable items I would add:
- In every bond through an opposite lone pair, the arcs cross at a non-member y and both loops plus y are exactly tight.
- The identity e = e1 + e2 + detour(y) holds on every such bond.
- Every tight set of m members fits in a lattice up or down triangle of side m−2.
