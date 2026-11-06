# Difference laws carry only field-representable matroids

Status: Proved

Ticket `MATROID-CONVERSE-20261021-001B`, 2026-10-21. It uses:
- the definitions and Theorem 1 of `KNOT-CIRCUITS-20261020-001B-P001` ("the
  circuits proof");
- the shadow and lift theorems of `DIAGONAL-LEMMA-20261021-001B-P001` ("the
  shadow proof");
- the census `MATROID-CONVERSE-20261021-001A-E001` ("A").

## Standard statement

**Definitions.**
- A set Y of a system's variables is **free** when its projection is the full
  product of the variables' ranges. The constrained sets are the others, and
  the circuits are the minimal constrained sets.
- A law **composes like cycles** when every system's circuits satisfy
  circuit elimination. Then every system's free sets are the independent sets
  of a matroid: the **system's matroid**. A variable with a single value is a
  coloop.
- **𝓡** is the class of matroids that are direct sums of matroids, each
  representable over some finite field.

**The question.** The shadow proof showed that composing like cycles sees only
which sets are constrained. The matroid-level converse asks whether every law
that composes like cycles has, system by system, the constrained sets of a
difference law. Equivalently, it asks which matroids such laws can carry.

**This proof shows the following.**
1. **Single relations carry anything** (Proposition 1). Every downset of
   subsets of a finite set that contains the singletons is the free-set family
   of one relation.
   - So the Vámos matroid is the matroid of a relation, for example of its
     support relation or of a union of two linear codes over GF(7).
   - The laws of both relations fail.

   The converse is therefore a question about laws, not about relations.
2. **The top lemma** (Theorem 2). Let finite algebras in a Mal'tsev variety
   each have a unique maximal congruence. A subdirect product of them is the
   full product exactly when its image in the product of the simple quotients
   ("tops") is full.
3. **Group and field laws** (Theorem 3).
   - **Groups.** Suppose G is a finite group in which every nontrivial
     subgroup has a unique maximal normal subgroup. In a law of cosets of
     subgroups of powers of G, every system's matroid is a direct sum of one
     GF(p)-representable matroid per prime p, together with parallel classes.
   - **Fields.** In a law of affine subspaces over a finite field F, every
     system's matroid is F-representable.
4. **What never appears** (Corollary 4). The Vámos matroid, the non-Pappus
   matroid and the 2-sum of the Fano and non-Fano matroids are connected and
   representable over no field. So none of them is the matroid of any system
   of such a law, or of its shadows, lifts and disjoint unions.
5. **What remains open** (Conjecture 5). Is every law that composes like
   cycles inside 𝓡? Census A found that every one-tuple perturbation of
   x + y + z ≡ 0 over Z₃, or of its lift, either fails or keeps the Z₃ law's
   constrained sets in every sampled system.
6. **Tops exist in every such law** (Proposition 6). In any law that composes
   like cycles, every range has a unique maximal pp-definable equivalence. No
   difference operation is needed. So each variable of each system has a top,
   and the conjecture can be sharpened to a top lemma for all such laws.

## Nearest known results

- **Secret sharing and partition representations.**
  - Brickell and Davenport (J. Cryptology 1991) showed that ideal secret
    sharing schemes induce matroids.
  - [Seymour (J. Combin. Theory B 56, 1992)](https://collaborate.princeton.edu/en/publications/on-secret-sharing-matroids/)
    showed that the Vámos matroid is not one of them.
  - Matúš (Discrete Math. 203, 1999) studied matroid representations by
    partitions.
  - [Simonis and Ashikhmin (Des. Codes Cryptogr. 14, 1998)](https://en.wikipedia.org/wiki/V%C3%A1mos_matroid)
    studied almost affine codes.

  All four work with *uniform* representations, where a set's projection has
  size q^{rank}.
- **Entropic matroids.** [Abbe and Spirkl (2019)](https://arxiv.org/abs/1909.12175)
  showed that p-entropic matroids are linear for p = 2, 3 but not for p = 9.
- **Group theory.**
  - The Frattini argument: a subgroup K of P with K·Φ(P) = P is P itself.
  - [Fleischer's lemma (1955)](https://arxiv.org/pdf/2311.04994): subdirect
    products of two algebras in a Mal'tsev variety are pullbacks.
  - Scott's lemma: a subdirect product of non-abelian simple groups is a
    product of diagonals.
  - Congruence lattices in a Mal'tsev variety are modular.

**Classification: new to the program; built from classical tools.**
- Constrained sets relative to ranges are weaker than the uniform notions
  above. That is why Proposition 1 is trivial while Seymour's theorem is not.
- The top lemma generalizes the Frattini argument. I expect a form of it is
  known in universal algebra, but I did not find it stated.
- I found no statement of the matroid consequence for group laws.

## Proposition 1 (single relations carry any matroid)

Let I be a downset of subsets of a finite set E that contains every singleton.
Then the support relation

  S_I = {x ∈ {0,1}^E : the set of 1-coordinates of x lies in I}

has exactly I as its family of free sets.

*Proof.*
- Every coordinate takes both values, because the singletons lie in I.
- If Y ∈ I, every pattern on Y has its support inside Y. It extends by zeros
  to a member of S_I, so Y is free.
- If Y ∉ I, the all-ones pattern on Y would need a member whose support
  contains Y. No member of I contains Y, because I is a downset. So Y is
  constrained. ∎

**The Vámos matroid.** It is a matroid on a, a′, b, b′, c, c′, d, d′:
- every set of at most three elements is independent;
- every set of five is dependent;
- among the 4-sets, exactly five of the six "pairs of pairs" are dependent:
  all except {c, c′, d, d′}.

It is carried by two relations:
- **The support relation.**
- **A union of two GF(7) codes C₁ ∪ C₂.**
  - C₁ is four concurrent lines, so every pair of pairs is dependent.
  - In C₂, a and a′ are parallel, and the line bb′ meets cc′ and dd′, which
    are skew.
  - Both matroids are weak-map images of Vámos, and their independent sets
    together are exactly Vámos's.
  - Two proper subspaces never cover a vector space. So a set is free in the
    union exactly when it is free in one of the codes.

**Both laws fail.**
- **The support relation.** Its projection onto a 4-element circuit is "not
  all ones". Every fibre of that relation contains 0, so its fibres meet, and
  two copies fail (the converse proof's Lemma 2). This holds for the support
  relation of any matroid with a circuit of three or more elements.
- **The union of codes.** Its projection onto {a, a′, b, b′} has a selector
  (a′ for a), so two copies sharing a and a′ fail.

The checks confirm both, and so does A (Q1, Q2).

## Theorem 2 (the top lemma)

Let A₁, …, A_n be finite algebras in a Mal'tsev variety. Suppose each has at
least two elements and a unique maximal congruence μᵢ, so that its top
Aᵢ/μᵢ is simple. Let R ≤ A₁ × … × A_n project onto every Aᵢ. Then
R = A₁ × … × A_n exactly when the image of R in ∏ Aᵢ/μᵢ is the full product.

**Lemma A (maximal congruences of a product).** Every maximal congruence N of
P = ∏ Aᵢ contains the product congruence μ₁ × … × μ_n.

*Proof.*
1. **Two complementary congruences.** Let ηᵢ relate tuples that agree in
   coordinate i, and η̄ᵢ relate tuples that agree outside coordinate i. Then
   ηᵢ ∧ η̄ᵢ = 0. Also ηᵢ ∘ η̄ᵢ = 1: move the i-th coordinate first, then the
   others.
2. **Transposed intervals.** In a Mal'tsev variety the congruence lattice is
   modular. So the intervals [0, η̄ᵢ] and [ηᵢ, 1] are isomorphic, through
   θ ↦ θ ∨ ηᵢ.
3. **One coatom.** The second interval is the congruence lattice of Aᵢ, so
   [0, η̄ᵢ] has exactly one coatom. That coatom is μᵢ⁽ⁱ⁾: "μᵢ in coordinate i,
   equality elsewhere".
4. **N contains μᵢ⁽ⁱ⁾.**
   - If N ⊇ η̄ᵢ, then N ⊇ μᵢ⁽ⁱ⁾.
   - Otherwise N ∨ η̄ᵢ = 1. By modularity the interval [N ∧ η̄ᵢ, η̄ᵢ] is
     isomorphic to [N, 1], which has two elements. So N ∧ η̄ᵢ is the coatom
     μᵢ⁽ⁱ⁾.
5. **Conclusion.** The product congruence is the relational product of the
   μᵢ⁽ⁱ⁾, changing one coordinate at a time, so it lies in N. ∎

**Lemma B (Fleischer).** In a Mal'tsev variety, a subdirect product R of B and
C is a pullback: R = {(b, c) : φ(b/β) = c/γ} for congruences β, γ and an
isomorphism φ: B/β → C/γ.

*Proof of Theorem 2.* Induction on n; the case n = 1 is immediate.
1. **The first n − 1 coordinates.** The projection R′ of R onto them projects
   onto each factor and has a full top image. By induction it is
   P′ = ∏_{i<n} Aᵢ.
2. **Fleischer.** By Lemma B, R is the pullback of an isomorphism
   φ: P′/β → A_n/γ. If γ is total, R is the full product.
3. **Otherwise.**
   - γ ≤ μ_n, because every proper congruence lies below the unique maximal
     one.
   - So φ induces P′/N ≅ A_n/μ_n for a maximal congruence N of P′.
   - By Lemma A, N contains the product of the μᵢ for i < n. So on R, the top
     of the last coordinate is a function of the other tops.
   - A_n/μ_n has at least two elements, so the image of R in the tops is not
     full. ∎

## Theorem 3 (group and field laws)

**(a) Groups.** Let G be a finite group in which every subgroup with at least
two elements has a unique maximal normal subgroup. Let Γ be a law whose
relations are cosets of subgroups of powers of G. Then:
- Γ composes like cycles;
- every system's matroid is a direct sum M₂ ⊕ M₃ ⊕ M₅ ⊕ … ⊕ N, where each M_p
  is representable over GF(p) and N is a direct sum of rank-one parallel
  classes.

**(b) Fields.** If Γ's relations are affine subspaces over a finite field F,
every system's matroid is F-representable, and Γ composes like cycles.

*Proof.*
- **(b).** A system's allowed states form an affine subspace. Y is free
  exactly when the columns indexed by Y of a generator matrix of its direction
  space are independent.
- **(a), setting up.**
  - The allowed states S form a coset of a subgroup of G^V. Translating does
    not change free sets, so take S to be a subgroup.
  - Each range H_y is a subgroup with a unique maximal normal subgroup μ_y.
    The congruences of a group are given by its normal subgroups.
  - By Theorem 2, applied to π_Y(S) ≤ ∏_{y∈Y} H_y, Y is free exactly when the
    image of π_Y(S) in ∏ H_y/μ_y is full.
  - Let S̄ ≤ ∏_y T_y be the image of S in the simple tops T_y = H_y/μ_y. Then
    S and S̄ have the same free sets.
- **(a), splitting the top image.**
  1. **Abelian against non-abelian.** Split the variables into those with
     abelian tops, each cyclic of a prime order p_y, and those with
     non-abelian simple tops.
     - Any common quotient of a subgroup of an abelian group and a subdirect
       product of non-abelian simple groups is trivial. The second has only
       products of non-abelian simple groups as quotients, by Scott's lemma.
     - So, by Goursat, S̄ is the product of its abelian part and its
       non-abelian part.
  2. **One prime at a time.** The abelian part is the product of its Sylow
     subgroups. For each prime p, the Sylow p-part S̄_p is a subgroup of
     Z_p^{V_p}, that is, a GF(p)-linear code.
  3. **Diagonals.** By Scott's lemma, the non-abelian part is a product of full
     diagonals over a partition of its variables into blocks.
  4. **Reading the free sets.** Y is free exactly when, for each p, Y ∩ V_p is
     free in the code S̄_p and Y meets each block at most once. That is the
     claimed direct sum.
- **(a), composing like cycles.** Matroids satisfy circuit elimination, so Γ
  composes like cycles. This agrees with Theorem 1 of the circuits proof. ∎

In every example checked, the tops are cyclic of prime order and the
non-abelian part is empty.

## Corollary 4 (what never appears)

Every system of a law covered by Theorem 3 has its matroid in 𝓡. So do:
- the systems of its shadows and lifts, which have the same constrained sets
  (shadow proof, Theorems 1 and 2);
- the systems of disjoint unions of such laws, whose matroids are direct sums.

**Three matroids outside 𝓡.** Each is connected and representable over no
field, so it is not in 𝓡:
- the Vámos matroid (not representable, classical: Vámos, Ingleton);
- the non-Pappus matroid (Pappus' theorem holds over every field);
- the 2-sum of the Fano matroid, which needs characteristic 2, and the
  non-Fano matroid, which needs characteristic other than 2.

None of the three is the matroid of a system of these laws. Yet each is the
matroid of a single relation, by Proposition 1.

**The checks.** They confirm that Vámos as defined here is connected, not
binary and not ternary.

## Conjecture 5 (the matroid-level converse)

- **(weak)** Every law that composes like cycles has every system's matroid in
  𝓡.
- **(top lemma)** In every law that composes like cycles, a set is free exactly
  when its image in the product of its variables' tops is full. Proposition 6
  shows the tops exist. Theorem 2 proves this for difference laws, and the
  shadow and lift theorems give it for shadows and lifts.
- **(strong)** Every such law is dressed. There is a law Δ covered by Theorem 3
  such that each system has, through a surjection of values, the constrained
  sets of the same system over Δ. Shadows, lifts and disjoint unions are
  dressed in this sense.

**Evidence from census A.**
- **Q1–Q2.** Both relations that carry the Vámos matroid have failing laws.
- **Q3.** Every sampled system of five group laws has the free sets of its top
  image, with no circuit mixing primes.
- **Q4–Q5.** There are 91 one-tuple perturbations of x + y + z ≡ 0 over Z₃
  and of its lift with 2 doubled. 83 have a failure. The 8 survivors are
  exactly the removals from the lift's (2,2,2)-block, and each keeps the Z₃
  law's constrained sets in every sampled system. So the survivors are dressed.

Six of those eight removals take out a non-constant tuple, which the lift
theorem does not cover.

**What would refute it.** A law that composes like cycles and has a system
carrying a matroid outside 𝓡. The matroids outside 𝓡 used here have eight or
nine elements, so a search for one needs systems at least that large. That is
beyond the random search used on small domains.

## Proposition 6 (tops exist in every law that composes like cycles)

Let Γ be a law that composes like cycles, without assuming any difference
operation. Let B be a pp-definable set with at least two elements, which is a
subalgebra of the polymorphism algebra. Then B has a unique maximal
pp-definable equivalence relation, that is, a unique maximal congruence.

*Proof.* Let α and β be proper pp-definable equivalences on B. It is enough to
show that their join is proper.
1. **The base case.** In the system α(x, e) ∧ β(e, y) over B, each variable
   ranges over B. Both {x, e} and {e, y} are ties, because α and β are proper
   and reflexive. Elimination at e makes {x, y} constrained, so α ∘ β ≠ B².
2. **Induction.** Let ρ be any proper alternating product α ∘ β ∘ … of length
   k. It is reflexive, so in ρ(x, e) ∧ γ(e, y), with γ the next factor, both
   are again ties. Elimination makes ρ ∘ γ proper.
3. **Conclusion.** Every alternating product is proper. On a finite set the
   join α ∨ β is one of them, so it is proper. ∎

This generalizes the "only if" half of the circuits proof's Theorem 1, which
used that congruences permute. Here only the composition of ties is used.

**What it changes.** Every variable of every system of such a law has a top,
the quotient of its range by the unique maximal congruence. The checks find:
- in the lift K₄, the single proper derived equivalence merges 2 and 3, and
  its top is Z₃;
- over Z₆, which does not compose like cycles, the mod-2 and mod-3
  equivalences join to the total relation.

A proof of Conjecture 5's top lemma, together with a description of subdirect
products of simple algebras in such laws, would prove the weak conjecture.

**A possible route.** Tame congruence theory (Hobby and McKenzie 1988)
classifies the local behaviour of finite algebras into five types: unary,
affine, Boolean, lattice and semilattice.
- In the four non-affine types, the structure induced on a minimal set
  carries relations such as OR or a semilattice order, whose laws fail
  elimination.
- But that structure is reached through polynomial operations, which use
  constants, and laws here have none. A proof would have to close that gap.
- If composing like cycles excluded the four non-affine types, the minimal
  sets would be affine and the local structure linear. That is the shape
  Theorem 3 proves for groups.

This route is not attempted here.

## Remark (general Mal'tsev algebras)

Theorem 2 holds for every Mal'tsev law that composes like cycles. Its tops are
simple Mal'tsev algebras.
- By commutator theory (Freese and McKenzie 1987), abelian ones are affine
  over a simple module, and their subdirect products are linear over a finite
  field.
- Non-abelian ones give skew-free subdirect products.

So I expect Theorem 3's conclusion to hold for all such laws. That step is not
proved here.

## What this does not show

- **Laws without a difference operation.** The converse is not proved for
  them. Conjecture 5 is open.
- **General Mal'tsev algebras.** The Remark's extension is not proved.
- **Knots only.** For laws that compose only their knots like cycles, the free
  sets need not form a matroid. The question is not addressed.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` runs in about 80 seconds and writes `result.json`. All checks pass,
and all controls are rejected.

- **Proposition 1.**
  - The support relations of 200 random downsets have exactly those free sets.
  - Both Vámos relations have exactly the Vámos free sets, over all 256
    subsets.
  - Each relation's circuit projection has a direct case, and its two copies
    fail.
- **Theorem 2.** On 60 random subdirect products per group (S₃, D₅,
  AGL(1,5), Z₄, Z₉), fullness agrees with fullness of the top image.
- **Theorem 3.** On 60 random systems per group, the free sets are those of
  the direct sum of the per-prime GF(p) codes read from the top image. No
  non-abelian top occurs.
- **Corollary 4.** The Vámos matroid is connected, not binary and not ternary.
- **Proposition 6.** Consider every equivalence relation found among the binary
  projections of systems of at most two copies.
  - In the lift K₄, the shadow K₆ and x + y + z ≡ 0 over Z₉, every two proper
    ones have a proper join.
  - Over Z₆, two of them join to the total relation.
- **Census agreement.** A's Q1–Q3 hold.
- **Controls:**
  - "the top lemma holds without a unique maximal congruence", rejected by Z₆
    (whose subgroup x ≡ y (mod 2) has a full image mod 3 but is not full);
  - "a single relation's law composes like cycles", rejected by the Vámos
    support relation;
  - "a group-law system's matroid is read in one characteristic", rejected by
    an S₃ system with a sign-parity circuit and an A₃ circuit;
  - "every law has a unique maximal pp-definable equivalence", rejected by
    Z₆.
