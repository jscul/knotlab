# Five per handle, Tutte's number per planar piece

Status: Proved

Ticket `THREEFOLD-AMPLITUDE-20261030-001A`, 2026-10-30.

**What it uses:**
- **`SPACE-SELECTION-20261030-001A`:**
  - the corner relation R of a gadget;
  - the sector expansion R = (ζ − ζ⁻¹)^(−n) Σ_ε s_A ζ^(ε·s) Z(ε) (Lemma 1);
  - exactness ⟺ the mixed sector sums vanish and Z(+++) ≠ 0 (Theorem 2).
- **`SPACE-SELECTION-20261030-001C`, Theorem 2 (the duality).**
  - For a three-fold odd gadget, Z(ε) = (−i√3)^(n−1) ε_A ε_B ε_C N\*(ε), at ζ = e^(iπ/3).
  - N\*(ε) counts the proper phase assignments of the dual G\* with corner phases ε.
- **`THREEFOLD-SPACES-20261030-001A`:**
  - Theorem 1: a connected cubic system that is not 2-colourable is minimally so, and its incidence matrix is SNS;
  - Theorem 2 (splice calculus): every nontrivial tight cut is a 3-edge splice cut, and signs of perfect matchings factor across it. So H is
    SNS iff both pieces are SNS for a common sign pattern on the cut;
  - the gadget builder.
- **`THREEFOLD-GRAMMAR-20261030-001A`:**
  - the braces of a three-fold space are Heawood graphs, doubled squares and Pfaffian glue braces (Theorems 2 and 5);
  - the doubled square is SNS exactly when an odd number of its four parallel classes is negated (Theorem 2(ii)).
- **`THREEFOLD-SURFACES-20261030-001A`:** the genus formula. It is used only in Corollary 7.
- **External, not replayed:**
  - Lovász–Plummer, *Matching Theory*, Theorem 4.1.6: every matching covered bipartite graph has a bipartite ear decomposition;
  - braces on at least six vertices are 3-connected;
  - Kasteleyn: every planar bipartite graph has a signing satisfying the face condition, and it is Pfaffian;
  - Tutte's tree-trinity theorem (1948) and the root independence of arborescence numbers of balanced digraphs, in the form presented by
    Mathews (2017, Theorem 3.4, its proof, and Definition 3.5). The Tutte matchings with a given outer triangle are in bijection with the
    spanning arborescences of each of the trinity's three digraphs.
  - Kálmán (2013, Theorem 10.1): the arborescence number is the number of hypertrees.

## Why this ticket exists

The owner asked whether the knot's own number on its three-fold spaces reads off the topology the knot builds. A probe found λ(0) = 5^genus on
twelve spaces whose glue is doubled squares, and 2·5⁶ on the twisted cube. This ticket proves what λ(0) is: a product over the space's
pieces. Each Fano atom contributes 5, and each planar piece of glue contributes Tutte's tree-trinity number.

## Standard statement

**Setting.**
- **Signed systems.** A *signed system* H is a list of lines, each a triple of points with repetition allowed, so a line may hold a point twice.
  - A *signing* is a set of incidences at which the point's colour is complemented on that line. Repeated incidences of a point on a line
    carry the same sign.
  - A 2-colouring is *proper* on a line when the line's three seen values are not all equal. H is *colourable* when some colouring is proper
    on every line.
  - H is *cubic* when every point has three incidences and every line three; B(H) is its incidence (multi)graph.
  - The signing is *Pfaffian* when all perfect matchings of B(H) contribute to the determinant of the signed incidence matrix with one sign,
    i.e. the matrix is SNS.
- **Switching.** *Switching* a point or a line flips the signs of all its incidences. A *switching class* is the set of signings related by
  switchings.
- **Amplitude.**
  - A(H, L) is half the number of colourings proper on every line except L.
  - If H is not colourable, each such colouring makes L constant as seen. Flipping all colours exchanges the two constant values, so A(H, L)
    counts them with L's seen value fixed.
  - H has a *corner-independent* amplitude a(H) when A(H, L) is the same for every line L.
