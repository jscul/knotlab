# Transporting sequentially named Boolean products

Status: Proved

## Standard statement

Fix a CNF \(G\) and a substitution of its original variables by signed literals or constants over a CNF \(F\) on \(n\) variables with \(m\) clauses. For every input clause of \(G\), including any switch unit, require its image to contain the true constant, contain a complementary pair, or coincide with an actual clause of \(F\) after discarding false constants and repeated literals. Take the occurrence-counting syntactic degree-two polynomial-resolution system over \(\mathbb F_2\) and allow one additional kind of node. It assigns a fresh Boolean name \(t\) to \(fg\), where \(f,g\) are affine polynomials in the names available *before* this node. Its exact conclusion is the singleton \([t+fg=0]\).

Every \(S\)-node refutation of \(G\) with \(d\) such declarations yields a refutation of \(F\) in this same extended calculus. All \(d\) declarations are charged in \(S\). The source proof has exactly \(d\) declarations, the same dependency graph between their written factors, and at most

\[
\min\{2S-d,\ S+m+n+1\}
\]

nodes when the literals within each source clause are distinct. The construction takes polynomial time in the explicit bit lengths of both formulas, the literal map, and the target certificate. A source lower bound used with this statement must cover the declared product-name rule and the indicated resource restrictions.

## Nearest known result

Alekseev's Definition 7 gives the classical form of sequential algebraic extension equations, with each right side allowed to use earlier names, in polynomial calculus over a domain with a square-root rule. Pang gives the underlying syntactic resolution rules for disjunctions of bounded-degree polynomial equations and counts proof nodes. Here each permitted right side is the product of two affine forms over \(\mathbb F_2\), each introduction is a proof node, and the routing map transports that very declaration into the source proof. The predecessor already verifies substitution on ordinary quadratic rules and the routing construction already supplies the base axiom images. The present proof adds causal name checking, exact declaration transport, and compiled deductions that use the new lines. [Alekseev, Definition 7](https://drops.dagstuhl.de/storage/00lipics/lipics-vol200-ccc2021/LIPIcs.CCC.2021.21/LIPIcs.CCC.2021.21.pdf#page=5) · [Pang, §1](https://arxiv.org/html/2610.00837v2#S1) · [Base quadratic transport](../../QUADRATIC-ROUTE-TRANSFER-20261115-001A/QUADRATIC-ROUTE-TRANSFER-20261115-001A-P001_quadratic_substitution/proof.md) · [Routing axiom projection](../../ROUTE-PARITY-TRANSFER-20261115-001A/ROUTE-PARITY-TRANSFER-20261115-001A-P001_literal_projection/proof.md)

## The calculus and its models

Write \([p]\) for the formal equation \(p=0\). The ordinary rules are syntactic weakening by disjuncts, single-occurrence contraction, deletion of \([1]\), linear combination and multiplication of one selected atom by a polynomial, with every displayed polynomial of degree at most two. The initial CNF uses only original variables. The logical defaults are \([0]\) and \([x]\lor[1+x]\) for any currently available Boolean variable. Scalars, side contexts and repeated references have the predecessor's syntax. A refutation ends in the empty disjunction.

Number the original bits \(1,\ldots,N\). Declaration \(j\) introduces \(t_j=N+j\) using affine factors on \(1,\ldots,N+j-1\). This numbering records any choice of distinct fresh names by renaming in order. Constants, equal factors, complements, affine sums involving many bits and earlier product names are allowed. For example \(t=x(1+x)\) has formal equation \([t+x+x^2]\). Its Boolean value is always zero, while the equation shown in its declaration must retain the formal square. A fresh variable can have the same value as a prior expression and still has a separate syntactic identity. It can appear repeatedly in ordinary steps, Boolean defaults and later factors. A defining node has no ordinary deduction parents. Its factors depend on their earlier declarations. Ordinary source axioms, side clauses, selected polynomials, and even a multiplier whose eventual product vanishes must use names available at their node.

