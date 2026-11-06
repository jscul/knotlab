# Blurring makes counts hard and keeps failures and composition

Status: Proved

Ticket `BEYOND-TWO-20261101-001B`, 2026-11-01.

## Question

- **What A left.** A found that the known cycle-composing laws are coset laws, so their counts are easy.
- **Where to look.** KNOT-CIRCUITS Theorem 1 asks only for a Mal'tsev algebra whose subalgebras have unique maximal congruences.
- **The question here.** On three or four values, is there a law that composes like cycles but counts hard, and so, in PINNING C's
  sense, both selects and composes?

## Dependencies

- **`BEYOND-TWO-20261101-001A`.** The known laws count easily; the control relation.
- **`KNOT-CIRCUITS-20261020-001B`.** Its definitions (range-relative constrained sets, circuits, knots, composing like cycles) and
  Theorem 1.
- **`SELECT-COUNT-20261101-001A`.** The exclusion on two values.

## Definitions

- **Blurring.** Let a law have domain D and let φ map D′ onto D. The *blurred law* replaces every relation R by its preimage
  φ⁻¹(R) ⊆ D′^k.
- **Blurred signed parity.** It lives on three values, with φ(0) = φ(1) = 0 and φ(2) = 1. Its relations are the preimages R₀ and R₁ of
  even and odd parity on three places.
- **Blurred signed Z3.** It lives on four values, with φ(0) = φ(1) = 0, φ(2) = 1 and φ(3) = 2. Its relations are the preimages R_c of
  x + y + z = c (mod 3), for c = 0, 1, 2.

## Theorem

1. **Blurring lemma.** A system over the blurred law and its image over the law (the same constraints) satisfy the following.
   - **Solutions.** The solution set of the blurred system is the preimage of the image's, coordinate by coordinate.
   - **Failure.** The blurred system fails iff its image does.
   - **Circuits.** A variable set is constrained (range-relative) in one iff in the other, so they have the same circuits. The blurred law
     composes like cycles iff the law does.
   - **Counts.** The blurred count is Σ over the image's solutions a of ∏_v |φ⁻¹(a_v)|.
2. **Every Mal'tsev law on three values composes like cycles.** A three-element Mal'tsev algebra has at most one nontrivial congruence,
   so every subalgebra has a unique maximal congruence, which is Theorem 1's condition.
3. **Blurred signed parity, on three values.**
   - **Mal'tsev.** It has a Mal'tsev polymorphism. Of the 1020 non-simple Mal'tsev operations on {0,1,2}, exactly the 48 whose quotient
     is affine preserve it.
   - **Composition and knots.** It composes like cycles, and its relations are knots.
   - **Failures.** It fails (R₀ and R₁ on one triple), and its failures are recognised by Gaussian elimination on the image.
   - **Counting.** Its count is #P-complete. The count matrix of R₀, with one variable counted, is
     [[2,2,1],[2,2,1],[1,1,2]], of rank 2, so the law is not strongly balanced (Dyer–Richerby).
   - **So** it has mutual selection in PINNING C's sense and composes like cycles. SELECT-COUNT A's exclusion holds exactly on two values.
4. **Blurred signed Z3, on four values.** The same holds in every respect; its count matrices have rank 3.

## Proof

**Item 1.**
- **Solutions.** Each constraint of the blurred system is the full preimage of its image's constraint, so a tuple satisfies the blurred
  system iff its image satisfies the image system.
- **Ranges and projections.** Projections commute with taking preimages, coordinate by coordinate. So the range of a variable and the
  projection onto Y are the preimages of the image's.
- **Constrained sets.** The preimage of a proper subset of ∏ range(v) is a proper subset of the preimage of the product, because every
  value has a non-empty preimage. So Y is constrained in one system iff in the other.
- **Counts.** These follow by summing the sizes of the preimages. ∎

**Item 2.**
- **At most one congruence.** Suppose a three-element Mal'tsev algebra had two nontrivial congruences θ₁ ≠ θ₂, each with blocks of
  sizes 2 and 1. Then θ₁ ∧ θ₂ = 0 and θ₁ ∨ θ₂ = 1. Congruences of a Mal'tsev algebra permute, so θ₁ ∘ θ₂ = 1, and the algebra is
  isomorphic to A/θ₁ × A/θ₂, which has four elements. That is a contradiction.
- **Unique maximal congruences.** So the congruence lattice is a chain, and its maximal congruence is unique. Two-element subalgebras
  are simple.
- **The theorem applies.** This holds for the full polymorphism algebra of any Mal'tsev law on three values, whose congruences are
  among those of a Mal'tsev operation it contains. Theorem 1 then applies. ∎

**Items 3 and 4.**
- **Mal'tsev.** The lift m(x, y, z) of x − y + z is a Mal'tsev polymorphism. It returns z if x = y and x if y = z, and otherwise the
  first preimage of φx − φy + φz. It preserves every preimage relation, because its image does.
- **Composition.** By item 1 and Theorem 1, the blurred laws compose like cycles, since parity and Z3 are affine over fields.
- **Failures.** By item 1, the failures are those of linear systems.
- **Counting.** The count matrix M[x, y] = #{z : R(x, y, z)} is the size of a preimage. It takes two values on a full support, with
  rank 2 (parity) or 3 (Z3). A strongly balanced law has every such matrix of rank one on each block of its support, so these laws are
  not strongly balanced, and their counts are #P-complete by Dyer and Richerby's dichotomy.
- **The direct reason.** The count of the blurred law is the image's solutions weighted by 2 per zero, which is a weight enumerator
  evaluated off the special points. ∎

**On two values.** A surjection between two-element sets is a bijection, so no Boolean law can be blurred. This is consistent with
SELECT-COUNT A.

## Checks

`check.py` (`result.json`, about 1 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | The blurring lemma on 240 random systems: failure, every constrained set, and the weighted count. | 240/240 (69 failing) |
| 2 | All 531441 Mal'tsev operations on {0,1,2}. | 530421 simple (1 affine); 1020 with one congruence; none with two; 48 with an affine quotient, exactly the 48 preserving blurred parity |
| 3 | Blurred signed parity: lift, knots, a failing system, recognition (150/150 against brute force), count matrices of rank 2 against parity's rank 1, circuit elimination (87 pairs, 0 violations). | pass |
| 4 | Blurred signed Z3: the same, with rank 3 against Z3's rank 1 and circuit elimination (1000 pairs, 0 violations). | pass |

## Reading

- **Selection in PINNING C's sense is cheap beyond two values.** Doubling a value hides a multiplicity that relations cannot see, so
  composition and failures are untouched. Counting sees it, so counts become hard. This is the counting layer of SELECT-COUNT B, now
  making a law hard to count.
- **The bridge found here is formal.** Blurred parity's failures are parity's, which PARITY-CORRECTION showed to be local: a failure can
  be grafted into any system. Whether any of these laws fails as the knot does (globally, on a structural class of substrates) is
  ticket C.

## What this does not establish

- **The counting complexity of the simple three-element Mal'tsev operations.** This is not classified, apart from the affine one (easy)
  and those preserving blurred parity (hard).
- **Global failures.** Whether the blurred laws' failures are global is ticket C.

## Novelty

- **Ours.** Theorem 1.
- **Classical.** Congruence permutability, and the Dyer–Richerby and Bulatov dichotomies.
- **New here.** The blurring lemma as stated, the enumeration of Mal'tsev operations on three values, and the formal bridge.
- **Folklore risk.** The bridge is moderate in folklore risk: blurring is the usual way to build non-balanced Mal'tsev examples.
