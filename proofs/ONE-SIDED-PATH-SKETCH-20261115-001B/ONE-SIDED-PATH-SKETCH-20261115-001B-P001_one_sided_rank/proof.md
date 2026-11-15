# A quadratic observation on one side preserves the full affine-tree leaf count

Status: Proved

## Standard statement

All bits and polynomials are over the two-element field. Two evaluators receive the same finite input vector \(x\). The left relation requires \(s=Q(x),u=A(x)\). The right relation requires \(t=Q(x)\) and leaves \(u\) free. Impose \(s+t=1\). Both \(Q\) and \(A\) are arbitrary Boolean polynomials of degree at most two, including affine and constant terms. Set \(r=\rho(Q)\), where \(\rho\) is half the rank of the alternating polar form. A leaf can reject when iterating the two separate exact affine hulls of the satisfying points within its current affine cell gives an empty intersection. An internal query can be any affine function of \(x,s,t,u\) and can depend on earlier answers.

The minimum deterministic refutation leaf count is **exactly \(2^r\)**. In particular it is 512 at half-rank nine, with arbitrarily many additional input coordinates in the radical. A 17-edge path has half-rank nine, so this applies to its one-sided even-edge sum and to every other quadratic observation on those inputs. The count refers to the specified case tree with its supplied evaluator partition.

## Nearest known result

The unsketched scalar case has exactly \(2^r\) leaves. The preceding two-sketch study also gives a lower bound of \(\lceil(2/3)2^r\rceil\) when one side exposes only the total, and exact results for certain shared product decompositions. The present result covers an arbitrary single quadratic supplied only by the other evaluator. [Unsketched scalar theorem](../../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/proof.md) and [preceding rank lower bound](../../../proofs/TWO-PRODUCT-SKETCHES-20261115-001B/TWO-PRODUCT-SKETCHES-20261115-001B-P001_uniform_lower/proof.md)

