# Do two arrangements the cheapest growth reaches share a bond-distance table with different states?

Epic `GROWN-PAIR-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `UNIQUE-TABLE-20261119-001#1`.
Assumption A97; goal G1. **Refereed (R1): confirmed, no Block, no Narrowing; three record points folded in (Referee R1 below).**

**Record.** Pre-registration (frozen, commit `6d8f1cdca`) and Amendment 1 (`6d894fd0d`, after the first pairing script ran out of
time, before any pair was read): [preregistration.md](preregistration.md). Code:
[the experiment family](../../experiments/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs/) (`job.py`, `pairs2.py`;
after the run `other_states.py`, `two_rounds.py`). Results:
[pairs2.json](../../artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs/pairs2.json),
[other_states.json](../../artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs/other_states.json),
[two_rounds.json](../../artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs/two_rounds.json).
`pairs2.json`'s next-stage tally (`other_state_grown_groups_next_stage`: 79, 3, 70) is an earlier pass by hash with one provenance
per arrangement, superseded by `other_states.json`'s exact 85 / 3 / 64, which the note uses and the referee reproduces.

## The answer

**In the owner's terms.**
- **Yes: the growth itself makes such pairs, and the table does not catch up.** Among the census stages of up to 14 junctions that
  the cheapest growth reaches in complete rounds, 152 groups of non-isomorphic grown arrangements have the same bond-distance table
  (up to renaming the distinctions) but different allowed states. No exchange of distinctions relates them, so these are reachable
  collisions with no table symmetry behind them. Every one of them comes from a start in which two knots share two distinctions.
- **They stay together.** Of the 88 such groups whose next stage is in range, 85 again have one table and still different states one
  round later, and all 54 checked two rounds later as well. So within two rounds the growth does not separate them at the level of
  distances, unlike the six static rivals of `UNIQUE-TABLE-20261119-001`, which the law never makes and which differ at once.
