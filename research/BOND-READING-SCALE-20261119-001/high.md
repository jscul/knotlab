# Higher-order bounds and smaller literal witnesses

The comparison fixes a specified old permutation and every distinction in each live junction. Readings are minimum bond cardinalities, with a separate value for no common bond. The finite panels minimize marked junction count and then marked distinction count among parameters satisfying the folding certificate and the chosen future objective.

## A later pair must change

The smaller marked junction count at each tested order uses decreasing branches on one color and stable branches on the other. The table gives literal counts `(J,n)` and the minimum cardinalities of two matched old hub-spoke pairs. All their present readings through order `r` agree. The two successor cardinalities differ on old distinctions, so the result holds under every choice of fresh names.

| Present order `r` | Start | Marked stage | Successor | Current pair and image | Successor pair and image |
|---|---:|---:|---:|---:|---:|
| 4 | (144, 910) | (315, 1,360) | (504, 2,197) | 50, 50 | 48, 50 |
| 5 | (219, 1,469) | (472, 2,063) | (703, 3,020) | 80, 80 | 79, 80 |
| 6 | (347, 2,462) | (739, 3,316) | (1,033, 4,394) | 132, 132 | 130, 132 |
| 7 | (492, 3,772) | (1,132, 5,708) | (1,900, 10,396) | 182, 182 | 180, 182 |
| 8 | (709, 5,490) | (1,589, 7,830) | (2,407, 12,008) | 238, 238 | 236, 238 |

Letting both colors decrease gives these distinct size tradeoffs. The next pair and its image retain the same values as in the first table.

| `r` | Start | Marked stage | Successor |
|---|---:|---:|---:|
| 4 | (225, 1,162) | (405, 1,342) | (423, 1,360) |
| 5 | (340, 1,876) | (626, 2,162) | (648, 2,184) |
| 6 | (543, 3,148) | (1,019, 3,624) | (1,047, 3,652) |
| 7 | (812, 4,844) | (1,548, 5,580) | (1,580, 5,612) |
| 8 | (1,169, 7,070) | (2,249, 8,150) | (2,287, 8,188) |

Every example is first distinguished at present order `r+1`. Mark both the red hub and the main anchor incidences at one fixed red shield, and every anchor incidence at the blue test middle `c`. These marks force every anchor and the red hub together, and place the fixed shield and `c` opposite. The original shore can connect through the blue hub and the exterior. Moving `c` to `a` leaves `a` isolated on a shore that also contains the shield. The recorded finite cardinalities at orders 5–9 are 136, 220, 365, 545 and 787. The history, fixed names, old cycle witnessing the equation change, branch flows, and both later pair bonds were checked for each row. [Literal verification and exact panel records](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/high_results.json)

## When the later set can have any size

The same weighted shield host can be used with no capacity drop. Make the simulated exterior into an ordinary junction. Remove a fixed unit distinction joining a shield to a weak anchor and put one loose distinction at each of its endpoints. The endpoints lie in opposite parts of the incidence graph, so they have no common neighbor. The first complete round adds two unary junctions, for an overhead of two junctions and five distinctions over the closed host. The replacement keeps terminal cut cost one. The two-terminal formula therefore carries all future observations through order `r`. The old order-`r+1` finite-versus-absent query persists at the successor. This panel supplies a failure of the unrestricted later-table objective.

| `r` | Start | Marked stage | Successor | Later order `r+1` finite versus absent |
|---|---:|---:|---:|---:|
| 4 | (24, 651) | (26, 655) | (30, 663) | 176, absent |
| 5 | (29, 1,213) | (31, 1,217) | (35, 1,225) | 325, absent |
| 6 | (34, 2,031) | (36, 2,035) | (40, 2,043) | 540, absent |
| 7 | (39, 3,153) | (41, 3,157) | (45, 3,165) | 833, absent |
| 8 | (44, 4,627) | (46, 4,631) | (50, 4,639) | 1,216, absent |

The static shield comparison has the same host as the pair search. A separate comparison in this ticket uses a host without shields. [Two-terminal formula](../LATER-BOND-READING-20261119-001/boundary-proof.md) · [Static shield panel](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/high_results.json)

## Exact certificate and scope

In the weighted host, identify the two hubs and the simulated exterior. The resulting graph is complete bipartite between middles and outer junctions. The marked exchange is now an exact incidence symmetry. A cut below the least cost of separating these three sites has the same boundary support before and after identification. For lifting, deletion of a boundary of that cost leaves the three sites connected on their common shore. Any smaller competitor also contracts with its connectedness unchanged.

Within the identified host, the marked incidence graph gives a more economical exhaustive comparison than listing all sets of literal distinctions. A component with `b` outer sites and `t` marked middles requires at least `b+t−1` marks, attained by a spanning tree. All its outer sites have the same shore assignment. All its marked middles are forced opposite. Thus the exact worst minimum is computed from the component sizes, positions of the distinguished anchor and merged hub, and the numbers of each middle type in each component. Repeated marks within a weighted bundle or merged virtual crossing impose the same condition as one mark. A query affected by the permutation uses at least one test middle. The checker ranges over every such component profile realizable with at most `r` marks. For orders 4–8 the profile counts are 1,111, 5,768, 25,467, 100,457 and 364,220. The threshold is the exact least cut separating the three original sites, derived by minimizing the sum of the two possible contributions at every middle for each outer assignment. For fixed signs of the distinguished anchor and hubs, that sum is concave in the number of weak anchors on one shore, so either endpoint suffices.

The independent successor calculation fixes the required marked crossings and checks connectedness of both shores. Unmarked sites of one type with placements on both shores only need the two extreme counts with that property. The presence of each type decides connectivity, and the cost is linear in its occupancy. Coefficientwise dominated cuts cannot lower a minimum. Two small, asymmetric unquotiented controls reproduce the exact folded maxima, splitting thresholds and all four target pair minima.

