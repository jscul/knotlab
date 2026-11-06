# Bounded scan: patterns of patterns in three dimensions

Date 2026-10-25. Scope: a short idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and enter
claims only as cited hypotheses, never as admitted evidence.

## Question

With one bit per edge, counting laws on ordered triangulations see a closed three-manifold only through |H¹(M; Z₂)|, with or without
twists, orientation or positive weights (`HUB-DIMENSION-20261024-001`, `TWIST-3D-20261025-001`). What do larger distinctions see, made of
patterns of bits? The first discriminator is the most structured family: laws whose triangle rule makes the long edge a function of the
two short edges. The prediction to test is that only groups survive.

## Sources and relevance

| Source | Relevance |
| --- | --- |
| Dijkgraaf and Witten (1990), *Topological gauge theories and group cohomology*; Wakui (1992), *On Dijkgraaf–Witten invariant for 3-manifolds* | The forward direction: a finite group G on the edges of an ordered triangulation, with no cocycle, gives the invariant \|Hom(π₁(M), G)\|/\|G\|. With a cocycle it needs phases. |
| Freed and Quinn (1993), [*Chern–Simons theory with finite gauge group*](https://arxiv.org/abs/hep-th/9111004); Faria Martins and Porter, [arXiv:math/0608484](https://arxiv.org/abs/math/0608484) | Groupoid and homotopy-cardinality forms of the same invariant; extensions to categorical groups, which need labels on triangles as well. |
| Duskin and Glenn, hypergroupoids ([nLab: hypergroupoid](https://ncatlab.org/nlab/show/hypergroupoid)) | The nearest converse: a simplicial set is the nerve of a groupoid exactly when it is 2-coskeletal and its 2- and 3-horns have unique fillers. Those hypotheses are horn conditions on a simplicial set that knows its vertices. Here the vertices carry no labels, and the hypotheses are counting identities from the moves. |
| Funar (2013), [*Torus bundles not distinguished by TQFT invariants*](https://arxiv.org/abs/1101.0509); Hempel (2014), [*Some 3-manifold groups with the same finite quotients*](https://arxiv.org/abs/1409.3509) | Non-homeomorphic closed 3-manifolds whose fundamental groups have the same finite quotients: Sol torus bundles (Funar) and Seifert fibred spaces (Hempel). No homomorphism count separates them. |
| Kuperberg and Samperton (2018), [*Computational complexity and 3-manifolds and zombies*](https://arxiv.org/abs/1707.03811); Samperton and Weiß (2026), [arXiv:2602.02885](https://arxiv.org/abs/2602.02885) | Complexity of these counts. Counting homomorphisms from π₁ of a homology sphere to a fixed non-abelian simple group is #P-complete, and existence is NP-complete. For class-2 nilpotent targets there is a polynomial algorithm on triangulations. |

## Discriminators

- **Laws with a function rule (ticket A).**
  - Scoping enumerated in C all 19,683 multiplication tables on three labels and all 4,294,967,296 on four.
  - Every surviving table reduces, after deleting triangles that lie in no allowed tetrahedron, to a groupoid:
    - Z₃, Z₄ and Z₂ × Z₂;
    - the pair groupoid, two objects with one arrow each way, hidden inside 12 non-associative Latin squares;
    - one or two constant labels.
  - A merged-label construction, two arrows of different components given one label, fails the 1–4 identity. It creates tetrahedra
    that mix the components.
  - A proof for every finite label set, total or partial, is in hand. Every label's allowed tetrahedra split into blocks, and units
    from two different blocks always form an allowed tetrahedron, so there is one block. Associativity, objects and inverses follow.
- **All relations on three labels (ticket B).**
  - Scoping enumerated in C all 2²⁷ triangle relations, functions or not.
  - The 7,948 survivors reduce to seven laws: one, two or three constant labels, Z₂, Z₃, and the free laws on two and three labels.
  - Each is a groupoid law pulled back along fibres of equal size.

## Novelty status

- `known-overlap-found` for the invariants: untwisted Dijkgraaf–Witten for groups and groupoids.
- `no-overlap-in-bounded-search` for the converse in this setting: move identities, with vertices unlabelled, force a groupoid. The
  nearest result is the Duskin–Glenn characterization. Folklore risk is medium, because the statement is natural and its ingredients
  are standard.
- `no-overlap-in-bounded-search` for the complete census of relations on three labels; low depth.

## Barriers

- **What the invariants can be.** If only groupoids survive, every count is a sum of terms \|Hom(π₁(M), G)\|/\|G\|. Together these see
  exactly the numbers of homomorphisms to finite groups. By classical group theory they then see the finite quotients of π₁.
- **What no count can see.**
  - Lens spaces with the same order of π₁. L(5,1) and L(5,2) are not even homotopy equivalent, yet every such count agrees on them.
  - The pairs of Funar and Hempel.
  - Seeing a linking form needs phases, as in twisted Dijkgraaf–Witten.
- **The complexity side.**
  - Abelian groups give linear algebra.
  - Non-abelian simple groups give #P-complete counts (Kuperberg and Samperton).
  - So the same split as in two dimensions, affine easy and non-affine hard, reappears.
