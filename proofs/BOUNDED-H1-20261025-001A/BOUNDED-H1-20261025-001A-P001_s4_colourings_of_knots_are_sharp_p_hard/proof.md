# S4 colourings of knots are #P-hard

Status: Proved

## Standard statement

**Setting.**
- G = (V, E) is a connected plane multigraph with n vertices and m edges.
- **The diagram.** D(G) is the alternating link diagram whose Tait graph is G: its black regions are the vertices of G, and it has one
  crossing per edge.
- **Tripling.** G⁽³⁾ repeats every edge three times, side by side. So D(G⁽³⁾) has, for each edge uv, a twist of three crossings between
  the black regions of u and v.
- **Colourings.** Col(D) is the number of colourings of the arcs of D by the six transpositions of S₄ that satisfy the Wirtinger rule
  at every crossing (the outgoing under-arc is the conjugate of the incoming one by the over-arc). Equivalently, Col(D) is the number of
  homomorphisms from the link group to S₄ that send every meridian to a transposition.
- **Graph notation.** For a spanning subgraph H:
  - c(H) is its number of components, isolated vertices included;
  - B(H) is its bicycle space over F₂ (edge sets that are both cycles and cuts);
  - τ(H) is its number of spanning trees.

**Theorem 1 (bicycle law).**

  Col(D(G⁽³⁾)) = Σ_{φ: V → Z₃} 2^{c(H_φ) + dim B(H_φ)}, with H_φ = (V, {uv ∈ E : φ_u = φ_v}).

Equivalently:
- **Parity form.** Col(D(G⁽³⁾)) is the number of pairs (φ, x) ∈ Z₃^V × F₂^V such that every vertex v has an even number of edges vw
  with φ_w = φ_v and x_w ≠ x_v.
- **Twelve-state form.** Col(D(G⁽³⁾)) = 2^{−n} Σ_{z ∈ Z₁₂^V} Π_{uv ∈ E} M(z_u, z_v), where M = J − 2N and N is the permutation matrix
  of a fixed-point-free involution ν of Z₁₂.

**Theorem 2 (links).** Let G′ be G with every edge subdivided. Then

  Col(D(G′⁽³⁾)) = 2^{−n}·4^m·Z(G; 12, 1/2), with Z(G; q, v) = Σ_{A ⊆ E} q^{c(V, A)} v^{|A|}.

The link has 1 + β₁(G) components. Hence counting transposition colourings of link diagrams by S₄ is #P-hard, by a reduction that
makes one query.

**Theorem 3 (knots).** Counting homomorphisms from knot groups to S₄ that send meridians to transpositions is #P-hard under
polynomial-time Turing reductions. The knot is given by a diagram. Knot complements have H₁ = Z, so this is hardness with bounded first
homology, for a compact 3-manifold with torus boundary.

## Nearest known result

- **Kuperberg and Samperton**, *Coloring invariants of knots and links are often intractable* (AGT 2021).
  - For non-abelian simple G and a class C, counting homomorphisms from knot groups that send meridians into C is almost parsimoniously
    #P-complete.
  - Their braid-group "zombie" method needs a simple group. It does not cover solvable groups.
- **Affine (Alexander) quandles** are counted by linear algebra. Examples: Fox colourings, which are S₃ with transpositions, and A₄ with
  3-cycles.
- **Larose and Zádori.** General equation systems over a non-affine quandle are NP-complete. The knot-recognition paper (arXiv
  1505.06595) notes that knot systems are special and leaves them open.
- **Galindo (2026).** The full dichotomy when homology may grow. It says nothing about knots or bounded homology.
- **Rosenstiehl and Read (1978).** A connected plane graph has 1 + dim B left-right cycles (Godsil and Royle, *Algebraic Graph Theory*,
  §17.3). Cited, and checked on every subgraph used.
- **Vertigan (2005).** Planar Tutte and chromatic polynomials are #P-hard off a few curves and points. Cited.
- **What is new.**
  - The bicycle law.
  - The identity with Potts(12, 1/2).
  - The knot gadgets.
  - Hardness for S₄, the first solvable group for which knot or link colouring counts are shown #P-hard.
- **Novelty.** No overlap in the bounded scan (`research/BOUNDED-H1-20261025-001/scan.md`). Folklore risk low to medium.

