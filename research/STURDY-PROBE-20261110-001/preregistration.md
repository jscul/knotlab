# Pre-registration: a probe that is not fooled

Epic `STURDY-PROBE-20261110-001` (backlog B134, G15), written on 2026-11-10 before any run with the new probe on a test space, at the
coordinator's go-ahead. One design, one mark. Code frozen with this file in
`proofs/STURDY-PROBE-20261110-001A/STURDY-PROBE-20261110-001A-P001_a_sturdier_probe/` (`probe_lib.py`, `check.py`).

## The question

The example learner's probe certifies only that an asked value is reachable; it reads a wrong value as unreachable when one 4,000-step
walk from the current state misses it. Every inexact stop since `IN-OUT-20261110-001` was such a miss (5 of 90 writes with the fixed
learner, 9 of 60 with the credit learner on S3 and S4, 5 of 45 on S5, three of them acceptances of `0001`, which theorem D forbids). Does a
sturdier negative check remove them, and at what cost?

## Measured on dev only, before this freeze

On the dev spaces, from 1,004 clamped patterns whose floor is reachable, a walk at temperature 0.7 reached it in a median of 200 to 560
steps; 99% within 4,000 to 7,000; the longest took 23,956 steps from the current state and 10,289 from a fresh state. So one 4,000-step
walk misses about one reachable value in a hundred.

## The design (frozen)

The positive checks are unchanged. Each negative check (the wrong value of an example that asks for a decided output) becomes four walks
of 25,000 steps: the first from the current state, three from fresh random states of the free points; the example passes only if none
reaches the floor with the wrong value held. Nothing else changes: the fixed learner of `CREDIT-PIN-20261110-001A` and the credit learner of
`CREDIT-PIN-20261110-001B` are used as they are, with this probe in place of the old one. Both probes count their walk steps.

## The runs (ticket A)

1. **Cost baseline.** `CREDIT-PIN-20261110-001A`'s run (fixed learner, S1 to S4, 18 interfaces, targets `1uu0`, `u10u`, `uuuu`, `0uu1`,
   `0001`, seed 3000 + k) with the old probe counting its steps; it must reproduce that run's rows.
2. **Fixed learner, sturdier probe:** the same run with the new probe.
3. **Credit learner, sturdier probe:** `CREDIT-PIN-20261110-001B`'s run (S3 and S4 with seed 3000 + k, S5 with 5000 + k) with the new probe.

Outcomes as before, each counted on its own; maps are scored by SAT afterwards.

## The mark (decisive)

**Z:** no inexact stop and no `0001` stop in runs 2 and 3 together. Reported with it: learned and held at leaves and composites against the
old figures (55 of 56 and 10 of 16; 29 of 32, 11 of 16, 21 of 24 and 12 of 12), and the probe's step cost against the baseline.

## What the earlier figures are

The figures 100 of 100 (`NATIVE-WRITE-20261110-001`), 55 of 56 and 10 of 16 were scored by SAT on the law at each stop, so a fooled probe
could not inflate them; it turned a run that should have continued into an inexact stop, counted apart. The native writer's probe is a
different one (an unclamped walk of 20,000 steps reading an atom's own region), and it was never fooled in 100 writes. What this epic can
change is how many writes succeed once the learner is no longer stopped early by a false reading.

## Predictions

Z holds; learned-and-held counts stay or rise, since writes that stopped inexactly now continue; the probe costs several times more
steps. If Z fails, the next epic is B133 (three held inputs), not another learner-tuning epic.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58. The runs are expected to take more than ten minutes and are registered in
`docs/LONG_RUNNING.md`.
