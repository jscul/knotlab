# Cubic bond-ball growth from one knot

## Standard statement

Construct the parity incidence code of an orthant by a coordinate-free local rule and bound its minimal dependencies, including after an eight-coordinate finite restriction.

## Nearest known result

The [full-lattice proof](../../LOGIC-AXIS-20261107-001A/LOGIC-AXIS-20261107-001A-P001_rulers_without_ends/proof.md) derives the exponent on a supplied arrangement. The [cut-cube proof](../../CUBE-DOUBLING-20261118-001A/CUBE-DOUBLING-20261118-001A-P001_cube_doubling/proof.md) measures independent orders. The [design](../../../research/CUBIC-FROM-A-KNOT-20261117-001/preregistration.md) states the target and controls.

## Theorem and scope

There is a local assembly from one ternary parity knot, using only which designated constraints share distinctions, with an infinite continuation on which the number of distinctions within bond distance \(r\) of **every** distinction is \(\Theta(r^3)\). All finite steps preserve every old allowed state. Every distinction can change by a finite modification at every solution. A local parallel policy produces this continuation up to relabeling. The more permissive single-addition rule admits other continuations.

There is also a continuation starting with the original six-state betweenness knot, passing through the original eight-distinction cut cube, and keeping its eight distinctions and their exact joint relation. A bounded attachment uses them at the eight corresponding positions of the new meeting pattern. This continuation has the same exponent at every distinction, including each original one. Its finite choices and its proof are given in the [eight-distinction construction](cube_interface.md).

The supplied data are the local assembly law, the local parity relations, and, in the second construction, the finite attachment. The growth rule reads the designated knots' incidence. The volume measurement reads only the allowed states. The classical coordinate description below certifies the outcome. No initial unbounded arrangement, metric, axis names or growth history are inputs to the local update. The classical space obtained is the nonnegative integer orthant. The theorem is about logical dimension measured by volume growth.

## 1. The move and its local parallel policy

A junction is one designated local parity constraint. Distinctions are the binary variables. A loose distinction occurs in one junction. Two distinct junctions are neighbors when they share a distinction. Start with a single junction on three loose bits whose sum is zero mod two.

In a serial move take one loose bit from each of one, two, or three different junctions. For multiple junctions, every pair must have a common neighbor in the current presentation. For three junctions, there must be no common neighbor of all three. Add one even-parity constraint on the chosen bits and three fresh bits. The new relation has arity four, five, or six. There are exactly four completions of any old row, since two fresh values can be chosen freely and the last is fixed. Branches with joins and branches with only singletons are both legal. Consider the singleton branch that consumes all loose bits at each successive level. Its infinite incidence graph is a tree, with both ends of every bit attached. It admits no nonzero finitely supported even flow because a nonempty finite forest has a leaf. The exhaustion condition matters. A serial history that grows just one ray leaves two ports of the seed loose forever, and flipping those two preserves all its equations. Counting its incidence neighbors would measure a different property.

The following parallel policy is specified on the same transitions. All its groups are computed from the current snapshot before any changes.

1. Take the junctions holding loose bits. Two such junctions are candidates for a pair if they have a common neighbor.
2. Use every triple of pairwise candidates with no neighbor common to all three. Use every candidate pair belonging to none of those triples.
3. At each junction assign distinct loose bits to these groups, one per group. Make a singleton attachment for every remaining loose bit. Each group adds the parity junction prescribed above. If the available bits cannot cover the groups, this parallel transition is unavailable.

These tests inspect bounded incidence neighborhoods. For example, every third candidate of a triple containing a given junction is at most two neighbor steps away, and a witness to common-neighbor membership is one more step. A pair's membership in a triple is decided within that same bounded neighborhood of its endpoints. The policy needs no round number. Simultaneous updating is a declared part of the policy. The choice among symmetric loose bits is an arbitrary bijection. Different bijections give isomorphic outputs by permuting the formerly loose bits at their junctions. An allocation need not fix all old bit identities under that comparison. No scheduler supplies any bit value in the allowed-state relation.

## 2. Identification of the meeting pattern

Use coordinates for this proof only. Let \(e_1,e_2,e_3\) be the three unit vectors and \(I_t=\{v\in\mathbb N^3:\sum v_i\le t\}\), with zero included in \(\mathbb N\). In the proposed representation a junction sits at each \(v\), and the three bits it introduces correspond to the positive edges \(v\longrightarrow v+e_i\). A bit becomes shared when that next junction appears. The seed is \(I_0\). After round \(t\), the junctions with loose bits are exactly those with coordinate sum \(t\), each with three.

Inductively two distinct live junctions share a neighbor exactly when they are \(u=a+e_i\) and \(v=a+e_j\) for \(i\ne j\). Among other live junctions the only ones that can be candidates with both are \(a+e_k\) and, if nonnegative, \(a+e_i+e_j-e_k\), with \(k\) the third index. Indeed neighbors on this level differ by a vector \(e_l-e_m\). Comparing its difference from each of \(u,v\) gives just those two alternatives. The first triple has the common old neighbor \(a\) and is excluded. The second is exactly the triple of predecessors of \(a+e_i+e_j\). It has no common old neighbor. If that third predecessor is absent, the pair is precisely the full predecessor set of a child with two positive coordinates. For a parent on this level, its potential children are \(v+e_1,v+e_2,v+e_3\). After all multiple-parent groups, the residual slots count exactly the children with one positive coordinate. The seed has three such slots. This proves the step to \(I_{t+1}\), and hence the assertion at every finite level.

