# Can the first three-parent join be read from bond distances?

Yes. In the specified seven-junction example the eighth junction can take three existing distinctions exactly when their three mutual bond distances are **6, 8 and 8**. Twelve of the 816 possible triples pass this test. Each lets the junction introduce either two or three fresh distinctions. Reading the rule takes only three entries of the current table.

We compared the example with every reachable arrangement on eighteen distinctions under the law allowing either fresh count. Only the original incidence type matches its full distance table. There are 48 ways to rename the distinctions and keep that table, and every one preserves the legal next choices on the actual distinctions. These comprise 9 single choices, 17 two-parent choices and 12 three-parent choices. All twelve triples are exchangeable by renamings. [Proof and checks](../../proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/proof.md)

| Existing junctions | Reachable arrangements at width eighteen | Arrangements with ambiguous next choices |
| ---: | ---: | ---: |
| 6 | 89 | 0 |
| 7 | 1,609 | 0 |
| 8 | 1,797 | 6 |
| **Total** | **3,495** | **6** |

Forward growth and an independent enumeration removing possible last junctions gave the same three counts. Full tables distinguish all 3,495 incidence types. Within six types, a symmetry of the full table allows a loose distinction to trade places with a distinction already used. The next single choices change in all six, and the two-parent choices change in four of them. Every three-parent menu in the census survives every full-table renaming. These are exact counts of distinct arrangements, each counted once. [Forward comparison](../../proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/width.json) · [Independent comparison](../../proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/reference.json) · [All classes](../../proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/classes.json)

## Where the information first disappears in this comparison

A different seven-junction start has fifteen distinctions. Each of its three eligible parents has two loose distinctions. For the eighth junction choose one from each pair and introduce three new distinctions. Or take the unused member of each pair and introduce the same three new distinctions. Both choices are legal. Adding the seven older parity equations cancels every shared distinction and leaves precisely the six members of the three pairs. The two candidate eighth equations therefore impose exactly the same constraint, given the older equations.

The resulting arrangements both have eighteen distinctions and agree on **all 1,024 allowed states** on the same names. Their bond distances agree entry for entry. Yet a distinction taken by the first history is still loose in the second. A ninth junction may use it only in the second history. Legal two-parent choices also differ. Neither resulting arrangement has a legal three-parent choice. This is an explicit obstruction to reading the entire next menu from current distances when the fresh count can vary. [Literal replay of both histories](../../proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/witness.json)

The all-size result for exactly three fresh distinctions uses a narrower growth law. What the variable-count example pinpoints is which piece of information can disappear even under parity. Two legal ways to make the same constraint can leave different distinctions available for use. The question of choosing a dimension has a separate completion test. [Fixed-count result](../BOND-NEXT-JOIN-20261117-001/next_joins.md) · [Companion question](../VARIABLE-OUTPUT-READER-20261118-001/companion.md)

## Evidence and scope

The width and primary target were fixed before the comparison. An advisor checked the use of independent reachability counts, physical renaming in growth, and the need to grade sets on each current distinction. The exact witness also has a direct parity proof. Independent checks within the task use different enumeration and distance algorithms. As an exploratory calculation, pooling all distances above four still recovers the designated menu, while pooling above three gives a specific false triple. The global width-eighteen counts use the full scalar table. The evidence bears on G1 and A97. [Preregistration](preregistration.md) · [Shorter-table check](../../proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/triples.json)
