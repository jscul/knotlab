# Fano leaves and planar glue

Status: Proved

Ticket `THREEFOLD-GRAMMAR-20261030-001A`, 2026-10-30.

**What it uses:**
- `THREEFOLD-SPACES-20261030-001A`:
  - the dictionary: for a connected 3-regular triple system, not 2-colourable ⟺ the incidence matrix is sign-nonsingular (SNS) ⟺
    the trivial signing of the incidence graph is Pfaffian;
  - the splice calculus. Perfect-matching signs factorize across 3-edge tight cuts. With signed matrices, both pieces carry one common
    pattern on the three cut edges, which up to switching negates no edge or one edge;
  - the library.
- `THREEFOLD-SPACES-20261030-001C`: Fano blocks, and the twisted 14-point system T14.
- `SPACE-SELECTION-20261030-001C`, Theorem 2 (the duality). A gadget whose contacts each join three triangles with odd base count, with
  distinct corner triangles, is exact at the knot iff two conditions hold for its dual triple system H:
  - H is not 2-colourable;
  - H minus the corner line is 2-colourable.
- Classical results, not replayed:
  - Lovász: the tight-cut decomposition of a matching-covered graph, and the uniqueness of its list of braces.
  - The characterization of tight cuts in bipartite graphs.
  - Plummer: braces on at least six vertices are 3-connected.
  - Pfaffian signings pass to tight-cut contractions.
  - Kasteleyn's face-parity signings of planar bipartite graphs.
  - Robertson, Seymour and Thomas (Annals 1999), Theorem 6.8 and its proof, quoted below.

## Why this ticket exists

The approved recommendation was to prove that every three-fold space is assembled from Fano blocks by splices and odd cycles. Scoping
before activation found the twisted cube (Theorem 1), so that grammar is incomplete. Under the owner's rule this ticket adopts the more
interesting reading: the glue is any planar connector obeying Kasteleyn's parity, and the question is whether the Fano plane is the only
leaf.

The answer is yes (Theorem 5). The case left open at activation was leaves built by repeated sums. It was closed by the trisum form of
the Robertson–Seymour–Thomas theorem together with a 4-cycle induction (Lemma 3).

## Standard statement

**Setting.**
- **Systems.** H is a connected 3-regular triple system with distinct points per line that is not 2-colourable. B(H) is its incidence
  graph. A *multi-system* allows repeated points in a line, and its incidence graph has parallel edges.
- **Decomposition.**
  - Tight cuts and braces are as in ticket A of the previous epic.
  - Contracting a shore gives a *contracted vertex*.
  - A *leaf* of a tight-cut decomposition is a brace with exactly one contracted vertex.
- **Fano pieces.** A *Fano piece* is a Fano plane minus one element, attached through the three incidences it loses. Its brace is the
  Heawood graph. There are two kinds:
  - a *Fano block* is Fano minus a line, attached at that line's three points. It forces its ports equal and acts as a point;
  - a *dual block* is Fano minus a point, attached at the three lines through it. Its three outside points are not all equal, so it
    acts as a line.

  Which kind a given leaf has can depend on the decomposition chosen.
- **Other pieces.**
  - The *doubled square* is the 4-vertex cubic multigraph made of a 4-cycle with two opposite edges doubled.
  - The *twisted cube* is the cube K₄⁽³⁾ (four points, the four triples) with three negated incidences that lie on disjoint pairs of
    faces. Each negated incidence's point is replaced by a copy of T14, with T14's twisted port on that incidence. It has 43 points.
- **Trisums** (Robertson, Seymour and Thomas).
  - Let G₁, G₂, G₃ be graphs whose pairwise intersections are one 4-cycle C, each with a vertex outside C.
  - A *trisum* is G₁ ∪ G₂ ∪ G₃ with some (possibly none) of the edges of C deleted.

**Results.**
- **Theorem 1 (the approved grammar is incomplete).** The twisted cube is a linear connected 3-regular triple system that is minimally not
  2-colourable. Its braces are six Heawood graphs, three doubled squares and the cube.
  - Every system built from Fano planes by splices and by cycles of Fano blocks, plain or twisted and spliced, has only Heawood graphs and
    doubled squares as braces.
  - By the uniqueness of the brace list, the twisted cube is not such a system.
- **Theorem 2 (structure).** In every tight-cut decomposition of B(H):
  - (i) every piece is a cubic bipartite multigraph;
  - (ii) a brace with a parallel pair has four vertices and is the doubled square. It is SNS exactly when an odd number of its four
    parallel classes is negated; a class with mixed signs never is;
  - (iii) every parallel pair of a piece has a contracted endpoint. So doubled squares have at least two contracted vertices, and every
    leaf is a simple cubic brace on at least six vertices whose induced signing is trivial except possibly one negated edge at its
    contracted vertex (up to switching);
  - (iv) every brace carries an induced Pfaffian signing.
