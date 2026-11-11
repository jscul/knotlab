# Closure of what a drawn knot pattern needs to compute parity

Status: Proved

Ticket `PARITY-NEEDS-20261111-001Z`, 2026-11-11.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PARITY-NEEDS-20261111-001/parity_needs.md`.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, an atom a piece and a world of knots a pattern (Intuitions guide, Glossary). The
mathematics is unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The 8-distinction genus-4 parity gadget is a valid drawn knot pattern and its parity relation a K1-K3 knot, by an independent check. | independent check | A |
| 2 | The least genus with three-input parity is 1: the 8-point lattice torus (2,0,4) in its most constrained class computes it; 16 of 281 lattice tori do. | exhaustive computation | A |
| 3 | No planar disk parity gadget unless P = NP. | proved by hand | note |

## Answer

One handle is enough for a drawn knot pattern to count three held distinctions.

## Recommendation

**Research directions:** a learned memory that computes parity (sub-goal B146), awaiting a go-ahead.
