# One hidden bit per tile against the pinwheel's crystals

Status: Proved. The lemmas are by hand; the census is an exact computation (`check.py` with `decor_lib.py`, about six minutes with
16 workers).

Ticket `ROUND-PRICE-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** Decorate the pinwheel tilings with hidden labels and forbid, by a finite list of allowed labelled patches, every
  labelled patch that does not occur in a decorated pinwheel tiling. Does the list force the tiles, labels forgotten, to form a
  pinwheel tiling, or at least a non-periodic one?
- **Labels read from the tiling do not help.** If each label is a function of a bounded window of the undecorated tiling, a periodic
  tiling still obeys the list (Lemma 1).
- **Decorated substitutions.** A decorated substitution gives each child of Conway's cut a label fixed by its parent's label and
  its child index. Whether its collar law admits a periodic plane does not depend on the radius of the list (Lemma 2).
- **One bit.** For each of the 1,024 decorated substitutions on two labels, the census decides at which levels the cut rhombus and
  brick crystals of `COLLAR-PLANE-20261108-001` carry an obeying labelling.

## Nearest known result

- **Decorated matching rules.** Radin (Annals of Mathematics 139, 1994) forced the pinwheel with decorated tiles; Mozes (1989) and
  Goodman-Strauss (Annals of Mathematics 147, 1998) force substitution tilings in general, with decorations that are decorated
  substitutions in this sense and alphabets far larger than two labels.
- **Small aperiodic sets.** The least aperiodic Wang tile set has 11 tiles (Jeandel and Rao, 2021). The least decoration that forces
  a given substitution tiling, such as the pinwheel, was not found in a bounded search.
- **The delta.** Lemma 1 is the standard reason decorations must carry non-local information. The census, on the pinwheel and one
  bit, is new as far as found (no-overlap-found).

## Terms

- **Pinwheel, collars, keys, crystals.** As in `COLLAR-PLANE-20261108-001A`. R_k is the k-fold cut of the rhombus lattice; it is
  collar-legal from k = 1. The brick crystal is the k-fold cut of brick rows of 1 × 2 rectangles whose diagonals alternate along
  each row; it is collar-legal from k = 2 (`COLLAR-PLANE-20261108-001C`).
- **A decorated substitution** on labels {0, 1} is a pair s = (s(0), s(1)) of 5-tuples. A tile with label a gives its child i (in
  the order of `atlas_lib.cut`) the label s(a)_i.
- **A decorated pinwheel tiling** is a pinwheel tiling with a hierarchy in which every tile's label is s of its parent's label at its
  child index.
- **The labelled collar law** L(s) is the set of complete labelled collars of decorated pinwheel tilings. It is computed as the
  closure of labelled collars under the labelled cut, from one labelled tile of each handedness and label.
- **Admits, excludes.** A crystal admits s at level k when some labelling of its tiles gives every tile a labelled collar in L(s),
  and excludes it otherwise.

## Lemma 1 (labels read from the tiling add nothing)

Let λ label each tile of each pinwheel tiling by a function of its patch of tile radius ρ, up to congruence, and let r ≥ 1. Then for
k ≥ k(r + ρ) of `COLLAR-PLANE-20261108-001A` (Theorem 3), the crystal R_k, labelled by λ applied to its own patches, has every
labelled patch of tile radius r equal to one of a λ-labelled pinwheel tiling. So no finite list of λ-labelled patches forces
aperiodicity.

*Proof.* Every patch of tile radius r + ρ of R_k is a pinwheel patch, so λ is defined on R_k's tiles, and each tile's label within a
patch of radius r is read from the surrounding patch of radius r + ρ. That patch occurs in a pinwheel tiling, where λ gives the
same labels. ∎

**Examples.** Child indices are read from the collar (`COLLAR-PLANE-20261108-001B`, Lemma 1). So is any finite part of a tile's
address in the hierarchy, its parent's child index, its grandparent's, and so on, from windows growing with the depth. A decoration
that forces roundness must carry information that no bounded window determines.

## Lemma 2 (the radius does not matter)

If the collar law L(s) admits R_j, then for every r the law of s at tile radius r admits R_(j + k(r)).

*Proof.* Cut an obeying labelling of R_j by s: each child gets s of its parent's label. The cut of a decorated pinwheel tiling is a
decorated pinwheel tiling, and L(s) is closed under the labelled cut. So by the argument of Theorem 3 of
`COLLAR-PLANE-20261108-001A`, after k(r) cuts every labelled patch of tile radius r lies in the labelled cut of one labelled collar
of L(s), which occurs in a decorated pinwheel tiling. ∎

In particular, admitted at k implies admitted at every larger k (r = 1). So each decoration has a first admitted level, or excludes
the crystal at every level.

## Theorem 3 (the census)

Of the 1,024 decorated substitutions on two labels:
- **Most admit the rhombus crystal at once.** 172 admit R_1, 792 first admit R_2, and 30 first admit R_3. Each admission is a
  periodic labelling on a torus of index 1, 2 or 4, checked tile by tile.
- **30 exclude R_1, R_2 and R_3.** Of these:
  - 4 admit R_4;
  - 8 exclude R_4 and admit the brick crystal, at level 2 (4 of them), 3 (2) or 4 (2);
  - 18 exclude R_4 and the brick crystal at levels 2, 3 and 4.
- **So.** 1,006 decorations admit a periodic plane, and by Lemma 2 their law of any radius does too. The other 18, nine up to
  exchanging the labels, exclude both crystals at every level tested. In each of the 18, s(0) and s(1) differ at children 0 and 4,
  the children at the parent's corners Q and P. The nine are:

  | s(0) | s(1) |
  | --- | --- |
  | 0 0 0 0 1 | 1 0 0 1 0 |
  | 0 0 0 1 0 | 1 0 1 1 1 |
  | 0 0 1 1 1 | 1 0 0 1 0 |
  | 0 1 1 0 0 | 1 0 0 0 1 |
  | 1 0 0 0 0 | 0 0 1 0 1 |
  | 1 0 0 0 1 | 0 1 1 0 0 |
  | 1 0 1 0 1 | 0 0 0 0 0 |
  | 1 0 1 0 1 | 0 0 1 1 0 |
  | 1 0 1 1 0 | 0 0 1 0 1 |

*Proof.* Computed (`census.json` lists every decoration's verdicts). An admission is a satisfying assignment that the check
verifies directly. An exclusion is an unsatisfiable formula: no labelling of the box's descendants gives every constrained tile a
labelled collar of the law, and a labelling of the crystal would restrict to one. ∎

**Which law.** L(s) lists the labelled collars of interior tiles of decorated supertiles, that is of the k-fold cuts of one
labelled tile, for every top label and handedness. A decorated pinwheel tiling is one whose finite labelled patches all lie in
such supertiles, so it obeys L(s). With two labels nothing is listed in vain: a label that is never a child's label appears only on
a supertile's top tile, whose collar is never complete, and every other label lies on a cycle of the label graph (a → s(a)_i), so it
recurs at every level.

## What it says

- **One bit read as a decoration usually fails.** Most one-bit decorations admit the rhombus crystal after one or two cuts, so
  their laws, at every radius, allow a periodic plane.
- **But not all.** Eighteen exclude both crystals as far as tested. Whether one of them forces the pinwheel is the next question: it
  would follow if the decorated law forced composition at every level, as ticket B of `COLLAR-PLANE-20261108-001` forced it once.

## The check

`check.py` (with `decor_lib.py`) computes, exactly:
- **The laws.** The labelled collar law of each decoration, through the skeleton of the cut on the 200 collar types of both
  handednesses (108 complete).
- **Admitted.** A periodic labelling of R_k on a torus of index 1, 2 or 4 over the rhombus lattice, found by CaDiCaL and checked
  tile by tile.
- **Excluded.** No obeying labelling of the descendants of the cells with |i|, |j| ≤ 1, whose collars lie in |i|, |j| ≤ 2: an
  unsatisfiable formula.
- **Controls.** Relabelling 0 and 1 gives the same verdicts; the constant decorations admit R_1; an empty law is unsatisfiable and a
  law allowing everything is satisfiable on the box; the labelled collars of genuine decorated level-4 pinwheel patches, computed
  from coordinates, lie in the law.

## Nonclaims

- **Exclusion is level by level.** The 18 exclude the two crystals at the levels tested (rhombus 1 to 4, brick 2 to 4), not proved
  at every level, and other periodic planes were not tested.
- **One class of decorations.** Decorations whose children's labels depend on more than the parent's label and the child index, or
  labels on edges as in Radin's rules, are not covered.
