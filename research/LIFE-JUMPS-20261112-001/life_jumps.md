# Jumps over a whole life

Epic `LIFE-JUMPS-20261112-001` (sub-goal B167, from `RANDOM-FATES-20261112-001` direction 1; G17 Typical and rare meeting patterns,
with G7), 2026-11-12, at the coordinator's go-ahead. Pre-registered in commit 68f4ef038 before the registered run. The canonical K1–K3
test is unchanged. Refereed by the referee thread (LIFE-JUMPS-R1, `referee-R1/report.md`, commit ee4aedcd4): **confirmed with
fixes**, folded in below; four corrections logged (two Narrowing, two Not a block).

## Words

As in the guide's glossary and `RANDOM-FATES-20261112-001`: tie class, ends, last base, move, horizon, minimal contradiction. The
**share** is the largest tie class over the distinctions in some knot; **k knots before the end** removes the last k knots; the
**closing hazard** h is the share of all triples of distinctions that lie on one side of one tie class (a closing knot on such a triple
ends the growth). Growth is timed in knots.

## The question

`RANDOM-FATES-20261112-001` found that uniform knots end in a jump while growth that keeps adding distinctions carries large tie
classes long before its end. Over whole lives, on fresh seeds: how does the largest tie class grow; does the end come with or without
a jump; does the law signal the end long before; does living growth with rare closings stay free of a large class? This is the
owner's question of what the patterns that "go for a while then die" look like on the way, and whether it is "similar to limits".

## The question in standard terms

