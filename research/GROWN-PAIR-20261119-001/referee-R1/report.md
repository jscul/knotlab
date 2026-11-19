# Referee report GROWN-PAIR-001-R1 (own growth, tables and searches)

**Verdict: confirmed. No Block, no Narrowing; three wording and record points.**
- **The 152 are real.** In every one of the 152 groups the referee regrew both listed arrangements from their recorded starts with
  its own engine. In every group:
  - the two arrangements are not isomorphic;
  - their exact tables are isometric (the referee's own shore enumeration and isometry search);
  - their allowed states differ, by an exact search over every table isometry (no undecided case).
- **The statements around them hold.**
  - Every start has two knots sharing two distinctions.
  - The full membership was rebuilt: 460 grown stages, of which none is a hash collision. One group has three state groups, as the
    study's count says, and no start reaches two state groups of one group. So "none pairs two stages of the same start" holds
    over every member, not only the listed ones.
  - Since the arrangements are not isomorphic, no symmetry of the table carries one onto the other.
- **The next-stage comparison reproduces exactly.**
  - One round on: 85 groups again have one table with states still differing, 3 have tables that differ, and 64 are out of range.
  - Two rounds on: 54 of 54 in range, again one table with differing states.
  - On no group does the referee's verdict on the next table differ from the study's.
- **"Where junctions meet at most once, the states are kept" holds at these sizes, and one size past.**
  - The referee rebuilt the whole meet-once population: 1,208 grown stages of up to 14 junctions, equal round by round to the
    study's.
  - 81 table groups have two or more meet-once arrangements, and all 81 keep the same states. The study's 80 counts only groups
    whose grown arrangements all meet once; the 81st also holds one grown stage in which two junctions share two, and all three
    have the same states.
  - At 15 and 16 junctions (254 meet-once grown stages), 8 table groups appear, and all 8 keep the same states.
- **Lighter than a full rebuild in one place.** The population counts (52,163 stages, 9,498 table groups, 4,626 with two or more
  grown arrangements, 4,474 of them with the same states) were read as data, not rebuilt. So the referee confirms that the 152
  exist and are what the note says, but not that they are all of them.

## 1. The 152 groups (`job_grown.py` under `scripts/longrun.py`, `grown_readout.py`, `referee_grown.json`)

What was done for each group of `other_states.json`, with no study code imported or run:
- **Provenance.** Each listed arrangement's start (census index to key, from `runs/census-exact5`) was regrown to the recorded
  round with the referee's engine (complete rounds, the fewest counts; FRESH-COUNT-R1 and FIRST-KNOT-R1). The stage was then
  compared with the recorded arrangement by exact isomorphism.
- **Tables.** Exact tables came from the referee's closed-aware shore enumeration (CENSUS-READ-R1). Isometry was decided by its
  exact search over twin quotients (VARIABLE-OUTPUT-READER-001F-R1).
- **States.** The test asks whether some bijection of distinctions carries one equation space onto the other. Every such
  bijection preserves the table, so the search runs over table isometries only:
  - distinctions held by the same junctions are taken in increasing order;
  - a branch is cut as soon as a star's image leaves the other span.
  The search is exact, and it never reached its cap.

| Check | Groups |
| --- | ---: |
| Regrown stage is the recorded arrangement (both listed arrangements) | **152 of 152** |
| The start has two knots sharing two distinctions | **152 of 152** |
| The two listed arrangements come from different starts | **152 of 152** |
| Arrangements not isomorphic | **152 of 152** |
| Tables isometric | **152 of 152** |
| Allowed states differ (exact) | **152 of 152** (none undecided) |

## 2. Full membership and lineage (`job_members.py`, `members_readout.py`, `referee_grown_members.json`)

`other_states.json` lists one arrangement per state group, and only two, and its lineage test compares those listed only. The
referee rebuilt the full membership as follows:
- **Which stages.** Every grown stage carrying a group's study table hash was taken (index and round read from the study's results
  as data).
- **Joining a group.** Each such stage was regrown, and joined the group if its exact table is isometric to the listed
  arrangements'.
- **Placing it.** It was then placed in a state group by exact search, opening a new state group when it matched none.

