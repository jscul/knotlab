# Closure of the beyond-two-values epic

Status: Proved

Ticket `BEYOND-TWO-20261101-001Z`, 2026-11-01.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/BEYOND-TWO-20261101-001/beyond_two.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The known cycle-composing laws are coset laws with uniform fibres, so they count easily and none selects. | classical (cosets; Dyer–Richerby) | A |
| 2 | Blurring keeps failures and circuits, so cycle-like composition, and weights counts. | new as stated | B, item 1 |
| 3 | Every Mal'tsev law on three values composes like cycles (all 531441 operations). | new; from KNOT-CIRCUITS Theorem 1 | B, item 2 |
| 4 | Blurred parity (3 values) and blurred Z3 (4 values) compose like cycles, fail recognisably and count #P-complete: the formal bridge. | new | B, items 3–4 |
| 5 | The knot fails exactly on Pfaffian substrates, always globally; parity on those with an even number of perfect matchings, never globally; Z3 on all, globally exactly at corank 1. | new census; classical parts | C, items 1–3 |
| 6 | Blurred Z3 on corank-1 substrates selects in the knot's full sense and composes like cycles: a bridge at four values. | new | C, item 4 |
| 7 | Its selected spaces are rigid (only ties after removing a line); the knot's can keep a knot. | new | C, item 5 |

## Pending the owner

- **Still open.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): ask whether cycle-like composition forces rigid selection.
- **First test.** The remaining Theorem 1 laws: the coset laws of Z4, S3 and D_p, and the simple Mal'tsev laws on three values. Look for
  global failures and for knots that survive the removal of a line.
- **Then.** Try to prove rigidity for every Mal'tsev law.

The table is in the decision note.
