# Counting on plain Pfaffian braces is #P-hard

Status: Proved

Ticket `PLAIN-BRACE-20261031-001B`, 2026-10-31.

**What it uses:**
- **`PLAIN-BRACE-20261031-001A`:**
  - Lemma 1: a site acts by (NW)^k;
  - Theorem 4: single-site and multi-site recovery;
  - Lemma 3: the lattice condition.
- **`SOFT-CROSS-20261031-001B`, Theorem 3:** counting the colourings of plain cubic bipartite systems is #P-complete. The instances are
  connected for connected formulas. This is also Fan and Cai, 2020.
- **The Pfaffian certificate:** the argument of `SOFT-CROSS-20261031-001A`, Theorem 5, with `SEYMOUR-COUNT-20261030-001A`, Lemma 1(iii) and
  `THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4.
- **`PLAIN-COUNT-20261031-001B`, Lemma 4:** a plain non-colourable system has no nice 4-cycle.
- **External, not replayed:**
  - Hall-type characterization of braces (Lovász and Plummer): a connected bipartite graph with sides of size n ≥ 3 is a brace iff
    |N(X)| ≥ |X| + 2 for every X on one side with 1 ≤ |X| ≤ n − 2;
  - Tutte's barycentric embedding of 3-connected planar graphs, which has convex faces;
  - plane duality: a bond of a connected plane graph is crossed exactly by a simple closed curve through its faces;
  - Valiant's planar algorithm and the Robertson–Seymour–Thomas structure of Pfaffian braces, for Corollary 8.

## Why this ticket exists

Ticket A built an exact crossing inside braces from plain cubes. To prove hardness, a hard source must be drawn with all its crossings
replaced, so that every instance is still a brace. Hard sources have small cuts of their own: `SOFT-CROSS-20261031-001B`'s graphs have 2-edge
cuts at every cap. Weaving the source into a planar frame removes them.

## Standard statement

**Setting.**
- **A frame** F is a planar cubic bipartite graph that is *cyclically 4-edge-connected*: every edge cut whose two sides both contain cycles
  has at least four edges. Example: the prism C₂ₙ × K₂, n ≥ 2.
- **A woven drawing** of a connected cubic bipartite source G:
  - F is drawn without crossings, and the vertices of G lie in the interiors of distinct faces of F;
  - all edges are in general position: no edge passes through a vertex, crossings are transversal, no three edges share a point, and edges
    with a common end do not cross.
- **The planarization** P has every crossing as a vertex of degree 4.
- **The woven host** H replaces every crossing by a site of ticket A (square edges present).
- **The woven instance** T glues every junction square by trisum to two plain cubes.

**Results.**
- **Lemma 1 (Hall).** A connected cubic bipartite graph on at least six vertices that is cyclically 4-edge-connected is a brace.
- **Lemma 2 (sites are ladders).** A site with k junctions is the ladder P₃ₖ × K₂, with its ports at the four corners. Every vertex set that
  contains a cycle has at least four boundary edges, ports counted.
- **Lemma 3 (bonds of the planarization).** Every bond of P with at most three edges has one side consisting of a single vertex of degree 3.
- **Lemma 4 (weaving).** The woven host H is cyclically 4-edge-connected.
- **Lemma 5 (the cube junction).** Let H be cubic and cyclically 4-edge-connected, and C a 4-cycle of H. Delete C's edges and glue two cubes
  on C (each cube's opposite square joined to C by a perfect matching). The result is again cyclically 4-edge-connected.
- **Lemma 6.** Every woven instance T is a plain Pfaffian brace.
- **Theorem 7.** Counting the proper 2-colourings of 3-regular 3-uniform hypergraphs whose incidence graphs are Pfaffian braces is #P-hard
  under polynomial-time Turing reductions.
  - The hard instances are prism frames with plain cube junctions.
  - With every site restored, the count is #col(G)·#col(F).
- **Corollary 8 (plain Pfaffian braces).**
  - The planar ones count in polynomial time (Valiant).
  - The Heawood graph is a single graph.
  - The class is #P-hard (Theorem 7).
  - The Fano plane is the only plain brace without twists (`PLAIN-COUNT-20261031-001B`).

## Nearest known result

- **Known:**
  - hardness of the problem on general graphs (Fan and Cai, 2020), and its planar tractability;
  - the structure of Pfaffian braces (Robertson, Seymour and Thomas; McCuaig);
  - keeping gadgets well connected is a common concern in hardness proofs for restricted graph classes.
- **No overlap found** (candidate local delta, folklore risk moderate):
  - hardness on plain Pfaffian braces;
  - the weaving lemma;
  - the cube junction lemma.

## Proof of Lemma 1

- Let X be on one side, 2 ≤ |X| ≤ n − 2. The case |X| = 1 gives |N(X)| = 3.
- **Suppose |N(X)| ≤ |X| + 1.**
  - N(X) receives all 3|X| edges of X and sends 3|N(X)| − 3|X| ≤ 3 edges to the rest of its side.
  - |N(X)| = |X| would disconnect the graph, so |N(X)| = |X| + 1 and the cut around X ∪ N(X) has three edges.
- **Both sides contain cycles.**
  - X ∪ N(X) has 2|X| + 1 vertices and 3|X| edges, more than its vertices.
  - The other side has 2n − 2|X| − 1 vertices and 3(n − |X|) − 3 edges, at least as many.
  - Each side therefore contains a cycle, which is a cyclic 3-edge cut, a contradiction.
- So |N(X)| ≥ |X| + 2, and the graph is a brace. ∎

## Proof of Lemma 2

**The ladder.**
- The rungs in order are:
  - (l_s, π_s);
  - for every junction j, (c0(j), c1(j)) and (c3(j), c2(j)) (square edges);
  - between consecutive junctions, (π_j, λ_j).
- That is 3k rungs, and consecutive rungs are joined along the two rails (the site's edges of ticket A).

**Ports and cycles.** The ports sit at the four corners. The cycles of a ladder are the boundaries of runs of consecutive rungs.

**Four boundary edges.** If Y contains such a cycle, then on each rail the maximal run of Y-vertices containing it has two ends. At each end
the next rail edge, or the corner's port, leaves Y. These four edges are distinct.

**Check.** Section 2 verifies the ladder isomorphism and the bound exhaustively for k ≤ 3. ∎

## Proof of Lemma 3

**The curve.** Let ∂X be a bond of P with at most three edges, and γ a simple closed curve crossing exactly these edges, once each, with X
inside (on the sphere).

**At most one frame vertex inside.**
- Let U be the set of frame vertices inside γ. A frame edge with one end in U crosses γ an odd number of times, so ∂_F U has at most three
  edges.
- F is cyclically 4-edge-connected and cubic. So one of U and its complement induces a forest, and a forest with t vertices and c components
  has t + 2c ≥ t + 2 boundary edges. Hence that side has at most one vertex.
- Exchanging inside and outside if needed, U has at most one vertex.

**Case U = {u}.**
- u's three frame edges use all of γ's crossings, so no edge of G crosses γ.
- The inside of γ meets only the three faces at u, which hold at most three vertices of G. G is connected with at least six vertices, so G
  lies outside.
- No crossing lies on u's edges inside γ, because a G-edge would have to enter. So X = {u}.

**Case U = ∅, a frame edge passing through.** It crosses γ twice, leaving at most one crossing.
- The inside lies in the two faces beside that edge, and holds at most two vertices of G.
- A vertex of G inside would send at least two edges out: its neighbours lie in other faces, and at most one of them is the other inside
  vertex. That is impossible.
- Any G-piece inside would cross γ twice. So X would be empty, a contradiction.

**Case U = ∅, no frame edge passing through.**
- The inside lies in one face, with at most one vertex v of G.
- If v is inside, its three edges use the three crossings, and X = {v}.
- Otherwise every G-piece inside crosses γ twice and a crossing vertex needs four crossings, so X is empty, a contradiction. ∎

## Proof of Lemma 4

Let ∂X be a bond of H with at most three edges, both sides containing cycles.

**Case 1: no site is split.** Then X is a union of whole sites and original vertices. Contracting each site gives a bond of P with the same
edges.
- By Lemma 3 one side is a single original vertex, which has no cycle.
- A single site is a degree-4 vertex of P, with four edges, too many.
- Either way, a contradiction.

**Case 2: a site S is split.**
- S is 2-edge-connected (a ladder), so at least two of the cut edges lie inside S. At most one edge is cut elsewhere, so no other site is
  split.
- **P − s is 2-edge-connected.** Suppose a bridge b separates A from B in P − s, with a of s's four edges going to A.
  - The bonds around A and A ∪ {s} have 1 + a and 5 − a edges, so one of them has at most three edges.
  - By Lemma 3 it would isolate a single original vertex adjacent to s twice. That vertex would be a common end of two crossing edges, or
    both pieces of one edge, both excluded.
- Expanding the other crossings into 2-edge-connected sites keeps H − S 2-edge-connected, so H − S lies on one side.
- The other side Y ⊆ V(S) contains a cycle. By Lemma 2, |∂Y| ≥ 4, a contradiction. ∎

## Proof of Lemma 5

**The pieces.** Write J for the twelve vertices c_i, q_i, q′_i (square edges deleted) and T for the result. Let ∂X be a bond of T with at
most three edges, both sides containing cycles.

**If J lies on one side.** Restoring the square gives a cut of H with the same edges, and both its sides contain cycles: the side holding J
contains C. This contradicts cyclic 4-edge-connectivity.

**If J is split.**
- J is 2-edge-connected, so at least two cut edges lie in J and at most one host edge is cut.
- **H − V(C) has no bridge.** Suppose a bridge b separates A from B in H − V(C), and a of C's four outside edges go to A. The cuts of H
  around A and around B then have 1 + a and 5 − a edges, so one of them has at most three.
  - By cyclic 4-edge-connectivity that side is a single vertex v, joined to two opposite corners of C.
  - Then C together with v is cut off by three edges, a cyclic 3-cut of H. Contradiction.
- So H − V(C) lies on one side, and the other side Y ⊆ J contains a cycle.
- An exhaustive check over the 2¹² subsets of J (section 2) shows that every such Y has at least four boundary edges, host edges counted. A
  contradiction. ∎

## Proof of Lemma 6

**The host.**
- By Lemma 4 the host H is cyclically 4-edge-connected, hence 3-connected, with a unique plane embedding.
- A 4-cycle of such a cubic plane graph is a face: a separating 4-cycle would leave a side behind an edge cut of size at most 2. So every
  junction square is a face of H.

**The certificate.** The cubes are planar braces with the square as a face. Kasteleyn signings of H and of the cubes, switched to one odd
pattern on every square, glue to a non-colourable signing (`SEYMOUR-COUNT-20261030-001A`, Lemma 1(iii), junction by junction). By
`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4, T is Pfaffian.

