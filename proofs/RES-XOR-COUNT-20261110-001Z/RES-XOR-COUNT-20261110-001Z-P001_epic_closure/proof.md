# Closure of Res(xor) beyond tree-like on the sphere's count

Status: Proved

Ticket `RES-XOR-COUNT-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RES-XOR-COUNT-20261110-001/res_xor_count.md`; the frozen transfer statement is
  `research/RES-XOR-COUNT-20261110-001/transfer_statement.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Braun's generic criterion certifies at most exp(d^2/(6v)) nodes for a system with a polynomial-calculus refutation of degree d <= 2v/3; on the sphere's count, of degree O(sqrt n), only a constant. | new as far as found; proved | A |
| 2 | Carrying Braun's bit-PHP bound to the count needs a reduction from PIGEON with each point one parity; none by ordinary decision trees exists (PPP^dt not in PPADS^dt) and none by parities is known. | routine; proved (from Beame et al.) | A |
| 3 | No stifling gadget is affine, so lifted sources reach the count only through non-affine points; the count's xor-lift is the count again. | routine; proved | A |

## Answer

No published Res(xor) bound beyond tree-like reaches the count by any route of the frozen statement; the epic moves to cutting planes
(B82).

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`; whether to share `BPHP-MORE-PIGEONS-NOTE-20261019-001` with Braun.

## Recommendation

**Research directions**: cutting planes (B82) taken next under the coordinator's standing instruction. The table is in the decision note.
