# A four-distinction bond with a large shore supplies no legal triple input

**Theorem.** In the serial two-or-three-fresh parity law, let \(F\) be a
four-distinction bond whose ordinary shore contains at least three
junctions. No legal three-parent choice uses a distinction of \(F\), in
the current presentation or in any continuation of it.

## The shore can be built first

Use the wired graph of the meeting pattern for the proof. Each shared
distinction goes from its earlier to its later holder, and each loose
distinction goes from its holder to the exterior. The ordinary graph is
simple and bipartite. The ordinary shore \(U\) of \(F\) is the side of its
cut that excludes the exterior.

The latest three sites of \(U\) supply at least six outputs. At most two
of those outputs can be used inside \(U\), since their only possible
recipients inside \(U\) are among the same three sites. Equality is
necessary at cut size four. Each of the three sites makes two outputs,
their internal meetings form a path, and those sites supply all four
boundary distinctions. In particular no input enters \(U\).

Build \(U\) first in its original relative order. It includes the seed
and every parent of each included site. The first common neighbor of any
two sites must precede the younger of the pair. Otherwise that neighbor
would have used both as parents, which requires an earlier common neighbor.
The first common neighbor is thus a parent of the younger site and is
retained when restricting to \(U\). This preserves every required pair
witness, and a restriction cannot create a common witness for three.

Afterwards replay the remaining sites in their original relative order.
Their original pair witnesses are still available. Moving a site of
\(U\) earlier cannot give one of these originally legal three-parent
joins a previously absent common witness. Such a witness would originally
have been born later, using all three parents after their first joint
addition. That later join would already have been forbidden. Each actual
operand is used only once, so its availability also survives reordering.

In this reordered prefix, the middle of the last three sites' path must
be the middle site in birth order. If born first, it spends its two
outputs on the two final sites, and every earlier output has an ordinary
recipient. This is the excluded two-sink history. If born last, both
earlier path sites have a loose output and share the last site as witness.
Joining those two outputs creates the same excluded form, with the last
site of \(U\) and that new join as the two sinks. Thus the path is
\(A\to M\to C\), and the remaining loose outputs are one at \(A\), one
at \(M\), and two at \(C\). All other old sites have no loose outputs.
[Two-sink restriction](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md#two-elementary-source-restrictions)

## Holding one of the four distinctions loose

Call the sites of the reordered prefix old and sites added after it new.
An old site with no available loose output never gains a new neighbor.
In each case below the marked distinction stays loose until the proposed
join. A distinction already consumed is shared thereafter.

### The distinction at \(A\)

While the distinction at \(A\) is held, \(A\) has no new child. A new
candidate co-parent of \(A\) must have used an old neighbor of \(A\).
The only one available is \(M\), which can supply at most one new
candidate. The only possible other old co-parent is \(C\), since
\(M\) has the opposite bipartition color and all other old sites have
no loose outputs. With \(C\) and the new candidate present, \(M\) would
be a common witness for all three. This excludes any legal triple using
the distinction of \(A\).

### The distinction at \(M\)

Both prospective co-parents are new, since \(A,C\) are of the opposite
color. Each must be adjacent to \(A\) or \(C\), the only old neighbors of
\(M\) that can have new neighbors. To avoid a common witness of all
three parents, one co-parent \(P\) must be a child of \(A\) and avoid
\(C\), and the other must be a child of \(C\) and avoid \(A\).

The site \(P\) was born unary. At the use of \(A\)'s one output, none of
its old neighbors can have a new child, since the distinction at \(M\)
is held and the other neighbors are exhausted. Thus \(A\) can have no
new co-parent at that join. The only possible old co-parent is \(C\),
which \(P\) avoids.

In the ordinary graph induced by the new sites, the component of \(P\)
starts with no child of \(C\) and retains that property. A join using
only new parents could first merge this component with another one only
if a cross-component parent pair had an old common witness. The only
old sites which can have new children are \(A,C\). The site \(A\) has
just the child \(P\), and \(C\) has no child in the component, even
when it has two children elsewhere. A join using \(C\) and a new
parent from the component already needs a shared witness. Any possible
witness would have to be an earlier child of \(C\), since the old
neighbors of \(C\) have no new children while \(M\) is held. Such a
witness would already belong to the component. These arguments exclude
both a first merger and a first child of \(C\) in the component of \(P\).

Thus \(P\) and any child of \(C\) avoiding \(A\) have no common new
neighbor. They have no common old neighbor either, because the only old
neighbor of \(P\) is \(A\). The required pair of co-parents is illegal.

### Either distinction at \(C\)

Hold one of \(C\)'s outputs. Now each of \(A,M,C\) can have at most
one new child, with the same child possible for \(A\) and \(C\). Let
\(P,U_1,N\) denote these children when present, respectively.

The components of the ordinary graph on the new sites are determined
by meetings and identifications among \(P,U_1,N\). For a join using only
new parents, a pair from different components would need an old common
witness. Each old site has at most one new child, so this is impossible.
For a join using an old parent \(i\), this is the first use of an output
of \(i\), and its neighbors are still all old. Any new co-parent must
therefore be the child of an adjacent old holder on the path
\(A\!\!-\!M\!\!-\!C\). Thus the only joins that can connect new
components are these joins with old parents, and their links are among
the displayed children. If \(P,N\) are distinct, they cannot meet.
At the birth of the later one, the earlier child meets only its own
endpoint among the old sites. It cannot also meet the opposite-color
\(M\), and cannot use both endpoints while \(P,N\) are distinct. Its
endpoint is not adjacent to the other endpoint of the path.

An old co-mark at \(A\) has already been excluded by the first case,
and \(M\) has the wrong color. A new candidate co-parent of \(C\) must
meet \(M\) or \(N\), because these are the only neighbors of \(C\) that
can meet a new site. At most one such candidate meets \(M\), namely
\(U_1\). Two candidates meeting \(N\) give a common neighbor for all
three parents. A legal triple would therefore need \(U_1\) and another
candidate meeting \(N\), with no meeting between \(U_1\) and \(N\).
But then \(U_1,N\) lie in different new components, since distinct
\(P,N\) cannot meet. The two candidates would have no common new
witness across these components and no common old witness, as every old
site has at most one new child. This rules out the last case.

## Consequences for the exhibited four-distinction frontier

In the fourteen-junction history the three holders are \(11,12,13\)
and the boundary is \(\{27,29,30,31\}\). The theorem applies even when
later joins consume any of those outputs. A legal triple must instead
use three new holders. Its pair witnesses are distinct, and among old
sites only \(C\) can witness a pair of new holders. Thus at least two of
its witnesses are new as well. In particular every extension by at
most four junctions has an empty legal triple menu. A longer extension
can have legal triples. For example, start a three-output unary
offshoot on one of the four distinctions, attach one unary child per
output, and join each pair of those three children. The three new
pair joins then have three distinct pair witnesses and no common
witness, so one loose output from each gives a legal triple.
[The exhibited history](short_supports.md#a-reachable-history)

Turning the same boundary support into a junction while retaining the
old checks would give two ordinary meetings with \(C\) and make an
ordinary triangle through \(A,M\). Replacing just one old check cannot
remove both defects. The support at \(C\) must change, as must at least
one of those at \(A,M\). This rules out insertion, a one-check
substitution, and any attempt to make that support a junction by
changing only later checks. A rival with the same complete allowed
relation also has the same legal triple verdicts by the allowed-state
invariance theorem. Equality of scalar tables for rivals with different
relations and marks entirely in the new part remains a separate test.
[Allowed-state invariance](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md)
