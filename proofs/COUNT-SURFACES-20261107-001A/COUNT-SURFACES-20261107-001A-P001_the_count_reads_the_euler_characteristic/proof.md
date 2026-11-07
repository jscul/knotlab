# The knot's count reads the Euler characteristic

Status: Proved by hand (theorems 1–5). The finite claims are checked by computation with controls (`check.py`). §6 is computation
only.

Ticket `COUNT-SURFACES-20261107-001A`, 2026-11-07.

## Standard statement

**Setting.**
- Let T be a triangulation of a closed connected surface S whose triangles are coloured in two colours, with neighbours differing.
- The **points** are the triangles of colour 0 and the **lines** those of colour 1. A point lies on a line once for every side they
  share.
- The incidence graph B (one edge per side of T) is the dual cellulation of S, so B's faces are T's vertices. Every vertex has even
  degree, and the vertex v carries d_v line corners (half its degree).
- A **signing** s puts a bit on every side. A line's not-all-equal constraint reads its three literals x_p xor s(side).
- A line's **corner** at a vertex v is the pair of its two sides at v. Under an assignment the corner **agrees** when those two
  literals are equal. A satisfied line has one agreeing corner, a violated (monochromatic) line three.
- Write agree_v for the number of agreeing corners at v, viol for the number of violated lines, n for the number of points (= lines)
  and χ for the Euler characteristic of S.

**Theorem 1 (parity).** Under every assignment, agree_v ≡ d_v + flip_v (mod 2), where flip_v is the sum of the signs on the sides of
v's corners.

**Theorem 2 (signings).**
- The vertices where agree_v is even form a set D(s) with |D| ≡ χ (mod 2), and every vertex set of that parity occurs.
- For each D, the signings with even set D form 2^(2 − χ) classes up to gauge (flipping a variable, or complementing a line's three
  literals).
- In particular, signings with no even vertex, the Kasteleyn signings, exist iff χ is even.

**Theorem 3 (the count).** Under every assignment,

  viol − Σ_v ⌊agree_v / 2⌋ = (χ − |D|) / 2.

- **Which side is forced.** The count forces a violated line iff χ > |D|, which happens only on the sphere with no even vertex. It
  forces some vertex to over-agree (⌊agree_v / 2⌋ ≥ 1) iff χ < |D|. When χ = |D| it forces nothing.
- **Membership.** In both forced cases the identity is a Sherali–Adams refutation with integer coefficients, of degree max(3, d_v).
  It refutes the line constraints in the first case and the vertex constraints in the second. The forced search problems therefore
  lie in PPADS^dt when the vertex degrees are bounded.
- **Orientability** enters nowhere. No search problem forced by the count, on any surface, is PPA^dt-hard.

**Theorem 4 (matchings).**
- **Each satisfying assignment and its complement** give the same corner map A: one agreeing corner per line, with vertex degrees odd
  off D and even on D.
- **Each such corner map A** is accepted by exactly one of the 2^(2 − χ) sign classes. It is the corner map of exactly two
  assignments in that class and of none in the others.
- **When χ = |D|** the corner maps are the perfect matchings of the lines with the vertices outside D. So the satisfying assignments
  are, two to one, the perfect matchings in one mod-2 homology class prescribed by the signs.

**Theorem 5 (lattice tori).** Let L ⊆ Z² have index N and Hermite basis (p, 0), (q, r), and let T(L) be the triangular lattice modulo
L. Every vertex has degree 6, so the all-zero signing has no even vertex, and the four sign classes are the twists ω ∈ Hom(L, F2).
1. **The criterion.** Class ω is satisfiable iff the triangle conv{(0, 0), (p, q), (0, −r)} has an integer point (s, t) with
   ((p + s) mod 2, (q + r + t) mod 2) = (ω(p, 0), ω(q, r)).
2. **The classification.** A class is unsatisfiable exactly in three cases:
   - one class on each **degenerate** torus (L contains a unit vector, so some line repeats a point);
   - one class on each **thin** torus (L contains a vector of norm² 3, circumference √3) of **even** index;
   - the untwisted class of the two **Fano tori** (N = 7, L = ⟨(7, 0), (2, 1)⟩ or ⟨(7, 0), (4, 1)⟩), whose points and lines form
     the Fano plane.
