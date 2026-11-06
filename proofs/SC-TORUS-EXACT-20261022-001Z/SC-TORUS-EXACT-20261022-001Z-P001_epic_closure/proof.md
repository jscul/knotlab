# Closure of the exact torus values epic

Status: Proved

Epic `SC-TORUS-EXACT-20261022-001` closed on 2026-10-22. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/SC-TORUS-EXACT-20261022-001/exact_torus_values.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For every orientation of a square-lattice torus and every primitive period d, exactly one holds: the orientation has a directed closed walk W with det([W], d) < 0, or the rotated dual orientation has a directed closed walk of class d. | Farkas-type duality; not found in a bounded search; moderate–high folklore risk (homology flows and cohomology cuts) | `SC-TORUS-EXACT-20261022-001A-P001`, Theorem 1 |
| 2 | The realized primitive classes are exactly the primitive periods of a closed convex cone C, and the dual realizes exactly those of its polar C°. On twisted tori C is {0}, a line or the plane. | New in this form | `…001A-P001`, Theorems 2–3 |
| 3 | For the uniform orientation the law of C is polar-invariant. On square tori P(C ⊆ V) = P(C ⊇ V) = P(C ⊆ H) = P(C ⊇ H), and P(positive horizontal winding) = 1 − P(pure (1, 0)) ≥ 1/2. So the conjectured 3/4 means: no directed closed walk winds horizontally with probability exactly 1/4. | New reformulation of a published conjecture | `…001A-P001`, Theorem 4 |
| 4 | Half a bit is decisively rejected. On squares twisted along one axis, E∞ = 0.49627 ± 0.00028 bits (13 standard errors below 1/2; 0.4967 ± 0.0006 with a 1/L² term), so P(consistent) tends to 0.7089, not 1/√2. | Corrects the previous epic's accepted candidate | `SC-TORUS-EXACT-20261022-001B-E001` |
| 5 | The untwisted one-direction wrapping is 0.75041 ± 0.00019 (3/4 accepted at 2.2 standard errors; 0.75007 ± 0.00039 with a 1/L² term). | Independent confirmation of published numerics | `…001B-E001` |
| 6 | The second difference of P(contractible) over the twist sectors vanishes on squares in the limit (0.0008 ± 0.0005) and on the 2 : 1 rectangle (0.00002 ± 0.00034). Inconsistency on tori twisted along the long side decays with exponent 0.1965 ± 0.0004, the class's β/ν. | Empirical; new to the program | `…001B-E001` |

## Challenged assumptions

The decision note records five workspace assumptions this epic challenges:
- that half a bit is the exact value on squares with one odd side;
- that the duality identities might derive the values;
- that 3/4 is only a statement about undirected wrapping;
- that the cone theorem's duality was unknown;
- that the 2 : 1 torus twisted along its long side holds 1/8 bit.

## Recommendation

**Full pivot** from exact values of strongly-connected percolation.
- **Why.** The stop rule is met: half a bit failed, and the proof attempt
  found no mechanism for 3/4.
- **Next.** A bounded search for the next barrier question, comparing three
  candidates:
  - the lower bound P(C = plane) ≥ c;
  - space from a law (question 9);
  - dynamics (question 4).
- **Interest:** 1/3.
- **Alternatives:** pursuing 3/4 directly (1/3), and sharing the
  reformulation with its authors (1/3, the owner's call).
- **Execution:** deferred to the owner.
