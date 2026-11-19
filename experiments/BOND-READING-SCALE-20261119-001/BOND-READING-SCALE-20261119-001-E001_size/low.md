# Small reached witnesses and a pair-reading minimum by current width

Let \(J\) count current ordinary junctions and \(n\) count current literal distinctions. The growing end is fixed pointwise by a single specified old permutation. In this note \(K\) is the minimum common bond cardinality, with infinity when no bond exists. Pair bond distance is \(K-1\) when finite. The two-round delayed controls below report pair bond distances.

| Present reading | Future discrepancy | Repeated meetings allowed, current \((J,n)\) | Meet once, current \((J,n)\) |
|---|---|---|---|
| Pairs | Immediately next pair | (10,21), sharp in width | (12,23), both sharp for this comparison |
| Pairs | First pair break two rounds later | (9,21) | (11,23) |
| Pairs and triples | Immediately next pair | (96,368) | (200,536) |
| Pairs and triples | Immediately next old triple, with every next pair carried | (84,362) | (197,545) |
| Pairs and triples | Old quartet separates and all later pairs and triples carry | (21,189) and (23,173) | (136,356) |

The remaining rows give witnessed upper bounds. Each between-round discrepancy uses old names. The earlier meet-once minimum applies to the immediately next pair comparison. [Meet-once minima](../../../proofs/GROWN-END-MEET-ONCE-20261119-001A/GROWN-END-MEET-ONCE-20261119-001A-P001_pointwise/proof.md#minimum-reached-size-by-exhaustive-calculation)

## Weighted immediate predecessors for pair transport

The all-age check for the immediately next pair comparison completed **438,040** weighted predecessor allocations through current width 20. It found zero nonextensions and zero unresolved cases. The global minimum immediately failing width with repeated meetings allowed is therefore **21**, attained by the known 10-junction witness. The joint panel \(J\le10,n\le21\) checked **1,518,991** allocations and found exactly one failure, at \((10,21)\). The counts use ordinary simple support representatives and labeled edge multiplicities and loose allocations on each representative. Some equivalent configurations occur more than once. [Width and joint panel](../../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low_repeat.json) · [Original width-21 witness](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json)

The observed stage has a connected ordinary immediate predecessor even at arbitrarily large age. The classical holder graph of that predecessor is connected after deleting any ordinary holder with the exterior wired to all loose holders. This is exactly the condition that the corresponding parity row is a bond. The enumeration uses every connected ordinary support and every legal choice of its live vertices. Positive multiplicities on the ordinary links do not change candidate groups, the loose demands, or the inferred number of fresh distinctions. After reserving the required inputs, distributing extra loose distinctions enumerates the unary births. For each resulting shape the exact new count fixes the width budget for arbitrary predecessor multiplicities. The weighted arity floor is enforced at each ordinary junction.

At most two newborn junctions give the previously proved safe cases for the next pair table. The proof uses only one shared input per parent of a newborn and the old parity projection gate, and allows parallel meetings between earlier sites. Every remaining case has at least three live loose distinctions at observation, so the arity sum gives \(3J+3\le 2n\). With at least three births, the total weight of the predecessor's ordinary edges is at most \(n-6\), before imposing stronger arity and output-count bounds. These two inequalities justify the current-junction and predecessor edge caps. Positive-age history length is unrestricted in the immediate comparison.

The pair checker builds full stabilizer-chain representatives, fixing the new live supports pointwise. It first tests equation transport on the group of pair readings pooled above bond size six. If that group is inconclusive, it calculates every generator of the exact pair group, with present missing bonds kept distinct. The span test is on literal names, so it covers maps that split a class of parallel distinctions. Equation-preserving generators extend by the identity on fresh names. For the others the checker tests the entire next table, including exact fresh renaming when needed. The next-only comparison can pass while the equation span changes. At width 20, 89,904 cases passed by an exact successor test after the span check found a noncarrying generator.

A separate panel omitted the width cap and allowed at most two ordinary meetings per holder pair. It completed **200,941** allocations through eight current junctions without a failure. Across the completed portions through nine it scored 2,825,636 allocations without a failure. Five shards timed out, all at six predecessor junctions and all restricted to nine current junctions. They cover 40 simple predecessor supports. This leaves the nine-junction tier and the unrestricted repeated-meeting minimum by \(J\) open. The archive lists each omitted graph-stream interval. [Partial no-width-cap panel](../../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low_repeat_partial_m2.json)

The two-newborn cases also preserve the supplied order in every later round. If the two live junctions have no common parent, their future families grow independently and each has one or two initial loose distinctions. One supplies a fixed unit cut. From two inputs at one root, the new living family starts with two sites, each with two loose distinctions. The next joins are along the path of pairwise-backed sites, with one unary birth at each end. The resulting family again has a path as its candidate graph and two loose distinctions at each site. Induction gives two disjoint routes from the root to the exterior, one along each succession of end sites. This retains separating cost two. The marked substitution formula for each branch preserves the whole supplied order. If the two live sites have a common parent and one loose distinction each, the next round closes by replacing the exterior with the implied junction. If their loose counts are one and two, the next counts are again one and two with a common parent. With the new pair junction treated as the old exterior, this round replaces the spare fixed loose distinction by a two-terminal series of capacities one, two, and one. The same unit substitution applies on each iteration. Two unary births with a common parent and two loose distinctions each would violate the earlier arity or full parity projection gates. Thus an any-later pair failure needs at least six current junctions: below six, at least three newborns leave at most two predecessors, and permuting the movable parallel distinctions between those two holders already preserves their equations.

## Delayed pair failures

The repeated-meeting construction has a middle junction meeting each of two terminals twice. At the start one terminal has three loose distinctions. The other is joined twice to a holder with two loose distinctions. From its first observation the full current table agrees under an exchange of one distinction at each terminal. It still agrees one round later. On the third complete round the three descendants on the first terminal's side join with one fresh distinction. The chosen old pair breaks. The same timing works in the meet-once construction, using the ordinary graph known as a diamond for the four core junctions. At the second terminal, two extra holders meet each other and that terminal. They have loose counts two and one. The first adds one pair and one unary junction on that side, and their terminal cost remains two through the tested rounds.

| Meeting convention | Age one \((J,n)\) | Age two \((J,n)\) | Age three \((J,n)\) | Bond distances of old pair and image |
|---|---:|---:|---:|---|
| Repetitions allowed | (9,21) | (15,30) | (20,39) | 3 and 3, then 3 and 3, then 2 and 3 |
| Meet once | (11,23) | (16,29) | (19,33) | 3 and 3, then 3 and 3, then 2 and 3 |

Every pair was measured directly at each listed age, with four changed pairs in the final stage of either history. The marks \(\{0,1\}\) and \(\{1,2\}\) are already shared at the start. Independent reconstruction verifies each complete round. [Literal histories and bonds](../../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low_delayed.json)

## One or a few contracting branches after the triple reading

Use the two earlier weighted shield hosts, with current separations measured by connected cuts in their complete boundary graph. Leave the blue branches stable. Within the red type, choose exactly \(k\) contracting branches and replace every other branch by a price-preserving one. It is enough to test one subset at each \(k\) because permutations within the red type commute with the mark. At price four the stable branch begins as one holder joined four times to its pole, with four loose distinctions. Four unary first births give four disjoint routes. The next six pair births retain four routes through the cyclic consecutive pairs. The price-six version uses six unary and then fifteen pair births. Every literal branch price and both independent complete rounds were checked on the named witnesses.

The old full pair and triple tables stay unchanged under the specified map because all marked exterior costs in the virtual boundary reading were compared. Physical branch marks add their fixed marked separating surcharge to the corresponding virtual marks, with the same correction on each side of the permutation. That formula applies at the successor too. Equality of every successor virtual pair therefore carries every physical successor pair, fixing every fresh name. The first pair and triple discrepancies are on purely internal old named distinctions.

| Original host | Earliest contracted-red count for a pair | Its current \((J,n)\) | First contracted-red count for a triple | Its current \((J,n)\) |
|---|---:|---:|---:|---:|
| Price four, six red shields | 4 | (96,368) | 1 | (84,362) |
| Price six, five red shields | 3 | (106,520) | 1 | (94,536) |

At \((96,368)\), the pair \(\{0,48\}\) and its image \(\{10,48\}\) read \(K=30,30\) and then \(28,30\). At \((84,362)\), every successor pair agrees, while \(\{0,27,34\}\) and \(\{10,27,34\}\) read \(K=40,40\) and then \(37,40\). The archive gives every tested \(k\), all full comparison counts, and the complete literal histories of the earliest pair and triple cases in each host. [Partial-branch search and certificates](../../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low_partial.json)

## A small persistent quartet difference

Close the exact weighted boundary of each earlier shield host by treating its wired exterior as an ordinary junction. It has the complete preserved pair and triple readings. Remove a fixed distinction at the fourth test junction and give each of its two former holders one loose distinction. They have no common ordinary witness, so they produce two unary births with independent descendants. The new exterior has those two endpoints, stays connected, and retains a terminal cut of one through either fixed first input. The same-terminal and mixed bond formulas for replacing one fixed distinction at unit separating cost give every later pair and triple reading. A pure old quartet gives infinity and 48 at \((23,173)\), and infinity and 52 at \((21,189)\). The same replacement leaves those pure old readings unchanged at each later age. The old first hub support stays a bond, while its image meets a fixed old four-distinction cycle oddly. Every later junction meets that cycle evenly, so the image stays outside the equation space. The two hosts give separate upper bounds by \(J\) and by \(n\).

The separate complete-four-holder illustrations use a pair-table permutation that exchanges two opposite distinctions and fixes the distinction used for the unit replacement. It sends one three-distinction star to three distinctions of a cycle and exposes a missing bond. The complete literal illustrations have \((7,13)\) with repeated meetings and \((8,15)\) with meet once, with all later pairs carried and a persistent triple reading of three versus infinity. [Static-to-growing controls](../../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low_all_order.json)

## Compact meet-once constructions

For each repeated ordinary holder pair retain one direct distinction. Replace its remaining \(k\) distinctions by a closed simple part of terminal cost \(k\). For \(k\ge2\), add \(k\) ordinary junctions each meeting both old holders, with a matching of internal links and one three-junction path in place of one pair when \(k\) is odd. Every new internal junction has arity at least three. The \(k\) disjoint two-step routes give the cut lower bound, attained by keeping every internal junction with one terminal. For \(k=1\), insert a triangle of three junctions, two connected to one terminal and the third to the other. Each sees just one old holder, and the terminal cut has size one.

Every cost-\(k\) replacement with \(k\ge2\) used here has at least one exhausted terminal at the start. Retaining the direct distinction keeps all old ordinary adjacencies. The new closed parts create no additional candidate groups of live holders. The inherited law therefore makes the same newborn supports after relabeling, as separately confirmed by two literal engines. The marked substitution proof uses one old name to mark a replaced part, irrespective of the number of marked names chosen inside it. When the two terminals are together, old paths through their retained direct distinction keep the connectivity test invariant. The old permutations transport the identical parts with their marked separating costs unchanged. Hence they preserve the full stated reading. The failing marks use retained direct names, and their bond minima follow from the same cut formula at every measured age. [Expanded histories and marks](../../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low_lift.json)

## Replay

Run from the repository root with the project Python environment. The weighted population uses nauty 2.8.9. Use `--geng` for an alternate executable, and `--geng-library` for a library directory only if needed by that installation.

```sh
family=experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size
scratch=$(mktemp -d)
.venv/bin/python -B "$family/low_delayed.py"
for host in 104 118; do
  .venv/bin/python -B "$family/low_partial.py" --host "$host" > "$scratch/partial-$host.json"
done
.venv/bin/python -B "$family/low_all_order.py" > "$scratch/all-order.json"
.venv/bin/python -B "$family/low_lift.py" "$scratch/partial-104.json" "$scratch/all-order.json"
for panel in 20:12 21:10; do
  width=${panel%:*}
  junctions=${panel#*:}
  .venv/bin/python -B "$family/low_repeat.py" prepare "$scratch/pop-$width" --width "$width" --junctions "$junctions"
  .venv/bin/python -B scripts/longrun.py launch "$family/low_repeat.py" --out "$scratch/run-$width" \
    --unit "bond-scale-repeat-$width" --workers 4 --case-timeout 180 --case-mem 350M --mem-max 3G \
    --prepare-only --param folder="$scratch/pop-$width" --param width="$width" --param junctions="$junctions" --param shard=32
  .venv/bin/python -B scripts/longrun.py run --out "$scratch/run-$width" --foreground
  .venv/bin/python -B "$family/low_repeat.py" collect "$scratch/run-$width" > "$scratch/repeat-$width.json"
done
.venv/bin/python -B "$family/low_repeat_control.py" "$scratch/repeat-20.json" "$scratch/repeat-21.json"
```

For the partial no-width-cap panel, prepare with `--width 0 --junctions 9` and use runner parameters `width=0`, `junctions=9`, `multiplicity=2`, and `shard=8`. The `collect --partial` mode names every omitted interval.