3. **Thin tori are cyclic chains.** Every line holds three consecutive points of one cycle. Binary search finds a violated line of
   an unsatisfiable class with at most 2⌈log₂ n⌉ + O(1) queries, so the false-clause search is in FP^dt.

## Nearest known results

- **Kasteleyn's condition on surfaces.**
  - Theorem 1's parity is the bipartite Kasteleyn condition: a face of length 2d needs sign product (−1)^(d+1).
  - Kasteleyn (1963); Cimasoni–Reshetikhin (CMP 2007), where Kasteleyn orientations exist iff the vertex count is even and form
    H¹-torsors; Cimasoni, *Dimers on graphs in non-orientable surfaces* (LMP 2009), with 2^(2 − χ) Pfaffians.
  - Theorems 1–2 restate this for not-all-equal corners. The T-join proof below is self-contained.
- **The plane.**
  - `TWO-ROUND-BRIDGE-20261106-001B` (χ = 2, D = ∅: F = L + 2 forces a violated line).
  - `COUNT-NOTE-20261107-001B` (the degree-3 ±1 Sherali–Adams certificate).
  - `COUNT-TFNP-20261107-001B` (PPADS^dt-complete on the octahedral spheres).
- **Height changes on tori.**
  - Kenyon–Okounkov–Sheffield, *Dimers and amoebae* (Annals 2006): the Newton polygon is the set of slopes.
  - Ibeas Martín, *Full support of the Kasteleyn operator associated with a bipartite toroidal graph* (arXiv 1206.5178, 2012): every
    integer point of the Newton polygon is realized by a perfect matching.
  - Lemma 5.1 is the honeycomb case, with an elementary floor construction. The delta is the parity reading, sign class ↔ parity of
    an integer point, and the classification it gives.
- **Antiferromagnets on triangulations.**
  - On lattice tori the satisfying assignments are the zero-frustration ground states of the triangular Ising antiferromagnet
    (Wannier 1950), with periodic (untwisted) or antiperiodic (twisted) couplings. Equivalently they are honeycomb dimers (Blöte–
    Hilhorst 1982).
  - Jiménez–Kiwi (arXiv 1107.3767, 2011): for the closely related "satisfying spin assignments" of triangulations of orientable surfaces
    of unbounded genus, deciding existence is NP-complete and counting is #P-complete. Ground states correspond to perfect matchings
    of the dual, with degeneracy at most twice their number (the 2-to-1 of theorem 4).
- **Sperner on surfaces.** Friedl–Ivanyos–Santha–Verhoeven (CIAC 2006): locally 2-dimensional Sperner problems are complete for PPAD,
  PPADS and PPA, with PPA on non-orientable surfaces. Theorem 3 contrasts with this.
- **Classes.**
  - PPADS^dt = unary Sherali–Adams (Göös, Hollender, Jain, Maystre, Pires, Robere, Tao, JACM 2024, corollary 4).
  - Beame–Cook–Edmonds–Impagliazzo–Pitassi (JCSS 1998) proved all separations possible among PPA^dt, PPAD^dt, PPADS^dt and PPP^dt
    (stated so in that survey); in particular LONELY does not reduce to PIGEON, so PPA^dt ⊄ PPP^dt ⊇ PPADS^dt.
- **Classification.**
  - Known-with-delta for theorems 1, 2 and 5.1.
  - New as far as found: theorem 3 (the defect identity and which side it forces), theorem 4 for the knot's constraints, theorem 5.2's
    list of unsatisfiable lattice tori, and the reading that the count's forcing is orientation-blind.
  - Folklore risk: moderate for 5.2. The antiferromagnet literature on boundary conditions may contain it in another language; a
    bounded search found sector discussions (Nourhani–Crespi–Lammert, J. Phys. A 2023) but no such list.

## 1. Parity

*Proof of theorem 1.*
- Walk around v. Its corners are c_1, …, c_d in lines l_1, …, l_d, and the points between them are p_1, …, p_d, so c_i joins p_i and
  p_{i+1} (indices mod d).
