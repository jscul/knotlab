# A rule that never nests its fills

Epic `NEVER-NEST-20261118-001`, 18 November 2026, by Claude. It takes B197, from `MEET-ORDERS-20261118-001` (direction 2), after
`LOCAL-ROOM-20261118-001`, agreed with the coordinator. Goals G1 and G16; tests A99. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `d285dd83f` at 04:06:13 UTC.
- The run: E1, E2 and R2 from 04:06 to 04:28 UTC; R1 from 04:06 to 05:17 UTC.
- Proof: [proof.md](../../proofs/NEVER-NEST-20261118-001A/NEVER-NEST-20261118-001A-P001_refill/proof.md), N1 to N5 before the run,
  N6 after it.
- Code: [nnlib.py, run.py, checks.py and readout.py](../../experiments/NEVER-NEST-20261118-001B/NEVER-NEST-20261118-001B-E001_nest/).
- Results: [results.json.gz, readout.json and posthoc.json](../../artifacts/NEVER-NEST-20261118-001B/NEVER-NEST-20261118-001B-E001_nest/).
  `run.py --merge` writes results.json (14 MB); it is kept compressed, and its four parts, which it repeats exactly, are not kept.

## The answer

**Yes. The rule that takes only the fills keeping two orders, and otherwise lengthens the line by one subdivision, grows full
two-way grids and keeps two orders forever, in nearly every run, even with its knots confined to pairs that already share one
(computed to n = 40 from every bracketing of 5 to 8). Without that confinement it does so in every run, from every line (proved).
What these rules are given is the number two; nothing marks which split belongs to which order, and nothing is remembered. A local
version, which completes a corner only across two splits that cross, does the same once its first crossing reaches every split.**

- **NN, B197's rule: knots only on pairs that already share one** (R1, 254 runs to n = 40; E1 exact to n = 12).
  - Two orders at every step after the first fill, in every run and with probability 1 in the exact distributions, as the rule
    requires; it never stalls.
  - It fills like a grid. On steps 21 to 40 the median fill fraction is 0.80 at every start size, against 0.80 to 0.86 for a grid
    of these sizes that completes every row before the next. A full grid recurs at some n from 30 to 40 in 100%, 93%, 99% and 95% of runs from bracketings of 5,
    6, 7 and 8, and both chains grow after n = 20 in 86% to 93%. No run goes without a fill in steps 31 to 40.
  - Exact to n = 12: from bracketings of 5, a full grid at n = 12 with probability 0.85 (0.85 to 0.87 by bracketing), 0.82 from
    bracketings of 6; the expected fill fraction to n = 12 is 0.80, 0.93, 1.00 and 1.00 for starts of 5 to 8.
  - *Post hoc* (labelled; recomputed from the frozen traces): in 241 of the 254 runs every lengthening after the first full grid
    came at a full grid, so each new row or column was completed before the next began, as N3 proves for NNF. Of 1,262 such
    lengthenings, 23 came early, in 13 runs, and left a hole. 4 runs never reached a full grid by n = 40. Right after every
    lengthening at least one fill that keeps two orders was on offer (two or more in 1,124 of 1,290 cases). The advisor's
    one-way regrowth is real but rare.
  - It also takes fills of five and seven distinctions that keep two orders (316 of the 2,441 fills read while the line could be tracked), which Lemma C does not
    cover.
- **NN2 (any cost) is no different.** Two orders at every step, median fill fraction 0.80 to 0.83, a full grid at some n from 30
  to 40 in 93% to 100% of runs. It lengthens by steps of other kinds that add states where NN subdivides.
- **NNF (any pairs) and CC (corners across crossing splits): the proofs, checked.** From every line NNF reached a full grid before
  its first lengthening, at n ∈ {8, 9}, {10, 12}, {12, 15, 16} and {14, 18, 20} for 5 to 8 (N4), and then lengthened only at full
  grids, in 250 of 250 runs; from the 2 × 2 pattern NNF and CC did the same in 50 of 50 each (N3, N5). CC never fills a line.
- **CC after one fill of a line** reaches a full grid in 13, 6, 7 and 5 of 50 runs from lines of 5 to 8: *post hoc*, exactly
  the runs whose first fill has the line's two ends as its ends, which N6 (proved after the read-out) explains. A split the first
  fill leaves uncrossed is never crossed under CC.
