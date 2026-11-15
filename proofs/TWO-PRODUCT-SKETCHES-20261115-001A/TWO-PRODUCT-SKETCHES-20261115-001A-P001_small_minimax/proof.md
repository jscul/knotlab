# The best two private product sketches on small paths

Status: Proved

## Standard statement

A path of \(m\) products has \(m+1\) original bits \(x_0,\ldots,x_m\), products \(x_i x_{i+1}\) for \(0\le i<m\), and checksum \(Q\) equal to their sum in \(\mathbb F_2\). Choose any two fixed masks \(A,B\subseteq\{0,\ldots,m-1\}\), independently, including empty and full masks. Write \(P_A,P_B\) for the two sums of selected products. After imposing opposed full checksums, the two *separate* honest relations on the visible tuple \((x,s,a,b)\) are

\[
 L:\ s=Q(x),\quad a=P_A(x),\quad b\text{ free},\qquad
 R:\ s=1+Q(x),\quad b=P_B(x),\quad a\text{ free}.
\]

For each current affine case \(W\), replace it by \(\operatorname{aff}(W\cap L)\cap\operatorname{aff}(W\cap R)\) to a fixed point. The affine hull of the empty set is empty. An empty case is one terminal case. At a nonempty fixed point the reader may query any affine bit of the visible tuple, adaptively, with two child cases. The two masks remain fixed throughout the tree. Count leaves and maximum query depth separately.

| Number of path products | Leaves with only the full checksums | Minimum leaves with two chosen sketches | Minimum depth with two chosen sketches |
| ---: | ---: | ---: | ---: |
| 1 | 2 | 2 | 1 |
| 2 | 2 | 2 | 1 |
| 3 | 4 | 4 | 2 |
| 4 | 4 | 4 | 2 |
| 5 | 8 | 6 | 3 |
| 6 | 8 | 6 | 3 |
| 7 | 16 | 8 | 3 |
| 8 | 16 | 8 | 3 |

For five products the **complete distribution over all 1,024 ordered mask pairs** is 92 pairs requiring six leaves, 72 requiring seven, and 860 requiring eight. All have minimum depth three. Each of the 124 pairs having at least one empty or full mask costs eight. With six products, exposing the same prefix of two products on both sides costs six, while exposing the same prefix of three costs eight, even allowing a different first question. With nine products the certified bounds are \(8\le L_9\le12\). [Exact mask classes and coverage](checks.json) · [Explicit query trees](trees.json)

For a separate uniform result, suppose \(Q=\sum_{i=1}^r u_i v_i\) on independent pairs and the sketches select subsets of these same products after an invertible linear input recoding. A *label* of pair \(i\) is \((\mathbf1_{i\in A},\mathbf1_{i\in B})\). One constant mask leaves the exact public cost \(2^r\). If both masks recover the same nontrivial partition of sizes \(j,r-j\), the exact minimum is \(2^j+2^{r-j}\). Three or four distinct labels imply at least \(2f(r-1)\) leaves, where \(f(k)=2^{\lfloor k/2\rfloor}+2^{\lceil k/2\rceil}\) for \(k\ge2\). Thus at \(r=16\), three or four labels require at least 768 leaves. The balanced common partition costs exactly 512. This statement requires the *simultaneous* representation of both sketches by the independent products.

## Nearest known result

