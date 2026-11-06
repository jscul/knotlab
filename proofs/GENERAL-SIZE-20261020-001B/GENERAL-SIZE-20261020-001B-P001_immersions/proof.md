# Tseitin size on all graphs: an immersion transfer, a polynomial-exponent bound, and a reduction that meets an obstruction

Status: Proved

Lemma 1, Theorems 2 and 3, and parts (i) and (ii) of Proposition 5 are
proved below.
- **Theorem 3 is a reduction.** Its hypothesis, Conjecture 4, is not proved.
- **Proposition 5** shows that half of that hypothesis fails on a natural
  family of graphs. Its part (iv) is proved from part (iii), which is a
  sketch.

Ticket `GENERAL-SIZE-20261020-001B`, 2026-10-20. It builds on two earlier
results:
- `CELL-SIZE-20261020-001B-P001`: Theorem 1 (the cell theorem), Corollary 4
  (walls) and Lemma 5 (topological minors);
- `PC-DEGREE-20261020-001B-P001`: PC degree is about half the carving width.

PCR is over a field of characteristic other than 2. Size counts monomials
(PCR) or clauses (resolution).

## The open problem

Do resolution refutations of a Tseitin formula T(G, c) on a bounded-degree
graph G need size 2^{Ω(tw(G))}? Refutations of size 2^{O(tw)}·poly(n) exist
(Alekhnovich–Razborov).
- **Regular resolution: yes.** Itsykson, Riazanov and Smirnov (SAT 2022) prove
  2^{Ω(tw)}, up to a polynomial factor, for all graphs. This follows
  2^{Ω(tw/log n)} by Itsykson, Riazanov, Sagunov and Smirnov, and
  de Colnet–Mengel for bounded degree.
- **General resolution: open.** Size–width gives 2^{Ω(tw²/n)}. Bounded-depth
  Frege gives 2^{tw^{Ω(1)}} (Galesi, Itsykson, Riazanov and Sofronova).
- **PCR.** Size–degree gives 2^{Ω(tw²/n)}. `CELL-SIZE-20261020-001` gives
  2^{Ω(tw)} on planar, minor-free and grid-like graphs.

## Statements

**Weak immersion.** A *weak immersion* of H in G maps the vertices of H to
distinct vertices of G, and each edge ab to a path P_ab from φ(a) to φ(b). The
paths are pairwise edge-disjoint. They may share vertices, including images of
other vertices.

**Lemma 1 (immersion monotonicity).** Let G be connected with maximum degree
Δ, and let a connected graph H be weakly immersed in G. For every odd charge c
on G there is an odd charge c_H on H with
size_P(T(H, c_H)) ≤ 2^{O(Δ)}·size_P(T(G, c)), for P = resolution and
P = PCR.

**Theorem 2 (all graphs).** Let G be a connected graph of treewidth t and c an
odd charge. Every resolution or PCR refutation of T(G, c) has size
2^{Ω(t^{1/9}/polylog t)}.
- For resolution, Galesi et al. already give 2^{t^{Ω(1)}}.
- For PCR, we know of no earlier bound of this kind.

**Cellular and compact.** Call a graph H:
- *cellular* if it has a cell system (𝒞, U; L, ℓ), as in
  `CELL-SIZE-20261020-001B-P001`, with L, ℓ ≤ λ₀ and |U| ≤ ε₀·tw(H). Here λ₀ is
  a fixed constant and ε₀ = ε₀(λ₀) > 0 is small enough for Theorem 1 there;
- *compact* if |V(H)| ≤ tw(H)·polylog tw(H).

**Theorem 3 (reduction).** Suppose every graph of maximum degree 3 and
treewidth t contains a topological minor H that is cellular or compact, with
tw(H) ≥ t/polylog t. Then for every connected graph G and odd charge c,
resolution and PCR refutations of T(G, c) have size
2^{Ω(tw(G)/polylog tw(G))}.

**Conjecture 4.** The hypothesis of Theorem 3 holds.

**Remark (immersions add nothing to Theorem 3).** By Lemma 1, the hypothesis
could be weakened to weak immersions in bounded-degree graphs. That would not
make it easier to prove.
- It must still hold for graphs of maximum degree 3.
- There, a weak immersion of a graph of minimum degree at least 2 is a
  topological minor. Two paths through a vertex need four edges, and a path
  through a branch vertex of degree d needs d + 2.

So the crossings that immersions allow, which motivated Lemma 1, are not
available where the problem lives.

