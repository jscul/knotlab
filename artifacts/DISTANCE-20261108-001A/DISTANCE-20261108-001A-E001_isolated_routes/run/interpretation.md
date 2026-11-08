# Counted length along isolated routes: interpretation

Experiment `DISTANCE-20261108-001A-E001` (exploratory), the frozen test of A40, pre-registered in the register on 2026-11-08 (commit
510ff23fc) before it ran, with its contract, `run.py` and `distance_lib.py` fixed by sha256 there. Run once under the frozen contract,
in under a second on 16 workers. Totals and every failure (none) are in `result.json`.

## Control

The theory named in the contract: a chordless route isolated by freezing carries one walk of L arcs and none shorter
(`LOOP-NET-20261108-001A`, Theorem 1; `LATTICE-NET-20261108-001A`, Theorem 1). The test reads the lag from the cells, by rows of M^T,
not from walks.

## Primary observable

| Part | Routes or splits | Passed |
| --- | --- | --- |
| (a) affinity: first lag g·L + 1 | 2,250 routes on 17 networks, spacings 2, 3, 4, lengths 1 to 10 | 2,250 |
| (b) additivity: (t_P − 1) + (t_Q − 1) = t − 1 | 7,285 splits (1,139 skipped by the declared rule) | 7,285 |
| (c) cells, at unequal spacing 2 to 5 | 372 routes on the square torus of side 5 and the genus-2 network of 16 rings, four replicates each | 372 |

Every length from 1 to 10 had routes on every network except the small Platonic ones (the tetrahedron has none longer than 3 arcs, the
cube and octahedron none longer than 7). No network on the roster has two corners between the same two contacts.

## Reading against the decision rule

- **A40 is Confirmed** by the frozen rule: (a), (b) and (c) all pass. Along a route isolated by freezing, the substrate makes the far
  contact first need the near ring g·L + 1 lags after the start, g fixed by the spacing and independent of L and of the route's shape,
  and these lags add when routes are joined.
- **What the substrate counts is cells.** At unequal spacing the first lag is 1 plus the cells the route carries, so counted length in
  contacts is the same reading exactly where contacts are equally spaced.

## Nonclaims

- **Exploratory and finite:** the roster only. The proof for every network is Theorem 1 of `DISTANCE-20261108-001B`.
- **Isolated routes only.** In the full network the plain first need is filtered by the parity of shortest routes
  (`DISTANCE-20261108-001B`, Theorem 4).
- **Two-time knots only** (A30).
