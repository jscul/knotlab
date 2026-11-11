# Learning counts through a shared distinction

Status: Proved (V1 and R exact; learning computed, frozen). `check.py`, ticket A of
`research/SHARED-COUNT-20261111-001/preregistration.md`, frozen with the code in commit `6c391343f` before any run. The harness and summary
parts reproduce; the learning parts were run once (about 80 minutes for J2 and 2 hours for J3 on ten processes) and are recorded run by
run in `runs_learn2.jsonl` and `runs_learn3.jsonl`.

## The test

A copy is the drawn knot pattern (2, 0, 4): 8 distinctions and 8 not-all-equal knots, every knot holding three distinctions and every
distinction in three knots, drawn as a two-coloured triangulation of the literature's torus (knots one colour, distinctions the other,
faces at its vertices). In its tightest class it forces distinction 5 to the sum mod 2
of distinctions 0, 1 and 4 (`PARITY-NEEDS-20261111-001`). J2 joins two copies by one shared distinction (copy 1's read distinction 5 is copy
2's input 0): 15 distinctions, 16 knots. J3 chains three copies: 22 distinctions, 24 knots. Inputs are held, the last copy's distinction 5 is
read, and the shared distinctions are hidden. The learner is `PARITY-FIVE-20261111-001`'s harness, unchanged: the credit learner with the
sturdier probe over every input pattern, budget 8,000,000 steps per target, targets the count, its negation and the count again, ten runs
per base; each copy's dissonance is read with its own drawing's faces (A66).

## What the construction drops

A drawn knot pattern has every distinction in three knots and one drawing. J2 and J3 keep the not-all-equal knots, three distinctions
in every knot, and the co-knotted pairs of each copy as they were (sharing one distinction adds no pair). They drop two things: each shared distinction lies in six knots, three from each
copy, and the pattern has no single drawing, only one per copy (drawn, the two surfaces share the one triangle that stands for the
shared distinction, so their union is not a surface).

## Results

| Check | Result | Evidence class |
| --- | --- | --- |
| V1: the joined harness with one copy reproduces `LEARN-PARITY-20261111-001`'s first T1 run | yes, step for step | computed, exact replay |
| R: the count is realizable at J2's interface (5 inputs) and J3's (7 inputs) | yes, in exactly one class combination of 16 and of 64: every copy in its tightest class | exhaustive; settled by definition |
| P5: J2, the count of five learned and held in at least 8 of 10 | **10 of 10**; all 30 writes (count, negation, count) learned and held; no inexact stop | computed, frozen |
| P7: J3, the count of seven learned and held in at least 8 of 10 | **0 of 10**: every run reached its 120-minute cap before the first stop, dropped by rule | computed, frozen |

J2's first targets took a median of 199,200 learning steps (from 6,200 to 502,200), against 13,400 for one copy alone
(`LEARN-PARITY-20261111-001`); the longest run took 79 minutes of its 90.

## Against the pre-registration

V1, R and P5 held as predicted, R in exactly the predicted class combinations. P7 failed. The runs record only their outcomes, so
whether a J3 run was near its stop when the cap came is not known: P7 shows that the unchanged learner does not learn the count of
seven within two hours, not that it cannot.

## What it says

Through one shared distinction, the unchanged learner learned a count that the same two copies, grown on a drawn knot pattern of the
literature's genus 2, cannot even compute (`PARITY-FIVE-20261111-001`, exact). Sharing the read distinction of one copy as the input of the
next is the overlap a drawn knot pattern does not allow; it costs about fifteen times the steps, and a third copy put the count of seven
beyond the frozen time.
