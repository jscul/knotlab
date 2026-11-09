# Closure of why doubling keeps every stage balanced

Status: Proved

Ticket `DOUBLE-BALANCE-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/DOUBLE-BALANCE-20261109-001/double_balance.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | If no cell outside a ring holds its born cells and its own cells hold them independently, contacts bind it exactly as in the static stage. | known-with-delta; proved | A (lemma) |
| 2 | Doubling every lag keeps every stage balanced at every lag. | known-with-delta; proved | A (theorem) |
| 3 | Doubling every 2, 4, 6 or 8 lags breaks isolation and balance by 24 × 24; every 3 lags keeps both. | computed, exact | A (check 3) |

## Answer

The doubling law keeps its knots by isolating its rings; slower doubling lets rings hear each other and loses balance.

## Recommendation

**Research directions**, #1: another birth rule. The table is in the decision note.
