# Closure of the full-dichotomy epic

Status: Proved

Epic `DICHOTOMY-3D-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/DICHOTOMY-3D-20261025-001/full_dichotomy.md`, and the literature finding is in
`research/DICHOTOMY-3D-20261025-001/scan.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Dehn-filling parallel copies of the edge curves of the closed doubles by p-th roots (slopes λμ^(−p), λμ^p) multiplies each anyon channel by \|Σ_{τ^p = λ} ψ(τ)\|²/ψ(1)². For the order-16 dihedral group this kills the reflection channels, so the collision 256 · 16 = 64² disappears and the top coefficient is 4^m·8·P(G, 4)/2^\|V\|. | `candidate-local-delta`; folklore risk medium | `DICHOTOMY-3D-20261025-001A-P001` |
| 2 | Index-p theorem: for an abelian normal A of prime index p acting nontrivially on pA, the top coefficient is \|A[p]\|^{2m}\|Γ:pA\|\|A[p]\|(\|L′\|/\|A\|)ⁿ P(G, \|[pA, σ]\|²). The trivial-action cases give (\|Z\|/\|Γ′\|)ⁿ P(G, \|Γ:Z\|\|Γ′\|) or, for p ≥ 3, \|A\|ⁿ P(G, p). This covers every 2-power dihedral, semidihedral and generalized quaternion group of order ≥ 16. | `candidate-local-delta` as explicit identities; the hardness is not new | `…001A-P001` |
| 3 | The full dichotomy, that counting homomorphisms from closed triangulated 3-manifold groups is #P-hard exactly for non-abelian groups, already follows from Galindo's Turaev–Viro dichotomy (arXiv 2605.06984, May/June 2026) applied to Vec_Γ. This predates `HARD-3D-20261025-001`, whose claims to settle S₃ and to show the bounded-H² hypothesis necessary are therefore not new. | Literature finding (cited, not proved here) | `scan.md` |

## Challenged assumptions

The decision note records three workspace assumptions that this epic challenges:
- **S₃ and the order-16 dihedral group were open in late 2026.** False: Galindo, May 2026.
- **Fins alone cannot reach the order-16 group, so new instances are needed.** Partly false: root fillings on the same doubles suffice.
- **A scan of the named open problem suffices.** False here. The decisive result was phrased for quantum invariants.

## Recommendation

**Full pivot**, from hardness with growing homology to bounded first homology.
- **The question.** Is counting maps into S₄, of derived length 3, #P-hard on closed 3-manifolds whose H₁ has bounded order, while
  every metabelian target is polynomial there?
- **Interest:** 2/3.
- **Alternatives:**
  - return to the program's core intuitions (1/3);
  - approximate counting for solvable targets (1/3);
  - a companion note with the explicit colouring identities (1/3).
- **Execution:** deferred to the owner.