## 1. Tripled twists

**Transpositions over S₃.**
- Every transposition of S₄ fixes one of the three pairings of {1, 2, 3, 4}, so it lies over one transposition of S₃ = S₄/V₄.
- The two transpositions over a given one commute, and they differ by an element of V₄.
- Label the S₃ transpositions by Z₃ so that conjugation reads a ▷ b = 2a − b.

A twist of two strands with k crossings acts on the colours at its top by the Hurwitz move σ: (x, y) ↦ (x ▷ y, x), applied k times.

**Lemma 1.1.**
- **(a)** σ³ fixes every pair of transpositions of S₃.
- **(b)** Take transpositions of S₄ over colours a and b, and write each one as its colour plus a bit.
  - If a = b, then σ³(x, y) = (y, x): the bits follow the strands, which cross.
  - If a ≠ b, then σ³ adds to each position's bit a constant that depends only on (a, b): the bits keep their positions.

*Proof.*
- **(a)** σ(a, b) = (2a − b, a), σ²(a, b) = (b, 2a − b) and σ³(a, b) = (3b − 2a, b) = (a, b) mod 3.
- **(b), equal colours.** Transpositions over the same colour commute, so σ(x, y) = (y, x).
- **(b), unequal colours.** Direct evaluation of σ³ on the 6 × 6 table of conjugates (check part 3). ∎

## 2. Colourings over S₃ are vertex potentials

**Lemma 2.1.** The S₃-transposition colourings of D(G⁽³⁾) correspond bijectively to φ: V → Z₃. The twist of edge uv is monochromatic
exactly when φ_u = φ_v.

*Proof.*
- **Every twist acts like a smoothing.** By Lemma 1.1(a) each twist transmits S₃ colours by position. So colourings correspond to
  colourings of the curves obtained by smoothing every twist so that its strands keep their positions.
- **The resulting curves.** That smoothing turns the diagram into n disjoint circles: one around each black region, passing the twists
  at u on u's side.
- **The colours.** Each circle takes a free colour φ_u. The twist of uv carries φ_u on the u side and φ_v on the v side, so its
  crossings are monochromatic iff φ_u = φ_v.
- **Check part 1.** The multiset of monochromatic-twist sets over all colourings equals the multiset of {uv : φ_u = φ_v} over all
  φ ∈ Z₃^V, on 19 graphs. ∎

## 3. The bicycle law

**Proof of Theorem 1.**
- **The fibre.** Fix φ. A lift to S₄ chooses, on each arc, one of the two transpositions over its colour (a bit), subject to the
  crossing rules.
- **Bits follow a smaller diagram.** By Lemma 1.1(b):
  - at a monochromatic twist (φ_u = φ_v) the bits follow the strands, which cross;
  - at a jump twist they keep their positions, up to constants. Keeping positions at the crossing of uv is the smoothing that deletes
    uv.

  So the bits are constant (up to fixed constants) along the left-right cycles of H_φ, with each isolated vertex contributing its
  circle. The internal arcs of each twist are determined by the boundary bits.
- **The fibre is an affine space.** The lifts form an empty set, or an affine space whose dimension is the number of these curves.
- **It is not empty.** S₃ = Stab(4) ⊂ S₄ is a complement of V₄, and its transpositions are transpositions of S₄. Composing the S₃
  colouring with this inclusion gives a lift.
- **Counting curves.** By Rosenstiehl and Read, each component C of H_φ with an edge has 1 + dim B(C) left-right cycles. So there are
  c(H_φ) + dim B(H_φ) curves.

**The parity form.** dim ker(L_H over F₂) = c(H) + dim B(H).
- **Why.** x ↦ δx maps ker L_H onto B(H): δx is a cut, and L_H x = ∂δx = 0 makes it a cycle. Every bicycle arises, and the kernel of
  this map is the locally constant functions.
- **As a count.** L_H x = 0 says exactly that each vertex has an even number of H-edges whose endpoints carry different bits.

