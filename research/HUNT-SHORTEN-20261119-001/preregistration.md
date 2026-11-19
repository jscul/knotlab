# Can a new junction shorten a bond in a way the distances do not foresee? Pre-registration

Epic `HUNT-SHORTEN-20261119-001` (`EXTEND-ROUND-20261119-001#1`, the coordinator's go-ahead; A97, A108, G1), 2026-11-19.
Frozen before the runs. The canonical K1–K3 test is unchanged.

## The question

Claim B (EXTEND-ROUND): a table isometry that keeps what the round reads (R: the live junctions, their loose counts, the sets of
them met by one junction) extends to an isometry of the next round's tables. It held on 2,198 of 2,198 extensions, but is not
proved. The advisor's mechanism for a failure is a new junction with one fresh distinction sitting inside a bond and shortening it.
Construct that configuration directly, and test Claim B where the hypothesis can hold.

## Prior work in the program

`python3 -B scripts/track.py objects "attach a junction shorten a bond table isometry extension self-pairs" --until 2026-11-19 --exclude HUNT-SHORTEN-20261119-001`

- `EXTEND-ROUND-20261119-001`: Claim B and its 2,198 extensions (the direct predecessor).
- `PARENT-RULE-20261119-001`: the 1,034 static pairs, and the census stages with table symmetries the states lack (181 of 1,099).
- `CREATED-PAIR-20261119-001`: the growing end.
- `RING-READ-20261118-001`: reading growth back from bond distances alone (a relative: what the distances fix of what grows).

## Method

- **Part 1, the mechanism (`attach.py`).** Take every static meet-once other-states pair of at most 7 junctions (1,034, all such
  collisions within PARENT-RULE's bounds) and every full-table isometry φ. Attach one new junction to both sides. It takes one
  loose distinction from each of a set S of 1 to 3 live junctions that φ matches (star onto star, loose onto loose), plus f ∈ {1,
  2} fresh ones, with |S| + f ≥ 3. Then check:
  - whether the extension matches the new tables entry by entry;
  - whether the two new tables are isometric at all;
  - the advisor's path formula on failures.
- **Part 2, the law after one attachment.** Where the extension matches, check whether it keeps R. If it does, run the law's round
  on both and check the extension. A failure is a Claim B counterexample.
- **Part 3, the advisor's self-pairs (`selfpairs_job.py`, shared runner).** These are the real test of Claim B beyond 7 junctions.
  Take every census stage of round 1 or later with at most 14 junctions that is open. For each:
  - enumerate its table's isometries onto itself, on holder twin classes (cap 2,000);
  - keep those that do not carry the equations (Claim B\* covers the rest) but do keep R;
  - check the extension, up to 20 per stage, entry by entry against the census's own next stage.
  A failure is a Claim B counterexample. Isometries that break holder classes are not enumerated.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| H1 | No offshoot attachment (one parent, two fresh) ever fails (the advisor: a theorem, 95%) | one fails |
| H2 | A pair-junction attachment fails somewhere (seen in the smoke test; not fresh) | none fails |
| H3 | No Claim B counterexample in Part 2 (the advisor 90%, mostly by vacuity) | one |
| H4 | No Claim B counterexample in Part 3 (mine 70%; the advisor's 65% for self-pairs and grown pairs) | one |

Reported: how many cases each part tests, the strata, and the path-formula diagnostic.

**How to word the results (the advisor's):**
- a Part 1 failure shows that a table isometry alone does not survive attaching one pair-junction, and leaves Claim B untested;
- Claim B is tested only in Parts 2 and 3;
- "none up to N" holds for Claim B only within the stated classes: the static pairs (vacuous at 7 junctions), one attachment
  further, and the census's self-pairs to 14 junctions.

## Design-stage observations (disclosed)

- **Part 1, on 4 pairs:** every pair-junction attachment failed in one pair, with non-isometric new tables; offshoot attachments
  never failed.
- **Part 3, on 120 starts:** 74 extensions of R-keeping non-state self-isometries, all matching.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)). It sketched H1 as a
theorem, and it supplied:
- the wording above;
- the path-formula diagnostic;
- self-pairs and grown pairs as the real tests of Claim B (self-pairs taken; grown pairs deferred).

## Runs and stop rule

`attach.py` once (minutes, under a 16 GB cap); `selfpairs_job.py` once (265 shards, 8 workers, 16 GB cap). Then stop.
