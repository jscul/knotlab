# Two separately revealed product sums still require exponentially many affine branches

Status: Proved

## Standard statement

Work over the two-element field. Let \(Q,A,B\) be Boolean polynomials of degree at most two on the same \(n\) inputs \(x\). Write \(\rho(F)\) for half the rank of the alternating polar form of \(F\), and assume \(k=\rho(Q)\ge1\). The public coordinates are \(x,s,t,u,v\), with \(s+t=1\). The left relation is \(s=Q(x),u=A(x)\). The right relation is \(t=Q(x),v=B(x)\). The other side's sketch is free in each individual relation.

A refutation starts with these public affine conditions. Inside an affine cell it repeatedly takes the affine hull of the points satisfying each separate relation and intersects the results. It branches on any Boolean affine functional of **all** visible coordinates. A terminal rejection requires an empty saturated cell. Let \(L\) count the leaves of any such deterministic tree. Then

\[
 L\ \ge\ \left\lceil\tfrac23\,2^{\lceil k/2\rceil}\right\rceil.
\]

For even \(k\) the stronger bound \(L\ge2^{k/2}\) holds. The statement allows independent choices of the two sketches and query choices depending on earlier answers. On the path of \(m\) products \(x_{i-1}x_i\), \(Q\) is their sum and each sketch is any fixed XOR of those products. Here \(k=\lceil m/2\rceil\). Optimizing both masks and the tree gives \(\Theta(2^{k/2})\) leaves. At \(m=31\) the one-sided argument proves at least 256 leaves. A tree with fewer than 512 requires **each** mask \(M\) to have \(\min(\rho(M),\rho(Q+M))\in\{7,8\}\).

For \(p\) left and \(q\) right fixed product sums, put \(b=\min(p,q)+1\). The path optimum lies between \(\lceil(2/3)2^{\lceil k/b\rceil}\rceil\) and \(b2^{\lceil k/b\rceil}\). Polynomial leaf count requires \(\Omega(m/\log m)\) bits on each side, and matched prefixes attain that order.

## Nearest known result

The declared predecessor proves exactly \(2^k\) leaves when only the two opposed totals are visible. It also gives a 512-leaf common midpoint construction for 31 products. The present lower bound permits one independently chosen product sum on each side and all affine mixtures in a query. [Opposed checksums, predecessor C](../../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/proof.md)

Cohen and Shinkar determine the DNF-of-parities size of inner product. Besselman and coauthors study direct sums in randomized parity decision trees. Here free propagation takes each evaluator's exact affine hull inside the current cell and can repeat before any paid branch. The proofs below establish the lower bound for that inference rule directly. [Cohen and Shinkar](https://eccc.weizmann.ac.il/report/2014/099/) and [Besselman et al.](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.16)

## Quadratic ranks and affine hulls

If \(T\) is a nonempty source affine subspace of codimension \(e\), then \(\rho(F|_T)\ge\rho(F)-e\). Deleting one dimension of the domain deletes a row and a column of the polar matrix. Conversely a quadratic of half-rank \(b\) becomes affine on a linear subspace of codimension \(b\). Successively choose vectors with polar pairing one, split off their two-dimensional nondegenerate span by taking its orthogonal complement, and retain one vector from each pair together with the radical. The polar form vanishes on the retained subspace.

For uniform source \(x\), any affine \(\ell\) satisfies \(\left|\mathbb E(-1)^{F(x)+\ell(x)}\right|\le 2^{-\rho(F)}\). Square the expectation and substitute \(x+h\) for the second independent input. The inner average over \(x\) vanishes unless \(h\) lies in the polar radical. Its surviving terms have absolute value at most one and the radical has proportion \(2^{-2\rho(F)}\).

**Graph lemma.** Suppose every nonzero combination of the \(j\) output quadratics of \(G\) has half-rank at least \(R\). The graph of \(G\) intersects every affine cell of codimension at most \(R\), and its intersection with each affine cell of codimension strictly below \(R\) spans that cell. The same holds after translating the outputs or adding affine functions of the inputs.

