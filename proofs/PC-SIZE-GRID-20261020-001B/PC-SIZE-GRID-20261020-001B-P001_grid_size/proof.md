# Polynomial calculus size of Tseitin formulas on grids is exponential in the side

Status: Proved

Ticket `PC-SIZE-GRID-20261020-001B`, 2026-10-20. It builds on the tangle
lemma of `PC-DEGREE-20261020-001B-P001` (Lemma 2 there).

## Theorem

Let G = G_{a,b} be the a × b grid, let c be any charge with odd total, and let
F be a field of characteristic other than 2.
- **Lower bound.** Every refutation of the Tseitin formula T(G, c) in
  polynomial calculus over the 0/1 basis (PC), or in polynomial calculus with
  twin variables (PCR), has size at least 2^{γ·min(a,b) − O(1)}. Here
  γ = log₂(1/(1−q))/(30·360) ≈ 1.0·10⁻⁶, and q = p(1−p)²⁴/2 with p = 1/25.
- **Upper bound.** There are PC and PCR refutations of size
  2^{O(min(a,b))}·poly(ab).
- **So** the size is 2^{Θ(min(a,b))}·poly(ab). For the n × n grid that is
  2^{Θ(√N)}, with N the number of vertices.

Size counts monomials over all lines of a refutation. No other property of the
size measure is used.

The size–degree relation of Impagliazzo, Pudlák and Sgall gives nothing here.
The degree is Θ(min(a,b)) and the number of variables is ≈ 2ab, so
degree²/variables is O(1).

## Proof

### 1. Restrictions that delete well-separated faces

The faces of G are the unit squares F_{i,j}. A face is a *candidate* unless it
is one of the four corner faces.

The distribution 𝒟(p):
- Each candidate face is *active* independently with probability p.
- An active face is *selected* if no other active candidate lies within
  L∞-distance 2 of it. So selected faces lie at pairwise L∞-distance at least
  3.
- ρ gives the four edges of every selected face independent uniform values,
  and leaves every other edge free.

**Effect on the formula.** Write D for the set of edges ρ assigns and
G′ = G − D. Then T(G, c)↾ρ = T(G′, c′), where c′ adds to c the values
assigned at each vertex. Each assigned edge changes two charges by the same
bit, so the total charge stays odd.

### 2. The cut lemma: every cut keeps a fifth

**Lemma 1.** Let a, b ≥ 3. For every ρ in the support and every X ⊆ V,
|δ_G(X)| ≤ 5·|δ_{G′}(X)|. In particular G′ is connected.

*Proof.* Work in the plane dual: its vertices are the faces and the outer
face o, and each edge of G is a dual edge between its two sides. An edge is
deleted exactly when one of its sides is selected. Three facts follow from
the construction:
- (i) No face is edge-adjacent to two selected faces, since any two faces
  adjacent to a common face are within L∞-distance 2. In particular, no two
  selected faces are adjacent.
- (ii) Two distinct inner faces share at most one edge.
- (iii) A selected face shares at most one edge with o, because corner faces
  are excluded.

The cut δ_G(X) is an even subgraph of the dual, since every face boundary
crosses it an even number of times. So it splits into edge-disjoint simple
dual cycles.

Fix such a cycle φ₀, e₁, φ₁, …, e_r, φ_r = φ₀. Call e_t *free* if it is
deleted, which happens exactly when one of φ_{t−1}, φ_t is selected.
- **A free run is short.** Take a maximal run of consecutive free crossings
  e_t, …, e_{t+ℓ−1}. A face strictly inside the run has both of its crossings
  free.
  - If such a face is not selected, both of its run neighbours are selected.
  - By (i) and (ii) that face cannot be an inner face, so it is o.
  - By (iii) its two neighbours are different selected faces.
  - Selected faces alternate with non-selected ones, and o occurs at most
    once in a simple cycle. So the interior of a run alternates selected
    faces with o, using o at most once. It has at most three faces (f, o, f′
    at most), and ℓ ≤ 4.
