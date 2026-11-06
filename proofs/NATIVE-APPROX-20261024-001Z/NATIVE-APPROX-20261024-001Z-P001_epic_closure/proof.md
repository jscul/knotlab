# Closure of the approximate-counting epic

Status: Proved

Epic `NATIVE-APPROX-20261024-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/NATIVE-APPROX-20261024-001/approximate_counting.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The knot axiom K2 is McQuillan's "strictly terraced" condition: every knot, both pins and the free unary function are strictly terraced. | Elementary; new to the program | `NATIVE-APPROX-20261024-001A-P001`, Lemma 1 |
| 2 | A knot is windable exactly when it excludes at most two tuples or is a parity knot: 26 of the 34 knots. | `candidate-local-delta`; folklore risk medium | `…001A-P001`, Theorem 2; inequality and exact linear feasibility agree on all 34 knots |
| 3 | Given McQuillan's theorem, native counting with pins has a fully polynomial randomized approximation scheme for each of the 26 windable knots. With the four topological knots, which count exactly, 28 knots are settled; 24 of them are hard to count exactly (given Backens) and easy to approximate. | Classical theorem applied; conditional | `…001A-P001`, Corollaries 3 and 4 |
| 4 | The six knots left open form one orbit: the Fibonacci knot with one or two negated places. Their native networks are Fibonacci networks with disequality twists on some edges, and in the Fibonacci basis a twist is a signed reflection, so the count is a signed two-spin sum. | `candidate-local-delta`; folklore risk medium | `NATIVE-APPROX-20261024-001B-P001`, Theorems 1 and 2, Proposition 3; 1,000 networks |
| 5 | Winding, the Fibonacci holographic algorithm and weighted Fibonacci gates all stop at a twist. | Elementary from cited theorems | `…001B-P001`, Proposition 4 |
| 6 | The predicted decay of boundary influence for the six on random native trees did not occur. Without pins the width stayed at 1 on every tree up to depth 16. With pin probability 0.2 the median width was 0.0014 to 0.0025 at depth 12, above the 0.001 threshold, falling by about 0.43 per level. | A recorded computation | `NATIVE-APPROX-20261024-001C-E001`, refuted under its frozen rule; controls passed, independent re-check reproduced the verdict |
| 7 | A knot freezes every native tree without pins exactly when its excluded tuples take both values at every place. Exactly 14 knots do, including the six, not-all-equal and parity, so decay uniform over boundary pins fails for the six without signalling hardness. This explains conclusion 6. | Elementary; folklore risk high | `NATIVE-APPROX-20261024-001D-P001`, Theorem 1, Proposition 2, Corollaries 3 and 4 |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- that being hard to count exactly means being hard to count approximately (false for 24 knots);
- that a probe with uniform boundaries measures decay (false: worst-case boundaries freeze the trees);
- that freezing signals hardness (false: not-all-equal and parity freeze native trees and are easy).

## Recommendation

**Continue with a fresh epic: can native emergence simulate a hub?**
- **The question.** Can networks of the six open knots, with pins, make a soft hub: a three-leg function that puts more weight on 000
  and 111 than on any other value?
- **Why now.**
  - Deciding needs a real hub as well as a knot (`NATIVE-HARDNESS-20261024-001`).
  - An amplifiable soft hub would carry the six to bounded-degree counting with pins, which has no approximation scheme unless
    NP = RP (Dyer, Goldberg, Jalsenius and Richerby).
  - A bound on the hub ratio would point toward approximability.
- **The lead (scratch).** Untwisted Fibonacci gadgets have one spin in the Fibonacci basis, and non-negativity bounds their hub ratio
  by 1. Only a twist can lift it.
- **The first discriminators.**
  - A search of twisted gadgets up to about twelve knots in the signed two-spin form.
  - An attempt to extend the ratio bound to twisted gadgets.
- **Interest:** 2/3.
- **Alternatives:** twists in three dimensions (1/3); a Markov chain beyond winding (1/3); a note on native complexity (1/3).
- **Stop if** no ratio above 1 appears up to twelve knots and no bound can be proved; or if a ratio above 1 appears but cannot be
  amplified.
- **Execution:** deferred to the owner.
