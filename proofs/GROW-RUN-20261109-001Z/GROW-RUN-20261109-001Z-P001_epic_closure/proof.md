# Closure of growth while running

Status: Proved

Ticket `GROW-RUN-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROW-RUN-20261109-001/grow_run.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A band inserted while the tube runs leaves every ring it has not reached intact: every contact keeps binding it at every lag. | known-with-delta; proved | A (Theorem 1) |
| 2 | Every contact binds the band's rings at every lag; an insertion at lag 0 is the next stage. | known-with-delta; proved | A (Theorem 2) |
| 3 | 68% of the bindings of reached rings fail; over every insertion lag of 13 tubes only lag 0 keeps every contact persistent in every case (42 to 64 of 634 lags overall). | new as far as found; computed, exact over every lag | A (checks 2, 3), stress test |
| 4 | The failing contacts spread from the band at the time length of a row. | computed | A (check 4), stress test |
| 5 | With a band every P lags only the newest band keeps every binding. | computed | A (check 6), stress test |

## Answer

Growth while running breaks persistence quickly and causally: intact outside the insertion's reach, mostly lapsed inside it. The band
law's balance is a property of growth between runs (A42, confirmed for stated reasons).

## Recommendation

**Research directions**, selected #1, growth chosen by the dynamics where influence has not arrived (B23, the coordinator's fallback).
The table is in the decision note.
