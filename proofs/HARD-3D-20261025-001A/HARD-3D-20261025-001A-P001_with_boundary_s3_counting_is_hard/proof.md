# With boundary, counting maps into S3 is #P-hard

Status: Proved

## Standard statement

**Theorem.** The following problem is #P-hard under polynomial-time Turing reductions:
- **Input:** a triangulation of a compact orientable 3-manifold M (with boundary).
- **Output:** |Hom(π₁(M), S₃)|.

The same holds for the dihedral group D₈ of order 8.

**The instances.** For a connected plane multigraph G = (V, E), the **fin handlebody** X_G is a compact orientable 3-manifold with
π₁(X_G) = ⟨a_u (u ∈ V), t_e (e ∈ E) | [t_e, a_u a_v⁻¹] (e = uv)⟩.

**Proposition 1 (the count).** For every finite group H,

  |Hom(π₁(X_G), H)| = Σ_{y ∈ H^V} Π_{e=uv} |C_H(y_u y_v⁻¹)|.

**Proposition 2 (interpolation).** Let G^(k) be G with every edge repeated k times, drawn as parallel arcs, and let
Z_k = |Hom(π₁(X_{G^(k)}), S₃)|.
- The numbers N(a, b, c) of labellings y ∈ S₃^V can be recovered from Z₁, …, Z_K, where K = (m+1)(m+2)/2. Here a, b and c are the
  numbers of edges whose difference y_u y_v⁻¹ is the identity, a rotation and a reflection.
- N(0, m, 0) = 2·P(G, 3), twice the number of proper 3-colourings.

## Nearest known result

- **Kuperberg and Samperton (2018)** prove #P-completeness for every fixed non-abelian simple group, on closed manifolds and even
  homology spheres. Samperton's thesis treats knot complements as well.
- **Samperton and Weiß (2026)** prove #P-completeness for every non-abelian group when the input is any finite presentation. They list
  S₃ as an open case for 3-manifold groups.
- **What is new here.** A 3-manifold realization of a spin model on an arbitrary plane graph, with centralizer sizes as edge weights,
  for which interpolation is elementary. The bounded scan (`research/HARD-3D-20261025-001/scan.md`) found no earlier treatment of S₃.
  The closed case is ticket B.

## 1. The construction

Fix a connected plane multigraph G with n vertices and m edges, drawn in the plane.

**The handlebody.**
- Let B be the unit ball and ρ the reflection of R³ in the equatorial plane. Since ρ is orientation-reversing on ∂B, it is the right
  identification for an orientable 1-handle seen from outside.
- Draw G in the open northern hemisphere of ∂B, with a small disk D_u⁺ around each vertex.
- Let D_u⁻ = ρ(D_u⁺) and the southern drawing be the mirror image.
- Attach a 1-handle h_u ≅ D² × [−1, 1] for each vertex, along D_u⁻ and D_u⁺, so that the identification of ∂D_u⁻ with ∂D_u⁺ along the
  handle is ρ. The result is a genus-n handlebody H.
- **Generators.** Let a_u ∈ π₁(H, ∗), with ∗ ∈ ∂B, be the loop that runs inside B to D_u⁻, through h_u to D_u⁺, and back inside B.
  Then π₁(H) is free on the a_u.

**The curves.** For an edge e = uv, the curve γ_e is made of four pieces:
- the drawn arc α_e⁺ from ∂D_u⁺ to ∂D_v⁺;
- the straight strand of h_v from ∂D_v⁺ to ∂D_v⁻;
- the mirror arc ρ(α_e⁺), traversed from ∂D_v⁻ to ∂D_u⁻;
- the straight strand of h_u from ∂D_u⁻ to ∂D_u⁺.

**The curves are disjoint.**
- Northern arcs are disjoint because the drawing is plane.
- Southern arcs are their mirror images.
- North and south are separated by the equator.
- On h_u the strands run straight. They are parallel because the endpoints on ∂D_u⁺ and ∂D_u⁻ correspond under ρ, which is the handle
  identification.

**Classes and fins.**
- The class of γ_e in π₁(H) is conjugate to a_u a_v⁻¹.
- Let A_e be disjoint annular neighbourhoods of the γ_e in ∂H.
- For each edge, glue a **fin** T_e = T² × [0, 1] to H, identifying a neighbourhood A′_e of a circle S¹ × {pt} × {0} with A_e, core to
  core, orientations compatible.
- X_G = H ∪ ⋃_e T_e is a compact orientable 3-manifold with boundary.

## 2. The fundamental group and the count

