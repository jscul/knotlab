# Bounded scan: toward the full dichotomy for counting in three dimensions

Date 2026-10-25. Scope: a short idea-and-barrier scan for the epic `DICHOTOMY-3D-20261025-001`. External sources calibrate
selection and enter claims only as cited hypotheses, never as admitted evidence.

## Question

`HARD-3D-20261025-001` proved counting homomorphisms π₁(M) → Γ from closed orientable 3-manifolds #P-hard for S₃, most dihedral
groups, Q₈ and A₄. It left the dihedral group of order 16 open, because two growth rates of its edge factors collide
(256 · 16 = 64²). The owner approved two questions:
- Does a second gadget separate the collision?
- How far does the method reach toward the full dichotomy: is the count #P-hard for every finite non-abelian group?

## The answer was already in the literature

**César Galindo, [*A Complexity Dichotomy for Quantum Invariants of 3-Manifolds*](https://arxiv.org/abs/2605.06984),
arXiv:2605.06984. Version 1 is dated 7 May 2026 and version 2 is dated 7 June 2026.**

- **Theorem 1.2 (and 9.3).** Let 𝒜 be a spherical fusion category, and let the input be a triangulation of a closed 3-manifold.
  - If 𝒜 is *trivializable pointed*, the Turaev–Viro invariant |M|_𝒜 is computable in polynomial time.
  - Otherwise it is #P-hard under polynomial-time Turing reductions.
- **Trivializable pointed** means tensor equivalent to Vec^ω_Λ, with Λ a finite abelian group and [ω] trivializable. Equivalently,
  the Drinfeld centre 𝒵(𝒜) is pointed.
- **The route.**
  - |M|_𝒜 equals the Reshetikhin–Turaev invariant of 𝒵(𝒜) (Turaev).
  - The RT dichotomy is proved for anomaly-free modular categories on graph manifolds M_G. These are built from blocks Σ₁,ᵣ × S¹ glued
    along a bounded-degree graph G, and satisfy Z(M_G) = 𝒟^|E| · Z_A(G) with A = (S_ij/(d_i d_j)).
  - The bounded-degree form of the Cai–Govorov dichotomy then applies.
  - It also proves the conjecture of Bridges and Samperton.

**What this gives here** (our reading; Galindo does not state it).
- **The invariant.** For 𝒜 = Vec_Γ, the untwisted Dijkgraaf–Witten case, and M closed and connected, |M|_{Vec_Γ} = |Hom(π₁(M), Γ)|/|Γ|.
- **When it is easy.** Vec_Γ has fusion ring Z[Γ]. This ring is commutative only when Γ is abelian. So for non-abelian Γ, Vec_Γ is
  pointed but not trivializable pointed. Equivalently, its centre Rep(D(Γ)) has non-abelian anyons and is not pointed.
- **Consequence.** For every finite non-abelian group Γ, counting homomorphisms from closed triangulated 3-manifold groups into Γ is
  #P-hard (Turing). For abelian Γ it is polynomial.

So the full dichotomy, including S₃ and the order-16 dihedral group, was settled in May 2026. That is five months before
`HARD-3D-20261025-001` closed. The scan of that epic, and its later search, missed it.

## Other sources

| Source | Relevance |
| --- | --- |
| Samperton and Weiß (2026), [arXiv:2602.02885](https://arxiv.org/abs/2602.02885) | Finitely presented groups: #P-complete exactly for non-abelian Γ. Class-2 targets: polynomial on triangulated 3-manifolds, with \|H²(M; Z(Γ))\| bounded in the revision. Names S₃ and the order-16 dihedral group as open. Galindo's theorem settles both. |
| Kuperberg and Samperton (2018), [arXiv:1707.03811](https://arxiv.org/abs/1707.03811) | Non-abelian simple groups, homology spheres, almost parsimonious reductions. Parsimony and homology spheres are not covered by Galindo's Turing reduction. |
| Delaney, Maria and Samperton, cited by Galindo | An algorithm parameterized by the first Betti number, for a class of Turaev–Viro invariants. Bears on the bounded-homology question. |
| Cai and Govorov; Cai, Chen and Lu | Dichotomies for weighted graph homomorphisms. Galindo's source of hardness. |
| Vertigan (2005) | Planar chromatic polynomial hardness at q ∉ {0, 1, 2}. Our source of hardness. |

## Discriminators found while scoping

All of this is scratch, not evidence.

**The second gadget works.**
- **The gadget.** Dehn-fill a parallel copy of each edge curve of the closed double along the slope λμ^(−p). This imposes λ = μ^p, and
  multiplies the anyon channel (λ, ψ) by Σ_{τ ∈ C(λ), τ^p = λ} ψ̄(τ)/ψ(1). With a mirror copy along λμ^p, the product is
  ρ_p = |Σ ψ(τ)|²/ψ(1)².
- **Why it separates.** The doubled square-root filling kills every reflection flux of the order-16 dihedral group, since no reflection
  is a square. That removes the collision.
- **The coefficient.** The surviving top coefficient is 4^m · 8 · P(G, 4)/2^n. Ticket A proves this as a case of an index-p theorem.

**Chromatic anyon sectors.** Five families of anyon sets of the quantum double have targets β·α^n·P(G, q):
- flux sectors: fluxes in N₁ \ N₂;
- charge sectors: central flux, with charges of Γ/N₂ that are not charges of Γ/N₁;
- complements of commuting pairs;
- non-fixed pairs of an abelian normal subgroup;
- complements of a subgroup of the abelian anyons.

A sector is recoverable from the counts when it is a face of the polytope of gadget growth rates (fins and doubled root fillings,
interpolated).

**The sector map.**
- Every non-abelian group surveyed, 39 groups of orders 6 to 48, has a recoverable sector with a verified identity and q ≥ 3. The one
  exception is S₃ × S₃, which is handled by its square sector.
- The survey includes the order-32 extraspecial groups and V₄ ≀ Z₂, which need abelian-anyon sectors split by square-root fillings.
- No abelian control has such a sector. This sanity check had to pass, since abelian counting is polynomial.

**Extraspecial groups.**
- **p odd.** The anyons of top dimension are exactly those whose charge is nontrivial on the centre, giving q = p (computed for order
  243).
- **p = 2.** Square-root fillings isolate the abelian anyons with nontrivial charge, giving q = 4^k for order 2^(1+2k), k ≥ 2.

## Novelty status

- **Hardness for every non-abelian group: not new.** It follows from Galindo's 2026 theorem.
- **HARD-3D's claims.** Its claims 3 and 4 were already implied by that theorem: S₃ settled on closed manifolds, and the bounded-H²
  hypothesis shown necessary for class-2 groups.
  - Its mathematics stands: the identities and constructions are verified.
  - Its novelty labels "settles a named open case" and "frontier change" are wrong.
- **What may still be new, all with medium folklore risk:**
  - The explicit chromatic coefficients: the double counts pairs of colourings, and the five sector families.
  - The root-filling gadget.
  - Independent, elementary corroboration of Galindo's theorem for large explicit families, through planar chromatic polynomials
    rather than the Cai–Govorov dichotomy.

## Barriers and scope

- Both routes are Turing reductions on instances whose first Betti number grows with the graph.
- Parsimonious reductions, approximate counting, and bounded homology are not settled by either route.
- Solvable targets see nothing on homology spheres.

## Decision

Narrow the epic:
- Record the literature finding.
- Prove the root-filling route in one compact ticket, since it settles the approved first discriminator and corroborates Galindo
  independently.
- Close without further write-ups of preempted hardness.
