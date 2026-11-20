# The clipped exterior on a 128-mark path

All predictions for the longer fixture held on both sides through age eight. The connected component of the old mark and the union of all retained components have different detection ranges. At offset `n+1`, the marked component gains `2n−1` knots under load. At `n+2`, its full typed incidence is isomorphic in the two arms, but the union still gains knots. At `n+3`, the entire marked union is isomorphic. [Frozen follow-up](exterior_validation_design.md)

| Age `n` | Extra knots in the marked component at `n+1` | Extra knots in the whole union at `n+2` |
|---:|---:|---:|
| 1 | 1 | 6 |
| 2 | 3 | 10 |
| 3 | 5 | 11 |
| 4 | 7 | 14 |
| 5 | 9 | 18 |
| 6 | 11 | 22 |
| 7 | 13 | 26 |
| 8 | 15 | 30 |

At age eight the quiet stage contains 4,397 knots and 24,505 distinctions. The loaded stage contains 1,760 knots and 4,513 distinctions. Both are within the physical caps. At offset nine the marked components have 540 quiet and 555 loaded knots. At offset ten, either marked component has 531 knots and 1,108 distinctions in both arms. The whole union at that offset has 1,062 knots and two components quiet, 1,092 knots and 32 components loaded. At offset eleven the unions both have 1,044 knots and 2,178 distinctions, with two components. The portion outside the marked component accounts for the extra union count at offset ten.

We reconstructed the actual bipartite incidence, including distinctions with one holder, and independently computed its hop distances from the original attachment. The existing knot projection agreed on every retained vertex and all sizes. For every equality, a correspondence proposed from the birth rosters gave a complete bijection. Its validation checked each displayed incidence, the distinction and knot types, and preservation of the supplied mark. The tested observation contains no roster labels. Every inequality had a mismatched literal invariant, and no fallback search was needed. There were 108 view comparisons, 60 validated isomorphisms, and 48 inequalities. All 80 specified positive-age predictions and 12 source controls passed. The result is a literal check on the named fixture through age eight. [Checker](../../experiments/DETECTION-PACE-20261119-001/DETECTION-PACE-20261119-001-E001_pace/exterior_check.py) · [Exact sizes and certificates](../../artifacts/DETECTION-PACE-20261119-001/DETECTION-PACE-20261119-001-E001_pace/exterior_check.json)
