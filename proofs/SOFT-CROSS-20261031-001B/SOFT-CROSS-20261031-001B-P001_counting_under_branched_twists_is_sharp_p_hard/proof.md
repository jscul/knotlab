# Counting under branched twists is #P-hard

Status: Proved

Ticket `SOFT-CROSS-20261031-001B`, 2026-10-31.

**What it uses:**
- **`SOFT-CROSS-20261031-001A`:**
  - Lemma 1: the dead cap;
  - Lemma 4: a line with one capped leg acts by 3M between its other two legs;
  - Theorem 5 (universality): counting on cubic bipartite signed systems Turing-reduces to counting on cubic bipartite Pfaffian graphs
    under signings. The instances are planar hosts carrying junctions of twisted truncated-octahedron pages.
- **`TWIST-COUNT-20261030-001A`:**
  - Lemma 5: good roots;
  - Theorem 6: unbranched twists count in polynomial time.
- **`SEYMOUR-COUNT-20261030-001B`, Theorem 5:** the knot's own class counts in polynomial time on every three-fold space.
- **External, not replayed:**
  - Creignou and Hermann (1996): #SAT(S) is #P-complete for every set S of Boolean relations that are not all affine. NAE₃ is not
    affine, since it has 6 elements and an affine set has a power of 2.
  - Vandermonde systems with distinct nodes are invertible.

## Why this ticket exists

Ticket A reduced counting on every cubic bipartite signed system to counting on the knot's graphs under twisted signs. That is a hardness
result only if the source problem is hard. The obvious hard source, #NAE-3SAT, does not bound how often a variable occurs. A cubic system
needs every point on exactly three lines.

This ticket bounds the occurrences by merge paths, and so closes the hard side of the counting boundary.

## Standard statement

**Setting.**
- **Formulas.** A *positive NAE-3SAT formula* Φ is a list of clauses, each a triple of variables (repetitions allowed). A solution makes
  every clause not all equal, and #Φ counts the solutions. D = 3·(number of clauses) is the number of occurrences.
- **The graph G_k** (k ≥ 2), unsigned and cubic bipartite:
  - every occurrence becomes a *copy point*, and every clause a *clause line* on its three copies;
  - the d copies of a variable lie on a cycle, and consecutive copies q, q′ are joined by a *merge path* q − ℓ₁ − p₁ − … − p_{k−1} − ℓ_k − q′
    of k lines;
  - each pair (ℓ_t, p_t), t < k, is closed by a dead cap: ℓ_t's spare leg goes to the cap's point and p_t's to the cap's line;
  - the *last lines* ℓ_k are grouped in threes. Each group is closed by an *absorber*: a dummy point δ joined to each of the three last
    lines through its own cap. There are D paths, so the grouping is exact.
- **Matrices.** M = [[1, 2], [2, 1]] = 3P₊ − P₋, with P_± = ½[[1, ±1], [±1, 1]].
- **The path polynomial.** p_Φ(t) is the sum, over the colourings x of the copies that make every clause line not all equal, of
  Π_{merge paths (q, q′)} (1 + t(−1)^{x_q + x_q′})/2. It is a polynomial of degree at most D, and p_Φ(1) = #Φ, because at t = 1 every factor
  is the equality [x_q = x_q′].

**Results.**
- **Lemma 1 (merge paths).** On the actual graph, a merge path of k lines, its last line capped onto a free point, acts between its end
  copies by 2(3M)^k = 2(9^k P₊ + (−3)^k P₋).
  - In G_k the factor 2 belongs to the absorber (Lemma 2), and the path acts by (3M)^k = 9^k(P₊ + (−1/3)^k P₋).
- **Lemma 2 (the absorber).** An absorber point is free, contributing a factor 2. Each of its three lines sees a free colour of its own,
  weighted 3, and so acts by 3M.
- **Theorem 3 (the source; known, Fan and Cai 2020).** #col(G_k) = 2^{D/3} 9^{kD} p_Φ((−1/3)^k). So #Φ = p_Φ(1) is computed in polynomial
  time from #col(G_2), …, #col(G_{D+2}).
  - Hence counting the colourings of unsigned cubic bipartite systems is #P-complete. Equivalently, counting the proper 2-colourings of
    3-regular 3-uniform hypergraphs is #P-complete.
- **Theorem 4 (the hard side).** Counting the colourings of cubic bipartite Pfaffian graphs under signings is #P-hard under polynomial-time
  Turing reductions.
  - The oracle instances are those of ticket A: planar hosts carrying trisum junctions of twisted truncated-octahedron pages.
  - In those instances every junction square has three twisted branches. For snakes with two or more junctions this holds in general, and
    for single junctions it is computed on the K₃,₃ instances.
