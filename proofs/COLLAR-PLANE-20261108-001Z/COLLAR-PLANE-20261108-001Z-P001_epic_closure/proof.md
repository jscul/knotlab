# Closure of the collar law off the pinwheel

Status: Proved

Ticket `COLLAR-PLANE-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/COLLAR-PLANE-20261108-001/collar_plane.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The lattice tiling by the rhombus that four 1:2 right triangles make around a common right angle, cut once by Conway's cut, is a periodic tiling (20 tiles per period) in which every collar is a collar of a pinwheel tiling. | no-overlap-found; proved (exact witness) | A |
| 2 | The cut keeps collar-legality, and after enough cuts every patch of any fixed radius of a collar-legal tiling is a pinwheel patch; so for every r a periodic tiling obeys the pinwheel's undecorated radius-r law, and the pinwheel has no undecorated local rules. The twice-cut lattice obeys the 1,168-form radius-2 atlas; the three-times-cut lattice obeys the radius-3 atlas. | known-with-delta (the method is the standard way local rules fail; Radin 1994 and Goodman-Strauss 1998 decorate); proved; radius 3 by stress test | A |
| 3 | In every collar-legal tiling each collar names its tile's parent and touching siblings agree, so the tiling is the cut of a tiling whose collars lie in a level-one law of 1,264 collars per handedness (54 pinwheel keys); 156 survive arc consistency, and the rhombus lattice's collar is one of them. | known-with-delta (recognizability, Solomyak 1998); proved | B |
| 4 | The four collar-legal patches on which outward growth left the pinwheel compose once with no conflict; their defect is one level up, in 45 non-key level-one collars. | proved (finite computation) | B |
| 5 | Of the periodic planes rejected uncut by `PINWHEEL-ATLAS-20261107-001B`, cut one to three times, only the rhombus lattice obeys the collar law after one cut; six brick-row planes and 16 more domino tilings join after two cuts; the larger tori after one cut are pending. | exploratory experiment | C |

## Answer

A periodic plane obeys the pinwheel's collar law, and its further cuts obey every larger radius, so no undecorated local law of the
pinwheel forces aperiodicity or roundness. The collar law forces one level of the pinwheel's hierarchy and no more.

## Corrections

Two earlier readings are narrowed (logged in `docs/CORRECTIONS.md`): `GROWTH-LAW-20261107-001`'s use of Dworkin and Shieh for the
collar law's dead ends, and `PINWHEEL-ATLAS-20261107-001`'s reading that the plane may need no hidden information.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with the price of roundness in the plane (G1): label each tile with its child index and test whether the labelled
collar law forces composition at two levels, then count the hidden bits that force the pinwheel. Rated Payoff 2/3 (Substantial),
Concreteness 1/3 (Stated), awaiting the coordinator's go-ahead. The table is in the decision note.
