# The triple forms of the coupled blocks

Status: Proved

## Standard statement

**The family.** M_n = S³₃(K_n), where K_n is the closure of σ₁³σ₂³ ⋯ σ_{n−1}³ · Δ²_n: a chain of n − 1 trefoils with one full twist.
`UT3-INTERACT-PROBE-20261026-001` found that for n = 3m the obstruction bimap of G = UT₃(F₄) ⋊ C₃ has one inseparable block of
F₄-size 2m − 1, plus m − 1 singletons.

**Proposition 8.** For n = 6, 9, 12, the twisted triple product T of M_n (`TRIPLE-PRODUCT-20261026-001A`) has the following
structure.
- **(a) Splitting.** T = T_block ⊕ (m − 1 singletons μ ξ³). Here T_block is inseparable, of dimension d = 3, 5, 7.
- **(b) The Bockstein part.** On the block, the Bockstein map D: a ↦ T(a, a, ·) has rank d − 1, and the alternating part is
  nonzero.
  - D is additive and Frobenius-semilinear, D(λa) = λ²D(a). Under a change of basis P its matrix becomes P̄ᵀ D P, so its rank is
    an invariant.
- **(c) The counts.** The block counts are 𝒩 = 244, 8176, 367684, with the corank distributions recorded by the probe.
- **(d) Not a function of D.** In a fixed basis, keep the entries T(e_i, e_i, e_k), which transform among themselves, and change
  only the entries with three distinct indices.
  - For d = 3 the count is 784 when that entry is 0 and 244 when it is nonzero.
  - For d = 5 several values occur.

**Answer to the question asked.** "Identify the cubic forms of the coupled blocks; does their count have a closed form?"
- **The forms.** Each coupled block is a twisted Bockstein part of corank one, plus an alternating part.
- **The Bockstein part** is governed by the linking pairing of the 3-fold cover's eigenspace. Borromean moves cannot change it.
- **The alternating part** is free: Borromean moves change it at will (`TRIPLE-PRODUCT-20261026-001C`). The count depends on it.
- **The counts.** This family's counts are the counts of one particular alternating part. No closed form was found, and three
  values cannot determine a recurrence.
- **Closed forms are not the decisive question.** The class that the twisting makes reachable, D plus every alternating form,
  contains #P-hard instances (`TRIPLE-PRODUCT-20261026-001D`, with D = 0).

## Nearest known result

- **Bimap decomposition.** It uses the centroid (Wilson), as used in `UT3-INTERACT-PROBE-20261026-001`.
- **Bocksteins.** For mod-2 cohomology rings of 3-manifolds, x² ⌣ y is given by the linking pairing (Turaev's realization of
  (linking pairing, cohomology ring)). Our D is the twisted analogue.
- **Novelty: low.** These are exact computations on three manifolds of one family.

## 1. Method

1. **Recover T.** Recover the trace form tr T up to one F₄ scalar per block. This uses the symmetric, F₄-balanced, injective
   solution of `TRIPLE-PRODUCT-20261026-001A`, part 3 of the check.
2. **Convert to F₄.** Choose an F₄ basis e_i, with ωe_i computed on cocycles. Then T(e_i, e_j, e_k) = x₀ + x₁ω, where
   x₁ = tr T(e_i, e_j, e_k) and x₀ = tr T(e_i, e_j, ωe_k) + x₁.
3. **Split off singletons.** Repeatedly find a ≠ 0 whose kernel K(a) = {b : T(a, b, ·) = 0} has codimension one, satisfies
   V = F₄a ⊕ K(a), and has T(a, K(a), ·) = T(a, a, K(a)) = 0. Each such a spans a one-dimensional block.
4. **Read the parts.** D_{ik} = T(e_i, e_i, e_k), and the alternating entries are T(e_i, e_j, e_k) with i < j < k.
5. **Count.** 𝒩 = Σ_a 4^{corank T(a, ·, ·)} over the block, and 7 for each singleton.

## 2. Results

| n | dim V | singletons | block d | rank D | block count | corank distribution | total 𝒩 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 4 | 1 | 3 | 2 | 244 | {0: 24, 1: 39, 3: 1} | 1708 |
| 9 | 7 | 2 | 5 | 4 | 8176 | {0: 360, 1: 498, 2: 120, 3: 45, 5: 1} | 400624 |
| 12 | 10 | 3 | 7 | 6 | 367684 | {0: 4368, 1: 6765, 2: 3360, 3: 1470, 4: 336, 5: 84, 7: 1} | 126115612 |

In every case the total equals the block count times 7 for each singleton, and the singletons are trefoil-type cubes μξ³.

## Check

`check.py` uses the standard library and `tp_lib.py` from `TRIPLE-PRODUCT-20261026-001A-P001`, read-only. It runs in about 75 s;
results are in `result.json`. It recomputes the table and the control of (d):
- d = 3: alternating coefficient s ↦ count is {0: 784, 1: 244, 2: 244, 3: 244}.
- d = 5: zeroing the distinct-index entries, and eight random choices of them, give at least two different counts.

## Scope

- Exact computation on three manifolds of one family, n = 6, 9, 12. The n = 15 block (d = 9) is not identified here.
- The split into a Bockstein part and an alternating part depends on the basis, except for D up to semilinear congruence. So the
  specific numbers in (d) are for the computed bases.
- No closed form for the block counts is claimed or excluded.
- No complexity claim; no P versus NP claim.