- **No cycle is entirely free.** That would need either a two-edge dual cycle
  f, o, which (iii) excludes, or o to appear twice.
- **Counting.** So at least one crossing in every five is kept:
  |δ_{G′}(X)| ≥ |δ_G(X)|/5.

**Connectivity.** If X were a component of G′, then δ_{G′}(X) = ∅, so
δ_G(X) = ∅ and X ∈ {∅, V}. ∎

### 3. Isoperimetry of the grid

**Lemma 2.** If ab/3 ≤ |X| ≤ 2ab/3, then |δ_G(X)| ≥ min(a,b)/3.

*Proof.* Let Y = V ∖ X. There are a rows of b vertices each.
- If some row lies in X and another lies in Y, then each of the b columns
  contains a cut edge.
- Otherwise suppose, say, that no row lies in Y. Then every vertex of Y lies
  in a row meeting both sides, so at least |Y|/b ≥ a/3 rows each contain a
  cut edge. The case where no row lies in X is the same with X in place of Y.

Either way |δ_G(X)| ≥ min(a,b)/3. ∎

### 4. The restricted formula still needs degree Ω(min(a,b))

**Lemma 3.** Let k = ⌈min(a,b)/15⌉ ≥ 5. For every ρ in the support, T(G′, c′)
has no PC or PCR refutation of degree d whenever 2d + 1 ≤ k. Hence its degree
is at least D = ⌊(k−1)/2⌋ + 1, which is about min(a,b)/30.

*Proof.* Let T′ = {X : |δ_{G′}(X)| ≤ k−1 and |X| < ab/3}. This is a tangle of
order k of the cut function of G′:
- **(T1).** If |δ_{G′}(X)| ≤ k−1, then Lemma 1 gives
  |δ_G(X)| ≤ 5(k−1) < min(a,b)/3. By Lemma 2, X is unbalanced, so X ∈ T′ or
  V∖X ∈ T′.
- **(T2).** Three sets of fewer than ab/3 vertices cannot cover V.
- **(T3).** |V∖{v}| ≥ ab/3.

G′ is connected (Lemma 1), and its total charge is odd. Every degree is at
most 4 ≤ 2d. So Lemma 2 of `PC-DEGREE-20261020-001B-P001`, the tangle
invariant applied to the restriction of T′ to cuts of size at most 2d, shows
that the reduced closure of degree d does not refute. The other systems
follow:
- the standard convention, the clause encoding and the 0/1 basis, by parts 2
  and 3 of that theorem;
- PCR, by substituting x̄ = 1 − x, which does not raise degree. ∎

### 5. Killing large monomials

**Lemma 4.** Let ℓ be a literal x_e or x̄_e, where e is not one of the 8
boundary edges at the corners. Then ℓ is set to 0 with probability at least
q = p(1−p)²⁴/2.

The events for edges whose containing faces are at pairwise L∞-distance at
least 5 are independent. Any t such edges include t/360 at that spacing. So a
monomial with at least D variables survives ρ with probability at most
(1 − q)^{(D−8)/360}.

*Proof.*
- **Probability.** A candidate face is selected with probability
  p(1−p)^{|N(f)|} ≥ p(1−p)²⁴, where N(f) is the set of other candidates
  within distance 2. Every non-corner edge lies on a candidate face, and its
  value is uniform.
- **Independence.** The event for e depends only on the activity of faces
  within distance 2 of the faces containing e, and on e's own bit. These sets
  are disjoint for edges whose faces are 5 or more apart.
- **Spacing.** The faces within distance 4 of the at most two faces
  containing e number at most 90, and they carry at most 360 edges. ∎

### 6. Size

Let π be a PC or PCR refutation of T(G, c) of size S, and suppose
S·(1 − q)^{(D−8)/360} < 1.
- By Lemma 4 and a union bound over all monomials of π, some ρ in the support
  kills every monomial with at least D variables.
