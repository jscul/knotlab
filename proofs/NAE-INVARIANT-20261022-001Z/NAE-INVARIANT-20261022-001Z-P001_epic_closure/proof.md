# Closure of the not-all-equal invariant epic

Status: Proved

Epic `NAE-INVARIANT-20261022-001` closed on 2026-10-22. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/NAE-INVARIANT-20261022-001/nae_invariant.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | With fair spokes, a not-all-equal world is the uniformly random orientation of the bipartite double cover that the deck swap reverses. It is inconsistent exactly when some strongly connected component is swap-invariant. | Classical test (Aspvall, Plass, Tarjan) in a new reading | `NAE-INVARIANT-20261022-001A-P001`, Theorem 1 |
| 2 | Strong components are clusters of cyclic edges. The world is inconsistent exactly when the projected cyclic edges have a cluster with an odd cycle: on a torus, a cross cluster or an odd winding. Every cross cluster carries the whole period lattice. | Elementary | `…001A-P001`, Theorem 2 |
| 3 | In a plane graph, every edge is cyclic in exactly one of an orientation and its rotated dual orientation. | Classical ingredients (Minty) | `…001A-P001`, Theorem 3 |
| 4 | On twisted tori the complementarity is exact. Without a twist it fails: primal and dual directed winding cycles can cross. | Not found in a bounded search | `…001A-P001`, Theorem 4 |
| 5 | On every twisted square-lattice torus, P(contractible) = P(cross), consistency = contractible + even windings, and −log₂(1 − P₀) ≤ E ≤ −log₂ P₀. The lower bound reduces to a crossing estimate for strongly-connected percolation and stays open. | New | `…001A-P001`, Theorem 5 |
| 6 | Emergence is scale-free on every scanned shape: aspect ratios, both odd-side patterns, shears, rotations and long cylinders. The shape function is measured (0.846 bits on squares with both sides odd). The bulk is the strongly-connected percolation class (dimension 1.80; untwisted wrapping 0.862/0.750/0.638; two-way arm exponent 0.197 = β/ν, not 5/24). The Pinson–Arguin Coulomb-gas family is rejected (χ² 1330 per degree of freedom). Half a bit on square tori with one odd side is accepted (E∞ = 0.4993 ± 0.0011); the long-cylinder exponent 1/16 is rejected (0.0645 ± 0.0003). | Empirical, confirmatory | `NAE-INVARIANT-20261022-001B-E001` |

## Challenged assumptions

The decision note records six workspace assumptions this epic challenges:
- that not-all-equal's amount is an unidentified invariant;
- that the seam picture is fundamental;
- that two-way crossings explain inconsistency;
- that simple certificates give the lower bound;
- that some Coulomb-gas formula fits;
- that two-way connection is backbone-like.

## Recommendation

**Continue** with exact torus values of strongly-connected percolation.
- **The test:** precision tests of half a bit (twisted, one odd side) and of
  the untwisted 3/4, a scan for further exact-looking values, and one bounded
  attempt to derive them from the duality identities.
- **Interest:** 2/3.
- **Alternatives:** banking the result as a note (1/3), and the lower bound
  (1/3).
- **Execution:** deferred to the owner.
