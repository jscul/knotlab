# Literal substitution in syntactic resolution over quadratic polynomials

Status: Proved

## Standard statement

Let \(G\) be a target CNF and \(F\) a source CNF with \(n\) variables and \(m\) input clauses. Fix one map \(\sigma\) from all target variables to signed source literals or constants. On ordinary CNF clauses, after removing false constants and duplicate literals, require each image to contain a true constant, contain a complementary source pair, or equal an actual clause of \(F\). Assume first that no signed literal appears twice within a single source clause. Repetitions of whole input clauses are allowed.

For every \(S\)-node syntactic \(\operatorname{Res}(\mathrm{PC}_2/\mathbb F_2)\) DAG refutation of \(G\), there is a refutation of \(F\) in the same system with

\[
S_F\le \min\{2S,\ S+m+n+1\}.
\]

Here clauses are disjunctions with explicit occurrences, contraction removes one duplicate, and all nodes including defaults and initial clauses count toward size. A weakening may append any finite multiset of degree-at-most-two equations. The bound is independent of the widths of the lines. A verified \(2S\) bound also holds when both input and output use sets as contexts and the output verifier demands exact removal of the selected atom before any needed weakening. Construction and verification cost polynomially many bit operations in the explicit inputs. In the multiset presentation, a lower bound \(L\) for the source implies \(\max\{L/2,L-m-n-1\}\) for every target refutation under this instance's projection.

## Nearest known result

