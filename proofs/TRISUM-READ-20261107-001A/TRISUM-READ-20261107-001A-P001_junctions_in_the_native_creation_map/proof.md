# Junctions in the native creation map

Status: Proved (exact computation on the creation maps of the seven small edge-atom trisum spaces, with REFINE-READ's 277 spaces as a
control)

Ticket `TRISUM-READ-20261107-001A`, 2026-11-07.

## Question

- **What was known.** HANDLE-COUNT showed that on the knot's plain spaces the cost of counting sits at the glue's junctions, where
  planar pieces meet along squares, and that atoms pay for them. REFINE-READ showed that native creation fixes the atoms.
- **The question.** Does native creation also fix the junctions? With nothing drawn, can the creation map say which lines form a
  junction, and how many junctions there are?

## Dependencies

- **`REFINE-READ-20261107-001A`.** Pair refinement on the native creation map (`refine_lib.py`), and its 277 spaces, used here as a
  control.
- **`HANDLE-COUNT-20261106-001A`.** The trisum-brace family (`families.py`) and the junction count.
- **`GENUS-READ-20261107-001A`.** The order-free far sides (K4^(3), the Fano plane, census 58), which make the map native.
- **The engine.** CHAIN-TRANSFER B's exact rows (the two-round rule at every line) and SEYMOUR-COUNT B's trisectors and trisum tree.

## Setting

- **The spaces.**
  - **The generator** is HANDLE-COUNT A's: a trisum brace of cubes and prisms (one to three trisums), its Pfaffian signing made
    minimal in its switching class, and a Fano atom on every signed incidence ("edge atoms").
  - **Seeds 1 to 400** gave 17 spaces of at most 60 lines up to isomorphism, each represented by its smallest seed.
  - **The generator also depends on Python's hash seed.** Its Pfaffian signing walks sets, so the signing, and with it the places of
    the atoms, can change from run to run; a run over seeds 1 to 400 gives 17 or 18 classes. Each stored space is the generator's space
    at its own seed under a recorded hash seed, up to isomorphism, and the 17 are pairwise non-isomorphic (check 1).
  - **The training spaces** are the seven that cost at most 200,000 solutions with line 0 removed (1,500 to 112,500): 29 to 47 points,
    three to five atoms, one junction each except seed 1, which has two.
  - **The other ten** (54 to 60 points) belong to ticket B.
- **The canonical structure, read from the incidence graph** (check 2).
  - **Atoms** are the minimal sides of 2-edge cuts: 7 lines and 7 points each. An atom's root is its line on the cut. Its loaded line is
    the line on the cut's other edge.
  - **The skeleton** is what remains when every atom is contracted back to an edge: a cubic brace that is neither planar nor the
    Heawood graph.
  - **Junctions** are all the skeleton's trisectors: two points and two lines, pairwise non-adjacent, whose removal leaves at least three
    components. They are exactly the squares of the trisum tree. A junction's two lines are square-mates.
  - **Leaves** are the planar pieces left by splitting the skeleton at every trisector. An atom belongs to the leaf of its edge.
  - **None of this depends on labels.** Three random relabelings of lines and points per space change nothing.
- **The native creation map.** Each ordered pair of lines (a, b) carries the order-free vector of removing a and gluing at b. The pair is
  degenerate when b shows fewer than six patterns.
  - **Blocking.** a blocks b when removing a does not create at b (degenerate included).
  - **Yes/no creation** is the bare relation "removing a creates at b".
- **Exact maps.** A row enumerates every solution of the space minus one line and applies the two-round rule at every other line.
  `tr_lib.fast_masks` gets the near-side masks from one matrix product per pattern of the gluing line. Recomputed this way, all 293 rows
  equal the stored map. Row 0 of every space also equals CHAIN-TRANSFER B's own engine (check 3).

## Results

1. **Yes/no creation alone reads the atoms (P3, P4).**
   - **The cores.** The lines that no removal blocks are exactly the atom cores, the six lines of each atom other than its root.
   - **The roots.** Each root is created at by exactly six removals, all of them core lines, and those six are the rest of its atom. No
     other line is.
2. **With the atoms set aside, yes/no creation reads the junctions (P5).**
   - **The signature.** A junction's two lines are never degenerate at removals outside the atoms, and each is the only such removal that
     blocks the other.
   - **It is exact.** No other pair of lines outside the atoms has this property, so the junctions are read, and so is their number.
   - **Why the atoms must be set aside.** In seed 1 one junction line carries an atom, and removing a line of that atom makes the junction
     line degenerate. With atoms included, only its other junction shows as a pair that blocks only itself (P6).
3. **Pair refinement fixes the whole structure (P1, P7).** On the native map, "same atom", "square-mates" and "same leaf" are unions of
   stable pair classes. The skeleton lines, the junction lines, the roots and the loaded lines are unions of diagonal classes.
4. **Even colour refinement of yes/no creation separates the junction lines (P2).**
5. **The control (check 5).** Across REFINE-READ's 277 spaces, taking the atoms to be the lines of Heawood braces:
   - **One space has a pair pinned apart from its atoms.** It is design 7, the only one of the 277 whose glue holds a non-planar brace
     other than Heawood. The pair is the two lines of that brace's one trisector.
   - **No pair is pinned by yes/no creation alone**, and every line that no removal blocks is an atom line.

## Reading

- **A junction is a mutual block.** Its two lines depend on each other alone: any other removal outside the atoms creates at both, and
  removing either one silences only the other. Plane glue never shows this (276 of the 277 control spaces have no such pair). The one
  control space that does has a junction exactly there.
- **Both kinds of handle are native.** REFINE-READ read the atoms. This ticket reads the junctions, the handles HANDLE-COUNT found the
  counting cost to depend on. Both are read from creation alone, with nothing drawn.
- **Doctrine.** The maps, the refinements and the signatures are invariant under relabeling lines and re-listing their points.

## The freeze

Before any map of ticket B's ten spaces was computed (17:20:41 PST on 2026-11-07), P1 to P7 were written to `predictions.json`, with this
library bound by hash and the ten spaces by the hashes of their lines (check 6). Ticket B tests them.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The 17 spaces | each reproduced at its seed under a recorded hash seed; pairwise non-isomorphic |
| 2 | Canonical structure, under three relabelings per space | atoms, skeleton, junctions, leaves fixed |
| 3 | Training maps recomputed | 293 of 293 rows equal; row 0 equal by CHAIN-TRANSFER B |
| 4 | P1 to P7 on the seven training spaces | all hold |
| 5 | Control on REFINE-READ's 277 spaces | one pair pinned apart from atoms: design 7's trisector |
| 6 | The freeze | predictions, library and ten spaces bound by hash |

## What this does not establish

- **Larger spaces.** More junctions, and junctions carrying atoms in other places, are ticket B's.
- **A proof.** The signature is measured on seven spaces, not derived.
- **Other families.** HANDLE-COUNT's T14 decorations attach atoms by 3-edge cuts and are not used.

## Novelty

- **New here.** The junction signature and the measurements.
- **Classical.** Trisums and trisectors (Robertson, Seymour and Thomas), and the refinements and their logic (Weisfeiler and Leman; Cai,
  Fürer and Immerman).
