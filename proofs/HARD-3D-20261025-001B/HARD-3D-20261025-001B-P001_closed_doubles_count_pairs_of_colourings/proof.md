# Closed manifolds: the doubles count pairs of colourings

Status: Proved

## Standard statement

**Theorem 1.** For each finite group Γ below, the following problem is #P-hard under polynomial-time Turing reductions:
- **Input:** a triangulation of a closed orientable 3-manifold M.
- **Output:** |Hom(π₁(M), Γ)|.

The groups are:
- **S₃**;
- **every dihedral group D_2N of order 2N ≥ 6 whose order is not a power of 2 at least 16**, that is, N odd, N even and not a power
  of 2, or N = 4;
- **the quaternion group Q₈**;
- **the alternating group A₄**.

**Corollary 2 (class 2).** D₈ and Q₈ are nilpotent of class 2, so for them the problem is #P-hard.
- Samperton and Weiß give a polynomial algorithm for class-2 targets on closed triangulated manifolds. The revised version of their
  paper assumes |H²(M; Z(Γ))| bounded.
- That hypothesis cannot be dropped, unless every #P function is computable in polynomial time.
- Our instances have H²(M; Z/2) of dimension growing linearly with the graph.

**Theorem 3 (the identity).**
- **The instances.** Let G = (V, E) be a connected plane multigraph with n vertices and m edges. Let M_{G,k} be the double of the fin
  handlebody of G^(k) (ticket A), in which every edge is repeated k times.
- **The expansion.** Z_Γ(G, k) = |Hom(π₁(M_{G,k}), Γ)| = Σ_β c_β(G) β^k. This is a finite sum whose bases β are products, over the
  edges, of the numbers |C_Γ(λ)|²/ψ(1)², with λ ∈ Γ and ψ ∈ Irr(C_Γ(λ)).
- **The target coefficients.** The coefficient of T^m is:

| Γ | T | Coefficient of T^m |
| --- | --- | --- |
| S₃ | 9 | 2·P(G, 9)/3ⁿ |
| D_2N, N odd | N² | 2·P(G, N²)/Nⁿ |
| D_2N, N even, N ≠ 4 | N² | 2·(4/N)ⁿ·P(G, N²/4) |
| D₈ and Q₈ | 16 | P(G, 8) |
| A₄ | 16 | 3·P(G, 16)/4ⁿ |

Here P(G, q) is the number of proper q-colourings. For S₃, nine colours are pairs of three colours.

## Nearest known result

- **Kuperberg and Samperton (2018)** prove #P-completeness, by almost parsimonious reductions, for non-abelian simple groups on
  homology spheres.
- **Samperton and Weiß (2026).**
  - Counting is #P-complete for every non-abelian group when the input is any finite presentation.
  - Class-2 targets are polynomial on closed triangulated manifolds; the revised version assumes |H²(M; Z(Γ))| bounded.
  - They name S₃ and the dihedral group of order 16 as the most interesting open cases for 3-manifold groups.
- **Burton, Maria and Spreer (2015)** prove the r = 4 Turaev–Viro invariant #P-hard through cubic forms.
- **What is new here.**
  - #P-hardness for S₃ and the other groups listed, on closed manifolds.
  - The identity: the double counts pairs of colourings.
  - The necessity of the bounded-H² hypothesis.
- **Novelty.** The bounded scan (`research/HARD-3D-20261025-001/scan.md`) and a later search found no earlier proof. The order-16
  dihedral group is not settled here (Section 5). Folklore risk: low to medium.

## 1. The double and its fundamental group

**Notation** (from ticket A):
- G is a connected plane multigraph with faces F and outer face f₀.
- H is the handlebody, with feet D_u^± in the northern and southern hemispheres (mirror images under ρ).
- γ_e are the curves, A_e their annular neighbourhoods, and T_e = T² × [0, 1] the fins.
- X_G = H ∪ ⋃ T_e, and M_G = X_G ∪_∂ X̄_G is the double. Write M_{G,k} = M_{G^(k)}.

**Lemma 1.1 (decomposition).** M_G = (Y \ N(L)) ∪ ⋃_e Q_e, where:
- Y = H ∪_{∂H} H̄ ≅ #ⁿ(S¹ × S²) and L = ⋃_e γ_e ⊂ ∂H;
- each Q_e is homeomorphic to Σ₁,₁ × S¹, glued along ∂N(γ_e) with its fibre to the longitude λ_e (the surface framing of γ_e in ∂H)
  and the boundary of the punctured torus to the meridian μ_e.

