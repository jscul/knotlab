# Who picks the number of orders

Epic `PICK-TWO-20261118-001`, 18 November 2026, by Claude. It takes `NEVER-NEST-20261118-001`'s first direction, chosen by the
coordinator. Goals G1 and G16; challenges A101. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block,
folded in on 18 November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `f13d6ac35` at 05:51:59 UTC.
- The run: C1 to C3 from 05:52 to 06:21 UTC; C4 from 05:52 to 08:03 UTC.
- Proof: [proof.md](../../proofs/PICK-TWO-20261118-001A/PICK-TWO-20261118-001A-P001_sources/proof.md).
- Code: [picklib.py, run.py, checks.py and readout.py](../../experiments/PICK-TWO-20261118-001B/PICK-TWO-20261118-001B-E001_pick/).
- Results: [results.json.gz and readout.json](../../artifacts/PICK-TWO-20261118-001B/PICK-TWO-20261118-001B-E001_pick/).

## The answer

**No rule here chooses two out of nothing. The number of orders is handed over by a cap, a price or the start, or it comes from
one move: a single fill on a line always makes exactly two orders, because one new distinction has two sides (proved). A rule that
takes one free fill while nothing crosses and is conservative afterwards settles at two from every line, with full two-way grids
recurring, and from a three-way start it keeps three.** So the two that can be had without naming it is one plus one: the line's
one order, and the one order that a single new distinction adds.
*Narrowed after the referee:* SEED names no number of orders. It allows one free step and then conserves. Arity makes that step one
order, and the line has one. The rule chooses the one step; arity chooses one order per step. The line start is needed too: from
an uncrossed tree that branches, one fill keeps k = 2 but can give λ = 3 (28 of 52 fills on the spider with four legs of two),
since a tree's λ is already ⌈leaves / 2⌉.

- **A cap of d gives exactly d** (C1). With "at most three orders", every run from lines of 5 to 8 reached λ = 3 and never
  exceeded it. It filled a full three-way grid before its first subdivision, at n = 12 from a line of five (3 × 2 × 2), at 16 or 18
  from six, at 24 or 27 from seven, and at 24 to 36 from eight. It then passed through two or more full three-way grids by n = 60
  in every run. With "at most four", every run reached λ = 4 and full four-way grids. The cap is the dimension.
- **A price picks through its increments** (C2, C3), as S5 proves.
  - Linear in λ: at w = 1.0 and 1.9, λ = 5 at n = 40 from a line of five and 4 from eight, gaining an order at every full grid.
    At w = 2.1 and 3.0 the line never leaves one order. At the tie w = 2.0, λ ends at 3 to 5.
  - Quadratic: w = 0.25, 0.35, 0.5 and 1.0 settle at exactly 4, 3, 2 and 1 orders, in every run, from both lines.
  - So a price can hold two, with full two-way grids recurring at w = 0.5, but only because 0.4 ≤ w < 2/3 is written into it.
- **The rules told no number** (C4; lines of 5, 6, 7, 8, 10 and 12, 20 runs each):

  | Rule | Two orders at every step after the first fill | Full two-way grids, three or more, every later subdivision at one | From Q₃ and the 3 × 3 × 3 grid |
  | --- | --- | --- | --- |
  | KEEP (fewest orders first) | never fills: one order | — | keeps 3 |
  | CC (corners across crossing splits) | never fills: one order | — | keeps 3 |
  | NEWCROSS (no new crossing between crossed splits) | in 80% of runs from five, 30% from eight to twelve; others reach 3 or 4 | 5 to 45% | keeps 3 |
  | FRESH (crossings only between splits that crossed nothing) | every run | 0 to 30% (separate blocks) | keeps 3 |
  | ODD (no odd cycle of crossings) | every run | every run | keeps 3 |
  | SEED (one free fill while nothing crosses, then copy or conserve) | every run | every run | keeps 3 |

  - **SEED** names only "crosses nothing". Its first fill makes exactly two orders from any line (S6). Afterwards it adds
    crossings only by giving an uncrossed split the crossers of a crossed one (S7). It then fills full two-way grids, and keeps
    filling them, at every line length. The first full grid comes at n = 8 or 9 from five, and at 30 to 42 from twelve.
  - **ODD** does the same. But "no odd cycle" is two-colourability. On these bases it is the cap of two (the advisor's argument:
    λ equals the largest set of pairwise crossing splits on every base reached, which held at every step of every run here), so
    its two is the parity's.
  - **Every rule conserved three from the three-way starts.** None of them stops at two from above: λ never decreases (S1).

