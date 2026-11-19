# Minimum reached junction count and current width

A pointwise-live table symmetry can first fail to extend at **12 current junctions** and **23 current distinctions** in the meet-once family. Both minima are attained by the same seven-junction start after one complete round. The negative bounds include every positive age and allow any starting arity of at least three. [Frozen design](../../../research/GROWN-END-MEET-ONCE-20261119-001/preregistration.md)

## Why a bounded predecessor census covers every age

Take the actual predecessor of any positive-age stage. Its junctions are connected, all ordinary pairs meet at most once, and an open ordinary junction has at least three distinctions. Its parity support is a bond precisely when deleting its holder leaves the rest of the augmented graph connected. The augmented graph wires the loose distinctions to one exterior.

The gates are inherited at every open round. Replacing an old loose distinction by a meeting with a newborn and its link to the exterior preserves the old complement connectivity after removing an old site. When removing a newborn, the old ordinary sites remain connected and every other newborn meets an old site. At least one other newborn has an exterior link. A round with one newborn consumes the whole loose boundary and gives it zero fresh distinctions, so its successor is closed and cannot undergo the tested next round. Otherwise every newborn makes at least one fresh distinction. An ordinary parent supplies only one distinction to each child, and every newborn has at least three distinctions in an open round. The arbitrary connected starts in the design therefore include every open predecessor that can matter.

Write \(n\) for the predecessor junction count and \(k\) for the number born in its round. Let \(L\) be its set of live holders. Its ordinary graph and \(L\) determine the forced multi-parent groups \(G\). If \(d_i\) of these groups use holder \(i\), its loose count is \(d_i+a_i\), where \(a_i\) counts unary births. In a current bound \(N\), the \(a_i\) sum to at most \(N-n-|G|\). This enumerates every loose allocation allowed by the bound.

The search uses every live subset and labelled loose allocation on each connected simple graph representative. The counts can include more than one allocation for a single arrangement when the underlying graph has a symmetry. Connectivity after deleting an ordinary site and the degree-plus-loose floor apply before allocation. Each surviving allocation is grown by the complete cheapest-count law.

## Safe cases with at most two newborns

When the tested next round consists of unary births, each old loose wire is replaced by a two-terminal network whose cheapest separating cut has size one. A bond involving an old distinction outside a replacement projects to a bond before replacement. When the old endpoints are separated, precisely one link of that replacement can cross a bond. In mixed readings, requiring a specific link of weight \(w\) adds \(w-1\) to the old bond size through the corresponding wire. Local readings wholly within replacements are fixed. Since the permutation fixes each original loose wire, it extends by the identity on fresh names. [Offshoot theorem](../../../proofs/PROVE-B-20261119-001A/PROVE-B-20261119-001A-P001_split/proof.md)

A current stage with two newborns is covered by the same argument if they have no common parent. If they do, there is one candidate pair for the next round. Each has one fresh distinction after a multi-parent birth, or two after a unary birth. With counts \(1,1\), the next site consumes the entire loose boundary as an implied equation, replacing the exterior holder and leaving the table unchanged. With counts \(1,2\), the paired child \(J\) has one fresh distinction and a unary child on the remaining wire has two. Taking \(J\) as the old exterior holder, this replaces that remaining wire by a series of links of weights \(1,2,1\). Its minimum capacity is one, and the preceding comparison applies. The \(2,2\) case would mean both newborns were unary at the same holder, with the only two loose distinctions in the entire predecessor. On a one-site predecessor this violates the arity floor. On a larger predecessor the two distinctions are the support of the sum of all rows and a proper subset of their holder's support, violating irreducibility.

Consequently the census tests only \(k\geq3\), from graphs with at most \(N-3\) predecessor junctions. The smaller newborn counts are covered by the preceding structural check.

## Exact symmetry and successor tests

With \(k\geq3\) all newborns are live and every previous loose distinction belongs to one of them. Thus only the inherited ordinary shared distinctions can move under the pointwise-live condition. The table calculation groups parallel exterior distinctions by endpoints, retaining their weights in the cut cardinalities. It computes the exact least bond through each pair needed for the symmetry search using cuts with both shores connected.

At each level of the pointwise stabilizer chain, find one exact symmetry for each possible image of the next unfixed distinction. These representatives generate the entire group, by reducing any element to the next stabilizer using a representative with the same image. The old permutations having an extension form a subgroup, since extensions can be composed and inverted while carrying old names onto old names.

First the checker pools bond cardinalities above six. If every generator of this larger group carries the parity span, the full table group does as well. An equation-carrying map extends by the identity on fresh names because it fixes all the taken distinctions. Otherwise the checker obtains the actual full table group and tests its generators. For a non-equation generator, a changed pair of old names prevents every fresh assignment. If the old entries agree, exact constrained matching tests existence of the fresh part.

