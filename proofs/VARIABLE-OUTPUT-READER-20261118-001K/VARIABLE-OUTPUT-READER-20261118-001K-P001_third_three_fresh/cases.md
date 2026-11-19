# A legal triple hidden at bond distance four

At width 26, exchanging distinctions 19 and 20 preserves every bond-distance entry through four and carries the legal triple \((12,20,21)\) to the forbidden triple \((12,19,21)\). The presentation is in the frozen family. The first two additions each use one parent and introduce three distinctions. Only the final addition again introduces three distinctions, and it uses three parents. Bond distance five is therefore necessary for this family. [Frozen prediction](../../../research/VARIABLE-OUTPUT-READER-20261118-001K/preregistration.md) · [Exact certificate](cases.json)

The eleven even-parity supports, in birth order, are

```text
(0,1,2)
(0,3,4,5)
(1,6,7,8)
(3,6,9,10)
(4,7,11,12)
(9,11,13,14)
(5,13,15,16)
(2,15,17,18)
(8,17,19,20)
(18,14,21,22)
(10,16,19,23,24,25)
```

Number the junctions from zero. The last addition takes inputs at junctions 3, 6 and 8. Their pair witnesses are \(\{1,5\},\{2\},\{7\}\) respectively, with empty joint intersection. After that addition, the three loose distinctions \((12,20,21)\) are at junctions 4, 8 and 9. Their three pair witnesses are 2, 5 and 7. The image uses distinction 19, which is shared by junctions 8 and 10. The complete legal menu consists of \((12,20,21)\) and \((12,20,22)\).

Write \(K=D+1\) for the least cardinality of a bond containing the pair. The transposition fixes each junction support through size five. It therefore fixes every bond through size five in this example. To see why those supports suffice, consider an ordinary shore with at least three junctions. Its first three have total degree at least eleven and at most two internal meetings, so their boundary has at least seven distinctions. Every later addition in this example has at least as many fresh distinctions as inputs, and thus cannot reduce the boundary. A bond through size five consequently comes from one junction or a pair of adjacent junctions, and in the latter case this requires the seed and a four-place junction. Both types of support are invariant under the transposition. [Short-shore calculation](../../VARIABLE-OUTPUT-READER-20261118-001I/VARIABLE-OUTPUT-READER-20261118-001I-P001_cycle_obstruction/nonshrinking.md)

| Presentation | Pairs checked | Entries changed through \(D=3\) | Through \(D=4\) | Through \(D=5\) | Full |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prior two-fresh final addition, width 25 | 300 | 0 | 8 | 16 | 24 |
| Three-fresh final addition, width 26 | 325 | 0 | 0 | 10 | 10 |

At width 26, for every \(j\in\{10,16,23,24,25\}\) the exact values are \(D(19,j)=5\) and \(D(20,j)=6\). The ten entries from these five pairs of values exhaust the differences under the transposition. At \(D=5\) and at full precision the self-isometry group has order 12 and preserves the menu. The entries through \(D=5\) force the entire rank-11 equation space, with zero unresolved short bonds. This also certifies the menu against every reachable rival with the same clipped table, via the allowed-state inverse. The width-25 replay is the matched control with only two fresh distinctions at the final junction. [Exact permutations and equation spaces](cases.json) · [Allowed-state inverse](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md)

## The two width-19 starting records

Both starting records were taken from the earlier minimum seven-to-six construction. For each, the checker used every literal legal triple as the inputs of a three-fresh junction. It then enumerated all legal two- and three-parent additions with two fresh distinctions up to two additions after that junction. No equivalence reduction was used. [Earlier starting records](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/suffix_windows.json) · [Replay code](cases.py)

| Width-19 starting record | Immediately after the six-place junction | One further addition | Two further additions |
| --- | ---: | ---: | ---: |
| Latest on the four-junction side | 8 | 48 | 336 |
| Latest on the five-junction side | 2 | 24 | 152 |

