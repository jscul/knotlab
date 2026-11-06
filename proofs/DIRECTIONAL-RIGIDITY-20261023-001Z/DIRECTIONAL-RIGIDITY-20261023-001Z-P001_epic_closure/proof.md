# Closure of the directional-rigidity epic

Status: Proved

Epic `DIRECTIONAL-RIGIDITY-20261023-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label
and evidence. It makes no new claim. The decision note is `research/DIRECTIONAL-RIGIDITY-20261023-001/directional_rigidity.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Polymorphisms do not separate rigid from selective three-place contacts. All 30 three-place tiling contacts have only projections (plus constants when the constants are doubly allowed), against majority for all 24 two-literal ones. Renaming the places of one relation changes its kind in five of the twelve renaming classes. | Classical tools; the observation is the program's | `DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Proposition 1 |
| 2 | The 30 three-place tiling contacts fall into four kinds by their doubly allowed and coin-pinned patterns: h/v stripes (2), diagonal stripes (8), straight walls (8), bending walls (12). | New to the program | `…001B-P001`, Proposition 0 |
| 3 | Stripes give rigidity. Diagonal stripes confine contradictions to the diagonal class; h/v stripes forbid them, on every torus. | Elementary; moderate folklore risk (non-expansive directions) | `…001B-P001`, Theorem 2; A (P3, P5) |
| 4 | Straight walls give rigidity with an exact count. When the relative twist is odd on the diagonal class, every configuration contradicts along all odd classes. Otherwise a configuration contradicts along all odd classes or none, and exactly 2^{2LM} − (2^{2l} − 2)^g contradict nowhere. | New to the program; low to moderate folklore risk | `…001B-P001`, Theorem 3; exact counts in A on 3 × 3 and 3 × 4, sampled on 4 × 4, 4 × 5, 5 × 5 (P4) |
| 5 | The twelve bending-wall contacts are selective: certified on 3 × 3, and in A selective on every torus computed (P6) | Certified computation | `…001B-P001`, Proposition 4; A |
| 6 | For the four bending contacts with no free place, an odd class contradicts exactly when every valid wall cycle with a transverse class has an overlap in ℤc + ℤe: walls block a cylinder by colliding with their own copies. The rule reproduces all 3 × 3 histograms of A for them. | New to the program; low folklore risk | `…001B-P001`, Theorem 7 |
| 7 | A three-place contact with both single lines and global contradictions has bending walls. So the experiment's mixed law reduces to the selectivity of bending contacts. | New to the program | `…001B-P001`, Corollary 5; A (P7) |
| 8 | The frozen experiment supports all seven predictions on all five tori, with 13 to 16 classes exhaustively on 3 × 3 and 3 × 4 and up to 12 classes in samples on 4 × 4, 4 × 5 and 5 × 5. It ran 26225 s against a 14400 s budget, unchanged. | A recorded computation | `DIRECTIONAL-RIGIDITY-20261023-001A-E001`, supported |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that an algebraic criterion separates rigid from selective contacts (false);
- that the direction structure falls at clause width (refined: clause width decides the mechanism, and 18 three-place contacts are
  rigid);
- that "never contradicting" is one phenomenon (two mechanisms);
- that rigid three-place contacts are degenerate (only the stripe kinds are).

## Recommendation

**Continue with a fresh epic: walls with choices.**
- **The question.** What is the exact rule for the eight bending contacts whose walls branch, and is every bending contact
  selective on every large enough torus?
- **The first step.** Reproduce their exact 3 × 3 and 3 × 4 histograms from wall cycles; then construct selective configurations on
  general tori.
- **Interest:** 2/3.
- **Alternatives:** a note on the classification (1/3) and the 3/4 constant (1/3).
- **Execution:** deferred to the owner.
