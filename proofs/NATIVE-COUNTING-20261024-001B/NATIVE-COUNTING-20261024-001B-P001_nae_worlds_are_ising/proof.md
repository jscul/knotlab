# Not-all-equal worlds count like an Ising model

Status: Proved

Ticket `NATIVE-COUNTING-20261024-001B`, 2026-10-24.

**What it uses:**
- from `NATIVE-COUNTING-20261024-001A-P001`: native counting with pins is #P-hard for not-all-equal, given Backens's dichotomy;
  networks without pins are left open there;
- from `NATIVE-HARDNESS-20261024-001` (closed): unsatisfiable native networks of not-all-equal are trees, so every closed network with
  a cycle is satisfiable;
- external theorems, cited as hypotheses and not admitted as local evidence:
  - **(KW)** the Kac–Ward formula (Kac and Ward 1952; short proof by Lis, Ann. Inst. H. Poincaré D 2016, arXiv:1502.04322). For a graph
    drawn in the plane with straight non-crossing edges, det(I − x Λ) = Z(x)², where Λ[(u→v), (v→w)] = exp(iθ/2) for w ≠ u, with θ
    the turning angle;
  - **(G)** on a surface of genus g, the even-subgraph sum is a signed combination of 4^g determinants (Cimasoni, arXiv:1101.5559;
    for perfect matchings, Galluccio and Loebl 1999);
  - **(CHL)** Cai, Huang and Lu, *From Holant to #CSP and back* (2012), Theorem 3.4 as quoted by Backens (Theorem 6). Holant([y₀, y₁, y₂] |
    [x₀, x₁, x₂, x₃]) on three-regular graphs is #P-hard unless x is degenerate, or x = M∘[1, 0, 0, 1] with (Mᵀ)⁻¹∘y affine or
    supported on two complementary inputs, or one of two forms of type [1, 1, 0, 0].

## Standard statement

**Setting.**
- **Closed worlds.** A *closed world* of not-all-equal is a native network with no legs: a loopless cubic multigraph G with n
  vertices (knots) and 3n/2 edges (bits). A vertex is satisfied when its three edges are not all equal.
- **The even-subgraph sum.** Z_G(x) = Σ x^|H| over the even subgraphs H of G, that is the edge sets meeting every vertex in an even
  number of edges.

**Theorem 1 (the identity).**
- **The count.** The number of satisfying assignments of a closed world is
  count = 2^(−n/2) · 3^n · Z_G(−1/3).
- **The Ising form.** Equivalently, it is 2^(−n/2) 3^n Z_Ising / (2^n cosh(b)^(3n/2)). Here Z_Ising is the partition function of the
  Ising model on G with coupling b, and tanh b = −1/3, that is e^(2b) = 1/2: an antiferromagnetic coupling.

**Corollary 2 (the sphere, given KW).**
- **A determinant.** For a closed world drawn in the plane with straight non-crossing edges,
  count = 2^(−n/2) 3^n √det(I + Λ/3), a determinant of size 3n.
- **Polynomial time.** So counting closed worlds on the sphere takes polynomial time. The square root is the positive one, since
  closed worlds are satisfiable.

**Remarks (cited).**
- **Higher genus (G).** With these determinant methods, a closed world on a surface of genus g needs 4^g determinants.
- **General cubic graphs (CHL).**
  - Not-all-equal is a generalized equality after a matrix M; its characteristic directions are (1, e^(±iπ/3)).
  - For every choice of cube roots in M, the transformed edge function (M Mᵀ)⁻¹ is neither affine nor supported on two complementary
    inputs, and not-all-equal is not degenerate.
  - So counting closed worlds is #P-hard on general cubic graphs, given (CHL).

**Reading.**
- **Counting cost tracks handles.** For not-all-equal, counting what emerges is a determinant on the sphere, and with these methods it
  costs four times as much per handle. In general it is hard. So the native genus, the topology built by the network itself
  (`SURFACE-GLUING-20261024-001`), controls the cost of counting.
- **The contrast with the topological knots.** For those knots the count is itself a function of the genus.

## Nearest known result

- **Theorem 1** is the high-temperature expansion of the Ising model, written through the Fourier transform of not-all-equal.
  Elementary; folklore risk high.