- **Lemma 3 (4-cycles of Pfaffian braces).** Let G be a Pfaffian brace on at least six vertices, other than the Heawood graph.
  - (i) For every 4-cycle C of G, G has a 4-cycle edge-disjoint from C.
  - (ii) If G is planar it has at least six 4-faces. Otherwise it has three pairwise edge-disjoint 4-cycles.
  - In particular, G has two edge-disjoint 4-cycles.
- **Theorem 4 (one-twist lemma).** Let G be a simple brace on at least six vertices with a Pfaffian signing that negates at most one
  edge. Then G is the Heawood graph and the signing negates no edge.
- **Theorem 5 (Fano leaves).** Every leaf of every tight-cut decomposition of B(H) is a Fano piece with its trivial signing.
  - So every non-2-colourable connected 3-regular triple system other than the Fano plane contains at least two vertex-disjoint Fano
    pieces, each attached by a 3-edge tight cut.
- **Theorem 6 (decoration: every planar cubic graph is glue).** Let P be a connected cubic multi-system with an SNS signing S. Up to
  switching, S negates no repeated incidence. Replace every point that carries a negated or repeated incidence:
  - by T14 if one or two of its incidences are negated, with T14's twisted port on the incidence whose sign differs from the other two;
  - by a Fano block if none or all three are.

  The result is a connected 3-regular triple system with distinct points per line that is not 2-colourable.
  - Every planar cubic bipartite graph has such a signing (Kasteleyn). So every planar cubic bipartite graph is the core of three-fold
    knot spaces.
  - Examples: the cube (43 points), the hexagonal prism (45), the truncated octahedron (90), the 3-cycle core (21) and the tripod core
    (22, a point unequal to three blocks that form a not-all-equal triple).

## Nearest known result

- **Pfaffian graphs.** The structure theory of Pfaffian bipartite graphs is classical: tight cuts (Lovász), Pfaffian contractions,
  Robertson–Seymour–Thomas, Kasteleyn. Theorems 2 and 6 are its specializations to cubic graphs and to the trivial signing.
- **Lemma 3.** Gorsky, Johanni and Wiederrecht (arXiv 2408.08128, Lemma 3.4) state Lemma 3 for non-planar Pfaffian braces other than the
  Heawood graph, and their Theorem 1.7 states that all Pfaffian braces other than the Heawood graph have girth 4. Their proof was not
  read. The proof below was written from the RST trisum structure alone.
- **Classification.**
  - Theorem 4, Theorem 5 and Theorem 6 in this form: no overlap found (candidate local delta).
  - Folklore risk is moderate, since all of it follows quickly from RST.
  - The reading as the knot's three-fold spaces is new here.

## Proof of Theorem 1

- **The twisted cube.**
  - The cube's three negated edges lie on disjoint pairs of faces, so every face (a 4-cycle) has exactly one negation. That is
    Kasteleyn's parity, so the signed cube is SNS (checked).
  - Each copy of T14 is SNS with its twist on the cut edge that carries the negation. By the signed splice calculus the decorated system is
    SNS untwisted, hence not 2-colourable. It is minimal because it is connected (previous epic, Theorem 1).
  - The decomposition is computed: six Heawood leaves, three doubled squares (one per T14 core), and the cube.
- **The approved class.**
  - A Fano splice glues two Heawood braces along their tight cut.
  - A cycle of k Fano blocks contracts, block by block, to the doubled 2k-gon. Its tight cuts peel off doubled squares: the shore made of
    one doubled point and its two lines is tight (Theorem 2(ii)).
  - Twisted cycles and splices of them combine these pieces.
  - By induction every system of the class has only Heawood graphs and doubled squares as braces. The check confirms this on six
    generated systems.
- **Uniqueness** of the brace list (Lovász) finishes the argument. ∎

## Proof of Theorem 2

- **(i)** In a bipartite matching-covered graph, a nontrivial tight cut has a shore with one more vertex on one side, and the minority side
  of the shore has all its neighbours inside. Counting the degrees of the majority side gives exactly three cut edges, and both
  contractions are cubic.
- **(ii) Parallel pairs.**
  - Let u (a point) and v (a line) be joined by two parallel edges, and let x be u's third neighbour. The shore {u, v, x} has two lines and
    one point, and the point's neighbours lie inside it, so it is tight. It is nontrivial whenever the graph has at least six vertices. So a
    brace with a parallel pair has at most four vertices.
  - A triple edge forms a 2-vertex component.
  - The only connected 4-vertex cubic bipartite multigraph is the doubled square: the multiplicities m(p, ℓ) = m(q, m) = a and
    m(p, m) = m(q, ℓ) = 3 − a are forced, with a ∈ {1, 2}.
  - Two parallel edges of different signs give two perfect matchings of opposite sign, so a Pfaffian signing is constant on each class.
    The four classes lie on one nice 4-cycle, which needs an odd number of negations. The check enumerates all 16 uniform patterns.
