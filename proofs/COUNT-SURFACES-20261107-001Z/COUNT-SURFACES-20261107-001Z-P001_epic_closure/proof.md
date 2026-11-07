# Closure of the knot's count on surfaces

Status: Proved

Ticket `COUNT-SURFACES-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/COUNT-SURFACES-20261107-001/count_surfaces.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On a closed surface each face's agreement parity is fixed by the signs. The even faces D satisfy \|D\| ≡ χ, and each D carries 2^(2 − χ) sign classes, so Kasteleyn signs exist iff χ is even. | known-with-delta; proved | A |
| 2 | Violated lines − Σ⌊agree/2⌋ = (χ − \|D\|)/2. The count forces a violated line only on the Kasteleyn sphere, and over-agreeing faces when χ < \|D\|. Wherever it forces it is in PPADS^dt, orientation-blind, and never PPA^dt-hard. | new as far as found; proved | A |
| 3 | When χ = \|D\|, satisfying assignments are, two to one, the perfect matchings of lines with faces off D in the one homology class the signs prescribe. | new for these constraints; proved | A |
| 4 | Lattice tori: a class is satisfiable iff the slope triangle has an integer point of matching parity. The unsatisfiable classes are exactly the degenerate tori, thin tori of even index, and the two Fano tori. Thin tori are cyclic chains (FP^dt). | criterion known-with-delta; classification new as far as found; proved | A |
| 5 | Simple lattice Klein bottles, hexagonal projective planes and genus-2 covers are satisfiable in every tested class. | computation | A |

## Answer

- **χ decides whether and where the count forces:** lines on the Kasteleyn sphere, faces when χ < \|D\|.
- **Orientability never enters.** Where the count forces, it stays in PPADS^dt.
- **Off the sphere,** the lattice knot spaces are satisfiable except thin and Fano tori. The TFNP class of the knot's own contradiction
  is a property of the sphere.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions:**
- **(i)** Negative curvature's count: is finding an over-agreeing face on Kasteleyn spaces of genus ≥ 2 PPADS-complete (2/3)?
- **(ii)** A return to question 9, whose choice is yours: uniform laws of lines and co-lines that build their own closed surface, and
  whether the count forces the knot's contradiction on them (2/3).

The table is in the decision note.
