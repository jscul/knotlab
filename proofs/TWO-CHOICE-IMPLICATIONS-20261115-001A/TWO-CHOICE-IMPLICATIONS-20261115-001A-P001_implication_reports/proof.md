# What two shared middles must report on a positive implication block

Status: Proved

## Standard statement

The starting example has three two-route stages, with a cut after the first. Pin the first, cut and last boundaries to \(1,0,0\). On the left enable only the implications from the first boundary to \(h\) and from \(k\) to the cut boundary. The left then permits just \(hk=10\). On the right enable only \(h\to c\to k\), where \(c\) is the internal boundary between the two right-hand stages. The right permits \(00,01,11\). Both coordinate marginals overlap, but the two blocks have no common assignment. Splitting either name restores feasibility. Every pad can be private. [Original discriminator](../../../research/GUARD-CHOICE-SEPARATION-20261115-001/decision.md)

Consider a nonempty block with fixed boundary bits \(a,b\) and two distinct named middles \(h,k\), each occupying one position in the block. They can therefore each have a mate in the other block under the global two-use limit. Other middle and pad labels may occur twice in their respective roles. Supply the actual guard vector. Suppose the enabled single halves on each pad can all be satisfied by one value of that pad. This includes private pads. Then the exact joint report is either infeasibility, or forced values together with the reachability implications between the remaining free ports. For two ports, the minimum number of proper implications in addition to unary values is zero for Cartesian products, one for a single directed implication with full marginals, and two for equality with full marginals. A directed implication is *proper* here if its two port variables differ.

At pins \((1,0)\) all thirteen possible reports of this form occur on the guarded stage layout. Ten occur in one stage, twelve by two stages, and all thirteen by three. Equality with both values possible first occurs at three stages and requires some internal middle identification. With no such identification at most one proper implication is needed in each block. The two-port report and a corresponding assignment to the physical occurrences take \(O(r+1)\) indexed operations on \(r\) stages with dense names.

## Nearest known result

