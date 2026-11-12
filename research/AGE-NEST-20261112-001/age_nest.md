# What the expanding growth's degrees do not carry

Epic `AGE-NEST-20261112-001` (`OLD-CORE-20261112-001` direction 1; G17, with G7), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in commit 283e418e9 before the registered run. The canonical K1–K3 test is unchanged. **Referee pending** (handed
to the referee thread).

## Words

As in `OLD-CORE-20261112-001`: the dying core, a knot's **youngest** distinction (its last to arrive), X(q) growth with closings
anywhere. A **prefix count** is the number of knots among the oldest j distinctions, for some j; keeping every knot's youngest
distinction keeps every prefix count.

## The question

Patterns with the X dying core's degrees never end (`OLD-CORE-20261112-001`). What does the core carry beyond its degrees that ends
it? The weighting is the process X(q) (A71).

## The question in standard terms

Along a ladder of resample ensembles of the first non-2-colourable prefix of a grown 3-uniform hypergraph, from degree-preserving to
history-preserving, which keep it non-2-colourable?

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The resamplers are fair.** Both chains are symmetric, and on five degree sequences, one regular and four uneven (17 to 16,534 patterns each), their exact transition matrices are connected within the classes they must keep: the degree chain on all patterns with those degrees, the age-keeping chain on each assignment of youngest distinctions. | computed, exact | fair |
| 2 | **Degrees miss it (replicated with a fair chain).** Patterns with the dying core's degrees, from a switch chain, end in a median of 0% of resamples at X(0.3) and X(0.35) (ninetieth percentile 5% and 30%), as `OLD-CORE-20261112-001`'s stub generator found. | computed, frozen | N1 held |
| 3 | **The nesting by age carries it.** Keeping the degrees and every knot's youngest distinction, and so every prefix count, the resamples end in a median of 40% (X(0.3)) and 50% (X(0.35)), above the degree-only share in 95% and 92% of the cores where the two differ. | computed, frozen | N2 held |
| 4 | **Degrees add nothing once the nesting is kept, and the schedule adds nothing to it.** Keeping only every knot's youngest distinction (degrees not kept) gives 40% and 55%; redrawing the whole core under the growth's own rule with its schedule gives 35% and 58%; each beats the nested-with-degrees rung in about half of the cores. No resample on any rung had the core's pair counts: every one is a different pattern from the law's point of view. | computed, frozen | N3 reported |
| 5 | **Control.** In the 104 cores holding a Pasch configuration, the trade kept every pair count and allowed no state, as the pair-count lemma says. | computed | Q0 held |
| 6 | **X(0.25)** (8 cores, reported only): the same order, weaker: degrees 0%, nested 15%, youngest only 12.5%, schedule 7.5%. | computed, frozen | reported |

## Answer

What ends growth with closings anywhere is how its knots nest in the order of arrival: how many knots lie among the oldest j
distinctions, for every j. Keep that, with or without the degrees, and about half of the redrawn cores still end, as many as when the
whole core is redrawn by the growth's own rule; keep the degrees and lose it, and none do. Degrees spread an old distinction's knots
to young partners; the nesting keeps the old distinctions knotted among themselves, and that is what makes them contradict each other.

## Reading

**Interpretation, not a theorem.**
- **The owner's "go for a while then die".** Under this weighting a pattern that keeps growing dies from its own past folding in on
  itself: the oldest part of it keeps gaining knots among its own members while the new arrivals stay loose. What the law cannot
  survive is a dense old core, and "old" is the right word here: it is the order of arrival, not the number of knots per distinction,
  that the end needs.
- **For the record's other results.** In growth along co-knotted pairs the degrees alone were enough (`OLD-CORE-20261112-001`); in
  growth with closings anywhere they are not, and the nesting is. The two processes end through different features of their history.

## Lag cutoffs and census-only claims

Computed on 183 dying cores of OLD-CORE's X endings (81 at X(0.3), 94 at X(0.35), 8 at X(0.25); its pilot's twelve held out), 20
resamples per rung. The fairness checks are exact for the five sequences enumerated, not for the cores' own sequences, where the
chains start from the core and run 20 steps per knot.

## Review

Referee pending (the referee thread). The advisor model reviewed the design cold before freezing: it proposed the nested rung, the
paired per-core test, the forced-resample count and the held-out pilot.

## Literature and provenance

Known: degree-preserving switch chains (Chodrow 2020 for hypergraphs with multi-edges; Dyer, Greenhill, Kleer, Ross and Stougie 2021
on sampling hypergraphs with given degrees); grown random networks differing from their degree-matched static versions (Callaway,
Hopcroft, Kleinberg, Newman and Strogatz 2001; Bollobás, Janson and Riordan); the pair-count lemma's trades (Pasch; Hedayat and Li
1979). Not found: which structure ends grown not-all-equal patterns. Classification: known-with-delta (the tools are known; the
answer is new).

## Workspace assumptions

A71, A72: used, unchanged.

## Ratio

Substantive: the census and the exact fairness checks. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what the expanding growth's degrees do not carry | **Status:** Successful (referee pending) | N1, N2 held: the nesting by age carries the end; degrees and schedule add nothing to it |
| Local direction — why growths end | Continue | A criterion on the prefix counts alone is the next step |
| Broader exploration — G17 | Searching | Other laws and weightings untried |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | A growing pattern dies from its own past folding in on itself, under this weighting |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71 and A72 used.
**Basket:** `OLD-CORE-20261112-001#2` (where X growth ends: the hazard fit over q from 0.2 to 0.3), `LIFE-JUMPS-20261112-001#2`
(a calibrated forecast), `MISSING-KNOTS-20261112-001#1`.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | An end read from the prefix counts | 2/3 — Substantial | 2/3 — Testable | Fit, on half the endings, the chance that a nested pattern with given prefix counts ends, and test it frozen on the other half and on growths still alive → a criterion of the end from the prefix counts alone, or none | Selected · awaiting go-ahead |
| 2 | Where X growth ends | 2/3 — Substantial | 3/3 — Ready | The hazard fit over q from 0.2 to 0.3 (`OLD-CORE-20261112-001#2`) → the critical closing rate, and whether the hazard decays | Alternative · deferred |

1. Payoff 2: a criterion on the prefix counts would say when a growing pattern dies from its history alone. Concreteness 2: the
   nested resampler is ready; the criterion's form is not yet chosen.
2. Payoff 2, Concreteness 3, as recorded.

**Recommendation.** Research directions, #1, awaiting the go-ahead.

## Final report as sent

(Appended after sending.)
