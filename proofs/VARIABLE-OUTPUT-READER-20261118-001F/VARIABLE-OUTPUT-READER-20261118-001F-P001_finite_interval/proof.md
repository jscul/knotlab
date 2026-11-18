# Every legal triple is determined by the full table at widths 21 through 26

**Standard statement.** Start with a ternary binary parity check and extend it serially by the prescribed incidence rule. Give each pair of coordinates the minimum cardinality minus one of a minimal nonempty parity-check support containing both. For each width from 21 through 26, every coordinate permutation that preserves this matrix between reachable presentations also preserves the predicate allowing an unordered three-coordinate extension.

**Nearest known result.** The earlier finite comparisons established this conclusion through width 20. In one width-32 example the table permits two different labeled parity codes with the same three-input choices. A distinct result at width 18 gives opposite permissions for smaller input sets under identical allowed states. The present result addresses three-input choices. [Earlier widths](../../VARIABLE-OUTPUT-READER-20261118-001E/VARIABLE-OUTPUT-READER-20261118-001E-P001_marked_symmetry/small_widths.md) · [Width-32 table](../../../research/VARIABLE-OUTPUT-READER-20261118-001E/decision.md) · [Smaller-input obstruction](../../../research/VARIABLE-OUTPUT-READER-20261118-001A/first_three.md)

## Result

All 6,898,145 reachable arrangement types in the six widths were compared. No two distinct arrangement types at the same width share a full table up to a permutation of the distinctions. Within each individual table every symmetry preserves the actual legal triple menu. The full distance table therefore decides each proposed triple at these widths without a retained ordering or labels from the past. There are 3,635,999 legal triple occurrences, with a separate occurrence counted for each unordered triple of distinctions in one representative of an arrangement type. [Detailed receipts](comparisons.json)

| Distinctions | Reachable arrangements | Arrangements with a legal triple | Legal triple occurrences | Arrangements requiring an exact symmetry check after the mark test |
|---:|---:|---:|---:|---:|
| 21 | 46,449 | 4,303 | 17,259 | 0 |
| 22 | 112,335 | 11,445 | 46,004 | 4 |
| 23 | 273,842 | 30,541 | 121,697 | 12 |
| 24 | 672,424 | 81,484 | 323,484 | 31 |
| 25 | 1,661,752 | 216,788 | 856,726 | 67 |
| 26 | 4,131,343 | 577,399 | 2,270,829 | 197 |

Together with the preceding finite checks, a first opposing pair or a first opposing symmetry of one arrangement must have at least 27 distinctions. This is only a lower bound. The width-27 examples that defeat a smaller observation have distinct full tables. [Earlier controls and exact limits](../../../research/VARIABLE-OUTPUT-READER-20261118-001C/all_sizes.md)

## Why the calculation covers every input

Represent an ordinary junction by a vertex, two junctions sharing a distinction by an edge, and the remaining distinctions by the loose count at each vertex. This classical colored graph is a complete encoding of the current incidence up to relabeling. The three-input menu also checks that the three selected distinctions are loose at different junctions, that every pair of holders has an ordinary common neighbor, and that no ordinary neighbor meets all three. When the next join is about to occur, every existing witness precedes it. All legal parent subsets and both fresh counts are tried. Exact canonical graph encodings remove repetitions. [Population algorithm and proof](population.md)

As an independent completeness check, count how many chronological sequences of parent sets and fresh counts end at every arrangement. Delete each possible last junction in turn, and account for ordinary automorphisms to remove equivalent site names. At each width this reverse total equals the sum of the legal extensions from the two preceding feasible widths. All histories at width 26 are accounted for in this way, including 8,585,343,953 different sequences with distinctions at the same holder interchangeable. The first missing reachable arrangement would break the identity. [Double-counting proof](history_balance.md) · [Counts by width](histories.json)

## Why the comparison covers every renaming

The classical wired graph adds one exterior vertex and joins every loose distinction to it. A nonempty ordinary shore gives a minimal nonempty parity-check support precisely when the shore and its complement in the wired graph are connected. Its size counts its crossing shared distinctions plus the loose distinctions on its ordinary side. The primary measurement enumerates every such shore, examines bonds in increasing cardinality, and assigns the first value through each pair. There are 2,131,786,800 measured pair entries over the six populations. The independent measurement builds a basis of the primal binary solution space and tests projected rank and minimality. [Measurement and comparison](compare.cpp) · [Independent rank calculation](audit.py)

For cross-arrangement comparisons the primary reader assigns a fixed modular value to every scalar and uses sums to encode a row's distance histogram. It refines each row using the other rows' encodings together with its distance to each row. Two symmetric sums of the refined encodings give the table's comparison key. A bijection preserving every entry necessarily preserves both key components. In each width all distinct ordinary presentations have different keys. This is a deterministic exclusion. Even a possible arithmetic collision between unrelated tables could only cause an additional exact comparison.

For a symmetry within one table, decorate each of the three marks with its refined row class and the distance between the other two marks. Sort the three decorations to remove their order. Every table symmetry preserves this triple value. If every class has a constant true verdict, no symmetry can reverse any verdict. Empty menus already satisfy this test. Exactly 311 positive arrangements had a class containing opposite verdicts and needed further comparison.

The exact comparison first groups distinctions whose exchange preserves every entry. Exchanges within each group and all isometries of the quotient between the groups cover every table symmetry. The search matches group sizes, common internal distances and all distances to groups already matched. A permutation changing the menu must change it under a generating permutation or a tested quotient lift. The 311 difficult cases required 1,194 internal exchanges or nonidentity lifts. Every one preserved its menu. An unordered triple can therefore be answered from the table alone by taking any matching representative and transporting the proposed marks to it. The representative and the map can both be found by finite enumeration. [Comparison checker](compare.cpp)

The independent checker remeasured all 311 using allowed-state ranks and reconstructed a legal history for each. Its enumeration of marked symmetries found that all 786 groups of equivalent legal triples were complete. A control replaced one legal triple with a forbidden one and kept the number of choices fixed. The actual distance-preserving swap of two distinctions exposed the change. The replay also compares every pair entry on a separate set of 86 source records against the independent measurement. [Independent audit](audit.md) · [Exact-case roster](residual_cases.jsonl) · [End-to-end replay](replay.py)

## A restricted all-size result

Suppose one presentation has at most four distinctions at each junction and at most one addition makes three fresh distinctions. Every competing presentation with the same pair table then has the very same allowed states and three-parent choices, even if its history is unrestricted. In this case the table forces the equations of size three and four, which generate all the original equations. The number of independent equations already reaches the largest permitted at that width, giving equality in the rival. The proof also describes what a bond of size five through two members of a legal triple can surround. [Structural proof](structural.md)

## Limit of the conclusion

One possible way to build an opposing pair can also be ruled out at every width. Start with the same identified presentation on both sides. Append one junction to each, with equal parent counts and equal fresh counts across the two. If every scalar agrees under a correspondence fixing the old distinctions and matching the new outputs, all triples drawn wholly from the old distinctions have the same verdict. The general question permits an isometry to exchange old and new distinctions or change the identified prefix. [Terminal-junction proof](structural.md#separate-derivation-for-a-terminal-junction)

No all-size upper bound on where the first opposing table could appear follows from a finite interval. The 18-distinction discrepancy for single- and two-parent permissions still applies to the same serial mixed-count law. If a larger table eventually gives opposite *triple* verdicts, its matching renaming must preserve every outside entry as well as those between the candidates. The least extra reading required by such an example would be a separate question.
