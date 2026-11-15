# Elimination by the rank of original affine factors

Status: Proved

## Standard statement

Let a CNF on \(n\) original Boolean variables have an \(S\)-node refutation in syntactic resolution over formal polynomials of degree at most two over \(\mathbb F_2\). Disjunctions are multisets. The refutation may declare a fresh name \(t_j=f_jg_j\) in one charged node with the single equation \([t_j+f_jg_j=0]\). Both factors are affine in original variables and earlier names. Boolean defaults on names are legal after their declarations.

Supply affine forms on the original variables. Let \(W\) be the span of their linear parts and put \(r=\dim W\). Suppose at least one of the two factors of every declaration is an original affine form with linear part in \(W\). Either operand may qualify, and its constant term is arbitrary. Then the same input CNF has an **unnamed degree-two refutation** using at most

\[
128\,2^r(n+r+1)(S+1)
\]

nodes. The converter checks the supplied cover, handles arbitrary declaration depth and repeated use, and constructs one branch for each of the \(2^r\) basis valuations. In particular two independent forms suffice for a four-case proof even when declarations also use their sum, their complements, and arbitrary affine combinations of earlier names as their other operands. The bound is a node count. The time and space to read or write polynomial inscriptions also depend on their encoded length.

## Nearest known result

Gaussian elimination over \(\mathbb F_2\) yields the basis and coordinates. The preceding one-factor result made two cases for one original affine form or its complement. An earlier simulation branched anew at every declaration. Here the new deduction derives any dependent factor equation in a single fixed branch context, so only the rank of the supplied forms occurs in the exponent. The ordinary proof rules and their DAG measure are those used in Pang's syntactic calculus. This theorem concerns the locally specified extension by proof-local names. [One shared original factor](../../PRODUCT-NAME-TRANSFER-20261115-001C/PRODUCT-NAME-TRANSFER-20261115-001C-P001_depth_and_unrestricted/proof.md) · [Branching on declarations](../../PRODUCT-NAME-TRANSFER-20261115-001B/PRODUCT-NAME-TRANSFER-20261115-001B-P001_bounded_elimination/proof.md) · [Pang, proof rules](https://arxiv.org/html/2610.00837v2#S1)

## The equation for a dependent factor

Write \([p]\) for \([p=0]\). Keep the independent linear forms \(b_1,\ldots,b_r\) in order of their first independent generator. Gaussian reduction records the representation of each eligible factor as

\[
h=\epsilon+\sum_{i\in I} b_i .
\]

Fix one assignment \(b_i=\beta_i\), set \(a_i=b_i+\beta_i\), and let \(H_\beta\) be the disjunction containing one failure equation \([a_i+1]\) for each \(i\). Then \(h\) takes value \(c=\epsilon+\sum_{i\in I}\beta_i\) on this branch. The syntactic certificate required for this conclusion is

\[
H_\beta\ \lor\ [h+c].
\]

For \(i\in I\), obtain the ordinary Boolean choice \(E_{b_i}=[a_i]\lor[a_i+1]\). A variable choice is a default axiom. An affine choice follows from the accepted construction which adds one variable at a time, derives the Boolean choice for the sum in four cases, and cuts the two choices. Constants use the true axiom and weakening. This takes at most \(32(n+1)\) nodes per form. Add only the selected \(a_i\) equations, using each \(E_{b_i}\) once. The other disjunct from each premise is its own failure equation. After \(|I|-1\) additions, the selected polynomial is exactly \(\sum_{i\in I}a_i=h+c\). Weaken by the remaining failures. For empty \(I\), start from the true equation \([0]\) and apply the same weakening. All disjuncts keep their required multiplicities even when polynomials coincide.

For \(r=2\), a gate with factor \(1+b_1+b_2\) uses values \(1,0,0,1\) on branches \(00,01,10,11\). On branch \(01\), for example, select \([b_1]\) and \([b_2+1]\). Their sum gives \([1+b_1+b_2]\) under the two failures \([b_1+1]\) and \([b_2]\). Thus the third linear combination needs no additional split.

## Replay in degree two

Construct a branch substitution \(\sigma_\beta\) in declaration order. It fixes each original variable. Given \(t=hg\), where \(h\) is the chosen covered factor, let \(G=\sigma_\beta(g)\). By induction \(G\) is affine on the originals. Send \(t\) to \(cG\). The defining equation then has formal image

\[
\sigma_\beta(t+hg)=(h+c)G .
\]

Multiply the selected \([h+c]\) in the preceding certificate by \(G\). This gives exactly the defining image under \(H_\beta\). The multiplication also works when \(G\) or \(h+c\) is zero and when either factor repeats a variable. Polynomial arithmetic cancels coefficients modulo two and retains formal squares.

Replay every original line under the same \(H_\beta\). An input axiom or the true axiom weakens by this context. For a Boolean default on an earlier name, derive the Boolean choice of its affine image, then weaken. Syntactic weakening, one-occurrence contraction, false-constant deletion, and multiplication apply to the same selected occurrence after substitution. The substituted product equals the image of the legal original product by the ring homomorphism, including all formal cancellations. Each displayed multiplier and each resulting equation consequently has formal degree at most two. In a binary linear combination the two contexts are both present. Contract exactly one extra occurrence of each of the \(r\) failures. This preserves every occurrence belonging to the image of the original line, even when a side equation equals a guard. The branch therefore ends in \(H_\beta\).