**Wall networks.** Fix a connected cubic graph K on m vertices (the skeleton)
and integers w ≥ 2 and b dividing w. The graph G(K, w, b) has maximum
degree 3 and is built as follows.
- **Walls.** Each vertex a of K carries a copy W_a of the elementary wall of
  height 2w. W_a has three disjoint *arcs* of w degree-2 boundary vertices
  (*ports*), in order along its boundary cycle.
- **Bundles.** Each edge ac of K carries a perfect matching between an arc of
  W_a and an arc of W_c, each arc used once.
- **Block scrambling.** Read each arc in boundary order and cut it into blocks
  of b consecutive ports. The matching sends the j-th block of one arc to the
  j-th block from the end of the other, by an arbitrary bijection inside each
  block.

At b = 1 every bundle reverses order. At b = w it is an arbitrary bijection.

**Proposition 5 (block scrambling defeats compact minors).** Let G = G(K, w, b).
- (i) tw(G) ≤ 3mw/2 + 2w + 2.
- (ii) Every topological minor H of G satisfies
  tw(H) ≤ C·√(m·(|V(H)| + mwb)), for an absolute constant C.
- (iii) *(Sketch.)* If K has edge expansion at least h > 0, then
  tw(G) ≥ c_h·m·w for w ≥ w₀(h).
- (iv) Suppose K is as in (iii). If a topological minor H has
  tw(H) ≥ tw(G)/λ and |V(H)| ≤ λ·tw(H), for some λ ≥ 1, then
  w ≤ C_h·λ²·b.

In particular, take λ = polylog(mw), b = √w and w large. Then no compact
minor keeps the treewidth up to polylog factors, so case (b) of Conjecture 4
fails for G(K, w, √w).

## Proofs

### Lemma 1

Let π be a refutation of T(G, c), and let G″ be the union of the paths P_ab.
G″ is connected, because H is.

1. **Restriction with parity correction.** Let F = E(G) ∖ E(G″).
   - Every component of (V(G), F) meets V(G″). A component that did not would
     touch no edge of G″, so it would be a whole component of G.
   - Root a spanning forest of (V(G), F) at vertices of G″. Choosing values on
     F bottom-up makes every vertex outside G″ even.
   - This gives π↾ρ, a refutation of T(G″, c″) of no larger size. The total of
     c″ is odd, since each assigned edge changes two charges.
2. **Identification is a weakening.** At each vertex v of G″, the incident
   edges of G″ fall into groups. There is one pair for each path passing
   through v, and, if v = φ(a), one group of deg_H(a) path ends.
   - Let G_split replace v by one copy per group. Put all of c″(v) on one copy
     and 0 on the others.
   - v's constraint is the sum mod 2 of its copies' constraints. So each
     clause of v's constraint follows from the copies' clauses, which use the
     same at most Δ variables.
   - Resolution derives such a clause in size 2^{O(Δ)}, and PCR simulates
     resolution.
   - Replace every axiom line of π↾ρ by such a derivation. This refutes
     T(G_split) in size at most 2^{O(Δ)}·size(π).
3. **Renaming.** The paths no longer share vertices, so G_split is a
   subdivision of H.
   - Rename along each path, as in Lemma 5 of `CELL-SIZE-20261020-001B-P001`.
     This is a literal renaming: free in resolution, and in PCR each
     now-trivial axiom line costs O(1).
   - The result refutes T(H, c_H), where c_H carries the pushed charges and has
     odd total. ∎

**On Lemma 5 of `CELL-SIZE-20261020-001B-P001`.**
- That lemma is stated with an additive loss of O(|V(S)|). Its proof gives the
  multiplicative form size_P(T(W, c_W)) ≤ O(size_P(T(G, c))). Only the trivial
  axioms that a refutation actually uses need an O(1) derivation.
- The additive form becomes vacuous when |V(G)| is exponential in the
  treewidth. The multiplicative form is used below, and it keeps Corollary 6
  there true as stated.

### Theorem 2

- **Grid minor.** By Chuzhoy and Tan (JCTB 146, 2021), every graph of
  treewidth t has a g × g grid minor with g = Ω(t^{1/9}/polylog t).
- **Wall.** The grid contains the wall W_h with h ≈ g/2. A minor of maximum
  degree 3 is a topological minor, so G contains a subdivision of W_h, and
  hence of W′_h.
- **Conclusion.** Lemma 5 (multiplicative form) and Corollary 4 of
  `CELL-SIZE-20261020-001B-P001` give 2^{Ω(h)}. No step uses the maximum
  degree of G. ∎

### Theorem 3

- **Reduce to maximum degree 3.** By the degree-3 treewidth sparsifier of
  Chekuri and Chuzhoy (SODA 2015), G contains a subdivision S of a graph of
  maximum degree 3, with tw(S) ≥ tw(G)/polylog tw(G).