Pang defines the syntactic rules, default axioms, degree bound and DAG node measure just before Theorem 1.1. The proof of Fact 7.1 explicitly permits appending multiple disjuncts in one weakening. Fact 2.2 discusses the separate role of derivable Boolean multilinearization. The earlier local routing theorem supplies the literal map on the actual guarded CNF, including its pinned switches. The earlier DAG converter handles affine pivots and one-premise semantic weakening. Here the transported rule includes genuine formal multiplication, and both proof checkers use syntactic deductions only. [Pang v2, §1](https://arxiv.org/html/2610.00837v2#S1) · [Fact 7.1](https://arxiv.org/html/2610.00837v2#S7) · [Exact routing map](../../ROUTE-PARITY-TRANSFER-20261115-001A/ROUTE-PARITY-TRANSFER-20261115-001A-P001_literal_projection/proof.md) · [Affine DAG transport](../../ROUTE-PARITY-TRANSFER-20261115-001B/ROUTE-PARITY-TRANSFER-20261115-001B-P001_dag_transport/proof.md)

## Formal products and exact side occurrences

An atom \([f]\) denotes \(f=0\) for an ordinary formal polynomial over \(\mathbb F_2\). A positive literal \(x\) is \([1+x]\), and a negative literal \(\neg x\) is \([x]\). The map sends a target variable to \(x,1+x,0,\) or \(1\). It extends uniquely to a unital ring homomorphism, so

\[
\sigma(\alpha f+\beta g)=\alpha\sigma(f)+\beta\sigma(g),\qquad
\sigma(fg)=\sigma(f)\sigma(g).
\]

Replacing a variable by an affine polynomial cannot raise total degree. This covers all the displayed polynomials of a legal step, including its multiplier. For example, identifying the two variables in \(uv\) gives \(x^2\). Substituting \(u=x,v=1+x\) gives \(x+x^2\). Both are formal identities. Formal Frobenius gives \((1+x)^2=1+x^2\). The additional equations valid on Boolean assignments, such as \(x^2=x\), require a licensed derivation whenever used inside this calculus.

Use the same \(\sigma\) at every proof node. Map a clause occurrence by occurrence and keep all resulting disjuncts, including repeated equations, \([1]\) (false), and \([0]\) (true). Consequently the image of a multiset sum of side contexts is exactly the sum of their images. A selected occurrence can always be singled out after substitution. Other occurrences with the same image stay where the rule places them.

| Target primitive | Source primitive on the mapped occurrences |
| --- | --- |
| Syntactic weakening \(A\longrightarrow A\lor B\) | Append the full image of \(B\). |
| Contraction \(A\lor[f]\lor[f]\longrightarrow A\lor[f]\) | Contract exactly one duplicate image. |
| False deletion \(A\lor[1]\longrightarrow A\) | Delete the selected \([1]\). The constant is fixed by the map. |
| Linear combination \(A\lor[f], B\lor[g]\longrightarrow A\lor B\lor[\alpha f+\beta g]\) | Combine the two selected images with the same scalars, using both side multisets in full. |
| Multiplication \(A\lor[f]\longrightarrow A\lor[fg]\) | Multiply \([\sigma(f)]\) by the polynomial \(\sigma(g)\). |

In particular, a target multiplication by a variable mapping to a negative literal becomes multiplication by \(1+x\) in one step. Zero factors, one factors, collapsing forms, both-zero combination coefficients, and semantically tautological derived parents are all covered by the same syntactic rules. Each inference uses its earlier output references, so the DAG is never unfolded. Introducing fresh unconstrained target names in a proof is handled by extending the finite map to those names, for example by zero.

## Initial clauses and default axioms

For each target CNF axiom select a source derivation of its entire formal image. A true constant \([0]\) is a supplied default axiom. A complementary source pair is precisely the two-atom default \([x]\lor[1+x]\). If neither occurs, remove all \([1]\) and duplicate literals for the *lookup only*. The projection hypothesis guarantees an actual matching source CNF axiom. In each case the selected starting clause is a submultiset of the desired image. One syntactic weakening restores every remaining occurrence at once. This also treats a source empty axiom and an image consisting entirely of false constants. The adapter validates every listed target axiom, even one unused in the supplied DAG.

The target default \([0]\) maps to itself. A variable Boolean axiom maps either to a source Boolean axiom, possibly with its two disjuncts exchanged, or to \([0]\lor[1]\), which follows by weakening the true default. No Boolean tautology test for arbitrary quadratic clauses is required. The only source leaves are input axioms of \(F\) and the stated two kinds of logical defaults.

Process the target proof in topological order. Each initial node needs at most two nodes and each inference needs one. Cache each actual source input or default leaf. In the second accounting every target node costs at most one inference and all distinct source leaves together cost at most \(m+n+1\). If the last target node is a cached empty input axiom, reusing the reference leaves that occurrence's budget available for a final identity weakening to empty. This proves both bounds. For source clauses storing repeated **literals** as part of the multiset input, the same construction contracts surplus copies once per used source axiom. Add \(D=\sum_C(|C|-|\operatorname{supp} C|)\) over those distinct, used input axioms to both estimates. The strict three-variable source has \(D=0\).

## Context conventions and bit work

With set contexts on *both* sides, distinct target disjuncts can acquire one image. At a multiplication or false deletion, strict removal of the selected image may also remove an aliased side occurrence. At a binary combination this can happen for at most its two selected images. All other side atoms and the new result are present. Thus the output of strict removal is a subset of the desired image, restored in one syntactic weakening if necessary. The same argument covers a selected atom explicitly retained in a target set context. Set contraction is an identity. This gives at most two source nodes per input node. In the usual set rule allowing a designated pivot within a side context, directly choosing the mapped side contexts also preserves each inference in one rule application. The executable uses strict removal for its emitted steps and checks any needed weakening.

Matching the conventions matters. Two multiset parents with the same \(k\)-atom side context produce two copies of each of those \(k\) equations by a linear combination. Erasing those copies after every step would conceal up to \(k\) separate contractions. The multiset implementation retains them even when all \(k\) different target atoms acquire the same source image. A formally nonconstant polynomial such as \(1+x^2+x\) cannot be deleted as a false constant.

Under a signed literal substitution, expanding a term of degree at most two produces at most four monomials before equal terms cancel. Coefficient parity, repeated variable indices in a monomial, the occurrence counts in a clause, rosters, named variable indices and DAG references can all be handled in polynomial bit work. The verifier separately reconstructs formal products coefficient by coefficient and counts the required side occurrences. Neither the bit-cost statement nor the node count treats multiplying explicitly large sparse polynomials as a constant-time machine operation.

## Executable checks

The finite census uses all 64 formal polynomials of total degree at most two in two variables, over all 36 signed/constant maps into two variables. Evaluation at all 16 points of \(\mathbb F_4^2\) distinguishes the 64 forms including \(x^2\) and \(x\), which agree on Boolean inputs. The replay checks 36,864 polynomial-image point values, 147,456 binary additions, and all 10,368 products staying within degree two under the original bound. A six-variable multiset refutation with shared parents becomes 97 source nodes from 96 target nodes. All three multiplications are ancestors of empty and their images include both a square and a product of distinct variables. The matched set replay uses 73 source nodes from 69 target nodes, with three explicit side-context repairs. Both resulting proofs also pass independent Boolean evaluation of every inference.

At the next size, all 1,024 formal quadratics of degree at most two in three names pass 327,680 point-value checks on five maps. The live width control has 32 distinct side literals with the same projected image. Its 65-occurrence binary conclusion remains intact. Both proofs perform exactly 32 single-occurrence contractions. Another control keeps a 513-occurrence binary conclusion in a seven-node DAG. Eleven mutations reject unauthorized weakening, Boolean-only simplification, illegal degree, invented defaults and axiom images, implicit multiset contraction, and bad proof references. Two actual routing projections check all 6,832 raw axioms and switch units. In the three-variable case the 3,192 images use 2,805 true defaults, 384 Boolean defaults and three exact input clauses. The four-variable case checks a nontrivial selection. [Numerical results](checks.json)

Run from the repository root.

~~~sh
family=proofs/QUADRATIC-ROUTE-TRANSFER-20261115-001A/QUADRATIC-ROUTE-TRANSFER-20261115-001A-P001_quadratic_substitution
python3 -B "$family/check.py"
~~~

The public API exports \(\texttt{backtranslate(source_n, source_cnf, target_n, target_cnf, images, target_proof)}\) and \(\texttt{verify(n, cnf, proof)}\). The optional keyword \(\texttt{convention}\) takes the values \(\texttt{multiset}\) (default) and \(\texttt{set}\). A map entry \(+(n+1)\) means one and \(-(n+1)\) means zero. Other entries are signed source literals. Proof and axiom indices start at zero. A polynomial is a list of monomials, each a list of one-based variable IDs with repetitions. Thus the empty polynomial list is zero, a single empty monomial represents one, and \(\mathtt{[[1,1],[1,2]]}\) represents \(x_1^2+x_1x_2\). Every listed polynomial in a clause denotes an equality to zero. The \(\texttt{Dag}\) builder supplies the primitive rules and helpers \(\texttt{resolve}\) and \(\texttt{contract_all}\), both of which expand to primitive proof nodes. [Public builder, transformer and verifier](solver.py)

The JSON translation package has the six API input keys. The independent verifier consumes the translation's output directly.

~~~sh
python3 -B "$family/check.py" --translate package.json | python3 -B "$family/check.py" --verify -
~~~
