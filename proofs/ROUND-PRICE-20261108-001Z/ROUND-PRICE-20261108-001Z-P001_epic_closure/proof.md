# Closure of the price of roundness in the plane

Status: Proved

Ticket `ROUND-PRICE-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/ROUND-PRICE-20261108-001/round_price.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Hidden labels that are functions of a bounded window of the pinwheel tiling never force aperiodicity: the cut rhombus crystal, labelled by the same function, obeys their law at every radius. | known-with-delta (the standard reason matching rules need decorations); proved | A |
| 2 | For decorated substitutions (a child's label fixed by its parent's label and child index), a crystal admitted by the collar law is admitted by the law of every radius after more cuts. | known-with-delta; proved | A |
| 3 | Of the 1,024 decorated substitutions on two labels, 1,006 admit the cut rhombus or brick crystal with a periodic labelling (172, 792 and 30 first admit the rhombus crystal after one, two and three cuts; 4 after four; 8 admit the brick crystal); 18 exclude both crystals at every level tested. | no-overlap-found; proved (exact census) | A |
| 4 | For those 18, every parent's label is forced, so the decoration would force the pinwheel if every surviving labelled parent collar obeyed the law; pairwise consistency leaves parent collars outside the law for each, and 2 of the 18 admit a brick-row crystal with period-4 diagonals after three cuts. Sixteen remain open. | no-overlap-found; proved (exact computation) | B |

## Answer

Roundness in the plane costs hidden information that no bounded window of the tiling determines. One bit per tile, placed by a
decorated substitution, fails in 1,008 of 1,024 cases; in the other 16 it already forces every parent's label, and whether it forces
the pinwheel is open.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with settling the sixteen (G1): radius-2 joint consistency on each candidate's surviving parent collars, then a search for
a periodic plane built from them. Rated Payoff 2/3 (Substantial), Concreteness 2/3 (Testable), awaiting the coordinator's go-ahead.
The table is in the decision note.
