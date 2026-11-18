# When two additions to the same prefix give identical allowed states

**Theorem.** Start from any finite reachable presentation under the serial two-or-three-fresh parity law. Make two different choices of actual loose inputs for a single addition to this same presentation. Use the same fresh distinctions in both additions and compare the allowed states on the identical names. If those states agree, both resulting presentations have an empty menu of legal three-parent additions.

The theorem concerns two successors with a common physical prefix. It leaves open full scalar-table comparison between arbitrary histories. The equal-state pair at width eighteen illustrates the theorem. Its singleton and pair menus differ, and both triple menus are empty. [Growth and observation rules](../../../research/VARIABLE-OUTPUT-READER-20261118-001C/preregistration.md) · [Width-eighteen example](../../../research/VARIABLE-OUTPUT-READER-20261118-001A/first_three.md)

## How equality reduces to complementary choices

Use the ordinary meeting graph, with one vertex per junction and one edge per shared distinction. It is connected and simple. It is bipartite by induction, since parents sharing a neighbor lie on the same side. A new vertex with several parents thus fits on the opposite side from all of them. A loose distinction has just one ordinary holder.

Let the chosen input sets be \(P,Q\). The two new parity equations have identical fresh terms. Every allowed old assignment extends over the fresh distinctions. The two extensions permit exactly the same assignments if and only if parity on \(P\mathbin{\triangle}Q\) already vanishes on every allowed old assignment. Such a parity equation is a sum modulo two of old junction equations, by the row-space characterization of homogeneous linear equations.

The support \(P\mathbin{\triangle}Q\) consists entirely of loose distinctions. Every ordinary meeting therefore has either both its junction equations selected in the sum or neither. Connectedness makes the selection constant over all junctions. The empty selection would give \(P=Q\). Selecting all the equations cancels every shared distinction twice and leaves exactly the entire loose frontier. Thus \(P,Q\) are disjoint and together use every loose distinction.

The last junction of the prefix has all its fresh distinctions loose. The seed has three, and any later junction has two or three. Each input group uses at most one from a given holder. Consequently this junction occurs in both groups and has exactly two loose distinctions. All parents appearing in either group lie on its bipartition side.

We next exclude a complementary split in which \(Q\) has three parents and \(P\) has a different set of parents. Suppose such a split exists. Append one junction \(S\) on \(P\) and then one \(T\) on \(Q\), taking two fresh distinctions on each. The actual inputs to \(T\) remain loose. All previous pair witnesses remain, and the only new potential common neighbor is \(S\). It misses at least one parent of \(Q\), since \(P\) has at most three parents and the parent sets differ. Both additions are lawful.

Orient ordinary meetings in order of creation. In the resulting finite graph, \(S,T\) have zero children and every other vertex has two or three distinct children. All outputs of the prefix have been consumed, and no one child consumes two outputs of the same parent. In particular the original seed has three children. The last vertex of the prefix has exactly the two children \(S,T\).

## An elementary count forces the reverse tests

For a bipartite graph with sides \(A,B\), let \(\Phi_A\) be the alternating sum of \((-1)^{|U|-1}\) over nonempty subsets \(U\subseteq A\) that have a common neighbor. The two sides give the same integer \(\Phi\). Indeed each qualifying \(U\) has a nonempty common neighborhood, and the alternating sum of its nonempty subsets is one. Expanding gives

\[
\Phi_A =
\sum_{\substack{\varnothing\ne U\subseteq A,\ \varnothing\ne V\subseteq B\\
                  U\times V\ \subseteq E}}
    (-1)^{|U|+|V|}
=\Phi_B.
\]

To count a new vertex's contribution, choose the side containing its old neighbors. The new vertex witnesses exactly the nonempty subsets of this neighbor set. Once the old graph is connected and has an edge, singleton subsets are already witnessed. For one old neighbor the change is zero. For two it is zero when the pair already had a witness and minus one otherwise. For three, write \(j\) for the number of previously witnessed pairs. If the triple already had a witness, the change is zero. Otherwise the new triple contributes one and the \(3-j\) new pairs contribute minus one apiece. The change is \(j-2\). Its maximum of one requires exactly the legal three-parent condition.