Cohen and Shinkar determine the DNF-of-parities size of the inner-product function. Besselman and coauthors study direct sums for randomized parity decision trees. Our terminal rule takes two affine hulls separately and can repeat the operation for free. The proof below treats that rule explicitly. [Cohen and Shinkar](https://eccc.weizmann.ac.il/report/2014/099/) and [Besselman et al.](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.16)

## Affine restrictions and scalar quadratics

Eliminate \(t=1+s\). An injective affine map from a restricted problem into a branch gives a lower bound on that branch's leaf count if it sends satisfying points of each evaluator to satisfying points of the corresponding evaluator. Affine hull and intersection are monotone, so restricted propagation can be stronger. Pull back every original query, pruning constant branches. The resulting restricted tree has at most as many leaves. This applies at intermediate hull steps and to queries mixing inputs and outputs. Sequential hull steps in either fixed order have the same saturated cell as simultaneous intersections, by monotonicity and finite descent.

One affine input restriction lowers a quadratic half-rank by at most one, since it removes a row and a column from the polar matrix in an adapted basis. For uniform input and every affine \(\ell\),

\[
 \left|\mathbb E(-1)^{q(x)+\ell(x)}\right|\le 2^{-\rho(q)}.
\]

Indeed, square the average and use two inputs \(x,x+h\). The average in \(x\) vanishes unless \(h\) belongs to the polar radical, of proportion \(2^{-2\rho(q)}\). If \(D=\{f=0\}\) is nonempty and has proper affine hull, then **\(D\) itself is affine of codimension at most two**. Choose a hyperplane containing \(D\). In affine coordinates its indicator \(1+f\) vanishes on the complementary halfspace, hence equals one of the two defining affine literals times another affine function, by the squarefree degree bound. Its ones are cut out by at most two affine equations. Every nonempty quadratic level has density at least \(1/4\). For a nonaffine quadratic this follows by taking any nonzero degree-two monomial and fixing the other inputs, which leaves at least one solution among the four assignments. In the affine or constant cases the same bound is immediate.

For a single quadratic \(q\), opposing graphs \(s=q\) and \(s=1+q\) on the full source require at least \(2^{\rho(q)}\) leaves when \(s\) is free. With \(s\) already fixed, the two opposite fibers need at least \(2^{\rho(q)-1}\) leaves for \(\rho(q)\ge1\). For the pinned version, at any codimension below \(\rho(q)-1\) the rank is still at least four, so both fibers meet every hyperplane half as a nonconstant quadratic remains there. Thus every such cell is stable and every leaf must have depth at least \(\rho(q)-1\). For the free version, a cell with free output over the projected inputs is spanned by the graph of a nonaffine function on that projection and also by its complement. A cell pinning \(s\) to an affine source form spends one condition doing so and reduces to the pinned argument. Thus all cells of codimension below \(\rho(q)\) are stable. In both versions all meaningful answers survive through the stated depth, giving the leaf lower bound. The one-leaf lower is sufficient at rank zero.

## Two conditional problems

Let \(f,q\) be arbitrary quadratics on a common input. Set

\[
 D=\{x:f(x)=0\},\qquad \theta=\Pr(D),\qquad t_0=\min\{\rho(q),\rho(q+f)\}.
\]

Use \(U\) for the problem with left equations \(f=0,s=q\), right equation \(s=1+q\), and public \((x,s)\). Use \(P\) for the problem on public \(x\) with left equations \(f=0,q=0\) and right equation \(q=1\). We will prove

\[
 L_U\ge 2^{t_0}\theta \quad\text{for all }t_0,
 \qquad
 L_P\ge 2^{t_0-1}\theta \quad\text{for } t_0\ge3. \tag{1}
\]

The second bound deliberately starts at three. On four packed source bits, with bit \(x\) of a truth table giving the value at input \(x\), \(f=\mathtt{0xe248}\) and \(q=\mathtt{0x8777}\) give \(t_0=2,\theta=10/16\). Their pinned problem closes without a query. The rejected extrapolation would require more than one leaf. The checker replays this example.

Both claims follow by induction on the number of inputs, proving the pinned case first at each dimension. Empty \(D\) gives right-hand side zero. If nonempty \(D\) has proper affine hull, preimpose \(D\) as a common affine restriction, of codimension \(c\). On it \(f=0\) identically, \(\theta=2^{-c}\), and the remaining scalar quadratic has half-rank at least \(t_0-c\). The preceding scalar bounds give (1), including when the restricted half-rank is zero. We may take \(D\) to span its source henceforth.

For every affine \(\ell\), the bias estimate gives

\[
 \left|\mathbb E\big[(-1)^{q+\ell}1_D\big]\right|
 =\tfrac12\left|\mathbb E(-1)^{q+\ell}+\mathbb E(-1)^{q+f+\ell}\right|
 \le2^{-t_0}. \tag{2}
\]

In \(P\), when \(t_0\ge4\), consider either half of any nontrivial source hyperplane. It meets \(D\) since \(D\) spans, and the relative density of that quadratic level on the half is at least \(1/4\). Both ranks on the half remain at least \(t_0-1\ge3\), so (2) restricted there is strictly smaller than this density. Some points in \(D\) on the half have \(q=0\) and some have \(q=1\). The entire left relation and the entire right relation therefore each span the source. The root is stable. Any meaningful query is one input hyperplane with two children. Write \(\theta_0,\theta_1\) for the conditional densities. They sum to \(2\theta\), and the two new minimum half-ranks are at least \(t_0-1\ge3\). Induction gives at least \(2^{t_0-2}(\theta_0+\theta_1)=2^{t_0-1}\theta\) leaves. The finite pinned base below is used at \(t_0=3\).

In \(U\), use the direct finite bases for \(t_0\le2\). For \(t_0\ge3\), (2) is strictly smaller than \(\theta\ge1/4\). Hence \(q\) cannot agree with any affine function on \(D\). Since \(D\) spans the source, the graph of \(q\) over \(D\) spans the entire source-output space. The graph of \(1+q\) over the full source also spans. A first query on inputs alone gives the claimed bound by smaller-dimension \(U\) induction and averaging the two conditional densities. A first query involving \(s\) pins \(s\) to one of two affine functions \(\ell(x)+e\). In that answer the problem is exactly \(P\) with \(q_e=q+\ell+e\), with the same \(D,\theta,t_0\). Each of the two answers costs at least \(2^{t_0-1}\theta\) by the pinned result just proved, giving (1).

## Reduction of the finite bases

For two alternating polar forms of half-rank at least \(j\), there is a common \(2j\)-dimensional linear subspace where both are nonsingular. For each form consider its \(2j\)-linear Pfaffian evaluated on \(2j\) vectors, the sum over all perfect matchings of the product of the paired entries. This is an alternating multilinear form. It is nonzero because a nonsingular \(2j\)-dimensional subspace for that individual form has a symplectic basis. To choose common arguments, successively choose each vector outside the two kernels of the partially evaluated nonzero multilinear forms. Two proper linear subspaces cannot cover a vector space. If neither contains the other, the sum of one vector from each difference lies in neither. At completion both forms take value one. Equivalently both restricted alternating matrices are nonsingular, by the Pfaffian-square determinant identity (in characteristic two this follows by pairing each permutation cycle of length at least three with its reverse in the determinant expansion).

Apply this observation to the polars of \(q,q+f\) with \(j=t_0\), and take a coset of the common subspace on which the density of \(D\) is at least its original density. Restriction to that coset is valid for each evaluator, preserves \(t_0\), and cannot weaken the desired numerical lower bound. It therefore suffices to check \(U\) at \(j=0,1,2\) on zero, two and four inputs, and \(P\) at \(j=3\) on six inputs, with both polars nonsingular. All affine coefficients, constants and both pinned orientations must be covered. The raw finite verification below establishes these bases. It never calls a pinned inequality at \(j=2\).

## Returning to the unrestricted root

We prove the main lower bound by induction on \(r\). When \(r=0\), \(Q\) is affine and the two outputs conflict immediately. At positive rank choose a linear complement to the radical and restrict the common inputs to it. This gives a \(2r\)-dimensional source with nonsingular polar form \(J\) and an arbitrary restricted quadratic sketch. Any lower bound there applies to the original source. Conversely, querying one coordinate of each symplectic pair of \(Q\) makes it affine on every branch, including the radical's possible linear contribution. This proves the matching \(2^r\) upper bound in the original dimension.

Write \(K\) for the polar form of \(A\) on the reduced source. If \(A\) or \(A+Q\) is affine, impose the corresponding affine equation expressing \(u\) through \(x,s\). It agrees with the left graph and embeds the plain opposed-total problem because the right side ignores \(u\). If neither is affine, the left graph on \(x,s,u\) spans, since an extra affine identity would make one nonzero combination of \(Q,A\) affine. The right scalar graph with \(u\) free spans as well.

If \(K\) and \(K+J\) are both nonsingular, every nonzero quadratic combination of \((Q,A)\) has half-rank \(r\). Its graph spans any cell of codimension below \(r\). Indeed, to test whether it meets a cell of codimension at most \(r\), row-reduce the equations on the output columns. There are then \(e\) input constraints and \(p\) independent output constraints, with \(e+p\le r\). On the input slice every nonzero combination of the \(p\) equations has absolute bias at most \(2^{-(r-e)}\le2^{-p}\). The Fourier expansion of their simultaneous indicator has positive mean, since the \(2^p-1\) nonconstant terms have total absolute bias strictly below one. The case \(p=0\) is immediate. Applying this intersection result to both halves of each hyperplane inside a cell of codimension below \(r\) gives the span claim. The plain graph with free \(u\) also spans all these cells, either by the same argument on its relevant projection or by the scalar restriction argument above. Every branch has depth at least \(r\) in this case.

We may now take at least one of \(K,K+J\) to be singular. A first pure input query restricts to two affine hyperplanes. A nonsingular alternating form in \(2r\) dimensions has half-rank exactly \(r-1\) on either hyperplane, with the normal's \(J\)-dual spanning the restricted radical. Both answers therefore cost at least \(2^{r-1}\) by induction, which allows arbitrary extra radical variables.

For a query with no \(u\) and with coefficient one on \(s\), choose nonzero \(v\) and \(\epsilon\in\{0,1\}\) with \(K(v,\cdot)=\epsilon J(v,\cdot)\). Such a vector exists by singularity of \(K\) or \(K+J\). The two-child embedding below applies. For a query involving \(u\), change coordinates affinely to make the query the first test of \(u'=u+\gamma s+\ell(x)\). On the left it is \(F=A+\gamma Q+\ell\), and the right still ignores this bit. If \(Q+F\) has nonsingular polar, the two answers are exactly the unpinned conditional problems for \(f=F\) and \(f=F+1\), with \(q=Q\) and \(t_0=r\). Their masses sum to one and (1) gives \(2^r\) leaves. If the polar of \(Q+F\) is singular, take \(v\ne0\) in its radical. Then \(K_F(v,\cdot)=J(v,\cdot)\), and the embedding applies to the pure private query in the new coordinates.

Here is the embedding in both cases. Normalize \(Q(0)=A(0)=0\) by shifting output constants, writing \(A=F\) when the private coordinate was changed. Present the query as \(\lambda(x)+\gamma s+\delta u+e\) with \(\lambda\) linear. In the output-only case involving \(s\) one has \((\gamma,\delta)=(1,0)\). In the normalized private case one has \((\gamma,\delta)=(0,1)\) and \(\epsilon=1\). Thus \(\gamma+\delta\epsilon=1\) in both. Pick \(w\) with \(J(v,w)=1\) and write \(Z=\langle v,w\rangle^{\perp_J}\). For \(z\in Z\), consider sources \(x=z+c w+\eta v\), where \(c\) is fixed and \(\eta\) is one varying bit. The changes in \(Q\) and \(A\) from switching \(\eta\) are the constants

\[
 d_Q=Q(v)+c,\qquad d_A=A(v)+c\epsilon.
\]

Choose \(c\) so \(\lambda(v)+\gamma d_Q+\delta d_A=1\). Take the residual checksum \(Q'(z)=Q(z+cw)\) and residual sketch \(A'(z)=A(z+cw)\). Use the affine output map \(s=s'+\eta d_Q,\ u=u'+\eta d_A\). Under this map the proposed query equals its affine value at \(\eta=0\) plus \(\eta\). Choose \(\eta\) to force either requested answer. This choice is affine in \(z,s',u'\). The whole map is injective, since the source recovers \(z,\eta\) in the direct sum decomposition and the shifts then recover both outputs. Each residual left graph maps to the true left graph, and each residual right graph maps to the true right graph. The polar of \(Q'\) is nonsingular on \(Z\), of half-rank \(r-1\). Both children consequently cost \(2^{r-1}\) or more. The induction proves the result for all finite input dimensions.

## Exact finite replay and interpretation of the count

The finite check first puts the nonsingular polar of \(q\) into independent symplectic pairs. An input translation absorbs any linear term of \(q\) because its polar has trivial radical. A constant may remain, so both signs are tested. The same translation changes only the affine part of \(f\), and every affine part of \(f\) is tested. Symplectic coordinate generators group the polar matrices of \(f\) into classes. The code checks each generator's invertibility and its preservation of the total polar, and an independent full matrix count verifies how many eligible polars the classes represent. Full generation of the symplectic group is unnecessary, since a subgroup still partitions all the eligible matrices.

On each truth-table representative the verifier constructs the actual left and right relations, saturates by repeatedly intersecting their separately computed affine hulls, and explores all affine hyperplane queries and positive integer splits of the leaf budget. It checks that a tree one leaf below the required bound is impossible. It tests 16 represented two-input cases and 1,792 four-input cases for the free total, and 3,555,328 six-input cases for the pinned total. This includes both full-density six-input cases requiring at least four leaves. The zero-rank free inequality follows from the one-leaf minimum. These finite inductions are reproducible combinatorial certificates, with the numerical bases checked by same-task exhaustive code at V1. [Verifier](check.py), [finite base enumeration](conditional_bases.py), and [saved result](checks.json)

The corresponding parent-child cost can be uneven. For \(Q=a_1b_1+a_2b_2\), \(A=a_1a_2\), the two answers to \(u\) have exact costs three and one, respectively, as checked on the raw relations. On the 17-edge path, first expose vertices \(1,3,5,7,12,14,16\), numbering vertices from zero and edges from one. Only \(x_9x_{10}\) remains nonlinear in the even-edge report. Query the report plus its now-affine remainder. Answer one forces both of those source bits to one by the left hull. The nine fixed vertices cover every edge, making the total affine and closing that answer after eight questions. The uniform 512 counts the leaves across the whole tree.

Even an integer set cover of the honest inputs can be too small. With the four bits of \(Q=x_0x_2+x_1x_3\) numbered little-endian, three groups of inputs each fit a scalar one-leaf terminal cell.

\[
 \{0,1,2,3,4,6\},\quad \{5,6,8,9,10,11\},\quad \{6,7,12,13,14,15\}.
\]

Together they cover every input, with common point 6. The verifier checks each one-leaf statement directly. If two arbitrary Boolean private observations are allowed, they can encode the first group containing an input, giving a valid three-leaf refutation. This last control changes the number and permitted type of observations. The main theorem proves the exact count throughout the entire one-quadratic model.
