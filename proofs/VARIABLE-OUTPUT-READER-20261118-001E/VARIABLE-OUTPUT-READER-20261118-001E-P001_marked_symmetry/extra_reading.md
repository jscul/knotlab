# What an additional bond reading guarantees

For a set \(S\) of \(k\) named distinctions, write \(d_k(S)\) for the least **cardinality** of a bond containing every member of \(S\), with infinity if there is none. Thus \(d_2=D+1\) on distinct pairs. An observation at arity \(k\) means the table for every such named subset, with one consistent renaming across the whole table.

Bond minima through arity five determine the entire allowed-state relation of every finite reachable presentation, and hence its actual legal three-parent choices. The table of triple minima alone determines every three- and four-bit bond. It also distinguishes the known scalar symmetry which changes the parity code at width 32. The least sufficient arity for the legal menu remains open.

For background, Seymour's work on triples in binary matroid circuits addresses whether a triple is contained in any circuit. In the cut setting that determines finiteness of the triple minimum. The tests below use its attained cardinality. [Seymour, *Triples in Matroid Circuits* (1986)](https://collaborate.princeton.edu/en/publications/triples-in-matroid-circuits/)

## Recognizing a bond from its one-bit deletions

In any finite cographic matroid, for \(r\ge4\), a set \(C\) of \(r\) edges is a bond if and only if

\[
 d_{r-1}(C\setminus\{i\})=r \qquad\hbox{for every }i\in C. \tag{1}
\]

Here the cographic matroid is the classical matroid whose circuits are the minimal nonempty cuts of a graph. The wired parity presentation is of this type because its dual words are exactly the graph cuts. The test concerns their supports and uses no growth history.

The forward implication is minimality. For the converse, any proper subbond of \(C\) belongs to some \((r-1)\)-subset of \(C\). A subbond of size \(r-1\) would itself give a smaller minimum. If its size were smaller, no bond of size \(r\) could contain that \((r-1)\)-subset, since the proposed bond would properly contain the subbond. Hence \(C\) either is a bond or is independent in the cographic matroid.

Suppose it is independent. Represent the binary matroid by columns, so that minimal nonempty zero-sums are exactly its bonds. One such representation assigns an edge its unit vector modulo the graph's cut space. The columns of \(C\), numbered \(e_1,\ldots,e_r\), are independent and may serve as basis vectors for their span. Condition (1) supplies, for each \(i\), a bond of the form \((C\setminus\{e_i\})\cup\{f_i\}\) with \(f_i\) outside \(C\). Thus its last column is

\[
 f_i=\sum_{j\ne i} e_j .
\]

These \(r\) columns are distinct. Restrict to the \(2r\) displayed elements. Contract the independent elements \(e_5,\ldots,e_r\) and delete \(f_5,\ldots,f_r\). For \(r=4\) neither operation is needed. Binary contraction of independent columns means quotienting by their span. The eight surviving columns in four coordinates are therefore the four unit vectors and their four complements. Contract \(e_4\). The seven remaining columns, in the quotient on the first three coordinates, are all seven nonzero binary triples. This is the Fano matroid.

The Fano matroid cannot occur here. The cographic class is closed under deletion and contraction because duality interchanges these two operations, which come from graph deletion and contraction on the graphic side. If Fano were cographic, its dual would be graphic. That dual has rank four, seven edges and circuits of minimum size four. Its nonzero binary dependency vectors form the row space of the matrix of all seven nonzero triples. Each nonzero linear functional takes value one on exactly four of them. The dual is connected because any two different nonzero triples have a common functional taking value one on both, and each such four-element support is minimal. A connected graph representing the dual would have five vertices by the graphic rank formula. It would be simple and triangle-free because every circuit has size at least four. In a triangle-free graph a vertex of degree four excludes edges between its four neighbors. A vertex of degree three leaves only one further vertex available to meet its three neighbors, which gives at most six edges in total. Maximum degree two gives at most five edges. The required seven edges are impossible. This contradiction proves (1). [Binary contraction and graph check](check_extra.py)

## Applying the test to this growth rule

A true bond of size \(k\) is identified directly by \(d_k(S)=k\). For \(k=4,5,6\) one may also use (1). The three-bit bonds are read by \(d_3(S)=3\), and (1) with \(r=4\) recovers the four-bit bonds from that same triple table. Apply (1) at \(r=5,6\) using quadruple and quintuple minima. The recovered bonds of sizes three through six generate the complete cut space. Every ordinary junction star is a bond and every star has size at most six. All the parity equations are sums of these stars. Taking the binary orthogonal complement gives all allowed states. The established allowed-state theorem then gives invariance of actual legal triples under each bijection of the observations. [Allowed-state invariance](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md)

There is a smaller sufficient selection of these same values. From triples keep only whether each minimum equals three, equals four, or takes another value. This recovers every bond of sizes three and four, and thus the whole code whenever those bonds generate it. From quintuples keep only whether its minimum equals five, equals six, or takes another value. This recovers the five-bit bonds directly and the six-bit bonds by (1). Thus the quadruple table can be dropped altogether in this selection. Any specific bijection of reachable scalar tables that were to change a legal triple would change at least one of these ternary or quintuple answers. No such change of a verdict is assumed in this argument.

## A three-coordinate discriminator and a sharp bound for a different reading

At width 32, exchanging 13 and 14 in the published reachable example preserves all 496 scalar entries but changes a six-bit parity equation. In that example

\[
d_3(\{4,11,13\})=10,\qquad d_3(\{4,11,14\})=8.
\]

Of all \(\binom{32}{3}=4960\) ternary entries, exactly 200 change. The two named values also hold in the width-20 source, where 56 ternary entries change. In both examples the transposition preserves the set of all dual words of each size through five and moves three six-bit dual words outside the actual dual. The 32-bit example has eight legal triples, and the transposition preserves their set. [Width-32 incidence and preceding scalar check](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/active_part.json) · [Exact ternary replay](check_extra.py)

A different, Boolean reading asks of a named set \(S\) whether its parity is even on all allowed states. It gives membership of \(S\) in the dual space, including sums of bonds. On the reachable family the complete pair table together with these Boolean answers through arity five can fail to identify the parity code, by the same exact transposition. Answers through arity six always suffice by the star bound. Six is therefore sharp **for recovering the full parity code with these Boolean parity questions**, even given the scalar table. The ternary minimum above separates the same presentations because it can report a larger containing bond. None of these lower bounds shows that the actual three-parent legality differs.

The cographic hypothesis in (1) matters. On the eight odd binary vectors of length four, every three distinct columns extend to a circuit of size four by adding their sum. Both pair and triple minima are constantly four. Some permutations change the four-circuit set, for example exchanging one of the eight columns with a point outside a specified circuit while fixing the other three. This binary example is excluded as a cographic representation by the same Fano contraction. [Finite countercontrol](check_extra.py)

There is also a limit to a direct triple test for six-bit sets even on cut codes. In the complete tripartite graph with classes \(\{0,3\},\{1,4\},\{2,5\}\), take the six edges of the cycle \(0,1,3,2,4,5,0\). Each of its twenty triples has minimum containing bond size six. The whole six-set is absent from the cut space. A direct check uses the 31 nonempty choices of a shore avoiding a fixed vertex. This rules out declaring a six-set a bond simply from agreement of all its internal triple minima. It gives no pair of different reachable presentations with identical global ternary tables. [Six-set control](check_extra.py)