**A brace.** Lemma 5, applied once per junction (each junction square remains a 4-cycle), keeps T cyclically 4-edge-connected. Lemma 1 makes
it a brace.

**Plain.** T carries no sign by construction. ∎

## Proof of Theorem 7

**The reduction.**
- **The source.** Let G be a connected plain cubic bipartite graph, from the #P-hard source of `SOFT-CROSS-20261031-001B`, Theorem 3.
- **The frame.** Take F = C₂ₙ × K₂ with 2n ≥ |V(G)|, drawn by Tutte's method so that its faces are convex.
- **The drawing.** Place G's vertices at rational points in distinct square faces, draw G's edges straight, and perturb into general
  position.
- **The instances.** Let m be the number of crossings. For t = 0, …, N − 1, with N = C(m + 3, 3), build the woven instance T_t with
  k = 2t + 1 junctions at every site. Each T_t is a plain Pfaffian brace (Lemma 6) of polynomial size.

**The count.**
- By ticket A, Theorem 4, the counts #col(T_t) determine the count with every crossing restored. That is #col(G ⊔ F) = #col(G)·#col(F).
- **#col(F) is known and nonzero.**
  - F is planar, so #col(F) is computable in polynomial time.
  - It is nonzero: F is a brace, so its square faces are nice 4-cycles, and a plain non-colourable system has none
    (`PLAIN-COUNT-20261031-001B`, Lemma 4).
