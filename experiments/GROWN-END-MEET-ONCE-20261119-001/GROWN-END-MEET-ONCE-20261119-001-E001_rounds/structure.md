# A failure with every starting junction of arity three or four

For every starting junction count of at least nine, there is a simple ordinary meeting arrangement whose first reached table has a symmetry fixing every distinction of every live junction, yet no fresh naming extends it through the second round. All starting arities are three or four. The nine-start example has eight such reached symmetries in total. Exactly four extend.

## The source and its complete rounds

Number the nine sites in the order A, B, C, D, U, V, S, T, W. Each support imposes even parity.

| Site | Support | Site | Support | Site | Support |
| --- | --- | --- | --- | --- | --- |
| A | 0, 2, 5, 6 | B | 1, 3, 16, 17 | C | 0, 1, 4 |
| D | 2, 3, 4 | U | 5, 7, 8 | V | 6, 9, 10 |
| S | 7, 9, 12, 13 | T | 8, 11, 14 | W | 10, 11, 15 |

In the classical incidence representation, write O for the exterior holding the loose ends. The circuit A–C–D–B–O–T–W–V–S–U–A visits every junction and the exterior. Deleting any vertex leaves the rest connected. Each displayed support is therefore a bond, an inclusion-minimal parity equation, so its simultaneous projection is exactly its full even-parity relation. The ordinary arrangement is connected and every pair of ordinary sites meets at most once. Direct enumeration of the joint states and the canonical forgetting check give 8, 8, 4, 4, 4, 4, 8, 4, and 4 allowed assignments on the nine rows, in site order.

Among the initially live sites the only candidate pairs are S,T through U and S,W through V. They use the two loose distinctions at S. The two loose distinctions at B give separate one-parent junctions. The new sites X,Y,Z,J have supports {12,14,18}, {13,15,19}, {16,20,21}, {17,22,23} respectively. The next groups are XY and ZJ, each backed by a single parent. Thus each first-round site has lookahead demand one. The two-parent sites give one fresh distinction each and the one-parent sites give two each. No taken group exhausts the old loose set.

Round two adds {18,19,24}, {20,22,25,26}, {21,27,28}, and {23,29,30}. The second of these four sites shares a parent with each of the last two, and the first shares a parent with none of them. The demands are 0, 2, 1, 1. The cheapest counts are 1, 2, 2, 2. The two law implementations reproduce both complete rounds. [Replay code](structure.py) · [Recorded supports and measurements](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/structure.json)

## The five interior distinctions

The distinctions 0,1,2,3,4 are AC,BC,AD,BD,CD. Write Q for the rest of the wired graph, including A and B. It meets these five distinctions only at the two poles A and B. Suppose Q is connected, and let λ be the minimum number of its distinctions crossing a cut separating its poles. Write K for the minimum size of a bond containing the named pair, so the recorded bond distance is K−1.

| Pair in the interior | K |
| --- | --- |
| Two distinctions at C, or two at D | 3 |
| AC and AD, or BC and BD | min(4, 2+λ) |
| AC and BD, or BC and AD | 4 |

The stars at C and D give the three-place witnesses. The shore {C,D} gives the four-place witness. With the poles together, a cut across any required cross-pair contains all four distinctions to A and B. With the poles apart, exactly one of AC,BC and one of AD,BD cross, along with at least λ distinctions of Q. For an opposite-pole pair CD must cross as well. For a same-pole pair the lower cost 2+λ is attainable by placing C and D together on the required side of a minimum separating cut in Q. Both shores of that minimum cut in Q are connected. A cut through an interior pair at C or D cannot have size two by the same two pole cases.

Every Q distinction has the same pair reading to AC and BC. If the poles are together then AC and BC cross together. If the poles are apart, switch both C and D to their opposite shores. A bond already had each Q shore connected, since a component missing that shore's sole pole could never connect through C or D. After switching, every moved site meets the pole on its new shore. This operation preserves both connected shores, the size of their boundary, and every Q crossing. It exchanges AC with BC and AD with BD. The argument also preserves a missing reading.

At age one, two disjoint routes run from A to O in Q via U,T,X and V,W,Y, and two run from O to B via Z and J. The two loose distinctions at X and Y separate the entire left portion from O, so λ=2. At age two, the single fresh distinction 24 alone separates it and λ=1. The transposition 0↔1 consequently preserves the full first table and fixes all four live supports pointwise. The next bond {0,2,24} gives D(0,2)=2, while D(1,2)=3. Even re-pairing older loose names cannot change this comparison on three previously shared names. The triple AC,AD,CD is an odd circuit, so it has no containing bond. Its marked image BC,AD,CD has minimum bond size 3+λ=5 at age one.

## Symmetries and larger starts

At age one the eight permutations of the four pole distinctions preserving the unordered partition {{AC,BC},{AD,BD}} and fixing all other names preserve the table. Exchanging C with D is a graph symmetry, and switching both interior sites across a cut gives equal readings to all exterior distinctions as above. At age two, the four surviving permutations must also preserve {{AC,AD},{BC,BD}}. All four work while fixing the fresh names. For the nine-start example exact enumeration found no additional reached permutations fixing the live supports. Two independent methods, enumeration of connected cuts and the dimension of the equations supported on each candidate, agree on all 276 reached and 465 successor entries. They found 432 and 1,106 bonds respectively. [Exact permutation counts](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/structure.json)

To add any number of closed sites while keeping arity at most four, first subdivide AU by a new site, joining that site also to V. Next subdivide the newest link out of A and join the inserted site also to U. Continue subdividing the newest link out of A, each time also joining the inserted site to the site inserted two steps earlier. Each site used as this third neighbor had degree three and is used once. Subdivision preserves the displayed spanning circuit. Every addition touches only closed sites in Q on A's side, so the live groups and cheapest counts stay the same. The first of the two routes from A simply follows the subdivided AU link. The two separating tips at age one and the sole separating tip at age two still cut off the whole A side. Thus the same marked failure holds for every resulting size. The literal checks cover the starting projections and both fresh lists at 9, 10, 11, 12, and 19 starting sites. The size-independent conclusion follows from the subdivision argument.
