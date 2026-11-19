# A smaller reached failure with one side growing differently

A **104-junction** reached stage preserves the entire pair and triple bond reading under a permutation fixing the live supports pointwise, yet its next pair table disagrees on two already shared names. The history has junction and distinction counts $(56,276)$, $(104,372)$, and $(146,450)$. The pair of names $\{0,5\}$ and its image $\{10,5\}$ have bond cardinalities **24 and 24** at observation and **22 and 24** after the next complete round. This is the smallest marked case in the bounded parameter comparison below. [Literal histories and bonds](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/weighted_shield_literal.json)

## The 104-junction arrangement

Use the classical holder graph. There are two ordinary hubs, two common ordinary anchors $v,r$, and four test junctions $a,b,c,d$. Junctions $a,b$ meet the first hub and $c,d$ the second. Each test junction has two distinctions shared with its hub, three with $v$, and one with $r$. Each hub additionally meets six shield junctions, with six distinctions each. Each shield also meets each common anchor once, and separately attaches to a growing branch. At observation the minimum cut between any shield and the exterior through its own growing branch has size four. The permutation swaps the entire bundles at $a$ with those at $c$ in the corresponding order. Every other name is fixed, including all live supports and all exterior branch names.

The first hub's six branches use the two-leaf version of the shrinking gadget and each falls from capacity four to one. The other six branches each use one old parent with four parallel distinctions to its shield and four loose distinctions. Four unary junctions form at the first round. In the next round their six pairs each give two fresh distinctions. The four disjoint routes through four cyclic pairs retain capacity four. Both rounds were reconstructed independently from the literal supports, and exact minimum cuts check each branch at all three stages. [Shrinking gadget](../../../research/LATER-BOND-READING-20261119-001/boundary-proof.md#a-synchronous-branch-of-linear-size)

The fixed core and the abstract branches can be checked on a much smaller graph. Put one virtual connection of the measured cost in place of each branch. For any query with a moved core distinction, a compatible actual bond has core holders on both sides. A branch with poles together lies wholly on their side. A branch whose poles split must restrict to two connected parts, one containing each pole. A marked branch then contributes its least separating cut through its marked names in place of the unmarked virtual cost. This adds a fixed surcharge whenever its virtual marker is required. A missing marked separating cut gives an absent bond on both sides. All exterior names are fixed, so equal virtual readings imply equal physical readings on every old query of at most three names. Repeated names from one parallel class ask for the same crossings as a single representative.

The decisive pair uses one hub distinction of $a$ and one of $b$. A later cut keeps the first hub and all six of its shields together. It cuts four test distinctions and three distinctions per shield, costing $4+6\cdot3=22$. Exact connected cuts give the minimum 24 on the image. The old quartet $\{0,2,5,105\}$ marks one hub distinction of $a$, one $v$ distinction of $a$, and the hub and weak-anchor distinctions of $b$. Its crossings isolate both $a$ and $b$ on the same side, so it has no common bond. Its image $\{10,12,5,105\}$ has a common bond of size 48. The archive lifts all finite decisive minima to actual physical bond supports and checks that deletion of each lifted support gives exactly its two connected parts. The successor disagreement occurs on old names, so every assignment of fresh names inherits it.

## Extent of the searches

The small-price search first examined 147,264 weighted decks with one shield per hub, an optional weak relay, and a possible absent fourth test. The prescribed map preserves the old lower and pair readings on 1,036 of them. These give 3,108 target-pair breaks across the three patterns of exterior reduction, each rejected by an old triple. The separate search with one to three shields on each side and either no weak relay or a weak relay joining every middle examined 87,536 exact weighted decks surviving the absence-of-bond filter. None preserve the old pairs.

The optimization around the successful host is exhaustive in the panels below. It has one common weak relay and all four test junctions. Test-to-hub and test-to-$v$ widths vary independently in $1,\ldots,4$. The two permanent shield-to-hub widths vary independently in $1,\ldots,16$, and the two exterior costs in $2,\ldots,14$. Individual shields of the same color agree in their widths. The first hub's branches all shrink, and the second hub's stay stable. The size bound uses the named branch realizations above or the corresponding two- or three-child small-price versions.

| Shields at red and blue hubs | Marked size cap | Parameter assignments | Full old survivors with a later target failure | Smallest marked witness |
|---|---:|---:|---:|---:|
| 4, 4 | 240 | 692,224 | 0 | — |
| 4, 5 | 240 | 692,224 | 0 | — |
| 5, 4 | 240 | 692,224 | 0 | — |
| 5, 5 | 240 | 692,224 | 7,517 | 118 |
| 5, 6 | 118 | 147,456 | 0 | — |
| 6, 5 | 118 | 139,264 | 0 | — |
| 6, 6 | 118 | 106,496 | 13 | 104 |

The 5,5 panel also replays within the 118 cap using a second representation of cut costs, retaining three witnesses. The other panels with 6 shields were completed through the 118 cap. The optimization keeps two individually marked shields of each color because a changed triple must include a moved test name. Unmarked shields of one color have identical neighborhoods. If they occupy both sides of a cut, connectivity uses only the presence of at least one on each side. Minimizing their linear cost over that split needs only the two extreme allocations. Thus one copy of each side's extreme multiplicity suffices in the cut enumeration. A candidate bond through a moved test name cannot isolate an unmarked proxy holder. For four marks the method keeps three explicit shields of each color. The literal threshold checks enumerate cuts with all ordinary holders present.

The selected hub pair needs all six red reductions in the 6,6 host with test widths 3,3 and exterior costs 8,8, and all five in the 118-junction example. The exact controls also reject combining all stable blue branches of the former host into a single stem. With a new common pole or the blue hub as the pole, marking the stem with the target pair gives cost $C+18$ and $C+26$. At $v$ or $r$, a pair with the stem suffices, with costs $C+18$ versus $C+25$ or $C+21$. All cuts through the stem pay its positive cost $C$, so these differences hold at every positive stem cost for each of the four tested layouts. [Parameter panels and controls](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/weighted_shield.json)

## Replay

```sh
family=experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future
.venv/bin/python -B "$family/weighted_shield.py" --prices 2 3
.venv/bin/python -B "$family/weighted_shield_grouped.py"
for panel in 4:4 4:5 5:4 5:5; do
  .venv/bin/python -B "$family/weighted_shield_optimize.py" --shields "${panel%:*}" "${panel#*:}"
done
for panel in 5:5 5:6 6:5 6:6; do
  .venv/bin/python -B "$family/weighted_shield_optimize.py" --shields "${panel%:*}" "${panel#*:}" --cap 118
done
.venv/bin/python -B "$family/weighted_shield_literal.py" --counts 6 6 --test 2 3 --hubs 6 6 --costs 4 4
.venv/bin/python -B "$family/weighted_shield_shared.py"
```