The dynamic parameters use `r−1` anchors, each shield count from `r` to `3r+4` with difference at most two, and each initial capacity from 2 to `6r+8`. The second price is the ceiling of the first color's total capacity divided by the second shield count, or one more. The permanent shield bundle equals its initial terminal capacity. Test hub multiplicity is 1 through `r` times the first shield count. The distinguished anchor multiplicity adds zero, one or two to it. The marked cap is `200r²`. The static panel allows each shield count from 1 to `3r+2`, maintains the same count difference and balancing rule, and ranges through prices `5r²` and test widths one and two. Each search finishes all smaller junction counts and all smaller widths at the winning count. A failed strict folding inequality leaves the underlying parameter tuple undecided by this certificate. The dynamic panel requires that a successor minimum differs from its image on one of the two selected old pairs and scores its exact cardinality in either direction. [Declared panel bounds and per-order counts](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/high_results.json)

## Construction bounds at all orders

Let `I=r−1`, `k=r−2`, `s=4r`, `L=2r²+1` and `M=ceil(21r/2)`. Use `s` shields per color, the two test multiplicities `L`, and `M` for each initial branch capacity and permanent shield bundle. Work with both colors decreasing. The future bond minimum through the first pair is at most `2L+sr` by taking the first hub with its shields. Under the image, distinct heavy cycles each require two crossings, for a lower bound of `4L`. These bounds differ strictly.

For the present certificate choose a component of the marked incidence graph containing an anchor and excluding the merged hub. Use its anchors on the other shore, and put each marked middle opposite its component. At most four test middles can be added. When the chosen anchors contain `v`, each added test middle costs at most `k`, since its `L` incidence to `v` stops crossing, and the distinguished anchor costs `4L+2s≤8L`. When they omit `v`, the four test middles together cost at most `8L+4k`. At most `r−1` marked shields and at most one extra connector pay their own degrees. If the merged component contains all outer sites, all marks belong to one middle and its singleton works. These cases give the upper bound

\[
U=k(2s+4)+8L+4k+r(2M+I).
\]

Distinguishing the hubs pays at least `sM` across a shield family and `2L` through the two independent test routes. Putting both hubs opposite the exterior pays `2sM`, also at least `sM+2L`. Thus the gap from the upper bound to the least splitting cut is at least `9r+10`. The marked counts are exactly `16rM+17r+5` junctions and `24r²+56rM−20r` distinctions, bounded by `168r²+25r+5` and `612r²+8r`. Unit replacements from the earlier theorem retain quadratic bounds in both counts for starts whose ordinary pairs meet at most once. [Unit replacement and transport proof](../../proofs/LATER-BOND-READING-20261119-001A/LATER-BOND-READING-20261119-001A-P001_future/proof.md)

A stable branch of capacity `B` can use `g` initial parents with nearly equal shares `l_i`, summing to `B`. Parent `i` meets the shield on `l_i` distinctions and holds `l_i` loose distinctions. Their first round joins every pair and adds `u_i=l_i−g+1` unary junctions from parent `i`. Each paired child obtains `g−2+u_i+u_j` fresh distinctions, and each unary child from parent `i` obtains `max(2,l_i−1)`. This gives `B+g−g(g−1)/2` marked junctions. Through the next round, route the two incoming paths at a paired child through separate joins with unaries in its two parent groups. If `u_i≥2`, the unaries themselves use distinct remaining joins in the same group. If `u_i=1`, send one paired path through a triple of paired children and send the unary path through the join it frees. For `g≥4` the cyclic triples of consecutive parent indices give distinct such routes. With three parents the recorded balanced recipe permits at most one such low-count group. With two parents it requires both counts at least two. The single-parent recipe covers smaller capacities. The literal integer-flow checks verify capacity through both rounds in every selected case.

For the static comparison, take both test multiplicities one. One can refine the shield term to `(r−1)(2M+I)`: when a connector is needed there are at least two selected anchors and no positive marked middle, so connecting that marked component uses one more mark than its marked middle count. With `s=2r−1` and `M=5r²−10` the marked junction count is `5r+6` and the width is cubic in `r`. With `s=4r` and `M=ceil(9r/2)` the count is `9r+8` and the width is quadratic. Both formulas retain the higher old obstruction with the permanent unit restoration. [Explicit general size tables](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/high_results.json)

## Reproduction

```bash
family=experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size
scratch=$(mktemp -d)
python3 -B "$family/high.py" prepare "$scratch"
python3 -B scripts/longrun.py launch "$family/high.py" --out "$scratch/orders4-7" \
  --unit bond-reading-scale-release --workers 6 --case-timeout 240 --case-mem 450M --mem-max 5G \
  --param engine="$scratch/high" --param low=4 --param high=7 --prepare-only
python3 -B scripts/longrun.py run --out "$scratch/orders4-7" --foreground
python3 -B scripts/longrun.py launch "$family/high.py" --out "$scratch/order8" \
  --unit bond-reading-scale-order8 --workers 1 --case-timeout 240 --case-mem 1600M --mem-max 4G \
  --param engine="$scratch/high" --param low=8 --param high=8 --prepare-only
python3 -B scripts/longrun.py run --out "$scratch/order8" --foreground
python3 -B "$family/high.py" collect "$scratch/orders4-7" "$scratch/order8"
```

All 15 final panel jobs completed. The final literal replays and independent controls took 38 seconds and peaked at 74,824 KiB RSS. The larger order-eight profile jobs used one worker to avoid the lower per-job memory ceiling of the initial parallel trial.
