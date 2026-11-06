# Census with doubled incidences

Status: Proved

Ticket `THREEFOLD-GRAMMAR-20261030-001B`, 2026-10-30.

**What it uses:**
- `THREEFOLD-GRAMMAR-20261030-001A`: the structure of tight-cut decompositions (Theorem 2), Lemma 3 (4-cycles of Pfaffian braces), the
  one-twist lemma (Theorem 4), the Fano-leaf theorem (Theorem 5), T14, and the library.
- `THREEFOLD-SPACES-20261030-001A`:
  - the dictionary: a connected cubic triple system with distinct points per line is not 2-colourable iff it is minimally so iff its
    incidence matrix is sign-nonsingular (SNS);
  - the splice calculus (Theorem 2);
  - the library.
- `THREEFOLD-SPACES-20261030-001B`: the census of systems with distinct points per line up to 13 points (sizes 7 and 13, one class each;
  no twisted system), and its SAT encoder.
- `THREEFOLD-SPACES-20261030-001C`: the block lemma (a Fano block forces its ports equal).
- Seymour 1974, not replayed: a minimally non-2-colourable hypergraph has at least as many edges as vertices.

## Why this ticket exists

The approved recommendation asked to extend the SAT census to pieces with a repeated point on a line. This ticket does that. With the
Fano-leaf theorem of ticket A the census then determines every three-fold space up to 22 points, which no direct SAT search reaches. The
direct search stopped at 14 points.

## Standard statement

**Setting.**
- **Multi-systems.** A *multi-system* K has n points and n lines. Line ℓ contains point p with multiplicity m(ℓ, p) ∈ {0, 1, 2, 3}, and
  every line and every point has three incidences.
- **Colourings.** A 2-colouring is proper on a line when the line's points, each counted once, carry both colours.
- **Twists.** A *twist* at an incidence (ℓ₀, p₀) of multiplicity one complements p₀'s colour on ℓ₀ (ticket A of the previous epic).
- **Census.** The *census* consists of the connected multi-systems that are not 2-colourable, or, for the twisted census, not
  2-colourable with their twist.
- **Repeated incidences.** An incidence with m ≥ 2 is *repeated*.
- **Fano pieces** (ticket A).
  - A *Fano block* is Fano minus a line, attached at that line's three points (its ports).
  - A *dual block* is Fano minus a point p, attached through the three lines through p, each of which receives one outside point (its
    slot).
- **Decoration.**
  - For a set S of points and lines of K, D(K, S) replaces each point of S by a Fano block, with its three incidences going to the three
    ports, and each line of S by a dual block, with its three points going to the three slots.
  - S *covers* K when every repeated incidence has an end in S.

**Results.**
- **Theorem 1 (census).** For n ≤ 10, the census has these numbers of isomorphism classes (points and lines kept apart, the twist marked):

  | n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | untwisted | 1 | 0 | 1 | 1 | 2 | 2 | 8 | 12 | 36 | 97 |
  | twisted | 0 | 1 | 1 | 3 | 7 | 19 | 54 | 166 | 515 | 1726 |

  On every class:
  - non-colourability coincides with sign-nonsingularity, with the twist where there is one;
  - every twisted class is 2-colourable once its twist is removed;
  - every brace of the tight-cut decomposition is a Heawood graph, a doubled square, a planar brace or a non-planar Pfaffian brace;
  - every leaf is a Heawood graph or a doubled square, and no Heawood leaf contains the twisted incidence.

  The only class with distinct points per line is the Fano plane. A non-planar Pfaffian brace occurs once: in a twisted class at n = 10,
  as the trisum of three cubes along a common 4-cycle. Decorated by ticket A, Theorem 6 (T14 on the twisted point, Fano blocks on the
  repeated points), that class gives a linear, minimal 35-point system that is not 2-colourable and keeps the trisum among its braces.
- **Lemma 2 (pieces act as points and lines).**
  - In every proper colouring, a Fano block's ports are equal, and every common value extends to the block.
  - A dual block's three slot values are not all equal, and every such triple extends to the block.
  - Twists at the attaching incidences are carried through.
  - Hence, for every S:
    - D(K, S) is (twisted) 2-colourable iff K is;
    - it is connected iff K is;
    - it has n + 6|S| points;
    - it has distinct points per line iff S covers K.
