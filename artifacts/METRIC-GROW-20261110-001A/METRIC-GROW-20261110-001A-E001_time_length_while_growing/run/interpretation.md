# Interpretation: time lengths of a growing plane

Run of the frozen contract `METRIC-GROW-20261110-001A-E001` (exploratory, not blind: smoke tests disclosed), 2026-11-10, launch
`metric-grow-a1` at 04:49 UTC. Parts C and S5 finished in 65 minutes. At the epic's close (about 07:30 UTC) part S7's second runs on the
7 × 7 tube were still running (each stage there cycles through about 800,000 lags), and parts V and X wait on them; they are folded in
when they finish (METRIC-GROW-A1). Code 2 was run on S5's pick at the close (`V5_at_close.json`). Readings exact.

## The outcomes on the 5 × 5 tube

| Outcome | Verdict | Evidence |
| --- | --- | --- |
| C: code 1 and code 2 agree on T, T1 and L | **Yes**, on all seven schedules (3 × 3, 5 × 5, 7 × 7) | `C.json` |
| Every T and T1 read through freezes | **Yes** for T in every balanced schedule; T1 in all but three ([2, 29], [2, 61], [29, 60]), whose failing readings are dropped from R1 | `S5.json` |
| M1: R1 a metric on every original ring | **Not met.** Of 42 balanced schedules (32 of two runs), one, [28, 60], reaches every original ring both ways; its round trip is symmetric but breaks the triangle inequality 60 times, e.g. R1(−2, −2) = 138 > R1(−2, −1) + R1(0, −1) = 90 + 36 | `S5.json` |
| M2: reads the lattice distance | **Not met** (needs M1) | |
| Deaf distance | **None on 5 × 5**: [28, 60] reaches every ring; no other balanced schedule reaches beyond distance 2 both ways | `S5.json` |
| Code 2 on [28, 60] | **Agrees**: every stage balanced to 40 × 40, T, T1 and L identical | `V5_at_close.json` |

## Where the triangle fails

- **Only across a doubling (post hoc).** Over all 14 two-run schedules with three T1 readings defined, the directed time length T1
  breaks the triangle inequality only when the far target is reached after the first doubling: no violation among targets reached
  within the first run. Within one stage the network does not change, so a route to u followed by the translate of a route to w is a
  route to u + w, and T1(u + w) ≤ T1(u) + T1(w) whenever both legs end before the doubling (concatenation, by hand).
- **Far costs more than the sum of near.** [28, 60]: R1 = 36 at distance 1, 48 and 60 at 2, 90 and 102 at 3, 138 and 150 at 4; T1
  from 12 (one ring left) to 84. The doubling at lag 28 doubles the ring steps between original rings, and legs after it are slower.
- **The hearing lags.** L reaches every ring in [28, 60] and is constant on taxicab classes (8, 20, 39, 63), but breaks the triangle
  inequality 104 times, as T does (104 times; T runs from 8 to 60).

## Nonclaims

- The 5 × 5 tube, g = 3, the frozen ranges and window; balance computed, not proved; the freeze readings exact per case; declared
  rings (A45) on a declared board (A51); open births (A44); the schedules declared, found by search. The 7 × 7 half is pending.

## The 7 × 7 half, folded in

S7 finished at 16,729 seconds and V at 16,804 (`S7.json`, `V.json`). Nine first runs keep the second stage balanced (1, 2, 4, 12, 13,
28, 29, 60, 61) and eight two-run schedules keep every stage balanced to 56 × 56. The deaf distance is 4: [60, 1] (and [60], [61])
reaches every ring within taxicab distance 4 out and back, inside the first stage, R1 = 36; 48, 60; 72, 84; 96, 108 at distances 1 to
4, with no triangle violation, as the within-stage bound requires; distance 5 is reached in part (120) and 6 not. No schedule meets M1.
Code 2 agrees on [60, 1]'s T, T1 and L, and, on 5 × 5, on [28, 60]'s balance and readings. X did not run (no M1 positive).
