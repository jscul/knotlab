# Tseitin size from cell systems: planar, minor-free and grid-like graphs

Status: Proved

Ticket `CELL-SIZE-20261020-001B`, 2026-10-20. This proof:
- generalizes `PC-SIZE-GRID-20261020-001B-P001` (grids) away from planarity;
- uses the tangle lemma of `PC-DEGREE-20261020-001B-P001` (Lemma 2 there);
- cites the tangle–branch-width duality (Robertson–Seymour, Graph Minors X
  (3.5); Geelen–Gerards–Robertson–Whittle 2006, Theorem 3.2) and the grid-minor
  theorems listed in Corollary 6.

Throughout, F is a field of characteristic other than 2. "PC" means polynomial
calculus in the 0/1 basis, and "PCR" means PC with twin variables. Size counts
monomials over all lines.

## Statements

**Cell systems.** Let G be a connected graph of maximum degree Δ. A *cell
system* (𝒞, U; L, ℓ) is a set U of exceptional edges and a family 𝒞 of cycles
(*cells*) with three properties:
- (C1) every cell has length at most L;
- (C2) every edge outside U lies on a cell;
- (C3) for every cell C and edge e = uv of C, there is a u–v path P_{C,e} of
  length at most ℓ that uses no edge of C.

**Theorem 1 (cell theorem).** Suppose G has a cell system (𝒞, U; L, ℓ) and its
cut function has a tangle of order k. Then every PC or PCR refutation of a
Tseitin formula T(G, c) with odd total charge, and every resolution
refutation, has size at least 2^{c·k − c′·|U|}. The constants c, c′ > 0
depend only on Δ, L and ℓ.

**Corollary 2 (plane graphs with short faces).** Let G be a 2-connected plane
graph of maximum degree Δ in which any two faces share at most one edge (for
example, any 3-connected plane graph), with inner faces of length at most L.
Then refutation size is 2^{Ω_{Δ,L}(tw(G))}.

**Corollary 3 (grids).**
- For d ≥ 3, the d-dimensional grid [k]^d needs size 2^{Ω_d(k^{d−1})}, which
  is 2^{Ω(tw)}.
- For d = 2 the theorem applies with 8 exceptional edges and reproves
  `PC-SIZE-GRID-20261020-001B`.

**Corollary 4 (walls).** Let W′_r be the elementary wall of height r with its
degree-2 vertices suppressed. Then T(W′_r) needs size 2^{Ω(r)}.

**Lemma 5 (topological minors).** Suppose a subgraph S of G is a subdivision
of a graph W. Then the PCR (or resolution) size of T(G, c), for any odd c, is
at least the PCR (or resolution) size of T(W, c_W) for a suitable odd c_W,
minus O(|V(S)|).

**Corollary 6 (minor-free graphs).** If G excludes a fixed graph H as a minor,
then every PCR or resolution refutation of T(G, c) has size 2^{Ω_H(tw(G))}.
This holds for every maximum degree. For planar graphs the bound is
2^{Ω(tw(G))} with an absolute constant.

**Tightness.** For bounded degree, resolution refutations of size
2^{O(Δ·tw)}·poly(n) exist (Alekhnovich–Razborov 2011; Itsykson et al.), and
PCR simulates resolution. So Corollaries 2, 3, 4 and 6 are tight up to the
constant in the exponent.

Theorem 1 and Corollaries 2–4 also hold for PC, since they use restriction
only. Lemma 5 and Corollary 6 rename literals, so they are stated for PCR and
resolution.

## Proofs

### 1. The detour lemma

**Lemma 7.** Let D ⊆ E and G′ = G − D. Suppose each e = uv ∈ D has a u–v path
P_e in G′, and every edge of G′ lies on at most C of these paths. Then
|δ_G(X) ∩ D| ≤ C·|δ_{G′}(X)| for every X ⊆ V. Hence
|δ_G(X)| ≤ (C+1)·|δ_{G′}(X)|, and G′ is connected.

*Proof.* If e ∈ δ_G(X) ∩ D, its endpoints lie on opposite sides of X, so P_e
crosses δ(X) at an edge f(e) of G′. Each f is chosen by at most C edges e. If
G′ had a component X, then δ_{G′}(X) = ∅, so δ_G(X) = ∅ and X ∈ {∅, V}. ∎

### 2. Restrictions and retention

Distances are graph distances between vertex sets.
- **Active cells.** Each cell is *active* independently with probability
  p = 1/(N+1). Here N is the largest number of other cells within distance 2ℓ
  of a cell.
- **Selected cells.** An active cell is *selected* if no other active cell
  lies within distance 2ℓ of it.
- **The restriction.** ρ sets every edge of every selected cell to an
  independent uniform bit. Let D be the set of edges it sets.
- **Effect on the formula.** T(G, c)↾ρ = T(G − D, c′), and the total charge
  of c′ is still odd.

**Lemma 8.** For every ρ in the support and every X ⊆ V,
|δ_G(X)| ≤ (L+1)·|δ_{G−D}(X)|. In particular G − D is connected.

