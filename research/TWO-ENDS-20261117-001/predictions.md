# TWO-ENDS-20261117-001: predictions

Frozen at the commit that adds this file, after the advisor's check of the plan (`advisor/plan_answer.md`), before any Part B
computation. Seen before the freeze:
- CARRIER's results, including L₁₂(3, 7), L₁₂(3, 8) ≥ 7 for 8db5da810c00-73 and -79 (certified);
- that stems of depth 2 and 3 give no bond of at most 8 from s = 7;
- KEEP-REACH's reading that, for the 13, pair projections starting below level 3 never become products.

The two pending runs (`CARRIER-A5`, `CARRIER-A6`) had not reported.

- **P1 (the bound-7 run).** For 8db5da810c00-79 at depth 12 there is a bond of at most 7 at s = 7, so L₁₂(3, 7) = 7. The advisor's
  view: "7 or 8, 7 more likely".
- **P2 (depth 13).** 8db5da810c00-73 has no bond of at most 6 at s = 7 or 8 at depth 13, as at depth 12.
- **P3 (automaton size).** For each of the 13, the saturated composite automaton has fewer than 10,000 states (type, composite).
- **P4 (the growth test fails for the 13).** For each of the 13, some non-product composite lies on a cycle of the automaton, so the
  product test does not prove growth. This follows KEEP-REACH's reading that deeper pair projections never become products.
- **P5 (the growth test on forgetting patterns).** For every control pattern that forgets (Theorem F), every composite of at least ℓ₀
  steps is a product, with ℓ₀ at most the forgetting length r plus 1. Theorem F's proof is this test for single orbits.
- **P6 (the third end, B3).** On the 13, exact L at s ≤ 6 is the same at depths 11 and 13 wherever both are decided. For −73 this is
  already known (3, 4, 5, 5, 6, 6 at both), so P6 adds only the other patterns where readings exist.

A failed P1 or P4 is a result, not a defect. If P4 fails, the 13 grow linearly, proved.
