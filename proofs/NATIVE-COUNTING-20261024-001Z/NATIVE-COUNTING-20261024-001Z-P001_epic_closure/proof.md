# Closure of the counting epic

Status: Proved

Epic `NATIVE-COUNTING-20261024-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/NATIVE-COUNTING-20261024-001/counting_emergence.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For a symmetric three-place signature, gluing topologically (two glued copies symmetric in four legs) is the equation f₀ f₂ + f₁ f₃ = f₁² + f₂², that is a generalized Fibonacci gate or [a, 0, 0, b]; among the 34 knots it selects exactly the four topological knots. | The recurrence is Cai, Lu and Xia's; the identification with topological gluing is `candidate-local-delta`, folklore risk high | `NATIVE-COUNTING-20261024-001A-P001`, Theorem 1 |
| 2 | Each topological knot is a sum of two cubes of orthonormal vectors, so every native network counts by Σⱼ λⱼⁿ ∏ legs (2^g for parity, Verlinde dimensions for Fibonacci) in polynomial time. | Classical (holographic algorithm; Verlinde) | `…001A-P001`, Theorem 2; 366 networks against brute force |
| 3 | The other 30 knots lie in none of the tractable families of Backens's Holant dichotomy with pins, so counting their native networks is #P-hard given that theorem, although deciding them is polynomial. | Classical theorem applied; conditional | `…001A-P001`, Theorem 3 |
| 4 | Emergence is countable exactly when it is topological: among the knots, native counting is polynomial exactly for those that see only the surface. | Synthesis (conditional on Backens) | Conclusions 1–3 |
| 5 | A closed native world of not-all-equal counts 2^(−n/2) 3^n Z(−1/3), with Z the even-subgraph sum: an antiferromagnetic Ising model with e^(2b) = 1/2. | Classical (high-temperature expansion); reading new to the program | `NATIVE-COUNTING-20261024-001B-P001`, Theorem 1 |
| 6 | On the sphere this count is a square-rooted Kac–Ward determinant, polynomial; with these methods a genus-g surface needs 4^g determinants, and on general cubic graphs counting is #P-hard (cited, condition checked). The cost of counting not-all-equal emergence tracks the genus of the network's own surface. | Classical theorems applied | `…001B-P001`, Corollary 2 and remarks; 26 planar graphs |

## Challenged assumptions

The decision note records three:
- that native logic is easy (refined: deciding is, counting is only for topological laws);
- that the topological knots are special to the program (identified as Fibonacci gates);
- that emergence counting is geometry-free (refined: for not-all-equal its cost depends on genus).

## Recommendation

**Continue with a fresh epic: approximate counting of native emergence.**
- **The question.** Is emergence hard to count exactly but easy to approximate?
- **The lead.** Closed not-all-equal worlds are antiferromagnetic Ising with tanh b = −1/3 on cubic graphs. That lies inside the
  uniqueness region, where approximation schemes are known.
- **First discriminator.** For each knot, test the correlation-decay condition on native trees, and look for a knot whose approximation
  is hard.
- **Interest:** 2/3.
- **Alternatives:** signed witness counts (1/3); a note on native decision, refutation and counting (1/3).
- **Stop if** every knot falls under known schemes or known hardness.
- **Execution:** deferred to the owner.
