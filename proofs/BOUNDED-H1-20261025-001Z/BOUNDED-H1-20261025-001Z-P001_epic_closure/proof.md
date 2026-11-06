# Closure of the bounded-homology epic

Status: Proved

Epic `BOUNDED-H1-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/BOUNDED-H1-20261025-001/bounded_homology.md`, and the literature scan is
`research/BOUNDED-H1-20261025-001/scan.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Bicycle law. On the alternating diagram of a plane graph with tripled edges, the S₃ transposition colourings are the vertex potentials φ. The S₄ transposition lifts over φ number 2^{c(H_φ) + dim B(H_φ)}, the number of left-right cycles of the monochromatic subgraph. The total is a twelve-state spin model with edge matrix J − 2N. | `candidate-local-delta`; folklore risk low to medium | `BOUNDED-H1-20261025-001A-P001`, Theorem 1 |
| 2 | Links. With every edge subdivided, the count is 2^{−n}·4^m·Z_Potts(G; 12, 1/2), so counting S₄ transposition colourings of link diagrams is #P-hard with one query. | `candidate-local-delta` | `…001A-P001`, Theorem 2 |
| 3 | Knots. Counting homomorphisms from knot groups to S₄ that send meridians to transpositions is #P-hard (Turing). Knot complements have H₁ = Z. S₄ is the first solvable group with hard knot colourings that the bounded scan found. | `candidate-local-delta`; no overlap found | `…001A-P001`, Theorem 3 |
| 4 | Groups with an abelian normal subgroup and nilpotent quotient, including every metabelian group, are polynomial with bounded mod-p first homology. This covers knot groups with a meridian class, and closed 3-manifolds with bounded \|H₁\|. | Folklore risk high | `BOUNDED-H1-20261025-001B-P001` |
| 5 | Closed manifolds with bounded H₁ are left open for S₄. Surgery or gluing must control the longitudes and the other meridian classes. | Recorded open step | Decision note |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- **Galindo's theorem leaves no complexity question in 3D counting.** False with bounded homology.
- **Only simple groups give hard knot-colouring counts.** False: S₄ does.
- **No knot-preserving gadget reaches a Potts or chromatic evaluation.** Wrong as stated: knot-preserving gadgets plus interpolation
  reach the chromatic polynomial at 12.

## Recommendation

**Continue with a fresh epic: closed manifolds with bounded H₁.**
- **First discriminator:** on the tripled alternating knots, the longitude values and the 4-cycle colourings, then the count of
  S³₂(K).
- **Interest:** 2/3.
- **Alternatives:**
  - which solvable groups are hard with bounded homology, for example SL(2,3) and GL(2,3) (2/3);
  - a short note on the bicycle law (2/3);
  - return to the core intuitions (1/3).
- **Execution:** deferred to the owner.
