# Does the new distance reader read every growing census arrangement?

Epic `CENSUS-READ-20261118-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-READ-20261118-001#1`. Goals
G1 and G17; assumption A97. **Referee pending.**

**Record.**
- Pre-registration, frozen before any case ran (commit `252bae194`), with five amendments: [preregistration.md](preregistration.md).
  Amendments 1 to 4 came before any verdict was read; Amendment 5 came after a preliminary readout, so its results are post-hoc.
- Code and runs: [the experiment family](../../experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/)
  (`job_exact3.py` for pass 5, which every number below comes from unless named; `readout5.py`, `checks5.py`).
- Results: [summary_pass5.json](../../artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/summary_pass5.json),
  [checks5.json](../../artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/checks5.json),
  [hidden28.json](../../artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/hidden28.json),
  [names.json and names_n.json](../../artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/), and the
  earlier passes' [preliminary summary](../../artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/summary_exact_prelim.json).

## The answer

**In the owner's terms.**
- **No: the ring was the easy case.** Across all 26,441 arrangements of the cheapest-count census (100,024 stages to round 8:
  every stage of at most 40 junctions, and larger stages for one arrangement in ten), the reader that read the ring back reads only
  2,353 stages exactly from their distances. Three things stand in its way.
- **Most starts have knots that share two distinctions.** In 24,385 arrangements (92%) two of the starting knots share two or more
  distinctions. The reader assumes junctions meet in at most one distinction, as everything the growth adds does, and on those
  93,808 stages it almost always fails (3 exact; 8,471 another arrangement with the same allowed states; 85,232 misread). Often the
  table there holds a distance of 1: two three-place knots that share two distinctions force their other two distinctions equal.
- **Where junctions meet once, it reads a little over a third.** On the 6,216 stages where no two junctions share two distinctions:
  2,350 exact (38%), 40 with only the outside junction swapped and 488 as another arrangement with the same allowed states (both are
  choices the table cannot make; 8% together), and 3,338 misread (54%).
- **Sometimes the table itself cannot say.** On 1,480 of those stages some exchange of distinctions keeps every distance and moves a
  junction: the junction hides, as in Codex's width-28 example. The reader is exact on none of them; no reader that uses only the
  table and not the names could be. Where no such exchange exists (1,944 stages of at most ten junctions, all exchanges checked), it
  reads 1,330 exactly (68%) and 92 more as another arrangement with the same states; the other 522 (27%) are failures of this
  reader, not of the table.
- **How far it must look is set by how big the knots are.** On every one of the 2,353 stages it reads exactly, it needs the
  distances up to the largest junction less one, never less and never more. The largest junctions there hold 3 to 9 distinctions,
  so it looks 2 to 8 far. Codex's readers under the other law look a fixed distance (four or five) on families with bounded
  junctions; here the junctions are not bounded, and the distance grows with them.
- **The 47 stages the old reader misread** (`FRESH-COUNT-20261118-001`'s mixed counts, replayed: 183 exact, 17 with the loose set read
  as a junction, 47 misread, as recorded): the new reader reads 194 of the 247 exactly and 11 of the 47; every mixed stage whose table
  has no junction-moving exchange (128) is read exactly or as the same states.

| Stages | Count | Exact | Outside swapped | Same states | Misread |
| --- | ---: | ---: | ---: | ---: | ---: |
| Two knots share two or more distinctions | 93,808 | 3 | 102 | 8,471 | 85,232 |
| Junctions meet at most once | 6,216 | 2,350 | 40 | 488 | 3,338 |
| … of these, an exchange keeps the table and moves a junction | 1,480 | 0 | 8 | 30 | 1,442 |
| … of these, no exchange moves a junction (all checked, at most ten junctions) | 1,944 | 1,330 | 13 | 79 | 522 |
| … of these, rigid (3-connected) | 1,050 | 447 | 39 | 103 | 461 |
| Mixed-count stages (FRESH-COUNT) | 247 | 194 | 1 | 18 | 34 |

The name-free reader R3n is shown; R3 under the census's own names is close (2,008 exact; 1,033 stages, 1.0%, change under one
renaming). Least distance needed against the largest junction, at every exactly read stage:

| Largest junction | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Stages read exactly (R3n) | 23 | 286 | 1,471 | 348 | 180 | 40 | 5 |
| Least distance needed | 2 | 3 | 4 | 5 | 6 | 7 | 8 |

## Predictions and verdicts

Scored on pass 5 (the corrected instruments of Amendment 5, so post-hoc), except where a pass is named.

| # | Prediction | Verdict |
| --- | --- | --- |
| C0 | Gate: (a) FRESH-COUNT's reader misreads 47 of 247; (b) small tables equal brute force; (b′) sides of 6 and 8 agree on large stages; (c) the ring reproduced | (a), (b), (c) held; **(b′) failed** on 199 of 200 large stages, so every stage was read again on exact tables (Amendment 3) |
| C1 | At rigid stages R3 is exact or an outside swap | **failed** (672 of 1,050 are not) |
| C1b | Where no pair shares two, R3's output has the true allowed states | **failed** (3,914 misreads) |
| C2 | R3 misreads in most arrangements sharing two; R3m never misreads | first part held (22,644 of 24,385); **second failed** (pass 3: 9,101 of 9,695 stages misread) |
| C3 | At 3-connected stages no same-state output but the outside swap | **failed** (R3: 61; R3n: 175, of which 56 are the truth with the loose set added) |
| C4 | At rigid stages read exactly, least distance = largest − 1 | **held** (342 of 342; and 2,008 of 2,008 at every stage R3 reads exactly) |
| C5 | R3 has the true states on all 247 mixed stages | **failed** (28 misread) |
| C6 | The old reader misreads in at least a tenth of arrangements past round 3 | **held** (pass 3: 944 of 944) |
| N1, N2 | R3n exact on Codex's 27-distinction example under 22 namings, and on the ring under 11 | **held** |
| N3 | R3n's verdict never changes under renaming | **failed** (51 of 100,024 stages) |
| N4 | At rigid stages R3n exact or swap, and then least distance = largest − 1 | first part **failed** (564 not); second **held** (447 of 447) |
| N5 | R3's verdict changes under renaming at fewer than 1% of stages | **failed**, narrowly (1.03%) |
| C7 | (reported) R3 on side-limited against exact tables | 3,243 of 47,768 stages over 14 junctions change verdict; 204 of 52,066 at 14 or fewer (201 closed stages, Amendment 5's fault) |

## How it works, and what the failures are

- **Stages and tables.** Every arrangement is grown by the census's own rule; at each round to 8 the exact bond table is computed
  over every bond, whatever the size of either side (include/exclude growth of a connected side with a maximum-flow cut, the RING-READ
  referee's method written afresh, which finds exactly the referee's six missed entries at ring round 25). Side-limited tables,
  enough on the ring, are wrong on the census: its grown stages have many short cuts with two large sides.
- **Knots that share two.** Two junctions meeting in two distinctions add to a consequence that cancels both, so their pairs sit in
  short bonds across the two junctions, and the reader's rule "a new junction meets each known one at most once" refuses the true
  junction. Dropping the rule (R3m) misreads even more. Reading these starts needs another reader.
- **Exchanges that keep the table.** A table symmetry σ that moves a junction leaves two arrangements with one table. Because R3n
  decides nothing by name, its output is carried to itself by every such σ, so it leaves out every junction σ moves; on Codex's
  width-28 pair both readers return the eleven prefix junctions and leave the hidden six-place junction out, in both histories, and
  return no wrong junction ([hidden28.json](../../artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/hidden28.json)).
  The smallest case in the census is three three-place knots in a triangle, whose table cannot tell its junctions from the triangles
  between them (the table's symmetries are the octahedron's 48, against the arrangement's 24).
- **Same states.** Where the junction graph with its outside end is not 3-connected, junctions can be exchanged (Whitney twists)
  without changing the allowed states, so an output with the true allowed states but other junctions is classed apart from a misread.
- **Names.** R3n's tie rule uses no names, but its verdict still changed under renaming at 51 stages: in the replays the candidate
  sets themselves differ between namings, which points to the step it shares with R3, whose running-size cut depends on the order in
  which the read junctions are enumerated (not proved to be the only source).

## Known results, and what this adds

Known: Whitney's 2-isomorphism theorem (1933); Tutte's characterisation of vertex stars as the non-separating bonds of a 3-connected
graph (not used here); Codex's `VARIABLE-OUTPUT-READER-20261118-001A` to `-001L` under the other law (all-size readers for families
with bounded junctions at fixed distances four or five; tables that hide a junction behind their own symmetries at widths 28 and 46,
`-001K`, `-001L`). What this adds: a census-wide map of where reading back from distances works under the cheapest counts. It mostly
fails, for three named reasons (starts whose knots share two distinctions; arrangements that are not rigid; tables whose symmetries
move junctions), and where it succeeds the distance needed is set by the largest junction.

## Limitations

- One reader (two versions). Its failures where the table has no junction-moving exchange (522 small stages) are this reader's; a
  better reader could do better there.
- The symmetry test is complete only at stages of at most ten junctions (twins, a sufficient test, at up to 40); larger stages are
  not classified.
- Stages of more than 40 junctions are read for one arrangement in ten (3,103 stages).
- Amendment 5's corrections came after a preliminary readout; its scoring is post-hoc. Passes 1 and 2 used side-limited tables and
  are kept only as a comparison.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It found that small stages are often not 3-connected,
so a correct reader can return another arrangement with the same allowed states; taken as the "same states" class, connectivity
tags and the restated C1, C1b and C3. It bet against C1, C3 and C4: right on C1 and C3, wrong on C4 (the horizon law held at
every exactly read stage).

## Preliminary, superseded (2026-11-19, committed `33192bd4a`)

The first 1,925 arrangements of pass 3 (exact tables, before Amendment 5's two fixes) gave 252 of 9,695 stages read exactly and the
horizon law on all 252; those numbers stand for that subset and instruments and are superseded by pass 5 above. Its two instrument
faults (closed stages; R3n dropping every dependent candidate) are fixed in pass 5.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the ring's reader across the census | **Status:** Partially successful | It reads 2,353 of 100,024 stages exactly (38% of the stages where junctions meet once); the horizon law holds on all of them; the failures are mapped to three causes |
| Local direction: reading a base back from its bond distances alone | Continue | Where the table has no junction-moving exchange, a better reader may close the 27% gap; knots sharing two need a reader of their own |
| Broader exploration: what bond distances carry (A97) | Known alternatives | Codex's law-aware readers prove all-size results on bounded families; tables whose symmetries hide a junction exist there and here |
| Long-term goal: G1 Space from a law (with G17) | Obstruction learned | Distances alone do not carry the typical small arrangement: its knots share two distinctions, or it is not rigid, or its table has symmetries the arrangement lacks |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does the table fix every arrangement it has no symmetry for? A complete search for presentations reproducing the table, on the 1,944 symmetry-checked stages | 3/3 — would make "distances carry everything but their own symmetries" a census fact (A97) | 2/3 — the candidate cliques, the exact table and the symmetry test exist; the search needs a bound | for the 522 stages the reader misses, search legal incidences built from all cliques for ones whose table matches → stop at a second presentation with no symmetry (a counterexample) or all 522 unique | Selected · awaiting go-ahead |
| 2 | A reader for knots that share two distinctions (92% of census starts) | 2/3 — the typical census start | 2/3 — the distance-1 and distance-2 pairs mark them | read the two-shared starts at round 0 with junctions allowed to meet twice → stop at a reader exact on the round-0 stages without symmetries, or a table ambiguity there | Alternative · deferred |
| 3 | Make the closure step order-free (the 51 stages R3n still reads by name) | 1/3 — tidiness of the instrument | 3/3 — the stages are listed | replace the running-size cut by a size bound proved for the census, rerun the 51 → stop when none change | Alternative · deferred |
| 4 | B203, a clock inside the growing ring | 2/3 | 3/3 | prove the tick from the model | Alternative · deferred |
| 5 | B204, a learner who must discover three-way readings | 2/3 | 2/3 | rate of pair-invisible facts at widths 27 to 32 | Alternative · deferred |

**Corrections:** one, logged: R3n is not wholly free of names (51 of 100,024 stages), which my preliminary note and messages called
"the name-free reader" (Not a block). The instruments' faults (side-limited tables; closed stages; dependent candidates) were found
and fixed inside this study before its result was reported. **Goals:** G1 checkpoint (obstruction learned), G17 checkpoint; no goal
changed. **Assumptions:** A97 gains this study, status unchanged (under challenge); none new. **Basket:** B196, B202,
`BOND-BALLS-20261111-001#2` in the line; B203 and B204 are #4 and #5.

## Final report as sent (2026-11-19 03:57 UTC)

**Outcome:** no. The ring was the easy case. Across all 26,441 census arrangements (100,024 stages, on exact tables), the reader that read the ring back reads 2,353 stages exactly. Closed, referee pending.

- **Why it mostly fails.** In 92% of the census starts, two knots share two distinctions. The reader assumes junctions meet at most once, and on those stages it almost never succeeds (3 exact of 93,808). On the 6,216 stages where junctions meet once, it reads 38% exactly. Another 8% come back as a different arrangement with the same allowed states, a choice no table can make, and 54% are misread.
- **Sometimes the table cannot say.** On 1,480 stages, exchanging two distinctions keeps every distance and moves a junction. Codex's hidden junction is this kind. The reader is right on none of them, and no reader working from the table alone could be. On Codex's width-28 pair it leaves the hidden junction out and returns only true junctions. Where no exchange moves a junction (1,944 small stages, all checked), it reads 68% exactly. The remaining 27% are failures of this reader, not of the table.
- **How far it must look is set by how big the knots are.** That held on all 2,353 stages it reads: it needs distances up to the largest junction less one, for largest junctions of 3 to 9, never less and never more.
- **The 47 old misreads.** These are FRESH-COUNT's mixed-count stages, now reproduced. The new reader gets 11 of the 47, and 194 of all 247 mixed stages.
- **Along the way.** Side-limited tables are wrong on the census: 3,243 large stages change verdict on the exact table. I also found and fixed two faults in my own tools, so the final numbers come from a corrected rerun scored after a preliminary look. That rerun is labelled post-hoc in the note.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the ring's reader across the census | **Status:** Partially successful | 2,353 stages read exactly; the horizon law held on all of them; the failures are mapped to three causes |
| Local direction: reading a base back from its distances | Continue | A better reader may close the gap where the table has no symmetry; knots sharing two need their own reader |
| Broader exploration: what distances carry (A97) | Known alternatives | Codex's law-aware readers work on bounded families; table symmetries hide junctions there and here |
| Long-term goal: G1 (with G17) | Obstruction learned | Distances alone do not carry the typical small arrangement |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does the table fix every arrangement it has no symmetry for? Complete search on the 522 symmetry-free stages the reader misses | 3/3 — distances carry everything but their own symmetries (A97) | 2/3 — the parts exist; the search needs a bound | search legal arrangements matching each table → stop at a second arrangement with no symmetry, or all 522 unique | Selected · awaiting go-ahead |
| 2 | A reader for knots that share two distinctions (92% of starts) | 2/3 | 2/3 | read the round-0 starts allowing junctions to meet twice | Alternative · deferred |
| 3 | Make the reader wholly free of names (51 stages still change) | 1/3 | 3/3 | an order-free closure step, rerun the 51 | Alternative · deferred |
| 4 | B203, the clock | 2/3 | 3/3 | prove the tick from the model | Alternative · deferred |
| 5 | B204, the learner's gap | 2/3 | 2/3 | rate of pair-invisible facts | Alternative · deferred |

**Corrections:** one, Not a block. I had called R3n "the name-free reader", but its verdict still changes under renaming at 51 of 100,024 stages. The cause is the step it shares with the old reader. **Goals:** G1 and G17 checkpoint (obstruction learned). **Assumptions:** A97 gains this study, still under challenge. **Advisor:** Fable 5.2, before the freeze. It flagged that small stages are often not rigid, which became the "same states" class. It bet correctly against my first C1 and C3, and wrongly against the horizon law.

Referee hand-off: the decision note is `research/CENSUS-READ-20261118-001/census_read.md`. Check these most closely: the exact table (`exact_table_v2.py`, including closed stages), the symmetry test, and whether Amendment 5's post-hoc fixes are honest. The prior-work line is in the pre-registration under "Prior work in the program".