- **The comparators.** KF3 leaves two orders in every run (λ = 5 to 7 at n = 40, as `CUBE-DOUBLING-20261118-001` proves). SUB
  keeps the line, with no fill. The class law matches NNF and CC from the 2 × 2 pattern: a full grid at n = 12 in 44, 45 and 45
  of 50, at n = 30 in 29, 32 and 31, with the same shapes at n = 40 (most often splits 6 and 5, then 7 and 4).

**In the owner's terms.**
- A law can grow a two-way grid without being handed the two orders. It is told only "never let a fill make a third order", and
  it reads that from the states.
- From any line, the free version fills the whole grid the line spans, then lengthens one row and fills it, forever (proved).
  When its knots must join distinctions that already share a knot, as B197 asked, it still does this in nearly every run
  (computed).
- What the earlier class law supplied split by split, which order each split belongs to, is read here from how the splits cross.
- What is still given is the number two. A law told to keep three would, as far as these arguments go, fill a three-way grid; no
  law here chooses two by itself.

## What each rule reads and what it is given

| Rule | Reads | Given |
| --- | --- | --- |
| NN (B197) | the states, and which pairs share a knot | the number two: the fills after which there are at most two orders |
| NNF | the states only | the number two |
| CC | two splits next to one distinction, and whether they cross | a first crossing |
| The class law (`LOCAL-ROOM-20261118-001`) | the states and a class for every split | the classes, by the start and by inheritance |

The number of orders, k and λ, is read from all the splits at once. Nothing marks which split belongs to which order, and nothing is
remembered from one step to the next: each rule's choice is a function of the present base. A rule told only to keep the number of
orders it has would never fill a line, since every fill of a line makes two (`STATE-RULES-20261117-001`, S4).

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | NN intermediate at every start size | **failed** | NN grows two-way grids at every start size by the frozen rule (median fill 0.80; full grid in 30–40 in 93–100%; both chains grow in 86–93%) |
| P2 | NN passes a full grid in ≥ half the runs, fewer from 8 than from 5 | held | 100%, 100%, 98.8%, 97.7% for 5 to 8 |
| P3 | NN median fill fraction on steps 21–40 in [0.25, 0.65] | **failed** | 0.80 at every start size |
| P4 | NN no fill in steps 31–40 in ≤ 15% of runs | held | 0% |
| P5 | NN2's median fill fraction below NN's | **failed** | 0.825, 0.80, 0.80, 0.80 against 0.80 each: equal or above |
| P6 | KF3 two orders at n = 40 in ≤ 10% of runs | held | 0%; λ = 5 to 7 |
| P7 | NNF (2 × 2 and every line) and CC (2 × 2): two orders at every step after the first, full grid after every completed row or column | held | 300 of 300 runs (a check of N3 to N5) |
| P8 | CC after one fill: a full grid in fewer than half the runs | held | 26%, 12%, 14%, 10% |

5 of 8 held. The three failures are one finding: the knot-sharing condition does not starve the rule, and NN grows like NNF. Both
of the advisor's forecasts (starvation, then holes and strips) and my own first expectation (starvation) were wrong.

## What the knot picture explained

