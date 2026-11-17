# Closure of mixed not-all-equal arrangements on the weave

Status: Proved

Ticket `WEAVE-MIX-20261117-001Z`, 2026-11-17. A ledger; it makes no new claim. The decision note is
`research/WEAVE-MIX-20261117-001/weave_mix.md`. Refereed (R1, confirmed with fixes; see the last section).

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Each not-all-equal-class knot breaks exactly one bond in its own signs; states up to the flip are perfect matchings with the inconsistent bonds subdivided; per cell 2 = 2u + i; the matching graph is bipartite iff every distinction meets an even number of inconsistent bonds. | classical applied (dimers); local | A (N1-N4, proved) |
| 2 | More than two inconsistent bonds per cell empties the base (29 of 29). | proved (N3); computed | A, B (Q2) |
| 3 | The frozen classification is unreliable: arrangements with the same inconsistent bonds differ by the twist around the cylinder, and it compared widths of opposite parity (Q0, Q1, Q3, Q5 failed). | computed | B |
| 4 | Post hoc (labelled), comparing widths of the same parity: four arrangements with odd counts look disordered (two 3 x 1 gauge copies with stable gaps and decaying correlations; two 2 x 2), none with all counts even; the referee's 2 x 2 law is unresolved. | computed, post hoc | B (readout.py) |

**Recommendation:** Research directions; the first (settle the candidates with the twist set explicitly) starts on the coordinator's go-ahead.

## After the referee (R1, 17 November 2026)

Confirmed with fixes, no Block; folded in the same day and logged in `docs/CORRECTIONS.md`. The rows above are kept as written.
- **Narrowing** of row 4. The two 2 × 2 survivors are decoupled (bands of two rows; strips of two columns), so one candidate pair
  remains: the two 3 × 1 arrangements, which are not gauge copies and are gapped one size past (widths 15 and 18).
- **Not a block** on row 3. Part of Q0's failure is a doubly degenerate top eigenvalue split by the 10⁻⁹ threshold, not the twist.
