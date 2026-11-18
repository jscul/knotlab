# Why do rings of five knots grow faster than any power under the cheapest counts? Pre-registration

Epic `RING-GROWTH-20261118-001` (the coordinator's go-ahead on `TOUCH-CENSUS-20261118-001#1`; goals G17, G2, G1), 2026-11-18.
Written after the ring of four four-place knots and one five-place knot had been grown (its recurrence c(t) = c(t − 5) + c(t − 6)
found by fitting, the advisor's model checked against it, and the referee's interim finding relayed), and before any other ring was
read. The canonical K1–K3 test is unchanged.

## What is frozen

The advisor's predictions for other rings ([answer](advisor/answer_1_fable.md)), scored by `ringcheck.py` in ticket B on rings grown
to 34 rounds or 15,000 junctions: a ring of period n, knots of four places except j extra open distinctions (a five-place knot adds
one, a six-place knot two), growing under the fewest counts.

| # | Ring (sizes in ring order) | Prediction | Fails when |
| --- | --- | --- | --- |
| R1 | 4,4,4,4,4,4,5 (n = 7, j = 1) | c(t) = c(t − 7) + c(t − 8) after a transient | the fitted minimal recurrence differs |
| R2 | 4,4,4,4,4,4,4,5 (n = 8, j = 1) | g = c − 4 satisfies g(t) = g(t − 4) + g(t − 5) | it does not |
| R3 | 4,4,4,5,5 and 4,4,5,4,5 (n = 5, j = 2) | c(t) = c(t − 5) + 2c(t − 6) + c(t − 7); rate ≈ 1.26 | either differs |
| R4 | 4,4,5,5,5 (n = 5, j = 3) | c(t) = c(t − 5) + 3c(t − 6) + 3c(t − 7) + c(t − 8); rate ≈ 1.38 | it differs |
| R5 | 4,4,4,4,6 (n = 5, j = 2 at one knot) | as R3 | it differs |
| — | 4,4,4,4,4,5 (n = 6), 4,4,4,5 (n = 4), 3,4,4,4,5 | no prediction (degenerate or unclean rings) | — |

A recurrence is "found" when Berlekamp–Massey on the counts from round 4 returns it with at least twice its order of terms to spare.
