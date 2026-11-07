# Closure of the count-note epic

Status: Proved

Ticket `COUNT-NOTE-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/COUNT-NOTE-20261107-001/count_note.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The knot sphere's count needs resolution width Θ(√n) and size 2^Θ(√n), now with every lemma proved: single-step vortex moves, straight cut systems with d ≥ (dist − 19)/2, a row count for the free component, islands, and a random restriction. | new as far as found; proved (two local lemmas decided exactly by computation) | A |
| 2 | Grid Sperner, and Itsykson et al.'s Sperner CSP, need resolution width Ω(m) and size 2^Ω(m). In the three-arc gauge the fixed boundary is flat. | new as far as found; proved (the size bound was a sketch) | A |
| 3 | The count has a degree-3 Sherali–Adams refutation with coefficients ±1, so finding a violated line is in PPADS^dt. | known-with-delta; proved (the placement by citation of Göös et al.) | B |
| 4 | Cutting-planes and XOR-reasoning solvers do no better than CDCL on K_2..K_7. | experiment | B |

## Answer

- **(a)** The self-contained note is written; no gap was found.
- **(b)** The count is placed in unary Sherali–Adams (PPADS^dt). Cutting planes and Res(⊕) remain open as proof systems.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions:**
- **(i)** The unary Nullstellensatz degree of the count. Low degree would put it in PPAD^dt; growing degree would make it a natural
  planar member of PPADS^dt outside PPAD^dt (2/3).
- **(ii)** A short cutting-planes refutation built from the line–face count (1/3).

The table is in the decision note.
