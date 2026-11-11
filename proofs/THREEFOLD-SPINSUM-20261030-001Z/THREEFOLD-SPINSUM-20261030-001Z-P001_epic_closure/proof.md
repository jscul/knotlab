# Closure of the three-fold-spin-sum epic

Status: Proved

Ticket `THREEFOLD-SPINSUM-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/THREEFOLD-SPINSUM-20261030-001/the_knots_amplitude_as_a_spin_sum.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: the knot's spaces are its contradictions; the earlier text is in git history.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The knot's colouring counts #col(H) and #col(H − L) are 2^{−g} Σ_q (−1)^{Arf q} N_q over the spin structures of a minimal map. So non-colourability is the balance of even and odd spin sectors. | instance of the Arf invariant formula; the balance reading is new | A-P001, Theorem 3 |
| 2 | Of the 4^g Kasteleyn sign classes of a minimal map, the knot's is the only one that is not 2-colourable. | new | A-P001, Proposition 4 |
| 3 | Fano torus: sectors 8, 8, 8 \| 24 closed and 16, 16, 16 \| 28 with one contact opened, on every map and contact. The even sectors are the knot's own, and the amplitude is not carried by them. | new (exact computation) | A-P001, Proposition 5 |
| 4 | 13-point space: sector matrices over the two handles have rank 4, so the sectors do not factor over handles, though the amplitude does. | new (exact computation) | A-P001, Proposition 6 |

## Recommendation

**Continue**, as a fresh epic: where counting near-critical instances becomes hard (2/3).
- **The setting.** The knot's contradictions sit on Seymour's bound for minimally non-2-colourable hypergraphs.
- **The questions.** Is the count with one line removed polynomial-time on every such system? Does it become #P-hard off the bound?
- **Status.** Deferred to the owner. The decision note has the full assessment.
