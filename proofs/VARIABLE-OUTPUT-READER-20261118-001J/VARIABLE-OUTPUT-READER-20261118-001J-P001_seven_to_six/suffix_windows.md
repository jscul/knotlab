# The smallest ordinary shores with six boundary distinctions

Assume the serial rule with two or three fresh distinctions at every
addition and a unique ternary seed. Among ordinary shores of at least
three sites, a boundary of size at most six needs at least nine sites
and at least 21 distinctions in the whole source. Both bounds are
sharp. A proper such shore needs whole source width at least 23, also
sharp.

Every nine-site example has boundary size six, no incoming ordinary
distinction, and one of the two ordinary incidence graphs described below.
It includes the seed and the first two births of the original source.

## At least nine sites

The ordinary incidence graph is simple, bipartite and \(K_{3,3}\)-free.
In any \(K_{3,3}\) its latest site would take all three neighbors across
the bipartition as parents, with a common witness among the other two
sites on its own side. That would forbid the birth. For three through
seven sites, the induced number of internal meetings is at most
\(2,4,6,8,10\) respectively. Bipartiteness gives the first three bounds.
At six sites a balanced split cannot be complete. At seven, with
parts three and four, at most two of the four sites can meet all three
opposite sites, giving at most ten. The other splits also give at most
ten. [Earlier small-shore count](../../VARIABLE-OUTPUT-READER-20261118-001H/VARIABLE-OUTPUT-READER-20261118-001H-P001_high_junctions/five_exceptions.md)

Eight sites have at most twelve meetings. For a three-by-five split
the same complete-neighborhood bound gives \(2\cdot3+3\cdot2=12\);
more unequal splits have at most twelve possible pairs. In a four-by-four
split with at least thirteen meetings there are at most three missing
pairs. If they can be covered by deleting a row and a column, the
remaining entries give a \(K_{3,3}\). Hence there are exactly three
missing pairs, with different rows and columns. Each part has a
degree-four vertex meeting every opposite site. All other sites have
degree three and their neighbors are covered by that full vertex on
their own side. None can be latest. The degree-four vertices would
need too many parents, and every degree-three vertex would see a
common witness for its three inputs.

Every nonseed site has total degree at least four. In a shore of size
\(t=3,\ldots,8\), the sum of degrees is at least \(4t-1\), and twice
the number of internal meetings is at most \(4t-8\). Its boundary
therefore has size at least seven.

For a companion suffix count valid at every size, the latest three
sites of an ordinary shore export at least four distinctions, since
they create at least six and share at most two among themselves.
Thus a shore of boundary at most six can have at most two incoming
distinctions. More generally, for its last \(k\) sites with
\(3\le k\le 8\), let \(d_k=2k-4-E_k\) be the deficit in internal
meetings and \(q_k\) the number of three-fresh sites. They export
\(4+d_k+q_k\) distinctions, so \(d_k+q_k\le 2-I\) if \(I\) bits enter
the shore. For \(I=2\), each terminal window has precisely four
exports and contains only two-fresh sites. Extending such a window
backward adds exactly two internal meetings at each step after the
initial three.

## Equality at nine sites and external inputs

The latest site \(x\) meets at most three earlier sites, so nine sites
have at most fifteen meetings by the eight-site bound. A short shore
must attain fifteen, and \(x\) must take three parents inside it. This
site has degree at least five. Since the whole degree sum must be at
most 36, the seed belongs to the shore, \(x\) has degree five and two
fresh outputs, and its seven other sites all have degree four. The
boundary has size exactly six. Only the four-by-five split can have
fifteen meetings. For a three-by-six split, at most two of the six
sites meet all three across from them, giving at most fourteen.
More unequal splits give at most fourteen directly.

**Latest on the four-site side.** Each other site on that side
must miss at least one of the three parents of \(x\), since a
common neighbor would forbid \(x\). The fifteen meetings force
each of the other three sites to meet both remaining sites of the
five-site side and exactly two parents of \(x\). Their omissions
must be all distinct, since otherwise the three sites share at
least one parent of \(x\) as well as the two other sites. This gives
one shape with \(x\) fixed. Its five-site part has internal degree
three at each site. The other three sites on the four-site side
have internal degree four.