- **(iii) Contracted endpoints.**
  - Two parallel edges between u and v in a piece come from two edges of B(H) that leave a contracted shore towards the same vertex,
    because B(H) is simple. So one endpoint is contracted.
  - The doubled square has two vertex-disjoint parallel classes, so it has two contracted vertices.
  - A leaf has one contracted vertex. It is therefore not a doubled square, so by (ii) it is simple, and it has at least six vertices.
  - A leaf is G/Ȳ for a tight cut ∂(Y), and its edges inside Y keep their (trivial) signs. The three cut edges carry the common pattern,
    which up to switching at the contracted vertex negates no edge or one edge.
- **(iv)** The trivial signing of B(H) is Pfaffian. Applying the signed factorization along the decomposition gives each brace a Pfaffian
  signing. ∎

## Proof of Lemma 3

- **Two facts from Robertson, Seymour and Thomas** (Theorem 6.8 and its proof, using their 5.9 and 6.5(iii)):
  - every Pfaffian brace is the Heawood graph, planar, or a trisum of three smaller braces G₁, G₂, G₃ along a 4-cycle C;
  - each Gᵢ is contained in G, so it has no K₃,₃ and is again a Pfaffian brace.

  The proof is by induction on the number of vertices. The pieces Gᵢ contain C, so none is the Heawood graph, which has girth 6.
- **Planar braces.** They are 3-connected (Plummer), so faces are cycles, each edge lies on two faces, and two faces share at most one
  edge. Faces have even length, and every degree is at least 3.
  - **Counting.** Euler's formula gives Σ_f (6 − |f|) = 12 + 2Σ_v (deg v − 3) ≥ 12. So there are at least six 4-faces.
  - **C is a face.** The faces sharing an edge with C are C and at most four others. So some 4-face is edge-disjoint from C.
  - **C is not a face.** Then C is separating, and the inside of C contains vertices.
    - The inside attaches to at least three vertices of C (3-connectivity). Let z ≤ 1 count the vertices of C with no inside edge, and let
      p count the inside edges beyond the first at each vertex of C.
    - Euler's formula for C together with its inside gives Σ (6 − |f|) = 10 − 2z + 2p over the inside faces. So there are at least
      5 − z + p inside 4-faces.
    - At most 4 − z inside faces contain an edge of C: when a vertex has no inside edge, its two C-edges share an inside face.
    - So at least 1 + p inside 4-faces avoid C.
- **Trisums.** Let G be a trisum of G₁, G₂, G₃ along C, and let D be any 4-cycle of G.
  - Every edge of G not on C lies in exactly one part Eᵢ = E(Gᵢ) − E(C). Each such edge has an end outside C, because G is bipartite and
    simple, so C has no chords.
  - **D meets two parts.** If D has edges in two parts i and j, it contains a vertex xᵢ inside Gᵢ and a vertex xⱼ inside Gⱼ. They are not
    adjacent, so they are opposite on D, and the other two vertices are common neighbours, which lie on C. So D = xᵢ a xⱼ b has no edge in
    the third part k.
  - **D meets one part.** Otherwise D lies in some E(Gᵢ), and then it misses both other parts.
  - **The partner.** In either case D misses some part k. By induction, Gₖ has a 4-cycle Qₖ edge-disjoint from C. Then Qₖ ⊆ Eₖ, it
    survives the deletion, and it is edge-disjoint from D.
- **(ii).** The planar case is the counting above. For a non-planar trisum, the three cycles Q₁, Q₂, Q₃ chosen against C lie in the three
  disjoint parts, so they are pairwise edge-disjoint. ∎

## Proof of Theorem 4

- **Nice 4-cycles.** In a brace every 4-cycle is nice: its two opposite edges extend to a perfect matching (2-extendability).
- **Parity.** A Pfaffian signing gives a nice cycle of length 2l exactly l − 1 negated edges mod 2. So every 4-cycle carries an odd number
  of negated edges.
- **Not the Heawood graph.** A Pfaffian brace other than the Heawood graph has two edge-disjoint 4-cycles (Lemma 3). One negated edge
  cannot lie on both, and zero negated edges lie on neither, so no such signing is Pfaffian.
- **The Heawood graph.**
  - Its trivial signing is Pfaffian (the Fano plane is not 2-colourable).
  - None of its 21 single negations is (computed). Indeed, Pfaffian signings of a matching-covered bipartite graph are unique up to
    switching, and the search finds exactly one class. ∎

