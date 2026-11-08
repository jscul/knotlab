# Curved circles from coins: the random split law, and the isotropic law

Status: Proved by hand, conditional on cited published theorems.
- **Theorems 2–4** use Seppäläinen's law of large numbers (1997, Theorem 1).
- **Theorem 5** uses Kingman's subadditive ergodic theorem and the positive time constant of Delaunay graph distance.
- **Checks.** Samples, constants and shapes are checked by computation (`check.py`).

Ticket `LOGIC-CIRCLE-20261107-001B`, 2026-11-07.

## Standard statement

1. **The graph H_p.** H_p is the plane graph on ℤ² with all axis edges and, independently in each unit square, the NE diagonal with
   probability p and the NW diagonal otherwise.
   - **Exact distance.** For vertices u ≤ w (componentwise), d(u, w) = (w_x − u_x) + (w_y − u_y) − Λ[u, w]. Here Λ[u, w] is the
     length of the longest chain of NE squares in the box [u, w] that strictly increases in both coordinates.
   - **Other quadrants.** The same holds with NW squares in the other two quadrants.
2. **The dual-distance limit.** By Seppäläinen's theorem, d(0, ⌊nz⌋)/n → c_p(z) almost surely, where
   - c_p(z) = |z_x| + |z_y| − g_q(|z_x|, |z_y|);
   - g_q(s, t) = (2√(qst) − q(s + t))/(1 − q) when qs ≤ t ≤ s/q, and min(s, t) otherwise;
   - q = p in the first and third quadrants and q = 1 − p in the second and fourth.
3. **The least cycle.** The least cycle of H_p through two edges, one near 0 and one near nz, has length 2c_p(z)n + o(n) in
   probability.
4. **The shape.** The unit ball {c_p ≤ 1} is a square whose corners are replaced by arcs of the ellipses
   (|x| + |y| − (1 − q))² = 4q|x||y|.
   - **Fair coins.** For p = 1/2 these arcs are circles of radius 1/2 centred at (±1/2, ±1/2).
   - **Its π.** Gołąb's self-perimeter is 2π_K, where π_K = 2 + 6/√5 − 4√2 ∫_{1/√2}^{√2} u²(1 + u⁴)^(−3/2) du ≈ 3.44120.
5. **Poisson-Delaunay.** For the Delaunay graph of a planar Poisson process, the least cycle through two edges at distance R is
   μR + o(R) almost surely, in every direction, with one constant μ > 0.

## Nearest known result

- **Seppäläinen**, "Increasing sequences of independent points on the planar lattice", Ann. Appl. Probab. 7 (1997) 886–898,
  Theorem 1.
  - **The setting.** Each site of the lattice is present independently with probability q.
  - **The limit.** The longest strictly increasing chain in [0, kn] × [0, n], divided by n, converges almost surely to
    (√q/(1 − q))(2√k − (k + 1)√q) for q ≤ k ≤ 1/q, and to min(k, 1) otherwise.
  - This is g_q(k, 1); homogeneity gives g_q(s, t).
- **Seppäläinen**, "Exact limiting shape for a simplified model of first-passage percolation on the plane", Ann. Probab. 26 (1998).
  It treats a different model, Bernoulli horizontal and fixed vertical passage times, and also finds a shape with flat pieces.
- **Isotropy.** First-passage percolation on Voronoi and Delaunay graphs of a Poisson process has a Euclidean-ball limit shape,
  because the process is isotropic (Vahidi-Asl and Wierman 1990, 1992; Howard and Newman; Pimentel).
- **Classification: known-overlap-found.** The delta, as far as found:
  - the exact distance formula for ℤ² with one random diagonal per square;
  - the reduction of the least cycle through two edges (bond distance) to twice that distance, by two disjoint near-geodesics in
    separated tubes;
  - the circular corners at p = 1/2 and the values π(p);
  - the reading as a parity law whose four-place knots are split into three-place knots by coins.

## Terms

- **The random split law.**
  - **The starting law.** Start from the parity law on the square grid: one variable per edge and a four-place parity knot at each
    vertex. Its plane dual is again the square grid.
  - **The split.** Split every knot into two three-place knots joined by a new variable; the new variable is forgotten to recover
    the old knot. Of the three ways to pair four variables, two are planar, and a coin picks one: probability p for one orientation.
  - **The dual.** Splitting the knot at a vertex adds one dual edge across the corresponding dual square, a diagonal. So the dual
    of the split law is H_p.
  - **Its knots.** Every vertex of the split law is a three-place knot.
- **Bond distance.** The split law's knots are the cycles of H_p (planar duality, as in ticket A). Bond distance δ(e, f) is the
  least cycle of H_p through e\* and f\*, minus one. It is a metric (`NATIVE-NETWORK-20261021-001` B, Theorem 2).
- **The circle and π** are as in ticket A.

## Theorem 1 (exact distance)

For u ≤ w, d(u, w) = Δx + Δy − Λ[u, w].

*Proof.*

