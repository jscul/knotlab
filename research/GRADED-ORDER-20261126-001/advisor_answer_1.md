# The advisor's review before the freeze (claude-fable-5-2, extra-high effort)

The route-cycle flag is two different failures under one name, and I have a hand-built start where the graded order should fail with no flag. Nothing here was run: file readings are marked as such, and the rest is by hand and `unverified`.

**Read:** the hivemind, `GRADED-ORDER` README and `graded.py`, both fresh files, `late.py`, `score.py`, the late-views README, decision and referee report, `explosive.md`, the `REDUCE-BLOCKS` proof, `eng.py` 282–365 (the roster), and the `weightlib.py` header.

## 1. The exception

- **The block clause is "two blocks share two knots".** That is the proved class's own hypothesis (`REDUCE-BLOCKS`, corollary 2). In 6408 the blocks {0,4,5} and {3,4,5} share 4 and 5; in the eight-knot start B_4 and B_5 share 2 and 3. The cell only hides it: `late.py` 113–114 counts both block-and-cell cycles as filled, and the block-to-block cycle is their sum.
  - Check: on every accepted start, `any(len(B1 & B2) >= 2)` over the kept blocks should equal the coded block clause.
  - No statement in the cycle space can be right, since a sum of two filled cycles is not filled here.
- **The cell clause is a different failure.** `late.py` 154–156 gives a cell no valid set when it holds two knots of another cell. The reading then makes one birth for both cells in round 1 where the growth makes two.
  - Worked on `fresh7_grow` line 104 and `tree+` line 121: one join against two, so they differ at round 1.
  - Natural statement: every round-1 group is a valid set.
- **The statement by rank:** a birth with two parents that share no parent. In the literature's words the order is not lower semimodular (Stanley, EC I, ch. 3).
  - The roster joins only births that pairwise share a parent (`eng.py` 335–355), so {4,2,5} and {4,3,5} enter two joins.
  - It is computable from `GeneralPiece.core_parents` without growing, so it can be frozen as a flag.
  - The exact test: the roster rule applied to the valid sets of one size returns the parent sets of the next. With Lemma R item 3 that is the whole induction.
- **A start where the graded order should fail with no flag:**
  - Start: eight knots, places `[5,7,6,4,7,6,4,5]`, pairs `0-7 1-7 2-7 4-7 5-7 0-1 1-2 1-3 2-3 0-4 4-5 4-6 5-6`.
  - Map: cells {0,1,2,3} and {0,4,5,6} share knot 0; the one kept block is {0,1,2,4,5}. Rank 4 equals filled 4, so it is a tree by the count, and `route_cycle` is false.
  - Round 1: the cells and the pairs 1–4, 1–5, 2–4, 2–5 are born. The pairs 1–4 and 2–5 share no parent.
  - Round 2: the growth should make four joins of four parents; the reading makes one of six.
  - First difference: round 1, where a cell gets 5 fresh distinctions against the reading's 2.
  - This shape cannot be built on seven knots, so it does not threaten F1 in the sample. Add it as a replay.
- **A flagged start that should agree:** none found among tree pieces. I went through the cases of what the two blocks hold outside the cell; this is not a proof.

## 2. What a referee presses first

1. **The F1 bucket "cells sharing a knot, no route cycle" may be one start 40 times.** All 40 (lines 81–120) have places 3,3,4,4,5,5,5. Lines 81, 82, 83 and 85 are one start up to renaming: a ring of six with a seventh knot on two neighbouring ring knots. `graded.py` 67 removes repeats by label only. I grew line 81 by hand and it agrees (births 5, 3, 1, then closing or relay).
2. **55 of the 95 flagged `tree+` starts have cells sharing two knots** (grep: all 40 of the mixed bucket, plus the 15). They should differ at round 1, so F2's "round 2" fails on them as worded. The block clause is tested only by the other 40.
3. **F3 has no scorer.** `score_file` prints only the first differing round.
4. **`tree+` is at bare sizes, so open equals round-1 demand.** Lines 41 and 81 have no pendant point: they close under parity within a few rounds and relay under not-all-equal. Cells with chains are then tested only by the `grow` set; count how many of the 175 have a chain.
5. **The README's "three to five places" is wrong for `tree+`**: line 41 has seven-place knots.
6. **`compare` scores only the rounds grown.** Report the rounds read for each start, and count a capped start apart.
7. **Time `predict(general=True)` on the start with the most pendant points**, under a memory cap, before the freeze.
8. **Stalls are not an issue**: bare sizes leave no knot short.

## 3. Numbers and the statement to prove

| Prediction | My number |
| --- | --- |
| F1 | 75% |
| F2, "differs" | 93% |
| F2, "first at round 2", as worded | under 5% |
| F2, "first at round 2", on the 40 block cases | 90% |
| F2, round 1 on the 55 with cells sharing two knots | 95% |
| F3, as worded | under 15% |
| F3, on the block cases with a scorer | 80% |

The statement to prove is not stated right:

- It should be false on the eight-knot start above.
- "The class read by the predictor" is defined by the count that let the route cycles in.
- It leaves out the chains, the relay and closing, and the floor max(D, 3 − p, 1).

A proof needs Lemma R, which is in hand, and one lemma about the order: for the class, any two parents of a valid set share a parent, and every clique that lies in no one parent's set of children is the parent set of exactly one valid set. Finding the class is the open part. Run the static test on the census and read off which maps fail. `EXPLOSIVE-20261119-001` direction 2 is the same open item.

Hivemind: one consultation entry and one standing fact (the roster's rule and the tree count, read at the lines) added, both `unverified`.
