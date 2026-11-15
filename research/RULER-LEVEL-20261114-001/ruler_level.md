# Why the reach across levels is one distinction per level

Epic `RULER-LEVEL-20261114-001` (`LEVEL-REACH-20261114-001#1`, approved by John 2026-11-14 17:46 UTC; G17, with G1), 2026-11-14 to
15. Proof note: [proof.md](../../proofs/RULER-LEVEL-20261114-001A/RULER-LEVEL-20261114-001A-P001_forest_ruler/proof.md). The canonical
K1–K3 test is unchanged. **Refereed** (RULER-LEVEL-R1, `referee-R1/report.md`, commit a0cbaa38f): **confirmed with fixes**, one
Block (an overview sentence) and Narrowings, folded in below and logged in `docs/CORRECTIONS.md`.

## The question

`LEVEL-REACH-20261114-001` found the ruler, a least bond of s + 2 from a level to the level s below, the most common reach across
levels. Why, and for which patterns?

## Answer

A sufficient condition: no cycle of knots and a descending chain. **Theorem A\*\*** (proved, from the program's theorem on patterns with
no cycle of knots, `RANDOM-FATES-20261112-001B` T1): if a pattern whose knots lie within a level or join adjacent levels has no cycle of
knots, its reach from level k to level k + s is L_k(s) = D_k(s) + 2, where D_k(s) ≥ s is the fewest knots on a path from level k to level
k + s; it is s + 2 exactly when a chain of s knots steps down one level at a time, and there is no bond when no path joins the levels.
*(Completed after the referee, Block on the overview sentence: "and there is no bond otherwise" was false; an acyclic pattern joined
only by a longer path has a larger finite bond, e.g. knots {0, 00, 01}, {00, 10, 11}, {10, 000, 001} at N = 3: a three-knot path and
reach 5. No census case is of this kind.)* **Theorem A** (proved): one placement of the tree type ((g, plain), (h₁, ·0), (h₂, ·1))
always gives a full binary tree across levels, so a ruler at every depth. In the census, read at depth 9, the acyclic case accounts for
299 of the 457 rulers (65.4% by description, 65.1% by weight); at every depth only Theorem A's form is covered, 117 of 457 (25.6%; 36.5%
by weight), and that form is tested syntactically (a description such as 2d27fb6fcfa3…, the bare tree at every depth after discarding a
placement that places nothing, fails the test). The other 158 rulers have cycles of knots. Within-level knots can shorten the finite
profile (five reproduced small random cases and one logged only; every failure shortens, none lengthens, and three levels cannot show a
rate). Why the cyclic rulers stay rulers is open. *(Wording narrowed after the referee.)*

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem A**: no cycle of knots gives L_k(s) = D_k(s) + 2 (s + 2 with a descending chain; no bond without a path) | proved (from T1) |
| 2 | Theorem A: one tree-type placement gives a full binary tree across levels at every depth | proved; checked on 2,000 random descriptions, ruler on 20 (the referee: 840 more, exact L 24 of 24 at N = 6, 7) |
| 3 | Census at depth 9: 299 of 457 rulers acyclic (65.4%; 65.1% by weight); all 546 acyclic descriptions as the formula gives (a census check, not evidence: the formula fixes acyclic outcomes, and no acyclic pattern is dead) | computed; reproduced by the referee on all 1,288 |
| 4 | Within-level knots can shorten the finite profile: [2,2,2], [3,3,3], [3,3,4], [3,4,4] twice among five reproduced small random cases with one tree placement (a sixth, [3,3,4], logged without its key) | computed, exploratory |

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — why the ruler | **Status:** Partially successful | The complete formula for acyclic patterns; the cyclic rulers open |
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
committed slim records) and the breaking cases (five reproduced, one logged only). Least sure: (a) the use of T1's distance (knots on the path) as the level count;
(b) Theorem A's acyclicity argument; (c) the census coverage relies on the pattern builder `pattern.py` of the reach code.
