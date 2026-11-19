# Equation transport from pair and triple bond readings

Every self-permutation preserving the full pair and triple bond distance tables and fixing every live support pointwise carried the parity-equation span in all **30,189 open reached stages** from **33,430 admissible starts**. This covers each positive age through 16 current junctions from canonical meet-once starts of 3 through 15 distinctions. The observed ages run from one to six, and the observed current widths reach 225. The search matched every stage and termination stratum of the archived census. [Frozen design](../../../research/GROWN-END-READING-20261119-001/preregistration.md) · [Archived population](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/census_results.json)

The parity-equation span and the fixed supports suffice to extend each permutation through every later complete round. Every new support consists of distinctions taken from the fixed old live supports and fresh distinctions, which the extension fixes as well. It carries the span of the old and new equations and fixes each new live support. Induction gives the next complete bond tables throughout the lawful continuation. [Claim B*](../../../research/EXTEND-ROUND-20261119-001/extend_round.md)

## Complete marked groups

Let $K(A)$ be the minimum cardinality of a bond containing the distinct queried names $A$, or infinity when there is no common bond. The corresponding bond distance for a finite reading is $K(A)-1$. The engine enumerates cuts of the graph representation that have connected complementary sides. It counts every distinction in a cut, including all parallel loose distinctions in its wired exterior. In this representation the vertices are junctions plus one exterior holder and the edges are distinctions. A query containing two names in one parallel class has the same cut constraint as a query containing either one. A movable name is shared by two nonlive holders and belongs to a singleton class by meet-once. With all names at live holders fixed, the nontrivial coordinate flips are already fixed too. The flip through exactly two names is allowed precisely when their incidence columns agree, and every pair with agreeing columns is a fixed pair of parallel loose names.

For each reading the engine finds one representative for every image of the next movable name under its stabilizer fixing the earlier names. Accepting a representative requires full consistency of the selected pair and triple readings, including entries involving fixed names. These representatives generate that entire marked group. Testing the parity span on the representatives is sufficient because the maps that carry it form a subgroup. When a coarser reading gives a span-carrying group, every finer subgroup carries it too.

| Sufficient certificate | Open stages |
|---|---:|
| At most one movable name | 49 |
| Pair bond cardinalities pooled above six | 22,896 |
| Full pair readings | 82 |
| Full pairs and triple bond cardinalities pooled above six | 7,131 |
| Full pairs and full triple readings | 31 |
| **Total** | **30,189** |

All 117 representatives at the 31 final cases carry the parity span. The independent replays cover every one of those cases. They rebuild the current arrangement with the original grower, enumerate the support-minimal words of the parity span, and compare all 17,225 pair readings and 201,780 triple readings, including infinite entries. They list the full marked pair group and select its members satisfying each triple reading, yielding 495 maps preserving the full pair and triple readings across the 31 cases. For each case the closure of the engine's representatives agrees with the listed group. Six further controls cover both archived one-round failures, all three minimum meet-once failures, and parallel fixed distinctions. The exact triple group carries the span in each. [Full minimum census](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/carry_census.json) · [Independent replays](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/carry_census_controls.json)

## Triple existence and equation transport

Keeping every pair bond distance and merely whether a common bond exists for each triple leaves non-span-carrying maps in **160 of the same 30,189 stages**. There are 382 noncarrying representatives of the exact existence groups and zero ungraded stages. The smallest failing case in current junction count and then width has eight junctions and 15 distinctions, one round from a six-junction, width-13 start. Its current supports are below. The first six are the starting supports.

```text
(0 1 2)  (0 3 4)  (5 6 9)  (7 8 10)
(1 3 5 7 11)  (2 4 6 8 12)
(9 10 13)  (11 12 14)
```

Swapping 5 and 6 fixes the live supports and preserves all 105 pair readings and the existence reading on all 455 triples. It sends the equation on {1,3,5,7,11} to the unsupported word {1,3,6,7,11}. The triple {0,5,7} has bond distance 5 and its image {0,6,7} has bond distance 6. The independent literal replay finds 32 marked pair maps, 16 preserving triple existence, and four preserving full triple minima. The 16 include 12 maps changing the span. All four full-minimum maps carry it. Both previously reported one-round failures are already removed by the existence reading. [Existence census and smallest witness](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/carry_census_existence.json)

### Future pair readings of this witness

The smallest noncarrying swap extends to each later complete round's pair table by fixing every fresh name. At observation, the two live holders have one loose distinction each, 13 and 14, and their sets of ordinary neighbors are disjoint. Thus the next births are unary. The descendants of those two births can never join in a single junction. A common witness of two live holders would have to be a parent of both. Each later live holder meets only parents of its own branch, by induction on the complete rounds.

In the graph representation each branch replaces one old exterior wire $e$ by a two-terminal network. Its poles are the old holder of $e$ and the exterior, and the retained first wire $e$ is a cut of size one separating the old pole from the whole branch. Any bond through a moved original distinction has old holders on both sides. If the two poles of a branch are on the same side of that bond, every vertex of the branch lies on that side. If the poles are opposite, each side inside the branch connects to its own pole. Projecting this bond onto the old holders restores each split wire, giving a bond in the original arrangement. Conversely an old bond can be lifted by independent connected terminal cuts for its split wires, each at minimum cost one.

For a queried fixed distinction $b$ in the branch of $e$, let $\sigma_e(b)$ be the minimum size of a connected terminal cut containing $b$, with infinity for absence. For a moved old distinction $a$, projection and lifting give $K_{\mathrm{later}}(\{a,b\}) = K_{\mathrm{old}}(\{a,e\}) + \sigma_e(b) - 1$. The old pair reads the same after the swap because $e$ is fixed. This also applies to the retained wire itself with local cost one. Old pairs outside the two branches retain their readings by the same projection and lifting. Pairs of fixed names are unchanged under the proposed continuation. The independent grower and two exact cut engines check all pair entries at the first three later stages, with sizes $(10,19)$, $(14,27)$ and $(20,39)$. This gives a persistent pair symmetry for this particular map alongside its failure of equation transport.

## Replay

Run from the repository root with C++20 and the project Python environment. The census and its replay agree byte for byte for each reading, with 349 successful shards each. The minimum census took about three seconds, and the existence census about four seconds, after compilation and roster preparation.

```bash
family=experiments/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings
scratch=$(mktemp -d)
.venv/bin/python -B "$family/carry_census.py" prepare "$scratch"
for reading in minimum existence; do
  .venv/bin/python -B scripts/longrun.py launch "$family/carry_census.py" \
    --out "$scratch/$reading" --unit "grown-end-carry-$reading" --workers 6 \
    --case-timeout 120 --case-mem 350M --mem-max 4G --prepare-only \
    --param engine="$scratch/carry_census" --param roster="$scratch/starts15.txt" \
    --param reading="$reading"
  .venv/bin/python -B scripts/longrun.py run --out "$scratch/$reading" --foreground
  .venv/bin/python -B "$family/carry_census.py" collect "$scratch/$reading" "$scratch/$reading.json"
  .venv/bin/python -B "$family/carry_census.py" residuals "$scratch/carry_census" "$scratch/$reading.json"
done
.venv/bin/python -B "$family/carry_census.py" controls "$scratch/carry_census"
.venv/bin/python -B "$family/carry_census.py" trace "$scratch/census" "$scratch/existence.json"
```
