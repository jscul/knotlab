# A note: the pinwheel tilings have no undecorated local rules

Status: Proved (a result conversion: the note restates proved results for outside readers, with an independent replay).

Ticket `ONE-BIT-20261108-001C`, 2026-11-08.

## Standard statement

The note (`note/pinwheel_local_rules.tex`, 5 pages, published at `notes/pinwheel-local-rules/` in knotlab) proves, for readers
outside the program:
- **Theorem 1.** For every radius r there is a periodic tiling of the plane by the pinwheel triangle all of whose patches of tile
  radius r are pinwheel patches; so the pinwheel tilings have no undecorated local rules of any radius.
- **The witness.** The lattice tiling by the rhombus of four triangles around a common right angle, cut once, has every collar a
  pinwheel collar (20 tiles per period).
- **One level.** The collar rule forces one level of composition and no more.
- **Hidden labels.** Labels read from a bounded window never help; of the 1,024 decorated substitutions on one bit per tile, 1,022
  admit a periodic plane, and one (with its relabelling) is open.

## Nearest known result

Radin (1994) forced the pinwheel with decorated matching rules; Mozes (1989) and Goodman-Strauss (1998) did so for substitution
tilings generally; Levitov (1988) framed undecorated local rules. The note's results are those of `COLLAR-PLANE-20261108-001`,
`ROUND-PRICE-20261108-001` and `ONE-BIT-20261108-001`, with their novelty labels (no-overlap-found for the witness, the census and the
open decoration).

## The check

`check.py` runs `replay.py`, which recomputes with its own code (standard library, exact arithmetic, an angle-count completeness test
in place of the original sector test) the 193 collars and 108 complete ones, the cut's closure on them, and the witness after one and
two cuts, with the uncut rhombus lattice and the once-cut rectangle lattice as controls that must fail. It also checks that the
note's files here equal the published copy and that every record folder the note cites exists.

## Nonclaims

- **No new mathematics.** Every statement is proved in the cited records; the note restates them.
- **Not reviewed.** No human expert has reviewed the note.
