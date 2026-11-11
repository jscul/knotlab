# Closure of the corner's row of the block inverse

Status: Proved

Ticket `CORNER-ROW-20261110-001Z`, 2026-11-11.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/CORNER-ROW-20261110-001/corner_row.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A partial rule only: rules in the frozen alphabet for the six entries next to the corners, all known or derivable before registration, and none found for the other 2(n − 1) − 6 entries, so no closed form for the corner row. The training verdict, committed before side 64, said "no pattern"; corrected. | the frozen outcome | A (checks 5, 6) |
| 2 | The row's denominators are supported exactly on the classes a ∈ GF(2n)* with Kloosterman sum K(a) ≠ 0, and every such class appears; that only these classes occur follows from the spectrum of A² on the v contacts. | new as far as found (that every class appears); computed, exact, 4 to 64, side 64 held out | A (checks 4, 8) |
| 3 | Every reduced denominator is a perfect square, and a class's largest exponent over the row is 2⌈\|K(a)\|/8⌉, not the spectrum's \|K(a)\|/2. | new as far as found; computed, exact, 4 to 64, side 64 held out | A (checks 4, 8) |
| 4 | Along each wall the entries have linear complexity exactly n/2 over GF(2)(s), the generic value. | computed, exact (Hankel certificate), 4 to 64 | A (check 7) |
| 5 | The corner row of K_n^(−1) is the walk series from the corner to the v contacts of the two side walls. | proved | A (Proposition 1) |
| 6 | Ticket B, conditional on a full rule, is retired without work, and the corner line is parked at side 64 by its frozen stop. | the gap | A, B |

## Answer

The corner row has no closed form of the kind looked for: rules were found only next to the corners, for entries known before
registration. Its denominators sit, exactly and held out at 64, on the Kloosterman classes of GF(2n), as squares with exponents
2⌈|K|/8⌉.

## Recommendation

**Full pivot**, no next action selected: the corner line is parked by its frozen stop, and the coordinator picks the next line. The
table is in the decision note.
