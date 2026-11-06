# Closure of the counting-on-Seymour's-bound epic

Status: Proved

Ticket `SEYMOUR-COUNT-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes
no new claim. The decision note is `research/SEYMOUR-COUNT-20261030-001/counting_on_seymours_bound.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Three non-colourable cubic pieces glued along a square (a trisum, all square edges deleted) have amplitude ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃. Here (α, β) splits a piece's colourings by which square point its far line leans to: not-all-equal on the leanings. | new (no overlap found) | A-P001, Theorem 3 |
| 2 | Seen from the square's other line, a piece's split is swapped; pieces glued at another square act only as weights on a piece's two leanings. | new | A-P001, Propositions 4–5 |
| 3 | In a cubic Pfaffian brace every trisector is independent and on no 4-cycle, with exactly three components. Splitting along trisectors ends in planar braces, with disjoint squares forming a tree. | consequence of Robertson–Seymour–Thomas | B-P001, Lemma 1 |
| 4 | A branch's leaning split is the absolute value of one weighted, row-restricted determinant of its planar leaf, the branches beyond its other squares giving the weights. | new; Lemma 4 (weighted Berman) is immediate from Berman | B-P001, Proposition 3, Lemma 4 |
| 5 | For every three-fold space and line L, #col(H − L) is computable in polynomial time without any signing (two determinants per planar leaf), and so is the knot's exactness factor λ(0). | new (no source found; folklore risk moderate) | B-P001, Theorem 5, Corollary 6 |
| 6 | The implementation matches direct counts on 67 braces, 7 three-fold spaces (22 to 118 points) and trisums to 480 vertices. It counts 1720-vertex instances where variable elimination would need factors on 30 variables. | computation | B-P001, check.py |

## Recommendation

**Continue**, as a fresh epic: counting one twist off the bound (2/3).
- **The setting.** Keep a three-fold space's incidence graph, and change its sign class away from the Pfaffian one. The system becomes
  colourable.
- **The question.** Is counting still polynomial for every sign class, or #P-hard for some family? The first answer puts tractability in the
  graph; the second makes the knot's non-colourability itself the boundary.
- **Status.** Deferred to the owner. The decision note has the full assessment.
