# Do the knots a growth added record its order?: pre-registration

Epic `MEET-ADDED-20261118-001` (sub-goal B199, `MEET-HIST-20261118-001#1`; goal G16; tests A97), 18 November 2026, by Claude, on
the coordinator's go-ahead. Frozen before the run. The canonical K1–K3 test is unchanged.

## The question

What one KF3-grown base's distances (its states) miss of how a line's knots nest is a small part of the order of growth, and that
part is not in the states (`MEET-HIST-20261118-001`, refereed). The base's starting knots still show the nesting, which says nothing
about what the growth recorded. Do the knots the growth added record the missing part, read with no names: as a bare graph of added
pairs, with the states, as triples, or with their rules?

## In standard terms

For a KF3 growth from a presentation, the grown split system with the hypergraph of added betweenness triples, read up to
relabelling; the mutual information of several readings with the presentation's unlabelled rooted binary tree.

## Prior work in the program

`python3 -B scripts/track.py objects "knots added by growth record the order of growth, presentations of a line" --until 2026-11-18 --exclude MEET-ADDED-20261118-001`

`python3 -B scripts/track.py objects "added co-knotted pairs with states, unnamed grown base, nesting" --until 2026-11-18 --exclude MEET-ADDED-20261118-001`

- `MEET-HIST-20261118-001`: same object and population; the shares this study extends to the added knots.
- `MEET-TWIST-20261118-001` and `MEET-ORDERS-20261118-001`: the growth and the presentations (relatives).
- `COMMON-FOLD-20261112-001` and `RANDOM-FATES-20261112-001`: unrelated (random knot patterns and their ends).

## Settled by construction (stated, not tested)

- An unnamed reading is a function of the all-named one, so each arm's share is at most the all-named share; pairs are read off
  triples, so the states with the added pairs carry at most what the states with the added triples carry; and the states with the
  pairs carry at least the states alone (the advisor). Only strictness and equality are predicted.
- With the starting pairs included the nesting is read at k = 0 (the sanity row SG; a gate).

## Exploration before this freeze (disclosed)

The smoke test on five (to k = 4) and six (to k = 3): added pairs alone 0 at five and 0, 0.009, 0.040 at six (the referee's
preview, a gate); states alone 0.60, 0.39, 0.22 (five, k = 2 to 4); states with the added pairs 1.0, 0.95, 0.94 (five) and 0.83,
0.90 (six, k = 2, 3); states with the added triples, and with their middles too, exactly the all-named share at every level (five
1.0; six 0.8313, 0.9113).

## Ticket B: computations

Code: `job.py`, `checks.py` and `merge.py` with `melib.py` (MEET-ORDERS-20261118-001B's engine, unchanged) in
`experiments/MEET-ADDED-20261118-001B/MEET-ADDED-20261118-001B-E001_added/`. 5 gate checks pass (the engine's hash; the
referee's preview reproduced; MEET-HIST's unnamed and all-named shares at five reproduced; the starting pairs read the nesting at
k = 0; every arm invariant under renaming).

Cases: labelled KF3 tracking the added knots, from every bracketing of five and six (to k = 4) and seven (to k = 3): 61 cases.

## Predictions (frozen; equalities to 1e-6, strict inequalities by more than 1e-9)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | The 5 gate checks pass | any fails |
| Q1 | The added pairs alone carry less than a quarter of the states-alone share at every k ≥ 1 (restated from "at most 0.05" on the advisor's advice; it expects the bare share to rise) | at least a quarter somewhere |
| Q2 | The states with the added knots, as triples and with their middles, carry exactly the all-named share at every k (n0 = 5 to 7; one joint prediction, the advisor: about 0.8, not by construction without a peeling lemma) | a difference somewhere |
| Q4 | The states with the added pairs fall short of the states with the triples at some k ≥ 3, for each n0 (strictness; the gap shrinks with n0) | no shortfall for some n0 |
| Q5 | The states with the added pairs carry strictly more than the states alone at every k ≥ 2 | not strictly more somewhere |

(Q3, the middles adding nothing beyond the triples, is folded into Q2 on the advisor's advice.)

**What would count against the account.** Q2 failing would leave part of the order of growth outside even the added knots read
with the states.

## Runs and stop rule

The shared runner, 61 cases, 8 workers at 1.8 GB, registered as MEET-ADDED-B1; expected under half an hour. The study stops after
the read-out, A97's status, the decision note, the referee hand-off and the report.

**Advisor.** Consulted once before the freeze: probabilities Q1 about 0.25 (as first written), Q2 about 0.8, Q4 about 0.8, Q5 about
0.97; which bounds hold by construction; and to score the triple and middle equalities jointly.
