# A certificate from singleton minima and one directed pair bit

For a stage with a strict successor, fix every distinction held by a live junction. Write \(C\) for the binary span of the junction equations. The least order is the first at which every renaming preserving the readings and the fixed names carries \(C\) to itself. This tests all subsequent readings of all orders. If there is no successor, the least order is zero. These statements follow from the restriction of later equation spaces to the old names and complete-round transport. [All-future equivalence](../BOND-READING-SCALE-20261119-001/limiting-reading.md) · [Complete-round transport](../EXTEND-ROUND-20261119-001/extend_round.md)

Put \(c_e=K(\{e\})\) and define the directed relation

\[
  R(e,f)\quad\Longleftrightarrow\quad K(\{e,f\})=c_e.
\]

Set \(R(e,e)=1\). Every pair-table symmetry preserves these labels and bits. The certificate proves sufficiency when all the permutations allowed by a suitable upper bound on their symmetry group preserve the equations. A failed certificate returns an interval for the least order.

## One flow per distinct holder pair

In the classical graph presentation, give each loose distinction the exterior as its second endpoint. Between each pair of endpoints retain one positive capacity equal to the number of literal distinctions joining them. For a distinction \(e=st\), every cut crossing \(e\) separates \(s,t\). Every minimum \(s,t\)-cut has connected shores. Indeed, moving a component of either shore away from its own shore's terminal removes at least one crossing distinction and creates none, since the graph is connected and capacities are positive. Thus \(c_e\) is exactly the minimum \(s,t\)-cut capacity, and the minimizing bonds through \(e\) are precisely those minimum cuts.

After a maximum flow, the \(s\)-shore of a minimum cut is exactly a set containing \(s\), omitting \(t\), and closed under positive residual reachability. This follows by writing the cut capacity minus the flow value as the total forward residual capacity crossing the cut. For a proposed crossing \(a\to b\) at another holder pair, the least possible closed shore is the set reachable from \(\{s,a\}\). It works exactly when neither \(b\) nor \(t\) is reachable there. There is no residual path from \(s\) to \(t\). The other three conditions are

\[
   s\not\leadsto b,\qquad a\not\leadsto t,\qquad a\not\leadsto b.
\]

