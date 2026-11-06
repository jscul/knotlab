# Composing like cycles is decided on the tops

Status: Proved

Ticket `CYCLE-TOPS-20261021-001B`, 2026-10-21. It uses:
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001` ("the circuits proof");
- Proposition 1 of `MALTSEV-CONVERSE-20261020-001B-P001` ("the converse proof");
- the lift theorem of `DIAGONAL-LEMMA-20261021-001B-P001` ("the shadow proof");
- Proposition 6 of `MATROID-CONVERSE-20261021-001B-P001` ("the matroid proof"):
  in a law that composes like cycles, every pp-definable set B with at least
  two elements has a unique maximal proper pp-definable equivalence μ_B, its
  top;
- Theorem 1 and Conjecture 6 of `MALTSEV-CONDITIONS-20261021-001B-P001` ("the
  conditions proof");
- the census `CYCLE-TOPS-20261021-001A-E001` ("A").

## Standard statement

**Definitions.** They are those of the circuits proof.
- A system conjoins copies of a law's relations, with any variables
  identified, and hides its witness variables.
- A variable's range is the set of values it takes.
- A set of variables is free when its projection is the product of their
  ranges, and constrained otherwise.
- Circuits are the minimal constrained sets: ties have two variables, knots
  three or more.
- A law composes like cycles when every system satisfies circuit elimination.
  Its circuits are then those of a matroid whose independent sets are the free
  sets (the circuits proof, Lemma 1).

**The blur.** Let S be a system with ranges B_v. For each variable v, let ρ_v
be a pp-definable relation on B_v that contains the diagonal.
- The blur S^ρ is the set of tuples t with some s ∈ S such that (s_v, t_v) ∈ ρ_v
  for every v.
- With ρ_v = μ_v, the top of B_v, a set Y is free in S^μ exactly when the image
  of Y's projection in ∏_{v∈Y} B_v/μ_v is the full product. Call that image the
  **top image**.

**This proof shows the following,** for every law that composes like cycles.
1. **Reflexive relations lie below the top** (Lemma 1). A pp-definable
   relation on a range B that contains the diagonal is all of B² or lies
   inside μ_B. This strengthens the matroid proof's Proposition 6 from
   equivalences to reflexive relations.
2. **The top lemma** (Theorem 2). Every system has exactly the circuits of its
   blur, for any proper reflexive pp-definable ρ_v, and in particular of its
   top image. No circuit hides below the tops. This proves the top-lemma form
   of the matroid proof's Conjecture 5.
3. **Ties are bijections of tops** (Corollary 3). The top image of every tie is
   the graph of a bijection between the two tops.
4. **Knots are functional or overlapping** (Corollary 4). At each variable of a
   knot, either the top image determines that variable's top class from the
   others, or every two of its top classes share a fibre.
5. **The conditions proof's Conjecture 6 is false** (Proposition 5). Parity
   beside the isolated-value relation J composes like cycles, but it is not
   Mal'tsev on its tops. Neither is K₄ beside the Z₃ law.
6. **The repair holds for disjoint unions** (Proposition 6). Every knot of a
   disjoint union lies in one part. So being Mal'tsev on the tops of the knot
   ranges passes to disjoint unions, and the counterexamples satisfy it.
7. **Conjecture 7** restates Conjecture 6 for knot ranges. Census A found such
   operations for every surviving law.

## Nearest known results

- **Parallel elements.** Two elements forming a 2-circuit of a matroid are
  parallel, and exchanging one for the other in a circuit gives a circuit.
  This is textbook matroid theory (Oxley, *Matroid Theory*, Chapter 1). The
  top lemma applies it to a system and its blurred copy.
- **Rectangularity and Mal'tsev operations.** A relation preserved by a
  Mal'tsev operation is rectangular (the circuits proof, Lemma 2).
- **The matroid proof's top lemma** (Theorem 2 there) is the analogue for
  subdirect products in Mal'tsev varieties. It used modularity and Fleischer's
  lemma. The proof here uses only circuit elimination, so it needs no
  difference operation.

**Classification: new to the program; elementary.**
- Theorem 2's argument is short once the blurred copy is placed in the same
  system. I found no source that asks the question, because free sets relative
  to ranges are the program's own notion.
- Proposition 5 corrects the conditions proof. Its counterexample was already
  in the converse proof, and was overlooked when Conjecture 6 was stated.

## Lemma 1 (reflexive relations lie below the top)

Let the law compose like cycles. Let B be a range with at least two elements,
and let ρ ⊆ B² be pp-definable and contain the diagonal of B. Then ρ = B² or
ρ ⊆ μ_B.

*Proof.* Suppose ρ ≠ B².
1. **τ = ρ ∘ ρᵀ is proper.**
   - In the system ρ(x, e) ∧ ρ(z, e), every variable ranges over B, since ρ
     contains the diagonal.
   - {x, e} and {z, e} are ties: their projections are ρ ≠ B², and single
     variables are free.
   - Elimination makes {x, z} constrained. Its projection is ρ ∘ ρᵀ.
2. **τ contains ρ, and is reflexive and symmetric.** If (x, y) ∈ ρ, take the
   middle value y: (x, y) ∈ ρ and (y, y) ∈ ρ.
3. **Every power of τ is proper.**
   - Let σ be a proper power of τ; it is reflexive and symmetric.
   - In σ(x, e) ∧ σ(e, y), the sets {x, e} and {e, y} are ties.
   - Elimination makes σ ∘ σ proper.
   - By induction τ^(2^k) is proper for every k.
4. **Conclusion.**
   - On a finite set the transitive closure of τ is one of these powers. It
     is a proper pp-definable equivalence containing ρ.
   - μ_B is the unique maximal proper pp-definable equivalence on B, so it
     contains every proper one. Hence ρ ⊆ μ_B. ∎

## Theorem 2 (the top lemma)

Let the law compose like cycles, and let S be a system with variables V and
ranges B_v.
- For each v with |B_v| ≥ 2, let ρ_v ⊆ B_v² be pp-definable, proper and
  reflexive, for example the top μ_v.
- For |B_v| = 1 let ρ_v be equality.

Then S and its blur S^ρ have the same circuits, and so the same free sets. In
particular, a set of variables is free exactly when its top image is the full
product.

*Proof.*
1. **One system holds both.** Let T be the system S(V) ∧ ⋀_v ρ_v(v, v′) on
   V ∪ V′, where V′ holds fresh copies.
   - The projection of T onto V is S, and its projection onto V′ is S^ρ.
   - v′ ranges over B_v, because ρ_v contains the diagonal of B_v.
2. **Each v is parallel to its copy.** For |B_v| ≥ 2, the projection of T onto
   {v, v′} is ρ_v ≠ B_v², and single variables are free. So {v, v′} is a
   circuit of T.
3. **T is a matroid.** The law composes like cycles, so the circuits of T
   satisfy elimination, and they are the circuits of a matroid.
4. **Parallel exchange.**
   - **The fact.** In a matroid, let {e, f} be a circuit, C a circuit with
     e ∈ C and f ∉ C. Then (C − e) ∪ {f} is a circuit.
   - **Some circuit lies inside it.** Elimination on C and {e, f} at e gives
     a circuit C₃ ⊆ (C − e) ∪ {f}. It contains f, since C − e contains no
     circuit.
   - **It is all of it.** Suppose C₃ = C″ ∪ {f} with C″ ⊊ C − e. Then
     elimination on C₃ and {e, f} at f gives a circuit inside C″ ∪ {e} ⊊ C,
     which is impossible.
5. **Circuits pass to the copies.**
   - A circuit C of S is a circuit of T: its projections and ranges in T are
     those in S.
   - Every variable of C has |B_v| ≥ 2. A constant variable lies in no
     circuit, because adding it to a set never changes whether the set is
     free.
   - Exchange the variables of C for their copies one at a time, by step 4.
     The result C′ is a circuit of T inside V′, so it is a circuit of S^ρ.
   - The same exchange, run backwards, takes every circuit of S^ρ to a circuit
     of S.
6. **Free sets.** A set is free exactly when it contains no circuit.
   - So S and S^ρ have the same free sets. Both are taken relative to the
     same ranges B_v.
   - With ρ = μ, the projection of S^μ onto Y is the saturation of S's
     projection. It is full exactly when the top image is full. ∎

**No hidden circuits.** A circuit of a law that composes like cycles is always
constrained modulo the tops. So the matroid of every system is the matroid of
its top image.

**What the proof uses.** Only elimination inside one system, and the
pp-definability of the tops. The conditions proof showed that composing like
cycles implies neither modularity nor n-permutability. So the matroid proof's
route through Fleischer's lemma could not be extended, and this one needs
neither.

## Corollary 3 (ties are bijections of tops)

Let the law compose like cycles, and let {x, y} be a tie of a system S. Then
its top image is the graph of a bijection B_x/μ_x → B_y/μ_y.

*Proof.* Let R be the blur by the tops of S's projection onto {x, y}. R is
pp-definable, has full projections, and is saturated: it is a union of
products of top classes.
1. **R is proper.** {x, y} is constrained in S, so by Theorem 2 it is
   constrained in the blur.
2. **λ = R ∘ Rᵀ is the top of B_x.**
   - λ relates x and x′ when their fibres in B_y meet. It is pp-definable and
     contains the diagonal, since every x has a partner.
   - It contains μ_x, because R is saturated.
   - If λ were all of B_x², the system R(x, e) ∧ R(z, e) would have ties
     {x, e} and {z, e} with {x, z} free. That breaks elimination.
   - So λ is proper. By Lemma 1, λ ⊆ μ_x, and therefore λ = μ_x.
3. **A function one way.** If two top classes of x shared a top class of y in
   their fibres, they would be λ-related, hence equal.
   - So each top class of y lies in the fibre of exactly one top class of x.
   - This gives a map g from the tops of y onto the tops of x.
4. **A function the other way.** Symmetrically, f maps the tops of x onto the
   tops of y.
5. **Conclusion.** The top image is both {(g(t), t)} and {(s, f(s))}, so f and
   g are inverse bijections. ∎

**The bijection is an isomorphism.** Every polymorphism preserves R, so the
bijection commutes with the operations that the polymorphisms induce on the
two tops. In particular, two tied variables have isomorphic tops.

## Corollary 4 (knots are functional or overlapping)

Let the law compose like cycles, let C be a circuit of a system, and let e ∈ C.
Let K be the blur by the tops of S's projection onto C, and take the
fibre-sharing relation

  λ_e(t, t′) = ∃a: K(a, t) ∧ K(a, t′),

where a ranges over the values of C − e. Then exactly one of these holds:
- **functional:** λ_e = μ_e, and every fibre of the top image at e is a single
  top class;
- **overlapping:** λ_e is all of B_e², so every two top classes of e share a
  fibre.

*Proof.* λ_e is pp-definable, contains the diagonal (every value of e has a
partner), and contains μ_e, because K is saturated. By Lemma 1 it is total or
equal to μ_e. ∎

For ties, Corollary 3 rules out the overlapping case. For knots it is open.
Census A found only functional knot images (H4), and so did the checks here.

## Proposition 5 (the conditions proof's Conjecture 6 is false)

**The definition.** The conditions proof called a law **Mal'tsev on its tops**
when one ternary polymorphism F satisfies F(x,y,y) μ_B x and F(x,x,y) μ_B y
for every range B and all x, y ∈ B. Its Conjecture 6 said every law that
composes like cycles is Mal'tsev on its tops.

**Counterexample.** Let Γ_B have three-variable even parity P on D₁ = {0, 1}
and J = {(2,2), (3,3), (3,4), (4,3)} on D₂ = {2, 3, 4}. Its domain is
D = {0, …, 4}.
1. **Γ_B composes like cycles.** This is the converse proof's Proposition 1.
   - A nonempty system is a product of a parity system, a J-system and
     unconstrained variables.
   - Parity is affine, and J ties every linked pair.
2. **The top of D is equality.**
   - **Mixed operations.** Every relation of Γ_B has its tuples inside one
     part. So a binary operation that is the first projection on D₁² and on
     D₂², and takes any values on mixed pairs, is a polymorphism.
   - **Both cases collapse.** Let E be a pp-definable equivalence on D that
     relates some a ≠ b.
     - If a and b lie in the same part, take c in the other part. Applying
       such operations to (a, b) and (c, c) puts any pair of values in E.
     - If a and b lie in different parts, apply them to (b, a) and (a, a). The
       first coordinate is mixed and the second is a, so (any value, a) lies
       in E.
   - Either way E is total. So equality is the only proper pp-definable
     equivalence on D.
3. **No operation is Mal'tsev on the tops.**
   - Such an F would be a Mal'tsev operation on D, since D is the range of an
     unconstrained variable. It would also preserve J.
   - But J is not rectangular: J(3, ·) = {3, 4} and J(4, ·) = {3} meet
     without being equal. ∎

**A second counterexample with knots in both parts.** K₄ on {0, 1, 2, 3} beside
x + y + z ≡ 0 over Z₃ on {4, 5, 6}.
- **It composes like cycles.** Systems split the same way. The lift theorem
  covers K₄, and the Z₃ law is affine.
- **The top of the whole domain is equality,** by the same argument as in
  step 2.
- **No Mal'tsev operation.** K₄ is not rectangular (the conditions proof,
  Theorem 1).

**What went wrong.** The whole domain is the range of an unconstrained
variable. Nothing links the two parts, so its top degenerates to equality. A
Mal'tsev operation is then demanded on parts where no knot needs one: J has no
knots at all.

## Proposition 6 (disjoint unions and knot ranges)

Let Γ = Γ₁ ⊔ Γ₂ have each relation's tuples inside D₁ or inside D₂. Then:
- **(a)** every knot of every system lies in a component built from one Γ_i,
  so its variables' ranges lie in D_i;
- **(b)** on a range B ⊆ D_i, the pp-definable equivalences of Γ and of Γ_i
  coincide, so the tops agree;
- **(c)** suppose each Γ_i has a ternary polymorphism F_i that is Mal'tsev
  modulo the tops on its knot ranges. Then Γ has one: F_i on D_i³, and any
  fixed choice on mixed triples.

*Proof.*
- **(a), components.** Split a system into components linked by shared
  variables.
  - A component holding a constraint of Γ_i has all its values in D_i. A
    component that mixes the two kinds of constraint is empty.
  - The solutions are the product of the components' solutions, so every
    circuit lies inside one component.
  - A component with no constraint is a single variable, which lies in no
    knot.
- **(b), formulas.** Let a formula Φ(x, y) define an equivalence on B ⊆ D_i.
  - If x and y lie in one component of Φ, that component uses Γ_i only.
  - Otherwise Φ is a product U(x) × V(y), and a product that is reflexive on
    B is all of B².
- **(c), the operation.**
  - The combined F preserves every relation, because each triple of tuples
    from one relation stays inside one part.
  - On every knot range, F acts as the corresponding F_i. ∎

**Both counterexamples satisfy the repair.**
- **Parity beside J.** Its knot ranges are parity's; J has none.
- **K₄ beside Z₃.** Combine the conditions proof's operation for K₄ with
  x − y + z on Z₃.

## Conjecture 7 (Mal'tsev on the tops of knot ranges)

Every law that composes like cycles has a ternary polymorphism F such that
F(x,y,y) μ_B x and F(x,x,y) μ_B y whenever B is the range of a variable that
lies in a knot of some system, and x, y ∈ B.

**Evidence.**
- The conditions proof's Theorem 5 covers difference laws, their lifts, and
  shadows with pp-definable equality of first components.
- Proposition 6 covers disjoint unions.
- Census A (H5) found such operations for every law without a failure: the
  five surviving block removals, both lifts of K₆ and both disjoint unions.

**What it would give.**
- **Rectangular knot images.** By Theorem 2, each system's matroid is that of
  its top image. Under Conjecture 7, F would induce a Mal'tsev operation on
  the tops of all knot variables. So the top images of knots would be
  rectangular.
- **What would remain.** The matroid proof's Remark would then reduce the
  matroid-level converse to the structure of subdirect products of simple
  Mal'tsev algebras: affine over finite fields when abelian, skew-free
  otherwise.
- **Which parts are already proved.** Corollary 3 handles ties and their
  parallel classes. Theorem 2 handles the passage to tops.
- **The step that is not proved.** The Remark's structure theory.

## What this does not show

- **Conjecture 7** is not proved.
- **Overlapping knot images** are not excluded (Corollary 4). None were found.
- **The matroid-level converse** remains open. It now rests on Conjecture 7
  and the matroid proof's Remark.
- **The right form of the conjecture.** Knot ranges are one natural repair.
  Weaker forms that let F depend on the system were not examined.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` writes `result.json`. All checks pass, and all controls are
