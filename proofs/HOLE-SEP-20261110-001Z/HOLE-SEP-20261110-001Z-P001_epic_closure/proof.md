# Closure of hole-row separation for bit LeftPigeon

Status: Proved

Ticket `HOLE-SEP-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/HOLE-SEP-20261110-001/hole_sep.md`; the frozen statement is
  `research/HOLE-SEP-20261110-001/separation_statement.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For bit LeftPigeon with 2lB - 1 <= n, a row-linear polynomial derived in PC degree B lies in the kernel K_k of the reduced decoder modulo Braun's unary degree-k ideal, so separation is a static kernel question. | new as far as found; proved (from Braun's lemmas) | A |
| 2 | The (l + 1)^2 inverse-counting identities lie in K_1 for every n and span it at n = 4, 8, 16 (32 in the stress test). | new as far as found; proved and computed (pre-registered) | A, B |
| 3 | At degree 2 the kernel is 73%, 49%, 32% of L_2 at n = 4, 8, 16, tracking (l + 1)^2 k / v; prediction P2 refuted; stop rule (b) triggered, its reading corrected (a kernel bounded away from all of L_k costs only a constant factor). | computed (pre-registered) | B |

## Answer

Hole-row separation is reduced to bounding one kernel, which is not zero; the route stops by its frozen rule, and the corrected question
is recorded.

## Pending the owner

- None new.
- Carried: as in `SEP-LEFT-20261110-001`.

## Recommendation

**Continue** with the kernel bound, for the coordinator to confirm. The table is in the decision note.
