# Closure of the sphere's count in stronger proof systems

Status: Proved

Ticket `COUNT-SYSTEMS-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/COUNT-SYSTEMS-20261110-001/count_systems.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every depth-d Frege refutation of the sphere's NAE formula has size exp(n^{eps_d}), through LeftPigeon, SINK and grid Sperner and the pigeonhole lower bounds. | known-with-delta (close to Dantchev 2006 for Sperner); proved | A |
| 2 | Over corner atoms (2-XORs of points) cutting planes refutes the count in O(n) lines. | known-with-delta; proved | B |
| 3 | Every corner parity holds under every assignment; the contradiction is an integer count invisible modulo 2; the point LP is feasible at x = 1/2. | known-with-delta; proved | B |

## Answer

Bounded-depth Frege needs exponential size on the count; Res(xor) and cutting planes stay open, each having only one of the count's two
ingredients, the corner parities and the integer count.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Recommendation

**Research directions**, none selected, for the coordinator. The table is in the decision note.
