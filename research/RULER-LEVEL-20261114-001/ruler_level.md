# Why the reach across levels is one distinction per level

Epic `RULER-LEVEL-20261114-001` (`LEVEL-REACH-20261114-001#1`, approved by John 2026-11-14 17:46 UTC; G17, with G1), 2026-11-14 to
15. Proof note: [proof.md](../../proofs/RULER-LEVEL-20261114-001A/RULER-LEVEL-20261114-001A-P001_forest_ruler/proof.md). The canonical
K1–K3 test is unchanged. **Referee pending.**

## The question

`LEVEL-REACH-20261114-001` found the ruler, a least bond of s + 2 from a level to the level s below, the most common reach across
levels. Why, and for which patterns?

## Answer

Exactly where the knots form no cycle. **Theorem A\*\*** (proved, from the program's theorem on patterns with no cycle of knots,
`RANDOM-FATES-20261112-001B` T1): if a pattern whose knots lie within a level or join adjacent levels has no cycle of knots, its reach
from level k to level k + s is s + 2 whenever a chain of s knots steps down one level at a time, and there is no bond otherwise.
**Theorem A** (proved): one placement of the tree type ((g, plain), (h₁, ·0), (h₂, ·1)) always gives a full binary tree across levels,
so a ruler at every depth. In the census at depth 9 this accounts for 299 of the 457 rulers (394 of the 605 ruler weight; 117 at every
depth by Theorem A), and for every acyclic description's outcome. The other 158 rulers have cycles of knots; cycles can also break
the ruler, shortening it to a constant or halving its rate (6 of 57 decided small random cases, computed). Why the cyclic rulers stay
rulers is open.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem A**: no cycle of knots plus a descending chain gives L(s) = s + 2; no path gives no bond | proved (from T1) |
| 2 | Theorem A: one tree-type placement gives a full binary tree across levels at every depth | proved; checked on 2,000 random descriptions, ruler on 20 |
| 3 | Census at depth 9: 299 of 457 rulers acyclic (394 of 605 weight); all acyclic outcomes as the theorem gives; every direct, other, undecided and dead description cyclic | computed |
| 4 | Cycles break the ruler both ways: [2,2,2], [3,3,3], [3,3,4], [3,4,4] among small random descriptions with one tree placement and within-level knots | computed, exploratory |

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — why the ruler | **Status:** Partially successful | Proved for every acyclic pattern; the cyclic rulers open |
| Local direction — rulers with cycles | Continue | 158 cyclic rulers and the breaking cases give a sharp question |
| Broader exploration — G17 nested line | Known alternatives | Joins the knots-alone ruler and the hypertree theorem |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Two thirds of the census's rulers are explained by a theorem |

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A82 used.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Rulers with cycles | 2/3 — Substantial | 2/3 — Testable | Test the advisor's discriminator (no cycle passes through two members of one chain knot) on the 158 cyclic rulers and the breaking cases → a proved condition, or the cases it misses | Selected · awaiting go-ahead |
| 2 | Undecided reach in bounded patterns | 2/3 — Substantial | 2/3 — Testable | As in `LEVEL-REACH-20261114-001#2` | Alternative · deferred |

1. Payoff 2: would explain the remaining third of the rulers and say when cycles shorten the reach. Concreteness 2: the discriminator is
   computable on the census's descriptions; a proof needs an upper and a lower bound of its own.
2. As recorded.

**Recommendation.** Research directions, #1, awaiting the go-ahead.

## Hand-off to the referee

Folder: this one (note, advisor Q/A, `exploratory/`); the proof family `proofs/RULER-LEVEL-20261114-001A/` (`proof.md`, `check.py`,
`result.json`). Proved: Theorems A** and A (A** applies T1 of `RANDOM-FATES-20261112-001B`). Computed: the census accounting (from the
committed slim records) and the six breaking cases. Least sure: (a) the use of T1's distance (knots on the path) as the level count;
(b) Theorem A's acyclicity argument; (c) the census coverage relies on the pattern builder `pattern.py` of the reach code.