Indeed, row-reduce the equations of a nonempty cell on their output columns. This leaves \(e\) independent source conditions and \(p\) independent combinations of outputs equal to source affine functions, with \(e+p\le R\). The source conditions describe a nonempty slice. For \(p>0\), each of the \(2^p-1\) nonzero combinations of the remaining conditions has absolute bias at most \(2^{-(R-e)}\le2^{-p}\) there. Expand the indicator of all \(p\) equalities as the product of their character indicators. Its mean is at least \(2^{-p}(1-(2^p-1)2^{-p})>0\). For \(p=0\) any input on the slice works. Every hyperplane and its complement inside a cell of codimension below \(R\) are therefore met, giving the span assertion.

Two operations allow the lemma to be used under arbitrary rounds of inference. If a relation is cylindrical over the projection \(\pi\), its hull inside an affine cell \(H\) is

\[
 H\cap\pi^{-1}\bigl(\operatorname{aff}(\pi(H)\cap R)\bigr).
\]

Indeed the relevant fibers of \(H\) are translates of the same direction space. The hull of a nonempty union of these fibers contains that direction space and projects onto the stated hull. The identity also holds for an empty union. Second, preimposing an affine restriction or injectively embedding a restricted model gives a lower bound for the original tree whenever its side relations map into their corresponding genuine relations. Each hull and intersection is monotone. A restricted run stays inside the original run step by step, and each original query pulls back to an affine query, possibly constant. The restricted tree has at most the original number of leaves.

## Mass until the first effective inference by the right side

Set \(b=\min(\rho(B),\rho(Q+B))\) and \(R=\min(k,b)\). If \(R>0\), the graph lemma applies to the right's pair \((Q,B)\). The right hull leaves the entire current cell alone as long as its projection to \((x,t,v)\) has codimension below \(R\). This remains true even when earlier equations mix \(u\) with right-side coordinates, by the cylinder identity.

Put a probability measure on points satisfying the left equations. Choose \(x\) uniformly, set \(s=Q(x),t=1+Q(x),u=A(x)\), and choose \(v\) independently and uniformly. Along each such point's query branch all left hull steps preserve the point until the right side first shrinks the cell. Such a shrink must occur for that point's branch to refute. The resulting nodes are prefix-free when each branch stops at its first right shrink. The affine cells immediately before those shrinks cover all left-honest mass and their number is at most the tree's leaf count. This argument counts a collection across branches. Sequential hulls in either fixed order reach the same saturated cell as simultaneous intersections, by monotonicity and finite descent.

For any codimension-\(c\) affine cell \(C\) of \((x,t,v)\), expand its indicator in the \(2^c\) characters in its row space. The constant character contributes \(2^{-c}\). Characters with nonzero \(v\)-coefficient average to zero. Among the remainder a nonconstant character can have nonzero mean only if its \(t\)-coefficient is one. At most \(2^{c-1}\) row-space characters have this coefficient, and each has absolute bias at most \(2^{-k}\). Thus a projected cell containing one first shrink has mass at most \(2^{-R}+2^{-k-1}\). Projection can only increase its mass. Consequently

\[
 L\ \ge\ \left\lceil\frac{1}{2^{-R}+2^{-k-1}}\right\rceil. \tag{1}
\]

The other estimate applies when one of \(B+\beta Q\), \(\beta\in\{0,1\}\), has half-rank \(b\). Restrict the source at cost \(b\) to make it affine, say \(B+\beta Q=\ell(x)\), and impose the visible affine equation \(v=\beta t+\ell(x)\). The right evaluator on this embedded space is exactly the single gate \(t=Q\), including the originally supplied sketch. The left gate can keep its arbitrary \(u=A(x)\). Let \(k'=\rho(Q|_T)\ge k-b\). Give uniform input on \(T\) to the left evaluator. Its \((x,t)\) projection is the graph of \(1+Q|_T\). If \(k'>0\), the right cannot shrink until the projecting cell has codimension at least \(k'\), and its projected mass there is at most \(2^{-k'}+2^{-k'-1}\) by the same Fourier expansion. For \(k'=0\) the trivial one-leaf bound suffices. Thus

