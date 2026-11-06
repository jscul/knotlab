# Signed bit laws on ordered triangulations: one twist and nothing else

Status: Proved

Ticket `SIGNED-3D-20261029-001A`, 2026-10-29.

**What it uses:**
- from `TWIST-3D-20261025-001A-P001`:
  - the ordered setting;
  - the generator of the move identities, reused verbatim and compared in check 1;
  - the factorization argument that turns identities into invariance;
  - the seven counting laws;
- classical background, cited and not admitted as local evidence:
  - group cohomology H³(Z/2; U(1)) = Z/2;
  - the Dijkgraaf–Witten state sum on ordered triangulations.

## Standard statement

**Setting.** As in `TWIST-3D-20261025-001A`.
- **Ordered triangulations.** Every tetrahedron of a triangulation of a closed orientable three-manifold carries an order 0 < 1 < 2 < 3 of
  its vertices. Faces are glued by the order-preserving maps, and each tetrahedron has a sign s = ±1 against the orientation.
- **Signed laws.** A signed law puts one bit on every edge and gives each labelling l of a tetrahedron's six edges (read in the order
  01, 02, 03, 12, 13, 23) a weight W_s(l) ∈ {−1, 0, 1}. The weight may depend on the sign s.
  - The state sum is c(T) = Σ_labellings Π_tetrahedra W_s(l).
  - The support of W is the set of labellings with nonzero weight.
- **Identities.** For every labelling of the boundary edges of an ordered 2–3 or 1–4 move, the signed sum over the new edges of the
  product of the new weights must equal λ (2–3) or μ (1–4) times the product of the old weights.
  - The state sum then changes by λ or μ under each move, as in `TWIST-3D-20261025-001A`.
  - When λ and μ are nonzero, N = c (λ³/μ)^V λ^(−T) is invariant.
- **Two symmetries.**
  - The *global sign* replaces W by −W.
  - The *face gauge* multiplies W_s(l) by τ(f₁)τ(f₂)τ(f₃)τ(f₄). Here τ assigns ±1 to each of the eight face labellings (x_ab, x_bc, x_ac),
    and f₁, …, f₄ are the labellings of l's four faces.

**Results.**
- **Lemma 1 (symmetries).**
  - The global sign turns a law with factors (λ, μ) into one with (−λ, −μ).
  - The face gauge keeps the factors and leaves the state sum of every closed ordered triangulation unchanged.
- **Theorem 2 (the census).** Let W be a nonzero signed law with μ ≠ 0.
  1. **Factors.** λ ≠ 0, and up to the global sign (λ, μ) is (1, 1), (1, 2) or (2, 16).
  2. **Support.** The support is one of the seven counting supports of `TWIST-3D-20261025-001A`, the same for both orientations, with that
     law's factors.
  3. **Classes.** Up to the face gauge, W is one of the twelve laws in the table, and each is the same for both orientations. On
     constant and free supports every sign pattern is gauge-trivial. On cocycle supports exactly one twist appears: the
     Dijkgraaf–Witten law (−1)^(x₀₁x₁₂x₂₃).
- **Corollary 3 (the twist needs the order).** No twisted class has a face-gauge copy that is the same for both orientations and invariant
  under the 24 permutations of the vertices; every untwisted class does.
  - So in the symmetric setting of `HUB-DIMENSION-20261024-001A`, signs add nothing.
  - By `TWIST-3D-20261025-001A`, order alone adds nothing to counting either. Together, order and signs add exactly the twist.
- **Remark 4 (what is excluded).**
  - **μ = 0.** Nonzero laws with μ = 0 exist for every λ; λ = 0 occurs only with μ = 0. With μ = 0, every 1–4 move kills the state sum and
    no normalized invariant is defined, so these laws are excluded, as in `TWIST-3D-20261025-001A`.
  - **The 2–3 move alone.** Requiring only the 2–3 identity is the reading in which one-vertex triangulations are compared, connected
    by 2–3 moves (Matveev, Piergallini). It admits more than 3,000 supports in scoping, many degenerate, and is not classified here.