Every assignment of the original bits extends **uniquely** through any finite sequence of legal declarations. Inductively, with the preceding values fixed, \(t_j+f_jg_j=0\) forces the Boolean value \(f_jg_j\) and that value satisfies the equation. This induction also applies to every model of the original CNF. All ordinary rules preserve truth under the extended valuation. Consequently a proof reaching the empty clause certifies unsatisfiability of the original formula. The freshness check matters even to existence. Simultaneously admitting \(t=(1+u)\cdot1\) and \(u=t\cdot1\) would yield \(1=0\) by a single combination and then the empty clause on an empty input.

## Transport and cost

Map the old target names by the given substitution. On encountering declaration \(j\), introduce the fresh source name \(z_j=n+j\) for the product of the two factor images and set \(\sigma(t_j)=z_j\). The inductive invariant is that every available target name has an image over exactly the current source roster. In particular the old map cannot mention any future source name. Each factor image remains affine and every previous \(t_i\) maps injectively to its own \(z_i\). Hence the source defining equation

\[
[z_j+\sigma(f_j)\sigma(g_j)]
=\sigma([t_j+f_jg_j])
\]

is exactly one legal node. Each coefficient of any earlier named variable in either written affine factor is preserved, including when the other factor specializes to zero. Thus the graph of dependencies between the two recorded factor expressions, and its maximum depth, are preserved. For any original source assignment, induction on \(j\) also shows that the source declarations take the same values as the target declarations evaluated under the induced target assignment.

For the remaining nodes, formal substitution commutes with addition and multiplication and fixes \([0]\) and \([1]\). Keep all clause occurrences, including false constants and aliases. Each ordinary inference translates in one syntactic step using the mapped references to its actual parents. An initial image starts from a genuine source axiom, the true default or the appropriate variable Boolean default. One syntactic weakening can append all missing occurrences. An original variable Boolean default may map to the true and false constants, handled by the same repair. A Boolean default for \(t_j\) maps exactly to the default for \(z_j\), whose declaration is already present.

Every declaration costs one node and every other target node costs at most two. Alternatively, cache the starting axioms. Every target node then pays for at most one inference or newly needed default for its own fresh name. The only additional starting axioms that can incur a second node at the same step are the \(m\) source clauses, \(n\) original Boolean defaults and the true default. An earlier identical empty input can be cited by an identity weakening at the final occurrence. This proves the displayed estimates while retaining all DAG reuse. With repeated literals in a multiset source clause, add the count of surplus copies contracted once per used source input clause. With sets for both presentations, strict removal of a chosen atom can also discard an aliased side atom. The predecessor's one syntactic weakening repairs those steps, giving \(2S-d\) with strict removal.

Checking the time-ordered rosters and finite parent references takes polynomial bit work. Expanding the product of two explicitly supplied affine factors with \(p,q\) terms uses at most \(pq\) term pairs before cancellation. During transport each monomial of degree at most two expands to at most four monomials under the signed map. The output keeps each named variable as a variable, so definition depth never forces recursive multiplication of all earlier right sides. Counts of nodes, widths of explicitly written polynomials, encoded names, and references are distinct resources.

## The proof checker

The verifier first checks every declaration against its exact two affine factors using the preceding roster, and separately checks the variables on every ordinary node at its own position. It checks original axiom IDs and ordinary parent IDs against the genuine input and preceding nodes. For the ordinary inference verification it reuses the terminal quadratic checker. Internally it prepends one dummy empty assumption and presents each *already validated* declaration to this checker as a weakening of that assumption. Only these replacement rows can address the dummy parent. All genuine parent references shift by one after the range check, and all genuine input axiom IDs are checked before appending the dummy CNF clause. This allows the kernel to verify every ordinary inference conditional on its actual earlier rows. The returned certificate contains the real declarations and the real input axioms. The checker separately requires that its genuine final node is empty.

