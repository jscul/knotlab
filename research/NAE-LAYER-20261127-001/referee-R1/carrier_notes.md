# Three separately carried values after one ordinary birth

The three-knot ring with one loose distinction per knot is entry 17 in the zero-based census. The supports below use a numbering that exchanges 0 and 1 in the archived start.

| Source knots | Ordinary first birth | Carried values |
| --- | --- | --- |
| (0,1,3), (1,2,4), (2,0,5) | (3,4,5,6) | \(f=[1=5],\ g=[2=3],\ h=[0=4=6]\) |

The numbers inside brackets name distinctions. A bracket gives 1 when their values agree. Each source knot contributes its only loose distinction. The new knot has one private fresh distinction, 6. Before growth the three equalities on the opposite pairs take all eight triples on 26 states. They still take all eight on the 44 grown states. Including 6 in the last reading gives exactly seven triples, with **001 missing**. The stage's only loose distinction takes both values. These are the same two of two loose patterns that the closed record reports.

To check the missing triple by hand, suppose \(f=g=0\) and \(h=1\). Complement every distinction if needed so 0, 4 and 6 all have value zero. Let \(v,w\) be the values of 1 and 2. Then 5 has value \(1-v\) and 3 has value \(1-w\). The first source law excludes \((v,w)=(0,1)\), the second excludes \((0,0)\), and the third excludes \((1,0)\). The birth law excludes the remaining pair \((1,1)\). Removing any one of the four laws restores 001, so every proper subset of the laws allows all eight. Forgetting any one of the three carried values gives four pairs. The computed joint image passes K1–K3.

Complementing every distinction in an allowed state preserves all three readings. Thus even knowing the entire triple leaves every individual underlying distinction open. No single knot's values determine any one of the three functions. Fixing a knot can still restrict their joint range. Of 32 feasible local readings across the four knots, only two retain all seven triples. Fixing the birth to each of its 14 feasible readings leaves two or three triples. The 44 states are connected by single-distinction changes. There are respectively 22, 22 and 26 such changes that alter \(f,g,h\), counting each change in one direction. The three supports are disjoint. Reading them on three disjoint groups of knots requires a different example below.

Pair each source shared distinction with the loose distinction of its one nonholder. The new distinction can extend any one of the three resulting pairs. Permuting the source knots exchanges these three choices. An enumeration considered all 105 partitions of the grown stage's seven distinctions into sizes two, two and three. On each support it used every binary reading unchanged by global complement and depending on every place, identifying readings exchanged by an output flip. A pair has one such reading and a triple has four. Of the 420 resulting triples, 120 pass the joint-state test, 18 lose their restriction on deletion of each law, and three also have every individual reading undetermined by any one knot. All three choices of the pair receiving 6 give the displayed relation up to renaming. The search chose this class of readings. Growth itself designates no one pair.

Following the same seven distinctions gives the same seven triples at rounds two, three and four, on five, seven and ten knots. At each stage, each of the first four laws remains essential and removing any later law preserves the seven triples. More generally, an ordinary birth here has a private fresh distinction. Any allowed old state extends by choosing a fresh value as needed in each new knot. This proves persistence of a fixed tuple image through every subsequent funded round.

## Two stronger readings of “separately carried”

- **Disjoint groups of knots.** Take a nine-knot ring with \(K_i=(x_i,x_{i+1},a_i,b_i)\), indices cyclic. Split it into three successive groups of three knots each. Each group reports 1 exactly when \(a_i=b_i=x_i\) at each of its knots. These disjoint groups use disjoint carrier supports. In isolation each group gives both values. Together they exclude only 111, which would require nine changes between successive shared values in a closed ring. For any requested triple with a zero group, alternate the shared values except at one knot of that group. In each zero group give one knot different loose values, including the knot where alternation fails. Everywhere else give both loose distinctions the preceding shared value. This realizes the requested triple. Removing any one of the nine laws restores 111 by allowing the alternation to fail there. All six choices of group offset and direction up to output order agree. The same carriers give seven triples through two ordinary rounds, on 18 and 27 knots. This relation is already present before growth. No one source knot suffices to read any of its three values.
- **Every feasible fixing of any one knot.** On a seven-knot ring with \(K_i=(x_i,x_{i+1},a_i)\), compare \(a_i\) with \(x_{i+3}\). The seven disjoint comparisons give 127 of 128 words on 2,186 states. If all agree, each triple of indices \(\{i,i+1,i+3\}\) would have to contain both values. Each of the seven indices belongs to three triples and each pair belongs to exactly one. Two indices meet at most five triples. Three indices either form a monochromatic triple themselves or meet only six triples, leaving another monochromatic triple. Applied to the smaller colour class, this excludes agreement everywhere. Removing any one law gives all 128 words. Group the comparisons into three sets of sizes two, two and three, with value 1 when every comparison in a group agrees. **All 105 choices** give exactly seven triples under **all 42** feasible single-knot fixings apiece. All seven source laws are essential for the displayed grouping. This ring stalls at the first ordinary round.

## Replay

The first calculation enumerates literal states and readings. The second checks individual patterns with clauses for not-all-equal and the equality readings. It also enumerates literal states on the first three small grown stages and on the seven-knot ring. The canonical checker takes the computed images. Growth uses the independently written [ordinary growth rule](growth_rule.py). The three-parent birth above also follows directly since the three live knots form one admissible group, spending all three loose distinctions.

From the repository root, run one command at a time. The first command in each pair times a prefix with the same method and memory cap. The three-partition search pilot took 0.0033 seconds for 12 of 420 readings. The small birth took 0.016 seconds for the source and first round. The nine-knot ring took 0.017 seconds for the source and first round. The seven-knot ring took 0.11 seconds including three of 105 groupings. Each full run finished in under one second.

```sh
r=research/NAE-LAYER-20261127-001/referee-R1
ulimit -v 2097152
.venv/bin/python -B "$r/carrier_search.py" --limit-partitions 3
.venv/bin/python -B "$r/carrier_search.py" --out "$r/carrier_search.json"
.venv/bin/python -B "$r/carrier_witness.py" birth --rounds 1
.venv/bin/python -B "$r/carrier_witness.py" birth --rounds 4 --out "$r/carrier_birth.json"
.venv/bin/python -B "$r/carrier_witness.py" nine --rounds 1
.venv/bin/python -B "$r/carrier_witness.py" nine --rounds 2 --out "$r/carrier_nine.json"
.venv/bin/python -B "$r/carrier_witness.py" seven --limit-partitions 3
.venv/bin/python -B "$r/carrier_witness.py" seven --out "$r/carrier_seven.json"
```

The nine-knot test chooses three groups by hand up to the stated symmetry. The seven-knot test chooses a cyclic comparison rule. These computations establish existence of exact relations under those readings. Selection of a unique reading by growth and iteration to a further layer remain open.