*Proof.*
- **The boundary.** ∂X_G = S ⊔ ⊔_e T_e × {1}, where S = (∂H \ ⋃ A_e) ∪ ⋃ A″_e and A″_e is the complementary annulus of A′_e in
  T_e × {0}.
- **The handlebodies.** In the double, H and H̄ meet along ∂H \ ⋃ A_e. So H ∪ H̄ is Y with an open neighbourhood of L removed, and its
  boundary tori are A_e ∪ Ā_e.
- **The fins.** Each fin meets its mirror along A″_e and T² × {1}, giving Q_e = T² × [0, 2] with A″ × {0} identified to A″ × {2}.
- **Q_e is a Seifert piece.** π₁(Q_e) is the HNN extension of Z² = ⟨g, τ⟩ along ⟨g⟩ by the identity, which is ⟨g⟩ × F(τ, κ). So
  Q_e ≅ Σ₁,₁ × S¹ with fibre g.
- **The gluing torus.** The boundary of Q_e is A′ × {0} ∪ A′ × {2}, glued to A_e ∪ Ā_e. Its circles parallel to g are the
  surface-framed longitudes of γ_e. The loop crossing A′ at both ends is the meridian, and in Q_e it equals [τ, κ]. ∎

**Lemma 1.2 (face regions).** ∂H \ L is the disjoint union of regions Σ_f, one per face f.
- **A bounded face.** Σ_f is the northern face disk f⁺, its mirror f⁻, and a band on each handle h_u for each corner (u, f). Its
  fundamental group is free, on loops x_i that go down the band of corner 1 and up the band of corner i. In π₁(H), x_i maps to
  a_{u₁}⁻¹ a_{u_i}, and in π₁(H̄) it maps to ā_{u₁}⁻¹ ā_{u_i}.
- **The outer face.** f₀⁺ and f₀⁻ are joined across the equator into an annulus. Its fundamental group also contains, for each corner u,
  a loop that goes down the band of u and returns across the equator. That loop maps to a_u⁻¹ in π₁(H) and to ā_u⁻¹ in π₁(H̄). The
  equator loop is trivial in both.

*Proof.* The arcs of the curves cut the northern and southern hemispheres into the face regions. The strands of the curves cut each
handle annulus into bands, one per corner, each joining the corner of f⁺ to the mirror corner of f⁻. Paths on ∂B are null-homotopic
rel endpoints in B and in B̄, so a band traversed from the + foot to the − foot contributes a_u⁻¹, respectively ā_u⁻¹. ∎

**Proposition 1.3 (presentation).** π₁(M_G) has generators a_u, ā_u (u ∈ V), s_f (f ∈ F, with s_{f₀} = 1) and τ_e, κ_e (e ∈ E), and
relations:
- ā_u = a_u for every corner u of f₀;
- a_{u₁}⁻¹ a_{u_i} = s_f ā_{u₁}⁻¹ ā_{u_i} s_f⁻¹ for corners u₁, u_i of a bounded face f;
- [τ_e, λ_e] = [κ_e, λ_e] = 1, with λ_e = a_v⁻¹ a_u;
- [τ_e, κ_e] = s_{f′} s_f⁻¹, where f and f′ are the faces beside e.

*Proof.*
- **The groupoid van Kampen theorem** for Y \ N(L) = H ∪_{⊔Σ_f} H̄. Base point in f₀, with base paths through B and through B̄. This
  gives the generators a_u and ā_u, the HNN letters s_f = p_f p̄_f⁻¹, and the face relations from Lemma 1.2.
- **The meridian.** It crosses from Σ_f to Σ_{f′} through H and returns through H̄. Its short paths are homotopic to base-path
  differences, so μ_e = s_{f′} s_f⁻¹.
- **The Seifert pieces.** Each Q_e adds τ_e and κ_e, commuting with the fibre λ_e and with [τ_e, κ_e] = μ_e. ∎

**Independent checks of the model** (check parts 1 and 2):
- The presentation reproduces T³ # S¹×S² for one edge, T³ # T³ # S¹×S² for a path of two edges, and (Σ₂ × S¹) # S¹×S² for a doubled
  edge, for S₃ and D₈.
- It reproduces the graph manifolds that the doubles over cycles are by a direct description: pants × S¹, with a punctured-torus
  Seifert piece glued to each boundary torus by the flip.
- It does not depend on the choice of outer face or on mirroring.

## 2. The count and its exponential polynomial

