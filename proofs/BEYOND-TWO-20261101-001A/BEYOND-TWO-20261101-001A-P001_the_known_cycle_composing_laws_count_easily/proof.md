# The known cycle-composing laws count easily

Status: Proved

Ticket `BEYOND-TWO-20261101-001A`, 2026-11-01.

## Question

- **What is already known.** SELECT-COUNT A showed that no Boolean law with a knot both selects its spaces (mutual selection) and
  composes its knots like cycles.
- **The search.** Beyond two values, look for a law that is Mal'tsev, composes like cycles and counts hard.
- **The first check (as approved).** Do the laws already known to compose like cycles count hard?

## Dependencies

- **`KNOT-CIRCUITS-20261020-001B`.** Theorem 1: a Mal'tsev law composes like cycles iff every subalgebra of its polymorphism algebra
  with at least two elements has a unique maximal congruence. It names its examples: affine laws over finite fields, and the coset laws
  of Z_(p^k), S3 and D_p (yes), and of Z6, Z2 × Z2, A4, D4, Q8, Dic3 and Z12 (no).
- **`SELECT-COUNT-20261101-001A`.** The exclusion on two values.
- **`PINNING-20261031-001C`.** Mutual selection: (M1) failures non-empty and recognisable in polynomial time, and (M2) the count #P-hard
  in general.

## Theorem

1. **Coset laws are strongly balanced.** Let G be a finite group and let every relation of the law be a coset aK of a subgroup K of a
   power G^k.
   - The solution set of every system, and every projection of it, is empty or a coset.
   - All non-empty fibres of a projection of a coset have the same size.
   - So every count matrix of the law is constant on the blocks of its support. The law is strongly balanced, and its count is
     computable in polynomial time (Dyer–Richerby, SIAM J. Comput. 2013).
   - Affine laws over a finite field are the special case of cosets of subspaces.
2. **The known cycle-composing laws count easily.** Every law that Theorem 1's examples show to compose like cycles is a coset law, so
   its count is polynomial. None of them has mutual selection.

**Remark.** Theorem 1 does not need cosets: any Mal'tsev algebra whose subalgebras have unique maximal congruences composes like
cycles. That is where the search continues (ticket B).

## Proof

**Item 1.**
- **Systems.** A relation on some of the n variables is a cylinder, which is a coset of K × G^(rest) in G^n. An intersection of cosets is
  empty or a coset of the intersection of the subgroups. So a system's solution set is empty or a coset aK.
- **Projections.** The projection π(aK) = π(a)π(K) is a coset.
- **Fibres.** The fibre over π(ak₀) is a k₀(K ∩ ker π), whose size |K ∩ ker π| does not depend on the point.
- **Count matrices.** A count matrix M[x̄, ȳ] = #{z̄ : R(x̄, ȳ, z̄)}, for a relation R defined by a system, is a fibre size of a
  projection of the coset R. So it is constant on its support. Its support is a coset, hence rectangular: a disjoint union of blocks.
  Every such matrix is block rank one, which is strong balance. ∎

**Item 2.**
- **Fields.** Affine laws over fields are coset laws of their additive groups.
- **Groups.** The coset laws of Z_(p^k), S3 and D_p are coset laws by definition. ∎

## Checks

`check.py` (`result.json`, under a second):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Theorem 1's criterion, computed on every subalgebra. Z3, Z4, GF(4) (with the operation ωx + ω²y) and S3 have one maximal congruence in every subalgebra; Z2 × Z2 has three. | 4 yes, 1 no, as KNOT-CIRCUITS |
| 2 | Uniform fibres on 40 random coset systems over each of Z3, Z4, GF(4) and S3, with four variables and every projection. | 1428 projections, all uniform |
| 3 | Control: a blurred relation (ticket B) has fibres of sizes 1 and 2. | pass |

## Reading

- **The first check is negative, as expected.** The laws known to compose like cycles are linear in the group sense, and linearity makes
  every fibre the same size, so counting is easy.
- **Where to look next.** A bridge needs a Mal'tsev law that composes like cycles without being a coset law, so that its fibres can
  differ in size. Ticket B finds such laws.

## Novelty

- **Classical.** Uniform fibres of cosets and the Dyer–Richerby dichotomy.
- **Ours.** Theorem 1.
- **New here.** Only the use of these as the first check.
