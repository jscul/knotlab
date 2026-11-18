# A rule whose second phase reads only the fill's knots

Epic `MID-RULE-20261118-001`, 18 November 2026, by Claude. It takes `KEEP-READ-20261118-001`'s first direction, with the
coordinator's go-ahead. Goals G1 and G16; challenges A101. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no
Block, folded in on 18 November (see Referee). **Stress test done:** part F, the free forms' runs (which check E4 and E5, both
proved), finished at 14:25 UTC and is folded in below. Q2, Q3 and Q5 held, so all five predictions held (`docs/LONG_RUNNING.md`,
MID-RULE-B1).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `1f3557541` at 09:15:27 UTC.
- The run: part K from 09:15 to 09:55 UTC; part F from 09:16 to 14:25 UTC (90 runs, 18,598 s).
- Proof: [proof.md](../../proofs/MID-RULE-20261118-001A/MID-RULE-20261118-001A-P001_ends/proof.md).
- Code: [midlib.py, run.py, checks.py and readout.py](../../experiments/MID-RULE-20261118-001B/MID-RULE-20261118-001B-E001_mid/).
- Results: [part_K.json.gz, part_F.json.gz, results.json.gz and readout.json](../../artifacts/MID-RULE-20261118-001B/MID-RULE-20261118-001B-E001_mid/).

## The answer

**A fill can make a new crossing only through two different end knots of its certificate (proved, on any base of betweenness
knots). So after one free fill, a rule taking only fills with at most one end knot never makes a third order. Free, it grows full
grids only from a spanning first fill or from the 2 × 2 pattern; knot-local, it never fills again.** (Headline narrowed after the
referee; the one free fill is a given, as in `PICK-TWO-20261118-001`.) That is a local reading of keeping, on its sufficient side.
It is also a conservative one: no crossing is ever added again. Knot-local, it keeps two orders by lengthening alone, since it
never accepts a second fill: in effect "one free fill, then lengthen". Free, it grows full grids from a line in only 6 / (n (n − 1))
of runs: 30% at five, 11% at eight, 4.5% at twelve.
- **With knots on any pairs (free).** It refills every new row from a full grid. From a line it reaches a full grid exactly when
  its first fill spans the line (proved).
  - Part F checks it on 60 free runs from lines of 5, 8 and 12. Replaying each run's first fill (post hoc, a check of E5), every run
    whose first fill spans reached a full grid (11 of 11), and none of the other 49 did.
  - The strong shares were 30% and 40% at five, 10% and 20% at eight, and 10% and 0% at twelve (10 runs each). E5's share
    6 / (n (n − 1)) predicts 30%, 10.7% and 4.5%.
- **With knots only on pairs that already share one (knot-local).** It starves. In all 105 runs from bracketings of 5 to 8, to
  n = 60, both forms (two or more middle knots; at most one end knot) made exactly one fill, the free first one. After that they
  only lengthened: two orders throughout, and no full grid. Right after a lengthening, the new distinction shares knots only with
  its two neighbours, and every fill that would use it needs two end knots.

So locality buys safety but not growth. A local, conservative rule never adds a crossing. It therefore never absorbs a split that
crosses nothing, and grows full grids only from a first crossing that reaches every split. Knot-sharing makes it starve outright.

**In the owner's terms.**
- A new crossing always needs two knots that each extend a pair outward to the new distinction. A fill tied mostly by knots that
  place it between two old distinctions cannot make one.
- A rule that, after the first free fill, takes only fills of that kind never makes a third order. It needs to read nothing but the
  fill's own knots.
- But it never makes a new crossing either. It cannot pull in a split that the first fill left uncrossed, so it fills a whole grid
  only when that first crossing reaches every split. When its knots must reuse pairs that already share one, it stops filling
  after the first fill.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| Q1 | No phase-two step changes k or λ | held | 210 of 210 knot-local runs and 80 of 80 free runs (MID2 and ONE) |
| Q2 | Free forms strong from 2 × 2 | held | 20 of 20 runs to n = 60, two orders and a full grid at every lengthening (E4, proved) |
| Q3 | Free forms from lines strong iff the first fill spans | held | as the frozen read-out scores it: strong exactly when a full grid is reached, 60 of 60; spanning first fill ⟺ full grid, 60 of 60 (post hoc replay, E5) |
| Q4 | Knot-local forms starve (fill fraction ≤ 0.15 on steps 31–60), λ = 2 throughout | held | exactly one fill per run, fill fraction 0 |
| Q5 | ANY raises λ above 2 in every run | held | λ reached 6 from the line of five and 7 from the line of eight, in 10 of 10 runs |

5 of 5 held, three of them after part F. The advisor predicted Q4's "about one fill per run" exactly. One MID2 run from the line of
twelve stopped at the 60-state limit at n = 55. Its readings hold up to there, and it is counted as not strong (no full grid).

## What the knot picture explained

