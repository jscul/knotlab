# Six-bit equations at a four-place cycle

Suppose a reachable source has one ternary seed and no bond of size at most
six with three or more sites on its ordinary shore. Suppose each component of
the ordinary graph on four-place sites is a tree or has just one cycle,
of length four. Consider a proposed shortest extra six-bit equation
\(W\) in a rival. Assume every source equation also holds in the rival
and each ordinary source site holds at most two bits of \(W\).
Every translate by source equations must have weight at least six.
If the common seed equation is the rival's unique ternary equation,
every six-bit rival equation is a bond, since a nonminimal one would
need two disjoint ternary bonds. Thus every weight-six translate must
pass all pair tests \(K\le6\) in the source when the tables agree up to
that threshold.

Under these conditions no \(W\) exists.

## Localizing the seed-free bits

At most one bit of \(W\) is at the seed, since with two its seed translate
would be shorter. Remove the possible seed bit to get \(Q\) of size at
least five.
In a bond of size at most six, two seed-free bits must meet at a site or
have holders at adjacent four-place sites. This follows from the
one- or two-site shore condition. In a short adjacent sum that uses
the seed, both seed-free bits meet at the other site.
Every \(q\in Q\) therefore has a four-place holder. Otherwise its at most
two holders could account for only two other members of \(Q\).

Let \(F\) denote the ordinary graph on the four-place sites. For each
\(q\), its holders in \(F\) are a single vertex or the endpoints of an
edge. Subdivide each edge of \(F\) once. Let \(T_q\) contain these holders
and every subdivision vertex next to one of them. Two such sets meet
exactly when their holder sets meet or contain adjacent vertices. A
disjoint pair must have one common holder outside \(F\). Each bit has
at most one such holder, and this holder has at most two bits of \(W\).
Thus the disjoint pairs form a matching. All \(T_q\) lie in one component
of \(F\), since two occupied components would give one set disjoint from
at least two others.

In a tree, disjoint \(T_q,T_r\) have an ordinary vertex strictly between
their holder sets on the unique connecting path. Every other \(T_s\)
must meet both, so that vertex would hold at least three bits. If all
sets meet pairwise, the subtree Helly property gives a point belonging
to every set. One can see this by rooting the tree and choosing the
deepest of the sets' nearest vertices to the root. It belongs to every
set because it lies on the route from each nearer vertex to a pairwise
intersection. An ordinary vertex can hold two marked bits at most. A
subdivision vertex can belong to at most four sets, two from each end
of its edge. Both possibilities are impossible for \(|Q|\ge5\).

Now take a component with a unique four-cycle. Suppose the holders of
\(e\in Q\) all lie off that cycle. They lie in one pendant tree \(B\),
whose only attachment to the cycle is a vertex \(c\). Write \(P=B+c\).
If another \(T_f\) is disjoint from \(T_e\), the two holder sets are
separated by an intermediate ordinary vertex. If the holders of \(f\)
meet \(P\), take an intermediate vertex on their unique connecting
tree path in \(P\). The distance between the holder sets is at least
two. If the holders of \(f\) miss \(P\), take \(c\). Deleting the
chosen vertex separates the two sets in the whole component, since any
route outside \(P\) leaves and returns through \(c\). The other at
least three sets have to contain that vertex.

Thus every \(T_f\) meets \(T_e\) inside \(P\). Restrict all of them to
the subdivided pendant tree \(P\). The restrictions are connected. If
two original sets meet outside \(P\), both contain \(c\) on the way from
their intersections with \(T_e\), so their restrictions also meet.
These restrictions therefore satisfy the same matching bound as in
the tree argument. They still contain the adjacent subdivision vertices
at each of their ordinary holders inside \(P\), so every disjoint pair
has an intermediate ordinary vertex. The tree argument gives the same
contradiction. Each bit of \(Q\) must consequently touch the four-cycle.

## The four translations that generate all local tests

