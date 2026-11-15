# Refuting the strict cycle by composing endpoint clauses

Status: Proved

## Standard statement

On \(h\ge3\) positions let \(a,b\) be the two shared bits and \(x_i,y_i,z_i\) the three private bits at each position. For stating the input relation write \(F_i=z_i(x_i y_i+ab)\) over \(\mathbb F_2\). Original check \(i\) imposes \(F_i+F_{i+1}=c_i\) with indices modulo \(h\). The source is the actual strict 3-CNF of the preceding proof. Each forbidden assignment to the eight distinct variables of a check has its own six ternary clauses and five private splitting variables.

Every odd-charge cycle has an **ordinary resolution refutation on this very CNF**. Every proof line is a disjunction of signed original input literals. The proof introduces no polynomial equations for a report and no additional variables. Any ordered binary parenthesization of the consecutive checks of an open path works, as does reversing or rotating that path. For the construction below, ordinary width is at most ten and at most \(2704h-1105\) nodes suffice. Expanding into the accepted unnamed multiset calculus uses at most \(7928h-7920\) primitive nodes, all of degree at most one. Every even-charge cycle has an explicit satisfying assignment for either initial report and any prescribed values of the two shared bits.

The 4,131-node triangle certificate includes every genuine source axiom and both parents and the signed pivot of every resolution. Its 9,264-node primitive expansion is independently replayed by the earlier syntactic kernel. [Complete ordinary certificate](triangle.res) · [Strict source construction and its minimality theorem](../../SHARED-REPORT-CANCELLATION-20261115-001A/SHARED-REPORT-CANCELLATION-20261115-001A-P001_strict_checks/proof.md)

## Nearest known result

