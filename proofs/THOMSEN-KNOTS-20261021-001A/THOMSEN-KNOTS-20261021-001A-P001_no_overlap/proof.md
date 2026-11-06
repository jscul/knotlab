# No knot overlaps: Thomsen's configuration and the 3-net of Q₈

Status: Proved

Ticket `THOMSEN-KNOTS-20261021-001A`, 2026-10-21. It uses:
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001` ("the circuits proof");
- `MALTSEV-CONVERSE-20261020-001B-P001` ("the converse proof"): Lemma 2 (direct
  hubs);
- `CYCLE-TOPS-20261021-001B-P001` ("the tops proof"): Lemma 1, Theorem 2 (the
  top lemma), Corollaries 3 and 4, and Conjecture 7;
- `KNOT-IMAGES-20261021-001B-P001` ("the images proof"): the 3-net law,
  Theorem 1 (Latin circuits compose like cycles), Corollary 2, Theorem 4
  (abelian 3-nets), Proposition 6 (Q₈) and the Latin conjecture;
- the census `KNOT-IMAGES-20261021-001A-E001`, for its squares and the certified
  top of Q₈.

## Standard statement

**Definitions.** They are those of the tops proof, for laws with sorts as in the
images proof.
- **Circuit relations.** A relation is a circuit relation when its variables
  form a circuit of it: it is constrained, and every proper subset of its
  variables is free relative to its ranges. The projection of a system onto
  one of its circuits is a circuit relation.
- **Overlap.** Let K be a circuit relation on a ∪ {e}, and B the range of e.
  - Its fibre-sharing relation at e is λ_e(t, t′) = ∃a: K(a, t) ∧ K(a, t′).
  - K **overlaps at e** when λ_e = B², so that every two values of e share a
    fibre. At the top level this is the overlapping case of the tops proof's
    Corollary 4.
- **Allowing t′ = t.** Let t ≠ t′ be variables with the same range B. A relation
  **allows t′ = t** when it contains (z, s, s) for every s ∈ B and every value z
  of its other variables in the product of their ranges.
- **Thomsen's configuration.** Take a Latin square (Q, ∘) and its 3-net law:
  rows X, columns Y, labels Z, and the one relation {(x, y, x ∘ y)}. Let

  T′(x₁, x₂, x₃, y₁) = ∃y₂, y₃: x₁∘y₂ = x₂∘y₁ ∧ x₁∘y₃ = x₃∘y₁ ∧ x₂∘y₃ = x₃∘y₂,

  and let T(x₁, x₂, x₃) = ∃y₁: T′(x₁, x₂, x₃, y₁).
  - Each equation u∘v = u′∘v′ is two atoms that share a hidden label.
  - So T′ is a system with six atoms and five hidden variables. T has one more
    hidden variable.
- **Thomsen's closure condition:** x₁∘y₂ = x₂∘y₁ and x₁∘y₃ = x₃∘y₁ imply
  x₂∘y₃ = x₃∘y₂.

**This proof shows the following.**
1. **Doubling** (Lemma 1). Let ρ be a circuit relation on Z ∪ {t, t′}, with Z
   nonempty, that allows t′ = t. Then two copies of ρ sharing t and t′ violate
   elimination. This is the selector case of the converse proof's Lemma 2.
2. **No circuit overlaps** (Theorem 2). In a law that composes like cycles, no
   circuit's top image overlaps at any variable.
   - **Why.** Take two copies of an overlapping knot that share all but one
     variable. By elimination they contain a circuit relation that allows
     t′ = t, and Lemma 1 applies.
   - **So the overlapping case never occurs.** Every circuit's top image is a
     Latin hypercube of the tops. This proves the images proof's Latin
     conjecture.
   - **The local converse holds at the top level.** A Latin hypercube is
     rectangular at every variable. The converse proof asked whether every
     knot is rectangular once knots compose like cycles. That is false below
     the tops (K₄ of the diagonal-lemma epic), and true modulo them.
3. **The characterization** (Corollary 3). A law composes like cycles exactly
   when each range with two or more values carries a proper pp-definable
   equivalence modulo which every circuit is functional at each of its
   variables. The tops then serve.
4. **3-nets** (Theorem 4).
   - T′ and T allow every tuple with two equal rows.
   - T′ is full exactly when Thomsen's condition holds. Otherwise T or T′ is a
     knot that overlaps at every variable.
   - So the 3-net law of a Latin square composes like cycles exactly when the
     square is isotopic to an abelian p-group.
   - A group's 3-net law composes like cycles exactly when it is an abelian
     p-group.
5. **Q₈** (Proposition 5).
   - T is the commuting-differences relation.
   - Its top image modulo ±1 is ω(c₁ + c₂, c₁ + c₃) = 0, where ω is the
     symplectic form on F₂². x + y + z does not preserve it. Three of its
     tuples replace the images proof's 416-equation certificate.
   - The system T(x₁, x₂, x₃) ∧ T(x₁, x₂, x₃′) violates elimination. So the
     3-net law of Q₈ does not compose like cycles.
   - **Conjecture 7 survives.** The images proof left two possibilities: Q₈
     fails in a larger system, or the tops proof's Conjecture 7 is false. The
     first holds, in a system of 16 variables.

## Nearest known results

- **Thomsen's condition.** It characterizes the quasigroups isotopic to abelian
  groups (Thomsen, 1930; Blaschke and Bol, *Geometrie der Gewebe*, 1938). See
  the [Encyclopedia of Mathematics entry on closure
  conditions](https://encyclopediaofmath.org/wiki/Closure_condition). Theorem 4
  uses one direction of it as a black box.
- **The converse proof's Lemma 2.** It showed that a knot with a selector forms
  a hub with a copy of itself, and Lemma 1 is its special case.
  - The new step is Theorem 2's derivation: one doubling and one use of
    elimination turn any overlapping knot into a circuit relation with a
    selector.
  - The converse proof's Observation 6 found such "one derivation" hubs for
    every 3-variable knot it tested, before tops were defined.
- **Multiary quasigroups.** Corollary 3 says that, modulo the tops, every
  circuit is the graph of a multiary quasigroup.
  [Zaslavsky's biased expansions](https://arxiv.org/abs/math/0411268) shows
  that such quasigroups attached to 3-connected graphs are groups in disguise.
  Composing like cycles does not fix the graph, so that theorem does not apply
  directly.

**Classification: new to the program; elementary.**
- Lemma 1 restates the converse proof's selector case.
- Theorem 2's derivation is short. I found no source for it, but an expert in
  matroids or constraint languages would find it quickly.
- Theorem 4 combines Lemma 1 with Thomsen's classical theorem and the images
  proof's Theorem 4.
- Proposition 5 is a computation.

## Lemma 1 (doubling)

Let ρ be a circuit relation on Z ∪ {t, t′}, with Z ≠ ∅, that allows t′ = t.
Let Z₁ and Z₂ be disjoint copies of Z, and

  Σ(z₁, z₂, t, t′) = ρ(z₁, t, t′) ∧ ρ(z₂, t, t′).

Then D₁ = Z₁ ∪ {t, t′} and D₂ = Z₂ ∪ {t, t′} are distinct circuits of Σ. Both
Z₁ ∪ Z₂ ∪ {t′} and Z₁ ∪ Z₂ ∪ {t} are free. So Σ violates elimination at t and
at t′.

*Proof.*
1. **The copies are circuits.** Σ's projection onto D₁ is ρ, because a tuple
   (z₁, s, s′) ∈ ρ extends by z₂ = z₁.
   - So D₁ has ρ's ranges, and it is a circuit of Σ because its variables form
     a circuit of ρ. Likewise D₂.
   - They are distinct because Z is nonempty.
2. **Removing t leaves a free set.** Take z₁ and z₂ in the product of Z's
   ranges, and s′ in the range of t′. Put t = s′. Both (z₁, s′, s′) and
   (z₂, s′, s′) lie in ρ, because ρ allows t′ = t.
3. **Removing t′ leaves a free set,** in the same way, putting t′ = t.
4. **Conclusion.** Every subset of a free set is free. So no circuit lies inside
   (D₁ ∪ D₂) − t, nor inside (D₁ ∪ D₂) − t′. ∎

**Relation to the converse proof.** There, s is a selector for e when, for each
value of s, the fibres over e pairwise meet. Allowing t′ = t makes t a selector
for t′: each fibre over t′ at t = s contains s. The converse proof's Lemma 2
then gives the same failure.

## Theorem 2 (no circuit overlaps)

Let the law compose like cycles. Let C be a circuit of a system S, and e ∈ C.
Then the top image of S on C is functional at e.

So every circuit's top image is a Latin hypercube of the tops: the top classes
of all variables but one allow exactly one top class of the last. This proves
the images proof's Latin conjecture.

*Proof.* Let K be the blur by the tops of S's projection onto C.
- K is pp-definable, because the tops are.
- By the top lemma, S and its blur have the same circuits, hence the same free
  sets. So K is a circuit relation on C.
- By the tops proof's Corollary 4, K is functional at e or overlaps at e.
  Suppose it overlaps. Write a = C − e, and B for the range of e.

1. **Two copies.** Let S₂(a, e, e′) = K(a, e) ∧ K(a, e′).
   - Its projection onto a ∪ {e} is K: put e′ = e.
   - So C₁ = a ∪ {e} and, in the same way, C₂ = a ∪ {e′} are circuits of S₂.
   - e′ has range B.
2. **Elimination gives a circuit D.** Pick y ∈ a. Elimination gives a circuit D
   inside U = (a − y) ∪ {e, e′}.
3. **D contains e and e′.** (a − y) ∪ {e} is a proper subset of C₁, so it is
   free. Likewise (a − y) ∪ {e′}. So D contains both e and e′.
4. **D contains more.** S₂'s projection onto {e, e′} is λ_e = B², so {e, e′} is
   free. Hence Z = D − {e, e′} is nonempty.
   - For a tie, a − y is empty, so this step already contradicts elimination.
     That is the tops proof's Corollary 3.
5. **D allows e′ = e.** Let ρ be S₂'s projection onto D. Take z in the product
   of Z's ranges and s ∈ B.
   - Z ∪ {e} is a proper subset of C₁, hence free in K.
   - So some (a, s) ∈ K agrees with z on Z, and (a, s, s) ∈ S₂ projects to
     (z, s, s).
6. **The contradiction.** ρ is a pp-definable circuit relation on Z ∪ {e, e′}
   that allows e′ = e. By Lemma 1, two copies of it form a system that violates
   elimination. ∎

**Where overlap is used.** Only in step 4. When K is functional at e, the
projection of S₂ onto {e, e′} is the top μ_B. Then {e, e′} is a tie, D may be
that tie, and Lemma 1 does not apply.

**Explicit failing systems.** The construction works on any circuit relation
that overlaps at e, in any law, with no tops involved. Either S₂ already
violates elimination (U is free), or two copies of D do. The checks replay this
on random overlapping knots and on the census's overlapping laws.

## Corollary 3 (the characterization)

For a law Γ the following are equivalent:
- (i) Γ composes like cycles;
- (ii) each range with two or more values carries a proper pp-definable
  equivalence, modulo which every circuit of every system is functional at each
  of its variables;
- (iii) Γ composes like cycles, and every circuit's top image is a Latin
  hypercube of the tops.

*Proof.*
- **(ii) ⇒ (i)** is the images proof's Theorem 1.
- **(i) ⇒ (iii)** is Theorem 2.
- **(iii) ⇒ (ii)** takes the tops. ∎

This removes the clause "no circuit is overlapping" from the images proof's
Corollary 2.

**What it says about Conjecture 7.** Conjecture 7 asks for one ternary
polymorphism that is Mal'tsev modulo the tops on knot ranges.
- **Corollary 3 does not supply one.** It describes each circuit's top image as
  a multiary quasigroup, one circuit at a time.
- **No separating law is known.** The images proof found one law that could
  separate the two properties, the 3-net of Q₈. Proposition 5 shows that it
  does not compose like cycles.

## Theorem 4 (3-nets)

Let (Q, ∘) be a Latin square of order n ≥ 2, with its 3-net law.
- **(a)** T′ and T allow every tuple in which two of x₁, x₂, x₃ are equal.
- **(b)** T′ is full exactly when Thomsen's condition holds.
- **(c)** Suppose Thomsen's condition fails.
  - If T is not full, it is a knot.
  - If T is full, T′ is a knot.
  - Either knot overlaps at every variable.
- **(d)** The 3-net law composes like cycles exactly when (Q, ∘) is isotopic to
  an abelian p-group.
- **(e)** For a group G, T′ = T × G and
  T = {(x₁, x₂, x₃) : x₂⁻¹x₁ and x₃⁻¹x₁ commute}. So the 3-net law of a group
  composes like cycles exactly when the group is an abelian p-group.

*Proof.*
1. **The hidden columns are determined.** Given x₁, x₂, x₃ and y₁, the first two
   equations determine y₂ and y₃, because each row of a Latin square is a
   bijection. So T′(x₁, x₂, x₃, y₁) says that these y₂ and y₃ satisfy the third
   equation.
2. **(a).**
   - If x₁ = x₂, the first equation forces y₂ = y₁. The third then reads
     x₁∘y₃ = x₃∘y₁, which is the second.
   - If x₁ = x₃, then y₃ = y₁ in the same way, and the third equation is the
     first.
   - If x₂ = x₃, the first two equations give x₁∘y₂ = x₁∘y₃, so y₂ = y₃. The
     third equation then reads x₂∘y₂ = x₂∘y₂.
3. **(b).** By step 1, T′ is full exactly when, for all x₁, x₂, x₃ and y₁, the
   y₂ and y₃ solving the first two equations solve the third. That is Thomsen's
   condition.
4. **(c).** Suppose Thomsen's condition fails.
   - **T.** Every 2-projection of T is full: given two of x₁, x₂, x₃, set the
     third equal to one of them and use (a). So if T is not full, it is a knot.
   - **T′.** If T is full, T′ is not, by (b). Its 3-projections are T and the
     three that omit one row. Each of those three is full by (a): extend any
     values of the other variables by setting the omitted row equal to another
     row. So T′ is a knot.
   - **Overlap.** By (a), a fibre over a tuple with two equal rows is
     everything.
     - In T, the fibre at x₃ over x₁ = x₂ is all of Q, and likewise at x₁ and
       at x₂.
     - In T′, the fibre at y₁ over (x₁, x₁, x₃) is all of Q, and the row
       variables are as in T.
5. **(d), the failures.** Suppose Thomsen's condition fails, and let ρ be the
   knot of (c).
   - By (a), ρ allows x₂ = x₁. Lemma 1 applies with t = x₁, t′ = x₂, and
     Z = {x₃} or Z = {x₃, y₁}. So
     T(x₁, x₂, x₃) ∧ T(x₁, x₂, x₃′) or T′(x₁, x₂, x₃, y₁) ∧ T′(x₁, x₂, x₃′, y₁′)
     violates elimination at x₁ and at x₂.
   - Theorem 2 gives the same conclusion without exhibiting the system.
6. **(d), the survivors.** If Thomsen's condition holds, Thomsen's theorem makes
   (Q, ∘) isotopic to an abelian group G: x ∘ y = γ(α(x) + β(y)) for bijections
   α, β and γ.
   - The maps α on rows, β on columns and γ⁻¹ on labels carry the relation of
     (Q, ∘) onto that of G.
   - So the two 3-net laws are isomorphic, with the same systems up to renaming
     values.
   - By the images proof's Theorem 4, the law composes like cycles exactly when
     G is a p-group.
7. **(e).** Write a = x₂⁻¹x₁ and b = x₃⁻¹x₁.
   - The first two equations say y₁y₂⁻¹ = a and y₁y₃⁻¹ = b.
   - Then x₃⁻¹x₂ = ba⁻¹ and y₂y₃⁻¹ = a⁻¹b. So the third equation says
     ba⁻¹ = a⁻¹b, that is ab = ba.
   - This does not involve y₁. So T′ = T × G, and T is the
     commuting-differences relation. It is full exactly when G is abelian. ∎

**Shared labels.** Every system of the 3-net law is also a system of the
single-sorted law {(x, y, x ∘ y)} on Q, with the same allowed states.
- So if the single-sorted law composes like cycles, so does the 3-net law, and
  (Q, ∘) is isotopic to an abelian p-group.
- The converse for single-sorted laws is not examined.

**Which form fires.**
- For every group and for the non-group class of order 5, T itself is the
  knot.
- Among 60 random squares of order 6, T is full for 23, and T′ is needed.
- The census's order-6 "diagonal survivor", which census A saw only as a
  collapse of its tops, fails through T′.

**Why census A missed these failures.** T and T′ have nine variables and six
atoms each, and their doubled systems have 16 variables and 12 atoms. Census A's
systems had at most six atoms and eight variables; its random systems for the
squares of order 8, Q₈ among them, had at most six variables. Scoping went up to
twelve variables.

## Proposition 5 (Q₈)

Write Q₈ as pairs (sign, class), with class in F₂² and
(s, a)(t, b) = (s + t + f(a, b), a + b), where f(a, b) = a₁b₁ + a₂b₂ + a₂b₁, as
in the images proof. Let μ be congruence modulo ±1, that is, equal classes. It
is census A's certified top on each sort.
- **(a)** T = {(x₁, x₂, x₃) : x₂⁻¹x₁ and x₃⁻¹x₁ commute}. It has 320 of the 512
  triples, and it is a knot that overlaps at every variable.
- **(b)** T is a union of μ-classes, and its top image is

  T̄ = {(c₁, c₂, c₃) ∈ (F₂²)³ : ω(c₁ + c₂, c₁ + c₃) = 0}, where
  ω(u, v) = u₁v₂ + u₂v₁.

  T̄ has 40 of the 64 triples.
- **(c)** x + y + z does not preserve T̄. (0, e₁, 0), (0, 0, 0) and (0, 0, e₂)
  lie in T̄, but their sum (0, e₁, e₂) does not. So no polymorphism of the
  3-net law of Q₈ is Mal'tsev modulo ±1. This replaces the images proof's
  416-equation certificate.
- **(d)** The system T(x₁, x₂, x₃) ∧ T(x₁, x₂, x₃′) has exactly two circuits,
  {x₁, x₂, x₃} and {x₁, x₂, x₃′}. It violates elimination at x₁ and at x₂. So
  the 3-net law of Q₈ does not compose like cycles.

*Proof.*
1. **(a).** This is Theorem 4(c) and (e), since Q₈ is not abelian.
   - For fixed x₁, the map (x₂, x₃) ↦ (x₂⁻¹x₁, x₃⁻¹x₁) is a bijection onto pairs
     of elements.
   - Q₈ has 40 commuting pairs: 8 elements times 5 conjugacy classes. So T has
     8 × 40 = 320 triples.
2. **(b).** Two elements commute exactly when f(a, b) = f(b, a).
   - f(a, b) + f(b, a) = a₁b₂ + a₂b₁ = ω(a, b). So commuting depends only on
     classes.
   - The class of x₂⁻¹x₁ is c₁ + c₂, and that of x₃⁻¹x₁ is c₁ + c₃. This gives
     T̄, and T is its full preimage.
   - For each c₁, the map (c₂, c₃) ↦ (c₁ + c₂, c₁ + c₃) is a bijection.
     ω(u, v) = 0 exactly when u and v are linearly dependent over F₂: 10 of the
     16 pairs. So T̄ has 4 × 10 = 40 triples.
3. **(c).** ω(e₁, 0) = ω(0, e₂) = 0, and ω(e₁, e₂) = 1.
   - By the images proof's Proposition 6, steps 1 and 2, a polymorphism F that
     is Mal'tsev modulo ±1 induces x + y + z on the classes of each sort.
   - F preserves T. Since T is a union of μ-classes, the induced operation
     preserves T̄. That is a contradiction.
4. **(d).** Apply Lemma 1 with ρ = T, t = x₁, t′ = x₂ and Z = {x₃}. T allows
   x₂ = x₁ by Theorem 4(a). The checks compute every circuit of the system:
   the two named are the only ones. ∎

**What it means.**
- **The images proof's open alternative is decided.** Q₈'s 3-net law fails in a
  system of 16 variables, four of them visible.
  - Its knot T has nine variables.
  - Its top image is the relation that is not affine, which the 416-equation
    certificate showed must exist.
  - Scoping had tested only top images small enough to enumerate (1,412 of
    them, all affine); T has 320 tuples.
- **Conjecture 7 survives.** No law is known that composes like cycles without a
  Mal'tsev operation on its knot tops.
- **Every non-abelian group fails.** The images proof's Proposition 5 covered
  groups generated by small elements. Theorem 4(e) covers all non-abelian
  groups.

## What this does not show

- **Conjecture 7** (Mal'tsev on the tops of knot ranges) is not proved.
  Corollary 3 makes each circuit's top image a multiary quasigroup, but it does
  not say how different circuits fit into one operation.
- **The matroid-level converse** remains open. It still rests on Conjecture 7
  and the matroid proof's Remark.
- **Single-sorted 3-net laws.** Those of abelian p-group isotopes are not
  classified; only the necessary direction is shown.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` writes `result.json` in about six seconds. All checks pass, and all