- **Lemma 3 (twisted dictionary).** A connected cubic triple system with distinct points per line and one twisted incidence is not
  2-colourable (with the twist) iff it is SNS with that incidence negated.
- **Lemma 4 (contraction).** Let H be a connected 3-regular triple system with distinct points per line, other than the Fano plane, that
  is not 2-colourable, or not 2-colourable with one twist. Then H = D(K, S) for a member K of the census (twisted with it), with S
  covering K and |S| ≥ 2.
- **Theorem 5 (the spectrum up to 22 points).** A connected 3-regular triple system with distinct points per line and at most 22 points
  that is not 2-colourable has 7, 13, 19, 21 or 22 points.

  | points | 7 | 13 | 19 | 21 | 22 |
  |---|---|---|---|---|---|
  | isomorphism classes | 1 | 1 | 4 | 1 | 1 |

  All of them are linear and minimal, so their duals are three-fold knot spaces.
  - With one twisted incidence the sizes are 14, 15, 18, 20, 21 and 22, with 1, 1, 1, 11, 7 and 3 classes. All are minimal; some at
    18, 20 and 22 points have two lines sharing two points.
  - The smallest twisted one is T14, the twisted doubled square with Fano blocks on both points.
- **Theorem 6 (independent SAT at 14 points).** The encoder of `THREEFOLD-SPACES-20261030-001B` finds no untwisted system with distinct
  points per line at 14 points. With one twist it finds exactly one isomorphism class, T14, whose incidence graph is not a brace.

## Nearest known result

- **Ticket A and the previous census.** The census with distinct points per line (THREEFOLD-SPACES B) gave the sizes 7 and 13 up to
  13 points. Theorem 5 agrees with it and extends it to 22.
- **Literature.** The square minimally non-2-colourable hypergraphs are characterized by Seymour (1974) and Robertson, Seymour and Thomas
  (1999) through Pfaffian braces. No table of sizes or counts for the 3-uniform 3-regular case was found.
- **Classification.** No overlap found (candidate local delta) for the census of multi-systems, the contraction to cores, and the size
  spectrum.

## Proof of Theorem 1

- **Encoding.** Variables y(k, ℓ, p) mean m(ℓ, p) ≥ k, for k = 1, 2, 3.
  - Cardinality constraints give the row and column sums.
  - By relabelling, point 0 lies on line 0, and the twist (multiplicity one) sits there.
  - Non-colourability is encoded as: for every colouring with point 0 coloured 0, some line is monochromatic on its support.
  - Minimality is encoded by witnesses: for every line, a colouring that is proper on every other line.
- **Minimal means connected.** If K were disconnected, removing a line from a component other than a non-colourable one would keep K
  non-colourable.
- **Connected means minimal.**
  - Let K be connected and not 2-colourable, and let K′ ⊆ K be a minimal non-colourable set of lines on the points V′.
  - If K′ avoids the twisted line, Seymour's theorem (lines as their supports) gives |K′| ≥ |V′|.
  - If K′ contains it, replace p₀ on that line by a new point p₀′ and add the 2-element line {p₀, p₀′}. The result is minimally not
    2-colourable, so |K′| + 1 ≥ |V′| + 1.
  - Every point of V′ has at most three incidences in K′, so 3|K′| ≤ 3|V′|. Equality holds, so every point of V′ has all its incidences
    in K′, and K′ is a union of components. Hence K′ = K.
  - A triple incidence forms a component of its own, so it occurs only at n = 1.
- **Symmetry breaking.** Rows 1..n−1 and columns 1..n−1 are put in non-increasing lexicographic order. Each row is read as the thermometer
  codes (y1, y2, y3) of its entries, so the order on entries is the order on multiplicities.
  - Sorting rows never decreases the matrix read row by row.
  - Sorting columns maximizes that reading over column orders.
  - So alternating sorts terminate in a doubly sorted matrix without moving row 0, column 0 or the twist.
  - The census without these constraints, with a second solver, gives the same classes for n ≤ 5.
- **Enumeration.**
  - All symmetry-broken solutions are enumerated with blocking clauses.
  - They are classified by graph isomorphism of incidence graphs, with multiplicities and the twist as edge labels.
  - The properties are computed per class: brute-force colourings, exact determinants and permanents, and tight-cut decompositions. ∎

