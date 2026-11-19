# Pre-registration: the proved theorem past the census

Epic `SCALE-THEOREM-20261119-001`, ticket `SCALE-THEOREM-20261119-001B`, 19 November 2026, by Claude, on the coordinator's go-ahead.
Goal G17.

## The question

The identification line proved, under (S0) no stall, (S3) no round-1 group of three, (S4) no two live knots with two common
neighbours, and (S6′) at least two loose distinctions, that the growth is the clusters of the relayed extended map of joins. Its
growth class is read off piece by piece:
- a finished piece closes if it is alone, and relays (dimension 2) otherwise;
- a tree core with R chains has dimension R;
- a bare single cycle has dimension 1;
- any other cycle grows exponentially.

How much of SCALE-SHARE's sampled starts of 5 to 20 knots does this cover? What dimensions does it predict, and do they match
SCALE-SHARE's refereed shares?

## Population and method

- **The samples.** SCALE-SHARE's own: for n = 5, 6, 7, 8, 10, 12, 16 and 20, eight Metropolis chains of 1,000 samples each, regenerated
  exactly with its seeds (`scale.chain`), and weighted to distinct arrangements by |Aut| / n!. Shares are labelled shares, as SCALE-SHARE
  gives them, with counts stated.
- **The readers.** Each sample is classified by DOUBLE-IDENT's class and read by the theorem's rule (`scalelib.py`, built on
  DOUBLE-IDENT's code). Its class under CLUSTER-ALL's cluster rule is also recomputed.
  - The two readers share low-level code (`joinlib`'s round-1 groups), but not the reading of the class.
- **The regrowth.** On chain 0, the first 60 growing samples in the class at each size are regrown. Their per-round (parents, fresh)
  multisets are compared to round 6 with the relayed cover's.
- **The run.** Through the shared runner (`SCALE-THEOREM-B1`, `runs/scale-theorem`).

## Pilot (disclosed)

One extra chain (seed 99) of 200 to 400 samples at n = 5, 8, 12, 16 and 20:
- in-class share of non-stalling starts: 0.82, 0.75, 0.82, 0.65 and 0.76;
- out of the class, about half by (S3) and half by (S4);
- in the class, dimension 2 is 85% of growers at 5, 91% at 8, 22 of 22 at 16 and 27 of 28 at 20;
- the theorem's class equals the cluster rule's on every in-class sample, and 15 regrown per size at 16 and 20 agree.

The frozen run's integrity check was also tried on chain 0 at n = 5: 1,000 of 1,000 recorded classes reproduced, and 60 of 60
regrown agreed.

## Predictions (frozen; scored by `merge.py`)

| # | Prediction | Falsified by |
| --- | --- | --- |
| P1 | (integrity) the regenerated samples' cluster-rule classes equal SCALE-SHARE's recorded ones | one sample that differs |
| P2 | in the class, the theorem's growth class equals the cluster rule's on every sample | one sample that differs |
| P3 | the in-class share of non-stalling starts lies in [0.55, 0.90] at every size | a size outside |
| P4 | in the class, dimension 2 is at least 75% of growers at every size, and higher at 20 than at 5 | either failing |
| P5 | (risky) dimension three or more never exceeds 1% of in-class growers at any size | a size above |
| P6 | (the stop rule) every regrown in-class sample agrees round by round to round 6 | one that differs |
| P7 | (risky; it tests the class's selection more than the theorem) the in-class dimension-2 share of growers is within 5 points of SCALE-SHARE's share of all growers, at every size | a size more than 5 points off |

**Readouts:**
- counts at each size;
- the cluster rule's class mix inside and outside the class, whose weighted mix is SCALE-SHARE's figures;
- the out-of-class reasons ((S3) or (S4));
- the dimension-2 mechanism (two chains, relay, both);
- the exponential share in the class.

## What would follow

- **P3 to P5 holding.** The proved class covers most non-stalling starts at every size. Inside it, dimension 2 dominates and grows
  more dominant, and three stays rare.
  - The mechanism, in the theorem's terms: three needs a tree core with three separately fed chains. Each chain needs a knot with
    open places left after its joins, and open places per knot fall like √(5/n). A finished piece always relays as two.
- **P6 failing** stops the study at that size.

## Prior work in the program

`python3 -B scripts/track.py objects "typical growth share by size stall dimension sampled arrangements proved class" --until 2026-11-19 --exclude SCALE-THEOREM-20261119-001`

- `SCALE-SHARE-20261119-001`: the samples and the cluster rule's shares, the object compared with.
- `DOUBLE-IDENT-20261119-001`: the class and the census's shares.
- `CLUSTER-ALL-20261119-001`: the cluster rule.
- `RELAY-IDENT-20261119-001`: the dimension rule on trees and the census tally, the same words.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before this freeze. Adopted:
- predictions renamed P1–P7, so that they do not collide with (S3) and (S4);
- P4's floor lowered to 75%;
- P7 marked as testing the selection, with the in/out mix reported;
- counts stated alongside the shares;
- the shared low-level code named.

Its mechanism for "three stays rare" is quoted under What would follow, as its argument. Its sharper prediction is not adopted as a
test: "a start with two loose distinctions never has dimension 3" follows from the rule by counting (three chains need at least
three loose distinctions), so it would check the reader, not the growth.
