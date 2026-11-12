# A graded native rule, free repair

Status: Proved (V and E exact; learning computed, frozen). `check.py`, ticket A of `research/NATIVE-GRADE-20261112-001/preregistration.md`,
frozen with the code in commit `7999dd625` before any learning run. All parts but the learning reproduce; the learning was run once
(`runs_learnJ1.jsonl`, `runs_learnU.jsonl`; the longest run 1,087 seconds).

## The test

Rule GE: W = 2 × violated knots + 2 × min(number of shortest sums 0, number of shortest sums 1), so the learner rests where all the law's
shortest sums are equal, whatever the value, and is charged 2 for each shortest sequence that would have to change. The repair after each
stop is the learner's own, free to re-sign. Ten runs each on J1 (one copy of (2, 0, 4); 64 laws at rest, 4 counting; no place on two or more
shortest sequences) and on U (the 6-distinction undrawn base; 2 laws at rest, 1 counting; 18 of 24 places on two or more).

## Exact (computed before freezing)

The value-free rest set holds a counting law on J1 (4 of 64) and on U (1 of 2). On the next two bases of the frozen undrawn search, U(7, 9)
and U(8, 10), every rule fixing the shortest sums (all equal, all 0, all 1) leaves 8 laws at rest and none counts.

## Results (computed, frozen)

| Base | Stopped at the count, first target | Held, first target | All writes held | First-target probes, median (random draws among laws at rest, expected) | Reading |
| --- | --- | --- | --- | --- | --- |
| J1 | 10 of 10 | 6 of 10 | 17 of 30 | 244.5 (16) | still drifts |
| U | 10 of 10 | 8 of 10 | 19 of 30 | 5 (2) | holds, by the frozen first-target mark |

P(J1) fails and P(U) passes. Across all three targets, U held 19 of 30 writes, so the graded rule's rigidity there is partial: the frozen
mark is met at the first target only.

## What it says

A graded rule of the knots, needing no chosen value, finds the count on both bases and keeps it where most places lie on two or more
shortest sequences (U, at the first target), but not where none does (J1), as the rule's construction predicts. It keeps the law less
reliably than the supplied rule of A68 (30 of 30). On J1 the learner took far more probes than random draws among the laws at rest would
need: what steers it to the count is still the rest set, not the examples.
