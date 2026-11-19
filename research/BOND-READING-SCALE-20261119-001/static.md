# A permanent small-reading ambiguity with explicit size bounds

These examples answer the target in which the *later* marked set can have any size. They preserve every reading through the tested order forever. The different later entry is on an old set of larger size.

Use two ordinary junctions \(R,B\), \(s\) middle junctions of each color, and \(t\ge2\) further ordinary junctions. Each middle meets its own colored junction in \(L\) distinctions, and each of the \(t\) further junctions in one. Exchange a red and a blue middle, matching each spoke type and copy. Replace one fixed unit distinction from an unmoved middle to an uncolored junction by giving each endpoint a loose distinction. These two endpoints have no common ordinary neighbor. In the first complete round they give two independent one-parent junctions, each with two fresh distinctions. Every ordinary star is a bond. Deleting either colored junction leaves the middle junctions connected to the others through the uncolored junctions, and deleting any uncolored junction leaves at least one other. The two-end replacement is connected through the exterior and has separating cost one, at every later age. Its branch inputs and every live distinction are fixed. Applying the unit replacement formula gives the same readings for all orders that matched on the closed graph, including marks in the two new branches. [Unit replacement argument](../LATER-BOND-READING-20261119-001/boundary-proof.md)

The positive-age stage has
\[
                    J=t+2s+4,\qquad n=2s(t+L)+5.
\]
Select one distinction from each of the \(s\) bundles on \(R\). The smallest bond through these representatives is the entire physical star of \(R\), of size \(sL\). Any bond through the matched names also pays for \(s\) entire parallel bundles. Its cost can equal \(sL\) only if it is their union. That union crosses a permanent four-step cycle oddly and therefore gives no equation. Thus its old reading after growth exceeds \(sL\) or is absent. The old support under comparison avoids the replaced unit. The examples use the same growth history on both sides.

## Uniform current certificate

Identifying \(R,B\) gives a complete bipartite graph. The proposed exchange is an exact symmetry there. There are \(s\min(t,L)\) incidence-disjoint routes between \(R\) and \(B\) in the original graph. Pair each red middle to a different blue middle and use distinct uncolored junctions for its paths. The lower bound is attained either at the star \(R\) or by taking \(R\) with all its red middles, so it is the minimum separating cut. Every bond strictly below it in the identified graph lifts with both shores connected: deletion of its distinctions leaves \(R,B\) connected on their common shore. Conversely every original bond costing less contracts. This also proves equal minima for literal marks on different copies of the same bundle.

For any \(r\ge2\) take \(t=L=r+1\) and \(s=2r+5\). Choose an uncolored junction untouched by the at most \(r\) requested names. Take it and all marked middles as one shore. Both shores are connected and every requested name crosses. If \(m\le r\) middles are marked, this cut costs \(2s+(L+t-2)m\), strictly below \(sL\) by at least \(3r-5>0\). This proves the family size bounds \(J=5r+15\), \(n=8r^2+28r+25\), independently of a finite fit or census.

The exact sufficient-folding screen enumerates the connected components of the marked bipartite incidence. All outer sites of a component must have one color and its middles the opposite color. A component with \(a\) outer sites and \(b\) marked middles can be specified by exactly \(a+b-1\) crossing constraints. For a cut with the merged hub on the negative shore, \(a\) positive uncolored sites and \(m\) positive middles, the cost is \(2sa+(L+t-2a)m\). Under \(L\le t\), this is below \(sL\) precisely when \(m<s\) and \(L>2a+tm/(s-m)\). Single-vertex shores and unused sites are included in the minimization. For a fixed pattern the threshold increases with \(m\). The panel exhausts those conditions for \(2\le r\le14,\ 2\le t\le r+2,\ 2\le s\le2r+5\). Above \(L=t\) the separating cost is fixed and folded costs only rise. The test yields a sufficient family certificate. [Screen and checks](../../experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/static_order.py) · [Results through fourteen](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/static_order_fourteen.json)

## Exact two-hub comparison

A separate calculation keeps the two hubs distinct and scores every original cut for each type of marked pattern. When all middles are considered without colors, the incidence automorphisms within either color and a single exchange between the colors together generate all middle permutations. Therefore every current \(r\)-mark reading is preserved by that particular exchange exactly when its value on every uncolored marked incidence pattern is independent of the assignment of its middles to red and blue. Repeated copies of one marked type make the same request.

The calculation first enumerates the patterns of up to seven distinct marked incidence types, up to permutation of unused or equally situated uncolored sites and middles. It then assigns each pattern's middle colors in all feasible ways. Fix the side of \(R\), and consider either side for \(B\). A marked middle has a forced side opposite its marked outer endpoints, or those marks cannot cross. After choosing the sides of the marked outer sites, only the numbers of remaining middles of each color and uncolored sites on either side are relevant. At fixed values of the other counts, the cost is linear in each count. Connectedness changes only at zero, one, or the corresponding opposite extreme. Checking the endpoints and their immediate neighbors therefore gives the exact minimum including infinity. Five small panels were independently recalculated by direct listing of literal shores and mark sets. Actual starts and two complete rounds were replayed for the listed winners by two growth implementations. [Exact program](../../experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/static_exact.py) · [Exact panel](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/static_exact_seven.json) · [Literal checks](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/static_replay.json)

Counts in the exact panel are \(2\le t\le10,\ 2\le s\le17,\ 1\le L\le12,\ sL\ge3\). The seven mark-pattern counts at orders one through seven are \(2,6,15,42,108,300,811\). Samples past the exact two-hub panel use the sufficient-folding screen with its own bound.

| Order | Least \(J\) then \(n\) in exact two-hub panel | Least \(n\) then \(J\), displayed as \((J,n)\) |
|---:|---:|---:|
| 3 | (25, 165) | (26, 149) |
| 4 | (30, 245) | (32, 197) |
| 5 | (35, 341) | (37, 285) |
| 6 | (40, 365) | (40, 365) |
| 7 | (45, 481) | (45, 481) |

For the folding screen at orders 8, 9, 10, 11, 12, 13 and 14 the least junction-first sizes are respectively \((51,689),(55,761),(61,1017),(65,1105),(71,1409),(75,1513),(81,1865)\). These are binding bounds or minima only in the named panel for the named comparison. The decision note combines them with smaller examples from other families.
