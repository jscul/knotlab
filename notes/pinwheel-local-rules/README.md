# The pinwheel tilings have no undecorated local rules

[PDF](pinwheel_local_rules.pdf) · [TeX source](pinwheel_local_rules.tex) ·
[replay.py](replay.py) · 5 pages · draft of 8 November 2026

**Results.** Radin forced the pinwheel tilings with decorated matching rules.
The decorations cannot be dropped.

- **A periodic plane obeys the collar rule.** Four triangles around a common
  right angle make a rhombus. The lattice tiling by these rhombi, cut once by
  Conway's subdivision, has every collar (a tile with all the tiles it touches)
  equal to a collar of a pinwheel tiling.
- **Every radius fails.** Each further cut defeats a larger radius, so for every
  r a periodic tiling has all its patches of radius r in pinwheel tilings.
- **One level is forced.** The collar rule forces one level of the hierarchy,
  and no more.
- **Hidden labels.** Labels read from a bounded window of the tiling never help.
  Of the 1,024 decorated substitutions on one bit per tile, 1,022 still admit a
  periodic plane. One (with its relabelling) is open.

**The intuition.** A cut hides a crystal's seams under the pinwheel's own
structure, one level per cut, so no fixed window can see them. Roundness has to
be paid for with hidden information that no window of the tiling holds, in the
plane as on the sphere.

**Check it.** `python3 replay.py` (standard library only, about half a minute)
rebuilds the 193 collars from one triangle with its own code, decides
completeness by an angle count, and checks the witness after one and two cuts,
with two controls that must fail.

**Records.** [Collar plane](../../research/COLLAR-PLANE-20261108-001/collar_plane.md) ·
[price of roundness](../../research/ROUND-PRICE-20261108-001/round_price.md) ·
[one bit per tile](../../research/ONE-BIT-20261108-001/one_bit.md)
