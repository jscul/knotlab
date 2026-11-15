# One visible alternating-edge sum still costs 512 terminal cases

Status: Proved

## Standard statement

On independent bits \(x_0,\ldots,x_{17}\), put
\[
 Q=\sum_{i=0}^{16}x_i x_{i+1},\qquad
 A=x_1x_2+x_3x_4+\cdots+x_{15}x_{16}.
\]
The first evaluator exposes \(s=Q,v=A\). The second exposes only \(t=Q\). Require \(s+t=1\). In a current affine case, replace each evaluator's exact relation in the case by its affine hull, intersect the two hulls, and repeat to a fixed point. A nonempty case may be split by any adaptive affine Boolean question on the inputs and all visible outputs. A refutation closes every leaf. Its **minimum number of leaves is 512 and its minimum worst-case depth is nine**.

Some legal leaves close after only eight queries. There is a 512-leaf tree with 128 leaves at depth eight, 128 at depth nine and 256 at depth ten. The lower bound counts all leaves with a probability measure, which accounts for this asymmetry. For the path on \(2k-1\) edges with the same one-sided even-edge disclosure the exact answers are \(2^k\) leaves and depth \(k\) for every \(k\ge3\).

## Nearest known result

The opposed-total theorem gives exactly \(2^{\rho(Q)}\) leaves when the totals are the only visible evaluations. Earlier one-sided mass estimates allow a factor \(2/3\) in that count, and the two-sketch analysis proves threshold estimates when both partial sums have sufficiently large rank. This proof uses the **honest private sketch but a fair total bit** to charge individual thresholds on the specified alternating pencil. The short-tree base cases use literal finite Boolean relations and every affine question. Classical results on inner-product truth sets concern other representation measures. [Opposed totals](../../TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/proof.md) · [Predecessor one-sided estimates](../../TWO-PRODUCT-SKETCHES-20261115-001B/TWO-PRODUCT-SKETCHES-20261115-001B-P001_uniform_lower/proof.md) · [Two-sketch criteria](../../TWO-PRODUCT-SKETCHES-20261115-001C/TWO-PRODUCT-SKETCHES-20261115-001C-P001_sketch_strategies/proof.md) · [Cohen–Shinkar, *The Complexity of DNF of Parities*](https://eccc.weizmann.ac.il/report/2014/099/)

## The raw pencil and two trees

Let \(\rho(f)=\tfrac12\operatorname{rank}B_f\), where \(B_f(x,y)=f(x+y)+f(x)+f(y)+f(0)\) over \(\mathbb F_2\). Group the \(2k\) inputs into even- and odd-indexed reports. In those bipartite coordinates the matrices of \(Q,A,Q+A\) are \(I+J,J,I\), with \(J\) the \(k\)-by-\(k\) lower shift. Matrix rank of a bilinear form is its polar half-rank. Thus the three half-ranks are \(k,k-1,k\). In particular at \(k=9\) the middle rank is eight. The operator \((I+J)^{-1}J\) has the same power ranks as \(J\), namely \(k,k-1,\ldots,0\): its \(i\)-th power is \(J^i(I+J)^{-i}\). It is one nilpotent Jordan block on the chosen bipartite factor. These coordinates describe the actual adjacent products.

Fix all \(k\) even-indexed inputs in a balanced tree. Every product then has a fixed factor, making \(Q\) affine, and the two totals give incompatible affine requirements in both evaluator hulls. This proves both upper bounds.

To see an early closing case on 17 edges, fix \(x_4,x_6,\ldots,x_{16}\) to zero and ask \(v=1\). The residual functions are \(A=bc,\ Q=ab+bc+cd\) on \(a,b,c,d=x_0,x_1,x_2,x_3\). The left evaluator forces \(b=c=1\) and \(Q=a+d+1\) becomes affine. The opposite total then closes the branch. On the sibling \(v=0\) ask \(b+c\). Answer zero forces both \(b=c=0\) on the left. For answer one ask \(b\), making both middle bits fixed in each answer and \(Q\) affine again. These terminal query lengths are \(1,2,3,3\) after the initial seven questions. Every one of the 128 assignments to the seven bits gives the same tree after subtracting the known affine terms of \(Q,A\) from the totals and the sketch. The relative signs of the totals are preserved. The checker verifies this affine reduction on all 262,144 original inputs and applies literal two-sided hull iteration to the four reduced terminal cases. [Raw tree replay](checks.json)

## Rank, probability and affine restriction

Write \(F\) for a quadratic on an affine input space, using any origin. Its bias is \(\mathbb E(-1)^F\). A codimension-\(c\) input restriction loses at most \(c\) units of polar half-rank by deleting rows and columns in an adapted basis. The bias has absolute value at most \(2^{-\rho(F)}\): squaring it and substituting the second input as \(x+h\) makes the inner character average vanish unless \(h\) is in the polar radical. Both truth levels of a quadratic of half-rank at least two span its domain since on every hyperplane half it still has positive half-rank. A quadratic of half-rank one is \(yz\) plus an affine function in polar-pair coordinates. A nonzero linear radical term makes both levels span the domain, as each is a graph of a nonaffine function. Without such a term, translate \(y,z\) to remove their linear terms. Exactly one level fixes both bits and has density \(1/4\); the other level spans and has density \(3/4\).

Eliminate \(t=1+s\). The ambient coordinates are \((x,s,v)\). For a queried affine case \(C\) of codimension \(d\), let \(j\) be the rank on the two output columns of its defining rows. Its input projection \(L\) has codimension \(d-j\). Gaussian elimination leaves \(j\) independent output combinations equal to affine input forms. Any affine embedding of a restricted problem whose honest left and right points map to honest left and right points can only lower the minimum number of leaves. Indeed each parent question pulls back to an affine question and each image of a restricted hull stays in the corresponding full hull at every round; this follows from monotonicity and the fact that affine maps preserve affine hulls. Restricting to the smaller problem may prune empty branches.

For \(d\le k-1\) each nonzero left pencil combination has half-rank at least \(j\) on \(L\). The case meets the actual left graph. When \(j>0\) expand its \(j\) equation indicators into characters: the constant contributes \(2^{-j}\), and each of the remaining \(2^j-1\) normalized character expectations has magnitude at most \(2^{-j}\), so their sum cannot cancel the constant. For \(j=0\) any input over \(L\) extends. The right side has one output and the same argument applies after projecting away its free sketch. Equivalently the right scalar graph meets every projected affine space of codimension at most \(k\). Thus every hyperplane half inside a case of codimension less than \(k-1\) meets each side, and each side spans the current case. At these levels saturation gives no free equations.

Remove constant questions. The tree reaches a full binary level of \(2^{k-1}\) affine cases, each of codimension \(k-1\). We determine what can happen at these cases and then charge their subtrees.

## Which cases can already close?

At \(d=k-1\), the lower bounds for the half-ranks of \(Q,A,Q+A\) on \(L\) are \(j+1,j,j+1\). Affine terms in any constraint do not change these ranks.

* **No output row (\(j=0\)).** The total and the sum \(Q+A\) remain nonaffine. A relation in the affine hull of the left graph could additionally fix \(v\) to an input affine form only if \(A\) itself has become affine. Make that definition if available. The right evaluator leaves \(v\) free, and the nonaffine scalar total gives two graphs spanning the same remaining case. If \(A\) is also nonaffine, every pencil combination is nonaffine, so the left graph itself spans all the coordinates of the case.
* **One output row pinning only \(s\).** Both total truth sets span \(L\) because \(Q\) has half-rank at least two. Over its level the left can give at most one additional equation \(v=g(x)\), since the input set spans. After this optional equation both sides span the same affine space.
* **One output row \(v+\epsilon s=l(x)\).** The right graph is the opposite scalar graph, with \(v\) recovered from the row. The left has inputs \(H=\{A+\epsilon Q+l=0\}\), with \(s=Q\). If \(H\) spans \(L\), either its graph spans \(L\) times the output bit, or else it defines \(s=g(x)\) for an affine \(g\). In the latter case the right inputs \(Q+g=1\) still span \(L\) because the half-rank is at least two. Thus both hulls stabilize. If \(H\) fails to span, the rank-one classification above forces \(\epsilon=0\) and makes \(H\) exactly a rare affine level of \(A+l\), of density \(1/4\). The case then reduces to opposite scalar graphs over \(H\). It closes immediately precisely when \(Q\) becomes affine on \(H\).
* **Both outputs pinned (\(j=2\)).** The left and right input sets are \(Z=\{q=0,f=0\}\) and \(\{q=1\}\), where \(q,f\) include the affine pins on \(s,v\). The half-ranks of \(q,f,q+f\) on \(L\) are at least \(3,2,3\). The following argument shows that the saturated case is always nonempty.

For the last assertion, the two-equation indicator expansion gives \(Z\) positive density, since \(2^{-3}+2^{-2}+2^{-3}<1\). Let \(N\) be the linear space of normals of \(\operatorname{aff}Z\) in \(L\). For each nonzero \(\ell\in N\), the complementary hyperplane half contains no point of \(Z\). There the three half-ranks are at least \(2,1,2\). The bias identity for the absent joint zero thus forces the three biases to be exactly \(-1/4,-1/2,-1/4\). In particular \(q\) has half-rank three on \(L\) and two on that hyperplane. Its polar radical on \(L\) is contained in the kernel of \(\ell\): otherwise the restriction to that hyperplane surjects onto the same nondegenerate quotient, and its rank would not drop. Hence \(\ell=B_q(z_\ell,\cdot)\). Choose the lifts \(z_\ell\) linearly on \(N\).

Translation by \(z_\ell\) preserves both hyperplane halves since \(\ell(z_\ell)=0\). On the empty half its derivative \(q(z_\ell)+q(0)+\ell(x)\) must vanish, as a constant derivative of one would make the observed bias zero. Thus for every \(x\in Z\),
\[
 \ell(x)=1+q(z_\ell)+q(0)\quad\text{for every nonzero }\ell\in N.
\]
Using this formula on two independent \(\ell_1,\ell_2\) and their sum proves \(B_q(z_{\ell_1},z_{\ell_2})=1\). Three independent normals are impossible: bilinearity would give \(B_q(z_{\ell_1},z_{\ell_2+\ell_3})=1+1=0\). If \(N\) has dimension two, its lifts span a nondegenerate polar plane. The direction space of \(\operatorname{aff}Z\) is its perpendicular complement, so restricting \(q\) to it loses exactly one unit of half-rank. A zero- or one-dimensional \(N\) also loses at most one. The half-rank of \(q\) on \(\operatorname{aff}Z\) is consequently at least two in every case. The right truth level there spans \(\operatorname{aff}Z\), as does the left by definition. Both outputs are pinned affinely, so this is a nonempty fixed case for every allowable dimension of the normal space.

We have proved that each one-leaf case on this level has just one sketch row \(v=l(x)\), and its particular honest level has density \(1/4\). The example above attains this exception.

## Heavy cases need at least three leaves

Give \(x\) its uniform distribution, take \(s\) as an independent fair bit, and set \(v=A(x)\). Call the resulting measure \(\nu\). It is used to count cases in the complete level reached before any shrinkage. It need not consist of solutions of either full evaluator.

A codimension-\(d\) case has ambient-uniform mass \(2^{-d}\). If its equations give no equation \(v=l(x)\), its \(\nu\)-mass has the same value: if the lone output row involves \(s\), its conditional probability is precisely \(1/2\) for each input. Otherwise write \(F=A+l\) and \(b=\mathbb E_L(-1)^F\). Requiring \(v=l(x)\) then has probability \((1+b)/2\) among uniform inputs in \(L\); requiring a second output equation costs exactly another \(1/2\) from the fair \(s\). In all cases
\[
 \nu(C)=2^{-d}(1+b),
\]
using \(b=0\) when no sketch equation occurs. At \(d=k-1\), an actual sketch equation has \(\rho(F|_L)\ge j\ge1\) and therefore \(|b|\le1/2\). An already closed case, as classified above, has \(b=-1/2\).

It remains to show that every cell with \(b>0\) needs at least three leaves (its saturated root and a single split cannot suffice). We reduce this statement to two finite calculations independently of input dimension or the affine terms in the restrictions.

**Common restriction lemma.** If two alternating forms have ranks at least \(2t\), there is a \(2t\)-dimensional subspace on which both are nonsingular. For each form \(B\) evaluate the multilinear alternating function of \(2t\) vectors obtained by summing the products of their \(B\)-pairings over all perfect matchings. This Pfaffian is nonzero on a tuple of \(t\) polar pairs. It is alternating since a repeated pair of arguments either pairs with itself, giving zero, or cancels upon exchanging its partners. For any tuple, it is nonzero exactly when the restricted polar matrix is nonsingular: in polar-pair coordinates of the restricted form the value on a basis is one for \(t\) pairs and zero in the presence of a radical. If two such multilinear functions are nonzero, choose the next vector outside the union of their two contraction kernels. These kernels are proper subspaces and two proper subspaces cannot cover a vector space: in the incomparable case the sum of vectors chosen in their respective differences belongs to neither. Continue until both evaluations are nonzero. The resulting tuple is independent and proves the lemma. After choosing this subspace, average the bias of \(F\) across its affine cosets. If the original bias is positive, at least one coset still has positive bias. Both polar forms on the chosen coset keep full rank.

With one output row and positive bias, the row must be \(v=l(x)\). On \(L\) the problem has left set \(F=0,\ s=q(x)\) and right set \(s=1+q(x)\), with \(q=Q|_L\). The half-ranks of \(q,q+F\) are at least two, so use the lemma with \(t=2\). On the chosen four-bit coset, a polar-pair basis and subtracting the affine part from the free \(s\) normalize \(q\) to \(x_0x_1+x_2x_3\), preserving \(\rho(q+F)=2\). Every quadratic \(F\) of positive bias on four bits for which \(q+F\) is nonsingular requires at least three leaves for these indicated sets. The direct finite verification is described below. Since the smaller affine subproblem admits all pullbacks of the original questions and exact separate hulls, its lower bound applies to \(C\).

With two output rows the problem on \(L\) has the left set \(q=F=0\) and the right set \(q=1\), with the affine pins absorbed into \(q,F\). The half-ranks of \(q,q+F\) are at least three. Apply the same lemma with \(t=3\). In six bits a nonsingular quadratic becomes \(x_0x_1+x_2x_3+x_4x_5+c\) in affine coordinates. Indeed an input translation removes any linear term since its polar matrix is invertible. Since \(s\) is pinned, both values of \(c\) are checked. For every positive-bias \(F\) with \(q+F\) nonsingular, the two indicated sets require at least three leaves. This is the second finite gate.

Now take \(d=k-1\). The subtree below any level-\(d\) case uses at least \(2(1+b)\) leaves. An already closed case has \(2(1+b)=1\). Any other case with \(b\le0\) needs at least two. If \(b>0\), the finite gates give three and \(2(1+b)\le3\). The level-\(d\) cases partition the whole initial ambient space and their \(\nu\)-masses sum to one. Summing the charges gives
\[
 L_{\mathrm{tree}}\ \ge\ \sum_C 2(1+b_C)
      =2^{d+1}\sum_C\nu(C)=2^k .
\]
The balanced scalar tree attains this count and depth \(k\); a binary tree with \(2^k\) leaves has worst depth at least \(k\). On the explicit 17-edge unbalanced tree the two sketch halves after each seven-input prefix have \(\nu\)-mass \(1/512\) and \(3/512\). They use exactly one and three leaves respectively.

## Exhaustive finite gates and replay

The four-bit checker generates *all* \(2^{11}=2{,}048\) quadratic Boolean functions from their constant, linear and square-free quadratic monomials. It eliminates those with singular \(q+F\), represents the two relations on all 32 input/output states by truth tables, and takes exact affine hulls until stable. From a surviving case it tests each of the 31 nonconstant linear query masks, including the visible total \(s\); adding a constant only exchanges the branches. No positive-bias case closes in one or two leaves. Negative-bias and zero-bias controls do admit shorter trees. [Four-bit gate](check.py)

For six bits the polar matrix of \(F\) has 15 possible above-diagonal entries. The checker visits all 32,768 masks, grouping them under verified invertible transvections preserving the total's polar matrix. These transformations give exact equivalences. A change in the affine part of \(q\) is removed by an input translation, changing at most its constant. All 64 linear parts, both constants of the transformed \(F\), and both signs of \(q\) are tested on each retained polar representative. This enumeration is complete even if the selected generators define finer classes than the full symplectic group. It discards singular \(q+F\) and zero or negative bias for \(F\). For each remaining pair it saturates the two literal truth sets and tests both answers to every nonconstant affine query on the six free coordinates. The checker records cost three as the proved lower bound whenever neither one nor two leaves suffice. Weighted by the verified equivalences, the counts by \(\rho(F)=0,1,2,3\) are respectively **2, 2,520, 249,984 and 737,280**. All pass. [Six-bit gate](pinned_six_check.py)

Run from the repository root.

    python3 -B proofs/ONE-SIDED-PATH-SKETCH-20261115-001A/ONE-SIDED-PATH-SKETCH-20261115-001A-P001_even_path/check.py

The archived JSON records both finite gates, the literal 17-edge tree, a matched consistent charge, and an example where pinning both outputs gives a proper nonempty fixed space. Pencil calculations are replayed through 23 edges, including the size immediately above the 17-edge instance. The result concerns refutation trees using the specified separate-hull rule and a fixed one-sided sketch. [Numerical certificate](checks.json)
