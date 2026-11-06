# Closure of the twisted-triple-product epic

Status: Proved

Epic `TRIPLE-PRODUCT-20261026-001` closed on 2026-10-26.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/TRIPLE-PRODUCT-20261026-001/triple_line.md`.
- **The literature scan** is `research/TRIPLE-PRODUCT-20261026-001/scan.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For G = UT₃(F₄) ⋊ C₃, maps over a character ψ number \|Z¹(F₄_ω)\| · \|B¹(F₄_{ω²})\|² · 𝒩(T), where T is the twisted triple product and 𝒩(T) = #{(a, b) : T(a, b, ·) = 0} is a cubic character sum. With H₁ = Z/3, \|Hom\| = 1 + 128 · 4^d · 𝒩(T). | Routine (folklore risk high); the reading as one cubic form is the point | `TRIPLE-PRODUCT-20261026-001A-P001` |
| 2 | The coupled blocks of `UT3-INTERACT-PROBE-20261026-001` are a twisted Bockstein part of corank one plus an alternating part, with counts 244, 8176, 367684. The counts change with the alternating part, so no closed form follows from the twisting. | Exact computation (low novelty) | `TRIPLE-PRODUCT-20261026-001B-P001` |
| 3 | Y-surgery with leaves in ker ψ keeps H₁ and adds λ₁ ∧ λ₂ ∧ λ₃ to T. Every functional is a leaf, so every alternating perturbation is realizable, by Borromean moves on knots. | `candidate-local-delta`; folklore risk medium | `TRIPLE-PRODUCT-20261026-001C-P001` |
| 4 | Counting maps to G is #P-hard on 3-surgeries of knots, all with H₁ = Z/3. The alternating form Σ_{uv} (x_u + x_v) ∧ p_e ∧ s_e has kernel count 4^{2m−n} Z(64, 15), the Tutte polynomial at (79/15, 16). | `candidate-local-delta` (bounded-homology hardness for Fitting height 2; Potts formula for trilinear kernel counts); folklore risk medium | `TRIPLE-PRODUCT-20261026-001D-P001` |
| 5 | With bounded first homology, the line is not the Fitting height. It separates pairwise obstructions with bounded targets (SL(2,3), polynomial) from three-way twisted obstructions with a free alternating part (this group, hard). | Synthesis of 3, 4 and `SL23-BOUNDED-20261025-001A` | Decision note |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- **The line separates Fitting heights 2 and 3.** False.
- **Twisted central layers behave like untwisted ones under bounded homology.** False for this group.
- **A closed form for the coupled counts would decide the complexity.** Beside the point.
- **Realizable forms are constrained beyond the linking data.** False.

## Recommendation

**Continue.**
- **First:** an independent review of C and D, and a last pass on prior art phrased in TQFT terms.
- **Then:** an epic on coprime class-2-by-cyclic groups G = N ⋊ C_r. Conjecture: with bounded H₁, counting is #P-hard if and only
  if the commutator pairing is nonzero on two eigencharacters χ, χ′ with χ, χ′ and χχ′ all nontrivial.
- **Interest:** 3/3.
- **Alternatives:**
  - a short note (2/3; sharing is the owner's call);
  - approximate counting (1/3);
  - return to the core program through the Borromean bridge (2/3).
- **Execution:** deferred to the owner.