By van Kampen along each annulus, π₁(H ∪_{A_e} T_e) = π₁(H) ∗_{⟨γ_e⟩} Z², where Z² = ⟨g_e, t_e⟩ and the core of A′_e is g_e ↦ γ_e.
Hence

  π₁(X_G) = ⟨a_u, t_e | [t_e, w_e]⟩,

with w_e a conjugate h a_u a_v⁻¹ h⁻¹. Replacing t_e by h⁻¹ t_e h gives the stated presentation.

**Proof of Proposition 1.** A homomorphism is determined by the images y_u of the a_u and τ_e of the t_e. The only conditions are that
τ_e commutes with y_u y_v⁻¹, which leaves |C_H(y_u y_v⁻¹)| choices for each edge. ∎

## 3. Interpolation and colourings

**The edge weights.**
- Parallel copies of an edge give parallel curves, so X_{G^(k)} exists. Each copy contributes its own centralizer factor:
  Z_k = Σ_y Π_e |C(y_u y_v⁻¹)|^k.
- In S₃ the centralizer sizes are 6 for the identity, 3 for the two rotations and 2 for the three reflections. So
  Z_k = Σ_{a+b+c=m} N(a, b, c)·(6^a 3^b 2^c)^k.

**Proof of Proposition 2.**
- **The nodes are distinct.** λ(a, b, c) = 6^a 3^b 2^c = 2^(a+c) 3^(a+b) determines a + c and a + b, hence (a, b, c) when a + b + c = m.
- **The system is solvable.** The K equations for k = 1, …, K form a Vandermonde system in the unknowns N(a, b, c), so they determine
  them. The numbers have polynomially many bits, so Gaussian elimination over Q takes polynomial time.
- **All edges rotations.** Every edge difference lies in A₃ \ {e} exactly when all y_u lie in one coset of A₃ (2 choices, since G is
  connected) and adjacent labels differ within it (3 elements). So N(0, m, 0) = 2·P(G, 3). ∎

**Proof of the Theorem.**
- **The source problem.** Counting proper 3-colourings of planar graphs is #P-hard. This is cited: Vertigan (2005) showed that the
  chromatic polynomial of planar graphs is #P-hard to evaluate at every algebraic q other than 0, 1 and 2.
- **The reduction.** Given a connected planar G:
  - build triangulations of X_{G^(k)} for k = 1, …, K, each with O(n + km) handles;
  - ask the oracle for each Z_k;
  - solve for N(0, m, 0), and output half of it.
- **Triangulation is cited.** Producing a triangulation from such an explicit handle description in polynomial time is standard: each
  handle and fin is a fixed triangulated piece, and the curves are polygonal.
- **Membership in #P.** The count is a #P quantity, the number of S₃-labellings of the triangulation's edges divided by 6^(vertices − 1).
  So the problem is #P-complete under Turing reductions.
- **D₈.** The centralizer sizes are 8 on the centre and 4 elsewhere. The nodes 8^a 4^(m−a) are distinct. The labellings with no
  central edge number |Z|^n·P(G, [D₈ : Z]) = 2^n·P(G, 4), and q = 4 is a hard point. ∎

## Check

`check.py` uses the standard library only and runs in about 4 s. Its result is `result.json`.
- **Brute force against the formula.** Enumerating all images of all generators gives the same count as Proposition 1 on the
  triangle, on the triangle with a doubled edge and on the path, and for D₈ on the triangle.
- **Interpolation.** On seven plane (multi)graphs it recovers N(0, m, 0) = 2·P(G, 3): the triangle, square, K₄ (giving 0), diamond,
  wheel W₄, triangle with a doubled edge, and path. On four of them it recovers 2^n·P(G, 4) for D₈.
  - The nodes are distinct.
  - An extra value Z_{K+1} is reproduced, which confirms that the expansion is complete.
- **Controls.**
  - The abelian group Z₆ gives equal counts, for every k, on a square and on a triangle with a pendant edge. Their numbers of
    3-colourings differ.
  - The wrong targets P(G, 3) and 2·P(G, 4) are rejected.
  - Values with a multiplicative coincidence, 2, 4 and 8, are detected as colliding nodes.

## Scope

- **Covered.** Compact orientable 3-manifolds with boundary.
- **Closed manifolds.** These are ticket B, where doubling adds a dual sector.
- **Kind of reduction.** Turing, not parsimonious.
- **What the instances carry.** First Betti number growing with G. Every homomorphism from a homology sphere into a solvable group is
  trivial, so solvable targets need homology.
- **Cited, not proved.** Hardness of planar colouring (Vertigan) and polynomial-time triangulation.
- **No overclaim.** No claim about P versus NP.