- **Gadgets.** A three-fold odd gadget G has n triangles, contacts of three triangles with an odd number of base incidences, and three
  distinct corner triangles. Its dual H = G\* ∪ {L₀} has the triangles as points, and the contacts and the corner line L₀ as lines. It is
  cubic with n points and n lines.
- **Trinities.** Let P be a planar cubic bipartite brace on at least six vertices, with its points and lines as the two colour classes.
  - Its planar dual T is a triangulation whose triangles are 2-coloured: lines white, points black. It is therefore a *trinity*: its
    vertices, the faces of P, are properly 3-coloured.
  - A *Tutte matching* with outer triangle L matches every line other than L to a face around it, bijectively onto the faces not around L.
  - Their number |M_T(L)| is Tutte's tree-trinity number ρ(P).

**Results.**
- **Lemma 1 (signings).**
  - (i) The Pfaffian signings of a matching covered bipartite multigraph form one switching class. A Pfaffian signing never gives two
    parallel edges different signs.
  - (ii) Switching changes no number of colourings of H − L, for any line L.
- **Theorem 2 (the amplitude identity).** Let G be a connected three-fold odd gadget with n triangles whose dual H is not 2-colourable. Then
  the knot is exact on G and λ(0) = (−1)^(n−1) A(H, L₀) ≠ 0.
- **Lemma 3 (point lemma).** Let H be a signed system that is not colourable, and p a point with three incidences. The incidences lie on
  lines ℓ₁, ℓ₂, ℓ₃, which need not be distinct, with signs t = (t₁, t₂, t₃).
  - For y ∈ {0,1}³ let N(y) count the colourings of the points other than p that are proper on every line when the i-th incidence of p is
    made to see y_i.
  - Then N(c ⊕ t) = 0, and N(c ⊕ t ⊕ e_i) = A(H, ℓ_i), for c = 0, 1 and i = 1, 2, 3.
- **Theorem 4 (factorization).** Let H be a connected cubic signed system with a Pfaffian signing, and ∂(X) a nontrivial tight cut of B(H),
  where the shore X has one point more than it has lines.
  - **The cut.** Its three cut edges join points p₁, p₂, p₃ of X (the *ports*) to lines ℓ₁, ℓ₂, ℓ₃ of the other shore X̄, with signs
    s = (s₁, s₂, s₃). Neither the ports nor the lines need be distinct.
  - **The pieces.** For τ ∈ {0,1}³:
    - H_X(τ) is X with a new line z on the ports, signed τ;
    - H_X̄(τ) is X̄ with a new point z on ℓ₁, ℓ₂, ℓ₃, signed τ ⊕ s;
    - all other signs are as in H.

    By the splice calculus there is a τ for which both pieces are Pfaffian. Fix one.
  - **The statement.** Let B be one piece and H′ the other. Suppose B is not colourable and A(B, ·) takes one value a(B) > 0 on the lines
    through or equal to z. Then:
    - for every line L of H′ other than z, A(H, L) = a(B) · A(H′, L);
    - H′ is not colourable.
