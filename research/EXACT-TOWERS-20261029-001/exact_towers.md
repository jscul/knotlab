# Exact self-similar laws and the towers they build

Epic `EXACT-TOWERS-20261029-001`, closed 2026-10-29.

## The question

- **The owner's decision.** On 2026-10-29 the owner approved the recommended continuation of `HUB-SURVIVORS-20261029-001` ("Yes,
  please continue"): exact self-similar laws.
- **The question.** A hub gadget is an *exact counted fixed point* when it rebuilds its knot and gives every allowed leg tuple the
  same number c of hidden completions. Substituting it for every copy, level after level, builds a tower whose law never changes,
  counts included. So:
  - which knots have such gadgets, at which sizes, with which factors;
  - what spaces do their towers build;
  - what can exact self-reproduction not build?
- **Intuitions targeted:**
  - space from logic without a drawn space;
  - the growth of emergent information (log₂ c bits per copy per level);
  - universally influential cycles;
  - everything relational.

**The evidence:**
- [Exact counted fixed points of the knots](../../proofs/EXACT-TOWERS-20261029-001A/EXACT-TOWERS-20261029-001A-P001_exact_counted_fixed_points_of_the_knots/proof.md)
  (A, proof);
- [The minimal exact towers](../../proofs/EXACT-TOWERS-20261029-001B/EXACT-TOWERS-20261029-001B-P001_the_minimal_exact_towers/proof.md)
  (B, proof);
- **scoping (scratch, not evidence):**
  - the mechanism runs;
  - the drift of "x or (y ≠ z)" over four levels;
  - a first test of shared-midpoint subdivision on small spheres.

## Outcome in one paragraph

**Exact self-reproduction is common. Each law's smallest exact self-reproduction builds a definite hierarchical space, but every such
space is finitely ramified, and its scale-free order exists only at the hard law.**
- **Census (A).** Up to six copies, exact counted fixed points exist for:
  - parity (every rebuild, by linearity);
  - twisted not-all-equal (from four copies);
  - the two three-excluded classes (from five);
  - not-all-equal, at seven copies.

  "x or (y ≠ z)" is rebuilt but never exact, and its counted law drifts.
- **Mechanisms (A).** Linearity; symmetry (only the punctured tetrahedron and the Fano plane); collapse (tied pairs, frozen hidden
  variables); decoration (pendants). A remainder of 22 gadgets at six copies has none of these.
- **Towers (B).**
  - A single-scale exact gadget builds a tower with an unchanging corner law, corners at distance s^k and growth exponent
    log m / log s.
  - Every such tower has bounded treewidth and is cut off by three points at every scale.
  - The smallest towers are the Sierpinski gasket (parity, log₂ 3), the slit triangle (twisted not-all-equal, 2) and the Fano tower
    (not-all-equal, log₃ 7).
- **Fragility (B).** Softening an exact law grows m-fold per level, at least threefold in general. So every softened tower flows to
  the free law.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorems 1 to 3 | The factor is the free solution count over \|K\|. Every parity rebuild is exact, since the fibres of an affine map are equal. Transitive automorphisms force exactness, which is possible only for parity, not-all-equal and twisted not-all-equal. |
| A, Lemma 4 | With the legs on distinct copies, deleting a leg's copy leaves exactly c extensions of each excluded tuple. A knot's excluded tuples are isolated. |
| A, Theorem 5 | Exhaustive census, three to six copies, every placement. Exact classes and smallest sizes: parity 3, twisted not-all-equal 4, three-excluded 5. "x or (y ≠ z)" is rebuilt (1, 8, 77 shapes) but never exact, and its far tuples lead the counts. Mechanisms of all 4057 irredundant exact gadgets of the non-parity classes, 22 with none. Smallest single-scale exponents: log₂ 3, 2, log₂ 6, and log₃ 7 for the Fano plane. |
| B, Theorem 1 | Exact towers. m^k copies and 3 + h(m^k − 1)/(m − 1) variables. The corner law is the same at every level, with c^((m^k − 1)/(m − 1)) completions. Distances scale by s, and balls of radius s^j hold exactly the level-j sub-tower. Tree decomposition of width h + 2, with three-corner cuts. |
| B, Theorem 2 | Softening is repelled at least threefold per level. |
| B, Theorem 3 | The three minimal towers, with exact softened maps r(r² + 3)/(3r² + 1), 4r/(1 + r)² and the Fano map, multipliers 3, 4 and 7, all flowing to the free law. Corner information is constant at every distance. |

