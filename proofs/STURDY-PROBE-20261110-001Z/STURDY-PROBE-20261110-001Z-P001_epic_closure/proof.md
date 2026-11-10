# Closure of a probe that is not fooled

Status: Proved

Ticket `STURDY-PROBE-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/STURDY-PROBE-20261110-001/sturdy_probe.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | With each negative check four 25,000-step walks, the example learner made no inexact stop and no 0001 stop in 156 writes and 39 runs, at 2.5 times the old probe's walk steps. | computed, frozen | A |
| 2 | With it, the fixed learner learned 56 of 56 leaf and 10 of 16 composite writes and the credit learner all 84 of its writes. | computed, frozen | A |

## Answer

The probe's false acceptances are removed, and with them the credit learner learns every gate through composites.

## Recommendation

**Research directions:** three held inputs (backlog B133), awaiting a go-ahead.
