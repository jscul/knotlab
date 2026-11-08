# A finite rule on knots regrows the pinwheel law

Status: Proved. Locality and induction are argued by hand; the finite closure of the labels and exact agreement with the geometric
construction at levels 0–7 are computed (`check.py`).

Ticket `PINWHEEL-NATIVE-20261107-001A`, 2026-11-07.

## Standard statement

- **The tilings.** Let T_k be the patch of Conway and Radin's pinwheel tiling obtained by applying Conway's cut k times to one right
  triangle with legs 1 : 2.
- **The structure.** Record only:
  - which tiles share which boundary segments;
  - for each tile, its handedness and the order of its segments along each of its three sides;
  - for each segment, the two tiles' side types, its interval along each of those sides, and whether the two sides run the same
    way along it.
- **The result.**
  - **Few labels.** Only eleven segment labels occur at any level: eight inside the patch and three on its boundary.
  - **A finite rule.** A finite rule on these labels maps the recorded structure of T_k to that of T_{k+1}, for every k.
  - **No geometry.** The rule uses no coordinates and no angles.

## Nearest known result

- **Collared tiles.** Substitution tilings with finite local complexity have finite combinatorial descriptions, through collared
  tiles and Anderson–Putnam complexes.
- **The pinwheel.** It does not force its border, so collaring is needed.
  - **Barge, Diamond, Hunton and Sadun** (Ergodic Theory Dynam. Systems 30, 2010) computed its cohomology this way.
  - **Frettlöh, Whitehead and Whittaker** (J. Aust. Math. Soc., 2014) give an Anderson–Putnam complex with 138 edges.
- **Combinatorial versions.** Combinatorial substitutions realizing geometric ones are a young topic (for example the topological
  substitution for the Rauzy fractal, arXiv:1603.02790).
- **Classification: known-overlap-found.** The delta, as far as found:
  - an explicit eleven-label rule acting on the knots and distinctions of a parity law;
  - its exact verification;
  - the census it gives: the pinwheel's only T-junctions are at midpoints of long legs.

## Terms

- **The tile law of T_k.** Knots are the tiles; each is a parity relation over the segments of its boundary.
- **Distinctions** are the segments: pieces of tile sides between consecutive tile corners. Each interior distinction is shared by
  two knots, each boundary distinction by one.
- **A tile.** (O, P, Q) is the right-angle vertex, the end of the long leg and the end of the short leg. Its sides run S: O→Q,
  L: O→P, H: Q→P.
- **Conway's cut** adds three points and five pieces:
  - **The points.** H, the foot of the altitude from O, at 1/5 of the way from Q along H; M, the midpoint of L; F₁ and F₂, the
    midpoints of OH and HP.
  - **The pieces.** C₁ = (H, O, Q), C₂ = (F₁, M, O), C₃ = (F₁, M, H), C₄ = (F₂, H, M), C₅ = (F₂, P, M).
- **A distinction's label.** For each of its knots, the side type and the interval [lo, hi] it occupies along that side, as a
  fraction of the side. For an interior distinction, also whether the two sides run the same way along it.
- **A knot's label.** Its handedness, and its three sides as ordered lists of distinctions.

## Theorem 1 (a finite rule regrows the law)

**The rule R** acts on the labelled structure:
- **Knots.** Every knot is replaced by five knots, with handedness χ·(−1, −1, +1, +1, −1) for a parent of handedness χ.
- **Distinctions.** Every distinction is replaced by the sequence of pieces its label prescribes. The table is below, with labels
  named a to h (interior) and x, y, z (boundary):

| Label | Its two sides | Same direction | Pieces |
| --- | --- | --- | --- |
| a | H[0,1] \| H[0,1] | no | g e d e g |
| b | H[0,1] \| H[0,1] | yes | h c c |
| c | L[0,1] \| L[0,1] | yes | b b |
| d | L[0,½] \| L[0,½] | no | a |
| e | L[0,½] \| L[½,1] | yes | b |
| f | L[0,½] \| S[0,1] | no | b |
| g | L[½,1] \| S[0,1] | yes | a |
| h | S[0,1] \| S[0,1] | yes | b |
| x | H[0,1] (boundary) | — | z y y |
| y | L[0,1] (boundary) | — | x x |
| z | S[0,1] (boundary) | — | x |

