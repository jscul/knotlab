# The sphere's count needs resolution width Θ(√n) and size 2^Θ(√n): the proof written out

Status: Proved by hand, every lemma written out. Two local lemmas are decided exactly by computation over all critical angles, which
covers every k. The other lemmas are confirmed on finite instances (`check.py`).

Ticket `COUNT-NOTE-20261107-001A`, 2026-11-07. This note replaces two sketched steps of `SPHERE-WIDTH-20261107-001A`:
- **The winding bound** becomes the distance lemma for straight cut systems (§5–§6).
- **The isoperimetric step** becomes single-step vortex moves inside one octant and a row-counting lemma (§4, §7–§8).

It also writes out the island lemma, the random restriction and the grid-Sperner boundary (§10–§12).

## Standard statement

Let K_k be the octahedral knot sphere and NAE(K_k) its Kasteleyn-signed not-all-equal formula (n = 4k² variables, 8k² clauses of
width 3).

**Theorem A (width).** For k ≥ 1812w + 6, every resolution refutation of NAE(K_k) has width at least w. So the width is at least
⌊(k − 6)/1812⌋ = Ω(√n). Width O(√n) suffices.

**Theorem B (size).** There is an absolute constant c > 0 such that every resolution refutation of NAE(K_k) has size at least 2^{c·k}
= 2^{Ω(√n)}. Size n^{O(1)}·2^{O(√n)} suffices.

**Theorem C (grid Sperner).** Let Sperner_m be 2D Sperner on the side-m triangular grid with the fixed boundary of
`FLAT-STATES-20261107-001B`. Each interior vertex's colour is given by three indicator variables with exactly-one clauses. Clauses
forbid the fully labelled small triangles, either all of them or only those oriented like the boundary.
- Every resolution refutation has width Ω(m) and size 2^{Ω(m)}.
- The same holds for Itsykson–Malova–Oparin–Sokolov's Sperner CSP, which restricts to Sperner_m.

The constants are poor (c ≈ 10⁻¹³ in Theorem B) but absolute.

## Nearest known result

- **Grid principles.** Mutilated chessboard and grid Tseitin need resolution size 2^{Ω(n)} on n×n grids (Dantchev–Riis 2001;
  Alekhnovich 2004).
  - The mutilated chessboard is refuted by a degree-1 linear (Sherali–Adams) count.
  - The sphere's count is refuted by Sherali–Adams of degree 3 with unary coefficients (`COUNT-NOTE-20261107-001B`).
  - So both separate Sherali–Adams from resolution.
- **2D Sperner.** Tree-like resolution needs size 2^{Θ(n)} (Itsykson–Malova–Oparin–Sokolov 2014). Finding a trichromatic triangle needs
  Θ(√N) queries (Crescenzi–Silvestri; Friedl–Ivanyos–Santha–Verhoeven). No general-resolution width or size bound was found
  (§13).
- **Methods.** Two standard tools:
  - width via the existential pebble game (Atserias–Dalmau);
  - size via local random restrictions (Dantchev–Riis).

  Three ingredients are new as far as found:
  - single-step moves of a height-function vortex;
  - straight cut systems with a distance lemma;
  - island terms.
- **Classification.** new as far as found for these formulas.

## Setting

**The formula.**
- **Points and lines.** The 8k² triangles of the k-frequency octahedron |x| + |y| + |z| = k are 2-coloured: triangles sharing a side
  get different colours. Points are one colour class and lines the other. A line's three points are the triangles sharing a side with
  it, so every point lies on three lines.
- **Clauses.** Each line l = {a, b, c} carries Kasteleyn signs s_{l,p} (`TWO-ROUND-BRIDGE-20261106-001B`). With literals
  y_p = x_p ⊕ s_{l,p}, it gives the clauses (y_a ∨ y_b ∨ y_c) and (¬y_a ∨ ¬y_b ∨ ¬y_c).
- **Unsatisfiable.** The formula is unsatisfiable (`TWO-ROUND-BRIDGE-20261106-001B`, theorem 2).

**The point graph G.**
- **Edges.** Two points are adjacent when they share a line. An edge is a pair (l; a, b); two points share two lines only at the
  six corners.
- **Faces.** Drawn with points at triangle centroids, G's faces are the lines and the subdivision vertices. The six vertices of the
  octahedron give two-point faces ("corner faces"); all other faces have three points. As a simple graph, G triangulates the sphere.
- **Metric.** dist is G's graph distance and B(x, s) = {y : dist(x, y) ≤ s}.

**The core.**
- F is the face x, y, z ≥ 0 and o its central point.
- Ω = {p ∈ F : dist(o, p) ≤ ρ}, with ρ = ⌊k/6⌋. Inside F, distance is the triangular lattice's distance, so Ω is a lattice hexagon
  with 3ρ² + 3ρ + 1 points.

**The unfolding.**
- Unfold F and its three neighbours into F's plane. They form a triangle T of side 2k.
- T's vertices are the far corners −e_i. The midpoints of T's sides are F's corners e_i.
- Point centroids form a triangular lattice in T. Scale it to unit spacing.

## 1. Frames and labels

Facts proved in `FLAT-STATES-20261107-001A` (statement 1) and `SPHERE-COUNT-20261106-001A` (lemma 1).

