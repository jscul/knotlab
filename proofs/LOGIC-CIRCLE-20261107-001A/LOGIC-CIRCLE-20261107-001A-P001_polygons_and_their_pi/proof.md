# Polygons: the circle of a periodic or line-arrangement law, and its π

Status: Proved by hand. The table of 19 laws is computed exactly; bond distances are checked on samples (`check.py`).

Ticket `LOGIC-CIRCLE-20261107-001A`, 2026-11-07.

## Standard statement

1. **Periodic plane graphs.**
   - **Setting.** Let G be a doubly periodic, locally finite plane graph with locally finite plane dual G\*. Let G be
     3-edge-connected and G\* 2-connected.
   - **β.** For edges e, f of G, let β(e, f) be the least size of a bond (minimal edge cut) of G containing both, minus one.
   - **The bound.** |β(e, f) − 2‖x_f − x_e‖_P| ≤ C. Here x is the position of an edge's midpoint, and ‖·‖_P is the norm whose unit
     ball is the velocity polygon P of G\*.
   - **The velocity polygon.** P is the convex hull of displacement/length over the cycles of the finite quotient G\*/ℤ².
   - **Consequence.** P has rational vertices in lattice coordinates, so Gołąb's self-perimeter of the norm is rational and lies
     in [6, 8]. Gołąb's self-perimeter is the perimeter of the unit circle measured in the norm itself.
2. **Niven.** Niven's theorem implies that if P is an affine image of a regular 2n-gon, then n ∈ {2, 3}.
3. **Line arrangements.**
   - **Setting.** Take a simple arrangement of lines in k ≥ 2 directions with unit normals n_j. The lines of direction j have
     density ρ_j with bounded discrepancy.
   - **Bonds.** In the planar graph of the arrangement (vertices the crossings, edges the segments), every bond through segments s
     and t has at least 2·sep(s, t) + 4 elements, or 2·sep + 2 when s and t lie on one line. Here sep counts the lines strictly
     separating s and t. Some bond has at most 2·sep(s, t) + C elements.
   - **The norm.** Hence β(s, t) = 2 Σ_j ρ_j |⟨x_t − x_s, n_j⟩| + O(1), and the unit ball of the norm is half the polar of the
     zonotope Σ_j ρ_j [−n_j, n_j].
   - **Regular grids.** For n equiangular directions of equal density, the unit ball is a regular 2n-gon. Its self-perimeter is
     4n sin(π/2n) for odd n and 4n tan(π/2n) for even n.

## Nearest known result

- **Periodic graphs.** Graph distance on a doubly periodic graph is within a bounded amount of a polygonal norm, the velocity
  polygon. So no periodic graph has round large-scale balls.
  - Fritz, "Velocity polytopes of periodic graphs and a no-go theorem for digital physics", Discrete Math. 313 (2013), whose
    corrigendum credits the same objects to Eon's cycle figures and to Kotani–Sunada.
  - For periodic metrics: Burago (1992).
- **Self-perimeters.**
  - **Gołąb (1932).** The self-perimeter of a centrally symmetric convex disc lies in [6, 8]. It is 6 exactly for affine regular
    hexagons and 8 exactly for parallelograms.
  - **Regular polygons.** Their self-perimeters rise to 2π for 2n-gons with n odd and fall to 2π for n even (Martini and
    coauthors, "On self-circumferences in Minkowski planes", Extracta Math. 34 (2019); Wolansky, arXiv:2604.01950).
- **Line arrangements.** The cell graph of a simple line arrangement is a partial cube: the distance between two cells is the
  number of lines separating them. De Bruijn (1981) obtained Penrose rhombus tilings as duals of pentagrids.
- **Niven (1956).** sin and tan take rational values at rational multiples of π only at 0, ±1/2, ±1 and 0, ±1 respectively.
- **Classification: known-overlap-found.** The delta, as far as found:
  - (i) the least bond through two edges is twice the distance in the dual, up to a constant, so the knot-size metric of a parity law
    has the dual's velocity polygon as its shape;
  - (ii) for line arrangements, every bond crosses every separating line twice, and that bound is reached up to a constant;
  - (iii) the rationality of π for every periodic law, with Niven's theorem as a route to the crystallographic restriction for
    these shapes;
  - (iv) the exact table of the 19 laws on Archimedean and Laves tilings.

