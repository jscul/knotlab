# Closure of the pinwheel-native epic

Status: Proved

Ticket `PINWHEEL-NATIVE-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PINWHEEL-NATIVE-20261107-001/pinwheel_native.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Label each boundary segment of the pinwheel's level-k patch by its two tiles' side types, its interval along them and their relative direction. Only eleven labels occur (eight inside, three on the boundary). A finite table on these labels, with handedness χ·(−1, −1, 1, 1, −1) for the five children and five fixed inside segments per tile, maps the labelled tile structure of level k to that of level k + 1, for every k. | known in substance (collared tiles, Anderson–Putnam complexes); this explicit rule new as far as found; proved, and checked exactly at levels 0–7 | A |
| 2 | Every interior segment of a pinwheel tiling is a whole hypotenuse, long leg or short leg against the same kind of side, or half a long leg against a short leg or another half. The only T-junctions are at midpoints of long legs. | elementary; proved | A |
| 3 | The vertex graph of the pinwheel patch with a vertex at infinity is 3-connected at levels 2–5. At levels 5–7, each interior segment's oriented label is determined by the unlabelled rooted neighbourhood of radius 2 of the plane graph (no conflict among up to 235,394 darts), while permuted and non-local labellings conflict. | exploratory experiment | B |

## Answer

- **Grown with nothing drawn.** The pinwheel's parity law grows by a finite local rule: split every knot into five, read each
  distinction's kind within radius 2, and split it by an eleven-label table. On the tested patches the rule reads only the law.
- **What it grows.** Its result is the law whose circle is round.

## Pending the owner

- **Carried.** Whether a native knot must also be natively bound (`LOGIC-AXIS-20261107-001`).
- **Carried from earlier epics.**
  - PHASE-HALO and FACE-CLAIM qualifications.
  - The SELECTION-NOTE erratum.
  - Superseding KNOT-COMPOSE D001.
  - Counted length as a native magnitude.

## Recommendation

**Continue**, as a fresh epic: a round plane grown at its open ends, starting with atlas growth.
- **Ratings.** Payoff 3/3 — Barrier · Concreteness 2/3 — Testable.
- **The question.** From one knot, add knots only where every nearby distinction keeps a radius-2 neighbourhood of the pinwheel
  atlas. Does growth reach dead ends, and do the grown patches stay pinwheel patches?
- **Alternatives.** Prove radius 2 for every pinwheel tiling (Payoff 1/3 · Concreteness 3/3); the spectrum of rational π among
  periodic laws (Payoff 1/3 · Concreteness 3/3).

The table is in the decision note.