- **Corollary 5 (a two-sided boundary).** On cubic bipartite Pfaffian graphs:

  | Signing | Counting |
  |---|---|
  | the knot's own class (Pfaffian) | #col = 0, and #col(H − L) in polynomial time (`SEYMOUR-COUNT-20261030-001B`, Theorem 5) |
  | twisted, no square with three twisted branches | polynomial time (`TWIST-COUNT-20261030-001A`, Theorem 6) |
  | all signings | #P-hard (Theorem 4); the instances used have branched twists |

  So the knot's sign class, and how twists away from it branch, divide easy counting from hard counting on the knot's own graphs.

## Nearest known result

- **Theorem 3 is known.** Fan and Cai, *Dichotomy result on 3-regular bipartite non-negative functions* (arXiv 2011.09110, 2020), classify
  Holant(f | =3) for nonnegative symmetric ternary f.
  - Their problem Holant([0, 1, 1, 0] | =3) is exactly ours: points are the (=3) side, lines the not-all-equal side.
  - They prove it #P-hard: a gadget turns it into [3, 2, 2, 3], hard by their Lemma 4.2.
  - They note that its planar restriction is in FP, by the same Hadamard transformation as `TWIST-COUNT-20261030-001A`, Lemma 1:
    [0, 1, 1, 0] ↦ [3, 0, −1, 0] and (=3) ↦ [2, 0, 2, 0].
  - The proof here is an independent elementary replay, from #NAE-3SAT by merge paths and dead caps. It is kept because it is short and
    reuses ticket A's gadgets.