**The twelve-state form.**
- **Fourier.** Write [even] = ½ Σ_{t_v ∈ F₂} (−1)^{t_v·(⋯)} at each vertex.
- **The interaction.** Each edge then contributes (−1)^{(t_u + t_v)·[φ_u = φ_v]·[x_u ≠ x_v]}.
- **As a matrix.** With z = (t, φ, x) ∈ Z₂ × Z₃ × Z₂ = Z₁₂, this is M(z, z′) = 1 − 2N(z, z′). Here N(z, z′) = [z′ = ν(z)] and
  ν(t, φ, x) = (1 − t, φ, 1 − x). ∎

## 4. Links

**Proof of Theorem 2.**
- **The middle vertices.** Summing the middle vertex of each subdivided edge, with its factor ½, gives ½M² = ½(J − 2N)². Using J² = 12J,
  JN = NJ = J and N² = I, this equals 4J + 2I = 4(J + ½I).
- **The Potts model.** Hence Col = 2^{−n}·4^m·Σ_z Π_e (1 + ½[z_u = z_v]) = 2^{−n}·4^m·Z(G; 12, 1/2).
- **Components.**
  - A bicycle of G′ is a cycle that is also a cut. Every such cycle uses both halves of each subdivided edge on it, so it comes from a
    cycle of G.
  - The cut condition then forces all original vertices onto one side, with the middle vertices of the cycle's edges on the other.
  - So B(G′) is exactly the cycle space of G, of dimension β₁(G), and there are 1 + β₁(G) components.
- **Hardness.**
  - Z(G; 12, 1/2) = 12^{c} (1/2)^{n−c} T(G; 25, 3/2).
  - Planar Tutte evaluation at (25, 3/2) is #P-hard: (x−1)(y−1) = 12 is not 1 or 2, and the point is not exceptional (Vertigan).
  - One query on a diagram with 6m crossings. ∎

## 5. Gadgets

