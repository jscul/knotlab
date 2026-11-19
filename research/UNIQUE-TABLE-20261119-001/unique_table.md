# Does the bond-distance table fix every census arrangement it has no symmetry for?

Epic `UNIQUE-TABLE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `CENSUS-READ-20261118-001#1`.
Assumption A97; goal G1. **Referee pending.**

**Record.**
- Pre-registration, frozen before any population stage ran (commit `db461d862`), and Amendment 1 (commit `537ba66a9`, before any
  result was read): [preregistration.md](preregistration.md).
- Code: [the experiment family](../../experiments/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/) (`uniq.py`,
  `job.py`, `job_amend.py`, and after the run `realize.py`, `verify_rivals.py`, `pairs.py`, `final_readout.py`).
- Results: [final.json](../../artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/final.json),
  [summary.json](../../artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/summary.json),
  [realize.json](../../artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/realize.json),
  [verify_rivals.json](../../artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/verify_rivals.json),
  [pairs.json](../../artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/pairs.json).

## The answer

**In the owner's terms.**
- **No: distances do not carry everything but their own symmetries.** On 6 of the 527 census stages examined, a second arrangement
  has exactly the same table of bond distances, every one of 120 to 210 pairs, and different allowed states. No exchange of
  distinctions turns one into the other: the table has no symmetry to blame. Both are legal as arrangements: the same number of
  junctions, each of at least three distinctions, no two sharing two, none at a cut vertex.
- **The table misses something the growth needs at once.** Grown as a new start (every junction with a loose distinction live), in
  5 of the 6 the rival cannot take a single step under the cheapest counts (it stalls) while the true arrangement grows 3; under the
  census's own continuation (only the round-1 junctions live, as the truths actually grow) those five rivals grow 4 against 3 (the
  referee's reading, corrected here). In the sixth both grow, by different joins. Either way the law separates them at its next step. So two arrangements with one
  table differ in what can form next. A three-way reading (the least consequence holding three distinctions) tells them apart
  (116 to 208 triples differ); the count of allowed states in which two distinctions disagree does not (for parity it is the same
  for every pair).
- **What the table cannot hold, what the states cannot hold, and what was the reader's weakness, kept apart.**
  - Its own symmetries: none here by the choice of population (a short lemma below); across the census they hide junctions on
    1,480 stages where junctions meet once (`CENSUS-READ-20261118-001`).
  - Same allowed states, other junctions: 72 of the 527 (13.7%), and 61 of 1,389 control stages the reader had read (4.4%). No
    table can decide these, since the table is a function of the allowed states; this is what A108 says the growth reads and the
    states do not hold. At a stage where no two junctions cut the rest apart, such a rival exists exactly when the loose
    distinctions number at least three and at most one junction holds two or more of them (then that junction becomes the outside).
  - Different allowed states, same table: the 6.
  - The reader's weakness: 428 of the 527 (81%) are unique within the bound, so the table fixes them and the reader missed them.
  - Undecided by this method: 21 (4.0%).
- **How the six differ.** In five, two junctions that share one distinction trade one distinction each. In one, a single junction
  holds a loose distinction instead of a shared one. Two mechanisms, not one.

| Stages | Count | Unique within the bound | Same states, other junctions | Other states, same table | Undecided |
| --- | ---: | ---: | ---: | ---: | ---: |
| Population (symmetry-free, reader misread) | 527 | 428 | 72 | 6 | 21 |
| … 3-connected | 176 | 127 | 44 | 0 | 5 |
| … with a 2-separation | 335 | 299 | 14 | 6 | 16 |
| … closed (nothing loose) | 15 | 1 | 14 | 0 | 0 |
| Controls (symmetry-free, reader exact) | 1,389 | 1,328 | 61 | 0 | 0 |

The six pairs (arrangements on the same named distinctions; the junctions that differ):