\[
 L\ \ge\ \left\lceil\tfrac23\,2^{\max(0,k-b)}\right\rceil. \tag{2}
\]

The two sides can be interchanged. In particular, put \(a=\lceil k/2\rceil\). If \(b\ge a\), (1) gives \(L\ge2^a\) after rounding, since \(2^a-2^a/(1+2^{a-k-1})<2^{2a-k-1}\le1\). For \(b<a\), (2) gives \((2/3)2^a\) or better. For even \(k\), \(k-b\ge a+1\) in this alternative, proving the stronger even case.

## The path upper bound and the 31-product filter

A run of \(j\) consecutive path edges has half-rank \(\lceil j/2\rceil\). Its even-to-odd bipartite incidence matrix has a full-rank triangular square minor of that order, which is also the smaller bipartition size. Disjoint runs add their half-ranks. Use the same sketch on both sides, taking the first \(2\lfloor k/2\rfloor\) products. The two disjoint edge sets give ranks \(\lfloor k/2\rfloor\) and \(\lceil k/2\rceil\), even when they share a vertex. Query \(u+v\). If it is one, expose \(\lfloor k/2\rfloor\) linear source coordinates making the prefix affine on every branch, which forces \(u=v\). If it is zero, expose \(\lceil k/2\rceil\) coordinates making the other sum affine, which forces \(s+u=t+v\). One can use the smaller bipartition of each run for these coordinates. This proves an upper bound of \(2^{\lfloor k/2\rfloor}+2^{\lceil k/2\rceil}\) and hence the claimed order of growth.

For \(m=31\), \(k=16\). Equation (2) excludes fewer than 512 leaves when \(b\le6\). Equation (1) does so when \(b\ge10\). At \(b\ge9\), the graph lemma requires projection codimension at least nine. Codimension ten or more gives mass strictly below \(1/512\) by (1)'s mass estimate. At codimension nine, if an equation contains \(v\), at most \(2^7\) row-space characters survive with \(v\)-coefficient zero and \(t\)-coefficient one. Hence the excess over \(2^{-9}\) is at most \(2^{-18}\). If \(v\) and \(t\) are both free over the source, the mass is just \(2^{-9}\).

It remains to consider \(v\) free and \(t\) affine on a codimension-eight source slice. Such a cell cannot witness the first right shrink. On the slice \(\rho(Q)\ge8\) and \(\rho(B),\rho(Q+B)\ge1\). Moreover at least one of the latter two is at least four by rank subadditivity. A hyperplane with a \(v\)-coefficient prescribes an affine value of \(B\) in addition to the prescribed affine value of \(Q\). The sum of the three absolute character biases is at most \(2^{-8}+2^{-1}+2^{-4}<1\), so both values can be realized. A hyperplane independent of \(v\) simply imposes one further source condition, on which the half-rank of \(Q\) is still at least seven, allowing both checksum answers. The right graph spans the cell. Thus every first-shrink cell has mass at most \(2^{-9}+2^{-18}\), with reciprocal strictly greater than 511. Together the two one-sided bounds leave only \(b=7,8\) for **each** mask as possible strict improvements. They give 342 and 256 leaves, respectively, at those two ranks.

## The surviving rank-seven masks on 31 products

There is a stronger exclusion when the smaller of \(M,Q+M\) has half-rank seven. Write \(J\) for the nonsingular polar matrix of \(Q\), and \(K\) for the polar matrix of this smaller component, of rank \(2a\). On \(I=\operatorname{im}K\) put

\[
 \omega(Kx,Ky)=x^\top Ky,\qquad \eta(u,v)=u^\top J^{-1}v.
\]

