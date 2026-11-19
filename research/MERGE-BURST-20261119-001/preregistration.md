# Pre-registration: what explosive starts do after their merge

Epic `MERGE-BURST-20261119-001`, ticket `MERGE-BURST-20261119-001B`, 19 November 2026, by Claude, on the coordinator's go-ahead for
`EXPLOSIVE-20261119-001#1`. Goal G17. Framed by A110: blow-up is expected, and the question is what a sample of the explosive kind
typically does.

## The question

EXPLOSIVE found 16 explosive starts within seven places. One closes: a group of 309 parents, then a binomial burst of its 9
survivors. The other 15 were stopped at its per-start limits. For each of the 15, does it:
- end after one merge and a finite burst;
- repeat (merge, burst, merge again);
- or keep growing past its burst?

## The method: read the burst from the stage, don't build it

- **The stage identity** (BREAK-EDDIES, refereed). The growth continued from its stage after s rounds is the growth of that stage
  taken as a start.
- **The reduction (the study's hypothesis).** Drop every block of the stage's map that equals or lies inside another block.
  - A dropped block adds no candidate pair, and no common neighbour the larger block does not already supply.
  - The advisor's sketch: round-1 candidates and valid sets read only point sets, which a family and its maximal blocks share.
    Later rounds read old knots only through those. In the class, every dropped block sits inside exactly one maximal block.
- **The reading.** At the first stage whose reduced map is in the class (no two maximal blocks sharing two points, no cycle of
  three maximal blocks, no stall, two or more loose distinctions), the future is read by the rank rule. It is counted for 40 rounds
  by DEAD-CAP's branch system, whose proof uses no bound on places.
- **The check.** The child grows up to 8 more rounds and compares them with the count. It also reads the reduced stage one round
  later.
  - The pilot showed that the next stage can leave the class: the 36 pairs of the 9 survivors form cycles of three blocks.
  - So that read is recorded, and it counts only when the next stage is itself in the class.

## Pilot (disclosed)

On the closed case, the reduced stage after round 14 is one block of 9. Its reading is "closes". Its count is 36, 84, 126, 126, 84,
36, 9, 1, 0, equal to the grown rounds.

## Population and limits

- **The starts.** EXPLOSIVE's explosive starts within seven places, read from `runs/explosive`: the 15 stopped ones, and the closed
  one as a control.
- **The child.** Each start grows in its own forked child, limited to 6 GB and 15 minutes, to round 60, under scripts/longrun.py.
- **When the child stops.** An end by memory, by time, or at round 60 without a reading are three different findings, and are
  recorded apart.

## Predictions (frozen)

| # | Prediction | Falsified by |
| --- | --- | --- |
| R1 | On every start with a reading, the branch system's count equals every grown check round. The number checked at 3 or more rounds is reported, and readings with fewer are counted apart | one round that differs |
| R2a | Every first reading is a single maximal block | a reading with two or more |
| R2b | (risky) Every start that reaches a reading closes after its burst | a reading that is polynomial or exponential |
| R3 | At least 5 of the 15 reach a reading within the limits | fewer |
| R4 | Where the stage one round after the reading is itself in the reduced class, its reading agrees | a disagreement |

A **merge event** is a round whose largest group is at least 50 and at least ten times the previous round's. "After its burst" means
a reading reached after a merge event; a reading with no merge event before it is reported as such.

## What would follow, and what it is

- **Proved or exhausted?** Each start's reading is a computation, exact on the pre-registered hypothesis (the reduction) and the
  refereed theorems. The 15 are a sample: EXPLOSIVE's explosive starts under its weighting, not the kind as a whole. Nothing here
  generalises from the one closed case.
- **R2b holds on every start read.** In that sample the explosive kind is a merge followed by a finite burst.
- **R2b fails.** Some explosive starts keep growing past their burst, and the kind splits.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze.
- **It sketched** the reduction's proof and named its weak point: relays.
- **It guessed:** about 6 of 15 reach a reading, about 5 close, 0 to 1 keep growing, and 1 to 3 repeat.
- **Adopted from it:**
  - R1's minimum of 3 rounds, with unchecked readings counted apart;
  - R2 split into R2a and R2b;
  - R3 at 5;
  - the floor of 50 on merge events;
  - the stability check (R4, narrowed as above after the pilot).
- **Not adopted:** an engine-against-engine check of reduced against unreduced stages. A reduced map is not a presentation: dropping
  a dead knot frees its distinctions and changes its neighbours' open counts. So R1 tests the reduction only through the reading.
