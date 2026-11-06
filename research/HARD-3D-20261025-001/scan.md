# Bounded scan: where counting in three dimensions becomes hard

Date 2026-10-25. Scope: a short idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and enter
claims only as cited hypotheses, never as admitted evidence.

## Question

`PATTERN-3D-20261025-001` showed that counting laws whose long edge is a function of the short edges are groupoid laws. Their counts
are therefore numbers of homomorphisms π₁(M) → G into finite groups. When is computing these numbers hard?

## Sources and relevance

| Source | Relevance |
| --- | --- |
| Kuperberg and Samperton (2018), [*Computational complexity and 3-manifolds and zombies*](https://arxiv.org/abs/1707.03811); Samperton, [arXiv:1805.09275](https://arxiv.org/abs/1805.09275) | For a fixed non-abelian simple group, counting homomorphisms from π₁ of a closed triangulated 3-manifold, even a homology sphere, is #P-complete. Existence of a nontrivial homomorphism is NP-complete. Only simple groups are covered. |
| Samperton and Weiß (2026), [*Obstruction theory and the complexity of counting group homomorphisms*](https://arxiv.org/abs/2602.02885) | Counting homomorphisms from a finitely presented group is #P-complete exactly when G is non-abelian. For class-2 nilpotent G and closed triangulated 3-manifolds there is a polynomial algorithm, stated without a bound on H² in v1 and with \|H²(M; Z(G))\| bounded in the revised version. They write that "two of the most interesting open cases are when G = D6 = S3 ... or G = D16". |
| Burton, Maria and Spreer (2015), [*Algorithms and complexity for Turaev–Viro invariants*](https://arxiv.org/abs/1503.04099) | The r = 4 Turaev–Viro invariant is #P-hard, by Kirby and Melvin's realization of cubic forms over Z/2. This is the signed Z/2 law, so bits with signs are already hard. |
| Jaeger, Vertigan and Welsh (1990); Vertigan (2005), *The computational complexity of Tutte invariants for planar graphs* (SIAM J. Comput.) | Evaluating the chromatic polynomial of a planar graph at any algebraic q other than 0, 1 and 2 is #P-hard. |
| Dyer and Greenhill; Bulatov and Grohe | Dichotomies for graph homomorphism and partition-function counting. Background for the spin models met here. |

## Discriminators found while scoping

All of this is scratch, not evidence.

**Fin handlebodies.**
- For a plane graph, take a handlebody with one handle per vertex. For each edge, attach a thickened torus along a curve in the class
  a_u a_v⁻¹; a planar drawing and its mirror give disjoint curves.
- π₁ = ⟨a_u, t_e | [t_e, a_u a_v⁻¹]⟩. The S₃ count is the spin model Σ_y Π_e \|C(y_u y_v⁻¹)\|, with centralizer sizes 6, 3, 2.
- Repeating edges k times and interpolating recovers 2·P(G,3). It matched brute force on five planar graphs.

**Doubles: closed manifolds.**
- First attempt, a wrong presentation: a single-edge test (the double must be T³ # S¹×S², which has 288 homomorphisms) showed the
  outer face's region passes around the equator.
- Corrected presentation: π₁ is a graph of groups over the faces, plus a Seifert piece Σ₁,₁ × S¹ for each edge.
- It reproduces three independently identified manifolds and the graph-manifold description of the doubles over cycles.
- It does not depend on the choice of outer face or on mirroring.

**Growth rates.**
- With edges repeated k times, the closed count is a sum of terms β^k.
- For S₃, rotation edges and identity edges in the 2-dimensional channel share the rate 9 per edge, the charge–flux coincidence.
- The coefficient of 9^(mk) is exactly 2·P(G,9)/3^\|V\|, checked on ten planar graphs. It counts pairs of 3-colourings.
- The same mechanism, a Potts model on the dual graph, gives the following coefficients:
  - order-8 dihedral and quaternion groups: P(G,8);
  - order-10 dihedral group: 2·P(G,25)/5^\|V\|;
  - order-16 dihedral group: 2·P(G,16)/2^\|V\|;
  - A₄: 3·P(G,16)/4^\|V\|.

## Novelty status

- `no-overlap-in-bounded-search` for #P-hardness of S₃, of the order-16 dihedral group and of the other groups here on closed
  3-manifolds. The 2026 paper lists the first two as open, and a search for later results found none. Folklore risk: low to medium.
  The construction is elementary, so an expert may have noticed it unpublished.
- The class-2 consequence (order-8 dihedral, quaternion) agrees with the revised Samperton–Weiß theorem, which assumes bounded H². It
  contradicts their first version, which did not.

## Barriers and scope

- Our instances have first Betti number growing linearly with the graph. Solvable groups see nothing on homology spheres: every
  homomorphism into S₃ is trivial there. So these results are about the general problem, not homology spheres.
- The reductions are Turing reductions by polynomial interpolation, not parsimonious ones.
- Producing triangulations from the handle descriptions in polynomial time is standard and is cited, not implemented.
