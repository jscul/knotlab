# Referee report JUNCTION-MAP-001-R1 (own growth; the study's map run read-only as the object under test)

**Verdict: confirmed. No Block, no Narrowing.**
- **The stage gate (the owner's first point) holds.** Growth from a stage equals growth of that stage taken as a start. This was
  shown for BREAK-EDDIES (BREAK-EDDIES-001-R1, Section 3):
  - **The argument.** The referee's engine reads only the present presentation: stars, holders, adjacency, the live junctions
    (exactly the holders of a loose distinction) and the GF(2) span.
  - **The tests.** 369 of 369 pass (123 starts, s = 1, 2, 3, 8 rounds each).
  - **Here.** On this study's 94 starts, the referee's own growth from each stage agrees with the study's gate figures stage for
    stage (below).
- **maplib's lifted cut is a fair reading of the go-ahead (the second point).**
  - **What maplib changes.** The cluster rule's only scope cut, a round-1 group of three sharing two points with another block or
    group, becomes a pass.
  - **What the rule does then.** It keeps the group as its own hyper-block. It removes the group's covered pairs from the simplices'
    lines, and it merges simplices only when they share two points.
  - **So** the group and the block it overlaps share two points and no line. In the block graph they form a cycle of length two
    (group – a – block – b – group), and the unrolled map opens it like any other loop.
  - **The reading.** Junctions are the points (the stage taken as a start), and the excluded overlap is kept as a loop of length two,
    as the go-ahead asked. The cut also covers two groups of three sharing two points, which is lifted the same way.
- **J1 and J2 reproduce exactly against the referee's own growth.** The study's map (`maplib.lifted_analyse`, `maplib.lifted`) was
  run read-only on each stage taken as a start, grown by the referee's engine:
  - **all 261 stages holding the overlap** are right at round s + 1 and wrong at s + 2;
  - **all 14 clean stages** are exact for every round compared;
  - **the 7 with the rule's first break** differ at s + 2 too;
  - **status and first difference** equal the study's on 282 of 282 stages.
- **The mechanism, by hand (the third point):** the ring of five with a spare (catalogue entry C-0) at stage s = 2 (Section 2). The
  map counts 13 at round 4 where the growth makes 9. Each of the two loops of length two closes into a group of three in the
  growth, and the map counts its three sides as three pairs.

## 1. The run (`job_jmap.py` under `scripts/longrun.py`)

| Stage status (the rule's analyse on the referee's stage) | Stages | First round at which map and growth differ |
| --- | ---: | --- |
| overlap | 261 | **s + 2 in all 261** |
| clean | 14 | **none** (exact over every round compared, up to 8) |
| the rule's first break | 7 | s + 2 |
| Status and first difference equal to the study's | **282 of 282** | |

## 2. The mechanism on the ring of five with a spare (C-0, knots 5, 4, 4, 4, 4), stage s = 2

The stage taken as a start, from the referee's engine:
- **Size.** 18 junctions. The live ones are the round-2 junctions 11 to 17, with parents 11 ← (5, 6), 12 ← (5, 10), 13 ← (5, 9),
  14 ← (6, 10), 15 ← (6, 8), 16 ← (7, 8) and 17 ← (7, 9).
- **The candidate map.** Old junctions 5, 6, 7, 8, 9, 10 give the simplices {11, 12, 13}, {11, 14, 15}, {16, 17}, {15, 16},
  {13, 17} and {12, 14}.
- **The group of three.** {11, 12, 14} is one: its pairs meet at 5, 6 and 10, and no junction meets all three.
- **The overlap, twice.** The group shares 11 and 12 with block {11, 12, 13}, and 11 and 14 with block {11, 14, 15}. The pair
  (11, 12) is the group's, so the first block keeps only the lines 11–13 and 12–13, and likewise 11–15 and 14–15 for the second.
  That makes two loops of length two.

**Round 3 (s + 1): right.**
- **The growth** makes 8 junctions: one for the group {11, 12, 14}, called 18, and seven pairs: 19 = (11, 13), 20 = (11, 15),
  21 = (12, 13), 22 = (13, 17), 23 = (14, 15), 24 = (15, 16) and 25 = (16, 17).
- **The map** counts the same 8.

**Round 4 (s + 2): wrong.**
- **The growth** makes 9. 18, 19 and 21 meet pairwise at 11, 13 and 12, and no junction meets all three, so they form one group of
  three. So do 18, 20 and 23, at 11, 15 and 14. Seven pairs follow.
- **The map** predicts 13 (`maplib.lifted`, read-only: 8, 13, 25, 54 for rounds 3 to 6; the growth gives 8, 9, 10, 11).
- **Where the 4 come from.** Unrolled, each loop of length two becomes a line: the far end of the path 18 – 11 – 19 – 13 – 21 – 12
  is a new copy of 18, not 18 itself. So the map counts three pairs where the growth closes one group of three: 2 extra per loop,
  4 in all.
- **The note's sentence** ("on a second lap the growth reaches the same junction, where the unrolled map counts a new one") is
  this, read on one start.

## 3. Not rechecked

J3 (the knot-level map with the cut lifted, wrong by round 2 on 82 of 82) and the merged-simplex reading were not rerun.

## How the work was split

- **The referee:**
  - read `junction_map.md`, the pre-registration, `maplib.py`, `job.py` and CLUSTER-ALL's `clusters.analyse`;
  - wrote `job_jmap.py`, on its FIRST-KNOT-R1 and TOUCH-CENSUS-R1 code.
- **Run read-only as the object under test:** the study's map (`maplib.lifted_analyse`, `maplib.lifted`) and the rule's
  `analyse` for the status.
- **No growth code of the study was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 303 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
