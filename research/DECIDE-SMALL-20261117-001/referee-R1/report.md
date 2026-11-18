# Referee report DECIDE-SMALL-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - "476 new" is counted on distinct patterns. The referee's own digest of each clause set gives 627 distinct patterns, 151 seen
    before and 476 new, at depth 12 and again at depth 16.
  - The dedup holds two sizes past the study's recheck: none of the 6,177 merges splits at depth 16.
  - The 55 "undecided" ground-truth cells hide no misfit. 22 of them are certified readings that fit, and the referee's SAT closes
    31 of the other 33. The last one is consistent with Theorem F's rechecked hypothesis.
  - Early exit and T4's combination of carriers are sound, and checked.
  - The MODE-BOND-A1 fold-in is sound as an existence check.
- **What changes.** Wording and counts only:
  - 44 of the 452 "grow by forgetting" have no bond between the ends at all;
  - the ground truth fits 167 readings, not 145;
  - the intuition entry and the goals bullet should name the population's scope.

## What holds

- **Counting on distinct patterns (the coordinator's first question; `referee_decide.py` item 1, `referee_decide_extra.py` item 5).**
  - The referee digests each clause set: the SHA-256 of the sorted knot triples of `pattern(key, N)`. The study's code is not used.
  - At depth 12 the populations are:
    - the study's 627 descriptions, which are 627 distinct patterns;
    - KEEP-REACH's 2,380 small-orbit descriptions alive at every depth, which are 583;
    - the census's 786 descriptions, which are 181;
    - 73 patterns are in both KEEP-REACH's and the census's.
  - Of the 627, 106 are in KEEP-REACH's, 112 in the census's, and 151 in either, so **476 are new**. Every count is the same at
    depth 16.
  - The three populations together hold **1,167 distinct patterns**, which is the note's "1,000 and more". All of them are decided:
    - the census: 740 forget and 46 have a two-orbit bond at every s;
    - KEEP-REACH's: all 583 (MODE-BOND-R1);
    - the 627 here.
  - If a merge were wrong, 627 and 476 would be lower bounds. A difference at depth 12 is a real difference, so neither number can
    be too high.
- **The dedup one size past (the owner's point (c); item 2).**
  - All 6,804 kept draws were rechecked at depth 16 against their group's first draw. None of the 6,177 merges splits, and the 627
    representatives stay distinct.
  - **Not proved.** A short length bound of Moore's kind does not follow directly. A level's clause set is the image of the words'
    action, a set of triples, not one output per address.
  - Equality at every depth looks decidable in principle: each description's triples over all levels form a regular set of
    three-track address words. Not attempted.
  - The note says this ("rechecked … not proved").
- **Early exit (the owner's point (a); item 3, and the study's full checks).**
  - **The logic.** Each test is a sufficient condition proved in an earlier study: T1, T5 and T3 for growth, T2 and T4 for
    boundedness. So the order cannot change a verdict. Only a false theorem or a faulty implementation could make two tests of
    opposite kinds both pass.
  - **The study's 62 full checks** run all five tests:
    - 45 growing patterns pass all three growth tests (T1, T5 and T3) and neither bounded test;
    - 16 bounded patterns pass T2 and T4, and 1 passes T4 alone;
    - no pattern passes tests of both kinds. So the full checks do run both sides.
  - **The referee's sample** (seeded, 40 + 40, with the referee's own SAT tools from KEEP-REACH-R1, at N = 8):
    - *40 T1 patterns.* No two-orbit bond at s = 1..5 is smaller than Theorem F's bound 1 + ⌈s/r⌉. Every joint r levels apart is a
      product (0 non-products). The bond part is weak where no two-orbit bond fits at N = 8, which is 10 of the 40.
    - *40 T2 patterns.* A two-orbit bond exists at every s = 1..5 (0 missing).
  - **The ground truth** (below) agrees on about 45 T1 patterns and on the T2 and T4 upper bounds.
- **T4's combination of carriers (the owner's point (b); `referee_decide_extra.py` item 7).**
  - **Why the combination is sound.** The combination is a pointwise least of genuine bonds. At each s and depth one carrier's bond
    exists and bounds L there, so the maximum over cells bounds L everywhere. Nothing needs to hold for one kind of carrier
    throughout.
  - **The referee's own SAT, at depths 9 and 10, s = 1..5, within T4's maxima:**
    - *1740 (maximum 5).* Orbit-and-block bonds alone hold every cell, with 3 to 5 members.
    - *9432 (maximum 4).* Neither kind alone holds every cell:
      - block bonds hold for s ≤ 3 and none fits at s = 4, 5;
      - stems of depth 2 begin at s = 3 and hold through s = 5 with 4 members.

      So the combination is what decides 9432, and it does so correctly.
  - The ground truth agrees: 9432 reads L₉ = 3, 3, 4, 4, tight at its bounds.
