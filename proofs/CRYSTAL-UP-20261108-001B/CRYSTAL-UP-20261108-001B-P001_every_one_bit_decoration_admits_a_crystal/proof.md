# Every one-bit decoration of the pinwheel admits a crystal

Status: Proved. Finite certificates, each checked by independent code (`check.py`: standard library only, built on the knotlab
note's standalone replay, apart from the pipeline that found them); the census it completes is `ROUND-PRICE-20261108-001`'s.

Ticket `CRYSTAL-UP-20261108-001B`, 2026-11-08.

## Standard statement

- **One bit per tile.** A one-bit decoration labels the pinwheel's tiles 0 or 1 through Conway's cut: a tile labelled a gives its
  child m the label s(a)_m. Its law lists the labelled collars of decorated supertiles. There are 1,024 decorations
  s = (s(0), s(1)). Exchanging every label turns a decorated tiling for s into one for s~, with s~(b) = 1 − s(1 − b).
- **Theorem.** For every one of the 1,024 decorations some periodic plane obeys its law, and so, after further cuts, obeys its law
  at every radius. One hidden bit per tile, placed by a decorated substitution, never forces the pinwheel.

## Nearest known result

Goodman-Strauss (1998) shows that every substitution tiling of this kind, the pinwheel included, is forced by some decoration, and
Radin (1994) gave decorated matching rules for the pinwheel; neither bounds the number of labels from below. The exhaustive answer
for two labels was not found in prior work (no-overlap-found).

## Terms

- **Crystal.** A periodic plane, here with a periodic labelling.
- **Obeys the law.** Every labelled collar (a tile with every tile touching it, in its own frame, with labels) is one of the law's.
- **The law.** The closure of the four one-tile labelled collars (either hand, either label) under the labelled cut, kept when
  complete by the angle count; the check computes it on its own, 620 labelled collars for s = 10101 / 00110.

## Lemma 1 (the radius does not matter)

If a crystal obeys the collar law of s, then for every radius r a further cut of it obeys the law of s at tile radius r.

*Proof.* This is `ROUND-PRICE-20261108-001A`'s Lemma 2, whose proof uses nothing about the rhombus lattice. Cut the obeying
labelling by s: the cut of a decorated pinwheel tiling is one, so the collar law is closed under the labelled cut. After enough cuts
every labelled patch of tile radius r lies inside the labelled cut of one labelled collar of the law, which occurs in a decorated
pinwheel tiling. ∎

## Theorem 2 (the census)

- **1,008 decorations** admit the cut rhombus lattice, cut brick rows or brick rows with period-4 diagonals, with periodic
  labellings: the exact census of `ROUND-PRICE-20261108-001A` and `-001B`.
- **The other sixteen**, eight classes up to exchanging labels, each have a certificate here:
  - **Seven classes:** the escapes of `ONE-BIT-20261108-001B`, one per class, exported from its recorded results as a domino-torus
    plane cut two to four times with the periodic labelling found there. The check confirms that each is a tiling and that all its
    labelled collars lie in the law, and with every label exchanged in the relabelled decoration's law.
  - **s = 10101 / 00110 and its relabelling 11001 / 01010:** the 26 crystals found by `CRYSTAL-UP-20261108-001A-E002`
    (`crystal.json`), 8 to 40 tiles per period. The smallest, X, has lattice (1, 2), (−16/5, 8/5), the short leg being 1. Four of
    its tiles have their legs along the axes and four are turned by arctan(4/3), the angle of the 3-4-5 triangle and twice the
    pinwheel's angle arctan(1/2); every crystal found splits the same way, half and half. Four of X's eight collars are not
    pinwheel collars, so X obeys no pinwheel law. Cut once with the labels s sets from X's labels, all 40 labelled collars of a
    period lie in the law; cut twice, all 200 do. Every one of the 26 cut once obeys the law, the six with 20 tiles cut twice as
    well, and with every label exchanged each cut once obeys the law of 11001 / 01010.

With Lemma 1 every decoration admits a crystal at every radius. ∎

## What it says

- **One bit per tile never suffices** as a decorated substitution: the plane's price of roundness, measured this way, is more than
  one hidden bit per tile (A35). Two bits (backlog B8) is the next count.
- **The last escapes are a new kind of crystal.** The earlier escapes were cuts of domino tilings, whose tiles all have their legs
  along the axes. These mix two orientations, a turn of twice the pinwheel angle apart, and their non-pinwheel collars disappear
  after one cut.

## The check

`check.py` reads `crystal.json` and `escapes.json` and writes `result.json`; `make_certificates.py` records how both were made
(provenance only). Controls, each of which held: the undecorated closure has 193 collars, 108 complete (the replay's own counts);
the law is the same from each one-tile seed, and every collar in it is a pinwheel collar; X uncut does not obey the law; flipping
any one of X's eight labels breaks the cut.

## Nonclaims

- **Not about other measures.** Labels on edges, or labels that depend on a parent's neighbours, are not decorated substitutions in
  this sense (A35's challenge).
- **Not a lower bound on decorations in general.** Two or more labels per tile are not tested here.