## Proof of Theorem 5

- **A leaf.** By Theorem 2(iii)–(iv), a leaf is a simple brace on at least six vertices with a Pfaffian signing that negates at most one
  edge after switching.
- **Heawood and untwisted.** By Theorem 4 the leaf is the Heawood graph with no negated edge.
- **The two kinds.**
  - If its contracted vertex is a line, the leaf's original vertices are seven points and six lines: a Fano plane minus a line, attached
    at that line's points.
  - If the contracted vertex is a point, they are six points and seven lines: a dual block.
- **At least two pieces.**
  - If the decomposition is trivial, B(H) is a brace with Pfaffian trivial signing, so by Theorem 4 it is the Heawood graph and H is the
    Fano plane.
  - Otherwise the decomposition tree has at least two leaves. Distinct braces own disjoint sets of original vertices. ∎

## Proof of Theorem 6

- **The cuts.** Every decoration is attached by a 3-edge tight cut (ticket A of the previous epic, Theorem 2(i)).
- **Repeated incidences.** The doubled classes of a cubic multigraph form a matching. Switching at one end of each negated doubled class
  makes S negate no repeated incidence.
- **Switching at decorated points.** At a decorated point with k negated incidences, switching at that point (if k ≥ 2) leaves 0 or 1.
  Switching preserves Pfaffian signings, so the core P stays SNS.
- **The pieces.** The attached pieces are SNS with the matching pattern:
  - a Fano block untwisted;
  - T14 twisted, on the odd incidence (THREEFOLD-SPACES C, Theorem 2).
- **The conclusion.** By the signed splice calculus the decorated system is SNS untwisted, hence not 2-colourable.
  - Lines get distinct points, because repeated incidences receive distinct ports.
  - Connectedness is preserved.
- **Every planar cubic bipartite graph.** It has a Kasteleyn signing: each bounded face of length 2l carries l − 1 negations mod 2, and
  such a signing is Pfaffian. The check computes one by GF(2) elimination on a planar embedding for three examples. It verifies SNS of the
  signed cores and non-colourability of all five decorations by SAT, and minimality of the four smaller ones.
- **Knot spaces.** Minimality gives the duality's conditions, so these are three-fold knot spaces. ∎

## What the computation checks

`check.py` (about two seconds):
- the brace lists of the twisted cube and of six generated systems;
- the structure facts on all computed decompositions;
- the doubled-square signings;
- **Theorem 4 and Lemma 3:**
  - the Heawood graph: 21 single negations, and its Pfaffian classes;
  - three planar braces;
  - two non-planar cubic trisums: three cubes on a common 4-cycle with that cycle deleted (16 vertices), and that graph summed with two
    more cubes along one of its 4-cycles (24 vertices).

  For each brace the check confirms that it is a brace, that it has exactly one Pfaffian class, the partner property, the number of
  disjoint 4-cycles, and that no signing negating at most one edge is SNS;
- the Fano pieces of seven systems. The Fano splice has one block and one dual block; in the computed decomposition of the 5-cycle of
  blocks, one leaf is a dual block;
- the five decorations;
- **controls:**
  - a non-Kasteleyn signing decorates to a 2-colourable system;
  - the untwisted 2-cycle is 2-colourable;
  - the trivial signing of a planar graph is not SNS;
  - the Fano plane is one brace;
  - K₃,₃ has no Pfaffian signing.

## Reading

- **The knot's own space is made of Fano atoms and planar glue.**
  - Every leaf is a Fano plane with one element removed.
  - Every other brace is a doubled square, a planar brace, or a trisum of smaller ones, ultimately of planar braces.
  - Original incidences carry no sign, so the twists that the glue's Pfaffian signing needs sit on the attachments: every 4-cycle of a
    glue brace passes through an attached piece whose cut pattern is twisted. It works like a flux through each face, and Kasteleyn's
    parity says how much.
  - Odd cycles of Fano blocks are the simplest glue. Every planar cubic bipartite graph can serve.
- **Planarity is forced, not drawn.** Apart from the Heawood graph, the only Pfaffian braces are planar or are glued from planar ones by
  trisums. So everything in a three-fold knot space beyond its Fano atoms is assembled from planar pieces.
  - This is a combinatorial planarity of incidence graphs, not a metric dimension.
  - The two-dimensional structure is imposed by the knot's law through the sign parity, not by a chosen drawing.

## Nonclaims

- **External inputs.** RST's Theorem 6.8 and its proof are used as an external result (the quoted structure: a trisum of three smaller
  Pfaffian braces), and so are Kasteleyn's signings. Neither is replayed.
- **The examples.** The computation checks examples, not the induction.
- **No classification** of which glue braces occur is claimed beyond Theorems 2 and 6.
