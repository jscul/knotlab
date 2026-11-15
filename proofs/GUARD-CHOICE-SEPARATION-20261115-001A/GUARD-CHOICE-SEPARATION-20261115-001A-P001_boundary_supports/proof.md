# When can the two occurrences of a choice be separated?

Status: Proved

## Standard statement

Split a serial two-route layout at a boundary \(y\), with nonempty blocks on both sides. Write \(a,b\) for its outer boundaries. Fix all stage guards. Suppose exactly one typed middle or padding name \(h\) occurs in both blocks, once in each. Each other middle or pad occurs at most twice and belongs to just one block. Endpoint padding, raw-slot witnesses and public guards are private. The original layout uses one value of \(h\). The split layout gives the right occurrence a fresh name of the same role. Both layouts still use the same boundary \(y\).

For \(a,y,b\in\{0,1\}\), let \(L_{ay}\) be the set of \(h\) values admitting a left-block witness, and \(R_{yb}\) the corresponding set for the right block. First omit the external endpoint requirements. Splitting preserves **every displayed boundary triple** exactly when no triple has two nonempty disjoint supports. For a Boolean \(h\), such a loss means that the two blocks force opposite values. Splitting preserves **the two outer boundaries after forgetting \(y\)** exactly when every split-feasible outer pair has at least one \(y\) for which the supports intersect. These criteria can give different answers on the same two-stage guarded input.

The supports are eight Boolean membership queries per side. We give a constructive bound in terms of the actual guards. For block \(i\), let \(q_i\) count internal pad names whose enabled single halves occur with both signs, excluding a pad fixed at the cut. With indexed names and \(r_i\) stages in that block, both support tables, a stored witness per feasible entry and a decision for the original guards take \(O(2^{q_L}(r_L+1)+2^{q_R}(r_R+1))\) operations and \(O(r_L+r_R+1)\) working words. The merge takes constant work on the tables, plus linear work if a complete raw model is requested.

## Nearest known result

The table operation is the natural join of two Boolean relations on their shared attributes. Computing a projection after a join and keeping the attributes needed for consistency are classical database operations. The local predecessor's block solver joins records at \(y\) when no middle or pad crosses the cut. Here we calculate exactly when equality of one additional hidden attribute may be dropped, distinguish two choices of observed boundaries, and compute witnesses on actual guard-pinned layouts. [Yannakakis, *Algorithms for Acyclic Database Schemes*](https://www.sigmod.org/publications/dblp/db/conf/vldb/Yannakakis81.html) · [Unshared-boundary solver](../../SWAPPED-ROUTE-GROUPING-20261115-001C/SWAPPED-ROUTE-GROUPING-20261115-001C-P001_decision_and_controls/proof.md)

## Joining the supports

A mask \(00,01,10,11\) represents respectively \(\varnothing,\{0\},\{1\},\{0,1\}\). For the displayed triple \((a,y,b)\), the exact predicates are
\[
 J(a,y,b)=[L_{ay}\cap R_{yb}\ne\varnothing],\qquad
 S(a,y,b)=[L_{ay}\ne\varnothing]\land[R_{yb}\ne\varnothing].
\]
Every whole witness restricts to two local witnesses with the same \(y,h\). Conversely, choose an \(h\) in the intersection and a witness from its corresponding entry on each side. Their only common variables are \(y,h\). Concatenating their boundary sequences at \(y\) and their occurrence values yields a consistent whole witness. In the split layout each side may choose its own \(h\), which proves the second identity. Thus \(J\) implies \(S\), and \(S\land\neg J\) is exactly an opposite-singleton pair. Witnesses chosen independently before selecting a common supported value may require replacement.

For the outer relation replace \(J,S\) by \(\bigvee_y J,\bigvee_y S\). It is necessary to use the same \(y\) in each left-right comparison. For example, if both blocks enforce a route across themselves and additionally have an incoming implication from their own start to \(h\), then with \(a=1,b=0\) the left block requires \(y=1\), the right \(y=0\). Their unions of supported \(h\) values over these distinct boundaries share \(h=1\). No \(y\) works in the whole layout.

The positive route implications give a smaller test. A block with boundaries \(t,t\) admits \(h=t\) by giving every boundary and middle value \(t\). A block with boundaries \(0,1\) admits either \(h\) value. For a prescribed middle \(h=v\), assign all internal boundaries and middles \(v\). For a padding \(h\), prescribe its value and give the middles and internal boundaries value zero. All original implications then hold. It follows that the only potentially lost displayed triples are \((1,0,0)\) and \((1,1,0)\). Indeed, if a block rises from 0 to 1 its support is full, and if both blocks are constant with the same value their supports share that value. At the two remaining triples the exact opposite-singleton tests are
\[
\begin{aligned}
(1,0,0)\text{ lost}&\iff L_{10}=\{1\},\ R_{00}=\{0\},\\
(1,1,0)\text{ lost}&\iff L_{11}=\{1\},\ R_{10}=\{0\}.
\end{aligned}
\]
The displayed directions use \(0\in R_{00}\) and \(1\in L_{11}\). The only potentially lost outer pair is \(10\). The split admits it precisely when \(L_{10}\) or \(R_{10}\) is nonempty. The original admits it precisely when
\[
(L_{10}\cap R_{00})\ \cup\ (L_{11}\cap R_{10})\ne\varnothing .
\]
For the actual SAT question the raw external guards enforce the positive first endpoint or negative last endpoint only when their respective twelve guards are all on. Filter the outer pairs by these requirements. If either requirement is absent, a constant assignment of route values can satisfy the other one. A change to the outer relation can therefore be hidden even at the final SAT yes/no test.