- Dividing gives #col(G). ∎

## Proof of Corollary 8

- **Planar plain braces** count in polynomial time (Valiant's holographic algorithm; Fan and Cai note it).
- **The Heawood graph** is a single graph.
- **Every other Pfaffian brace** is a trisum (Robertson, Seymour and Thomas), and Theorem 7 makes the class #P-hard.
- **The twist statement** is `PLAIN-COUNT-20261031-001B`, Corollaries 3 and 5. ∎

## What the computation checks

`check.py` (about 50 seconds):
- **1, Lemma 1 on examples.**
  - Eight cyclically 4-edge-connected planar cubic bipartite graphs (prisms of 8 to 24 vertices, and flag graphs of K₄, the triangular prism
    and the square pyramid) are braces.
  - Two cubes minus a vertex, joined by three edges, have a cyclic 3-cut and are not a brace.
- **2, Lemmas 2 and 5.**
  - Sites with 1, 2 and 3 junctions are the ladders P₃ₖ × K₂.
  - Every vertex set containing a cycle has at least four boundary edges: exhaustive, up to 2¹⁸ sets. The same holds for the cube junction
    (2¹² sets).
  - Replacing a square of the 4-prism, the 6-prism or the truncated octahedron by the cube junction gives a brace (direct test).
- **3, Lemmas 4 and 6.** Five woven instances:

  | Source | Frame | Crossings | Vertices |
  |---|---|---|---|
  | two halves joined by a 2-edge cut (not a brace) | 12-prism | 48 | 708 |
  | two halves joined by a 2-edge cut (not a brace) | 12-prism | 64 | 932 |
  | two halves joined by a 2-edge cut (not a brace) | truncated octahedron | 58 | 848 |
  | K₃,₃ | 6-prism | 14 | 214 |
  | the Heawood graph | 14-prism | 74 | 1078 |

  - In every one the host is planar and cyclically 4-edge-connected, and the instance is plain and certified Pfaffian.
  - The 214-vertex instance passes the direct brace test.
- **4, a single site inside a woven instance.** In the 708-vertex and 214-vertex instances, two sites each were varied over 1, 3, 5 and 7
  junctions. Ticket A's formula returns exactly the count with that site restored (numbers up to 65 digits).
- **5, the frame factor.**
  - #col(C₂ₙ × K₂) = 6, 20, 46, 122, 324, 842, 2206, 5780 and 15126 for 2n = 4, …, 20, all nonzero.
  - Observation: these are L₂ₙ − 1, or L₂ₙ + 2 when 3 divides n, with L the Lucas numbers.
  - With every site restored the count is 8424 = 26·324, that is #col(G)·#col(F).
- **6, controls.**
  - The two-halves source drawn without a frame (21 crossings) keeps its 2-edge cut: the host is not cyclically 4-edge-connected, and the
    instance is not a brace.
  - An even number of junctions at one site leaves the host non-planar.

## Reading

- **Connectivity does not protect counting, and neither does Pfaffian-ness.**
  - A brace is as connected as a bipartite graph can be in the matching sense.
  - A Pfaffian brace has its perfect matchings counted by one determinant.
  - Yet plain cubes and a prism encode every count.
- **The plain picture is complete in the worst case.**
  - Planarity is easy.
  - The knot's atom is the one non-planar plain brace without twists.
  - Everything else is hard as a class.
- **Two against three, once more.**
  - One plain page is a planar matchgate.
  - Two meeting at a square are soft and non-matchgate, but not a crossing.
  - A ladder of such squares is an exact crossing, and with it every counting problem.

## Nonclaims

- **Not every non-planar plain brace is hard.** Theorem 7 is about the class. Particular families, for example those with few junctions, may
  be easy.
- **The multi-site interpolation is not run end to end.** It is proved (ticket A, Lemma 3). Single sites are recovered inside woven
  instances.
- **External results.** The Hall-type characterization of braces, Tutte's embedding, plane duality, Valiant's algorithm and the
  Robertson–Seymour–Thomas structure theorem are not replayed.
