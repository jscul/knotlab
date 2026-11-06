# Where counting in three dimensions becomes hard

Epic `HARD-3D-20261025-001`, closed 2026-10-25.

## The question

The owner approved the recommendation made at the close of `PATTERN-3D-20261025-001`.
- **What was known.** Deterministic counting laws in three dimensions are groupoid laws. Their counts are the numbers
  |Hom(π₁(M), Γ)| for finite groups Γ.
- **What the literature says.**
  - Abelian targets are easy.
  - Non-abelian simple targets are #P-complete (Kuperberg and Samperton, 2018).
  - Class-2 nilpotent targets are polynomial on closed manifolds with |H²(M; Z(Γ))| bounded (Samperton and Weiß, 2026). The same paper
    calls S₃ and the dihedral group of order 16 "two of the most interesting open cases".
- **Intuitions this epic targets.**
  - The complexity side: is the affine/non-affine boundary the boundary of hardness in three dimensions?
  - Space from logic.

**The evidence:**
- [With boundary, counting maps into S₃ is #P-hard](../../proofs/HARD-3D-20261025-001A/HARD-3D-20261025-001A-P001_with_boundary_s3_counting_is_hard/proof.md)
  (A, proof);
- [Closed manifolds: the doubles count pairs of colourings](../../proofs/HARD-3D-20261025-001B/HARD-3D-20261025-001B-P001_closed_doubles_count_pairs_of_colourings/proof.md)
  (B, proof);
- [bounded scan](scan.md);
- **scoping (scratch, not evidence):**
  - fin counts;
  - a first, wrong presentation of the double, caught by a known manifold;
  - growth-rate decompositions;
  - the colouring identities for seven groups.

## Outcome in one paragraph

**Every non-abelian symmetry tested makes three-dimensional counting #P-hard. Abelian ones stay easy.**
- **With boundary (A).** Draw a planar graph on a handlebody and attach a thickened torus along each edge's curve. The number of
  homomorphisms into S₃ is a spin model whose edge weights are centralizer sizes. Repeating edges and interpolating recovers twice the
  number of proper 3-colourings of the graph, which is #P-hard for planar graphs.
- **Closed (B).** Doubling the handlebody gives a closed manifold whose count mixes the colourings with a dual sector.
  - Remarkably, the mixture is exactly 2·P(G, 9)/3^|V|: the double counts pairs of 3-colourings, nine colours at once.
  - The same Potts duality gives chromatic polynomials for every dihedral group, for the quaternion group and for A₄.
  - So counting homomorphisms from closed 3-manifold groups is #P-hard for:
    - S₃, settling the first named open case;
    - every dihedral group whose order is not a power of 2 at least 16;
    - Q₈ and A₄.
  - The class-2 groups among them (the dihedral group of order 8 and Q₈) show that the bounded-H² hypothesis in the class-2 algorithm
    cannot be dropped.
- **Still open.** The dihedral group of order 16, the second named case. Its identity holds, but a collision of growth rates
  contaminates the extraction.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Fin handlebody count | Spin model Σ_y Π_e \|C(y_u y_v⁻¹)\| | Proved (A) |
| Interpolation | 2·P(G, 3) on seven plane graphs | Proved (A) |
| First presentation of the double | Off by a factor 6 on one edge; the outer face wraps around the equator | Scratch, corrected |
| Corrected presentation | Matches five identified manifolds; invariant under outer face and mirroring | Proved (B) |
| Growth-rate decomposition | Rotation edges and identity edges in the 2-dimensional channel share the rate 9 | Scratch, then proved |
| The mixed coefficient | Exactly 2·P(G, 9)/3^\|V\|, and analogues for six more groups | Proved (B) |
| Order-16 dihedral group | Identity holds, but 256·16 = 64² contaminates it (192 on the 4-cycle) | Open, documented |

## What was proved

| Result | Content |
| --- | --- |
| A | Compact orientable 3-manifolds with boundary: counting homomorphisms into S₃ (and D₈) is #P-hard. |
| B, Theorem 3 | Closed doubles: the target coefficient is a chromatic polynomial for S₃, dihedral groups, Q₈ and A₄. |
| B, Theorem 1 | Closed manifolds: #P-hard for S₃, every dihedral group whose order is not a power of 2 at least 16, Q₈ and A₄. |
| B, Corollary 2 | For class-2 groups the bounded-H² hypothesis is necessary. |

## What this changes

- **For the complexity side of the thesis.**
  - In two dimensions the program found that affine laws (parity) are easy and the rest are hard.
  - In three dimensions the deterministic laws are groups. Every abelian group is easy, and every non-abelian group tested is #P-hard,
    including the smallest, S₃.
  - The easy-hard line coincides with the abelian/non-abelian line, at least for unbounded homology.
- **For the knot reading.**
  - The group knots that survive the moves divide along the program's affine line.
  - Abelian group knots are affine: they count by linear algebra on homology.
  - The non-abelian ones tested are hard.
- **A relational reading of the double.** Closing the manifold makes each colouring appear with its mirror partner: nine colours are
  pairs of three. The hardness lives in that pairing.
- **Against the literature.**
  - S₃ for closed manifolds, open in February 2026, is settled.
  - The first version of the class-2 algorithm claimed no H² bound. Our instances show the bound is needed, which agrees with the
    authors' revision.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Closing a manifold might hide the colourings (doubles have a dual sector) | Raised during this epic's scoping | **False.** The dual sector adds a second colouring: the coefficient is P(G, 9) rather than P(G, 3), and it is still #P-hard. |
| Only simple groups are known to be hard on 3-manifolds | The literature (Kuperberg–Samperton; Samperton–Weiß open cases) | **Extended.** S₃, dihedral groups, Q₈ and A₄ are hard on closed manifolds with growing homology. |
| Class-2 nilpotent targets are polynomial on all closed 3-manifolds | First version of Samperton–Weiß | **False** unless every #P function is polynomial-time: D₈ and Q₈ are #P-hard on our instances, which have unbounded H². |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Fin handlebody plus planar colouring hardness | `candidate-local-delta`; elementary; folklore risk medium |
| B, the colouring identity | The double's presentation plus Potts duality | `candidate-local-delta`; folklore risk low to medium |
| B, hardness for S₃ on closed manifolds | A + B | Settles a case listed as open in 2026; no later work found |
| B, class-2 necessity | B for D₈ and Q₈ | Consistent with the authors' revision; new as an explicit hardness family |

**Did the perspective do real work?** Yes, more than in recent epics.
- **What it supplied.**
  - The question itself, which deterministic native laws are hard, came from the program's thesis.
  - The method came from the program's own tools: counting laws, duality and colourings.
- **What was a surprise.** The pairs-of-colourings identity was found by fitting data, then proved.
- **What is still to do.** The result needs independent review before anyone relies on it.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: where counting becomes hard | **Status:** Successful | S₃ settled on closed manifolds, plus dihedral groups, Q₈ and A₄; the order-16 group open. |
| Local direction: doubles of fin handlebodies | Continue | One collision blocks 2-power dihedral groups. A second gadget parameter should separate reflections. |
| Broader exploration: complexity of 3D counting | Known alternatives | Bounded-homology regimes; homology spheres (solvable targets are trivial there); signed and phased laws (Burton–Maria–Spreer). |
| Long-term goal: the complexity side of the thesis | Capability gained | Three-dimensional counting divides at abelian/non-abelian, matching the affine/non-affine boundary found in two dimensions. |
| Next recommendation: the full dichotomy | **Next step:** Continue, with a fresh epic | Close the order-16 case, then all non-abelian groups. See below. |
| Interest: that recommendation | **3/3: hot** | Concrete evidence: seven groups follow one mechanism, and one precise obstruction remains. Payoff: a complete classification that settles both named open cases. Main uncertainty: groups without a suitable abelian subgroup may need new gadgets. |
| Execution | Deferred to the owner | Bound: one epic. Stop if a second gadget does not separate the order-16 collision. |

**The next step in more detail.**
- **The question.** Is counting homomorphisms from closed 3-manifold groups #P-hard for every finite non-abelian group?
- **The first discriminator.** The dihedral group of order 16. Add to every edge a second kind of gadget, for example a solid torus
  attached along a (2, 1) curve, whose growth rates tell reflections from central edges. This gives a two-parameter interpolation.
- **Then.** A uniform choice of character and abelian subgroup, or a reduction to groups that contain one of the solved cases.

**Alternatives:**
- **Result conversion (2/3).** Write a self-contained note with replication code. Add a triangulation-level check: build
  triangulations of a few doubles and count S₃-colourings directly. That would make the result independently reviewable. Sharing it
  outside is the owner's call.
- **Bounded homology (1/3).** Is S₃ polynomial when b₁ is bounded, as for the r = 4 Turaev–Viro invariant?