**Latest on the five-site side.** Every one of the other four
sites on that side meets \(x\)'s single nonneighbor and exactly two
of its three parents. No parent of \(x\) can be present at all
five sites across the bipartition, because its total degree is
four. Hence the three omitted-parent multiplicities are \(2,1,1\).
This gives the second shape. The parent omitted twice has internal
degree three. After removing \(x\), it is the only site of internal
degree two. Every other remaining site has internal degree at
least three. Since every remaining nonseed site was born with at
most two parents, the degree-two site must be second latest. It
cannot be the seed. All three other sites on its side have all
four bits internal.

In either shape the seed has all three outputs internal. The
first global child is therefore in the shore. It has four
internal bits. In the second shape the only potential exception
on its side is the site proved second latest. Thus the second
global addition also lies in the shore. Both additions are
unary, since the seed and its first child have no common ordinary
neighbor. They must each make three fresh distinctions because
the seed is the unique ternary junction.

Let \(u\) count unary sites among the seven four-place sites of
the shore, and let \(I\) count incoming crossings. Summing their
parent counts and the last site's three gives \(17-u=15+I\).
The first two unary additions give \(u\ge2\), so \(I=0\) and \(u=2\).
This excludes incoming crossings even for proper shores interleaved
with exterior births.

The resulting parent-closed order can be restricted to the
shore. The first witness of a pair of parents predates the
younger parent, since a first common witness born later would
already need a witness at its own birth. It is then a parent of
the younger site and survives restriction. The restricted order
retains every parent and cannot acquire a common witness for a
previously lawful triple. Its width is 21, since its only
three-fresh additions are the first two unary sites.

Every such shore is connected, since following parents reaches the
seed. Every ordinary site outside it has a forward path to the
wired exterior, following outputs that cannot enter the shore.
Thus the other shore is connected as well. Its six-bit support
is a bond in the full presentation.

## Sharpness and finite checks

A source with \(N\) sites has width \(2N+1+s\), with \(s\) the
number of three-fresh additions after the seed. For \(N\ge9\)
there are at least two such additions, so width is at least 21.
For a proper shore \(N\ge10\), giving width at least 23. Width
22 cannot contain a short large shore, since \(N\) would have to
be nine, and the only nine-site sources with such a shore have
exactly two three-fresh additions.

The two incidence shapes both replay from the seed at width 21.
In the first, start with unary three-fresh \(a,b\) on the seed,
make binary two-fresh \(v\) on \(a,b\), and make binary two-fresh
\(c\) on the seed and \(v\). Make one two-fresh site on each of
\((a,b),(a,c),(b,c)\). Their three distinct witnesses allow the
last triple on those three pair joins. Its two fresh outputs
take the frontier from seven distinctions to six. The second
shape is replayed with the named order \(p,b,r,z,s,a,q,c,x\).
Both are recorded with their literal distinction names. A
binary two-fresh addition on a legal pair of their surviving
outputs gives the proper nine-site bond at width 23.
[Named rows and complete cut checks](suffix_windows.json)

The finite check finds 96 \(K_{3,3}\)-free thirteen-meeting graphs
among the 560 labeled four-by-four candidates, with no admissible
last site. Among 15,504 fifteen-meeting four-by-five graphs, it
finds 240 and 720 labeled graph-and-last-site cases of the two
equality shapes. For one fixed naming of each shape it checks
every candidate order and assignment of the incoming slots. It
finds 288 and 96 lawful closed orders and no order with one or
two incoming bits, already before using pair witnesses across a
boundary. All closed orders are independently replayed with the
inherited local rule.

The selected orders have eight and two legal triples just before
the final join. Both have an empty triple menu immediately after.
All 210 pair entries are measured at width 21, including after
renaming. The two full tables have no isometry between them. All
twelve and four self-isometries of the two tables preserve their
respective menus. The attached width-23 controls each have one
proper nine-site bond and one whole ten-site bond of size six.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/suffix_windows.py
~~~

[Replay checker](suffix_windows.py) · [Exact results](suffix_windows.json)
