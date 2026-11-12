# An end read from the prefix counts

Epic `PREFIX-END-20261112-001` (`AGE-NEST-20261112-001` direction 1; G17, with G7), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in commit 22005bffb before the registered run. The canonical K1–K3 test is unchanged. **Referee pending** (handed to
the referee thread).

## Words

As in `AGE-NEST-20261112-001`: the **age profile** or prefix counts e(j), the knots among the oldest j distinctions. **Concordance**
is the share of matched pairs (a last base against a growth at risk at the same age) in which a feature is higher for the last base,
ties half. X(0.3) is growth with closings anywhere at closing rate 0.3; the weighting is that process (A71).

## The question

The age profile carries the end of growth with closings anywhere (`AGE-NEST-20261112-001`, refereed). Can the end be read from it,
better than from what uses less (knots per distinction, degrees), and how close to the base's own chance of ending (its closing
hazard)? First, the simplest reading: is some early part past its own uniform end when the growth ends?

## The question in standard terms

For the 2-colourable prefixes of a grown 3-uniform hypergraph process, how well do statistics of the prefix-edge-count profile
discriminate the step just before 2-colourability is lost from steps of growths still at risk at the same age?

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **No early part is past its own uniform end.** In none of the 685 last bases, and none of their matched negatives, does any early part (the oldest j distinctions, j in {20, 40, 80, 160, 320} and the deciles) have a uniform resample with its own j and knots that allows no state more than half the time. The simplest reading fails outright, as `AGE-NEST-20261112-001`'s referee found for the dying cores. | computed, frozen | E1 held |
| 2 | **Density alone reads some of it.** Knots per distinction has concordance 0.685 (0.661 to 0.710): endings select histories rich in closings. | computed, frozen | E0 held |
| 3 | **The age profile reads more than density, but no more than the degrees.** The profile's own end share (100 redraws keeping each knot's youngest distinction) has concordance 0.747 (0.723 to 0.770), 0.062 above density (0.032 to 0.088), so the kill condition is not met; but the degrees' second moment, κ = Σd(d − 1)/Σd, has 0.744, and the difference is 0.003 (−0.019 to 0.025). The largest early density has 0.727, 0.042 above density (E3 failed). | computed, frozen | E2 held; E3 failed |
| 4 | **A fit does not beat the degrees.** A conditional logistic regression on density, κ, the largest early density and nine profile densities, fit on even runs, has concordance 0.773 on odd runs, 0.009 above κ (−0.018 to 0.035). | computed, frozen | E4 failed |
| 5 | **The ceiling is far higher.** The base's own closing hazard, the share of triples on one side of one tie class, has concordance 0.947 (0.936 to 0.957). What reads the end is the law's own ties, not any count of knots. | computed, frozen; the hazard is the end's chance by definition | reported |
| 6 | **Young growths are easier to read.** In the youngest third of endings the profile's share reads 0.80 and density 0.75; in the oldest third 0.69 and 0.66. Against negatives that live at least 500 knots more, every feature reads a little better (density 0.72, κ 0.77, the fit 0.80 on odd runs). | computed, frozen | reported |

## Answer

The end of growth with closings anywhere can be read from its age profile, beyond its density, but no better than from its degrees,
and a fitted model on the profile does no better either; none of these comes near what the law's own ties say (concordance 0.95
against 0.75). No early part of a dying growth is past its own uniform end. So the age profile carries the end (redraws keeping it
die, those keeping only the degrees do not), but as a forecast it adds nothing to the degrees, which in this growth are its oldest
distinctions' knots.

## Reading

**Interpretation, not a theorem.**
- **Carrying and reading part here.** Degrees do not carry the end (`AGE-NEST-20261112-001`), yet they read it as well as the age
  profile does. In growth with closings anywhere the most knotted distinctions are the oldest, so a degree statistic and the profile
  move together across growths; which one is the cause is settled by the resamples, not by the forecast.
- **The arithmetic band.** For X the typical density of every early part is fixed by the growth's arithmetic (`OLD-CORE-20261112-001`,
  corrected); what this test compares is the variation around it between growths of one age, which the band does not decide.
- **The owner's "go for a while then die".** The law shows its end in its own ties, as `LIFE-JUMPS-20261112-001` found; counts of
  knots, by age or by degree, see a shadow of it.

## Lag cutoffs and census-only claims

Computed on 800 X(0.3) growths to 6,000 moves (685 endings), three risk-set negatives each at the same age and run parity. The
hazard uses exact tie classes; the profile's share 100 redraws; the uniform null 20 per early part. No all-size claim.

## Review

Referee pending (the referee thread). The advisor model reviewed the design cold before freezing (changes listed in the
pre-registration).

## Literature and provenance

