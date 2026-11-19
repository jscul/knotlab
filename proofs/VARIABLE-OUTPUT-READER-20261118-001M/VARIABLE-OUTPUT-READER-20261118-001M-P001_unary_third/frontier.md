# The complete unary-third loose frontier

A history in this family has at most four shrinking joins and at
least five loose distinctions. Four shrinks occur only if the
extra unary join precedes all four. All five-loose records have
empty triple menus. A positive six-loose record also requires the
extra unary join to precede every shrink. [Frozen prediction](../../../research/VARIABLE-OUTPUT-READER-20261118-001M/preregistration.md)

## An exact finite state at every depth

Begin after the first two unary three-fresh joins, with seven loose
bits. The second of those joins may use the seed or the first
child. Every binary two-output join preserves the loose count. A
three-parent two-output join reduces it by one. The one additional
unary join supplies three outputs and consumes one, raising the
count by two. The count is \(7-t\) before this birth and \(9-t\)
after it, for \(t\) shrinks.

The predecessor's state keeps the loose count of each live holder,
the ordinary adjacencies of live holders, and the distinct
projected neighborhoods of exhausted sites having at least two
live neighbors. A pair of live holders has a witness if one live
adjacency row or an exhausted projected neighborhood contains both.
For a triple use the pair test and require that no row or
neighborhood contains all three. At an addition, decrement each
parent by one and add its incidence to the newborn holder. Include
the projected neighborhoods of parents that exhaust their
outputs. An exhausted site can never gain another neighbor, so
projection preserves its effects on all later moves. Holder
names within equivalent records can be permuted. [Exact quotient and predecessor replay](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins)

