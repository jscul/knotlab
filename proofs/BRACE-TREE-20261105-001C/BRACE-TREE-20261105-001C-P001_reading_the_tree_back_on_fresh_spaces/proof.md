# Reading the tree back on fresh spaces

Status: Proved (exact computation on fresh spaces; the predictions were fixed in ticket B, and one of them is refuted)

Ticket `BRACE-TREE-20261105-001C`, 2026-11-05.

## Question

Ticket B found rules relating native creation to the tight-cut decomposition on 50 spaces, and fixed a reconstruction (the source rule).
Do they hold on spaces they were not found on?

## Dependencies

- **`BRACE-TREE-20261105-001B`.** The dictionary, its 21 rules, the cut-direction and glue results, the source rule and `dict_lib.py`.
- **`BRACE-TREE-20261105-001A`.** `brace_lib.py`.
- **The fresh census.** Every three-fold class of 23 to 26 points, made by `gen_census.py` (THREEFOLD-SURFACES B's construction with the
  size bound raised from 22 to 26) and stored in `fresh_census.json`. Both are bound by hash.

## Predictions (fixed in ticket B, unchanged)

- **The rules.** Each of the 21 places of B's dictionary with two atom lines joined through atoms only keeps its one relation.
- **Cut directions.** Across a cut between two atoms, creation runs one way, from the receiver's intact lines to the emitter's lines.
- **Glue.** Lines of plane pieces and doubled squares never create at each other unless a non-Fano handle lies between.
- **The source rule.** Kept blocks of mutual creation count the Heawood braces, and the genus, on every space without a non-Fano brace.

## The fresh spaces (111)

- **The census of 23 to 26 points.** All 100 classes: 11 untwisted of 25 points, and twisted ones: 4 of 23, 11 of 24, 4 of 25 and 70 of
  26 points.
- **New trees of Fano atoms (11).**
  - Two atoms at points of the Fano plane with a third at a line off both.
  - Two receivers with an atom on one of them.
  - Chains of receivers, two and three deep.
  - A zigzag, in which one atom emits at two cuts.
  - Two atoms hanging from an atom that hangs from the base.
  - Mixed trees on the prisms over 8- and 10-cycles.
  - Census 58 with two atoms.
- **Every one fails.** Creation is exact.

## Results

| Prediction | Fresh evidence | Verdict |
| --- | --- | --- |
| B's 21 rules | 32,016 pairs at those places: every one as predicted | holds |
| Cut directions | 163 cuts between two atoms: every one one-way, receiver to emitter | holds |
| The source rule | 110 spaces without a non-Fano brace: kept blocks = Heawood braces = genus in all 110 | holds |
| Glue silent unless a non-Fano handle lies between | 12 creating pairs, all with a Fano atom between | refuted as stated |

**New places.** Six places B never saw each carry one relation; they are zigzags:
- `><>` (an emitter line against a cut line two cuts on): mutual; against an intact line: one-way (backward).
- `<><` (a cut line against an emitter line): mutual; an intact line against it: one-way (forward).
- `><<` and `>><`: mutual.

They agree with B's rules read at the two ends of the path. A cut line meets the atom across its cut mutually; an intact line meets
it one way.

**The source rule.**
- **Without a non-Fano brace (110 spaces).** The plain block count equals the genus in only 83 of the 110. The source rule, fixed
  before any of these spaces was computed, recovers it in all 110.
- **With census 58.** The one space built on census 58 (genus 3, two Fano atoms) gives 4 kept blocks.

**The glue refutation, located.**
- **Where.** All 12 creating pairs lie in one class, twisted 26-point class 65. Each is a planar-glue line against one doubled-square
  line, with a Fano atom between them on the tree path. Creation runs one way, from the plane piece to the doubled square's cut line.
- **The corrected statement holds.** Glue lines with no handle between them are silent: 1,354 of 1,354 fresh pairs, and 306 of 306 in
  ticket B. A Fano atom between can relay creation from one plane piece to another, as atoms relay halos.

## Reading

- **The rules generalize.** The relation between two atom lines is fixed by their place in the tree whenever only atoms join them, on
  spaces up to 26 points the rules were not found on.
- **Cut directions are native.** Creation runs from the receiver's intact lines to the emitter's lines, at every one of 163 cuts.
- **Native creation reads the genus, touching atoms included.** On every three-fold space of 23 to 26 points the source rule counts the
  Fano atoms, so native selection recovers the genus where atoms touch: 110 of 110 fresh spaces, after 47 of 47 in ticket B.
- **The limits.**
  - **Non-Fano handles.** Census 58 and the trisum brace are not read correctly.
  - **Relays through atoms.** Glue across an atom can create, as the one refuted prediction shows.

## Checks

`check.py` (`result.json`; about twenty minutes with 22 processes, enumerating solutions by SAT):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (with the fresh census and its generator); upstream proofs Proved | pass |
| 1 | The fresh spaces | 11 trees and 100 classes of 23 to 26 points, each failing |
| 2 | B's rules on fresh pairs | 32,016 of 32,016 as predicted; 6 new places, one relation each |
| 3 | Cut directions | 163 of 163 one-way, receiver to emitter |
| 4 | Glue | refuted as stated: 12 creating pairs, all across a Fano atom, all in one class; silent with no handle between (1,354 of 1,354) |
| 5 | The source rule | 110 of 110 spaces without a non-Fano brace; the plain block count 83 |

**Solutions enumerated two ways.** A first run enumerated all assignments by brute force (about five hours); this check enumerates
them by SAT (`sat_solutions`), whose output is identical. The two methods agree on 665 of 665 removals of ticket B's spaces. Both runs
gave the same numbers in every section the change of method touches.

## What this does not establish

- **Proofs.** All of this is computed; only ticket A's lemma for atoms attached at a line is proved.
- **Larger spaces.** Nothing beyond 26 points.
- **Non-Fano handles.** Census 58 and the trisum brace are not covered by the rules or the rule.
- **Why the source rule works.** Ticket B gives the reason on the rules it found; a proof would need the rules themselves.

## Novelty

New here: the test of the brace dictionary and of the source rule on fresh spaces, the zigzag places, and the relay of creation between
glue pieces through a Fano atom.
