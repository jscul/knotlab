# The first opposing distance-three tables and the finite full-table check

**Bond distance three loses triple permission at width 20.** This is the first width with any legal triple in the binary-third family. **Through width 30, every source in this family with a legal triple has its actual junction supports preserved by every full-table match to a reachable mixed-law rival.** These are finite claims. The growth schedule is the one in the frozen prediction, with two initial unary three-fresh joins, one further binary three-fresh join, and all other joins binary or ternary with two fresh distinctions. [Frozen predictions](../../../research/VARIABLE-OUTPUT-READER-20261118-001L/preregistration.md) · [Census and witness tables](census.json)

## Exact opposing permission at width 20

The following are two serial histories, with each column listing the successive even-parity supports on its own distinction names.

| Left | Right |
| --- | --- |
| \(0,1,2\) | \(0,1,2\) |
| \(0,3,4,5\) | \(0,3,4,5\) |
| \(1,6,7,12\) | \(1,6,7,8\) |
| \(3,6,8,9\) | \(3,6,9,12\) |
| \(2,8,10,13\) | \(2,9,10,11\) |
| \(4,7,11,14\) | \(4,7,13,14\) |
| \(5,10,15,16\) | \(5,10,15,16\) |
| \(9,11,17,18,19\) | \(8,11,17,18,19\) |

The left-to-right permutation sends 8→9, 9→12, 12→8, 11→13 and 13→11, and fixes the other names. It preserves all 190 pair readings clipped at bond distance three. It carries the left forbidden triple \((11,15,17)\) to the right legal triple \((13,15,17)\). The left menu is empty and the right menu contains the 12 triples taking one bit from each of \(\{13,14\},\{15,16\},\{17,18,19\}\). It sends the last left support to \(\{12,13,17,18,19\}\), which differs from the last right support. Fourteen entries first differ at bond distance four, and 35 full entries differ. For instance the left entry on \((9,11)\) has bond distance 4 and its image on \((12,13)\) has bond distance 6. [Pair entries and complete menus](census.json)

Among the 78 width-20 types, 18 have a legal triple. The clipped search grades 18 opposing cross lifts and 31 opposing self-isometry generators. One self-isometry exchanges 9 and 14, carrying legal \((12,14,18)\) to forbidden \((9,12,18)\). It fixes all 190 readings through distance three, with eight discrepancies at distance four and twelve at full precision. Every distance-four symmetry or cross comparison at this width preserves the junction supports and menus. The least bond sizes containing all three marked distinctions are 10 and 8 in the cross comparison, and 8 and 9 under the self-permutation. This extra reading also separates those two specific contrasts. [Both width-20 witnesses](census.json)

The earlier width-26 control is obtained by adding loose distinction 25 to a binary site of the J witness. Its swap of 19 and 20 carries a legal triple to a forbidden one while preserving every entry through distance three. This construction has eight discrepancies at distance four and 24 at full precision. [J witness](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/frontier.json) · [Live and forbidden marks](census.json)

## Census through width 30

| Width | Physical types | With a legal triple | Types with at least two shrinks | Live types with at least two shrinks |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 2 | 0 | 0 | 0 |
| 14 | 4 | 0 | 0 | 0 |
| 16 | 9 | 0 | 0 | 0 |
| 18 | 25 | 0 | 0 | 0 |
| 20 | 78 | 18 | 0 | 0 |
| 22 | 257 | 113 | 0 | 0 |
| 24 | 919 | 373 | 0 | 0 |
| 26 | 2,979 | 1,228 | 19 | 2 |
| 28 | 9,617 | 2,780 | 314 | 65 |
| 30 | 25,055 | 5,860 | 1,391 | 285 |

