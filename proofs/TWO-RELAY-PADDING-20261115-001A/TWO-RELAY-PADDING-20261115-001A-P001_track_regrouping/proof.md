# Reading disjoint guarded corridors by their shared pads

Status: Proved

## Standard statement

Let $J$ be forced true and $K$ forced false. Take finitely many directed implication chains from $J$ to $K$ with distinct internal original names, private to each chain. Call each such chain a corridor. A given visible switch vector independently enables the two padded halves $D\lor p$ and $D\lor\neg p$ of each original implication $D$. Hidden pad names can repeat anywhere. Each half has three separately named switches and witnesses.

For every fixed pad assignment, the remaining variables extend exactly when the assignment satisfies one normalized clause per surviving corridor. Compute these clauses by the four cases below. If each pad occurs in at most two normalized clause positions, the visible switch vector has a witness exactly when every connected component of the clause graph defined below has a mark or contains a cycle. **Every inclusion-minimal contradictory subset of labelled normalized clauses is one entire unmarked tree component, and each such component is minimal.** The smallest of these components gives the minimum clause count. A satisfying assignment all the way through the raw guarded strict clauses, or every such contradictory component, can be constructed in linear indexed time.

## Nearest known result

Groote and Ploeger use paths of literal tests to express clauses in switching graphs. Tovey established linear-time decision for SAT with at most two occurrences per variable, the matching criterion for equal exact width and maximum degree, and NP-completeness with binary and ternary clauses at degree three. The earlier project result decides a serial family with one repeated middle name. Here we transfer the signed clause conditions to two forced relay names and individually guarded half-clauses, give the assignment on the raw strict formula and identify exactly which whole clause occurrences form minimal obstructions. The bounded-occurrence SAT classifications are classical. [Groote and Ploeger](https://pure.tue.nl/ws/portalfiles/portal/3142478/639900.pdf) · [Tovey, theorems 2.1 and 2.4 and section 3](https://doi.org/10.1016/0166-218X(84)90081-7) · [One-relay predecessor](../../ONE-RELAY-PADDING-20261115-001Z/ONE-RELAY-PADDING-20261115-001Z-P001_synthesis/proof.md)

## The clause for an actual switch vector

For a half with three displayed literals $L_1,L_2,L_3$, the four raw clauses are

\[
 (w_1\lor w_2\lor w_3)\ \land\
 \bigwedge_{i=1}^3(\neg e_i\lor\neg w_i\lor L_i).
\]

If any $e_i=0$, taking that $w_i=1$ suffices regardless of the literals. With all switches on, some literal has to be true and its witness can be chosen. Thus a half is active precisely when all its switches are on. At an occurrence $D=(u\to v)$, a drop means $u=1,v=0$. The two half-activations specify exactly when the drop is available.

| Active halves on this occurrence | Pad assignments allowing a drop | Contribution to this corridor's disjunction |
| --- | --- | --- |
| Neither | Both values | True, so discard the whole clause |
| $D\lor p$ only | $p=1$ | $p$ |
| $D\lor\neg p$ only | $p=0$ | $\neg p$ |
| Both | Neither value | False, so omit this position |

Every chain from a one to a zero must have at least one drop. Conversely, if one position permits a drop, set the original chain variables up through its tail true and the remaining ones false. This assignment fails only that implication. Different chains can choose their positions independently once a single common pad assignment is fixed, since only $J,K$ are shared original names. This proves the stated equivalence for each pad valuation, before the pads are forgotten.

The corridor condition is therefore a disjunction. Remove repeated equal literals within it, including repeats on consecutive positions. Opposite literals on one pad make the clause true for every pad valuation, even on adjacent positions. If all positions have both halves active, the disjunction is empty and the corridor alone makes the forced endpoints inconsistent. If no clauses survive, every pad assignment extends. Retain separate corridor labels when two surviving rows are identical. Occurrences used by the degree bound are counted after this normalization.

These conditions occur in the original two-branch stage schedule. To realize a corridor of length $2+2h$, put $J$ in the first branch of a starting stage, follow its outgoing implication, then the two first-branch implications at each of $h$ intermediate stages, and the incoming implication to $K$ in the closing stage. Consecutive corridors use disjoint groups of stages. Turn other implications off, apart from the initial $x_0\to J$ and the final $K\to x_r$, whose halves are both active. The endpoint units enforce $x_0$ and $\neg x_r$ using their complete private switch blocks. Hence the two relay values really are forced. An unconditional position contributes no literal and can pad an odd length. Two unconditional positions realize an empty clause.

## Why the component criterion is exact

Use the following classical undirected multigraph to represent the normalized formula. Its vertices are labelled clauses, including each empty clause. A **pure** pad occurs with only one sign, in one or two clauses. Set it to the value satisfying every one of its occurrences, and mark each affected vertex. Every **mixed** pad has one occurrence of each sign in different clauses. Put one edge between those clauses for this pad. Parallel edges from different pads remain distinct. Orienting an edge toward one endpoint means choosing the value that satisfies the literal at that endpoint. Now every vertex must either be marked or receive an edge.

An unmarked connected tree of $k$ clauses has $k-1$ mixed pads. Each can satisfy exactly one of their clauses, so at least one clause fails. This includes a singleton vertex with no literal. In a component with a mark, root a spanning tree at any marked vertex and orient its edges away from the root. Every other vertex then receives an edge. In an unmarked component with a cycle, take one edge outside a spanning tree, point it toward one of its endpoints and root the tree there. Again direct the tree edges outward. This also works when the extra edge is parallel to a tree edge. Assign all unused mixed pads arbitrarily. The pure assignments are consistent even when the same sign marked clauses in different components.

To prove minimality, delete one clause from an unmarked tree component. Each nonempty remaining piece has a neighbour of the deleted clause. A cut mixed pad now has just one surviving occurrence, so it supplies a mark in that piece. The preceding construction satisfies every remaining piece. For a singleton tree, deletion leaves the empty family. Every proper subset of that tree therefore has a model. Conversely, any subset omitting at least one clause from *each* unmarked tree is satisfiable. Use an assignment for the surviving part of each tree and keep the full formula's marked or cyclic components satisfied. Mixed pads belong to single components, and all globally pure pads can take their common favourable value. This proves that the whole unmarked trees are exactly the inclusion-minimal contradictory clause subsets. The statement counts normalized clause occurrences. Raw guard deletion can change a literal within a clause or discard a whole corridor.

For the time claim, assume the input names have integer indices. A linear pass computes the half activations and deduplicates each clause using per-pad signs and clause indices. Another pass collects occurrences and builds the graph. A traversal records one spanning tree, any marked root and any spare edge per component. Each incidence is used a constant number of times, including the outward traversal constructing the assignment. Assign arbitrary values to pads appearing only in discarded corridors. Scan each original corridor to locate one permissible drop and fill its private originals as above. In each raw slot choose one witness whose switch is off or whose displayed literal is true. The resulting assignment and all minimal contradictory components have linear total output size.

## Width and degree measure different restrictions

| Hypothesis on the normalized pad clauses | Consequence |
| --- | --- |
| At most two occurrences per pad, arbitrary width | The component algorithm finds an assignment or all minimal contradictory clause sets in linear indexed time. |
| At most two literals per clause, arbitrary pad degree | This is 2-SAT. Use the implications $\neg a\to b,\neg b\to a$ for $(a\lor b)$ and treat a unit as a repeated literal. An empty clause is immediately contradictory. A pad sharing a strongly connected component with its negation is exactly the remaining failure condition. A reverse implication pairing and topological order of components give a satisfying assignment in linear time. [Aspvall, Plass and Tarjan](https://doi.org/10.1016/0020-0190(79)90002-4) |
| Exactly three distinct pads per clause, each occurring at most three times | Every formula is satisfiable. Any $k$ clauses have $3k$ incidences meeting at least $k$ pads. Hall's theorem assigns each clause a different pad, which can be set to satisfy its occurrence. |
| Both binary and ternary clauses allowed, at most three occurrences per pad | SAT is NP-complete. The binary clauses enforce agreement among copies in Tovey's reduction. |

For the last row, start from the admitted strict three-variable-per-clause SAT problem. For a pad with $k>3$ occurrences, replace its occurrences by $k$ distinct copies with the original signs. Add a cyclic list of $k$ implications from each copy to the next. These binary clauses force every copy to have one common value. Each copy has one original occurrence and two binary occurrences. The linear construction preserves satisfiability in both directions, and an assignment can be checked in linear time. The example of four binary clauses $(p\lor q_i)$ with distinct $q_i$ illustrates the width-two family at degree four. One clause containing four distinct pads illustrates the degree-two family at width four. [Admitted strict SAT source](../../EVIDENCE-001D/EVIDENCE-001D-P001_uniform_strict_3_cnf_sat_completeness_admission/proof.md)

## Literal controls and reproduction

The two corridors imposing $(p)$ and $(\neg p)$ form an unmarked two-clause tree. Replacing the second by another $(p)$ yields two marks and a model. The two clauses $(p\lor q)$ and $(\neg p\lor\neg q)$ have two parallel mixed edges and admit $p=1,q=0$. Two empty corridors each give a separate singleton core. All of these decisions are checked on guarded strict three-variable clauses in the original two-branch stage schedule.

Run the following command from this directory. The checker uses the repository Python environment for the literal SAT replay and prints a JSON object.

~~~sh
python3 -B check.py
~~~

The enumeration retains repeated clause occurrences and includes all normalized degree-at-most-two multisets over three labelled pads through four clauses (3,467 formulas) and over four pads through three clauses (25,436 formulas). Direct truth assignments test all 230,606 labelled clause subsets in the two censuses and independently recover exactly the claimed minimal contradictory sets. A 2,049-clause tree is minimally contradictory. Marking it with one pure pad or closing a cycle with one extra mixed pad yields a constructed witness. An additional test enumerates all 4,096 signings of four three-pad clauses on four names, each pad of degree three.

For two length-two corridors, the checker exhausts the 15 pad equality partitions and 256 half activations per partition. On the actual guarded strict CNF it compares 7,680 complete switch vectors and all 24,064 pad valuations on one representative per half setting. In all 3,317 feasible cases it also constructs a whole raw assignment from the orientation and evaluates every literal clause. Larger controls include a 24-pad example with eight ternary clauses and 24 binary copy implications. Its guarded schedule is unsatisfiable and deleting one source ternary makes it satisfiable. The all-size component classification follows from the proof above. [Executable checker](check.py) · [Numerical evidence](checks.json)
