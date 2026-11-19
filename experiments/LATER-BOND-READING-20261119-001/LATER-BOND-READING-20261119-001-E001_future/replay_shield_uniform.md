# Exact smaller shield witnesses

The smallest fixture replayed here reaches **104 junctions and 372 distinctions**. It has six shields of each color, two anchors, weight two on the hot hub bundles, weight three on the hot anchor bundles, and shield bundles of weight six. The branches have cost four at observation. The compact red branches drop to cost one and the one-parent blue branches retain cost four. The marked pair and its image have minimum bond sizes 24 and 24 before the next round, then 22 and 24. The compared names are already shared.

The compact uniform witness with parameters `(I,s,L,M) = (2,6,3,8)` reaches a marked stage of **224 junctions and 700 distinctions**. The marked exchange preserves the full pair and triple readings, all pair-flip bits, and every live distinction. The two compared minimum bond sizes are both 26 there, then 24 and 26 after the next complete round. The compared names were already shared, so fresh renaming cannot repair the difference.

A smaller checked variant uses five shields per color, weights three on the hot hub bundles and two on the hot anchor bundles, shield bundles of weight eight, and branch cost six at observation. Its red branches shrink and its blue branches retain cost six. It reaches **118 junctions and 504 distinctions**, where all old pair and triple readings still agree under the marked exchange. The successor bond sizes are 21 and 22, distinguishing old names `(3,9)` and `(9,15)`.

| Parameters and realization | Start | Marked stage | Successor | Current marked minima | Successor minima |
| --- | ---: | ---: | ---: | ---: | ---: |
| `(2,5,3,14)`, linear branch | `(188,888)` | `(328,1028)` | `(338,1038)` | `(24,24)` | `(21,24)` |
| `(2,6,3,8)`, linear branch | `(152,628)` | `(248,724)` | `(260,736)` | `(26,26)` | `(24,26)` |
| `(2,6,3,8)`, compact branch | `(128,604)` | `(224,700)` | `(236,712)` | `(26,26)` | `(24,26)` |
| Two-color branch variant with six initial routes | `(58,324)` | `(118,504)` | `(198,809)` | `(22,22)` | `(21,22)` |
| Two-color branch variant with four initial routes | `(56,276)` | `(104,372)` | `(146,450)` | `(24,24)` | `(22,24)` |