controls are rejected.

- **Theorem 2's construction.** It ran on 400 random knots of three and four
  variables over two and three values. At each of the 1,372 variables where a
  knot overlaps:
  - S₂ violated elimination at once 1,097 times;
  - otherwise, the circuit D had three variables (155 times) or four (120),
    allowed e′ = e, and its two copies violated elimination at e and at e′.

  The census's overlapping laws (e = x + yH over Z₅ and Z₇, and the equality
  indicator) fail in the same way at every overlapping variable, each through
  a doubled 3-variable circuit.
- **Theorem 4.** It covers 790 squares: all 590 of orders 2 to 4, 60 random
  squares each of orders 5, 6 and 7, and the 20 census squares. For each:
  - T′ by its formula agrees with an enumeration of the hidden columns;
  - every tuple with two equal rows is allowed;
  - "T′ is full", Thomsen's condition (by brute force) and "isotopic to an
    abelian group" agree;
  - when Thomsen's condition fails, the knot T or T′ is verified to overlap at
    every variable, and its doubled system to violate elimination.

  **The random squares.**
  - Order 5: 5 satisfy Thomsen's condition, and 55 fail through T.
  - Order 6: 37 fail through T and 23 through T′.
  - Order 7: all 60 fail through T.

  **17 groups:** Z₂ to Z₈, Z₂², Z₂×Z₄, Z₃², S₃, D₄, Q₈, D₅, A₄, D₆ and Dic₃.
  T′ = T × G, T is the commuting-differences relation, and every non-abelian
  group fails through T.
- **Proposition 5.**
  - The pair representation matches the census square, and its census top is
    mod ±1 and certified.
  - T computed by enumerating the hidden columns is the commuting-differences
    relation, with 320 triples.
  - T is saturated by ±1, its top image is the 40 triples of T̄, and the three
    tuples sum outside it.
  - The doubled system's circuits are exactly the two named, with failures at
    x₁ and x₂.
- **Controls,** each rejected:
  - "two copies of any knot sharing two variables violate elimination". Over
    Z₃, x + y + z = 0 is a Latin knot; its two copies are tied (z₁ = z₂), and
    elimination holds.
  - "the three-row configuration T detects every square that violates
    Thomsen's condition". A random square of order 6 has T full and T′ a knot.
  - "Thomsen's configuration is a knot in every group's 3-net law". For Z₅,
    both forms are full.
  - "every top image of the Q₈ 3-net law is closed under x + y + z". T̄ is not.
