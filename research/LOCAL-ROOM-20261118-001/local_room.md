# A law whose free room runs only along two orders

Epic `LOCAL-ROOM-20261118-001`, 18 November 2026, by Claude, on the coordinator's queue. It is `CUBE-DOUBLING-20261118-001`'s
second direction. Goals G1 and G16; tests A99. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block,
folded in on 18 November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `d031243aa` at 02:06:53 UTC.
- The run:
  - L1 ran from 02:06:53 to 02:16:50 UTC.
  - L2 finished at 02:44 but failed to write its output (tuple keys in JSON). Amendment 1 (`60e7df863`), recorded before any
    read-out of L2, fixed the writing only.
  - L2 was rerun with the same seeds, from 02:45 to 03:21:46 UTC.
- Proof: [proof.md](../../proofs/LOCAL-ROOM-20261118-001A/LOCAL-ROOM-20261118-001A-P001_reach/proof.md).
- Code: [locallib.py, run.py, checks.py and posthoc.py](../../experiments/LOCAL-ROOM-20261118-001B/LOCAL-ROOM-20261118-001B-E001_local/).
- Results: [results.json and posthoc.json](../../artifacts/LOCAL-ROOM-20261118-001B/LOCAL-ROOM-20261118-001B-E001_local/).

## The answer

**A limit on how far a knot may reach, read from the states, does not give a filled two-way grid. Within two splits the
cheapest growth still makes cubes. Within one split it never fills, yet once its first steps make two orders, they persist and
in most runs both keep growing, sparsely. A remembered class per split does: under it the cheapest growth fills a full two-way
grid and keeps two orders forever, in every run.** The classes are handed over by the start, as the number of orders was before.
*Narrowed after the referee:* what this shows is that two orders need more than a reach limit. A rule that reads more of the states,
such as which side of the crossing graph a split is on, is not excluded, and `NEVER-NEST-20261118-001` tests one.

- **Within two or three splits: the cube, as proved.** LF3(2) and LF3(3) reach Q3 at n = 8 with probability 1 and Q4 at n = 16 in
  100 of 100 runs, from one knot and from the 2 × 2 pattern (R2). They differ from the unlimited rule between doublings (two
  orders at n = 6 with probability 2/3 within two splits, against 1/2), not at them.
- **Within one split: no free fill, and the orders freeze after the first steps** (R1, and computed exactly to n = 14).
  - Every step adds exactly two states: 2n from one knot and 2n − 2 from the 2 × 2 pattern, as R1 requires.
  - The first two steps can still make more orders. Steps of two or three knots, each on an adjacent pair, can copy an inner
    distinction (a branch) or double a split with the new distinction on the far side of another (a crossing). The pre-registered
    "the line at every n" was wrong.
  - From n = 5 on, the distribution of kinds never changes again, at any n to 14 (exact) and to 20 (100 runs):

    | From | A line | A branching tree | Two orders | Three orders |
    | --- | --- | --- | --- | --- |
    | One knot | 30.3% | 22.7% | 45.5% | 1.5% |
    | The 2 × 2 pattern | 0 | 0 | 87.8% | 12.2% |
  - **What persists when two orders form** (post hoc, labelled; the frozen runs recomputed from their seeds). In most runs both
    orders keep growing. In the 45 two-order runs from one knot, the shorter of the two chains of nested splits has mean length
    1.9, 2.8, 4.1 and 5.8 at n = 6, 10, 14 and 20. The longer has median 3, 6, 9 and 13, and the crossings grow from 2 to 44. From
    the 2 × 2 pattern it is the same: 1.7 to 5.6, and 2 to 42 crossings.
    *Scoped after the referee:* these chains come from a largest matching, which also places the splits that cross nothing, and
    places them arbitrarily, so the shorter chain is inflated. Read by the crossing graph's two colour classes (300 runs per start),
    the shorter class has mean 1.24, 2.02, 2.87 and 4.20 at n = 6, 10, 14 and 20, and the crossings have median 3, 10, 20 and 56.
    At n = 20, in 22 of 131 two-order runs from one knot (about one in six) the shorter class is still a single split: a long chain
    crossed once. From the 2 × 2 pattern, 9 of 252.
  - But no cell is ever filled: each new distinction adds a split, so n distinctions carry n − 1 splits from one knot (n − 2 from
    the 2 × 2 pattern). A filled grid of the same size carries only about 2√n. It is the thinnest two-way growth there is, two
    orders woven as sparsely as possible.
