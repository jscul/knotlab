# Polynomial calculus degree of Tseitin formulas is half the carving width, up to one

Status: Proved

The lower bound cites the tangle duality theorem of Robertson and Seymour.

Ticket `PC-DEGREE-20261020-001B`, 2026-10-20. It follows
`TSEITIN-NS-DEGREE-NOTE-20261020-001`, which found that Nullstellensatz degree
is governed by *linear* layouts: the toggle width, and in the ±1 encoding
after reduction, exactly the cutwidth. Polynomial calculus (PC) is governed by
*tree* layouts at *half* size.

## Setting

- **The graph and charge.** G = (V, E) is a connected simple graph with
  n ≥ 2 vertices, and c is a charge with c(V) odd. F is a field of
  characteristic other than 2.
- **Variables.** There is one variable y_e = ±1 per edge. We work in
  R = F[y]/(y_e² − 1), with basis the monomials y_A (A ⊆ E) and deg y_A = |A|.
- **Notation.** s_v = (−1)^c(v). E(v) is the star of v. δ(U) is the set of
  edges leaving U, and Δ is the maximum degree.
- **Encodings.**
  - *Balanced binomial:* y_{A_v} − s_v·y_{B_v}, where E(v) = A_v ⊔ B_v and
    |A_v| = ⌈deg v/2⌉.
  - *Standard binomial:* y_{E(v)} − s_v.
  - *Clause:* the indicators of the assignments of E(v) violating v.
- **Reduced PC of degree d.**
  - Lines are elements of R of degree at most d, starting from the axioms
    (each of degree at most d).
  - From lines p and q we derive αp + βq.
  - From p we derive y_e·p when its degree in R is at most d.
  - PC_R is the least d at which 1 is derived.
- **Standard PC.** Lines are polynomials of degree at most d, and the axioms
  y_e² − 1 are included. Only a line of degree at most d − 1 may be
  multiplied by a variable. This degree is PC_S.
- **Carving width cvw(G).** The least, over subcubic trees whose leaves are
  the vertices, of the largest |δ(X)| over the splits of tree edges. Leaf
  edges count.
- **Tangles** (as in Hicks and Oum, *Branch-width and tangles*, Theorem 1). A
  tangle of order k+1 of p(X) = |δ(X)| is a family T of vertex sets with
  three properties:
  - (T1) if p(X) ≤ k, then X ∈ T or V∖X ∈ T;
  - (T2) no X, Y, Z ∈ T have X ∪ Y ∪ Z = V;
  - (T3) V∖{v} ∉ T for every v.
- **Duality.** No tangle of order k+1 exists if and only if the branch-width
  of p, which is cvw(G), is at most k. This is Robertson and Seymour, Graph
  Minors X (JCTB 52, 1991), (3.5), and Geelen, Gerards, Robertson and Whittle
  (JCTB 96, 2006), Theorem 3.2.

## Theorem

1. ⌈cvw(G)/2⌉ ≤ PC_R(balanced) ≤ ⌊cvw(G)/2⌋ + 1, which is exact when cvw(G)
   is odd.
2. PC_R(standard) = PC_R(clause) = max(Δ, PC_R(balanced)).
3. PC_R ≤ PC_S ≤ PC_R + 1 for the standard and clause encodings.
4. None of these depends on where the odd charge sits.

So the usual Tseitin formula, written clause by clause, needs PC degree
between max(Δ, ⌈cvw/2⌉) and max(Δ, ⌊cvw/2⌋ + 1) + 1 over every field of
characteristic other than 2.

## Proof

### 1. The closure model

Fix d, and let M_d be the monomials of degree at most d. A *signed partition*
of M_d splits it into classes.
- Each class C is either *consistent*, with a sign function φ_C on it, or
  *inconsistent*.
- Its space is W = ⊕_C W_C, where:
  - for consistent C, W_C = {Σ a_A y_A : Σ a_A φ_C(A) = 0, supp ⊆ C};
  - for inconsistent C, W_C = span(C).
- In a consistent class, A and B are *related with sign* φ(A)φ(B); that is,
  y_A − φ(A)φ(B)·y_B ∈ W.

