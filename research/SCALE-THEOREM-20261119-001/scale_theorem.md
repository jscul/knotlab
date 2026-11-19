# The proved theorem past the census: shares by size

Epic `SCALE-THEOREM-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead. Goal G17. **Refereed:** report [R1](referee-R1/report.md), confirmed, no Block; two wording points
folded in on 19 November (see Referee).

**Record.**
- **Pre-registration:** [preregistration.md](preregistration.md), frozen in commit `540551a62` at 14:44 UTC after a pilot (disclosed).
- **The run:** the shared runner (`SCALE-THEOREM-B1`, `runs/scale-theorem`, 64 cases, all ok by 14:46 UTC).
- **Code:** [scalelib.py, job.py, merge.py](../../experiments/SCALE-THEOREM-20261119-001B/SCALE-THEOREM-20261119-001B-E001_shares/), built
  on SCALE-SHARE's sampler and DOUBLE-IDENT's class and rule.
- **Results:** [results.json](../../artifacts/SCALE-THEOREM-20261119-001B/SCALE-THEOREM-20261119-001B-E001_shares/results.json).

## The answer

**In the owner's terms.**
- **The proved theorem covers about three non-stalling starts in four, at every size from 5 to 20 knots.** SCALE-SHARE's own 64,000
  samples, regenerated exactly, were read by the theorem instead of grown.
  - The class (no stall, no first-round group of three, no two live knots with two common neighbours) holds 83% of the non-stalling
    starts at five knots, and 73% to 77% from ten knots on. 685 of its 14,478 starts hold at most one loose distinction; they are
    DOUBLE-IDENT's proved edge case and close at round 1 (wording from referee R1).
  - The rest fail it in roughly equal parts: a group of three (5–11%) or two common neighbours (12–17%).
- **In the class, two dimensions take over, and three never occurs.**
  - Dimension 2 is 85% of the class's growers at five knots, rising to 98% at twenty.
  - Dimension 1 falls from 12% to 2% of the class, and closing from 22% to 2%.
  - Not one of the 12,270 growers in the class has dimension three or more. All 43 three- and four-dimensional samples are outside
    the class: they have mutually touching knots, a group of three or two common neighbours.
- **Why, in the theorem's terms.** Three dimensions need a tree-like piece carrying three chains, and each chain needs a knot with
  open places left after its joins. Under this sampling open places per knot fall with size: about 1.23·√(5/n) over all
  samples (1.22 at five knots, 0.61 at twenty), and faster over the class (1.07 at five, 0.38 at twenty, roughly n^−0.74; referee
  R1's measurement, replacing the advisor's √(5/n)). So tree-like pieces with three separately fed chains are vanishingly rare. A finished piece always counts two. The advisor gave this argument; the run confirms
  its outcome.
- **The relay's share grows.** Among the class's two-dimensional growers, "relay and two chains" rises from 35% to 58%, and a relay
  alone falls from 21% to 9%. In large starts two dimensions come mostly from both mechanisms at once.
- **It matches SCALE-SHARE.** The class's two-dimensional share of growers is within three points of SCALE-SHARE's share among all
  growers at every size (85% against 82% at five knots, 98% against 98% at twenty).
- **Real growth agrees.** 477 growing samples in the class were regrown, 60 per size (57 at twenty). All agree with the theorem
  round by round to round 6, in every junction's parents and fresh count. There was no size at which rule and growth part.

| Knots | Non-stalling | In the class | Out by (S3) / (S4) | In the class: closes / dim 1 / dim 2 | Dim 2 among the class's growers | SCALE-SHARE, all growers |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| 5 | 4,413 | 82.9% | 4.7% / 12.4% | 22.0% / 11.6% / 66.4% | 85.1% | 82.4% |
| 6 | 3,724 | 81.0% | 6.8% / 12.2% | 18.9% / 10.1% / 70.9% | 87.4% | 85.2% |
| 7 | 3,035 | 78.1% | 8.4% / 13.5% | 15.3% / 9.2% / 75.6% | 89.2% | 87.0% |
| 8 | 2,634 | 76.5% | 10.0% / 13.6% | 13.0% / 7.7% / 79.3% | 91.2% | 88.7% |
| 10 | 1,764 | 75.2% | 10.6% / 14.2% | 8.5% / 5.0% / 86.4% | 94.5% | 92.9% |
| 12 | 1,405 | 74.6% | 11.0% / 14.4% | 6.1% / 4.6% / 89.2% | 95.0% | 93.6% |
| 16 | 851 | 76.0% | 10.6% / 13.4% | 3.9% / 2.3% / 93.8% | 97.6% | 97.2% |
| 20 | 544 | 73.3% | 9.9% / 16.7% | 1.5% / 2.3% / 96.2% | 97.7% | 98.1% |

Labelled shares, as SCALE-SHARE gives them; counts are of samples (8,000 per size). Exponential growth in the class: 4 samples in
all (n = 5, 6, 12).

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread. No study reader was run.
- **Confirmed.** Its own classification matches on 64,000 of 64,000, and the growth class and mechanism on 14,478 of 14,478 in the
  class. Every table figure reproduces. Its own regrowth of 1,518 in-class growers (one in eight by hash, plus every exponential
  one) agrees to round 6. P2 is the scorer's label slip, handled correctly. Weighting to distinct arrangements changes nothing.
- **Folded in (wording, not blocks).** The class names "no stall", and the 685 starts with at most one loose distinction are
  named as DOUBLE-IDENT's edge case. The open places per knot are quoted as measured (about 1.23·√(5/n) over all samples, about
  n^−0.74 over the class) instead of the advisor's √(5/n).

## Correction (Narrowing, 19 November, from WEIGHTINGS-20261119-001)

"Three or more lives only among mutually touching knots" (position table) and "the rare dimensions live only there" (directions)
hold under SCALE-SHARE's weighting only. Under uniform random trees, every start is in the proved class, and three or more
dimensions is 12% of growers at twelve knots and 37% at twenty. Those starts all have a knot of six or more places. So the out-of-class
quarter is where the rare dimensions sit for knots of at most five places, not where they must sit
([WEIGHTINGS decision note](../WEIGHTINGS-20261119-001/weightings.md); logged in docs/CORRECTIONS.md).

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | the regenerated samples' cluster-rule classes equal SCALE-SHARE's recorded ones | **held** | 64,000 of 64,000 |
| P2 | in the class, the theorem's growth class equals the cluster rule's | failed as scored | every in-class sample agrees in substance; the 4 "failures" are the scorer comparing the label "exponential" with "ring (exponential)" (post hoc) |
| P3 | the in-class share of non-stalling starts lies in [0.55, 0.90] at every size | **held** | 0.733 to 0.829 |
| P4 | in the class, dimension 2 is at least 75% of growers at every size, higher at 20 than at 5 | **held** | 85.1% → 97.7% |
| P5 | (risky) dimension three or more is at most 1% of in-class growers | **held** | 0 of 12,270 |
| P6 | (the stop rule) every regrown in-class sample agrees round by round to round 6 | **held** | 477 of 477 |
| P7 | (risky) the in-class dimension-2 share of growers is within 5 points of SCALE-SHARE's | **held** | at most 2.7 points off |

6 of 7 held as scored. P2's failure is the scorer's label slip, and it holds once the labels are matched.

## Known results, and what this adds

- **Known.** SCALE-SHARE's shares, computed by the cluster rule; the identification line's theorems.
- **What this adds.** The shares are now read from proved statements on 73–83% of non-stalling starts at every size to twenty
  knots. Inside the proved class, three dimensions do not occur in 64,000 samples. The class's selection keeps SCALE-SHARE's
  dimension-two share within three points.

## Limitations

- **Sampling.** Metropolis samples are autocorrelated, so binomial intervals would be too narrow; counts are stated instead.
  SCALE-SHARE's sampler and its weighting are taken as given.
- **The regrowth** checks 60 growing samples per size to round 6, not every sample.
- **The out-of-class quarter** is still read only by the computed cluster rule. That includes every three- and four-dimensional
  sample.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. Its answer stayed within its text.
- **Its mechanism for three staying rare held.** Tree-like pieces with three separately fed chains need open places per knot near
  one. It gave √(5/n) for the sampler; referee R1 measured about 1.23·√(5/n) over all samples and n^−0.74 over the class, so the
  argument holds more strongly.
- **Its warnings were adopted:** renaming, P4's floor, P7 as a test of selection, counts, and the shared code. It expected the class
  to inflate dimension two; it does, by 1 to 3 points.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the theorem past the census | **Status:** Successful (6 of 7 held as scored; P2 a label slip) | The proved class holds 73–83% of non-stalling starts at every size to 20; in it, dimension 2 rises to 98% and three never occurs; real growth agrees (477 of 477) |
| Local direction: an exact model of the cheapest parity growth | Continue | Proved on about three starts in four at every size; the rest is mutually touching knots |
| Broader exploration: what the cheapest growth builds | Known alternatives | Typical growth is two-dimensional, from chains and relays; three or more lives only among mutually touching knots |
| Long-term goal: G17 | Capability gained | Typical and rare growth explained from proved statements at every size sampled |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Mutually touching knots (first-round groups of three, two common neighbours): the out-of-class quarter, which holds every three- and four-dimensional sample | 3/3 — the rare dimensions live only there | 1/3 — a different complex is needed | find the complex on the census's 2,958 out-of-class starts → stop at one, or a start where none exists | Alternative · in the basket |
| 2 | Three dimensions on purpose: build in-class starts with three chains in one piece (spiders) at 7 to 20 knots, and measure how rare they are under SCALE-SHARE's measure | 2/3 | 3/3 | enumerate in-class trees with three chains by size → stop at their measure | Alternative · proposed |

## Final report as sent (2026-11-19 14:50 UTC)

**Outcome:** Past the census, the proved theorem covers about three non-stalling starts in four at every size from 5 to 20 knots. Inside that class, two dimensions take over and three never occurs. I read SCALE-SHARE's own 64,000 samples, regenerated exactly, with the theorem instead of growing them. 6 of 7 frozen predictions held as scored; the seventh "failure" was a label slip in my scorer. Closed, referee pending.

- **Coverage.** The proved class holds 83% of non-stalling starts at five knots and 73% to 77% from ten knots on. The rest have a first-round group of three (5–11%) or two live knots with two common neighbours (12–17%).
- **Dimensions in the class.** Two dimensions rise from 85% of growers at five knots to 98% at twenty. One dimension falls from 12% to 2% of the class, and closing from 22% to 2%. Not one of the 12,270 growers in the class is three-dimensional. All 43 three- and four-dimensional samples sit outside the class, among knots that all touch each other.
- **Why.** Three dimensions need a tree-like piece fed by three chains, and each chain needs a knot with open places left over. Open places per knot fall like √(5/n), so such pieces almost never appear; the advisor gave this argument before the run. Two dimensions come more and more from a relay and two chains together, which rises from 35% to 58% of the class's two-dimensional growers.
- **Checks.** The class's two-dimensional share matches SCALE-SHARE's share of all growers within three points at every size. All 477 growing samples I regrew in the class (60 per size) agree with the theorem round by round to round 6, so the rule never parted from real growth.

| Knots | In the class (of non-stalling) | Two dimensions among the class's growers | SCALE-SHARE, all growers |
| --- | ---: | ---: | ---: |
| 5 | 82.9% | 85.1% | 82.4% |
| 8 | 76.5% | 91.2% | 88.7% |
| 12 | 74.6% | 95.0% | 93.6% |
| 20 | 73.3% | 97.7% | 98.1% |

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the theorem past the census | **Status:** Successful (6 of 7 held as scored; P2 a label slip) | The class holds 73–83% of non-stalling starts at every size; two dimensions rise to 98% in it and three never occurs; 477 of 477 regrown agree |
| Local direction: an exact model of the cheapest parity growth | Continue | Proved on about three starts in four at every size; the rest is mutually touching knots |
| Broader exploration: what the cheapest growth builds | Known alternatives | Typical growth is two-dimensional, from chains and relays; three or more appears only among mutually touching knots |
| Long-term goal: G17 | Capability gained | Typical and rare growth explained from proved statements at every size sampled |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Mutually touching knots (first-round groups of three, two common neighbours): the out-of-class quarter, home of every three- and four-dimensional sample | 3/3 | 1/3 | find a complex on the census's 2,958 out-of-class starts → stop at one, or a start where none exists | Alternative · in the basket |
| 2 | Three dimensions on purpose: in-class starts with three chains in one piece, and their measure | 2/3 | 3/3 | enumerate in-class trees with three chains by size → stop at their measure | Alternative · proposed |

**Corrections:** none. All four identification proofs are now refereed and confirmed, with their folds committed (7555411f3). The line summary is `research/DOUBLE-IDENT-20261119-001/line_summary.md`. **Goals:** G17 checkpoint (capability gained). **Assumptions:** none changed. **Basket:** a new direction from you, nothing taken from the basket. **Advisor:** Fable 5.2, before the freeze, staying within its text. Its mechanism for three staying rare held. It also asked me to rename the predictions, lower P4's floor, treat P7 as a test of selection with the in/out mix reported, and give counts and the shared code; all adopted.

**Referee hand-off.** The decision note is `research/SCALE-THEOREM-20261119-001/scale_theorem.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check that `scalelib.theorem_class` uses DOUBLE-IDENT's class and rule unchanged, the integrity check against SCALE-SHARE's recorded classes, and P2's label mapping.
