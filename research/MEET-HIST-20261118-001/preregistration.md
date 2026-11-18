# Can the order of growth be read from a grown base without names?: pre-registration

Epic `MEET-HIST-20261118-001` (`MEET-DIST-20261118-001#1`, regraded after its referee's Block; goal G16; tests A97), 18 November
2026, by Claude, on the coordinator's go-ahead. Frozen before the run. The canonical K1–K3 test is unchanged.

## The question

`MEET-DIST-20261118-001`'s referee found that one grown base's states (equivalently, its disagreement counts), read on unnamed
distinctions, carry part of how the line's knots nest, and read with the distinctions' names carry all of it at five. Which names
carry the rest: knowing which distinctions are the line's, or the order in which the new ones came? And is that order readable
from the grown base?

## In standard terms

For a KF3 growth from a presentation P, one grown split system read at four levels of labelling (none; the original points
labelled; the added points labelled by arrival; all labelled), the mutual information of each with the presentation's
unlabelled rooted binary tree, and the conditional entropy of the arrival order given the other readings.

## Prior work in the program

`python3 -B scripts/track.py objects "names of distinctions, order of growth, grown disagreement counts, presentations of a line" --until 2026-11-18 --exclude MEET-HIST-20261118-001`

`python3 -B scripts/track.py objects "history versus distance, order in which distinctions were added, information carried by labels" --until 2026-11-18 --exclude MEET-HIST-20261118-001`

- `MEET-DIST-20261118-001`: same object; the unnamed shares and the referee's named shares this study decomposes.
- `MEET-GROW-20261118-001` and `MEET-ORDERS-20261118-001`: the same growth and population (relatives).
- `DISTANCE-INFO-20261117-001`: A97 tested on not-all-equal bases (a relative, no growth).
- `TOP-INFO-20261114-001`: unrelated (bonds of covered copies).

## Settled by construction (stated, not tested)

- **Through the knots.** The grown base's knots include the presentation's own, so reading which knots meet gives the nesting at
  once, at every k. The question is about the states (equivalently, by `DISTANCE-ORDER-20261117-001`'s 3(a), the distances).
- **Naming the order names the line** (the advisor). Marking which distinctions are new and their order leaves the line's
  distinctions as an anonymous set, a chain of nested cuts that the states order up to reversal; so "the order named" equals "all
  named" (checked as a sanity row, not a prediction). For the same reason "the line named" equals "which distinctions are the
  line's known".
- So the readings form a chain: unnamed (U) → which distinctions are the line's (NL) → the order of growth among the new ones too
  (N).

## Exploration before this freeze (disclosed)

The smoke test on five: shares U 0.60, 0.39, 0.22; NL 0.70, 0.69, 0.51; N (and NO) 1.0 at k = 2, 3, 4. The referee's six:
NL 0.67, 0.71 and N 0.83, 0.91 at k = 2, 3.

## Ticket B: computations

Code: `job.py`, `checks.py` and `merge.py` with `melib.py` (MEET-ORDERS-20261118-001B's engine, unchanged) in
`experiments/MEET-HIST-20261118-001B/MEET-HIST-20261118-001B-E001_names/`. 4 gate checks pass (the engine's hash; the unnamed
reading equals the engine's state classes; each reading invariant under its allowed renamings and the line's reversal; the
referee's named shares at five reproduce).

Cases: labelled KF3 from every bracketing (weight 1, so the prior is uniform over labelled presentations) of 5, 6, 7 (to k = 4)
and 8 (to k = 3): 193 cases.

## Predictions (frozen; ties count as failures)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | The 4 gate checks pass | any fails |
| H1 | The order of growth is not readable from the grown states even with the line's distinctions named: H(N \| NL) > 0 at every k ≥ 2 (n0 = 5 to 8) | 0 at some k ≥ 2 |
| H2 | The order of growth adds to the named line: share(N) > share(NL) at every k ≥ 2 | not strictly greater somewhere |
| H3 | Knowing which distinctions are the line's adds to the unnamed: share(NL) > share(U) at every k ≥ 2 | not strictly greater somewhere |
| H4 | The order of growth carries more than knowing the line's distinctions: share(N) − share(NL) > share(NL) − share(U) at every k ≥ 2 | not strictly greater somewhere |

Sanity row (by construction, not scored as a prediction): share(NO) = share(N) at every k ≥ 1.

**What would count against the account.** H1 failing would make the order of growth readable from named states; H4 failing would
put most of the missing share in knowing which distinctions are the line's, not in the order.

## Runs and stop rule

The shared runner, 193 cases, 12 workers at 1.2 GB, registered as MEET-HIST-B1; expected under half an hour. The study stops after
the read-out, A97's status, the decision note, the referee hand-off and the report.

**Advisor.** Consulted once before the freeze: H4 as first written (the order named alone equals all named) holds by construction,
so it became the sanity row and the present H4 replaced it; probabilities about 0.97 (H1, implied by strict H2), 0.88 (H2), 0.90
(H3); and ties scored as failures.
