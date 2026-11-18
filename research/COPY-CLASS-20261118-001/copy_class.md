# What SEED's copy step reads

Epic `COPY-CLASS-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead after `COPY-READ-20261118-001`'s referee.
Goals G1 and G16; challenges A101. Refereed: report [R1](referee-R1/report.md), facts confirmed, **Block on one reading**,
folded in on 18 November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `354ccd409` at 12:25:50 UTC.
- The run: from 12:26 to 12:36 UTC (135 starts).
- Post hoc: [posthoc.py](../../experiments/COPY-CLASS-20261118-001B/COPY-CLASS-20261118-001B-E001_class/posthoc.py), from 12:37 to
  12:46 UTC.
- Proof: [proof.md](../../proofs/COPY-CLASS-20261118-001A/COPY-CLASS-20261118-001A-P001_model/proof.md).
- Results: [results.json.gz, readout.json, posthoc.json and posthoc_rest.json](../../artifacts/COPY-CLASS-20261118-001B/COPY-CLASS-20261118-001B-E001_class/).

## The answer

*Corrected after the referee (Block on a reading; see Referee).* The facts stand; the reading built on them does not.

**SEED's copy step is decided on the splits separating the fill's two end pairs and a model's crossers (proved). The frozen local rule
accepted no copy step, because its candidate set was always empty. The "swapped" rule agreed with SEED on every fill, but trivially:
it can only accept what SEED accepts, and on every copy step its candidates were all the crossed splits, so it is SEED's own clause.
No rule here names the copy step from the fill's own pairs. What the data do show, by the referee's exploratory finding: a fill is a
copy step exactly when its far end pair is separated by every crossed split. That sign needs no comparison of crosser sets, but it
still reads every crossed split.**

- **What is proved (C1 to C3).**
  - Every new crossing joins splits separating the fill's two end pairs.
  - So SEED's verdict is decided on those splits and the crosser set of a model.
  - In a full two-way grid a model's crossers are a whole order.
  - (*After the referee:* C3's last sentence, that any exact rule must see a whole order, goes past its proof.)
- **The frozen rule CR** sought the model among the crossed splits separating the end pair that touches the middle pair. It accepted
  none of the 850 copy steps and none of the 84,352 refused fills. *After the referee:* no crossed split ever separates that pair on
  a copy step, so CR's candidate set was empty every time. It pointed at nothing, not at a wrong model.
- **SEED's own condition, read locally (CRANY),** agreed with SEED on all 85,202 extensions. C1 held on all 2,056,136 knot sets.
- **The swapped rule CRSWAP** (post hoc) agreed with SEED on all 85,202 extensions, and on the referee's 114,006 fresh ones. But the
  agreement is trivial, for two reasons:
  - CRSWAP keeps SEED's clause (a) and searches a subset of SEED's candidates, so it can accept only what SEED accepts. All 84,352
    refused agreements are automatic.
  - On every copy step every crossed split separates the far end pair (850 of 850 here, 2,066 of 2,066 fresh). So CRSWAP's
    candidates are SEED's own, and naming the far pair narrows nothing.
- **The referee's sign** (exploratory: seen on 4 starts, then scored unchanged on 180 fresh starts and this study's 135). A
  crossing-making fill is a copy step exactly when its far end pair is separated by every crossed split.
  - It held on all 2,066 fresh copy steps and none of 111,940 refused fills.
  - It held on all 850 of this study's copy steps and none of its 84,352 refused fills, including the 1,234 that fail clause (b).
  - The referee proved that the sign implies clause (a). Its implying clause (b), and the converse, are open.
- **How much the check reads.** The sign reads one bit per crossed split. On the referee's runs a copy step's check covers a median of
  91% of all splits, and at least 20%. The model's crossers numbered 1 to 8 (post hoc, counted per knot set and absorbed split).
- **Refusals.** 83,118 refused crossing-making fills broke clause (a): crossed splits came to cross. The other 1,234 failed clause
  (b) in a mixed way. None failed as a pure subset or superset of a model's crossers.
- **The copy class.** All 850 copy steps were in `COPY-READ-20261118-001`'s one closure class, at the new sizes too (lines of 12).

**In the owner's terms** (corrected).
- A fill that pulls a loose split into the grid is tied by three knots. One end knot's pair is crossed by nothing, and the other end
  knot's pair is separated by every crossed split.
- That second fact alone, read on the states, decides whether the fill copies. No knot points at a particular split to copy.
- But checking it means looking at every crossed split. So the copy step is not local in what it reads, even though its sign is
  simple.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | CR agrees with SEED on every crossing-making extension | **failed** | recall 0 (0 of 850), no false acceptance; CR's candidate set was empty every time |
| P2 | CRANY agrees with SEED; C1 on every knot set | held | 85,202 of 85,202; 2,056,136 of 2,056,136 |
| P3 | Most refusals clause (a); among (b), subsets outnumber supersets | **failed** | (a) 98.5%, but (b) refusals were all mixed |
| P4 | Some copy steps have a model with two or more crossers | **unscored** | its instrument (CR's candidates) was empty by construction; post hoc it holds (1,089 of 1,544 readings here; 2,660 of 3,438 on the referee's runs) |
| P5 | Every copy step in the copy class | held | 850 of 850 |

2 of 4 scored held (P2, P5); P1 and P3 failed, and P4 is unscored. *After the referee:* P1 failed from an empty candidate set, not a swap. P3 failed on its own terms, since its clause-(b) part is independent of CR (all such refusals are mixed, 3,698 of 3,698 on fresh seeds).

## What the knot picture explained

- **Why the far pair** (an explanation, not proved; *after the referee:* every crossed split separates the far pair on a copy step, so it is not a choice of model). The tail's new crossers are the splits separating the middle pair (C1, with the middle knot
  pinning the rest). The model must be an existing split with exactly those crossers. Its own splits are those the other end knot
  pins, since that knot pins the new distinction to its far distinction, which lies on the model's side.
- **Why it is not bounded.** The model's crossers are whatever crosses it, and in a grown grid that is a whole order.

Known mathematics, labelled: none beyond the split-system notions already cited. What this adds: a rule that names only a fill's own
pairs and decides SEED's copy step, with the locality of its naming separated from the extent of what it reads.

## What it means for A101 and the goals

- **A101** stays under challenge. Growing two orders over the whole line needs the copy step. *After the referee:* it is decided by
  one sign, the far end pair separated by every crossed split, which reads every crossed split.
- **G1:** obstruction learned for extent. *The capability first claimed here, a copy rule named by the fill's own pairs, is withdrawn
  (Block).*
- **G16:** capability gained: the copy step's three knots (one end pair crossed by nothing, the other separated by every crossed
  split), and the referee's exploratory sign.

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

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with fresh code: the facts confirmed, **Block on
one reading**.
- **Confirmed.**
  - On 180 fresh starts (to n = 34, lines of 14 and 16), CRSWAP equals SEED on all 114,006 crossing-making extensions (2,066 copy
    steps).
  - C1 holds on 2,652,636 knot sets.
  - CR accepts none of the copy steps.
  - All copy steps lie in the copy class.
- **Block.** "The far end knot names the model; the copy step is named by the fill's own pairs", and the G1 capability built on it.
  CRSWAP's agreement is trivial, as set out in the answer above. CR's failure is an empty candidate set.
- **The referee's finding (exploratory).**
  - The sign "the far end pair is separated by every crossed split" decides SEED's copy step exactly, on fresh seeds and on this
    study's engine.
  - The referee proved that the sign implies clause (a).
- **Narrowings (wording).** "Named by the fill's own pairs" is not fair: the check reads a median of 91% of all splits. C3's last
  sentence goes past its proof.
- **Not a block (scoring).** P1 failed from an empty set. P3 failed on its own terms. P4 is unscored. The score is 2 of 4 scored
  predictions held.

Folded in the same day, logged in `docs/CORRECTIONS.md` (one Block entry) and knotlab's `HISTORY.md`. The G1 capability is withdrawn,
and the line summary, the intuition entry, A101's line and the goals rows are corrected.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what separates copy steps inside the copy class | **Status:** Refereed with a Block on its reading; 2 of 4 scored held | The frozen rule had an empty candidate set; the swapped rule is SEED's own clause; the referee's sign decides it exactly (exploratory) |
| Local direction: naming the copy step locally | Obstruction learned | No knot points at a model; the sign reads every crossed split |
| Broader exploration: reading it in bounded extent | Obstruction learned | It reads a model's crossers, a whole order in a grid |
| Long-term goal: G1 | Obstruction learned (capability withdrawn) | The copy step is decided by one global sign |

**Next step:** Research directions. The coordinator stops the two-order line after this study.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The referee's sign, frozen and proved: "the far end pair is separated by every crossed split" equals SEED's copy step (sign implies clause (b), and the converse), or a counterexample; then whether the copy class's betweenness reads it | 3/3 | 3/3 | Freeze the sign, attempt both proofs, rerun on fresh starts → stop at a proof or a counterexample | Selected (coordinator) |
| 2 | Replace "every crossed split" by a bounded check: in a full grid the distinctions every split separates are the extremes of both orders; is the sign readable from those extremes? | 2/3 | 2/3 | Characterise the far pair's position in grids → stop at a bounded test or an obstruction | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (capability gained; obstruction learned for extent) and a G16 checkpoint (capability gained); no goal
changed.

**Assumptions:** A101 stays under challenge; A99 gains this study.

**Basket:** read; nothing taken.
