# Closure of a learned network that computes

Status: Proved

Ticket `GATES-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GATES-20261110-001/gates.md`.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Cuts read AND; an unsatisfiable component forces the reading to 1, so nothing 0 where both stored bits are 1 is read; a cut leaf read from outside is never negated. | proved by hand | A |
| 2 | 43,091 networks in five frozen families read AND, OR, single bits and constants, never NOT a_1 (P4 failed); names read the parity of a leaf's class bits (post hoc). | exhaustive computation | A |

## Answer

Not in the families tried: monotone readings of the acting bits only.

## Recommendation

**Research directions:** reading the class, not the bit (backlog B122), awaiting a go-ahead.
