# The law's count of missing knots

Epic `MISSING-KNOTS-20261112-001` (`RANDOM-FATES-20261112-001` direction 2; G17, with G1), 2026-11-12, at the coordinator's
go-ahead. Pre-registered in commit 68f4ef038 before the registered run. The canonical K1–K3 test is unchanged. **Referee pending**
(handed to the referee thread).

## Words

As in the guide's glossary and `RANDOM-FATES-20261112-001`: newest-four growth, least bond L, a stretch (consecutive distinctions in
order of arrival). M counts, over the windows of four consecutive distinctions between a pair, the knots each window lacks; the
**Bernoulli band** has each knot within four consecutive distinctions present independently with probability p.

## The question

Along newest-four growth the least bond grows linearly with distance (`RANDOM-FATES-20261112-001C`), and after that run its referee
fitted about 0.10 to 0.12 bond members per missing knot at every closing rate. Is that a unit of the pattern, the same however the
pattern is made, or a fit of one process?

## The question in standard terms

For 3-uniform hypergraphs of bandwidth 3 under proper 2-colouring, does the least size of a minimal non-shattered set containing
two vertices depend, across generating processes, only on the number of absent edges between them?

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **On newest-four growth the unit replicates.** On fresh bases the slope of L on M is 0.115, 0.118, 0.114, 0.113, 0.109 and 0.098 at q = 0, 0.1, 0.3, 0.5, 0.7, 0.9, pooled R² 0.986. | computed, exact, frozen | M1 held |
| 2 | **It is not a fixed unit of the pattern.** On the Bernoulli band the slope falls with density: 0.112, 0.106, 0.098, 0.088 and 0.089 at p = 0.5 to 0.9, below the registered band at p = 0.8 and 0.9. The registered rival held, just: the slope at p = 0.9 is 0.795 of that at p = 0.5 (bound 0.8). Missing knots cost less where they are isolated among present ones. | computed, exact, frozen | M2 failed; M2r held |
| 3 | **Within one base, missing knots explain the bond only where closings are frequent.** Across a base's eleven stretches of 64, the median slope of L on M is 0.113 to 0.127 on newest-four growth at q = 0.3 to 0.9 and 0.082 to 0.138 on the band, but 0.056 at q = 0.1 and negative (−0.23) at q = 0: with few closings nearly every window lacks most knots, M hardly varies, and the bond is set by something else. | computed, exact, frozen | M3 failed |
| 4 | **M is still the steadiest count tried.** Its slopes vary by 9.6% across the cells with at least half the pairs bound, against 11% for distinct missing knots, 17% and 27% for missing knots of span 3 and span 2, and 22% for windows lacking two or more. | computed | M4 reported |
| 5 | **How often far distinctions share a bond** repeats `RANDOM-FATES-20261112-001C`: at 256 apart, 9% at q = 0 and 0.1, 24% at 0.3, 61% at 0.5, 94% at 0.7 and all at 0.9; on the band 15% at p = 0.5, 68% at 0.6, 86% at 0.7 and all at 0.8 and 0.9. | computed, exact | reported |

## Answer

Missing knots are the right thing to count, but not a fixed unit. Across two processes and eleven settings the least bond grows by
0.088 to 0.118 members per missing knot, the steadiest of the counts tried; it costs less where the missing knots are scattered
among present ones (the band at high density) and, where closings are rare, missing knots no longer predict the bond inside a base.

## Reading

**Interpretation, not a theorem.** What the law counts along the growth that never ends is close to its gaps, as
`RANDOM-FATES-20261112-001` read it, but the price of a gap depends on its neighbours: a gap surrounded by present knots costs less
than one among other gaps. The count is not "one per missing knot" in a fixed unit; it is a local cost that a finer count, of how
gaps cluster, might make exact.

## Lag cutoffs and census-only claims

Computed on 110 bases of 800 distinctions, gaps 16 to 256, members of a bond within 8 of the pair (the margin; `RANDOM-FATES-
20261112-001C`'s referee found no undefined pair change with members anywhere). No all-size claim.

## Review

Referee pending (the referee thread). The exact programme was refereed in `RANDOM-FATES-20261112-001C` (0 mismatches on 60,932
pairs against brute force).

## Literature and provenance

Not found (bounded search, `RANDOM-FATES-20261112-001`): least non-shattered sets through two vertices on bounded-bandwidth
patterns. The count M was found by `RANDOM-FATES-20261112-001C`'s referee after that run; this epic is its first frozen test.

## Workspace assumptions

A71 (each process one weighting of many) is used: the result changes with the process, as A71 allows.

## Ratio

Substantive: the census and its summary. Administrative: the pre-registration, this note, the closure.

## Corrections

None. (The exploratory unit was reported as exploratory; it is now narrowed by this test, not corrected.)

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a unit for the law's count | **Status:** Partially successful (referee pending) | Replicated on newest-four growth; not fixed across processes; fails within bases at low closing rates |
| Local direction — the count along newest-four growth | Continue | A cost per gap that depends on its neighbours is the next candidate |
| Broader exploration — G17 | Searching | The whole-life census (`LIFE-JUMPS-20261112-001`) runs beside it |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The law's count along the never-ending growth is close to a count of gaps |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G1); no goal change. **Assumptions:** A71 used.
**Basket:** `RANDOM-FATES-20261112-001#3` to `#5` stay open.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The cost of a gap from its neighbours | 2/3 — Substantial | 2/3 — Testable | Fit a cost per missing knot by how many of its window's other knots are missing, on half the bases, and test it frozen on the other half and on a third process → one cost table for every process, or none | Selected · awaiting go-ahead |
| 2 | Why low closing rates cut | 2/3 — Substantial | 2/3 — Testable | Characterize the ends of stretches no bond spans (the referee's two-knot link) and test a rule on fresh bases → a local rule, or none | Alternative · deferred |

1. Payoff 2: an exact unit would make the count along the never-ending growth a law's own number. Concreteness 2: the data are in
   hand; the cost table is not yet defined.
2. Payoff 2: the cuts are where the law refuses to count. Concreteness 2: one mechanism is recorded, not shown sufficient.

## Final report as sent

(Sent together with `LIFE-JUMPS-20261112-001`'s report; appended there.)