- **The ground truth's undecided cells (the coordinator's second question; item 4).**
  - **What the 55 contain.** The note's 55 non-integer cells are not all undecided:
    - 16 read "none": patterns 0, 5, 34 and 35, which have no bond at any s;
    - 6 read "> 10";
    - all 22 are certified readings on growth verdicts, so they fit;
    - only 33 cells are undecided within 60 s.
  - **The referee's check of the 33, by SAT at depth 9:**
    - *30 growth cells with a lower bound of 2 or 3.* No pair across levels 3 and 3 + s is constrained, so L₉ ≥ 3 (lower bound 3),
      or the cell fits trivially (lower bound 2). All fit.
    - *The 2 bounded cells.* A bond within the upper bound exists: 4 members for 1740 at s = 4, and 5 for 52 at s = 4. Both fit.
    - *The last cell* is pattern 93 at s = 4, where r = 1 needs L₉ ≥ 5.
      - Not shown directly: the referee shows only that no bond has two members.
      - Theorem F's hypothesis holds there: every joint one level apart is a product at depth 9, from level 3 to 8. Its readings 3,
        4, 5 at s = 1..3 are exactly 1 + s.
  - **So no misfit hides there.** 167 certified readings fit, the referee's check fits 32 more, and one is open but consistent.
- **The MODE-BOND-A1 fold-in (fd39c35df).**
  - **Sound as an existence check.** Every pair of the backward closure is derived step by step and carries its witness. The
    gadget criterion, M₁ nonempty and M₁ ≠ M₂ at a level-3 type, is a property of one pair. So stopping at the first pair at a
    level-3 type returns a genuine gadget, and nothing depends on the closure being complete.
  - **What was found.** For both ca1efb37ad88 controls, the existence check finds 122 gadgets before it stops:
    - 120 are base pairs at the level-3 start types 3 and 4. These are periodic non-product composites that begin at level 3, the
      simplest kind of gadget;
    - 2 come up through blocks from type 2.

    The first, `(3, 3, 1, 3)`, is a base pair.
  - So **P2 holds on all 5 controls**. These two controls' gadget counts are unknown, since the full closure passed its cap. The
    note's wording is accurate.

## 1. "452 grow by forgetting" includes 44 with no bond between the ends (Not a block, wording and counts)

- **The count.** By union-find on the knot triples at depth 10 (item 6):
  - 1 pattern is empty;
  - 42 have every knot within one level, 2 of them with no knot at level 3;
  - 1 (4450) has a top component that stops at level 4.
- **Why their reach is "none".** Every knot spans at most one level (checked on all 627). So a component that misses a level at
  depth 10 misses it at every depth.
  - By Lemma J, no bond meets level 3 and level 3 + s:
    - for every s ≥ 1 in 43 patterns;
    - for every s ≥ 2 in 4450.
  - Their reach is "none", not a growth. Theorem F's bound holds for them vacuously.
- **How the program has named them.** The census names this class "no bond" (278 of its 786 descriptions).
- **The other side.** The other 408 T1 patterns, the 174 bounded and the T3 pattern have the ends joined at every s ≤ 4.
- **What to fix.**
  - Split the T1 row: 408 grow, and 44 have no bond across the ends. The same split applies to the unseen column.
  - The Answer's "it grows when some part of what joins the ends forgets" does not describe the 44, since nothing joins the ends.
  - P3 holds either way: T1 decides 72%, or 65% without them.

## 2. The ground truth's count (Not a block)

