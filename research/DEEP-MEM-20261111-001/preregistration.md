# Pre-registration: deeper memories from examples

Epic `DEEP-MEM-20261111-001` (backlog B135, G15), written on 2026-11-11 before any run on the test spaces, at the coordinator's go-ahead
after the owner resumed the learning line. Code frozen with this file in
`proofs/DEEP-MEM-20261111-001A/DEEP-MEM-20261111-001A-P001_deeper_memories_from_examples/` (`deep_lib.py`, `check.py`).

## Why B135 and not B136

B136 (is every map of held points unate) asks for a proof whose route is not yet visible: forcing in these laws runs along chains of
lines, and two chains of opposite parity activated by different contexts would give a non-unate map, so the census's answer is not
explained by any argument I can state. B135 is testable now with frozen tools and answers the question the learning line left open:
whether learning from examples reaches atoms buried deeper or more of them under one composite. B136 stays in the basket.

## The question

`STURDY-PROBE-20261110-001`'s learner (credit from pinned dissonance, the sturdier probe) learned every gate target at leaves and at
composites of two atoms (84 of 84). Lemma C of `IN-OUT-20261110-001` says a composite's interface shows its atoms only through their AND,
so every extra atom under a composite multiplies blind search; pinned dissonance gives credit atom by atom. Does learning still reach a
leaf three levels down, and three atoms under one composite?

## Spaces (new to this learner)

- **T1:** the outer host K_2 with two composites D2(thin): each a K_2 composite holding a closed composite of one thin leaf and one more
  thin leaf, so its first leaf sits three levels down (88 points, four leaves).
- **T2:** the outer host K_2 with two composites C3(thin): each a K_3 composite of three thin leaves (104 points, six leaves, 4,096 classes).
- **T3:** as T1 with Fano leaves (100 points).
- **Dev (used to size the budget, not blind):** K_2 with D2(thin) and C2(thin); K_2 with C3(thin) and C2(thin). At 8,000,000 steps the
  learner learned and held 4 of 4 targets at a one-atom composite two levels down, 3 of 4 at a two-atom composite three levels down, and
  5 of 8 at three-atom composites (two seeds).

## The test (frozen)

- **Learner:** `CREDIT-PIN-20261110-001B`'s credit learner with `STURDY-PROBE-20261110-001A`'s sturdier probe, unchanged, except the budget:
  8,000,000 steps per target.
- **Interfaces:** every group with three outer points: leaves, the one-atom inner composites, the top composites (24 groups).
- **Targets in turn:** `1uu0`, `u10u`, `uuuu`, `0uu1`, then `0001`; learner seed 8000 + k. Disturbance and M1 after each stop, as before.
- **Check 1 (exact):** every gate target is realizable at every group (some class with a floor state has the group acting with a gate).

## Marks (decisive, one line each)

- **L:** leaves, at least 90% of their writes learned and held.
- **D1:** one-atom composites two levels down, at least 90%.
- **D3:** two-atom composites three levels down, at least 90%.
- **W3:** three-atom composites, at least 90%.
- **A:** `0001` never stops.
- **R:** no inexact stop.
- Reported: the median steps of learned gate-on writes (`1uu0`, `0uu1`) for each kind of group.

## Which marks are settled by their own definition

- **A is settled as to learning:** theorem D makes `0001` impossible at every interface, so it can never be learned; the mark tests only
  whether the probe can be fooled into a stop.
- No other mark is settled: check 1 is computed, not assumed, and if it fails at a group that group's writes cannot succeed and the
  report says so; R can fail if the sturdier probe is fooled on these larger spaces.
- In `THREE-IN-20261110-001`, mark I (parity and majority never stop) was settled the same way as A here: once the census showed them
  impossible, it tested only the probe.

## Predictions

L and D1 hold; D3 and W3 fail at this budget; A holds; R: 0; the gate-on cost grows with the number of atoms under a group more than with
its depth.

## Stop rule (one epic)

One frozen test. A failing mark is the answer for this learner at this budget.

Assumptions in force: A20, A21, A46, A47, A49, A50 (its temperature alternative), A52, A58. The run takes well over ten minutes and is
registered in `docs/LONG_RUNNING.md`.