- **Inside each knot**, five new distinctions appear:
  - H–F₁ (label f) between C₁'s L and C₃'s S;
  - F₁–O (g) between C₁'s L and C₂'s S;
  - F₁–M (c) between the L sides of C₂ and C₃;
  - H–M (a) between the H sides of C₃ and C₄;
  - F₂–M (h) between the S sides of C₄ and C₅.
- **The children's sides** are assembled from these pieces and new distinctions. `rule_table.json` lists them.

**Claim.**
- (a) Applied to the labelled tile law of T_k, R gives the labelled tile law of T_{k+1}, for every k.
- (b) The label set {a, …, h, x, y, z} is closed under R.

*Proof.*

(a) **Locality.**
- **The cut's points.** It adds points only at the midpoint of a long leg, at 1/5 and 3/5 of a hypotenuse from Q, and at the
  interior point F₁.
- **Each distinction sees two tiles.** Tiles are convex with disjoint interiors, so the interior of a distinction lies on the
  boundary of exactly its two tiles. The points added inside it are the points those two tiles add on those sides.
- **So the label decides.** Where those points fall, and how the parent sides are covered by the children's sides, are fixed by
  the label:
  - S is covered by C₁'s H, reversed;
  - L by C₂'s H, then C₅'s H;
  - H by C₁'s S reversed, then C₄'s L reversed, then C₅'s L.
- **So the splitting is a function of the label alone.** The five inside distinctions and the children's handedness come from the
  cut.
- **Induction.** The base is the single triangle, with three boundary distinctions labelled x, y, z.

(b) **Closure.** Start from x, y, z and the five inside labels, and apply the table until no new label appears. The set stabilizes
after two rounds at eleven labels. ∎

**Corollary 2 (the round circle is grown by symbols).**
- **The rule is a table.** R is a finite table on eleven symbols and five child positions; it contains no coordinate and no angle.
- **What it grows.** The laws it grows are the pinwheel's tile laws, and the corner law is read from the same structure.
- **So the circle is grown by symbols.** The round circle of `PINWHEEL-ROUND-20261107-001` A belongs to laws grown by this table.

**Corollary 3 (the census of distinctions).**
- **The eight kinds.** Every interior distinction of the pinwheel is one of:
  - a whole hypotenuse against a whole hypotenuse, either way round;
  - a whole long leg against a whole long leg;
  - a whole short leg against a whole short leg;
  - half a long leg against a short leg, or against another half of a long leg.
- **So the only T-junctions** are at midpoints of long legs.
- **At level 7** the eight interior labels occur 21,297; 17,578; 22,617; 4,254; 8,508; 15,625; 24,133 and 19,121 times (a to h).

## The check

`check.py`, which runs in about 5 s, verifies the following.
- **Regrowth.** At levels 0–7, the symbolic rule's incidences (knot, side, exact interval, alignment) and handedness are identical to
  those of the geometric pinwheel built in exact integer coordinates. Level 7 has 78,125 knots and 133,883 distinctions.
- **Closure.** The alphabet closes at eleven labels.
- **Locality, on the geometric side.** At level 6, distinctions with one label always split into the same sequence of child labels.
- **Controls**, all rejected:
  - one child side's direction flipped;
  - the handedness pattern changed;
  - the hypotenuse cut at 1/5 and 2/5;
  - alignment ignored.
- **The table** is written to `rule_table.json`.

## Nonclaims

- **The labels are names.** The fractions ½, 1/5 and 3/5 name label classes; the rule runs on the table.
- **Whether the rule can read its labels** from the unlabelled law is ticket B's question.
- **Patches only.** The patches here grow from one triangle. Infinite pinwheel tilings are limits of such patches, and the theorem
  is stated for the patches.
