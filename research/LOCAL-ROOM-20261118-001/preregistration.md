# A law whose free room runs only along two orders: pre-registration

Epic `LOCAL-ROOM-20261118-001`, 18 November 2026, by Claude, on the coordinator's queue. This is `CUBE-DOUBLING-20261118-001`'s
second direction. Goals G1 and G16; tests A99. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

The cheapest growth fills the cube because every missing combination of sides has a three-knot certificate. Is there a law whose
free room runs only along two orders, so the growth keeps two orders and fills them like a grid?

First candidate: a reach limit read from the states, under which every knot joins distinctions within r splits of each other.
Second, if the reach limit cannot do it: one remembered class per split. Then knots may only join distinctions whose separating
splits are of different classes, and a split made by subdividing another inherits its class.

## Ticket A: the proof (written before this freeze)

`proofs/LOCAL-ROOM-20261118-001A/LOCAL-ROOM-20261118-001A-P001_reach/proof.md`.
- **R1.** Within one split there is never a free fill.
- **R2.** Within two or more splits the cheapest growth still reaches the cube at every doubling.
- **R3.** No reach limit tells a grid's fill from a line's, so none keeps exactly two orders while filling cells.

## Ticket B: computations

`experiments/LOCAL-ROOM-20261118-001B/LOCAL-ROOM-20261118-001B-E001_local/`: `locallib.py`, `run.py`, `checks.py`, building on
`STATE-RULES-20261117-001B-E001`'s `rules.py` (pinned). Three checks pass before this freeze.
- **L1.** Exact class distributions of LF3(r), r = 1, 2, 3, from one knot and from the 2 × 2 pattern, to n = 14; 100 runs each to
  n = 20.
- **L2.** The class law from the 2 × 2 pattern, its two splits in two classes, with no pendants: 200 runs to n = 30.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | LF3(1): no zero-cost step ever. From one knot the line at every n with probability 1 (2n states); from the 2 × 2 pattern 2n − 2 states at every n (R1) | otherwise |
| P2 | LF3(2) and LF3(3): Q3 at n = 8 with probability 1 (exact), and Q4 at n = 16 in 100 of 100 runs, from both starts (R2) | otherwise |
| P3 | The class law: two orders (k = λ = 2) at every step of every run to n = 30, no stall, and a full grid ((a + 1)(b + 1) = n) at some n beyond 9 in every run (advisor) | otherwise |

The class law's balance between its two orders (the distribution of a and b) is read with no prediction. The advisor's
"exactly two splits apart" variant is not run.

**What would count against the headline.**
- A reach limit that keeps two orders (P2 fails with a two-order end): then a states-only law can hold two orders.
- A class-law run that leaves two orders: then even remembered classes do not suffice.

**The headline, stated before running.**
- A limit on how far a knot may reach, read from the states, either forbids every free fill or allows the cube.
- What holds two orders is a remembered distinction between them: each split remembers which order it belongs to. Given that
  memory, the cheapest growth fills a full grid and keeps two orders.
- The memory is handed over by the start, as the number of orders was in `STATE-RULES-20261117-001`.

## Runs and stop rule

`run.py --part L1` and `--part L2`, then `--merge`. The study stops after its read-out, followed by the decision note, the referee
hand-off and the report. The advisor was consulted before this freeze. It confirmed R1, gave R2's bootstrap reading and R3's
obstruction, and proposed the class law.