For an edge e, put C_e = {A ∈ C : |A △ e| ≤ d}.

**Lemma 1.** The set V_d of derivable lines equals W for the least signed
partition satisfying two conditions:
- (a) each axiom's two monomials are related with the axiom's sign;
- (b) for every class C and edge e, if C is consistent, then A △ e and B △ e
  are related with sign φ(A)φ(B) for all A, B ∈ C_e. If C is inconsistent,
  each A △ e (A ∈ C_e) lies in an inconsistent class. Here a class becomes
  inconsistent when a relation of y_A with itself, with sign −1, arises.

*Proof.*
- **W ⊆ V_d.** Every relation added is derived in one of two ways: it
  translates a derived binomial by y_e, within degree d, or it is a linear
  combination. A relation of A with itself with sign −1 gives 2y_A, so y_A is
  derived (char F ≠ 2), and then every monomial of the class is too.
- **V_d ⊆ W.** W contains the axioms and is a subspace. Suppose p ∈ W and
  deg(y_e p) ≤ d. Then supp(p) ⊆ ∪_C C_e, and p = Σ p_C with p_C ∈ W_C
  supported in C_e.
  - If C is consistent, p_C is a combination of differences
    y_A − φ(A)φ(B)·y_B with A, B ∈ C_e. Multiplied by y_e these become
    relations of type (b), which lie in W.
  - If C is inconsistent, y_e·p_C lies in the span of the monomials
    A △ e, which are in W by (b).
  - V_d is the least subspace with these closure properties, so V_d ⊆ W. ∎

Hence 1 is derived exactly when the class of ∅ is inconsistent.

### 2. Labels

The cut space is {δ(U)}. Since G is connected, δ(U) = δ(U′) exactly when
U′ ∈ {U, V∖U}.
- **Every relation's difference is a cut.** If A and B are related, then
  A △ B is a cut: axioms give E(v) = δ({v}), translation keeps A △ B, and
  transitivity adds cuts.
- **Labels.** The *label* of the relation is the unique U with
  δ(U) = A △ B and (−1)^c(U) equal to the relation's sign. It is unique
  because c(V) is odd, so U and V∖U have opposite signs.
- **How labels change.**
  - Axioms have labels {v}.
  - Translation keeps labels.
  - Composing relations takes the symmetric difference of their labels,
    since signs multiply and c(U) + c(W) ≡ c(U △ W).
- **Inconsistency means label V.** A relation of A with itself with sign −1
  has label V.
- **Charge independence.** Which pairs are related, and which labels arise,
  does not depend on the charge; only the signs do. So the degree does not
  depend on where the odd charge sits (part 4). With an even charge, label V
  carries sign +1, and no contradiction ever arises.

### 3. Lower bound: tangles keep every label small

**Lemma 2.** Let T be a tangle of order 2d + 1 of p. In the construction of
the degree-d closure from balanced axioms, every relation's label lies in T.
In particular no relation is labelled V, so the closure does not refute.

*Proof.* A relation between A and B has |δ(label)| = |A △ B| ≤ |A| + |B| ≤ 2d,
so (T1) applies to its label. We induct over the construction.
- **Axioms.** These are labelled {v}. Since |δ({v})| = deg v ≤ 2d (the
  balanced axiom has degree ⌈deg v/2⌉ ≤ d), (T1) and (T3) give {v} ∈ T.
- **Translation** keeps labels.
- **Composition.** Suppose U, W ∈ T and X = U △ W. If X ∉ T, then
  V∖X ∈ T by (T1). But U ∪ W ∪ (V∖X) = V, since a vertex in neither U nor W
  is outside X. That contradicts (T2), so X ∈ T.
- **No label V.** V ∉ T by (T2), since V ∪ V ∪ V = V. ∎

**Corollary.** If cvw(G) ≥ 2d + 1, then the duality gives a tangle of order
2d + 1, so PC_R(balanced) > d. Taking d = ⌈cvw/2⌉ − 1 gives
PC_R(balanced) ≥ ⌈cvw/2⌉.

