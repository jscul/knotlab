# A native rest set

Status: Proved (V and E exact; learning computed, frozen). `check.py`, stage 2 of `research/LAW-RIGIDITY-20261112-001/preregistration.md`
(the addendum), frozen with the code in commit `d2bd7c40a` before any stage-2 run. All parts but the learning reproduce; the learning was
run once (`runs_learnN0U.jsonl`, `runs_learnN1J1.jsonl`; the longest run 278 seconds).

## The test

A base's shortest cyclic sequences: distinct knots and distinct distinctions in turn, each knot holding the distinction before it and the
one after (the literature's shortest Berge cycles). On both bases they have two knots: two knots sharing two distinctions. A law's sum
around one is the sum of its signs there, mod 2. Rule N0 lets the learner rest only where every shortest sum is 0, rule N1 only where every
one is 1; W = 2 × violated knots + 2 × [some shortest sum is wrong], and the repair flips distinctions only (A68). Nothing reads a drawing.
The bases: J1, one copy of (2, 0, 4) (4 shortest sequences); U, the 6-distinction, 8-knot base no drawing fits (14).

## Results

| Rule and base | Laws at rest (exact) | Counting among them (exact) | Learned and held, first target | All writes | Median steps |
| --- | --- | --- | --- | --- | --- |
| N0 on U | 2 (the plain law, where the learner starts, and the counting law) | 1 | 10 of 10 | 30 of 30 | 4,400 |
| N1 on J1 | 32 | 4 | 10 of 10 | 30 of 30 | 14,800 |
| N0 on J1 | 32 | 0 | not run: no counting law at rest | | |
| N1 on U | 0 | 0 | not run: no law at rest | | |

Both run marks pass. The frozen stage-2 mark, one rule learned and held on both bases, fails by definition: N0 leaves J1 no counting law
at rest and N1 leaves U no law at all.

## What it says

On a base that no drawing fits, a rule read from the knot pattern alone, resting only where the law's sum around every shortest sequence
is 0, with the supplied rigid repair, lets the learner learn and hold the count in every run: the first learned and held map on such a
base. With two laws at rest, any stop is at the count; what the runs show is that the learner gets there, quickly. The same rule leaves
one copy of (2, 0, 4) no counting law: there, every counting law has sum 1 on each shortest sequence, and the drawing's faces, which the
learner with faces reads, are sequences of three knots, not the shortest. No choice of one value for every shortest sequence serves both
bases.