1. **Clamping.** Let κ map a vertex to its nearest point of the box [u, w], coordinate by coordinate.
   - κ maps every edge of H_p to an edge or a single vertex.
     - An axis edge maps to an axis edge or a vertex.
     - A diagonal of a square inside the box maps to itself.
     - A diagonal of any other square has at least one coordinate clamped to a constant, so it maps to an axis edge or a vertex.
   - So every path from u to w maps into the box with no more edges. Distances may be computed inside the box.
2. **A potential.** For z in the box, let Λ(z) be the longest strictly increasing chain of NE squares in [u_x, z_x) × [u_y, z_y),
   and h(z) = (z_x − u_x) + (z_y − u_y) − Λ(z).
3. **Λ's steps.** Moving one unit right or up adds a column or a row of squares. A strictly increasing chain meets it at most once,
   so Λ grows by 0 or 1.
4. **h is 1-Lipschitz on edges.** Check each kind of edge.
   - **Axis edge.** h changes by 1 − (0 or 1).
   - **NE diagonal of square (i, j).** Λ(i + 1, j + 1) ≥ Λ(i, j) + 1, by appending the square.
     - It is also at most Λ(i, j) + 1: a chain cannot hold both a square in column i and a square in row j, since neither would
       precede the other.
     - So h changes by 2 − 1 = 1.
   - **NW diagonal of square (i, j).** It joins (i + 1, j) and (i, j + 1). Both Λ values lie in [Λ(i, j), Λ(i, j) + 1], so h changes
     by at most 1.
5. **Conclusion.**
   - **Lower bound.** d(u, w) ≥ h(w) − h(u).
   - **Attained.** The up-right path that takes the diagonals of a longest chain and axis steps between them has exactly that
     length.
   - **Other quadrants.** They are the same after reflection, with NW squares. ∎

## Theorem 2 (dual distance)

d(0, ⌊nz⌋)/n → c_p(z) almost surely.

*Proof.*
- By Theorem 1, d = n(|z_x| + |z_y|) − Λ + O(1), with Λ the longest strictly increasing chain of correctly oriented squares in an
  n|z_x| × n|z_y| box.
- Those squares are present independently with probability q.
- Seppäläinen's theorem and homogeneity give Λ/n → g_q(|z_x|, |z_y|) almost surely. ∎

## Theorem 3 (bond distance)

Let e\* be an edge at 0 and f\* an edge at ⌊nz⌋. Then δ(e, f)/n → 2c_p(z) in probability.

*Proof.*

**Lower bound.**
- A cycle through e\* and f\* consists of these two edges and two disjoint paths joining their ends.
- So δ ≥ 2·dist(ends of e\*, ends of f\*) + 1.
- By Theorem 2, liminf δ/n ≥ 2c_p(z) almost surely.

**Upper bound in the open first quadrant** (the others by symmetry).
1. **Boxes.** Fix m. Write a = nz_x/m and b = nz_y/m, and let B_k = [ka, (k + 1)a] × [kb, (k + 1)b] for k < m.
2. **The first path.** P₁ joins the corners of B_0, …, B_{m−1}. Inside each box it follows a geodesic from the lower-left to the
   upper-right corner, which is up-right by Theorem 1.
3. **The second path.**
   - Let B′_k = B_k + (D, −D) with D = ⌈max(a, b)⌉ + 2. The two unions of boxes are disjoint: an overlap of B_k and B′_j would need
     D/a + D/b < 2.
   - P₂ does the same inside the B′_k.
   - Near each end, P₂ joins the other end of e\*, or of f\*, by a vertical and a horizontal run of length O(D). These runs lie
     outside the quadrant region that P₁ occupies.
4. **One cycle.** P₁, P₂, e\* and f\* form a cycle.
5. **Its length.** Box corners are rounded to integers, at a cost of O(m).
   - By Theorem 1, the geodesic inside a box has length a + b − Λ(box).
   - Each box's environment has the law of a box at the origin, so by Seppäläinen's theorem, for fixed η > 0,
     Λ(box) ≥ (n/m)(g_q(z_x, z_y) − η) with probability tending to 1. Taking a union over the 2m boxes, all of them do.
   - Then |P₁| ≤ n(z_x + z_y − g_q(z_x, z_y) + η) + O(m) = n(c_p(z) + η) + O(m), and likewise |P₂| with O(D) = O(n/m) more.
   - So δ ≤ 2n(c_p(z) + η) + O(n/m) + O(m).
   - Divide by n and let n → ∞, then η → 0 and m → ∞. ∎

## Corollary 4 (the circle: a square with elliptic corners)

The circle's shape is ½{c_p ≤ 1}.

**The curved part.** In the first quadrant with q·s ≤ t ≤ s/q:
- c = (s + t − 2√(qst))/(1 − q), so c = 1 means (s + t − (1 − q))² = 4qst.
- This is an ellipse: the quadratic part s² + (2 − 4q)st + t² has discriminant 16q(q − 1) < 0.
- For q = 1/2 it is (2s − 1)² + (2t − 1)² = 1, a circle of radius 1/2 centred at (1/2, 1/2).

**The flat parts.** Outside that cone c = max(s, t), so the boundary is flat: segments of x = ±1 and y = ±1.