- **Corollary 2 and the remarks** apply classical results: Kac–Ward, Fisher and Kasteleyn; Galluccio–Loebl; Cimasoni; Cai–Huang–Lu.
- **The local contribution** is the reading: in the program's closed worlds, the emergent count of not-all-equal is an Ising partition
  function at the point e^(2b) = 1/2.

## Proof

### Theorem 1

- **The Fourier transform.** Write f for not-all-equal and f̂(y) = Σₓ (−1)^(x·y) f(x). By the weight of y, f̂ = [6, 0, −2, 0].
  - Weight 0: there are six allowed tuples.
  - Weight 1: the sum is 3 − 3.
  - Weight 2: the sum is 1 + 1 − 2 − 2 = −2.
  - Weight 3: the sum is 3·(−1) + 3·1 = 0.
- **Insert the inverse transform.** Put f(x) = 8⁻¹ Σ_y f̂(y) (−1)^(x·y) at every vertex and sum over assignments σ of the edges.
  - An edge e = uv with u ≠ v appears in the inputs of u and of v. So it contributes Σ over σₑ of (−1)^((y_{u,e} + y_{v,e}) σₑ),
    which is 2 if y_{u,e} = y_{v,e} and 0 otherwise.
  - The surviving terms are edge sets H, with y_v the indicator of H at v. Since f̂ vanishes on odd weights, H meets every vertex in 0
    or 2 edges: H is an even subgraph.
- **The weights.** H contributes 6 for each vertex outside it and −2 for each vertex on it. In a cubic graph, an even subgraph has as
  many vertices of degree two as edges. So
  count = 8^(−n) 2^(3n/2) Σ_H 6^(n−|H|) (−2)^|H| = 2^(−n/2) 3^n Σ_H (−1/3)^|H|.
- **The Ising form.** Expanding exp(b s_u s_v) = cosh b (1 + s_u s_v tanh b) gives Z_Ising = 2^n cosh(b)^|E| Z_G(tanh b). And
  tanh b = −1/3 means (e^(2b) − 1)/(e^(2b) + 1) = −1/3, that is e^(2b) = 1/2. ∎

### Corollary 2

- **The determinant.** By (KW), det(I + Λ/3) = Z_G(−1/3)².
- **The positive root.** A closed world with a cycle is satisfiable, since unsatisfiable native networks of not-all-equal are trees
  (`NATIVE-HARDNESS-20261024-001`). So the count is positive, and so is Z_G(−1/3).
- **Time.** The determinant has size twice the number of edges and is computed in polynomial time. ∎

## Checks

`check.py` uses the standard library only (seed 20261024). It confirms:
- **Theorem 1** exactly (rational arithmetic) on 40 random connected loopless cubic multigraphs with 4 to 10 vertices, and the Ising
  form numerically on those with at most 8 vertices.
- **Corollary 2** on 26 random planar cubic graphs with up to 16 vertices.
  - **The drawings.** Each starts from a prism drawn with convex faces and is refined by up to four chords inside convex faces. Each
    drawing is verified to have straight edges, no proper crossing, and no two edges leaving a vertex in the same direction.
  - **The results.** The determinant equals Z² every time, and for graphs with at most 18 edges the count equals 2^(−n/2) 3^n √det.
- **The hardness condition** for not-all-equal: none of the nine cube-root choices meets an exceptional case, and each choice
  reproduces not-all-equal.

**Disclosure.** A first version of the generator could insert a chord between two collinear edges of a face. That produced a drawing
with overlapping edges, where the determinant formula fails, as expected outside the hypotheses of (KW). The generator now rejects such
chords, and the drawing test checks for overlaps.

**Controls.**
- **The drawing must be planar.** The determinant formula fails for K(3,3) and for the Petersen graph drawn with crossings.
- **The power of 3 matters.** The count formula with 3^(n+1) disagrees.
- **The hardness test can say yes.** It accepts all-equal, a generalized equality with orthonormal factors, as an exceptional case.

## What this does not show

- **Local proofs of (KW), (G) and (CHL).** The determinant formula, the genus dependence and the hardness are cited.
- **The other knots' closed worlds.** Only not-all-equal is treated.
- **Approximate counting and phase transitions.** The antiferromagnetic coupling here is not critical on the honeycomb lattice, where
  the critical value of |tanh b| is 1/√3. Nothing further is examined.