- Restricting a PC or PCR refutation by a partial assignment gives a
  refutation of the restricted formula. So π↾ρ refutes T(G′, c′) with degree
  below D.
- That contradicts Lemma 3.

Hence S ≥ (1 − q)^{−(D−8)/360} ≥ 2^{γ·min(a,b) − O(1)}. ∎

### 7. Upper bound

Eliminating variables column by column along the shorter side gives a
resolution refutation of width O(min(a,b)) and size 2^{O(min(a,b))}·poly(ab).
- PCR simulates resolution clause for clause.
- PC expands each clause of width w into at most 2^w monomials.

Both stay within 2^{O(min(a,b))}·poly(ab).

## Checks

`check.py` runs in about 140 s:

| Check | Result |
| --- | --- |
| Lemma 1, exhaustive: every valid selection and every X on the 4×4, 4×5, 5×5, 4×6, 3×8 and 4×7 grids | holds; the factor 5 is attained, so the lemma is sharp; no nontrivial cut vanishes |
| Lemma 1, sampled: 12×12, 20×20 and 30×17 grids, p = 1/25 and the stress value 0.3; 3,593 vertex sets from rectangles, unions, grown regions, random sets and sets hugging the holes | holds; every restricted grid connected |
| Controls for Lemma 1: separation 2, or corner faces allowed (5×5) | each breaks the lemma: ratios up to 7–11, or cuts that vanish |
| Lemma 2, exhaustive, every grid with at most 28 vertices | holds; the minimum balanced cut is min(a,b) there |
| Lemma 4: exact selection probabilities on a 30×30 grid against 20,000 samples; independence of far edges | z ≤ 3.4; joint-kill z = 1.2; minimum literal kill probability 0.0075 = q |
| Lemma 3 sanity: degree of every damaged 5×5 grid by the label closure | consistent; the tangle bound is nontrivial only on the undamaged grid (degree 4 ≥ 3) |
| The constant: γ = 1.007·10⁻⁶ ≥ 10⁻⁶ | holds |
| ±1 control: restrictions in the ±1 basis never kill a monomial, consistent with the polynomial-size ±1 refutations | holds |

## What this does and does not settle

- **Polynomial calculus.** It gives the first exponential size lower bound we
  know of for polynomial calculus or PCR on plain grid Tseitin formulas,
  meaning bounded degree and no substitution, and it is tight. Beck,
  Nordström and Tang (STOC 2013) handled the XOR-substituted grid, where each
  edge is doubled. Their remark that random restrictions break plain
  bounded-degree grids is what the separated-face restrictions address.
- **Resolution.** Resolution on grids was already covered by lower bounds for
  bounded-depth Frege (Håstad; Håstad and Risse).
- **General graphs.** Whether Tseitin formulas on all bounded-degree graphs
  need size 2^{Ω(tw)} is open even for resolution, and this does not settle
  it. The argument uses short faces. Any plane graph of bounded degree whose
  inner faces are short and share at most one edge with the outer face should
  go through the same way, but this is not proved here.
- **Constants and characteristic.** The constant γ is far from optimal.
  Characteristic 2 is excluded: there Tseitin has polynomial-size refutations.

## Novelty

A targeted search on 2026-10-20 covered:
- polynomial calculus size of Tseitin on grids (Beck–Nordström–Tang 2013;
  Filmus–Lauria–Mikša–Nordström–Vinyals, on space; Mouli 2024, on bases);
- resolution and treewidth (Itsykson, Riazanov and Smirnov 2022: open for
  general resolution);
- bounded-depth Frege on grids (Håstad; Håstad and Risse; Galesi et al.).

It found no statement of this bound. The ingredients are standard: random
restrictions, and complexity measures on binomials in the style of Buss,
Grigoriev, Impagliazzo and Pitassi. The bound may be known to specialists. No
human expert has reviewed it.
