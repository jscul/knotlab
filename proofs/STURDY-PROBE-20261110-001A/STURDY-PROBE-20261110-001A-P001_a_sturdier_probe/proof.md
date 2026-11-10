# A sturdier probe

Status: Proved (computed, frozen). `check.py` (about sixteen minutes, interface runs in parallel), ticket A of
`research/STURDY-PROBE-20261110-001/preregistration.md`, frozen with the code in commit `fb162b543` before any run on a test space.

## The design

Positive checks as before (one 4,000-step clamped walk from the current state). Each negative check, the wrong value of an example that
asks for a decided output, is four walks of 25,000 steps, one from the current state and three from fresh random states of the free
points; the example passes only if none reaches the floor (`probe_lib.py`). The learners are unchanged.

## Results

| Run | Leaves learned and held | Composites learned and held | Inexact stops | `0001` stops | Probe steps | Learner steps |
| --- | --- | --- | --- | --- | --- | --- |
| Old probe, fixed learner, S1 to S4 (reproduces `CREDIT-PIN-20261110-001A`) | 55 of 56 | 10 of 16 | 5 | 0 | 135,620,778 | 97,380,600 |
| Sturdier probe, fixed learner, S1 to S4 | 56 of 56 | 10 of 16 | 0 | 0 | 335,240,875 | 108,410,600 |
| Sturdier probe, credit learner, S3 and S4 | 32 of 32 | 16 of 16 | 0 | 0 | 559,016,656 (with S5) | 100,041,800 (with S5) |
| Sturdier probe, credit learner, S5 | 24 of 24 | 12 of 12 | 0 | 0 | | |

- **Mark Z holds:** no inexact stop and no `0001` stop in either run with the sturdier probe (156 writes and 39 runs of `0001`).
- **Cost:** on the same run the sturdier probe took 2.5 times the old probe's walk steps (335 million against 136 million), about 3
  probe steps per learner step instead of 1.4; wall time for all three runs was 15.5 minutes on 22 cores.
- **The fixed learner's composite writes** that had stopped inexactly now ran to the budget instead: 6 not reached, 10 learned (4 of 8
  gate-on writes, median 495,800 steps).
- **The credit learner** learned every one of its 84 writes, composites included (gate-on medians 487,400 steps on S3 and S4, 475,100 on
  S5), where the fixed learner learned 4 of 8 gate-on composite writes.

## What the earlier figures were

They were scored by SAT, so a fooled probe never inflated them. Re-checked with the sturdier probe: 55 of 56 becomes 56 of 56, 10 of 16
stays 10 of 16, and the credit learner's 11 of 16 becomes 16 of 16 (29 of 32 leaves becomes 32 of 32; S5's 21 of 24 and 12 of 12 become
24 of 24 and 12 of 12). The native writer's 100 of 100 used its own probe, never fooled, and is not touched.