The parallel insertions can be serialized. For parents with a designated common child, each pair has just its lower common neighbor and that child in the full orthant. Other insertions cannot supply a false common neighbor of all three. Every allocated bit stays loose until its own group consumes it. The same reasoning permits **any finite coordinate down-set** to be visited first, using a predecessor-respecting witness order, then extended to the entire orthant. Coordinates here select one permitted serial history. The complete-round construction gives a second description that supplies no such choices of locations.

A box of side \(n\) has \(n^3\) junctions, \(3(n-1)n^2\) shared bits and \(3n^2\) loose bits. Keep all loose boundary bits. Its \(n^3\) parity equations are independent: in any nonempty combination, the last junction contributes its three fresh outputs uncanceled. Its relation has \(2^{2n^3}\) rows. Future insertions extend each row, including in the countable limit by successively assigning the fresh values. Thus the box is also the marginal on its incident bits in that limit. At side three it has 27 junctions, 54 shared bits and 27 loose bits. This is a permitted exact serial prefix. A complete parallel generation makes different finite shapes. In particular the side-three box is contained in \(I_6\), which has 84 junctions. An arbitrary-size box is obtained by the same rule.

## 3. Bond distance on the infinite parity branch

The assembly proves that the limit is described by the classical graph \(G\) on \(\mathbb N^3\) with unit coordinate edges. Its distinctions are the edges. Its allowed states \(C\) are all assignments whose incident sum is even at every vertex. Denote the lower endpoint of an edge \(e\) by \(a(e)\). For \(e\ne f\), bond distance is the least \(|F|-1\) of a finite set of at least three distinctions containing both whose projection is constrained, whose every proper projection is free, and which admits a state. If no such set exists, the distance is infinite. Include the center in its own ball. We use no triangle inequality for this ruler.

**Finite constraint lemma.** For finite \(F\), every linear parity check valid on \(C\) is a finite vertex cut \(\partial U\), for \(U\) a finite set of vertices. Conversely each such cut is valid. For the nontrivial direction, flipping any elementary four-edge square preserves every vertex parity. Hence the check's edge set meets every such square evenly. Its bit sum along any monotone path from the origin to \(v\) defines a potential at \(v\), since neighboring step exchanges sweep a square and relate all such paths. The difference of potentials on an edge is exactly its indicator in the check. The potential is constant outside a box containing the check: any two exterior vertices connect to their coordinatewise maximum in the exterior. Choose that constant to be zero. The check is the cut of the finite set where the potential is one. Conversely sum the equations at vertices of \(U\) to obtain the cut. A finite projection of a binary linear space is determined by all its implied linear checks on that support. Thus this characterizes the entire finite marginal, including K1–K3 minimality.

**Locality of dependencies.** If a check splits into pieces by putting two of its edges together whenever they occur on the same elementary square, each piece separately meets every square evenly. The lemma makes each piece a check. Every minimal dependency is consequently connected by such squares. The anchors of two edges on a single square differ by at most one in sup norm, giving
\[
  \|a(e)-a(f)\|_\infty \leq \delta_C(e,f).
\]
More generally, finite observations with anchor separation greater than one have independent projections. Every check on their union decomposes into checks on the separate sides by the same argument. This statement concerns the allowed sets and entails no probability distribution.

**Existence of long bonds.** For \(e\ne f\), take closest endpoints at ordinary graph distance \(d\). Join them by a shortest coordinate-monotone path \(P\). Neither opposite endpoint lies on \(P\), by minimality, including the case where \(P\) is one shared vertex. The complement of \(P\) is connected. Among three axes two can be assigned the same sign of monotonicity along \(P\), assigning arbitrary signs to constant coordinates. From any point outside \(P\) its two positive rays on those axes cannot both meet \(P\): distinct meeting points would be incomparable in the signed coordinate order of the path. One ray therefore escapes a box containing \(P\). The exterior of that box is connected.

The cut \(F=\partial P\) through \(e,f\) is a bond. Deleting it leaves exactly the connected finite path-vertex set and a connected infinite exterior, so the finite constraint lemma gives just one nonzero check on \(F\), its full parity. There are at least three edges in the cut by taking an extremal positive edge in each direction. At most \(6(d+1)-2d=4d+6\) edges leave the path. Consequently \(\delta_C(e,f)\le4d+5\). Every prescribed star is the same argument with a single vertex. Zero is an allowed state. Each individual edge flips on an elementary square at every solution, giving the infinite-system source condition.

For integer \(r\ge5\), put \(m=\lfloor(r-5)/4\rfloor\). For every nonnegative \(t\) with \(\sum t_i\le m\), take the three outgoing edges from \(a(e)+t\). The endpoint upper bound includes all of them. The lower distance bound limits any ball to anchors in the ordinary sup-norm box of radius \(r\), with at most three bits per anchor. Hence
\[
  3\binom{m+3}{3}\ \leq\ |B_C(e,r)|\ \leq\ 3(2r+1)^3.
\]
Both inequalities concern the infinite state relation. Counting junctions in a finite drawing would not prove them.

## Verification and evidence

The [independent finite check](check.py) reconstructs the incidence without input coordinates. Its separately written auditor recovers the layers and checks the sides three and four serially, row-space conservation including loose outputs, actual projected relations, canonical knot tests, relabeling, alternative allocations and a tree control. The [cut and attachment check](cut_control.py) uses literal betweenness truth tables and a separate parity parameterization for the original eight variables. A separate [bounded path audit](path_check.py) checks the marked-edge escape argument on 2,688 paths. The [recorded results](result.json) give these finite checks alongside the all-radius proof. The proof and its audit were developed in the same research task. There is no independent external referee verdict or proof-assistant certification. External novelty is unassessed.
