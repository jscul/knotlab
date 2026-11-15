# Derive and cancel signed checks from a strict ternary CNF

Status: Proved

## Standard statement

Use Boolean arithmetic over \(\mathbb F_2\). There are two original bits \(a,b\) and three more original bits \(x_i,y_i,z_i\) at each of \(h\ge3\) positions. All these variable names are distinct. Define the functions
\[
 F_i=z_i(x_i y_i+ab).
\]
Write the desired cycle checks as \(F_i+F_{i+1}=c_i\), with indices modulo \(h\) and independently specified charges \(c_i\in\{0,1\}\). There is a uniform strict 3-CNF on the original bits and private clause-splitting variables whose projection is precisely their conjunction. It is satisfiable exactly for even total charge. For odd total charge **deleting any individual strict clause restores satisfiability**.

Every odd instance has an explicit multiset \(\mathrm{Res}(\mathrm{PC}_2/\mathbb F_2)\) refutation with \(h+1\) charged product declarations and \(O(h)\) proof nodes. The only declared products are \(ab\) and the \(h\) terms \(x_i y_i\). Each check equation is derived from the strict input clauses before it enters the final sum. For charges \(0,0,1\), the source has 1,968 strict clauses, and its complete 14,159-node refutation is saved. [Complete triangle certificate](triangle.json.gz) · [Human-readable source and cancellation trace](trace.json)

## Nearest known result