- **Why the free rule never runs out.** In a two-way grid that is not full, the empty cell nearest the line, on either side, always
  has its two neighbours and their shared corner filled, and three knots complete the corner (N4). After a lengthening, every
  cell of the new row is the distinction that sides with the majority of three present ones (the literature's median), so the
  row fills (N3).
- **Why the corner rule needs a crossing that reaches every split.** Completing a corner across two crossing splits never makes
  a third split cross anything new (N6). A split that crosses nothing after the first fill stays apart forever, and the grid never
  closes.
- **Why the knot-sharing condition rarely bites.** Completing a cell of a new row needs two old neighbours in a row to share a
  knot (the end knots on the new distinction's own pairs do the rest). Earlier fills join each new cell to the cells it was
  completed from, so in a grown grid most neighbouring pairs already share a knot, and the refill goes through; the 13 runs with a
  hole are the exceptions.
- **Why a third order never appears.** A fill that keeps two orders sits in a cell of the grid of the two chains; the twisted
  corner, which would make two splits of one chain cross, is exactly the fill that is refused (N3 (i)).

Known mathematics, labelled: median graphs and the median of three in a product of chains, and the corner completion of a grid.
What this adds, in the program's terms: the second order's identity, which `LOCAL-ROOM-20261118-001`'s class law supplied split by
split, is read here from the states, once the law is told how many orders to keep.

## What it means for A99 and the goals

- **G1:** capability gained. A law that grows two orders and keeps them, filled, without end: proved for NNF from any line and
  CC from the 2 × 2 pattern, computed for NN (B197) from every bracketing of 5 to 8 to n = 40. What it is given is the number two
  (new A101).
- **G16:** capability gained. A shape is made by a rule that reads only the states (and, for NN, which knots meet), with the
  order each split belongs to read from the crossings.
- **A99** stays assumed; these laws sit on top of it. **A97** gains this study among the two-way laws: the grids grown here are
  the bases on which a two-way distance can now be read.
- **B197** is answered: the never-nest rule does not run out of fills.

## Limitations

- Exact distributions to n = 12 (NN) and n = 10 (NN2); runs to n = 40, one or two seeds per bracketing.
- NNF's and CC's courses are proved; their runs check the proofs and read the shapes.
- The rules are told the number two; no rule here picks it (A101).
- NN's growth past n = 40, and its 13 runs with holes and 4 without a full grid, are computed, not proved.
- Ties are uniform over knot sets for the knot-sharing rules and over distinct extensions for the others, as declared.

## Reproduce

```sh
cd experiments/NEVER-NEST-20261118-001B/NEVER-NEST-20261118-001B-E001_nest
../../../.venv/bin/python -B checks.py
for P in E1 E2 R1 R2; do ../../../.venv/bin/python -B run.py --part $P --procs 12; done
../../../.venv/bin/python -B run.py --merge && gzip -9 ../../../artifacts/NEVER-NEST-20261118-001B/NEVER-NEST-20261118-001B-E001_nest/results.json
../../../.venv/bin/python -B readout.py && ../../../.venv/bin/python -B posthoc.py
```

## Advisor

Consulted twice before the freeze.
- **First consultation** (on the design). It confirmed that the rule is well defined. It asked for the subdivide-only baseline, the
  fills available after each lengthening as a diagnostic, and the positive criteria. It predicted starvation: a bounded number of
  fills, then lengthening only.
- **Second consultation** (on N1 to N3 and the knot-sharing refill argument). It checked the lemmas and named their gaps:
  - N2's chains are canonical only once the crossing graph is connected.
  - Fills of five distinctions can complete what triples cannot.
  - N3 needs the minimal-empty-cell lemma before the first full grid, which became N4.

  It withdrew the starvation prediction: knot-sharing makes regrowth one-directional, so it expected intermediate growth with
  holes and strips. It gave P1 to P5 and the decision rule.

The CC rule, P8 and N5 were added after the second consultation, prompted by `LOCAL-ROOM-20261118-001`'s referee, and were not
reviewed by the advisor. It was not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a rule that never nests its fills (B197) | **Status:** Successful (referee pending), with 3 of 8 predictions failed | NN grows full two-way grids in nearly every run to n = 40; NNF does in every run, proved; CC does from a crossing that reaches every split |
| Local direction: holding two orders while filling | Promising | Held without per-split memory; the number two is still given |
| Broader exploration: a law that picks two orders by itself | Unexplored | Every law that holds two orders is told two, or handed a crossing |
| Long-term goal: G1 | Capability gained | A two-way grid grows forever from a line, read from the states |

**Next step:** Research directions. Directions 1 and 2 tie at the top and are independent; I recommend 1 next.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Who picks two? Tell NNF to keep at most d orders and test whether it fills full d-way grids (the proofs of N3 and N4 look as if they carry over); then look for a states-only rule told no number that settles at two | 3/3 | 2/3 | Prove or refute the d-way N3 and N4, and run d = 3 → stop at a rule that picks two, or an obstruction | Selected |
| 2 | A fully local rule from a bare line: CC with a first step read from the states (the fill whose ends are the line's two ends, readable as the distinctions every split separates) | 3/3 | 2/3 | Define the first step from the states, prove with N6 that CC then fills every grid → stop at a proof or a counterexample | Alternative |
| 3 | Why NN refills: prove that the new row's neighbouring pairs share knots, and explain the 13 runs with holes and the 4 without a full grid | 2/3 | 3/3 | Characterise the co-knotted neighbour pairs of NN's full grids → stop at a proof or the failing pattern | Alternative |
| 4 | The distance on a grown grid: does the pair-count distance on NN's and NNF's grids read as a two-way ruler (A97)? | 3/3 | 2/3 | Read the pair counts of the grown grids against the grid's own distance → stop at a ruler or its failure | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (capability gained) and a G16 checkpoint (capability gained); B197 answered; no goal changed.

**Assumptions:** new A101 (the number of orders kept is given, two); A99 and A97 gain this study among what rests on them.

**Basket:** read; B197 answered.