**In the owner's terms.**
- Told how many orders to keep, a rule keeps that many, whatever the number. Told a price, it keeps the number the price works out
  to.
- With neither, a rule that only keeps what it has stays a line.
- The one way to two without saying "two" is to allow a single free step from the line and then only conserve. Because a new
  distinction has two values, that one step always splits the line's order into exactly two, never more. After that, the grid
  fills and grows. Started from three orders, the same rule keeps three.
- So the rule chooses one step, arity makes that step one order, and the line supplies the first order (wording after the
  referee).

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | CAP(3) from lines of 5–8: λ reaches 3, never more; a full 3-grid before the first subdivision; ≥ 2 full 3-grids by 60 in ≥ 90% from 5 and 6 | held | every run; first full 3-grids at 12, 16/18, 24/27, 24–36; two or more in 100% |
| P2 | CAP(4) from the line of 5 and Q₄: λ reaches 4, never more | held | every run, also from the line of 8 |
| P3 | Linear price: 2.1 and 3.0 keep one order; 1.0 and 1.9 reach λ ≥ 4 by 40 from five; 2.0 grows past 2 in most runs | held | λ = 5 at 40 from five; one order; at 2.0 every run ends at 3 to 5 |
| P4 | Quadratic price settles at 4, 3, 2, 1 for w = 0.25, 0.35, 0.5, 1.0 | held | every run, both lines |
| P5 | ODD behaves as NNF | held | strong at every line length |
| P6 | FRESH weak at every length, not strong | held | strong in 30% at most |
| P7 | NEWCROSS from eight: fewer than half end at two | held | 6 of 20 |
| P8 | SEED strong at every length, keeps 3 from the controls | held | every run |
| P9 | KEEP and CC: one order from lines, three from the controls | held | every run |

9 of 9 held. The predictions were mostly the advisor's, given before the freeze. The study's answer rested on the definition of
"told no number", which was frozen first.

## What the knot picture explained

- **Why one fill makes exactly two.** On a line every pair of cuts is nested. A new distinction lies inside some cuts and outside the
  rest, and only pairs with one cut of each kind can come to cross. That makes the new crossings two-sided, so each kind stays one
  order (S6).
- **Why caps and prices decide.** Any full grid that is not a cube has a twisted corner, a fill that raises the orders by exactly
  one (S4). So every grid offers the next order for free, and only the rule's price or cap says whether to take it (S5).
- **Why conservation keeps the start.** A corner across crossing splits never fills an empty intersection, so nothing nests
  differently and nothing new crosses (S2).

Known mathematics, labelled: lattice dimension (Eppstein), Dilworth's chain cover, perfect crossing graphs and medians. What this
adds, in the program's terms: the number of orders is a parameter of the law, unless it comes from the start and one move, and
the program's line start plus one distinction's two values gives exactly two.

## What it means for A101 and the goals

- **A101** is under challenge. The number two can come without being named, from the start's one order and one fill's two sides
  (SEED). That source is still not the rule's choice: from three orders the same rule keeps three. *After the referee:* what SEED is
  given is one order-making step; its number is the start's λ + 1 from an uncrossed line, and the start's λ otherwise.
- **G1:** capability gained. A rule told no number grows full two-way grids forever from every line, and the sources of the number
  are mapped: cap, price, start, parity and arity.
- **G16:** capability gained. Caps of three and four grow full three- and four-way grids. The number of orders is shown to be the
  law's parameter.
- **A99** stays assumed. λ equals the largest set of pairwise crossing splits on every base reached (not in general: trees) (the advisor's argument; computed
  here, not proved).

## Limitations

- Runs to n = 60 (n = 40 for prices), 10 to 20 per start; SEED's and FRESH's two orders after the first fill are proved for k (S7)
  and computed for λ.
