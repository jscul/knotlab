# The three reached pairs whose successors separate

None of the three priority GROWN-PAIR pairs has a source table isometry preserving the growing end. All six stages were rebuilt from their original starts at round one. Each pair has nine junctions on both sides and grows to fourteen. The successors have different numbers of distinctions in every pair. These three separations therefore leave the proposed extension of a growing-end-preserving matching untested. [Archived reached groups](../../../research/GROWN-PAIR-20261119-001/grown_pair.md) · [Frozen design](../../../research/GROWN-END-SWAP-20261119-001/preregistration.md)

| Archived group | Current distinctions | All source table maps | Maps carrying every live support | Maps preserving the growing end | Successor distinctions |
|---|---:|---:|---:|---:|---:|
| g000 | 19 | 64 | 32 | 0 | 29, 28 |
| g034 | 20 | 192 | 96 | 0 | 30, 29 |
| g074 | 21 | 768 | 384 | 0 | 31, 30 |

All 1,024 source maps transport the loose set. Zero carry the equation span. The same obstruction occurs in each pair. The unique live holder with one loose distinction is absent from every meeting set on one side and belongs to a maximal meeting set on the other. Thus a map carrying the live supports and loose counts cannot preserve the meeting family. This applies to both the entire family of sets of size at least two and the maximal-family reading used in EXTEND-ROUND. [Definition of the growing end](../../../research/EXTEND-ROUND-20261119-001/extend_round.md#lemma-a-and-claim-b-proved)

## Reconstruction and exact comparison

The checker reads the archived group indices and raw census stages. It takes both original start keys per group, regrows them by the complete cheapest-count parity law and checks the reached supports against the archived rows. It checks full pair tables by connected cut enumeration, compares the ordinary incidence graphs, and retains the original provenance. A candidate old map must send each live support and its loose group to a corresponding live support, and then transport the meeting family.

The first exact search encodes that reading with the full pair table and quotients permutations only within each live holder's loose group. These coordinates have identical ordinary incidence and can be permuted freely in the old table. The second search enumerates the complete uncompressed table isometries with VF2 and tests the original supports and meeting family on each map. Their counts agree. No isometry ceiling was reached. All six successors are within the declared bound of thirty junctions.

In a recoding control, simultaneously rename one source and its measured successor, then deliberately exchange the images of two old loose distinctions of the same holder. The exchanged map still carries the exact old table, growing end and equation span. Holding that map rigidly on all old names gives an old successor pair with \(K=4\) on one side and \(K=6\) on the other. Re-pairing loose names inside the designated holder restores agreement on the entire successor table. This tests the distinction between the two extension conventions on a known recoding.

The checked cross-arrangement roster ends with the three priority groups. The independently certified positive-age obstruction satisfies the stopping rule for the wider study.

~~~sh
.venv/bin/python -B experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/carried.py
~~~

[Replay checker](carried.py) · [Literal histories, map totals and control](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/carried.json)