The public function \(\texttt{ancestors}\) follows both ordinary premise references and references to declaration nodes needed by the symbols of a row. For example, an application of the Boolean default to \(t_j\) can require its declaration even when the defining equation never serves as an ordinary inference premise. A control verifies that ordinary-parent-only pruning loses this dependency. To serialize a pruned proof with the consecutive-ID convention, renumber the retained declarations and parent references in their original order. [Transformer and verifier](solver.py)

## Real guarded deductions

Start from one genuine axiom \(A\lor[f]\) that survives the projection. Choose two different original signals \(g,h\), both distinct from the underlying source variable of \(f\). Introduce \(t=fg\) and \(u=th\). Multiplication gives \(A\lor[fg]\) and \(A\lor[f(1+g)]\). Combining the former with the first declaration gives \(A\lor[t]\). Split \(t\) in the same way on \(h\), use the second declaration to obtain \(A\lor[u]\), and split and rejoin \(u\) on \(g\). A second use of the definition of \(u\) recovers \(th\), and a second use of the definition of \(t\) recovers \(fg\). Joining the complementary products recovers \(A\lor[f]\), with every duplicate context contracted explicitly. This replaces the original axiom reference in an actual guarded refutation.

| Raw fixture | Strict clauses | Pinned switches | Target nodes | Source nodes |
| --- | ---: | ---: | ---: | ---: |
| Three-variable clause list | 2,464 | 1,848 | 6,640 | 5,834 |
| Four-variable fixed catalog with selected clauses | 5,920 | 4,440 | 9,518 | 8,304 |

In both target and source proofs, each declaration serves twice as an ordinary premise in the ancestry of empty, and the second name is selected for multiplication. Both definitions retain a product of distinct variables. Independently enumerating all four proposed values of the two names for each original source assignment gives exactly one extension. Across these assignments the pairs \(00,10,11\) occur. Every source proof line passes direct evaluation on those extensions. Changing either defining row while retaining the deductions is rejected. These controls establish actual use in the exhibited proofs. Original unsatisfiability already holds before the declarations. [Executable replay](check.py) · [Results](checks.json)

As a separate check, exhaustive truth tables give unique extensions for all 64 two-declaration programs with zero original bits, all 1,024 with one, and all 16,384 with two. A proof reciting an empty input after an unrelated definition and Boolean default yields a four-node source proof ending in an explicit empty weakening in both conventions. The 17 negative cases exercise redefinition, future and self-reference, forbidden degrees, altered equations, Boolean defaults before declaration, a counterfeit refutation from cyclic definitions, constant/name capture and references aimed at the kernel's dummy premise. Pang's lower bound addresses the underlying system without these declarations. The transport here compares the source and target in the extended system.

## Reproduction and interface

~~~sh
family=proofs/PRODUCT-NAME-TRANSFER-20261115-001A/PRODUCT-NAME-TRANSFER-20261115-001A-P001_named_substitution
python3 -B "$family/check.py"
~~~

\(\texttt{Dag(n, cnf)}\) supplies the old quadratic operations and \(\texttt{define(f,g)}\), returning the fresh variable ID and the zero-based definition node ID. The \(\texttt{define}\) row carries \(\texttt{variable}\), \(\texttt{factors}\) and \(\texttt{clause}\) fields. Polynomials are lists of monomials with repeated one-based indices permitted in a term. The empty polynomial is zero, and a single empty monomial is one. Each atom denotes equality to zero. \(\texttt{verify(n,cnf,proof)}\) takes the number of original variables. \(\texttt{backtranslate(source_n,source_cnf,target_n,target_cnf,images,target_proof)}\) returns a source certificate. Its external literal map is only for original variables, using \(+(n+1)\) and \(-(n+1)\) for constants one and zero. The API distinguishes this external encoding from the first genuine source product name \(n+1\). Both methods accept the optional \(\texttt{convention}\) keyword. A JSON object with the six named translation arguments can be checked end to end as follows.

~~~sh
python3 -B "$family/check.py" --translate package.json | python3 -B "$family/check.py" --verify -
~~~
