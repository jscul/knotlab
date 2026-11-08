# Chains of three rings: interpretation

Experiment `PROCESS-CHAIN-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 5,632 chains in 120 s on 16
workers. 53 of them did not repeat within 4,096 lags and are counted apart. Every other verdict is exact at every lag. Rows are in
`rows.json`, totals in `result.json`.

## Controls

Both pass.
- **The light cone.** No binding of the end rings is ever claimed before the light-cone lag d + 1 (ticket A's Theorem 2).
- **Completeness.** Every configuration has its verdicts or is reported undecided.

## Primary observable

| Chain (A/B/C cells) | Decided | Both contacts persist | Of those, c2 binds the ends from d + 1 | Ends bound at c2 at all |
| --- | --- | --- | --- | --- |
| 3/4/3 | 1,408 | 30 | 0 | 0 |
| 4/4/4 | 1,408 | 42 | 0 | 2 |
| 4/6/4 | 1,394 | 46 | 0 | 0 |
| 5/6/5 | 1,369 | 64 | 0 | 0 |

- **H1 fails completely.** In all 182 chains where both contacts persist, neither contact binds the two end rings at every lag from
  d + 1 on. In the whole census the ends are bound at c2 in two chains, both on 4/4/4 cells, and in neither do both contacts persist.
- **The families.** 176 of the 182 persistent chains are self-blind and 6 are proposal parities.

## Why the persistent chains do not compose

Each of the 182 chains was replayed to its repeat, recording whether c2 depends on ring A at each lag.
- **Rings that read no neighbour (112).** Rules 51 and 204 never read their neighbours, so the middle ring never reads c1 and the
  chain is effectively listening (ticket A's Theorem 1).
- **The far ring never reaches c2 (62).** Its influence is blocked or cancelled on the way.
  - **Blocked.** Rule 60 reads only its left neighbour, so with a contact law that reads only one side, the flow from c1 stops one
    cell short of c2.
  - **Cancelled.** With the contacts opposite each other on the middle ring, linear rules such as 150 and 105 at 4/4/4 and 90 at
    5/6/5 carry c1's influence both ways round in equal time, and the two arrivals cancel.
- **It reaches c2 and then fades (4).** Rule 90 at 5/6/5 with self-blind laws: c2 depends on ring A at lags 4 to 7, where nothing
  outside ring A fixes it, and then no more.
- **It reaches c2 and stays, but can be overridden (4).** Rule 77 at 5/6/5: c2 depends on ring A at every lag from 4 on, but some
  setting of the other cells always makes ring A irrelevant.

## Reading against the decision rule

- **Persistence and transmission did not coexist.** In every chain where both contacts persist, ring A's influence at c2 is absent,
  fades, or can be overridden. The two chains whose ends are bound at c2 do not keep both contacts.
- **Opposite contacts favour cancellation.** All contacts here sit opposite each other on the middle ring, so the two ways round
  have equal length. The stress test moves them off the opposite point and adds a size.

## Nonclaims

- **Declared chains only.** All three rings on one rule, the same law at both contacts, the contacts opposite on the middle ring.
- **Undecided chains.** 53 are counted apart.
- **Two-time knots only** (A30).
