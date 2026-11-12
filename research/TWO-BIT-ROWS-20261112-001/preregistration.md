# Two distinctions per position: pre-registration

Epic `TWO-BIT-ROWS-20261112-001` (`ROW-NEST-20261112-001` direction 1; G17, with G1), 2026-11-12, at the coordinator's go-ahead.
Frozen before the registered run. The canonical K1–K3 test is unchanged. The law is NAE on three-place knots on distinct
distinctions.

## Words

A **generation** (the literature's "row") is an ordered list of positions, each holding two distinctions; each generation has one
position more than the one before it, and is joined to it by the same **rule** at every position: a set of knots on relative
distinctions. These are words for how knots meet, not a drawn picture. **Flat** rules reach the two distinctions at the old positions
i − 1, i, i + 1 and the new positions i − 1, i; **hopping** rules reach old position i, old position ⌊i/2⌋ (far from i once i grows:
non-neighbouring parts) and new positions i − 1, i. The last generation is **closed** by a knot on every three consecutive
distinctions.

## The question

`ROW-NEST-20261112-001` found that with one distinction per position nothing keeps time. With two, a pair can carry a bit that
complement symmetry does not erase (whether its two distinctions are equal). What is the fewest knots that make life at depth t, or
what the first generation allows, depend on t with a period (a **harmony**) or without one within depth 40 (a candidate
**counter**), and how rare is each under short descriptions, flat against hopping? Counting with rich enough local rules is known
(tile encodings, `NEST-COUNT-20261112-001`); what would be new is the fewest knots and the rarity. If nothing keeps time, the answer
is that two NAE distinctions per position with this reach are still too few.

## Design (frozen in `census.py`)

First generation 2 positions; depths 1 to 40; readings alive(t) and the first generation's relation (complement classes of its four
distinctions). Classes as in `ROW-NEST-20261112-001`: constant, eventually constant, harmony (period 2 to 10 holding from some depth
a ≤ 20), unexplained within 40. Every rule with one or two knots is read (7,260 flat, 1,596 hopping); 4,000 rules per variant with
three to thirty knots are drawn by the code (number of knots plus one by Elias gamma, then a uniform set). Weight of a rule with m
knots: 2^−(gamma(m + 1) + log2 C(R, m)), R = 120 flat, 56 hopping.

## Settled by definition (stated, not tested)

Without the closed last generation every reading could only shrink with depth (`ROW-NEST-20261112-001`'s advisor), so the closing
is what lets depth matter. The first generation's relation is one of 2^8 sets. A sampled share is of the drawn rules, not proved.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | **Two distinctions per position make a harmony.** Some rule, flat or hopping, has life or the first generation's relation depending on depth with a period of 2 or more. | none |
| P2 | **They still do not count.** No rule has an unexplained sequence within depth 40. | any |
| — | Reported: the fewest knots for each, the weight shares, flat against hopping, the depth of the last change. | — |

## Plumbing (disclosed)

A plumbing run of 20 sampled rules per variant (seed 99, scratch) printed only timing and that the summary runs.

## Stop rule and runtime

One run (about six minutes on 16 workers), its summary, a hand-off to the referee thread, report; then pause for the referee
verdicts, as the coordinator asked.