**Proposition 2.1.** |Hom(π₁(M_G), Γ)| = Σ_{(y,σ)} [cons] Π_e W(λ_e, μ_e). Here:
- y ∈ Γ^V and σ ∈ Γ^F with σ_{f₀} = e;
- λ_e = y_v⁻¹ y_u and μ_e = σ_{f′} σ_f⁻¹;
- W(λ, c) = #{(τ, κ) ∈ C(λ)² : [τ, κ] = c};
- "cons" means there is a ȳ with ȳ_u = y_u on f₀ that satisfies the bounded-face relations. Such a ȳ is unique, because G is connected.

*Proof.* A homomorphism is a choice of (y, ȳ, σ, τ, κ) satisfying the relations. For each edge, τ_e and κ_e range over pairs in C(λ_e)
with commutator μ_e. ∎

**Proposition 2.2 (thickening).** Z(G, k) = Σ_{(y,σ) on G} [cons] Π_e W_{λ_e}^{*k}(μ_e), where *k is the k-fold convolution over
C(λ).

*Proof.*
- **Digons.** The k parallel copies of e bound k − 1 digons, each with corners u and v.
- **Their variables.** The relation of a digon d forces σ_d into the coset {σ : σ⁻¹ g σ = ḡ} = C(g)σ₀, where g = y_u⁻¹ y_v. The
  adjacent outer faces lie in the same coset.
- **Telescoping.** The weights W(λ, σ_{d_i} σ_{d_{i−1}}⁻¹) vanish unless the step lies in C(λ) = C(g). Summing over the digon variables
  telescopes into the convolution power. ∎

**Proposition 2.3 (spectrum).**
- W_λ is a class function on C(λ). By Frobenius, #{(τ, κ) ∈ K² : [τ, κ] = c} = |K| Σ_ψ ψ(c)/ψ(1), so its Fourier coefficients are
  Ŵ_λ(ψ) = |C(λ)|²/ψ(1)².
- Hence W_λ^{*k}(c) = Σ_{ψ ∈ Irr C(λ)} (ψ(1)/|C(λ)|)·(|C(λ)|²/ψ(1)²)^k·ψ(c).
- So Z(G, k) is an exponential polynomial whose bases are products, over the edges, of the numbers |C(λ)|²/ψ(1)².
- **Check part 4.** For S₃ on two graphs and for D₈ on one, the closed counts for k = 1, …, K are fitted exactly by these bases, and two
  further values are reproduced. ∎

## 3. The target coefficients

**Lemma 3.1 (Potts duality).** Let H be a plane graph, possibly disconnected, on n vertices. Let Q be a set of q elements and f₀ a face.
Then

  Σ_{σ : F(H) → Q, σ(f₀) fixed} Π_{e ∈ E(H)} ([σ_{l(e)} = σ_{r(e)}] − 1/q) = q⁻ⁿ·P(H, q).

*Proof.*
- **Pinning.** By symmetry the unpinned sum is q times the pinned one.
- **Rewriting.** The weight is (−1/q)(1 + v*·δ) with v* = −q. So the unpinned sum is (−1/q)^|E| Z(H*; q, −q), where H* is the dual and
  Z(Γ; q, v) = Σ_σ Π_e (1 + vδ_e).
- **Duality.** For a plane graph with k components, Z(H*; q, v*) = q^(|F|−k) v^(−|E|) Z(H; q, v) when vv* = q. This follows from
  Z(H; q, v) = q^k v^(n−k) T(H; 1 + q/v, 1 + v), from T(H; x, y) = T(H*; y, x), and from |F| − k − |E| = 1 − n.
- **Conclusion.** With v = −1, Z(H; q, −1) = P(H, q). So the unpinned sum is q^(1−n) P(H, q), and the pinned sum is q⁻ⁿ P(H, q). ∎

**Theorem 3.2 (S₃).** The coefficient of 9^(mk) in Z(G, k) is 2·P(G, 9)/3ⁿ.

*Proof.*
- **(i) The bases.** The per-edge factors are:
  - 36 for λ = e with a one-dimensional ψ;
  - 9 for λ = e with ψ = χ₂, and for λ a rotation with any of the three ψ;
  - 4 for λ a reflection.

  A product equals 9^m only when every factor is 9, since 36 and 4 are even.
