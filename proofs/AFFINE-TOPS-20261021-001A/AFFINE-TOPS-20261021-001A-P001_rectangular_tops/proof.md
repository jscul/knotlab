# Rectangular top images and Mal'tsev operations modulo the tops

Status: Proved

Ticket `AFFINE-TOPS-20261021-001A`, 2026-10-21. It uses:
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001` ("the circuits proof"),
  including its Lemma 1: under elimination, the free sets of a system are the
  independent sets of a matroid;
- `MATROID-CONVERSE-20261021-001B-P001` ("the matroid proof"): Proposition 6,
  tops exist;
- `CYCLE-TOPS-20261021-001B-P001` ("the tops proof"): Theorem 2 (the top
  lemma), Corollary 3 (ties are bijections of tops), Proposition 5 and
  Conjecture 7;
- `KNOT-IMAGES-20261021-001B-P001` ("the images proof"): Theorem 1 (Latin
  circuits compose like cycles);
- `THOMSEN-KNOTS-20261021-001A-P001` ("the overlap proof"): Theorem 2, every
  circuit's top image is a Latin hypercube;
- the censuses `CYCLE-TOPS-20261021-001A-E001` and
  `KNOT-IMAGES-20261021-001A-E001`, for the laws and certified tops used in the
  checks.

## Standard statement

**Definitions.** They are those of the tops proof, for laws with sorts as in
the images proof.
- **Top images.** A system S has ranges B_v with tops μ_v. Its top image S̄ is
  its image in the product of the quotients B_v/μ_v. A one-value range is its
  own top.
- **Fibres.** Fix a set W of variables and an assignment ω to W that occurs in
  S̄. The fibre over ω is the set of assignments to the other variables that
  complete ω in S̄.
- **Rectangular.** Split a relation's variables into nonempty parts X and Y.
  The relation is rectangular for the split when (x, y), (x, y′) and (x′, y) in
  it imply (x′, y′). Equivalently, any two X-assignments have equal or disjoint
  sets of partners.
- **Generated ranges.** For values a and b of one sort, ⟨a, b⟩ is the set of
  values g(a, b) over the binary polymorphisms g.
  - It is a range: that of the variable at (a, b) in the system of binary
    polymorphisms (step 1 of Theorem 3, with pairs for triples).
  - It lies in every range containing a and b, because polymorphisms preserve
    ranges.
- **Knot ranges.** A knot range is the range of a variable that lies in a knot
  (a circuit of three or more variables) of some system.
- **Mal'tsev modulo θ.** A ternary operation F is Mal'tsev modulo an
  equivalence θ when F(a, b, b) θ a and F(a, a, b) θ b.

**This proof shows the following,** for every law that composes like cycles.
1. **Uniform fibres** (Lemma 1). Over the assignments to any fixed set of
   variables, all nonempty fibres of a top image have the same size.
2. **Top images are rectangular** (Theorem 2), for every split of the
   variables.
3. **A Mal'tsev operation modulo generated tops** (Theorem 3). Some ternary
   polymorphism F is Mal'tsev modulo the top of ⟨a, b⟩, for all a and b of one
   sort.
4. **Subranges of knot ranges** (Lemma 4). Let B be a knot range. A subrange
   that meets two top classes of B meets them all, and its top is the
   restriction of B's.
5. **Conjecture 7 holds** (Corollary 5). F is Mal'tsev modulo the top of every
   knot range. This proves Conjecture 7 of the tops proof.
6. **The characterization** (Corollary 6). A law composes like cycles exactly
   when:
   - every range with two or more values has a top;
   - every tie's top image is a bijection; and
   - some ternary polymorphism is Mal'tsev modulo the top of every knot range.

## Nearest known results

- **Rectangularity and Mal'tsev operations.** A finite structure has a Mal'tsev
  polymorphism exactly when every pp-definable relation is rectangular for
  every split ("strongly rectangular"). This is classical in the counting
  constraint literature: [Dyer and Richerby, An effective dichotomy for the
  counting constraint satisfaction problem](https://arxiv.org/abs/1003.3879);
  see also [Modular counting CSP](https://arxiv.org/abs/2501.04224).
  Theorem 3 reruns that argument modulo the tops.
- **Balance.** Dyer and Richerby's balanced relations have counting matrices
  made of rank-one blocks. Uniform fibres (Lemma 1) are a strong form of
  balance, modulo the tops.
- **The program's input.** What makes fibres uniform is the overlap proof's
  Theorem 2: no circuit of a law that composes like cycles overlaps.

**Classification: new to the program; the step from rectangularity to an
operation is classical.**
- Lemma 1, Theorem 2, Lemma 4 and Corollaries 5 and 6 are new to the program.
- I found no source for "composing like cycles gives a Mal'tsev operation
  modulo the tops". Given the classical tools, an expert in algebraic
  constraint satisfaction could find it, so the folklore risk is moderate.

## Lemma 1 (uniform fibres)

Let the law compose like cycles. Let S be a system with top image S̄, and W a
set of its variables. Then all nonempty fibres of S̄ over assignments to W have
the same size.

*Proof.* By the circuits proof's Lemma 1, the free sets of S form a matroid.
By the top lemma, S̄ has the same free sets: a set is free exactly when its
projection is the full product of its tops. Choose a basis I of W, and extend
it by J to a basis of all the variables.
1. **Everything is a function of I ∪ J.** Let v lie outside I ∪ J. Its
   fundamental circuit C lies inside I ∪ J ∪ {v}. By the overlap proof's
   Theorem 2, the top image of C is functional at v. So in S̄ the class of v is
   a function of the classes on I ∪ J. Likewise, the classes on W are a
   function of those on I.
2. **I ∪ J is free.** Every assignment of top classes to it occurs in S̄.
3. **Counting.** Let ω be an assignment to W that occurs in S̄.
   - Restricting completions of ω to J is injective by step 1, because ω fixes
     the classes on I.
   - It is onto all assignments to J by step 2: the tuple extending
     (ω on I, s on J) has W-part determined by ω on I, which is ω.
   - So every nonempty fibre has the product of the sizes of the tops on J as
     its size. ∎

## Theorem 2 (top images are rectangular)

Let the law compose like cycles. Every system's top image is rectangular for
every split of its variables into X and Y.

*Proof.* Let S^μ be the blur of S by its tops, and X′ a copy of X. Consider the
system Ω = S^μ(X, Y) ∧ S^μ(X′, Y).
- **Ω has S's ranges,** because a tuple of S^μ extends by X′ = X. So it has the
  same tops. It is a union of top classes, with top image
  Ω̄ = {(x, x′, y) : (x, y) ∈ S̄ and (x′, y) ∈ S̄}.
- **Fibres.** Write N(x) for the set of y with (x, y) ∈ S̄. In Ω̄ the fibre over
  (x, x) is N(x), and the fibre over (x, x′) is N(x) ∩ N(x′).
- **The conclusion.** Suppose (x, y), (x, y′) and (x′, y) lie in S̄.
  - Then (x, x′) has a nonempty fibre, since it contains y.
  - By Lemma 1 with W = X ∪ X′, |N(x) ∩ N(x′)| = |N(x)| = |N(x′)|.
  - Hence N(x) = N(x′), and y′ ∈ N(x′). ∎

**Below the tops this fails.** The relation K₄ of the diagonal-lemma epic
composes like cycles, but its fibres over two coordinates have sizes 1 and 2
(the checks' control). The diagonal-lemma epic showed that K₄ is not
rectangular.

## Theorem 3 (a Mal'tsev operation modulo generated tops)

Let the law compose like cycles. There is a ternary polymorphism F such that,
for all values a and b of one sort:
- F(a, b, b) and a lie in one top class of ⟨a, b⟩; and
- F(a, a, b) and b lie in one top class of ⟨a, b⟩.

*Proof.*
1. **The system of ternary polymorphisms.** Take one variable for each triple
   (c₁, c₂, c₃) of values of one sort.
   - For each relation R and each three tuples r¹, r², r³ of R, impose R on the
     variables at (r¹ᵢ, r²ᵢ, r³ᵢ), for i = 1, …, k.
   - The solutions are exactly the tables of ternary polymorphisms. The three
     projections π₁, π₂ and π₃ are solutions.
   - **The two ranges.** The variables at (a, b, b) and at (a, a, b) both range
     over ⟨a, b⟩. The value f(a, b, b) is g(a, b) for the binary polymorphism
     g(x, y) = f(x, y, y), and every binary g arises from f(x, y, z) = g(x, y).
     The variable at (a, a, b) is similar.
2. **The relation R.** Hide every variable except those at the triples
   (a, b, b) and (a, a, b), and call the result R. Split its variables into:
   - X, the triples (a, b, b) with a ≠ b; and
   - Y, the triples (a, a, b).
3. **Three patterns.** On X, π₁ reads a, while π₂ and π₃ read b. On Y, π₁ and
   π₂ read a, while π₃ reads b. Write A_X, B_X, A_Y and B_Y for these patterns.
   Then R contains:
   - (A_X, A_Y), from π₁;
   - (B_X, A_Y), from π₂;
   - (B_X, B_Y), from π₃.
4. **The fourth corner.** By Theorem 2, R's top image is rectangular for the
   split.
   - Take x = B_X, y = A_Y, y′ = B_Y and x′ = A_X. The top image contains the
     classes of (A_X, B_Y).
   - So some tuple of R agrees with A_X on X and with B_Y on Y, modulo the tops
     of the generated ranges.
   - It extends to a solution of the hidden system, which is the required F. ∎

This is the classical proof that strongly rectangular structures have Mal'tsev
polymorphisms, read modulo the tops.

## Lemma 4 (subranges of knot ranges)

Let the law compose like cycles. Let B be a knot range, and B′ ⊆ B a range
that meets at least two classes of μ_B. Then:
- B′ meets every class of μ_B; and
- μ_{B′} = μ_B ∩ B′².

*Proof.*
1. **B′ meets every class.** Let B″ be the union of the μ_B-classes that meet
   B′. It is a range, being pp-definable. Let Σ be its set of classes, so that
   |Σ| ≥ 2.
   - **The knot.** Take a knot C of some system S, with e ∈ C of range B. Let
     K be the blur by the tops of S's projection onto C, and a = C − e, which
     has at least two variables.
   - **K is Latin.** By the overlap proof's Theorem 2, K̄ is a Latin
     hypercube. With the classes on a minus one variable a_j fixed, the class
     of a_j determines the class of e bijectively.
   - **Restrict e.** Suppose Σ is not every class, and let K′ = K ∧ B″(e).
     - Every variable of a keeps its range in K′: fix a value of a_j, and
       choose the class of another variable of a so that e lands in Σ.
     - The set a is constrained, because classes that send e outside Σ are
       lost.
     - Every proper subset of a is free, by the same choice.
     - So a is a circuit of K′.
   - **The contradiction.** The top image of that circuit has fibres of |Σ|
     classes at a_j. Since |Σ| ≥ 2, it is not functional, against the overlap
     proof's Theorem 2. Hence Σ is every class.
2. **The tie.** Let λ(x, u) = μ_B(x, u) ∧ B′(u).
   - By step 1, x ranges over B and u over B′.
   - λ is constrained, since two values of B′ in different classes of μ_B are
     not related.
   - So {x, u} is a tie. By the tops proof's Corollary 3, its top image is the
     graph of a bijection between B/μ_B and B′/μ_{B′}.
3. **The tops agree.** λ contains (u, u) for each u ∈ B′, and (u, u′) whenever
   u μ_B u′.
   - If u μ_B u′, the classes of u and u′ in B′ are both matched with the class
     of u in B. So u μ_{B′} u′.
   - If u μ_{B′} u′, the class of u in B′ is matched with the classes of u and
     of u′ in B. So u μ_B u′. ∎

The lemma uses a knot through B. For ranges that meet only ties it is not
claimed.

## Corollary 5 (Conjecture 7)

The polymorphism F of Theorem 3 is Mal'tsev modulo the top of every knot range:
F(a, b, b) μ_B a and F(a, a, b) μ_B b for all a, b in a knot range B. This
proves Conjecture 7 of the tops proof.

*Proof.* Let B′ = ⟨a, b⟩, which lies inside B.
- If B′ lies in one class of μ_B, so do F(a, b, b), F(a, a, b), a and b.
- Otherwise, Lemma 4 gives μ_{B′} = μ_B ∩ B′², and Theorem 3 gives the
  claim. ∎

**Why the generated tops.** The tops proof's Proposition 5 found that parity
beside J has no polymorphism Mal'tsev modulo the top of every range containing
its arguments. The checks confirm this by exhaustive search.
- In its encoding on {0, …, 4}, the values 3 and 4 lie in the whole domain,
  whose top is equality.
- They also generate {2, 3, 4}, whose top joins 3 and 4.
- Theorem 3 asks only for the second, and the checks find such an operation.

## Corollary 6 (the characterization)

For a law Γ the following are equivalent:
- (i) Γ composes like cycles;
- (ii) all three of these hold:
  - (a) every range with two or more values has a top;
  - (b) every tie's top image is a bijection;
  - (c) some ternary polymorphism is Mal'tsev modulo the top of every knot
    range.

*Proof.*
- **(i) ⇒ (ii).** (a) is the matroid proof's Proposition 6, (b) is the tops
  proof's Corollary 3, and (c) is Corollary 5.
- **(ii) ⇒ (i).** By the images proof's Theorem 1, with the tops as the
  equivalences, it is enough that every circuit's top image is functional at
  each of its variables. Ties are covered by (b). For a knot:
  - **Rectangular.** Let K̄ be the knot's top image and F the polymorphism of
    (c). F preserves the knot's relation and every top, since both are
    pp-definable. So the operation it induces preserves K̄, and it is Mal'tsev
    on each coordinate, because every variable of the knot has a knot range.
    Hence K̄ is rectangular.
  - **Fibres.** For the split into a variable e and the rest, fibres at e are
    equal or disjoint. They are the classes of the pp-definable equivalence
    "two values share a fibre", which contains μ_e.
  - **Not total.** If that equivalence were total, every fibre would be all of
    e's top, e would be free over the rest, and the knot would not be a
    circuit.
  - **Functional.** So it is proper, hence inside the top by (a), hence equal
    to μ_e. That means K̄ is functional at e. ∎

**Examples.**
- **(b) is needed.** In x ≤ y on two values, (a) holds and there are no knots,
  so (c) holds trivially. There are no knots because the median preserves ≤,
  so every pp-definable relation is decided by its pairs of variables.
  - Yet the tie x ≤ y is not a bijection.
  - x ≤ e ∧ z ≤ e fails elimination.
- **The circuits proof's Theorem 1.** With a genuine Mal'tsev polymorphism,
  (c) holds, and (b) follows from (a) by the same rectangularity argument. So
  Corollary 6 reduces to that theorem's condition: every range has a unique
  maximal congruence.

**What it means for the series.**
- The conditions epic asked whether composing like cycles is a Mal'tsev
  condition. The answer is yes, modulo the tops, given bijective ties.
- Ticket B of this epic describes the operation: on each knot range's top it
  is x − y + z for an elementary abelian p-group.

## What this does not show

- **Tie ranges.** Whether F can also be Mal'tsev modulo the tops of ranges met
  only by ties is not decided. Lemma 4 needs a knot.
- **The structure of the tops and the matroids.** These are ticket B's
  subject.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` writes `result.json` in about five seconds. All checks pass, and all
