# Bonds of bounded size have bounded across-span on base 16

**Theorem.** For every positive integer \(m\) there is a finite \(F(m)\) such that every bond with at most \(m\) distinctions on base 16 has across-span at most \(F(m)\), irrespective of the along-counts of any of its members. Thus for every fixed size, endpoints sufficiently far apart across the base cannot share a bond of that size. This includes distinctions lying outside the interval between the endpoints.

Here a **bond** is a finite constrained set whose every proper subset is free in the allowed-state sense. An assignment to a free set extends to a state of the whole infinite base. Across-span is the difference of the largest and smallest across-counts in the set. This is a theorem about those projections. It supplies no finite-flip source verdict for a knot at an infinite solution.

## The base

Write a distinction as \((x,r)\) in the previously fixed counts. The rule is not-all-equal on every translate of \((0,0),(0,1),(1,0)\) and of \((0,0),(0,2),(1,2)\). Complement every bit at odd along-counts and call the resulting assignment \(p_x(r)\). For a move from \(p\) to \(q\), a changed bit at \(r\) must have had both \(p(r+1)\) and \(p(r-2)\) opposite to \(p(r)\). Bits can always stay unchanged. These are exactly the two original rules in this representation, including when any number of legal changes occur together. Complementing fixed coordinates preserves free sets and their single deletions. [Base 16 flip rule](../../ACROSS-FOLD-20261112-001A/ACROSS-FOLD-20261112-001A-P001_ladders/proof.md)

## Extending an across interval

Let \(I=[a,b]\) consist of at least three successive across-counts. Keep the constraints for which both the row and its tested neighbour lie in \(I\). This retains each of the two neighbour tests separately, including at the boundary. Every legal succession of such words extends to the whole base.

For the proof, define \(h(r)=r\) on \(I\). Below it use the unique member of \(\{a,a+1,a+2\}\) congruent to \(r\) modulo three. Above it use the member of \(\{b-2,b-1,b\}\) congruent to \(r\). For each step \(d\) in \(\{1,-2\}\), one has \(h(r+d)-h(r)\) in \(\{1,-2\}\). Indeed whenever either end of such a step falls outside, the two images lie in the same end triple, and their difference is 1 modulo three. Pull each word back along \(h\). A change on row \(r\) has both tested neighbours opposite to it, because their images are tested neighbours of \(h(r)\) in \(I\). This works even when the two images coincide. A finite succession extends in both along directions by keeping its first and last words fixed. Conversely any global state restricts to a valid state in that finite rectangle.

## Realizing a bounded number of observations locally

Suppose at most \(m\) observed sites have across-counts in an interval \(I\) of width \(w\ge3\), and the prescribed bits there extend to a global state. List the distinct observed along-counts in increasing order. Project a witnessing state to \(I\). Between two consecutive observed along-counts the first and last words are joined by a walk in the same directed relation on \(2^w\) words. Remove loops in this walk. It now needs at most \(2^w-1\) moves, no more than the original time gap. Fill unused steps by keeping the word unchanged. No observation lies strictly between these two along-counts. This preserves the entire word at every observed along-count and gives at most

\[
H=(m-1)(2^w-1)
\]

moving steps in total. Extend these words along \(h\); changes occur only on those same steps, though the extension may change infinitely many rows.

There is also a realization that uses only the rows of \(I\) enlarged by \(2H\) on each side, with any desired background elsewhere. Let \(M\le H\) be the number of moving steps. Initially copy the first extended word on \(I\) enlarged by \(2M\) on both sides. Set the other rows to the background, held fixed. At the \(j\)-th moving step copy the next extended word on \(I\) enlarged by \(2(M-j)\), leaving every other bit unchanged. On that new interval the previous state still agrees with the previous extended word, including both neighbour sites for every possible change. All changes are therefore legal. At every intervening unchanged step keep every bit fixed. This proves the claim for arbitrarily many unobserved along-counts, independently of their separation. If there is only one observation time, the first word alone suffices.

In particular, if several groups of observations have disjoint enlarged intervals then any separately extendible assignments on them can be realized together. Use each group's initial word inside its interval of influence and the same fixed background outside their union. Carry out all its permitted changes at their prescribed along-counts. Every changed bit and its two previously tested neighbours are inside its own interval. The rule permits independent changes on the same step. Disjoint closed intervals may be adjacent.

## A bound independent of all along-counts

For a fixed \(m\), put \(w_0=3\) and define \(w_{j+1}=2w_j+4(m-1)(2^{w_j}-1)\). Take \(F(m)=w_{m-1}-1\). This deliberately loose bound is only used to establish finiteness.

Start one group at each occupied across-count of a support of size at most \(m\). Enclose its sites in three successive across-counts. A group with current interval of width \(w\) has the enlarged interval just proved, with \(2(m-1)(2^w-1)\) extra sites on each side. Whenever two enlarged intervals intersect, replace their two original intervals by their joint span, and merge the two groups. If all current widths are at most \(w_j\), the next width is at most \(2w_j+4(m-1)(2^{w_j}-1)\). This accounts for both old widths and the entire gap. Each merge reduces the number of groups, so there are at most \(m-1\) merges.

If the procedure ends with two or more groups, each group is a proper subset of the support. If the support were a bond, every assignment to each group would extend to the base. Their enlarged intervals are disjoint, so the preceding construction combines extensions for *every* assignment on the full support. This contradicts binding. A bond must therefore finish in one interval, whose width is at most \(w_{m-1}\). This proves the theorem.

## What this settles

Across-span tending to infinity forces the size of every connecting bond to tend to infinity, uniformly over the along-counts. Equivalently, whenever bond distance exists it eventually exceeds each fixed constant in that across direction. The theorem makes no existence assertion for a pair without a common bond. Along the already proved positive-across family existence is known for its stated range. The proof neither gives the proposed sharp linear lower bound nor determines the growth of balls or a dimension. Along-count separation alone can still grow without any increase in bond size, as the known travelling triple shows.

The standard mathematical statement concerns the across-diameter of finite minimal non-shattered sets in a particular two-dimensional shift of finite type. The finite-state path bound is elementary. The ingredients specific to this shift are the modulo-three extension and the ability to keep any subset of the bits still. The classical comparison is with [Schmidt’s discussion of mixing shapes](https://www.mat.univie.ac.at/~kschmidt/Publications/minnesota2.pdf). No literature priority is claimed. The local checker stress-tests the two ingredients against the original, unflipped constraints. The all-size assertion follows from the proof.

## Independent review and replay

The base 16 proof reviewer independently checked the two ends of the modulo-three extension, deletion of repeated finite-strip words and padding at specified observations, the inset-by-two induction, simultaneous legal changes at adjacent intervals and the merge recurrence. The review found no gap. It was a mathematical reading in this research chat. External peer review and proof-assistant verification are unperformed.

Run `python3 -B proofs/BONDS-AND-COUNT-20261112-001D/BONDS-AND-COUNT-20261112-001D-P001_across_span/check.py` from the repository root. It checks both along parities against the original NAE constraints, all strip transitions for widths three through six, localization on all reachable pairs of width three or four, and the simultaneous use of adjacent patches. A control without the two-row margin fails.
