# Pre-registration: a learner whose examples steer its search

Epic `STEER-LEARN-20261112-001` (sub-goal B165, G15 with G16; program learning), written on 2026-11-12 before any frozen run, at the
coordinator's go-ahead. Frozen with the code in `proofs/STEER-LEARN-20261112-001A/STEER-LEARN-20261112-001A-P001_steering_rules/`
(`steer_lib.py`, `check.py`). The rules and the test were drafted with the advisor model before freezing (B165's entry). A smoke test of
each learner at seed 1 (outside the frozen seeds) checked only that the code runs. Nothing is tuned after a result is read.

## The question

`SEARCH-AUDIT-20261112-001` found that the line's learner finds a target no faster than blind draws among the laws it may rest at: its
examples stop the search but do not steer it. Can a native rule let the examples steer, so that the learner finds the target faster than
blind search, and does the speed-up follow the taught target?

## Settings, targets and blind baselines (exact, `check.py --part harness`, before freezing)

One copy of (2, 0, 4), J1, interface 0, 1, 4, read 5.

| Setting | Laws at rest | Target | Chance per blind draw | Blind median (mean) |
| --- | --- | --- | --- | --- |
| F, the drawn engine (dissonance with the drawing's faces) | 4 | the count, `01101001` | 1/8 | 6 (8) |
| F | 4 | g = `0uu01uu1` | 1/16 | 11 (16) |
| GE, the graded value-free engine of `NATIVE-GRADE-20261112-001` | 64 | the count | 1/32 | 22 (32) |
| GE | 64 | g = `00001111` | 1/64 | 45 (64) |

A blind draw is a signing at rest drawn uniformly; its map counts the interface's own flips (audit's method). The swap target g is, by a
frozen rule, the map other than the count and its negation whose chance is closest to the count's (ties in sorted order).

## The learners (frozen)

All start from the base law at the solver's first satisfying state, relaxed by M1, and run to their first stop (budget 2,000,000 steps, 5
minutes per run). The probe is the sturdier probe over every input pattern, draw for draw; it also keeps, for each example, the end state
of its positive walk, and the wrong state reached when a negative check fails.

| Rule | What it does | What it uses that blind search does not |
| --- | --- | --- |
| **B**, the credit learner unchanged | random sign changes at violated knots near the interface; cools knots that stay dissonant | nothing about the examples beyond pass or fail |
| **P**, persistence targeting | proposes sign changes at knots in proportion to 1 + the number of failing examples whose end state violates them; no cooling | which knots the failing examples' end states violate |
| **M**, make and break | after a failing probe, changes the sign, among the places of the knots violated in the first failing example's end state, that newly violates a knot in the fewest stored end states of passing examples (tabu of 5) | the failing example's end state, and the passing examples' end states |
| **A**, two-sided acceptance | accepts a proposed sign change outright when it violates some stored wrong state and no stored passing state; otherwise the usual rule | the passing examples' end states, and the wrong states the negative checks reached |

**Every check is charged.** Cost is counted in probes: each world probe (a full probe of the current law against all eight examples) is
one; each candidate law checked against the stored states (one per candidate sign change scored by M, one per proposal judged by A) is one
more. The mark uses the charged count, so a win cannot come from uncounted checks. World probes alone are reported too.

## Runs (frozen)

Four rules × two settings × two targets (the count and g) × 100 seeds (11000 + k): 1,600 runs, each written as it finishes. In the g runs
the learner also records whether its law at any probe computed the count (scoring only, read by SAT).

## Marks and readings (frozen)

- **Passes on a target:** the median charged probes to find is at most half the blind median, and at least 3 of 4 runs find within the
  blind median (unfound runs count as never).
- **Steering shown (rule, setting):** passes on the count and on g. The speed-up must follow the taught target.
- **Readings:** if some rule shows steering in some setting, the examples steer it there; if a rule passes on the count only, it is a bias
  toward the count's laws, not steering; if none passes, no rule here steers.
- **Not settled by definition:** blind baselines are exact; the learners' probes are runs.

## Prior work

The rules are known local-search ideas lifted to the law: M is WalkSAT's break count (Selman, Kautz and Cohen 1994) with the examples as
clauses; P is clause weighting, as in the breakout method (Morris 1993) and SAPS (Hutter, Tompkins and Hoos 2002); A is a contrastive rule,
raising the dissonance of wrong states and keeping correct ones low, as in Boltzmann machine learning (Ackley, Hinton and Sejnowski 1985)
and contrastive divergence (Hinton 2002), or perceptron updates on errors (Rosenblatt 1958). Known as heuristics; what is not known to me is
whether any of them lets a learner of this kind beat blind search over its own rest set.

## Predictions

At least one of P, M, A passes on the count in F; steering (passing on g too) is uncertain; B fails, as the audit found.

## Caps and long runs

1,600 runs on 20 processes, 5 minutes per run, expected one to two hours; registered in `docs/LONG_RUNNING.md`; part cap 4 hours.

## Publication hold

These are 8-distinction bases; a rule that beat blind search here would not be a general method for SAT. If a result looked like one, it
would not be committed before the owner is told.

## Stop

Every (rule, setting, target) settled; then report.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58.