The same bound holds for the standard binomial and clause encodings: by
section 6 they have the same closure once d ≥ Δ, and are not writable below
it. It also holds in the standard convention, whose closure is contained in
the reduced one.

### 4. Geometry

For a set γ of edges, put S_d(γ) = {A : |A| ≤ d, |A △ γ| ≤ d}. These are the
positions at which a relation with difference γ fits in degree d.

**Lemma 3.**
- **(a) Mobility below 2d.** If |γ| ≤ 2d − 1, then S_d(γ) is nonempty and
  connected under single toggles A ↦ A △ e.
- **(b) Rigidity at 2d.** If |γ| = 2d, then S_d(γ) consists of the d-subsets
  of γ, and no toggle stays inside it.
- **(c) Three-point center.** If X₀, X₁, X₂ have pairwise symmetric
  differences of size at most 2d, then some P has |P △ Xᵢ| ≤ d for i = 0, 1, 2.

*Proof.*
- **(a).** Take A ⊆ γ with |A| = ⌈|γ|/2⌉; this lies in S_d(γ).
  - From any point of S_d(γ), removing an element of A ∖ γ lowers both
    |A| and |A △ γ|.
  - Within γ, the allowed sizes form the interval [|γ| − d, d], which
    contains at least two integers. Moving from A to a target T, remove an
    element of A ∖ T when the size allows, or else add an element of T ∖ A.
    Both moves are blocked only if |γ| − d = |A| = d, that is, |γ| = 2d.
- **(b).** If |γ| = 2d, then |A| + |A △ γ| ≥ |γ| = 2d forces A ⊆ γ and
  |A| = d. A toggle then makes one of the two sizes d + 1.
- **(c).** Let M be the coordinatewise majority, and let legs ℓᵢ = |Xᵢ △ M|
  with ℓ₀ ≥ ℓ₁ ≥ ℓ₂. Then |Xᵢ △ Xⱼ| = ℓᵢ + ℓⱼ.
  - Move t = max(0, ℓ₀ − d) coordinates from M toward X₀.
  - The distances become ℓ₀ − t ≤ d, then ℓ₁ + t ≤ ℓ₀ + ℓ₁ − d ≤ d, and
    ℓ₂ + t ≤ ℓ₁ + t. ∎

### 5. Upper bound: carvings

Let a carving have width w, and put d = ⌊w/2⌋ + 1, so that w ≤ 2d − 1. Root
the carving at an edge splitting V into U₀ and V∖U₀. Bottom up, derive for
each tree node U a relation labelled U at some position.
- **Leaves.** Use the balanced axiom. Its degree is ⌈deg v/2⌉ ≤ d, since
  deg v ≤ w.
- **Internal nodes, U = U₁ ⊔ U₂.**
  - The sets ∅, δ(U₁) and δ(U) have pairwise differences δ(U₁), δ(U₂) and
    δ(U), all of size at most w ≤ 2d. Lemma 3(c) gives a P with |P|,
    |P △ δ(U₁)| and |P △ δ(U)| all at most d.
  - By Lemma 3(a), translate U₁'s relation to position P, and U₂'s relation
    to position P △ δ(U₁). Every intermediate line has degree at most d.
  - The lines y_P − σ₁·y_{P△δ(U₁)} and y_{P△δ(U₁)} − σ₂·y_{P△δ(U)} combine
    to y_P − σ₁σ₂·y_{P△δ(U)}, which is labelled U.
- **Root.** Translate the relations labelled U₀ and V∖U₀ to one position P.
  Their difference is ±2·y_{P△δ(U₀)}. Multiplying by the variables of that
  monomial lowers the degree step by step and reaches the constant ±2, which
  is nonzero since char F ≠ 2.

Hence PC_R(balanced) ≤ ⌊cvw/2⌋ + 1. ∎

### 6. Encodings and conventions

For each vertex, put B_v = span{y_A − s_v·y_{A△E(v)} : A ⊆ E(v)}.
- **B_v is the clause span.** Each element vanishes where y_{E(v)} = s_v. The
  2^{deg v − 1} pairs {A, A △ E(v)} give independent elements, so B_v
  matches the clause span in dimension, and the two spans are equal.
