# The node reading's two exceptions: chained twins and lifts that do not meet

> **Referee report R1, 27 November 2026: confirmed with fixes — Block on the sentence that every accepted `grow` start
> is in the class, and on the classifier as a complete inventory** ([the report](referee-R1/report.md)). All 67 twin
> starts and the three failed-lift starts reproduce, and every draw count of the table reproduces on all 30,000 draws.
> - **Block: not every `grow` start.** The table shows 774 of 775 accepted `grow` draws certified in the class; an accepted
>   seven-knot `grow` start of the graded-order study (held-out draw 257587) has chained twins. Read "every accepted start
>   drawn here", not every accepted start.
> - **Block: the classifier kept one piece.** At a tie between two pieces failing in the same round it kept the first;
>   a 54-knot start with one piece of each kind lost a mechanism. Repaired (`shapes.py` keeps every piece at the earliest
>   round); the counts above are unchanged.
> - **Narrowings.** A twin family can have three or four lifts, and a split can have one shortening and three lifts, or
>   three families; "N3 never fails alone" and the lift-split count are for completed cores: of the 3,166 `tree+` draws
>   left unresolved by the caps, 1,363 already violate a class condition on the checked prefix, 876 of them N2 alone, so
>   failed lifts are frequent among large cores and rare only among the cores that finish here. Seven-knot `tree+`
>   distinct starts are 227 and the rank-limited ones 12 (one hash collision). Read this record with these changes.

Epic `TWO-EXCEPTIONS-20261127-001`, under G17 with G1, after `CHAIN-COUNT-20261127-001` and both referees of 27 November
(that study's direction 2, widened). Structure only: nothing here is grown. Computed; referee pending.

**What was asked.** The node reading is proved on starts whose node core meets N1 (no chained twins), N2 (lifts meet) and
N3 (base-holding families close) (`CHAIN-COUNT-20261127-001`). Two referees built starts outside it without chained
twins. Which families break the reading where it fails, and how often is a start outside the class under the named
weightings?

## 1. Every failure seen starts with one of two families

[shapes.py](shapes.py) finds, on each start whose core finishes, the first round at which Lemma R's round rule on the
extended nodes differs from the extended nodes' parent sets, and classes each family the round rule makes there that no
extended node has as its parents:
- a **twin family**: two lifts (T_1, a), (T_2, a) of two core parents on one vector, with two or more members one chain
  step lower, on one vector, whose cores are common children of T_1 and T_2 (Lemma D's chained-twin case; the lower
  members may be pure twins that hold no chain base);
- a **lift split**: two families inside one parent set P(y), each holding one of two lifts that share no parent (N2's
  failure).

| Starts | First failure is a twin family | A lift split | Something else | Agree through round 10 |
| --- | ---: | ---: | ---: | ---: |
| the 67 sample starts with chained twins (both twin samples, the graded-order misses, the six-knot cycle set) | 67 | 0 | 0 | 0 |
| the referees' three failed-lift starts (9, 13 and 24 knots) | 0 | 3 | 0 | 0 |
| the 369 other sample starts checked, and the referees' four controls | — | — | — | all |

([samples](shapes_samples.txt), [the referees' starts](referee_witnesses.jsonl).) So on every failing start seen the
reading breaks first at one of the two families its proof names, at the round the referees and the growth comparisons
found. Where both conditions fail, the twin family comes first on every sample start.

## 2. How often a start is outside the class

[counts.py](counts.py): draws of the weightings `tree+` and `grow` of `WEIGHTINGS-20261119-001B`, 3,000 at each size,
seed 2026112701; accepted starts (the late-views class, pieces with a cycle included) counted by draw with repeats (the
weighting's own count) and by distinct start up to renaming; the node core capped at 5,000 families and 250,000
parent-sharing pairs in one round (a capped core is only too large to check here, not unending:
`CYCLE-READ-20261127-001`, referee R1).

| Weighting | Knots | Accepted (draws / distinct) | In the class, with chains | In the class, no chains | Chained twins | Lifts that do not meet, only | N3 only | Core unfinished at rank 25 | Over the cap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `grow` | 7 | 232 / 227 | 179 / 174 | 53 / 53 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `grow` | 8 | 201 / 200 | 172 / 171 | 29 / 29 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `grow` | 9 | 147 / 147 | 128 / 128 | 19 / 19 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `grow` | 10 | 127 / 127 | 118 / 118 | 8 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 |
| `grow` | 11 | 68 / 68 | 63 / 63 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `tree+` | 7 | 3000 / 226 *(R1: 227)* | 1774 / 46 | 916 / 149 | 0 / 0 | 0 / 0 | 0 / 0 | 45 / 11 | 265 / 20 |
| `tree+` | 8 | 3000 / 487 | 1754 / 124 | 711 / 243 | 52 / 10 | 0 / 0 | 0 / 0 | 64 / 16 | 419 / 94 |
| `tree+` | 9 | 3000 / 860 | 1775 / 254 | 469 / 247 | 85 / 49 | 0 / 0 | 0 / 0 | 37 / 12 | 634 / 298 |
| `tree+` | 10 | 3000 / 1249 | 1786 / 442 | 335 / 233 | 86 / 53 | 1 / 1 | 0 / 0 | 22 / 8 | 770 / 512 |
| `tree+` | 11 | 3000 / 1634 | 1769 / 654 | 241 / 195 | 79 / 52 | 1 / 1 | 0 / 0 | 13 / 9 | 897 / 723 |

- **Under `grow`** every accepted start drawn here from seven to eleven knots *(R1: not every accepted start; one known start has chained twins)* is in the proved class (one ten-knot start is over the
  cap), most with chains: there the late view is a theorem.
- **Under `tree+`** the class holds 90% of accepted draws at seven knots, 82% at eight, 75% at nine, 71% at ten and 67% at
  eleven. Chained twins are 0, 1.7, 2.8, 2.9 and 2.6% of accepted draws. Lifts that do not meet without chained twins
  occur once in 3,000 draws at ten knots and once at eleven *among cores that finish (R1: 876 capped draws already show
  them on the checked prefix)*. N3 never fails alone *among finished cores*. The rest are cores over the cap
  (9% rising to 30%) and cores of pieces with a cycle that do not finish by rank 25 (2% or less).

So under both weightings, the reading's failure on starts whose cores finish here is almost always chained twins *(R1:
of 3,000 `tree+` draws a size; `grow` showed no finished exception)*, and the main limit as size grows is the size of
the core, where failed lifts are frequent.

## What is not done

The objective's second part, extending the reading by the two families and testing it against growth, was not
attempted: after a twin family or a lift split, births are no longer pairs of a core node and chain lengths, and the
error grows (on the nine-knot witness, 236 births against 151 at round 24). Reading them needs a structure the proof
does not have; it is the decision's direction 1.