- **Find H.** By hypothesis, S contains a subdivision of a cellular or compact
  H with tw(H) ≥ tw(S)/polylog. That subdivision is a subgraph of G.
- **Transfer.** Lemma 5 of `CELL-SIZE-20261020-001B-P001` (multiplicative
  form) gives size_P(T(G, c)) ≥ Ω(size_P(T(H, c_H))). Note that H has maximum
  degree 3.
- **Cellular H.** Its cut function has a tangle of order
  cvw(H) ≥ (tw(H)+1)/6. This uses the duality theorem and the bound from
  Corollary 2's proof there. Theorem 1 then gives
  2^{c·cvw(H) − c′|U|} ≥ 2^{Ω(tw(H))}, since |U| ≤ ε₀·tw(H) with ε₀ small.
- **Compact H.** T(H) has |E(H)| ≤ 3|V(H)|/2 variables and initial width 3.
  - Its PCR degree is at least ⌈cvw(H)/2⌉ ≥ tw(H)/12, by
    `PC-DEGREE-20261020-001B-P001` for the clause encoding.
  - Its resolution width is at least its PCR degree.
  - The size–width relation of Ben-Sasson and Wigderson, and the size–degree
    relation of Impagliazzo, Pudlák and Sgall (which holds for PCR), give
    2^{Ω(tw(H)²/|V(H)|)} = 2^{Ω(tw(H)/polylog tw(H))} once tw(H) is large. ∎

### Remark

Let a weak immersion of H, of minimum degree at least 2, lie in a graph of
maximum degree 3. Then no vertex lies inside two paths, and no path passes
through a branch vertex. So the paths are internally disjoint, and H is a
topological minor. ∎

### Proposition 5

**(i) Upper bound.**
- Order the walls W_{a_1}, …, W_{a_m}. Let P hold, for each bundle edge, its
  endpoint in the earlier wall, so |P| = 3mw/2.
- Sweep the walls in order, each column by column. A wall of height 2w has
  pathwidth at most 2w + 1. Add P to every bag.
- Every bundle edge then has its earlier end in every bag and its later end in
  some bag of its own wall. ∎

**(ii) The surface bound.**
1. **The surface.** Thicken K into a ribbon surface: a disk per vertex holding
   its wall, and an untwisted band per edge.
   - Draw each bundle inside its band. Blocks map to blocks in reversed order,
     so block strips are disjoint.
   - Crossings occur only between edges of the same block: at most
     (3m/2)(w/b)·C(b,2) ≤ 3mwb/4 in all.
   - The ribbon surface has Euler characteristic m − 3m/2. Capping its
     boundary gives a closed orientable surface Σ of genus at most
     m/4 + 1/2.
2. **Planarize.** Let S ⊆ G be a subdivision of H. Put a vertex at each
   crossing of S's drawing, then suppress degree-2 vertices. This gives a
   graph H′ embedded in Σ with |V(H′)| ≤ |V(H)| + 3mwb/4.
3. **Bound tw(H′).** Graphs of genus g on n vertices have balanced separators
   of size O(√((g+1)n)) (Gilbert, Hutchinson and Tarjan 1984). This holds for
   every subgraph, so tw(H′) = O(√(m·|V(H′)|)).
4. **Return to H.** H is obtained from H′ by splitting each crossing vertex
   into two, then suppressing. Splitting at most doubles bags, so
   tw(H) ≤ 2·tw(H′) + 1. ∎

**(iii) Lower bound (sketch).** Let |X| ≤ δ·m·w.
- **Good walls.** Call a wall good if it holds at most δ′w vertices of X.
  - Removing x vertices from a wall cuts off O(x) of its boundary vertices
    from the rest. A cut of length x encloses a boundary stretch of length
    O(x).
  - So in a good wall, one component keeps all but O(δ′w) ports of each arc.
- **Good bundles.** Two adjacent good walls are joined by at least
  w − O(δ′w) bundle edges between their large components.
- **Bad walls are few.** At most (δ/δ′)m walls are bad. Removing them from the
  expander K leaves a component with all but O((δ/δ′)m/h) vertices.
- **Conclusion.** One component of G − X holds most ports. So balanced
  separators, weighted by ports, have size above δmw, and
  tw(G) ≥ δmw − 1. This argument does not use the bundles' order.

**(iv) Combining.** Let t = tw(H) ≥ c_h·m·w/λ.
- Part (ii) with |V(H)| ≤ λt gives t² ≤ C²m(λt + mwb). Hence
  t ≤ C²mλ + Cm√(wb).