## Terms

- **The law.** A parity law on a plane graph G has one variable per edge and one parity knot per vertex: the incident variables sum
  to 0.
- **Its knots.**
  - Its knots (finite sets of variables on which the law is constrained as a whole while every proper part is free, K1–K3) are the
    finite bonds of G with at least three edges (`OPEN-END-GROWTH-20261107-001` B).
  - When G and G\* are locally finite plane graphs, the finite bonds of G are the edge sets of the finite cycles of G\* (planar
    duality).
- **Bond distance.** δ(e, f) is the size of the least knot through e and f, minus one. Here that is the least cycle of G\* through
  the dual edges e\*, f\*, minus one.
  - It is a metric (`NATIVE-NETWORK-20261021-001` B, Theorem 2: a circuit inside C₁ ∪ C₂ joins the ends).
  - Under the hypotheses of 1, G\* is simple, so every such cycle has at least three edges.
- **The circle.** The circle of radius r around e is the set of variables f with δ(e, f) ≤ r, placed at edge midpoints. Its shape
  is the limit of (1/r)·circle.
- **π of a shape.** π_K of a centrally symmetric convex disc K is half the perimeter of K measured in the norm whose unit ball is
  K (Gołąb). It is unchanged by linear maps, lies in [3, 4], and equals π for the Euclidean disc.

## Theorem 1 (periodic laws)

Under the hypotheses of standard statement 1, there is a constant C with |δ(e, f) − 2‖x_f − x_e‖_P| ≤ C for all variables e, f.
The circle's shape is ½P, a centrally symmetric polygon with rational vertices in lattice coordinates, and π of the circle is
rational.

*Proof.*

(a) **The quotient and the polygon.**
- Let Λ ≅ ℤ² act by translations, and let Q = G\*/Λ, a finite multigraph. Each directed edge of Q carries an integer displacement
  (lattice coordinates, fixed lifts of the vertices). A closed walk W of Q has a displacement disp(W) and a length len(W).
- Let P = conv{disp(c)/len(c) : c a simple cycle of Q}. Reversing a cycle negates it, so P is centrally symmetric. Its vertices are
  ratios of integers.
- **0 lies inside P.** G\* is connected and Λ-periodic, so the displacements of closed walks of Q generate a finite-index subgroup
  of Λ, and every closed walk is a union of simple cycles.

(b) **Paths cannot beat P.**
- Let a path of G\* have length ℓ, from u to w. Its projection to Q is a walk.
- Removing simple cycles one at a time splits the walk into simple cycles c_i and a simple path of length below |V(Q)|.
- Each disp(c_i) lies in len(c_i)·P, so x_w − x_u lies in ℓ·P plus a bounded set. Hence ‖x_w − x_u‖_P ≤ ℓ + C₀.

(c) **Lower bound.**
- Let Z be a cycle of G\* through e\* = ab and f\* = cd.
- Z minus these two edges is two disjoint paths, each from an end of e\* to an end of f\*.
- By (b) each has length at least ‖x_f − x_e‖_P − C₁, so δ(e, f) = |Z| − 1 ≥ 2‖x_f − x_e‖_P − 2C₁ + 1.

(d) **Ladders.**
- **The path p.** Let c be a simple cycle of Q with D = disp(c) ≠ 0 and l = len(c). Its lift is a simple two-way path p of G\*,
  invariant under translation by D, within some distance r of a line parallel to D.
- **A disjoint copy.** Choose T ∈ Λ whose distance from that line exceeds 2r + 1. Then p and p + T are disjoint.
- **The connector q.** Take any path of G\* from p to p + T, and let q be its part from the last vertex on p to the next vertex on
  p + T. The interior of q avoids both paths. Let q run from w ∈ p to w′ ∈ p + T.
- **The cycle.** For m large, q and q + mD are disjoint, and Z_m = p[w, w + mD] ∪ (q + mD) ∪ (p + T)[w′, w′ + mD] ∪ q is a simple
  cycle of length 2ml + 2|q|.
- **The bound.** Z_m contains every edge of p between w and w + mD. So any two such edges g, g + mD have
  δ(g, g + mD) ≤ 2ml + 2|q| − 1.

