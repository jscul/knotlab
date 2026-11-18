# What SEED's copy step reads

Epic `COPY-CLASS-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead after `COPY-READ-20261118-001`'s referee.
Goals G1 and G16; challenges A101. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `354ccd409` at 12:25:50 UTC.
- The run: from 12:26 to 12:36 UTC (135 starts).
- Post hoc: [posthoc.py](../../experiments/COPY-CLASS-20261118-001B/COPY-CLASS-20261118-001B-E001_class/posthoc.py), from 12:37 to
  12:46 UTC.
- Proof: [proof.md](../../proofs/COPY-CLASS-20261118-001A/COPY-CLASS-20261118-001A-P001_model/proof.md).
- Results: [results.json.gz, readout.json, posthoc.json and posthoc_rest.json](../../artifacts/COPY-CLASS-20261118-001B/COPY-CLASS-20261118-001B-E001_class/).

## The answer

**The frozen local rule failed on every copy step: it looked for the model in the wrong end pair. With the roles swapped (found
after the read-out, labelled), the rule decides SEED's copy step exactly. It was found on a fifth of the starts and then agreed with
SEED on all 68,547 crossing-making fills of the other four fifths. The rule names only the fill's own pairs. But it compares crosser
sets, and a model's crossers are a whole order of a full grid, so it is local in what it names and not bounded in what it reads.**

- **What is proved (C1 to C3).**
  - Every new crossing joins splits separating the fill's two end pairs.
  - So SEED's verdict is decided on those splits and the crosser set of a model.
  - In a full two-way grid a model's crossers are a whole order.
- **The frozen rule CR.** It sought the model among the crossed splits separating the end pair that shares a distinction with the
  middle knot's pair, as the advisor read the roles. It accepted none of the 850 copy steps and none of the 84,352 refused
  crossing-making fills. Recall was 0 and there were no false acceptances. For every copy step the model was never there.
- **SEED's own condition, read locally (CRANY).** With clause (a) read on the end pairs' splits and the model sought among all
  crossed splits, the rule agreed with SEED on all 85,202 extensions. C1 held on all 2,056,136 knot sets.
- **The swapped rule CRSWAP** (post hoc). It seeks the model among the crossed splits separating the other end pair, the one that
  does not share a distinction with the middle pair.
  - It was found on every fifth start (27 starts): it agreed with SEED on all 16,655 extensions, 134 of them copy steps.
  - It was then scored, unchanged, on the other 108 starts: all 68,547 extensions agreed, 716 of them copy steps.
  - In every copy step the model lay there.
- **The roles, then.** The end pair touching the middle knot's pair is the tail being pulled in. The middle knot names what it comes
  to cross. The other end pair's splits hold the model whose crossers it copies.
- **How much the reading takes in.** The model's crossers numbered 1 to 8, a median of 27% of all splits (post hoc, counted per
  knot set and absorbed split). In a full grid they would be the whole other order (C3).
- **Refusals.** 83,118 refused crossing-making fills broke clause (a): crossed splits came to cross. The other 1,234 failed clause
  (b) in a mixed way. None failed as a pure subset or superset of a model's crossers.
- **The copy class.** All 850 copy steps were in `COPY-READ-20261118-001`'s one closure class, at the new sizes too (lines of 12).

**In the owner's terms.**
- A fill that pulls a loose split into the grid is tied by three knots, and each has a job:
  - one end knot holds the loose split;
  - the middle knot says which splits it will come to cross;
  - the other end knot points at an existing split whose crossings it must copy exactly.
- Whether the copy is exact can be checked by looking only at the splits those knots' own pairs touch.
- But the check compares two sets of crossers, and in a grown grid a split's crossers are one whole order. So the rule is local in
  what it names, while what it reads spans an order.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | CR agrees with SEED on every crossing-making extension | **failed** | recall 0 (0 of 850), no false acceptance; the roles were swapped |
| P2 | CRANY agrees with SEED; C1 on every knot set | held | 85,202 of 85,202; 2,056,136 of 2,056,136 |
| P3 | Most refusals clause (a); among (b), subsets outnumber supersets | **failed** | (a) 98.5%, but (b) refusals were all mixed |
| P4 | Some copy steps have a model with two or more crossers | **failed** as measured | measured through CR's models, none found; post hoc, 1,089 of 1,544 model readings (counted per knot set and absorbed split) have two or more |
| P5 | Every copy step in the copy class | held | 850 of 850 |

2 of 5 held. P1, P3 and P4 turn on the same mistake, the swapped roles; P4's measurement depended on CR.

## What the knot picture explained

- **Why the model is the far pair** (an explanation, not proved). The tail's new crossers are the splits separating the middle pair (C1, with the middle knot
  pinning the rest). The model must be an existing split with exactly those crossers. Its own splits are those the other end knot
  pins, since that knot pins the new distinction to its far distinction, which lies on the model's side.
- **Why it is not bounded.** The model's crossers are whatever crosses it, and in a grown grid that is a whole order.

Known mathematics, labelled: none beyond the split-system notions already cited. What this adds: a rule that names only a fill's own
pairs and decides SEED's copy step, with the locality of its naming separated from the extent of what it reads.

## What it means for A101 and the goals

- **A101** stays under challenge. Growing two orders over the whole line needs the copy step. That step is now named by the fill's
  own pairs, but it reads a model's crossers, which span an order.
- **G1:** capability gained (a copy rule named by the fill's own pairs, exact on 85,202 fills, post hoc and then held out). An
  obstruction was also learned: it is not bounded in extent.
- **G16:** capability gained (the roles of the three knots of a copy step).

## Limitations

- CRSWAP is post hoc. It was found on a fifth of the frozen run's starts and scored on the rest of the same run, not on a fresh
  freeze. A referee rerun with new seeds would confirm it.
- Bases up to 30 distinctions; lines up to 12.

## Reproduce

```sh
cd experiments/COPY-CLASS-20261118-001B/COPY-CLASS-20261118-001B-E001_class
../../../.venv/bin/python -B checks.py
../../../.venv/bin/python -B run.py --procs 8 && ../../../.venv/bin/python -B readout.py
../../../.venv/bin/python -B posthoc.py && ../../../.venv/bin/python -B posthoc.py --rest
```

## Advisor

Consulted before the freeze.
- **What it did.** It advised cutting the knot-radius tiers as vacuous, derived the three knots' roles and the candidate rule CR,
  and asked for classifier scoring, the refusal breakdown and starts with larger models.
- **Where it was wrong.** Its assignment of the model to the end pair sharing a distinction with the middle pair was backwards. The
  frozen rule therefore failed, and the swap was found after the read-out.

It was not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what separates copy steps inside the copy class | **Status:** Successful (referee pending), 2 of 5 held | Frozen rule failed (roles swapped); the swapped rule is exact post hoc and held out |
| Local direction: naming the copy step locally | Promising | Named by the fill's own pairs |
| Broader exploration: reading it in bounded extent | Obstruction learned | It reads a model's crossers, a whole order in a grid |
| Long-term goal: G1 | Capability gained | The copy step is named by the fill's knots; its check spans an order |

**Next step:** Research directions. The coordinator stops the two-order line after this study.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Confirm CRSWAP on a fresh freeze (new seeds, longer lines), and prove it: the model always lies among the far end pair's crossed splits | 2/3 | 3/3 | Freeze CRSWAP and rerun; attempt the proof from E1 and the copy class's pins → stop at a proof or a counterexample | Alternative |
| 2 | Replace "the model's crossers" by a bounded check: in a full grid the model's crossers are the other order; is "the middle pair is separated by every split of the other order" readable from its ends? | 2/3 | 2/3 | Characterise the middle pair's position in grids → stop at a bounded test or an obstruction | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (capability gained; obstruction learned for extent) and a G16 checkpoint (capability gained); no goal
changed.

**Assumptions:** A101 stays under challenge; A99 gains this study.

**Basket:** read; nothing taken.
