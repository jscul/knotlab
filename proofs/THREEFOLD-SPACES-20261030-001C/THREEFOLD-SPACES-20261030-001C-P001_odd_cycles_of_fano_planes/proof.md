# Odd cycles of Fano planes: beyond Fano compositions

Status: Proved

Ticket `THREEFOLD-SPACES-20261030-001C`, 2026-10-30.

**What it uses:**
- `THREEFOLD-SPACES-20261030-001A`:
  - the dictionary (Theorem 1) and the splice calculus with twists (Theorem 2);
  - Theorem 3: Fano compositions have 7 + 6k points;
  - the library.
- `THREEFOLD-SPACES-20261030-001B`: no twisted cubic triple system on at most 13 points.
- `SPACE-SELECTION-20261030-001C`, Theorem 2 (duality). A three-fold gadget with odd base counts and distinct corner triangles is exact at
  the knot iff two conditions hold for its dual triple system H (triangles as points, contacts plus the corner line L₀ as lines):
  - H is not 2-colourable;
  - H − L₀ is 2-colourable.

## Erratum for ticket A, Theorem 4

`THREEFOLD-SPACES-20261030-001A-P001` (closed) states a reduction: if no cubic brace has a sign-nonsingular signing with one negative edge,
then every non-colourable cubic triple system is a Fano composition and has 7 + 6k points.
- **The conclusion is false.** Theorem 3 below gives a non-colourable linear cubic triple system on 27 points, and Theorem 1 gives one on 21
  points. Neither size is 1 mod 6.
- **The gap.** The proof decomposes along tight cuts and treats both contractions as cubic triple systems with three distinct points per
  line. But a contraction can put a point twice on one line. Contracting the Fano block {0, 3, 4, 5, 6, 11, 12} of the 14-point system
  below turns the line (11, 12, 13) into (t, t, 13). Such pieces, a doubled incidence or a parallel edge in the incidence graph, lie outside
  both the induction and the one-twist hypothesis.

Theorems 1–3 of ticket A, Lemma 5, Corollary 6 and Proposition 7 are unaffected. Ticket B's exhaustive results are stated directly by SAT
and are also unaffected.

## Standard statement

**Setting.**
- **Cubic triple systems** are as in ticket A: three distinct points per line.
- **A Fano block** is a Fano plane minus one line. Its three *ports* are the points of the missing line.
- **A cycle of k Fano blocks** takes blocks B₀, …, B_(k−1). It joins B_i to B_(i+1) (indices mod k) by the *connecting line* through
  ports 0 and 1 of B_i and port 2 of B_(i+1).
- **A twist** complements one incidence of a line in colourings (ticket A).

**Results.**
- **Lemma (block).** A Fano block forces its three ports to one colour in every proper colouring, and both colours occur. So a block acts as
  one point with three ports.
  - A line through two ports of one block and a port of another block is the inequality x ≠ y between the two blocks' colours.
  - Twisting it at the single port makes it the equality x = y.
  - Twisting it at a doubled port makes it vacuous.
- **Theorem 1 (odd cycles of Fano planes).** A cycle of k Fano blocks is a linear, connected cubic triple system on 7k points. It is 2-colourable
  iff k is even.
  - k = 1 is the Fano plane itself.
  - k = 3 gives 21 points, and k = 5 gives 35.
- **Theorem 2 (twisted cycles).** With one connecting line twisted at its single port, a cycle of k blocks is 2-colourable iff k is odd.
  - The twisted 2-cycle has 14 points and is sign-nonsingular with its twist (|det| = per = 320).
  - It is isomorphic, twist included, to the twisted system found by SAT at 14 points.
  - By ticket B no twisted system has at most 13 points, so it is the smallest twisted cubic triple system.
- **Theorem 3 (27 points).** Splice two twisted 2-cycles at their twisted incidences, a point splice pairing the twisted cut edges. The
  result is a linear connected cubic triple system on 27 points that is not 2-colourable. Pairing the cut edges otherwise gives a
  2-colourable system.
- **Corollary 4 (the knot).** By the duality, the knot is exact on three-fold gadgets with 21, 27, 35, … triangles that are not Fano
  compositions: the duals of odd cycles of Fano blocks and of the 27-point system, with any corner line.
  - The 21-triangle gadgets are exact at the knot directly, with λ(0) = 125.
  - The 35- and 27-point systems satisfy both duality conditions for every corner line.
