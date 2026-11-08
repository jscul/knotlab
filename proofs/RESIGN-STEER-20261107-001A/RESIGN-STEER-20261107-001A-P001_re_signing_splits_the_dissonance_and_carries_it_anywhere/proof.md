# Re-signing splits the forced dissonance and carries it anywhere

Status: Proved by hand (theorems 1–4). The finite claims are checked by computation with controls (`check.py`).

Ticket `RESIGN-STEER-20261107-001A`, 2026-11-07.

## Standard statement

**Setting.**
- Let T be a triangulation of the sphere whose triangles are coloured in two colours, neighbours differing. The **points** are the
  triangles of colour 0, the **lines** those of colour 1, and T's vertices are called **faces** (they are the faces of the
  point–line incidence graph). With n lines there are n points and n + 2 faces.
- A **signing** s puts a bit on every side. A line's not-all-equal constraint reads its three literals x_p ⊕ s(side). A line's
  **corner** at a face is the pair of its two sides there, and it **agrees** under an assignment when those two literals are equal.
- Write viol for the number of violated lines, agree_v for the number of agreeing corners at face v, E = Σ_v ⌊agree_v / 2⌋, and
  D(s) for the **even faces**, where agree_v is even under every assignment (`COUNT-SURFACES-20261107-001A`, theorem 1). A
  **Kasteleyn** signing s0 has no even face.
- A **flat state** of the Kasteleyn law has exactly one violated line and E = 0.
- H is the bipartite graph joining each line to its three faces, and B the n × (n + 2) 0/1 matrix of H. T is **simplicial** when
  two triangles share at most one side; then no line repeats a face and no two lines share two faces.

**Theorem 1 (bookkeeping).** In every state and every law, viol − E + |D| / 2 = 1. One sign change toggles exactly the two faces at
the ends of its side, so it changes |D| / 2 by −1, 0 or +1 and viol − E by the opposite amount. With four or more even faces every
state over-agrees somewhere: E ≥ |D| / 2 − 1.

**Theorem 2 (two even faces suffice, wherever they sit).** Let T be simplicial. For every pair of distinct faces u, v, every law with
D = {u, v} is satisfiable, and its satisfying assignments are, two to one, the perfect matchings of H − {u, v}.
- (a) Every single sign change of a Kasteleyn signing gives a satisfiable law.
- (b) For every line l, the Kasteleyn law has a flat state whose violated line is l.

**Theorem 3 (every line carries the dissonance equally).** Let T be simplicial, let n0, n1, n2 be the sizes of the three colour
classes of T's vertex 3-colouring, and let

  N(T) = √( det(B Bᵀ) / (n0 n1 + n1 n2 + n2 n0) ).

- (a) For every line l, exactly 2 N(T) flat states of the Kasteleyn law have l as their violated line.
- (b) For every pair of faces u, v of different colours, H − {u, v} has at least N(T) perfect matchings, with equality when u and v
  are adjacent.

**Theorem 4 (re-signing alone carries the dissonance).** Let T be simplicial, x a flat state of a Kasteleyn law s0 with violated
line l0, and t any line. Some sequence of single sign changes, each on a side of the currently violated line or on a side with an
end at a current even face, ends with no even face and t as the only violated line of x, while x never changes. After every change
the configuration is either (one violated line, E = 0, no even face) or (no violated line, E = 0, two even faces), and the two even
faces can be brought to any pair of faces. The final signing is s0 plus the boundary of a set R of triangles, so the end
configuration is x with the points of R flipped, under s0.

## Nearest known results

- **Matchings and signs.** Kasteleyn's theorem for plane bipartite graphs (Kasteleyn 1967; Kuperberg, *An exploration of the
  permanent-determinant method*, 1998). `COUNT-SURFACES-20261107-001A` theorem 4: with |D| = χ the satisfying assignments are,
  two to one, the perfect matchings of the lines with the faces off D in one homology class.
- **Hall's theorem and Euler's formula.** Lemma 2.1 is the usual Euler count for plane bipartite graphs without 4-cycles.
- **Colourings.** Heawood (1898): a plane triangulation has a proper vertex 3-colouring exactly when every vertex has even degree.
  Complementary Plücker coordinates (the maximal minors of a matrix and the minors of its kernel agree up to a scalar and signs).
