# Referee report CARRIER-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - Theorem K\* and Lemma P are correct.
  - "C′ is false" follows at every depth, not only at depths 11 and 12. The bound comes from K\* with the every-depth routine,
    whose tiers and periodicity cover every s and every N.
  - The referee read both routines against Theorem W's, and recomputed by SAT, with its own orbits, pieces and bond search, every
    block and stem value at depths 7 and 8 over every orbit pair: 108 of 108 block values and 50 of 50 stem values equal the stored
    tiers, which cover r = 0 to 4 and so every tier of −147 and −111.
  - One size past, at depth 12, carriers of at most 5 are found at s = 5, 7 and 9 and checked as bonds of the whole pattern.
  - The owner's three points:
    - (a) The case (ii) stem descent agrees with SAT.
    - (b) The block tiers to r₀ + 1 are right.
    - (c) For −73 at s = 7, "none of at most 8" is in fact "none of any size" (product test, every pair).
- **What changes: the counts.**
  - The 25 descriptions are only 10 distinct patterns. Their clause sets are identical at depths 8, 9 and 12, because the mutated
    words act identically.
  - **The 12 counterexamples are 5 distinct patterns,** so C′ is refuted by 5 patterns.
  - **The 13 are 5 distinct patterns.**
  - **"Two mutants, −73 and −79," at depth 12 are one pattern.** The two certified runs refuted the same 25,518 formulas.
  - **Upstream:** KEEP-REACH's 2,380 "patterns" are 583 distinct, its 39 are 16 distinct, and the census's 786 descriptions are 181
    distinct. The referee's own KEEP-REACH report missed this.

## What holds

- **Theorem K\* (proved).**
  - A set inside X is constrained or free in P_N exactly as it is in the projection onto X. So a bond of an exact projection that
    meets both levels is a bond of P_N.
  - This needs no property of X beyond exactness. It also makes C\*'s "if" direction immediate for any pieces whose projection is
    computed exactly.
  - The computational half ("decided for every s and every N by a finite computation") is the every-depth routine, with one caveat:
    bonds are searched to 8 members, so "decided" means decided up to 8 (see (c)).
- **Lemma P (proved).**
  - (a) is the window tree's separation: O_v's subtree meets the rest only at O_v. So the projection onto O_u, O_v and O_v's
    children is the pair relation before O_v's subtree, joined on O_v with the window's allowed assignments whose child parts
    extend.
  - (b) keeps each ancestor's assignment through Theorem W's descent. Keeping a coordinate forgets less, and it does not change
    which states are allowed.
