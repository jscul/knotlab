# Knots compose like cycles exactly in difference laws whose distinctions do not split

Status: Proved

Ticket `KNOT-CIRCUITS-20261020-001B`, 2026-10-20. It uses the census
`KNOT-CIRCUITS-20261020-001A-E001` ("A" below) and the hub remark of
`GALLAI-KNOTS-20261020-001B-P001`.

## Standard statement

### Setting

A **law** is a set Γ of relations on a finite domain D. A **system** over the
law conjoins relations of Γ and equalities on some variables, then hides the
witness variables. So a system is a relation pp-definable from Γ.

- **Ranges.** In a system S, a variable's **range** is the set of values it
  takes. These are its open alternatives.
- **Constrained sets.** A set Y of variables is **constrained** when its
  projection is smaller than the product of their ranges.
- **Circuits, ties and knots.**
  - **Circuits** are the minimal constrained sets.
  - **Ties** are circuits of 2 variables.
  - **Knots** are circuits of at least 3 variables.
- **Agreement with K1–K3.** With full ranges, a knot is exactly a set whose
  relation passes K1–K3 (Fact 2 of `docs/KNOT_INTUITION.md`).

Two circuits **compose like cycles** when they satisfy circuit elimination:
- they are distinct circuits C₁ and C₂;
- for every variable e that they share, (C₁ ∪ C₂) − e is still constrained.

A law composes like cycles when every system over it does. It composes
**knots** like cycles when this holds whenever C₁ and C₂ are knots.

A **failure** is two circuits and a shared e for which (C₁ ∪ C₂) − e is
unconstrained. The other variables of the two circuits are then left free
once e is forgotten. The program calls this a **hub**.

### Results

1. **Knots are circuits** (Lemma 1). Where elimination holds, the knots and
   ties of a system are the circuits of a matroid. Its independent sets are
   the unconstrained sets.
2. **Difference laws** (Theorem 1). Let Γ have a Mal'tsev polymorphism m,
   that is, m(x, x, y) = m(y, x, x) = y. Then Γ composes like cycles exactly
   when every subalgebra of its polymorphism algebra with at least two elements
   has a unique maximal congruence.
   - **Fields.** Affine laws over finite fields compose like cycles.
   - **Groups.** The coset law of a finite group G composes like cycles
     exactly when every subgroup of G has a unique maximal normal subgroup:
     - yes: Z_{p^k}, S3, and D_p for odd primes p;
     - no: Z6, Z2×Z2, A4, D4, Q8, Dic3 and Z12.
3. **Boolean laws** (Theorem 2). A Boolean law composes like cycles exactly
   when it is affine. It composes knots like cycles exactly when it is affine
   or bijunctive; bijunctive laws have no knots.
4. **Hubs** (Proposition 3). Two knots sharing only e form a hub exactly when
   every e-fibre of one meets every e-fibre of the other. Colouring stars,
   Horn clauses and OR₃ are instances.
5. **Readings.**
   - Tseitin's knots are the bonds of its graph, and the gauge law's knots are
     its cycles.
   - A law with an isolated reflexive value ties every linked pair, so it
     composes like cycles without having any knot.

## Nearest known results

- **Rectangularity.** A relation preserved by a Mal'tsev operation is
  rectangular. This is classical; it is the base of Bulatov and Dalmau's
  algorithm for Mal'tsev constraints (SIAM J. Comput. 2006).
- **Quotient form.** Subdirect products in congruence-permutable varieties are
  graphs of isomorphisms between quotients (Fleischer's lemma; Goursat's lemma
  for groups).