| Support | Factors (λ, μ) | Sign patterns | Classes up to gauge | Laws |
| --- | --- | --- | --- | --- |
| all 0 (one labelling) | (1, 1) | 1 | 1 | counting |
| all 1 | (1, 1) | 1 | 1 | counting |
| all equal (two labellings) | (1, 1) | 1 | 1 | counting |
| even cocycles (8) | (1, 2) | 8 | 2 | counting; twisted: (−1)^(x₀₁x₁₂x₂₃) |
| odd cocycles (8) | (1, 2) | 8 | 2 | counting; twisted: (−1)^((1−x₀₁)(1−x₁₂)(1−x₂₃)) |
| even or odd (16) | (1, 2) | 64 | 4 | untwisted; twisted on the even part, on the odd part, on both |
| free (64) | (2, 16) | 64 | 1 | counting |

## Nearest known result

- **In the repository.**
  - `TWIST-3D-20261025-001A`: counting laws in the same ordered setting give the seven laws, and twists add nothing.
  - `HUB-DIMENSION-20261024-001A`: the symmetric census.
  - Both, together with `PATTERN-3D-20261025-001`, name phases (twisted Dijkgraaf–Witten) as what counting lacks.
- **Outside.**
  - **The twisted law is classical.** H³(Z/2; U(1)) = Z/2, and (−1)^(abc) is its nontrivial cocycle. The Dijkgraaf–Witten state sum
    (Dijkgraaf and Witten 1990; on ordered triangulations, Wakui 1992) with this cocycle is the twisted Z/2 theory.
  - **In physics** the untwisted and twisted Z/2 theories are the toric code and the double semion.
  - **The search.** A bounded search on 2026-10-29 used two queries, on state-sum classifications with Z/2 edge labels and signed
    weights, and on twisted Z/2 invariants of lens spaces. It found the general Turaev–Viro and Dijkgraaf–Witten frameworks and work on
    mod-2 Dijkgraaf–Witten invariants through triple cup products and linking forms. It found no exhaustive census of signed Boolean
    state sums.
- **Classification.**
  - The twisted law and its invariance are classical.
  - The census (Theorem 2), with its support statement, and Corollary 3: no overlap found (candidate local delta).

## Proof of Lemma 1

- **Global sign.** A 2–3 identity has three weights on each new term and two on the old side, so negating W negates the new side and
  keeps the old: λ becomes −λ. A 1–4 identity has four weights per new term and one on the old side: μ becomes −μ.
- **Face gauge.**
  - **Face labellings agree.** Faces are glued by order-preserving maps, so a triangle's labelling (x_ab, x_bc, x_ac) is the same in
    both tetrahedra that contain it.
  - **Inside a move region.** Every boundary triangle lies in exactly one old and one new tetrahedron, and every inner triangle of
    either side lies in two tetrahedra of that side.
  - **The identities.** So the gauge multiplies both sides of every identity by the product of τ over the boundary triangles, which is
    fixed by the boundary labelling. The inner factors square to 1.
  - **Closed triangulations.** Every triangle lies in two tetrahedra, so the state sum is unchanged. ∎

## Proof of Theorem 2

- **The range of the factors.**
  - A 1–4 identity's old side is a single weight, and every labelling occurs as the old tetrahedron of some 1–4 move. Its new side has
    16 terms in {−1, 0, 1}. So a nonzero law has |μ| ≤ 16.
  - A 2–3 identity has two new terms. So |λ| ≤ 2 whenever some old side is nonzero.
  - A law whose 2–3 old sides all vanish would satisfy the identities for every λ with the same μ. The search covers λ = 0, ±1, ±2, and
    no such law with μ ≠ 0 appears.