- **(ii) The coefficient.** It is Σ_{(y,σ)} [cons] Π_e f(λ_e, μ_e), where:
  - f(rotation, μ) = Σ_{ψ ∈ Irr A₃} (1/3)ψ(μ) = [μ = e];
  - f(e, μ) = (2/6)χ₂(μ), which equals 2/3, −1/3 and 0 on the identity, rotations and reflections;
  - f(reflection, ·) = 0.
- **(iii) One coset.** A nonzero term has every edge difference in A₃. So all y_u lie in one coset of A₃ (2 choices); write them as
  c ∈ Z₃^V.
- **(iv) The face variables are rotations.** The weight f(e, ·) vanishes on reflections, rotation edges force equality, σ_{f₀} = e and
  the dual graph is connected. So every σ_f ∈ A₃. Conjugation by A₃ fixes the differences y_u⁻¹ y_w ∈ A₃, so ȳ = y is consistent, and
  consistency is automatic.
- **(v) A Potts model.** σ is constant across rotation edges, so it is a function on the faces of H_c = (V, {e : c_u = c_v}). On
  A₃ ≅ Z₃ its weight is [x = 0] − 1/3. By Lemma 3.1 the σ-sum is 3⁻ⁿ P(H_c, 3).
- **(vi) Pairs of colourings.** Summing over the 2 cosets and over c gives 2·3⁻ⁿ Σ_c P(H_c, 3) = 2·3⁻ⁿ P(G, 9). For the last step,
  identify the 9 colours with pairs (c, c̄) ∈ Z₃²: an edge is monochromatic exactly when c_u = c_v and c̄_u = c̄_v. ∎

**Theorem 3.3 (dihedral groups).** Let Γ = D_2N = R ⋊ ⟨s⟩ with R ≅ Z_N, and let T = N².
- **N odd.** The same proof gives 2·P(G, N²)/Nⁿ.
  - The degree-2 characters sum to N[k = 0] − 1 on r^k and vanish on reflections, so the identity weight is [k = 0] − 1/N on R.
  - Non-identity rotations have C = R of order N, which gives continuity.
  - Reflections have |C| = 2, so their factor is 4 ≠ N².
- **N even, N ≠ 4.** The coefficient is 2·(4/N)ⁿ·P(G, N²/4).
  - The degree-2 characters sum to N[k = 0] − 1 − (−1)^k. The central weight is [x = 0] − 1/(N/2) on R² = ⟨r²⟩ and 0 elsewhere, which
    is a Potts model with q = N/2.
  - Central edges, those with c_u − c_v ∈ {0, N/2}, carry this weight. Non-central rotations give continuity. Reflections, with
    |C| = 4, are excluded.
  - Σ_{c ∈ Z_N^V} P(H_c, N/2) = 2ⁿ·P(G, N²/4).
- **N = 4 (D₈).** The coefficient is P(G, 8).
  - Every non-central element has an abelian centralizer of order 4, so its factor is 16 = T.
  - Central edges carry a Potts weight with q = 2 on the centre.
  - The labellings y ∈ D₈^V are unrestricted, and consistency is automatic because σ is central.
  - So the coefficient is Σ_y 2⁻ⁿ P(H_y, 2) = Σ_{κ ∈ (D₈/Z)^V} P(H_κ, 2) = P(G, 8).

**Theorem 3.4 (Q₈ and A₄).**
- **Q₈** has the character table and centralizer orders of D₈, so the D₈ argument applies word for word and gives P(G, 8).
- **A₄.** Take the Potts set to be V₄.
  - The weight (3/12)χ₃ equals [x = 0] − 1/4 on V₄ and 0 on 3-cycles.
  - Non-identity elements of V₄ have centralizer V₄, of order 4, which gives continuity.
  - 3-cycles have |C| = 3, so their factor is 9 ≠ 16.
  - There are 3 cosets of V₄, which gives 3·4⁻ⁿ·P(G, 16).

**Uniqueness of the target base.** The factors are:
- 4N² for central λ with a one-dimensional ψ;
- N² for central λ with a degree-2 ψ, and for non-central rotations;
- 4 (N odd) or 16 (N even) for reflections.

A product equal to N^(2m) needs 4^(a+c) = N^(2c) when the reflection factor is 4, or 2^(a+2c) = N^c when it is 16. Here a counts
central one-dimensional factors and c counts reflection factors.
- For N odd, or N even and not a power of 2, this forces a = c = 0.
- For N = 4, reflections are themselves target factors.
- For Q₈ the factors are 64 and 16.
- For A₄, 144^a 16^b 9^c = 16^m forces a = c = 0.
- For N = 2^j with j ≥ 3 the target collides with a = (j − 2)c (Section 5).

