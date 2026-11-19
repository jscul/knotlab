# Referee report THREE-WAY-001-R1 (own readings, forcing and searches)

**Verdict: confirmed, with one count corrected. No Block.**
- **The three-way readings are right.** The referee computed them from its own bonds (the glossary's word, the circuits of the
  equation space), not from `triples.py`. On all 11 static rivals:
  - the pair readings agree with the truth's on every pair;
  - the three-way readings differ in exactly the study's counts, case by case: 116, 192, 144, 192, 192 and 208 triples;
  - an exact search finds no renaming of the distinctions that keeps both readings, though the identity keeps the pairs.
- **All 152 reached groups come apart.** The referee rebuilt each group's full membership (151 groups have two state groups, one has
  three). For every one of the 154 pairs of state groups, a renaming keeps the pair table, and none keeps the pair table and the
  three-way readings together. This is an exact search, independent of the study's VF2 test.
- **The 23 are decided.** On all 23, the referee's own forcing with pairs alone leaves the equations open. With triples added it
  reaches them, and every forced word is a bond of the truth. Two stages have a same-states rival within the bound, so the split is
  21 unique and 2 with a same-states rival.
- **21 or 23: both are right, for different questions.**
  - **UNIQUE-TABLE's 21** are the stages whose class was undecided. Its classification puts a found rival above a decision.
  - **This study's 23** are the stages whose equations were still open.
  - **The two extra stages** are pop-0192 and pop-0212. UNIQUE-TABLE counted them among its 72 same-states stages, because a
    same-states rival had been found, although their equations were open.
- **The count to correct: 74 should be 77.** "74 of the 527 (72 + 2)" counts pop-0192 and pop-0212 twice, since they are already
  among the 72. It also leaves out five of the six other-states stages (pop-0236, -0308, -0338, -0442, -0501): each of them also
  has a same-states rival within the bound (the referee's search, and the study's own records). UNIQUE-TABLE's classification put
  them under "other states" first. So the stages that stay alike with triples, as same-states arrangements, number **72 + 5 = 77**.
- **One size past, the separation still holds.** The referee rebuilt every grown stage of 15 and 16 junctions (3,873). They form 564
  table groups: 542 keep the same states, and 22 have other states. None of the 22 meets once, and three-way readings separate all
  22.
- **The wording is guarded as asked.** "Complete up to the allowed states" is stated as "found so far" in the answer, "on
  everything found" in the position table, and "not shown in general" in the Limitations. Three smaller wording points follow.

## 1. Readings (`referee_three.py`)

- **Bonds.** A bond is a cut of the junction graph with both sides connected (closed-aware: with nothing loose there is no outside
  vertex). This is UNIQUE-TABLE-R1's enumeration, and bonds are exactly the circuits of the equation space.
- **The readings.** The pair reading is the least bond holding both distinctions, and the three-way reading the least bond holding
  all three, or none.
- **Checked against the shore table.** On every one of the 152 groups, the bond-based pair table equals CENSUS-READ-R1's shore
  table entry by entry.
- **The exact search** (`iso_both`) assigns distinctions one at a time:
  - each candidate image must have the same sorted row of pair readings and the same sorted multiset of three-way readings;
  - every pair and every triple among the distinctions assigned so far is checked;
  - the search has a cap, and no run reached it.

## 2. The 11 static rivals (`job_three.py` under `scripts/longrun.py`, cases six-*; `referee_three.json`)

| Check | Result |
| --- | --- |
| Truth regrown from its start and round, isomorphic to the recorded truth | 11 of 11 |
| Pairs differing on the recorded names | 0 in every case |
| Triples differing on the recorded names | 116, 192, 192, 144, 144, 192, 192, 192, 192, 208, 208: **equal to `triples.json`, case by case** |
| Triples that no bond holds (the truth) | 86 to 257 |
| A renaming keeps the pair table (control) | 11 of 11 (the identity) |
| A renaming keeps the pair table and the three-way readings | **0 of 11** |

## 3. The 23 undecided stages (cases und-*)