- **Each encoding generates B_v once d ≥ Δ.** The standard binomial is the
  element with A = ∅, and the balanced one is the element with A = A_v.
  Multiplying by y_e for e ∈ E(v) reaches every element, with lines of degree
  at most deg v ≤ d.
- **Part 2.** So for d ≥ Δ all three encodings have the same reduced closure.
  Below Δ the standard and clause axioms cannot be written, and V_d ⊆ V_{d+1}.
  Together these give part 2.
- **Part 3, PC_S ≥ PC_R.** The multilinear reduction of a standard line lies
  in the reduced closure: a product y_e·p with deg p ≤ d − 1 reduces to
  y_e·red(p), which has degree at most d.
- **Part 3, PC_S ≤ PC_R + 1.** A reduced derivation of degree d is a standard
  derivation of degree d + 1. Every multiplied line has degree at most d, and
  reducing modulo y_e² − 1 uses Boolean multiples of degree at most d + 1. ∎

## Checks

`check.py` replays each step on declared instances (27 s):

| Check | Instances | Result |
| --- | --- | --- |
| Lemma 3 (a), (b), (c) and the median construction | every γ on up to 7 edges, d ≤ 3; every pair (X₁, X₂) on up to 6 edges | pass, 561 position cases |
| Lemma 1: the label closure agrees with plain linear algebra over F₃ | every connected graph with ≤ 6 vertices and ≤ 9 edges, every degree up to refutation | 255 cases agree |
| Lemma 2 and the duality | small graphs, cubic graphs ≤ 8 vertices, K₄₄, Petersen, K₆, K₄₅, K₅₅; every d from ⌈Δ/2⌉ to ⌊cvw/2⌋+1 | Exhaustive search finds a tangle of order 2d+1 exactly when cvw ≥ 2d+1. Every label of the degree-d closure lies in it, and the closure does not refute. |
| Theorem part 1: explicit carving derivations | 155 graphs including K₅₅ (cvw 12) and Heawood | every derivation replays as legal reduced PC steps of degree ≤ ⌊cvw/2⌋+1, ending in a nonzero constant |
| Theorem parts 2 and 3 | cubic graphs ≤ 8 vertices, Petersen, K₄₅, K₆ | pass |
| Controls: a sign flipped in a derivation; tangle search without (T2); closure without translations on K₄ at degree 3 | — | each fails as it should |

The census `PC-DEGREE-20261020-001A-E001` confirms the theorem's predictions
on 1,253 graphs.

## What this does not settle

- **Even carving width.** Both ends of the sandwich occur: in the census, 191
  graphs are at cvw/2 and 628 at cvw/2 + 1. At |δ(U)| = 2d a relation is
  rigid (Lemma 3(b)), so the centers of adjacent merges must agree. The
  exact rule is open. Having a vertex of degree cvw does not decide it.
- **Size.** Degree only. Through the size–degree relation of Impagliazzo,
  Pudlák and Sgall, this gives size bounds only where cvw ≫ √n, as for
  expanders, where they are known.
- **Other groups.** Tseitin modulo p and other abelian groups are not
  covered. The labels would be ℤ_p-labellings, and the tangle argument needs
  a form for them.
- **Comparison with Nullstellensatz.**
  - In the ±1 encoding after reduction, NS degree is exactly the cutwidth
    (`TSEITIN-NS-DEGREE-NOTE-20261020-001`). So NS degree is at least
    roughly twice the PC degree whenever cw ≈ cvw.
  - On complete binary trees, cvw = 3, so the PC degree is constant. The
    cutwidth grows with the height, so NS needs degree logarithmic in n.

## Novelty

A targeted search on 2026-10-20 found exact game characterizations for
resolution (Galesi, Talebanfard and Torán), branch-width governing resolution
size (Alekhnovich and Razborov), and linear PC degree lower bounds on
expanders (Buss, Grigoriev, Impagliazzo and Pitassi), but no statement of PC
degree in terms of carving width. The argument is elementary given the
duality theorem. No human expert has reviewed it.
