# Pre-registration: let the examples shape the dissonance the learner feels

Epic `CLAMP-LEARN-20261112-001` (sub-goal B168, with the cheap part of B169; G15 with G16; program learning), written on 2026-11-12 before
any frozen run, at the coordinator's go-ahead. Frozen with the code in
`proofs/CLAMP-LEARN-20261112-001A/CLAMP-LEARN-20261112-001A-P001_a_clamped_phase/` (`clamp_lib.py`, `check.py`). The design and predictions
were put to the advisor model cold before freezing (below). Nothing is tuned after a result is read; one clamp length (K = 200) is used, not
tuned.

## The question

`STEER-LEARN-20261112-001` (refereed, Confirmed) found that steering at the probe does not let the learner's examples steer its search, and
that every learner reaches some targets faster than blind search and the count more slowly, from a fixed start. Energy-based learners in the
literature are taught during their walk: the clamped phase. Does a learner whose moves feel the dissonance under each example's clamp, one
example at a time, find the count faster than every honest baseline, and does the speed-up follow the taught target?

## Prior work

A clamped phase against a free (or negative) phase is the shape of Boltzmann machine learning (Ackley, Hinton and Sejnowski 1985),
contrastive Hebbian learning (Movellan 1990), contrastive divergence (Hinton 2002), equilibrium propagation (Scellier and Bengio 2017), and
coupled learning in physical networks (Stern, Hexner, Rocks and Liu 2021). All change parameters from the difference between clamped and
free states. Known. What would be new: a native learner of signed not-all-equal knots whose clamped phase beats blind search over its own
rest set, after the restriction that clamping alone imposes is subtracted.

## What the advisor model said (a colleague's view, checked against the design)

- A negative phase that simply accepts sign changes raising the dissonance under the wrong output would degrade the law everywhere; use a
  contrastive acceptance (the change under the correct clamp minus the change under the wrong one) instead. Adopted as CA.
- A clamp with correct outputs only is more likely a filter than a steer: it restricts the walk to laws consistent with the examples. With
  4 laws at rest, the first examples eliminate the competitors, so steering and filtering cannot be told apart there. Hence GE (64 laws)
  for the test, and control (b) below.
- Start proximity, probe inflation (clamping can change how often the learner probes) and a gauge-dependent success test are artefact
  routes: random starts (as the referee also asked), every step counted (probe walks included), and the exact map as the success test.
- Its cleaner test (drift under each clamp against shuffled outputs) is noted for a later epic; this one keeps the search test.

## Settings and exact baselines (computed before freezing, `check.py --part baselines`)

| Setting / target | Laws at rest | Chance per uniform draw | Blind median | Chance among laws consistent with every positive example | Restricted blind median | Mean probe walk steps per law | Blind median in steps (uniform / restricted) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GE / the count `01101001` | 64 | 1/32 | 22 | 1/8 | 6 | about 161,500 | 3.55 million / 0.97 million |
| GE / g `00001111` | 64 | 1/64 | 45 | 1/10 | 7 | about 269,500 | 12.1 million / 1.89 million |
| F / the count | 4 | 1/8 | 6 | 1/2 | 1 | about 268,000 | 1.61 million / 0.27 million |
| F / g `0uu01uu1` | 4 | 1/16 | 11 | 1 | 1 | about 172,000 | 1.89 million / 0.17 million |

Restriction to consistent laws is nearly the whole answer in F (half or all of the consistent signings are the target), which confirms the
advisor's point: F is reported, not tested.

## The learners and runs (frozen; setting GE, random starts)

- **B**, the unchanged learner (`STEER-LEARN-20261112-001`'s B), from random starts: the biased walk as it runs on this target.
- **C**, a clamped phase: the world holds one example's inputs and output (a fair coin for `u`) for 200 steps, cycling through the eight;
  state and sign moves feel the dissonance under the clamp; after each cycle the clamp is released, the state relaxed, and the sturdier
  probe run if the learner is at rest.
- **CA**, contrastive acceptance: as C, and a copy of the state relaxed under the wrong output (100 state-only steps per example); a sign
  change is accepted by the Metropolis rule on its change under the correct clamp minus its change under the wrong one.
- A random start is a uniform law at rest with a uniform flip of each distinction. Targets: the count and g. 100 seeds each (12000 + k),
  budget 2,000,000 learning steps, 5 minutes per run, each written as it finishes.
- **Every step is counted:** learning moves (state and sign moves reported apart), the wrong copy's relaxation, and every probe's walk
  steps. The currency is all steps; probes are reported too.

## The biased walk (B169's cheap part, frozen)

The unchanged learner taught an impossible map (`00000001`, not self-dual, so no law computes it), the map of its law read at each of 60
probes, 20 seeds (13000 + k), from the fixed start and from random starts, in F and GE: the share of probes computing the count and g,
against the uniform chances above. If the fixed start's share departs from uniform and the random starts' does not, the bias is the start.

## Marks (frozen)

- **Passes (rule, target):** the median of all steps to find is at most half the restricted blind median in steps, at least 3 of 4 runs
  find within it, and the median is at most half B's median (unfound runs count as never).
- **Steering shown:** passes on the count and on g.
- **Readings:** beating the uniform blind median but not the restricted one is filtering by the clamp, not steering; passing on one target
  only is a bias; passing on both is steering.
- **Settled by definition:** the restricted baseline subtracts what clamping alone gives; not settled.

## Predictions (with the advisor's)

C and CA beat the uniform blind median in steps; neither beats the restricted median by half; no steering shown. The fixed start's share of
the count is below uniform and the random starts' near uniform (the bias is mostly the start).

## Caps and long runs

The walk: 80 walks of 60 probes, expected 20 to 40 minutes; the runs: 600 runs, 5 minutes each at most, expected one to two hours. Both
registered in `docs/LONG_RUNNING.md`, part caps 2 and 4 hours.

## Stop

All marks and the walk's shares settled; then close as referee pending with a hand-off.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58.