The sum around an odd signed cycle is the ordinary characteristic-two charge argument for Tseitin equations. Resolution over linear equations uses the same cancellation when the parity equations are available. The preceding grouped-product work derived conditional reports from original clauses and handled degree-two images of named products. Here the checks are supplied solely by a strict CNF on two shared inputs and local triples. The additional claims are exact projection and clause-minimality for this source, followed by actual bounded-degree derivations of all the equations to be added. [Resolution over linear equations modulo two](https://doi.org/10.1016/j.apal.2019.102722) · [Earlier grouped proof replay](../../GROUPED-PRODUCT-REPLAY-20261115-001C/GROUPED-PRODUCT-REPLAY-20261115-001C-P001_fresh_bit_replay/proof.md) · [Named degree-two proof rules](../../PRODUCT-NAME-TRANSFER-20261115-001A/PRODUCT-NAME-TRANSFER-20261115-001A-P001_named_substitution/proof.md)

## The complete strict source

For an ordered check \((i,j,c)\) with \(i\ne j\), enumerate the 256 assignments in order \(a,b,x_i,y_i,z_i,x_j,y_j,z_j\). Each assignment \(\alpha\) with \(F_i+F_j\ne c\) gives one width-eight clause \(l_1\lor\cdots\lor l_8\). Its literal is positive where \(\alpha\) is zero and negative where \(\alpha\) is one. The clause excludes exactly \(\alpha\). Replace it by the following six strict clauses, with five variables \(t_1,\ldots,t_5\) private to this one row:
\[
\begin{gathered}
 l_1\lor l_2\lor t_1,\quad
 \neg t_1\lor l_3\lor t_2,\quad
 \neg t_2\lor l_4\lor t_3,\quad
 \neg t_3\lor l_5\lor t_4,\\
 \neg t_4\lor l_6\lor t_5,\quad
 \neg t_5\lor l_7\lor l_8 .
\end{gathered}
\]
When all the literals are false the clauses propagate \(t_1=\cdots=t_5=1\) and the last clause fails. Otherwise set \(t_k=1\) precisely when the first \(k+1\) literals are all false. This satisfies the chain. Distinct rows share no private variables, so all row witnesses can be chosen simultaneously for every accepted original assignment. This proves the stated projection for arbitrary lists of checks. Each listed clause has three distinct underlying variables. The original coordinates, followed by private chain variables, exhaust the input roster.

For fixed \(ab=0\), exactly one of the eight local triples makes \(F_i=1\). For \(ab=1\), exactly three do. Accordingly 72 of the 256 original assignments give differing report values: there are \(3\cdot2\cdot1\cdot7+2\cdot3\cdot5\) such assignments. A charge-zero check has 72 forbidden rows, and a charge-one check has 184. With \(k\) ones in the charge list, the source has \(R=72(h-k)+184k\) forbidden rows, \(6R\) strict clauses, and \(2+3h+5R\) input variables. Reversing the endpoint order changes the local serialization and preserves the accepted original assignments. [Encoder and actual clause lifter](solver.py)

For any fixed values of the shared \(a,b\), every prescribed vector of report bits is attainable. To obtain a zero choose \(z_i=0\). To obtain a one choose \(z_i=1,\ x_i=1,\ y_i=1+ab\). Thus the checks project on their report values to the usual signed cycle. Choose \(F_0\) freely and propagate the equations. Upon returning to \(F_0\) the assignments are consistent exactly when \(\sum_i c_i=0\). Each of the two initial choices extends in that case. On the supplied cycle presentation the decision therefore takes one parity scan of its charges. The proof below certifies an odd answer from the original strict clauses.

## Individual strict clauses are necessary

Assume odd total charge, and delete a strict clause from the chain for forbidden row \(\alpha\) of check \((i,j,c)\). Keep all eight bits of \(\alpha\), including both endpoints' complete triples and the shared bits. The other \(h-1\) checks form a path. Propagating from one prescribed endpoint around the path requires their difference to be the sum of those other charges. This is \(1+c\), exactly their difference in \(\alpha\). Realize every internal report bit using the fixed \(a,b\) as above. Thus the only violated check is the specified check, and the only violated width-eight clause is its one row \(\alpha\).

All other rows have private extensions satisfying their six clauses. Number the six clauses in the missing row \(0,\ldots,5\). If clause \(g\) is removed, assign \(t_k=1\) for \(k\le g\) and zero otherwise, with \(k=1,\ldots,5\). All eight original literals in this row are false. This private assignment violates exactly its \(g\)-th strict clause, including either end clause when \(g=0\) or \(5\). The construction works for either charge and either orientation. It also proves that deleting any entire check restores satisfiability.

## A bounded-degree derivation of each check

Use \([P]\) for the atom \(P=0\). The calculus works with formal polynomials and disjunctions retaining repeated occurrences. On the genuine strict input, introduce exactly the \(h+1\) declarations
\[
 K=ab,\qquad L_i=x_i y_i.
\]
Let \(R_i=z_i(L_i+K)\) as an expression. At a check \(e=(i,j,c)\) the desired derived line is the **singleton** \([P_e]\) for \(P_e=R_i+R_j+c\).

For each of the 256 original assignments on the check's eight variables, let \(H_\alpha\) be its width-eight failure disjunction. It contains \([v+1+\alpha_v]\) for each variable \(v\). We derive \(H_\alpha\lor[P_e]\).

* On a forbidden assignment, successively resolve its six genuine strict clauses on \(t_1,\ldots,t_5\). The result is exactly \(H_\alpha\). In the primitive calculus, each such resolution adds the selected complementary equations and deletes the false constant, contracting duplicated side occurrences if present. Weaken by \([P_e]\).
* On an allowed assignment, the Boolean axiom for \(v\) gives \([v+\alpha_v]\) with the opposite atom as its single side disjunct. To compute a product value, multiply \([f+s]\) by \(g\) and add \(s\) times the chosen \([g+t]\). This gives \([fg+st]\) with the two input side contexts. If \(fg\) is a declared product, add its defining equation to get its name in the selected atom. Use this deduction to obtain the conditional values of \(K,L_i,L_j\). Add the equations for \(L_i\) and \(K\). Apply the same product rule to \(z_i\) and the affine expression \(L_i+K\). The result is \([R_i+F_i(\alpha)]\) under the five corresponding original failure atoms. Do the same for \(j\). Adding these two atoms gives \([P_e]\), because the assignment obeys the charge. The two failure atoms for \(a,b\) each occur twice. Contract exactly their extra copies to obtain \(H_\alpha\lor[P_e]\).

Merge the two branches of the last variable by adding the selected opposite failure atoms, deleting \(1=0\), and contracting the second copy of the common context. Repeat for the other seven variables. The last line is \([P_e]\) alone. Every multiplication used either two original coordinates or an original coordinate and a linear combination of declared names. In particular no assertion about the value of a report is an input axiom. The executable prefix returns the genuine root of each check and its exact polynomial for reuse in any chosen proof order. [Derivation and cancellation implementation](solver.py)

## Cancellation, cost and the direct degree obstruction

When all check equations on the cycle are added, every \(R_i\) occurs exactly twice. Only the sum of charges remains. For odd charge this gives the singleton \([1]\), from which false-constant deletion derives the empty disjunction. For even charge this sum is \([0]\), in agreement with the explicit satisfying assignments.

At fixed local arity, fewer than 32 primitive nodes per assignment suffice before merging, even charging the required Boolean variable axioms. There are 255 merges per check. Each needs at most ten primitive nodes because its common context has at most eight occurrences. Including the \(h+1\) declarations, \(h-1\) final additions and final deletion, \(10{,}744h+1\) is a uniform node upper bound. Consecutive checks leave only two endpoint expressions in each partial sum. In that order every line has bounded width and each displayed polynomial has a bounded number of terms, so an ordinary indexed serialization uses \(O(h\log(h+2))\) bits. Other orders retain \(O(h)\) nodes but can display longer intermediate sums.

Removing all the names at once would turn one check polynomial into
\[
 z_i x_i y_i+z_j x_j y_j+abz_i+abz_j+c .
\]
With \(a=b=0,\ z_j=0\), the restriction is \(z_i x_i y_i+c\). Its values have odd parity across the eight remaining original assignments. Every degree-at-most-two polynomial has even parity there, since each multilinear monomial of degree at most two has an even number of ones. The Boolean identity for squares leaves this obstruction intact. In the triangle refutation, row 16 is the first actual failing multiplication. It selects the equation for coordinate 5 and multiplies by the sum of names 1652 and 1653. In original coordinates the selected product is the sum of monomials (1,2,5) and (3,4,5). This is a barrier to representing that particular intermediate value by one original-variable quadratic. The final sum can simplify after adding the check equations, and other proof methods remain possible.

## Certificate and checks

For charges \((0,0,1)\), the proof derives singly the check equations at zero-based nodes 4318, 8508 and 14155. Nodes 14156 and 14157 add them, and node 14158 deletes \([1]\). All 1,968 original strict axioms and all four declared products are explicit ancestors of the empty conclusion. The compressed JSON contains the full input CNF and every primitive proof row. The trace records the exact final rows, a sample forbidden row, the first failed raw substitution, and hashes of the full input and proof. The checker also supports `--emit-triangle OUTPUT.json` for fresh uncompressed output. [Full certificate](triangle.json.gz) · [Trace](trace.json)

The tests use an independent SAT backend on all 256 original pins of either charge and both orientations, and on complete three- and four-position cycles with every charge pattern. Separate constructive checks exhibit a satisfying assignment after **each** individual strict clause deletion on the triangle and a larger reordered signed cycle. The reordered four-position cycle has 3,744 single-clause deletion witnesses and a second complete proof of 21,487 nodes using five names. Its first sum combines disjoint checks and contains eight quadratic monomials. The checker verifies the full raw proof with the accepted kernel, tests the mandatory antecedents and a changed source-row index, and compares the native three-bit restriction against all 128 quadratic Boolean functions for each charge. These are V1 same-task checks of a uniform construction. An independent intra-task reviewer checked the endpoint and private-clause necessity argument. [Checker](check.py) · [Verified counts](checks.json)