*Proof.* We build a detour system with congestion at most L and apply
Lemma 7.
- **One selected cell per edge.** Two selected cells share no edge, since
  they lie more than 2ℓ apart. So each e ∈ D lies on exactly one selected
  cell C_e. Take P_e = P_{C_e,e}.
- **P_e avoids D.** It avoids the edges of C_e by (C3). Every vertex of P_e
  is within ℓ of C_e, while any other selected cell is more than 2ℓ away.
- **Congestion.** An edge f of G − D on detours of two different selected
  cells would have an endpoint within ℓ of both, making them at most 2ℓ
  apart. So f lies on detours of at most one cell, hence of at most L edges
  e. ∎

### 3. The tangle survives

**Lemma 9.** If the cut function of G has a tangle T of order k, then that of
G − D has a tangle of order k′ = ⌊(k−1)/(L+1)⌋ + 1.

*Proof.* Let T′ = {X ∈ T : |δ_{G−D}(X)| ≤ k′−1}.
- If |δ_{G−D}(X)| ≤ k′−1, then by Lemma 8,
  |δ_G(X)| ≤ (L+1)(k′−1) ≤ k−1. So T contains X or V∖X, and that set is in
  T′.
- Properties (T2) and (T3) are inherited from T. ∎

### 4. The degree after restriction

**Lemma 10.** T(G − D, c′) has no PC or PCR refutation of degree d with
2d + 1 ≤ k′. So its degree is at least D₀ = ⌊(k′−1)/2⌋ + 1.

*Proof.* G − D is connected (Lemma 8) and its total charge is odd. Lemma 2 of
`PC-DEGREE-20261020-001B-P001` applies to the tangle of Lemma 9, restricted to
cuts of size at most 2d. Every axiom writable in degree d has a vertex of
degree at most 2d, so its singleton label is small. The extension to the
standard convention, the clause encoding and the 0/1 basis is parts 2–3 of
that theorem. PCR reduces to PC by substituting x̄ = 1 − x, which does not
raise degree. ∎

### 5. Killing literals

**Lemma 11.** Let ℓ_e be a literal of an edge e ∉ U. Then ℓ_e is set to 0
with probability at least q = p(1−p)^N/2.

The events for edges more than 4ℓ + 3L apart are independent. Let R be the
largest number of edges within distance 4ℓ + 3L of an edge, so
R ≤ 2Δ^{4ℓ+3L+1}. A monomial on t variables then survives with probability at
most (1−q)^{(t−|U|)/R}.

*Proof.*
- **Probability.** A cell containing e is selected with probability at least
  p(1−p)^N. Given that, e's bit is uniform.
- **Independence.** The event depends only on e's bit and on the activity of
  cells within 2ℓ + L of e. For edges more than 4ℓ + 3L apart these sets are
  disjoint.
- **Counting.** A greedy choice keeps (t − |U|)/R pairwise-far variables of
  the monomial. ∎

### 6. Proof of Theorem 1

Let π be a PC or PCR refutation of size S with S·(1−q)^{(D₀−|U|)/R} < 1.
- By Lemma 11 and a union bound over the monomials of π, some ρ in the
  support kills every monomial with at least D₀ variables.
- Restricting π by ρ gives a refutation of T(G − D, c′) of degree below D₀,
  which contradicts Lemma 10.

Hence S ≥ (1−q)^{−(D₀−|U|)/R} = 2^{c·k − c′·|U|}.

For resolution, PCR simulates resolution with polynomial overhead, so the
same bound holds up to that overhead. ∎

### 7. Corollary 2

Take the inner faces as cells, with U = ∅.
- **(C1), (C2).** Inner faces have length at most L. The graph is
  2-connected, so every edge lies on two distinct faces, at most one of which
  is the outer face.
- **(C3).** Let f be an inner face and e = uv an edge of f.
  - If e's other face g is inner, then g − e avoids the edges of f, since the
    two faces share only e. Its length is at most L − 1.
  - Otherwise e is f's only edge on the outer face. Each other edge e_i of f
    lies on an inner face g_i, which shares only e_i with f. Concatenating
    the paths g_i − e_i around f joins u to v, avoids every edge of f, and
    has length at most L².
- **The tangle.** By the duality theorem, the cut function has a tangle of
  order cvw(G).
- **Carving width against treewidth.** cvw(G) ≥ (tw(G)+1)/6 once tw ≥ Δ.
  From a carving of width w, put into each internal node's bag the endpoints
  of the edges crossing its three tree edges, and into each leaf v's bag v
  and its neighbours. A vertex x appears exactly along the tree paths from
  x's leaf to its neighbours' leaves, which form a connected subtree. Bags
  have at most 6w vertices.
- **Conclusion.** Theorem 1 gives 2^{Ω(tw)}. ∎

### 8. Corollary 3

Take the unit squares as cells.
- **d ≥ 3.** An edge e of a square C also lies on a square in a different
  plane, which shares only e with C. That gives a detour of length 3, with
  U = ∅ and L = 4.
- **The tangle.** The tangle order is at least the balanced edge-cut of
  [k]^d, which is Θ(k^{d−1}), as is the treewidth.