(e) **Upper bound.**
- **The cone.** Let x = x_f − x_e lie in the cone spanned by adjacent vertices D₁/l₁ and D₂/l₂ of P. Write x = αD₁ + βD₂ with
  α, β ≥ 0. Then ‖x‖_P = αl₁ + βl₂, since the norm is linear on the cone.
- **Stepping stones.**
  - Let g₀ be an edge of a lift of c₁ within bounded distance of e, and g₁ = g₀ + ⌊α⌋D₁.
  - Let g₂ be an edge of a lift of c₂ near g₁, and g₃ = g₂ + ⌊β⌋D₂, which lies near f.
- **Nearby edges.** Bond distance between edges at bounded distance is bounded: there are finitely many configurations up to Λ,
  and G\* is 2-connected, so every two edges lie on a cycle.
- **Conclusion.** By the triangle inequality and (d),
  δ(e, f) ≤ δ(e, g₀) + δ(g₀, g₁) + δ(g₁, g₂) + δ(g₂, g₃) + δ(g₃, f) ≤ 2⌊α⌋l₁ + 2⌊β⌋l₂ + C₂ ≤ 2‖x‖_P + C₂.

(f) **π is rational.**
- The vertices of P are rational, and so are its edge vectors.
- The normals n_i with ⟨n_i, v⟩ = 1 on edge i are rational, so the norm of an edge vector, max_i ⟨n_i, s⟩, is rational.
- So the perimeter is rational, and scaling P by ½ does not change π. ∎

**Remark.** Every vertex of P comes from a simple cycle of the finite graph Q, so the circle of a periodic law has finitely many
sides. A rounder polygon needs more simple cycles, hence a larger period.

## Corollary 2 (harmonies: rational π, and only two regular circles)

- (i) **Rational π.** The π of every periodic law's circle is a rational number in [3, 4].
- (ii) **Only two regular circles.** Suppose a periodic law's circle is an affine image of a regular 2n-gon.
  - Its π is 2n sin(π/2n) for odd n, or 2n tan(π/2n) for even n (computed in Corollary 4). By (i) this is rational.
  - By Niven's theorem, sin(π/2n) is rational only for n = 1 or 3, and tan(π/2n) only for n = 2.
  - So the circle is a parallelogram (π = 4) or a hexagon (π = 3). These are exactly Gołąb's two extremes.
- (iii) **No round circle.** No periodic law has an elliptic (round) circle. An ellipse is not a polygon, and its π is the
  transcendental π (Lindemann).

## Theorem 3 (laws on line arrangements)

**Setting.**
- **The arrangement.** A is a simple arrangement (no three lines through a point) of lines in k ≥ 2 directions, with unit normals
  n_j. The number of family-j lines meeting any segment of length ℓ perpendicular to them is ρ_jℓ + O(1).
- **The law.** One variable per segment between consecutive crossings, and one four-place parity knot per crossing.
- **The dual.** Its plane dual is the cell graph: cells are adjacent across a segment. Its knots are the cycles of the cell graph.

**Statement.** For segments s and t,
- 2·sep(s, t) + 3 ≤ δ(s, t) ≤ 2·sep(s, t) + C, or 2·sep + 1 ≤ δ when s and t lie on one line;
- δ(s, t) = 2 Σ_j ρ_j |⟨x_t − x_s, n_j⟩| + O(1).

So the circle's shape is {x : 2 Σ_j ρ_j |⟨x, n_j⟩| ≤ 1}, half the polar of the zonotope Σ_j ρ_j[−n_j, n_j].

*Proof.*

(a) **Lower bound.**
- A cycle Z of the cell graph through s\* and t\* is a closed curve. Each of its edges crosses exactly one segment of one line.
- A closed curve in general position crosses every line an even number of times.
  - A line strictly separating s from t is crossed at least twice.
  - The line ℓ_s through s is crossed at s and at least once more, and likewise ℓ_t.
  - If ℓ_s = ℓ_t, the crossings at s and t suffice.
- So |Z| ≥ 2·sep + 4, or 2·sep + 2 on one line.

(b) **Upper bound: a route.**
- **The directions.** Order the line directions by angle. The direction of x = x_t − x_s lies between two angularly adjacent line
  directions d_a and d_b, so x = αd_a + βd_b with α, β ≥ 0.