| Result | Count |
| --- | ---: |
| Grown stages carrying the 152 groups' table hashes | 460 |
| … with a table not isometric (a hash collision) | 0 |
| Table groups with two state groups / three | 151 / **1** (the study's `state_groups` says the same; only two are listed) |
| Groups in which one start reaches two state groups | **0** |
| Undecided searches | 0 |

## 3. The next stages (the same run)

The next stages are the census's own continuation: round + 1 and round + 2 from the same starts, regrown by the referee, at most 14
junctions.

| | Out of range | One table, states differ (every pair) | Tables differ | One table, same states |
| --- | ---: | ---: | ---: | ---: |
| Round + 1 | 64 | **85** | **3** | 0 |
| Round + 2 | 98 | **54** | 0 | 0 |

The note's "64 and 31 groups fell outside" reads 31 as the share of the 85 that leave range at the second round (85 − 54). The
referee's next-table verdict agrees with the study's (`next_tables_isomorphic`) on every group.

## 4. Where junctions meet at most once (`job_meetonce.py`, `job_meetonce_groups.py`, `job_companion.py`, `meetonce_readout.py`, `referee_grown_meetonce.json`)

The study's files list only 200 table groups (`pairs2.json` writes `groups[:200]`), and among them only 4 of the 80 meet-once groups.
So the referee rebuilt the population:
- **The stages.** Every census start was regrown to round 8, keeping each stage of up to 14 junctions in which no two junctions
  share two distinctions.
- **The groups.** Stages were deduplicated by exact isomorphism and grouped by exact table isometry, then by exact states.

| | Count |
| --- | ---: |
| Meet-once grown stages (rounds 1 to 5 occur) | **1,208**: 817, 250, 98, 37, 6 by round, equal to the study's results round by round |
| Table groups of two or more meet-once arrangements | 81 (79 of two, 2 of three) |
| … same states up to renaming / other states | **81 / 0** |
| … whose table a grown two-shared stage also carries | 1 (census 1395, round 1, eight junctions): same states as both |
| **One size past:** meet-once grown stages of 15 and 16 junctions | 151 and 103 |
| … table groups of two or more; same states / other states | 8; **8 / 0** |

- **80 against 81.** The study counts a group only when all its grown arrangements meet once (`all(grown_meet_once)`). The 81st group
  also holds a grown arrangement in which two junctions share two. All three share the states, so it is one of the 4,474, not one
  of the 152. Under the study's definition the count is 80, and it is right.
- **The note's qualifier.** The note says "at these sizes" and, in its Limitations, that larger sizes were not tested. Only the
  headline bullet's first sentence, "Where junctions meet at most once, no such pair appears", lacks it (point 1 below). The
  referee's check at 15 and 16 junctions agrees with the statement there too, as an observation.

## 5. What it means for A97

The sharper test that UNIQUE-TABLE's referee set is answered for complete rounds:
- **What is answered.** Two reached arrangements, with no table symmetry between them, share every pairwise bond distance and differ
  in their allowed states.
- **Where it applies.** Every such pair comes from a start whose knots share two distinctions, and holds two junctions sharing two.
  Where junctions meet once, the reached collisions keep the states, to 16 junctions.
- **What is not answered.** The note does not say whether "distance" in A97 must be pairwise. The three-way follow-up asks exactly
  that, and the status of A97 is the owner's to set.
- **For the serial law.** The repeat under Codex's serial mixed law should begin with whether that law reaches stages in which two
  junctions share two distinctions at all. Every one of the 152 is such a stage.

## Wording and record points for the owner (listed, not folded in)

1. **The headline bullet** "Where junctions meet at most once, no such pair appears" should carry its qualifier in the first
   sentence: "at up to 14 junctions (and, by the referee's check, 15 and 16)". The rest of the note already says so. **Not a block.**
2. **`pairs2.json`'s next-stage tally** (`other_state_grown_groups_next_stage`: 79 equal, 3 differ, 70 missing) is the earlier
   hash-based pass, which takes one provenance per arrangement. The note uses `other_states.json`'s exact 85 / 3 / 64, which the
   referee reproduces. A line saying which file is superseded would prevent a misreading. **Not a block.**
3. **One group has three state groups**, but `other_states.json` lists two arrangements per group. Its next-stage comparison
   therefore covers those two, and the third is found only by rebuilding the membership (Section 2). "152 groups" is right; "151
   with two state groups and one with three" would be exact. **Not a block.**

## How the work was split

- **The referee:**
  - read `grown_pair.md`, the pre-registration, `pairs2.py` and `other_states.py`;
  - wrote `job_grown.py`, `grown_readout.py`, `job_members.py`, `members_readout.py`, `job_meetonce.py`,
    `job_meetonce_groups.py`, `job_companion.py` and `meetonce_readout.py`, on its FRESH-COUNT-R1, FIRST-KNOT-R1, CENSUS-READ-R1
    and VARIABLE-OUTPUT-READER-001F-R1 code.
- **Read as data:** the census keys (`runs/census-exact5`); the study's groups and representatives (`other_states.json`); the
  stage index, round, table hash and `max_shared` from the study's results (`results_grown-pair.jsonl.gz`), used only to choose
  which stages to regrow and to compare counts.
- **No study code was run.**
- **Where it ran.** Every computation ran under `scripts/longrun.py` within the 16 GB cap, with a 2 GB limit per case (peak 264 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