- **d = 2.** Use the non-corner squares as cells. The 8 boundary edges at the
  corners form U, and ℓ = 9 (the check measures it). ∎

### 9. Corollary 4

W′_r is a 2-connected plane graph whose faces pairwise share at most one edge.
- **Faces.** Two bricks share at most one edge. Suppression merges each
  boundary path, and each corner's two boundary sides, into a single edge.
  So each brick shares at most one edge with the outer face.
- **Bounds.** Inner faces have length at most 6, and the maximum degree is 3.
- **Treewidth.** tw(W′_r) = tw(W_r) ≥ r − O(1), because W_r contracts to an
  r × r grid.

Corollary 2 applies. ∎

### 10. Lemma 5

Let F be the set of edges of G not in S.
- **Restriction with parity correction.** Every component of (V, F) contains
  a vertex of S. If a component K had none, no edge of S would touch K, and
  then K would be a component of G that misses S, which is impossible. Root a
  spanning forest of (V, F) at the vertices of S. Then choose values on F,
  bottom-up, that make every vertex outside S even. This gives
  T(G, c)↾ρ = T(S, c_S) with odd total. The constraints outside S are
  satisfied and drop out.
- **Renaming along paths.** Take a path a = w₀, …, w_m = b of S whose inner
  vertices have degree 2, with edges e₁, …, e_m. Rename
  x_{e_j} := x_{e₁} ⊕ σ_j, where σ₁ = 0 and σ_{j+1} = σ_j ⊕ c_S(w_j). This
  is a literal renaming, free in PCR and in resolution. It makes each inner
  constraint trivial and moves charge σ_m to b. Trivial axioms cost O(1)
  each in PCR, since x·x̄ = x − x² = 0. The result is T(W, c_W), and its total
  charge is still odd. ∎

### 11. Corollary 6

- **Grid minors.** If G excludes H as a minor and tw(G) ≥ c_H·g, then G has a
  g × g grid minor (Demaine–Hajiaghayi, Combinatorica 2008). For planar G,
  tw(G) ≤ 6g − 5 when there is no g × g grid minor (Robertson–Seymour–Thomas,
  JCTB 1994).
- **A wall.** The g × g grid contains the wall W_h with h ≈ g/2 as a
  subgraph. A minor of maximum degree 3 is a topological minor, so G contains
  a subdivision of W_h, hence of W′_h.
- **Conclusion.** Lemma 5 and Corollary 4 give 2^{Ω(h)} = 2^{Ω_H(tw(G))}.
  No step uses the maximum degree of G. ∎

## Checks

`check.py` covers the following:

| Check | Result |
| --- | --- |
| (C1)–(C3) on grids (5×6, 8×8, with the 8 corner edges exceptional), triangulated grids (6×6, 10×10), suppressed walls (r = 2…10) and 3D grids (3×3×3, 4×4×4, 3×4×5) | hold. L = 4, 3, 6, 4 and ℓ = 9, 4, 13, 3. Faces pairwise share at most one edge. The small plane instances are 3-connected. |
| Detour systems under the selection rule: wall14, trigrid14×14, grid3d 6×6×6, 200 samples each (≈80 selections) | every detour avoids D; largest congestion 2 ≤ L |
| Retention, exhaustive over all X, for every single cell: wall3, trigrid4×5, grid4×5, grid3d 2×3×3, grid3d 2×2×5 | worst ratio 3 ≤ L+1; no cut vanishes |
| Control: two bricks of wall3 only 2 apart, below the radius rule | some cuts vanish, so the radius is needed |
| Selection probabilities on wall20 | match p(1−p)^{|conflicts|}, z ≤ 2 |
| Transfer to a wall topological minor inside a 6×9 grid with a pendant path and triangle | the correction forest reaches every vertex; all outside vertices even; wall total odd. Over 300 random assignments the renamed formula is equivalent to the suppressed wall's. |
| Constants for walls | q ≈ 4.6·10⁻⁴, R ≈ 4.8·10³, so ≈ 10⁻⁸ bits per unit of tangle order. Asymptotic only. |

## Scope

- **General graphs.** This does not settle 2^{Ω(tw)} for all bounded-degree
  graphs, which is open even for resolution (`GENERAL-SIZE-20261020-001`
  takes it up). Graphs without short cycles have no cell system.
- **Constants.** The constants are poor; nothing was optimized.
- **Characteristic 2.** Characteristic 2 is excluded for PC and PCR. The
  resolution bounds do not depend on a field.

## Novelty

A targeted search on 2026-10-20 found the following:
- regular resolution is 2^{Θ(tw)} for all graphs (Itsykson et al.);
- bounded-depth Frege gets 2^{tw^{Ω(1/d)}} on all graphs (Galesi et al.) and
  near-tight bounds on grids (Håstad; Håstad–Risse);
- PCR results on grids cover XOR-substituted grids and space.

It found no statement of 2^{Ω(tw)} for general resolution or PCR on planar,
minor-free or d-dimensional grid graphs. The ingredients are standard, and the
detour lemma is elementary. No human expert has reviewed this.
