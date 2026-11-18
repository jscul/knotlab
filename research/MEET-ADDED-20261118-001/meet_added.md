# Do the knots a growth added record its order?

Epic `MEET-ADDED-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes sub-goal B199
(`MEET-HIST-20261118-001`'s selected direction). Goal G16; tests A97. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block, folded in on 18
November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `259e35081` at about 05:09 UTC on 18 November. The
  run (long run MEET-ADDED-B1, 61 cases on the shared runner) ended at 05:12 UTC, 61 of 61 ok.
- Code: [job.py, checks.py, merge.py and melib.py](../../experiments/MEET-ADDED-20261118-001B/MEET-ADDED-20261118-001B-E001_added/).
- Results: [results.json](../../artifacts/MEET-ADDED-20261118-001B/MEET-ADDED-20261118-001B-E001_added/results.json).

## The answer

- **Given the grown states and told which knots the growth added, a reader recovers what the full names give about the nesting,
  exactly at five and six and within 0.0002 at seven; neither the states nor the added knots suffice alone, and knowing which
  knots were added is itself history** (*narrowed after the referee*: first "the knots carry it, not the distances"; computed, exact, every presentation of 5, 6 to k = 4 and 7 to k = 3; prior uniform over labelled
  presentations). Shares of the information about the bare bracketing:

  | Line of, k | Added pairs alone | States alone | States + added pairs | States + added knots | All named |
  | --- | --- | --- | --- | --- | --- |
  | 5, k = 2 / 3 / 4 | 0 / 0 / 0 | 0.60 / 0.39 / 0.22 | 1.0 / 0.95 / 0.94 | 1.0 / 1.0 / 1.0 | 1.0 / 1.0 / 1.0 |
  | 6, k = 2 / 3 / 4 | 0.009 / 0.040 / 0.050 | 0.65 / 0.63 / 0.53 | 0.83 / 0.90 / 0.91 | 0.83 / 0.91 / 0.93 | 0.83 / 0.91 / 0.93 |
  | 7, k = 2 / 3 | 0.002 / 0.016 | 0.57 / 0.62 | 0.68 / 0.787 | 0.68 / 0.7915 | 0.68 / 0.7916 |

  - The states with the added knots (as triples, and the same with their middles) equal the all-named share exactly at every level
    of five and six, and at seven to within 0.00012 at k = 3, the only level where they differ (Q2 failed there by that margin).
  - The added pairs alone, with no states, carry almost nothing (at most 0.05; Q1), as the referee's preview showed; with the
    states they carry nearly all (Q5), a little less than the triples from k = 3 (Q4).
- **What this reading assumes.** It hands the reader the added knots as a separate structure, so it is told which knots the growth
  made, and that is a piece of history. Read with every knot, starting and added, not told apart, the states carry 1.0 at every k,
  k = 0 included, because the starting knots are the presentation; even all knots without the states carry 1.0. The added knots
  alone (with middles, no states) carry 0 to 0.41 at five and 0 to 0.12 at six; the added pairs alone at most 0.05 (the referee).
- **The shortfall at seven is real** (the referee, with independent classes): 44 classes of (states, added knots) merge named
  bases whose laws over the bare bracketing differ; for example fills on {0, 1, 6}, {1, 2, 6} and {4, 5, 6} grown in two orders
  are isomorphic with their added knots but have laws ½/½ against 13/22, 9/22. The order of three fills carries a sliver that the
  added knots do not fix.
- **The order itself stays mostly unknown even then**: the named base given the states and the added knots still has 0.40 to 1.28
  bits of uncertainty; only the small part of the order that bears on the nesting is recorded.

**In the owner's terms.**
- Given a grown base's states and told which knots the growth made, a reader recovers everything the full history would about how
  the first knots met, on lines of five and six, and all but a sliver on seven: each new distinction's knots say what it was tied to.
- Neither the states alone nor the new knots alone tell it, and knowing which knots are new is itself history. A reader given every
  knot, old and new mixed, recovers it at once, because the old knots are how the knots first met.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 5 gate checks pass | held | the referee's preview reproduced |
| Q1 | Added pairs alone below a quarter of the states-alone share at every k ≥ 1 | held | at most 0.050 against 0.53 |
| Q2 | States + added knots (triples and middles) = all named, exactly, at every k | **failed** (seven, k = 3) | exact at five and six (every k) and at seven k = 1, 2; at seven k = 3 short by 0.00012 |
| Q4 | States + added pairs short of the triples at some k ≥ 3, each n0 | held | five 0.95 < 1.0; six 0.90 < 0.91; seven 0.787 < 0.7915 |
| Q5 | States + added pairs above the states alone at every k ≥ 2 | held | every n0 and k |

3 of 4 held. Q2 failed by a margin of 0.00012 of the entropy at one level, as the advisor warned an old distinction with few
knots might pass for a late arrival at larger n.

## What it means for A97 and the goals

- **A97** stays under challenge. Narrowed after the referee: what one grown base's distances miss about how its knots met is
  recovered from the states together with the knots the growth made, when the reader is told which those are; that knowledge is
  itself history. With every knot the nesting is given outright; with the distances alone, only in part.
- **G16:** capability gained. The missing share located in the added knots, almost exactly.

## Limitations

- Fewest-knot presentations, KF3, one prior; five and six to k = 4, seven to k = 3.
- Q2's equality is computed, not proved; the advisor's peeling lemma (reading the order of growth back from the states with the
  added knots, up to swaps that do not change the bracketing) is open, and it fails by a sliver at seven, k = 3.

## Reproduce

```sh
cd experiments/MEET-ADDED-20261118-001B/MEET-ADDED-20261118-001B-E001_added
../../../.venv/bin/python -B checks.py
cd ../../..
.venv/bin/python -B scripts/longrun.py launch experiments/MEET-ADDED-20261118-001B/MEET-ADDED-20261118-001B-E001_added/job.py \
  --out <dir> --unit <name> --workers 8 --case-mem 1800M
