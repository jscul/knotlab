# A smaller reached failure of the triple reading

A start of **128 junctions and 604 distinctions** gives a marked stage of **224 junctions and 700 distinctions**. Its specified renaming fixes every distinction in every live junction and preserves the complete pair and triple readings, including absence of a common bond. It carries the old pair `(0,7)` to `(7,14)`. Both pairs currently have minimum bond size 26. One complete round later their minimum sizes are **24 and 26**, so every naming of the fresh distinctions fails. In the marked stage the four-set `(0,3,7,13)` has no common bond and its image `(7,13,14,17)` has minimum size 74. Order four is therefore the first that distinguishes this matching. [Literal history, permutation and minimizing supports](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/census_shields.json)

The parameters are two anchors, six attached middle junctions on each hub, multiplicity three on the four distinguished mids' hub and main anchor connections, and a growing branch with capacity eight at each attached middle. The twelve branch capacities drop together from eight to one at age two. The largest literal support holds 54 distinctions. The allowed change supported on `(0,3,7,10)` meets the moved hub equation oddly, so the same permutation changes the equation span at every replayed stage. It preserves the pair flip reading through equality of the exact holder classes. [Construction and all-size result](../../proofs/LATER-BOND-READING-20261119-001A/LATER-BOND-READING-20261119-001A-P001_future/proof.md)

| Complete rounds | Junctions | Distinctions | Each attachment's separating cost |
|---|---:|---:|---:|
| 0 | 128 | 604 | 8 |
| 1 | 224 | 700 | 8 |
| 2 | 236 | 712 | 1 |
| 3 | 248 | 736 | 1 |

## Exact bounds on the smaller example

The parameter grid ranges over 1–4 anchors, 1–8 attached middle junctions of each color, distinguished multiplicity 1–8, and attached-branch capacity 2–18. The cutoff is 328 current junctions using the smaller literal branch with `M+1` starting junctions and `5M−2` starting distinctions for `M ≥ 4`, and the earlier smaller recipes at capacities two and three. Of 4,352 tuples, 864 exceed the current size bound and 3,378 give admissible starts within it. The selected old pair changes in 2,875 cases. Of those, 1,832 fail a tested current pair, 824 fail a fixed current triple, and 100 fail another triple. The remaining 119 preserve every current pair and triple. The reported example is smallest in this grid by marked junction count and then marked distinction count. The earlier rectangle with capacities two and three, at most three attached middles of each color and the same anchor and multiplicity bounds gives 186 admissible starts, all separated by the present pair reading.

For a marked query involving a moved distinction, replace each independent branch by one virtual distinction weighted by its minimum separating cost. A marked branch must cross this cut. Its internal marked minimum adds a fixed surcharge that is shared by the query and its image. The same calculation covers lack of a feasible cut. Within a repeated ordinary meeting, every cut crosses the whole bundle or none of it. These reductions account for all literal pair and triple queries, even when two marks reduce to one name. Terms with every name fixed require no comparison.

In the grid, permutations of identical attached middles of each color and of the ordinary weak anchors fix the geometry and commute with the proposed renaming. For an order-three comparison with a moved mark, at most two marks select attached middles. Keep the marked sites individually and enumerate the two shores by counts of the others. For the smallest hit, a second calculation uses all 1,048,575 ordinary shores and all 620,485 connected cuts with no quotient. It checks 3 changed singletons, 168 changed pairs and 4,627 changed triples, counting one comparison per pair of marked sets carried to one another. The two cut calculations also agree on the reported four-mark query. The production growth code and separate parent and demand replay recover the literal history. Integer flow checks all attachment capacities, and the minimizing cuts lift to connected cuts on both shores in the literal presentation. [Exact grid and independent checks](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/census_shields.json)

## One anchor and all 24 named permutations

With only the anchor `v`, choose any color-zero attached middle `z`. Mark one distinction in each meeting from `h₀` to `a`, from `h₀` to `z`, and from `z` to `v`. The last two marks force `h₀` and `v` onto the same shore. Both `a` and `z` must lie opposite, where `a` has no neighbor. This prevents a common bond. Under the displayed permutation the first mark belongs to the `h₁,c` meeting. The shore consisting of `h₀,v,a,b,c` is connected. The other is connected through `h₁,d`, the attached middles and the exterior. This gives a finite reading for the image at every positive multiplicity and every positive number of attached middles of each color. The checker also verifies this obstruction for each of the eight tested attachment counts.

At the 224-junction example, all **24 permutations of the four distinguished middles**, with their incidences carried by copy and all other distinctions fixed, preserve the full current readings through order three. The within-color switches and the verified cross-color switch generate all 24. There are three sets of permutations obtained by composing a representative with within-color switches on either side. Their sizes are 4, 4 and 16. The displayed four-mark query excludes the 16 permutations that mix the color pairs. Exchanging the two whole colors takes `(0,3,28,37)` with no common bond to `(14,17,28,37)` with minimum size 73, excluding the second set of four. The **four within-color permutations** preserve the physical incidence and extend through every later round. Thus four marks suffice to select the extenders in this 24-permutation comparison. [Group records and both four-mark tests](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/census_shields.json)

## A different split-core stress test

An earlier lane fixes three or four vertices of the folded ordinary core while interchanging two other vertices with identical sets of neighbors among them. It permits every meeting among the fixed vertices and either choice of whether the interchanged vertices meet. It then splits the first fixed junction, separating the two moved incidences, ranges over the other incident assignments, and attaches separate growing branches at both halves and at one or two other fixed junctions. Every legal branch assignment of kinds one through five was tested at positive ages one through four, with future profiles available through age five. The selection checks 7,262 non-equational core and attachment choices, 2,637,594 legal branch assignments, and 10,550,376 marked stages. There are 5,376 current pair-preserving stages and zero current triple-preserving stages for this planted move. Counts use the labelled choices in this construction. A literal capacity control independently replays all five branch kinds and measures the changes from `[1,2,3,4,5]` to `[1,1,1,4,5]`, then `[1,1,1,1,5]` and finally `[1,1,1,1,1]`. A separate three-attachment control preserves the current pairs, fails a current triple with infinity versus four, and fails a successor old pair with four versus three. [Independent-attachment census and controls](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/census_interfaces.json)

## Reproduction

Run from the repository root. The shield grid finished all 32 jobs in about 34 seconds with six shared-runner workers. The release checks took another 14 seconds, with 241,000 KiB peak memory. The independent attachment comparison uses C++20 and four workers.

```bash
family=experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future
scratch=$(mktemp -d)
python3 -B scripts/longrun.py launch "$family/census_shields.py" --out "$scratch/shields" \
  --unit later-bond-shield-lean --workers 6 --case-timeout 120 --case-mem 550M --mem-max 5G --prepare-only
python3 -B scripts/longrun.py run --out "$scratch/shields" --foreground
python3 -B "$family/census_shields.py" "$scratch/shields"

python3 -B "$family/census_interfaces.py" prepare "$scratch"
python3 -B scripts/longrun.py launch "$family/census_interfaces.py" --out "$scratch/independent" \
  --unit later-bond-independent --workers 4 --case-timeout 120 --case-mem 250M --mem-max 3G \
  --param engine="$scratch/census_interfaces" --prepare-only
python3 -B scripts/longrun.py run --out "$scratch/independent" --foreground
python3 -B "$family/census_interfaces.py" collect "$scratch/independent"
```
