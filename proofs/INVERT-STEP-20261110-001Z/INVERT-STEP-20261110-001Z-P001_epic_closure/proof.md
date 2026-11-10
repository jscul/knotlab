# Closure of growth on an invertible substrate

Status: Proved

Ticket `INVERT-STEP-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/INVERT-STEP-20261110-001/invert_step.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On a finite network an injective step has finite order, at which every contact is its own first value: no contact persists. | known-with-delta; proved | A (theorem) |
| 2 | In a finite network with a persistent contact no row after the first is open. | known-with-delta; proved | A (Corollary 1) |
| 3 | No finite substrate has an invertible step and a persistent contact; checked on 256 linear substrates, first and second order, on five tubes. | proved; checked | A (Corollary 2, checks 1 to 3) |
| 4 | `DOUBLE-BALANCE-20261109-001A`'s invertible map is the own cells' evolution, not the step, which forgets. | proved; checked | A (remark, check 4) |

## Answer

Persistence needs forgetting: B39 has no substrate on a finite network.

## Recommendation

**Research directions**, the proof pair B55 and B64.
