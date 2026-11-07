# Closure of the acts-as-one epic

Status: Proved

Ticket `ATOM-ONE-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/ATOM-ONE-20261107-001/atom_one.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every Fano atom of a knot space, with its closed sides, is the Fano plane up to flips. Of the 256 signed Fano planes only the plain one is a knot. | new; proved (exhaustive), on the project's cut theorem | A |
| 2 | A Fano atom with any one line removed sends the free relation through each of its cuts. | new; proved (91 of 91) | A |
| 3 | Without the knot, invariance holds for every relation only with at most one line-type cut. With more, 209 of 1,609 (configuration, cut) pairs are invariant. | new; proved (exhaustive) | A |
| 4 | Deep points of a removal's side, even paired with deep points behind the atom's other elements, never change creation at a Fano atom's line. They add far sides only at a receiving atom's cut lines with a six-pattern port relation. | new; proved (5,880 cases) | B |
| 5 | A free relation passes through a closed Fano atom unchanged. | new; proved (182 of 182) | B |
| 6 | A Fano atom acts as one: for creation in every knot space, and far side by far side except at that place. On Fano trees it holds without exception. | new; proved (corollary) | B |
| 7 | Deep points behind a receiving atom's own other elements could add creation (56 of 980 abstract cases), so bounding cannot show the closed verdict is exact. | new; proved (exhaustive) | B |
| 8 | On 191 saved and 86 fresh spaces, every Fano atom's line receives exactly its closed verdict, at 154,165 of 154,165 pairs. The exception occurs at 1,325 receiving cuts and adds nothing. | new; computed (predictions written first) | C |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
  - Whether to publish the recent epics to knotlab and jscul.dev.

## Recommendation

**Continue** (2/3): prove the genus reading on Fano trees.
- **The aim.** Show that FAR-READ B's rule returns exactly the Fano atoms of every Fano tree.
- **What remains.** That no atom splits into two parts acting as one, and that the twin steps pick out the atoms.
- **Then.** Plane glue.
- **Alternatives.** Whether junction handles act as one (2/3); a proof of the exception (1/3).

The table is in the decision note.
