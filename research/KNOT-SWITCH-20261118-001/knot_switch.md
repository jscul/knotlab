# What the knots read when nothing crosses yet

Epic `KNOT-SWITCH-20261118-001`, 18 November 2026, by Claude. It takes `PICK-TWO-20261118-001`'s first direction, chosen by the
coordinator. Goals G1 and G16; challenges A101. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `d753ef8bf` at 08:20:07 UTC.
- The run: S1 from 08:20 to 08:37 UTC.
- Proof: [proof.md](../../proofs/KNOT-SWITCH-20261118-001A/KNOT-SWITCH-20261118-001A-P001_switch/proof.md).
- Code: [knotlib.py, run.py, checks.py and readout.py](../../experiments/KNOT-SWITCH-20261118-001B/KNOT-SWITCH-20261118-001B-E001_switch/).
- Results: [results.json.gz and readout.json](../../artifacts/KNOT-SWITCH-20261118-001B/KNOT-SWITCH-20261118-001B-E001_switch/).

## The answer

**SEED's "nothing crosses yet" reads, in the knots: no four distinctions yet carry four knots each the middle of one. That set of
four is a knot together with its fill, a "filled knot". A filled knot allows only two crossing patterns on its four distinctions,
so it forces a crossing in any presentation (proved). Along every growth here, the first fill makes the first filled knot and the
first crossing in the same step (proved, and checked at all 11,050 steps of 420 runs).** So the two enters exactly when the knots
first close on themselves, in four knots on four distinctions, the smallest even knot set there is.

- **The switch, four ways at once.** At every step of every run (KF3, NN, NN2 and SEEDK from 105 bracketings of 5 to 8), four
  readings agreed: no two splits cross; there is no filled knot; the knot complex has no even knot set (b₂ = 0); no fill has been
  made yet. The same held for "some four distinctions have all four triples knotted", without the middles.
- **Which of them is the knots' own.** b₂ depends on the presentation: a line presented by every implied knot has b₂ = C(n − 1, 3)
  and nothing crossing. The filled knot does not: wherever it appears, a crossing follows from the four knots alone (W2).
- **SEED with knots only on pairs that already share one (SEEDK) is strong.** From every bracketing of 5 to 8 it keeps two orders at
  every step after the first fill. In 105 of 105 runs it passes through full two-way grids three or more times, and every
  lengthening after the first comes at a full grid. The knot-sharing condition costs it nothing, as it cost NN almost nothing.
- **After the switch, the knots make loops, not closed sets** (post hoc, labelled). In SEEDK the first fill is the only one that
  makes a filled knot in 104 of 105 runs; every later fill joins knots on pairs that do not touch, and adds loops to the complex
  (b₁ about 36 by n = 40). In every rule, b₂ rose at a step exactly when a new filled knot appeared, in 10,622 of 10,630 steps
  (all steps of NN and SEEDK). Filled knots do not count orders: under KF3 the orders rose 240 times without one.

**In the owner's terms.**
- A line grows by knots that never close: each new knot hangs off an old pair, and the knots' pattern has no loop and no enclosure.
  Nothing crosses.
- The first fill adds three knots that close up with an old one: four distinctions, every three of them knotted, each one the
  middle of a knot. Those four allow only two ways of being split, and the two cross. That is where the second order comes from,
  and why it is exactly one more: one closed set of four allows exactly two crossing patterns.
- After that, the two-way grid grows by knots that close loops but never enclose again.
- So the knots' state that SEED reads is "the knots have not yet closed on themselves".

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| Q1 | W3 holds at every step of every run | held | 11,050 of 11,050 steps |
| Q2 | "All four triples knotted" agrees with a crossing at every step | held | 11,050 of 11,050 |
| Q3 | SEEDK strong at every start size | held | 105 of 105 runs |
| Q4 | b₁ > 0 by the end in at least half the KF3 runs | held | 105 of 105 |

4 of 4 held. Q1 is the proof's check. Q4 was informed by the gate checks, which is disclosed.

