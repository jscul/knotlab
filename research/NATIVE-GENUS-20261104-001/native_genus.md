# A native reading of genus

Epic `NATIVE-GENUS-20261104-001` (program topology), 2026-11-04.

## The question

- **The approval.** The owner said "Yes, let's continue investigating." to RELAY-NET-20261104-001's recommendation.
- **What it asked.**
  - Build spaces with several Fano atoms in plane glue, joined by wires and liquid regions.
  - Ask whether the creation map over all removals splits into one halo per atom, so that it counts the handles and locates them.
  - Ask whether wires that carry one atom's halo into another's region blur the count.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The splitting lemma.** Whether a removal creates at a gluing line depends only on the atoms holding the two lines; every other atom acts as the vertex it replaced. | proved for atoms attached at a point; checked exactly for atoms attached at a line (13 designs, 5,130 entries) | A |
| 2 | **One halo per atom.** Each removal's halo is its own atom's halo, as if that atom were alone. On plane glue, atoms attached at a line have no halo. | corollary of 1; exact | A |
| 3 | **The native count.** The lines outside a largest creation-free set fall into one piece per atom when plane glue separates the atoms (through interior points), and each piece is an atom. | computation, fixed in advance: 416 of 420 separated spaces | B |
| 4 | **Its limits.** Touching atoms merge; three atoms on the 4-point cube merge; through shared points, atoms meeting at a glue point merge; through interior points, some census-58 atoms split. | computation | B |
| 5 | **The census.** On the 32 three-fold spaces up to 22 points, where atoms mostly touch, the count equals the genus in 10. It counts Fano atoms, not the trisum handle. | computation | B |
| 6 | **Blocks.** Maximal blocks of mutual creation within each piece equal the genus in 29 of the 32 and in all 310 Fano pairs. They overcount where two point-attached atoms hang from one Fano atom, and census 58 breaks into many blocks. | exploratory computation | B |
| 7 | **Wires.** A rigid strip or a hub lands one atom's halo on a second atom's cut lines in every placement tested. The count stays one piece per atom, and each halo stays its atom's. | computation: exact on a 26-point strip network (13 placements), each atom alone at a hub (24) | C |

## Answer

- **Does the creation map split into one halo per atom?** Yes, exactly, row by row: a removal's halo is its own atom's. Two atoms meet in the
  map only in entries where one holds the removal and the other the gluing line.
- **Does it count and locate the handles?** Yes, wherever plane glue separates them: the creative lines are the atoms' lines, and their
  pieces are the atoms. Handles that touch merge into one piece.
- **Do wires blur the count?** No.
  - **Overlap is real.** They do land one atom's halo on another atom's cut lines, in every placement tested.
  - **The count reads neither halo.** It uses the quiet glue and the lines the glue creates at, and a halo changes neither.
  - **Attribution survives.** Each halo line belongs to removals of one atom, and each removal lies in one piece.

## Reading

- **Native selection detects non-planarity locally.** Plane glue never creates, and the glue creates at every Fano line. So native
  selection marks exactly the handles, and the splitting lemma keeps them apart.
- **It counts Fano atoms.** The genus counts handles of any kind. The count reads Fano atoms only: the trisum handle of one census class is
  invisible to it.
- **Touching is resolved one level down.** Inside a piece, blocks of mutual creation still separate most touching Fano atoms. That points
  to a native reading of the whole brace decomposition:
  - quiet lines for plane glue;
  - blocks for Fano atoms;
  - one-way creation for the direction of a cut;
  - mutual silence for doubled squares, as inside census 58.
- **Doctrine.**
  - The count is a property of native creation, not of an embedding or a picture.
  - Steps and pieces describe placements only; no distance or metric is introduced.

## Literature

- **Ours.** The interface and screening lemmas (HANDLE-LOCALITY A, B), the reduction lemma (STRIP-RELAY A), relays (STRIP-RELAY C,
  RELAY-NET), genus = number of Fano atoms (THREEFOLD-SURFACES A, B), and the census of three-fold spaces (THREEFOLD-GRAMMAR B).
- **Classical.**
  - Splitting along one-bit separations (2-sums).
  - Tight-cut decompositions into bricks and braces (Lovász).
  - Minimum genus by SAT (Beyer, Chimani, Hedtke and Kotrbčík).
- **New here.** The splitting lemma for several atoms, the native count and its exhaustive small tests, the census comparison, blocks of
  mutual creation, and wires against the count.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — a native reading of genus | **Status:** Successful | **Found.** The creation map splits by atom (proved for atoms at points). The native count counts and locates handles that plane glue separates (416 of 420). Wires do not blur it. **Limits.** Touching atoms merge, the census matches in 10 of 32, and the count reads Fano atoms, not the trisum handle. **Refuted predictions.** Three atoms on the 4-point cube merge; census-58 atoms can split through interior points. |
| Local direction — counting creative pieces | Practically complete | **What is left.** Proofs of its computed premises (plane glue never creates; the glue creates at every Fano line), and spaces beyond 26 points. |
| Broader exploration — reading the brace decomposition natively | Opened | **Leads.** Blocks of mutual creation (29 of 32 census classes), one-way creation across a cut, and mutual silence inside doubled squares. **Unassessed.** Other non-planar braces, such as the trisum. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native selection counts and locates handles, with no embedding, wherever plane glue separates them. **The missing bridge.** Handles that touch, and handles that are not Fano atoms. |
| Next recommendation — a native reading of the brace tree | **Next step:** Continue. Fix a refined block statistic in advance, for instance the fewest blocks of mutual creation covering a piece, with silent pairs merged. Test whether blocks, one-way creation and silence recover the tight-cut decomposition on the census and on fresh, larger trees of atoms, and try to prove the block lemma for Fano atoms. | **If yes.** Native selection reads the genus even where handles touch. **If no.** The obstruction shows what creation cannot separate. **Alternatives.** Proving that plane glue never creates (2/3); the display rule (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Exploratory blocks match the genus on 29 of 32 census classes and in all 310 Fano pairs. **Main uncertainty.** The plain block count overcounts atoms hanging from one Fano atom and fragments census 58, so a correct refinement may not exist. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The 32 census classes and fresh trees of three or four atoms, exact up to about 26 points. **Stop when** a block statistic fixed in advance is decided on the census and the fresh families. |