rejected.

- **Tops.** For every surviving law of census A, the recorded certificates are
  re-verified. Every coarser proper equivalence is broken by a recorded
  polymorphism, and the polymorphism is re-verified.
- **Lemma 1.** On random systems of these laws, every reflexive projection and
  every fibre-sharing relation on a range is total or lies inside the top.
- **Theorem 2.**
  - On the same systems, the blur by the tops has the system's circuits.
  - So does the blur by random proper reflexive relations taken from other
    systems.
  - On a sample of systems, the doubled system T is built explicitly. Each
    {v, v′} is a circuit there, and each circuit's copy is a circuit.
- **Corollaries 3 and 4.** Every tie's top image is a bijection. Every knot's
  top image is functional or overlapping at each variable; all were
  functional.
- **Proposition 5.**
  - For both unions, an explicit mixed binary polymorphism breaks every
    equivalence on the whole domain other than equality.
  - J and K₄ are not rectangular.
  - No elimination failure appears in random systems.
- **Proposition 6.**
  - In random systems of both unions, knot ranges lie inside one part.
  - The combined operations are polymorphisms and are Mal'tsev modulo the
    tops on the knot ranges.
- **Controls:**
  - "reflexive relations lie below the top without composition like cycles"
    (Z₆: x ≡ y mod 2 and mod 3 join to the total relation);
  - "the top lemma holds without composition like cycles" (Z₆: blurring by
    mod 2 frees the tie x ≡ y mod 3);
  - "tie images are bijections modulo any proper equivalence" (K₆ modulo
    equality, which is finer than its top);
  - "every law that composes like cycles is Mal'tsev on its tops"
    (parity beside J).
