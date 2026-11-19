# Referee report MERGE-BURST-001-R1 (all 16 explosive starts regrown with own code, every round's class read; checked with REDUCE-BLOCKS-R1)

**Verdict: confirmed. No reading slip; both readings stand. No Block. One Narrowing of wording.**
- **The reading is right at all 16 starts.** The referee regrew all 16 explosive starts round by round with its own engine. It
  reaches exactly the study's stop round, stop kind and largest group at every one.
- **Both readings are right.** The 9-point and the 781-point single blocks are where the study puts them, with the predicted next
  round.
- **No readable stage was missed.** Every round of the 14 unread starts is outside the reduced class.
- **The Narrowing.** "At every stage two maximal blocks share two knots" is true of their last rounds, not of every round. In 9 of
  the 14 an early stage fails instead on a cycle of three blocks.

## The points asked

1. **The reduction (`mblib.reduced`): stated and applied correctly.**
   - **What the code does.** It keeps each distinct live-neighbour set once and drops those inside another, leaving the maximal
     blocks. It then tests the class in this order: two maximal blocks sharing two points, a cycle of three blocks (three points
     pairwise in a common block with no block holding all three), a stall, and fewer than two loose distinctions.
   - **The referee's own blocks and class test**, in the same order, were applied at every round. They agree with the study's
     verdict at every round it records (its last four per start and its read rounds).
   - **Its validity is REDUCE-BLOCKS' Lemma R and Corollary 1,** refereed alongside (REDUCE-BLOCKS-R1): confirmed.
2. **Start-04: confirmed.** The referee's engine reaches it in the study's rounds:
   - **round 7:** 1,015 junctions;
   - **round 8:** a largest group of 974 parents and 781 new junctions, all in one maximal block, with no two blocks;
   - **the next round:** the rule's own groups, computed on that stage, are 304,590 pairs = C(781, 2).
   - **From there,** the branch system (DOUBLE-IDENT, DEAD-CAP, refereed) gives the binomial burst C(781, k) for k = 2 to 781.
     That is 780 more rounds and 2⁷⁸¹ − 782 junctions, "about 2⁷⁸¹". The referee did not grow past round 8 either; this is
     computed, as the study says.
3. **The closed case: confirmed.** One block of 9 appears at round 14. The next groups are 36 pairs, and EXPLOSIVE-R1 had already
   grown the burst 36, 84, 126, 126, 84, 36, 9, 1 to its close.
4. **The 14 unread starts fail on the class, not on a reading slip: confirmed.**
   - **Same growth.** Each child had 5.5 GB and 600 s, against the study's 6 GB and 15 minutes. Every one stops at the study's round
     with the study's largest group and stop kind:
     - start-01 at round 8, group 446 (time);
     - starts 02, 05 and 08 at round 8, group 22 (memory);
     - the rest at rounds 5 to 7, groups 12 to 42.
   - **No readable stage.** At no round of any of the 14 is the stage in the reduced class. The referee checked every round to 1,000
     junctions with its full class test, and the later rounds by block overlap.
   - **Why each stage fails:**
     - every last round has two maximal blocks sharing two or more points, and later rounds share up to 405 (start-01, round 8);
     - **but in 9 of the 14** (starts 02, 03, 05, 08, 09, 10, 11, 14 and 15) one to three early rounds have no two blocks sharing
       two points. Those stages fail instead because of a cycle of three blocks.

## Points for the owner (listed, not folded in)

1. **"At every stage the reduced map still has two maximal blocks sharing two knots"** (the answer and the final report). It should
   say "at every stage it is outside the class: two maximal blocks share two knots at every later stage, and at some early stages a
   cycle of three blocks". The study recorded only each start's last four rounds, which all share two. The wall the study locates
   is unchanged. **Narrowing of wording; Not a block.**

## How the work was split

- **The referee:**
  - read `merge_burst.md`, the pre-registration, `mblib.py`, `job.py` and `results.json`;
  - wrote `job_mb.py`, on its EXPLOSIVE-R1 engine (maximal-clique groups, structural implied test), with its own blocks, class
    test and next-round groups.
- **Read as data:** the starts, from `runs/explosive`.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap: `runs/referee-mb` (following the growth) and
  `runs/referee-mb-class2` (the class at every round). Each start ran in a child with an address-space and time limit.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
