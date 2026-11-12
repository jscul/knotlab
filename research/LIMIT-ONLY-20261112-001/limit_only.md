# Patterns alive only in the limit

Epic `LIMIT-ONLY-20261112-001` (`SHORT-DESC-20261112-001` direction 2; G17, with G7), 2026-11-12, resumed by the owner. Pre-registered
in commit 041ec89b5 before the registered run. The canonical K1–K3 test is unchanged. **Referee pending** (handed to the referee
thread).

## Words

A **nested family**: a description in which a three-port definition holds its own pattern inside each of its knots (SELF), read at
every depth with knots at the bottom. The **bottomless pattern** replaces every SELF forever; it **lives** when some assignment of
all its distinctions satisfies every knot, which by compactness holds iff the main relation is non-empty at the greatest fixed point
reached from "nothing". **Alive only in the limit**: some finite depth allows no state, the bottomless pattern lives. **Up**, **down**,
**equal**, **incomparable**: how the knot compares with its image under one substitution. **P**: the largest tuple of relations
inside the knot that its own image contains. Under the description code (W) shares are properties of the code (A71, A79).

## The question

How often do nested families die at a finite depth while the bottomless pattern lives, which ones, and what decides life at every
depth? The owner's "dying feels like limits".

## The question in standard terms

For iterated hyperedge-replacement families of positive NAE-3-SAT instances capped by the hyperedge: which have an unsatisfiable
finite member while the uncapped infinite limit is satisfiable, and does the greatest post-fixed point below the cap decide
satisfiability at every depth?

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Gates hold.** No family alive only in the limit lacks a self-holding definition whose limit lets its three ends be all equal (L1, Park's coinduction); the criterion by P never fails where the knot and its image compare (proved). | proved; checked on every family | G1 passed |
| 2 | **Small families never die.** All 516,880 one-definition families with at most three calls and three own distinctions live at every depth and in the limit; none has an image strictly inside the knot (82,670 equal, 430,106 up, 4,104 incomparable). | exact, exhaustive over the class | reported |
| 3 | **Under the code, 0.6% of nested families live only in the limit.** 1,341 of 223,261; they are 56% of the 2,381 families that die at some finite depth (replicating SHORT-DESC's 58%). They die at depth 2 (563), 3 (547), 4 (160), 5 (41), deeper (8) or at once (22), and all but one stay dead at every depth after. | exact per family, census frozen | P4 held |
| 4 | **They are mostly not the narrowing kind.** 38% have an image inside the knot (down); 62% are incomparable, where the image already allows the ends all equal. | exact per family, census frozen | P3 failed |
| 5 | **In the limit their self-holding knot sets its ends free.** Of their self-holding definitions' limit relations, 94% are free (all eight states), 5% a knot again, 0.6% ties. Only 10 of the 1,341 (0.7%) have no knot at all in the bottomless pattern. | exact per family | reported |
| 6 | **The criterion by P fails, where expected.** In W, 310 of 2,440 incomparable families (13%) live at every depth although P allows nothing: 193 whose orbit settles outside the knot, 117 with period above 1. In E, 1,320 of 4,104 (32%): 1,296 and 24. | exact per family, census frozen | P2 held |

## Answer

Dying at a finite depth while the bottomless pattern lives is not rare among dying families: under the description code more than
half of the families that die at some depth live in the limit. What decides it is exact and simple to state: the finite patterns
end in knots, which forbid their three ends from being all equal, and the bottomless pattern needs exactly that state somewhere
(proved); in the limit the self-holding knot usually sets its three ends entirely free. Small families (at most three calls) never
die at all. No single fixed-point criterion inside the knot decides life at every depth: it does when the knot and its image compare,
and fails in about a seventh of the rest under the code.

## Reading

**Interpretation, not a theorem.**
- **The owner's "dying feels like limits".** Each finite pattern dies because of the knots at its bottom; the pattern with no bottom
  lives. The death belongs to the cut-off, not to the pattern: every finite approximation of the limit, cut with knots, fails, yet
  the limit does not. That is the exact shape of a limit that no finite stage reaches.
- **What the limit is.** In nearly every case the bottomless pattern frees the knot's three ends: the knot, held inside itself
  forever, stops constraining them. A knot that holds itself without end dissolves at its ends, and only the end-less version lives.

## Lag cutoffs and census-only claims

E: every one-definition family with three ports, 0 to 3 own distinctions, 1 to 3 distinct calls, exhaustive. W: 223,261 families of
1.2 million tries of the description code (main variant). Fates exact at every depth (cycle detection) and in the limit. No claim
for larger bodies beyond W's sample.

## Review

Referee pending (the referee thread). The advisor model reviewed the first draft cold (`advisor_review_answer.md`): the first
conjecture was false in general, and the comparability split, P's iteration and the prior work are its.

## Literature and provenance

Known: compactness; Knaster–Tarski; Park's coinduction (L1 is a one-line case); Cousot and Cousot 1979 (iteration from seeds);
Kozen's mu-calculus; Lengauer and Wanke; Courcelle and Habel, Kreowski and Vogler. Not found: which NAE nested families live only in
the limit, or how often. Classification: known-with-delta.

## Workspace assumptions

A71, A79 used, unchanged.

## Ratio

Substantive: the exhaustive class and the census. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Data

`exhaustive_*.jsonl.gz` and `sample_*.jsonl.gz` (2.3 MB); `census.py --summary` reads them after `gunzip -k`. Conclusion 5's count
of bottomless patterns with no knot was made after the run from the records.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — patterns alive only in the limit | **Status:** Partially successful (referee pending) | G1, P2, P4 held; P3 failed: most are incomparable, not narrowing |
| Local direction — fates of nested families | Continue | An exact rule for incomparable families is open |
| Broader exploration — G17 | Searching | Other lines paused by the owner |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | "Dies at every finite depth, lives in the limit" is located and common among dying families |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71, A79 used.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A rule for incomparable families | 2/3 — Substantial | 2/3 — Testable | Decide life at every depth from the orbit's cycle in closed form for one self-holding definition (16 relations), test it frozen on W → a rule stated without iterating, or none | Selected · awaiting go-ahead |
| 2 | What the bottomless pattern reads | 2/3 — Substantial | 2/3 — Testable | On limit-only families, the least bonds of the bottomless pattern's finite parts against depth → the law counts depth in the limit, or not | Alternative · deferred |

1. Payoff 2: it would finish the classification of nested fates. Concreteness 2: the finite map is known; the closed form is not.
2. Payoff 2: what the law reads in a pattern that lives only without a bottom. Concreteness 2: NEST-READ's readers apply.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
