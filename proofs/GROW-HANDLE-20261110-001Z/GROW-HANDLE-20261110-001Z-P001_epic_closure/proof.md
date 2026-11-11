# Closure of learning that grows a handle

Status: Proved

Ticket `GROW-HANDLE-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROW-HANDLE-20261110-001/grow_handle.md`; the pre-registration is
  `research/GROW-HANDLE-20261110-001/preregistration.md`.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A rotation-system-to-knot-pattern builder, checked on six patterns against their own rebuild. | tool; checked | A |
| 2 | Splicing a Fano piece at a knot of a knot sphere along one of three bijections gives a torus, and the old Kasteleyn law extends with no even face uniquely up to gauge. | known-with-delta; proved | A |
| 3 | On 540 grown tori (K_2 to K_5) the piece acts as the replaced knot in the grown class and is transparent in the other three, so the grown law is the only unsatisfiable class: growth alone does not remove the dissonance. | no prior-work search made; computed (theorem 2), proved given it (theorem 3) | A |
| 4 | Learning then resolves it, and every resolution changes a sign in the grown handle. | known-with-delta; proved | A |
| 5 | Grown at the dissonance, the violated knot moves into the piece and learning resolves it in 3 sign changes on K_2 to K_5; farther away it costs more. | computed | A |

## Answer

Yes: growth plus learning removes the dissonance a sphere forces, through the handle growth makes, most cheaply at the dissonance.

## Recommendation

**Continue:** choosing the resolution (backlog B62), next by the coordinator's order. The decision note gives the two tables.
