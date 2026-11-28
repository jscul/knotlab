# Abstract patterns and the eight-knot check

All 36 published minimal patterns match individually, including their signs, cells, kinds, inert distinctions and cross-pair coverages. At eight knots there is **no odd minimal whole-choice set**, even when the number of distinctions shared by a pair is unrestricted. The reduction that proves the last extension needs a qualification about nonempty choices.

Each vote in the table is one full meeting pattern up to relabelling. The simple counts include knots with no meeting. The doubled counts require every knot to meet another and some pair to meet twice. A whole-choice set must contain a cell. Minimality tests all proper subsets, including those of even sign.

| Knots | Meetings per pair | Patterns | Whole-choice sets | Odd whole-choice sets | Minimal, even | Minimal, odd |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 4 | 0 or 1 | 11 | 1 | 1 | 0 | 1 |
| 5 | 0 or 1 | 34 | 8 | 7 | 1 | 2 |
| 6 | 0 or 1 | 156 | 16 | 12 | 0 | 0 |
| 7 | 0 or 1 | 1,044 | 48 | 28 | 0 | 0 |
| 8 | 0 or 1 | 12,346 | 92 | 49 | 0 | 0 |
| 4 | 0, 1 or 2, with a doubled meeting | 49 | 31 | 0 | 31 | 0 |
| 5 | 0, 1 or 2, with a doubled meeting | 703 | 263 | 20 | 0 | 1 |

Four mutually meeting knots account for one odd minimal class. Two knots both meeting the same three, the literature's $K_{2,3}$, account for the other three. The two may meet each other zero, one or two times. Every one of these additional distinctions is inert.

## What survives parity reduction

For two disjoint holder pairs with multiplicities $p$ and $q$, the whole choice has $pq$ cells on those holders. Therefore reducing every meeting multiplicity modulo two preserves the parity of the cross-pair counts and the fixed-order sign on every subset.

- **Having a cell can change.** A doubled meeting and a separate single meeting give a minimal even set with two cells. Its reduction has no cells. The glossary's definition needs the nonempty condition as well.
- **An odd minimal set descends.** Odd sign guarantees that some cell survives in the reduction. If a proper subset in the reduced pattern were a nonempty whole-choice set, its cell would still exist before reduction and all its cross-pair counts would still be even. This would contradict minimality. The complete simple classification at exactly eight consequently excludes odd minimal sets on eight knots for every finite multiplicity.
- **Minimality can change when meetings are doubled.** Let X and Y each meet A, B and C once. Add two distinctions shared by A and B. The full five-knot choice has ten cells, commutes and closes odd. Its only proper whole-choice sets are {X, A, B, C} and {Y, A, B, C}, each with two cells and even sign. Without the doubled meeting the five-knot choice is minimal. Nine of the 703 five-knot doubled classes have an odd whole choice and exclusively even minimal sets.
- **Literal cell counts can change at a surviving odd set.** On four mutually meeting knots, triple one meeting. Five cells remain and the set is minimal odd. Every cell has four holders, so there is no smaller candidate. This example is outside the abstract population's multiplicity cap.

For multiplicities at most two the descent also gives an exhaustive check of literal odd kinds through eight. The three simple odd minimal patterns have respectively 1, 16 and 8 labelled assignments of weights 0 or 2 on their absent pairs. Of these, 1, 2 and 1 retain minimality. In each of the four survivors the active meetings are all single. This checks the literal classification separately from parity.

## Fixtures and validation

Four mutually meeting knots have three cells and the two meeting the same three have six. Both are minimal odd. The ring of five with a knot meeting all five has 20 cells and no whole-choice subset. The ring of four has two cells and no whole-choice subset. The ring of three with a separate meeting is minimal even with three cells. The doubled meeting with a separate meeting is minimal even with two.

The literature's Petersen graph can be constructed on the ten two-element subsets of five symbols, with disjoint subsets meeting. Its whole choice has 75 cells and closes odd. All 847 proper subsets of at least four knots failed the whole-choice test. The remaining 176 proper subsets are too small for a cell. The largest mutually meeting subset has size two, and two knots share at most one neighbour.

The enumeration adds a knot of least total multiplicity to every smaller pattern. Deleting such a knot proves coverage. A refinement and individualization procedure identifies exact relabellings. Averaging the number of fixed pair-colourings over all knot permutations independently checks the class total at each size by Burnside's lemma. The generated simple patterns through seven also match every entry of the atlas. The archived classifier had skipped its 205 patterns with an isolated knot. They cannot have a full minimal set because removing the isolated knot preserves every cell.

Across the 14,343 patterns in the table, the integer formula matched a direct four-holder count on all 377,682 knot pairs. Cancellation in the literal repeated-distinction word agreed with interleaving parity in the starting order of every pattern and in 3,569 order tests on the 459 full whole-choice sets. Every one of the 6,726 knot-pair exchanges on these sets had the parity of the cross-pair coverage. The four minimal simple atlas patterns were also tested for a circular order with zero interleavings. Only the even three-cell pattern had one. The full JSON contains the orders, fixtures and counts.

The pilot through six enumerated 156 simple six-knot classes in 0.02 seconds and 792 unrestricted five-knot classes with weights at most two in 0.05 seconds. With at most 133,632 proposed extensions at eight, the full run was budgeted under two minutes. One process with a 2 GiB address-space cap completed it. Run from the repository root with

```sh
OMP_NUM_THREADS=1 .venv/bin/python -B research/NATIVE-CARRY-20261128-001/referee-R1/abstract_check.py --through 8 --output research/NATIVE-CARRY-20261128-001/referee-R1/abstract_counts.json
```

Nine-knot patterns and classifications beyond the ten-knot fixture were not run.
