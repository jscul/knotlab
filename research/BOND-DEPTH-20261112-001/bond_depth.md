# Counting inside: least bonds across depths

Epic `BOND-DEPTH-20261112-001` (`NEST-COUNT-20261112-001` direction 1; G17, with G1), 2026-11-12 to 13, at the owner's go-ahead.
Pre-registered in commit c717335c4 before the registered run. The canonical K1–K3 test is unchanged. **Referee pending** (handed to
the referee thread).

## Words

As in the pre-registration: the **ray** of copies C_0, C_1, … (each made by the first SELF call of the one before), a **ray bond**
(a bond among the ray's own distinctions containing a top port and an own distinction of C_s), L(s) its least size, and the classes
**bounded** and **growing** (an exact repeat of the DP's normalised costs, with gain 0 or more) and **undetermined within 30**.

## The question

Inside a nested pattern, does the law's reach from the top to depth s keep growing, or level off, and which is typical?

## The question in standard terms

The least size of a minimal non-shattered set containing a root vertex and a vertex at derivation depth s, along one derivation
ray, in the satisfying assignments of infinite iterated hyperedge-replacement NAE instances.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The method is exact and validated.** It agrees with exhaustive search on 120 of 120 cases and gives steps apart + 2 on chains with no cycle of knots. | computed | G passed |
| 2 | **In 204 of 664 families (31%) the reach is bounded, exactly.** The least ray bond settles at 3 (173 families), 2, a tie (30), or 4 (1), from depth 2 to 22; this transfers to the true least bond. | exact per family | P1 failed (below half) |
| 3 | **No family was shown to grow.** No repeat with a positive gain was found within depth 30. | exact per family, depth ≤ 30 | reported |
| 4 | **Within depth 30, reach grows steadily in 240 families (36%).** Their least ray bonds rise by about one member every level (55 families, 29 over 29 levels, as a ruler) or every two levels (71), or every three (29), steadily over the last ten levels; these are upper bounds on the true least bond and readings to depth 30, not proved rates. | exact per depth, depth ≤ 30 | reported |
| 5 | **In 163 more (25%) the reach is flat within depth 30** without a proven repeat. 44 families passed the cap of 20,000 states, 11 did not finish (stopped after three and a half hours), and 2 have no ray bond. | exact per depth | reported |

## Answer

Inside these nested patterns the law's reach does both. In about a third of the families it is exactly bounded: some distinction
two or three members away from the top constrains every depth, however deep. In another third, read to depth 30, it grows steadily,
by one member every level or two, the way it grows along a ruler, though the method has not proved that this continues; and a
quarter stay flat to depth 30 without proof. So, within depth 30, counting inside (the law's reach lengthening with depth) appears in more
than a third of the families read; whether it lasts in them is not settled, and no share of the full weighting is claimed.

## Reading

**Interpretation, not a theorem.**
- **For the owner's nested parts.** Where the reach is bounded, the top is tied to every depth through two or three distinctions:
  the larger pattern holds the smaller ones close. Where it grows, each level adds to the distance, as a count would.
- **What is not shown.** "Growing" here is within depth 30 and along one ray; side branches could shorten the true bond.

## Lag cutoffs and census-only claims

The 664 one-definition genuine families; the ray of first SELF calls; endpoints minimised over the top ports and the depth-s copy's
own distinctions; depths to 30. Run note: twelve helper workers were added at 01:35 UTC on the remaining families with the frozen
`run_family` unchanged (`helper_after_start.py`), records merged by family (duplicates identical); the last 11 families were stopped
at 03:33 UTC and are counted unfinished.

## Review

Referee pending (the referee thread). The advisor model reviewed the method cold (`advisor_review_answer.md`): it confirmed the
DP's minimality condition, showed growth is eventually linear or bounded per family, and suggested the cycle-mean computation and the
exact side-branch extension.

## Literature and provenance

Known: bonds as minimal non-shattered sets (Sauer–Shelah, Pajor); bounded-treewidth 2-QBF DPs (Chen; Pan and Vardi); min-plus
eventual periodicity. Not found: the growth of least bonds with depth in nested NAE patterns. Classification: known-with-delta.

## Workspace assumptions

A79 used.

## Ratio

Substantive: the method and its validation, the reading of 653 families. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — least bonds across depths | **Status:** Partially successful (referee pending) | Method exact and validated; P1 failed: 31% bounded exactly, 36% growing within 30 |
| Local direction — counting inside | Continue | The growing families need a proved rate |
| Broader exploration — G17 | Searching | The full census of 223,261 families waits on a faster method |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The law's reach inside nested patterns is measured exactly along a ray |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A79 used.
**Basket:** `CHEAP-COUNT-20261112-001#1` (counting with three distinctions per position; 2/3 Payoff, 2/3 Concreteness),
`PREFIX-END-20261112-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `LIMIT-ONLY-20261112-001#1` (2/3, 2/3),
`NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Proved rates for the growing families | 3/3 — Breakthrough-scale if the growth is proved | 3/3 — Ready | Compute the minimum cycle mean of each family's state graph (Karp), with side branches included bottom-up (the advisor's method) → a proved rate per family, or a bound | Selected · awaiting go-ahead (a good first Codex hand-off) |
| 2 | The full census | 2/3 — Substantial | 2/3 — Testable | Run the proved-rate method on the 223,261 drawn families → typical shares of bounded and growing reach | Alternative · after #1 |

1. Payoff 3: it would prove that the law counts inside a nested pattern, typically, without counting from its ends. Concreteness 3:
   the method is written; the cycle mean is standard.
2. Payoff 2, Concreteness 2: needs #1's speed.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