## Proof of Lemma 2

- **Fano blocks.**
  - The ports are forced equal (block lemma of the previous epic).
  - Given a common value c on the ports, colour the other four points ¬c. Every line of the block meets the removed line in one port and
    contains two of the four other points, so it is proper.
- **Dual blocks.**
  - Suppose the slot values were all equal to c. Colouring the removed point p with c would give a proper colouring of the Fano plane,
    since each line through p carries the same colours as its slot line. That is impossible.
  - **Extension.** Let the slot values be (c, c, ¬c). The fourth lines of the Fano plane avoid p and contain one point from each pair
    {a_i, a_i′} of the lines through p. Colour a₃ = a₃′ = c, a₁ = a₁′ = ¬c, a₂ = c and a₂′ = ¬c. Then every line through a slot and
    every remaining line is proper.
  - The stabilizer of p in the automorphism group of the Fano plane acts on the three lines through p as S₃. Together with swapping the
    colours, this covers every triple that is not all equal.
- **Twists.** A twisted incidence at a port sees the complement of the block's common value, exactly as the twisted incidence at the point
  did. A twisted incidence at a slot feeds its complemented value into the dual block's constraint.
- **The consequences.**
  - A colouring of D(K, S) restricts to K (a point takes its block's port value) and every colouring of K extends.
  - Each piece adds six points and six lines.
  - A line of K outside S that repeats a point p gets distinct ports iff p ∈ S. A line in S spreads its points over three different slot
    lines. So D(K, S) has distinct points per line iff S covers K. ∎

## Proof of Lemma 3

Let H have its twist at (ℓ₀, p₀). Point-splice T14 into H at p₀, along T14's root line (0, 1, 2), with port 0 on ℓ₀. Call the result H*.
- **T14 minus its root line acts as a twisted point.** Its port colourings are exactly ¬x₀ = x₁ = x₂ (computed). So H* is 2-colourable
  iff H is 2-colourable with its twist.
- **Signs.** By the splice calculus, H* is SNS iff some sign pattern σ on the three cut edges makes both pieces SNS. Up to switching at
  the root line, T14 is SNS only with the twist at port 0 (|det| = per = 320; the other three patterns give |det| = 192, 64, 64). So H* is
  SNS iff H is SNS with (ℓ₀, p₀) negated.
- **The untwisted dictionary.** H* is connected, cubic and has distinct points per line, so it is not 2-colourable iff it is SNS. ∎

## Proof of Lemma 4

- **Untwisted H.**
  - By ticket A, Theorem 5, the tight-cut decomposition of B(H) has at least two leaves. They are Fano pieces with disjoint shores.
  - Contracting each leaf shore (a block to a point, a dual block to a line) gives a connected cubic multi-system K, and H = D(K, S) with S
    the contracted elements.
  - The attachment is unique up to isomorphism: the stabilizer of a line, or of a point, in the Fano group acts as S₃ on its three
    incidences.
  - By Lemma 2, K is not 2-colourable and S covers K.
- **Twisted H.**
  - By Lemma 3, the signing σ = {e} is Pfaffian on B(H), where e is the twisted edge. B(H) is not a brace, by ticket A, Theorem 4.
  - Matching signs multiply edge by edge, so the splice calculus holds for signed systems with σ restricted to each piece.
  - **Each leaf is an untwisted Fano piece.** A leaf is signed by σ inside its shore and by a cut pattern that negates at most one edge
    after switching.
    - If e lay inside the shore, the leaf would carry a Pfaffian signing negating one or two edges.
    - The Heawood graph has no such signing: its Pfaffian signings are the switchings of the trivial one, and it has no cut of fewer than
      three edges.
    - A planar brace has at least six 4-faces, which two edges cannot all meet. A non-planar Pfaffian brace has three pairwise
      edge-disjoint 4-cycles (ticket A, Lemma 3).
    - So e is not inside any leaf. With at most one negated edge, every leaf is an untwisted Fano piece.
  - **e may lie on a leaf's cut,** as it does in T14. Contracting the leaves then puts the twist on the corresponding incidence of K.
  - **That incidence has multiplicity one.** Otherwise it would be one of two parallel incidences after contraction. Either a line of H
    contains two ports of one block, one of them twisted, or a dual block receives the same point twice, once twisted. That constraint
    would always hold, so removing a line would keep H non-colourable. This contradicts minimality (connected means minimal, as in
    Theorem 1).
  - By Lemma 2, K is in the twisted census. ∎

## Proof of Theorem 5

- **Reduction to the census.** By Lemma 4, every system with N ≤ 22 points other than the Fano plane is D(K, S) with |S| ≥ 2. So
  n_K = N − 6|S| ≤ 10, and K is in the census. By Lemma 2, every D(K, S) with S covering K is such a system.
- **The computation.** It lists D(K, S) for every census core, every cover with |S| ≥ 2 and every size up to 22, with the twisted
  incidence tracked through the decoration. It adds the Fano plane and classifies by isomorphism.
  - Every decoration is checked to be simple, cubic, connected and not 2-colourable by SAT.
  - Every class is checked to be linear and minimal.
- **The sizes, explained.** The untwisted cores with the fewest repeated incidences are:
  - n = 1: the triple incidence (one repeated incidence, two elements);
  - n = 3 and 4: three;
  - n = 5 and 6: four;
  - n = 7: the Fano plane (none; the other classes have at least three);
  - n = 8: four;
  - n = 9 and 10: two.

  Hence:
  - 13 = 1 + 2·6;
  - 19 = 7 + 2·6;
  - 21 = 3 + 3·6 = 9 + 2·6;
  - 22 = 4 + 3·6 = 10 + 2·6.

  The sizes 8 to 12 would need n ≤ 0, so only the Fano plane (no leaves) lies below 13. The sizes 14, 15, 16, 17, 18 and 20 would need a
  core with n = 2, 3, 4, 5, 6 or 8 and at most two repeated incidences, and there is none. ∎

## Proof of Theorem 6

- **Untwisted.** The encoder with lexicographic symmetry breaking, sound by its own argument, is unsatisfiable at n = 14.
- **Twisted.**
  - All symmetry-broken solutions are enumerated with blocking clauses and classified with the twist marked: there is one class.
  - It is isomorphic to T14, which ticket A's tight-cut search shows is not a brace.
- **Agreement.** This agrees with Theorem 5 and with ticket A, Theorem 4. ∎

## What the computation checks

`check.py` (about 25 minutes; the two SAT runs at 14 points take most of it and run in parallel):
- **the census** for n ≤ 10, untwisted and twisted, with every class tested;
- **the replay** without symmetry breaking for n ≤ 5;
- **the spectrum:**
  - every decoration of every census core at every cover with at least two pieces, up to 22 points, classified;
  - simplicity, cubicity, connectivity and non-colourability by SAT;
  - minimality of every class, and linearity of the untwisted ones;
  - the non-planar braces, tested Pfaffian, and the 35-point decoration of the core that carries one;
  - the number of classes at 19 up to point-line duality;
  - T14 as the decorated twisted doubled square;
- **the independent SAT runs at 14 points;**
- **controls:**
  - the doubled square is 2-colourable and not SNS;
  - a decoration missing a repeated incidence leaves a repeated point;
  - decorating a 2-colourable core gives a 2-colourable system;
  - T14 with its twist moved to another incidence of the twisted line is 2-colourable.

## Reading

- **Three-fold knot spaces are rare and come in steps of six.** Below 23 points they exist only at 7, 13, 19, 21 and 22 points: 8
  systems in all, each a small core dressed with Fano pieces.
  - Every step of six is one Fano plane minus an element.
  - The cores carry the shape.
  - The gaps at 14–18 and 20 come from the cores, not from the pieces: no small core has few enough repeated incidences.
- **The glue skeletons.** The cores with repeated incidences decompose into doubled squares, planar braces, Heawood graphs and, once, a
  non-planar trisum of three cubes, as ticket A predicts.
  - The trisum is real glue: it survives into a 35-point three-fold knot space.
  - So the knot's glue is not always planar, but it is always assembled from planar pieces.
  - The twisted cores, the carriers of the glue's twists, start at T14.

## Nonclaims

- **Bounds.** The census is complete for n ≤ 10 only, and the spectrum only up to 22 points.
- **Classes** are counted with points and lines kept apart (and the twist marked). Up to point-line duality there are fewer, as reported
  by the check at 19 points.
- **External input.** Seymour's theorem is used as an external result.