- **The encoding.**
  - Every weight is a pair of variables, nonzero and negative. A product of weights is nonzero iff all its factors are, and negative
    iff an odd number of them are negative.
  - A 2–3 identity forbids, under a selector for λ, every triple of values (old, new₀, new₁) with new₀ + new₁ ≠ λ · old.
  - A 1–4 identity counts its positive terms and its non-negative terms with a two-sided totalizer, whose output c_k holds exactly when
    at least k inputs hold. Under a selector for μ it fixes the count to 16 + μ · old, since #positive − #negative is that count minus
    16.
  - The identities are those of `TWIST-3D-20261025-001A`'s generator with the full triangle rule, compared one by one in check 1. A law
    therefore satisfies all identities exactly when the encoding is satisfiable with its values.
- **The search.**
  - Query every pair (λ, μ) with λ ∈ {0, ±1, ±2} and μ ∈ {0, ±1, …, ±16}. Nonzero laws exist exactly for (1, 1), (1, 2), (2, 16), their
    negatives (Lemma 1), and μ = 0.
  - For each positive pair, enumerate supports with blocking clauses until the solver reports none left: they are exactly the seven
    counting supports, each the same for both orientations.
  - For each support, enumerate sign patterns the same way. Then group them by the canonical member of their face-gauge orbit. The
    counts are those of the table, and the stated representatives lie in distinct orbits that cover every pattern found.
  - The representatives pass every identity by direct evaluation, independently of the encoding (check 5).
- **The twisted laws.**
  - On even cocycles, x is a coboundary δg, and (−1)^(x₀₁x₁₂x₂₃) is the Dijkgraaf–Witten weight of the nontrivial 3-cocycle
    (a, b, c) ↦ (−1)^(abc).
  - On odd cocycles, x + 1 is an even cocycle, and the twisted weight is that of x + 1. ∎

## Proof of Corollary 3

- **The test.** For each class, check 6 runs over all face-gauge copies of its representative: 2^m of them, m the number of face
  labellings in the support. It tests invariance under the 24 vertex permutations and equality of the two orientations.
- **The result.** The untwisted laws are themselves symmetric. No copy of a twisted law is.
- **The symmetric setting.** A symmetric law reads the same weights in every vertex order, so the ordered identities for it are exactly
  the unordered identities of the symmetric setting. Hence every symmetric signed law lies in one of the twelve classes, and so in an
  untwisted one. ∎

## What the computation checks

`check.py` (python-sat, about 40 seconds):
- **Identities.** The 10,880 identities equal `TWIST-3D-20261025-001A`'s.
- **Factors.** The 165 factor pairs.
- **Supports and signs.** Every support and sign pattern, by enumeration to exhaustion, with the twelve orbits identified.
- **Direct evaluation** of the twelve representatives, and of random face gauges of them.
- **The symmetry test** of Corollary 3.
- **Controls.**
  - One more sign flipped on the twisted law fails an identity, and the encoding rejects that pattern.
  - The twist on the free support fails for every factor pair.
  - Without the 1–4 identities, supports outside the seven appear.
  - Laws with μ = 0 exist.

## Reading

- **Signs add one phase, not one relation.**
  - The supports of signed laws are exactly the counting supports: constants, the parity (cocycle) relations, and the free law.
    Interference never creates a new relation.
  - What it adds is a phase on the parity supports: the cubic sign (−1)^(x₀₁x₁₂x₂₃), read along the path 0–1–2–3 that the vertex order
    draws through each tetrahedron.
- **Order and signs are needed together.** Order alone adds nothing to counting (`TWIST-3D-20261025-001A`), and signs alone add nothing
  (Corollary 3). The twist lives on the ordered spine, so it needs both.
- **In the program's terms.**
  - In two dimensions interference rebuilt nothing beyond parity on genuine space (`SIGNED-SUBDIVISION-20261029-001`).
  - On finitely ramified space it builds non-affine knots (`SIMPLEX-GASKETS-20261029-001`).
  - On three-manifolds the relation stays parity and interference adds exactly one phase. Ticket B finds what that phase sees.

## Nonclaims

- **Scope of the census.** Only weights in {−1, 0, 1} and one bit per edge. Complex phases, more labels per edge and other placements of
  bits are not covered.
- **Excluded laws.** Laws with μ = 0, and the reading with the 2–3 move alone, are excluded (Remark 4).
- **No physical interpretation.**
