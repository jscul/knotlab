# Frozen predictions on larger trisum spaces

Status: Proved (exact computation on the ten larger edge-atom trisum spaces, every map computed after the predictions were frozen)

Ticket `TRISUM-READ-20261107-001B`, 2026-11-07.

## Question

- **What ticket A found.** On seven small spaces, native creation reads the atoms, the junctions and the leaves. Before any map of the
  ten larger spaces existed, ticket A froze seven statements, P1 to P7, in `predictions.json` (17:20:41 PST).
- **The test.** Do they hold one size past training? The larger spaces have up to three junctions, and in some of them a junction line
  or a junction point carries an atom.

## Dependencies

- **`TRISUM-READ-20261107-001A`.** The library (`tr_lib.py`), the frozen predictions, the spaces (`spaces.json`) and the training
  maps, all bound by hash.
- **`REFINE-READ-20261107-001A`.** Pair refinement on the native map.
- **The engine.** CHAIN-TRANSFER A and B's exact rows: every solution, and the two-round rule at every gluing line.

## The spaces and their maps

- **Ten spaces**, 54 to 60 points, six atoms each:
  - one junction in six of them (seeds 240, 354, 96, 288, 282, 384);
  - two in seeds 34 and 46, and three in seeds 5 and 11;
  - a junction line carries an atom in seeds 240 and 5, and a junction point carries one in seed 11.
- **568 rows**, computed in three runs after the freeze (`provenance.json`).
  - **The first two maps** used ticket A's `tr_lib.exact_row`.
  - **The other eight** used `map_lib.exact_row`. It enumerates the same solutions in bounded memory, about 0.7 GB per worker on the
    largest space instead of 3.5 GB.
  - **Check 2** recomputes three rows of every space with both enumerators. The rows equal the stored ones, and the two enumerators
    return the same solution arrays.

## Results

1. **The atoms (P1 same atom and roots, P3, P4) hold in all ten.**
2. **The junctions (P1 junction lines and square-mates, P2, P5, P6) hold in all ten.**
   - **Read and counted.** With the atoms set aside, the pairs of lines that block only each other are exactly the junctions' line
     pairs: one, two or three per space.
   - **With the atoms included,** every pinned pair is still a junction pair. A junction whose line carries an atom is not pinned, as
     in ticket A's seed 1: none of seed 240's one junction shows, and two of seed 5's three.
3. **The skeleton and the leaves (P1 skeleton lines, P7) hold in all ten.**
4. **One frozen sub-statement fails, in one space.** In seed 5 (three junctions), the lines that carry an atom are not a union of
   native diagonal classes. Pair refinement puts the loaded line 9 and the unloaded line 8, the two own lines of one cube piece, in one
   class.
5. **The failure is a symmetry, so no native procedure could do better (check 4).**
   - **The automorphism.** The permutation exchanging lines 8 and 9, 2 and 3, and 10 and 11, fixing every other line, preserves the
     order-free vector of every ordered pair. It is an automorphism of the native creation map.
   - **It fixes every atom line,** the lines of the atom hung on line 9 included. The space itself has no such symmetry, since it would
     have to move that atom.
   - **Where it comes from.** Exactly one automorphism of the skeleton induces it on the skeleton lines. That automorphism keeps the
     switching class of the signing whose incidences carry the atoms, and moves the atoms' places.
6. **Yes/no creation is native (check 5).** In all 17 maps (37,078 non-degenerate entries) census 6 never creates where none of the
   three order-free far sides does.
   So whether creation occurs equals creation by the order-free far sides, and the yes/no statements do not depend on how points are
   listed.

## Reading

- **The test passed where it was aimed.** One size past training, with up to three junctions, native creation reads the junctions,
  counts them, and fixes the atoms and the leaves.
- **What it cannot read.** It cannot always say on which incidence an atom sits. In seed 5 a symmetry of the glue keeps the signing's
  switching class while moving the atom, and the native map cannot tell the two places apart.
- **A conjecture, not tested here.** The native creation map may depend on the signing only through its switching class. Seed 5 is
  one instance. Comparing the maps of two placements in the same class would test it (parked: backlog of `docs/RESEARCH_GOALS.md`).
- **Doctrine.** The maps, the refinement and the symmetry are invariant under relabeling lines and re-listing their points.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; ticket A Proved | pass |
| 1 | The freeze: predictions, library and ten spaces bound by hash; every map finished after it | pass |
| 2 | Three rows per space, by both enumerators | 30 of 30 equal; same solution arrays |
| 3 | P1 to P7 on the ten spaces | as reported: one sub-statement fails, in seed 5 |
| 4 | The failure is a native symmetry | automorphism verified; induced by one skeleton automorphism that keeps the switching class |
| 5 | Census 6 never creates alone | 0 of 37,078 entries in 17 maps |

## What this does not establish

- **Larger spaces and other families.** The test reaches 60 points and three junctions.
- **The conjecture.** That the native map depends on the signing only through its switching class is seen in one space, not tested.
- **A proof of the junction signature.** It is measured, now on seventeen spaces, not derived.

## Novelty

- **New here.** The held-out test, and the native symmetry that hides where an atom sits.
- **Classical.** Switching classes of signed graphs (Zaslavsky), and trisums and trisectors (Robertson, Seymour and Thomas).