- **What the note says.** "145 of the 200 cells decided … 55 undecided within 60 s, not counted" (the Answer, conclusion 4, P7).
- **What the cells show.** 167 cells hold certified readings, and all fit. 33 are undecided, and the referee's SAT closes 32 of them.
- **Fix:** "167 certified readings on 50 patterns all fit (22 of them 'none' or '> 10' on growth verdicts); 33 cells undecided
  within 60 s".
- 4 of the 50 patterns have no bond at all. The ground truth's draw-order selection includes the degenerate patterns of §1.

## 3. The sample's weighting where "every pattern" is claimed (the coordinator's third question; Not a block)

- **The note.**
  - The Answer states the weighting ("under this weighting").
  - The conclusions say "of a fresh 10,160-draw sample".
  - The objects row and the close commit name "KEEP-REACH's weighting". These are fine.
- **The intuition entry and the goals bullet.**
  - Both read "Every small-orbit pattern seen is decided". "Seen" scopes it, and the claim holds for all 1,167 distinct patterns
    seen.
  - But neither names the population's scope, which is a scope and not only a weighting:
    - automata of at most three states;
    - one to four knot placements;
    - orbits of at most four addresses.
  - The goals bullet names "a fresh fair-coin sample". The intuition entry names nothing.
  - **Fix:** "every small-orbit pattern seen (627 fresh distinct patterns from automata of at most three states with one to four
    placements, KEEP-REACH's fair-coin weighting)".
- **The note's Next steps.** "1,000 and more" can read "1,167".

## 4. Smaller points (Not a block)

- **The dedup.** It stays unproved, as the note says. It now holds at depth 16. A wrong merge would only lower 627 and 476.
- **Time.** T4 took 93 s on 9432 against a 120 s limit. A limit cannot change a verdict, since a timeout is rerun with four times
  the limit. But T4 runs near its limit on such patterns.
- **The predictions.** P1 and P3 to P7 hold, and P2 fails narrowly (9.2% against 10–30%), as reported. P7 holds more strongly than
  stated.

## Fixes for the thread (listed for the owner, not folded in)

1. **The growth count.**
   - Split "452 grow by forgetting" into 408 that grow and 44 with no bond across the ends ("no bond", as the census names it).
   - Do this in the table, the conclusions, the goals bullet and checkpoint row, and the objects row.
   - Adjust the Answer's "it grows when some part of what joins the ends forgets".

   **Not a block, counts.**
2. **The ground truth.** 167 certified readings fit and 33 cells are undecided, not 145 and 55. **Not a block.**
3. **The scope.** Name the automata's size and placements in the intuition entry and the goals bullet, and write "1,167" for
   "1,000 and more". **Not a block.**
4. **Optional.** Record the depth-16 dedup recheck beside the depth-14 one.

## How the work was split

- **The referee:**
  - read the note, the design, the predictions, `decide.py`, `ground_truth.py` and all the outputs;
  - read the MODE-BOND-A1 fold-in and `decorated.py`'s closure;
  - wrote its own clause-set digests, the population overlaps and the merge recheck;
  - wrote the union-find on knots, the undecided-cell checks and the T4 carrier cells, reusing its own SAT tools from CARRIER-R1
    and KEEP-REACH-R1 (`referee_decide.py`, `referee_decide_extra.py`);
  - ran the study's `decorated.gadgets` once, only to read which kind of pair the existence check returns.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_decide.py` and `.json`:**
  - 1, counts on distinct patterns at depth 12;
  - 2, every merge at depth 16;
  - 3, the early-exit sample;
  - 4, the 33 undecided ground-truth cells.
- **`referee_decide_extra.py` and `.json`:**
  - 5, the overlap at depths 12 and 16 and the union;
  - 6, the ends joined, by union-find, with knot level spans;
  - 7, T4's carriers per cell.

Reproduce, from `research/DECIDE-SMALL-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_decide.py > referee_decide.json
../../../.venv/bin/python -B referee_decide_extra.py > referee_decide_extra.json
```

The pattern 93 check is one call: `check_forget(key, 9, 1)` from KEEP-REACH-R1's `referee_two_orbit_sat.py`. It returned 0
non-products at levels 3 to 8.