Both forms are alternating and \(\omega\) is well defined and nondegenerate. If \(\eta\) vanishes on every \(\omega\)-orthogonal pair, then \(\eta(u,\cdot)\) is a scalar multiple of \(\omega(u,\cdot)\) for each nonzero \(u\), by containment of the latter form's kernel in the former's. Comparing the values for \(u,v,u+v\) with \(u,v\) independent shows that the scalar is constant. Thus \(\eta=0\) or \(\eta=\omega\), giving \(KJ^{-1}K=0\) or \(KJ^{-1}K=K\), respectively.

Otherwise there is an \(\omega\)-orthogonal pair with \(\eta(u,v)=1\). Extend its span inside \(I\) to a maximal \(\omega\)-isotropic subspace \(N\) of dimension \(a\). This extension follows by repeatedly adjoining any vector in the orthogonal complement outside the current subspace while its dimension is below \(a\). On \(T=\operatorname{ann}N\), the form \(K\) vanishes, since for \(x\in T\) one has \(\omega(Kx,N)=0\), giving \(Kx\in N\). Moreover \(T^{\perp_J}=J^{-1}N\), and the radical of \(J|_T\) corresponds under \(J\) to the radical of \(\eta|_N\). Thus

\[
 \operatorname{rank}(J|_T)=2k-2a+\operatorname{rank}(\eta|_N)\ge2k-2a+2.
\]

Use this particular input restriction in (2). On the 31-edge path with \(a=7\), the surviving half-rank is at least ten, forcing at least 683 leaves.

To resolve the two exceptions, order source coordinates by the parity of their path indices. The off-diagonal block of \(J\) is \(P=I+\operatorname{subdiag}(1)\). The corresponding block of \(K\) is \(E=\operatorname{diag}(d_i)+\operatorname{subdiag}(e_i)\). The bits \(d_i\) select the odd-numbered edges, and \(e_i\) select the even-numbered edges between \(d_i,d_{i+1}\). Put \(U=P^{-1}E\). The two exceptional identities become respectively \(U^2=0\) and \(U^2=U\), as follows by multiplying the two off-diagonal polar blocks (the other diagonal block of \(J^{-1}K\) is similar to \(U^\top\)). For square zero, the diagonal entries \(d_i\) vanish. Then \(U_{ij}=e_j\) for \(i>j\). If \(j<h\) are consecutive positions in the list of indices where \(e_i=1\), the \((h+1,j)\) entry of \(U^2\) is one. Therefore \(E\) has rank at most one in the square-zero case.

The surviving rank-seven component must consequently satisfy \(U^2=U\). Equivalently its two complementary edge masks have half-ranks adding to 16. Indeed \(\operatorname{im}U+\operatorname{im}(I+U)\) is the entire space. The sum is direct exactly when \(U(I+U)=0\). This product has image contained in the intersection, and conversely a projector is the identity on its image and zero on the image of its complement.

The projector masks have a short description. Write \(c_j=d_j+e_j\). Below the diagonal, \(U_{ij}=c_j\) for \(i>j\). Idempotence requires, for all such indices,

\[
 c_j\bigl(d_i+d_j+\sum_{j<h<i}c_h\bigr)=c_j.
\]

Before the first nonzero \(c_j\), all intervening even-edge bits equal the odd-edge bit to their left. At the first nonzero \(c_j\), the equation for \(i=j+1\) forces \(d_{j+1}=1+d_j\). Taking differences of successive equations forces \(d_{i+1}+d_i=c_i\) thereafter. Thus from this gap onward the even-edge bits all equal the odd-edge bit to their right. Conversely, any such single cut gives the displayed idempotence equations by telescoping, including the case with no nonzero \(c_j\). For a fixed \(k\)-bit word \(d\), exactly one plus the number of transitions of \(d\) distinct even-edge strings occur. The rank of a triangular projector is the integer number of ones on its diagonal, since its zero and one eigenspaces give a direct sum. Therefore the number of rank-\(a\) projectors, when \(0<a<k\), is

\[
 \binom{k}{a}+2(k-1)\binom{k-2}{a-1}.
\]

For \(k=16,a=7\) this is 101,530. Including the complement orientation gives 203,060 raw masks with rank pair \((7,9)\) or \((9,7)\), out of the 105,830,912 whose smaller half-rank is seven. In combination with the preceding one-sided filter a strict gain at 31 products requires **each** mask either to have smaller half-rank eight, or to lie among those 203,060 rank-seven choices.