All 570 menus were empty at the recorded endpoints, so the realized further additions were binary. The checker rebuilt 180,782 pair entries under renamed inputs and checked complete menu transport. The full equation ranks at widths 22, 24 and 26 were 9, 10 and 11 respectively. Every table forced its full rank from \(D\le5\) with zero unresolved short bonds. Forcing through \(D\le4\) recovered one fewer independent equation in every case.

On each starting record, the designated two-fresh cap from the predecessor produces a minimal six-distinction boundary across several junctions. The alternative three-fresh cap has a six-place junction on its actual input and output distinctions. In both comparisons the predecessor boundary has fourteen pair minima \(K=6\) and one \(K=5\), at its two new outputs \((19,20)\). The true six-place junction has all fifteen minima equal to \(K=6\). [Complete readings on the two six-distinction supports](cases.json)

## A live triple using a fresh output of the six-place junction

Keep the first nine displayed supports and finish with \((10,16,19,21,22,23)\) and \((12,20,24,25)\). Its eight legal triples use 14, one of \(18,21,22,23\), and one of \(24,25\). This includes \((14,21,24)\), which uses a fresh output of the six-place junction. At this width the entries through \(D=5\) again force rank 11. The two width-26 live tables are distinguishable under every relabeling already through \(D=3\). [Live cases and equation forcing](cases.json)

## At width 28 the equation space can differ at bond distance five

Both legal triples of the late exceptional case can be used for a further two-fresh addition. For each successor the entries through \(D=5\) force eleven equations and leave ten compatible rank-12 binary spaces. Testing all short bonds as possible junction supports under the literal growth law yields two reachable spaces, each with a unique literal set of supports and an empty triple menu. The complete table forces just the original space. [Compatible spaces and replay search](cases.json)

For the successor consuming \((12,20,21)\), keep the first ten supports displayed above and use the following last two supports in each history.

| History | Eleventh support | Twelfth support |
| --- | --- | --- |
| Source | \((10,16,19,23,24,25)\) | \((12,20,21,26,27)\) |
| Rival | \((12,20,21,26,27)\) | \((10,19,22,23,24,25)\) |

The rival takes the exceptional three-fresh step after its first shrinking join. Both histories satisfy the same frozen source conditions and agree on all 378 entries through \(D=5\), with names fixed. The nine changed full entries first appear at \(D=6\), where the source has six more entries equal to 6. The allowed states differ, and the equal empty menus certify the immediate triple verdict on these cases. [Full tables and exact changed entries](cases.json)

## The width-28 match ends before the first live descendant

From the source above, the exact closure of subsequent two-fresh moves contains 115 distinct records of loose holders and their common-neighbor witnesses, with a legal triple in seven records. The first such descendant has width 40 and follows six binary additions. The rival's closure contains 27 records and every one has an empty triple menu. The frontier representation is used here only for reachability of legal moves. [Exact frontier representation](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins) · [Closure results](cases.json)

At the first step of that source path both histories use \((23,26,28,29)\). The rival has a single pair of holders available at that step. Changing which loose bit is used at either holder just relabels the presentation. The two width-30 tables agree through \(D=4\), and four named entries separate them at \(D=5\). The pair from 22 to each of 28 and 29 has exact \(K=6\) in the source and 8 in the rival. The pair from 16 to each of 28 and 29 has the reverse values. Even though the clipped histograms agree, the clipped row profile with counts \((0,3,0,17,9)\) at \(K=3,4,5,6,>6\) occurs only in the source. This excludes every relabeling at \(D=5\). [Exact row profile and pair comparison](cases.json)

At steps two through six the first live source path was compared with every rival holder-choice history at the same depth. The respective counts were \(1,1,2,6,10\), and exact comparison already separates every table at \(D=3\). The width-40 source has four legal triples, and its entries through \(D=5\) force rank 18 with no residual candidate. Thus the difference in future reachability follows a separation of the observed tables. [Full path, endpoint table and legal marks](cases.json)

The literal checker uses wired cuts for its main tables. On the width-21 through width-28 named examples it also enumerates the parity span and removes every support containing a proper nonempty equation, then checks each pair minimum against the wired-cut result. The continuation comparison computes its short minima directly from the parity span. [Reproduction](cases.py)