- **Theorem 4 has no overlap found** (candidate local delta, folklore risk moderate).
  - Planar tractability via Hadamard matchgates is classical (Valiant). So is hardness for general graphs (Fan and Cai, and the Holant and
    #CSP dichotomies of Cai, Lu, Xia and others).
  - What is new is that hardness survives on *Pfaffian* graphs, where perfect matchings still count in polynomial time, once the signs
    twist away from the Pfaffian class and the twists branch. Unbranched twists stay easy.
  - A Holant paper on graphs with a Pfaffian matchgrid could contain this. None was found.

## Proof of Lemma 1

- **Each pair.** Each pair (ℓ_t, p_t), t < k, is ticket A's Lemma 4. ℓ_t sees its cap's free point: NAE summed over that colour gives 1 when
  its other two legs agree and 2 when they differ, which is M. The cap contributes 3 for every pair of attachment colours (A, Lemma 1).
- **The last line.** The last line sees its own cap's free point in the same way. That cap's line attaches to the absorber point, which the
  cap leaves unconstrained.
- **The product.** So the path acts by (3M)^k. With M = 3P₊ − P₋ this is 3^k(3^k P₊ + (−1)^k P₋).
- **Check.** Section 1 confirms the 2 × 2 transfer matrix on the actual graph for k = 1, …, 5, with the free point's factor 2. For example,
  k = 2 gives [[90, 72], [72, 90]] = 2(3M)². ∎

## Proof of Lemma 2

- Each of the three caps contributes 3 whatever its attachments see (A, Lemma 1). So δ is constrained by nothing (a factor 2), and each line
  sees its cap's point as a free colour, which gives 3M.
- Section 2 confirms 2·27·M(a₁, b₁)M(a₂, b₂)M(a₃, b₃) for all 64 boundary patterns. ∎

## Proof of Theorem 3

**The count.**
- Every vertex of G_k is a copy point, a clause line, or part of a merge path, a cap or an absorber.
- Contract every path, cap and absorber by Lemmas 1 and 2. What remains is the copies, with the clause lines' not-all-equal constraint and
  one factor (3M)^k per merge path, times 2^{D/3}. So

  #col(G_k) = 2^{D/3} Σ_x [clauses NAE] Π_paths 9^k (P₊ + (−1/3)^k P₋)(x_q, x_q′) = 2^{D/3} 9^{kD} p_Φ((−1/3)^k),

  since (P₊ + tP₋)(a, b) = (1 + t(−1)^{a+b})/2.

**Solving.**
- p_Φ has degree at most D. The nodes (−1/3)^k, k = 2, …, D + 2, are distinct, so the D + 1 counts determine its coefficients, and with them
  p_Φ(1) = #Φ.
- G_k has 10kD + 2D/3 vertices: per path, k lines, k − 1 points and k caps of 8 vertices; plus D copies, D/3 clause lines and D/3
  absorbers. All numbers have O(kD) bits, so the reduction is polynomial.

**Hardness.** #Positive-NAE-3SAT is #P-complete (Creignou–Hermann), so the colouring count of unsigned cubic bipartite systems is #P-hard.
It lies in #P, so it is #P-complete.

**Check.** Section 3 builds G_k for six formulas, including an unsatisfiable one and one with single occurrences:
- with D + 2 values of k each, on graphs of up to 2710 vertices, every direct count equals 2^{D/3} 9^{kD} p_Φ((−1/3)^k), with p_Φ computed
  from the formula alone;
- the interpolation recovers every coefficient of p_Φ, and #Φ = 4, 6, 6, 0, 6, 6 exactly. ∎

## Proof of Theorem 4

**The reduction.**
- Given Φ, build G_k for D + 1 values of k (Theorem 3). Each G_k is an unsigned cubic bipartite system (check, section 4).
- Draw each G_k with polynomially many crossings, for example with vertices in convex position and straight edges. Then ticket A's Theorem 5
  computes #col(G_k) from the counts of polynomially many Pfaffian instances under signings.
- Composing the two Turing reductions gives #Φ from a Pfaffian-instance oracle.

**Branched twists.**
- In ticket A's instances both pages of every junction are twisted (A, section 2: neither page tensor has the split form, which is
  `TWIST-COUNT-20261030-001A`'s criterion for an untwisted branch).
- A cut of a graph restricts to a cut of every subgraph. So a branch containing a twisted page is twisted, and at a junction of a snake with
  two or more junctions the host-side branch contains the other junctions' pages.
- Hence all three branches are twisted. Section 4 confirms it on the K₃,₃ instances with 3 and 5 junctions: three twisted branches at every
  junction and no good root. The single-junction instance has three as well, because there the host's own signing differs from its
  Kasteleyn signing by a non-cut. ∎

## Proof of Corollary 5

The three rows are `SEYMOUR-COUNT-20261030-001B` (Theorem 5), `TWIST-COUNT-20261030-001A` (Theorem 6) and Theorem 4. On a Pfaffian graph,
the Pfaffian class is non-colourable (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4), so #col = 0 there. ∎

## What the computation checks

`check.py` (about 5 seconds):
- **1, merge paths.** Transfer matrices for k = 1..5 on the actual graph.
- **2, the absorber.** All 64 boundary patterns.
- **3, the reduction.** Six formulas with D = 3 to 15, D + 2 values of k each. The direct counts equal the predicted form at every k, and
  the recovered coefficients and counts are exact.
- **4, the composition.** Every G_k is unsigned, connected and cubic bipartite, with 10kD + 2D/3 vertices. Twisted branches in A's
  instances: (3), (3, 3, 3) and (3, 3, 3, 3, 3) for 1, 3 and 5 junctions, with no good root.
- **5, controls:**
  - D counts leave #Φ undetermined: the one null vector of the D × (D + 1) system has nonzero sum;
  - p_Φ has nonzero error terms, so no single count suffices;
  - absorbers attached without caps keep the exponential form but recover a wrong number: 3⁻⁹ and 3⁻¹⁸ instead of 4 and 6. The dead caps
    are what make each last line act by 3M.

## Reading

- **The hard side is the knot's sign class broken in a branching way.**
  - On the knot's own graphs, with the knot's own signs, colouring counts are polynomial: the knot's not-all-equal law on the trisum's
    leanings (`SEYMOUR-COUNT`).
  - Twisting the signs along a chain of squares keeps counting polynomial, because the twisted junctions act as similitudes of the knot's
    angle (`TWIST-COUNT`, Theorem 4).
  - Twists that branch, three at one square, make counting #P-hard. Repeating such junctions sharpens their soft crossing into a sharp one,
    and every cubic counting problem can be routed through them.
- **What carries the hardness.** It is not the graph: the graph is Pfaffian, and its perfect matchings count in polynomial time. It is how
  far the signs stand from the knot's class, and in what pattern.

## Nonclaims

- **Theorem 3 is not new.** It is Fan and Cai's #P-hardness of Holant([0, 1, 1, 0] | =3), replayed here by an independent elementary
  reduction.
- **Not a statement about single instances.** Theorem 4 is a worst-case statement about the family. The boundary reads: unbranched twists
  always count in polynomial time; with branched twists counting is #P-hard in general. Particular branched families may still be easy.
- **No end-to-end run of the composed reduction.** That would be formula → G_k → Pfaffian instances → counts. Ticket A demonstrated its
  reduction on K₃,₃ with one crossing, and this ticket demonstrates the source reduction. The composition is a theorem, not a computation.
- **External results.** Creignou–Hermann, Vandermonde invertibility, and Fan–Cai (cited for priority, not used) are not replayed.