## A live example where existential projection conceals the difference

In the first stage use upper middle \(h\), fresh lower middle \(m\), and one pad \(p\) at **both** incoming implications. Enable just the positive padded half of \(a\to h\) and just the negative half of \(a\to m\). Thus \(p=0\) forces the first implication and \(p=1\) forces the second. Disable \(h\to y\), and enable both halves of \(m\to y\). Give all remaining pad positions fresh names. Projecting \(m,p\) leaves exactly \(a\to(h\lor y)\). In the second stage enable just the unconditional upper implication \(h\to b\) and disable all other implications. Both physical occurrences of \(h\) participate.

At \(a=1,y=0,b=0\) the left supports only \(h=1\), while the right supports only \(h=0\). The split accepts this triple. At \(a=1,y=1,b=0\) the left supports both values, so the shared choice \(h=0\) works. In fact all four outer pairs survive, since choosing \(h=0,y=a\) works for any \(a,b\). The sole displayed loss is \((1,0,0)\).

A separate witness control enables the two incoming implications \(a\to h\) and \(y\to h\), with other implications off. The two occurrences can each force \(h=1\), and no displayed triple is lost. At \((1,0,0)\) a left witness with \(h=1\) and a right witness with \(h=0\) satisfy the split formula yet disagree on the original name. Choosing the right witness indexed by \(h=1\) supplies a simultaneous satisfying assignment. Complete agreement of the displayed predicates therefore allows choice of compatible witnesses, without requiring every pair of individually valid witnesses to agree.

## Computing the entries and constructing raw witnesses

For an implication \(D=(u\to v)\) at a pad \(p\), its raw slots have literals \(D\lor p\) and \(D\lor\neg p\). Each slot enforces its padded clause only when all three of its raw guards are on. A slot with any guard off can set the witness at that position true. Both enabled slots force \(D\), independently of \(p\). One enabled slot forces \(D\) only at the pad value falsifying its padding literal. Zero enabled slots release \(D\).

For each side and each prescribed value of \(h\), fix the corresponding pad if \(h\) is a pad. Every remaining pad having just one sign among enabled single halves can be set to satisfy that sign. This can only release implications. Edges with both halves on impose \(D\) at either value. A pad with no such single halves may be set arbitrarily. Enumerate the values of the \(q_i\) remaining mixed pads. For each valuation form the directed graph of the forced positive implications on this block's boundaries and middles. For each pair of endpoint pins additionally pin the corresponding middle when \(h\) is a middle. Mark all vertices reachable from the true pins. There is a witness exactly when no false pin is marked. Necessity follows along each forced implication. For sufficiency assign value one to exactly the marked vertices, and take the current pad valuation. Saving these values in original occurrence order gives one model for that table entry. Releasing the single-sign pads preserves every possible solution on the pinned route variables, so the enumeration is complete.

Compacting each role into indexed arrays costs linear work in the full layout. Each block thereafter uses its own compact indices. Each reachability pass costs \(O(r_i+1)\). There are a constant number of pins per pad valuation, and at most eight witnesses are stored per block. This proves the time and space bounds. Alternatively a block method that accepts all three pins and returns witnesses can be queried eight times. Using a decision-only method would also require extracting the requested model. The predicate test on completed tables does not pay for obtaining them.

Indeed, membership in an arbitrary supplied block table can already encode SAT. Use the listed two-use compiler as the left block. Mark its unused lower middle in its initial external stage as \(h\). Its two implications have every guard off, so prescribing \(h=0\) adds no condition on the source. Pin the two block boundaries to \(1,0\), exactly the endpoint values required by that compiler. Entry \((1,0,0)\) is then present precisely when the source strict CNF is satisfiable. A fresh right stage can contain the other occurrence of \(h\) without sharing any additional name. This observation concerns computing a support entry. [Two-use compiler and endpoint attachments](../../TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md)

To extend the selected route model to every private raw variable, set each guard to its supplied pin. If the endpoint literal is false, choose one inactive slot in its four-clause padding group and set the two endpoint pads to falsify both pad literals of that slot. All the other sign choices then hold. An endpoint whose literal is true permits any pad values. In each ternary slot set a single witness true at an off guard or a true padded literal. This satisfies the witness disjunction and all three guarded clauses. The [solver](solver.py) implements both the table calculation and this linear extension to a signed assignment on the emitted raw variables.

## Replay

The [checker](check.py) uses PySAT on the predecessor's emitted raw strict clauses for the two blocks, the shared layout and the separately renamed layout. It tests every effective one-stage pattern on each side for both crossing roles, selected combinations of those patterns, partially switched-off raw slots and layouts through seven stages. It compares 9,520 local table entries and 4,760 displayed triples across 595 guard vectors. It pins the whole simultaneous boundary/middle/pad witness in 4,368 admitted triples. For each of the 587 actual positive guard inputs it also constructs and evaluates a full raw assignment, including the endpoint pads and every private slot witness. Tests include the externally masked triple, a safe split with incompatible preselected witnesses, and the false positive from forgetting \(y\) too soon. The proof is uniform. The V1 replay compares separate algorithms in the same task, using the actual predecessor emitter and a SAT backend. [Retained counts](checks.json)