- Dividing by m: c_h·w/λ ≤ C²λ + C√(wb).
- If C²λ dominates, then w ≤ 2C²λ²/c_h. Otherwise
  w ≤ 4C²λ²b/c_h². Either way w ≤ C_h·λ²·b, since b ≥ 1. ∎

## Evidence on wall networks

`check.py` builds G(K, w, b) on a random cubic skeleton with m = 16. It
measures three things:
- **E1.** Cell systems in G, with degree-2 vertices suppressed.
- **E2.** The spectral gap 3 − λ₂ of two topological minors, built explicitly.
- **E3.** The shortest cycle through each bundle edge (m = 4, w = 64).

| Measurement | Result | Reading |
| --- | --- | --- |
| E1: ordered bundles (b = 1), cells = bricks and the 6-cycles through neighbouring bundle edges | U = ∅, L = 6, longest detour ℓ = 17, at w = 12 and 24 | G itself is cellular: case (a) |
| E2: wall boundary cycles plus bundles, uniform bundles (b = w) | gap 0.0064, 0.0029, 0.0014 at w = 12, 24, 48 | about 1/w; not compact |
| E2: three nested ladders routed vertex-disjointly in each wall (3w − 6 branch vertices per wall) plus bundles, uniform bundles | gap 0.054, 0.042, 0.044 | stays near 0.04: compact, case (b) |
| E2: the same ladders, ordered bundles (b = 1), and b = 4 at w ≥ 24 | gap 0 (disconnected) | the ladder minor needs mixing |
| E3: median (max) shortest cycle through a bundle edge, b = 1, 4, 16, 64 | 6 (6), 6 (10), 8 (16), 12 (18) | about 4 + √b: cells only at scale √b |

So, on the measured instances, uniform and ordered bundles each satisfy the
hypothesis of Theorem 3, through different cases. The choice of minor matters: the obvious one, boundary cycles, is not
compact, while the ladders are.

Block scrambling at b ≈ √w breaks both cases:
- **Case (b) fails.** Proposition 5 rules out compact minors.
- **Case (a) degrades.** G's own cells have length about w^{1/4}, where the
  constants of the cell theorem degrade.
- **Natural cellular minors lose treewidth.** Natural cellular minors keep
  only order-consistent tracks. Heuristically, that is about √b tracks of
  each block, losing a factor √b of treewidth.

We did not prove that every cellular minor fails. G(K, w, √w) on an expander
K is therefore a candidate counterexample to Conjecture 4, and the cheapest
test case for any method aiming at 2^{Ω(tw/polylog tw)}.

## What this leaves open

The search was to stop if no restriction keeps a large tangle in graphs
without short cycles. That condition is met.
- **The two tools.** Random restrictions keep a tangle only where deleted
  edges have short detours (cells). Size–width and size–degree need the
  number of variables close to the treewidth (compactness).
- **Theorem 3** reduces the open problem to finding one of the two inside a
  topological minor.
- **Proposition 5** gives graphs where compactness provably fails and cells
  exist only at a growing scale.
- **What closing the gap needs.** Either a restriction argument whose loss is
  polylogarithmic in the cell length, or a different method.

## Checks of Lemma 1

`check.py` builds weak immersions of non-planar graphs in planar grids, by
random placement and edge-disjoint routing. It then checks every step of
Lemma 1:

| Instance | Crossings | Paths edge-disjoint | Outside vertices even | Split implies original (all assignments) | Subdivision of H | Renamed formula equivalent, odd charge (300 random assignments) |
| --- | --- | --- | --- | --- | --- | --- |
| K₃,₃ in the 6×6 grid | 5 | yes | yes | yes | yes | yes |
| Petersen in the 10×10 grid | 16 | yes | yes | yes | yes | yes |

Neither graph is a topological minor of a planar grid, so these transfers need
immersions. The whole check runs in about 10 s.

## Scope

- **Not proved.**
  - Conjecture 4, and therefore the open problem.
  - Proposition 5(iii), which is a sketch.
  - Any claim about E1–E3 beyond the measured instances.
- **Proof systems.** Lemma 1 holds for resolution and PCR. PC without twin
  variables is not covered, because renaming does not preserve its size.
- **Constants.** Theorem 2's exponent is limited by the grid-minor theorem.

## Novelty

A targeted search on 2026-10-20 found:
- no use of immersions, or of vertex identification as a weakening, to
  transfer Tseitin lower bounds;
- no PCR bound for all graphs in terms of treewidth.

The reduction and the wall networks were not searched for separately. Lemma 1
is elementary. Proposition 5 combines the genus separator theorem with a
crossing count. No human expert has reviewed this.
