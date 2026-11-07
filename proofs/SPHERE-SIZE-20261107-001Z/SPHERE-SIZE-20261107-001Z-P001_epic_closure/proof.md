# Closure of the sphere-size epic

Status: Proved

Ticket `SPHERE-SIZE-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SPHERE-SIZE-20261107-001/sphere_size.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Islands keep the count hard: fixing any packing of small islands (pairwise >= 17 apart, away from the corners) to constant labels leaves a formula that still needs resolution width Omega(k). | new as far as found; proved | A |
| 2 | The sphere's count needs resolution size 2^Theta(sqrt n): random island packings kill every wide clause of a small refutation, leaving a narrow refutation of a restricted formula. | new as far as found; proved (constants tiny) | B |
| 3 | Grid Sperner, and Itsykson et al.'s Sperner CSP, need size 2^Omega(m) in general resolution. | sketch | B |

## Answer

- **Settled.** Resolution size of the sphere's count is 2^Theta(sqrt n). Together with Sherali-Adams level 3, the knot's sphere
  separates Sherali-Adams from resolution, as the mutilated chessboard does.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions** (2/3 for (a)):
- **(a)** A self-contained note on the width and size proofs, closing the sketched lemmas.
- **(b)** Cutting planes and Res(xor) on the sphere's count (1/3).

The table is in the decision note.
