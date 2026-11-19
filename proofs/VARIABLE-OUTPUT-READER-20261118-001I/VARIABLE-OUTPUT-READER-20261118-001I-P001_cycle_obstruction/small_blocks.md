# Three small four-place blocks exclude a shortest extra equation

The local tests leave zero survivors for the three ordinary graphs
\(K_{2,3}\), \(K_{2,4}\), and \(K_{3,3}\) with two disjoint meetings
removed. These are the classical names of the tested bipartite blocks.
The result uses the source short-shore and common-equation hypotheses
of the shortest-word argument. It applies to a maximal biconnected
block inside a larger four-place graph. [Shortest-word conditions](cycle_inverse.md#what-an-extra-equation-would-force) · [Exact checker](small_blocks.py) · [Counts and examples](small_blocks.json)

## Confinement to a maximal block

Consider a shortest extra six-distinction word \(W\) in an alleged
rival with the same table through \(K=6\). Each of its equal-weight
translates by common equations is a rival bond, since the seed is
the only ternary bond. Each such word uses at most two distinctions
at a holder and at most one at the seed. For a six-place source star
the bound of two uses the identifying pair required in the
shortest-word argument.

Delete the possible seed distinction, leaving a set \(Q\) of at least
five. Each member has a four-place holder. Every pair in \(Q\) needs
equal or adjacent four-place holders or a shared non-four-place holder.
Indeed the source's short bonds are single stars and sums of two
adjacent stars. For a cross-pair of seed-free distinctions in a short
two-star sum, both stars must have four places. The four-place graph
induced by all the four-place holders of \(Q\) is connected and contains
a cycle by the previous forest argument.

Let \(B\) be a maximal biconnected block containing one such occupied
cycle. An exterior component of the four-place graph attaches to at
most one vertex of \(B\). Otherwise a path through the component
would extend the biconnected block between two distinct vertices.
Suppose that some selected distinction \(e\) avoids \(B\), and its
four-place holders lie in an exterior component attached at \(v\).
Any selected distinction touching \(B\) away from \(v\), and avoiding
\(v\), must share a non-four-place holder with \(e\). The possible
four-place endpoints of that distinction are in \(B\) and in
components attached away from \(v\). None can coincide or meet the
four-place endpoints of \(e\). There is at most one such partner
\(f\), and \(f\) has exactly one four-place holder in \(B\).

The two places available at \(v\) and the one partner \(f\) can occupy
at most four block vertices. Since the chosen cycle is occupied, it
must have four vertices \(v,a,w,b\) in order. Both \(v a,v b\) are
selected and \(f\) touches \(w\). There is no room for another
selected distinction touching \(B\). Any other selected distinction
avoiding \(B\) must approach the two internal bits \(v a,v b\) through
the same attachment \(v\). It would have to share \(f\)'s non-four-place
holder, which already holds \(e,f\). This leaves at most four
distinctions in \(Q\), a contradiction. Consequently all its
distinctions touch \(B\).

Translating by stars of \(B\) only changes distinctions touching
\(B\). This preserves locality for every equal-weight translate,
including its seed-free part. A selected exterior four-place holder
can be adjacent only to its own attachment vertex among the vertices
of \(B\). Exterior four-place endpoints from two distinct attachments
cannot meet one another. Therefore nonadjacent, disjoint core endpoints
can only pass the pair test by sharing a non-four-place exterior holder.

## Finite domain and results

One slot represents each internal distinction. Each vertex of degree
\(d\) inside \(B\) has \(4-d\) further slots. Bipartiteness puts the slots
at any common exterior holder on one side. Simplicity allows at most
one slot from each core vertex in that group. The checker exhausts
these partitions on both sides and separately specifies the seed as
any group of up to three slots of one color, including none. It allows
one exterior seed distinction if the seed has unused capacity. It
ignores constraints at that proxy's other endpoint and permits all
pairs involving a seed distinction. This enlarges the test domain.

For every six-subset, the checker forms all translates by the block's
four-place stars. A shorter translate rejects the subset. For each
translate still of size six, it applies the holder limits and the
necessary pair tests on all seed-free pairs. A pair passes if its
four-place holders in the block coincide or are adjacent, or its
slots share an exterior holder. As the same test applies to every
weight-six word of a translation class, grading a class preserves the
count of all its words.

| Block | Raw six-subsets | Exterior models | Locally minimal model-word pairs | Initial passes | Final survivors |
|---|---:|---:|---:|---:|---:|
| \(K_{2,3}\) | 5,005 | 1,079 | 431,568 | 25,968 | 0 |
| \(K_{2,4}\) | 12,376 | 8,849 | 14,680,896 | 458,880 | 0 |
| \(K_{3,3}\) minus two disjoint meetings | 18,564 | 5,427 | 25,887,897 | 11,872 | 0 |
| Total | 35,945 | 15,355 | 41,000,361 | 496,720 | 0 |

For example, in \(K_{2,4}\) with parts \(ab\) and \(wxyz\), the word
\(\{aw,bw,by,y{:}1,z{:}0,s\}\) initially passes if the two displayed
ports share a holder and \(s\) is an exterior seed distinction.
Adding the star of \(y\) gives
\(\{aw,ay,bw,y{:}0,z{:}0,s\}\). The ports \(y{:}0,z{:}0\) have
distinct same-color sites and do not share an exterior holder in this
model, so the tied translate fails the pair test. Each block has a
matched control that passes all
conditions when the pair test is omitted. A separate set-based pair
comparison agrees with the compiled pair masks on one nonempty
exterior partition per block. Independent inclusion-exclusion with
Bell numbers checks every seed-specific partition set. In one color,
\(n\) ports with \(m\) repeated origins give
\(\sum_{i=0}^m(-1)^i\binom{m}{i}B_{n-i}\) admissible partitions.

## Consequence for blocks of at most six sites

A nontrivial biconnected bipartite block with at most six vertices has
minimum internal degree two. Apart from cycles, the three shapes
tested here and the eight-meeting six-vertex block exhaust the
possibilities. For a three-by-three bipartition the missing meetings
form a matching, since every degree is at least two. The full
\(K_{3,3}\) cannot occur in the four-place graph. Its latest site would
need three inputs from the block and a four-place site has at most two.

For a simple cycle block, every translate still has its occupied
cycle in \(B\). The only outside four-place endpoints in such a
translate are immediate neighbors of their attachment vertex and
become leaves in the induced endpoint graph. The previous cycle
exclusion then applies to this block. Together with the eight-meeting
case and the three checks here, this precludes a shortest extra
six-word in a source with all four-place blocks of size at most six,
under the stated hypotheses. The all-size conclusion concerns arbitrary
numbers of such blocks, with the short-equation and identifying-pair
conditions still in force. [Cycle exclusion and incidence recovery](cycle_inverse.md#confinement-to-one-cycle) · [Eight-meeting block](dense_check.md)
