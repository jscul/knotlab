# A cap on knots per distinction, and what matched starts remember

Epic `KNOT-CAP-20261117-001`, 17 to 18 November 2026, by Claude, on the coordinator's go-ahead. It takes the first direction of
`STATE-RULES-20261117-001`, that study's referee's lead, and the owner's question about erasure, passed on from Codex. Goals G1 and
G16; tests A97 and A99. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block, folded in on 18 November
(see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `3e41d8f11` at 23:58:38 UTC on 17 November. The five
  parts ran from 23:58:38 to 01:02:23 UTC.
- Proof: [proof.md](../../proofs/KNOT-CAP-20261117-001A/KNOT-CAP-20261117-001A-P001_caps/proof.md).
- Code: [caplib.py, run.py and checks.py](../../experiments/KNOT-CAP-20261117-001B/KNOT-CAP-20261117-001B-E001_cap/).
- Results: [results.json](../../artifacts/KNOT-CAP-20261117-001B/KNOT-CAP-20261117-001B-E001_cap/results.json).

## The answer

- **The two natural caps stop the cheapest growth exactly at its first two orders** (proved, and exact). A cap of three knots per
  distinction, or of two knots per pair of distinctions, lets one knot grow into the 2 × 2 pattern and then allows nothing more.
  - Looser caps let the growth past it:
    - four, five or six knots per distinction give a mixture that passes two orders, and four often stalls;
    - nine or more give the cubes again: Q3 at n = 8 in 200 of 200 runs and Q4 at n = 16 in 191 of 200 at nine.
  - No cap tried keeps two orders growing. At n = 16 none has two orders with at least four fills in a majority of its runs.
- **How the knots meet can change the number of orders, not only the bases** (exact). This revises the earlier reading from one
  pair of starts.
  - **The six-starts of `STATE-RULES-20261117-001`** (the line's 12 states, with a distinction in all four knots or in none):
    - the two starts' classes of states and knots carry the same multiset of probabilities through n = 9, and the number of orders
      is exactly the same there (two orders at n = 8: 51/140 from each); *scoped after the referee: their classes of states differ
      (14 against 15 at n = 8, 52 against 57 at n = 9), and the coarse counts by 0.0023 at n = 9;*
    - the first difference in the number of orders is at n = 10, and it is tiny (two orders 0.0027 against 0.0017);
    - the bases differ at once: at n = 7 each start has four classes of states, one shared, distance 3/4.
  - **The five-starts** (the line of five's 10 states, three knots each, the shared distinction at an end or in the middle) differ in
    the number of orders from the first fill: two orders at n = 7 with probability 5/12 against 11/18, and 3 against 4 orders at
    n = 10 in 52 : 48 against 42 : 58. *After the referee:* every three-knot presentation of that line has exactly one shared
    distinction, at an end, next to an end or in the middle; this study tested two of the three positions.
  - **Under a cap of five per distinction** the six-starts differ sharply as well: two orders at n = 10 in 181 against 95 of 300
    runs. *After the referee:* that is the degree cap reading the fan's hub (four knots against three at the start), so it is built
    into the cap and not separate evidence about the knots.
- **After the knots are erased the states remember, with a fading imprint** (exact). Grow with the knot-reading rule to n = 8, then
  forget the knots and continue from the states alone:
  - the six-starts' distance falls from 0.78 to 0.66, 0.52 and 0.41 at n = 9, 10 and 11, while with the knots kept it stays near
    0.7 (0.68 and 0.72 at n = 9 and 10);
  - the five-starts' falls from 0.65 to 0.46, 0.30 and 0.20, and by n = 14 it is near the sampling floor (sampled 0.06 against a
    floor of 0.05; p = 0.035). *Narrowed after the referee:* with the knots kept it fades too (0.65, 0.47, 0.40 at n = 8, 9, 10,
    against 0.65, 0.46, 0.30 erased).

  So for the six-starts the knots carry what the states only keep for a while. For the five-starts the difference fades with or
  without them, a little faster without.

**Which state differences.** At n = 7 the six-starts' classes found in one start only come in matched sets: three from each, all
with 12 states, 5 splits and two orders, with 1, 2 and 3 crossings. Every coarse count agrees, and the bases still differ: the
difference is where along the line the second order sits. For the five-starts the coarse counts themselves differ (distance over
features 0.67 at n = 6, falling to 0.12 at n = 10).

**In the owner's terms.**
- The first contact past one knot, the square, is where the two natural limits on contacts stop. Logic's cheapest continuation and
  its tightest local limits meet at two orders, and nothing grows past them.
- Looser limits do not hold two orders; they let the growth run on.
- How the knots meet is information the states do not hold. It changes which shapes grow, and for some starts how many orders they
  have.
- When the knots are forgotten, the states keep a fading memory of how they met. For the six-starts the fading is the erasure's;
  for the five-starts the difference fades with the knots kept as well.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| C1 | c = 3 and the pair cap from one knot: the 2 × 2 pattern at n = 4, then a stall, each with probability 1 | held | exact; 200 of 200 runs for the pair caps |
| C2 | c = 4: no stall at n = 5; at n = 16 at most 3 fills, no cube, two orders in a majority | **failed** (last clause) | no stall at 5, at most 2 fills, no cube; but 88 of 200 runs stall by n = 16 and only 32 of the other 112 have two orders: costlier single knots add orders |
| C3 | c = 5: no Q3 at 8; c = 6: Q3 at 8 in under half, no Q4; c = 9: Q3 at 8 in a majority, Q4 at 16 in a minority; c = 12: Q3 at 8 in a majority | **failed** (one clause) | 0; 28 of 200 and no Q4; 200 of 200, but Q4 in 191 of 200, a majority; 200 of 200 |
| C4 | No rule: two orders with at least 4 fills at n = 16 in a majority | held | none (most: c = 4, 32 two-order runs with at most 2 fills) |
| C5 | Six-starts: equal two-order probability at 8; distance 3/4 at 7 and at least 0.7 through 10; features at most 0.03 | **failed** (one clause) | equal (0.3643); 3/4; but 0.677 at n = 9; features at most 0.0027 |
| C6 | Five-starts: distance 0 at 5, at least 0.5 at 6, at least 0.6 through 10; two-order probabilities equal | **failed** | 0; 0.667; 0.722, 0.651, then 0.470 and 0.399; two orders 0.417 against 0.611 at n = 7 |
| C7 | Sampled six-starts at n = 7, 8: distance above both floors, permutation p < 0.01; two-order counts equal within 3 standard errors | held | 0.744 and 0.793 against floors under 0.08, p = 0.005 (the least 200 shufflings give); 362 and 363 at n = 8 |
| C8 | Erasure: non-increasing, still positive at n = 9, 10, 11 for the six-starts | held | 0.779, 0.655, 0.522, 0.414 |
| C9 | c = 5 and 6 from the six-starts: under 5% stall by n = 12 | **failed** (c = 5) | c = 5: 34 and 51 of 300; c = 6: none |

4 of 9 held. The failures were mostly the advisor's quantitative predictions:
- one-knot growth under a cap keeps its orders;
- Q4 is rare at nine;
- the distance stays above 0.7;
- equal numbers of orders for the five-starts;
- few stalls at five.

The proved statements (C1, C8) and the main negative (C4) held.

The exploratory parts gave the following.
- The pair cap with knot-locality grows an exact line from both six-starts: one order at every step, in 300 of 300 runs.
- Sampled after erasure, the six-starts' distance is swamped by the floor from n = 11 on (p = 0.71 at n = 12), as warned.

## What the knot picture explained

- **Why the tight caps stop at the square.**
  - The square's four knots use every distinction three times and every pair twice.
  - Any new knot must take two old distinctions, so it breaks both limits at once.
  - The square is the knot pattern that is complete in both senses.
- **Why looser caps do not hold two orders.** When the cap blocks the free fills, the cheapest allowed single knot is no longer a
  subdivision or a pendant, which keep the orders (`STATE-RULES-20261117-001A`, S2). It is a costlier knot between distinctions
  further apart, and that doubles two splits at once and can make a new crossing.
- **Why erasure fades.** A rule that reads only the states cannot increase the difference between two distributions of states
  (proved, T4). Each step merges some of the classes the two starts reach separately.

Known mathematics, labelled: data processing for total variation. Local: the stops, the comparisons and the erasure curves.

## What it means for A97, A99 and the goals

- **A97** stays under challenge, with a positive finding: how knots meet is information the states lack, enough to change what
  grows and, from the five-starts, how many orders. The states keep a fading imprint of it (the fading due to erasure shown for
  the six-starts).
- **A99** (the move set) stays assumed. The caps were added on top of it.
- **G1:** obstruction learned. The natural caps stop at two orders without growing them, and looser caps pass them.
- **G16:** capability gained. Exact distances between matched starts, with and without the knots, and the rate at which the states
  forget.

## Limitations

- Two matched pairs, one knot rule (knot-local fewest states) for the comparisons, and caps on degree and on pairs only.
- Exact counts reach n = 10 or 11, and runs n = 12 to 16.
- The "which state differences" reading uses classes and coarse counts. A finer description of where the fills sit is left for a
  follow-up.

## Reproduce

```sh
cd experiments/KNOT-CAP-20261117-001B/KNOT-CAP-20261117-001B-E001_cap
../../../.venv/bin/python -B checks.py
for P in K1 K2 K3 K4 K5; do ../../../.venv/bin/python -B run.py --part $P; done
../../../.venv/bin/python -B run.py --merge
```

## Advisor

Consulted twice before the freeze. It derived the cap predictions and T3's bound and proposed the pair cap. It retracted its first
account of the six-starts and gave the matched-start and erasure predictions, with the design fixes: the floor with permutation
tests, the no-erasure control, three kinds of distance and the table of classes in one start only. Its exact value of 3/4 at n = 7
held. Five of its quantitative predictions failed (above). Not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh exact code (rational propagation,
nothing shared with `caplib.py` or `rules.py`): confirmed with fixes, no Block.
- T1 to T4 are proofs. The referee's exact run agrees for the degree cap of three and the pair cap of two, with and without
  locality.
- The six-starts' order distributions are identical through n = 9 (two orders 51/140 at n = 8 and 9409/339822 at n = 9), and the
  first difference at n = 10 is confirmed (0.0027098 against 0.0017223).
- The five-starts' 5/12 against 11/18 at n = 7, and 173/6552 against 233/2457 at n = 8, reproduce.
- The exact erasure values carry no floor, so the fade is real.

Folded in the same day, each item logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing.** For the five-starts the kept control fades too (0.65, 0.47, 0.40 against erased 0.65, 0.46, 0.30). Only for the
   six-starts is the fading due to the erasure.
2. **Not a block.** "Correspond class for class" overstated it. What matches is the multiset of probabilities of classes of states
   and knots, and the order distributions. The classes of states differ (14 against 15 at n = 8), and the coarse counts by 0.0023
   at n = 9.
3. **Not a block.** A three-knot line of five has its one shared distinction at an end (120 labelled presentations), next to an end
   (120) or in the middle (60). Two of the three positions were tested.
4. **Not a block.** The c = 5 difference between the six-starts is the cap reading the fan's hub, built in, not separate
   evidence.
5. **Not a block.** The scoped `STATE-RULES-20261117-001` sentence gains "with a tiny difference from n = 10", and this note's
   Corrections line, which said "none", now names the Narrowing logged at the close.

The sampled six-start values are at the floor from about n = 10 (sampled 0.715 against the exact 0.522), as the note said.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a cap that stops growth at two orders | **Status:** Successful, with mixed predictions (referee pending) | The tight caps stop exactly at the 2 × 2 pattern (proved); looser ones pass it; none keeps two orders growing; 4 of 9 held |
| Local direction: how knots meet, against the states | Promising | Exact: it changes what grows, and for the five-starts and under a cap how many orders; the states keep a fading imprint |
| Broader exploration: a law that grows exactly two orders | Unexplored | The tight caps stop, the loose ones run on; nothing in between grows a grid |
| Long-term goal: G1 | Obstruction learned | No local limit tried grows two orders and keeps them |

**Next step:** Research directions. The coordinator has queued S6 next.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | S6: prove that the cheapest growth gains one order at each doubling (every missing combination is filled before a new split is needed), or find a reachable exception | 3/3 | 3/3 | Contract first; prove forceability of every unoccupied orientation from both N + 2 classes → stop at a proof or a counterexample | Selected (coordinator) |
| 2 | Why the five-starts differ in the number of orders: an exact account of end hub against middle hub at the first fill | 2/3 | 3/3 | Enumerate the first two steps from both and explain the 0.417 against 0.611 → stop at the explanation | Alternative |
| 3 | The forgetting rate: does the distance after erasure fall geometrically (about ×0.8 per step for the six-starts, ×0.67 for the five-starts), and what sets the rate? | 2/3 | 2/3 | Exact to n = 12 for both pairs → stop at a rate law or its failure | Alternative |
| 4 | The 3 × 1 weave pair with the twist fixed and the ruler measured | 2/3 | 3/3 | Queued by the coordinator after S6 | Alternative |

**Corrections:** one (Narrowing), logged at the close: `STATE-RULES-20261117-001`'s "the knots change what grows, not how many
orders" holds for its six-starts (exactly through n = 9, with a tiny difference from n = 10), not in general. *Corrected after the
referee: this line first said "none".*

**Goals:** a G1 checkpoint (obstruction learned) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 under challenge, with this positive finding; A99 unchanged; no new entry.

**Basket:** read; nothing taken.