## 4. Hardness

**Proof of Theorem 1.**
- **The source problem.** For a connected planar G, P(G, q) is #P-hard to compute for every q in {9, N², N²/4, 8, 16}. This is
  Vertigan (2005), cited: the planar chromatic polynomial is #P-hard to evaluate at every algebraic q other than 0, 1 and 2, and each
  of these q is at least 8.
- **The reduction.**
  - Build triangulations of M_{G,k} for k = 1, …, K. Here K, the number of distinct bases, is polynomial in m.
  - Ask the oracle for each count.
  - Solve the Vandermonde system; the bases are distinct.
  - Read off the target coefficient.
- **Sizes.** The sizes are polynomial. Triangulating the explicit handle description of the double is standard, and is cited.
- **Membership in #P.** As in ticket A, the problem is in #P. ∎

**Proof of Corollary 2.** M_{G,k} has b₁ = n + 2mk, and its homology is torsion-free, so H²(M; Z/2) ≅ H₁(M; Z/2) is unbounded. ∎

## 5. The order-16 dihedral group

- **The identity holds.** On the target channels it gives 2·P(G, 16)/2ⁿ (checked on the triangle and on the theta graph).
- **But the bases collide.** 256·16 = 64², so the coefficient of 64^(mk) mixes the target with labellings having equally many central
  edges in one-dimensional channels and reflection edges.
  - A cycle carries an even number of reflection edges, so on the triangle nothing can mix in.
  - On C₄ the coefficient is 6522 = 6330 + 192: the identity plus a nonzero contamination (check part 4).
- **What closing it needs.** A second independent parameter, for example a gadget that tells reflections from central edges. This is
  left open.

## Check

`check.py` uses the standard library only and runs in about 130 s. Its result is `result.json`.

1. **Identified manifolds**, for S₃ and D₈. Every count from the presentation equals an independent count:

   | Manifold | S₃ | D₈ |
   | --- | --- | --- |
   | Single edge: T³ # S¹×S² | 288 | 1408 |
   | Path of two edges: T³ # T³ # S¹×S² | 13824 | 247808 |
   | Doubled edge: (Σ₂ × S¹) # S¹×S² | 4176 | 47104 |
   | Doubles over C₃ and C₄, as graph manifolds | equal | equal |

2. **Invariance.** One value over all choices of outer face and over mirroring, on the diamond, K₄, C₄ and the triangle with a pendant
   edge.
3. **Digon collapse.** The full counts of the doubled graphs equal the collapsed formula for S₃ on C₃ and C₄ and for D₈ on C₃. The
   numbers have up to twelve digits.
4. **Exponential polynomials.**
   - For S₃ on C₃ and C₄ (10 and 15 bases) and for D₈ on C₃ (4 bases), the closed counts for k = 1, …, K are fitted exactly by the
     stated bases, and two further values are reproduced.
   - The coefficients of the target bases are 112/3, 304/3 and 336, equal to the identities.
   - **Order-16 dihedral group.** 256·16 = 64², a collision. On C₃ no contamination can occur, by parity. On C₄ the coefficient of
     64^(mk) is 6522, against the identity's 6330: contamination 192.
5. **Coefficient identities**, in exact rationals:
   - S₃ on nine graphs (C₃, C₄, C₅, three theta graphs, diamond, K₄, triangle with pendant);
   - D₈ on five, the order-10 dihedral group on three, the order-12 one on two;
   - Q₈ and A₄ on three each;
   - the order-16 group on its target channels, on two graphs.
6. **Controls.**
   - A genus-1 rotation system for the diamond (one face) breaks the S₃ identity, which shows that planarity is used.
   - The wrong targets 2·P(G, 8)/3ⁿ and 2·P(G, 3) for S₃, and 2·P(G, 9)/3ⁿ for D₈, are rejected.
   - The abelian group Z₆ gives equal closed counts on C₄ and on the triangle with a pendant edge. Their numbers of 3-colourings
     differ.

## Scope

- **Covered.** Closed orientable 3-manifolds that are doubles of fin handlebodies over plane multigraphs.
- **Kind of reduction.** Turing reductions by interpolation, on instances with growing first Betti number.
  - Solvable targets see nothing on homology spheres.
  - The class-2 consequence concerns unbounded H² only. It does not contradict the revised Samperton–Weiß theorem.
- **Cited, not proved.** Hardness of planar colouring and polynomial-time triangulation.
- **No overclaim.** No claim about P versus NP or about physics.
