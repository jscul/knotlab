# Can bond distances identify every legal three-parent join at width nineteen?

Yes. In all **8,191 reachable arrangements**, the full bond-distance table identifies exactly which triples of existing distinctions may join. Of these arrangements, 582 have a legal triple. Their 2,381 actual choices all survived every distance-preserving renaming. Either two or three fresh distinctions can be introduced after each choice. [Proof and checks](../../proofs/VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/proof.md)

| Existing junctions | Reachable arrangements | Arrangements with a legal triple | Legal triples across them |
| ---: | ---: | ---: | ---: |
| 7 | 1,740 | 71 | 575 |
| 8 | 5,355 | 440 | 1,670 |
| 9 | 1,096 | 71 | 136 |

Two independent calculations agreed. One grew every reachable incidence and tested the symmetries of its table. The other removed possible last junctions and tested all ways a legal triple could move under a renaming. All full tables distinguished the underlying incidence types. In 512 arrangements, a table symmetry moved one eligible triple to another. [Forward calculation](../../proofs/VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/population.json) · [Independent calculation](../../proofs/VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/reverse.json)

## How much of the table does a triple need?

Three full rows can still leave the answer ambiguous. In two reachable arrangements, each of the 51 distances involving the proposed triple agrees under the same renaming. Each pair of parents has a common neighbor in both arrangements. Only in the second arrangement do all three parents share one, which makes its triple forbidden. The surrounding table distinguishes the cases. One has 32 pairs at bond distance four and the other has 33. [Worked example with its renaming](../../proofs/VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/near_witness.json)

A single yes-or-no answer from the rest of the table sufficed across the census. **Is the total number of unordered pairs at distance four odd?** Compute that bit once for the whole arrangement. For each proposed triple, take its three rows together, disregard the names, append the bit and consult the published catalogue for width nineteen. It contains 616 legal descriptions. Without the bit, eight forbidden triples match a legal description. With the bit, the reader answers correctly on all **7,937,079** candidate triples. This reader was found by inspecting the census and then checked against every case. [Reader](../../proofs/VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/check_reader.py) · [Catalogue and results](../../proofs/VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/reader.json)

The earlier obstruction for single and two-parent choices at width eighteen still bounds what a general reader can recover. Triple eligibility is a distinct question. The nineteen-distinction result establishes that the surrounding arrangement can supply exactly the information a proposed triple is missing. Whether this particular bit or any other distance reader suffices at every width remains open. [Width-eighteen result](../VARIABLE-OUTPUT-READER-20261118-001A/first_three.md)