The first ordinary edge has \(\Phi=1\). In the forward history every later legal pair attains zero and every legal triple attains one. Thus the final value is \(1+\tau\), where \(\tau\) counts all forward three-parent additions. Let \(N\) be the number of vertices, \(\sigma\) the number of one-parent additions and \(k\) the number of vertices with three children. Count ordinary edges once at each later endpoint and once at each earlier endpoint. This gives

\[
|E|=2(N-1)+\tau-\sigma=2(N-2)+k.
\]

The first two additions must have one parent. After the first addition, the two existing vertices share no neighbor. Therefore \(\sigma\ge2\) and \(k=\tau-\sigma+2\le\tau\).

Now expose the same graph in reverse birth order. Initially there are the two sinks and their first common neighbor, the last vertex of the prefix. This three-vertex path has \(\Phi=1\). Every remaining vertex arrives on its two or three original children. Its increase is at most zero or one respectively. All \(k\) three-child vertices occur in these remaining steps. Hence \(1+\tau\le1+k\). Equality holds throughout. Every remaining reverse addition on two vertices has a previous common neighbor, and every reverse addition on three has pairwise previous witnesses and no common previous witness. These reverse properties follow from the count.

## Why the reverse graph cannot reach the three children of the seed

Put the sinks in layer zero. Initially layer one holds their first common neighbor. We prove by induction that the exposed graph consists of successive two-vertex layers, with at most one vertex in the last layer while it is being formed. All edges between consecutive layers are present, and these are the only edges.

Call a layer complete for this argument once the layer immediately after it contains two vertices. Suppose a new reverse vertex \(X\) uses a parent in such a layer. Choose the earliest-numbered parent layer \(i\), with a parent \(u\) there. It too has a two-vertex successor layer. The reverse step needs at least two parents and every pair of parents must already have a common neighbor. In the current graph a second parent can therefore occur only in layer \(i\) or \(i+2\).

If a second parent \(v\) lies in \(i+2\), it is adjacent to both successors of \(u\) in layer \(i+1\), and also to \(X\). These two successors and \(X\) are three distinct original parents of \(u\), since they all follow it in reverse order. The vertex \(v\) is earlier than \(u\) in original time and witnesses all three. This contradicts the original addition of \(u\). A vertex with fewer than three original parents already contradicts the three required incidences.

If both members of layer \(i\) are parents of \(X\), take \(u\) to be the member appearing first in reverse order. Its layer mate witnesses both successors and \(X\), and precedes \(u\) in original time. The same forward contradiction applies. In layer zero this also says directly that \(S,T\) would have three common original parents, whereas their distinct parent sets have size at most three. In either case \(u\) has a later reverse vertex \(X\), so \(u\) cannot be the original seed.

Consequently no new reverse parent can come from a layer with two successors. When the last layer consists of a single vertex, only the preceding two-vertex layer and that singleton are available. They are on opposite bipartition sides, so the step must use both members of the preceding layer and completes the last layer. When the last layer already has two vertices, only its two members are available, and using them begins the next layer. This proves the induction from the initial three-vertex path. Every remaining reverse step takes exactly two parents. The original seed, exposed last, has three children and would require a reverse step on three. The contradiction excludes the proposed complementary split.

## The triple menus

If one complementary group uses three parents, the exclusion implies that both groups use the same three parents. After either addition the only old loose holders are these three. They now share the new junction as a common neighbor. If both groups use at most two parents, at most two old loose holders remain in either successor. In both cases the newborn lies on the opposite bipartition side from every remaining old loose holder. It cannot form a legal triple with them. These exhaust the possibilities and prove the theorem.