- **Proposition 5 (brace amplitudes).** With any Pfaffian signing, each of these braces is not colourable and has the corner-independent
  amplitude shown:

  | Brace | Amplitude |
  |---|---|
  | Heawood graph | 5 |
  | doubled square | 1 |
  | planar brace P | ρ(P), Tutte's tree-trinity number |
  | trisum of three cubes along a common 4-cycle (the cycle's edges deleted) | 6 |

  If P is the omnitruncation (flag graph) of a planar map M, then ρ(P) = τ(M), the number of spanning trees of M.
- **Theorem 6 (the product formula).** Let H be a connected cubic system that is not 2-colourable, whose braces are Heawood graphs, doubled
  squares, planar braces and trisums of three cubes. Then for every line L,

  A(H, L) = 5^h · Π_P ρ(P) · 6^t,

  with h Heawood braces, P running over the planar braces, and t trisums.
- **Corollary 7.** On every gadget whose dual is such a space, the knot's exactness factor is

  λ(0) = (−1)^(n−1) · 5^h · Π_P ρ(P) · 6^t,

  whatever the corner line and the bases.
  - With planar glue, h is the genus (`THREEFOLD-SURFACES-20261030-001A`). So |λ(0)| = 5^genus · Π_P ρ(P), and |λ(0)| = 5^genus when the glue
    is doubled squares.
  - **Examples:**

    | Space | Points | λ(0) |
    |---|---|---|
    | the tripod core | 22 | −5³ |
    | the twisted cube (glue: the cube = Omni(digon), τ = 2) | 43 | +2·5⁶ |
    | hexagonal prism glue (Omni(triangle), τ = 3) | 45 | +3·5⁶ |
    | truncated octahedron glue (Omni(K₄), τ = 16) | 90 | −16·5¹² |
    | trisum glue | 35 | +6·5⁴ |

## Nearest known result

- **Tutte's tree-trinity theorem** (Tutte 1948): the three arborescence numbers of a trinity coincide.
  - Mathews (2017) presents the proof through Tutte matchings, which biject with the arborescences.
  - Kálmán (2013) identified the common number with the hypertree counts of the trinity's hypergraphs. For a graph (hyperedges of size two),
    hypertrees are spanning trees.
- **Berman (1980).** The 0/1 adjacency matrix between non-root vertices and non-outer white triangles has |det| = |M_T|: all Tutte matchings
  carry one sign. That is a determinant statement. The count here is a count of colourings of a signed system.
- **Search.** One literature search found no source counting the proper colourings of a Kasteleyn-signed planar triple system.
- **Folklore risk.** It is moderate for the pointer argument in Proposition 5, which is elementary.
- **What is new here** (no overlap found, candidate local delta):
  - that the knot's exactness factor counts Tutte matchings on planar glue;
  - the point lemma;
  - the factorization over tight cuts;
  - the brace amplitudes 5, 1 and 6.

## Proof of Lemma 1

- **(i) The cycles M Δ M′ span the cycle space.** Let G be matching covered and bipartite, with a bipartite ear decomposition
  K₂ + P₁ + … + P_r (Lovász–Plummer 4.1.6). Then r = |E| − |V| + 1 is the dimension of the cycle space.
  - **Building C_i.** For an ear P_i with ends u, w, take a perfect matching M₁ of G_i through P_i's first edge. The internal vertices of P_i
    force M₁ to contain the odd-numbered edges of P_i. A perfect matching M₀ of G_{i−1} differs from M₁ ∩ E(G_{i−1}) by alternating cycles
    and one u–w path Q.
  - **C_i is alternating.** The cycle C_i = P_i ∪ Q is M₁-alternating, so C_i = M₁ Δ M₂ for a perfect matching M₂ of G_i.
  - **Extending to G.** Both M₁ and M₂ extend to G by matching the internal vertices of the later ears along those ears.
  - **Independence.** C_i contains P_i's edges and C_j (j < i) does not, so C₁, …, C_r are independent and span the cycle space.
- **(i) The switching class.**
  - If σ and σ′ are Pfaffian, each gives M₁ and M₂ terms of one sign. So the product σσ′ is +1 on every C_i, hence on every cycle.
  - A ±1 edge function that is +1 on every cycle of a connected graph is a switching.
  - Two parallel edges with different signs would give two perfect matchings, differing only there, terms of opposite sign.
- **(ii)** Switching a point is the bijection x ↦ x ⊕ e_p between colourings, and leaves every seen value unchanged. Switching a line
  complements its three seen values, which preserves not-all-equal. ∎

## Proof of Theorem 2

- **The normalization of λ.** If the mixed sector sums vanish, Lemma 1 of `SPACE-SELECTION-20261030-001A` and Z(−−−) = −Z(+++) give

  R = (ζ − ζ⁻¹)^(−n) Z(+++) s_A (ζ^E − ζ^(−E)) = (ζ − ζ⁻¹)^(1−n) Z(+++) · w.

  Here w = s_A (ζ^E − ζ^(−E))/(ζ − ζ⁻¹) is the wave. So λ = Z(+++)/(ζ − ζ⁻¹)^(n−1).
  - Z(−−−) = −Z(+++) holds by the duality, since N\*(−−−) = N\*(+++) by flipping all phases.
- **The knot angle.** At ζ = e^(iπ/3), ζ − ζ⁻¹ = i√3, and the duality gives Z(+++) = (−i√3)^(n−1) N\*(+++). So
  λ(0) = (−1)^(n−1) N\*(+++).
- **N\* is the amplitude.**
  - A proper phase assignment of G\* is a 2-colouring of H − L₀, and corner phases +++ mean L₀'s points have colour +.
  - Since H is not 2-colourable, every colouring of H − L₀ makes L₀ constant, so the mixed sums vanish.
  - Half of these colourings make L₀ constant +, so N\*(+++) = A(H, L₀).
- **Nonzero.** H is connected and cubic, hence minimally not 2-colourable (`THREEFOLD-SPACES-20261030-001A`, Theorem 1(b)). So H − L₀ is
  colourable and A(H, L₀) > 0. ∎

## Proof of Lemma 3

- **No colourings when all three incidences see p's value.** A colouring counted by N(c ⊕ t), together with p = c, would colour H.
- **The bijection.** Fix c and i. The colourings counted by N(c ⊕ t ⊕ e_i) are exactly the colourings of H − ℓ_i with p = c.
  - **Forward.** In a colouring of H − ℓ_i with p = c, line ℓ_i (with p's true values) is not proper, or the colouring would colour H. So
    its three seen values are equal, and complementing the value at the i-th incidence makes it proper. Every other line sees p's true
    values and is proper.
  - **Backward.** A colouring counted by N(c ⊕ t ⊕ e_i) gives every line other than ℓ_i p's true values, and all of them are proper. So it
    is a colouring of H − ℓ_i with p = c.
  - **Repeated lines.** If ℓ_j = ℓ_i for some j ≠ i, its j-th incidence sees p's true value in both descriptions.
- **The count.** Flipping all colours shows that half of the colourings of H − ℓ_i have p = c, so N(c ⊕ t ⊕ e_i) = A(H, ℓ_i). ∎

## Proof of Theorem 4

**The pieces.** By the splice calculus, H is the point splice of H_X̄ into H_X along the cut, and matching signs factor. Carrying H's cut signs
s in the piece H_X̄ gives a τ with both pieces Pfaffian.

**Setting up the count.**
- A colouring of H − L is a colouring of X's points and of X̄'s points. X's lines see only X's points. X̄'s lines see X̄'s points and, at the
  cut incidences, ℓ_i sees v_i ⊕ s_i, where v = (x_{p₁}, x_{p₂}, x_{p₃}) are the port values. So

  #col(H − L) = Σ_v N_X(v) · N_X̄(v).

  - N_X(v) counts colourings of X with port values v that are proper on X's lines other than L.
  - N_X̄(v) counts colourings of X̄ proper on X̄'s lines other than L, when ℓ_i sees v_i ⊕ s_i at the i-th cut incidence.
- In H_X(τ) the line z sees v ⊕ τ. In H_X̄(τ) the point z = c makes the i-th cut incidence see c ⊕ τ_i ⊕ s_i.

**Case B = H_X(τ)** (z a line, L in X̄).
- B is not colourable, so N_X(v) = 0 unless v ⊕ τ is constant.
- For v = c ⊕ τ (v_i = c ⊕ τ_i), N_X(v) counts the colourings of B − z with z seeing c, which is A(B, z) = a(B).
- So #col(H − L) = a(B) Σ_c N_X̄(c ⊕ τ). Here N_X̄(c ⊕ τ) counts the colourings of H′ − L with z = c, since ℓ_i then sees c ⊕ τ_i ⊕ s_i.
- Hence #col(H − L) = a(B) · #col(H′ − L).

**Case B = H_X̄(τ)** (z a point, L in X).
- N_X̄(v) is the count of Lemma 3 for B at z, with pattern y = v ⊕ s. The point z = c shows c ⊕ τ ⊕ s.
- So N_X̄(v) = 0 when v ⊕ τ is constant. Otherwise N_X̄(v) = A(B, ℓ_i) = a(B), where i is the coordinate in which v ⊕ τ differs from the
  other two.
- So #col(H − L) = a(B) Σ N_X(v), summed over v with v ⊕ τ not constant. That sum is #col(H′ − L), since in H′ = H_X(τ) the line z sees
  v ⊕ τ.

**H′ is not colourable.** A colouring of H′ combines with a compatible colouring of B's shore into a colouring of H. Such a colouring exists
because a(B) > 0: in the first case it has port values c ⊕ τ; in the second it is counted by N_X̄(v) for the v in question.

**Halving** both sides gives the amplitudes. ∎

## Proof of Proposition 5

By Lemma 1 it suffices to treat one Pfaffian signing of each brace.

**The Heawood graph.**
- The trivial signing is Pfaffian, because the Fano plane is not 2-colourable (`THREEFOLD-SPACES-20261030-001A`, Theorem 1).
- Colour a line's three points c. The other four points form a quadrangle, so any two of them lie on a line with a point of the first.
- Hence at most one of the four has colour c, giving 1 + 4 = 5 at every line.

**The doubled square.**
- Its lines are ℓ = {p, q, q} and m = {p, p, q}. Let a, b, c, d mark the negated classes ℓp, ℓq, mp, mq.
- Line ℓ is proper iff x_p ⊕ x_q = 1 ⊕ a ⊕ b, and m iff x_p ⊕ x_q = 1 ⊕ c ⊕ d.
- With an odd number of negated classes, the Pfaffian case (`THREEFOLD-GRAMMAR-20261030-001A`, Theorem 2(ii)), these are incompatible.
- Deleting either line leaves two colourings, so the amplitude is 1.

**A planar brace P.**
- **Kasteleyn signings.** P is 3-connected, so every vertex lies on three distinct faces, and each face through it holds two of its three
  edges.
  - P has n points, n lines and, by Euler's formula, n + 2 faces.
  - Take a Kasteleyn signing σ: the face condition holds, with |σ ∩ ∂f| ≡ l_f − 1 for a face f of length 2l_f.
  - Switching preserves the face condition, so by Lemma 1 every Pfaffian signing is Kasteleyn.
- **Odd incidences.** A colouring of P − L gives each line w ≠ L exactly one *odd* incidence o(w), whose seen value differs from the other two.
- **Cycle parity.** Around a cycle γ of P − L, the seen values must close up.
  - At each line of γ, the two incidences on γ see different values iff one of them is odd.
  - Summing along γ gives |O ∩ γ| ≡ |σ ∩ γ| (mod 2), where O = {o(w)}.
  - Conversely, an O satisfying all these parities determines exactly two colourings, since P − L is connected.
  - So A(P, L) is the number of such O.
- **Reduction to faces.** The cycle space of the plane graph P − L is generated by the faces of P not at L. So the parities reduce to
  |O ∩ ∂f| ≡ l_f − 1 for those faces.
- **Pointers.**
  - Say w *points to* the face at w that does not contain o(w).
  - A face f has l_f lines on its boundary, so |O ∩ ∂f| = l_f − #{w pointing to f}. The condition says each face not at L receives an odd
    number of pointers.
- **Counting pointers.**
  - The n − 1 faces not at L need at least one pointer each, and the n − 1 lines other than L supply one pointer each.
  - So each such face receives exactly one, and no pointer goes to a face at L.
  - These pointer systems, read backwards, are the Tutte matchings with outer triangle L: each face not at L is sent to an adjacent line.
    Hence A(P, L) = |M_T(L)|.
- **Not colourable.** A colouring of all of P would need n pointers to reach all n + 2 faces an odd number of times each, which is
  impossible.
- **Identification.**
  - Mathews' proof of Tutte's theorem gives a bijection from the Tutte matchings with outer triangle L to the spanning arborescences of each of
    the trinity's three balanced digraphs, rooted at the vertices of L.
  - Arborescence numbers of balanced digraphs do not depend on the root. So |M_T(L)| = ρ(P) for every L.
- **Omnitruncations.** If P is the omnitruncation of a planar map M, T is the barycentric subdivision of M. The digraph on M's vertices has,
  for each edge uv of M, one arc u → v and one arc v → u. Its arborescences are the oriented spanning trees of M, so ρ(P) = τ(M).

**The trisum of three cubes.**
- One Pfaffian signing was found by search.
- With it the trisum is not colourable, and every line gives amplitude 6 (computed).

∎

## Proof of Theorem 6 and Corollary 7

- **Peeling.**
  - H's trivial signing is Pfaffian (`THREEFOLD-SPACES-20261030-001A`, Theorem 1).
  - Fix L and root a decomposition tree of B(H) at the brace containing L.
  - Peel a leaf B other than the root. Its cut is a tight cut of the current system, and by Theorem 4 B is one piece with a Pfaffian signing.
  - By Proposition 5 it is not colourable and has the corner-independent amplitude of its type. So Theorem 4 contributes a(B), and leaves a
    Pfaffian, non-colourable system H′ whose braces are the remaining ones.
- **The last brace** contributes A(B_L, L) = a(B_L). Multiplying gives the formula, which does not depend on L.
- **Corollary 7.**
  - Theorem 2 converts the formula into λ(0).
  - The bases do not enter N\*.
  - With planar glue, the genus formula gives h = genus. ∎

## What the computation checks

`check.py` (about four seconds):
- **the amplitude identity:** the law's corner relation by variable elimination on gadgets of eight spaces, two corner lines each;
- **the point lemma** at every point of five spaces and of five signed cores. Three of the cores have points held twice by a line.
- **the brace amplitudes:**
  - the Heawood graph at every line;
  - all 16 uniform signings of the doubled square;
  - seven planar braces at every line, where the amplitude, the Tutte matchings (a permanent) and the arborescence numbers of all three colour
    classes agree;
  - the trisum of three cubes at every line;
- **the factorization** on eleven spaces up to 90 points;
- **controls:**
  - the unsigned and the wrongly signed cube core are colourable;
  - plain not-all-equal gives +125 on the 22-triangle gadget, where the knot gives −125;
  - every line deletion of the Fano plane is colourable.

## Reading

- **The law's own number.** On its three-fold spaces the knot reproduces itself with factor 5 per handle, times Tutte's tree-trinity number
  of each planar glue piece. The sign is (−1)^(n−1), negative exactly when the number of triangles is even.
  - The handles are counted exactly.
  - The flat glue contributes a classical count of trees: for omnitruncation glue, the spanning trees of the underlying map; in general,
    Kálmán's hypertrees.
- **Corner independence.** The number does not depend on where the gadget's corners sit, or on how the bases are assigned. It is a property
  of the space.
- **What the number does not tell.** λ(0) alone does not determine the genus. A planar piece can contribute a power of 5 too: the 10-prism,
  the omnitruncation of a 5-cycle, contributes 5. The genus is visible in λ(0) only together with the decomposition, or when the glue is
  doubled squares.

## Nonclaims

- **Non-planar glue.** Only the trisum of three cubes is treated. General trisums are not; ticket B tests corner independence on the census.
- **External inputs.** Tutte's theorem, its matching form, and Kálmán's identification are used, not replayed. The computation confirms them
  on the stated examples.
- **Scope of λ(0).** It is treated only for three-fold odd gadgets with distinct corner triangles.