- **The route.**
  - From an end u of s, walk along segments for O(1) crossings to a family-a line ℓ_a (gaps are bounded).
  - Follow ℓ_a for length about α, turn onto a family-b line ℓ_b where they cross, and follow it for about β.
  - Reach an end w of t in O(1) more crossings, never traversing s or t.
- **It crosses only separating lines.** No line direction lies strictly between d_a and d_b, so ⟨d_a, n_j⟩ and ⟨d_b, n_j⟩ never
  have opposite signs. Hence ⟨·, n_j⟩ is monotone along both long legs. The legs therefore cross each line at most once, and only
  lines separating their ends.
- **S.** Let S be the set of crossings on the route. Then |S| ≤ sep(s, t) + C₃.

(c) **Upper bound: the bond.**
- **∂S is small.** S induces a connected subgraph. Its edge boundary ∂S has at most 4|S| − 2(|S| − 1) = 2|S| + 2 edges, and it
  contains s and t.
- **The bond B.** Let C_∞ be the infinite component of G − S. Choose the O(1) connectors so that the far ends of s and t lie in it;
  only a bounded neighbourhood of the route can be enclosed.
  - Then B = ∂C_∞ ⊆ ∂S is a bond. C_∞ is connected, and its complement is S together with pockets attached to S, also connected.
  - B contains s and t.
- **Conclusion.** δ(s, t) ≤ |B| − 1 ≤ 2|S| + 1 ≤ 2·sep(s, t) + 2C₃ + 1.

(d) **The norm.**
- By bounded discrepancy, sep(s, t) = Σ_j ρ_j |⟨x, n_j⟩| + O(1).
- So δ(s, t) = 2 Σ_j ρ_j|⟨x, n_j⟩| + O(1) = 2h_Z(x) + O(1), where h_Z is the support function of Z = Σ_j ρ_j[−n_j, n_j].
- The unit ball of h_Z is the polar Z°. ∎

## Corollary 4 (the circle as a limit of grids)

(i) **Equiangular, equally dense families.**
- **The shape.** Take n families with normals at angles πj/n and equal densities. Then Z is a regular 2n-gon, and so is Z°.
- **π.** Let m = 2n.
  - A side of the regular m-gon of circumradius 1 has Euclidean length 2 sin(π/m). It points toward a vertex when n is odd, and
    toward a side midpoint when n is even.
  - The polygon's radius in those directions is 1 and cos(π/m) respectively.
  - So π = m sin(π/m) for odd n, and m tan(π/m) for even n.
- **Archimedes.** These are half the perimeters of the regular m-gons inscribed in and circumscribed about the unit circle.
- **Approach to π.**
  - From below (odd n): 3, 3.0902, 3.1153, …
  - From above (even n): 4, 3.3137, 3.2154, …

(ii) **Irrational for n ≥ 4** (Niven).

(iii) **Periodic only for n = 2, 3.**
- **n = 2, 3 are periodic for any offsets.** A translation T preserves the arrangement when every ⟨T, n_j⟩/spacing is an integer.
  For n = 3 the three conditions reduce to two, since the normals satisfy n₀ = n₁ − n₂ up to sign.
- **No n ≥ 4 arrangement is.** If one were doubly periodic, Theorem 1 would make its circle a rational polygon, contradicting (ii).
- This is the crystallographic restriction, reached through π.

(iv) **Penrose.**
- De Bruijn's pentagrid (n = 5, offsets summing to an integer) is the dual of a Penrose rhombus tiling.
- Its law's circle is a regular decagon with π = 10 sin(π/10) = 5(√5 − 1)/2 = 5/φ ≈ 3.0902, where φ is the golden ratio.

## Computation 5 (the laws on the Archimedean and Laves tilings)

- **Method.**
  - The circle of the law on a tiling is half the velocity polygon of the dual tiling.
  - Polygons are computed exactly, in rational arithmetic, from all simple cycles of the quotient graphs.
  - The three regular tilings appear in both lists below, so there are 19 distinct laws.
- **Laws on Archimedean tilings:**

