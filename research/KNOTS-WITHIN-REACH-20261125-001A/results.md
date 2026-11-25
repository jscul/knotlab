# How many knots lie within reach, and does the growing end carry a distance of its own? Result

Ticket `KNOTS-WITHIN-REACH-20261125-001A` (sub-goals B261 and B269; goals G1 and G2 with G5; assumptions A110, A97,
A98 and A105), 2026-11-25. Computed by an engine written from the frozen texts by a helper that had not seen the
drafter's prototype; two central tables recounted by the thread from the raw records. Evidence class of everything
here: **computed, bounded, referee pending**; the five lemmas of the claim are argued, checked on every run, and not
refereed.
[Pre-registration](preregistration.md) · [claim](../KNOTS-WITHIN-REACH-20261125-001/claim.md) ·
[definitions](../KNOTS-WITHIN-REACH-20261125-001/definitions.md) ·
[the run's summary](../../artifacts/KNOTS-WITHIN-REACH-20261125-001A/KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach/summary.md) ·
[the readings taken](../../experiments/KNOTS-WITHIN-REACH-20261125-001A/KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach/deviations.md)

**No run gives the same power of 2 or more from every knot examined on a range that lengthens with the rounds, under
the registered thresholds. What exists at one round reads power 1 from every member counted from, or lies wholly
within reach, in every run read. The count over the growth's whole history does read power 2 from every knot examined
on 54 runs of the capped laws at the longer of the two lengths grown, and on 111 runs under looser thresholds; one
degree of that 2 is the rounds themselves, so it says the roster is of degree 1 and no more. At the growing end, how
strongly two members' loose distinctions are related does not keep the order of their steps apart: it fails on stages
as small as seven knots, with loose counts held equal. So nothing here is a count that grows as a power above 1 in
what the growth holds at one round, and nothing at the growing end is a distance beyond what the members' own counts
explain.**

The words. **H(u, r)**, the history count, is the number of knots of every round within r holder steps of knot u, the
knots that have stopped growing included. **P(u, r)**, the roster count, is the number of members of u's part within r
steps in the roster after one round: what exists then. A count **reads power j** when it lies between two multiples of
r^j, within a factor of 2, on a stated range. **The gate** holds for a run when one j does this from every knot
examined on one common range of at least a factor 8, and **the scaling condition** when the range lengthens as the
rounds double. The answers for a run are "both", "gate only", "no gate" and "undecided". The **census** is the 3,376
starts of three to five knots of an earlier study. The laws are named in the claim: the ordinary count; the cap of
three with short knots waiting, retiring or making offshoots; the same with no cap, or caps of 2 and 4; and ten laws
with a taking rule. At the growing end, **κ** is how strongly a loose distinction of one member and one of another are
related under the weighting "each allowed state of the structure after that round once"; **δ** is the two members'
arrival delay, and the other two orders compared are their witnessed steps and their holder steps.

## Verdicts

| # | Kind | Verdict | What was found |
| --- | --- | --- | --- |
| Run 0 | controls and checks | Hold, with one frozen formula short | 30 unit tests; a ring of 400 knots reads power 1 from every knot; a tree, a 99-knot six-regular pattern and a comb read as built; the lemmas' checks pass on 136, 87 and 1,930 cases. The registered count from a made knot of a bare ring lacks its upper end (below). |
| P1 | seen in scratch | Holds | Under the cap of three with retiring, births per round are of degree 1 on a census share of 0.80 (each start once; 0.81 with each numbering once). |
| P2 | seen in scratch | **Fails** | Predicted: under a cap, no start has births of degree 2 or more. Found: 9 starts under each of the three laws with the cap of three, 13 under the cap of 4, none under the cap of 2. |
| P3 | seen in scratch | **Fails** | With retiring and no cap, 19 starts have births of degree 2 as predicted, but the share of degree 1 is 0.666, just under the two thirds predicted. |
| P4 | seen in scratch | Holds | Under the cap of three with retiring, 449 of 449 runs that reach round 100 keep the same number of parts and a constant gain of the largest part. |
| P5 | seen on two starts, open on the rest | Holds | No run passes the gate with the scaling condition at j of 2 or more; 196 of 235 runs are decided (both 21, gate only 0, no gate 175, undecided 39). Recounted by the thread from the raw records: the same. |
| P6 | seen for two sizes, sketched | **Fails as worded** | The bare rings pass the gate with j = 1 and the scaling condition at every size, as predicted. The added clause, that on the first n − 1 steps the made knots alone read power 2, fails for small rings by arithmetic and for the largest on 5 of 128 made knots. |
| P7 | open | **Fails** | The 10 runs of the capped laws that hold the gate at the shorter length all read j = 1, not 2. At the longer length 54 hold it with j = 2. |
| P8 | by argument | Holds | The fixed ration of three from one knot reads power 3, with births of degree 2. |
| P9 | seen in scratch | Holds | The roster count reads power 1 (1,700 readings), all within reach (169) or is undecided (283); none reads power 2 or more. With the third capped law added after the freeze: the same. |
| P10 | seen in scratch | Holds | Under the laws with a taking rule no run is held by hubs (0 of 7,552). |
| P11 | seen in scratch | Holds | Under parity, 434 tied pairs of loose distinctions at two knots that both pass the knot test, in 221 runs. |
| P12 | replication | Holds | The smallest stage where κ does not keep the order of δ with loose counts equal has 7 knots (one census start after round 1), under three laws. |
| P13 | replication | Holds | The registered statistic is positive under three laws (434,145; 230,767; 245,891). |
| P14 | replication | Holds | Under the ration "just enough for three places" with retiring, all 1,224 comparisons are tied in δ. |
| P15 | replication, one clause open | Undecided | Two registered order tests fail on some stage under three laws, as predicted; under the fourth law one of them is tested on no stage, so that clause cannot be judged. |

## The five questions of the claim

1. **Births per round, by law** (219 starts of three and four knots and the first 250 of five; each start once).
   Ordinary count: degree 1 on 217, constant on 84, degree 2 on 19, degree 3 on 4, ended on 145. Cap of three with
   retiring: 379, 70, 9, none, 11. No cap with retiring: 329, 106, 19, 4, 11. Cap of 2: 441, 17, none, none, 11. So
   retiring alone turns most starts that end under the ordinary count into growths of degree 1, and the cap of three
   stops births of degree 3 and about half of those of degree 2. Recounted by the thread: the same.
2. **The gate.** "Both" on 21 runs, every one with j = 1 and constant births: the seven bare rings, four small named
   starts under each of three laws, and two census starts under one. No run gives power 2 or more from every knot
   examined on a range that lengthens.
   Under the swapped thresholds (a range of a factor 4, a factor of 3 between a knot's bounds) 111 runs answer "both"
   at j = 2, so the negative rests on the registered thresholds.
3. **Laws with a taking rule.** Not held by hubs in any run, under any of the four kinds of step; 4,232 runs "not
   held" and 4,264 ended.
4. **Parity at the growing end.** Yes: on 1,602 stages some rule holds among fewer loose distinctions than all of
   them, the smallest a rule on 2 of 4 loose distinctions in a structure of 6 knots under a taking rule.
5. **Not-all-equal at the growing end.** Under the ordinary count and the three capped laws, κ fails to keep the
   order of δ, of witnessed steps and of holder steps, on stages from 6 or 7 knots up. With loose counts held equal
   the smallest stage has 7 knots; with loose counts and shared-place counts both held equal, 9 or 10 knots. Under
   the ordinary count δ equals the witnessed steps on all 74,327 pairs compared. Under "just enough for three places"
   everything is tied.

## What did not hold as worded

- **The count from a made knot of a bare ring.** The definitions give it without its upper end: it holds for r up to
  the round the knot was made in, and beyond that the count is n(t + r + 1). The engine is right; the frozen formula
  was short. One disclosed sentence fails with it: "on the first 32 steps the made knots alone read power 2" is false
  for 23, 11 and 5 of 128 made knots at 66, 132 and 264 rounds.
- **P6's clause**, as above; **P9 named a law the gate run does not grow** (grown as a supplement after the freeze);
  one registered sorting of pairs has no place for pairs in different parts before the roster is past its start; and
  the registered shuffle is not defined across several parts. Each is recorded with the reading taken.
- **Two disclosed scratch runs under taking rules are not reproduced** (other seeds, not stated); the verdict there,
  not held by hubs, is the same.

## What this shows and does not show

- **The count is of the growth's history.** A power of H includes one degree from the rounds wherever the number of
  parts is fixed. The bare ring shows it exactly: its roster is the same ring after every round, and H reads 1 beyond
  the ring's size. A reading of 2 for H on the capped laws is therefore a roster of degree 1 read through its
  history; the roster count, read on its own, never passes 1.
- **No claim about space.** Nothing here is named by space, and a count of knots within holder steps is not a
  distance read from the allowed states. No limit is taken: every count is of a finite structure at its last round.
- **The thresholds are supplied.** The gate's factor of 2 and range of a factor 8 were fixed before the run, and the
  answer at j = 2 changes under the swapped ones.
- **The growing end.** κ is graded, and under three laws the grading is not explained by loose counts alone; but it
  does not keep the order of steps or of delay, so it is not a distance in that sense on the stages read.
- **Supplied**: the laws; the starts; the knots counted from; the thresholds; the weighting of takes; the stage
  weighting; the cap on which stages are computed. **Made by births**: the structures counted.
- **Bounded**: starts of three to five knots and 15 named ones; 100 rounds for births, 66 and 132 for the gate (264
  and 528 for the bare rings), rounds 1 to 3 or 4 at the growing end.
- **Not run**: 750 of the 1,000 sampled five-knot starts of the first table (cut at the hour to a prefix fixed
  before the run); the knot test on 1,428 of 2,863 runs (every knot tested passed: 247,186 under not-all-equal and
  216,017 under parity); the exact check of the statement about uniform takes, whose probe showed more than 100,000
  histories for one numbering, so that statement stays argued and unchecked; 4,139 stages at the growing end above
  the registered cap. None of these is a negative.

## Deviations and limits

- **Readings recorded by the engine's author: 34**, each before the run it affects.
- **Under the laws with a taking rule** 70 of 451,393 knots fail the knot test under not-all-equal and 204 of 327,600
  under parity, mostly joins of many parents under the one rule that chooses by name.
- **Numberings** change "ended" against "not held" in 107 of 612 groups of runs under the rules that choose by name,
  and never give a run held by hubs.
- **A slip by the engine's author**: some of its own processes were stopped from lists matched by name, against the
  rule to stop only by process number. Each list held only its own processes.
- **Evidence class**: computed by an engine written from the frozen texts, with eight built controls; two tables
  recounted by the thread from the raw records; no second program. Scientific referee pending.
