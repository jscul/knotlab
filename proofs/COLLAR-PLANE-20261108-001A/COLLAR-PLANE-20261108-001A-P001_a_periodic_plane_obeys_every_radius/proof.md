# A periodic plane obeys every undecorated local law of the pinwheel

Status: Proved. The arguments are by hand; the witness, the cut's closure on collars, the radius-2 check and the controls are
computed exactly (`check.py`, about ten seconds).

Ticket `COLLAR-PLANE-20261108-001A`, 2026-11-08.

## Standard statement

- **The tilings.** A pinwheel tiling is a tiling of the plane by right triangles with legs 1 and 2 in which every finite patch is
  congruent to part of a patch T_k, the result of applying Conway's cut k times to one triangle (Radin 1994). A tile's *collar* is
  the tile with every tile that touches it.
- **The result.** Cut once, the lattice tiling by the rhombus that four tiles make around a common right angle is a periodic tiling
  in which every collar is congruent to a collar of a pinwheel tiling. Its further cuts are periodic too, and for every radius r one
  of them has every patch of radius r congruent, after scaling, to a patch of a pinwheel tiling.
- **So.** No finite list of undecorated patches, of any radius, that every pinwheel tiling obeys forces a tiling to be a pinwheel
  tiling, or even non-periodic. The pinwheel has no undecorated local rules in Levitov's sense; its matching rules need decorations.

## Nearest known result

- **Matching rules.** Radin (Annals of Mathematics 139, 1994) forced the pinwheel tilings with decorated tiles. Goodman-Strauss
  (Annals of Mathematics 147, 1998) gave decorated matching rules for substitution tilings in general, after Mozes (1989).
- **Undecorated local rules.** Levitov (Commun. Math. Phys. 119, 1988) asked which tilings are forced by an atlas of undecorated
  patches of some radius; Penrose-type rhombus tilings have such rules only in a few symmetries, and Socolar's weak rules (1990)
  cover more.
- **The pinwheel's collars.** Collared pinwheel tiles describe its tiling space as an inverse limit (Barge, Diamond, Hunton and
  Sadun 2010; Frettlöh, Whitehead and Whittaker 2014). `PINWHEEL-ATLAS-20261107-001A` lists the 108 complete collars and the 1,168
  radius-2 dart codes.
- **The argument's shape.** Cutting a periodic tiling that obeys the small-radius law to defeat every larger radius is the
  standard reason local rules can fail for substitution tilings.
- **Classification.** The method is known. The witness, and the conclusion that no undecorated local law of the pinwheel forces
  aperiodicity, were not found in a bounded search (no-overlap-found, not a novelty claim). Folklore risk is moderate.

## Terms

- **Tiles and the cut.** A tile is a triple (O, P, Q): the right angle, the end of the long leg, the end of the short leg. Conway's
  cut adds H = (4Q + P)/5, M = (O + P)/2, F₁ = (O + H)/2 and F₂ = (H + P)/2, and gives the children (H, O, Q), (F₁, M, O),
  (F₁, M, H), (F₂, H, M) and (F₂, P, M), each similar to the parent with ratio 1/√5.
- **Keys.** A collar's key is the tile's handedness and the set of collar tiles written in the tile's own affine frame (O at 0, Q at
  (1, 0), P at (0, 1)). The 108 complete keys of `PINWHEEL-ATLAS-20261107-001A` (Theorem 2 there) are the collars of tiles of all
  pinwheel tilings: every collar of a pinwheel tiling is one of them, and each occurs as the collar of an interior tile of some T_k.
- **Collar-legal.** A tiling by congruent copies of one tile is collar-legal when every tile's key is one of the 108.
- **Tile radius.** The patch of tile radius r around a tile d: the tiles reachable from d by at most r steps between touching tiles.
- **The rhombus lattice R.** The tiles (O, P, Q) = ((0, 0), (0, ±2), (±1, 0)), four right triangles with legs 1 and 2 around the
  origin, make a rhombus with diagonals 2 and 4. Its translates by the lattice Λ = Z(1, 2) + Z(1, −2) tile the plane. R_k is the
  k-fold cut of R.

## Lemma 1 (the cut keeps collar-legality)

The cut maps each complete key to five complete keys. So the cut of a collar-legal tiling is collar-legal.