## An independent lower bound using a single restricted quadratic graph

There is also a direct bound of \(2^{\lceil k/3\rceil}\) that forces every restricted branch to the indicated depth. Set \(D=\lceil k/3\rceil\). In the span of \(Q,A,B\) modulo affine functions, whenever a nonzero quadratic part has half-rank less than \(D\), use its isotropic subspace to make it affine at a cost of at most \(D-1\) input conditions. Each step eliminates a quadratic direction. After at most two eliminations, the rank of the restricted \(Q\) is still at least \(k-2(D-1)\ge D\), so it survives and no third elimination is possible. The remaining independent quadratic parts have minimum half-rank \(D\) or more.

Let \(F=(Q,A,B)\) on this restriction and let \(K\) consist of all coefficients \(c\) for which \(c\cdot F=\ell_c(x)\) is affine. The first coordinate vector is outside \(K\), so choose \(\delta\in K^\perp\) with \(\delta_1=1\). In output coordinates \(y=(s,u,v+\delta_3)\) impose \(c\cdot y=\ell_c(x)\) for \(c\in K\). The resulting affine space has as many free output coordinates as there are independent quadratic parts. It contains the sheets \(y=F(x)\) and \(y=F(x)+\delta\). The first sheet satisfies the actual left evaluator. The second has \(s=Q+1,v=B\) and satisfies the actual right evaluator. Using any basis of independent output classes, the graph lemma shows that each sheet spans every cell of codimension below \(D\) in this affine space. Repeated hull propagation retains all such cells. After dropping constant questions **every** restricted branch therefore has depth at least \(D\), which forces \(2^D\) leaves.

For an elementary path-only check, keep edges numbered \(1,4,7,\ldots\). Their endpoints induce a matching. Keep only the most frequent pair of mask bits on those edges and set other vertices to zero. At least \(h=\lceil m/12\rceil\) independent products remain. For constants \(\alpha,\beta\) the restricted masks are \(A=\alpha Q, B=\beta Q\). Set \(u=\alpha s,v=\beta t\). The two restricted relations are the opposite scalar graphs of a rank-\(h\) sum, and the graph lemma for one output gives at least \(2^h\) leaves.

## How many fixed sums suffice for polynomial growth

More generally, give the left and right evaluators \(p\) and \(q\) fixed product sums in addition to their totals. With \(h=p+q\), any affine tree under the same whole-evaluator hull rule has at least

\[
 2^{\lceil k/(h+1)\rceil}
\]

leaves. Use the preceding restricted-graph argument with the vector of \(h+1\) quadratics consisting of \(Q\) and every supplied sum. For \(D=\lceil k/(h+1)\rceil\), at most \(h\) low directions can be eliminated because \(k-h(D-1)\ge D\) ensures that \(Q\) survives them. For the two translated sheets choose a direction annihilating every affine dependence and having total coordinate one, as above. Translate the raw coordinate of every right sketch by its component of this direction, and use raw coordinates unchanged for the left sketches. This gives the required two genuine evaluator sheets in a common affine space. The graph lemma used only \(e+p'\le D\) for the number \(p'\) of independent output conditions on a tested cell, so it applies for arbitrarily many supplied outputs.

The allocation matters as well. Put \(b=\min(p,q)+1\). In fact

\[
 L\ \ge\ \left\lceil\tfrac23\,2^{\lceil k/b\rceil}\right\rceil
\]

