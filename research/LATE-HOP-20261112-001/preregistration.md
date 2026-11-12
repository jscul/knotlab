# The late hopping rules, read deeper: pre-registration

Epic `LATE-HOP-20261112-001` (`TWO-BIT-ROWS-20261112-001` direction 1; G17, with G1), 2026-11-12, at the coordinator's go-ahead.
Frozen before the registered run. The canonical K1–K3 test is unchanged. Words and rules as in `TWO-BIT-ROWS-20261112-001`
(generations growing by one position, two distinctions per position, flat and hopping reach, the closed last generation).

## The question

Five hopping rules changed late (depths 21 to 35) and could not be classified within depth 40. Read to depth 200, do they settle,
keep a period, or keep changing? And are their changes tied to where the last generation's length passes a power of two, which the
hop to half the index would supply by construction?

## Selection and readings (frozen; `selection.json` beside the code)

From TWO-BIT-ROWS's records: the 5 hopping rules unexplained within 40; the 24 other hopping rules whose life or first-generation
relation last differs from the depth before at depth 16 or later; the 2 flat harmonies and the 4 flat rules with the latest change:
35 rules. Readings as in TWO-BIT-ROWS (its code imported unchanged) for depths 1 to 200.

## Classes (frozen)

Constant; eventually periodic with the smallest period p ≤ 50 holding from some depth a ≤ 100 to 200 (eventually constant when
p = 1); else neither within 200. For each sequence, the depths at which it differs from the depth before, set against the depths
where 2 + t is a power of two (within 2).

## Settled by construction (stated, not tested)

The hop links a new position i to old position ⌊i/2⌋, so the chain of hops from a position has length ⌊log₂ i⌋, which grows by one
exactly when a generation's length passes a power of two. A change at those depths is what the reach itself supplies, a clock of
the construction rather than of the law. A rule that keeps changing only there counts in that weak, built-in sense.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| L1 | **The five settle.** Each of the five is eventually periodic (p ≤ 50 from a ≤ 100) within 200. | any is neither |
| L2 | **Late changes are the reach's.** Every change after depth 40, in any selected rule, falls within 2 of a depth where 2 + t is a power of two. | any change elsewhere |
| — | Reported: the classes of all 35, the flat rules' fates, the periods. | — |

## Plumbing (disclosed)

The selection was built and one rule timed to depth 60 (scratch); no sequence beyond TWO-BIT-ROWS's depth 40 was looked at.

## Stop rule and runtime

One run (minutes on 8 workers), its summary, a hand-off to the referee thread, report; then pause, as the coordinator asked.
