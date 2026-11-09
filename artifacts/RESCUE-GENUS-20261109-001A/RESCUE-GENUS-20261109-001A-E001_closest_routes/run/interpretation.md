# How on-time maps of higher genus reach their rings: interpretation

Experiment `RESCUE-GENUS-20261109-001A-E001` (exploratory), run once on 2026-11-09 under the frozen contract (pre-registered in
dee5004a4), in 1,754 s on 16 workers. Exact: distances and shortest-route counts by breadth-first search from one target contact. Every
row is in `result.json`.

## Control

The seen roster reproduces `PLAIN-TIME-20261108-001A-E001`: 706 distinct regular maps of genus at least 2, 141 on time.

## Primary observable

| Roster | Maps of genus ≥ 2 | On time | On-time ring–target pairs: every closest contact by one route | One by one route, another tied | Only tied closest contacts, odd |
| --- | --- | --- | --- | --- | --- |
| Seen (23 groups, the pilot) | 706 | 141 | 23,187 | 679 (82 maps) | 2 (one map) |
| New (PSL(2,31), PSL(2,37), PGL(2,17), PGL(2,19), SL(2,11), GL(2,7), S7) | 1,056 | 77 | 28,519 | 603 (49 maps) | 0 |

- **H1 holds on the new roster, with no counterexample.** In every one of the 77 on-time maps, every ring has, for the target, a closest
  contact reached by a single shortest route. On the seen roster the one exception is the map of S6 of type (6, 6), genus 61 and 120
  rings, where two rings have closest contacts reached by 2, 2 and 3 routes.
- **H2 holds, vacuously on the new roster.** No late map has its diameter within two of its first tie; on the new roster no map does at
  all, so H2 was not tested there.

## Reading against the decision rule

H1 holds: the rescue on higher genus is the tori's mechanism. A map of higher genus reads distance plainly when every ring keeps a
fastest way to every contact that is a single route; odd counts of several routes rescue a ring only in the one map of S6. H2 adds
nothing out of sample.

## Deviations, recorded

- **Time.** The run took 29 minutes, inside the contract's 30-minute budget but over the ten minutes after which a check is registered in
  `docs/LONG_RUNNING.md`; it is registered there after the fact, as folded in.

## Nonclaims

- **Exploratory and finite:** the rosters only; orientably regular maps only.
- **Two-time knots only** (A30).
