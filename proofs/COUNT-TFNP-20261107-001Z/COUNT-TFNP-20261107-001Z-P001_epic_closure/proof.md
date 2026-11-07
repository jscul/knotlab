# Closure of the knot's TFNP epic

Status: Proved

Ticket `COUNT-TFNP-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/COUNT-TFNP-20261107-001/count_tfnp.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | One-sided 2D grid Sperner is PPADS^dt-complete, and two-sided grid Sperner PPAD^dt-complete. Chen–Deng's planar uncrossing keeps every sink, source and orientation. | known-with-delta; proved | A |
| 2 | Finding a violated line of the octahedral knot sphere is PPADS^dt-complete. Finding a violated line or a monochromatic face is PPAD^dt-complete. | new as far as found; proved | B |
| 3 | The knot sphere's not-all-equal formula has no polylogarithmic-degree Nullstellensatz refutation over F2, nor a unary one, although unary Sherali–Adams refutes it at degree 3. Its count is not in PLS^dt. | new as far as found; proved (qualitative) | B |

## Answer

The count is in PPADS but not in PPAD (nor PPA or PLS) in the black-box world. Only the knot's orientation separates it from the
PPAD-complete two-sided count.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions:**
- **(i)** The knot's count on non-orientable and higher-genus knot spaces: whether the surface's Euler characteristic and orientability
  decide its class (2/3).
- **(ii)** A return to question 9, whose choice is yours.

The table is in the decision note.
