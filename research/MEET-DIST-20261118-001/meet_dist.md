# Is the knots' nesting a distance?

Epic `MEET-DIST-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes sub-goal B198
(`MEET-TWIST-20261118-001`'s selected direction). Goal G16; tests A97 directly. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `5df037bcd` at about 04:23 UTC on 18 November. The
  run (long run MEET-DIST-B1, 315 cases on the shared runner) ended at 04:27 UTC, 315 of 315 ok.
- Code: [job.py, checks.py, merge.py and melib.py](../../experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/).
- Results: [results.json](../../artifacts/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/results.json).

## The answer

- **Before growth the nesting is not a distance; growth writes part of it into the distances, never all, and then blurs it**
  (computed, exact, every presentation of 5 to 9 distinctions). All presentations of a line have the same disagreement counts, so
  at the start the counts carry none of how the knots nest. Under KF3 one grown base's table of disagreement counts carries this
  share of the information about the bare bracketing (mutual information over entropy, prior uniform over labelled presentations):

  | Line of | k = 1 | k = 2 | k = 3 | k = 4 |
  | --- | --- | --- | --- | --- |
  | 5 | **0.63** | 0.60 | 0.39 | 0.22 |
  | 6 | 0.45 | **0.65** | 0.63 | 0.53 |
  | 7 | 0.37 | 0.57 | **0.62** | 0.58 |
  | 8 | 0.30 | 0.51 | 0.58 | |
  | 9 | 0.26 | 0.45 | 0.53 | |

  The share rises, peaks below two thirds (at k = 1, 2, 3 for five, six, seven: about n0 − 4 new distinctions), and falls.
- **It is not the growth's failure to look.** Revealing the same number of knots directly, as fills chosen at random with no growth
  (the advisor's bag-of-knots null), carries the whole of it by k = n0 − 3 (1.0 at five from k = 2, at six from k = 3, at seven at
  k = 4). KF3's grown tables carry less than the null at every k ≥ 2 (D4). The growth reveals the knots it fills and, in the same
  steps, confuses which knots they were: later fills are fills of re-bracketed triples, and up to renaming they mix.
- **In law the nesting is fully readable from k = 1** (D1, D2). Different bare bracketings give different laws of grown tables from
  the first new distinction, and every two presentations that are not mirror images from the second. At k = 1 some presentations
  with one bare bracketing tie (1, 2, 17 and 41 pairs at six to nine), as the advisor predicted from mirrored self-mirror regions.
- **The labels matter.** The unlabelled multiset of the table's entries carries less than the full table from k = 2 (D5): from
  0.12 to 0.42 of the information, against 0.40 to 0.65 for the full table.
- **And the distance between grown distinctions is not the nesting** (by hand, before the run). Two fill points' disagreement
  count measures steps along the line between the distinctions their triples do not share, not how far apart the knots nest: 4
  for the end placement's knots (0,1,2) and (0,2,3), 6 for the middle placement's (0,1,2) and (0,2,4), though each pair shares a
  pair of distinctions.
- **Distance and states are the same here** (DISTANCE-ORDER's statement 3(a), checked): for these bases the table with the state
  count determines the allowed states, so what the grown distances miss of the nesting, the grown states miss too. The share not
  carried is not held in some other form; the growth does not keep it.

**In the owner's terms.**
- How the knots meet starts as information that no distance holds: every presentation of the line has the same distances.
- Growth turns part of it into distance. A grown base's distances tell how the knots nest better than chance, best after a few
  new distinctions, but at most about two thirds of the way, and later growth blurs it again.
- Read off the distances as plain numbers, without knowing which distinction is which, they tell much less.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 4 gate checks pass | held | table classes = state classes on five and six to n0 + 3 |
| D1 | In law, different bare bracketings differ from k = 1 (5 to 9) | held | no equal pair at any k ≥ 1 |
| D2 | In law, non-mirror presentations differ from k = 2 (5 to 9) | held | no equal pair at k ≥ 2; at k = 1, 1, 2, 17, 41 ties within one bare bracketing (six to nine) |
| D3 | The share is largest at k = 1 or 2 and smaller at the last k, every n0 | **failed** | holds for five and six; seven peaks at k = 3; eight and nine still rise at k = 3, the last computed |
| D4 | KF3 below the bag-of-knots null at every k ≥ 2 where it exists | held | every n0 and k |
| D5 | The unlabelled multiset below the full table from k = 2 | held | every n0 and k |

4 of 5 held. D3 failed by timing, not direction: the peak moves later as the line grows (about n0 − 4 new distinctions), and the
fall is seen for five, six and seven.

## What it means for A97 and the goals

- **A97** stays under challenge, with a quantitative finding. How the knots nest is information that no distance holds before
  growth; KF3 writes up to about two thirds of it into a single grown base's distances, and the rest is lost, not hidden: in these
  bases the distances determine the states. Under the owner's premise the nesting is a distance only in part, and only after
  growth.
- **G16:** capability gained. The information a grown base's distances carry about how the knots nest, measured exactly against a
  null and an ablation.

## Limitations

- Fewest-knot presentations, KF3, up to k = 4 (three for eight and nine); the long-growth fade is seen for five to seven only.
- One prior (uniform over labelled presentations of one labelling); shares, not naming chances, are the headline because chains
  dominate that prior.
- The disagreement count is the one distance read (A98's reading).

## Reproduce

```sh
cd experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables
../../../.venv/bin/python -B checks.py
cd ../../..
.venv/bin/python -B scripts/longrun.py launch experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/job.py \
  --out <dir> --unit <name> --workers 12 --case-mem 1G
