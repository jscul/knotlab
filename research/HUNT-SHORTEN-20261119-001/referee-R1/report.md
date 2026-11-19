# Referee report HUNT-SHORTEN-001-R1 (the self-pairs test re-run with own code: every stage, every symmetry, no cap of 20)

**Verdict: confirmed. No Claim B counterexample, now on every symmetry of every stage in the bound. No Block. One wording point
on the stated bound, Not a block.**
- **The self-pairs test holds, and far beyond what was tested.** The referee regrew every census start with its own engine and
  computed full tables with its own shore enumeration. It then enumerated every isometry of each stage's table onto itself, by
  its own search, with no cap of 20 and no cap of 2,000.
  - **One per class of the same holder.** The search takes one representative per coset of the permutations inside holder classes:
    images increase inside each class.
    - Such a permutation keeps the equations and the reading.
    - It leaves the extension's verdict unchanged. Loose distinctions are re-paired by the extension, and shared ones stay twins
      in the next stage.
  - **So symmetries that break holder classes are included,** which the study left out.
  - **The result.** On the 23,003 open stages of round 1 or later with at most 14 junctions:

    | | Count |
    | --- | ---: |
    | Isometries, up to holder classes | 3,155,442 |
    | … that carry the equations (Claim B\* covers them) | 526,507 |
    | … that keep the reading without carrying the equations | **1,746,752** |
    | … of which break holder classes | 1,630,590 |
    | … extended through the next round, an isometry of the next table entry by entry | **1,746,752** |

    **There is no failure.** The study tested 33,918 of these, about 2%.
- **The study's counts reproduce where it looked.** 23,003 open stages, of which 21,899 have two junctions sharing two and 1,104
  meet once, equal its figures.
  - **Stages with a holder-preserving symmetry** that keeps the reading but not the equations: 3,816. That is the study's 3,810
    tested stages plus its 6 that ran late.
  - **Such symmetries:** 116,162, where the study found 108,289. The difference is its 34 stages cut at 2,000.
  - **The extension and the reading test** are EXTEND-ROUND-R1's, whose control rejects perturbed extensions.
- **No stage is left out by the census's eight rounds.** The study grows at most eight rounds, so it tests stages of rounds 1 to 7.
  The referee grew to round 14 and found no open stage of round 8 or later with at most 14 junctions. Each round adds a junction,
  so stages that late are already larger.
- **The one stage the referee's search capped** was finished separately, with streamed representatives and no cap. It is start
  [[4, 4, 4, 4, 4], [0, 0, 1, 2, 2, 0, 2, 2, 0, 0]] at round 2, with 11 junctions and 23 distinctions. All 362,496 of its
  reading-keeping symmetries extend, and all of them break holder classes.

## Point for the owner (listed, not folded in)

1. **"The bound, as asked" is stated more widely than the study covered.** It says "every open census stage of round 1 or later
   with at most 14 junctions, under every table symmetry taken on holder classes that keeps the reading (at most 20 tested per
   stage)". The study covered less than that:
   - **6 stages ran late,** so not every stage;
   - **34 stages had their holder-class symmetries cut at 2,000,** so not every symmetry;
   - **20 per stage** means 33,918 tested of the 108,289 found.

   The table names these ("6 stages late, 34 capped"). The bound should name them too. **Not a block.** The referee's run now
   covers the bound as stated, and more: every stage, every symmetry including those breaking holder classes, and every one
   tested. It holds.

## Not checked

- **Part 1's attachments** (41,268 cases, 14,792 failures) and Part 2 were read, not re-run. The hand-off asked for the self-pairs
  test.

## How the work was split

- **The referee:**
  - read `hunt_shorten.md`, the pre-registration, `selfpairs_job.py` and its output;
  - wrote `job_selfpairs.py`, `job_onestage.py` and `selfpairs_readout.py`. They use its own FIRST-KNOT-R1 engine with the
    program's rule, GROW-SMALL-R1's full tables, EXTEND-ROUND-R1's reading test and extension, and a new coset-representative
    isometry search.
- **Read as data:** the touch census's arrangements in `runs/touch-census`, and the study's `selfpairs.json` for the comparison.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 642 MB, about 9 minutes, plus 1 minute for the finished
  stage).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
