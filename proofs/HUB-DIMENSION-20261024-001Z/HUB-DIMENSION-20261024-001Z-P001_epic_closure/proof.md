# Closure of the dimension-three epic

Status: Proved

Epic `HUB-DIMENSION-20261024-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/HUB-DIMENSION-20261024-001/dimension_three.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A native network of a triangulation (bits on faces, each shared by two tetrahedra) is the dual graph with slots; one-tetrahedron triangulations of the sphere and of L(4,1) share their native network. Native networks cannot see dimension three. | Elementary; classical census | `HUB-DIMENSION-20261024-001A-P001`, Proposition 5 |
| 2 | Of the 32,768 symmetric laws of bits on edges (one rule per triangle and one per tetrahedron), those satisfying the 2–3 and 1–4 move identities reduce to seven: all 0, all 1, all equal, free, even parity, odd parity, and even or odd. Every other law that is ever allowed breaks on explicit sampled moves. | `candidate-local-delta` | `…001A-P001`, Theorem 1 and Proposition 4 |
| 3 | Their normalized counts are constants or the size of the mod-2 first cohomology; even parity counts |H¹(M; Z/2)| 2^(V−1) (flat connections). So bits see dimension three only through hubs and then only through mod-2 first cohomology, and cannot separate the sphere from L(5,2). | Classical (Dijkgraaf–Witten for the two-element group); the restriction to these laws is new | `…001A-P001`, Theorem 3, Corollaries 2 and 6 |
| 4 | The Fibonacci rule with real Turaev–Viro-form weights of full support needs d² = d + 1 and an all-τ tetrahedron weight −(W₉ t₂)² < 0, so no count of hidden witnesses realizes it as a three-manifold invariant; an exact solution exists in Q(√5). | Known phenomenon (sign problem); the certificate is `candidate-local-delta` | `HUB-DIMENSION-20261024-001B-P001` |
| 5 | Native space is two-dimensional topology. Dimension three needs hubs, which also carry NP-hardness, and even then bit laws see only mod-2 cohomology, and the Fibonacci harmonies need signs. | Synthesis | Conclusions 1–4 |

## Challenged assumptions

The decision note records three:
- that hubs would supply dimension three (refined: necessary, but they give only mod-2 cohomology for bit laws);
- that a law seeing surfaces exactly would see three-manifolds with suitable weights (false for counts);
- that space is recognized rather than created (unchanged in dimension three).

## Recommendation

**Research directions: signed witnesses.**
- **The search.** A bounded scan of three questions:
  - whether signed witness counts are natural for the program, for example witnesses weighted by the parity of a hidden bit;
  - what they buy in three dimensions (Turaev–Viro);
  - what they cost in complexity (differences of counts, as in GapP).
- **Interest:** 1/3. The evidence names signs as the missing ingredient, but whether signs can be native is unclear.
- **Alternative:** a full pivot toward "patterns of patterns" (1/3).
- **Stop if** signs cannot be read as native relations.
- **Execution:** deferred to the owner.
