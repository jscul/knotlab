# Closure of full reach on honeycomb tori

Status: Proved

Ticket `HONEY-REACH-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/HONEY-REACH-20261109-001/honey_reach.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On the honeycomb torus of rule-60 rings with equally spaced contacts, three steps between contacts of one kind multiply by M = (1 + x)(1 + y/x)(1 + 1/y) over GF(2); a ring never needs another exactly when every power of M vanishes on a window of seven or six points. | known-with-delta; proved | A |
| 2 | Every power of M vanishes on the three mirror lines through a ring. | known-with-delta; proved | A |
| 3 | When 3 does not divide the side, the ring fixed by the turn of 120° about a ring never needs it, so composition never reaches every ring. | known-with-delta; proved | A |
| 4 | From side 7, the mirror lines pin no ring but that one. | proved | A |
| 5 | When 3 divides the side, every ring needs every ring, on every side from 3 to 300. | computed | A, stress test |
| 6 | When 3 does not divide n, each ring is never needed by exactly 2(N − 1)(N − 2) + 1 rings, N = 2^(v2(n) + 1) (2^(v2(n) − 1) for powers of two), on sides 3 to 300. | computed | A, stress test |

## Answer

Full reach on honeycomb tori fails whenever 3 does not divide the side, by proof, at the ring the turn of order 3 pins; it holds on every
side divisible by 3 to 300, by computation.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Recommendation

**Research directions**, none selected here: which lattices compose everywhere leads (Payoff 2/3, Concreteness 3/3). The table is in
the decision note.