| Check | Stages |
| --- | ---: |
| The referee's forcing with pairs only spans the equations | 0 of 23 |
| With pairs and triples it spans them | **23 of 23** |
| Every forced word is a bond of the truth (a soundness check) | 23 of 23 |
| A same-states rival within the bound (UNIQUE-TABLE-R1's search) | 2 (pop-0192, pop-0212) |

- **The forcing argument, checked.** In every code with the same readings, each pair or triple read s lies in a circuit of s
  distinctions, all of whose pairs and triples read at most s. A candidate is dropped in two cases:
  - it is strictly comparable with a forced word;
  - some nonzero word of its span with the forced words is lighter than the least circuit through every one of its distinctions.
    This is sound because every nonzero word of a binary code is a disjoint union of circuits.
  A key left with one candidate forces it. The argument is sound.
- **What "unique" rests on.** Forcing shows that every matching code contains the truth's equations. Equality then needs UNIQUE-TABLE's
  bound, at most as many junctions and so no larger rank, as "21 unique" inherits.
- **The referee's dropping rule is the weaker one** (lighter than the least circuit through each of its distinctions). The stronger
  form (through any one of them) is also sound.

**An extra run, stopped part way** (`job_all527.py`). The referee's forcing was run on the 527 stages and stopped after about half
an hour, with 475 done, rather than registered as a long run (the remaining 52 have slow candidate sets).
- **With triples:** it spans the equations on 473 of the 475.
- **Pairs alone:** 342, against the study's own pair forcing on 345 of the same stages.
- **The two exceptions,** pop-0009 and pop-0010, are not fixed by either forcing. UNIQUE-TABLE decided them by its exhaustive
  one-missing search. This is a limit of the method there, not a rival.

## 4. 21 against 23, and 74 against 77 (the coordinator's question; the study's records read as data)

`final_readout.py` classes a stage in this order: other states (a legal rival with other equations), then same states (a
same-states rival within the bound), then unique (decided), then undecided. `triples.py` takes as undecided every stage that is not
decided, whatever rivals it has.

| Stages | UNIQUE-TABLE's class | Equations decided before triples? | Same-states rival within the bound |
| --- | --- | --- | --- |
| 21 | undecided | no | none |
| pop-0192, pop-0212 | **same states (among the 72)** | no | 1 each |
| pop-0236, -0308, -0338, -0442, -0501 | other states | yes (one-missing search) | **1 each** (the referee's search; the records' `same_code_rivals` also 1) |
| pop-0007 | other states | yes | none |

- **The 21 and the 23.** The 21 are the stages whose class was undecided; the 23 are those whose equations were open. Both are
  right, and the note should say which it means.
- **The 74.** "That leaves 74 of the 527 (72 + 2)" adds the two stages to the 72 they are already in. The stages left alike after
  triples, as same-states arrangements, are the 72 plus the five other-states stages that also have a same-states rival: **77**.
  The table row "Same-states rivals … | 74" and "74 stages" in the three-gaps list change likewise.

## 5. The 152 reached groups (cases grown-*)

- **The groups.** Each group's members are every grown stage carrying its study table hash: 460 in all, regrown by the referee,
  joined by exact table isometry and placed by exact states (as in GROWN-PAIR-R1). One arrangement per state group was kept.
- **The test.** For every two state groups, the exact search asked whether a renaming keeps both readings.

| | Count |
| --- | ---: |
| Groups (two state groups / three) | 152 (151 / 1) |
| Pairs of state groups | 154 |
| … a renaming keeps the pair table | 154 |
| … a renaming keeps the pair table and the three-way readings | **0** |

This includes the third state group of the one group with three, which `other_states.json` does not list.

## 6. One size past (`job_meetonce.py --param all=1`, `job_meetonce_groups.py` from GROWN-PAIR-R1; `job_past.py`)

The population and the grouping:
- **The stages.** Every census start was regrown in complete rounds to round 8, keeping each stage of 15 or 16 junctions: 2,415 and
  1,458 stages.
- **The grouping.** Stages were deduplicated by exact isomorphism, grouped by exact table isometry, then by exact states.
- **The triple test,** for every group with other states.

| | Count |
| --- | ---: |
| Table groups of two or more non-isomorphic arrangements | 564 |
| … same states / other states | 542 / **22** |
| … other-states groups with an arrangement meeting once | 0 |
| … other-states pairs that a renaming keeps on pairs | 22 |
| … … and on pairs and triples | **0** |

So one size past both GROWN-PAIR's statements hold:
- reached collisions with other states recur (22), and none meets once;
- three-way readings separate all of them.

Groups whose members straddle 14 and 15 junctions were not formed.

## 7. The wording

The coordinator's question: is completeness stated only as found, not proved? **Yes**, in the answer ("every collision … found so
far"), the position table ("on everything found"), the Limitations ("that three-way readings suffice in general is not shown") and
the final report ("not proved in general").

## Corrections and wording points for the owner (listed, not folded in)

1. **74 should be 77** (Sections 4 and 2). "74 of the 527 (72 + 2)" counts pop-0192 and pop-0212 twice, and leaves out the five
   other-states stages that also have a same-states rival. The stages that stay alike with triples, as same-states arrangements,
   are 72 + 5 = 77. This changes the answer's bullet, the table row and the three-gaps list. **Not a block:** the qualitative claim,
   that same-states rivals are out of reach of any reading of the states, is unchanged.
2. **"21" and "23" name different things** and should be named: 21 stages of undecided class (UNIQUE-TABLE), 23 stages with open
   equations (here). The two extra stages are pop-0192 and pop-0212. **Not a block.**
3. **"The smallest consequence that holds all three"** (the owner's-terms bullet and the final report) should be "the smallest
   bond containing all three, less one, or none". The reading is a bond, a circuit, which is the glossary's word. A smallest
   consequence holding three need not be a bond, and on the six stages 86 to 257 of the truth's triples lie in no bond at all, so
   "none" is a reading that does work. **Not a block.**
4. **"21 unique"** holds within UNIQUE-TABLE's bound (at most as many junctions). The note does not restate the bound. **Not a block.**

## How the work was split

- **The referee:**
  - read `three_way.md`, the pre-registration, `triples.py`, and UNIQUE-TABLE's `final_readout.py`;
  - wrote `referee_three.py` (readings, the exact search, forcing), `job_three.py`, `job_past.py`, `job_all527.py` and
    `three_readout.py`, on its UNIQUE-TABLE-R1 (bonds, same-states search), CENSUS-READ-R1, FRESH-COUNT-R1 / FIRST-KNOT-R1 and
    GROWN-PAIR-R1 code.
- **Read as data:** `verify_rivals.json`, `triples.json` (starts and rounds of the 23, and the study's counts), `other_states.json`,
  GROWN-PAIR's stage results and the census keys, and UNIQUE-TABLE's run records (classification fields).
- **No study code was run.**
- **Where it ran.** Every computation ran under `scripts/longrun.py` within the 16 GB cap, with a 2 GB limit per case (peak 273 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
