# Two unlengthened shifts beyond one box: paused (partial results)

Epic `WEIGHTS-20261112-001`, 2026-11-12. Paused at the owner's request ("Let's pause on research at the next good stopping point"),
relayed by the coordinator. The registered run (pre-registration commit 9d760a7dc) was stopped at about 18:45 UTC, before its end, with
every finished sample saved. **These are partial results, not the frozen verdict;** the epic is open and not refereed.

## Where it stopped

- **β = 0 (uniform over the 738 kinds of [0, 3] × [−3, 3]):** complete by its stopping rule. 120 samples, 7 dropped at the 3,600 s
  cap across the run; 347 bases; 46 travelling bases with a kind outside the old box, **all 46 with two certified unlengthened shifts**
  (main arm; Wilson 95% interval 92 to 100%). By the frozen criterion (W1) this weighting **passes**. The old-box stratum is empty
  under β = 0 at r = 3 to 5 (as the kind mix predicted), so W2's replication check has no data. The travelling rate is lower than in
  the old box (46 travelling among 347 bases, against about a third at r = 4, 5 there).
- **β = 1:** partial, 50 samples; 27 travelling new-kind bases, all 27 with two certified directions (below the 40 the stopping rule
  needs, so inconclusive by size); 4 old-box ones, all with two.
- **β = 2:** not started.
- **Calibration (the enlarged arm on the old census's 23 one-direction bases):** 4 of 23 done, none gained a second direction.
- **Stated limit, as agreed with the coordinator:** the certificate family is tori and strips repeating across only; no case needed the
  completion pass with the two-way certificate so far (no forced-but-uncertified case among the 73 travelling new-kind bases).

## Resuming

Rerun `census.py --part census` and `--part calibration` after adding a skip of (β, sample) pairs and calibration items already in
`census.jsonl` and `calibration.jsonl` (the frozen code restarts from sample 0, so it would duplicate rows); then the completion pass,
the decision note and the referee hand-off. Partial counts: `partial_summary.json` beside this note.

## Basket (for when the line reopens)

The rest of this epic (β = 1 to 40 new-kind travelling bases, β = 2, the calibration); what gives the bonds on the uncovered side of
sample 24 at r = 3 (small non-travelling sets: bounded reach is wider than the travel cones); the cone rule (failed its pilot); the
plateau of certified upper bounds at 6 (no lower bound anywhere: an audit of every candidate would give one); the harmony thread's
repeat sizes on the 8 weak survivors.