The four cycle sites have four internal distinctions and eight external
slots. Let \(m\) be the number of \(W\) bits on those twelve slots and
\(i\) the number of selected internal distinctions. Then \(m\in\{5,6\}\),
and \(m+i\le8\) by the two-per-site incidence bound. Summing all four
stars gives precisely the eight external bits, so minimality gives
\(m-i\le4\). Also, an unselected cycle distinction cannot join two
saturated sites. Flipping both stars across such a meeting would
cancel four selected bits from their six-bit sum.

For \(m=6\) we have \(i=2\) and all sites are saturated, which violates
the last rule. The same rule excludes \(m=5,i=3\). For \(m=5,i=2\)
there is one unsaturated site and both unselected internal distinctions
must touch it. The two selected internal distinctions form the path
opposite it. The three stars excluding the middle of that path have
an eight-bit boundary containing all five local bits. Their sum
shortens \(W\).

The only remaining case is \(m=5,i=1\). Sum the three stars excluding
one endpoint of the selected internal distinction. The sum contains
the selected internal distinction and all selected external bits
except those at the omitted site. Minimality forces a selected
external bit at that endpoint, and likewise at the other endpoint.
Each receives exactly one. The two remaining external bits must be
distributed one per remaining site, since putting both at one site
creates another unselected internal distinction between saturated
sites. The sixth bit of \(W\) is the exterior seed distinction.

The chosen external bits at each pair of opposite cycle sites must
have the same outside holder. Any route giving adjacent four-place
holders to such a pair would create a second cycle in \(F\). Now flip
the star at one endpoint of the selected internal distinction. This
preserves the size, and exchanges its selected external bit for the
other external bit at that site. If the replacement is at the seed,
the translate has two seed bits and can be shortened by the seed
equation. Otherwise it cannot have the same outside holder as the
first external bit, by ordinary simplicity. Its pair with the
opposite external bit in the translate therefore has \(K>6\).

## Why a single binary exception cannot make a longer cycle

Before the sole two-fresh binary addition, each four-place site was
born unary. Thus \(F\) is a forest. In each component all but its
first site have one earlier parent in that component. If the exception
joins two four-place sites in one component, the younger site's
unique parent is an earlier common witness for the pair. Indeed a
first common witness born after both sites would already need a
witness at its own birth. The younger site's parent is four-place,
since otherwise the younger site would be the first site of its
component. The two-step path through that parent is the unique path
in the forest, so the added site creates exactly a four-cycle.
Other placements of the exception leave a forest. Later unary
four-place sites cannot add cycles.

## Exact coverage of the local check

The check enumerates the 12 named cycle slots and one extra seed bit.
It considers every six-subset and all sixteen translations. It
enumerates every partial matching between external slots at opposite
cycle sites, with every permitted way to place zero, one, or two
cycle-to-seed slots. This covers every outside holder coincidence
relevant to a seed-free pair. An outside holder can meet only one
color on the cycle by bipartiteness, and meets a given site at most
once by simplicity. Thus the two pairs of opposite cycle sites have
independent partial matchings. With no cycle-to-seed slot there are
seven matchings on either pair, for 49 models. With a single such
slot there are eight placements and \(3\cdot7\) matchings each,
for 168 models. With two such slots there are eight placements on
opposite sites and \(2\cdot7\) matchings each, for 112 models.

The remaining outside choices are existentially relaxed. All pairs
involving a seed bit are allowed, and an outside matching may be
counted even when no serial history realizes it. Rejecting this wider
set suffices for the localized necessary conditions.

There are 1,716 six-subsets and 329 outside models. For each model
64 words pass the weight test under all four stars. Across those
models 1,024 words also pass the first seed and pair tests. All 1,024
fail a tied pair test and 768 also reach a tied word that shortens
under the seed equation. A control using a deliberately non-simple
outside incidence does pass the same tied tests. The earlier
six-bit pair clique is also reproduced as a local control and
shortens by two after flipping the stars at \(p,w\).

Run from the repository root with the Python environment.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001I/VARIABLE-OUTPUT-READER-20261118-001I-P001_cycle_obstruction/local_check.py
~~~

[Checker](local_check.py) · [Exact counts and controls](local_check.json)
