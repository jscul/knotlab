# Closure of the twist relations epic

Status: Proved

Epic `TWIST-RELATIONS-20261022-001` closed on 2026-10-23. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim. The decision note is `research/TWIST-RELATIONS-20261022-001/twist_relations.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Shearing a square-lattice torus by its width relabels the twist sectors (a, b) → (a, a + b), and the mirror maps shear s to −s once the twisted seam is moved by a gauge transformation, for every orientation. | Lattice form of standard modular covariance; low novelty | `TWIST-RELATIONS-20261022-001A-P001`, Theorem 1 |
| 2 | Hence E = P00 − P01 carries only whole harmonics of the shear, and O = P10 − P11 only half-integer ones, with O = 0 at half shear. Additivity D = E − O = 0 is a relation of one basis, broken by shear, and at half shear it needs P00 = P01. | New to the program; elementary | `…001A-P001`, Theorems 2–3 |
| 3 | In twisted sectors P(consistent) = 1 − P(contractible) − P(odd winding), so the consistency relation is equivalent to D = odd10 + odd01 − odd11. None of the measured large-size relations is exact on the 3 × 3 torus. | Elementary | `…001A-P001`, Theorem 4, Proposition 5 |
| 4 | The odd-line identity: for each class, the two twists odd on it give the same probability that the cone is that line. Accepted on 8 new tori (24 tests, max \|z\| 2.63, about 10⁻⁵); exact on the small tori counted. Its stronger shear-independent form is decisively rejected (z = −7.31 on 12 × 8). | Not found in the literature; a conjecture with strong evidence; the stronger form a recorded negative | `TWIST-RELATIONS-20261022-001B-E001` |
| 5 | Rectangle additivity holds at aspects 3/2, 2 and 3 (D_inf within 1.7 standard errors), and in the orthogonal basis of the rotated square (2.5 standard errors, not yet decaying). On squares D(s) = D(0) + E(0)(1 − cos πs/L) to 0.001. On the 2:1 torus higher harmonics appear. | Empirical | `…001B-E001` |

## Challenged assumptions

The decision note records five workspace assumptions this epic challenges:
- that additivity is an exact law;
- that the consistency relation is a second law;
- that exact equalities on the smallest tori prove exact laws;
- that the odd-line identity and shear independence are the same statement;
- that one half-integer harmonic describes every shear.

## Recommendation

**Continue:** prove the odd-line identity.
- **First,** the exact count on the 4 × 4 torus at every shear.
- **Then** one bounded proof attempt with barrier-following seams.
- **Interest:** 2/3.
- **Alternatives:** the bounded direction search (1/3), and additivity itself (1/3).
- **Execution:** deferred to the owner.