*Proof.* Touching children have touching parents, so a child's collar lies in the cut of its parent's collar, and Φ (cut the collar
and take each child's collar) is a map on keys (Lemma 1 of `PINWHEEL-ATLAS-20261107-001A`). The closed set of 193 keys contains the
five images of each of its keys (Theorem 2 there). A child of a tile whose collar covers a neighbourhood of it has a collar covering
a neighbourhood of the child, so the images of a complete key are complete. The check confirms all 108 × 5 images directly. ∎

## Theorem 2 (the witness)

R_1 is a tiling of the plane, invariant under Λ, with 20 tiles in each period, and every tile's key is one of the 108 complete keys.
Its tiles use 10 of them.

*Proof.* R is a tiling and the cut of a tiling is a tiling. Translations commute with the cut, so R_1 is invariant under Λ. The
central rhombus is a fundamental domain of Λ, so its cut, 20 tiles, contains one tile from each orbit, and a tile's key is invariant
under translation. The check computes the key of each of the 20 tiles exactly, from a patch of R_1 holding every tile that touches
them, with a spatial hash and again by brute force; all 20 are complete keys. ∎

R itself is not collar-legal: four right angles meet at the centre of each rhombus, and the check finds its collar outside the 108.

## Theorem 3 (every radius)

Let w be the least distance, over the 108 complete keys, from the central tile to the outside of the union of its collar (tiles with
legs 1 and 2). Then w > 0; computed in floating point it is 0.447214, 1/√5 to six places. Let T be collar-legal, let r ≥ 1, and let k satisfy
(r + 1) √5 · 5^(−k/2) < w. Then every patch of tile radius r of the k-fold cut of T is congruent, after scaling by 5^(k/2), to a
patch of a pinwheel tiling.

*Proof.* Each complete key covers a neighbourhood of its central tile, so each has positive width, and there are finitely many.
Let d be a tile of the k-fold cut and c the tile of T that contains it. A tile reached from d in at most r steps between touching
tiles has all its points within r times the tile diameter √5 · 5^(−k/2) of d, hence of c, so it lies inside the union U of c's
collar. In U the k-fold cut of T consists of the k-fold descendants of the collar's tiles, so the patch around d is part of the
k-fold cut of c's collar K. K is the collar of an interior tile of some T_m, so the k-fold cut of K is part of T_(m+k). ∎

The check computes the least k: 3 for r = 1, 4 for r = 2 or 3, 5 for r = 5 or 10, 8 for r = 100. The bound is not sharp. The
1,168-code radius-2 dart atlas of `PINWHEEL-ATLAS-20261107-001A` is passed already by R_2: all 4,048 interior darts tested have
their code in the atlas.

**Corollary 4 (no undecorated local law of the pinwheel forces aperiodicity).**
- **Periodic planes at every radius.** For every r the tiling R_k with k as in Theorem 3 is periodic (lattice Λ, 4 · 5^k tiles
  per period) and every patch of tile radius r in it is a pinwheel patch.
- **The atlas's law.** R_2 (100 tiles per period) obeys the pinwheel's radius-2 law: the 1,168 forms of
  `PINWHEEL-ATLAS-20261107-001A` (computed).
- **So.** A local law that lists pinwheel patches of any fixed radius, without decorations, also allows a periodic plane. Radin's
  decorations, or some other hidden information, are needed to force the pinwheel.

## The check

`check.py` verifies, exactly, and writes `result.json`:
- **The law.** The closure has 193 keys, 108 complete. The cut maps every complete key to five complete keys.
- **The witness.** R_1's 20 fundamental tiles all have complete keys (hash and brute force; 10 distinct keys). R_1 is invariant
  under Λ. R_2's 100 fundamental tiles all have complete keys (42 distinct).
- **The atlas.** All 4,048 interior darts of a patch of R_2 have their radius-2 code among the 1,168.
- **The width.** w = 0.447214 > 0 over all 108 keys (floating point; only its sign is used in the proof), and the least k
  for r = 1, 2, 3, 5, 10, 100.
- **Controls.** Each must fail, and does:
  - R uncut has a collar outside the 108;
  - the rectangle lattice (a tile and its half-turn across the hypotenuse, translated) cut once and cut twice has collars outside
    the 108;
  - R_1 breaks the radius-2 atlas (90 of 232 interior darts);
  - R_1 with one rectangle of two tiles flipped to its other diagonal, still a tiling, has collars outside the 108 (11 of the 11
    tiles at the flip).

## Nonclaims

- **Not the pinwheel.** R_k is not a pinwheel tiling: it is periodic, so it has finitely many tile orientations, while every
  pinwheel tiling has infinitely many. It obeys the pinwheel's local laws without being one of its tilings.
- **Decorated rules unaffected.** Radin's decorated matching rules still force the pinwheel; the result concerns undecorated laws.
- **Least period open.** Whether a collar-legal plane has fewer than 20 tiles per period is not decided here.
