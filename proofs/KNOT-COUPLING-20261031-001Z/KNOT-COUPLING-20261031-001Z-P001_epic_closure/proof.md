# Closure of the knot's coupling epic

Status: Proved

Ticket `KNOT-COUPLING-20261031-001Z`, 2026-10-31.
- **What this is.** A ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim.
- **The decision note** is `research/KNOT-COUPLING-20261031-001/the_knots_coupling.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A knot's space minus one incidence acts on an edge by [[α, β], [β, α]] (α = M(H)/2, β = M(H with the incidence negated)/2). Chains multiply through-paths by ρ^k. At the knot's law (λ = 0) the atom is an exact negation. | new (elementary) | A-P001, Lemmas 2–4 |
| 2 | Exact ratios of the Fano atom and the three splice classes. Every real degeneracy is covered, and the ratios are independent. | new (exact) | A-P001, Propositions 5–7 |
| 3 | At the dimer coupling λ = −3, M = (−2)ⁿ #PM of the incidence graph: a determinant on the knot's spaces, #P-complete in general. | classical (Seymour; Robertson–Seymour–Thomas; Kasteleyn; Dagum–Luby), read as a coupling | A-P001, Proposition 8 |
| 4 | Correction of `NEXT-DIRECTION-SCAN-20261031-001B`: the deep-branch junctions also satisfy the matchgate identity at u = ∞ (the dimer coupling). | correction | A-P001, Correction 9 |
| 5 | One atom with a finite, nonzero ratio of infinite order at λ₀ ∉ {1, −3} makes counting on the knot's spaces #P-hard. In particular this holds at every real λ₀ outside {0, 1, −1, −3}. | new; standard technique; source hardness Fan–Cai and the counting arc | B-P001, Theorem 1, Corollary 2 |
| 6 | The five couplings λ ∈ {0, 1, −1, ∞, −3} are polynomial on the knot's spaces. | elementary or classical | B-P001, Proposition 3 |
| 7 | Deficiency one (one line deleted): #P-hard at the same couplings; polynomial at λ = 0 (the note's Theorem 1) and at λ = ±1, ∞; open at λ = −3. | new / open | B-P001, Theorem 4, Remark 5 |
| 8 | The dichotomy holds over ℂ: the curve of two atom ratios has only the torsion points (1, 1) and (−1, −1), reached at λ = ∞ and 0. | new; classical tools (Lang; Beukers–Smyth) | C-P001, Theorem 1 |
| 9 | End to end: colouring counts of three plain Pfaffian systems, one non-planar, recovered from counts of knot's spaces. This covers four couplings (one complex), two atoms and deficiency one, with an independent counter. | check | B-P001, checks 3 and 6 |

## Literature

- **Not found.** No dichotomy restricted to Pfaffian graphs or to non-2-colourable systems.
- **Nearest.**
  - Fan and Cai's Holant(f | =3) dichotomies over all cubic systems (arXiv 2011.09110, 2110.01173).
  - The planar classifications of Cai, Lu and Xia; Cai and Fu; and Cai, Fu, Guo and Williams.
- **Folklore risk.** Moderate. All tools are classical; the class and its two singled-out laws appear new.

## Recommendation

**Research directions** (2/3): a bounded scan of mutual selection across the knot catalogue.
- **The question.** Does each three-place law's unsolvable cubic systems form a polynomially recognisable class, and which couplings does
  it make easy?
- **Alternative.** Fold the dichotomy into the counting note (2/3).
- **Execution.** Planned; it awaits the owner. The decision note has the full assessment.