## What this changes for the core intuitions

- **Space from logic without a drawn space.**
  - Each law's smallest exact self-reproduction selects a space: the gasket, the slit triangle, the Fano tower. Nothing is drawn
    except the requirement that every level obey the same law with the same counts. The growth exponents are 1.585, 2 and 1.771.
  - Parity alone reaches six exponents within six copies, so the law fixes the space only at its smallest size.
  - Every such space is finitely ramified. Exact self-reproduction with private hidden variables cannot build a space in which
    cutting off a region costs more than three points. Separation in two or three dimensions needs neighbouring copies to share
    hidden variables.
- **Growth of emergent information.** Each level adds log₂ c hidden bits per copy: 1 bit for the gasket and the slit triangle,
  log₂ 5 ≈ 2.32 bits for the Fano tower. Per variable this tends to log₂ c / h: 1/3, 1/3 and about 0.387 bits.
- **Universally influential cycles.**
  - At the hard law, corners at distance s^k are exactly as correlated as at distance 1. Parity shares 1 bit among the three and
    0 between any two; not-all-equal shares 0.082 bits between two.
  - That influence lives only at the hard law. A chance r of violating a copy grows m-fold per level, so the law holds only up to
    the scale holding about 1/r copies.
- **Possible and typical (everything relational).**
  - The allowed states are the knot at every level of every rebuilding tower, and that is what the canonical knot test reads.
  - Counts, a branch-internal measure, agree with them only in exact towers. For "x or (y ≠ z)" the relation survives while the
    counted law concentrates on a decomposable pair. Set-level emergence can persist where counted emergence fades.
- **The two/three boundary.** Exact towers beyond parity need hubs, which are equality fan-out. Without hubs only parity is rebuilt
  (`GEOMETRY-LAW-20261029-001A`).

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| A law that survives patterns of patterns keeps its emergence at every scale | `HUB-SURVIVORS-20261029-001` (survival read as relations) | **Refined.** Its allowed states do, which is what the canonical knot test reads. Its counted law may not: for "x or (y ≠ z)" it concentrates on a decomposable pair of tuples. Only exact towers keep both. |
| Self-reproduction would build space | The geometry question (question 9) | **Refined.** It builds spaces with definite growth exponents, including 2, but every one is finitely ramified: bounded treewidth, three-point cuts at every scale. |
| Scale-free correlations mark universally influential structure | The universally-influential-cycles intuition | **Qualified.** Exact towers keep their corner law at every distance, but only at the hard law. Any softening grows m-fold per level and destroys it (the classical picture for finitely ramified fractals). |

## Scoping and corrections

- **Redundant copies.** A doubled constraint inflates the copy count and changes nothing. The first scoping counted the
  tetrahedron with a doubled copy as a five-copy single-scale gadget (exponent log₂ 5). The census counts irredundant gadgets.
- **Pendants.** A constant-weight pendant is padding in the same way. The exponent table lists only pendant-free gadgets.
- **Wrong orbits.** The first mechanism test compared orbits with the representative placement instead of each gadget's own
  relation, and reported transitive gadgets as not transitive. Corrected before the checks.
- **Pinning.** At five copies every exact three-excluded gadget has a frozen hidden variable. At six copies that fails, so it is not
  claimed.
- **The multiplier.** In the three minimal towers every copy, not only the legs' copies, leaves exactly c extensions of an excluded
  tuple, which makes the multiplier exactly m. That holds in only 54 of 458 gadgets. Only the leg-copy statement (Lemma 4) is
  general.
- **Iterating in fractions.** Iterating the softened maps in exact fractions blows up with the degree. The trajectories use floats,
  and exactness rests on the polynomial identities.

## Literature (bounded)

- **Finitely ramified fractals.** Gefen, Mandelbrot and Aharony (1980): finitely ramified fractals have no order above zero
  temperature. Theorem 2 of ticket B is the hard-constraint analogue, with an explicit multiplier.
- **Hierarchical lattices.** Berker and Ostlund (1979), Kaufman and Griffiths (1981): renormalization is exact on lattices built by
  substitution. Their fixed points are studied for given interactions.
