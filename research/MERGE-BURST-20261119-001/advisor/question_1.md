# Question for the advisor (MERGE-BURST-20261119-001, before the freeze)

You have no tools. Answer only from this text, say where you are unsure, and keep it short.

**Setting.** As in the explosive-kind study. The cheapest growth continued from its stage after s rounds is the growth of that stage
taken as a start (refereed). Its knots are the junctions, with their distinctions as places; two junctions sharing a distinction
touch; the live junctions are those holding a loose distinction. In the proved class the growth is the clusters of the cover of the
relayed map X⁺, counted exactly by DEAD-CAP's branch system, whose proof uses no bound on places.

**The closed case (pilot, disclosed).** The smallest explosive start has six knots. In round 14 one group of 309 parents swallows
nearly everything and leaves 9 live junctions, each with 8 loose distinctions and demand 8. They share 196 to 286 common neighbours
pairwise, so (S4) fails massively. But almost all those neighbours' blocks are the same set: all 9.

Reducing the stage's map to its maximal blocks (dropping any block equal to or inside another) leaves one block of 9. That reduced
stage is in the class: no stall, no two maximal blocks sharing two points, no cycle of three maximal blocks. It reads as one finite
piece with no rays, alone, so it closes. The branch system gives 36, 84, 126, 126, 84, 36, 9, 1, 0, and the engine grows exactly
that.

**The hypothesis to freeze.** Blocks equal to or inside another block change nothing. They add no candidate pair, and no common
neighbour that the larger block does not supply. From round 1 on, the growth reads old knots only through round-1 candidates and
valid sets. So the growth from a stage equals the branch system's count on the reduced stage, whenever the reduced stage is in the
class.

**Plan.**
- Follow EXPLOSIVE's 15 stopped explosive starts (6 to 9 knots, a seven-place knot each, overlapping groups of three), plus the
  closed one as a control. Each runs in a child of 6 GB and 15 minutes, to round 60.
- After each round, reduce the stage. At the first reduced stage in the class, read the future (closes, polynomial dimension D, or
  exponential), count its next 40 rounds by the branch system, and grow 8 more rounds to check them.
- Also count "merge events", rounds whose largest group is at least ten times the previous round's.
- Predictions:
  - R1: on every start with a reading, the prediction equals the grown rounds.
  - R2 (risky): every start that reaches a reading closes after its burst.
  - R3: at least 8 of the 15 reach a reading within the limits.

**Questions.**
1. Is the reduction sound? In particular:
   - can a block inside another still matter, for instance through a point the larger block lacks? (It cannot be inside then.)
   - does dropping equal blocks change the cover, the count or the relays?
   - is there a short proof I can write?
2. Before the run, predict how many of the 15 close, how many keep growing, and whether "repeats" (two merges before a reading)
   should be common.
3. What should I change in R1–R3 before freezing?
