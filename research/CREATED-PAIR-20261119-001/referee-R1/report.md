# Referee report CREATED-PAIR-001-R1 (own growth, full tables and isometry enumeration on all 87 pairs)

**Verdict: confirmed. No Block. One wording point, Not a block. One size past, the contrast holds on all 86 carried pairs.**
- **The isometry enumeration is complete, and every count reproduces.**
  - **The study's method.** `isos.py` runs VF2 on the complete graphs, with WL colours on the nodes. networkx's WL hashes are
    canonical, and they are kept by any isometry, so they only prune. No twin quotient is taken, and the cap of 200,000 is never
    reached.
  - **The referee's method.** Its own backtracking uses joint colour refinement on the table rows and forward checking, with no
    WL colours and no twin quotient. Twins are separate distinctions, so every isometry is a leaf.
  - **The result.** All 64 small pairs agree with the study's rows, row by row: the isometries, those keeping the loose
    distinctions, those keeping the growing end, the most junctions kept, and none carrying the states. The totals are 23,496 and
    96.
  - **A second, separate search** is restricted from the start to isometries keeping the loose distinctions. It gives the same
    counts in every pair, both directions, including 0 for the created pair.
- **The created pair and its junction maps hold, label for label.**
  - **Regrown from atlas 448 and 581.** The referee's engine gives exactly `junction_maps.py`'s lists, labels included. The round
    tags confirm that junctions 0–6 are the starts.
  - **Its 96 isometries** fall into the two junction maps of `junction_maps.json`, 48 each. Each keeps 11 of the 12 junctions:
    - A's start knot {0, 1, 8} goes to B's round-1 junction {11, 14, 21};
    - A's round-1 junction {9, 12, 15, 21} goes to B's start knot {2, 5, 8, 17};
    - six of A's seven starts go onto starts.
  - **The four-way join is the 12th junction.** Under every isometry, the image of A's join contains 21, which is loose in B, and
    not 17. B's join contains 17, the image of A's loose 21.
  - **No isometry keeps the loose distinctions**: 0 of 96, in both directions and in the restricted search. The loose counts and
    loose classes (1, 2, 2, 2, 3) agree, so E0 holds.
- **"The weight counts differ" holds.** The weight counts of the two equation spaces differ (122 against 125 words of weight 9,
  for one). So no renaming of the distinctions at all carries one space onto the other, which is stronger than the 0 of 96.
- **One size past: the 23 larger carried pairs the study left out.** These are the round-2 stages of 15 and 17 junctions. In all
  23:
  - **All 21,504 isometries keep the loose distinctions,** and every pair keeps the growing end.
  - **The most junctions kept is all but two,** and no isometry carries the states.

  So E3 holds on all 86 carried pairs, and E3b fails only in the six 9-junction pairs the note names.

## The checks (`job_created.py` under `scripts/longrun.py`; 88 cases, all ok)

| | Carried, small (63) | Created (1) | Carried, larger (23; one size past) |
| --- | ---: | ---: | ---: |
| Isometries (own enumeration, no twin quotient) | 23,496 | 96 | 21,504 |
| … keeping the loose distinctions (filter / restricted search) | 23,436 / 23,436 | 0 / 0 | 21,504 / 21,504 |
| Pairs with an isometry keeping the loose distinctions | 63 | 0 | 23 |
| Pairs with an isometry keeping the growing end | 57 (either direction) | 0 | 23 |
| Most junctions kept | all but two, in all 63 | all but one | all but two, in all 23 |
| An isometry carrying the states | 0 | 0 | 0 |
| Loose counts and loose classes equal (E0) | 63 | 1 | 23 |
| Agrees with the study's row | 63 of 63 | 1 of 1 | (not analysed by the study) |

## Point for the owner (listed, not folded in)

1. **"Their difference sits inside, two junctions away from the growing ends"** overstates where it sits. The referee took the
   isometries that keep all junctions but two and measured, in the junction graph, how far the two unmatched junctions are from
   the nearest live junction:
   - **distance 2** in 14 of the 63 small carried pairs, and in all 23 larger ones;
   - **distance 1** (next to a live junction) for at least one of them in the other 49 small pairs;
   - **live** for one of them in the six 9-junction pairs. The E3b row already says this.

   A reading that fits the data: "on closed junctions, next to or one step from the growing end, except in the six smallest pairs".
   **Not a block:** the contrast that matters, keeping the loose distinctions, is unaffected.

## Remark (no correction)

- **"That is why all of them stay together a round further"** is the note's account, not something it shows. The Limitations say so
  plainly: the sufficient direction is unproved, and E3b failed on 6 pairs that still persist. Direction #1 is the right test of it.

## How the work was split

- **The referee:**
  - read `created_pair.md`, the pre-registration, `isos.py`, `junction_maps.py` and both outputs;
  - wrote `job_created.py` and `created_readout.py`. They use its own FIRST-KNOT-R1 engine with the program's rule, its
    CENSUS-READ-R1 shore enumeration (exact: every stage has at most 17 junctions), its PARENT-RULE-R1 starts from the atlas, and
    a new isometry enumerator.
- **Read as data:** GROW-SMALL's `origin.json`, the literal lists in `junction_maps.py`, and `isos.json` for the row-by-row
  comparison.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 166 MB, a few seconds).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
