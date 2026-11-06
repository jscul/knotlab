# Bounded scan: counting with bounded first homology

Date 2026-10-25. Scope: a short idea-and-barrier scan for the epic `BOUNDED-H1-20261025-001`. External sources calibrate selection and
enter claims only as cited hypotheses, never as admitted evidence.

**Lesson from the previous epic.** That epic's question had already been answered in quantum-invariant language. This scan therefore
searched both phrasings:
- **Topology:** homomorphism counts and knot colourings.
- **Quantum invariants:** Dijkgraaf–Witten, Turaev–Viro and Reshetikhin–Turaev invariants, and Tambara–Yamagami categories.

## Question

With unbounded homology, counting homomorphisms π₁(M) → Γ from closed 3-manifolds is #P-hard exactly for non-abelian Γ.
- **The source.** Galindo 2026, applied to Vec_Γ (`DICHOTOMY-3D-20261025-001`).
- **The instances.** All the hardness instances have first Betti number growing with the input.
- **The question here.** Where does the line fall when the first homology is bounded?
- **The intuition targeted.** The complexity side of the thesis, and its "patterns of patterns" reading. Metabelian groups have one
  pattern level above the abelian quotient; S₄ has two (S₄ → S₃ → Z₂).

## Sources and relevance

| Source | Relevance |
| --- | --- |
| Galindo (2026), [arXiv:2605.06984](https://arxiv.org/abs/2605.06984) | Turaev–Viro dichotomy from triangulations: #P-hard unless trivializable pointed. Its graph-manifold instances have growing first homology. Says nothing about bounded homology. |
| Bridges and Samperton (TQC 2025), [*Towards a Complexity-Theoretic Dichotomy for TQFT Invariants*](https://arxiv.org/abs/2503.02945) | Tensor-contraction dichotomy, and the conjecture Galindo later proved. Section 1.3 notes that for restricted classes ("knots in S³", "links in S³", "integer homology spheres") "the classification may change". |
| Kuperberg and Samperton (2018; 2021), [arXiv:1707.03811](https://arxiv.org/abs/1707.03811), [*Coloring invariants of knots and links are often intractable*](https://arxiv.org/abs/1907.05981) (AGT 21, 2021) | Non-abelian simple G: counting π₁(S³ \ K) → G sending meridians to a class C is almost parsimoniously #P-complete for knots; homology spheres too. They use braid-group "zombie" actions, which need simple groups. Solvable groups are not covered. |
| [*A combinatorial approach to knot recognition*](https://arxiv.org/abs/1505.06595) (2015) | Larose and Zádori: general equation systems over a quandle Q are polynomial iff Q is affine, otherwise NP-complete. The paper stresses that knot-colouring systems are special, and leaves knot colourability by non-affine quandles open. |
| Samperton and Weiß (2026), [arXiv:2602.02885](https://arxiv.org/abs/2602.02885) | Finitely presented groups: #P-complete iff non-abelian. Class 2 on triangulated 3-manifolds is polynomial when \|H²\| is bounded. No bounded-homology statement for solvable targets. Their footnote cites Matei–Suciu with "no complexity bounds". |
| Matei and Suciu (2005), [*Counting homomorphisms onto finite solvable groups*](https://arxiv.org/abs/math/0405122) | Counting epimorphisms onto solvable groups through twisted cohomology in degrees 1 and 2: the mechanism behind the polynomial side here. |
| Maria–Spreer; Delaney–Maria–Samperton (SoCG 2025), [arXiv:2311.08514](https://arxiv.org/abs/2311.08514) | Fixed-parameter algorithms for TV₄ and Tambara–Yamagami invariants, in the parameter dim H₁(M; Z/2). Bounded homology helps some invariants. |
| Rosenstiehl and Read (1978); Las Vergnas; the matrix-tree theorem | The medial link of a plane graph H has 1 + dim B(H) components per connected piece, where B is the bicycle space; dim B = 0 exactly when the number of spanning trees is odd. |
| Vertigan (2005); Jaeger, Vertigan and Welsh (1990) | Planar Tutte and chromatic polynomials are #P-hard away from H₁, H₂ and a few points. In particular P(G, 12), and the Potts model at (q, v) = (12, 1/2). |
| Zaslavsky, signed graphs | The 12-state model for plain tripled knots is the zero-free signed Potts model of the all-negative graph. Its planar complexity is not established in the literature found; the gadget route below avoids needing it. |

**No source found** proves #P-hardness for counting colourings of links or knots by a solvable or non-affine quandle, or for counting
maps into a solvable group with bounded homology.

## Discriminators found while scoping

All of this is scratch, not evidence.

**Pretzels are too structured.** The pretzel knots P(3, …, 3) with n strands have exactly 5ⁿ + 1 S₄-transposition colourings.

**The bicycle law.**
- **The setting.** Alternating diagrams of plane graphs G with every edge tripled. There, Fox 3-colourings are all vertex potentials
  φ: V → Z₃, because the Laplacian vanishes mod 3.
- **First guess, wrong.** The number of transposition lifts is 2^{c(H_φ)}, with H_φ the monochromatic subgraph. This held on small
  graphs and failed on 8–9 vertex graphs.
- **The corrected law.** The exponent is c(H_φ) + dim B(H_φ), the number of components of the alternating link of H_φ. It holds
  exactly on more than 170,000 colourings over twenty graphs.
- **The local reason.**
  - In a 3-twist with equal colours, the V₄ bits follow the strands.
  - With unequal colours, the three crossings compose to a swap, so the bits follow the positions.

**Links.**
- **The identity.** With every edge also subdivided, the count is 2^{−n}·4^m·Z_Potts(G; 12, 1/2), exact on eight graphs.
- **The obstacle.** These are links with 1 + β₁(G) components.

**Knots.**
- **The gadget algebra.** Two-terminal gadgets act through span{J, I, N}. A component-preserving gadget needs an odd number of spanning
  trees and an odd number of terminal-separating 2-forests.
- **The gadget.** Γ₁ = S(e, P(e, S(e, e))) has b = 8/17 and g = −2/17. It keeps knots knots: C₃ with Γ₁ gives a knot with 1,158,510
  colourings, as predicted.
- **The reduction.** Parallel powers multiply (1+b, 1+g) = (25/17, 15/17), so the bases are distinct by prime factorization and
  interpolation recovers P(G, 12). Doubling the edges outside a spanning tree makes the spanning-tree count odd without changing P.

**Metabelian targets.** They need only boundedly many maps into the abelian quotient, plus affine lifts. S₃ itself can have
exponentially many maps on knot groups, which is why S₄ is not covered.

## Novelty status

- **#P-hardness of counting S₄-transposition colourings of knots and links.** No overlap in this bounded search. Kuperberg and
  Samperton cover only simple groups. Folklore risk low to medium.
- **The bicycle law, and the identity with Potts(12, 1/2).** No overlap found. Medial links and bicycles are classical; their use for S₄
  colourings appears new.
- **The polynomial side for metabelian, and abelian-by-nilpotent, targets with bounded homology.** Folklore risk high, since it is a
  direct use of twisted cohomology in the style of Matei and Suciu. It is stated so that the line is explicit.

## Barriers and scope

- **Knots are the bounded-homology statement proved here.** Their complements have H₁ = Z.
- **Closed manifolds with bounded H₁ are not yet covered.** Dehn surgery or gluing turns knot counts into closed counts. Doing so needs
  the longitude values and the 4-cycle colourings controlled, and that is left as the next step.
- **Both hardness statements are Turing reductions.** The link statement needs a single query.
- **No claim about P versus NP**, approximation, or physics.