- **The class law** (one remembered class per split; knots only across splits of different classes; a subdivided split keeps its
  class): from the 2 × 2 pattern, its two splits in two classes, 200 runs to n = 30.
  - Every run has two crossing orders at every step, and none stalls.
  - Each new row or column is filled completely before the next is started, so every run passes through full grids
    (a + 1)(b + 1) = n: 2 × 3 at 6 in all 200, then 3 × 4 at 12 in 166, and 5 × 6 or 3 × 10 at 30 in 100.
  - There is no pull toward balance. At n = 30 the class counts (a, b) range from (2, 11) to (10, 2), most often (4, 5) and (5, 4).
  - Twisted corners, which would make a third order, are never allowed: they need a knot across two splits of the same class.
  - *Scoped after the referee:* two orders are close to built in. The start hands over the two classes, the ban on knots within one
    class is exactly the ban on the twisted corner (R3), and the ban on pendants keeps every split classed. What the law grows is
    the rest: no stall, each row or column completed before the next, and varied grid shapes. As in `GRID-GROW-20261117-001`'s
    Block, the second order's identity is supplied, not read. Row completion and "a full grid beyond n = 9" are computed (200 of 200
    runs, and the referee's own implementation agrees), not proved.

**Why no reach limit can do better** (R3, proved). The fill of a grid's cell uses the same reaches as the fill that makes a second
order from three consecutive distinctions of a line. A limit read from the states sees only those reaches, so it allows both or
neither: the cube, or no fill.

**In the owner's terms.**
- A limit on reach read from the states cannot pick out two orders: the corner of a square and three points in a row look the same
  to it.
- Under the tightest reach, two orders that form in the first steps last forever, and both keep growing, but nothing is ever filled
  in: the two orders are woven as thinly as possible.
- What holds two orders and fills them, among the laws tried here, is memory: each split remembers which of the two orders it
  belongs to, and knots may only join across the two. Given that, the cheapest growth builds a full grid, row by row, forever. The
  memory itself is given at the start, two classes from the first square. *After the referee:* this shows that two orders need
  more than a reach limit, not that they need memory. A rule reading the crossing graph is untested here.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | LF3(1): no zero-cost step; the line at every n from one knot (2n states); 2n − 2 states from the 2 × 2 pattern | **failed** (the line clause) | no zero-cost step and the state counts as predicted; but the line has probability 0.30 from n = 5 on |
| P2 | LF3(2), LF3(3): Q3 at 8 (probability 1), Q4 at 16 in 100/100, both starts | held | exact and 100/100 for all four |
| P3 | The class law: two orders at every step of every run to 30, no stall, a full grid beyond n = 9 in every run | held | two orders at every step of all 200 runs; no stall; full grids along every run. The per-run "beyond n = 9" follows from the completion of each new row (post hoc argument, consistent with the counts by n: 166 full at 12, 100 at 30) |

P1's failure is the study's main surprise: R1 forbids free fills, not new orders. I had assumed that the cheapest single-knot
steps (subdivisions) were the only cheapest steps, but steps of several knots on adjacent pairs cost the same and can branch or
cross.

## What the knot picture explained

- **Why reach cannot select two orders.** A knot sees only how far apart its distinctions are. A cell's corner and three points in
  a row have the same distances.
- **Why the orders freeze within one split.** With no free fill, every step pays for a new split. Under the class law a fill is allowed only across splits of different classes, so a new row's cells fill one after
  another, each beside a filled row and column, and the twisted corners (a knot across two splits of one class) are never
  allowed.

## What it means for A99 and the goals

- **G1:** obstruction learned for reach limits (proved), and a near miss: the thinnest two-way growth persists under the tightest
  reach, in most runs with both orders growing.
- **G16:** capability gained. The class law grows a full two-way grid forever, the first law in this line that holds two orders and fills them; it
  needs one remembered bit per split.
