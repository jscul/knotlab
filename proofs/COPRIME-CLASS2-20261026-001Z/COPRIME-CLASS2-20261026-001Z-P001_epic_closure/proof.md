# Closure of the coprime class-2 epic

Status: Proved

Epic `COPRIME-CLASS2-20261026-001` closed on 2026-10-26.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/COPRIME-CLASS2-20261026-001/class2_line.md`.
- **The literature scan** is `research/COPRIME-CLASS2-20261026-001/scan.md`, with the prior-art pass in A's review note.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The independent review found no blocking gap in the twisted-triple-product hardness. Two repairs (the explicit construction; "bounded H₁ is not enough" instead of a refutation of Samperton–Weiß) and nine clarifications are recorded. Moussard 2017 is the precursor of the steering formula. | Review | `COPRIME-CLASS2-20261026-001A` (documentation) |
| 2 | For H(F_q) ⋊ C_r, the count is a kernel count of the eigen-triple form on V_α × V_β × V_{(αβ)⁻¹}. Y-surgery with leaves in ker ψ changes every eigen-component by ε Σ_σ sgn(σ) Π (leaf functionals). Over prime fields, every form of the allowed symmetry type is realizable. | Finite-cover analogue of Moussard. Folklore risk medium to high | `COPRIME-CLASS2-20261026-001B-P001` |
| 3 | Coprime class-2 groups without a hard pair are polynomial with bounded H₁, and on knot groups. | `candidate-local-delta`. Folklore risk medium | `COPRIME-CLASS2-20261026-001C-P001` |
| 4 | Heisenberg-by-cyclic groups over odd prime fields with a hard pair are #P-hard on r-surgeries of knots and on knot groups. With 3, this is a dichotomy for the family. | Candidate new. Folklore risk medium | `COPRIME-CLASS2-20261026-001D-P001` |
| 5 | Rowell's Conjecture 3.2(b) (2009), exact polynomial counting on link groups for solvable G, fails for S₄, UT₃(F₄) ⋊ C₃ and these Heisenberg groups, unless every #P function is computable in polynomial time. | Candidate new as an observation. External confirmation needed | `COPRIME-CLASS2-20261026-001D-P001` Corollary 5; `BOUNDED-H1-20261025-001A`; `SL23-BOUNDED-20261025-001B` |

## Challenged assumptions

The decision note records four:
- **The steering formula is new.** Corrected: Moussard is the precursor.
- **The hardness answers Samperton–Weiß's twisted question.** Withdrawn.
- **The S₄ knot result is "only" bounded-homology hardness.** Understated: it contradicts Rowell's conjecture.
- **The steering change is r·det.** Corrected to ±det.

## Recommendation

**Continue, as result conversion.**
- **The note.** "Counting homomorphisms from knot groups to solvable groups can be #P-hard", covering S₄, UT₃(F₄) ⋊ C₃ and the
  Heisenberg dichotomy, with a #BIS remark on Rowell's part (a). Prepare an external-review package.
- **Interest:** 3/3.
- **Alternatives:**
  - general class-2 hardness (2/3);
  - approximate counting (2/3);
  - return to the core program through the Borromean bridge (2/3).
- **Execution:** deferred to the owner. Sharing anything is the owner's call.