The predecessor proves the public-only \(2^r\) theorem for a quadratic of polar rank \(2r\) and gives the full-product matching bound when every individual product in both evaluations is available. It also constructs upper bounds from selected prefix checksums. Affine parity decision trees and the polar normal form for Boolean quadratics are established tools. This leaf fixes exactly one private sketch per evaluator and grants each complete evaluator its own exact, repeated affine hull. It proves small global optima for that model and exact diagonal subclasses. External novelty remains unassessed. [Predecessor including the public-rank and full-product results](../../TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/proof.md) · [Cohen and Shinkar on parity decision representations](https://eccc.weizmann.ac.il/report/2014/099/)

## Trees and the first strict improvement

Fix the same prefix of \(j\) products on both sides and ask \(a+b\). On answer one it suffices to make the shared prefix affine by fixing an alternating set of its path vertices. The two hulls then force the same value for \(a,b\), closing that case. On answer zero the two original sums outside the prefix have opposite required values, \(s+a\) and \(1+s+b\). Fix alternating vertices of the suffix to make this common function affine. The tree has \(2^{\lfloor(j+1)/2\rfloor}+2^{\lfloor(m-j+1)/2\rfloor}\) leaves. In fact these are the respective **exact child costs for this particular first question**. For the first child set the exterior vertices outside the prefix to zero, preserving the endpoint shared with the suffix, and set \(a=s,b=1+s\). For the second set the exterior prefix vertices to zero and \(a=b=0\). Each affine restriction contains the exact opposed public-only model on the active block. The predecessor's rank theorem supplies the matching lower bounds. A split with \(j=2\) has child costs two and four for \(m=5\) and \(m=6\).

Unequal masks attain the same optimum on five products. Number bits from the low end, so \(A=6\) selects products 1,2, while \(B=14\) selects 1,2,3. Query \(a+b\). On answer one query \(x_1+x_3\), closing both cases. On answer zero query \(x_0+x_1+x_3+x_4+x_5\), then \(x_1+x_4\) in each branch. This closes four further cases. To see why the two-leaf branch works, \(P_A=x_2(x_1+x_3)\) becomes affine. The left hull gives \(a=P_A\). On the right \(b=P_A+x_3x_4\), so the fixed discrepancy forces \(x_3=x_4=1\). The remaining \(Q\) is now affine on this branch and both checksums disagree. On the four-leaf branch the two input equations make \(Q+P_A=x_0x_1+x_3x_4+x_4x_5\) affine. Combining the two sides' hull consequences again forces \(x_3=x_4=1\), after which \(P_A\) and \(Q\) become affine. For either value of the second query on the two-leaf branch, the exact case sizes are 128, 64, 8, and then 0 over successive rounds. Masks \(1,3\) supply the distinct exact seven-leaf example, with a tree using queries that mix an input, a checksum, and a sketch. [All three sizes and the actual queries](trees.json)

## Finite exhaustive decision procedure

For a nonempty saturated case \(W\), a tree has at most \(K\) leaves exactly when some nonconstant linear form splits \(W\) into children that fit budgets \(i,K-i\) for some \(1\le i<K\), after saturating each child. An empty child consumes one leaf. A live child consumes at least two. This recurrence is exhaustive by cutting at the root of a tree or adjoining two witnesses. An affine constant only permutes the two answers. The implementation enumerates each distinct character of the direction space of \(W\) using its pivot coordinates; these coordinate restrictions form a basis of its dual. It computes each hull by taking a base point and the linear span of the observed differences. It stops saturation only at equality or emptiness. [Bit-set threshold minimax](minimax.cpp) · [Separate literal point-set implementation](solver.py)

The following equivalences reduce the finite search.

- Replace \(A\) by its complement with \(a\mapsto a+s\), or \(B\) by its complement with \(b\mapsto b+1+s\). Both maps are affine bijections of the corresponding honest relations, including their free foreign bits.
- Switching evaluators sends \((s,a,b)\) to \((1+s,b,a)\). Reversing the path relabels inputs and reverses both masks.
- Translate \(x\) by \(u\). Correct \(s,a,b\) by \(F(x+u)+F(x)\) for \(F=Q,P_A,P_B\), respectively. These corrections are affine in \(x\), so this is an affine automorphism of both whole relations. For fixed output coefficients \((\alpha,\beta,\gamma)\), a root question \(\ell(x)+\alpha s+\beta a+\gamma b\) is equivalent, up to a constant, to every question obtained by shifting \(\ell\) by a row of the polar-form row space of \(\alpha Q+\beta P_A+\gamma P_B\). Every such shift is achieved by some \(u\). We use this reduction only at the initial saturated root. When a normalized mask is zero, its rooted coordinate is already fixed. On smaller cases we enumerate all distinct characters of that case.

The five-edge mask symmetries have 76 orbits. The lower threshold of five leaves fails in every orbit. The two additional thresholds six and seven give the complete distribution above because the public strategy uses at most eight. The independent point-set program also tests the three-leaf lower threshold over every ordered mask pair at three edges, with every ambient linear form and neither mask nor translation symmetry. It rechecks the affirmative trees on the actual restricted relations, including an arbitrary-form witness emitted by the C++ minimax. [Per-orbit five-edge costs](checks.json) · [Checker](check.py)

## Affine restrictions and seven-edge coverage

If an affine map sends the two honest sets of a smaller problem into the respective two honest sets of a larger one, a larger proof pulls back to a proof of the smaller problem with at most the same leaves. Indeed, if the image of a smaller current case is contained in the larger case, the inclusions persist through each hull and intersection because affine maps commute with taking affine hulls and preserve inclusion. They persist under the pulled-back query. Drop a query that becomes constant on the smaller fixed point. If the larger case closes, the smaller one closes as well. This argument does not require an exact cover of the larger case.

**Any subsequence of positions embeds.** Identify the endpoints of each deleted edge. The retained edges form a shorter path, while a deleted product has value \(y^2=y\) for its contracted Boolean bit \(y\). Thus the three large sums equal the three retained sums plus known affine corrections. Adjust \(s,a,b\) by these respective corrections. This maps both smaller honest sets into the correct larger sets, preserving the free sketch on each side. In particular the global minimum cannot decrease with path length.

For every seven-edge pair, test all 21 five-position subsequences against the *proved* five-edge cost table. Also test whether the matching result proved below supplies a lower bound of eight. Subsequence restrictions prove the bound for 16,376 ordered pairs. Of these, 824 also pass the matching test. The other eight pairs all belong to the orbit of masks \(7,7\) and pass the matching test alone. The union covers all 16,384 ordered pairs. The explicit prefix of length four attains eight. With eight edges contract one position for the lower bound and split \(4+4\) for the upper. With nine edges contract to eight for the lower and split \(4+5\) for the upper. The latter is a one-size-past interval. [Exact cover counts and sample embeddings](checks.json) · [Cover verifier](check.py)

There is a stronger restriction for the actual six-edge midpoint. On the five-edge problem take \(A=B=14\), whose exact cost is eight. Map its bits \(y_0,\ldots,y_5\) to the six-edge tuple

\[
 (x_0,\ldots,x_6)=(y_2,\ y_1+y_3,\ y_4,\ y_1,\ y_0,\ y_5,\ y_0+y_4).
\]

The sum of the first three large products is \(y_1y_2+y_2y_3+y_3y_4\). The last three sum to \(y_0y_1+y_4y_5\). Thus both the full and midpoint checksums agree with their five-edge counterparts, with \(s,a,b\) unchanged. Every six-edge midpoint tree costs at least eight. The off-center \(2+4\) tree costs six. For a one-sided sketch at six edges, contraction gives the five-edge one-sided lower bound eight for every choice and the public tree attains it.

## Independent products and the three-label obstruction

Suppose \(Q=\sum_{i=1}^r u_i v_i\) on independent pairs, with mask labels \((c_i,d_i)\). A constant mask imposes \(a=0\) or \(a=s\) from the left; a constant right mask imposes \(b=0\) or \(b=1+s\). Saturation imposes those equations at the root, so discard such redundant bits. The other output bits are free in the affine hull of each whole side at the root. For example on the left an extra affine identity involving \(s,a\) would yield a vanishing linear combination of \(1,u_i,v_i\) and the independent monomials \(u_i v_i\) of \(Q,P_A\). The coefficients of two independent output sums must vanish; the free \(b\) contributes no constraint. The right side has the symmetric statement.

Consider an arbitrary query after these eliminations. Write \((\alpha,\beta,\gamma)\) for its coefficients of \(s,a,b\), assigning zero to a discarded coordinate. A pair \(i\) can absorb this query if its input coefficients are not both zero or if
\[
 \alpha+\beta c_i+\gamma d_i=1.
\]
Indeed the contribution from this pair is a nonconstant Boolean polynomial \(\lambda u_i+\mu v_i+(\alpha+\beta c_i+\gamma d_i)u_i v_i\). Choose two genuine AND states on which it takes opposite values. Keep the other \(r-1\) pairs live. As a function of the smaller visible tuple, select between those two fixed states to cancel the rest of the query to the required answer. Each installed input and its true product \(h\) is affine in that selector bit; the selector itself is affine in the smaller visible tuple. Map the retained outputs to \(s'+h,\ a'+c_i h,\ b'+d_i h\). Every smaller left or right solution maps into the corresponding larger solution, including its unconstrained foreign sketch. This gives an affine copy of the smaller problem in **each** child. A query whose only remaining effect is a constant can be discarded.

**One constant mask.** If both are constant, the public polar-rank theorem gives \(2^r\) leaves. If just one side has a nonconstant sketch, the remaining output coefficients are tested against both vectors \((1,0)\) and \((1,1)\). Every nonconstant query can therefore be absorbed by some pair. Deleting that pair leaves a one-sided problem or a public problem, so induction gives at least \(2\cdot2^{r-1}=2^r\) leaves. The public input questions attain this bound. The base \(r=0\) closes at the root.

**Exactly two labels with both masks varying.** After taking a complement if necessary both masks indicate the same group \(J\), of size \(j\), and its complement has size \(k\), with \(j,k>0\). The sole nonconstant query that no pair absorbs is \(a+b\), up to a constant. In its two branches, restrict the other group to zero and the redundant sketch bits to their honest affine values as in the prefix proof. The public \(j\)-pair and \(k\)-pair problems give respective lower bounds \(2^j,2^k\), and making the relevant products affine attains both. Any other query can be absorbed by a pair in both branches. If both labels remain after deleting it, the inductive lower bound on the sum of the two children is at least \(2^j+2^k\). If the deletion exhausted a singleton group, each child contains the public problem on the other \(k\) pairs and \(2\cdot2^k\ge 2+2^k\). This proves exactness for all first questions, including input/output mixtures.

**Three or four labels.** Any three distinct vectors of the form \((1,c_i,d_i)\) are linearly independent over \(\mathbb F_2\). Hence every nonconstant query is absorbed by a pair in both children. For every pattern on \(r\ge2\) pairs the universal diagonal lower bound is \(f(r)\). Prove this by induction, using the one- and two-label formulas, convexity of \(2^j+2^{r-j}\), and \(2 f(r-1)\ge f(r)\) for \(r\ge3\). In the three- or four-label case the stronger conclusion \(2f(r-1)\) follows directly from the two embedded children. For \(r=16\) this gives \(2(128+256)=768\). The public \(2^r\) upper bound also shows that three or four labels on three pairs have exact cost eight. For three distinct labels, the checker tests every one of the 511 nonconstant queries, both answers, and all 128 visible points of the smaller model. It verifies each affine embedding and both side inclusions. With two variable labels it checks that the single unabsorbed query is precisely the sketch discrepancy.

## Testing simultaneous recoding on odd paths

Write \(m=2r-1\), \(U=(x_0,x_2,\ldots)\), \(V=(x_1,x_3,\ldots)\). Then \(Q=U^T M V\) with \(M\) unit lower bidiagonal. Make \(M_A,M_B\) by retaining just their indicated entries. The two operators \(T_A=M^{-1}M_A,\ T_B=M^{-1}M_B\) admit a common basis of eigenvectors with eigenvalues \(0,1\) exactly when they are commuting idempotents. Necessity follows for diagonal matrices. For sufficiency an idempotent splits the space into its kernel and image, each preserved by the commuting second operator. Split both spaces once more for the second operator. In the resulting basis put \(V=S v\), \(u=S^T M^T U\). Then \(Q=u^T v\) and the sketches select subsets of the \(r\) individual independent products. This tests a specified simultaneous change of the two input classes.

On seven-edge paths 832 ordered mask pairs pass. Their proved lower bounds are eight for 36 pairs, ten for 40, twelve for 600, and sixteen for 156. Each pair was counted with its actual ordered multiplicity. The checked finite audit constructs the common basis and compares the three original functions on every assignment for every representative that qualifies. The test is sufficient for the lower-bound cover. Other masks can still have the same minimum for different reasons. [Operators and diagonal labels](matching.py) · [Numerical checks](checks.json)

The point-set hull implementation, tree format and finite minimax are directly reproducible with `python3 -B check.py`. The tree nodes are `[q, zero_child, one_child]`, where the low \(m+1\) bits of \(q\) multiply \(x_0,\ldots,x_m\), followed by \(s,a,b\), and `null` denotes an empty saturated case. The query mask uses ordinary integer bit positions, so indices start at zero. The computed minima concern this deterministic case-tree procedure with the stated observations. They do not give a lower bound on general satisfiability algorithms.