| Stage | Start, round | True junctions that differ | Rival's | Next round, cheapest counts (grown as a new start) |
| --- | --- | --- | --- | --- |
| pop-0007 | knots of 3,3,3,3,5, round 1 | [6,9,11,12] | [6,11,12,13] | both grow 3, different joins |
| pop-0236 | 3,3,5,5,5, round 1 | [4,5,9,10,11], [7,8,9,12,13,14,15] | [4,5,9,10,14], [7,8,9,11,12,13,15] | truth grows 3; rival stalls |
| pop-0308 | 3,4,4,5, round 1 | [3,4,8,9,10], [5,6,7,8,11,12] | [3,4,8,9,11], [5,6,7,8,10,12] | truth grows 3; rival stalls |
| pop-0338 | 3,4,4,5,5, round 1 | [3,6,10,11,12], [7,8,9,10,13,14,15] | [3,6,10,11,14], [7,8,9,10,12,13,15] | truth grows 3; rival stalls |
| pop-0442 | 3,4,5,5,5, round 1 | [5,6,9,10,11], [8,9,12,13,14,15] | [5,6,9,10,14], [8,9,11,12,13,15] | truth grows 3; rival stalls |
| pop-0501 | 4,4,5,5,5, round 1 | [5,6,10,11,12], [8,9,10,13,14,15,16] | [5,6,10,11,15], [8,9,10,12,13,14,16] | truth grows 3; rival stalls |

Five of the six have a second rival of the same kind (11 rivals in all), each verified the same way.

## The bound, and what is proved against what is exhaustive

- **The rivals considered (frozen).** Arrangements on the same named distinctions with every distinction in one or two junctions,
  every junction of at least three distinctions, no two junctions sharing two, every junction a bond of the rival (no cut vertex
  but the outside one), and at most as many junctions as the truth. Junction sizes are not bounded. This is legality as a static
  arrangement. Whether a rival can be grown from some start by the cheapest counts is a further question: for the six, the rival's
  junctions with no loose distinction, taken as a start and grown one round, do not give the rival (the truth passes the same test),
  so they are not round-one stages of their own start; other histories were not tried.
- **Forcing (argued sound; computed per stage).** A pair at table distance d lies in some circuit of d + 1 distinctions in every
  matching code, and every pair of such a circuit is at distance at most d; candidates that strictly contain a forced word, or whose
  span with the forced words holds a word lighter than the least circuit through one of its distinctions, are dropped; a pair left
  with one candidate forces it. Forcing reached the true equations on 392 of the 527; then, within the bound, every rival has the
  true equations.
