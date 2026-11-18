# A rule whose second phase reads only the fill's knots

Epic `MID-RULE-20261118-001`, 18 November 2026, by Claude. It takes `KEEP-READ-20261118-001`'s first direction, with the
coordinator's go-ahead. Goals G1 and G16; challenges A101. Referee pending. **Stress test pending:** part F, the free forms' runs
(which check E4 and E5, both proved), is still running and will be folded in when it finishes (`docs/LONG_RUNNING.md`, MID-RULE-B1).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `1f3557541` at 09:15:27 UTC.
- The run: part K from 09:15 to 09:55 UTC; part F started at 09:16 UTC and is still running.
- Proof: [proof.md](../../proofs/MID-RULE-20261118-001A/MID-RULE-20261118-001A-P001_ends/proof.md).
- Code: [midlib.py, run.py, checks.py and readout.py](../../experiments/MID-RULE-20261118-001B/MID-RULE-20261118-001B-E001_mid/).
- Results: [part_K.json.gz](../../artifacts/MID-RULE-20261118-001B/MID-RULE-20261118-001B-E001_mid/).

## The answer

**A fill can make a new crossing only through two different end knots of its certificate (proved, on any base). So a rule that takes
one free fill and afterwards only fills certified with at most one end knot keeps two orders forever from any line. It is told no
number, and after its switch it reads only the fill's own knots.** That is a local reading of keeping, on its sufficient side.
It is also a conservative one: no crossing is ever added again.
- **With knots on any pairs (free).** It refills every new row from a full grid. From a line it reaches a full grid exactly when
  its first fill spans the line (proved; the runs that check this are pending).
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
| Q1 | No phase-two step changes k or λ | held (part K) | 210 of 210 knot-local runs; part F pending |
| Q2 | Free forms strong from 2 × 2 | pending | proved (E4) |
| Q3 | Free forms from lines strong iff the first fill spans | pending | proved (E5) |
| Q4 | Knot-local forms starve (fill fraction ≤ 0.15 on steps 31–60), λ = 2 throughout | held | exactly one fill per run, fill fraction 0 |
| Q5 | ANY raises λ above 2 in every run | pending | |

Two held and three are pending, which part F will settle. The advisor predicted Q4's "about one fill per run" exactly.

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

- Part F (the free forms, a check of proved statements) is pending.
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

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a rule reading only the fill's knots after the switch | **Status:** Successful (referee pending; part F pending), 2 of 5 held, 3 pending | It keeps two orders forever (proved); knot-local, it starves after one fill |
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
