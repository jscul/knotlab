# Closure of a learner whose examples steer its search

Status: Proved

Ticket `STEER-LEARN-20261112-001Z`, 2026-11-12. Referee pending.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/STEER-LEARN-20261112-001/steer_learn.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | None of three steering rules finds the count faster than blind search over its rest set, every check charged; no steering shown. | computed, frozen | A |
| 2 | Every learner finds the swap target faster than blind search in the drawn setting: a bias of the walk, not of the examples. | computed, frozen | A |

## Answer

Steering at the probe does not let the examples steer this learner.

## Recommendation

**Research directions:** let the examples shape the dissonance the learner feels (B168), awaiting a go-ahead; B169 recorded.