The abstract projection onto forced values and a preorder, including its count of 13 binary relations and its extension by reachability, was proved in ROUTE-FRONTIER-MEMORY-20261115-001A. Directed implication graphs and their strongly connected components also appear in the classical 2-SAT algorithm. The one-choice predecessor computes local supports and joins compatible witnesses. Here the additional claims concern which reports are attained at each endpoint setting by actual two-use stage blocks, the minimum number of proper implications and stages, and the cases where the individual marginals give the wrong joined decision. [Frontier projection and count](../../ROUTE-FRONTIER-MEMORY-20261115-001A/ROUTE-FRONTIER-MEMORY-20261115-001A-P001_exact_boundary_profiles/proof.md) · [Aspvall, Plass and Tarjan](https://doi.org/10.1016/0020-0190(79)90002-4) · [One-choice support solver](../../GUARD-CHOICE-SEPARATION-20261115-001A/GUARD-CHOICE-SEPARATION-20261115-001A-P001_boundary_supports/proof.md)

## Eliminating the releasable pads

Each branch contains \(x_{i-1}\to M\to x_i\). Each such implication \(D\) has two padded ternary slots, \(D\lor p\) and \(D\lor\neg p\). A slot is active exactly when all three of its guards are on. An inactive slot can choose an off guard's witness, and an active slot can choose a witness exactly when one of its literals is true. With both slots active, \(D\) must hold for either value of \(p\). With exactly one active slot, the pad can release \(D\) by satisfying the selected padding literal.

For each pad examine every position having exactly one active slot. If all selected padding literals on that pad have the same sign, choose the value satisfying that sign. If there is no such position, choose either value. This one assignment simultaneously releases all single halves and respects every position with both halves active whenever its implication holds. Consequently, **for every assignment of the boundaries and middles**, an extension to the pads and private witnesses exists exactly when the implications with both slots active hold. Construct the directed graph \(G\) of these compulsory implications, identifying repeated middles. This condition on pad signs is sufficient for the construction. When a pad has opposite active signs, simply dropping both conditional implications can change the report. [Guard and pad semantics](../../TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md)

The tables below use exposed local boundary pins. If the raw external endpoint groups are supplied, a fully active positive initial group additionally requires \(a=1\), and a fully active negative final group requires \(b=0\). Incompatible supplied pins give the empty report immediately. When merging two blocks, all names besides the shared boundary and the reported ports must be private between them, or any other shared pads must have a common releasing valuation across both blocks. In the latter case, scan the conditional occurrences in both blocks together, choose one releasing bit for each shared pad, and pass the same bits to both witness constructions through `pad_release`. A block using that pad only in unconditional implications can accept either bit.

## Projection and construction of witnesses

The following calculation also works for \(p\) distinct middle ports. Let \(T,F\) be the vertices prescribed true and false by the boundary pins. Write \(u\leadsto v\) for directed reachability, including length zero. If a vertex of \(T\) reaches one of \(F\), the report is empty. Otherwise mark a port forced true if reachable from \(T\), and forced false if it reaches \(F\). For the remaining ports include \(i\to j\) exactly when \(i\ne j\) and \(i\leadsto j\) in \(G\).

All these conditions are necessary by propagation along the compulsory implications. For sufficiency, take any port values satisfying the report, seed the prescribed true vertices and the ports assigned one, and set exactly their reachable vertices true. A false boundary pin is unreachable by consistency and the forced-false tests. A port prescribed zero cannot be reached from a true pin. It cannot be reached from a forced-true port because those ports already lie in the closure of \(T\). If a free port assigned one reached a free port assigned zero, their reported implication would fail. A port that reaches \(F\) cannot be reached by any chosen seed without reaching \(F\) as well. This proves simultaneous extension, and taking the releasing pad values supplies the physical occurrence assignments. In particular, when both ports are free, a missing directed reachability \(i\not\leadsto j\) has a witness with \(i=1,j=0\), obtained from the seeds \(T\cup\{i\}\).

Forward search from \(T\), reverse search from \(F\), and one search from each port compute the report in \(O((p+1)(r+1)+p^2)\) indexed operations, using \(O(r+p^2+1)\) working words including an explicit list of ordered implications. A requested port tuple extends in \(O(r+p+1)\) work. Local dense name arrays take linear time to initialize. If the caller elects to keep indices from a larger namespace of size \(D\), initialization additionally costs \(O(D)\). For two stored reports at the same cut boundary, conjoin their unary conditions and implications on the shared ports. Mark all ports reachable from the union of the true pins. If none of the false pins are reached, the marked set is a common tuple. Extend it in the two component graphs and concatenate the boundary and occurrence assignments. The previous linear private-witness construction supplies all remaining raw variables, including external endpoint pads and guarded-slot witnesses. [Report, join and constructive solver](solver.py) · [Raw witness extension](../../GUARD-CHOICE-SEPARATION-20261115-001A/GUARD-CHOICE-SEPARATION-20261115-001A-P001_boundary_supports/solver.py)

## Exactly which binary reports occur

If one port is forced and the report is feasible, its joint relation is the Cartesian product of the two marginal supports. With both ports free, \(00\) and \(11\) are always admitted. The only choices concern \(01\) and \(10\). Forbidding \(10\) is \(h\to k\). Forbidding \(01\) is \(k\to h\). Forbidding both is equality. Thus being logically implied by a report does not make an arrow its complete description. The report equals one specified proper implication precisely when both ports are free, reachability holds in its direction and fails in the other direction.

| Support on \(h,k\) | Number of types | Smallest report in unaries and proper implications |
| --- | ---: | --- |
| Empty | 1 | Infeasible |
| One assignment | 4 | Both unary values |
| One port fixed and the other free | 4 | One unary value |
| All four assignments | 1 | No conditions |
| Exactly one off-diagonal assignment excluded | 2 | The ordered implication excluding it |
| \(00,11\) | 1 | Both ordered implications |

A single unary excludes two assignments, and a single proper implication excludes one. A singleton therefore needs at least two conditions. With both marginals full no unary restriction can be used. The two diagonal assignments alone need both proper implications. The three remaining Boolean tables are OR, NAND and inequality. Each fails closure under coordinatewise minimum or maximum, whereas all the displayed positive-implication reports have both closure properties. These statements classify the chosen report language on simultaneously releasable pads.

The following counts range over all legal blocks and compatible external guard units.

| Local boundary pins \((a,b)\) | Attainable binary supports | Reason for unary restrictions |
| --- | ---: | --- |
| \(0,0\) | 7 | The all-zero assignment works. Only zeros can be forced. |
| \(0,1\) | 4 | The true last boundary has no outgoing arc, and the false first boundary has no incoming arc. Every port is free. |
| \(1,0\) | 13 | Both kinds of pin and infeasibility are available. |
| \(1,1\) | 7 | The all-one assignment works. Only ones can be forced. |

For \(00\), four rectangles arise from independently choosing “zero” or “free” at each port, and three more full-marginal supports have proper implications. At \(11\) the analogous count uses “one” or “free”. The four full-marginal types are all realized with disconnected external boundaries as described below.

### Realizations and their stage costs

At pins \(1,0\), put \(h,k\) in the two branches of one stage. For a desired unary one, turn on the incoming implication to that middle. For unary zero, turn on its outgoing implication. To leave it free, disable both. This realizes all nine nonempty rectangles. An entire enabled branch forces the incompatible implication \(1\to0\), giving the empty report. With pins \(00\) or \(11\) the same construction supplies all permitted rectangles. Every pin compatible with an all-off stage realizes full support. Each displayed compulsory implication here and below uses both fully active halves, with all undesignated slots off and all pads private.

For a one-way report, put \(h\) in the first of two stages and \(k\) in the second. Enable only \(h\to x_1\) and \(x_1\to k\). Every boundary setting gives exactly \(h\to k\). Reversing the two physical middle positions gives the other direction. With one stage the two different port middles are in parallel and neither reaches the other. More generally, without repeated internal middles, increasing stage order is a topological order with the middles between their adjacent boundaries. Two free ports can never reach each other in both directions, and within one stage neither can reach the other.

For equality use three stages. Put the two ports in the two branches of stage two. Put the same local middle \(J\) in stages one and three. Enable just
\[
 J\to x_1,\qquad x_1\to h\to x_2,\qquad
 x_1\to k\to x_2,\qquad x_2\to J .
\]
Both choices can be zero or both one, and the compulsory directed cycle forces them equal. The outer boundaries are disconnected. \(J\) is the only internally repeated middle, and it occurs exactly twice. Each port occurs only once in this block, so real mates may be placed in another block. Disabling just one raw guard in the two private-pad halves of \(x_2\to J\) releases this implication and gives all four port assignments on the same wiring.

For necessity, neutral ports forced equal must lie in the same nontrivial strongly connected component by the projection theorem. A port occurring only once has just one possible incoming arc, from the immediately preceding boundary, and just one possible outgoing arc, to the immediately following boundary. A port in the first stage cannot be on a directed cycle because the first boundary has no incoming arc. A port in the last stage cannot be on a directed cycle because the last boundary has no outgoing arc. In a block of at most two stages every port occupies a first or last stage. Thus three stages and at least one repeated internal middle are necessary for local full-marginal equality, and the construction attains both bounds. Two separately acyclic blocks can nevertheless impose opposite directions across the same two ports and jointly force equality.

## Exactly when marginal agreement gives a false positive

For two feasible rectangular reports, coordinatewise agreement gives a common tuple. Two full-marginal positive reports share \(00\) and \(11\). The remaining possibility for a failure is a rectangle disjoint from a full-marginal nonrectangular report. That rectangle must avoid both diagonals, hence must consist of the one tuple \(01\) or \(10\). The other report is then either equality or the one proper implication excluding that tuple. Conversely each of those combinations has overlapping coordinate marginals and no common tuple. The introductory three-stage example realizes one of them.

At a displayed triple \((a,y,b)\), any left support available at \(a,y\) and any right support available at \(y,b\) may be supplied together. Rename all private names apart, and identify just the two port names and the cut boundary. Counting an ordered pair together with its displayed triple gives \((7+13)(7+4)+(4+7)(13+7)=440\) cases. An off-diagonal singleton requires a block with endpoint pins \(10\). Exactly four displayed triples have such a block. At each there are two possible off-diagonal singletons and two positive reports excluding each, hence **16 marginal false positives**. This count keeps \(y\) fixed. To forget \(y\), take the union of the joined decisions for its two values.

## Validation and scope

The [checker](check.py) runs the original guarded ternary clauses in PySAT, compares all requested port tuples with the report, and checks selected models by pinning all boundaries and physical occurrences together and evaluating the completed raw model. It replays the original three-stage example with each subset of the two port identities split. For two-stage blocks it exhausts the 12 ordered ways to place the ports, both identifications of the two remaining middle positions and all 256 subsets of the eight compulsory implications. The equality fixture, its one-guard change, and two acyclic blocks giving opposite directions are checked separately. All 440 boundary-triple/report-pair cases are built as actual serial formulas and checked on all four port assignments. Additional tests use two-use, same-sign shared pads, incomplete raw guard triples and up to five ports. A negative raw control uses one pad with opposite single halves to realize OR, outside the simultaneous-release premise. [Numerical replay](checks.json)

The proof is uniform. The finite comparison is V1, using independent raw SAT and clause evaluation within this task. The operation counts apply to constructing this report and extending supplied values on the specified blocks.
