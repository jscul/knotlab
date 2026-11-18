# Can bond distances tell which joins come next?

**Yes, at every finite stage of the pure parity growth rule.** Give a reader the bond distances between the current distinctions, including loose ones, and the known rule. From distances up to five it can recover exactly which distinctions meet at each junction. It can then list every legal single addition, predict all the groups in a simultaneous round, or tell that the round requires more loose distinctions than are available. This holds for every legal way of adding junctions, including the complete rounds that grow the cubic system. [Proof](../../proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/proof.md)

## Same-size rearrangements

These three arrangements each have four junctions, twelve distinctions and 256 allowed states. The last example is obtained by growing a chain of three, then joining the seed and the third junction to a new one. Both parents have the middle junction as a common neighbor.

| Arrangement | Single-parent joins next | Two-parent joins next | Three-parent joins next |
| --- | ---: | ---: | ---: |
| Three children of the seed | 3 | 3 | 0 |
| Chain of four | 5 | 2 | 0 |
| Seed neighboring a five-distinction junction | 4 | 2 | 0 |

The next-round counts are for the simultaneous rule. All serial choices of loose distinctions were checked separately. The examples also have different distance tables. Comparing only their size or their total number of allowed states would give the same answer for all three. [Literal checks of the allowed states](../../proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/check_examples.py)

The census enumerated all **552 distinct legal presentations through seven junctions**, identifying arrangements related by a renaming that preserves which distinctions are loose and where they meet. There were 1, 1, 2, 6, 21, 89 and 432 by size. The same number of distinct bond-distance tables appeared at each size. On two renamings of every presentation the reader recovered the exact junctions on the supplied distinctions and the exact next joins. It also identified all 489 presentations on which the simultaneous rule was blocked. The earlier two-threshold shortcut failed on 280 presentations, including the fourth-junction example with the five-distinction neighbor of the seed. Distances above five could be pooled without affecting recovery. [Census results](../../proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/finite_checks.json)

## Why it works for every round

Bond distance asks how many distinctions the smallest knot containing a pair needs, minus one. A junction has at most six distinctions. A short bond can also be made by combining two neighboring junctions, so two close distinctions can appear to share a junction when they are actually on opposite sides of a join.

The feature that resolves this ambiguity is that **any combination of three or more junction equations leaves at least seven distinctions in its parity check**. The last three junctions in the combination introduce nine distinct outputs. They can share at most two of those outputs among themselves. Consequently every bond of size six or less comes from one junction or two neighbors. In the two-neighbor case each participating junction has already been recovered from smaller bonds. The reader removes exactly the false pairings they create, then reads the larger junctions. Finite checks tested the cases where this distinction matters. A separate check at twenty junctions enumerated all 1,048,576 combinations of the equations and recovered all twenty junctions from the truncated table. [Proof of the reconstruction](../../proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/proof.md#3-the-distance-reader)

For the workspace's intuition about distance, this gives a constructive example. Once the pure parity growth law is fixed, the relations produced at one stage carry all the information that law needs at the next. One pair of patterns with equal tables and different next joins is impossible within this family. Interchangeable loose distinctions can still realize a join in several ways. Already at the three children of the seed there are 216 allocations on the old distinctions. The distance table specifies all of them. At a partially completed round it computes the rule afresh from the current snapshot. [Proof of the next-step claim](../../proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/proof.md#4-reading-the-next-join-including-all-permitted-choices)

The older eight-distinction betweenness attachment gives a concrete limit. Each of its 28 original pairs lies in a three-distinction knot. Run this same reader on the attached system and the first threshold groups at least eight distinctions as one junction. The actual junctions each have at most six. The proof already fails at that first threshold. Recovery of the mixed construction from its distances remains open. [Attachment control](../../proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/proof.md#scope)

## Reproduction

The proof is mathematical and the scripts check finite cases. From the repository root run the following with the project environment. The census uses exact graph isomorphisms. The separate check projects the literal allowed states and calls the canonical knot checker.

~~~sh
k=BOND-NEXT-JOIN-20261117-001
p="proofs/$k/$k-P001_distance_reader"
.venv/bin/python -B "$p/check_rearrangements.py"
.venv/bin/python -B "$p/check_examples.py"
~~~

The callable `recover_stars(table)` takes a mapping from pairs of bit names to their scalar distance. Either ordering of a pair is accepted. Distances greater than five may be represented by the number six. [Reader and census code](../../proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/check_rearrangements.py) · [Study design](preregistration.md)