**The algebra.**
- **Gadgets.** Two-terminal series-parallel networks Γ with every edge tripled.
- **The interaction.** Summing the internal vertices of Γ gives (½)^{#internal}·M_Γ, with:
  - M_e = M = J − 2N for a single edge;
  - series composition as the matrix product, and parallel composition as the entrywise product.
- **The algebra closes.** span{J, I, N} is closed under both products: J∘X = X, I∘I = I, N∘N = N and I∘N = 0 (check part 4, all gadgets
  up to 4 edges).
- **Hadamard coordinates.** Write M_Γ = α(J + bI + gN) = α((1+b)I + (1+g)N + R), with R = J − I − N. The parts I, N and R are disjoint
  0/1 matrices, so parallel composition multiplies the Hadamard coordinates (1 + b, 1 + g) and α.

**Lemma 5.1.** τ(G[Γ]) = τ(G)·t_Γ^{n−1}·f_Γ^{m−n+1}.
- **Notation.** t_Γ counts the spanning trees of Γ, and f_Γ the spanning 2-forests that separate the terminals.
- **Proof.** A spanning tree of G[Γ] meets each copy of Γ in a tree or a separating 2-forest, and the copies meeting it in trees form a
  spanning tree of G.

**Lemma 5.2.** D(K⁽³⁾) is a knot iff τ(K) is odd, for a connected plane multigraph K.
- **Components.** An odd twist connects strands like one crossing, so D(K⁽³⁾) and D(K) have the same components.
- **Counting them.** Their number is 1 + dim B(K), and dim B(K) is the F₂-nullity of the reduced Laplacian. That Laplacian's determinant
  is τ(K).

**The consequence.** If t_Γ, f_Γ and τ(G) are all odd, then D(G[Γ]⁽³⁾) is a knot (check part 4: six gadget classes with odd t and f
keep three hosts knotted; the other 21 classes do not).

**The gadget used.** Γ₁ = S(e, P(e, S(e, e))) has M_{Γ₁} = 68J + 32I − 8N.
- **Its data.** Hadamard coordinates (25/17, 15/17); t = 3 and f = 5.
- **Its parallel powers.** The k-fold parallel power has t_k = 3k·5^{k−1} and f_k = 5^k, odd for odd k, and coordinates
  ((25/17)^k, (15/17)^k).

## 6. Knots

**Proof of Theorem 3.** Let H be a connected planar graph. Computing P(H, 12) is #P-hard (Vertigan; q = 12 ∉ {0, 1, 2}).

1. **Make the tree count odd.**
   - Choose a spanning tree T₀ and double every edge outside it, giving H̃, which is still planar.
   - P(H̃, q) = P(H, q), since parallel edges do not change proper colourings.
   - τ(H̃) = Σ_T 2^{|T \ T₀|}. Only T₀ gives an odd term, so τ(H̃) is odd.
2. **Build the knots.** For odd k = 1, 3, …, 2K − 1, with K = (m̃ + 1)(m̃ + 2)/2 and m̃ = |E(H̃)|, form K_k = D((H̃[Γ₁^{∥k}])⁽³⁾). It is
   a knot by Lemma 5.2, and has 12·k·m̃ crossings.
3. **The counts.** By Theorem 1 and Section 5, Col(K_k) = 2^{−N_k}·68^{k·m̃}·Σ_{i,j} N_{ij} β_{ij}^k. Here:
   - N_k = n + 2k·m̃;
   - β_{ij} = (25/17)^i (15/17)^j;
   - N_{ij} counts z ∈ Z₁₂^V with i edges having z_u = z_v and j edges having z_v = ν(z_u).

   The β_{ij} are pairwise distinct: β_{ij} = 5^{2i+j} 3^j 17^{−i−j}. So the K values determine every N_{ij}, by a Vandermonde system in
   β_{ij}² after factoring out β_{ij}.
4. **Read off the answer.** P(H, 12) = Σ_j N_{0j}: the 12-colourings with no equal edge are the proper ones, whatever the N-related
   edges.

**Sizes.** The diagrams have O(m³) crossings, so the reduction runs in polynomial time. ∎

## Check

`check.py` uses the standard library only and runs in about 36 s. Its output is `result.json`.

1. **The bicycle law.**
   - On every colouring of 19 graphs: 11 named (including the 4-cycle with two pendants) and 8 random grid subgraphs with up to 9
     vertices and 13 edges. That is up to 19,683 colourings per graph.
   - The S₃ colourings are in bijection with potentials.
   - The lift dimension equals the F₂-Laplacian nullity of H_φ.
   - The left-right cycles of every tested H_φ number c + dim B.
2. **The counts.**
   - Parity form = twelve-state form = Col, on nine graphs.
   - For subdivided graphs, Col = 2^{−n} 4^m Z(G; 12, 1/2). Examples: C₄ gives 390,636; K₄ gives 6,801,840.
   - The link has 1 + β₁ components.
3. **The local lemma**, from the permutation table.
4. **Gadgets.**
   - The algebra matches the summed interactions for all gadgets up to 4 edges.
   - Lemma 5.1 holds on every substitution.
   - Knots are kept exactly by the gadgets with odd t and f.
5. **End-to-end knot counts.** Single edge, path and C₃ with Γ₁, and single edge with a 6-edge gadget. Every diagram is a knot, and the
   counts match 2^{−N} α^m P_G(b, g). C₃ with Γ₁ gives 1,158,510.
6. **The interpolation.** For K₄, C₅ and the diamond:
   - the doubled graphs have 49, 9 and 19 spanning trees;
   - the bases are distinct;
   - the Vandermonde solve recovers P(H, 12) (11,880, 161,040 and 13,200) from the counts predicted by Theorem 1;
   - the diagrams for k = 1 and k = 3 are knots.

   The large diagrams are not colour-counted directly; their counts come from Theorem 1, which parts 1, 2 and 5 test.
7. **Controls.**
   - The law without the bicycle term fails on the 4-cycle with two pendants.
   - Six-crossing twists decouple: Col = 3ⁿ·2^{components}.
   - Wrong Potts parameters are rejected.
   - An even parallel power of Γ₁ gives a link.

## Scope

- **Covered.** Link and knot diagrams built as alternating diagrams of plane graphs with tripled edges, and the transposition meridian
  condition.
- **Not covered.**
  - The unrestricted count |Hom(π₁(S³ \ K), S₄)|, which adds the meridian classes of 3-cycles, 4-cycles and double transpositions.
  - Closed manifolds with bounded first homology. Dehn surgery or gluing turns these knot counts into closed counts, but needs the
    longitude values and the 4-cycle colourings controlled. That is the next step.
- **Kind of reduction.** Turing reductions; a single query for links.
- **Cited, not proved.** Rosenstiehl–Read (verified on all tested subgraphs) and Vertigan.
- **No overclaim.** No claim about P versus NP, approximation or physics.