**Frames and transport.**
- A frame at a point is a pair (σ, g) ∈ Z3 × Z2.
- Moving from a to b inside a line l shifts σ by ±1 (by l's cyclic order) and g by s_{l,a} ⊕ s_{l,b}.

**Labels.**
- A label λ ∈ Z6 colours a point with frame (σ, g) by S_λ[σ] ⊕ g, where S0, …, S5 = 011, 001, 101, 100, 110, 010.
- Since S_{λ+2}[σ] = S_λ[σ − 1] and S_{λ+3} is the complement of S_λ, a frame change acts as a label shift.

The two facts used below:
- **(F1) Holonomy.** Transport around a line or a three-point face composes to nothing. Around a corner face it is the label shift −1.
- **(F2) Two consecutive labels.** In a line's own frame its points lie on the three sublattices. If their labels lie in {j, j + 1},
  the line is not monochromatic: S_j and S_{j+1} differ in exactly one position, so the line's word is S_j or S_{j+1} up to a common
  complement, and neither is constant.

## 2. Cut systems and label states

**Cut systems.**
- **Definition.** A cut system for a point z off the corner faces is six pairwise vertex-disjoint paths in the line–face graph, from
  the six lines and faces containing z to the six corner faces. (In the line–face graph, lines and faces of G are adjacent when they
  share an edge of G.)
- **Frames.** Develop frames over the sphere cut along the paths, with z excluded.
- **Shifts.** For an edge (l; a, b) with a, b ≠ z, let t(a, b) be the label shift between b's developed frame and b's frame
  transported from a through l. By (F1), t(a, b) ∈ {−1, 0, 1}, it vanishes unless a path crosses the edge, and t(b, a) = −t(a, b).
- **Holonomy.** The sum of t around a closed walk is 6 times its winding about z minus its windings about the corners. So it is −1
  around each corner face and +6 around z's six neighbours. (`FLAT-STATES-20261107-001A` statement 2.)

**Label states.**
- **Definition.** A label state with vortex z is an integer function L on the points other than z with
  |L(b) + t(a, b) − L(a)| ≤ 1 for every edge (l; a, b) with a, b ≠ z. Lines through z bind their other two points.
- **Colouring.** Its colouring χ_L gives p the colour of label L(p) mod 6 in p's developed frame, and gives z any colour.

**Lemma 2.1.** χ_L satisfies every line not through z, and L ≡ 0 is a label state.

*Proof.*
- **Lines.** For a line l ∌ z, the sum of t around l is 0. Transporting the three labels into l's frame therefore gives integers that
  are pairwise within 1, hence within two consecutive values, and (F2) applies.
- **The flat state.** L ≡ 0 is a label state because |t| ≤ 1. ∎

**Weights.**
- **Definition.** Set w(a → b) = 1 − t(a, b) ∈ {0, 1, 2}. A label state is exactly a potential: L(b) − L(a) ≤ w(a → b) on every
  directed edge.
- **Distance.** d_z(p, q) is the least weight of a walk from p to q in G − z.
- **Holonomy along a walk.** For a walk β, d(β) = ℓ(β) − H(β), where ℓ is its length and H the sum of t along it.

## 3. The window criterion

**Pebbles.** A pebbled colour at p allows exactly three consecutive labels, a_p, a_p + 1 and a_p + 2 (mod 6). The window start a_p
is fixed mod 6; any integer representative may be used, since changing it by 6 shifts that pebble's sheet below.

**Lemma 3.1.** Pebbled colours on a set P ∌ z admit a label state with vortex z iff the integer system

  s_q − s_p ≤ ⌊(d_z(p, q) + a_p + 2 − a_q)/6⌋   (p ≠ q in P)

has no negative cycle.

*Proof.*
- **Fixed sheets.** Fix the sheets s_p. The constraints become L(p) ∈ [a_p + 6s_p, a_p + 6s_p + 2] together with the potential
  inequalities.
- **Interval bounds.** A difference system with interval bounds and no negative cycle in its weights is feasible iff
  lo_q − hi_p ≤ d_z(p, q) for all p, q: take L(v) = min_p (hi_p + d_z(p, v)) (McShane). There is no negative cycle in the weights
  because w ≥ 0.
- **The sheets.** That condition is the displayed inequality. An integer difference system is feasible iff it has no negative cycle
  (Bellman–Ford). ∎

## 4. Single-step certificates

**Lemma 4.1.** Setup:
- y and y′ are adjacent points with cut systems Γ and Γ′.
- P is a set of pebbled colours with y, y′ ∉ P.
- P admits a label state with vortex y but none with vortex y′.

Then there are distinct pebbles p_1, …, p_r (r ≥ 2) and d_{y′}-shortest paths β_i from p_i to p_{i+1} in G − y′ (indices mod r) with:
- Σ_i d_{y′}(β_i) ≤ 3r − 6;
- the closed walk B = β_1 ⋯ β_r passes through y.

*Proof.*
- **The negative cycle.** Lemma 3.1 at y′ gives distinct pebbles with Σ_i ⌊(d′_i + a′_i + 2 − a′_{i+1})/6⌋ ≤ −1, where
  d′_i = d_{y′}(p_i, p_{i+1}) is attained by a path β_i. Since ⌊x/6⌋ ≥ (x − 5)/6 for integers x and the a′ telescope,
  Σ d′_i ≤ 3r − 6. A cycle needs r ≥ 2.
- **Gauge equivalence off y and y′.**
  - Let H = G − {y, y′}. It is connected, since G triangulates the sphere.
  - On H, t and t′ have the same sum around every face: 0 around lines and three-point faces, −1 around corner faces, and +6 around
    the face of H that contains y and y′, which is the union of their faces.
  - A connected plane graph's face boundaries generate its cycles, so t′ − t = dφ on H for an integer function φ, meaning
    φ(b) − φ(a) = t′(a, b) − t(a, b).
  - Both t and t′ lift the same frame transport in their developed frames. So, read mod 6, φ is the frame difference up to a
    constant, and window starts satisfy a′_p ≡ a_p − φ(p) + c (mod 6).
- **If B avoided y.**
  - Then every β_i lies in H, and d_y(β_i) = d_{y′}(β_i) + φ(p_{i+1}) − φ(p_i).
  - Use the representatives a_p := a′_p + φ(p) − c at y. Then d_y(β_i) + a_i − a_{i+1} = d′_i + a′_i − a′_{i+1}, so
    Σ_i ⌊(d_y(p_i, p_{i+1}) + a_i + 2 − a_{i+1})/6⌋ ≤ −1.
  - That is a negative cycle at y, contradicting Lemma 3.1. ∎

Only adjacency is used. No winding numbers or curves between distant vortices are needed, which is why the vortex will move one step
at a time.

## 5. Straight cut systems

**Construction.** Let k ≥ 36 and z ∈ Ω.
- **The segments.** For each corner c, take the segment in T from z's centroid to the point of c's corner face at distance 0.01 from
  c toward z. Rotate it about z's centroid by the angle 10⁻³/length, so that it meets no other centroid.
- **The arc.** Its arc is the sequence of faces the segment meets. It starts in the face at z whose angle contains the segment's
  direction, and ends in c's corner face.
- **Edges outside T.** Near a corner some edges leave T. They are drawn in the unfolding of the outer face across T's side.

**Junctions.**
- **Zero-weight steps.** A step a → b has weight 0 exactly when an arc crosses the edge from the arc's right to its left, the
  counterclockwise direction about z.
- **X0.** Let X0 be the set of points that are the head of one zero-weight step and the tail of another.

**Lemma 5.1.** For k ≥ 36 and z ∈ Ω, the six arcs form a cut system, and X0 has at most 18 points, all within distance 3 of z.

*Proof.*
1. **Directions.**
   - F's centroid lies within 1/√3 of o's centroid, the nearest point centroid, and z lies within lattice distance ρ ≤ k/6 of o.
     So z's centroid lies within k/6 + 0.58 of F's centroid.
   - The near corners lie at distance k/√3 from F's centroid, and the far corners at 2k/√3.
   - So the direction from z to a near corner deviates from the ideal direction (90°, 210° or 330° in F's lattice frame) by at most
     arcsin(0.289 + 1.0/k) < 19° (k ≥ 36). For the far corners (270°, 30°, 150°) the deviation is below 10°. The perturbations
     change directions by less than 0.1°.
   - Check 2 finds the largest deviations over every core vortex to be 17.6° and 8.8°.
   - Each ideal direction is the centre of the 60° angle of one face at z. So the six arcs start in six different faces.
2. **Near z (radius 5).**
   - Since k ≥ 36, the corners are farther than 13 from z, and the lattice within radius 5 is flat. The configuration there is
     determined by the six directions.
   - The **local lemma** (check 1) decides it exactly. It runs over every interval between critical angles (rays through lattice
     points) within 22° of the near ideals and 11° of the far ones.
   - Result: faces met by different rays within radius 5 are disjoint, and at most 18 points, all within lattice distance 3, can
     head one ray's crossing and tail another's.
3. **Beyond radius 5.**
   - Two arcs are segments from z's centroid at an angle of at least 60° − 22° − 11° = 27°.
   - A face (diameter 1) met by both would hold points of both at mutual distance at most 1. That forces both within radius
     1/sin 27° + 1 < 5.
   - A point at distance at most 1 from both arcs satisfies |p| sin 27° ≤ 2. The reason: inside the wedge,
     sin φ + sin(27° − φ) ≥ sin 27°, and outside it the far arc is even farther. So |p| < 5.
4. **One arc, two sides.**
   - A crossed edge joins a point on the arc's right to a point on its left, so no point heads and tails crossings of the same arc.
   - This holds near the arc's corner as well. All edges crossed there are drawn in the one unfolding across that corner's T-face,
     and an outer point's two possible drawings never both occur among crossed edges.
5. **Conclusion.**
   - Faces met by two arcs and points of X0 lie within radius 5 (steps 3 and 4), where step 2 bounds them. Away from z and the
     corners each arc is alone.
   - Each corner is approached by one arc: the others pass at distance more than 5 from it for k ≥ 36.
   - So the arcs are pairwise vertex-disjoint paths of faces, which makes them a cut system, and X0 is as stated. ∎

Check 3 builds the straight cut system for every core vortex of K_12, …, K_36. In every case:
- the six arcs are disjoint;
- the flat state violates exactly one line, through z;
- |X0| ≤ 7, within distance 2 of z.

## 6. The distance lemma

**Lemma 6.1.** For z ∈ Ω (k ≥ 36) with its straight cut system, d_z(x, x′) ≥ (dist(x, x′) − 19)/2 for all points x, x′ ≠ z.

*Proof.*
- **A simple shortest path.** Weights are non-negative, so a d_z-shortest walk can be taken simple: removing a closed sub-walk never
  increases its weight. Call it β, with length ℓ.
- **Few adjacent zero steps.** Two consecutive zero-weight steps meet at a point of X0. Since β visits each point once, at most 18
  pairs of consecutive steps are both zero.
- **Counting.** Group the zero-weight steps into R maximal runs, separated by at least one other step. Then n0 ≤ R + 18 and
  ℓ ≥ n0 + R − 1, so n0 ≤ (ℓ + 19)/2.
- **Conclusion.** d_z(β) ≥ ℓ − n0 ≥ (ℓ − 19)/2 ≥ (dist(x, x′) − 19)/2. ∎

Check 4 confirms it on K_24 and K_36 with slack at least 8.5.

## 7. Single steps

**The bad set.** For a pebble set P let D(P) = {x : |P ∩ B(x, s)| ≥ s/25 for some s ≥ 1}. It contains every point within distance 25
of a pebble, in particular P itself.

**Lemma 7.1.** Suppose:
- P admits a label state with vortex y ∈ Ω (straight cut system);
- y′ ∈ Ω is adjacent to y, and y′ ∉ P;
- y ∉ D(P).

Then P admits one with vortex y′.

*Proof.* Otherwise Lemma 4.1 gives a closed walk B through y and r pebbles, with Σ d′_i ≤ 3r − 6.
- **Hops.** By Lemma 6.1 at y′, dist(p_i, p_{i+1}) ≤ 2d′_i + 19 for each i.
- **The vortex.** y lies on some β_j, and the part of β_j from y to p_{j+1} weighs at most d′_j. So dist(y, p_{j+1}) ≤ 2d′_j + 19.
- **All pebbles of B.** Going around the cycle, every p_m lies within Σ_i (2d′_i + 19) ≤ 25r − 12 of y.
- **Contradiction.** Hence |P ∩ B(y, 25r)| ≥ r, so y ∈ D(P) (take s = 25r). ∎

Check 5 confirms the mechanism on K_30. All 11 blocked steps have certificates through the old vortex within budget, with pebbles
within distance r of it.

## 8. One large free component

**Lemma 8.1.** Let |P| ≤ w and ρ ≥ 302w. Then Fr(P) = Ω ∖ D(P) has a component M(P) holding more than half of Ω's points. It is
unique, and M(P′) ⊆ M(P) whenever P ⊆ P′.

*Proof.*
- **Vitali covering.**
  - Every x ∈ D(P) ∩ Ω has a witness radius s_x with |P ∩ B(x, s_x)| ≥ s_x/25, so s_x ≤ 25w.
  - Choose greedily, by decreasing radius, a maximal family of pairwise disjoint witness balls B(x_i, s_i) centred in D(P) ∩ Ω.
    Every witness ball meets a chosen ball of at least its radius, so D(P) ∩ Ω ⊆ ∪ B(x_i, 3s_i).
  - The chosen balls are disjoint and each holds at least one pebble. So Σ s_i ≤ 25w and there are at most w of them.
- **Rows.**
  - Use cube coordinates (u, v, −u − v) about o, so Ω = {max(|u|, |v|, |u + v|) ≤ ρ}. A row is a lattice line u = const,
    v = const or u + v = const inside Ω.
  - A path of length at most 150w ≤ ρ/2 between points of Ω stays in F, where distance is lattice distance. So each set
    B(x_i, 3s_i) ∩ Ω meets at most 6s_i + 1 rows of each direction, and at most 151w rows of each direction are blocked.
  - The free rows lie in Fr(P).
- **Free rows meet.**
  - Rows u = u₀ and v = v₀ meet inside Ω when |u₀|, |v₀| ≤ ρ and u₀v₀ ≤ 0. The same holds for the other pairs of directions.
  - Since ⌊ρ/2⌋ + 1 > 151w, each direction has a free row with offset in [0, ρ/2] and one in [−ρ/2, 0]. These central rows meet
    each other, and every free row meets a central row of another direction.
  - So all free rows lie in one component.
- **Counting.**
  - A point of Ω on no free row lies on blocked rows of two directions. There are at most (151w)² such points.
  - |D(P) ∩ Ω| ≤ Σ(27s_i² + 9s_i + 1) ≤ 16875w² + 226w.
  - So the component of the free rows has at least 3ρ² + 3ρ + 1 − 39676w² − 226w points, which is more than half of Ω when
    ρ ≥ 302w.
- **Uniqueness and monotonicity.**
  - Uniqueness is clear.
  - If P ⊆ P′, then Fr(P′) ⊆ Fr(P). So M(P′) is a connected subset of Fr(P) holding more than half of Ω, and lies in M(P). ∎

## 9. Width

**The game.** Let 𝓗 be a nonempty set of partial assignments with three properties:
- no member falsifies a clause;
- it is closed under restriction;
- every f ∈ 𝓗 with |dom f| < w extends, within 𝓗, to any further variable.

Then no resolution refutation has width below w.
- **Why.** Show by induction along the refutation that every clause C with fewer than w variables is satisfied by each f ∈ 𝓗 with
  dom f = vars(C).
- **Axioms.** An axiom is not falsified by f, so it is satisfied.
- **Resolution steps.** For a step from C ∨ x and D ∨ ¬x to C ∨ D:
  - extend f to x;
  - restrict the extension to the two premises' variables, which keeps it in 𝓗;
  - one of the premises is satisfied without its x-literal, so f satisfies C ∨ D.
- **The empty clause** would be satisfied by ∅: impossible. (This is the existential pebble game of Atserias–Dalmau.)

**Proof of Theorem A.** Let k ≥ 1812w + 6, so k ≥ 36 and ρ ≥ 302w. Let f ∈ 𝓗 when two conditions hold:
- |dom f| ≤ w;
- some label state with vortex y ∈ M(dom f) (straight cut system) has a colouring that agrees with f.

The four requirements:
- **Nonempty.** ∅ ∈ 𝓗: M(∅) = Ω, and the flat state works.
- **No falsified clause.** y ∉ D(dom f) ⊇ dom f. Lines not through y are satisfied (Lemma 2.1), and lines through y contain the
  unassigned y.
- **Restriction.** Restrictions stay in 𝓗 because M(dom f) ⊆ M(dom f′) for dom f′ ⊆ dom f.
- **Extension.** Let P = dom f, q a new point and P′ = P ∪ {q}.
  - Pick y′ ∈ M(P′) ⊆ M(P), and a path from y to y′ inside M(P).
  - Move the vortex along it one step at a time. Each step is allowed by Lemma 7.1, since every point of the path lies in
    Ω ∖ D(P) and is not a pebble.
  - At y′, extend f by the state's colour at q. Then y′ ∈ M(P′).

So every refutation has width at least w. ∎

**Upper bounds.**
- **Width.** The primal graph is planar with treewidth O(k). Davis–Putnam elimination along a tree decomposition refutes in width
  O(k).
- **Size.** The same elimination has size n·2^{O(k)} = n^{O(1)}·2^{O(√n)} (`TWO-ROUND-BRIDGE-20261106-001B`).

## 10. Islands

**Islands.**
- **The packing.** An island packing is a set of centres c, at distance at least 5 from the corner points, pairwise at distance at
  least 47. Each island is I = B(c, 1), with 7 points and no corner point; points of different islands are at least 45 apart.
- **The restriction ρ.** Each island gets a label λ_I ∈ Z6 in a frame developed inside I, which is consistent because I contains no
  corner face. ρ fixes every island point to that label's colour.
- **Zones.** The zone Z is the set of points within distance 6 of an island. The vortex will stay outside it.

**Lemma 10.1 (terms).** Let y ∈ Ω ∖ Z, with its straight cut system and weights.
- **The representatives.** Window starts can be chosen with A_p ∈ [−3, 6] at island points and a_p ∈ [0, 5] at other pebbles.
- **The terms.** With these, τ(p, q) = ⌊(d_y(p, q) + A_p + 2 − A_q)/6⌋ satisfies:
  - (i) τ ≥ 0 for p, q in the same island;
  - (ii) τ ≥ 1 for p, q in different islands;
  - (iii) τ ≥ −2 always.

*Proof.*
- **One arc per island.**
  - An arc crossing an edge inside I passes within distance 1 of I's centre c. Two such arcs would put c within distance 1 of two
    arcs at an angle of at least 27°, hence within 2/sin 27° < 4.5 of y's centroid.
  - But dist(y, I) ≥ 7, and graph distance 7 means Euclidean distance at least 7·√3/2 > 6.
  - A segment meets the convex hexagon I once, so at most one arc crosses I, and it crosses I's edges all in one direction.
- **The lifts.**
  - Let λ_p (p ∈ I) be the integers with λ_b = λ_a − t(a, b) on every edge inside I, and λ ≡ the island's label in the global
    frames. This is consistent because the holonomy inside I is 0.
  - So λ takes at most two values on I, which differ by 1. Choose λ_c ∈ [0, 5].
  - Each island point's colour allows the window [λ_p − j_p, λ_p − j_p + 2] for some j_p ∈ {0, 1, 2}. Set A_p = λ_p − j_p ∈ [−3, 6].
- **(i).** It suffices that d(p, q) ≥ λ_q − λ_p, since A_p + 2 − A_q ≥ λ_p − λ_q.
  - Let β be a shortest simple path from p to q.
  - **d(β) ≥ 1:** the claim holds because |λ_q − λ_p| ≤ 1.
  - **d(β) = 0:** all steps weigh 0. A second step would make β's second point a member of X0 ⊆ B(y, 3), but that point is adjacent
    to I and so at distance at least 6 from y. So β is a single zero-weight edge inside I, where t(p, q) = 1 and λ_q = λ_p − 1.
- **(ii).** dist(p, q) ≥ 45, so d(p, q) ≥ 13 (Lemma 6.1) and τ ≥ ⌊(13 − 3 + 2 − 6)/6⌋ = 1.
- **(iii).** d ≥ 0 and A_p + 2 − A_q ≥ −3 + 2 − 6. ∎

**Lemma 10.2.** Let D_I(P) = {x : |P ∩ B(x, s)| ≥ s/900 for some s ≥ 1}.
- **(a)** The islands alone admit a label state with vortex y, for every y ∈ Ω ∖ Z.
- **(b)** Suppose P ∪ islands admit a state with vortex y ∈ Ω ∖ Z; y′ ∈ Ω ∖ Z is adjacent to y and y′ ∉ P; and y ∉ D_I(P). Then
  they admit one with vortex y′.

*Proof.*
- **(a).** A cycle inside one island has all terms at least 0. A cycle visiting two or more islands has at least two terms of at least
  1, and none negative. So no cycle is negative.
- **(b), the certificate.** Otherwise Lemma 4.1, with the island points as pebbles, gives a negative cycle at y′ whose walk passes
  through y.
- **(b), the blocks.** Split its members into r real pebbles and V maximal runs inside one island. Use Lemma 10.1 at y′:
  - consecutive runs belong to different islands and contribute at least 1;
  - at most 2r transitions touch a real pebble, each contributing at least −2;
  - the rest contribute at least 0.
- **(b), the count.**
  - So −1 ≥ (V − r) − 4r, which gives V ≤ 5r − 1, and r ≥ 1 by (a).
  - The cycle has at most r + 7V < 36r members, so Σ d′_i < 108r.
  - Every real pebble on B lies within Σ(2d′_i + 19) < 216r + 19·36r = 900r of y. So y ∈ D_I(P), a contradiction. ∎

**Lemma 10.3.** Let ρ ≥ max(119, 11000w) and |P| ≤ w. Then Fr_I(P) = Ω ∖ (D_I(P) ∪ Z) has a component M_I(P) holding more than half
of Ω's points. It is unique, and M_I(P′) ⊆ M_I(P) for P ⊆ P′.

*Proof.*
- **Very free rows.**
  - Cover D_I(P) ∩ Ω by balls B(x_i, 3s_i) as in Lemma 8.1, now with Σ s_i ≤ 900w.
  - Work in Ω⁻, the hexagon of radius ρ − 16 about o. A row of Ω⁻ is very free if its offset differs by at least 17 from that of
    every row meeting a covering ball. At most 5435w rows of each direction are not very free.
- **Detours around zones.**
  - Where a very free row meets the zone of an island with centre c, it detours along the hexagonal ring of radius 8 about c.
  - That ring lies outside every zone: zones are within 7 of their centres, and centres are 47 apart.
  - It lies on rows within 15 of the very free row, so it misses the covering balls.
  - It lies inside Ω.
- **One component.** The connection argument of Lemma 8.1 then applies to very free rows with their detours. It needs
  (ρ − 16)/2 + 1 > 5435w, which holds.
- **Counting.**
  - Points of Ω⁻ on no very free row: at most (5435w)².
  - Zone points: each centre owns a disjoint ball of radius 23 (1,657 points) and a zone of at most 169 points. So
    |Z ∩ Ω| ≤ 0.102·|hex(ρ + 30)|.
  - The component therefore holds at least |hex(ρ − 16)| − (5435w)² − 0.102|hex(ρ + 30)| > |Ω|/2 points for ρ ≥ 119 and
    w ≤ ρ/11000. ∎

**Theorem 10.4.** For every island packing ρ, every resolution refutation of NAE(K_k)|ρ has width at least
w_I = ⌊⌊k/6⌋/11000⌋, whenever ⌊k/6⌋ ≥ 119.

*Proof.* As for Theorem A, with three changes:
- assignments live on non-island points;
- states must agree with ρ on the islands;
- vortices lie in M_I(dom f).

The family's properties:
- **Nonempty.** By Lemma 10.2(a).
- **No falsified clause.** The only violated line passes through the vortex, which is neither fixed by ρ (it lies outside Z) nor
  pebbled.
- **Extension.** It walks the vortex inside M_I(P) using Lemma 10.2(b). ∎

## 11. Size

**The random restriction.**
- **Proposals.** Every point at distance at least 5 from the corner points proposes itself as a centre independently, with
  probability ε = 1/M, where M = |B(47)| = 6769. This bounds every ball of radius 47 in G, since G has nonnegative curvature.
- **Keeping.** A proposal is kept when no other proposal lies within distance 47. Kept centres are then at least 48 apart, so their
  islands form a packing as in §10.
- **Labels.** Each island gets an independent uniform label.

**Properties.**
- **(P1) Coverage.** Take a point p at distance at least 6 from the corner points. Then p is fixed with probability at least
  Σ_{c ∈ B(p,1)} ε(1 − ε)^{M−1} ≥ 7/(eM) =: p₀.
  - The seven events "c is kept" are disjoint, because kept centres are 48 apart.
  - Each centre c has at most M − 1 competitors.
- **(P2) Fair colours.** Given that p is fixed, its colour is uniform: three of the six labels give each colour. So a literal on p is
  satisfied with probability at least q = p₀/2.
- **(P3) Locality.** Whether p is fixed, and its colour, depend only on proposals within distance 48 of p and on one label. Events for
  points more than 96 apart are independent. V = |B(96)| = 27,937.
- **(P4) Corners.** At most N_c = 1092 points lie within distance 5 of a corner point.

**Proof of Theorem B.** Let Π be a refutation of size S and W₀ = w_I.
- **Wide clauses die.** Take a clause with W ≥ W₀ literals. Discard its literals near the corners, then greedily keep literals on
  points pairwise more than 96 apart. At least (W − N_c)/V remain. By (P2) and (P3) the clause survives ρ with probability at most
  (1 − q)^{(W − N_c)/V}.
- **The union bound.** If S·(1 − q)^{(W₀ − N_c)/V} < 1, some ρ satisfies every clause of Π with at least W₀ literals. Then Π|ρ refutes
  NAE(K_k)|ρ in width below W₀, contradicting Theorem 10.4.
- **The bound.** So S ≥ 2^{α(W₀ − 1092)}, with α = −log₂(1 − q)/V = 9.82·10⁻⁹ (check 9). Since W₀ ≥ k/66000 − 2, the size is
  2^{Ω(k)}, with an absolute constant near 10⁻¹³. ∎

## 12. Grid Sperner

**Setting.**
- **The grid.** Vertices (a, b) with a, b ≥ 0 and a + b ≤ m, at positions (a + b/2, b√3/2).
- **The boundary.** It is fixed as in `FLAT-STATES-20261107-001B`. The corners are coloured 0, 1, 2, and each side takes its far
  corner's colour after its first vertex. So the three doors, where the boundary's colour changes, are the boundary edges next to
  the corners.
- **The core.** The vortex is a down-pointing small triangle whose centroid lies within m/6 of the grid's centroid.

**Label states.**
- **The arcs.** Three straight arcs run from the vortex's centroid to just beyond the three doors, each rotated slightly.
- **Shifts and frames.** τ(u, v) ∈ {−1, 0, 1} is the signed crossing of an edge by the arcs. The frame φ(v) ∈ Z3 is the developed
  sum of τ, consistent because τ's holonomy is 3 ≡ 0 around the vortex and 0 around other triangles.
- **States.** A state is an integer height h with |h(v) − h(u) + τ(u, v)| ≤ 1 on every edge, read as colours h + φ (mod 3).
- **Fully labelled triangles.** Every triangle except the vortex sees two consecutive values, so it is not fully labelled. The
  vortex is fully labelled and oriented like the boundary.
- **The flat boundary.** The fixed boundary colours are a flat state: every boundary vertex has the same window start
  colour − φ (check 8). The boundary's colour steps by +1 exactly where the arcs cross it.

**The ingredients carry over with these changes.**
- **Windows of size 1.**
  - Pebbled colours fix h mod 3: s_q − s_p ≤ ⌊(d(p, q) + a_p − a_q)/3⌋.
  - A negative cycle with m′ members has Σ d ≤ 2m′ − 3.
- **Local lemma and distance lemma.**
  - Check 7 decides exactly that three rays from a down-triangle's centroid, within 20° of 90°, 210° and 330°, meet disjoint faces
    beyond the vortex. At most 3 points, the vortex's own vertices, can be junctions.
  - Directions from the core deviate by less than 19°.
  - So d ≥ (dist − 4)/2 (checked: check 8).
- **Single steps.**
  - Move between down-triangles D₁, D₂ that share a vertex u.
  - Removing the two edges of the up-triangle between them merges D₁, it and D₂ into one face. Both cut systems give that face
    holonomy 3, so they are gauge-equivalent on what remains.
  - A certificate must therefore use one of the two removed edges, and both contain u.
- **Boundary terms.**
  - All boundary window starts are equal, so boundary–boundary terms are ⌊d/3⌋ ≥ 0.
- **Depth (no islands).**
  - Suppose a certificate through a vortex vertex u at depth D₀ uses a boundary member. Take the stretch of B between the nearest
    boundary members before and after u.
  - Its weight is at least D₀ − 4 by the distance lemma, and its terms add up to at least (D₀ − 4 − 4(j + 1))/3, where j ≤ r is its
    number of real pebbles.
  - Every other term is at least −1 at a real pebble and at least 0 otherwise.
  - So a negative cycle forces D₀ ≤ 10r + 5.
  - Core vertices lie at least m(√3 − 1)/6 from each side in Euclidean terms, so D₀ ≥ 0.14m − 1 ≥ m/8 for m ≥ 64.
  - With m ≥ 200 and r ≤ w ≤ m/100, certificates through the vortex use only real pebbles.
- **Pure certificates.** Every real pebble lies within Σ(2d_i + 4) ≤ 8r of u.
  - Bad set D_S(P) = {x : |P ∩ B(x, s)| ≥ s/8 for some s}.
  - Anchors are kept at distance at least 2 from it, so every triangle at an anchor avoids it.
  - The free component follows by Lemma 8.1's row count.

**Width.** The game of §9 then gives width Ω(m), by the same proof.

**Size.**
- **Islands.**
  - Islands B(c, 1) have centres at distance at least 2 from the boundary, so they never contain boundary vertices.
  - Centres are at least 8 from the three corners and pairwise at least 20 apart, so islands are at least 18 apart.
  - Every interior vertex at distance at least 9 from the corners can be covered.
- **Representatives.** An island near the boundary is crossed by no arc: arcs meet the boundary only at the doors, near the
  corners. Its window start can be chosen in {−1, 0, 1} relative to the boundary's.
- **Terms.**
  - Boundary–island terms are at least 0 (check 8). An adjacent pair has d ≥ 1, since no zero-weight edge joins them, and
    ⌊(1 + 0 − A)/3⌋, ⌊(1 + A − 0)/3⌋ ≥ 0.
  - Same-island terms are at least 0, between-island terms at least 1 (d ≥ 7 at distance 18), and terms at real pebbles at least −2.
- **Depth with islands.**
  - In the stretch from the boundary to u:
    - island–island terms are at least max(1, (d − 4)/3) ≥ d/7;
    - same-island hops weigh at most 4, and there are at most six per island visit;
    - the other terms are at least (d − 4)/3.
  - This gives a weight of at most 31·(its terms) + 144j + 32. A negative cycle forces D₀ ≤ 268r + 5.
- **Pure certificates with islands.** These are counted as in Lemma 10.2: u lies within 288r of every real pebble.
- **The restriction.** The random restriction of §11 then gives size 2^{Ω(m)}.

**Itsykson et al.'s CSP.** Their 2D Sperner CSP lets the side vertices choose between their side's two colours. Fixing those colours
restricts it to Sperner_m, and restriction never increases width or size. So the same bounds hold for it.

## 13. Final literature check (2026-11-07)

Web searches, standard and extended, on:
- resolution width and size for 2D Sperner and grid principles;
- Göös et al.'s TFNP characterizations;
- height-function or vortex principles in proof complexity;
- cutting planes, Res(⊕) and parity resolution on planar not-all-equal or Sperner formulas;
- 2024–2026 work on Sperner in proof complexity.

| Source | What it gives | Relation |
| --- | --- | --- |
| Itsykson, Malova, Oparin, Sokolov, *Tree-like resolution complexity of two planar problems* ([arXiv:1412.1124](https://arxiv.org/abs/1412.1124)) | Tree-like size 2^{Θ(n)} for the 2D Sperner CSP and a grid matching CSP | Theorem C extends this to general resolution (width and size) |
| Crescenzi–Silvestri; Friedl, Ivanyos, Santha, Verhoeven ([quant-ph/0505185](https://arxiv.org/abs/quant-ph/0505185)) | Query complexity Θ(√N) of 2D Sperner | Consistent: width Θ(√n) is a proof-complexity counterpart |
| Dantchev–Riis, *Planar tautologies hard for resolution* (FOCS 2001); Alekhnovich 2004 | Mutilated chessboard and grid Tseitin need size 2^{Ω(n)} | The paradigm adapted in §11 |
| Göös, Hollender, Jain, Maystre, Pires, Robere, Tao, *Separations in Proof Complexity and TFNP* (JACM 2024; [arXiv:2205.02168](https://arxiv.org/abs/2205.02168)) | PPADS = unary Sherali–Adams; resolution is not simulated by unary Sherali–Adams | `COUNT-NOTE-20261107-001B` places the count in PPADS^dt; here resolution is far weaker on it |
| Dantchev, Galesi, Ghani, Martin (stabbing planes, 2021–22) | A "Sperner's theorem" (antichain) method for stabbing planes | Unrelated despite the name |

**Not found:**
- any general-resolution width or size bound for 2D Sperner;
- any proof-complexity treatment of height functions with vortices;
- any cutting-planes or Res(⊕) result on these formulas.

**Folklore risk.**
- Moderate for the method: experts would expect the Atserias–Dalmau and Dantchev–Riis paradigms to extend.
- Low for the statements about K_k.
- Moderate for grid Sperner, whose statement is natural enough that an unpublished proof may exist.

## 14. Checks

`check.py` (`result.json`), about 4 minutes:

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Local lemma at a sphere vortex (exact, all critical intervals) | no faces shared within radius 5; at most 18 junctions, all within distance 3 |
| 2 | Arc directions over every core vortex of K_36 and K_48 | at most 17.6° (near corners) and 8.8° (far corners) from ideal |
| 3 | Straight cut systems for all 335 core vortices of K_12, …, K_36 | arcs disjoint; each flat state violates one line, through z; \|X0\| ≤ 7, within distance 2 |
| 4 | Distance lemma on K_24 and K_36 | d ≥ (dist − 19)/2, slack at least 8.5 |
| 5 | Single steps on K_30 | 11 of 11 blocked steps have certificates through the old vortex, within budget, with pebbles within distance r |
| 6 | Islands on K_48 and K_60 (3 and 5 islands, separation 45) | same-island terms ≥ 0 (least 1), between-island terms ≥ 1 (least 7), starts in [−2, 5], islands alone admit a state |
| 7 | Local lemma for grid Sperner (exact) | no faces shared beyond the vortex; at most 3 junctions |
| 8 | Grid Sperner, all 408 core triangles of m = 24, 36, 48 | boundary flat; only the vortex fully labelled; \|X0\| ≤ 3; d ≥ (dist − 4)/2; boundary and boundary–island terms ≥ 0 |
| 9 | Size constants | radius-20 balls never exceed the flat count (1261); p₀ = 3.8·10⁻⁴, α = 9.82·10⁻⁹ |

## 15. What this does not establish

- **Constants.** Optimal constants, or any fine-grained exponent; c ≈ 10⁻¹³.
- **Decorations.** The decorated three-fold spaces of `TWO-ROUND-BRIDGE-20261106-001B` are not covered.
- **Stronger systems.** Cutting planes, Res(⊕) and bounded-depth Frege are not covered. `COUNT-NOTE-20261107-001B` places the count in
  unary Sherali–Adams and records solver behaviour only.
- **Computer-assisted steps.**
  - The local lemmas (checks 1 and 7) are computer-assisted. They evaluate one direction inside each open interval between critical
    angles, in floating point, with a tolerance of 10⁻⁹ that the generic rotation keeps clear.
  - The ball-size bound of §11 is argued from the cone points' smaller angle and confirmed near every corner of K_48 (check 9).
- **Review.** No human or external review has been made.