In 153 current histories the successor exceeded the ordinary shore-scan cutoff. The fallback needs only successor rows of moved old distinctions. A bond in such a row splits that distinction's endpoints. The search roots its non-exterior side at the selected endpoint, excludes the other endpoint and exterior, and enumerates connected shores using a maximum-flow bound on their possible boundary size. It raises this bound until every required pair has its exact finite entry or until the bound covers all cut cardinalities. All 484 non-equation generators of those cases extend by the identity on fresh names. The largest has 32 successor junctions and 161 successor distinctions. The highest required bond size was 20. The rooted method recovers the same obstruction as both whole-table methods on the named 12-junction witness.

## Completed bounds

| Current junctions | Unrestricted current width | Current width at most 22 | Current width at most 23 and at most 12 junctions |
|---:|---:|---:|---:|
| 4 | 1 | 1 | 1 |
| 5 | 1 | 1 | 1 |
| 6 | 8 | 7 | 7 |
| 7 | 68 | 67 | 67 |
| 8 | 562 | 515 | 544 |
| 9 | 7,541 | 3,533 | 4,956 |
| 10 | 148,067 | 13,003 | 22,436 |
| 11 | 5,410,517 | 33,668 | 83,389 |
| 12 | — | 24,201 | 137,818 |
| 13 | — | 1,263 | — |
| **Total** | **5,566,765** | **76,259** | **249,219** |

There are zero nonextensions and zero undecided cases in both completed bounds. The unrestricted sweep goes through eleven current junctions. The width check is global for \(W\leq22\). If there are \(F\) loose distinctions at observation, then \(2W-F\) is the sum of the site arities. A possibly failing stage has \(F\geq3\), so it has at most \(\lfloor(2W-3)/3\rfloor\leq13\) junctions. Its predecessor has at most ten junctions. An ordinary predecessor with \(E\) shared distinctions must have \(E\leq W-6\), since each of the at least three children consumes at least one distinction and makes at least one fresh distinction. Before allocating extras, the checker uses the stronger lower bound \(E+\sum_{g\in G}(|g|+1)+3\sum_i a_i\). It checks the actual current width after growth.

For the positive control, a seven-junction start has 16 distinctions. Its first two complete rounds take it to \((12,23)\) and then \((16,30)\), listing junction count and width. The specified old transposition fixes every live support pointwise and preserves the entire current table. It exchanges successor pair bond sizes three and four on two already shared old distinctions. Independent literal round replay and complete connected-shore calculations check this witness and the earlier meet-twice control. The independent literal census through seven current junctions agrees on every small population and checks all 147 of its nonidentity pointwise-live maps against the successor tables. These minima concern the current stage, under the pointwise-live self-permutation test.

## Starting size at both current minima

The joint bound of at most 12 current junctions and 23 current distinctions contains exactly three failing predecessor allocations, with no undecided cases. Their current presentations are pairwise nonisomorphic. The audit records each full loose vector, its ordinary shared pairs, all three literal stages, and an explicit fixed old pair that changes its successor bond size from three to four. An independent verifier remeasures every pair of each current and successor table.

The newborns in an open reached stage are exactly its live holders, and they form an independent set in the ordinary graph. Removing them and preserving every distinction still incident to an older holder gives the sole candidate predecessor up to renaming. The audit applies that deletion recursively and checks each candidate by regrowing a complete round with the independent literal engine. All three failing stages peel once. For the seven-junction predecessor, another peel proposes three pairwise meeting junctions with loose counts \(1,1,3\). The literal round makes a single three-parent junction and two unary junctions, giving six junctions. Each eight-junction predecessor has two live holders that already meet, ruling out a further peel. Thus the earliest starts have \((7,16)\), \((8,17)\), and \((8,17)\) junctions and distinctions, each one round before its failure. **Seven is the smallest starting junction count among failures attaining both current minima.** [Joint minimum census and peel records](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound_threshold.json)

## Replay

~~~sh
.venv/bin/python -B experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound.py --cap 11
.venv/bin/python -B experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound.py --cap 13 --width 22
.venv/bin/python -B experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound.py --cap 12 --width 23
~~~

The sweeps used nauty 2.8.9. The driver looks for `nauty-geng` or `geng` on `PATH` and expects `geng -cq` to stream graph6 representatives. Pass `--geng` for a separate executable and `--geng-library` only to override the inherited `LD_LIBRARY_PATH`. The `--controls-only` replay needs no `geng` installation.

[Reached-junction results](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound_c11.json) · [Width-bound results](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound_w22.json)
