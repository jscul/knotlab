# Which growth is typical as starts of touching knots get larger? Pre-registration

Epic `SCALE-SHARE-20261119-001` (`CLUSTER-ALL-20261119-001#1`, the coordinator's go-ahead; goal G17), 2026-11-19. Written after a
pilot (disclosed: 200 samples at five and six knots, 60 at eight to sixteen) and the advisor's answer, before the frozen samples.
The canonical K1–K3 test is unchanged. Classes are stated without rounds: stalls; closes; dimension = the largest number of endless
chains feeding one piece of the map; holds a ring (exponential).

## The question

By the cluster rule alone (`CLUSTER-ALL-20261119-001`), which growth is typical among arrangements of n touching knots of three to
five places, for n = 5, 6, 7, 8, 10, 12, 16, 20, under the census's two weightings? Does the rule's scope survive, including the
six-knot break shape?

## Method

- **Sampling.** Metropolis chains uniform over labelled descriptions: sizes 3 to 5 and multiplicities; one multiplicity or one
  size moved by one; feasible connected states only. Each n has eight chains of 1,000 samples: four start from a path and four
  from a dense ring (dispersed). Burn-in is 400 n² and thinning 30 n² proposals.
- **Weighting.** Labelled weighting is primary. Distinct weighting uses |Aut| / n!, and its effective sample size is reported.
- **Classification.** By `scale.classify`, with rule-free features recorded per sample: shared distinctions, cycle rank, open
  places per knot, over-demanded knots.
- **Spot checks.** For n = 6, 7, 8, 10 and 12, 200 samples that do not stall are grown 15 rounds and compared with the rule.
- **The five-knot sample** is compared with the exact census's labelled shares (a check of the sampler).

## Prior work in the program

`python3 -B scripts/track.py objects "dimension of the cheapest parity growth over every small arrangement of touching knots" --until 2026-11-19 --exclude SCALE-SHARE-20261119-001`
`python3 -B scripts/track.py objects "typical growth class large random arrangements of knots stall share" --until 2026-11-19 --exclude SCALE-SHARE-20261119-001`

- `TOUCH-CENSUS-20261118-001` — the same object up to five knots; its referee's six-knot Metropolis sample is this sampler's model.
- `PLUS-ONE-20261118-001` — the same population at six knots (400 random samples, a different sampler).
- `CLUSTER-ALL-20261119-001` — the rule used, and its scope and break.
- `JOIN-GROWTH-20261118-001` — unrelated population (hand-built joins).

## Predictions (frozen; the advisor's P1–P8, then mine)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | mean open places per knot falls with n, about √(5/n) within a factor 1.5 for n ≥ 8 (rule-free) | outside the factor at some n ≥ 8 |
| P2 | the stall share does not fall from n = 7 on (by more than 0.01); non-stall in [0.12, 0.22] at 12, [0.06, 0.13] at 16, [0.03, 0.08] at 20 | any fails |
| P3 | −ln(non-stall)/n does not fall from n = 10 to 20 (by more than 0.01), and P(no knot over-demanded) ≥ exp(−mean number over-demanded) − 0.01 | either fails |
| P4 | closes, as a share of non-stalled starts, is lower at 16 than at 6 | it is not |
| P5 | two dimensions is the most common polynomial growth at every n, dim 2 : dim 1 in [2.5, 6], dim 3 at most 2% of all, no dimension 4 or more | any fails |
| P6 | exponential (a ring) at most 3% of labelled starts at every n | above 3% at some n |
| P7 | out of scope at most 2% of labelled starts, peaking at n = 7, 8 or 10 | either fails |
| P8 | the labelled-versus-distinct difference is smaller at 20 than at 6, and at most 0.05 (total variation × 2) at 16 | either fails |
| P9 | every spot-checked start (200 non-stalled per n at 6, 7, 8, 10, 12) in the rule's scope equals the rule for 15 rounds | any differs |
| P10 | the break shape is at most 5% of non-stalled starts at every n | above 5% |

The advisor's sharpest falsifier is P1. If open places per knot do not fall, the stall trend comes from the rule's demand, not
from the counting of descriptions.

## Runs and stop rule

`job.py` through the shared runner (69 cases, 6 workers); `merge.py` scores. Under an hour, registered. Stop at the shares.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **The measure drives the stall trend.** Uniform labelled descriptions favour many shared distinctions, so open places per knot
  fall like √(5/n).
- **Its predictions.** It gave P1–P8 and asked for growth spot checks on non-stalled starts at 10 and 12, dispersed chain starts,
  effective sample sizes and the five-knot check.
- **The break.** It warned that the break shape is O(1) per start, and that new break shapes may appear above five knots.