regardless of how many sketches the more exposed side receives. To see this, take the right side to be the less exposed one. Apply the same low-rank elimination to its \(q+1\) quadratics alone with \(D'=\lceil k/(q+1)\rceil\). This leaves an input slice on which \(Q\) has half-rank \(k'\ge D'\) and every combination of the independent right quadratic parts has half-rank at least \(D'\). Impose all the resulting affine dependencies among the right output coordinates and the inputs. Choose \(t\) as the first of the independent right output coordinates, since \(Q\) survives modulo affine functions. The other named right coordinates are affine functions of the chosen output coordinates and the inputs. The right relation in these coordinates is the graph of the independent residual quadratics, with the left-only sketches free. Its hull preserves the full current cell whenever the codimension of the projection to the right coordinates and inputs is below \(D'\).

For the first-right-shrink count, give a uniform input on this slice to the left evaluator. Set all its own supplied sums honestly, set \(t=1+Q\), and choose the remaining **independent** right output coordinates as independent fair bits. Recover all dependent right coordinates using the imposed affine equations. Every such point satisfies the left relation. On an affine projected cell of codimension at least \(D'\), independent fair output coordinates kill every character in which they occur, leaving mass at most \(2^{-D'}+2^{-k'-1}\le(3/2)2^{-D'}\). The same prefix-free cover proves the assertion. In particular, even revealing every individual product on one side maintains a \((2/3)2^k\) lower bound if the other side exposes only its total.

For the matching order on paths, partition the edges into at most \(b\) consecutive blocks of lengths at most \(2\lceil k/b\rceil\). This is possible since \(m\le 2k\). Reveal the prefix ending at every internal boundary on both sides. The initial disagreements at the two outside boundaries are zero and one, interpreting the empty prefix as zero. Within any interval with different endpoint disagreements, query the disagreement at a middle boundary and retain the subinterval whose endpoints disagree. This works with every sequence of intermediate answers. Its binary search has one terminal interval per block. On the final block the two local prefix differences compute the same edge sum and their public answers disagree. Exposing the smaller parity class of the block's incident vertices, of size at most \(\lceil k/b\rceil\), makes that common sum affine and closes the case. Thus

\[
 L_{\rm opt}\ \le\ b\,2^{\lceil k/b\rceil}.
\]

For fixed \(p,q\) this gives the precise exponential rate up to factors depending on the allocation. For polynomial growth \(L\le m^C\), the lower bound requires \(\min(p,q)+1\ge k/(C\log_2 m+\log_2(3/2))\). Conversely, \(\Omega(m/\log m)\) fixed bits available **on each side** suffice by taking matched prefixes delimiting blocks of \(O(\log m)\) products. For instance one can use \(\lceil m/w\rceil-1\) sketches per side with \(w=\lceil\log_2(m+1)\rceil\), giving at most \(\lceil m/w\rceil 2^{\lceil w/2\rceil}\) leaves. The threshold order refers to the ability to choose the fixed masks and attain some polynomial. Its degree can depend on the allocation constant. This uses neither cross-side access to the private product lists nor a monotonicity assumption on prefix disagreements.

## Checks and scope

`check.py` independently enumerates affine cells of a three-output example obtained by multiplication in the field of eight elements. All 174,763 cells of codimension zero, one or two pass the graph-span test. A codimension-three control loses three dimensions. It also traces 128 actual mixed-query trees on all mask pairs of a three-product path, checks the mass cover at the first right inference, verifies 8,190 raw path masks and their linear restrictions against a run-count recurrence, and exercises zero, one and two low-rank eliminations on larger paths. The recurrence counts all \(2^{31}\) individual masks without materializing them. Exactly 419,516,042 pass the necessary one-sided rank filter for a strict improvement over 512. The direct polar checker tests 682 smaller odd-path masks and constructs a 31-edge restriction with residual half-rank ten. A separate enumeration of 10,922 masks checks the projector cut description and rank count through seven bipartite coordinates. The full 31-edge recurrence also gives 101,530 in each complement orientation. Generalized rank elimination is checked for up to eight simultaneous outputs, and every sequence of internal disagreement bits is checked through twelve blocks. The counts are finite verification at V1, independent of the symbolic upper and lower estimates.

The theorem concerns deterministic tree refutations with two fixed separately computed sketches. A procedure comparing the two quadratic expressions directly can cancel them at once. These leaf bounds concern the specified information and inference rule. The one-sided bound in this proof leaves a finite gap at 31 products.
