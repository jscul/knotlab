# Advisor review of the draft design

Epic `SLOW-LOOP-20261117-001`, 2026-11-17. The advisor model (`claude -p --model claude-fable-5-2 --tools "" --output-format
json`; the reply's `modelUsage` names `claude-fable-5-2`) was given the first stage's results, the calibration and the first draft
cold. Its verdict was "freeze with changes", with eight changes. Its points, checked here, and what changed:

| Point | Taken? | Change |
| --- | --- | --- |
| RND is not at equal budget: backoff halves the budget of the arm that finds less | partly | realized slow work is reported, and a frozen measure of the attention signal is added that does not depend on budget: moves found per 10^6 probe incidences, G against RND |
| ST is untuned while G picks from 48 settings, and ST's moves differ from G's when β = 0.5 | yes | ST has its own 8-setting grid (passes 1 or 8, shadow knots or not, abort after 5% of knots without a find), tuned on the same instances with the same score |
| G's tuning is degenerate: on `rand` the slow loop can only lose, so the score picks the grid floor, and T reads lazy against eager | yes, declared | stated before tuning: if G's ρ is the floor, T reads a lazy policy against an eager one, not transfer as such |
| The primary cell's natural comparator is CDCL, run on 20 instances in CPU alone | yes | CDCL on all 50 instances of the `local` and `embed` cells, with propagations recorded |
| CPU can flip a verdict, since the rebuild is partly Python | partly | the CPU is split into fast loop, probes and rebuild; the verdicts keep the total, which is conservative for the slow arms |
| The censoring direction for F was missing | yes | over 5% censored in F makes R an upper bound, in the arm a lower bound, in both undetermined |
| G's fast loop is NOV even where F is PS | yes | R against NOV alone is reported beside R |
| Not re-tuning after a change makes a loss uninterpretable | noted | a loss is read as a loss of this pairing (stated) |
| The primary cell is a foregone conclusion; the informative cell is missing | yes | stated under "settled by construction"; an embedded pattern was added as a held-out cell (a `local` sub-pattern on a quarter of the distinctions, weakly coupled to a uniform pattern), where the attention counts can matter. Calibration of a first version showed it easy for Novelty+; the weakly coupled version was then chosen, and both are disclosed |
| Rule 1 can fire with no attention effect; the rules are not exhaustive | yes | rule 1 now needs G/RND ≤ 0.9 in the winning cell; a rule "pays, attention not shown" and a default branch were added |
| Bound the conclusions: rule 1 confirms scheduling by visit counts, not metacognition; rule 4 does not refute the owner's idea | yes | both stated in the rule |
| Calibration already points to "static is as good" | yes | stated |
| Predictions: raise P1, P2, P3, P9; lower P4, P6, P7; P4 ambiguous | yes | P1 80%, P2 85%, P3 90%, P4 25% ("work win or better"), P6 15% (calibration on the embedded pattern), P7 35%, P9 90%; P5 raised to 75% for the tuned ST, P8 lowered to 25% (calibration: shadow knots hurt); P12 and P13 added for the embedded cell |
| A clause-weighting arm (PAWS or SAPS) | no | it needs a new search family and its own tuning; recorded as a direction, and the decision rule says what its absence leaves open |
| "Implied knot" is ambiguous | yes | renamed **shadow knot**, which is the definition (the pattern's shadow on three distinctions that passes K1–K3); the glossary's "shadow" has that meaning |
| Spatial words: "where the search dwelt", "random places", "width", "landscape" | yes | "the knots the search attended to most" (its attention counts), "random knots"; bandwidth and landscape only under standard terms or prior work |
| Gate numbering skips G4 | yes | G4 added: a mutant that applies every tie with the wrong parity must be caught on every small instance where it made a tie |
| The policy score does not say how unsolved runs count | yes | stated (log of work at the cap plus log of one plus the least violated count); the slow loop now records its least violated count |
| The freeze date in the text | yes | the commit time is the only authority |

Not used after the results.
