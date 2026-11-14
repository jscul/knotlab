# Rigidity at every level for the alternating addressed patterns: what blocks a proof

Epic `RIGID-LEVEL-20261114-001` (`LEVEL-RETURN-20261113-001#2`; G17, with G8), 2026-11-14, at the coordinator's go-ahead, as a
bounded proof attempt (about two hours, thinking and small checks only, beside `LEVEL-REACH-20261114-001`'s run). The canonical K1–K3
test is unchanged. **Referee pending** (light: the claims below are small computations and a record of an obstruction).

## The question

`LEVEL-RETURN-20261113-001` certified that description #2's pattern without its two special knots (at even levels) and its full
pattern (at odd levels) have only the parity state and its complement, at levels 6 to 14 and 7 to 13; with the referee's proof that
parity violates exactly two knots at every even level, rigidity at an even level implies death there. Can rigidity be proved at every
level?

## Answer

Not within the attempt. Rigidity stays **certified for n ≤ 14 and conjectured beyond**. What blocks a uniform proof, each point checked:

| # | Finding | Kind |
| --- | --- | --- |
| 1 | **The constraint is not affine.** With g = f XOR parity each knot says "the apex agrees with at least one of the same-parity pair"; it forbids (t, t, ¬t) and allows the other six, which is not closed under XOR, so no GF(2) argument applies directly (the advisor's, checked). | proved (by hand) |
| 2 | **One-sided closure is inert.** The closure of a single knot's pair under "both in ⇒ apex in" holds only 3 to 5 addresses at levels 5 to 12, so a refutation must branch on both classes; the pair graph is not bipartite (levels 5 to 12), so every non-trivial split puts some pair inside one class. | computed (`exploratory/closure.py`) |
| 3 | **Propagation needs growing depth.** The first lemma a proof would need, "no defect under flipping the second letter" (f(A) ≠ f(A ⊕ e₂) for every A), is not refuted by unit propagation or by failed-literal probing of depth 1 at levels 6, 8, 10 (36 sampled A), and depth 2 refutes 3 of 6 at level 6 and 0 of 3 at level 8. | computed (`exploratory/probe.py`) |
| 4 | **Proof sizes outgrow the pattern.** CaDiCaL's LRAT proofs of rigidity have 97, 817, 16,610, 60,561 and 2,364,396 steps at even levels 6 to 14 (the pattern grows fourfold per two levels; the proof eight to forty-fold), and 477, 5,263, 13,144, 707,181 at odd levels 7 to 13. | computed (from `LEVEL-RETURN`'s rigidity run) |
| 5 | **The natural inductions fail.** Solutions do not project along the two-to-one map between levels; the prefix decomposition leaves the placement set (the section of q1q1 at 0 is q2q2) and a knot's members can start with different letters, so after k letters 2^k functions are coupled (the advisor's, checked for one step). | proved for one step (by hand) |

So no bounded-depth, automatic derivation of "g constant" is in sight: the evidence (points 3 and 4) points to a global obstruction
rather than a local one, which fits the pattern's exponential activity (the interface between halves is the whole level).

## Lag cutoffs

Probing at three levels and a few dozen sampled addresses; proof sizes from one solver, not minimal proofs. Nothing here proves that
no uniform proof exists.

## What would still be worth trying

The advisor's route B: write f at level n + 2 as four functions on level n (the two tail letters) and check whether the twisted
patterns this produces form a finite family closed under the two-letter step; if they do, rigidity or death of each member is a
finite product-automaton check. Its first test (the tail lemma f(x·ab) = f(x·00) + a + b) is implied by rigidity, so it may be as hard
as the theorem. Recorded as a direction, not started.

## Review

Referee pending. The advisor model was consulted once (`advisor_question.md`, `advisor_answer.md`): points 1 and 5, route A (adopted:
points 3 and 4) and route B are its; its stop rule (exponential proof growth and growing probing depth: record and stop) was applied.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — rigidity at every level for #2 | **Status:** Inconclusive | Certified to 14; every route tried needs depth that grows with the level |
| Local direction — local derivations of rigidity | practically exhausted | Propagation depth and proof size grow with the level |
| Broader exploration — G17 nested line | Known alternatives | The reach census is running; rigidity is its direct extreme |
| Long-term goal — G17 Typical and rare meeting patterns (with G8) | obstruction learned | Rigidity here looks global, not automatic |

**Corrections:** none. **Goals:** a G17 checkpoint (obstruction learned); no goal change. **Assumptions:** none.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Reach across levels | 3/3 — Breakthrough-scale | 2/3 — Testable | `LEVEL-REACH-20261114-001`'s registered run, under way → its summary | Selected · started |
| 2 | Twisted families across two levels | 2/3 — Substantial | 1/3 — Speculative | Enumerate the twisted patterns of the two-letter step at levels 5 to 9 → a finite family closed under the step (then a product check), or growth | Alternative · deferred |

1. Under way; John approved it.
2. Payoff 2: it would turn rigidity, and so the death at every even level, into a finite check. Concreteness 1: the family may not be
   finite, and its first test is implied by the theorem.

**Recommendation.** Research directions, #1 (started); #2 deferred.