Each size lists ordinary junctions and distinctions. `I` counts anchors, `s` counts shields per color, `L` weights the hot bundles, and `M` is the first reached branch cut cost. The compact branch identifies the two old witnesses with two of the leaves. For each literal branch the production rule, using maximal cliques for group enumeration, and the independent complete-round replay agree on both rounds. The result records `M` disjoint routes from the pole at the marked stage and the sole loose successor distinction. These certify the change in branch cut cost from `M` to one. [Branch construction](../../../research/LATER-BOND-READING-20261119-001/boundary-proof.md#a-synchronous-branch-of-linear-size)

## Direct minima and arity four

The connected-cut oracle enumerates the actual compressed graph with its two separate hubs and outside holder. The 328-junction witness has 153,539 compressed bonds and the other two realizations have 620,485 apiece. Every old minimum is read from the incidence of each bundle in the bonds, sorted by cost independently for each age. The entire graph, including the outside, is retained. The largest old triple minima, 98 and 64, exceed the corresponding coarse shielding thresholds of 70 and 48, so the direct comparison matters in these examples.

For a query containing a host name, a branch with any marked distinction has its terminals separated in every relevant bond. Compressing adds the fixed marked branch surcharge to the compressed minimum. The host permutation fixes every branch name, so matching the compressed minima through at most three bundle names proves equality of the full old pair and triple readings, including any absent readings. The literal comparison checks the live end and the complete relation of equal parity columns separately.

| Compressed host | Old triple queries | Old triple orbits compared | Quartet orbits compared | Quartet orbits differing | First quartet source and image |
| --- | ---: | ---: | ---: | ---: | ---: |
| `(2,5,3,14)` | 22,100 | 18,709 | 218,509 | 904 | no bond, 89 |
| `(2,6,3,8)` | 34,220 | 29,593 | 404,091 | 1,582 | no bond, 69 |

In both hosts the first differing literal quartet is `{0,3,28,30}` with image `{14,17,28,30}`. The source marks both anchor links of test middle `a`, the distinguished anchor's link to the first red shield, and that shield's red spoke. These marks put `a` and the red shield together, opposite both anchors and the red hub. That isolates `a` on a shore with another vertex. The image uses the test middle `c`, which can connect to the blue hub. A literal connected cut attains the recorded finite minimum. Four is the first distinguishing arity for these markings.

Both successor minima are attained by explicit literal connected-shore bonds. This replay verifies the given parameter choices. The global minimum over shield parameters, other hosts, or all reached arrangements is outside its scope.

## The entire marked group through arity four

The fourth-order reading also resolves every marked map of the four compact stages below. Each group size counts maps modulo permutations of parallel distinctions with identical holders. Those permutations preserve every equation and introduce no obstruction.

| Marked stage | Live distinctions fixed individually | Maps preserving pairs and triples | Maps also preserving quartets | Remaining maps carrying the full equation span |
| --- | ---: | ---: | ---: | ---: |
| 224 junctions, 700 distinctions | 360 | 24 | 4 | 4 |
| 176 junctions, 856 distinctions | 564 | 24 | 4 | 4 |
| 118 junctions, 504 distinctions | 290 | 24 | 4 | 4 |
| 104 junctions, 372 distinctions | 180 | 24 | 4 | 4 |

The 176-junction case uses the same host as the 224-junction one. Its red branches shrink from cost eight to one while the blue branches retain cost eight, as witnessed by distinct routes through both literal rounds. Its history is `(80,472)` to `(176,856)` to `(350,1870)`. For the 118-junction case the old exchange has 2,084 differing quartet orbits. The first is `{0,2,24,26}` with no containing bond, while its image `{12,14,24,26}` has minimum 50 and a recorded literal attaining bond.

For the 104-junction case the marked pair is `{4,10}` and its image is `{10,16}`. The replay checks all 34,220 current compressed triples and records 4,432 differing quartet orbits. The first quartet in the replay order is `{0,3,24,26}` with no containing bond. Its image `{12,15,24,26}` has a literal minimum bond of size 46. The separate quartet `{3,4,6,10}` has no containing bond and its image `{6,10,15,16}` has exact minimum 48. The latter source marks put both red test middles together, opposite their red hub and both anchors, leaving them disconnected.

Fixing every live distinction individually does not stipulate that the whole interior of a branch is fixed. To check it, compute each movable distinction's exact pair readings to every fixed name. For a query confined to one branch the oracle includes its same-terminal bonds, with a virtual connector for the complementary piece, and its separating bonds plus the unmarked separating cost in that complementary piece. This calculation pins every branch-interior column in all four cases. In the host the only ambiguous classes are eight hot columns and four weak names. To identify the hot columns, test whether the minimum through two labels and an invariant probe agrees with the minimum through either label and that probe. Distinct labels from the same column always satisfy these equalities. The checker finds a probe distinguishing every pair of unlike hot columns. Thus the triple readings recover the identical-holder relation without supplying the flip bits.

The remaining enumeration ranges over physical-column maps, allowing all assignments that meet the exact pair constraints. Every complete branch-fixed map can then be tested on the compressed readings at each arity. A fixed literal name on a minimum separating bond represents a marked branch, including in the blue branches where the chosen name was taken in the first round. This realizes each discriminating compressed query literally. The 24 candidates all keep the triples, and each of the 20 changing the equation span fails a quartet. Exact GF(2) reduction certifies the four survivors on every literal junction row. Those four therefore extend to later complete rounds. This is a result for the full groups of these four marked fixtures.

```bash
.venv/bin/python -B experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform.py --params 2 6 3 8
.venv/bin/python -B experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform.py --full-branch --params 2 5 3 14 --params 2 6 3 8
.venv/bin/python -B experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group.py
.venv/bin/python -B experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group.py --hybrid
.venv/bin/python -B experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group.py --hybrid-params 2 5 3 2 8 6
.venv/bin/python -B experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group.py --hybrid-params 2 6 2 3 6 4
```

[Compact literal replay](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_compact.json) · [Both linear-branch replays](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform.json) · [224-stage marked group](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group.json) · [176-stage marked group](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group_hybrid.json) · [118-stage replay and marked group](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group_small.json) · [104-stage replay and marked group](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group_104.json)