For random 3-uniform hypergraph processes under proper 2-colouring, the backbone up to global flip along one realization, from the
start to the loss of 2-colourability, and its value as a predictor of that loss.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Uniform knots: nothing, then one jump.** The share stays at about 1/n for 90 to 95% of the life (medians 0.02, 0.005, 0.003 at n = 100, 200, 300 at 90% of the life), then rises within the last 20 knots: 0.03, 0.28 and 0.74 at 20, 10 and 5 knots before the end at n = 100, and 0.88 at the last base. Forty knots before the end the share is at most 0.05 in 95 to 100% of runs, and at least 0.5 at the last base in 93 to 95%. The closing hazard is 0 twenty knots before the end and about 0.16 at the last base. | computed, frozen | J1 held |
| 2 | **Its length is a number of knots, consistent with the census.** Ten knots before the end the median share is 0.28, 0.20 and 0.23 at n = 100, 200 and 300 (all 30 runs at 300, the last folded in after the referee: J1 at n = 300 reads 96.7% and 93.3%), and five before 0.74, 0.49 and 0.78: within a factor of two at n = 300 against n = 100, as registered, but a factor-of-two test pins nothing finer (`RANDOM-FATES-20261112-001`'s correction). At 95% of the life the share is 0.25 at n = 100 and 0.003 at n = 300, so the stretch is not a fixed share of the life. | computed, frozen | J1b held |
| 3 | **Growth that adds distinctions: a share that rises over the life, with no final jump.** At X(0.3) the median share is 0.04 at a tenth of the life, 0.08 at half, 0.12 at three quarters, 0.24 at 90% and 0.33 at the end; the last 50 knots add almost nothing (0.32 at 50 before, 0.36 at the last base). The same shape at X(0.35) (0.16 at half, 0.49 at the end), O global (0.3) (0.11, 0.23) and O local (0.3) (0.12, 0.25). The share 20 knots before the end over the share at the last base has median 1.00 in all four, against 0.02 to 0.05 for uniform knots. Among growths that end after at least 200 knots, the largest class has at least ten members and a share of at least 0.05 at half the life in 61 to 75%, in each process (survivors: 15% at X(0.3), 67% at O global (0.3)). | computed, frozen | J2 held; J3 held |
| 4 | **The law signals the end, for ends within a few times the reading's age** (*narrowed after the referee: knots per distinction alone, with no ties, already gives AUC 0.74 and 0.71, so the ties add about 0.1; for growths that end after 3,000 knots the share separates them from survivors with AUC only 0.67 at 300 knots and 0.74 at 1,000; censoring at 6,000 does not inflate it*). At X(0.3), the share after 300 knots separates the 70 growths that later end from the 13 still bases at 6,000 knots with an area under the ROC curve of 0.82 (medians 0.044 against 0.010), and after 1,000 knots with 0.84 (46 against 13; 0.052 against 0.004). The closing hazard does the same (0.77 and 0.85). | computed, frozen | J4 held |
| 5 | **Rare closings: no large class.** X(0.2) is still a base after 6,000 moves in 99 of 100 runs; after 6,000 knots (78 runs reach 6,000 knots; the others have 5,999 after a move that added nothing) the largest class has a median of 2 members and at most 15 in 96% (at most 51), and the share falls toward 0 as the base grows (0.004 at a tenth of the life, 0.001 at half). | computed, frozen | J5 held |
| 6 | **The class is in the most knotted distinctions, and older than that only in X.** In every ending of the four growth processes, the median arrival index of the largest class's members at the last base is below half the distinctions (J6 held). *Narrowed after the referee: a set of the class's size drawn with probability proportional to each distinction's knots meets that criterion in every ending too, so J6 is forced by degree. Beyond degree the class is older at X(0.3) (median index 0.22 of n against the null's 0.30; below the null's 5th percentile in 86% of endings) and partly at X(0.35) (0.28 against 0.33; 60%), and not in the overlap processes (0.24 against 0.25; 7 to 8%).* | computed, frozen; the null the referee's | J6 held (forced by degree) |
| 7 | **Facts that hold by definition (checks).** The largest class's size never falls; a knot with a new distinction ties it only if its pair is tied equal, so every rise of more than one comes from a closing knot; and the end comes exactly when a closing knot falls on one side of one class, so the closing hazard is the end's chance per closing. | proved (stated in the pre-registration) | — |

## Answer

The patterns that go for a while and then end look, on the way, like one of two things, depending on the weighting. Uniform knots on a
fixed set of distinctions show nothing for nine tenths or more of their life and then tie most of the base within about twenty knots:
no approach, one jump (the known discontinuous backbone at the 2-colouring threshold, read along one growth). Growth that keeps
adding distinctions ties a growing share of itself over the second half of its life, in its most knotted distinctions (older than
their knots predict only in X), and the end adds nothing to it: the share approaches its final value before the end comes. Read
early, that share forecasts an end that comes within a few times the reading's age, about 0.1 of AUC better than counting knots per
distinction, and weakly beyond; with rare closings the class stays small as the growth goes on. *(Narrowed 2026-11-12 after the
referee.)*

## Reading

**Interpretation, not a theorem.**
- **The owner's limits.** In growth that adds distinctions the law's own quantity, the share of the largest tie class, rises steadily
  and levels off before the end; that is the nearest thing in the record to the owner's "similar to limits". In uniform knots there is
  no limit, only a jump. Which one a growth shows depends on whether new distinctions keep arriving: they dilute the ties, so a tie
  class must form in the old, dense part before it can end the growth.
- **"Relative to each other."** The signal is entirely the law's: the share of distinctions tied to one another. No outside clock is
  needed to see the end coming; the growth's own relations announce it.
- **Living forever.** Where closings are rare the share goes to zero: the growth keeps every distinction loose, which is how it
  lives on (A71: under this weighting).

## Lag cutoffs and census-only claims

Computed under the named processes and horizons, all 690 growths (the last U300 growth folded in after the close). The facts in conclusion 7 are proved.
The forecast (J4) is at one process, X(0.3). No all-size claim.

## Deviations, disclosed

The registered unit ran the uniform growths on 300 distinctions first, and each took 22 to 67 minutes under a heavily shared machine.
The growth settings (X, O) and then the uniform settings on 100 and 200 distinctions were run in two more units with the frozen
`census.task` and the same seeds (`xo_driver.py`, `u_driver.py`), written to `runs_xo.jsonl` and `runs_u.jsonl` and merged into
`runs.jsonl` with one record per growth. The registered unit, which kept running, reached its four-hour cap with 28 of the 30 growths on
300 written and had by then also run 660 growths that the other two units ran: all 660 pairs of records are identical (a check of
determinism). The last two growths on 300 ran in a fourth unit (`u300_driver.py`); one is written, and the other, still running at the
time of writing, is pending (`docs/LONG_RUNNING.md`, LIFE-JUMPS-A3); one run cannot move J1's shares by more than
a thirtieth. The frozen summary put numpy booleans in its verdicts, which json cannot write, so it is run as `summary_fixed.py`: the
frozen code with `default=lambda o: o.item()` added to its two json calls and its path set (the diff is those lines).

## Stress test

One size past: U300 against U100 and U200 is the registered size check. Fresh seeds against `RANDOM-FATES-20261112-001`'s readings:
the k = 1 to 50 profiles agree (X(0.3) 0.32 to 0.36 here against 0.35 to 0.38 there; U100 0.88 at the last base against 0.89).

## Review

**LIFE-JUMPS-R1** (the referee thread, confirmed with fixes): J1 to J6 recomputed from the records with independent code, every figure
matching; 414 growths regenerated from the seeds with its own generators and another solver, all matching; the side units' records
identical to the merged ones; `summary_fixed.py` changes only how booleans are written. Its fixes, made above: J6 forced by degree
(Narrowing), J4 narrower than "long before" (Narrowing), the literature (Not a block), the 30th U300 growth (Not a block). Its scope:
the tie classes at each reading were recounted from the records, not recomputed. The advisor model reviewed the design cold before
freezing (changes listed in the pre-registration).

## Literature and provenance

- **Known, and rediscovered here in kind (the referee's).** J1, J1b and J3's uniform side: the end comes at a median of 2.105 knots per
  distinction at n = 300, the known 2-colouring (NAE-3-SAT) threshold of random 3-uniform patterns (about 2.105; Achlioptas and Moore;
  Castellani, Napolano, Ricci-Tersenghi and Zecchina), and just before it a backbone of forced pairs appears discontinuously (Monasson,
  Zecchina, Kirkpatrick, Selman and Troyansky 1999; for 2-colouring and frozen variables Achlioptas and Ricci-Tersenghi; Semerjian);
  the XOR analogue is the discontinuous core of random XORSAT (Dubois and Mandler; Mézard, Ricci-Tersenghi and Zecchina). J2, J5 and J6:
  grown random networks with occasional closing edges have a giant component only above a closing-rate threshold, with an
  infinite-order transition, and old vertices sit in it (Callaway, Hopcroft, Kleinberg, Newman and Strogatz 2001; Dorogovtsev, Mendes
  and Samukhin). J4: early warning from a rising order parameter is a generic idea (Scheffer and co-authors). Also spines (Istrate,
  Boettcher and Percus 2005) and explosive percolation (Achlioptas, D'Souza and Spencer 2009).
- **New.** The single-growth measurements counted in knots before the end; J3's contrast between the two weightings; J4's forecast,
  its size and its baselines; J6's excess age beyond degree in the expanding processes.
- **Not found** (bounded search): the backbone up to flip along one growth, its course in growth that adds variables, and its use as a
  forecast of the end.
- **Classification.** Known-with-delta, as above.

## Workspace assumptions

A71 (each process one weighting of many) and A72 (a growth ends when it allows no state), used, status unchanged.

## Ratio

Substantive: the census of 690 whole lives and its summary. Administrative: the pre-registration, this note, the closure, two drivers.

## Corrections

Four, from the referee (`docs/CORRECTIONS.md`, 2026-11-12): **Narrowing**, J6's "the class is old" is met by degree alone and is older
than degree only in X; **Narrowing**, J4's forecast is "within a few times the reading's age, weakly beyond", about 0.1 of AUC above
knots per distinction; **Not a block**, the literature (J1 and J3 the known threshold and backbone, J5 and J6 grown networks);
**Not a block**, the 30th U300 growth folded in (J1 96.7% and 93.3%, J1b 0.234).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — tie classes over whole lives | **Status:** Successful (refereed, confirmed with fixes) | J1 to J6 held: uniform knots jump at the end; growth that adds distinctions rises over its life to a level and its early share forecasts the end |
| Local direction — the course to the end | Continue | Why the share rises in growth that adds distinctions is not yet explained |
| Broader exploration — G17 | Searching | Other laws and weightings untried |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | The owner's "similar to limits" has a measured form: a rising share that levels off before the end, in one weighting, and a jump in the other |

**Corrections:** four, after the referee (two Narrowing, two Not a block). **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71 and A72 used,
status unchanged. **Basket:** `RANDOM-FATES-20261112-001#3` (other weightings), `#4` (larger uniform sizes), `#5` (the other meaning
of "die"); `MISSING-KNOTS-20261112-001#1` and `#2`.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The old core's own end | 3/3 — Major | 3/3 — Ready | On the frozen growths, read the knots among the oldest k distinctions as a pattern of its own and test, frozen, whether a growth ends when that core reaches the uniform end (about 2.1 knots per distinction) → a law of when growth that adds distinctions ends, or none | Selected · awaiting go-ahead |
| 2 | A calibrated forecast | 2/3 — Substantial | 3/3 — Ready | Sum the closing hazard over the closings still to come and compare with the ends observed, frozen → the hazard explains the ends, or later jumps add to it | Alternative · deferred |
| 3 | Larger uniform sizes | 1/3 — Modest | 2/3 — Testable | Tie classes only at n = 400 to 800 (`RANDOM-FATES-20261112-001#4`) → the end's length fixed in knots, or growing like √n | Alternative · deferred |

1. **The old core.** Payoff 3: it would say when the patterns that "go for a while" end, by a law read off their own oldest part, and
   explain the rising share. Concreteness 3: every growth regenerates from its seed (660 duplicate records identical), and the
   advisor's reading gives the core's density, (1 + q/2)/(1 − q). Resource bound: an hour on the existing growths.
2. **A calibrated forecast.** Payoff 2: it would turn the forecast into a number. Concreteness 3: the hazard is recorded at every
   reading.
3. **Larger uniform sizes.** Payoff 1, Concreteness 2: solver cost grows fast past 300.

**Recommendation.** Research directions, #1, awaiting the go-ahead.

## Final report as sent

Sent to the owner on 2026-11-12 at about 15:00 UTC, in the project thread, together with `MISSING-KNOTS-20261112-001`'s report:

> **Over a whole life, and the count of gaps: both done (referee pending).** The patterns that go for a while and then end look different on the way, depending on the weighting.
>
> **Jumps over a whole life**: all 7 frozen predictions held, across 689 growths.
> - **Uniform knots: no approach, one jump.** Nothing is tied for 90 to 95% of the life. Then most of the base ties in the last 20 knots.
> - **Growth that keeps adding distinctions: closest to your limit.** Its largest tie class rises over the second half of life, from 8% at half-life to 33% at the end at X(0.3). It always sits in the oldest distinctions, and the end itself adds nothing.
> - **The law forecasts the end.** Read 300 knots in, the size of that class separates growths that will end from those that won't (AUC 0.82). With rare closings the class stays near zero, and the growth lives on.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt: tie classes over whole lives | **Status:** Successful (referee pending) | J1 to J6 held on fresh seeds |
> | Local direction: the course to the end | Continue | Why the share rises is not yet explained |
> | Broader exploration: G17 | Searching | Other laws and weightings untried |
> | Long-term goal: G17 Typical and rare meeting patterns (with G7) | Capability gained | "Similar to limits" has a measured form in one weighting and a jump in the other |
>
> **Next step:** Research directions. Selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | The old core's own end | 3/3 Major | 3/3 Ready | Read the oldest k distinctions as a pattern of their own → does the growth end when that core reaches the uniform end (2.1 per distinction)? | Selected · awaiting go-ahead |
> | 2 | A calibrated forecast | 2/3 Substantial | 3/3 Ready | Sum the closing hazard still to come → it explains the ends, or later jumps add to it | Alternative · deferred |
> | 3 | Larger uniform sizes | 1/3 Modest | 2/3 Testable | Ties only at 400 to 800 → the end's length fixed or growing | Alternative · deferred |
>
> **The count of missing knots**: partly confirmed. On the growth that never ends, the law's distance grows by about 0.11 members per missing knot, which replicated. On a second way of making the same kind of pattern, the cost falls as the knots get denser. Within one base with rare closings, the count stops predicting the distance. So it counts gaps, but not in a fixed unit.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt: a unit for the law's count | **Status:** Partially successful (referee pending) | M1 held. M2 and M3 failed. The rival held |
> | Long-term goal: G17 (with G1) | Capability gained | The count is close to a count of gaps |
>
> **Next step:** Research directions. Selected: #1, the cost of a gap from its neighbours (2/3, 2/3), awaiting go-ahead.
>
> **Corrections:** the census referee's five are already logged (one Narrowing, four Not a block). None new here.
> **Goals:** two G17 checkpoints, capability gained. No goal change.
> **Assumptions:** A71 and A72 used, unchanged.
> **Basket:** #1 is sub-goal B170.
> **Advisor:** reviewed both designs cold before freezing; its fixes are listed in the pre-registrations.
> **Pending:** one last uniform growth on 300 distinctions, which can move a share by at most 1/30. The five slow runs from the census were stopped unfinished, and nothing rests on them.
