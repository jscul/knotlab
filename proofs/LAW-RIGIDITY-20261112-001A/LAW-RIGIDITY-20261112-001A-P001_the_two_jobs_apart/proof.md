# The drawing's two jobs, apart

Status: Proved (V and E exact; learning computed, frozen). `check.py`, stage 1 of `research/LAW-RIGIDITY-20261112-001/preregistration.md`,
frozen with the code in commit `94c87c2a7` before any learning run. All parts but the learning reproduce; the learning was run once
(`runs_learnR.jsonl`, `runs_learnRS.jsonl`; the longest run 234 seconds).

## The test

On one copy of the drawn knot pattern (2, 0, 4) (J1), the learner with the drawing's faces feels a graded face term. R replaces it with a
flat one: W = 2 × violated knots + 2 × [some face lacks exactly one agreeing corner], so the learner rests only at the 4 laws the faces
allow (exact: 4 of J1's 512 laws, 1 of them counting) but feels no grade. RS is R with a repair that flips distinctions only after each
stop (a rule we supply, A68). Ten runs each, the same seeds, so a run of R and of RS are the same until the first stop.

## Results

| Variant | Stopped at the count, first target | Learned and held, first target | All writes learned and held | Median steps, first target |
| --- | --- | --- | --- | --- |
| F, with faces (`LEARN-PARITY-20261111-001`) | 10 of 10 | 10 of 10 | 30 of 30 | 13,400 |
| K, knots alone (`UNDRAWN-LEARN-20261111-001`) | 1 of 10 | 0 of 10 | 0 of 30 | — |
| R, rest set, no grade | 10 of 10 | 4 of 10 | 12 of 30 | 17,800 (held runs) |
| RS, rest set and a rigid repair | 10 of 10 | 10 of 10 | 30 of 30 | 25,400 |

M1 (R held in at least 8 of 10) fails; M2 (RS learned in at least 8 of 10) passes. RS holds by definition (its repair cannot change the
law); what it adds over R is shown by R's 18 unheld writes, whose repairs re-signed knots and left the rest set.

## What it says

The faces' two jobs come apart. Restricting where the learner may rest is enough to find the count, at about the speed with faces, with no
grade; the grade is not needed. Keeping it needs a reason for the law not to change during a repair: the faces' grade gave one, and a
supplied rule that repairs flip distinctions only gives another.
