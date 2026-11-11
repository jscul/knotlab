# Closure of grow where learning is stuck

Status: Proved

Ticket `GROW-STUCK-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROW-STUCK-20261110-001/grow_stuck.md`.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The dissonance weight W = violated knots + E + \|D\|/2 is at least \|χ\|/2 in every state of every law. | reading of a known count; proved | A |
| 2 | From a sphere one Fano piece reaches floor 0, and each further piece adds one unit no learning removes. | proved | A |
| 3 | A learner that grows only when no sequence of at most r steps lowers W grows at the dissonance at once; with r ≥ 3 it grows once and resolves in 3 sign changes, with r ≤ 2 it overgrows and never resolves (K_2 to K_6). | computed | A |

## Answer

Yes, the learner can decide where to grow, and grows exactly once at the dissonance, if it sees three steps ahead.

## Recommendation

**Continue:** layers through pieces (sub-goal B54), next by the coordinator's order.