- **Conjecture 5 (structure).** Every non-colourable connected cubic triple system is assembled from Fano blocks by:
  - splices;
  - cycles of blocks with an odd number of inequalities, counting a twist as turning an inequality into an equality.

  Equivalently, the tight-cut decomposition of its incidence graph consists of Heawood graphs and planar pieces with doubled edges whose
  faces all have length 2 mod 4 (Kasteleyn's condition), with consistent twists. The cycle of k blocks contracts to the doubled 2k-gon,
  whose faces are k digons and two 2k-gons, and 2k ≡ 2 mod 4 iff k is odd.

## Nearest known result

- **Tickets A and B.**
- **The general theory.** Robertson–Seymour–Thomas (1999): a Pfaffian brace is the Heawood graph or is built from planar braces by
  4-sums. Kasteleyn's face condition governs planar Pfaffian orientations. Conjecture 5 is the reading of these for cubic triple systems
  with trivial or once-twisted signings. It is not proved here.
- **Obstructions to 2-colouring.** The odd cycle (for graphs) and the Fano plane (for 3-uniform hypergraphs) are the classical minimal
  obstructions.
- **Classification.**
  - Theorems 1–3 are short consequences of the block lemma and ticket A's splice calculus.
  - Their reading for the knot: no overlap found (candidate local delta).

## Proof of the block lemma

- Every proper colouring of the Fano plane minus a line makes the missing line monochromatic, since otherwise the Fano plane would be
  2-colourable.
- Both colours occur by complementation. The check counts the 10 colourings exhaustively.
- **The connecting line.** Let x be the colour of B_i and y that of B_(i+1). A line (x, x, y) is proper iff x ≠ y. Twisting the single
  port gives (x, x, ¬y), which is proper iff x = y. Twisting a doubled port gives (¬x, x, y), which is always proper. ∎

## Proof of Theorem 1

- **Structure.** Each block contributes 7 points and 6 lines, and k connecting lines are added: 7k points and 7k lines.
  - Each port gains one connecting line, so every point is on three lines.
  - Two blocks share no point, and a connecting line meets each block in at most two ports, never on a common block line. So the system is
    linear.
  - It is connected through the connecting lines.
- **Colourings.** By the lemma, proper colourings correspond to colourings x₀, …, x_(k−1) of the blocks with x_i ≠ x_(i+1) for all i (mod k).
  That is a proper 2-colouring of the k-cycle, which exists iff k is even. ∎

## Proof of Theorem 2

- **Colourings.** One equality and k − 1 inequalities around a cycle are satisfiable iff k − 1 is even, i.e. iff k is odd.
- **The 14-point system.**
  - Isomorphism with the SAT solution is checked with the twisted incidence marked.
  - Sign-nonsingularity is checked by exact determinant and permanent: |det| = per = 320 with the twist. Without the twist,
    |det| = 192 < 320.
- **Minimality** is ticket B's SAT result. ∎

## Proof of Theorem 3

- Both copies are sign-nonsingular with the same twisted cut edge. By ticket A, Theorem 2(iii), their splice is sign-nonsingular
  untwisted. By Theorem 1 of ticket A it is therefore not 2-colourable. This is confirmed by SAT.
- **The pieces.** The two copies are the twisted 2-cycles. Their blocks give the core a single cycle of blocks joined by inequalities and two
  twisted equalities, which cancel in parity.
- **Not a composition.** 27 is not 1 mod 6, so by ticket A, Theorem 3, the system is not a Fano composition.
- **Control.** A mis-paired splice is 2-colourable, as the check confirms. ∎

## Proof of Corollary 4

The duality needs H not 2-colourable and H − L₀ 2-colourable for the corner line L₀. The check confirms both for every line of the 35- and
27-point systems by SAT. The second condition holds in general by minimality (ticket A, Theorem 1). The 21-triangle gadgets are evaluated
directly. ∎

## What the computation checks

`check.py` (about a minute):
- **The erratum.** The 27-point system, and the contraction of the 14-point system that repeats a point.
- **The block lemma**, exhaustively.
- **Cycles of k = 1..7 blocks.** Structure, colourability by SAT, and agreement with the core.
- **Twisted cycles of k = 1..6 blocks.**
- **The 14-point system.** Isomorphism with the SAT solution, and exact determinant and permanent.
- **The knot side.** Direct evaluation at 21 triangles, and the duality conditions at 27 and 35.
- **Controls:**
  - even cycles are 2-colourable;
  - a doubled-port twist makes the 3-cycle 2-colourable;
  - a mis-paired splice is 2-colourable.

## Reading

- **The knot's own space is built from the two obstructions to 2-colouring.**
  - A gluing made only of three-fold knot contacts is a knot space exactly when its dual resists 2-colouring as a whole but not after the
    corner line is removed.
  - There are two classical reasons a structure resists 2-colouring: an odd cycle of "different" constraints, and the Fano plane, the
    smallest system of triples with no proper 2-colouring.
  - The knot uses both. Fano blocks are the three-place atoms. Lines that meet a block twice are two-place "different" constraints. Odd
    cycles of these close the space.
- **The two/three boundary, once more.** The Fano plane is the three-place obstruction and the odd cycle the two-place one. The knot's
  three-fold space needs both, and a twist (a sign) is what turns an even cycle into an odd one.
- **Correction recorded.** The first reduction (ticket A) treated Fano compositions as the whole family. It missed pieces with doubled
  incidences, which are exactly where odd cycles enter.

## Nonclaims

- **Conjecture 5** is not proved.
- **No sizes beyond 13.** No classification at a fixed size beyond 13 points is claimed here. The searches for 14 and 15 points are scoping:
  14 is SAT-negative untwisted, recorded in the decision note.
- **Corollary 4 at 27 and 35 points** rests on the duality theorem of `SPACE-SELECTION-20261030-001C` and on SAT. Those gadgets are too
  large to sum over directly.
