# Closure of which knot patterns must be worked in order

Status: Proved

Ticket `SEQUENTIAL-WALL-20261116-001Z`, 2026-11-16. A ledger; it makes no new claim. The decision note is
`research/SEQUENTIAL-WALL-20261116-001/sequential_wall.md`. Refereed: `SEQUENTIAL-WALL-R1`, confirmed with fixes, no Block (commit
`c960effc1`); four wording corrections logged on 16 November.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Forcing in atom patterns is P-complete; of the 34 three-place knot laws 2 are AC0, 2 parity-L-complete, 14 P-complete, 16 NP-complete; not-all-equal propagation is P-complete with two held values. | known (applied); the gadget known-with-delta | B, A (gates) |
| 2 | A distinction's phase under the forcing law is the least Strahler number of its derivation trees; few phases without reuse; the wall needs reuse and several-way demand; a dual law decides patterns without cycles in min(P, P_dual) phases. | known and known-with-delta | B |
| 3 | On random atom patterns at the jump, rounds grow like n^0.30 and phases 0.57 per doubling (312 rounds against 12 phases at n = 2^20); unlayered random circuits need at most 4 phases, layered ones about d^0.41. | computed, frozen (9 of 13 held, 4 failed and read) | A |

**Recommendation:** Research directions, carrying open atoms (the owner's braid made exact), not started.