- **Where junctions meet at most once, no such pair appears at up to 14 junctions** (and, by the referee's check, at 15 and 16).
  80 groups of grown arrangements of that kind share a table, and in
  every one of them the allowed states are the same up to renaming: the arrangements differ only in which junction holds what. So
  at these sizes the knots that share two distinctions are what lets distances lose the states.
- **Sharing a table is common; sharing it with other states is rare.** The 52,163 stages are 51,959 non-isomorphic arrangements;
  32,207 of them share
  their table with another (9,498 groups); 4,626 groups contain two or more grown arrangements; 4,474 of those agree in their states
  up to renaming, and 152 do not.

| Groups of non-isomorphic stages with one table (up to renaming) | Count |
| --- | ---: |
| All (any provenance) | 9,498 |
| With two or more grown arrangements | 4,626 |
| … of these, states agree up to renaming (same states, other junctions) | 4,474 |
| … of these, other states | 152 (151 with two state groups, one with three) |
| … … next stage in range: one table again, states still differ / tables differ | 85 / 3 |
| … … two rounds on, in range: one table, states differ | 54 of 54 |
| Grown groups where junctions meet at most once: states agree / differ | 80 / 0 (the referee's 81 adds one group that also holds a stage where two junctions share two; same states) |

## The two notions, and what is counted

- **Legal as a static arrangement** (`UNIQUE-TABLE-20261119-001`'s bound) against **reached by growth** (here): a census stage of
  rounds 1 to 8 under the cheapest counts in complete rounds from one of the 26,441 starts. Starts (round 0) are counted apart; a
  group is grown–grown when two or more of its arrangements are reached at round 1 or later. No other-states group has two members
  from the same start.
- **Up to renaming.** Two stages have their own distinctions, so "same table" means some bijection of distinctions carries one
  table onto the other (exact isomorphism, VF2); "same states" means some such bijection also carries one equation space onto the
  other (no value flips). Earlier studies compared arrangements on shared names; this is the weaker, fair notion for two stages.
- **Codex's serial mixed law** was not run; this is the complete-round law only. The referee's census for the serial law (to width
  31) is the place to repeat it.

## Predictions and verdicts

| # | Prediction | Verdict |
| --- | --- | --- |
| G | No arrangement carries two tables | held (0 of 51,959 classes) |
| P1 | At least one non-isomorphic pair with one table | held (9,498 groups) |
| P2 | At least one grown–grown pair | held (4,626 groups) |
| P3 | No grown–grown pair where junctions meet once on both sides | **failed** (80 groups), but all of them have the same states |
| P4 | Every grown–grown pair grows differently within two rounds | **failed** (85 of 88 other-state groups have one table again at the next round, 54 of 54 two rounds on) |
| P5 | At least one grown–grown pair with other states | held (152 groups) |

## How it was done

Every census stage of at most 14 junctions (52,163 stages) was regrown, and its exact full table computed (every pair, every bond).
Each table was given a Weisfeiler–Leman hash, an isomorphism invariant, and the same was done for each arrangement. Arrangements
were deduplicated by exact isomorphism, with every provenance kept. Within each hash bucket, arrangements were grouped by exact
table isomorphism: VF2, with nodes coloured by their Weisfeiler–Leman subgraph hashes. Grown arrangements within a table group were
then grouped by states, using the table with its circuits attached. Next stages are the census's own continuation (round + 1 and
round + 2 from the same start), not a replay from the junctions alone (the UNIQUE-TABLE referee's lesson).

## Known results, and what this adds

Known: Codex's reachable collisions under the serial mixed law (`VARIABLE-OUTPUT-READER-20261118-001K`, `-001L`, `-001N`), each
related by a table symmetry and keeping what can form next; `UNIQUE-TABLE-20261119-001`'s six static collisions without a symmetry,
none reachable (its referee). What this adds: under complete rounds the law itself reaches collisions with no table symmetry, 152
groups at up to 14 junctions, all from starts whose knots share two distinctions; they persist at the table level for at least two
rounds; and where junctions meet once, reached collisions keep the states.

## Limitations

- Up to 14 junctions per stage, the census's starts, complete rounds only; the serial law not run.
- Where junctions meet once, other-state collisions might appear at larger sizes; not tested.
- "Persist" is checked at the table level (table isomorphism and states) for up to two rounds where the next stages stay within 14
  junctions (64 and 31 groups fell outside).

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)): deterministic hashing,
seeded VF2, the sanity check, deduplication with provenance, starts apart, results by size, states stated existentially over table
isomorphisms and decided by one combined test (all taken). Its guesses: a pair at all about 70% (held), a grown–grown pair without
a symmetry about 30% (held), among meet-once stages about 35% (a same-states pair held; no other-states pair).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: two reached arrangements with one table and other states | **Status:** Successful | 152 grown groups at up to 14 junctions, no table symmetry between them, all from starts whose knots share two distinctions; they persist two rounds |
| Local direction: what reading of a base is complete | Continue | Where junctions meet once, reached collisions keep the states here; three-way readings are the next test |
| Broader exploration: what distances carry (A97) | Known alternatives | Codex's serial-law collisions with a symmetry; static collisions without one (unreachable); now reached ones without one |
| Long-term goal: G1 with A97 | Obstruction learned | Distances alone do not carry the allowed states of what the law builds once knots share two distinctions |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Are the table plus three-way readings complete on the 527 symmetry-free stages (UNIQUE-TABLE's #2)? | 2/3 — names the reading a complete description needs | 3/3 — the readings and the search exist | rerun forcing and the rival search with three-way readings → stop at all decided unique, or a pair sharing them too | Selected · awaiting go-ahead (the coordinator's next) |
| 2 | Where junctions meet once, do reached collisions with other states appear at 15 to 24 junctions? | 3/3 — whether the clean case is safe | 2/3 — pooled tables for buckets, exact ones for candidates | the census stages of 15 to 24 junctions, meet-once only → stop at a grown other-states pair, or none | Alternative · deferred |
| 3 | The same comparison under Codex's serial mixed law | 2/3 | 2/3 | the referee's serial census to width 31 | Alternative · deferred |
| 4 | Do the 152 ever separate (more rounds, larger stages)? | 2/3 | 3/3 | follow each group to round 8 with exact tables beyond 14 junctions | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (obstruction learned). **Assumptions:** A97 gains this study (status unchanged; its
sharper test now answered for complete rounds, with knots sharing two). **Basket:** #2 is 3/3 and untaken, so it is recorded as a
sub-goal (B205); B203, B204 remain.

## Referee R1 (2026-11-19)

[Report](referee-R1/report.md), its own growth engine, tables and searches. **Confirmed, no Block, no Narrowing; three record points,
folded in above and logged in `docs/CORRECTIONS.md` (Not a block).**
- **The 152.** Every listed pair regrown from its start: not isomorphic, exact tables isometric, states different by an exact search
  over every table isometry; every start has two knots sharing two distinctions. Full membership rebuilt (460 grown stages): 151
  groups have two state groups and one has three; no start reaches two state groups of one group.
- **Next stages.** 85 / 3 / 64 one round on and 54 of 54 two rounds on, exactly.
- **Meet once.** The whole population rebuilt (1,208 stages, equal round by round); 81 table groups, all same states (the study's 80
  counts groups whose grown arrangements all meet once). One size past, at 15 and 16 junctions (254 stages), 8 groups, all same
  states; `MEET-ONCE-20261119-001` continues to 40.
- **Read, not rebuilt.** The population counts (52,163 stages; 9,498, 4,626, 4,474 groups), so the referee confirms that the 152
  exist and are what the note says, not that they are all of them.
- **Record points.** (1) the headline qualifier "at up to 14 junctions"; (2) which file's next-stage tally is superseded; (3) one
  group has three state groups, of which `other_states.json` lists two, so its next-stage check covers those two.

## Final report as sent (2026-11-19 08:28 UTC)

**Outcome:** yes, the growth itself makes such pairs. Among census stages of up to 14 junctions grown in complete rounds, 152 groups of different arrangements have the same bond-distance table, up to renaming the distinctions, but other allowed states. No table symmetry relates them. Closed, referee pending.

- **What they share.** Every one of the 152 comes from a start in which two knots share two distinctions, and none pairs two stages of the same start. Where junctions meet at most once, 80 reached groups share a table, and all 80 keep the same states. So at these sizes, knots sharing two distinctions are what lets distances lose the states of what the law builds.
- **They stay together.** In 85 of the 88 groups whose next stage is in range, the next stages again have one table and still different states. All 54 groups checked two rounds on are the same. This is unlike yesterday's six static rivals, which the law never makes and which it separates at once.
- **Common versus rare.** 32,207 of 51,959 stage arrangements share a table with another one. Most such grown groups, 4,474, have the same states with other junctions; only 152 have different states.
- **Two notions, kept apart.** "Legal as a static arrangement" (yesterday's six) differs from "reached by growth" (these 152). Starts are counted separately, and the law used is complete rounds only. Codex's serial mixed law was not run.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: two reached arrangements with one table and other states | **Status:** Successful | 152 grown groups up to 14 junctions, no table symmetry between them, all from knots sharing two distinctions; they persist two rounds |
| Local direction: what reading of a base is complete | Continue | Where junctions meet once, reached collisions keep the states here; three-way readings are the next test |
| Broader exploration: what distances carry (A97) | Known alternatives | Codex's collisions come with a symmetry; static ones without a symmetry are unreachable; reached ones without a symmetry now exist |
| Long-term goal: G1 with A97 | Obstruction learned | Distances do not carry the allowed states of what the law builds once knots share two distinctions |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Are the table plus three-way readings complete on the 527? | 2/3 | 3/3 | rerun the search with three-way readings → stop at all unique or a pair | Selected · awaiting go-ahead |
| 2 | Meet-once reached collisions at 15 to 24 junctions (sub-goal B205) | 3/3 | 2/3 | meet-once census stages → stop at an other-states pair or none | Alternative · deferred |
| 3 | The same comparison under Codex's serial law | 2/3 | 2/3 | the referee's serial census | Alternative · deferred |
| 4 | Do the 152 ever separate? | 2/3 | 3/3 | follow them to round 8 | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (obstruction learned); new sub-goal B205. **Assumptions:** A97 gains this study, status unchanged. **Advisor:** Fable 5.2, before the freeze, on hashing, deduplication, keeping starts apart, and how to state "same states". It guessed the outcome about right.

Referee hand-off: the decision note is `research/GROWN-PAIR-20261119-001/grown_pair.md`. Check these most closely: that the 152 really are non-isomorphic with isomorphic tables and other states (`other_states.json`), and the next-stage comparison. The prior-work line is in the pre-registration.