.venv/bin/python -B experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/merge.py <dir>
```

## Advisor

Consulted once before the freeze. It reproduced the hand count at five, showed that the first D2 (from k = 1) was false at six,
judged the rising and threshold predictions unlikely, and argued that the design tested memory of the presentation rather than
nesting as a distance. Its sharper tests became the bag-of-knots null (D4), the multiset ablation (D5) and the literal test
settled by hand. Not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is the knots' nesting a distance | **Status:** Successful (referee pending) | Exact: none before growth, at most about two thirds after, peaking near n0 − 4 new distinctions; 4 of 5 held |
| Local direction: how knots meet as information under KF3 | Continue | The fade's long-run limit and which part of the table carries it are open |
| Broader exploration: A97 on other growths and readings | Searching | One rule, one distance reading |
| Long-term goal: G16 Learning the rules behind what a system allows | Capability gained | A measured transfer of knot information into distance |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Long growth: does a single grown base's share fall to zero, and how fast in n0 and k? | 2/3 | 3/3 | Sample KF3 to k = 20 from every presentation of 6 and 7 with a plug-in estimate and a floor → a rate, or a floor above zero | Selected · awaiting go-ahead |
| 2 | Which part of the table carries the nesting: the old-by-new block, the new-by-new block, or the old-by-old block | 2/3 | 3/3 | Information shares per block, exact, five to seven → stop at the block that carries most | Alternative · deferred |
| 3 | Prove the k = 1 value: one fill reveals one knot's triple up to mirror, so the k = 1 share is a function of the knots' position types | 1/3 | 3/3 | Write the formula and check it on 5 to 9 → stop at a proof | Alternative · deferred |

- **#1.** Payoff: whether the nesting's trace in distance is transient or lasting bears on A97's reading over time. Concreteness:
  sampling code exists; exact laws are out of reach past k = 4.
- **#2.** Payoff: says where the trace sits. Concreteness: a re-reading of the same runs with block keys.
- **#3.** Payoff: small; the k = 1 mechanism is understood. Concreteness: high.

**Corrections:** none.

**Goals:** a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 under challenge, with this finding added; A100 gains this study among what rests on it; no new entry.

**Basket:** read; B198 taken by this epic.