- Corner c_i disagrees iff x_{p_i} + s(l_i, p_i) + x_{p_{i+1}} + s(l_i, p_{i+1}) = 1. Summing over i, every x_{p_i} appears twice,
  so the number of disagreeing corners is ≡ flip_v (mod 2).
- Hence agree_v = d_v − disagree_v ≡ d_v + flip_v. ∎

## 2. Signings

*Proof of theorem 2.*
- **Signings as chains.** A signing is a set of sides, that is a 1-chain on T's 1-skeleton over F2. Every side at v borders exactly one
  line corner at v per endpoint at v, so flip_v is the degree of v in s (mod 2).
- **Prescribing D.** By theorem 1, D(s) = D iff deg_s(v) ≡ d_v + 1 + [v ∈ D] for every v. This is a T-join problem on the connected
  1-skeleton, solvable iff the number of odd targets is even.
- **The parity.** T has 2n triangles and 3n edges, so V = n + χ by Euler's formula. Then

    Σ_v (d_v + 1 + [v ∈ D]) = 3n + (n + χ) + |D| ≡ χ + |D| (mod 2),

  so D occurs iff |D| ≡ χ.
- **The classes.** Two signings with the same D differ by a cycle of the 1-skeleton.
  - Flipping a point's variable complements its three literals, which adds the boundary of its triangle.
  - Complementing a line's three literals leaves its constraint unchanged, which adds the boundary of the line's triangle.
  - So the gauge group is the boundary space B_1(T), and the classes form Z_1 / B_1 = H_1(S; F2), of dimension 2 − χ for any closed
    connected surface. ∎

## 3. The count

*Proof of theorem 3.*
- **Two ways to count.** Each corner lies in one line and at one vertex, so Σ_l agree_l = Σ_v agree_v.
- **The line side.** A line has 1 agreeing corner if satisfied and 3 if violated, so Σ_l agree_l = n + 2 viol.
- **The vertex side.** By theorem 1, agree_v = 2⌊agree_v / 2⌋ + [v ∉ D]. So Σ_v agree_v = 2E + V − |D| = 2E + n + χ − |D|, with
  E = Σ_v ⌊agree_v / 2⌋.
- Equating the two gives the identity. ∎

**Which side is forced.**
- The identity gives viol ≥ (χ − |D|)/2 and E ≥ (|D| − χ)/2.
- A closed surface has χ ≤ 2, with equality only for the sphere. Since |D| ≡ χ, the case χ > |D| ≥ 0 means χ = 2 and D = ∅: the
  Kasteleyn sphere.
- The case χ < |D| occurs, for example:
  - with no even vertex on every surface with χ < 0 (orientable genus ≥ 2: E ≥ g − 1);
  - with the three degree-4 corners even on the hexagonal projective plane (the all-zero signing: E ≥ 1);
  - with the six corners even on the octahedral sphere (the all-zero signing: E ≥ 2).

**Refutations.**
- **The polynomials.** Read agree, viol and ⌊agree_v / 2⌋ as polynomials in the points' variables. viol_l is the sum of the two
  falsifying conjunctions of line l's clauses. ⌊agree_v / 2⌋ is a nonnegative integer combination of the conjunctions of v's d_v
  points on which v over-agrees, each of which falsifies one of v's constraints (agree_v ≤ 1 off D, agree_v = 0 on D).
- **The refutations.** With M = |χ − |D||/2 ≥ 1:
  - for χ > |D|, Σ_l viol_l − E = M refutes the lines;
  - for χ < |D|, E − Σ_l viol_l = M refutes the vertices.
- **Normalizing.** Subtracting (M − 1)·(x_1 + (1 − x_1)) gives the constant 1. All coefficients are integers bounded by max(d_v, M),
  so this is a unary Sherali–Adams refutation of degree max(3, d_v).
- **The class.** By Göös et al., the false-clause search problem is in PPADS^dt for bounded d_v.
- **Orientability.** No step used an orientation of S. Since PPA^dt ⊄ PPADS^dt, no forced problem here is PPA^dt-hard, unlike
  Sperner on non-orientable surfaces.

## 4. Matchings