controls are rejected.

- **Laws used:**
  - from census `CYCLE-TOPS-20261021-001A-E001`, with its certified tops: the
    five surviving removals from the lifted Z₃ law's (2,2,2)-block, both lifts
    of K₆, parity beside J, K₄ beside Z₃, parity, and Z₃;
  - from census `KNOT-IMAGES-20261021-001A-E001`: the 3-net laws of Z₄, Z₂×Z₂
    and Z₂×Z₄.
- **Lemma 1 and Theorem 2.** For each law, 120 random systems (sort-respecting
  for the 3-nets) had some variables hidden.
  - That gives 1,680 top images, with 4,791 visible variables in all.
  - For every set of visible variables, the nonempty fibres have one size.
  - Every top image is rectangular for every split.
- **Theorem 3, Lemma 4 and Corollary 5.** Six laws were checked: parity beside
  J, K₄ beside Z₃, the full lift, the removal of (2,2,2), parity, and Z₃. In
  each:
  - the range generated by each pair of values is computed exactly from the
    binary polymorphisms, and each one is a range whose top the census
    certified;
  - a search finds a polymorphism Mal'tsev modulo the generated tops, and it
    is re-verified against every relation;
  - it is Mal'tsev modulo the top of every knot range;
  - all 11 subranges of knot ranges meeting two top classes meet them all and
    carry the restricted top.
- **Corollary 6.** In the eleven census laws, the census certified every top,
  found every tie bijective, and found a polymorphism Mal'tsev on the knot
  ranges.
- **Controls,** each rejected:
  - "every law has rectangular top images". In the 3-net of Q₈, Thomsen's
    configuration has a top image of 40 triples that is not rectangular, with
    fibres of different sizes.
  - "some polymorphism is Mal'tsev modulo the top of every range containing
    its arguments". Exhaustive search finds none for parity beside J.
  - "fibres are uniform below the tops". The relation K₄ has fibres of sizes 1
    and 2.
  - "conditions (a) and (c) of Corollary 6 suffice". In x ≤ y, the tie is not
    a bijection and elimination fails.