Pair the two final branches with the same prefix and opposite last basis bit. Add their complementary last failure equations, delete the resulting false constant, and contract one extra copy of the common prefix. Repeat to obtain empty. When \(r=0\) there is one branch and no cut. If the last original node cites an already cached empty axiom, an identity weakening can display the empty conclusion as the last node of the serialized unnamed proof. ∎

## Cost and projection

The basis choices cost at most \(32r(n+1)\) nodes once, shared across branches. Each original node on one branch costs at most \(32(n+1)+r+3\) nodes, including a fresh affine Boolean derivation when needed. A declaration needs at most \(r-1\) additions for a nonempty subset, one weakening and one multiplication after its basis choices. A binary ordinary inference uses \(r\) extra contractions. The fewer than \(2^r\) final cuts cost at most \(r+2\) nodes each. With the possible final identity weakening these bounds give the displayed constant. The counts refer to primitive nodes, with one syntactic weakening allowed to append an explicit list of equations. Original side widths enter reading, copying, and verification work.

Let \(L\) be the explicit length of the input certificate, formula, and generators. Gaussian elimination, selection of gate factors and each branch replay use polynomial work in \(n+L\). In particular an affine image has at most \(n+1\) terms and a quadratic image has at most \(\binom{n+2}{2}\) terms. Shared names need only their current affine images. Total explicit work is \(2^r\operatorname{poly}(n+L)\). The factor \(2^r\) counts the converter's cases. The theorem supplies no lower bound on the minimum number of cases.

A signed-literal or constant substitution on original variables acts linearly on the space of linear parts and changes constant terms independently. It carries a supplied cover to a cover of rank at most \(r\). The accepted transport keeps the proof-local names fresh in their original order. Thus one may recompute the rank after projection and charge only the surviving rank in this elimination. [Name-preserving transport](../../PRODUCT-NAME-TRANSFER-20261115-001A/PRODUCT-NAME-TRANSFER-20261115-001A-P001_named_substitution/proof.md)

## Original proof and checks

The original test refutes the four clauses \(x,y,z,\neg x\lor\neg y\lor\neg z\). It declares

\[
t=xz,\qquad u=ty,\qquad v=(1+x+y)(1+t+z),\qquad w=(1+u+v)y.
\]

The forward derivation obtains the assertion \(w=1\). From it and the product definitions the proof recovers the input units used against the negative clause. One use of \(t=1\) is first recovered by adding \((t+1)t\) and \((t+1)^2\). All 81 input proof nodes are ordinary ancestors of empty. The four names compute four distinct nonconstant functions on the original Boolean cube. The second and third declarations force the independent directions \(y\) and \(x+y\) in any original cover because their other operands contain \(t\).

| Case | Rank | Declarations | Depth | Branches | Unnamed nodes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original four clauses | 2 | 4 | 3 | 4 | 618 |
| Identify \(x=y\) by actual proof transport | 1 | 4 | 3 | 2 | 238 |
| Send \(x=y=1\) by actual proof transport | 0 | 4 | 3 | 1 | 79 |
| Three independent forms and ten nested gates | 3 | 10 | 10 | 8 | 928 |

A direct subset-sum computation checked 4,096 query answers across all ordered pairs of affine generators in three variables. The even-weight subspace on five variables gave another 1,536 checks with four overlapping generators in every order. Direct expected guard multisets matched 341 primitive derivations across ranks zero through four. The existing quadratic kernel checked the output inferences syntactically, and an independent Boolean truth-table evaluator checked their implications on the bounded input cubes. Two seven-node proofs with one and 257 side occurrences respectively both gave 54 output nodes. Extra controls rejected an uncovered gate, an invalid future name even when its two occurrences cancel, a nonlinear generator, a new name used as an original generator, an invalid declaration order, a malformed Boolean default before a repeated empty input axiom, and an incorrectly changed multiplier. These are same-task machine checks at V1. The unbounded theorem rests on the symbolic construction. External novelty remains unassessed. [Executable check](check.py) · [Numerical results](checks.json)

## Public interface and replay

`AffineBasis(n, generators)` accepts the preceding checker's list-of-monomials format. It exposes its independent constant-free `.forms`, integer `.rank`, and `.coordinates(h)`, returning an affine offset and a bit mask in this basis or `None` outside the covered space. Bit \(i\) selects `basis.forms[i]` in zero-based Python indexing. The rank is that of the supplied generators. A smaller valid cover can be supplied independently.

`eliminate(n, cnf, proof, generators)` returns a checked unnamed certificate and numerical statistics. To reuse the equation derivation, initialize `boolean = B["affine_boolean_builder"](dag)` once. For a branch tuple call `failures, derive = guard_equation_builder(dag, basis.forms, bits, boolean)`. The tuple `bits` assigns the basis forms in order. For `offset, mask = basis.coordinates(h)`, `selected, node = derive(mask)` gives the polynomial \(h+h(\beta)\) and the DAG node that holds it under the full failure context. The offset cancels from this polynomial. Branches are enumerated in lexicographic order and the last bit is cut first. [Converter](solver.py)

```sh
python3 -B proofs/AFFINE-FACTOR-RANK-20261115-001A/AFFINE-FACTOR-RANK-20261115-001A-P001_ranked_elimination/check.py
```