## What the knot picture explained

- **Why the filled knot forces a crossing.** Its four knots rule out every way of splitting the four distinctions but two: a with c
  against b with r, and a with r against c with b. Distinct distinctions need both, and those two cross.
- **Why the line has none.** A bracketing's knots are the triangles of a polygon's division, and no four distinctions of it all
  share knots pairwise.
- **Why later fills make loops.** A fill hangs three knots from the new distinction on three old pairs. On the line they are the
  three pairs of one knot, which closes a filled knot. In a grid they are pairs in different places, which do not touch, so the new
  knots link up as loops without enclosing (W1).

Known mathematics, labelled: the Mayer–Vietoris sequence for attaching a cone, and the four-point configuration (the literature's
boundary of a tetrahedron, a 2-cycle). What this adds, in the program's terms: where the second order enters, read from the knots
themselves.

## What it means for A101 and the goals

- **A101** stays under challenge, sharper. SEED's two is read in the knots as "the knots have not yet closed", which needs no
  number. Still, the rule must be told to stop being free once they have.
- **G1:** capability gained. The rule told no number holds two orders with knots only on pairs that already share one (SEEDK), and
  its switch is a state of the knots.
- **G16:** capability gained. The knot complex's even sets and loops are read along growth.

## Limitations

- One seed per bracketing; runs to n = 30 (n = 40 for SEEDK).
- "b₂ rises exactly with a new filled knot" and "later fills make loops" are post hoc readings of the frozen traces.
- The filled knot forces a crossing in any presentation, but its converse (a crossing implies a filled knot) is shown only along
  these growths.

## Reproduce

```sh
cd experiments/KNOT-SWITCH-20261118-001B/KNOT-SWITCH-20261118-001B-E001_switch
../../../.venv/bin/python -B checks.py
../../../.venv/bin/python -B run.py --part S1 --procs 12 && ../../../.venv/bin/python -B run.py --merge
../../../.venv/bin/python -B readout.py
```

## Advisor

Consulted once before the freeze. It made four points:
- My first version claimed the knot complex never gains a loop. The advisor showed this is false, and that a single knot on a long
  pair breaks the switch under literal KF3 (it does not arise here: every rule's first move is a fill).
- It separated the readings that depend on the presentation (b₂) from the one that does not.
- It proposed the filled knot (its "fill-type four-set") and the word "even knot set".
- It estimated SEEDK strong at about 65%; it was strong in every run.

It was not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what SEED's switch reads in the knots | **Status:** Successful (referee pending), 4 of 4 held | "No filled knot yet": the first closed four of knots is the first crossing, in every presentation one way and along every growth both ways |
| Local direction: two orders from the knots' own state | Promising | SEEDK is strong with knot-sharing moves |
| Broader exploration: SEED's second phase in the knots | Unexplored | Its copy-or-conserve condition reads crossings; no knot reading is known |
| Long-term goal: G1 | Capability gained | The second order enters with the knots' first closed set |

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What the knots read in SEED's second phase (copy or conserve). Refusing new filled knots is not it: under KF3 the orders rose 240 times with no new filled knot, by fills whose pairs do not touch. Find the knot state that tells a fill keeping two orders from one that raises them | 3/3 | 2/3 | Classify the fills SEEDK refuses and takes after its switch by their pair graphs and the knots they meet → stop at a knot-level rule equal to SEED's on these runs, or a pair of fills alike in the knots and different in orders | Selected |
| 2 | The converse of W2 in general: on which presentations does a crossing imply a filled knot? | 2/3 | 2/3 | Search small irredundant presentations with a crossing and no filled knot → stop at a characterisation or a counterexample family | Alternative |
| 3 | What the loops count: does b₁ along SEEDK read the grid's size or shape? | 2/3 | 2/3 | Compare b₁ with the grid's chains and cells along SEEDK → stop at a formula or none | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (capability gained) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A101 stays under challenge, with this study's reading; A99 gains it.

**Basket:** read; nothing taken.