*Proof of theorem 4.*
- **From an assignment.** Let x satisfy every line. Its agreeing corners A(x) have one corner per line, and by theorem 1 the vertex
  degrees are deg_A(v) ≡ [v ∉ D]. The complement x̄ has the same agreements. When χ = |D|, theorem 3 gives E = 0, so deg_A(v) =
  [v ∉ D] exactly: a perfect matching of the lines with the vertices off D.
- **The point graph P.** Fix such an A. The assignments with A(x) = A solve, over F2, one equation per corner (l; a, b):

    x_a + x_b = s(l, a) + s(l, b) + [corner ∉ A].

  - **Its faces.** Draw each corner as an arc from a's triangle to b's through l near the corner's vertex, crossing the sides (l, a)
    and (l, b). The point graph P (points; corners as edges) is then cellularly embedded in S. Its faces are the line triangles and
    the vertex polygons, and its Euler characteristic is n − 3n + (n + V) = χ.
  - **Solvability.** The system is solvable iff the right side sums to 0 around every cycle of P. When it is, it has exactly the two
    solutions x and x̄, since P is connected.
- **Face cycles impose nothing.**
  - Around a line triangle the sum is 2(…) + (3 − 1) ≡ 0.
  - Around the polygon of v it is flip_v + d_v − deg_A(v) ≡ [v ∉ D] − [v ∉ D] = 0.
  - So the conditions factor through H_1(P; F2) = H_1(S; F2): A is accepted by s iff the functional
    Φ_{A,s}(γ) = Σ_{corners of γ} (s-terms + [∉ A]) vanishes.
- **Changing the class.** Gauge changes do not affect acceptance. Changing s by a cycle z of T's 1-skeleton (a flat signing) adds to
  Φ the sum of z over the sides γ crosses. That is the mod-2 intersection number of z with γ.
- **Exactly one class.** The mod-2 intersection pairing on H_1(S; F2) is nondegenerate (Poincaré duality with F2 coefficients, valid
  for non-orientable S). So as [z] ranges over H_1, Φ ranges over all of Hom(H_1, F2), and exactly one class gives Φ = 0. ∎

## 5. Lattice tori

**Coordinates.**
- Points are up(i, j) ↔ (i, j) ∈ Z², and the line down(i, j) holds up(i, j), up(i + 1, j) and up(i, j + 1).
- The vertex (a, b) of T is the co-line {up(a − 1, b), up(a, b), up(a, b − 1)}.
- The steps f1 = (1, 0), f2 = (−1, 1) and f3 = (0, −1) sum to zero. They go around every line and every co-line.
- Lifting to the plane, the twist ω becomes twisted periodicity. A class-ω assignment is an x: Z² → F2, not-all-equal on every line,
  with x(p + u) = x(p) + ω(u) for u ∈ L. This is how `check.py` labels classes: by the holonomy of the signs along (p, 0) and (q, r).

**Lemma 5.1 (heights).** Class ω is satisfiable iff some G ∈ Hom(L, Z) has a linear extension in
Δ' = {G(1, 0) ≥ 0, G(0, −1) ≥ 0, G(1, 0) + G(0, −1) ≤ 1} and satisfies G ≡ ω + ω_C (mod 2), where ω_C(a, b) = a + b.

*Proof.*
- **Only if: the height function.**
  - Since χ = 0 = |D|, theorem 3 makes every co-line, like every line, hold exactly one agreeing pair.
  - Set Δh = 1 across a disagreeing step and −2 across an agreeing one. Around every line and co-line this sums to 0, so h is
    well-defined on the simply connected plane, with h ≡ x (mod 2) and h ≡ i − j (mod 3).
  - **The function g.** With h = (i − j) − 3g, the increments of g along (1, 0), (0, −1) and (1, −1) lie in {0, 1}.
  - **Periodicity.** The agreement pattern is L-periodic (adding ω(u) to both ends keeps agreement). So g(p + u) = g(p) + G(u) for a
    G ∈ Hom(L, Z), and x(p + u) − x(p) ≡ h(p + u) − h(p) ≡ (u_a + u_b) + G(u). That is, ω = ω_C + G.
  - **The slope.** Since N·(1, 0), N·(0, −1) and N·(1, −1) lie in L and each is a sum of N steps worth 0 or 1, G's linear
    extension lies in Δ'.