- **Codes and matroids.**
  - The minimal supports of a linear code are the circuits of a matroid
    (Whitney; Tutte).
  - [Almost affine codes](https://arxiv.org/abs/1704.02819), after Simonis and
    Ashikhmin (1998), give matroids from projection sizes.
  - Matroids built on maximal subgroups exist (Weidner 1996), but none on
    projections.
- **Boolean clones.**
  - Post's lattice of Boolean clones (Post 1941), in the notation of
    [Böhler, Creignou, Reith and Vollmer, Part I](https://www.cs.hs-rm.de/~reith/resources/Veroeffentlichungen/bo-cr-re-vo03.pdf)
    (SIGACT News 2003).
  - Schaefer's classes: affine, bijunctive, Horn, dual Horn, 0-valid and
    1-valid.

**Classification: likely new as stated, built from classical parts.**
- **Theorem 1** characterizes circuit elimination of range-relative
  dependencies by unique maximal congruences of subalgebras, with its group
  form. I did not find it stated (searches on 2026-10-20). Its proof is short
  from rectangularity, so experts may know it in another guise.
- **Theorem 2(i), affine ⇒ cycles,** is the binary matroid of a linear code.
  The converse and the knot level (ii) rest on Post's lattice plus explicit
  hubs; I found neither stated.

## Lemma 1 (knots are circuits)

In a nonempty system S:
1. Constrainedness is upward closed. A constrained set projects onto a
   constrained subset, and a projection of a full product is full.
2. So the circuits are the inclusion-minimal constrained sets. No circuit
   contains another, and a set is unconstrained exactly when it contains no
   circuit.
3. With full ranges, Y is a knot exactly when π_Y(S) passes K1–K3:
   - K1 says Y is constrained;
   - K2 says every set one smaller is unconstrained, hence every proper
     subset is, by item 1;
   - K3 holds since S ≠ ∅.
4. If elimination holds in S, its circuits satisfy the circuit axioms of a
   matroid: they are nonempty, none contains another, and elimination holds.
   The independent sets, those containing no circuit, are then the
   unconstrained sets. ∎

## Lemma 2 (rectangularity)

If m is a Mal'tsev polymorphism of Γ, then m preserves every system over Γ:
pp-definitions preserve polymorphisms.

Split a system's variables into blocks U and W. If (u, w), (u, w′) and
(u′, w) are allowed, then so is (u′, w′):

m((u′, w), (u, w), (u, w′)) = (m(u′, u, u), m(w, w, w′)) = (u′, w′). ∎

## Theorem 1 (difference laws)

Let Γ have a Mal'tsev polymorphism, and let 𝔸 be its polymorphism algebra.
Γ composes like cycles if and only if every subalgebra B of 𝔸 with |B| ≥ 2 has
a unique maximal congruence.

In a Mal'tsev algebra congruences permute. So "B has two maximal congruences"
is equivalent to "B has proper congruences θ₁ and θ₂ with θ₁ ∘ θ₂ = B²". Two
distinct maximal congruences join to the total relation, and permuting
congruences compose to their join. Conversely, such θ_i lie in maximal M_i,
and M₁ = M₂ would give M₁ ∘ M₁ = M₁ ≠ B².

*Proof of "only if".*
1. Let B have proper congruences θ₁ and θ₂ with θ₁ ∘ θ₂ = B².
2. By the finite Galois connection, B, θ₁ and θ₂ are pp-definable from Γ:
   every relation preserved by all polymorphisms is pp-definable.
3. In the system S(x, e, z) = B(x) ∧ B(e) ∧ B(z) ∧ θ₁(x, e) ∧ θ₂(e, z), each
   variable ranges over B.
4. {x, e} and {e, z} are circuits, since θ₁ and θ₂ are proper.
5. {x, z} is unconstrained, because its projection is θ₁ ∘ θ₂ = B². This is a
   failure.

*Proof of "if".* Suppose circuits C₁ ≠ C₂ share e and Y = (C₁ ∪ C₂) − e is
unconstrained in a system S.
1. **Setting up.**
   - Let D_v be the ranges. Each is a subalgebra, being a pp-definable unary
     relation.
   - Neither circuit contains the other, so A′ = C₁ − C₂ and B′ = C₂ − C₁ are
     nonempty.
   - Let I = (C₁ ∩ C₂) − e and A = C₁ − e.
2. **R₁ is rectangular with full projections.** Let R₁ = π_{C₁}(S), viewed as
   a relation between ∏_{v∈A} D_v and D_e.
   - Its projection onto A is the full product, because A ⊊ C₁.
   - Its projection onto e is D_e.
   - By Lemma 2 it is rectangular.
3. **γ₁ is a proper congruence.** Define g γ₁ g′ when some a has (a, g) and
   (a, g′) in R₁.
   - Rectangularity makes γ₁ an equivalence relation.
   - R₁ = {(a, g) : g ∈ φ₁(a)}, where φ₁(a) is a γ₁-class.
   - γ₁ is pp-definable from S, so it is a congruence of the subalgebra D_e.
   - It is proper, since otherwise C₁ would be unconstrained.
4. **γ₂.** In the same way C₂ gives a proper congruence γ₂ and a map φ₂.
5. **For fixed c, φ₁ reaches every class.** I ∪ {e} = C₁ − A′ is a proper
   subset of C₁, so it is unconstrained. So for each c ∈ ∏_I D_v and each
   g ∈ D_e, some a′ has g ∈ φ₁(a′, c). The same holds for φ₂.
6. **Every pair of classes meets.** Y is unconstrained, so every (a′, c, b′)
   extends to some s ∈ S. Then s_e ∈ φ₁(a′, c) ∩ φ₂(b′, c). By step 5, every
   γ₁-class meets every γ₂-class.
7. **The composition is total.** Step 6 means γ₁ ∘ γ₂ = D_e². So D_e has two
   maximal congruences. ∎

**Remark (whole-domain convention).** Take the whole domain as every
variable's alternatives. Then a variable confined to a proper subalgebra is
constrained by itself and joins no larger circuit. The same proof gives
elimination exactly when 𝔸 itself has a unique maximal congruence. A4 shows
the difference: its unique maximal normal subgroup is V4, yet its law fails
inside a V4-coset under ranges.

### Corollaries

- **Fields.** Take the affine law over F_q: all cosets of F_q-subspaces. Its
  polymorphisms include every affine combination.
  - The subalgebras of F_q are points and F_q itself.
  - A congruence's class of 0 is an F_q-subspace of F_q, hence 0 or F_q.
  - So the condition holds. This includes GF(4), on the same four elements as
    Z2×Z2.
- **Groups.** The coset law of G is Inv(x y⁻¹ z): the sets closed under
  x y⁻¹ z are exactly the cosets of subgroups.
  1. Its subalgebras are the cosets gH. Each is isomorphic, as a heap, to H by
     h ↦ gh.
  2. The heap congruences of H correspond to the normal subgroups N of H,
     through x θ y ⟺ x y⁻¹ ∈ N:
     - the class of 1 is closed under products, inverses and conjugation,
       using m(a, 1, b) = ab, m(1, a, 1) = a⁻¹ and m(ga, g, 1) = gag⁻¹;
     - conversely, every normal subgroup gives a congruence.
  3. So the coset law composes like cycles exactly when every subgroup has a
     unique maximal normal subgroup.
  4. For abelian G, that means G is a cyclic p-group.
- **Splitting a distinction.** Two proper congruences that compose to the
  total relation split the variable's values into two independent
  coarse-grainings that together pin it. The variable then carries two
  distinctions. Knots binding one coarse-graining each meet at a hub.

## Theorem 2 (Boolean laws)

For a Boolean law Γ:
- (i) Γ composes like cycles exactly when Γ is affine;
- (ii) Γ composes knots like cycles exactly when Γ is affine or bijunctive.

*Proof.*

1. **Affine laws compose like cycles.** This is Theorem 1 over F₂, or directly
   the binary matroid.
2. **Bijunctive laws have no knots.** Majority is a polymorphism, so every
   system equals the conjunction of its unary and binary projections (Baker
   and Pixley). A set of three or more variables whose pairs are all
   unconstrained is therefore unconstrained. So every circuit has at most 2
   variables, and the knot-level statement is vacuous.
3. **The clone facts used.** These are read off Post's lattice. Here S₀^k is
   the clone of functions for which any k (not necessarily distinct) arguments
   with value 0 share a coordinate equal to 0, and S₁^k is its dual.
   - **(F1)** Every Boolean clone that lacks minority, x ⊕ y ⊕ z, lies in one
     of these:
     - M, the monotone functions;
     - S₀² or S₁²;
     - N = [¬, 0, 1].
   - **(F2)** Every Boolean clone that lacks both minority and majority lies
     in one of these:
     - V = [∨, 0, 1];
     - E = [∧, 0, 1];
     - S₀³ or S₁³;
     - N.
   - **Why the lists are complete.** Post's lattice lists every Boolean clone.
     - The clones containing minority are BF, R₀, R₁, R₂, D, D₁ and the five
       L-clones.
     - Every other clone lies in M (the M-, V- and E-clones and D₂), in S₀²
       or S₁² (the S-clones), or in N (N₂ and the I-clones). That gives (F1).
     - Among these, M, M₀, M₁, M₂, D₂ and the S-clones of degree 2 contain
       majority. The S-clones of degree at least 3 lie in S₀³ or S₁³, the
       V-clones in V, the E-clones in E, and the rest in N. That gives (F2).
4. **The hub relations lie in the right co-clones.**
   - **Implication.** x ≤ y ∈ Inv(M), since monotone functions preserve ≤.
   - **x ∨ y ∈ Inv(S₀²).** Suppose f(a) = f(b) = 0 with every column (a_i,
     b_i) ∈ x ∨ y. Then a and b share a 0-coordinate, giving a column (0, 0).
     That is a contradiction. The same argument with three arguments gives
     OR₃ ∈ Inv(S₀³).
   - **Duals.** The dual arguments give ¬x ∨ ¬y ∈ Inv(S₁²) and
     NAND₃ ∈ Inv(S₁³).
   - **The clauses.** x ∨ y ∨ ¬z is closed under ∨ and contains 000 and 111,
     so it lies in Inv(V). Dually, ¬x ∨ ¬y ∨ z lies in Inv(E).
   - **The twisted relations.** The twisted implication
     T₃ = {(x⊕s, e⊕s, s) : x ≤ e} is complement-closed and contains 000 and
     111, so it lies in Inv(N). So does the twisted atom
     T₄ = {(x⊕s, y⊕s, e⊕s, s) : ¬x ∨ ¬y ∨ e}.
5. **The hubs.**
   - **Ties** (the fibre criterion of Proposition 3):
     - (x ≤ e) ∧ (z ≤ e) leaves {x, z} free, through e = 1;
     - (x ∨ e) ∧ (z ∨ e) leaves {x, z} free, through e = 1;
     - (¬x ∨ ¬e) ∧ (¬z ∨ ¬e) leaves {x, z} free, through e = 0.
   - **Knots:**
     - OR₃(x, y, e) ∧ OR₃(z, w, e), through e = 1;
     - NAND₃, through e = 0;
     - two dual Horn clauses sharing their negated variable, through 0;
     - two Horn clauses sharing their positive variable, through 1.
   - **Complement-closed laws.** Here a value of e cannot be pinned, so the
     twisted forms share e and s, and eliminating e leaves the rest free:
     - T₃(x, e, s) ∧ T₃(z, e, s), whose circuits are 3-variable knots;
     - T₄(x, y, e, s) ∧ T₄(z, w, e, s), whose circuits are 4-variable knots.
     For each s, every fibre contains the value of e that s selects.
6. **Conclusion.**
   - Non-affine ⇒ a tie-level or knot failure, by (F1) and the hubs in step 5.
   - Neither affine nor bijunctive ⇒ a failure between knots, by (F2) and the
     knot hubs in step 5. ∎

**The census's shortfall.**
- A's search found no knot at all for the eight negation-twists of 1-in-3,
  which are neither affine nor bijunctive.
- Theorem 2 still applies to them. `check.py` verifies an explicit
  pp-formula for each: four copies over eight variables define a 3-variable
  Horn or dual-Horn knot that forms a hub.
- With these, every census row agrees with Theorem 2.

## Proposition 3 (hub criterion)

Let K₁ on (a, e) and K₂ on (b, e) be knots with full ranges and disjoint a, b,
and let S = K₁ ∧ K₂.
- **Both remain circuits.** The vars of K₁ and K₂ are circuits of S, because a
  knot's projection onto any single variable is full.
- **The criterion.** Elimination at e fails exactly when
  E₁(a) ∩ E₂(b) ≠ ∅ for all a and b, where E_i are the e-fibres.

**Examples.**
- **The colouring star.** It is "not all q colours" on (x₁, …, x_{q−1}, u).
  Its u-fibres have at least q − 1 ≥ 2 elements, so any two meet when q ≥ 3.
  This is the shared-vertex hub of `GALLAI-KNOTS-20261020-001B-P001`, Remark 6.
- **Parity knots.** They have singleton fibres {x ⊕ y} that can be disjoint,
  so they never form a hub. ∎

## Readings

- **Tseitin and gauge laws.** Take a Tseitin system on a 2-edge-connected
  graph.
  - Its solutions are a coset of the cycle space. A set of edges is
    constrained exactly when it contains the support of a nonzero cut vector.
  - So its circuits are the bonds (minimal edge cuts), and its knots are the
    bonds with at least three edges.
  - The gauge law has the cut space as its solutions, so its circuits are the
    cycles.
  - Both laws are affine, so their knots compose like cycles. Two bonds
    sharing an edge leave a bond inside their union without it.
- **Colouring.** The colouring law (q ≥ 3) has no Mal'tsev polymorphism. Its
  star knots form hubs, so it does not compose like cycles.
- **Isolated values.** Suppose R ⊆ D² has an isolated reflexive value c:
  (c, c) ∈ R, and no other pair of R contains c.
  - In every connected system over R, the all-c assignment is a solution.
  - Every solution is either all c or avoids c on a connected component.
  - So any two open variables of a component are tied, every circuit is a
    tie, and elimination holds.
  - These are A's twelve non-Mal'tsev three-element relations without a
    failure. They have no knots.

**Conjecture.** A law whose systems have knots, and which composes them like
cycles, has a Mal'tsev polymorphism.
- Proved for Boolean laws (Theorem 2).
- Supported by A on all binary relations over three elements: every
  non-Mal'tsev relation there either fails or has no knots.

## What this does not show

- **Non-Mal'tsev laws.** Beyond Boolean domains, I give no classification:
  the conjecture above is open.
- **Knot level for difference laws.** At the knot level, Theorem 1 gives
  elimination wherever its condition holds. Where it fails, a failure between
  knots also needs knots inside each coarse-graining. That case is not
  classified here.
- **What composing like cycles means here.** It is a matroid structure on the
  variables. It is not a contact network, composed topology in the protected
  sense, a path or a distance.
- **Range convention.** The range-relative convention is stated and kept
  explicit. Under the whole-domain convention, the condition concerns the
  whole algebra only.

## Checks

`check.py` runs in about 12 seconds and writes `result.json`. All checks pass,
and all controls are rejected.

- **Lemma 1** on 400 random relations:
  - the two circuit methods agree;
  - K1–K3 agrees with circuits;
  - augmentation holds in all 249 relations that satisfy elimination.
- **Lemma 2:** 3,360 rectangularity tests.
- **Theorem 1** on 14 Mal'tsev algebras: the Z3 and Z4 heaps, GF(4) affine,
  Z2×Z2, three products of 2-element algebras, and seven random ones. Forty
  generated subalgebras each.
  - No failure where the condition holds.
  - The construction fails where it does not hold.
  - All 10 failures found yield the proof's two permuting proper congruences.
- **Groups.** The condition holds exactly for Z2, Z3, Z4, Z5, Z7, Z8, Z9, S3
  and D5, out of 20 groups of order at most 12.
  - The constructions fail for the other eleven.
  - Random cosets show no failure for the nine that pass.
- **Fields.** GF(4) and GF(5) affine: no failure.
- **Theorem 2:**
  - clone memberships, through the generators of M, V, E and N, and by
    enumeration of the ternary members of S₀² and S₁²;
  - all nine hubs;
  - 180 bijunctive relations and 147 random 2-CNF systems without knots;
  - 150 random affine systems without failure;
  - the eight explicit 1-in-3 hubs;
  - agreement with all 268 Boolean census rows.
- **Proposition 3:** 474 random knot pairs over two and three values.
- **Readings.**
  - Tseitin circuits equal bonds and gauge circuits equal cycles on K4, K3,3,
    the prism, the cube, the Petersen graph, W5 and K5.
  - 160 random systems over the 40 isolated-value relations have only ties.
- **Controls, all rejected:**
  - "a Mal'tsev polymorphism suffices" (Z2×Z2);
  - "the whole algebra's congruences suffice" (A4: one maximal normal
    subgroup, yet failing);
  - "tie and knot verdicts coincide" (implication);
  - "hub iff some fibre is a singleton" (parity);
  - "self-complementary laws compose like cycles" (the twisted implication).