Known: the uniform threshold; early-warning ideas; age-dependent random patterns (Bollobás, Janson and Riordan 2007, inhomogeneous
random hypergraphs), whose framework gives thresholds for components and cores, not for 2-colourability, so it supplies no threshold
condition to test here (none found in a bounded search). Not found: reading a grown not-all-equal pattern's end from its age profile.
Classification: known-with-delta.

## Workspace assumptions

A71, A72: used, unchanged.

## Ratio

Substantive: the census of 800 growths and 4,750 bases. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — an end read from the prefix counts | **Status:** Partially successful (referee pending) | E0, E1, E2 held; E3, E4 failed: the profile reads beyond density but not beyond degrees |
| Local direction — why growths end | Practically exhausted | The end is read best by the law's ties, by definition; counts add little beyond degrees |
| Broader exploration — G17 | Searching | Other weightings and laws untried |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | What ends a growing pattern and what reads it are now separated |

The local direction has reached diminishing returns: five epics have narrowed the end of growth with closings anywhere to its age
profile, and the forecast adds nothing beyond degrees. The next payoff lies in the weighting itself.

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71 and A72 used.
**Basket:** `OLD-CORE-20261112-001#2` (where X growth ends, over q from 0.2 to 0.3), `LIFE-JUMPS-20261112-001#2`,
`MISSING-KNOTS-20261112-001#1`, `RANDOM-FATES-20261112-001#3` (other weightings) and `#5` (the other meaning of "die").

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other weightings | 2/3 — Substantial | 2/3 — Testable | Weight small patterns by the shortness of their description (the owner's "simple realities more common") and compare outcomes and readings with the growth weightings, frozen → a result that changes with the weighting (A71's challenge), or one that does not | Selected · awaiting go-ahead |
| 2 | Where X growth ends | 2/3 — Substantial | 3/3 — Ready | The hazard fit over q from 0.2 to 0.3 with long horizons → a critical closing rate, or a slow onset | Alternative · deferred |
| 3 | The other meaning of "die" | 2/3 — Substantial | 2/3 — Testable | When new knots stop changing the tie classes and least bonds, against the end → the two readings agree or part | Alternative · awaiting the owner |

1. Payoff 2: it tests A71 directly and the owner's own guess that simple realities are more common. Concreteness 2: the census's
   readers apply; the description weighting must be defined (for example, patterns sampled with probability decreasing in the length
   of a fixed encoding).
2. Payoff 2, Concreteness 3, as recorded in the basket.
3. Payoff 2: the owner's second meaning. Concreteness 2: needs his answer.

**Recommendation.** Research directions, #1, awaiting the go-ahead; the local line on why growths end is practically exhausted.

## Final report as sent

Sent to the owner on 2026-11-12 at about 17:30 UTC, in the project thread:

> **Reading the end from the age profile: done (referee pending).** It works, but no better than simpler counts.
>
> - **No early part passes its own uniform end.** In none of 685 endings does any early part look like a dead uniform pattern of its own size.
> - **The age profile reads the end, but only as well as the degrees.** Matched against growths at the same age, the profile's own end chance scores 0.75. Plain density scores 0.69. A degree statistic scores 0.74, essentially tied, and a model fitted on the profile doesn't beat it.
> - **The law's own ties read it far better (0.95).** The age profile is what carries the end, as the earlier redraws showed. But as a forecast, counts of knots by age or by degree only see a shadow of what the ties show.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt: an end read from the prefix counts | **Status:** Partially successful (referee pending) | E0 to E2 held. E3 and E4 failed: the profile beats density but not the degrees |
> | Local direction: why growths end | Practically exhausted | The law's ties read the end best, and counts add little beyond degrees |
> | Broader exploration: G17 | Searching | Other weightings and laws are untried |
> | Long-term goal: G17 Typical and rare meeting patterns (with G7) | Capability gained | What ends a growing pattern, and what forecasts it, are now separated |
>
> **Next step:** Research directions. Selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Other weightings | 2/3 Substantial | 2/3 Testable | Weight small patterns by how short their description is (your "simple realities more common"), then compare outcomes and readings → results change with the weighting, or don't | Selected · awaiting go-ahead |
> | 2 | Where the expanding growth ends | 2/3 Substantial | 3/3 Ready | Hazard fit over closing rates 0.2 to 0.3 → a critical rate, or a slow onset | Alternative · deferred |
> | 3 | The other meaning of "die" | 2/3 Substantial | 2/3 Testable | When new knots stop changing what the law reads, compared with the end → agree or part | Alternative · awaiting your answer |
>
> **Corrections:** none new. The three referee verdicts today were folded in (one Narrowing each).
> **Goals:** G17 checkpoint, capability gained.
> **Assumptions:** A71 and A72 used, unchanged.
> **Advisor:** reviewed the design first. It replaced the 2.1 test with a fair null at each part's own size, and added risk-set negatives, the hazard ceiling and a kill condition.