.venv/bin/python -B experiments/MEET-ADDED-20261118-001B/MEET-ADDED-20261118-001B-E001_added/merge.py <dir>
```

## Advisor

Consulted once before the freeze: probabilities (Q1 about 0.25 as first written, so restated; Q2 about 0.8, not by construction
without a peeling lemma, with the warning that a sparsely knotted old distinction could pass for a late one; Q4 about 0.8; Q5
about 0.97), which bounds hold by construction, and to score the triple and middle equalities jointly. Not consulted after.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with independent VF2 classes: confirmed with
fixes, no Block. `exact_with_knots` is KF3's law, and every share reproduces to six digits, the seven, k = 3 shortfall included.
Folded in the same day (logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`):
1. **Narrowing** (the headline, the owner's terms, A97). "The knots carry it, not the distances" is not fair: the reading tells
   the reader which knots the growth added, which is history; with every knot undistinguished the nesting is given outright (1.0 at
   every k). The fair sentence is the headline above.
2. **Not a block.** The shortfall at seven is real: 44 classes merge named bases with different laws; the order of three fills
   carries a sliver the added knots do not fix. This answers direction 1's first step.
3. **Not a block.** The arm the coordinator asked for (states with every knot, undistinguished) is trivially 1.0; recorded above.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: do the added knots record the order's missing part | **Status:** Successful (refereed R1, confirmed with fixes) | Told which knots were added, the states recover the all-named share: exact at five and six, within 0.00012 at seven; 3 of 4 held |
| Local direction: how knots meet as information under KF3 | Practically exhausted at these sizes | The missing share is located; what remains is a peeling lemma and the sliver at seven |
| Broader exploration: A97, knots against distances | Searching | One rule, fewest-knot presentations of lines |
| Long-term goal: G16 Learning the rules behind what a system allows | Capability gained | The nesting's trace located in the grown knots |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The peeling lemma: from the states and the added knots, read the order of growth back up to swaps that keep the bracketing; find what fails at seven, k = 3 | 2/3 | 2/3 | List the seven, k = 3 grown bases that the added knots confuse but the names separate → stop at the cause, or a proof for the cases where it holds | Selected · awaiting go-ahead |
| 2 | Beyond lines and fewest knots (A100): does the trace sit in the added knots for redundant presentations too? | 2/3 | 2/3 | Add one redundant knot and rerun the arms at five → holds or fails | Alternative · deferred |
| 3 | Long growth: all arms sampled to k = 20 | 2/3 | 3/3 | Sample six and seven → the limits | Alternative · deferred |

- **#1.** Payoff: turns the near-equality into a statement with a cause. Concreteness: the confused cases are few and listable.
- **#2.** Payoff: whether this is about lines or knots. Concreteness: needs a redundant-knot start.
- **#3.** Payoff: the long-run picture. Concreteness: sampling only.

**Corrections:** one Narrowing and two Not-a-block points from the referee, logged; see Referee.

**Goals:** a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 under challenge, with this finding added; A100 gains this study among what rests on it; no new entry.

**Basket:** read; B199 taken by this epic.

## Final report as sent

Posted in the project thread at about 05:15 UTC on 18 November 2026 (the tables are those of the Position section above, with the
directions shortened):

> **Sixth study done (referee pending): the knots the growth added record the missing part, almost exactly.** Read a grown base
> with its states and its added knots, and no names. That tells as much about how the first knots nested as the full history does.
> It matches exactly on lines of five and six, and comes within 0.00012 on seven, the one level where the two differ. The added
> knots' pattern alone, without the states, tells almost nothing (at most 0.05). So what the distances miss is written in which new
> distinction was tied to which older ones: the knots carry it, not the distances. 3 of 4 predictions held; the exact-equality one
> failed by that sliver at seven, as the advisor warned it might.
>
> Corrections: none. Goals: G16 checkpoint. Assumptions: A97 under challenge, with this finding added.