First require the residual capacity on \(a\to b\) to vanish. Its positive original undirected capacity then gives positive reverse residual capacity. Consequently \(a\not\leadsto b\) holds precisely when \(a,b\) lie in different strongly connected components. Test both orientations. This gives the complete directed row of \(R\) from one flow, two reachability sets and one strongly connected component decomposition. It handles parallel distinctions, ties among minimum cuts, and pairs present in no common bond. Such a pair has a false bit in both directions. [Classical residual description of minimum cuts](https://publications.polymtl.ca/5993/)

With \(v\) vertices including the exterior when present, and \(m\) occupied holder pairs, the implementation uses \(m\) maximum flows, \(O(m(v+m))\) additional graph operations and \(m^2\) packed output bits up to row padding. Dinic's general bound gives \(O(v^2m^2)\) total flow work. Every parallel distinction is restored with its literal multiplicity before testing a permutation. Physical holders accelerate the computation of the observable arrays. The only colors passed to the group test come from fixed names, singleton minima and directed pair bits.

## Deciding orders zero and one

For two movable names \(i,j\), their transposition sends each \(x\in C\) to

\[
  x+(x_i+x_j)(\mathbf e_i+\mathbf e_j).
\]

It preserves \(C\) exactly when the two columns agree on every generator, or \(\mathbf e_i+\mathbf e_j\in C\). Column agreement means the two names have the same holder pair. The second test is equality of the two unit vectors reduced modulo \(C\). Gaussian elimination obtains all unit-vector remainders once.

At order zero all movable names are one class. At order one they are partitioned by \(c_e\). Within each class, transpositions with one chosen member generate its full symmetric group. Exact tests of those transpositions therefore determine orders zero and one. A lower bound of two includes a literal noncarrying transposition with equal singleton minima. A reached stage without a successor is handled first.

## Certifying order two and bounding unresolved cases

The literal union of the minimum bonds through \(e\) is \(U_e=\{f:R(e,f)\}\). If \(|U_e|=c_e\), this is one identifiable bond. Include all such bonds and all fixed live rows. If they span \(C\), every symmetry carries \(C\).

For a second certificate, put all movable names having identical complete rows, complete columns and singleton costs into blocks. Inside each block every permutation preserves the retained readings. A symmetry permutes entire blocks of equal size. Color each block by its size, singleton minimum and both directed incidences to every fixed name. Refine these colors until stable by counting outgoing, incoming and mutual bits in each color class. The resulting partition is invariant under every symmetry of the full pair readings. For a proposed permutation \(\pi\), test each source star \(S\) by checking that the remainder of \(\pi S\) modulo \(C\) vanishes. Equal dimensions make containment sufficient.

Three tests use this partition.

1. An individual source star has image in \(C\) whenever, in each movable color class, it uses either the whole class, the empty set, or only names from a class with a single unit-vector remainder. In the third case the source star and its image use equally many names of that remainder, so their difference has zero remainder. Include the span of all such certified rows in the bound below.
2. Test the transpositions generating the full symmetric group of each block. If they all carry \(C\), also test generators swapping equally colored blocks, using a canonical bijection of their names. If all carry \(C\), compositions carry every permitted permutation. Testing arbitrary permutations within each color class of blocks can overestimate the true group. When an unsafe permutation occurs inside an observable block, its existence only establishes a failure of this reduced reading test. The full pair minima can still distinguish the swap.
3. Optionally compute generators of the colored directed quotient with BLISS. The graph contains only stable color classes of size greater than one. Each omitted singleton class has constant incoming and outgoing incidences from every remaining color class by stability. All quotient vertices have a loop. Hence removing these singleton classes and the common loops preserves exactly the permitted permutations of the remaining quotient vertices. Check the resulting generators against the entire directed relation and lift each to a permutation of the literal names. Their safety, together with safety inside each block, proves that all pair-preserving maps carry \(C\).

For any remaining source star of size \(w\), reading through order \(w\) carries it into \(C\). Indeed the star is the disjoint union of bonds obtained by successively removing a contained bond, and each bond at most that size transfers by its literal equality test. If deleting the junction leaves a connected graph, its star is itself a bond. Choosing one distinction per distinct neighbor, \(d\) in total, forces the complete star into every bond through the selection. The observable union of the minimum bonds through the selection at order \(d+1\) then gives the exact support. Thus \(\min(w,d+1)\) suffices for this star. Add stars in increasing order of their individual bounds until the proven rows span \(C\). The largest bound needed is the reported upper endpoint. [Proof of the focusing bound](../BOND-READING-SCALE-20261119-001/limiting-reading.md#focusing-one-bond-and-counting-junctions)

## Implementation and controls

`scale_order(stars, has_successor=flag, use_bliss=False)` implements the polynomial certificate. The flag is the stage's known lawful continuation status. When omitted, the function consults the complete-round rule, which includes enumeration of maximal candidate sets. The default `use_bliss=True` permits a bounded optional graph-automorphism search after the polynomial test. A missing solver or a timeout keeps the proven interval. The result records inclusive `lo` and `hi`, its method and supporting counts. `pair_suffices` is `True` when `hi <= 2` and `None` when the available evidence leaves the pair verdict open. The returned witness for a lower bound of two changes the equations while preserving all singleton readings and fixing the end. [Python certificate](../../experiments/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/scale_reader.py) · [Flow implementation](../../experiments/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/scale_reader.cpp)

The `--check` mode compares every computed bit and singleton value with direct enumeration of cuts whose two shores are connected. It passed all 1,542 cases obtained from the connected labeled simple graphs on two through five vertices, with unit capacities and one deterministic positive multiplicity pattern for each graph. These cases checked 50,384 ordered holder-pair bits. On the same networks, direct membership of transposed star rows in the full cut space independently verified all 29,161 literal transposition tests used for the lower orders. The archived five-junction, 11-distinction pair failure returned \([2,4]\), and the 13-junction, 91-distinction triple failure returned \([2,7]\). Each archive control also passed the direct cut comparison. A separate BLISS test on the six distinctions of the complete four-vertex graph verified a safe coupled exchange and an unsafe independently permitted exchange. Run from the repository root with its Python environment. [Archived pair obstruction](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/lower_native_center_summary_17.json) · [Archived triple obstruction](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/lower_probe_symmetric.json)
