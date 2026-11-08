# Closure of the pinwheel-atlas epic

Status: Proved

Ticket `PINWHEEL-ATLAS-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PINWHEEL-ATLAS-20261107-001/pinwheel_atlas.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The collared tiles of all pinwheel patches form 193 keys closed under Conway's cut (108 complete, in 54 mirror pairs). Four cuts of each complete collar contain every radius-2 neighbourhood of its centre. So the radius-2 neighbourhoods of darts in every pinwheel tiling take exactly 1,168 forms, each with one oriented label: every edge's label is a function of the unlabelled planar map within radius 2. At radius 1 there are 198 forms, 9 with two labels; the level-7 patch already shows every form. | method known (collared tiles); the atlas and the readability theorem new as far as found; proved | A |
| 2 | No tested periodic plane has every radius-1 neighbourhood in the law: 96,474 configurations fail (rectangle grids and brick rows with diagonal patterns of period up to 2 × 2, all domino tilings of the 2×2 to 4×4 tori with all diagonal choices, the six two-tile shapes tiled by half-turns), and so does the frame-consistent cut. The pinwheel passes and the tetrakis triangulation fails. | not found in prior work (undecorated local rules: Levitov); exploratory experiment | B |
| 3 | In the bare growing patch T_k (levels 4–7), every dart's label, boundary included, is a function of its unlabelled radius-2 code, pooled over all levels (3,227 codes, no conflict). | exploratory experiment | D |
| — | Outward growth one tile at a time: not run, held as backlog at the owner's request. | retired | C |

## Answer

- **The law reads itself.** The pinwheel's radius-2 law is finite (1,168 forms) and determines every label. The regrowth rule runs on
  the bare map, inside by theorem and at the boundary on the levels tested.
- **The law is selective.** No tested periodic plane comes close: each fails at radius 1. Whether the law forces aperiodicity is
  open.

## Pending the owner

- **Carried.** Whether a native knot must also be natively bound (`LOGIC-AXIS-20261107-001`).
- **Carried from earlier epics.** The PHASE-HALO and FACE-CLAIM qualifications; the SELECTION-NOTE erratum; superseding
  KNOT-COMPOSE D001; counted length as a native magnitude.

## Recommendation

**Continue — No next action selected.** The lines are held at the owner's request to wrap up current work. The candidates, rated in
the decision note:
- does the undecorated law force aperiodicity (Payoff 2/3 · Concreteness 2/3);
- outward growth in every growth order (Payoff 2/3 · Concreteness 1/3);
- radius 2 at the boundary as a theorem (Payoff 1/3 · Concreteness 3/3).
