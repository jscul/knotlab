# Sum-of-squares and Sherali–Adams on Tseitin formulas: degree is the carving width, and size is 2^{Θ(tw)} beyond expanders

Status: Proved

Ticket `SOS-SIZE-20261020-001B`, 2026-10-20. It builds on:
- `PC-DEGREE-20261020-001B-P001`: tangles, the duality theorem and the PC
  degree upper bound;
- `CELL-SIZE-20261020-001B-P001`: cell systems, the restriction and its
  lemmas;
- `GENERAL-SIZE-20261020-001B-P001`: the bound for all graphs.

It also cites:
- Berkholz (STACS 2018, "The relation between polynomial calculus,
  Sherali–Adams, and sum-of-squares proofs") for the definitions and for the
  simulation of polynomial calculus by sum-of-squares;
- Atserias and Dalmau (JCSS 2008) for the pebble-game characterization of
  resolution width.

## Setting

- **The formula.** G = (V, E) is connected, and c: V → {0, 1} has c(V) odd.
  The variables are x_e ∈ {0, 1}. We also write y_e = 1 − 2x_e ∈ {±1}, a
  linear change of variables that preserves degree.
- **Notation.**
  - s_v = (−1)^{c(v)}, s_U = ∏_{v∈U} s_v, and y_F = ∏_{e∈F} y_e.
  - δ(U) is the set of edges leaving U, E(v) = δ({v}), and Δ is the maximum
    degree.
- **Encodings of v's constraint.**
  - *clause:* the indicator χ_a of each assignment a of E(v) that violates v;
  - *standard binomial:* y_{E(v)} − s_v;
  - *balanced binomial:* y_{A_v} − s_v·y_{B_v}, where E(v) = A_v ⊔ B_v and
    |A_v| = ⌈deg v / 2⌉.
- **Proof systems** (Berkholz, Section 2).
  - *Sherali–Adams (SA) refutation:*
    Σ_i g_i f_i + Σ_j q_j (x_j² − x_j) + p₀ = −1. The f_i are axioms, and p₀
    is a nonnegative combination of juntas ∏_{j∈A} x_j ∏_{j∈B} (1 − x_j).
  - *Sum-of-squares (SoS) refutation:* the same, with p₀ = Σ_c p_c² and each
    p_c given explicitly.
  - *Degree:* the largest degree among the g_i f_i, the q_j (x_j² − x_j) and
    p₀. For SoS this includes twice the largest deg p_c.
  - *Size:* the number of monomials of the g_i, q_j and p_c (for SA, of the
    g_i, q_j and the juntas). Berkholz's encoding length is at least this.
  - *Twin variables:* x̄_j, with the axioms x_j + x̄_j = 1, change nothing
    below unless stated.
- **Tangles** (as in `PC-DEGREE-20261020-001B-P001`). A tangle 𝒯 of order k
  of the cut function satisfies:
  - (T1) if |δ(X)| ≤ k − 1, then X ∈ 𝒯 or V∖X ∈ 𝒯;
  - (T2) no three members cover V;
  - (T3) V∖{v} ∉ 𝒯.

  By the duality theorem, a tangle of order cvw(G) exists. Every carving has
  a leaf edge at a vertex of maximum degree, so cvw(G) ≥ Δ.

## Statements

**Theorem 1 (tangles give pseudo-expectations).** Let the cut function of G
have a tangle 𝒯 of order k. For F ⊆ E with |F| ≤ k − 1, set:
- E[y_F] = s_X if F = δ(X) with X ∈ 𝒯;
- E[y_F] = 0 if F is not a cut.

Extend E linearly to polynomials of degree at most k − 1, after reducing them
to multilinear form. Then for every D ≤ k − 1 there is no SA and no SoS
refutation of T(G, c) of degree D. This holds, with or without twin
variables:
- in the clause and standard binomial encodings;
- in the balanced binomial encoding when every vertex has degree at most
  k − 1. Without that hypothesis it can fail; see the controls.

**Corollary 2 (degrees).** For every connected G and odd c:
- SA degree and SoS degree are at least cvw(G) in the clause and standard
  encodings, and in the balanced encoding when Δ < cvw(G).
- SoS degree is at most 2·max(Δ, ⌊cvw(G)/2⌋ + 1) + 2 in the standard and
  clause encodings. So cvw(G) ≤ SoS degree ≤ cvw(G) + 4 whenever
  cvw(G) ≥ 2Δ − 2.
- SA degree in the clause encoding is at most ⌊3·cvw(G)/2⌋ + 1.

**Theorem 3 (size on cell systems).** Let G have maximum degree Δ, a cell
system (𝒞, U; L, ℓ) as in `CELL-SIZE-20261020-001B-P001`, and a tangle of
order k. Then every SoS refutation of T(G, c) has size at least
2^{c·k − c′·|U|}, and so does every SA refutation, with other constants.
- This holds in all three encodings, with or without twin variables.
- The constants depend only on Δ, L and ℓ, and the bound holds for
  k ≥ k₀(Δ, L).

**Corollary 4 (families).** SoS and SA refutations of Tseitin formulas need
size:
- 2^{Ω(min(a,b))} on a × b grids;
- 2^{Ω(k^{d−1})} on d-dimensional grids [k]^d;
- 2^{Ω_{Δ,L}(tw)} on 2-connected plane graphs whose faces pairwise share at
  most one edge, with inner faces of length at most L;
- 2^{Ω(r)} on suppressed walls W′_r.

For bounded degree all of these are tight for SoS up to the constant in the
exponent.

**Corollary 5 (with twin variables).** With twin variables, SoS and SA
refutations of T(G, c) need size:
- 2^{Ω_H(tw(G))} on every graph excluding a fixed minor H;
- 2^{Ω(tw^{1/9}/polylog tw)} on every connected graph.

## Proofs

### Lemma A (tangle facts)

Let 𝒯 be a tangle of order k.
1. If |δ(X)| ≤ k − 1, exactly one of X, V∖X lies in 𝒯. (T1 gives at least
   one. Both would give X ∪ (V∖X) ∪ X = V, against T2.)
2. ∅ ∈ 𝒯, and {v} ∈ 𝒯 whenever deg v ≤ k − 1. (Apply part 1. V ∉ 𝒯 by T2,
   and V∖{v} ∉ 𝒯 by T3.)
3. If X, Y ∈ 𝒯 and |δ(X △ Y)| ≤ k − 1, then X △ Y ∈ 𝒯. (Otherwise
   V∖(X △ Y) ∈ 𝒯, and X ∪ Y ∪ (V∖(X △ Y)) = V.)

So E is well defined. G is connected, so a cut F with |F| ≤ k − 1 is δ(X) for
exactly X and V∖X. Write X_F for the one in 𝒯.

### Lemma B (multiplicativity)

Let |F|, |F′|, |F ⊕ F′| ≤ k − 1.
- If F and F′ are cuts, then E[y_{F⊕F′}] = E[y_F]·E[y_{F′}]. Indeed
  δ(X_F) ⊕ δ(X_{F′}) = δ(X_F △ X_{F′}). Lemma A.3 gives
  X_{F⊕F′} = X_F △ X_{F′}, and s_{X△Y} = s_X·s_Y.
- If exactly one of them is a cut, then E[y_{F⊕F′}] = 0, because cuts form a
  subspace of 𝔽₂^E. ∎

### Lemma C (local distributions)

Let |S| ≤ k − 1, and let H_S be the set of cuts inside S.
- H_S is a subspace, and by Lemma B, F ↦ E[y_F] is a character of it.
- So the system y_F = E[y_F] (F ∈ H_S) is consistent. Its solutions, an affine
  subspace in 𝔽₂-coordinates, carry a uniform distribution μ_S.
- Under μ_S, y_F is constant exactly when F ∈ H_S, and balanced otherwise.

Hence on functions of y_S, E is the expectation under μ_S. ∎

### Theorem 1

Take D ≤ k − 1. Apply E to a degree-D refutation. The right-hand side gives
E[−1] = −1. The left-hand side is nonnegative, by the following parts.

- **(a)** E[1] = s_∅ = 1.
- **(b) Boolean and twin axioms.** E[q·(x_j² − x_j)] = 0, because E reads
  multilinear reductions. The same holds for x_j + x̄_j − 1.
- **(c) Clause axioms.** Take a monomial m of g with deg(m·χ_a) ≤ D, and let
  S = vars(m) ∪ E(v), so |S| ≤ D.
  - E(v) ∈ H_S, with E[y_{E(v)}] = s_v by Lemma A.2. So y_{E(v)} = s_v
    μ_S-almost surely.
  - χ_a vanishes there, since it is supported on y_{E(v)} = −s_v.
  - By Lemma C, E[m·χ_a] = 0.
- **(d) Binomial axioms.** Take a monomial y_C with |C| + deg f ≤ D.
  - Standard: E[y_C·(y_{E(v)} − s_v)] = E[y_{C⊕E(v)}] − s_v·E[y_C] = 0, by
    Lemma B with F′ = E(v).
  - Balanced: C ⊕ A_v = (C ⊕ B_v) ⊕ E(v), so Lemma B gives
    E[y_{C⊕A_v}] = s_v·E[y_{C⊕B_v}]. This uses |E(v)| = deg v ≤ k − 1, the
    balanced hypothesis.
  - The standard and clause axioms at a vertex of degree at least k have
    degree above D, so they cannot occur.
- **(e) Juntas (SA).** A junta of degree at most D is a nonnegative function
  of y_S with |S| ≤ D, so its value is a μ_S-expectation, which is ≥ 0. With
  twin variables, juntas are products of literals and the same holds.
- **(f) Squares (SoS).**
  - Let deg p ≤ D/2, and write its reduction as Σ_A p_A y_A with
    |A| ≤ D/2. Then E[p²] = Σ_{A,B} p_A p_B E[y_{A⊕B}].
  - Call A ∼ B when A ⊕ B is a cut. This is an equivalence relation.
  - Fix a representative R of each class and set σ(A) = E[y_{A⊕R}] = ±1.
    Lemma B gives E[y_{A⊕B}] = σ(A)σ(B) inside a class and 0 across classes.
  - So E[p²] = Σ_classes (Σ_{A in the class} p_A·σ(A))² ≥ 0. ∎

### Corollary 2

- **Lower bounds.** Apply Theorem 1 with a tangle of order cvw(G).
- **SoS upper bound.**
  - `PC-DEGREE-20261020-001B-P001` gives polynomial calculus refutations, in
    the standard and clause encodings, of degree at most
    max(Δ, ⌊cvw/2⌋ + 1) + 1 under the standard convention.
  - That holds over every field of characteristic other than 2, including ℝ.
    The degree does not depend on the basis: y = 1 − 2x carries derivations
    to derivations of the same degree.
  - Berkholz (Theorem 1.1) turns a PC refutation of degree d into an SoS
    refutation of degree 2d.
- **SA upper bound.**
  - *Supports give a Duplicator strategy.* Let E be a pseudo-expectation of
    degree w + 1 that is nonnegative on juntas and vanishes on the clause
    axioms. Collect all partial assignments h on at most w + 1 variables
    whose μ_S-probability is positive.
    - The family is closed under restriction, since marginals are
      consistent.
    - It has the forth property, since μ_{S∪{x}} restricts to μ_S.
    - No h falsifies a clause, since such an h would have probability at most
      E[χ] = 0.

    So Duplicator wins the existential (w+1)-pebble game.
  - *Pebbling and width.* By Atserias and Dalmau, Spoiler wins that game when
    resolution width is at most w. So no such E exists. By linear programming
    duality (Farkas), an SA refutation of degree w + 1 then exists. So SA
    degree is at most W + 1, where W is the resolution width.
  - *Resolution width from a carving.* Root an optimal carving and derive,
    bottom-up, the clauses of "the parity of δ(U_t) is s_{U_t}" at each node
    t.
    - At a node with children t₁ and t₂, write F = δ(U₁) ∩ δ(U₂).
    - Derive each target clause ¬β by branching on F. Each full branch
      violates a child's parity and so meets a derived clause.
    - The clauses stay inside δ(U_t) ∪ F, of size
      (|δ(U₁)| + |δ(U₂)| + |δ(U_t)|)/2 ≤ 3cvw/2.
    - The final step at the root edge has width at most cvw. So
      W ≤ ⌊3cvw/2⌋. ∎

### Theorem 3

Let π be an SoS refutation of size S. Draw ρ from the cell restriction of
`CELL-SIZE-20261020-001B-P001` §2, which deletes D_ρ, and let k′ be the tangle
order of G − D_ρ from its Lemma 9.

1. **Restriction.** Substituting ρ maps π to an SoS refutation of
   T(G − D_ρ, c′).
   - Every vertex keeps an edge, since G − D_ρ is connected (Lemma 8 there).
   - So each axiom becomes 0 or a nonzero multiple of an axiom of the
     restricted formula.
   - Each assigned Boolean term vanishes.
   - The new multipliers are the g_i↾ρ, and the new squares are the p_c↾ρ.
2. **The degree it would need.** Let D′ = k′ − 1 and τ = ⌊D′/2⌋ + 1, and
   assume D′ ≥ 2Δ. Suppose ρ kills every monomial of every g_i and p_c with at
   least τ distinct variables. Then:
   - each g_i↾ρ has multilinear degree at most D′ − Δ;
   - each p_c↾ρ has multilinear degree at most D′/2.

   Parts (b)–(f) above need only these multilinear degrees, so the tangle of
   order k′ of G − D_ρ contradicts Theorem 1.
3. **Killing.** In the 0/1 variables, a monomial dies when one of its
   variables is set to 0; with twin variables, when one of its literals is.
   - Lemma 11 there shows a monomial with t variables survives with
     probability at most (1 − q)^{(t − |U|)/R}.
   - A union bound over the at most S monomials of the g_i and p_c gives
     S ≥ (1 − q)^{−(τ − |U|)/R}.
   - With k′ ≥ k/(L+1), this is 2^{c·k − c′|U|}.
4. **Sherali–Adams.** Berkholz (Lemma 2.1) turns an SA refutation of size N
   into an SoS refutation of size poly(N), so the SA bound follows. ∎

### Corollary 4

The cell systems and tangles of Corollaries 2–4 of
`CELL-SIZE-20261020-001B-P001` apply unchanged; for 2D grids, U is the 8
corner edges.

For the upper bound, take resolution refutations of width O(tw) and size
2^{O(tw)}·poly(n) (Alekhnovich–Razborov).
- PC in 0/1 variables simulates them with a 2^{O(width)} factor.
- SoS simulates PC with polynomial overhead (Berkholz).

So SoS refutations of size 2^{O(tw)}·poly(n) exist for bounded degree. For SA
the matching upper bound would need SA to simulate resolution, which Berkholz
attributes to Dantchev, Martin and Rhodes. We did not check that reference. ∎

### Corollary 5

Restriction with parity correction, then renaming along subdivided paths
(Lemma 5 of `CELL-SIZE-20261020-001B-P001`), carries a refutation of T(G) to
one of the wall's formula.
- **Renaming.** With twin variables, renaming x_e to a literal of the path's
  first edge is a ring homomorphism. It maps:
  - squares to squares;
  - juntas to juntas;
  - Boolean and twin axioms to consequences of degree 2;
  - branch-vertex axioms to axioms.
- **Trivial axioms.** Inner-vertex clause axioms become x·x̄. These are
  replaced by x(x + x̄ − 1) − (x² − x), at no extra degree and O(1) extra size
  per monomial.
- **Conclusion.** So the size bound passes to topological minors at a
  constant factor. Corollary 6 of `CELL-SIZE-20261020-001B-P001` and Theorem 2
  of `GENERAL-SIZE-20261020-001B-P001` then apply word for word. ∎

## Checks

`check.py` runs in about 4 s. For each graph it:
- computes cvw exactly;
- finds a tangle of order cvw by exhaustive search;
- builds E at degree D = cvw − 1;
- verifies every condition exactly over all monomials up to the stated
  degrees:
  - the three ideal constraints;
  - Sherali–Adams nonnegativity, by a Walsh–Hadamard transform on every edge
    set of size at most D;
  - SoS positivity, by an entrywise certificate M = Σ_classes σσᵀ, and by
    exact rational LDLᵀ when the matrix has at most 150 rows.

| Graph | n | cvw | D | Monomials in the moment matrix (classes) | Edge sets checked for SA | All conditions |
| --- | --- | --- | --- | --- | --- | --- |
| K₃,₃, prism, cube, Wagner | 6–8 | 4 | 3 | 10–13 (10–13) | 130–299 | hold |
| Petersen | 10 | 5 | 4 | 121 (61) | 1,941 | hold |
| Heawood | 14 | 6 | 5 | 232 (148) | 27,896 | hold |
| K₄,₄ | 8 | 8 | 7 | 697 (353) | 26,333 | hold |
| K₆ | 6 | 8 | 7 | 576 (516) | 16,384 | hold |
| 3 × 3, 2 × 5 and 3 × 4 grids | 9–12 | 3–4 | 2–3 | 13–18 | 92–834 | hold |
| 2 × 2 × 3 grid | 12 | 6 | 5 | 211 (157) | 21,700 | hold |
| 3 × 4 and 3 × 5 grids with one non-corner face set at random | 12–15 | 3–4 | 2–3 | 14–19 | 92–988 | hold |

- **Duality on small instances.** For every instance with at most 9
  vertices, no tangle of order cvw + 1 exists.
- **Controls: flipping one small set breaks the construction.**

| Graph | Flipped set | What fails |
| --- | --- | --- |
| Cube | a vertex | the ideal constraints |
| 3 × 3 grid | a pair | the balanced ideal constraints |
| Petersen | a pair | positivity only; every ideal and SA condition still holds |
| A hub joined to every vertex of two disjoint copies of K₄ (Δ = cvw = 8) | none: the tangle makes both copies of K₄ small | exactly one balanced constraint, at the hub; every standard and clause constraint holds |

The last control shows that the degree hypothesis for the balanced encoding is
needed: a vertex of degree cvw lets two small sets cover all the other
vertices. In the grids with Δ = cvw, the balanced constraints at the
maximum-degree vertices lie outside the hypothesis; they hold there anyway and
are reported separately.

## Scope

- **Not proved.**
  - The exact SoS degree inside [cvw, cvw + 4], and the exact SA degree
    inside [cvw, ⌊3cvw/2⌋ + 1].
  - Size bounds without twin variables beyond graphs with cell systems.
  - Any bound on the block-scrambled wall networks of
    `GENERAL-SIZE-20261020-001B-P001`, where the same barrier stands.
- **Characteristic.** SoS and SA are over ℝ; nothing here concerns finite
  fields.

## Novelty

- **What a targeted search on 2026-10-20 found.**
  - SoS size lower bounds for Tseitin only on expanders: Grigoriev's degree
    bound, with the size–degree relation of Atserias and Hakoniemi.
  - No SoS or Sherali–Adams size lower bound for Tseitin on grids, planar or
    other non-expanding graphs.
  - No characterization of SoS degree by carving width.
- **Theorem 1** is Grigoriev's construction with the expander replaced by a
  tangle. Its degree consequence, Θ(tw) for bounded degree, may be folklore.
  The constants, the size bounds and the twin-variable corollaries are, as
  far as we found, new.
- **Review.** No human expert has reviewed this.
