# The law's count of missing knots: pre-registration

Epic `MISSING-KNOTS-20261112-001` (`RANDOM-FATES-20261112-001` direction 2; G17, with G1), 2026-11-12, at the coordinator's
go-ahead. Frozen before the registered run. The canonical K1–K3 test is unchanged. Words as in the guide's glossary and
`RANDOM-FATES-20261112-001` (newest-w growth, least bond L, a stretch).

## The question

Along newest-four growth the least bond containing two distinctions grows linearly with their distance in order of arrival, at a
rate that falls with the closing rate (`RANDOM-FATES-20261112-001C`, frozen and refereed). After that run its referee found that one
count fits at every closing rate: M, the knots missing from the windows of four consecutive distinctions between the pair, with
about 0.10 to 0.12 bond members per missing knot. Is that a unit of the patterns (the same however they are made), or a fit of one
process?

## Design (frozen; `census.py`)

- **Bases** (800 distinctions, 10 each, fresh seeds): newest-four growth at q = 0, 0.1, 0.3, 0.5, 0.7, 0.9; and a second process,
  the **Bernoulli band**: each of the knots within four consecutive distinctions present independently with probability p, at
  p = 0.5, 0.6, 0.7, 0.8, 0.9.
- **Pairs.** Between cells: 8 pairs per gap g in {16, 32, 64, 128, 256} per base (gap jittered by 0 to 3). Within a base: the
  eleven non-overlapping stretches of 64 from distinction 40.
- **Counts.** M (missing knots summed over windows, so a knot of span 2 can count twice), and the competitors D (distinct missing
  knots), M3 and M4 (distinct missing knots of span 2 and of span 3), W2 (windows with at least two missing), and the gap.
- **L** exact by `RANDOM-FATES-20261112-001C`'s programme; the share of pairs with a bond reported per cell.

## Predictions (frozen)

The advisor model reviewed a draft cold. It judged M1 a replication (within one process M is nearly proportional to the gap, so
the slope on M is the slope on the gap rescaled), expected M2 to fail at high p from the pilot, warned that M double-counts and
that conditioning on pairs with a bond selects low-M stretches, and proposed the within-base test M3 and the rival to M2.

| # | Prediction | Fails when |
| --- | --- | --- |
| M1 | **Replication.** On fresh newest-four bases the slope of L on M (defined pairs) lies in [0.09, 0.13] at every q, with pooled R² at least 0.95. | any q outside, or R² below |
| M2 | **The unit is the pattern's.** On the Bernoulli band the slope of L on M lies in [0.09, 0.13] at every p. | any p outside |
| M2r | **Rival (registered against M2).** The slope at p = 0.9 is at most 0.8 times the slope at p = 0.5 (missing knots cost more where they are isolated). | above 0.8 |
| M3 | **Within a base, the same unit.** In every cell where at least five bases have at least six stretches with a bond, the median over bases of the slope of L on M across the base's stretches of 64 lies in [0.09, 0.13]. | any eligible cell outside |
| M4 | Reported only: which count (M, D, M3, M4, W2) gives slopes with the smallest coefficient of variation across cells with at least half the pairs defined. | — |

## Pilot (disclosed)

One base each with seed 4242 (scratchpad): newest-four (0.5) slope 0.119; Bernoulli band 0.114 (p = 0.5), 0.107 (0.7), 0.086
(0.85), and at p = 0.3 almost no pair with a bond. The referee's fit of `RANDOM-FATES-20261112-001C` is the source of M. A smoke test
of the frozen code read one base each of newest-four (0.5) and the Bernoulli band (0.7), registered seeds, base 0.

## Stop rule and runtime

One run, its summary, a hand-off to the referee thread, report. About fifteen minutes on six workers.