The record includes the number of prior shrinks at the extra
unary birth or a flag that the birth has yet to occur. This is all
the history needed for the allowed move types. The count bound of
nine live holders makes the set of records finite independently of
history length. The two starts close to 74,546 records and 484,418
transitions. The previous bounded control through 16 sites is
reproduced exactly. All 707 post-birth records with five or six
loose bits are replayed on literal histories, checking the
inherited rule and the frontier at every step on those paths.
[Earlier bounded control](../../VARIABLE-OUTPUT-READER-20261118-001L/VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third/rival.md#bounded-frontier-control)

## Timing, earliest sources and binary predecessors

After the extra unary birth the reachable records are as follows.
Widths are assigned by breadth-first search, since at fixed site
count each completed source introduces the same number of bits.

| Shrinks before extra unary | Total shrinks | Loose bits | Records | With a legal triple | First width | First positive width |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 9 | 46,659 | 12,292 | 12 | 18 |
| 0 | 1 | 8 | 14,766 | 4,968 | 20 | 22 |
| 0 | 2 | 7 | 3,038 | 1,053 | 24 | 26 |
| 0 | 3 | 6 | 338 | 57 | 28 | 30 |
| 0 | 4 | 5 | 27 | 0 | 32 | — |
| 1 | 1 | 8 | 5,994 | 785 | 24 | 28 |
| 1 | 2 | 7 | 1,209 | 154 | 30 | 42 |
| 1 | 3 | 6 | 171 | 0 | 44 | — |
| 2 | 2 | 7 | 1,055 | 154 | 30 | 42 |
| 2 | 3 | 6 | 171 | 0 | 44 | — |

The six-loose graph has 680 records and 2,440 binary transitions.
Of its 57 positive records, 37 have an incoming binary transition.
Its reverse binary subgraph reaching a positive menu contains 63
records and 80 transitions. Six currently empty records are one
binary move from a positive. The archived graph gives the complete
record and triple groups at every index.

At five loose the closed binary graph has 27 records and 64
transitions. Each menu is empty, so a fifth shrink cannot occur.
The first literal five-loose source has width 32. The earliest
positive six-loose source has width 30 and permits
\(\{21,23,28\}\) and \(\{21,23,29\}\).

## Exact complementary choices

For each possible extra unary birth and subsequent source move
with parent set \(P\), subtract its one consumed bit per holder.
The other bits can be taken by a single legal rival group exactly
when the residual holder counts are all zero or one and the
nonzero holders form a legal parent group. This test includes
unary rival choices even though the source allows no further
unary moves.

There is exactly one record and source holder group passing the
test. At six loose, three holders each have two loose bits, with
the same parent group on both sides. The source has eight literal
ways to select one from each holder and the other group receives
the opposite choices. The named width-30 example uses
\(P=\{24,26,28\}\) and \(Q=\{25,27,29\}\). Completing either with
two fresh bits gives an empty menu at width 32. These two last
equations differ by the sum of all prefix equations, the six-bit
loose boundary. Thus those literal completions have different
last supports and identical allowed states. This equality
follows directly from the equations.

## Larger five-cuts in positive sources

Let \(U\) be an ordinary shore with at least three sites and at
most five boundary bits. Its latest three sites make at least
six outputs, with at most two ordinary meetings between them.
Thus at least four bits leave \(U\) and at most one enters it.

The seed must belong to \(U\). Otherwise its earliest site takes
the one entering bit and is unary with three fresh outputs.
Deleting that input makes it a local ternary seed. Every other
site of \(U\) keeps all its parents. The first common witness for
two parents predates the younger parent, since a later first
witness would need an earlier one. An outside witness would
therefore supply a second entering bit at that younger parent,
which is impossible. Restriction thus gives a lawful history.
Its first two additions again require unary three-fresh births.
These exhaust the two remaining global three-fresh allocations,
so the restricted history is in J and has at least five loose
outputs. The one incoming bit left room for at most four.
[J lower bound and replay](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins)

Now suppose the current source has a legal triple, so \(t\le3\).
If a bit enters \(U\), all four exports come from the latest
three sites. An ancestral chain from the seed to the outside
holder of the incoming bit must leave \(U\) before the bit
returns. Thus its inside recipient lies among the latest three
sites. This is after the first three sites of \(U\), since short
shores here have at least nine sites. The first three have at
least seven boundary bits. Each later selected site adds
\(p+h-2j\) to the boundary, with \(j\) selected parents.
The incoming bit contributes an additional two at its recipient
over the baseline \(h-p\). Only the \(t\) shrinking sites can
contribute a negative baseline. The total is therefore at least
\(7+2-t\ge6\), a contradiction. The shore is parent-closed.
[Minimum short-shore size](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/suffix_windows.md#at-least-nine-sites) · [Boundary increments](../../VARIABLE-OUTPUT-READER-20261118-001I/VARIABLE-OUTPUT-READER-20261118-001I-P001_cycle_obstruction/nonshrinking.md)

The parent-closed shore can be moved to the start. Its internal
birth order remains lawful by the first-witness argument. For
an outside join, moving the shore earlier retains each pair
witness. A newly earlier shore site cannot already meet an
outside parent of that join, because every ordinary crossing
is directed out of the shore. If it became a common witness
for an outside triple, all three parents would need to be in the
shore. In the original order this shore site would have joined
later on those three parents with the outside site already a
common witness, which is forbidden. The reorder is lawful.

With all three unary three-fresh births inside, the shore would
have at least six outputs at \(t\le3\). Thus it has exactly two
such births and two shrinks, the J case with five loose bits.
Moving it to the start puts the extra unary birth after two
shrinks. There are no positive three-shrink histories in that
order. Consequently a positive source has a larger five-cut
exactly when it has two shrinks and admits a lawful order with
both before the extra unary birth. In that order their J prefix
has five loose bits and supplies the cut. The prefix is connected
and every outside site can follow outputs to the wired exterior,
so the cut is a bond.

The first positive source of this type has width 42. Its first
twelve sites have boundary \(\{18,22,24,25,26\}\). At the
current stage the source admits \(\{35,36,40\}\) and three
other triples. The full history, proper shore and literal
two-shore connectivity check are archived.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001M/VARIABLE-OUTPUT-READER-20261118-001M-P001_unary_third/frontier.py
~~~

[Replay checker](frontier.py) · [Exact closure and named witnesses](frontier.json)
