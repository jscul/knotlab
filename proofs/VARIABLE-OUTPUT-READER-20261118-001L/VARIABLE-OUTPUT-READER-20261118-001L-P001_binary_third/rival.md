# Excluding the unary-third rival when a larger four-cut is forced

Assume a unique ternary seed and exactly three three-fresh additions,
all unary. Every other addition uses two or three parents and makes
two fresh distinctions. If a cut of size four has at least three
sites on its ordinary shore, the current triple menu is empty.
The conclusion holds at every size. It applies when matching pair
readings force such a cut in a proposed rival.

## A four-cut requires five shrinks

Take the latest three sites in an ordinary shore of size at least
three. They make at least six distinctions. At most two are consumed
within those three sites by ordinary simplicity and bipartiteness.
Any later use inside the shore would be at one of these same sites.
Thus at least four distinctions leave the shore. A four-cut makes
this an equality, with no incoming bit. The shore is parent-closed
and contains the seed, since following parents stays in it.

Restrict the original order to the shore. All the actual parents
remain. The first common witness of two parents predates the
younger parent, since a later first witness would itself have
needed an earlier witness to join them. It is therefore a parent
of the younger site and belongs to the shore. All required pair
witnesses survive. Removing sites cannot add a universal witness
for a triple. Thus the restriction is a lawful history.

In the restricted history, the first two additions must be unary.
At the second, the seed and its first child have no common witness.
Both additions make three outputs by uniqueness of the ternary seed.
If the shore has only those two three-fresh additions, it is in
the earlier J family. That exact closure has at least five loose
bits at every size. A four-cut therefore includes all three unary
three-fresh additions. The total of their increments is six, so
the restricted loose count is \(9-t\), where \(t\) is the number
of shrinking additions in the shore. Four loose bits require
exactly five such additions. [Exact J frontier bound](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins)

The whole history has at least five shrinks too, giving at most
four loose bits. The latest-three estimate now forces exactly
four loose bits. All four come from the latest three sites.
Those sites each make two outputs and have exactly two internal
meetings, forming a path. If fewer than three are still loose
holders, there is no candidate triple. Otherwise the three
holders include adjacent sites. Their opposite colors preclude
a common ordinary witness for that pair. The whole triple menu
is empty.

## What the extra unary attachment can retain

If the extra unary site has never supplied an input to a later
site, its three fresh bits are all loose and the site has only
its original parent as an ordinary neighbor. Any triple using
that site would use this parent to witness each of its pairs,
making the parent common to all three. At five total loose bits
there are only two loose bits elsewhere, so a positive menu
requires the extra unary site to have an ordinary child.

Its first such child must be binary. At that birth any two
additional parents would both meet the unique old neighbor of
the unary site, which would witness all three. The actual binary
child uses one additional parent and closes a four-cycle through
the original unary attachment. Hence that attachment cannot
remain an ordinary bridge in a positive five-loose history. If
the original side was already two-connected when the extra
unary was born, additions before its first child preserve
two-connectivity of the old side. The first child then adds
a path through the unary site between two different sites of
that side. The entire ordinary graph is two-connected and
remains so under the subsequent two- or three-parent additions.
Removing the extra unary site itself always leaves connectivity,
since each later site retains at least one other older parent.

## Bounded frontier control

The check uses the exact loose-holder state and both initial
shapes. It records the number of prior shrinks when the additional
unary birth occurs. That birth changes the loose count by two.
Every later binary move preserves the count, and a shrinking
move decreases it by one. A breadth-first search visits every
such tagged frontier first reachable within 16 ordinary sites.
This is width at most 36 after the extra unary birth. The state
recurrence determines every continuation, so an earlier
representative covers all later realizations at the depth bound.

There are 39,547 bounded records. At three shrinks, 57 of 329
records have legal triples. At four shrinks, all 27 reached
records have empty menus by literal replay. They all have the
extra unary birth before the first shrink. The set of these
27 records is closed under every continuation, with 64 transitions
and empty menus throughout. This last check covers arbitrary
continuation depth from the reached records. The all-size
exclusion used for comparison follows from the four-cut argument
above.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001L/VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third/rival.py
~~~

[Replay checker](rival.py) · [Counts and literal control](rival.json)
