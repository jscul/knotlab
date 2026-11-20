# Bond distances between original distinctions after one growth layer

On the one-spare ring attached to the 17-knot path, changing the stored state gives 15 versus 18 knots in the ring's radius-five bond ball. The secondary test asked whether this already changes the distance between two *specified old marks*. The old stage and scoring labels are common to the two arms. Both had 21 original scored marks. The full new stages had 50 knots and 162 distinctions in the quiet condition, or 61 knots and 178 distinctions when loaded.

| Old marks compared | Pairs specified | Exact equal minima | Certified different | Both readings insufficient to decide equality |
| --- | ---: | ---: | ---: | ---: |
| Two marks of the 17-knot background | 120 | 44 | 0 | 76 |
| One ring mark and one background mark | 80 | 4 | 0 | 76 |
| Two marks of the ring | 10 | 8 | 0 | 2 |

An equal entry in the third column has a certified minimum on both sides. Two lower bounds, even identical bounds, do not establish equality. Each retained comparison used the same physical old pair. Ordinary growth on the two states gives literally identical incidence. The result is **inconclusive** about a change in longer old-to-old bond distances. It establishes equality on 56 of 210 specified pairs and leaves 154 unresolved. The primary effect on newly reached knots in a ball requires no inference about those 154 pairs.

The exact full-table search reached its predeclared per-block limit on each side. The fallback searched for every connected minimal separating cut of cost at most ten at each root using the predeclared state cap. Distinct physical marks have bond distance one less than the cut cost. The pair receipt retains each exact minimum or certified lower bound. The default replay runs this deterministic cutoff directly. Supply `--try-full --out <file>` to repeat the original longer attempt separately. The weighting is one per physical pair in each row. This exploratory comparison was registered after seeing the primary through-five result, before measuring the extra distances. [Design](original_marks_design.md) · [Exact values and bounds](../../artifacts/STATE-FEEDS-GROWTH-20261119-001/STATE-FEEDS-GROWTH-20261119-001-E001_feedback/original_marks.json) · [Reproduction](../../experiments/STATE-FEEDS-GROWTH-20261119-001/STATE-FEEDS-GROWTH-20261119-001-E001_feedback/original_marks.py)