The ordinary incidence and loose count per holder encode the current physical support family up to distinction renaming. Build every successor and quotient by exact colored-incidence isometry, with the exceptional birth flag kept separately. Choosing a different loose distinction at the same holder gives a renaming of the old physical supports. Every future choice of parent group therefore exists on each representative. At the first live width, independent literal generation without interim incidence quotienting yields 1,545 parent-choice histories and exactly the same 78 types. Direct enumeration of the parity spans and their minimal supports agrees on all 14,820 pair entries at this width. [Generation code and literal controls](census.py) · [Population and table checks](census.json)

All 1,724 physical types with at least two shrinking joins were given full matrices by the connected-shore engine. For the 352 live cases, the exact matrix checks grade every generator from distance-twin classes and every quotient isometry lift. All 494 tested generators preserve the stars and the complete triple menu. The supplementary empty-menu check grades another 2,310 generators and preserves the stars in every case. All cross-type full-table buckets are singletons. In a collision bucket an exact comparison would be required. Fingerprints serve only as necessary conditions for isometry. [Connected-shore engine](../../VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval/compare.cpp) · [Exact matrix quotient](../../VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/check_classes.py)

### Why the rival check covers mixed histories

Let the source have \(n\) junctions, so its width is \(2n+4\). The readings through \(K=3\), where \(K=D+1\), give the sole ternary support. Any rival has a single ternary site, and its first two additions must be unary and make three fresh distinctions. With even width the number of three-fresh additions is odd, hence at least three. Its rank is thus at most \(n\), since every actual junction adds one independent parity constraint.

With at most one shrink, the first three selected sites of any larger ordinary shore contribute cut size at least seven and the sole shrink can save at most one. The short-shore theorem then forces every source star through size five, which gives rank \(n\) and equality of the complete equation spaces. For all 352 measured live cases with more shrinks the explicit sole-witness forcing algorithm also recovers rank \(n\) already through \(K=5\). It uses only the supplied pair table. Equality of the spaces directly gives equality of the triple menus. [Short-shore proof](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/inverse.md#five-bit-equations-at-the-first-shrink) · [Forcing algorithm](../../VARIABLE-OUTPUT-READER-20261118-001I/VARIABLE-OUTPUT-READER-20261118-001I-P001_cycle_obstruction/fixtures.py#L85) · [Allowed-state inverse](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md)

The source ordinary incidence is two-connected after the fourth junction closes the initial cycle. Every subsequent site has two or more parents, so this persists. The wired incidence is three-connected by the ordinary two-site deletion theorem. Its augmented stars are intrinsic in the common equations. For a star, deleting its support leaves all surviving bits linked by cycles. For a nonstar bond, each connected shore has a surviving bit and no surviving cycle meets both. Any equal-space rival therefore has the same \(n+1\) augmented stars. The remaining choice is which is the exterior. [Augmented-star proof](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#locating-the-ordinary-junctions-from-their-equations)

With zero or one shrink the exterior has at least seven bits, too large to become an ordinary site. With two shrinks it has six. An alternative exterior would need to meet every parallel pair, as would the original. In both presentations the chronologically final site has at least two loose outputs, so those final sites would be exactly the two proposed exteriors in exchanged roles. They have the same number \(h\) of fresh outputs. If \(h=2\), the rival's final six-place support would need four parents. If \(h=3\), the source's final high birth had only two inputs and its prefix had five loose bits. It belongs to the minimum-width family of J, which excludes a legal triple on that prefix. Yet the rival's final addition would need exactly the complementary triple on that same physical prefix. This excludes the exterior exchange in both cases. [Five-loose exclusion](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins)

The last cases are the four width-30 live sources with three shrinking joins. For each, the forced code has exactly one reachable ordinary support set under the unrestricted law. Generate possible support sets from the unique ternary seed and all code bonds of size at most six, retaining only literal loose-bit joins, and deduplicate current sets. Each step adds a linearly independent support. Completion at rank 13 is equivalent to spanning the whole forced code. Across the four sources this examines 3,299 different prefix support sets. [Unrestricted check](census.py) · [Per-width exact counts](census.json)

```sh
python3 -B proofs/VARIABLE-OUTPUT-READER-20261118-001L/VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third/census.py
```
