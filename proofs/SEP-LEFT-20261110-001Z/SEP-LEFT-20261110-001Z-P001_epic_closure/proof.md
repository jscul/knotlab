# Closure of bit LeftPigeon as Braun's second family

Status: Proved

Ticket `SEP-LEFT-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SEP-LEFT-20261110-001/sep_left.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Braun's generic criterion applies to bit LeftPigeon with its own clauses: if its row-linear space over all rows is separated at degree k(12l + 2), dag-like Res(xor) refutations have 3S + n(n + 1)(l + 1) >= exp(k^2/(3n) - 2). | new as far as found; proved (from Braun's theorems) | A |
| 2 | Pigeon-row separation transfers from bit PHP by the substitution g(h) := sum_x [f_x = h] x, at l times the degree, but the pigeon rows alone are too thin for the criterion; the hole sums lie in the substitution's kernel. | new as far as found; proved | A |
| 3 | On n = 2, 4, 8 holes bit LeftPigeon's row-linear spaces over all rows stay separated at least as far as bit PHP's, and the reach grows from n = 4 to 8 (density that grows by the frozen rule). | new as numbers; computed (pre-registered, exact) | B |

## Answer

B100 reduces to one statement, hole-row separation, which every computable instance supports.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`; whether to share `BPHP-MORE-PIGEONS-NOTE-20261019-001` with Braun.

## Recommendation

**Continue** with hole-row separation (sub-goal B103), for the coordinator to confirm. The table is in the decision note.