- **A99** stays assumed; the laws here sit on top of it.

## Limitations

- Reach limits read from the states, and one class law; other memories are not tried.
- Exact counts to n = 14; runs to 20 (reach) and 30 (class law).
- "What persists" is post hoc, recomputed from the frozen seeds.

## Reproduce

```sh
cd experiments/LOCAL-ROOM-20261118-001B/LOCAL-ROOM-20261118-001B-E001_local
../../../.venv/bin/python -B checks.py
../../../.venv/bin/python -B run.py --part L1 && ../../../.venv/bin/python -B run.py --part L2 && ../../../.venv/bin/python -B run.py --merge
../../../.venv/bin/python -B posthoc.py
```

## Advisor

Consulted before the freeze. It:
- confirmed R1;
- gave R2's bootstrap reading and R3's obstruction;
- proposed the class law.

It also expected the 2 × 2 start under the reach of one to open into a path of states. Not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh code: confirmed with fixes, no Block.
- R1 and R3 are correct. R2 holds under every tie rule: an exhaustive enumeration of every reachable class at reach 2 and 3, from
  one knot and from the 2 × 2 pattern, finds Q₂ to Q₅ at 4, 8, 16 and 32 as the only class, one doubling past the study's runs.
- The reach-one exact kinds reproduce (10/33, 5/22, 5/11 and 1/66 from one knot; 137/156 and 19/156 from the 2 × 2 pattern), and
  the kinds freeze run by run, from n = 5 for one knot and n = 6 for the 2 × 2 pattern.
- The class law, reimplemented from the note's words: two orders at every step of 200 of 200 runs, no stall, a full grid after
  n = 9 in every run, and no new split before the grid is full.

Folded in the same day, each logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Not a block.** R2's proof said that for s ≥ 3 only subdivisions are allowed. Pendants are allowed too (8 of Q₃'s 20 cheapest
   extensions under reach 2), and the proof's own bootstrap at s = 2 covers them at every s. The proof is repaired.
2. **Narrowing.** "Two orders need a remembered distinction" is shown only against reach limits; it now reads "need more than a
   reach limit", and a rule reading the crossing graph is named as untested. `NEVER-NEST-20261118-001` tests such rules.
3. **Not a block.** Under reach one, both orders keep growing in most runs, not all: in about one in six from one knot, one order is
   still a single split at n = 20. The matching-based chains count splits that cross nothing. The 2 × 2 start has n − 2 splits.
4. **Not a block.** The class law's two orders are close to built in, and its row completion is computed, not proved.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a law whose free room runs along two orders | **Status:** Successful, with one failed prediction (referee pending) | Reach limits cannot (proved); one remembered class per split can, and grows full grids forever; 2 of 3 held |
| Local direction: holding two orders | Promising | The class law holds them with memory; the thinnest two-way growth persists under the tightest reach |
| Broader exploration: two orders without handed-over memory | Unexplored | Whether a knot-reading rule (never nesting fills, B197) can do what the class law does |
| Long-term goal: G1 | Obstruction learned for states-only reach; capability gained with memory | Two orders need more than a reach limit (narrowed after the referee from "a remembered distinction between them") |

**Next step:** Research directions. The first starts next, agreed with the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A rule that never nests its fills (B197, from `MEET-ORDERS-20261118-001`): does reading the knots' bracketing do what the class law's memory does? | 3/3 | 2/3 | Freeze the never-nest rule against the class law and the plain knot-local rule → stop at the orders each keeps | Selected |
| 2 | Why the orders freeze within one split: a conservation proof for LF3(1) after its first steps | 2/3 | 3/3 | Prove that every cheapest step at reach one keeps k and λ once n ≥ 5 → stop at a proof or a counterexample | Alternative |
| 3 | The class law from one knot: can the classes be read, not given? | 3/3 | 1/3 | Look for a rule that assigns a class to a split from the states or knots at its birth → stop at one or an obstruction | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (obstruction learned for reach; capability gained with memory) and a G16 checkpoint (capability
gained); no goal changed.

**Assumptions:** A99 unchanged; no new entry.

**Basket:** read; B197 taken next.
