# Do three-way readings complete the bond-distance table?

Epic `THREE-WAY-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `UNIQUE-TABLE-20261119-001#2` and
`GROWN-PAIR-20261119-001#1`. Assumption A97; goal G1. **Referee pending.**

**Record.** Pre-registration, frozen before the run: [preregistration.md](preregistration.md). Code and result:
[triples.py](../../experiments/THREE-WAY-20261119-001A/THREE-WAY-20261119-001A-E001_triples/triples.py),
[triples.json](../../artifacts/THREE-WAY-20261119-001A/THREE-WAY-20261119-001A-E001_triples/triples.json). The first run stopped
on a module-name collision before computing anything; the fix is committed separately.

## The answer

**In the owner's terms.**
- **Yes, up to the allowed states.** Add, for every three distinctions, the size of the smallest consequence that holds all three
  (less one) to the pair distances, and every collision with different allowed states found so far comes apart.
  - The 11 static rivals of `UNIQUE-TABLE-20261119-001` each differ from the truth in 116 to 208 of their triples.
  - The 152 reached groups of `GROWN-PAIR-20261119-001` each come apart: no renaming that matches their pair tables also matches
    their three-way readings. The advisor had bet against this.
  - The 23 stages the pair table left undecided are all decided with triples: forcing reaches the true equations on every one. Of
    those, 21 are unique and 2 have a rival with the same states.
- **What three-way readings cannot add.** Arrangements with the same allowed states and other junctions remain alike, because every
  reading of the allowed states treats them alike. That leaves 74 of the 527 (72 + 2); only the growth law, which reads the
  junctions, can tell them apart.
- **So the three things, again.** On these stages:
  - pair distances miss some allowed states (the 6 static and 152 reached collisions);
  - pair plus three-way readings miss none found;
  - the allowed states themselves miss which junction holds what (74 stages, and 4,474 reached groups).

| Test | Count | Separated by three-way readings |
| --- | ---: | ---: |
| Static rivals with the same pair table and other states (UNIQUE-TABLE) | 11 | 11 |
| Reached groups with one pair table and other states (GROWN-PAIR) | 152 | 152 |
| Undecided stages, now decided by forcing with triples | 23 | 23 (21 unique, 2 same-states rival) |
| Same-states rivals (any reading of the states) | 74 | 0, by construction |

## Predictions and verdicts

| # | Prediction | Verdict |
| --- | --- | --- |
| T1 | All 11 different-states rivals differ in some three-way reading | held (116 to 208 triples each) |
| T2 | Forcing with triples decides at least half of the undecided, and no other code matches both readings | held (23 of 23 forced to the true equations) |
| T3 | Three-way readings separate all 152 reached groups | held (152 of 152; the advisor bet against it) |

## Method

Three-way readings come from the circuits of each equation space ("none" when no circuit holds all three). Forcing with triples
works as follows: a triple at reading d lies in a circuit of d + 1 distinctions, all of whose pairs and triples read at most d. A
candidate is dropped if it holds a triple read above its size less one, if it contains a forced circuit, or if it sits inside one.
A unique survivor is forced. For the reached groups, one isomorphism test per group is run on the pair table with every triple
attached as a vertex labelled by its reading.

## Known results, and what this adds

Known: three-way readings separate the width-32 pair of `VARIABLE-OUTPUT-READER-20261118-001E` under the other law; the pair-table
collisions of `UNIQUE-TABLE-20261119-001` and `GROWN-PAIR-20261119-001`. What this adds: on every collision found so far under the
cheapest growth, static or reached, three-way readings recover the allowed states, so pair plus three-way readings are complete up
to the allowed states there; the remaining gap is the states' own (which junction holds what).

## Limitations

- These are the collisions found so far: up to 10 junctions (static) and up to 14 (reached). That three-way readings suffice in
  general is not shown; differences visible only to four or more distinctions were not found here but were not ruled out.
- "States" are equation spaces (no signs), as in the predecessors.

## Advisor

Fable 5.2 before the freeze ([answer](advisor/answer_1_fable.md)). It confirmed the settled-by-construction point and the soundness
of forcing with triples, and added the "sits inside" filter (taken). It bet on the 11 and against all 152, reasoning that circuit
readings see only supports and that differences may first show at four. That bet was wrong here: all 152 were separated.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three-way readings on the known collisions | **Status:** Successful | All 11 static rivals and 152 reached groups separated; the 23 undecided stages decided |
| Local direction: what reading of a base is complete | Continue | Pair plus three-way readings are complete up to the allowed states on everything found; the gap left is the states' own |
| Broader exploration: what distances carry (A97) | Known alternatives | The same pattern as Codex's width-32 example under the other law |
| Long-term goal: G1 with A97 | Capability gained | A reading that recovers the allowed states where pair distances do not |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | B205: reached collisions where junctions meet once, 15 to 24 junctions (and 25 to 40) | 3/3 | 2/3 | the census's meet-once grown stages → stop at an other-states pair, or none | Selected · started next in this thread (the coordinator's go-ahead) |
| 2 | Are pair plus three-way readings complete beyond the found collisions? Search for a pair agreeing on both with other states | 2/3 | 2/3 | the 4,474 same-states groups are out by construction; search static rivals agreeing on triples at up to 10 junctions → stop at one or none | Alternative · deferred |
| 3 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 gains this study, status unchanged.
**Basket:** B205 taken next; B203, B204 remain.

## Final report as sent (2026-11-19 08:38 UTC)

**Outcome:** yes, up to the allowed states. Add three-way distances (the smallest consequence holding three given distinctions) to the pair distances, and every collision with other allowed states found so far comes apart. Closed, referee pending.

- **What comes apart.** All 11 static rivals from UNIQUE-TABLE separate, each differing in 116 to 208 triples. So do all 152 reached groups from GROWN-PAIR; the advisor had bet against that. The 23 stages that pair distances left undecided are now all decided: 21 unique, and 2 with a same-states rival.
- **What stays alike.** Arrangements with the same allowed states and other junctions stay alike, 74 of the 527, because no reading of the states can tell them apart. Only the growth law, which reads the junctions, can.
- **The three gaps.** Pair distances miss some states. Pair plus three-way distances miss none found so far, though not proved in general. The states themselves miss which junction holds what.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three-way readings on the known collisions | **Status:** Successful | 11 + 152 separated; 23 undecided decided |
| Local direction: what reading of a base is complete | Continue | Complete up to the allowed states on everything found |
| Broader exploration: what distances carry (A97) | Known alternatives | Same pattern as Codex's width-32 example |
| Long-term goal: G1 with A97 | Capability gained | A reading that recovers the states where pair distances do not |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | B205: reached collisions where junctions meet once, 15 to 24 (and 25 to 40) junctions | 3/3 | 2/3 | meet-once grown stages → stop at an other-states pair, or none | Selected · started next in this thread |
| 2 | Search for a pair agreeing on both readings with other states | 2/3 | 2/3 | static rivals agreeing on triples, up to 10 junctions | Alternative · deferred |
| 3 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 gains this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. It confirmed soundness and added one filter. It bet against T3 and was wrong.

Referee hand-off: the decision note is `research/THREE-WAY-20261119-001/three_way.md`. Check most closely the triple readings and the group test in `triples.py`.
