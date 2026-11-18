# A four-bit bond can bound fourteen ordinary sites

**Result.** There is a reachable width-32 presentation with a four-bit bond whose ordinary shore contains all fourteen junctions. The matrix forces this support, forces the full parity relation, and even determines that this support is the exterior star in every reachable realization. This is a different width-32 matrix from the one with eight legal triples. Its triple menu is empty. [Comparison with the other width-32 matrix](scalar_inverse.md#all-realizations-of-the-published-width-32-table)

## The necessary local form

Let \(U\) be the ordinary shore of a four-bit bond, and suppose it contains at least three sites. Its last three sites introduce at least six outputs altogether, at most two of them consumed inside \(U\) since the ordinary graph is bipartite and simple. Thus all of its four boundary bits are outputs of these three sites. Each made exactly two outputs and their two internal meetings form a path. No ordinary input enters \(U\).

The induced history on \(U\) is itself lawful. It contains the seed and all earlier parents of its sites. The restricted history retains pair witnesses because the earliest common neighbor of any two parents must predate at least one of them, since a later first witness would itself have had to join the pair using an earlier witness. Such a neighbor of a site inside \(U\) belongs to \(U\). Removing other vertices cannot introduce a universal witness.

There are three possible positions for the middle of this path in the chronology of the last three. If it was first, its two later neighbors are the only sinks, with all earlier outputs consumed and the seed sending three. This contradicts the two-sink restriction. If it was last, each of its earlier neighbors still has one loose bit. Add one more two-parent, two-output junction there, which is legal since the two sites have a common neighbor. This again leaves two sinks of the excluded form. The necessary pattern is therefore a chronological path \(A\to M\to C\). Its remaining outputs are one at \(A\), one at \(M\), and two at \(C\). [Two-sink restriction](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md#two-elementary-source-restrictions)

## A reachable history

Start at site 0 on bits 0, 1, 2. At each site use the least-numbered currently loose output of each listed parent and assign consecutive numbers to the new bits.

| Site | Parents | New bits |
| --- | --- | --- |
| 1 | 0 | 3 |
| 2 | 1 | 3 |
| 3 | 0, 2 | 3 |
| 4 | 1, 3 | 2 |
| 5 | 2, 4 | 2 |
| 6 | 3, 5 | 2 |
| 7 | 0, 6 | 2 |
| 8 | 5, 7 | 2 |
| 9 | 2, 8 | 2 |
| 10 | 1, 7, 9 | 2 |
| 11 | 4, 8, 10 | 2 |
| 12 | 3, 9, 11 | 2 |
| 13 | 6, 10, 12 | 2 |

For each of sites 10 through 13, the following groups contain all earlier witnesses for its first and second, first and third, and second and third parents, respectively. They are \((\{0\},\{2\},\{8\})\), \((\{5\},\{1\},\{7,9\})\), \((\{2\},\{4\},\{8,10\})\), and \((\{7\},\{3\},\{9,11\})\). Each join satisfies all three pair conditions and has no universal witness.

The only loose bits at the end are 27 at site 11, 29 at site 12, and 30 and 31 at site 13. The full ordinary shore is connected and its complement is the exterior alone. Its boundary \(Q=\{27,29,30,31\}\) is therefore a bond. None of the ordinary stars equals \(Q\).

## What the table determines

All six pair distances inside \(Q\) equal three. Any bond attaining one of these minima must be a four-set whose every pair has distance at most three. For every one of the six pairs, \(Q\) is the **unique** such four-set through that pair. Consequently even a single one of those shortest-pair obligations forces \(Q\) in every realization. In this particular matrix all nine such four-cliques are actual bonds, eight ordinary four-stars and \(Q\).

Full scalar inference on this matrix forces rank 14. The first pass has 482 viable supports through size six. The next has 30, all in that rank-14 space. Since the junction stars generate every reachable parity relation, any compatible realization has exactly the displayed space. Every possible mark is therefore forbidden by the all-size equal-state theorem. This can also be seen directly in the displayed fixture because any three eligible inputs would have to be selected among the four loose bits, whose mutual distances are all three, below the necessary bound of four for a legal triple. [Short-support deductions](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/proof.md#what-the-scalars-can-certify-without-reconstructing-a-history) · [Three-mark bound](scalar_inverse.md#a-necessary-distance-within-every-legal-triple)

Here the ordinary role of \(Q\) is also decidable. The ordinary graph has the spanning cycle

\[
0,1,2,3,4,5,6,13,10,9,12,11,8,7,0.
\]

Hence deleting any one ordinary site leaves it connected. The wired graph is 3-connected because deleting the exterior and one site uses this spanning-cycle property, and deleting two ordinary sites uses the general two-site removal theorem. The labeled allowed-state relation recovers the unrooted wired graph, since its vertex stars are precisely the bonds whose deletion leaves connected cycle matroid. The only parallel pair is \(\{30,31\}\), which joins site 13 to the exterior. These two endpoints are the only candidates for the exterior in a reachable representation. Were 13 chosen, the original exterior would have to be the last junction, since its parallel pair supplies the last junction's loose outputs. Its two inputs would be 27 and 29 at sites 11 and 12. Those sites share ordinary meeting 26. Adjacent sites in the bipartite ordinary graph have no common neighbor, so this proposed join is impossible. Thus \(Q\) always bounds the full ordinary shore on this matrix. [Recovery of vertex stars and rerooting](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md)

## Scope of four-clique reconstruction

One can always recover the trivalent stars from the distance-two triangles. Three pairwise incident bits either share a site or close an ordinary triangle, which bipartiteness excludes. For every adjacent pair of recovered trivalent stars \(S,T\), record \(S\triangle T\). This four-bit equation must be a bond, since two disjoint nonempty bonds would need at least six bits.

If **every** four-bond in a candidate class is either an ordinary star or such a sum, the following threshold rule recovers the four-stars. From the graph of pairs at distance at most three, remove links between \(S\setminus T\) and \(T\setminus S\) for each recorded sum. These cross-pairs share no ordinary site, since such a site would close an ordinary triangle. Under the stated hypothesis the remaining links are exactly same-site pairs belonging to stars of arity three or four. A four-clique then consists of four bits of a single four-star. The fourteen-site shore shows precisely where that hypothesis fails.

Without this hypothesis a sufficient test for a proposed \(Q\) is to find a pair at distance three belonging to no other threshold-three four-clique that avoids containing a ternary star. A minimum bond through the pair must be on that list. Uniqueness certifies its support. The example above passes the stronger test without even deleting candidates containing ternary stars.

## One extension hides a pairing inside six bits

Add site 14 on bits 27 and 30, with two new outputs 32 and 33. The parent sites 11 and 13 have the common neighbor 12. Split the six involved bits into

\[
X=\{27,30\},\qquad Y=\{29,31\},\qquad Z=\{32,33\}.
\]

The old frontier \(X\cup Y\) remains a bond because every new equation using the new junction includes its fresh outputs and cannot be a proper subword of the old bond. The new site gives the bond \(X\cup Z\), and the new full frontier gives the bond \(Y\cup Z\). These three supports cover all fifteen pairs. Every ordinary holder of these six bits has arity four or five, so no pair lies in a ternary bond. **All fifteen scalar entries are exactly three.**

Exactly three of the fifteen four-subsets of these bits are parity equations, namely the three displayed unions. Every other four-subset uses two bits of one group and one bit of each other group. It shares three bits with a displayed equation. If it too were an equation their sum would have support two. In particular every pair in every genuine quartet now admits false four-clique completions, none containing a ternary star. Even the complete six-bit scalar submatrix admits every permutation of the six bits, while only permutations preserving the three pairs preserve its four-bit equations. Additional entries in the full width-34 matrix are available to its reader. This local obstruction establishes no differing full-table verdict.

For an inclusion chain of nonlocal four-bit shores, the indices at which a particular bit crosses form an interval because its ordinary tail must lie inside and its head outside, using the exterior as the head of a loose bit. If only shared membership in those four-bit boundaries supplied links, four pairwise linked bits would have four pairwise intersecting intervals and hence a common shore. The six-bit example explains the obstacle to using that observation on the scalar matrix. The intervening ordinary star supplies exactly the links needed to disguise the two adjacent frontier supports.

The following check runs with the workspace Python from this proof directory. The history gives an explicit size bound for the phenomenon.

~~~python
from itertools import combinations
from check_32_realizations import graphic, short

parents = [(0,), (1,), (0, 2), (1, 3), (2, 4), (3, 5), (0, 6),
           (5, 7), (2, 8), (1, 7, 9), (4, 8, 10), (3, 9, 11), (6, 10, 12)]
stars = [(0, 1, 2)]
loose = [[0, 1, 2]]
width = 3
for step, group in enumerate(parents, start=1):
    used = [loose[i].pop(0) for i in group]
    count = 3 if step <= 3 else 2
    fresh = list(range(width, width + count))
    stars.append(tuple(used + fresh))
    loose.append(fresh)
    width += count

short.bridge.replay(stars)
bonds = graphic.cut_supports(short.bridge, stars)
table = short.bridge.scalar_table(bonds, width)
q = (27, 29, 30, 31)
assert tuple(i for ports in loose for i in ports) == q
assert width == 32 and short.as_mask(q) in bonds
cliques = short.short_cliques(table, width, 4)
assert len(cliques) == 9 and set(cliques) == {s for s in bonds if s.bit_count() == 4}
for i, j in combinations(q, 2):
    assert table[i, j] == 3
    pair = (1 << i) | (1 << j)
    assert [s for s in cliques if s & pair == pair] == [short.as_mask(q)]
forced, undecided, passes = short.infer(table, width)
assert len(forced) == 2**14 and not undecided
assert [row["viable_supports"] for row in passes] == [482, 30]

next_star = (27, 30, 32, 33)
short.bridge.replay(stars + [next_star])
next_word = short.as_mask(next_star)
next_space = forced | {word ^ next_word for word in forced}
pairs = [{27, 30}, {29, 31}, {32, 33}]
six_bits = sorted(set.union(*pairs))
actual = {short.as_mask(s) for s in combinations(six_bits, 4)
          if short.as_mask(s) in next_space}
assert actual == {short.as_mask(a | b) for a, b in combinations(pairs, 2)}
assert all(len(set(six_bits) & set(star)) < 2
           for star in stars + [next_star] if len(star) == 3)
~~~