**π.**
- **Fair coins.** For p = 1/2 the unit ball is the square [−1, 1]² with each corner replaced by a quarter circle of radius 1/2.
  - The four flat sides have norm-length 1 each.
  - Each quarter arc has norm-length (2/√5 + J)/2, with J = ∫_{arctan(1/2)}^{arctan 2} 2/(sin φ + cos φ + √(sin 2φ)) dφ.
  - Substitute t = tan φ, rationalise 1/(1 + t + √(2t)) = (1 + t − √(2t))/(1 + t²), then put t = u². This gives
    J = 4/√5 − 4√2 ∫_{1/√2}^{√2} u²(1 + u⁴)^(−3/2) du.
  - So π_K = 2 + 6/√5 − 4√2 ∫_{1/√2}^{√2} u²(1 + u⁴)^(−3/2) du = 3.441197851… This is an incomplete elliptic integral. Its
    irrationality is not proved here.
- **Other coins.** π(p) = π(1 − p):

| p | 0 or 1 | 0.05 | 0.1 | 0.25 | 0.5 |
| --- | --- | --- | --- | --- | --- |
| π of the circle | 3 | 3.2107 | 3.2832 | 3.3912 | 3.4412 |

- **p = 0 or 1.** Every square has the same diagonal, so the split law is the honeycomb law and the circle is ticket A's hexagon,
  with π = 3. Any coin bends its corners.
- **A caution.** π(p) passes the Euclidean value π near p = 0.0212. The circle there is a hexagon with slightly rounded corners,
  not a round circle. π alone does not detect roundness.

## Theorem 5 (an isotropic law of three-place knots has a round circle)

**Setting.**
- Π is a Poisson process of intensity 1 in the plane. Its Voronoi tessellation is almost surely three-regular.
- The Voronoi law has a three-place parity knot at each Voronoi vertex and a variable on each Voronoi edge. Its plane dual is the
  Delaunay graph.
- For y in the plane, e(y) is the variable whose Voronoi edge is nearest to y.

**Statement.** For every unit vector u, δ(e(0), e(nu))/n → μ almost surely, with the same μ > 0 for every u.

*Proof.*
1. **Subadditive.** X_{m,n} = δ(e(mu), e(nu)) satisfies the triangle inequality, so X_{0,n} ≤ X_{0,m} + X_{m,n}.
2. **Stationary and ergodic.** Translations along u preserve the law of Π and mix, so the increments are stationary and ergodic.
3. **Integrable.**
   - Two Voronoi edges with a common Voronoi vertex have duals on one Delaunay triangle, so their bond distance is 2.
   - Along a path of Voronoi edges, δ is therefore at most twice its number of edges.
   - The Voronoi cells met by the segment [0, u], with their edges, have finite moments. So E X_{0,1} < ∞.
4. **A limit exists.** By Kingman's subadditive ergodic theorem, X_{0,n}/n → μ(u) almost surely, a constant by ergodicity.
5. **The same in every direction.** A rotation preserves the law of Π, so μ(u) does not depend on u.
6. **μ > 0.**
   - As in Theorem 3, δ ≥ 2·d_D − 1, where d_D is Delaunay graph distance.
   - d_D grows linearly: its time constant is positive (Vahidi-Asl and Wierman; Pimentel). ∎

## The check

`check.py`, run in 21 s, verifies the following.
- **Theorem 1 against breadth-first search.** 36,963 vertex targets, for p ∈ {1/2, 1/4, 0.9}, 3 environments and 3 sources each, with
  0 mismatches.
- **Seppäläinen's constants on 3000 × 3000 samples.** The chain lengths divided by n are 0.826 against 0.828 and 0.666 against
  0.667, and on 6000 × 3000, 0.999 against 1 and 0.882 against 0.886.
- **Theorem 3 on samples.**
  - For p ∈ {1/2, 1/4}, n ∈ {20, 40, 80} and 7 directions, exact least cycles satisfy 2d + 1 ≤ δ ≤ 2d + 8.
  - The mean relative deviation from 2c_p(z)n falls from 3.1% to 1.9% at p = 1/2, and from 6.4% to 2.9% at p = 1/4.
- **The shape equations** hold to 2·10⁻¹⁵ on 2000 boundary points each for p = 1/2, 1/4 and 0.1.
- **π.** The closed form and a 40,000-gon agree to 10⁻⁸, and π(0) = 3.
- **Voronoi.** 300 pairs of adjacent Voronoi edges have bond distance 2.
- **Controls**, all rejected:
  - weakly increasing chains (5920 mismatches);
  - NE squares in the NW quadrant (7431 mismatches);
  - claiming a circle at p = 1/4 (error 0.5);
  - bond distance equal to the dual distance rather than twice it.

## Nonclaims

- **Cited theorems.** Theorems 2–4 rest on Seppäläinen's published theorem, cited and not re-proved; the check compares only its
  constants with samples. Theorem 5 rests on Kingman's theorem and the positivity of the Delaunay time constant.
- **Put in, not derived.** The roundness of the Voronoi law comes from the isotropy of its Poisson input, which is drawn in the
  Euclidean plane, not from logic alone.
- **Rates.** Rates of convergence are not proved.
