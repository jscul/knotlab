# Closure of which knot laws on the weave give a ruler from their counts

Status: Proved

Ticket `WEAVE-LAWS-20261117-001Z`, 2026-11-17. A ledger; it makes no new claim. The decision note is
`research/WEAVE-LAWS-20261117-001/weave_laws.md`. Referee pending.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Only the not-all-equal class of three-place knots (one complementary pair excluded) has Fourier degree at most two, so only its bases are carried by pair counts. | elementary | A, proved; B census |
| 2 | On the weave, NAE and agreeing-sign NAE laws are gauge copies of the triangular antiferromagnet (critical); the four disagreeing-sign laws tested are frozen. | classical applied (L2); computed | A, B (P1, P6; P2 failed at width 9 by a torus sector) |
| 3 | OR and not-exactly-two (hard hexagons at activity one) are disordered on the weave (gaps 1.12 and 0.86 per row; 1.39549 per distinction), and their pair counts do not determine their bases (first collisions at n = 6 and 5). | known (hard hexagons); computed | A (L3), B (P3, P4, P8) |
| 4 | Parity and two distance-two orientations freeze the weave; the third distance-two orientation is unclassified. | proved (parity); computed | A, B |

**Recommendation:** Research directions; the first (non-uniform pairwise arrangements on the weave) starts on the coordinator's go-ahead.

## After the referee (R1, 17 November 2026)

Confirmed with fixes, no Block; folded in the same day and logged in `docs/CORRECTIONS.md`. The rows above are kept as written.
- **Narrowing** of row 2. It holds for every law with one not-all-equal-class knot on all up knots and one on all down knots (all
  16). The referee's probes find a sparse signed mix and a 2 × 2 periodic law that look disordered.
- **Narrowing** of row 3. Those rulers step outward only in envelope: the gap's mode oscillates with period three.
- **Not a block.** Row 2's frozen laws rest on the exact cycle test: spectral radius 1, or 2 on two rows for NAE up with place 1
  odd down. Row 1's count of pairwise knots is 4. Also corrected: P2's twist is at every odd width, L2's wording, the docstrings,
  and the amendment's time.
