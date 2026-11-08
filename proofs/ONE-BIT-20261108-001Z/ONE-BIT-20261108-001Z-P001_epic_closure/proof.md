# Closure of one hidden bit per tile

Status: Proved

Ticket `ONE-BIT-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/ONE-BIT-20261108-001/one_bit.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The joint (radius-2) consistency test is sound for forcing, and on the eight one-bit decorations left open by `ROUND-PRICE-20261108-001` it leaves off-law labelled parent collars for each, so none is settled by it. | known-with-delta (local consistency); proved | A |
| 2 | Of the 96,416 domino tilings of tori up to 4 × 4 with diagonals, 32 are collar-legal after one cut and 176 after two; a mixed 4 × 4 tiling legal after two cuts, with a variant, admits seven of the eight decorations with periodic labellings, so one bit per tile as a decorated substitution fails in 1,022 of 1,024 cases. | no-overlap-found; exploratory experiment | B |
| 3 | The decoration s(0) = 10101, s(1) = 00110 (with its relabelling) excludes every crystal tried, has forced parent labels, and is open. | no-overlap-found; proved and exploratory | A, B |
| 4 | A five-page note, "The pinwheel tilings have no undecorated local rules", with an independent replay. | result conversion | C |

## Answer

One bit per tile, placed by a decorated substitution, lets a periodic plane through in 1,022 of 1,024 cases. One decoration up to
relabelling resists every crystal tried, and whether it forces the pinwheel is open.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with the last one-bit decoration (G1): crystals legal after two or three cuts on larger tori and mixed shapes, then a
forcing test on the undecorated geometry alone. Rated Payoff 2/3 (Substantial), Concreteness 2/3 (Testable), awaiting the
coordinator's go-ahead. The table is in the decision note.
