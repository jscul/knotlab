# Patterns alive only in the limit: pre-registration

Epic `LIMIT-ONLY-20261112-001` (`SHORT-DESC-20261112-001` direction 2; G17, with G7), 2026-11-12, resumed by the owner ("Let's start
with that one"). Frozen before the registered run. The canonical K1–K3 test is unchanged. The law is not-all-equal (NAE) on
three-place knots; the language is SHORT-DESC's (`dlang.py`), whose code is one weighting of many (A71, A79).

## The question

A nested family is a description in which a three-port definition holds its own pattern inside each of its knots (SELF). At depth
t the bottom SELF calls are knots. Some families have no allowed state at some finite depth, yet the **bottomless pattern** lives.
How often, which ones, and what decides it: the owner's "dying feels like limits".

## What "lives in the limit" means

The bottomless pattern replaces every SELF forever, so it has infinitely many distinctions and no knot at the bottom. It **lives**
when some assignment of all its distinctions satisfies every one of its knots (K3 for the infinite system; no knot or source claim
is made). By compactness this holds iff every finite part allows a state, and every finite part lies in a bottomless truncation (SELF
at the bottom dropped), so it holds iff the main relation is non-empty at the greatest fixed point G reached from "nothing".

## In standard terms

For iterated hyperedge-replacement families of positive NAE-3-SAT instances, capped at the bottom by the hyperedge itself: which
families have an unsatisfiable finite member while the infinite (uncapped) limit is satisfiable; a fixed-point criterion for
satisfiability at every depth, and where it fails.

## Settled by definition or known (stated, not tested)

- Alive at every finite depth implies a living limit: the knot allows less than "nothing", and substitution is monotone. Compactness,
  the limit as a greatest fixed point (Knaster–Tarski) and this direction are standard; ours is only the other cell, where finite
  depths die through the knots at their bottom, which the bottomless pattern never has.
- **L1** (Park's coinduction, one line): if every self-holding definition's limit relation lies inside the knot, every depth lives;
  so a family alive only in the limit has a definition whose limit relation lets its three ports be all equal, the one state the
  knot forbids. A **gate** (0 exceptions, else the code is wrong).
- **L2's exact part.** Let P be the largest tuple of relations inside the knot with P inside its image Φ(P) (iterate X ↦ knot ∧ Φ(X)
  from the knot). If the main relation is non-empty at P, every depth lives (P ⊆ Φ^t(P) ⊆ Φ^t(knot)). If the knot lies inside its
  image ("up"), depths only widen and P is the knot; if the image lies inside the knot ("down"), depths narrow to P. In both cases
  "alive at every depth iff main(P) non-empty" is proved, a **gate**. Where the knot and its image do not compare it can fail (the
  advisor's example: D = [a = b = c] ∧ SELF on three own distinctions). Every orbit is eventually periodic and is decided exactly by
  cycle detection.
- After SHORT-DESC's referee, 98% of nested families under the code are "up" and never die after depth 1: families alive only in the
  limit live in the remaining few, and every share under the code is a property of the code.

## Classes and readings (frozen in `census.py`)

**E**: every one-definition family with three ports, 0 to 3 own distinctions and one to three distinct calls (knots as unordered
triples, SELF as ordered triples, at least one SELF): about 517,000, each decided exactly. **W**: families drawn by the description
code (main variant), 8 workers × 150,000 tries, fresh seeds (sha256 of "LO" and the worker). Per family: fate over finite depths,
the limit, comparability (equal, up, down, incomparable), L1, L2 and, for each L2 failure, its kind (period above 1; the orbit's
fixed point outside the knot; other).

## Predictions (frozen)

The advisor model reviewed the first draft cold (`advisor_review_answer.md`): it showed the first conjecture false in general, gave
the comparability split and the P iteration, and named the prior work below; this design is its. No second review.

| # | Prediction | Fails when |
| --- | --- | --- |
| G1 | Gate: L1 has no exception; L2 has no failure in any family whose knot and image compare. | any |
| P2 | **The criterion's failure occurs under the code.** At least one family in W fails L2. | none |
| P3 | **Families alive only in the limit are mostly ones whose image lies inside the knot.** At least half of them are "down", in E and in W. | below half in either |
| P4 | **Most finitely dying families live in the limit** (a replication: SHORT-DESC measured 58% under the code). In W, at least half of the families that die at some finite depth live in the limit. | below half |
| — | Reported: counts by comparability and fate; L2 failures by kind and among incomparable families; first death depths and limit kinds of the families alive only in the limit; the smallest such families in E, as examples. | — |

## Prior work

Compactness of propositional logic; Knaster–Tarski; Park (coinduction); Cousot and Cousot 1979 (iteration from seeds, where only
pre- or post-fixed seeds give chains); Kozen's mu-calculus (least against greatest fixed points); Lengauer and Wanke (bottom-up port
tables of hierarchical graphs); Courcelle and Habel, Kreowski and Vogler (hyperedge-replacement grammars). Not found: which NAE nested
families live only in the limit, or how often.

## Plumbing (disclosed)

Two plumbing runs (1/200 of E, deterministic, and 3,000 tries of W with seed 99, scratch output) checked counts, timing and that the
summary runs; no outcome was looked at. The 1/200 of E is part of the registered run.

## Stop rule and runtime

One run (E on 8 workers, W on 8 workers), its summary, a hand-off to the referee thread, report. A few minutes.
