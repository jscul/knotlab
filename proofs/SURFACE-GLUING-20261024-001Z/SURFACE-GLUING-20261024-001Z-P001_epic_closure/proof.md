# Closure of the space-from-a-law epic

Status: Proved

Epic `SURFACE-GLUING-20261024-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/SURFACE-GLUING-20261024-001/space_from_a_law.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A hub-free network of three-place relations, every shared distinction joining exactly two copies, is a pants decomposition of a compact orientable surface whose genus is the cycle rank; two-place relations glue only into paths and cycles; a hub is a point where three sheets meet. | Classical (pants decompositions) | `SURFACE-GLUING-20261024-001A-P001`, Theorem 1 |
| 2 | A symmetric three-place relation glues topologically, as a relation or with counts, exactly when two glued copies give a result symmetric in their four legs. | The elementary half of the classical correspondence between 2D topological field theories and commutative Frobenius algebras | `…001A-P001`, Theorem 2 |
| 3 | Exactly four knots glue topologically with counts. The parity knots fix the boundary total, with 2^g witnesses: one hidden bit per handle. The no-lone-value knots remember the boundary only on spheres, and their closed counts are tr H^(g−1) = 2, 5, 15, 50, … for H = [[3,1],[1,2]]. | Known overlap, identified at closure. These are the fusion rules of the two multiplicity-free fusion rings of rank two: the abelian one, and the Fibonacci one, whose Verlinde dimensions are these counts. Each comes with either value as vacuum. The census is new to the program; the classification is not (Verlinde 1988; Ostrik 2003). | `…001A-P001`, Theorem 3 and Corollary 4; decision note |
| 4 | The frozen knots glue topologically only as relations; not-all-equal and the 27 asymmetric knots depend on the arrangement, not only on the surface. | New to the program (census) | `…001A-P001`, census over 220 shapes |
| 5 | Hub-free gluing, self-gluing and pinning never create a parity face of dimension three or more (exact count a₀b₁ + a₁b₀). So only the parity knots build parity without hubs; with hubs, not-all-equal and pins define it. | New to the program; `candidate-local-delta` | `SURFACE-GLUING-20261024-001B-P001`, Theorem 5 and Corollary 6 |
| 6 | Pairwise sharing, which the hub guardrail requires of native contact, is what makes native gluing two-dimensional. The two/three boundary of places is the boundary between dimension one and dimension two of what native gluing builds. | Synthesis | Conclusions 1 and 5 |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that space is only recognized, never created, by a law (refined: native pairwise sharing builds surfaces; no particular surface and
  no geometry is created);
- that only group-like relations glue topologically (false for counts: the Fibonacci fusion rule);
- that a law with memory can build it in any network (refined: without hubs, memory is never created);
- that the golden-ratio handle is new (corrected: it is the Fibonacci theory's Verlinde formula).

## Recommendation

**Continue with a fresh epic: dimension three through hubs.**
- **The question.** In two dimensions the Fibonacci rule counts surfaces exactly. Its three-dimensional theory lives on triangulations
  whose edge labels are shared by many tetrahedra, which is hubs. Do hubs let a Boolean knot see a 3-manifold?
- **First discriminator.** Count Fibonacci-admissible edge labellings of triangulations related by 2–3 moves.
  - If the counts change, three-dimensional topology needs weights (6j symbols involving φ).
  - Then test whether such weights can be native.
- **Interest:** 2/3. It continues the space intuition and ties space to complexity, since hubs carry NP-hardness. The main
  uncertainty: the machinery is classical, and Boolean counts are probably not invariant in three dimensions.
- **Alternatives:** the growth of emergent information per handle for the arrangement-dependent knots (1/3); a note on native gluing
  and the fusion rules (1/3).
- **Stop if** Boolean counts are not invariant and no native weighting is found.
- **Execution:** deferred to the owner.