- Rules that subdivide on a line stop at 62 states (n = 31), the fill enumeration's limit. They were proved to stay a line.
- "Told no number" admits ODD, whose "odd" is two-colourability; it is reported as the cap in parity's words.
- Ties uniform over distinct extensions; moves are fills and subdivisions only.

## Reproduce

```sh
cd experiments/PICK-TWO-20261118-001B/PICK-TWO-20261118-001B-E001_pick
../../../.venv/bin/python -B checks.py
for P in C1 C2 C3 C4; do ../../../.venv/bin/python -B run.py --part $P --procs 8; done
../../../.venv/bin/python -B run.py --merge && ../../../.venv/bin/python -B readout.py
```

## Advisor

Consulted once before the freeze, on the design. It made four main points:
- It found that two of my candidate rules (no odd crossing cycle; each split's crossers forming one chain) are the cap of two in
  disguise on these bases.
- It showed that my third candidate (NEWCROSS) as worded does not hold two.
- It proposed FRESH and SEED, and named the arity of one fill as a fourth source.
- It gave the general corner pinning (S4), the exactly-one raise and the cube exception (S5).

It also asked for the frozen definition of "told no number", the two tiers, line lengths 5 to 12 and the three-way controls. All its
predictions held. It was not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh code: confirmed with fixes, no Block.
- S1 to S7 hold, checked by hand (S2, S4 and S5 line by line; S7's colouring also works when several splits gain crossings at once).
- picklib's fill enumeration equals its brute-force closure on all 77 bases tested.
- With its own engine, 29 run batches to n = 60 agree: caps of three and four, the quadratic prices, KEEP, CC, ODD and SEED, and
  λ equal to the largest set of pairwise crossing splits at every step. It did not rerun the linear prices, FRESH or NEWCROSS.

Folded in the same day, logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing (wording).** "The one way to two without naming it is arity" now reads: the rule chooses the one free step, arity
   makes that step one order, and the line supplies one order. SEED is given one order-making step, not a number.
2. **Not a block.** λ = 2 after the first fill needs the line start: from uncrossed trees that branch, one fill can give λ = 3.
3. **Not a block.** FRESH's k ≤ 2 follows from S6's argument (the uncrossed splits stay one chain), not S7.
4. **Not a block.** S6's "changes more than once" reads "changes at least three times".
5. **Not a block.** λ equals the largest set of pairwise crossing splits on every base reached, not in general (trees).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: who picks the number of orders | **Status:** Successful (referee pending), 9 of 9 held | Caps and prices set the number; conservative rules keep the start's; one free fill from a line then conservation gives exactly two |
| Local direction: two orders without naming two | Promising | SEED grows full two-way grids from every line; its two is the line's one plus one fill's |
| Broader exploration: a law that picks two from any start | Obstruction learned for these rules | λ never decreases; every rule kept three from three-way starts |
| Long-term goal: G1 | Capability gained | The number of orders is located: cap, price, start, parity or one move's arity |

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Is SEED's "then conserve" natural? Find what in the knots ends the free phase: e.g. a rule whose free steps are those that leave every split crossing at most one order, or whose first crossing is read as a knot | 3/3 | 1/3 | State a knot-level reading of SEED's switch → stop at a rule that needs no "crosses nothing" test, or an obstruction | Alternative |
| 2 | The distance on the grown grids: does the pair-count distance on SEED's and NNF's grids read as a two-way ruler (A97)? | 3/3 | 2/3 | Read the pair counts of grown grids against their own grid distance → stop at a ruler or its failure | Selected |
| 3 | SEED with knots only on pairs that already share one (as B197 did for NNF) | 2/3 | 3/3 | Rerun SEED knot-local from every bracketing of 5 to 8 → stop at its tiers | Alternative |
| 4 | A fully local first step for CC from a bare line (NEVER-NEST's direction 2) | 2/3 | 2/3 | Read the line's ends from the states, fill across them, then CC → stop at a proof | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (capability gained) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A101 moves to under challenge (SEED gets two from the start and one fill's arity, not by being told); A99 gains
this study.

**Basket:** read; nothing taken.