Eliminating a Boolean variable by resolving its positive and negative occurrences is the classical Davis–Putnam procedure. The preceding local proof derives explicit polynomial check equations with product names and then adds those equations. Here we reconstruct every endpoint clause by ordinary resolution from the same indexed input, and count the deductions needed for different signed groupings. The optimization below is for this construction and its fixed middle-bit order. A globally shortest resolution proof is a separate question. External novelty remains unassessed. [Davis and Putnam, 1960](https://doi.org/10.1145/321033.321034) · [Named source proof](../../SHARED-REPORT-CANCELLATION-20261115-001A/SHARED-REPORT-CANCELLATION-20261115-001A-P001_strict_checks/proof.md)

## The table derived for a path

The clause excluding a tuple has the positive literal of each bit assigned zero and the negative literal of each bit assigned one. Keep the original identities of \(a,b\) throughout. A path of charge \(c\) exports the complete collection of eight-literal clauses excluding endpoint tuples with \(F_i+F_j\ne c\). At fixed \(a,b\), either private report value occurs. When \(ab=0\), there are seven private triples reporting zero and one reporting one. When \(ab=1\), those numbers are five and three. The counts of forbidden endpoint tuples are therefore

\[
R_0=3(2\cdot7\cdot1)+2\cdot5\cdot3=72,\qquad
R_1=3(7^2+1^2)+(5^2+3^2)=184.
\]

An original check obtains each excluded row from its six **actual indexed ternary clauses** by the source construction's five resolutions on its own auxiliaries. No literals other than the split pivot are duplicated in these resolutions.

Join paths \(i\) to \(j\) and \(j\) to \(k\) with charges \(c,d\). The intervals are disjoint apart from \(j\). For any compatible endpoint pair, choose the middle report to satisfy the first check. Its required value is attainable, and it satisfies the second precisely when \(F_i+F_k=c+d\). This proves the exact existential relation.

For a forbidden endpoint tuple, enumerate the eight middle triples. At each triple **exactly one** child equation fails. Take that child's already derived clause. It contains both shared literals, its own three outer endpoint literals and the three middle literals. Resolve complementary middle assignments in pairs, then repeat for the other two middle variables. The result contains both shared literals. Each outer private triple occurs, since changing the middle report switches which child fails. All three middle literals have been removed. This gives the full desired eight-literal clause in seven ordinary resolutions before sharing identical subderivations. No weakening step is needed.

Close an open path of \(h-1\) checks against the remaining original check on the same two endpoints. Reverse its displayed order when necessary. If the cycle charge is odd the tables have opposite charges, so exactly one of them contains each of the 256 endpoint exclusions. The eight-variable resolution tree derives empty in 255 ordinary resolutions. More generally two complementary proper intervals can be closed in the same way. No identification of two occurrences of an endpoint inside an eight-variable row is required.

For even total charge, set \(F_0\) to its requested value and propagate the prescribed differences around the cycle. A zero report uses private triple 000. A one report uses 111 when \(ab=0\) and 001 when \(ab=1\). Every long row now has a true literal. In each split block set a successive auxiliary to one exactly while all the original literals seen so far are false. This satisfies all six strict clauses, including the last one. ∎

## Exact cost of a join and an optimal order

Choose the middle coordinates in order \(z,x,y\), so resolution eliminates \(y,x,z\). Reuse an inference whenever it has the same two ordered parent IDs and the same signed pivot. A partial middle assignment describes an internal node of the three-bit resolution tree; let its depth \(t=0,1,2\) count the coordinates already fixed. For fixed \(a,b\) put \(N_0,N_1\) for the private triple counts above. If the remaining middle completions realize both report values, the partial derivation uses both outer endpoint triples. Such a node is specific to each forbidden endpoint tuple. If all completions instead have report \(m\), each deduction depends only on the left or only on the right outer triple. Across all forbidden endpoint tuples it occurs exactly

\[
N_{1+m+c}+N_{1+m+d}
\]

times with different parents. Indeed a left-only failure requires left value \(1+m+c\), while a right-only failure requires right value \(1+m+d\). Distinct remaining fixed literals, shared assignments or retained endpoint triples yield different parent instructions. For \(ab=0\) there are four pure-zero and three mixed internal prefixes. For \(ab=1\) there are three pure-zero, one pure-one and three mixed prefixes.

For the primitive multiset cost let \(G_0,G_1\) be the sets of middle report values realized in the two child subtrees of a prefix. The side contexts share the two original bits, the \(t\) already fixed middle literals, and three literals for each outer triple retained by both children. Which outer side is retained is a bijective function of the middle report value for a fixed forbidden row. Thus one ordinary resolution costs exactly \(4+t+3|G_0\cap G_1|\) primitive nodes there. They are the complementary linear combination, deletion of its false constant, and one contraction per duplicate side literal.

| Child charges | Distinct ordinary resolutions \(J\) | Primitive nodes \(K\) |
| --- | ---: | ---: |
| \(0,0\) | 268 | 1,968 |
| \(0,1\) or \(1,0\) | 680 | 4,984 |
| \(1,1\) | 420 | 3,296 |

In the eight-variable closing tree a node at depth \(t\) has \(t\) common side literals. Hence its primitive cost sums to \(\sum_{t=0}^7 2^t(t+2)=2048\). Let \(R=\sum_i R_{c_i}\). Each original row costs six axioms and five ordinary resolutions, or six axioms and ten unnamed primitive deductions. Every interior path join eliminates a distinct private triple, the closure uses only the two outer triples and the shared bits, and the initial splits have distinct private auxiliaries. Memoization cannot conflate instructions at different joins. The exact complete counts are therefore

\[
S_{\rm res}=11R+\sum_{\rm joins}J(c,d)+255,\qquad
S_{\rm prim}=16R+\sum_{\rm joins}K(c,d)+2048.
\]

Using \(R\le184h\) and \(h-2\) interior joins gives the two stated upper bounds. For a given cycle, original variable IDs, clause indices and proof references each take \(O(\log h)\) bits. Since widths are bounded, the indexed proof has \(O(h\log h)\) bits. Every constructed row contributes to empty. For any excluded child row one can choose the other outer endpoint report so the other child is satisfied and the parent row is forbidden; that child's row is then a leaf of the actual derivation. Closure uses every row of both final tables. The accepted minimality result also gives a linear lower bound on proof nodes in these axiom-by-axiom systems, since omitting a strict input clause leaves a satisfiable formula. Thus the order in \(h\) of the shortest ordinary or unnamed primitive refutation is linear on these odd cycles. [Minimality on the strict clauses](../../SHARED-REPORT-CANCELLATION-20261115-001A/SHARED-REPORT-CANCELLATION-20261115-001A-P001_strict_checks/proof.md)

For a fixed open order the charges of two subintervals follow from their prefix parities. For each interval choose the cut minimizing the sum of the two optimized subinterval costs and their one join cost \(J\). This dynamic program takes \(O(h^3)\) planning time and \(O(h^2)\) entries. A prescribed grouping bypasses the optimization. Both node measures have the same minimizers for a fixed order and closing edge. If the open leaves contain \(p\) charges equal to one, every parenthesization has exactly \((p-\pi)/2\) joins of type \(1,1\), where \(\pi\) is its total charge. Only those joins reduce the number of active ones, each by two. The total number of joins is fixed, so both measures increase strictly with the number of mixed joins.

## The same original input, three proofs

Take the five charges \((1,0,0,0,0)\), with edge 4 used for closing. The following certificates share the original variable order and all 2,832 strict clauses.

| Grouping of original edge IDs | Ordinary nodes | Primitive nodes |
| --- | ---: | ---: |
| \((((0,1),2),3)\) | 7,487 | 24,552 |
| \(((0,1),(2,3))\) | 7,075 | 21,536 |
| \((0,(1,(2,3)))\) | 6,663 | 18,520 |

All three use the same original rows. The last grouping first combines zero charges, so the exceptional charge participates in only one mixed join. The terminal kernel replayed the primitive left-fold and optimized proofs. The checker verifies the optimum by enumeration over 3,236 ordered parenthesizations across 124 specified open charge orders through six checks. A fixed direct join with a different coordinate order \(x,y,z\) took 336, 758 or 484 ordinary resolutions for the same three charge types.

For the stored triangle with charges \((0,0,1)\), the two original zero-charge tables cost 792 ordinary nodes each. Their join costs 268, the original charge-one table costs 2,024, and closure costs 255, for 4,131 nodes. These comprise 1,968 genuine axioms and 2,163 resolutions. Node 1590 resolves nodes 1588 and 1589 on variable 8. Its clause \((1,2,3,4,5,-9,-10,-11)\) excludes shared values 00 and endpoints 000 and 111 after removing the middle triple. The small numerical record gives the eight actual source-parent choices and all seven primitive two-parent ordinary resolutions of that row. The full certificate is 45,924 bytes. [Stored certificate](triangle.res) · [Trace and counts](checks.json)

## Replay, scope, and controls

`path_refutation(charges, grouping, start=0, reverse=False)` constructs the exact input via the source encoder and returns the signed DAG and its statistics. Groupings are `left`, `balanced`, and `optimal`. `prove_tree(encoded, tree, closing, reverse=False)` accepts ordered nested pairs of original edge IDs. `verify_resolution` reconstructs every signed clause; `quadratic_steps` streams every primitive multiset step, and `verify_quadratic` passes that stream to the accepted independent kernel. To read the stored certificate, call `read_certificate(encode_cycle((0,0,1)), text)` with A's encoder. Its header binds the exact original CNF in order by SHA-256. Each following line either cites an original strict clause or supplies the two prior node IDs and the signed literal resolved positively in the first parent. Node IDs are zero-based.

`PathBuilder(encoded)` emits nothing initially. Its `edge` and `join` operations emit their deductions when called. An already derived table can be reversed by `flipped()`, and `close` checks coverage and the opposite parity before deriving empty. For a supplied simple cycle in a larger source check graph, `cycle_edges=[(original_edge_id, reverse_flag), ...]` fixes its directed cyclic order. The original CNF and all its clause IDs are preserved, including unrelated clauses. A six-check verification arrived at original IDs 2 and 4, joined them, then closed with ID 1. Exactly 1,968 of the 4,608 genuine original clauses were used.

Keeping both shared bits in the tables is essential. With outer triples 000 and middle triple 001, the two adjacent report differences are both \(ab\). Charges zero and one separately admit witnesses when the shared bits may change, while no common witness exists. Deleting the middle \(z\) literal from the zero-charge exclusion for triples 000 and 111 wrongly excludes 000 and 110 at \(a=b=0\); that state extends to a model of the entire strict even cycle. The common term also cannot be canceled edgewise: with \(ab=1\), triples 111 and 000 both report zero while their cubic-only terms differ.

The checker independently enumerates 8,192 single-join completions, all 24 charge vectors at cycle lengths three and four, and 96 complete strict models for their even cases. It verifies signed proofs on growing cycles through 17 checks, tests reversed and rotated inputs, and rejects a changed pivot, a different original CNF and a nonadjacent join. The complete triangle and two five-check primitive expansions were replayed with the existing multiset kernel. These are V1 same-task checks of the uniform construction. The conclusion concerns this specified cycle encoding and supplied regroupings. [Implementation](solver.py) · [Checker](check.py)

```sh
python3 -B proofs/SHARED-REPORT-CANCELLATION-20261115-001B/SHARED-REPORT-CANCELLATION-20261115-001B-P001_regroup_paths/check.py
```
