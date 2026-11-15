# Rulers with cycles: what the first checks show

Epic `CYCLE-RULER-20261115-001` (`RULER-LEVEL-20261114-001#1`; G17, with G1), 2026-11-15, at the coordinator's go-ahead; small checks
and thinking only, on committed census records. The canonical K1–K3 test is unchanged. **Refereed** (CYCLE-RULER-R1, light,
`referee-R1/report.md`, commit 2006e5cef): **confirmed with fixes**, no Block; Narrowings folded in below.

## The question

Of `LEVEL-REACH-20261114-001`'s 457 rulers, 299 have no cycle of knots and are explained by `RULER-LEVEL-20261114-001`'s Theorem A**.
Why do the other 158, which have cycles, stay rulers, while within-level knots shorten the profile in other patterns?

## Findings

| # | Finding | Kind |
| --- | --- | --- |
| 1 | **The advisor's discriminator does not separate.** *(Narrowed after the referee: the script tested something weaker, any cross-level knot on a cycle over levels 0 to 9, not the knots of a descending chain from level 3; recomputed as stated, no cyclic ruler (0 of 158) has a cycle-free descending chain at any s, nor any cyclic non-ruler (one undecided has one at every s), so the conclusion survives.)* In every cyclic census description, rulers (158) and non-rulers alike (direct 100, other 73, dead 23, undecided 264), some cross-level knot lies on a cycle of knots (a biconnected block holding another knot); only 14 cyclic "no bond" descriptions have none. | computed (`exploratory/discriminator.py`) |
| 2 | **Nor does girth.** Every cyclic ruler and non-ruler read on levels 0 to 7 has Berge girth 2: two knots sharing two distinctions. | computed (`exploratory/girth.py`) |
| 3 | **The smallest shortening is a closed fork.** In the smallest of the five analysed breaking cases (a sixth was logged without its key; all from one sample of 80, 57 decided) (one tree placement plus within-level knots; levels 0 to 6, top level 1), the bond {0, 001, 011} of size 3 at s = 2 (the ruler would need 4) has a core of 7 knots: the top's knot to its two children, one knot down from each child, and four within-level knots at the target level, two pairs of which share two distinctions (*corrected after the referee*), that join the two branches; the referee confirmed the core minimal and the bond a true bond in the full 245-knot pattern. The top reaches the target level along both branches at once, and the within-level knots close them. | computed (`exploratory/cores.py`) |
| 4 | **Other shortenings are global.** The other analysed cases' cores hold 16, 18, 153 and 162 knots (their minimality not independently checked), mostly within-level: the shortening there comes from a level's whole within-level pattern, not a local motif. | computed |

## Closed forks counted (2026-11-15, the coordinator's one further step)

A cross-level knot whose upper member lies at a level 3 to 6 is a **closed fork** when its two lower members are joined by other knots
lying wholly in the levels below it, up to level 7 (`exploratory/forks.py`, computed on the committed records, minutes). Among cyclic
census descriptions: rulers 97 without a closed fork and 61 with; direct 18 without, 82 with; other 10 without, 63 with. Closed forks
go with shortened or broken reach (84% of the cyclic non-rulers against 39% of the cyclic rulers), but they do not separate: 61 rulers
have them and 28 non-rulers do not. As agreed, the cyclic line stops here; the open question is backlog B180.

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
| 1 | Closed forks | 2/3 — Substantial | 2/3 — Testable | Count closed forks within the levels read on the cyclic census descriptions → done: associated, not separating (above) | Selected · started (done) |
| 2 | Levels' own state sets | 2/3 — Substantial | 1/3 — Speculative | For a tree plus within-level knots, read each level's within-level states on sibling pairs and test whether "every sibling pattern extends" predicts the ruler → a condition, or none | Alternative · deferred |

1. Payoff 2: a local condition for the ruler with cycles. Concreteness 2: computable on committed records in minutes.
2. Payoff 2; Concreteness 1: the larger cores suggest it, but no statement is in hand.

**Recommendation.** Research directions; #1 done without separating; the cyclic line stops and the question is backlog B180; take stock.

## Review

Refereed (light; above). Advisor not consulted (no statement frozen). Objects search: nearest `RULER-LEVEL-20261114-001`,
`BOND-CHAIN-20261108-001`, `KNOT-CIRCUITS-20261020-001`; none reads cycles across levels.