| Law on | Knot sizes | Circle | π |
| --- | --- | --- | --- |
| 4.4.4.4 (square) | 4 | parallelogram | 4 |
| 3.3.3.3.3.3 (triangular) | 6 | hexagon | 3 |
| 6.6.6 (honeycomb) | 3 | hexagon | 3 |
| 3.6.3.6 (kagome) | 4 | hexagon | 3 |
| 3.12.12 | 3 | hexagon | 3 |
| 4.8.8 | 3 | parallelogram | 4 |
| 4.6.12 | 3 | hexagon | 3 |
| 3.4.6.4 | 4 | hexagon | 3 |
| 3.3.4.3.4 (snub square) | 5 | octagon | 10/3 |
| 3.3.3.4.4 (elongated triangular) | 5 | hexagon | 11/3 |
| 3.3.3.3.6 (snub hexagonal) | 5 | hexagon | 3 |

- **Laws on Laves tilings** (the regular three repeat the rows above):

| Law on | Knot sizes | Circle | π |
| --- | --- | --- | --- |
| rhombille (dual of 3.6.3.6) | 3, 6 | hexagon | 3 |
| triakis triangular (dual of 3.12.12) | 3, 12 | hexagon | 3 |
| tetrakis square (dual of 4.8.8) | 4, 8 | octagon | 10/3 |
| kisrhombille (dual of 4.6.12) | 4, 6, 12 | dodecagon | 16/5 |
| deltoidal trihexagonal (dual of 3.4.6.4) | 3, 4, 6 | hexagon | 3 |
| Cairo pentagonal (dual of 3.3.4.3.4) | 3, 4 | octagon | 10/3 |
| prismatic pentagonal (dual of 3.3.3.4.4) | 3, 4 | hexagon | 7/2 |
| floret pentagonal (dual of 3.3.3.3.6) | 3, 6 | dodecagon | 16/5 |

- **What the table shows.**
  - **Hexagons.** Every circle with π = 3 is a hexagon. The laws made only of three-place knots on the honeycomb, 3.12.12 and
    4.6.12 tilings all have π = 3, but the law of three-place knots on 4.8.8 has π = 4. Knot size does not fix the circle.
  - **The roundest periodic circles** in this table are the two dodecagons, with π = 16/5 = 3.2. A regular dodecagon would have
    12 tan 15° = 3.2154, which Corollary 2 rules out for periodic laws.
  - **Octagons.** The octagons have π = 10/3, against the regular octagon's 8(√2 − 1) = 3.3137.

## The check

`check.py`, run in 18 s, verifies the following.
- **The tilings.** Every vertex of the eleven tilings has the right sequence of face sizes, and the computed duals have the Laves
  degrees.
- **The table.** All 22 rows match exactly, in rational arithmetic. Every polygon is centrally symmetric with rational vertices,
  and every π lies in [3, 4], with 3 only for hexagons and 4 only for parallelograms.
- **An independent check of the polygons.** Karp's maximum-mean-cycle algorithm gives the support function of each polygon in 16
  random directions, agreeing to 2·10⁻¹⁶. This checks that the cycle enumeration is complete.
- **Bond distances.** Exact least cycles (two-unit minimum-cost flows) on patches of radius 9, 40 pairs per law.
  - The lower bound δ ≥ 2·dist + 1 holds on every pair.
  - |δ − 2‖x‖_P| ≤ 10 on every pair. The observed range is 0.1 to 8.7.
  - On patches of radius 18, three laws keep the same bounded excess out to 2‖x‖_P = 242.
- **Line arrangements** with n = 2, 3, 4, 5 and 7 families, plus a Penrose pentagrid. On every sampled pair,
  δ − (2·sep + 3) ∈ [0, 4], or the corresponding bound with 2·sep + 1 on one line.
- **Regular polygons.** π of the regular 2n-gons for n = 2, …, 12 against the formulas, to 10⁻¹².
- **Controls**, all rejected:
  - predicting the 4.8.8 law with the polygon of 4.8.8 itself rather than of its dual (excess −47 to −15);
  - counting each separating line once instead of twice (excess up to 25);
  - a cycle enumeration that skips loops (the square law loses its polygon);
  - a snub square with squares turned 10° instead of 15° (wrong faces).

## Nonclaims

- **The polygons are classical.** That periodic graphs have polygonal large-scale balls is classical (Fritz; Kotani–Sunada; Eon).
  New here are the reduction for bond distance, the rationality of π, and the table.
- **The constants are not computed.** Samples show the excess between 0.1 and 8.7.
- **π alone does not certify roundness.** Shapes far from round can have π = π. The statements here are about polygons.
