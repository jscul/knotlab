# A soft crossing interpolates to a sharp one

Status: Proved

Ticket `SOFT-CROSS-20261031-001A`, 2026-10-31.

**What it uses:**
- **`TWIST-COUNT-20261030-001B`:**
  - Lemma 1: the junction on a slice;
  - Proposition 3: the soft crossing, two twisted truncated-octahedron pages whose junction is crossover-type with straight entries
    (40000, −1112, 3336, −192).
- **`TWIST-COUNT-20261030-001A`:**
  - Lemma 1: the Hadamard form;
  - Lemma 2: branch tensors, with the page tensor code.
- **`SEYMOUR-COUNT-20261030-001A`, Lemma 1(iii):** three pieces with Pfaffian signings, odd on a common square, glue to a non-colourable trisum.
- **`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4:** a connected cubic signed system is non-colourable iff its signing is Pfaffian.
- **External, not replayed:**
  - Kasteleyn: a planar bipartite graph has a signing with l − 1 negations mod 2 on every face of length 2l, and it is Pfaffian.
  - Vandermonde systems with distinct nodes are invertible, and solvable in polynomial time in exact arithmetic.

## Why this ticket exists

`TWIST-COUNT-20261030-001` found that a junction of twisted pieces crosses two wires only softly: it passes both, but weighted. Hardness
proofs for planar-tractable counting problems need a *sharp* crossover. The standard way to get one is interpolation: repeat the soft gadget
and solve a linear system.

This ticket carries that out inside the knot's own graphs, which are Pfaffian. The result is that any cubic counting instance, planar or not,
can be read off from Pfaffian ones.

## Standard statement

**Setting.**
- **Instances.** A *signed system* is a cubic bipartite graph with a set of negated edges. #col counts the point colourings in which every
  line sees (colour ⊕ sign) not all equal. An instance is *Pfaffian* when some signing makes it non-colourable.
- **Tensors.** Tensors of 4-leg gadgets are taken in the colour basis F and in the Hadamard basis F̂ = H^{⊗4}F, with H = [[1, 1], [1, −1]].
  - *Crossover-type* means F̂ vanishes off y0 = y2, y1 = y3. Its *straight entries* are σ(s) for s = (y_A, y_B) ∈ {00, 01, 10, 11}.
  - The *exact crossover* is [z0 = z2][z1 = z3].
- **The soft crossing J.** A square (c0, c1, c2, c3), points c0 and c2, glued by trisum to two copies of the truncated octahedron. The
  copies carry the signings `SIGN_Q` and `SIGN_R` of `cross_lib.py` (both twisted), and c3's incidence into the second copy is negated.
  - Its legs are c0's and c2's edges to host lines (wire A) and c1's and c3's edges to host points (wire B).
  - Its straight entries are σ₁ = (40000, −1112, 3336, −192).
- **The dead cap.** The cube minus one edge (u, v), unsigned. u attaches to an outside line, v to an outside point.
- **The plumbing line.** A host line with one capped leg acts between its other two legs by M = [[1, 2], [2, 1]] in the colour basis. M has
  eigenvalues μ(0) = 3 and μ(1) = −1, on the eigenvectors (1, 1) and (1, −1).
- **The k-snake S_k.** k copies of J in series.
  - Between consecutive junctions, wire A passes a host line λ and wire B passes a host point, a host line μ and a host point.
  - The spare legs are closed by two caps: (λ, first point) and (μ, second point).
  - Wire B's crossing side alternates, so the wires cross k times.
- **A long edge with k pairs.** It replaces an edge (p, ℓ) by a path p − ℓ₁ − p₁ − … − ℓ_k − p_k − ℓ, each pair (ℓ_i, p_i) closed by a cap.
- **Drawings.** A drawing of a signed system G puts edges in the plane so that every crossing is between two edges with no common end, and
  two edges cross at most once.

**Results.**
- **Lemma 1 (the dead cap).** The cap's count is 3 for every pair of colours seen at its two attachments.
  - So a line attached to u sees a free colour of its own, and a point attached to v is unconstrained by v.
  - The cap contributes a factor 3.
- **Lemma 2 (the snake).** Ŝ_k (caps included) is crossover-type with straight entries σ₁(s) Λ(s)^{k−1}, where

  Λ(s) = (9/4) μ(y_A) μ(y_B) σ₁(s) = (810000, 7506, −22518, −432).
- **Lemma 3 (the lattice condition).** v₅(Λ) = (4, 0, 0, 0), v₁₃₉(Λ) = (0, 1, 1, 0) and v₃(Λ) = (4, 3, 4, 3).
  - So for count vectors n ∈ ℕ⁴ of fixed total, the products Π_s Λ(s)^{n_s} determine n.
  - Hence the numbers μ_n = Π_s Λ(s)^{2n_s} are distinct and positive.
- **Lemma 4 (long edges).** A long edge with k pairs acts between p and ℓ's view by 3^k M^k = 9^k P₊ + (−3)^k P₋, with
  P_± = ½[[1, ±1], [±1, 1]]. The exact edge is P₊ + P₋.
- **Theorem 5 (universality).** Let G be a signed system drawn with m crossings. There are instances G(k_E, k_S) such that #col(G) is computable
  in polynomial time from their counts:
  - each instance is Pfaffian, of size polynomial in |G|, m, k_E and k_S;
  - k_E ranges over |E(G)| + 1 consecutive values from a threshold, and k_S over 1, 3, …, 2N − 1 with N = C(m+3, 3).

  Hence counting colourings of cubic bipartite signed systems is polynomial-time Turing reducible to counting colourings of cubic bipartite
  Pfaffian graphs under signings.
- **Corollary 6 (K₃,₃).**
  - For the drawing of K₃,₃ with one crossing, the counts of four Pfaffian instances (k_S = 1, 3, 5, 7, no long edges needed) determine
    9·#col(K₃,₃, σ).
  - This is checked for three signings: 6, 2 and 2 colourings.
  - K₃,₃ itself is colourable under every signing, so it is not Pfaffian.

## Nearest known result

- **Interpolation and crossovers** are the standard machinery of #P-hardness for counting problems (Valiant; Vadhan; Dyer, Goldberg and
  Jerrum; Cai, Lu and Xia).
  - A planar-tractable problem becomes hard once a crossover is simulated.
  - Planar not-all-equal counting is tractable (Valiant), and so is the knot's own sign class on Pfaffian graphs (`SEYMOUR-COUNT`,
    `TWIST-COUNT-20261030-001A`).
- **What is new here** (no overlap found, candidate local delta):
  - the crossover is simulated *inside Pfaffian graphs*, from a soft crossing of twisted pieces of the knot's spaces;
  - the dead cap and the snake's explicit multipliers with their lattice condition.

## Proof of Lemma 1

Direct count over the cube's remaining three points (check, section 1): the count is 3 for all four colour pairs. ∎

## Proof of Lemma 2

**The connectors.**
- In the colour basis, S_{k+1} is S_k followed by the plumbing and a copy of J. Wire A's connector is λ with a capped leg: matrix 3M, the
  cap contributing 3.
- Wire B's connector is: a point (identity, its cap's line imposes nothing), μ with a capped leg (3M), and a point.
- The two caps of the interval contribute 3 · 3, already counted.

**In the Hadamard basis.**
- Contracting two legs costs a factor (1/2)² = 1/4.
- M is diagonal there, H M H / 2 = diag(μ(0), μ(1)).
- A crossover-type tensor, contracted on both of its out-legs with diagonal connectors and then with J (crossover-type), is crossover-type.
- Its straight entry in state s is multiplied by (9/4) μ(y_A) μ(y_B) σ₁(s) = Λ(s).

**Exactness.** Section 3 of the check verifies the formula for k ≤ 6 exactly. It also verifies that the resulting predictions equal the
direct counts of the actual K₃,₃ instances for k ≤ 7, under three signings. ∎

## Proof of Lemma 3

- **Factorization.** Λ = (2⁴3⁴5⁴, 2·3³·139, −2·3⁴·139, −2⁴3³).
- **Valuations.** For a count vector n of total m:
  - the valuation of Π Λ^{n} at 5 is 4n₀₀;
  - at 139 it is n₀₁ + n₁₀;
  - at 3 it is 4n₀₀ + 3n₀₁ + 4n₁₀ + 3n₁₁ = 3m + n₀₀ + n₁₀.
- **Recovering n.** These give n₀₀, then n₁₀, then n₀₁ and n₁₁ = m − n₀₀ − n₀₁ − n₁₀.
- **Distinct values.** Distinct n of the same total therefore give products of distinct absolute value, so the μ_n are distinct. Section 4 of
  the check also confirms it exhaustively for every total m ≤ 8. ∎

## Proof of Lemma 4

- Each pair (ℓ_i, p_i): ℓ_i sees its cap's free point, giving M, and the cap contributes 3. p_i is constrained only by ℓ_i and the next line.
- The path acts by (3M)^k = 3^k(3^k P₊ + (−1)^k P₋).
- Section 5 of the check confirms 9^k c₊ + (−3)^k c₋ on an actual graph for k ≤ 4, and that c₊ + c₋ is the count with the plain edge. ∎

## Proof of Theorem 5

**Construction.**
- **Long edges.** Draw G, and let k₀ exceed the largest number of crossings on one edge. Replace every edge by a long edge with k_E ≥ k₀ pairs
  along its curve, so that every path edge is crossed at most once.
- **Crossing sites.** At each crossing of path edges (p_A, ℓ_A) and (p_B, ℓ_B):
  - insert p_A − λ − [S_{k_S}, wire A] − ℓ_A and p_B − [S_{k_S}, wire B] − π − ℓ_B;
  - close λ and π by one cap.
- **The result** is a cubic bipartite graph G(k_E, k_S). It is the drawing of G with every crossing replaced by a snake region.

**Pfaffian.**
- The pieces are the host and the pages:
  - the host is everything outside the pages, with each junction's square edges;
  - the host is planar, since the drawing's crossings are gone and the caps are planar inside faces;
  - every junction square is a face of the host, and every page is a planar brace with its square a face.
- Kasteleyn signings of the pieces negate an odd number of each square's edges. By `SEYMOUR-COUNT-20261030-001A`, Lemma 1(iii), applied one
  junction at a time, the glued signing is non-colourable.
- So the graph is Pfaffian (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4). Section 6 of the check verifies this certificate for the K₃,₃
  instances, k_S = 1, 3, 5, 7.

**The count.** Expand each long edge into its P₊ and P₋ parts, and each snake site into its four straight states. Then

#col(G(k_E, k_S)) = 9^{k_E |E|} Σ_{j, n} D(j, n) (−1/3)^{k_E j} μ_n^{(k_S − 1)/2},

where j counts the long edges in their P₋ part and n is the vector of state counts at the m sites.
- D(j, n) does not depend on k_E or k_S. It includes the factors σ₁(s)^{n_s}.

**Solving.**
- The nodes (−1/3)^{k_E} are distinct for distinct k_E, and the μ_n are distinct (Lemma 3).
- The system over k_E ∈ {k₀, …, k₀ + |E|} and k_S ∈ {1, …, 2N − 1} is a tensor product of two Vandermonde systems, so it determines every
  D(j, n).

**The target.**
- Replace every long edge by P₊ + P₋ (weight 1 for both parts).
- Replace every site by the compensated crossover X*(z) = [z1 = z3] w(z0, z2), with w = [[−1, 2], [2, −1]]. Its weight on state s is
  X̂*(s)/σ₁(s) relative to D.
- Since 3M·w = 9·I, the inserted λ and its cap are compensated exactly.
- The result is 9^m #col(G): one factor 9 per crossing.

**Size.**
- There are m ≤ |E|² crossings and N = O(m³) unknowns per site pattern.
- There are (|E| + 1)·N instances, each with O(m · N + |E| k_E) junctions and vertices.
- All numbers have polynomially many bits. ∎

## Proof of Corollary 6

- **The drawing.** K₃,₃ is drawn as the hexagon P0 L0 P1 L1 P2 L2 with chords P0L1, P1L2 and P2L0. P0L1 and P2L0 cross once; no other edge
  is crossed, so no long edges are needed.
- **The solve.** The 4 × 4 system Z_k = (1/16) Σ_s c_s σ₁(s) Λ(s)^{k−1}, at k = 1, 3, 5, 7, is solved exactly. Then (1/16) Σ_s c_s X̂*(s)
  equals 9·#col(K₃,₃, σ) for all three signings (check, section 6).
- **K₃,₃ is not Pfaffian.** All 512 signings of K₃,₃ are colourable (section 7). ∎

## What the computation checks

`check.py` (about a second):
- **1, the cap.**
- **2, the soft crossing** rebuilt from the explicit signings: straight entries, zero turning entries, both pages twisted, MGI ≠ 0.
- **3, snakes.** The formula for k ≤ 6. Predictions equal 21 direct counts of K₃,₃ instances (k = 1..7, three signings, up to 444 vertices).
- **4, the lattice condition.** Valuations, and exhaustive distinctness for totals up to 8.
- **5, long edges** on the cube system with one long edge: 6, 54, 486, 4374, 39366, with the exact edge recovered.
- **6, end to end.** Three signings recovered (54, 18, 18 = 9 × 6, 2, 2). Pfaffian certificates for the four instances.
- **7, controls:**
  - a single host point on wire B makes the one-site system singular (Λ₀₁ = Λ₁₀);
  - an exclusive crossing (64, −8, 24, 0) loses the double state;
  - K₃,₃ is colourable under every signing;
  - seven single negations of the cube cap are not dead.

## Reading

- **The knot's graphs are universal for cubic counting.** Every cubic not-all-equal counting problem, on any graph, can be read off from the
  knot's own graphs: Pfaffian ones, with their signs twisted.
  - On these graphs the knot's own sign class counts in polynomial time.
  - What carries the hardness is the soft crossing: the interference of two twisted pages, repeated and interpolated into a sharp one.
- **Why the soft crossing suffices.** A sharp crossing is impossible in one junction (`TWIST-COUNT-20261030-001B`). Repetition makes the
  four crossing states grow at four multiplicatively independent rates, 5⁴, 139 and 3 in their factors, and that is enough to separate them.
- **The hard side is reduced to the source.** If counting on cubic signed systems is #P-hard, so is counting under twisted signs on the knot's
  graphs. Ticket B proves the source hard.

## Nonclaims

- **Hardness of the source.** It is ticket B. This ticket proves the reduction only.
- **Long edges and many crossings.** The general construction is proved but demonstrated only through its parts:
  - long edges on a small graph;
  - snakes on K₃,₃ with one crossing.

  A full two-parameter run on a larger drawing was not computed.
- **External results.** Kasteleyn's theorem and Vandermonde invertibility are used without replay.
