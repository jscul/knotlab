# Labelled composition for the surviving one-bit decorations

Status: Proved. The reduction is by hand; every finite statement is computed exactly (`check.py`, about three minutes).

Ticket `ROUND-PRICE-20261108-001B`, 2026-11-08.

## Standard statement

- **The route.** A decorated local law forces the pinwheel if, in every tiling that obeys it, the tiles group into labelled parents
  that obey the same law, at every level: the tiling then has a full hierarchy (Theorem 1 below).
- **The test.** For the nine one-bit decorations (eighteen counting the exchange of labels) that excluded both crystals in ticket A,
  the first half of the route holds: every parent's label is forced. The second half fails at the pairwise level: for each, some
  labelled parent collars that are not collars of the law survive arc consistency.
- **A third crystal.** One of the nine (with its relabelling) admits a crystal of a third family, brick rows with diagonals of
  period 4, after three cuts. The other eight admit none of those 16 crystals within three cuts on the tori tried.

## Nearest known result

- **Recognizability and decorated matching rules.** Forcing a hierarchy by forcing unique composition at every level is the method
  of Mozes (1989), Goodman-Strauss (1998) and Radin (1994), with large alphabets.
- **The delta.** The test on one-bit decorations of the pinwheel, through the level-one law of `COLLAR-PLANE-20261108-001B`, was not
  found in prior work (no-overlap-found).

## Terms

As in ticket A: decorations s, their labelled collar laws L(s), the crystals. Also:
- **The level-one law L1 and its core.** The complete collars whose cut gives every child a pinwheel collar, and the 156 per
  handedness that survive arc consistency (`COLLAR-PLANE-20261108-001B`).
- **Q(s).** The labelled collars (Y, p), with Y in the core of L1 and p a labelling of Y's tiles, whose decorated cut gives every
  child of Y's central tile a labelled collar in L(s).

## Theorem 1 (the route)

Suppose that for a decoration s:
- (a) in every core collar Y, the five children of the central tile can carry only the labels s(0) or s(1) when every child's
  labelled collar is in L(s); and
- (b) every labelled collar of Q(s) that survives arc consistency on Q(s) is in L(s).

Then every tiling whose labelled collars all lie in L(s) has a full hierarchy, and its tiles, labels forgotten, form a pinwheel
tiling.

*Proof.*
- **Composition.** The tiling obeys the collar law, so it is the cut of a tiling T₁ whose collars lie in L1
  (`COLLAR-PLANE-20261108-001B`, Theorem 3). Those collars occur in a plane, so they survive arc consistency: they lie in the core.
- **Parent labels.** By (a), each parent's children carry s(p) for one p, since s(0) ≠ s(1). Give the parent the label p.
- **The parents obey the law.** The labelled collars of T₁ then lie in Q(s) and survive its arc consistency, since T₁ supports them.
  By (b) they lie in L(s).
- **Induction.** Repeat with T₁. The tiling is the k-fold cut of a tiling for every k, so each finite patch lies in a supertile of
  some level. A supertile whose collar is a pinwheel collar cuts into a pinwheel patch, so every patch is a pinwheel patch. ∎

## Theorem 2 (the computation)

For each of the nine decorations:
- **(a) holds.** In no core collar can the central tile's children avoid s(0) and s(1).
- **(b) fails.**

  | s(0) | s(1) | L(s) | Q(s) | Survivors in L(s) | Keys outside L(s) | Non-keys |
  | --- | --- | --- | --- | --- | --- | --- |
  | 0 0 0 0 1 | 1 0 0 1 0 | 710 | 967 | 355 | 66 | 88 |
  | 0 0 0 1 0 | 1 0 1 1 1 | 746 | 1,009 | 373 | 61 | 30 |
  | 0 0 1 1 1 | 1 0 0 1 0 | 878 | 1,013 | 439 | 87 | 31 |
  | 0 1 1 0 0 | 1 0 0 0 1 | 722 | 1,280 | 361 | 92 | 85 |
  | 1 0 0 0 0 | 0 0 1 0 1 | 754 | 1,100 | 377 | 125 | 50 |
  | 1 0 0 0 1 | 0 1 1 0 0 | 660 | 1,178 | 330 | 93 | 43 |
  | 1 0 1 0 1 | 0 0 0 0 0 | 894 | 994 | 447 | 81 | 36 |
  | 1 0 1 0 1 | 0 0 1 1 0 | 620 | 1,192 | 310 | 50 | 250 |
  | 1 0 1 1 0 | 0 0 1 0 1 | 616 | 1,272 | 308 | 50 | 248 |

- **The rhombus collar** survives with no labelling, as ticket A's exclusion of the rhombus crystal requires.
- **A third crystal.** The decoration s(0) = 1 0 0 0 1, s(1) = 0 1 1 0 0, and its relabelling, admit a crystal of the 16 brick-row
  planes with diagonals of period 4 (`COLLAR-PLANE-20261108-001C`'s larger tori) after three cuts: a periodic labelling on a torus of
  index 1. For the other eight, no periodic labelling of those crystals was found within three cuts on tori of index 1 or 2.

*Proof.* Computed: SAT for (a), with one formula per core collar and forbidden label vector; enumeration with pruning for Q(s); arc
consistency to a fixed point; periodic labellings as in ticket A. ∎

## What it says

- **Parent labels come free.** For these decorations one bit per tile is enough to read each parent's label from its children,
  everywhere.
- **The open step.** Whether the decorated parents must obey the law again is not settled by pairwise consistency. Either a deeper
  consistency test removes the survivors, and the decoration forces the pinwheel, or the survivors build a plane that escapes, as
  the period-4 brick rows do for one of the nine.
- **So.** Sixteen one-bit decorations, eight up to relabelling, remain candidates for forcing the pinwheel with one hidden bit per
  tile.

## The check

`check.py` computes everything above and writes `result.json`. Controls, each of which must hold:
- **The keys survive.** Every labelled key of each law lies in Q(s) and survives arc consistency.
- **The test can fail.** The constant decoration, which admits the rhombus crystal, keeps the rhombus collar and 204 non-key
  survivors, and it admits a period-4 brick crystal after one cut.
- **Symmetry.** Each law and each Q(s) is mirror symmetric.

## Nonclaims

- **Arc consistency only.** Survivors of a pairwise test need not occur in any plane; no decoration is shown to fail or to force.
- **Three crystal families.** Other periodic planes were not tested against the sixteen.