- **"C′ is false" at every depth (the coordinator's first question).** C′ says the reach from level k is bounded exactly when a
  two-orbit bond from level k survives at every distance. Refuting it needs two things, both established at every depth by
  every-depth computations.
  - **These patterns are bounded.** A carrier of at most 5 exists at every s and every N:
    - two-orbit or block bonds give 3 and 4 at s = 1 and 2;
    - for −147 and −111, block bonds give 4 or 5 at every s, in the tiers r = 0, 1 and r ≥ 2;
    - for the others, stem bonds give 5 (4 at s = 3 for ca1efb37ad88) at every s ≥ 3, in the single tier r ≥ 0, since r₀ = 0.
  - **No two-orbit bond survives.** None exists from level 3 past s = 2 or 4, which is KEEP-REACH's routine. KEEP-R1 checked it by
    SAT at depth 8.

  The every-depth routine is exact for all s and all N because two things repeat:
  - the state sequence along s repeats (the study reports its start and period);
  - the feasible sets repeat from r₀ on, so remaining depths r ≥ r₀ (r₀ + 1 for blocks) share one tier, and smaller r are computed
    at their own depth.

  So the bound is proved by K\* and an exact finite computation, not read off depths 11 and 12.
- **The routines, read line by line.**
  - **`two_block.py`.** `every_depth_block` is KEEP-REACH's refereed routine with the property changed.
    - The children read F[r − 1]. So the tier r = r₀ is separate (children at F[r₀ − 1]), and r ≥ r₀ + 1 is stable.
    - For r < r₀, the last r₀ − r steps use the exact F[r + j − 1].
    - Small cases go to `direct_block` at their own depth.

    This is the owner's point (b), and it is right.
  - **`head_bond.py`.**
    - In case (ii), the states start at the common ancestor's two branches, with the other children feasible. They descend both
      branches and filter O_u by its own subtree's feasibility.
    - The head then holds O_u alone. B, O_v's ancestor at level k, is not in the stem, as the definition says. Each recorded step
      adds the child orbit's assignment.
    - The tier logic sends to the direct computation exactly the cases whose recorded steps would need unstable feasible sets
      (j < r₀ − r).
- **SAT at depths 7 and 8, every orbit pair** (`referee_carrier.py tiers0..2`, `.json`).
  - **How it was computed.** P_N is the census's `pattern(key, N)`, and the orbits are the referee's own (KEEP-REACH-R1's). The
    pieces are built from addresses:
    - O_v's children are its addresses' two children;
    - the stem's ancestors are the orbits holding O_v's addresses' ancestors at levels 4 and 5.

    Each projection is enumerated exactly by CaDiCaL with blocking clauses, and the least bond comes from the referee's own search.
  - **What was compared.** For all 12 descriptions, s = 1 to N − 3, at N = 7 and 8 (remaining depth r = 0 to 4), the least block
    bond and the least stem bond over all pairs were compared with the stored sequence at tier r.
  - **What it found.**
    - 108 of 108 block values and 50 of 50 stem values agree. The 10 other stem cells are −147's and −111's, which the study did not
      run.
    - The best carrier over s is at most 5 for every description at both depths.
- **One size past: depth 12** (`deep`, `deep2`, `all7`).
  - **The pairs searched.** At N = 12, for the five distinct patterns among the 12, the referee searched pairs at s = 5, 7 and 9
    until a carrier of at most 5 appeared.
  - **What it found.**
    - Block bonds of 4, 4 and 5 for −147 and −111.
    - Stem bonds of 5 for −58 and both ca1efb37ad88 patterns.
    - Every one is a bond of the whole depth-12 pattern by direct SAT: constrained, with every subset one smaller free.
  - **One false alarm.** A first sample of 24 random pairs missed the ca1efb37ad88 stems at s = 7 and 9 (`deep`, "found: null").
    Searching the pairs in order found them at once, at depths 10, 11 and 12, on a pair whose O_v descends from O_u.

## 1. The counts: 25 descriptions, 10 patterns (Narrowing)

The mutants were made by changing one word index of a placement. In these keys the changed words act identically on every level
(word 0 and word 2 of −73's automaton agree on every level to 12). So many mutants are the same pattern. `pattern(key, N)` gives
literally the same clause set at N = 8, 9 and 12 for:

| Group (identical patterns) | Kind |
| --- | --- |
| ca1efb37ad88-361, -364, -367, -375, -378, -386, -389, -418 | unexposed |
| ca1efb37ad88-835; bace53f8f952-58; -111; -147 (four singletons) | unexposed |
| 8db5da810c00-73, -79, -84, -94, -106 | products |
| 8db5da810c00-76, -86, -92 | products |
| 8db5da810c00-81, -97, -103 | products |
| 8db5da810c00-89; -100 (two singletons) | products |

What changes:
- **C′ is refuted by 5 distinct patterns,** not 12. The refutation stands.
- **"The nine ca1efb37ad88 mutants" are 2 patterns**, and "stems hold the top in ten patterns" (the glossary entry) is 3 patterns.
- **"P1 holds: all 12 mutants besides −73"** is 4 patterns besides −73's own.
- **"At depth 12 two of them, −73 and −79"** are one pattern.
  - Their two certified runs list the same 25,518 refutation hashes, so they solved the same formulas.
  - "At least 7 at s = 7 and 8" is one pattern's reading.
  - The pending CARRIER-A5 (−73, depth 13) and CARRIER-A6 (−79, bound 7) run on that same pattern.
- **Upstream** (`KEEP-REACH-20261117-001`, counts in descriptions):
  - its "2,380 small-orbit patterns that live at every depth" are 583 distinct clause sets at N = 9;
  - its third class of 39 (14, 13 and 12) is 16 (6, 5 and 5);
  - the census's 786 descriptions are 181 distinct.

  KEEP-REACH sometimes says "descriptions" and sometimes "patterns". Its fractions (1,081 forget and grow, 39 never forget) are
  fractions of descriptions. The referee's own KEEP-REACH-R1 did not recompute them and missed this.
- **Lesson.** Count distinct patterns (clause sets at a fixed depth, or orbits of the key space under words that act the same),
  not keys. A mutation that swaps a word for one with the same action changes nothing.

## 2. The owner's three points

- **(a) The case (ii) stem descent.** The referee split the pairs at N = 8, s = 3 to 5 by whether O_v descends from O_u.
  - In each case it computed the least stem bond by SAT, and the study's own descent restricted to that case
    (`referee_caseii_routine.py`). The two agree in all seven cells finished:
    - case (i): 5, 5, 5, 4, 5, 5, 5;
    - case (ii): 5, 5, 6, 5, 5, 5, none.

    The run stopped at its 3,000-second cap during −73 at s = 4.
  - The least bonds come from case (i) pairs, except where both cases tie.
  - Case (ii) never gives less. For bace53f8f952-58 at s = 5 it gives 6 against case (i)'s 5. For −73 at s = 3 it gives none.
- **(b) The block tiers to r₀ + 1.** The reading is right (above). For −147 and −111, r₀ = 1, so the tiers are r = 0, r = 1 and
  r ≥ 2. The SAT values at N = 7 and 8 cover all three, and every one agrees, including −147's split (5 at r = 0, 4 from r = 1) and
  −111's (5 at r ≤ 1, 4 from r = 2).
- **(c) "None of at most 8 from s = 7".** It is a cap as written. For −73 the referee tested what lies past it (`cap`).
  - **The test.** At depth 10 and s = 7, it asked, for every one of the 512 orbit pairs, whether the stem piece's projection is the
    product of its upper part (O_u and the two ancestors) and O_v. A product has no bond meeting both sides, of any size.
  - **The result.** 506 of 512 are products. The other 6 have no bond meeting both ends at any size (uncapped search). So depth-2
    stems carry nothing at s = 7 for −73.
  - **Every depth.** The study's stem tier for the 13 is the single tier r ≥ 0, since r₀ = 0, so this depth stands for every depth.
  - **Not finished.** The same test on −89 did not finish inside its cap, and −100 was not reached.
  - **What follows.** For −73, "none of at most 8" can be strengthened to "none at all" at s = 7. For the others it stays a cap.

## 3. The 13 (the coordinator's second question; Not a block, with one wording fix)

- **What is certified.**
  - L₁₁(3, 5) = L₁₁(3, 6) = 6 needs "no bond of at most 5" (certified by LRAT, 0 incomplete) and a stem bond of 6. The certified
    runs record "> 5" for every description at s = 5 and 6.
  - At depth 12, "> 6" at s = 7 and 8 holds for one pattern (−73 = −79), with 25,518 certified refutations and 0 incomplete.
  - The referee did not re-check the LRAT files: no LRAT checker is installed here.
- **At depth 9** (`thirteen`), the referee found a stem bond of 6 for −73 at s = 5, checked as a bond of the whole pattern, which
  agrees with the stored 6. The other four distinct patterns were not reached in the time given (pairs with no stem bond are
  searched to 6, and the first cell took 18 minutes). The study's `verify_bonds.py` covers all 13 at depth 11.
- **The wording.**
  - The note keeps "whether it rises without bound" open, and its table says "at least 7 at s = 7, 8 (depth 12, two of them)".
  - "Their reach keeps rising past every carrier found: 3, 4, 5, 5, 6, 6, then at least 7, 7" joins depth-11 values (s ≤ 6) to a
    depth-12 lower bound. Reach need not be monotone in N: a deeper pattern can make a bond's subset constrained.
  - So the fair reading is "the depth-11 and depth-12 readings rise to at least 7 at s = 7, 8 for one pattern", not "keeps rising".
  - The intuition entry's "two tested deeper need at least 7" should say "one pattern (two descriptions)".

## 4. Smaller points (Not a block)

- **P2.** Its failure on both counts is carried honestly. Threshold searches that ran out of budget are reported as undecided, not
  as evidence.
- **The predictions file.** It was frozen after the threshold run was launched; this is disclosed.
- **The repaired conjecture C\*.** It is stated with the advisor's unchecked pumping sketch. That is right as labelled.
- **"Stem".** The word is not from two or three dimensions. Its glossary entry should read "three patterns (ten descriptions)".

## Fixes for the thread (listed for the owner, not folded in)

1. **Counts.**
   - Say "descriptions" or give distinct patterns everywhere: the note, the proof's table, the intuition entry, the glossary entry,
     the goals checkpoint and A97's text if it counts.
   - The 12 are 5 patterns, the 13 are 5, −73 and −79 are one, and the nine ca1efb37ad88 are 2.
   - Correct KEEP-REACH's "2,380 small-orbit patterns" (583 distinct) and its third-class counts (16 distinct) in the same way.

   **Narrowing.**
2. **The 13's growth wording.** Replace "keeps rising past every carrier found" with readings scoped by depth and pattern.
   **Narrowing, wording.**
3. **The cap.** For −73 at s = 7, write "no depth-2 stem bond of any size" (the product test). For the rest, keep "of at most 8".
   **Not a block.**
4. **The record.** Give `deep`-style searches a fixed pair order or the full set of pairs; a random sample can miss the carrying
   pairs. **Not a block** (referee's own lesson).

## How the work was split

- **The referee:**
  - read the note, the predictions, the proof, `two_block.py`, `head_bond.py`, `threshold.py`, `threshold_deep.py`, the stored
    sequences and the certified threshold outputs;
  - checked K\*, Lemma P and the tier logic by hand;
  - wrote its own SAT computation of block, stem and two-orbit pieces over every orbit pair, its own bond search and direct bond
    checks on the whole pattern;
  - compared the 25 descriptions' clause sets.
- **The study's code** was run only in `referee_caseii_routine.py`, to read its case (ii) states for comparison.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_carrier.py`,** its parts' `.json` and `.log` files:
  - `tiers0`, `tiers1` and `tiers2` (depths 7 and 8, every pair);
  - `caseii`;
  - `deep`, `deep2` and `all7` (depths 10 to 12);
  - `thirteen` (depth 9, one cell);
  - `cap` (the product test; −73 finished, −89 stopped at the cap).
- **`referee_caseii_routine.py` and `.json`:** the study's descent split by case, against the referee's SAT.
- **`referee_duplicates.json`:** the groups of identical clause sets among the 25, the 39 and the 2,380.

Reproduce, from `research/CARRIER-20261117-001/referee-R1/`:

```sh
for p in tiers0 tiers1 tiers2 caseii deep deep2 all7 thirteen cap; do
  ../../../.venv/bin/python -B referee_carrier.py $p > referee_carrier_$p.json 2> referee_carrier_$p.log
done
../../../.venv/bin/python -B referee_caseii_routine.py > referee_caseii_routine.json
../../../.venv/bin/python -B referee_duplicates.py > referee_duplicates.json
```
