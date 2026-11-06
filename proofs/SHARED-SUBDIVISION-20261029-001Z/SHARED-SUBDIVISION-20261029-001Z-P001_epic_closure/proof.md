# Closure of the shared-subdivision epic

Status: Proved

Epic `SHARED-SUBDIVISION-20261029-001` closed on 2026-10-29. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/SHARED-SUBDIVISION-20261029-001/shared_subdivision.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Of 122 rules (copies of one three-bit knot class on the up triangles, or on all triangles, of the triangular lattice), shared subdivision leaves 22 exact at scale 2 (tori of side 6 and 8) and 6 at scale 3 (side 9). Set-level and counted exactness coincide. | Candidate local delta (exact census) | `SHARED-SUBDIVISION-20261029-001A-P001`, Theorem 1 |
| 2 | Every exact rule has affine solution sets and at most 2^L solutions on the L-torus. Every other rule has a non-affine solution set. Not-all-equal is never exact. | Candidate local delta (census) | `…001A-P001`, Theorem 2 |
| 3 | Parity on up triangles (Newman–Moore) is exact at scale 2 with N(2m) = N(m)², because (1 + S)² = 1 + S² over the two-element field. It is not exact at scale 3, and it is rigid on the plane. | Classical in substance | `SHARED-SUBDIVISION-20261029-001B-P001`, Theorem 1 |
| 4 | Parity on all triangles (Baxter–Wu) has colour-class solutions. It is exact at scale 2, not at scale 3, and rigid. Twelve three-excluded rules have the same solutions on tori of side 2 to 11, with no local explanation up to radius 3. | Classical; candidate local delta (the coincidence) | `…001B-P001`, Theorem 2 and Proposition 4 |
| 5 | Twisted not-all-equal on all triangles collapses to the 2^L configurations constant along lines (walls persist). It is exact at every scale, no triangle carries a knot, and it is not rigid (half-lines). | Elementary | `…001B-P001`, Theorem 3 |
| 6 | On genuinely two-dimensional space, exact self-reproduction keeps a knot only through parity. The other exact laws are parity in disguise or pairwise lines, and all have zero entropy density. | Synthesis | Conclusions 1 to 5; `…001B-P001`, Corollary 5 |

## Challenged assumptions

The decision note records three:
- that sharing boundaries would let non-linear knots reproduce themselves on genuine space (false in this family);
- that parity's exact self-similarity is geometric (it is arithmetic);
- that a rebuilt knot keeps its three-place structure (not on genuine space).

## Recommendation

**Continue, with a fresh epic: is exact self-reproduction on genuine space always affine?**
- **First discriminator.** All 256 relations on three bits on up triangles, at scales 2 and 3, together with an attempt at a local
  criterion.
- **Interest:** 2/3.
- **Alternative:** the critical counterpart for not-all-equal (1/3).
- **Execution:** deferred to the owner.