- **Same equations (complete by Whitney's theorem; enumerated).** Each block of the true graph through its whole class of twists at
  2-separations, re-glued at one vertex, which the bound makes the outside vertex, every combination checked for legality.
- **One equation missing (exhaustive per stage).** Where forcing reached rank n − 1 (121 stages), every code of rank n containing
  the forced words was tested against the table by its own circuits (up to 2^16 cosets; 9 stages above the cap are undecided).
  Codes other than the truth's with the same table appeared on 26 stages; an exhaustive search over n-sets of their circuits found
  legal arrangements spanning them on 6, and none on the other 20.
- **Verification.** Every rival found was
  checked directly: its own exact table equals the truth's on every pair (same-equation rivals on all 166 stages where they were
  found, development set included); for the 11 different-equation rivals, also with a second, independent brute-force table
  code (`RING-READ-20261118-001A`'s), with no cut vertex but the outside one, and as not isomorphic to the truth as arrangements.
- **Lemma (no symmetric rival here).** If a rival were π(truth) for an exchange π of distinctions with the same table, π would keep
  the table, and every such exchange keeps the true junctions on this population; so the rival would be the truth.

## Predictions and verdicts

| # | Prediction | Verdict |
| --- | --- | --- |
| G | Every rival found verifies (same table; same equations where so classed) | held (same-equation rivals on 166 stages; the 11 different-equation rivals verified separately) |
| U1 | Forcing reaches the true equations on at least half | held (392 of 527, 74%) |
| U2 | No rival with different equations | **failed** (6 stages) |
| U3 | Every closed stage has a same-state rival | **failed** by one (14 of 15) |
| U4 | At 3-connected stages, a rival exactly when the loose set has at least 3 distinctions and no junction holds two | **failed** (66 stages have one where a junction holds two loose distinctions: that junction can become the outside); corrected after the run, "at most one junction holds two or more", it matches all 501 3-connected stages (population and controls) |
| U5 | At least half of the decided stages have a same-state rival | **failed** (78 of 506 have a rival of either kind; 72 same-state) |
| U6 | At most a tenth of the controls have one | held (61 of 1,389) |

## Known results, and what this adds

Known: Whitney's 2-isomorphism theorem (1933) for graphs with one cut space; codimension-one extensions of graphic matroids (Shih,
1982, as the advisor recalled, not checked); the program's own tables that hide a junction behind a table symmetry
(`VARIABLE-OUTPUT-READER-20261118-001K`, `-001L`, under the other law) and that lose which distinction was spent while keeping what
can form next (`-001N`, as the coordinator relayed). What this adds: on the cheapest-count census, without any table symmetry, two
non-isomorphic legal arrangements can share their whole bond-distance table with different allowed states, and the growth law
tells them apart at its very next step; and an exact split of the reader's failures into the table's limits (6 + the states' 72)
and the reader's own (428).

## Limitations

- The bound is static legality with at most n junctions; rivals with more junctions are not covered (the one-missing search covers
  only codes of the truth's rank), and reachability by growth was tested only for round one from the rival's own start.
- 21 stages are undecided (forcing two or more equations short, or the coset search over its cap).
- The population is the census's symmetry-free stages of at most ten junctions where junctions meet once and the reader failed;
  stages where knots share two distinctions (92% of census starts) are outside it.
- U4's criterion was corrected after the run; the corrected one is post-hoc.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md)). It confirmed that forcing is sound, showed that my claim "a larger code forces a vertex
splitting" is false in general (which led to the bound of at most n junctions), required the outside choice per block and the
closure of twists, and supplied the symmetry lemma. Its criterion for 3-connected stages was one case short (U4). It expected no
different-states rival at 3-connected stages: right (all six have a 2-separation); and "at most a handful" of them overall: right.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is the census arrangement the only one with its table, symmetries aside? | **Status:** Successful | Stop condition reached: 6 stages have a non-isomorphic legal arrangement with the same table and other allowed states; 428 are unique within the bound, 72 have a same-states rival, 21 undecided |
| Local direction: what reading of a base is complete | Continue | Three-way readings separate all six; whether the law's own arrangements can collide is open |
| Broader exploration: what distances carry (A97) | Known alternatives | Codex's law-aware results on reachable histories; table symmetries; same states with other junctions (A108) |
| Long-term goal: G1 Space from a law, with A97 | Obstruction learned | Pair distances are not a complete description even up to their own symmetries; the growth law reads the difference at once |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do two arrangements the cheapest growth actually reaches ever share a table with different states? | 3/3 — the law-level answer to A97's premise, comparable with Codex's reachable histories | 2/3 — the census stages and the pipeline exist; pairs must come from two grown stages | compare the exact tables of all symmetry-free census stages of equal size, by a canonical form of the table → stop at a grown pair with one table and other states, or none at these sizes | Selected · awaiting go-ahead |
| 2 | Is the table with three-way readings complete on the 527? | 2/3 — names the reading a complete description needs | 3/3 — the readings are computed | repeat the forcing and rival search with three-way readings → stop at all decided unique, or a pair sharing them too | Alternative · deferred |
| 3 | Rivals with more junctions than the truth (beyond the bound) | 2/3 | 2/3 | codes of rank n + 1 containing the forced words on the 428 → stop at one matching legal arrangement, or none | Alternative · deferred |
| 4 | The 21 undecided stages | 1/3 | 3/3 | raise the coset cap; two missing equations | Alternative · deferred |
| 5 | B203 (a clock), B204 (a learner's gap) | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none of a published claim (U2 to U5 were predictions and failed as recorded). **Goals:** G1 checkpoint (obstruction
learned); no goal changed. **Assumptions:** A97 gains this study (against its strong reading), status unchanged; A108 gains it
(72 same-states rivals the table cannot decide). **Basket:** B196, B202, `BOND-BALLS-20261111-001#2`; B203, B204.

## Referee R1 (2026-11-19)

[Report](referee-R1/report.md), its own code. **Confirmed, no Block; two wording points, corrected and logged in
`docs/CORRECTIONS.md` (Not a block).** All six pairs (11 rivals) check: legal as static arrangements, tables equal entry by entry by
two of its methods, equation spaces differ, not isomorphic, every symmetry of the truth's table keeps its junctions. Forcing with
elimination is sound; the Whitney enumeration with per-block outside choice is complete for the bound; its own exhaustive search
agrees on all 1,867 stages both decided.
- **Which reading "the rival stalls" uses** (corrected above): as a new start the five rivals stall; under the census's continuation
  they grow 4 against the truth's 3.
- **Same-equation rival counts** (summary.json, the 166 stages of G) include on 51 stages the truth plus the loose set as one more
  junction, one over the frozen bound (at most n junctions); `final.json`'s classes apply the bound, and no verdict depends on it.
- **Reachability (the referee's test).** Taking every connected subset of a target's junctions as a start and growing one or more
  complete rounds, every truth is reached and none of the 11 rivals is, from any start after any number of rounds; under Codex's
  serial mixed law (its full-law census, widths 16 to 21) neither the rivals nor the truths are reachable. So the six are
  collisions of static arrangements that the law does not make; they bound Codex's line rather than contradict it: so far reachable
  collisions are related by a table symmetry, and collisions without one are unreachable. `GROWN-PAIR-20261119-001` tests whether the
  two can meet.

## Final report as sent (2026-11-19 05:57 UTC)

**Outcome:** no, distances do not carry everything but their own symmetries. On 6 of the 527 census stages examined, a second legal arrangement has exactly the same bond distance between every two distinctions but different allowed states, and no table symmetry turns one into the other. Closed, referee pending.

- **The six pairs.** In five of them, two junctions that share a distinction each trade one distinction; in the sixth, one junction holds a loose distinction instead of a shared one. All 120 to 210 pairs agree, checked by two independent table codes, and the two arrangements are not isomorphic. The growth law tells them apart at its very next step. In five, the rival cannot grow at all (it stalls) while the true arrangement grows; in the sixth, both grow, but by different joins. A reading of three distinctions at a time separates all six; the disagreement count cannot.
- **The three kinds, kept apart.**
  - **What the table cannot hold, its own symmetries:** none here, by the choice of stages. Across the census they hide junctions on 1,480 stages.
  - **What the allowed states cannot hold, same states but other junctions:** 72 of the 527, and 61 of 1,389 stages the reader had read. No table can decide these. At a stage that no two junctions cut apart, this happens exactly when there are at least three loose distinctions and at most one junction holds two of them.
  - **What only the table cannot hold, other states with the same table:** the 6.
  - **The reader's own weakness:** 428 of the 527 (81%) are fixed by their table within the bound, and the reader just missed them. Another 21 are undecided.
- **The bound.** Rivals are judged legal as static arrangements: at most as many junctions as the truth, no junction smaller than three, no two junctions sharing two distinctions, and no junction at a cut vertex. Junction sizes are not capped. The forcing step is argued sound; the searches are exhaustive within the bound. The six rivals are not one round's growth from their own start; other histories are untested, so they are legal but not shown to be reachable.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is the arrangement the only one with its table, symmetries aside? | **Status:** Successful | Stop condition reached: 6 non-isomorphic legal rivals with one table and other states; 428 unique, 72 same states, 21 undecided |
| Local direction: what reading of a base is complete | Continue | Three-way readings separate all six; whether two grown arrangements can collide is open |
| Broader exploration: what distances carry (A97) | Known alternatives | Codex's results on reachable histories; table symmetries; same states, other junctions (A108) |
| Long-term goal: G1, with A97 | Obstruction learned | Pair distances are not a complete description even up to their symmetries; the law reads the difference at once |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do two arrangements the growth actually reaches share a table with different states? | 3/3 — the law-level answer, comparable with Codex | 2/3 | compare canonical tables of all symmetry-free census stages of equal size → stop at a grown pair, or none | Selected · awaiting go-ahead |
| 2 | Are the table plus three-way readings complete on the 527? | 2/3 | 3/3 | rerun the search with three-way readings → stop at all unique or a pair | Alternative · deferred |
| 3 | Rivals with more junctions than the truth | 2/3 | 2/3 | codes of rank n + 1 on the 428 | Alternative · deferred |
| 4 | The 21 undecided | 1/3 | 3/3 | raise the caps | Alternative · deferred |
| 5 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none of a published claim. U2 to U5 were predictions and failed as recorded; U4's rule was corrected after the run. **Goals:** G1 checkpoint (obstruction learned). **Assumptions:** A97 and A108 gain this study, statuses unchanged. **Advisor:** Fable 5.2, before the freeze. It confirmed that forcing is sound, refuted my claim about larger equation spaces (hence the bound), and required the outside to be chosen per block. Its rule for the rigid stages was one case short.

Referee hand-off: the decision note is `research/UNIQUE-TABLE-20261119-001/unique_table.md`. Check these most closely: the six pairs (`verify_rivals.json`, tables and legality), the soundness of forcing with elimination, and whether the Whitney enumeration with per-block outside choice is complete. The prior-work line is in the pre-registration.