- **If: the floor construction.**
  - Given such G, let g(p) = ⌊G(p) + θ⌋. Its steps along the three directions are ⌊y + G(f)⌋ − ⌊y⌋ ∈ {0, 1}, because G(f) ∈ [0, 1].
    Also g(p + u) = g(p) + G(u).
  - Reversing the dictionary gives Δh ∈ {1, −2} on every step, summing to 0 around each line. So each line has exactly one agreeing
    pair, and x = h mod 2 has class ω_C + G. ∎
- **In the Hermite coordinates.** s = G(p, 0) and t = G(q, r) make Hom(L, Z) = Z², and Δ' becomes the triangle
  conv{(0, 0), (p, q), (0, −r)}. The class is ((p + s) mod 2, (q + r + t) mod 2). This is criterion 5.1.

*Proof of theorem 5.2.* A class is missed iff its coset of 2·Hom(L, Z) avoids the triangle Δ'.
- **Slicing.** Take a primitive w ∈ L and complete it to a basis {w, v}, so (G(w), G(v)) are unimodular coordinates.
  - The triangle's levels G(w) = j run over an interval of length hex(w) = max(|w_a|, |w_b|, |w_a + w_b|), the graph distance in the
    lattice (its vertices sit at G(w) = 0, w_a and −w_b).
  - The slice at level j is a segment in G(v). Its longest slice has length ℓ = N / hex(w), because the area is N/2.
  - A slice of length ≥ 2 holds two consecutive integers, so it hits both parities of G(v).
- **Degenerate: w a unit vector.** One level is an edge of length N and the other a single vertex, so exactly one class is missed
  (N ≥ 2).
- **Thin: w of norm² 3** ((1, 1), (2, −1), (−1, 2) or their negatives).
  - The vertex levels are three consecutive integers. The two outer levels carry one vertex each, so their parity gets exactly the
    classes of those two vertices.
  - Their G(v)-values differ by v_a + v_b, by v_a, or by v_b respectively. In each case that is ≡ N (mod 2), since N = |det(w, v)|.
  - The middle level's slice has length N/2 and covers both classes of its parity once N ≥ 4.
  - So exactly one class is missed iff N is even.
- **No vector of hex ≤ 1 or norm² 3.** Let σ = min hex over L ∖ 0.
  - **σ = 2** (w of norm² 4, (2, 0) or its images). One parity's levels include an edge of length N/2; the other parity holds the
    interior slice, of length N/4. Every class is hit once N ≥ 8.
  - **σ ≥ 3.** Both parities of j have a slice of length ≥ ℓ/2:
    - the middle vertex's level, together with an adjacent level on its longer side;
    - or an edge level together with the level next to it.

    So every class is hit once N ≥ 4σ. By Hermite's bound λ₁² ≤ N and hex ≤ (2/√3)|·|, σ ≤ (2/√3)√N, so N ≥ 4σ whenever N ≥ 22.
- The degenerate and thin analyses are exact for their w whatever else L contains. A unit vector and a norm²-3 vector span a sublattice of
  index ≤ 2, so the two cases are exclusive for N ≥ 3.
- **Small indices.** For N ≤ 21 the cases are decided by computation (check 6, which runs SAT to N = 40 and the criterion to
  N = 120). The only exceptions outside the three families are the two Fano tori, which miss the untwisted class. The untwisted class
  is the all-zero signing, a 2-colouring of the Fano plane. ∎

*Proof of theorem 5.3.*
- **The chain.** If L contains w = (1, 1), φ(i, j) = i − j vanishes on L modulo N, and is a bijection from points to Z_N. Each line
  {(i, j), (i + 1, j), (i, j + 1)} has φ-values c, c + 1, c − 1. The functionals i + 2j and 2i + j do the same for (2, −1) and
  (−1, 2).
- **Binary search.** Query the points of slices 0 and 1 and cut the cycle there. Then keep an arc whose lines cannot all hold given
  the queried values at its two ends.
  - Splitting at the middle pair, one half inherits that property: otherwise their solutions agree on the shared pair and glue.
  - When the arc has ≤ 7 slices, query it all. A line inside it is violated.
- This takes at most 2⌈log₂ n⌉ + 8 queries (check 7: 20 queries at n = 1024). ∎

## 6. Other surfaces (computation)

