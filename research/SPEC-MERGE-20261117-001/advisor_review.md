# Advisor review of the draft design

Epic `SPEC-MERGE-20261117-001`, 2026-11-17. The advisor model (`claude -p --model claude-fable-5-2 --tools "" --output-format
json`; the reply's `modelUsage` names `claude-fable-5-2`) was given the two earlier studies' results and the first draft cold. Its
verdict was "freeze with changes". Its points, checked here, and what changed:

| Point | Taken? | Change |
| --- | --- | --- |
| A0 on `rand` likely never merges, and tuning will likely pick non-merging, so "merges don't pay" could be read when none were made | yes | a fixed eager arm AE (epochs 2n, stability ≥ 4, 10% per round, patience 1) with its control runs in every cell; reading 0 "untested" added for no merges |
| The random control is not activity-matched | yes | every random control draws among pairs that both flipped in the last epoch |
| The fast loop is NOV while the comparator is the better of NOV and NOVt | partly | kept as the coordinator asked (NOV inside); R against NOV alone reported beside R |
| A0's setting is outside A's grid | yes | added to the grid (25 settings) |
| Gate D: target, unit (joint consistency of a round), conditions | partly | agreement with the solution the run finds is reported beside planted agreement; the gate cell, the handling of runs solved before a checkpoint and the maximum over three checkpoints are stated; per-round planted consistency against kept or undone is logged; a CaDiCaL joint-consistency check per round was not taken (CaDiCaL needs about 88 s on `rand` 3,200 alone) |
| The rule is not exhaustive (a win without evidence; a win only on `rand` 3.0 or 12,800; no merges) | yes | readings 0 to 5 in order |
| Kept rounds' permanence | yes | stated: a kept round is never undone, so a kept wrong merge can censor a run |
| Hold on rule 1 alone, with hashed outputs | yes | the hold applies to any win on a random cell, with the SHA-256 of the raw outputs sent to the coordinator before any commit |
| Predictions: P1 to about 80%, P4 to 15% or less, P7 to about 10%, P8 to about 45% | yes | as suggested; P3 restated as its complement |

Not used after the results.
