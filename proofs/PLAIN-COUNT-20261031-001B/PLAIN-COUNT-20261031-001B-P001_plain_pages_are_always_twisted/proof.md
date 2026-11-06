# Plain pages are always twisted

Status: Proved

Ticket `PLAIN-COUNT-20261031-001B`, 2026-10-31.

**What it uses:**
- **`TWIST-COUNT-20261030-001A`:**
  - twisted branches: the signing and the glued Pfaffian signing differ by a non-cut on the branch's own edges;
  - Lemma 3(iii): a branch containing a twisted branch is twisted;
  - Lemma 5: good roots;
  - Theorem 6: unbranched twists count in polynomial time.
- **`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4:** a connected cubic signed system is non-colourable iff its signing is Pfaffian.
- **`THREEFOLD-GRAMMAR-20261030-001B`:** the SAT census of non-2-colourable cubic systems, and Fano blocks.
- **External, not replayed:**
  - Euler's formula;
  - Kasteleyn: a planar bipartite graph's Pfaffian signings are the signings with |f|/2 − 1 negations mod 2 on every face f;
  - a Pfaffian signing has |C|/2 − 1 negations mod 2 on every nice cycle C, and any two differ by a cut (nice cycles span the cycle space of a
    matching-covered graph: Little; Lovász and Plummer);
  - Robertson, Seymour and Thomas: a Pfaffian brace is planar, the Heawood graph, or a trisum of smaller Pfaffian braces.

## Why this ticket exists

`SOFT-CROSS-20261031-001` located easy and hard counting by how twists meet. A twist was measured against signs supplied with the input.
Ticket A showed the signs can be traded for path lengths. The program's own objects, though, are plain triple systems.

So the question is where their twists sit. The answer is everywhere: Euler's formula puts a twist into every plain page.

## Standard statement

**Setting.**
- **Pages.** A *page* is a 2-connected planar cubic bipartite graph g with a square face S, the junction.
  - It is *plain* when no edge is negated.
  - Its *own edges* are all edges except S's four.
  - It is *twisted* when the plain signing differs from a Pfaffian (Kasteleyn) signing κ of g by a non-cut on its own edges. This is
    `TWIST-COUNT-20261030-001A`'s notion for a leaf.
- **Nice cycles.** A cycle C is *nice* when g − V(C) has a perfect matching.
- **Braces.** A *brace* is a bipartite graph in which every matching of two edges extends to a perfect matching.

**Results.**
- **Lemma 1 (Euler).** In a 2-connected cubic planar graph, the sum of 6 − |f| over the faces is 12.
  - If the graph is bipartite, at least six faces are squares.
  - At most five faces meet a square face: itself, and the faces across its four edges.
- **Theorem 2 (plain pages are twisted).** Every plain page is twisted.
- **Corollary 3 (twists branch in plain braces).** In a plain cubic Pfaffian brace that is a trisum, every square of the trisum tree has
  three twisted branches, and no root is good. So `TWIST-COUNT-20261030-001A`'s Theorem 6 reaches no plain trisum brace.
- **Lemma 4 (nice cycles).**
  - In a plain non-colourable system every nice cycle has length 2 mod 4.
  - In a brace every 4-cycle is nice.
- **Corollary 5 (the knot's atom).** The Heawood graph is the only cubic bipartite brace whose plain system is not 2-colourable.
  Equivalently, the Fano plane is the only non-2-colourable 3-regular 3-uniform hypergraph whose incidence graph is a brace.

## Nearest known result

- **Classical:** Euler's formula, Kasteleyn's face condition, and the parity of Pfaffian signings on nice cycles.
- **Lemma 4 is classical in another form.** That the plain signing is Pfaffian exactly when every nice cycle has length 2 mod 4 is the
  convertibility condition for permanents (Little 1975; Vazirani and Yannakakis 1989). `THREEFOLD-SPACES` matched it to non-2-colourability.
- **Corollary 5 is probably known** (folklore risk high). Robertson, Seymour and Thomas describe non-2-colourable square hypergraphs as
  splices of Fano planes, which likely implies it. It is given here with a short proof.
- **Theorem 2 and Corollary 3 have no overlap found.** Plain pages are always twisted, and plain trisum braces branch their twists at every
  square.

## Proof of Lemma 1

**The sum.** With V − E + F = 2, 2E = 3V and Σ|f| = 2E:

Σ(6 − |f|) = 6F − 2E = 6(2 + E − V) − 2E = 12 + 4E − 6V = 12.

**Squares.** In a bipartite graph faces have even length at least 4. Only squares contribute positively, 2 each, so there are at least six.

**Faces meeting a square.** At a vertex v of a square face S, the three faces are S and the two faces on either side of v's third edge.
Each of those two contains an edge of S at v. So every face that meets S meets it along an edge, and there are at most five such faces. ∎

## Proof of Theorem 2

**A square away from the junction.** By Lemma 1 some square face Q avoids S, so Q's four edges are own edges.

**Its parity.**
- A Kasteleyn signing κ of g has 4/2 − 1 = 1 negation mod 2 on Q. This also holds when Q is the outer face: the parities of all faces sum to
  E − F = V − 2, which is even.
- The plain signing has none.
- So plain ⊕ κ has odd parity on the cycle Q, which lies in the own edges. It is therefore not a cut there, and the page is twisted.

**The choice of κ does not matter.** Any two Pfaffian signings of a matching-covered bipartite graph differ by a cut, and a cut restricts to
a cut. ∎

## Proof of Corollary 3

**The leaves.** Split the brace along its trisum tree. The leaves are planar braces (Robertson–Seymour–Thomas; `SEYMOUR-COUNT-20261030-001B`,
Lemma 1), and their squares are faces: in a 3-edge-connected cubic planar graph every 4-cycle is a face.

**Every branch is twisted.**
- A branch at a square S is a subtree. It contains a tree leaf, a piece with a single square, and that piece is a plain page.
- By Theorem 2 that page is twisted, and by `TWIST-COUNT-20261030-001A`, Lemma 3(iii), so is the branch.
- So all three branches at every square are twisted, and by Lemma 5 no root is good. ∎

## Proof of Lemma 4

**Nice cycles.**
- Let C be nice. A perfect matching of g − V(C), together with alternate edges of C, is a perfect matching M, and C is M-alternating.
- The permutations of M and M ⊕ C differ by a cycle of length |C|/2. So a signing under which all perfect matchings carry the same sign has
  |C|/2 − 1 negations mod 2 on C.
- In a plain non-colourable system the plain signing is Pfaffian (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4). So 0 ≡ |C|/2 − 1, that is,
  |C| ≡ 2 mod 4.

**4-cycles in braces.** In a brace, for a 4-cycle abcd the matching {ab, cd} extends to a perfect matching M. Then M minus those two edges is
a perfect matching of g − {a, b, c, d}, so the cycle is nice. ∎

## Proof of Corollary 5

Let G be a cubic bipartite brace whose plain system is not 2-colourable.
- **Pfaffian, with no 4-cycle.** The plain signing is Pfaffian, so G is Pfaffian. By Lemma 4, G has no 4-cycle.
- **Robertson–Seymour–Thomas.** G is planar, the Heawood graph, or a trisum.
  - A planar G has a square face (Lemma 1).
  - A trisum contains a square face of a tree-leaf page that avoids that page's junction (Lemma 1), and its edges are edges of G.
- **So G is the Heawood graph**, and the plain Fano plane is indeed not 2-colourable. ∎

## What the computation checks

`check.py` (about 80 seconds):
- **1, Lemma 1** on 33 planar cubic bipartite graphs, 8 to 132 vertices: prisms, and flag graphs of planar maps including Delaunay
  triangulations. Each has 6 to 33 square faces, and at most 5 faces meet a square.
- **2, Theorem 2.** All 454 (graph, square) pages are twisted by the cut test, and the 197 small ones also by the tensor test (no split form).
- **3, Corollary 3.** Trisums of three truncated octahedra, of a cube, a 6-prism and a truncated octahedron, of three cubes, and a two-square
  tree (a truncated octahedron with four cubes). Each is:
  - a brace, certified Pfaffian, and colourable when plain;
  - three twisted branches at every square, with no good root.
- **4, Lemma 4 and Corollary 5:**
  - the census for n = 7 to 10 contains only the Fano plane, whose incidence graph is a brace;
  - five splices of Fano blocks, with 13 to 25 points, are non-colourable and not braces;
  - nowhere is there a nice cycle of length 4 or 8, while nice 6-cycles occur.
- **5, controls:**
  - the cut test is not degenerate: twenty random switchings of a Kasteleyn signing are untwisted, and one extra negation on a far square
    twists;
  - the Heawood graph is a brace with no 4-cycle, and is non-colourable when plain;
  - every graph of the family is colourable when plain and non-colourable under its Kasteleyn signing.

## Reading

- **In the plain world, twisting is the default.** A cubic plane needs squares (Euler), and a square forbids plain signs: a Pfaffian signing
  must put an odd number of signs on a 4-cycle. Every plain planar page carries a twist away from its junction.
- **So plain braces never offer the easy junction.** Counting stays easy at a junction when one side carries the knot's signs (a similitude
  at the knot's angle, `TWIST-COUNT`). Plain non-planar braces have no such side: their twists branch at every square.
- **The knot's own atom is the exception.** The Fano plane's incidence graph has no squares at all; its shortest cycles are hexagons, and
  6 ≡ 2 mod 4. It is the only plain brace without twists, and the only plain brace that cannot be 2-coloured.
- **With ticket A:** plain triple systems with Pfaffian incidence graphs are #P-hard to count in general, and plain braces branch their
  twists everywhere except at the knot's atom.

## Nonclaims

- **No hardness on plain braces.** Corollary 3 says only that the polynomial junction mechanism does not reach them. Ticket A's hard
  instances are not braces.
- **The census is exhaustive only to n = 10.** Larger systems are checked through splices. The proofs of Lemma 4 and Corollary 5 are general,
  given the external results.
- **External results.** Robertson–Seymour–Thomas, Kasteleyn, and the nice-cycle facts are not replayed.
