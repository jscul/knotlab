# The first full-table support ambiguity within the binary-third family

At width 32, two lawful binary-third histories have different final junction supports on the same names. The identity preserves all 496 exact pair readings. Both current triple menus are empty. Width 32 is the minimum for ambiguity of the actual supports under a full-table bijection between two histories in this family. [Exact replay and table](empty_witness.json)

## The two joins

The common prefix is the first width-30 record with six loose distinctions split into two legal complementary triples. Its three loose holders are junctions 9, 11 and 12, numbered from zero. They hold \(\{22,23\}\), \(\{26,27\}\) and \(\{28,29\}\), respectively. Their pair witnesses are junctions 8, 6 and 10 for the pairs \((9,11),(9,12),(11,12)\). There is no witness common to all three. Each history takes one loose distinction from every holder and makes the same two fresh distinctions, 30 and 31. [Prefix search](frontier.json) · [Literal history](empty_witness.json)

| History | Final inputs | Final even-parity support | Loose distinctions after the join |
| --- | --- | --- | --- |
| First | \(22,26,28\) | \(22,26,28,30,31\) | \(23,27,29,30,31\) |
| Second | \(23,27,29\) | \(23,27,29,30,31\) | \(22,26,28,30,31\) |

The final supports differ by the six loose distinctions of the prefix. That word is the sum of the prefix's parity supports, since every shared distinction occurs twice. The two final supports therefore generate the same extension of the prefix equation space. Its rank is 14 on both sides. The checker independently enumerates the equation spaces and all minimal supports by the connected-cut and parity-span methods, then compares every pair entry. [Replay checker](empty_witness.py)

After either join, the three old loose holders share the new junction as a common witness, so their remaining distinctions cannot form a legal triple. The new junction has just two loose outputs. Its color is opposite to those of the old loose holders, which excludes mixing these choices in a parent group. The same table also admits the support isomorphism \((22\ 23)(26\ 27)(28\ 29)\). The identity gives the ambiguity of supports on the supplied names. [Exact permutations and menus](empty_witness.json)

## Minimum within the family

A completed binary-third history has even width \(2n+4\), with first possible width 12. With at most one shrinking join, the short-shore transfer argument determines every junction equation through size five, so an equal table at a fixed width gives the same equation space. The augmented stars are then intrinsic. There are at least seven loose distinctions, and the exterior star is the only augmented support larger than an ordinary junction. Thus the actual supports are determined in this part of the family at every width. The exterior argument also applies at two shrinks, where equality of spaces leaves a six-place exterior and ordinary supports of size at most five. [Short-shore and exterior arguments](census.md#why-the-rival-check-covers-mixed-histories) · [Two-shrink equation transfer](structural.md#two-shrinking-sites)

At every even width through 30, the census separately checks the full tables for all 1,724 types with at least two shrinking joins. Each cross-type comparison has a different invariant. Each of the 494 generators at a nonempty menu and the 2,310 generators at an empty menu preserves every support as a member of the physical set. This excludes a smaller support ambiguity between two family histories, including a self-isometry of one table. [Census method](census.md#census-through-width-30) · [Complete counts](census.json)
