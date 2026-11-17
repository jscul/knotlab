# DECIDE-SMALL-20261117-001: design

Epic `DECIDE-SMALL-20261117-001` takes direction #1 of `MODE-BOND-20261117-001` at the coordinator's go-ahead (2026-11-17 23:37
UTC). It serves G17, with G1. The advisor checked the design before the freeze (`advisor/design_question.md`,
`advisor/design_answer.md`); its changes are marked (advisor).

## The question

On KEEP-REACH's population every small-orbit pattern is decided by five proved tests. Is that because the tests are complete for
small orbits, or because the population was small and partly built from four seeds?

## The sample and its weighting

- **Weighting.** KEEP-REACH's fair-coin sampler (`run_sample.draw`) with a new seed, `'DECIDE-1117-<i>'`:
  - s uniform in {1, 2, 3} automaton states, each with an output flip and two transitions, all uniform;
  - 1 to 4 placements, uniform in number, each a sorted triple of distinct slots, uniform among the 3(1 + s + s²) slots.
- **Size.** 10,160 draws, ten times KEEP-REACH's fresh sample.
- **Kept.** Descriptions with orbits of at most four addresses that live at every depth.
- **Deduplication, before any test.** By the SHA-256 of the clause set at depth 12. Every merge is rechecked at depth 14, and a merge
  that splits there is reported (advisor). Only a pattern's first description is tested.

## The tests

Five tests, in this order, each proved earlier:

| Test | What it checks | Verdict | Source |
| --- | --- | --- | --- |
| T1 | forgetting on all assignments along blocks | grows | Theorem F, `BLOCK-REACH-20261116-001` |
| T2 | a two-orbit bond from level 3 at every s and depth tier | bounded | Theorem K, `KEEP-REACH-20261117-001` |
| T5 | the product test along joined children, on the component of level 3 | grows | Theorem G on the component, `MODE-BOND-20261117-001` |
| T3 | forgetting on the values states take, from level 3 | grows | Theorem F′, `KEEP-REACH-20261117-001` |
| T4 | orbit-and-block or depth-2 stem bonds at every s and tier, to 8 members | bounded | Theorem K\*, `CARRIER-20261117-001` |

Each test runs under its own limit of 120 s, and a timeout is recorded as such. The order is cheapest first.

## Changes after the advisor

- **No early stop.** Every draw is run, and every pattern that none decides is collected. The object of study is the first in draw
  order. This departs from the go-ahead's "stop at the first", for two reasons: the predictions need the full sample, and the cost
  is of the same order.
- **Consistency.** Every tenth distinct pattern runs all five tests. No pattern may be both growing and bounded.
- **Timeouts.** They are a third class, rerun with four times the limit.
- **Second tier, for undecided patterns only.** The least of four carriers at every s and tier:
  - orbit-and-block and depth-2 stem bonds to 12 members;
  - stems of depth 3, to 10;
  - depth-2 stems with the lower orbit's children, to 8.

  An undecided pattern is labelled "bounded by the second tier" or "undecided by both tiers".
- **Ground truth.** After the run, the census's certified search computes L₉(3, s), s = 1..4, on 50 decided patterns drawn in order
  (60 s per cell). Each reading must fit its verdict:
  - for T1, at least 1 + ⌈s/r⌉;
  - for T2 and T4, at most the bound;
  - for T5, at least Theorem G's bound.

## Read-out and stop

The study closes when the sample, the second tier and the ground-truth check are read. If some pattern is undecided by both tiers,
the first one in draw order is the object of a follow-up, named in the next steps.
