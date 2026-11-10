# Interpretation: a growing plane that reads distance 1, then 2

Run of the frozen contract `READ-GROW-20261110-001A-E001` (exploratory, nearly blind: one smoke test disclosed), 2026-11-10, launch
`read-grow-a1`. Parts C, S and V finished in 39 minutes; part X (one size past, 80 × 80, both codes) runs on in the background as
READ-GROW-A1 and is folded into the decision note when it finishes. Readings exact.

## The outcomes

| Outcome | Verdict | Evidence |
| --- | --- | --- |
| C: code 1 and code 2 agree | **Yes**, on all eleven schedules (3 × 3 and 5 × 5, g = 2 and 3): balance at each doubling, first failure lag, every first hearing lag | `C.json` |
| O1: every stage balanced through 40 × 40, distance 1 heard strictly before distance 2 | **Met by five schedules**: [12, 28], [28, 1], [28, 2], [35, 1], [43, 1] (of 23 two-run schedules with every stage balanced) | `S.json` |
| V: the first two O1 schedules on the full state and by code 2, at 40 × 40 | **Agree**: [12, 28] and [28, 1] balanced at every doubling under `readings()`; code 2 gives the same balance and the same hearing lags | `V.json` |
| O2: distance 2 first heard after more doublings than distance 1 | **Met by [12, 28]**: distance 1 at lag 8, in the first run; distance 2 at lags 23 and 32, in the second, after the doubling at lag 12 | `S.json` |
| O3: a metric reading the lattice distance | **Not met**: in no balanced schedule is every original ring heard; the four at distance 4 never are | `S.json` |

The contract's rule: B89's first step succeeds (O1 with V agreeing); its confirmation one size past waits for part X.

## The hearing lags

- **In one pause the plane reads taxicab distance.** [35, 1] and [43, 1] hear every ring at distance 1, 2 and 3 during their first run,
  at lags 8, 20 and 32: constant on each taxicab class and L = 12|v| − 4. Distance 4 would come at lag 44 by that law, and no first run
  of 44 to 48 lags keeps the second stage balanced (of 36 to 48, only 43 does). [28, 1] and [28, 2] hear distance 1 and 2 (lags 8, 20).
- **After a doubling the reading is no longer taxicab.** In [12, 28] the second run, after the doubling at lag 12, hears the four
  diagonal rings (1, ±1), (−1, ±1) at lag 23 and the four straight rings (±2, 0), (0, ±2) at lag 32: two lags in one taxicab class, the
  diagonal first.
- **Not a metric as they stand.** Where defined, the lags are symmetric, but they break the triangle inequality: L(2, 0) = 20 > L(1, 0)
  + L(1, 0) = 16 (the offset −4). L + 4 is subadditive on the heard rings of [35, 1] (12 times taxicab); that is a post-hoc reading,
  not a frozen outcome.

## Sizes

Every stage of the five O1 schedules is balanced at 10 × 10, 20 × 20 and 40 × 40 (two confirmed on the full state). Nothing larger is
known before part X; balance at every size is open.

## Nonclaims

- The 5 × 5 tube, g = 3, the frozen ranges; balance computed, not proved; plain dependence; declared rings (A45) on a declared board
  (A51); open births (A44); the schedules declared, found by search.

## Part X, folded in

Part X finished at 7,627 seconds of the run (`X.json`); code 1 and code 2 agree on all eight extensions (balance at every doubling,
first failures, hearing lags). Through 80 × 80: [28, 1, 1], [28, 1, 2] and [35, 1, 1] keep every stage balanced; [35, 1, 2], [28, 2, 1],
[28, 2, 2], [12, 28, 1] and [12, 28, 2] fail at 80 × 80. The contract's rule: the first step is confirmed one size past, by [28, 1] and
[35, 1]; [12, 28], the one schedule meeting O2, is not, so reading distance across a doubling is known only to 40 × 40.
