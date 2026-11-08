# The collar law forces one level of composition

Status: Proved. The arguments are by hand; every finite case is computed exactly (`check.py`, about two minutes with 22 workers).

Ticket `COLLAR-PLANE-20261108-001B`, 2026-11-08.

## Standard statement

- **The setting.** Tile the plane with right triangles with legs 1 and 2 so that every tile's collar (the tile with every tile that
  touches it) is congruent to a collar of a pinwheel tiling.
- **The result.** Such a tiling is always the Conway cut of a tiling by triangles √5 times larger, and that larger tiling is found
  locally: each collar names its tile's parent, and touching tiles that should be siblings name the same parent.
- **Where it stops.** The larger tiling need not obey the collar law. Its collars obey a weaker law, the level-one law, which is
  computed exactly: 1,264 collars per handedness, of which 54 are pinwheel collars. Only 156 of them can sit in a plane by
  arc consistency.

## Nearest known result

- **Recognizability.** For self-similar tilings with finite local complexity, every tiling in the substitution's own space
  decomposes uniquely into supertiles (Solomyak 1998). Unique composition at every level is the usual proof of aperiodicity.
- **The pinwheel.** It has finite local complexity only up to rotation; its collared tiles are those of Barge, Diamond, Hunton and
  Sadun (2010) and `PINWHEEL-ATLAS-20261107-001A`.
- **The delta.** Here composition is forced by the undecorated collar law alone, for every tiling that obeys it rather than for the
  substitution's own tilings, and only one level deep. The level-one law it leaves behind is new as far as found (no-overlap-found).

## Terms