- **Self-similar graphs.**
  - The Sierpinski gasket graphs and the Sierpinski tetrahedron (dimension 2) are classical.
  - Bounded treewidth of post-critically finite self-similar graphs: for example arXiv 2011.02735.
- **Not found.**
  - A Fano-plane fractal.
  - A classification of hard laws that are fixed points of substitution by their own copies.
  - The renormalization of Boolean functions in arXiv cs/0608053 decimates inputs, not constraints, and is unrelated.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Theorems 1 to 3 and Lemma 4 | Fibre counting, linear algebra, orbit counting, isolated excluded tuples | Elementary |
| A, Theorem 5 | Exhaustive census | Candidate local delta |
| B, Theorem 1 | Substitution with private hidden variables | Elementary; the fractals are classical |
| B, Theorem 2 | Lemma 4 of A | Hard-constraint analogue of a classical fact |
| B, Theorem 3 | The three smallest exact gadgets | Explicit maps new here; the gasket classical |

**Did the perspective do real work?** Partly.
- **The question came from the program.** Which laws reproduce themselves, counts included? It led to the census, the mechanisms and
  the selection of a smallest space per law.
- **The tower theorems are classical in substance.** Finite ramification, bounded treewidth, and the absence of order away from the
  hard law are known for fractals.
- **The program's set-level reading made one distinction visible.** The allowed states keep the knot while the counted law drifts.

## Gaps

1. **"x or (y ≠ z)" beyond six copies.** Decoration can tune counts, so it might become exact at larger sizes.
2. **The remainder.** Why the 22 remainder gadgets are exact.
3. **Shared boundaries.** Substitutions in which neighbouring copies share hidden variables, the only route past finite
   ramification. Scoping on the boundaries of the tetrahedron and the octahedron, each face cut into four with shared midpoints and
   copies on every face, gave this:
   - parity reproduces itself exactly, with one completion per coarse solution;
   - not-all-equal does not: coarse assignments it forbids gain fine solutions.
4. **Softened flows.** The softened flow of gadgets without enough symmetry, beyond first order.
5. **Review.** No human or external review.

## Work ratio

- **Artifacts that changed a conclusion (2):** A, B.
- **Administrative:** the closure ledger, the discovery record and its disposition.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: exact self-similar laws and their towers | **Status:** Successful | Census to six copies: five classes besides not-all-equal, smallest sizes, factors and mechanisms. Structure theorem for exact towers. The three minimal towers, with exact softened maps. |
| Local direction: exact substitution with private hidden variables | Practically exhausted for space | Every tower is finitely ramified (bounded treewidth, three-point cuts), whatever its growth exponent. The open census questions ("x or (y ≠ z)" beyond six copies, the 22) would not change that. |
| Broader exploration: space from logic (question 9) | Obstruction learned, one route open | Private substitution builds hierarchical spaces with definite exponents, never separation in two or three dimensions. The open route is substitution whose neighbouring copies share their subdivided boundary. |
| Long-term goal: emergence across scales, space from logic | Capability gained and obstruction learned | Laws now select their own spaces with definite exponents: the gasket, the slit triangle, the Fano tower. Scale-free order is confined to hard laws on tree-like spaces. |
| Next recommendation: shared-boundary self-reproduction | **Next step:** Continue, with a fresh epic on shared-boundary self-reproduction | Ask which knots are exact counted fixed points when every face of a triangulated surface is cut into four with midpoints shared between neighbours. This is the triangular-lattice substitution, which is not finitely ramified. First discriminator: every class and orientation rule on the boundaries of the tetrahedron, octahedron and icosahedron and on small tori. Scoping: parity exact on the tetrahedron and octahedron, not-all-equal not. |
| Interest: that recommendation | **2/3 (Promising)** | If only linear laws survive, this joins the program's repeated parity-only results (native gluing, Pachner moves, memory = affine) into one statement about genuine space. If a non-linear law survives, it builds two-dimensional space from logic. Main uncertainty: parity's survival may be an artefact of small spheres, and orientation rules multiply the cases for asymmetric knots. |
| Execution: that next action | Deferred to the owner | No successor created. Alternatives: settle "x or (y ≠ z)" beyond six copies (1/3); explain the 22 remainder gadgets (1/3). Stop the shared-boundary route if no non-linear class is exact on the first triangulations under any orientation rule. |
