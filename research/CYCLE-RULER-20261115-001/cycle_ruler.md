# Rulers with cycles: what the first checks show

Epic `CYCLE-RULER-20261115-001` (`RULER-LEVEL-20261114-001#1`; G17, with G1), 2026-11-15, at the coordinator's go-ahead; small checks
and thinking only, on committed census records. The canonical K1–K3 test is unchanged. **Referee pending** (light).

## The question

Of `LEVEL-REACH-20261114-001`'s 457 rulers, 299 have no cycle of knots and are explained by `RULER-LEVEL-20261114-001`'s Theorem A**.
Why do the other 158, which have cycles, stay rulers, while cycles shorten or halve the reach in other patterns?

## Findings

| # | Finding | Kind |
| --- | --- | --- |
| 1 | **The advisor's discriminator does not separate.** In every cyclic census description, rulers (158) and non-rulers alike (direct 100, other 73, dead 23, undecided 264), some cross-level knot lies on a cycle of knots (a biconnected block holding another knot); only 14 cyclic "no bond" descriptions have none. | computed (`exploratory/discriminator.py`) |
| 2 | **Nor does girth.** Every cyclic ruler and non-ruler read on levels 0 to 7 has Berge girth 2: two knots sharing two distinctions. | computed (`exploratory/girth.py`) |
| 3 | **The smallest shortening is a closed fork.** In the smallest of six small breaking cases (one tree placement plus within-level knots; levels 0 to 6, top level 1), the bond {0, 001, 011} of size 3 at s = 2 (the ruler would need 4) has a core of 7 knots: the top's knot to its two children, one knot down from each child, and four within-level knots at the target level, two of them sharing two distinctions, that join the two branches. The top reaches the target level along both branches at once, and the within-level knots close them. | computed (`exploratory/cores.py`) |
| 4 | **Other shortenings are global.** The other breaking cases' cores hold 16, 18, 153 and 162 knots, mostly within-level: the shortening there comes from a level's whole within-level pattern, not a local motif. | computed |

## Reading

A cycle of knots is not by itself what breaks the ruler, and short cycles are everywhere in this census. What the smallest case shows is
a closed fork: both children of one cross-level knot descend and are joined again by within-level knots, so a bond can take one member
per branch instead of a chain. The larger cases point to the within-level patterns' own constraints, which a statement about cycles
alone cannot see.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — why cyclic rulers stay rulers | **Status:** Inconclusive | The proposed discriminator and girth fail; the smallest breaking case is a closed fork |
| Local direction — structural conditions on cycles | unresolved | Breaking cases range from 7-knot forks to global effects |
| Broader exploration — G17 nested line | Known alternatives | Theorem A** stands for acyclic patterns |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | no demonstrated advance | No condition found for the cyclic third |

**Corrections:** none. **Goals:** a G17 checkpoint (no demonstrated advance). **Assumptions:** none.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Closed forks | 2/3 — Substantial | 2/3 — Testable | Count, in each cyclic census description, closed forks within s levels (both children of a cross-level knot rejoined by knots no deeper than the target) → absent in the cyclic rulers and present in the shortened ones, or not | Selected · awaiting go-ahead |
| 2 | Levels' own state sets | 2/3 — Substantial | 1/3 — Speculative | For a tree plus within-level knots, read each level's within-level states on sibling pairs and test whether "every sibling pattern extends" predicts the ruler → a condition, or none | Alternative · deferred |

1. Payoff 2: a local condition for the ruler with cycles. Concreteness 2: computable on committed records in minutes.
2. Payoff 2; Concreteness 1: the larger cores suggest it, but no statement is in hand.

**Recommendation.** Research directions, #1, awaiting the go-ahead.

## Review

Referee pending (light). Advisor not consulted (no statement frozen). Objects search: nearest `RULER-LEVEL-20261114-001`,
`BOND-CHAIN-20261108-001`, `KNOT-CIRCUITS-20261020-001`; none reads cycles across levels.
