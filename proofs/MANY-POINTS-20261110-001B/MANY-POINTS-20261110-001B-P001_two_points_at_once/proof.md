# Two points at once

Status: Computed (sampled pairs; the order test exhaustive per pair). `check.py` (1 minute), ticket B of
`research/MANY-POINTS-20261110-001/preregistration.md`, frozen in commit `880f19375` before any run.

## What is checked

Space (b) for the Fano and thin (2,1,2) leaves; four floors, written by the frozen search toward A1, A2, A4 and A3; at each floor 40
sampled pairs of points in each of four categories (1,280 pairs). Each point is flipped, a disturbance. The deterministic rule D (the
move lowering W most) resolves each disturbance alone. For a pair, the interaction I = ΔW(p, q) − ΔW(p) − ΔW(q), and the **grid** of D's
two move sequences: every interleaving is a path through it, so every order is legal when every grid step is a legal move that does not
raise W. Classes: cancel (I < 0), bind (I > 0), independent (I = 0, no shared move, every order legal, the far corner at the floor with the
floor's address), meet (otherwise). M1 then runs once from both flips and once from one, to read whether the address held.

## Results

| Category | Pairs | Independent | Cancel | Bind | Meet | Held after one | Held after two |
| --- | --- | --- | --- | --- | --- | --- | --- |
| different composites | 320 | 320 | 0 | 0 | 0 | 100% | 100% |
| same composite | 320 | 267 | 36 | 16 | 1 | 100% | 98.4% |
| both outer | 320 | 224 | 70 | 26 | 0 | 100% | 93.4% |
| outer and composite | 320 | 315 | 4 | 1 | 0 | 100% | 98.8% |

No pair was single-stuck. B1 (at least 90% of different-composite pairs independent), B2 (independence highest there) and B3 (held after
two at least 0.9 times held after one, everywhere) held; the failure line was not crossed; the stop condition (every category at least 90%
independent) was not met, so nearby points do interact. Interacting pairs mostly cancel: the mean I over cancel and bind pairs was
negative in every category.

**Post hoc (not frozen):** sorted by the distance between the two points (lines sharing a point are adjacent), every one of the 1,104
pairs at distance 2 or more was independent, and 154 of the 176 pairs at distance 1, sharing a line, interacted (110 cancel, 43 bind,
1 meet). Two points interact only when they share a line, on these samples.
