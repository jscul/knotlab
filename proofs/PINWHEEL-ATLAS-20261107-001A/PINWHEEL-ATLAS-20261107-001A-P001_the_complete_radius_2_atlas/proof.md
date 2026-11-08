# The complete radius-2 atlas of the pinwheel law

Status: Proved. The arguments are by hand; the finite closure, the edge test and the atlas are computed exactly (`check.py`, about 7
minutes).

Ticket `PINWHEEL-ATLAS-20261107-001A`, 2026-11-07.

## Standard statement

- **The tilings.** A pinwheel tiling is a tiling of the plane by right triangles with legs 1 : 2 in which every finite patch is
  congruent to part of a patch T_k, the result of applying Conway's cut k times to one triangle.
- **What is recorded.** Only the planar map (tile corners as vertices, pieces of tile sides between consecutive corners as edges,
  the counterclockwise order of edges at each vertex), and for each dart u → v its oriented label from
  `PINWHEEL-NATIVE-20261107-001B`: the side type and interval of the edge along the tile on its left and on its right, and whether
  the two sides run the same way.
- **The result.**
  - **A finite law.** Over all pinwheel tilings, the rooted neighbourhoods of radius 2 of darts take exactly 1,168 forms.
  - **The labels are read.** Each form carries exactly one oriented label. So in every pinwheel tiling, the label of every edge, and
    with it the eleven-label class of `PINWHEEL-NATIVE-20261107-001A`, is a function of the unlabelled planar map within radius 2.
  - **Radius 1 is not enough.** At radius 1 there are 198 forms, and 9 of them carry two different labels.

## Nearest known result

- **Collared tiles.** Closing collared tiles under a substitution is the standard way to describe a substitution tiling space by a
  finite complex (Anderson and Putnam, 1998). For the pinwheel, which does not force its border, this was done by Barge, Diamond,
  Hunton and Sadun (Ergodic Theory Dynam. Systems 30, 2010) and Frettlöh, Whitehead and Whittaker (J. Aust. Math. Soc., 2014).
- **The combinatorial rule.** Kenyon and Stephenson (Proc. Amer. Math. Soc. 147, 2019) treat pinwheel tiles as four-cornered
  combinatorial polygons. The corners are given to them; here the analogous labels are read from the bare map.
- **Recognizability.** Local recognition of supertiles is classical in the geometric setting (Solomyak, 1998, for tilings with
  translational finite local complexity; the pinwheel has finite local complexity only up to rotation).
- **Classification.** The method is known. The atlas, its count, and the theorem that labels are read within radius 2 from the
  unlabelled map are new as far as found.

## Terms

- **Tiles and the cut.** A tile is a triple (O, P, Q): the right angle, the end of the long leg, the end of the short leg. Conway's
  cut adds H = (4Q + P)/5, M = (O + P)/2, F₁ = (O + H)/2 and F₂ = (H + P)/2, and gives the children (H, O, Q), (F₁, M, O),
  (F₁, M, H), (F₂, H, M) and (F₂, P, M). These are affine combinations of O, P and Q, so the cut can be carried out in any affine
  frame.
- **A tile's frame.** The affine frame with O at the origin, Q at (1, 0) and P at (0, 1). A tile's handedness says whether this frame
  has the plane's orientation.
- **A collar.** A tile together with every tile that touches it (shares a point). Its key is the tile's handedness and the set of
  collar tiles written in the tile's frame. A collar is complete when its tiles cover a neighbourhood of the central tile.
- **Φ.** Cut every tile of a collar, and for each child of the central tile, take the children that touch it. This gives the keys of
  the five children's collars.
- **The rooted code** of a dart u → v at radius r: a breadth-first traversal from u, starting at v and turning counterclockwise,
  which records each discovered vertex's degree and its neighbours' discovery numbers out to graph distance r. It is the code of
  `PINWHEEL-NATIVE-20261107-001B` and uses no labels, coordinates or angles.

## Lemma 1 (touching children have touching parents)

If two tiles of the cut tiling touch, so do their parents, since each child lies inside its parent. So the collar of a child lies
inside the cut of its parent's collar, and Φ computes it. The cut is affine, so Φ depends only on the key. ∎

## Theorem 2 (finitely many collars)

- **The set.** The collars of all tiles of all patches T_k form a set S of 193 keys. Their first appearances are at levels 0–6
  (1, 5, 25, 69, 71, 18 and 4 keys).
- **Complete collars.** Exactly 108 of the keys are complete. They first appear at levels 2–6 and have 10 to 18 tiles. They come in
  54 mirror pairs (h, X) and (−h, X). The 7 keys without a mirror partner are partial collars on the boundary of the one triangle.