- **Monomers and worms.** Monomer–monomer correlations of dimer models (Fisher and Stephenson 1963). Worm and directed-loop
  algorithms for dimers (Sandvik and Moessner 2006; Alet et al. 2006) create two monomers, move one along alternating paths and
  close the worm as a loop update: theorem 4's walk is this, with the walk carried by the signs instead of the dimers.
- **The model.** Ground states of the triangular Ising antiferromagnet are honeycomb dimers (Blöte and Hilhorst 1982); satisfying
  assignments of triangulations (Jiménez and Kiwi, arXiv 1107.3767). Ciucu's electrostatics of holes in lozenge tilings (Memoirs AMS
  178, 2005) is the comparison for ticket B.
- **The record.** `FLAT-STATES-20261107-001A` builds flat states through any chosen point, with explicit vortex steps, by developing
  frames over a cut sphere. Theorem 2(b) gives one through any chosen line on every simplicial sphere, by matchings.
- **Classification.**
  - Theorems 1, 2 and 4: known-with-delta. Each is a short consequence of the tools above. The delta is the setting: the knot's own
    law, whose dissonance is forced, with the even faces as the law's marks.
  - Theorem 3: no overlap found. A bounded search (lozenge tilings and honeycomb matchings with two adjacent vertices removed;
    dimers and Ising antiferromagnets on spheres and polyhedra; Kasteleyn kernels and 3-colourings of Eulerian triangulations;
    Ciucu's hole correlations) found neither the uniform count nor the closed form. This is not a novelty claim.

## 1. Bookkeeping

*Proof of theorem 1.*
- `COUNT-SURFACES-20261107-001A` theorem 3 gives viol − E = (χ − |D|) / 2, and χ = 2.
- A signing is a 1-chain on T's 1-skeleton, and flip_v is the degree of v in it mod 2 (the same record, proof of theorem 2). One
  sign change adds one edge, so it toggles the parity of exactly its two ends, and each of them enters or leaves D.
- With |D| ≥ 4, E = viol + |D| / 2 − 1 ≥ |D| / 2 − 1. ∎

**Index reading.** In the count's Poincaré–Hopf reading a violated line has index 2 and a face 1 − agree_v, so an even face always
has odd index. The forced unit is held either by the state, as a violated line, or by the law, as two even faces of odd index.

## 2. Two even faces

**Lemma 2.1 (Hall surplus).** If T is simplicial, then every nonempty set S of lines has |N(S)| ≥ |S| + 2, where N(S) is the set of
faces of the lines in S.

*Proof.*
- Let G be the subgraph of H with vertex set S ∪ N(S) and all 3|S| edges at S. It is a plane graph. Let c be its number of
  components and f its number of faces; Euler's formula gives (|S| + |N(S)|) − 3|S| + f = 1 + c.
- H has no cycle of length 2 (no line repeats a face) and none of length 4: two lines sharing faces u and w would both contain the
  side uw, which lies in one triangle of each colour. So every cycle of G has length at least 6.
- Each face's boundary has total length at least 6. A boundary walk containing a cycle is at least that long. A boundary walk
  containing no cycle goes around a tree component twice, and the tree has a line with three edges.
- The boundary lengths sum to twice the number of edges, so 6f ≤ 6|S|. Hence |N(S)| = 1 + c + 2|S| − f ≥ 1 + c + |S| ≥ |S| + 2. ∎

*Proof of theorem 2.*
- **Matchings.** For every S, |N(S) ∖ {u, v}| ≥ |S|, so Hall's theorem gives a matching of all n lines into the n faces off
  {u, v} (Euler on T: 2n triangles and 3n sides give n + 2 faces). It is perfect.
- **Laws.** Signings with D = {u, v} exist and form one class up to gauge (`COUNT-SURFACES-20261107-001A` theorem 2, with
  |D| ≡ χ and 2^(2 − χ) = 1). By theorem 4 of that record, with |D| = χ, their satisfying assignments are, two to one, the perfect
  matchings of H − {u, v} accepted by the class, and on the sphere one class accepts them all.
- **(a)** By theorem 1, one sign change of s0 gives D = the two ends of its side.
- **(b)** Let a, b be two faces of l and c the third. A perfect matching of H − {a, b} matches l to c, its only face left. Its
  assignment x satisfies every line under s1 = s0 + (side ab of l), and by theorem 1 its E is 0, so the even faces a and b have no
  agreeing corner. Changing the side ab back toggles l's corners at a and b, which disagreed and now agree. l's corner at c agreed,
  so l is violated, a and b agree once each, and nothing else changes. So x is a flat state of s0 with violated line l. ∎

## 3. Every line equally

*Proof of theorem 3.*
- **Step 1, the kernel.** T's vertex degrees are even, so it has a proper vertex 3-colouring σ (Heawood), and every triangle has
  one vertex of each colour. A function on the faces that is constant on each colour class, with values summing to 0, is therefore
  in the kernel of B. These functions form a 2-dimensional space. Step 2 shows that B has a nonzero maximal minor, so its kernel has
  dimension (n + 2) − n = 2 and is exactly this space. In a basis, colour class i has coordinates κ_i ∈ R², with
  κ_0 + κ_1 + κ_2 = 0 and κ_0, κ_1 independent.
- **Step 2, adjacent pairs.**
  - The faces of the plane graph H are the n hexagons around the points (a point's three faces and the three lines across its
    sides), each a simple 6-cycle since T is simplicial.
  - Let a, b be adjacent faces, and p the point containing their side. Deleting a and b merges the hexagons around a and around b,
    which meet at p, into one face. Every other face of H − {a, b} is an untouched hexagon.
  - Draw the merged face as the unbounded one. All-plus weights satisfy Kasteleyn's condition on every bounded face: a face of
    length 2d needs sign product (−1)^(d+1), which is +1 for d = 3. So H − {a, b} has |det B_{−a,−b}| perfect matchings, where
    B_{−a,−b} is B with columns a and b deleted. By theorem 2 this is positive.
- **Step 3, complementary minors.** For the full-rank n × (n + 2) matrix B and a kernel basis, a scalar λ ≠ 0 gives
  det B_{−u,−v} = ±λ (κ_{σ(u)} ∧ κ_{σ(v)}) for every pair u, v. Since κ_0 + κ_1 + κ_2 = 0, |κ_0 ∧ κ_1| = |κ_1 ∧ κ_2| =
  |κ_2 ∧ κ_0|. So |det B_{−u,−v}| is one constant c > 0 for every pair of different colours, and 0 for equal colours.
- **Step 4, (a).**
  - Adjacent faces have different colours, so H − {a, b} has exactly c perfect matchings for every side ab.
  - For a side ab of l, the flat states of s0 with violated line l are exactly the satisfying assignments of s1 = s0 + (side ab).
    One direction is theorem 2(b). Conversely, a flat state with violated line l has every face agreeing once, and changing the side
    ab satisfies l and leaves every line satisfied.
  - By theorem 2 these number 2c, for every line l.
- **Step 5, (b).** det B_{−u,−v} is a sum of ±1 over the perfect matchings of H − {u, v}, so their number is at least
  |det B_{−u,−v}| = c whenever σ(u) ≠ σ(v).
- **Step 6, the closed form.** Cauchy–Binet gives det(B Bᵀ) = Σ_{u<v} det(B_{−u,−v})² = c² (n0 n1 + n1 n2 + n2 n0). So c = N(T). ∎

**Values.** N(K_2) = 54, N(K_3) = 24,576, N(K_4) = 163,840,000 and N(K_5) = 15,284,826,363,950 on the octahedral spheres
(checks 4 and 7, with K_6–K_8).

**Reading.** Among the states with the least dissonance, the law with nothing learned puts its dissonance on every line equally often,
corners included: it prefers no place. Where the point goes is left to what is learned, or to the state's history.

## 4. Steering

**Lemma 4.1 (alternating walks).** Let T be simplicial, M a perfect matching of H − {a, b}, and w ∉ {a, b} a face. Some faces
a = w_0, w_1, …, w_k = w and lines l_1, …, l_k, with l_i at w_{i−1} and matched to w_i, make each
M_i = M_{i−1} − {l_i w_i} + {l_i w_{i−1}} a perfect matching of H − {w_i, b}.

*Proof.* H − {w, b} has a perfect matching M′ (theorem 2). In M Δ M′ every line and every face other than a and w has degree 0 or
2, while a and w have degree 1. So the component of a is an alternating path from a to w, and reading it from a gives the walk. ∎

**Lemma 4.2 (each step is one sign change at an even face).** Fix x, and let the agreeing corners of x under s be the matching
M_{i−1}, all lines satisfied. Changing the sign of the side of l_i joining w_{i−1} and w_i toggles exactly l_i's corners at those two
faces. So l_i's agreement moves from w_i to w_{i−1}, the even faces become {w_i, b}, all lines stay satisfied and E = 0.

*Proof of theorem 4.*
- **Split.** Change a side ab of l0, a side of the violated line. As in step 4 above, x satisfies every line of the new law, whose
  even faces are a and b.
- **Carry.** Pick two faces t1, t2 of t, keeping an even face that is already on t. Walk a to t1 by lemmas 4.1 and 4.2, never onto
  b, which is unmatched and so never a destination. Then walk b to t2 in H − {t1}.
- **Rejoin.** Change the side t1 t2 of t, which has both ends at even faces. t's corners at t1 and t2 disagreed and now agree, and
  its corner at its third face agreed, so t is violated. t1 and t2 now agree once each, there is no even face, and E = 0.
- Every configuration between split and rejoin has no violated line, E = 0 and two even faces. ∎

**Corollary 4.3 (a closed learning walk is a change of state).**
- The changed sides form a 1-chain z with D(s0 + z) = D(s0) = ∅, so z has even degree at every face: it is a cycle.
- On the sphere every cycle bounds, so z = ∂R for a set R of triangles. Adding a point's boundary flips that point's variable.
  Adding a line's boundary complements the line's three literals, which changes no constraint.
- So (x, s0 + z) has the agreeing corners of (x with the points of R flipped, s0). ∎

**Dimer reading.**
- A flat state's agreeing corners cover every face once, the violated line covering all three of its faces: a dimer cover with one
  trimer.
- The split turns the trimer into a dimer and two monomers, the even faces. The walk moves the monomers along alternating paths, as
  the worm algorithm of dimer models does. Rejoining makes a trimer elsewhere.
- Closing the worm is a loop update of the state (corollary 4.3).

**The owner's picture.** Read as in the assumptions register (A20, A21), rationalization moves the point into the law as two
half-charges. Learning carries them, and rejoining puts the point where it is wanted, while the state holds still. This is a reading,
not a theorem.

## What this does not establish

- **Locality.** Theorem 4's walk follows shortest alternating paths, chosen with a global view. Ticket B tests rules that see only an
  even face's lines and a target signal.
- **Other surfaces.** Off the sphere the signings with fixed D form 2^(2 − χ) classes, so learning could change the homology class
  and not only move the even faces. This is not studied.
- **Non-simplicial spheres.** Theorems 2–4 assume a simplicial T. The checks also cover a branched double cover in which two lines
  share two faces; every pair of faces is satisfiable there too.

## Checks

`check.py` (`result.json`), about ten minutes:

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Bookkeeping on 13 spheres, random laws and states; one sign change; four even faces on K_3 | identity holds; at most one unit moves; satisfying states with \|D\| = 4 over-agree |
| 2 | Every pair of faces on K_2–K_6, two tubes, three grown spheres and four double covers; SAT on K_2 (all) and K_3 (40); brute counts on K_2 | no pair unsatisfiable; satisfying assignments = 2 × matchings |
| 3 | Flat states with each line as the violated line, K_2–K_6 | all built |
| 4 | Uniformity over all lines, the kernel, the closed form, all-plus minors, the lower bound; K_2 by brute force | equal counts on every sphere with girth 6; 108 = 2 × 54 flat states per line on K_2 |
| 5 | Steering: every start and target on K_2 and K_3, 150 pairs on K_4–K_6; block-change check | every target reached; only the two allowed configurations; state fixed |
| 6 | Controls | the Kasteleyn law is unsatisfiable; counts from one face are not uniform; a sign change away from the dissonance leaves the allowed configurations; a far pair's all-plus minor is below its count |
| 7 | One size past: K_7 and K_8 | every single sign change and 300 random pairs satisfiable; uniformity and the closed form; 30 steering runs each |