- **Keys and claims.** A key is a collar's handedness with its tiles written in the central tile's affine frame. The 108 complete
  keys of `PINWHEEL-ATLAS-20261107-001A` each arise as the collar of child c of some parent under the cut. The preimages of a key
  under Φ (cut a collar, take each child's collar) are computed by `legality.py` of `GROWTH-LAW-20261107-001B`. A key *names* the
  child index c and the parent triangle a when every preimage gives the same c and a.
- **Collar-legal.** Every tile's key is one of the 108.
- **Compatible collars.** Two collars, placed at two tiles, could both be collars in one tiling when:
  - each tile is in the other's collar (they touch);
  - every tile of either collar that touches the other tile is in the other's collar;
  - no two distinct tiles of the two collars overlap.
- **Consistent.** A placed tile is consistent when some complete key of its handedness contains its current collar and the key's
  other tiles overlap no placed tile (the growth engine's test). In a collar-legal tiling every finite set of its tiles is
  consistent.
- **L1.** A complete collar X around a triangle is in the level-one law when, after cutting X, each of the central triangle's five
  children has a complete pinwheel key.

## Lemma 1 (each collar names its parent)

Each of the 108 complete keys names exactly one child index and one parent triangle. (Computed from the inverse of Φ on the closed
set of 193 keys.)

## Lemma 2 (touching siblings agree)

Let K be a complete key naming child c of parent a, and let s be another child of a that touches the central tile. Then s is a tile
of K. For every complete key Y of s's handedness, placed at s and compatible with K:
- **Either** Y names the same parent a, with s as child j;
- **or** placing the tiles of K and of Y together leaves some tile inconsistent.

*Proof.* K is the collar of child c in a cut collar, so it holds every child of a that touches child c. The rest is computed:
- **The pairs.** There are 956 compatible pairs: 478 with K of handedness +1, and their 478 mirrors.
- **Agreement.** In 888 of them Y names the same parent.
- **Disagreement.** In each of the other 68 (34 and their 34 mirrors), the check places K and Y and finds a tile with no consistent
  completion.
- **Mirrors.** The law is mirror symmetric, so the mirror pairs behave alike. ∎

## Theorem 3 (one level of composition is forced)

Every collar-legal tiling T of the plane is the cut of a tiling T₁ by triangles √5 times larger. T₁ is determined by T: each
tile's parent is the one its key names. Every collar of T₁ lies in L1.

*Proof.*
- **The parents.** Each tile t names a parent a(t) (Lemma 1).
- **Siblings agree.** If t is child c of a(t), each child of a(t) that touches t is a tile of T: it is in t's collar, which is
  t's key. Its key is compatible with t's, since both are collars in T, and T's tiles are all consistent. So by Lemma 2 it names the
  same parent.
- **All five children.** The five children of a triangle touch in a connected graph (computed). So all five are tiles of T, and
  all name a(t).
- **A tiling.** Each tile has one parent, and each parent is the union of its five children. So the parents have disjoint
  interiors, cover the plane, and their cut is T.
- **The level-one law.** A child's collar lies in the cut of its parent's collar (Lemma 1 of `PINWHEEL-ATLAS-20261107-001A`). So
  each collar of T₁ cuts into five complete keys, which is L1. ∎

The composition commutes with every symmetry of T. So if T is periodic, T₁ is periodic with the same translations and one fifth as
many tiles in each period.

## Theorem 4 (the level-one law)

- **Its size.** For handedness +1, L1 has exactly 1,264 complete collars. 54 of them are pinwheel keys and 1,210 are not.
  Handedness −1 gives the same sets.
- **Its core.** A collar in a plane all of whose collars lie in L1 must, at every neighbour, have a compatible L1 collar that can
  itself occur. Iterating this arc consistency leaves 156 collars: the 54 keys and 102 others. A radius-2 test, which asks for
  compatible L1 collars at all neighbours at once that are pairwise compatible, removes none.
- **The rhombus lattice.** The collar of a tile of the rhombus lattice (`COLLAR-PLANE-20261108-001A`: four tiles around a common
  right angle, translated) is one of the 102. So the periodic collar-legal plane of ticket A is the cut of a plane whose collars
  are all one of L1's non-key collars, and composition stops there.

*Proof.*
- **The children's keys.** Each of the five children of the central triangle needs a complete key consistent with the triangle's
  own cut. The candidates are 22, 7, 5, 5 and 20, and 124 assignments are pairwise compatible.
- **The neighbours.** Every tile of these keys outside the triangle is a child of a neighbouring triangle, one of 5 possible
  parents. The check tries all of them, keeping parents that overlap nothing and whose children touching the central triangle's
  children lie in those children's keys, and keeps the complete collars.
- **Every collar is found.** Every collar in L1 arises this way: the children's collars are keys, and the neighbours are their
  outside tiles' parents.
- **The core.** Arc consistency only removes collars that cannot occur. ∎

## Corollary 5 (the patches that left the pinwheel)

- **The patches.** `GROWTH-LAW-20261107-001B`'s four forced-first runs grew 543 to 1,005 tiles of collar-legal patches that are
  not pinwheel patches (data: `research/GROWTH-LAW-20261107-001/stress_test_growth.json`).
- **They compose.** In each, the parents named by the complete tiles never conflict, as Theorem 3 requires inside a plane.
- **The defect is one level up.** Their level-one tiles, the parents all five of whose children name them, have complete collars
  of which 4, 22, 39 and 7 are not pinwheel keys. These are 45 distinct collars, all in L1.

## The check

`check.py` computes every finite statement above exactly and writes `result.json`. It also writes `level_one_law.json`, the 1,264
collars with their key and core flags. Controls, each of which must fail where the claim succeeds, and does:
- **Compatibility alone is not enough.** 34 compatible sibling pairs disagree, so the consistency step is needed.
- **The consistency test can pass.** A genuine sibling pair from the level-5 patch places with every tile consistent.
- **The enumeration and the core keep the pinwheel.** L1 contains all 54 keys of handedness +1, and all 54 survive the core.
- **The patches do leave the pinwheel.** Their level-one tiles include non-key collars.

## Nonclaims

- **The core can be smaller.** The 102 non-key core collars pass arc consistency and the radius-2 test. That does not show each
  occurs in a plane; the rhombus lattice's does.
- **One level only.** Composition is not shown to be forced at level two. The rhombus lattice shows it cannot be in general.
