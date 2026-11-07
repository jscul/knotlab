# Uniform rules on the native map

Status: Proved (exact computation on the 191 saved and 86 fresh creation maps, through the order-free far sides)

Ticket `REFINE-READ-20261107-001B`, 2026-11-07.

## Question

- **What ticket A showed.** In every computed space the native creation map fixes the atoms: "same atom" is a union of stable pair
  classes.
- **What it did not show.** Each space may need its own description.
- **The question.** Does some uniform canonical rule, the same for every space, read the atoms of all of them? And where do the natural
  rules fail?

## Dependencies

- **`REFINE-READ-20261107-001A`.** Pair refinement (`refine_lib.py`).
- **GENUS-READ C.** Its native maps and native row twins.
- **GLUE-READ C.** Its two-stage rule.

## The rules (`rules_lib.py`)

All rules begin with GLUE-READ C's first step: the lines in yes/no twin classes of two or more are the atom lines. Then:

| Rule | Two atom lines are joined when |
| --- | --- |
| Yes/no two-stage (GLUE-READ C) | they create at each other and at the same other atom lines |
| Native row twins (GENUS-READ C) | they create at each other and send the same order-free vector to every other atom line |
| Maximal twin cliques | they lie in one maximal clique of the native twin relation |
| Native twins vetoed by pair refinement | they are native twins and their pair class holds only native twins |
| Native twins compatible at glue lines | they are native twins and at no glue line do both create with different order-free vectors |

**Classes.** These are connected components, except for the cliques.

## Results

| Rule | Spaces read (of 277) | Failures merging atoms |
| --- | --- | --- |
| Yes/no two-stage | 219 | 53 |
| Native row twins | 234 | 38 |
| Maximal twin cliques | 234 | 38 |
| Vetoed by pair refinement | 234 | 38 |
| Compatible at glue lines | 234 | 38 |

- **No uniform rule here reads every space** (check 1).
- **Components and cliques agree.** The native twin relation is an equivalence in every space.
- **The veto never fires, as it cannot.** Being native twins is preserved by pair refinement, so every pair class holds only twins or no
  twins.
- **How the native twins fail (check 2).** Where they fail, they merge atoms: 38 spaces.
  - **In 32,** two whole atoms are joined by complete twinship: every line of one is a native row twin of every line of the other.
  - **In the other 6,** the merged class holds parts of atoms.

## A regularity (check 3)

- **Within an atom.** Two lines of one Fano atom that are native row twins never both create at a glue line with different order-free
  vectors. That holds for 17,494 of 17,494 such pairs.
  - **What they do differ in.** At glue lines they differ only by one creating and the other not.
- **Across atoms.** 530 of 1,572 native-twin pairs do create at a common glue line in different ways: one through the Fano plane and
  census 58, the other only through K4^(3).
- **Why it is not enough.** That separates some merged atoms, but chains through the other 1,042 pairs still merge them.

## Reading

- **Rows at atom lines say too little.** Two atoms that meet one plane piece can send every atom line the same native vectors, from every
  one of their lines.
- **Their difference lives at the glue,** where an atom's own lines differ too.
- **How the regularity separates them.** It says how they differ: inside an atom only by presence, across atoms sometimes by kind.
- **A uniform reading needs more.** Pair refinement shows one exists in each space (ticket A). It is not yet known to come from one
  formula.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Five uniform rules | none reads all; 219, 234, 234, 234, 234; twins an equivalence in 277 of 277 |
| 2 | How the native twins fail | 38 spaces merge atoms, 32 by complete twinship of two whole atoms |
| 3 | Glue compatibility | within an atom 17,494 of 17,494 compatible; across, 1,042 of 1,572 |

## What this does not establish

- **A uniform rule.** None that reads every space was found, and none is shown impossible.
- **A proof of the regularity.**

## Novelty

New here: the measurement and the regularity.
