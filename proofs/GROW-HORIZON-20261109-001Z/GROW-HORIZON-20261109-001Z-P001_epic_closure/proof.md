# Closure of distance and balls in the doubling network

Status: Proved

Ticket `GROW-HORIZON-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROW-HORIZON-20261109-001/grow_horizon.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Doubling every lag isolates every ring: no ring ever hears another, and a contact needs only its two rings. | known-with-delta; proved | A (theorem) |
| 2 | Doubling every P lags confines each original ring's reach below 0.8 to 2.4 original spacings (P = 2 to 8): a horizon. | computed, exact to four doublings | A (check 2) |
| 3 | Inside the horizon the contacts needing a ring grow about fourfold per doubling. | computed | A (check 2) |
| 4 | Correction: `GROW-ALL-20261109-001`'s plane reads no distance while it doubles every lag (Not a block). | correction | A (theorem) |

## Answer

The doubling network has a horizon, zero at every-lag doubling.

## Recommendation

**Research directions**, #1 (B50) as ordered. The table is in the decision note.