| Family | Classes | Satisfiable |
| --- | --- | --- |
| Simple lattice Klein bottles Z²/⟨t_m, g_{h,c}⟩, m·h ≤ 64, both glide families c = 0, 1 | 4 each | 222 / 222 spaces, every class |
| Hexagonal projective planes, side 1–6, one or three even vertices (corner, three corners, random) | 2 each | 48 / 48 |
| Genus-2 double covers of seven lattice tori, branched at two vertices | 16 each | 17 / 17 spaces, every class |
| Double covers of K_2..K_4 branched at 4 corners (torus) / 6 corners (genus 2) | 4 / 16 | every class |
| Double covers of K_2..K_4 branched at 2 corners (a sphere, no even vertex) | 1 | none (the count) |
| Octahedral spheres K_2..K_5 with 2, 4 or 6 even vertices | 1 | all |

No Klein-bottle or projective-plane theorem is claimed. Every simple instance tested is satisfiable in every class.

## Checks

`check.py` (`result.json`), about 10 seconds:

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | 33 constructions (tori, Klein bottles, projective planes, spheres, double covers incl. one of a Klein bottle) | valid closed surfaces, two-coloured, links are cycles; χ and orientability as expected |
| 2 | Parity lemma; D-parity; realizability of every tested D of the right parity and of none of the other; Kasteleyn iff χ even; 2^(2 − χ) classes | pass on all 33 |
| 3 | The count identity on 792 assignments (random and Kasteleyn signings) | holds; lines forced only on spheres (and sphere covers), vertices whenever χ < \|D\| |
| 4 | Corner maps vs brute force on 9 small spaces (χ = −2..2, incl. 5,124 corner maps on a genus-2 cover) | each map accepted by exactly one class; #solutions = 2 × #accepted maps |
| 5 | Octahedral spheres K_2..K_5 | unsatisfiable with D = ∅, satisfiable with \|D\| = 2, 4, 6 |
| 6 | All 1,342 tori of index ≤ 40 by SAT; 10,631 more (index 41–120) by the criterion | SAT = criterion; unsatisfiable classes exactly: degenerate 1, thin-even 1, Fano 1, else 0 |
| 7 | Thin tori of even index up to n = 1024 | cyclic chains; binary search ≤ 20 queries at n = 1024 |
| 8 | Klein bottles, projective planes, genus-2 covers, sphere covers | §6 table |
| 9 | Controls | the identity with χ + 2 fails; a reflected triangle disagrees with SAT; counting every corner map for every class is wrong on the Fano torus; odd thin tori and the twisted Fano classes are satisfiable |

## Reading

**Interpretation, not a theorem.**
- **What the count reads.** The count is a discrete Poincaré–Hopf theorem. Give a line the index agree_l − 1 ∈ {0, 2} and a vertex
  1 − agree_v. The indices sum to χ, and the signs place the odd ones (the even vertices D) in advance.
- **Positive curvature (the sphere).** The defect must sit on a line: the knot's contradiction.
- **Negative curvature.** It must sit on the vertices: an over-agreeing face.
- **Flat surfaces (torus, Klein bottle).** Nothing is forced.
- **Orientation.** The count never uses an orientation, so the knot sees χ but not orientability. Where the count forces anything it
  stays in PPADS^dt; it cannot drop to PPA as Sperner does.
- **Unsatisfiability off the sphere** comes from elsewhere:
  - thinness, a one-dimensional chain (easy);
  - smallness (the Fano tori);
  - or a sphere hidden inside: three-fold spaces of any genus are refuted by the count of their plane core
    (`TWO-ROUND-BRIDGE-20261106-001B`), each Fano atom being a handle that stands for a negated incidence.

## What this does not establish

- **Non-lattice surfaces.** No classification of satisfiability off the lattice families.
  - For unbounded genus the related antiferromagnet problem is NP-complete (Jiménez–Kiwi).
  - Unsatisfiable families of fixed genus other than the sphere might exist outside the lattice families tested.
- **Hardness of the vertex count.** The over-agreeing-vertex search problem for χ < |D| is placed in PPADS^dt, but its hardness is not
  studied.
- **Klein bottles and projective planes.** These are computational only (§6).
