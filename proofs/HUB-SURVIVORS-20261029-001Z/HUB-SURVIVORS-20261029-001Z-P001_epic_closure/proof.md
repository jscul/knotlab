# Closure of the hub-survivors epic

Status: Proved

Epic `HUB-SURVIVORS-20261029-001` closed on 2026-10-29. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/HUB-SURVIVORS-20261029-001/hub_survivors.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Closing the coordinate permutations of a three-bit knot under intersection reaches a parity relation for "x or (y ≠ z)" and the three-excluded classes with a symmetry of order two, and an equality on two coordinates for twisted not-all-equal; the other classes reach neither. | Elementary, computed | `HUB-SURVIVORS-20261029-001A-P001`, Theorem 1 |
| 2 | Among hub gadgets of at most six copies (legs in one copy each, hidden variables in at least two copies), exactly seven of the 16 classes are rebuilt by their own copies: the two parity classes (from three copies) and the five classes of conclusion 1 (from four). | Candidate local delta (exhaustive census) | `…001A-P001`, Theorem 2 |
| 3 | The monotone atoms (excluding only 000, or only 111) are never rebuilt, at any size. | Elementary | `…001A-P001`, Theorem 3 |
| 4 | Not-all-equal is rebuilt by its copies on the lines of the Fano plane with one point split into the three legs. Every rebuilding hub gadget has at least seven copies, and at seven it is this punctured Fano plane. | Candidate local delta; classical ingredients (property B, m(3) = 7, the Fano plane unique) | `HUB-SURVIVORS-20261029-001B-P001`, Theorems 1 and 4 |
| 5 | The punctured Fano gadget gives each tuple of not-all-equal exactly 5 hidden completions, so not-all-equal is an exact counted fixed point of the Fano substitution. | Candidate local delta (symmetry and a count) | `…001B-P001`, Proposition 5 |
| 6 | With hubs, emergence beyond parity survives patterns of patterns, through parallel copies and, for not-all-equal, through the Fano plane's non-2-colourability. Without hubs only parity survives. | Synthesis | Conclusions 1–5; `GEOMETRY-LAW-20261029-001A` |

## Challenged assumptions

The decision note records three:
- that only parity survives patterns of patterns (true only without hubs);
- that hubs add only fan-out (they enable parallel composition);
- that geometry from a law needs a metric (an incidence geometry, the Fano plane, appears as a minimal self-reproduction).

## Recommendation

**Continue, with a fresh epic on exact self-similar laws.**
- **The question.** Classify the laws whose hub gadgets rebuild them with uniform counts, and their factors. Scoping found factors
  2, 3 and 5 for non-parity classes.
- **Then.** Study what spaces their towers build, starting with not-all-equal's Fano tower.
- **Interest:** 2/3.
- **Alternative:** settle the remaining classes at larger sizes (1/3).
- **Execution:** deferred to the owner.