- **Why two end knots.** Each knot makes the new distinction copy an old one on the states it pins. A new crossing puts the new
  distinction where no old one is, on two states, so two different knots must pin them. A middle knot cannot pin either, since its
  pair sits on one side of both splits (E1).
- **Why the knot-local forms starve.** After a lengthening by B(u, p, v), p shares knots only with u and v. A fill using p needs it
  in two knots, as an end of B(u, p, r) and B(v, p, r), and those are two end knots.

Known mathematics, labelled: medians in a product of two chains. What this adds: a local certificate condition, at most one end knot,
that can never change the number of orders.

## What it means for A101 and the goals

- **A101** stays under challenge. After the first fill, keeping two orders can be read from the fill's own knots, on the safe side
  (at most one end knot). But such a rule only conserves, and full growth needs the first crossing to reach everything.
- **G1:** capability gained (a local rule that holds two orders forever, proved), with an obstruction learned for growth (it never
  absorbs uncrossed splits; knot-local, it starves).
- **G16:** capability gained. The end-knot criterion for crossings.

## Limitations

- Part F's free runs stop at 60 states; one stopped early (n = 55). Ten runs per free start.
- Knot-local runs: one seed per bracketing, to n = 60.

## Reproduce

```sh
cd experiments/MID-RULE-20261118-001B/MID-RULE-20261118-001B-E001_mid
../../../.venv/bin/python -B checks.py
../../../.venv/bin/python -B run.py --part K --procs 8 && ../../../.venv/bin/python -B run.py --part F --procs 8
../../../.venv/bin/python -B run.py --merge && ../../../.venv/bin/python -B readout.py
```

## Advisor

Consulted once before the freeze. It made three points:
- It strengthened my lemma, "two middle knots never make nested splits cross", to E1 through the copy principle, so that "at most
  one end knot" suffices on any base.
- It gave E5's exact share and predicted the knot-local starvation, about one fill per run, which held exactly.
- It asked for the ONE rule, the ANY control and the retro-check of E1 on 3,110 fills.

It was not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh code: confirmed with fixes, no Block.
- E1 to E5 hold, checked by hand (the copy principle and the middle-knot step).
- E2 on bases no growth made: 400 random copy-free bases of 3 to 7 knots on 5 to 8 distinctions, 43,677 fills. Of these, 10,244
  have a certificate with at most one end knot, and none changes a relation or λ. Every certificate of the 33,430 crossing-making
  fills has at least two end knots.
- Part K with the referee's own engine: in 210 runs to n = 60 and 70 runs to n = 75, both knot-local forms made exactly one fill
  per run, held two orders, and reached no full grid.
- E5 checked independently: MID2F from the line of five with each of its 10 first fills to n = 14. The 3 spanning fills reach full
  grids, and the 7 others never do.

Folded in the same day, logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing (wording).** "Keeps two orders, told no number, reading only the fill's knots" holds only with its scope. Knot-local,
   the rule never accepts a second fill. Free, it grows full grids only from the 2 × 2 pattern or a spanning first fill. The one
   free fill is a given. The headline above is the referee's.
2. **Not a block.** "On any base" now reads "on any base of betweenness knots", where splits and λ are defined.

Q2, Q3 and Q5 were settled by part F after the fold-in (all held). Q3 was also checked by the referee on the line of five.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a rule reading only the fill's knots after the switch | **Status:** Successful (refereed), 5 of 5 held | It keeps two orders forever (proved); knot-local, it starves after one fill |
| Local direction: keeping two orders by a local rule | Promising on safety, obstructed on growth | Conservative rules never absorb uncrossed splits |
| Broader exploration: growth that absorbs | Unexplored | Absorbing a split needs a fill with two end knots, which the local test refuses |
| Long-term goal: G1 | Capability gained; obstruction learned | Two orders held locally, full growth needs the first crossing to reach everything |

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which two-end-knot fills absorb a split without raising: SEED's copy clause in knot terms (the two end knots pin the absorbed split's states from an existing split's crossers) | 3/3 | 2/3 | Classify SEED's accepted fills with two end knots by how their end pairs meet the base's knots → stop at a knot-level copy rule, or a look-alike pair | Selected |
| 2 | A first fill that spans the line, read from the states (the line's ends are the distinctions every split separates from all others on one side), so that the free local rule grows full grids from every line | 2/3 | 3/3 | Define the first step, rerun the free form → stop at strong from every line or a counterexample | Alternative |
| 3 | Knot-local starvation in general: prove that after a lengthening no knot-local fill has at most one end knot | 2/3 | 3/3 | Prove it from the lengthening's pair structure → stop at a proof or a counterexample | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (capability gained; obstruction learned for growth) and a G16 checkpoint (capability gained); no goal
changed.

**Assumptions:** A101 stays under challenge, with this study's reading; A99 gains it.

**Basket:** read; nothing taken.
