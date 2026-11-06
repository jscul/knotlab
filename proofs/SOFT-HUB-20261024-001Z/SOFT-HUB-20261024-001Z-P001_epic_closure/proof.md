# Closure of the hub-imitation epic

Status: Proved

Epic `SOFT-HUB-20261024-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/SOFT-HUB-20261024-001/imitating_a_hub.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | No native gadget of any knot is an exact hub on three or more legs: its support is co-independent and excludes at most half its values. | Elementary; folklore risk high | `SOFT-HUB-20261024-001A-P001`, Theorem 1 |
| 2 | For every gadget of every knot and every axis, pairs whose difference does not link all three terminals map injectively onto split patterns, so F(u)F(ū) is at most the split products plus the linked pairs; every linked pair branches at a knot with antipodal local tuples, and parity has none. | Elementary; folklore risk high | `…001A-P001`, Lemmas 2 and 3; 439,439 pairs in the check |
| 3 | Gadgets of windable knots have hub ratio at most √3 (given McQuillan); parity and no-lone gadgets at most 1, the latter through the Fibonacci recurrence f₂ = f₀ + f₁. | Classical theorem applied (windable); elementary (others) | `…001A-P001`, Theorems 4 and 5 |
| 4 | The eight non-windable knots are a closed neighbourhood plus the antipode of its centre (0, 1 or 3 defects); only whole difference components can be exchanged, so in the six open knots linked pairs pass through knots empty on one side and full on the other. | Elementary; new to the program | `…001A-P001`, Proposition 6 |
| 5 | Among gadgets of an open knot (annealing on all axes up to 40 knots, 100,000 random gadgets), the best hub ratio is 65/53 ≈ 1.23; no axis combines a windability violation with ratio above 1; linked pairs never exceed M_u²; compositions of the best hubs do not amplify. | A recorded computation | `SOFT-HUB-20261024-001B-E001`, supported; controls passed, independent re-check reproduced the verdict |
| 6 | Every tree gadget of an open knot satisfies F(u)F(ū) ≤ s_u + F(u + eᵢ)F(ū) + F(u)F(ū + eᵢ), so its hub ratio is at most 3; tree gadgets reach 12/11. | `candidate-local-delta`; folklore risk medium | `SOFT-HUB-20261024-001C-P001`, Theorem 1 and Corollary 2 |
| 7 | With a cycle the one-sided reroute is not injective (an explicit seven-knot gadget); the inequality for all gadgets is a conjecture, true on 48,000 random cases and all gadgets of conclusion 5. | Obstruction and conjecture | `…001C-P001`, Proposition 3 and Conjecture 4 |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- that a soft hub above ratio 1 would make approximation hard (refined: amplification is what matters, and none appears);
- that small random searches settle hub questions (false: annealing finds 65/53 where gadgets of up to seven knots showed 1);
- that the open knots are more hub-capable than windable ones (not supported).

## Recommendation

**Continue with a fresh epic: hubs with loops.**
- **The question.** Does the arm inequality, and so hub ratio at most 3, hold for gadgets of the open knots with cycles?
- **Why now.**
  - It is the only open part of "emergence cannot imitate reuse".
  - The one-sided reroute works on trees and fails as constructed with cycles.
- **The first discriminator.** Anneal directly for violations of the arm inequality, maximizing the ratio of its two sides, up to 40
  knots.
- **The proof routes.**
  - A fractional reroute averaging over all routes of an arm.
  - Induction on loops by self-gluing, with a multi-terminal inequality.
- **Interest:** 2/3.
- **Alternatives:** approximation schemes for the six by Markov chains (1/3); twists in three dimensions (1/3); a note on native
  complexity (1/3).
- **Stop if** no violation appears and neither proof route closes within one epic.
- **Execution:** deferred to the owner.