*Proof.* Start from the one-tile key of T₀. By Lemma 1, the collars of T_{k+1} are the images under Φ of the collars of T_k,
partial ones included, because a tile of T_k on the boundary has a partial collar and its children's collars lie in its cut. A
breadth-first search from the seed ends when every key's five images are already present. The set it finds is closed under Φ, so by
induction it contains every collar of every T_k. Completeness is tested exactly: at each corner of the central tile and at each tile
corner on its sides, every ray bounding a sector must be shared by exactly two of the tiles containing that point. ∎

## Lemma 3 (four cuts give enough room)

For each of the 108 complete keys, cut the whole collar four times. Every dart u → v whose tail u is a corner of a descendant of the
central tile then has u and v farther than 3 from the edge of the cut collar, in graph distance. So the radius-2 neighbourhoods of
these darts, and the full stars of their vertices, lie inside the cut collar. (Computed; with two cuts the test fails.) ∎

## Theorem 4 (the atlas)

Let A be the set of pairs (radius-2 code, oriented label) of the darts in Lemma 3, over all 108 complete keys.
- (a) **Every pinwheel tiling's darts are in A.**
- (b) **Every pair in A occurs** in some patch T_k, at a dart farther than 3 from its boundary.
- (c) **A has 1,168 codes, each with one label.**

*Proof.*
- (a) **Placing a patch deep inside.** Let d = u → v be a dart of a pinwheel tiling T, and B the patch of the tiles that meet a
  vertex within graph distance 3 of u.
  - **B is legal.** B is congruent to part of some T_k with k ≥ 4, or of its mirror image.
  - **A copy deep inside.** T₂ has interior tiles of both handednesses: tiles with complete collars, 3 of one and 1 of the other.
    Choose one, t, matching the congruence. The k-fold cut of t is a copy of T_k, or of its mirror image, inside T_{k+2}, by an
    orientation-preserving similarity. So B has a copy B′ there, with d′ the copy of d.
  - **The ancestor.** The tail of d′ is a corner of a tile c, and c's ancestor a four levels up descends from t (k ≥ 4). The tiles
    touching a descend from tiles touching t, and they cover a neighbourhood of a because t's collar covers a neighbourhood of t.
    So a's collar is complete, and its key is in S.
  - **The code is in A.** By Lemma 3, d′'s code and label are computed in the four-fold cut of a's collar, so they are in A.
  - **They are d's.** The vertices within distance 2 of u have full stars inside B. No tile outside B can put a corner on an edge
    between two of them, since both sides of such an edge are covered by tiles of B. So the code and the label of d′ are those of
    d.
- (b) **Each pair occurs.** A complete key occurs as an interior collar of some T_k. The darts of Lemma 3 are farther than 3 from
  the edge of the cut collar, which lies inside T_{k+4}, so they are interior darts of T_{k+4}.
- (c) **The count.** This is computed. ∎

**Corollary 5 (labels are read within radius 2 on every pinwheel tiling).**
- **The theorem.** In every pinwheel tiling, the oriented label of every edge is a function of the unlabelled planar map within
  radius 2 of the edge's tail. This upgrades `PINWHEEL-NATIVE-20261107-001B`, measured on patches, to every tiling.
- **What it means for the rule.** The eleven-label rule of `PINWHEEL-NATIVE-20261107-001A` can be run on the bare map: read each
  edge's label within radius 2, then cut. So regrowing the pinwheel needs no information beyond the map itself.

**Corollary 6 (T₇ already shows every form).** At radius 1 and 2, A equals the set of codes and labels of the interior darts of the
geometric patch T₇, computed independently from exact coordinates. So the measured counts of `PINWHEEL-NATIVE-20261107-001B`
(1,168 forms at level 7, and conflicts at radius 1) are the complete ones.

## The check

`check.py` verifies the following and writes `result.json` and `atlas.json`, which lists each radius-2 code with its label.
- **Closure.** The search closes at 193 keys, and every key's images are in the set.
- **Completeness.** 108 keys are complete, and they come in mirror pairs.
- **Room.** The edge test passes at four cuts.
- **Counts.** 1,168 codes with no conflict at radius 2; 198 codes with 9 conflicts at radius 1.
- **Independent cross-check.** Equality with the level-7 patch at both radii, labels included.
- **Controls.** Each must fail, and does:
  - two cuts (darts near the edge, an incomplete atlas);
  - a search stopped at level 3 (keys missing);
  - labels shuffled over a level-5 patch (conflicts).

## Nonclaims

- **The map, not yet the law.** The theorem reads labels from the planar map. That the law's allowed states determine the map rests
  on Whitney's theorem and on the 3-connectivity measured in `PINWHEEL-NATIVE-20261107-001B` on finite patches with an added outside
  vertex; it is not re-proved here for infinite tilings.
- **Frames are bookkeeping.** The affine frames and rational coordinates are used to enumerate collars. The atlas itself is
  combinatorial.
- **No forcing claimed.** The atlas says which radius-2 forms occur in pinwheel tilings. Whether a map with only these forms must be a
  pinwheel tiling is ticket B's question.
