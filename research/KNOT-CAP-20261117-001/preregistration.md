# A cap on knots per distinction, and what matched starts remember: pre-registration

Epic `KNOT-CAP-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. It takes the first direction of
`STATE-RULES-20261117-001`, that study's referee's lead, and the owner's question about erasure, passed on from Codex. Goals G1 and
G16; tests A97 and A99. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The questions

1. **Does a cap stop the cheapest growth at two orders?** In `STATE-RULES-20261117-001` the cheapest three-knot growth made two
   orders at once from one knot and then grew cubes. Does a cap on how many knots a distinction may join, or the parameter-free
   cap of two knots per pair of distinctions, stop it at two orders, with the two orders still growing?
2. **What differs between matched starts?** That study's referee found that two starts with the same states and different knots
   grow different bases, with the same number of orders. Which state differences, on a second matched pair too, and do they
   persist as n grows?
3. **What do the states remember after erasure?** The owner's question. Grow with the knot-reading rule to n = 8, forget the knots,
   and continue with the states-only rule. Do the two starts still differ at n = 9 and beyond?

## Ticket A: the proof (written before this freeze)

`proofs/KNOT-CAP-20261117-001A/KNOT-CAP-20261117-001A-P001_caps/proof.md`.
- **T1.** From one knot, the cap of three per distinction gives the 2 × 2 pattern, then stops.
- **T2.** The cap of two per pair does the same.
- **T3.** Under a cap c, at most (c·n − 3n + 6)/6 three-knot steps from one knot.
- **T4.** After erasure the distance between two starts' distributions cannot increase.

## Ticket B: computations

Code: `caplib.py`, `run.py` and `checks.py` in `experiments/KNOT-CAP-20261117-001B/KNOT-CAP-20261117-001B-E001_cap/`. It builds on
`STATE-RULES-20261117-001B-E001`'s `rules.py`, closed and pinned by hash. Seven checks pass before this freeze.

**Rules** (fewest states, ties uniform over knot sets, names erased):
- **cc:** degree cap c = 3, 4, 5, 6, 9 or 12.
- **pair2:** at most two knots per pair of distinctions.
- **pair2-local:** the same, with knot-locality (each new knot's two old distinctions already share a knot).
- **KF3:** no cap, knot-local, as in `STATE-RULES-20261117-001`.

**Matched starts:**
- **The six-starts:** the fan and non-fan of six (the line's 12 states).
- **The five-starts:** the line of five's 10 states with three knots each, one with the shared distinction at an end (B(a,b,c),
  B(a,c,d), B(a,d,e)) and one with it in the middle (B(a,b,c), B(a,c,e), B(c,d,e)). Every three-knot presentation of that line
  has a distinction in all three knots, so this is the closest five-distinction analogue of the fan and non-fan.

**Parts:**
- **K1.** The caps from one knot: exact class distributions to n = 7 for every rule above, and 200 runs each to n = 16 (c = 4, 5,
  6, 9, 12, pair2, pair2-local). Readings:
  - kinds (a line, a branching tree, two orders, m orders, a cube);
  - λ, states and stalls;
  - fills (zero-cost steps);
  - the largest degree.
- **K2.** Matched starts, exact: KF3 from both pairs to n = 10. Readings:
  - the total variation distance between the two starts' distributions over full classes (states and knots), over classes of
    states, and over coarse features (N, splits, crossings, λ, k);
  - the sorted class probabilities;
  - the two-order probability;
  - the classes present in one start only, with their mass and features.
- **K3.** Matched starts, sampled: KF3, 1,000 runs per start with identical seed strings, to n = 12. Also:
  - a floor: 1,000 more runs from each start with other seeds;
  - a permutation test (200 shufflings) of the distance over classes of states;
  - the two-order counts and λ.
- **K4.** Erasure: KF3 to n = 8, then the states-only fewest-states rule of `STATE-RULES-20261117-001` with up to three knots.
  - Exact to n = 11 from both pairs.
  - The no-erasure control: KF3 with the knots kept, exact to n = 10.
  - 1,000 runs per start to n = 14, with the floor and the permutation test.

  The seed strings name no start, so identical seeds do not pair the runs: the arms are independent.
- **K5.** The caps from the matched starts: c = 5, c = 6 and pair2-local, 300 runs per start to n = 12.

## Predictions (frozen; the advisor's where marked, with its confidence)

| # | Prediction | Fails when |
| --- | --- | --- |
| C1 | K1 exact: c = 3 and pair2 give the 2 × 2 pattern at n = 4 with probability 1, then stall with probability 1 (T1, T2) | otherwise |
| C2 | K1: c = 4 does not stall at n = 5; in its 200 runs at n = 16 every run has at most 3 fills (T3), none is a cube, and λ = 2 in a majority (the 2 × 2 pattern kept by one-knot steps; advisor) | otherwise |
| C3 | K1: no Q3 at n = 8 for c = 5 (advisor: 13 knots allowed, 14 needed); Q3 at n = 8 in under half the runs for c = 6 and no Q4 at 16; for c = 9, Q3 at 8 in a majority and Q4 at 16 in a minority; for c = 12, Q3 at 8 in a majority (advisor) | otherwise |
| C4 | K1: no rule tried grows two orders: at n = 16 none has λ = 2 with at least 4 fills in a majority of its runs | some rule does |
| C5 | K2: the two six-starts have the same two-order probability at n = 8 (advisor: 3/8, about 70% on equality); the distance over classes of states is 3/4 at n = 7 (advisor, about 75%) and stays at least 0.7 through n = 10; over coarse features it is at most 0.03 at every n | otherwise |
| C6 | K2: the five-starts give distance 0 at n = 5 (same states), at least 0.5 at n = 6 and at least 0.6 through n = 10; two-order probabilities equal (advisor, about 60%) | otherwise |
| C7 | K3: at n = 7 and 8 the sampled distance between the six-starts exceeds both floors, with permutation p < 0.01; two-order counts at n = 8 do not differ significantly (within 3 standard errors) | otherwise |
| C8 | K4 exact: after erasure the distance is non-increasing (T4) and still positive at n = 9, 10 and 11 for the six-starts (advisor: about 0.72, 0.65, 0.58, ± 0.15; exactly 0 by n = 11 about 10%) | it reaches 0 by n = 11 |
| C9 | K5: stalls in under 5% of runs by n = 12 for c = 5 and 6 from both six-starts | otherwise |

These are exploratory, with no directional prediction:
- the pair caps from the matched starts;
- K4's sampled values at n = 14, which the floor may swamp (the advisor's warning);
- the no-erasure control.

**What would count against the headline.**
- A cap under which two orders keep growing (C4 fails): a natural local law that selects two orders.
- An erased difference that vanishes at once: the states then keep no lasting imprint of how the knots met.
- An exact two-order probability that differs between the six-starts: the knots would then change the number of orders after all.

**The headline, stated before running.**
- The natural caps stop the cheapest growth exactly at its first two orders, the 2 × 2 pattern, and allow nothing more.
- Looser caps let it run on toward cubes.
- No cap tried keeps two orders growing.
- From matched starts the bases differ while the number of orders does not.
- After erasure the difference shrinks but does not vanish within three steps: the states keep an imprint of how the knots met.

**Classical:** data processing for total variation. **Local:** the stops, the bound and the comparisons.

## Prior work in the program

- `STATE-RULES-20261117-001` and its referee's 1,000-run comparison (the predecessor).
- `GRID-GROW-20261117-001`: the grid's knots, nine at an interior cell.
- `CARRY-FIFTH-20261117-001` (Codex): the line of four's two two-knot presentations and what retained knots mark.

## Runs and stop rule

`run.py --part NAME` for K1 to K5, each its own process, then `run.py --merge`. Registered in `docs/LONG_RUNNING.md` if a part
passes ten minutes. The study stops after its read-out, followed by A97 and A99 status, the decision note, the referee hand-off and
the report.

The advisor model was consulted twice before this freeze. It:
- derived the cap predictions and the bound;
- proposed the pair cap;
- retracted its first account of the six-starts;
- gave the matched-start and erasure predictions and the design fixes: the floor with permutation tests, the no-erasure control,
  three kinds of distance, and the table of classes in one start only.
