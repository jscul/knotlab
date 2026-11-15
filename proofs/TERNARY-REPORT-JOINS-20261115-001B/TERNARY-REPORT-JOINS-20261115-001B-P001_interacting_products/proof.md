# How sharing a report changes the exact number of affine pieces

Status: Proved

## Standard statement

Let \(G\) be a supplied finite simple undirected graph on \(n\) independent Boolean reports \(R_i\). Over \(\mathbb F_2\), display \(P_{ij}=R_iR_j\) for each edge and the checksum \(T=\sum_{ij\in E}P_{ij}\). A nonempty affine piece is a solution set of affine equations in the displayed coordinates. A cover can use overlapping pieces. A partition uses disjoint pieces. The minimum size is the same for both.

* Keeping all \(P_{ij}\) and \(T\) requires exactly \(2^{\tau(G)}\) pieces, where \(\tau(G)\) is the minimum vertex-cover size. Keeping only \(R,T\) requires exactly \(2^{\operatorname{rank}_{2} A_G/2}\), where \(A_G\) is the adjacency matrix.
* With \(m\ge1\) checks and \(n=m+1\) reports the star takes **two** pieces and the path takes **\(2^{\lfloor n/2\rfloor}\)**, in either display. In a tree of binary affine queries ending with one affine system per leaf, these are the exact minimum leaf counts. The minimum worst-case depths are respectively \(1\) and \(\lfloor n/2\rfloor\).
* On **any** \(G\), satisfiability with arbitrary affine equations on \(R,T\) and independent free bits admits a deterministic polynomial-time witness algorithm. On a star this also holds for equations involving individual \(P_{ij}\). On paths of growing length the decision problem with arbitrary affine equations involving the individual products is NP-complete. A reduction with two selected path products per three-literal clause preserves each satisfying original assignment and gives it a unique extension.
* For arbitrary \(G\) and arbitrary affine restrictions on the full display, let \(k\) be the rank of their individual-product coefficients after substituting \(T=\sum P_e\). The exact number of assignments is computable in \(2^k\operatorname{poly}(\text{input length})\) bit operations. This includes the dependent rows left over when the product coefficients cancel.

Bit coordinates, graph vertices and every input equation are supplied explicitly. The representation measure concerns a relation on **all** its allowed states. The decision and counting algorithms are separate statements about a supplied restriction of that relation.

## Nearest known result

Quadratic Boolean normal forms and restriction to affine subspaces are classical. Mirwald and Schnorr identify half the rank of an associated matrix with a different measure, the minimum number of AND gates for a scalar quadratic function. Cohen and Shinkar give the exact number \(2^{n/2}-1\) of affine terms in a DNF of parities accepting the one-inputs of inner product on \(n\) bits. Here both Boolean outputs occur in the graph of a function, and retaining the individual edge products changes the optimal exponent for some graphs. The proofs below derive both graph formulas directly. [Mirwald–Schnorr, *The multiplicative complexity of quadratic boolean forms*](https://www.sciencedirect.com/science/article/pii/0304397592902358) · [Cohen–Shinkar, *The Complexity of DNF of Parities*](https://eccc.weizmann.ac.il/report/2014/099/)

The prior report construction prescribed differences of freely realizable outputs \(F_i=z_i(x_i y_i+ab)\). The present constraints multiply pairs of those outputs and expose their checksum. The classical NP-completeness of 3-SAT supplies the usual terminology for the explicit equivalence and membership proof below. [Original report construction](../../SHARED-REPORT-CANCELLATION-20261115-001A/SHARED-REPORT-CANCELLATION-20261115-001A-P001_strict_checks/proof.md) · [Garey–Johnson, Theorem 3.1](https://perso.limos.fr/~palafour/PAPERS/PDF/Garey-Johnson79.pdf)

## The displayed coordinates and the raw reports

Every \(R\in\mathbb F_2^n\) has exactly one displayed product vector and total. Star checks share the center report in every pair. On the path, consecutive checks share one report and nonconsecutive checks have disjoint report coordinates. Both families are connected in the supplied graph. If all reports use the earlier \(F_i\), even distant checks mention the same raw \(a,b\). For each *fixed* \(a,b\), the choices \(x_i=1,\ y_i=1+ab,\ z_i=R_i\) realize every report vector simultaneously and give an affine section of the raw-to-report map. Existential raw inputs without further restrictions therefore preserve the decision answers. The section also preserves a report-graph lower bound after restriction and projection of any exact affine description of the full raw evaluator.

The two exact upper bounds describe the chosen display and its product with any number of genuinely independent free bits. Raw providers or private clause witnesses can have constrained fibres. An arbitrary extra binding such as \(w=uv\), using two new unrestricted inputs, can increase the affine-cover number. One single-edge graph plus this independent product already requires four pieces by the full-product theorem applied to two disjoint edges.

## Keeping the individual products

Write the graph of the simultaneous evaluation as \(\Gamma\). Projection of any affine piece \(D\subseteq\Gamma\) onto the reports gives an affine coset \(a+V\). Without auxiliary coordinates projection is one-to-one, and the inverse of this affine bijection is affine. Each displayed product must therefore be affine on \(a+V\). If extra witness coordinates are allowed, project them away first. Linear projection preserves affine sets, including when many witnesses represent one assignment.

Let \(\ell_i\in V^*\) be the linear part of report \(R_i\) on this coset. The product \(R_iR_j\) is affine precisely when \(\ell_i,\ell_j\) are dependent. For independent slopes choose directions whose pairs of values are \((1,0)\) and \((0,1)\). The four corresponding evaluations have XOR one, which fails the affine identity. For dependent slopes either one is zero or both are the same functional. In the latter case the Boolean evaluation identity \(\ell^2=\ell\) removes the degree-two term. This identity refers to functions of Boolean inputs.

The coordinate restrictions span \(V^*\) since a vector annihilated by every coordinate is zero. Select a basis from the coordinate restrictions. Its vertices form an independent vertex set, as an edge between two chosen vertices would have independent slopes. Thus \(\dim V\le\alpha(G)\), the maximum independent-set size. Each affine piece can cover at most \(2^{\alpha(G)}\) of the \(2^n\) reports. The same count holds for an overlapping cover. Conversely fix each report in a minimum vertex cover to a chosen bit. Each product then has a constant factor on the cell, and its total is affine. The \(2^{\tau(G)}\) settings partition the whole graph. Taking complements in the vertex set gives \(\alpha(G)+\tau(G)=n\), so the bounds meet. Appending the total \(T=\sum P_e\) adds an affine coordinate.

## Keeping only the total

Set \(Q(R)=\sum_{ij\in E}R_i R_j\). Its polar form
\[
 B(x,y)=Q(x+y)+Q(x)+Q(y)+Q(0)=x^\top A_G y
\]
is alternating. On a coset \(a+V\), the four-point differences of \(Q\) are \(B(v,w)\) for \(v,w\in V\). Thus \(Q\) is affine on that coset exactly when \(B\) vanishes on \(V\times V\), since its translate by its value at the origin of the coset then preserves addition.

Write \(\operatorname{rank}B=2r\). Indeed any nonzero alternating form admits \(h,k\) with \(B(h,k)=1\). Their span is a nondegenerate two-dimensional summand. Subtracting \(B(x,k)h+B(x,h)k\) sends any vector \(x\) into its orthogonal complement. Iterate to leave the radical of dimension \(n-2r\). Modulo the radical, the image of an isotropic \(V\) lies in its own orthogonal complement, hence has dimension at most \(r\). Therefore \(\dim V\le n-r\). Taking the radical and one vector from each such pair attains this dimension. The \(2^r\) cosets of that subspace partition the graph of the total into affine pieces, and point counting gives the same lower bound for a cover.

For a star with \(m\ge1\), \(Q=R_0(R_1+\cdots+R_m)\) has polar rank two. For a path numbered \(0,\ldots,n-1\), its kernel equations are \(v_1=0,\ v_{i+1}=v_{i-1}\) for \(0<i<n-1\), and \(v_{n-2}=0\) when \(n\ge2\). All odd-indexed coordinates vanish and all even-indexed coordinates agree. An even \(n\) also forces those even-indexed coordinates to vanish. The rank is \(2\lfloor n/2\rfloor\). The odd-indexed reports are a vertex cover of size \(\lfloor n/2\rfloor\), and the disjoint edges \((0,1),(2,3),\ldots\) require at least that many vertices in a cover. Both displays consequently have the stated optima for stars and paths. The complete graph on three reports distinguishes the two graph formulas: vertex-cover size two, polar rank two, hence four pieces for all products and two for the total.

## Affine queries and the first separating example

A binary query can inspect any affine parity of the displayed reports, products, total or free witnesses. On each branch the accumulated query answers and one terminal linear system must describe precisely the accepted states there. Every nonempty terminal set is affine, and all accepted reports are covered, even if witnesses are existentially hidden. The cover lower bound therefore applies. A tree of depth \(d\) has at most \(2^d\) leaves. Asking the cover coordinates, or a basis of the coset-label functionals for the scalar theorem, reaches the bound with a fixed set of queries. Appending arbitrary independent free bits preserves the bounds by projection and by taking products of the optimal pieces with the full witness space. This reasoning also applies to the number of accepting affine leaves of a verifier, while the stated optimal *total* leaf count allows one affine feasibility test at each leaf.

| Product checks \(m\) | Reports \(n\) | Star pieces / depth | Path pieces / depth |
|---:|---:|---:|---:|
| 1 | 2 | 2 / 1 | 2 / 1 |
| 2 | 3 | 2 / 1 | 2 / 1 |
| 3 | 4 | 2 / 1 | 4 / 2 |
| 4 | 5 | 2 / 1 | 4 / 2 |
| 7 | 8 | 2 / 1 | 16 / 4 |
| 16 | 17 | 2 / 1 | 256 / 8 |
| 64 | 65 | 2 / 1 | 4,294,967,296 / 32 |

With four reports, pin \((R_1,R_3)=(s,t)\). The three path products are \(sR_0,sR_2,tR_2\). In cells \(00,01,10,11\), the respective checksums are \(0,R_2,R_0+R_2,R_0\). Each cell contains four report assignments. The star still uses just its center bit. Zero checks give one affine piece.

Returning the bit \(T\) on an already-promised graph is another query specification. On the single product \(T=R_0R_1\) with report queries and constant-bit outputs, the sole one-input forces a singleton leaf and the three zero-inputs cannot form one affine set. Three leaves of depth at most two suffice. A direct query to a supplied valid \(T\) computes that bit in one question on every nonempty path. The checker independently optimizes all allowed binary parity splits for both specifications, including a case with an extra free bit. [Exact finite readouts](checks.json)

## Deciding one linearly restricted checksum

Supply affine equations on \((R,T,W)\), with \(W\) a tuple of free bits. Gaussian elimination either detects an incompatible row or parameterizes their joint solutions as \(v(u)=a+\sum_{i=1}^s u_i b_i\) with independent directions. Substitute in the single residual
\[
 D(u)=T(v(u))+Q(R(v(u))).
\]
This is a Boolean function of degree at most two. Its unique square-free expression has constant \(D(0)\), coefficients \(D(e_i)+D(0)\), and pair coefficients \(D(e_i+e_j)+D(e_i)+D(e_j)+D(0)\). These formulas follow by evaluating the square-free expression at those points. If all \(1+s+\binom{s}{2}\) evaluations are one, the residual is identically one and the instance is unsatisfiable. Otherwise the first zero gives an actual witness, including every product and \(W\). Gaussian elimination, these polynomially many graph evaluations, and witness recovery take polynomial bit-work. This argument holds for any single supplied Boolean quadratic that can be evaluated in polynomial time.

Both the pair evaluations and Boolean square reduction matter. For \(T=R_0R_1\) pinned to one, the zero report and both unit reports fail, and \((1,1)\) succeeds. With \(R_1=R_0\) and \(T=R_0+1\) the residual becomes \(u^2+u+1\), identically one on bits.

For a matched family, on the path with \(n=2j+1\) impose \(R_i=R_{2j-i}\) for \(0\le i<j\). Distinct reflected edges occur in pairs, so \(T=0\). Changing only the pin from \(T=0\) to \(T=1\) changes SAT to UNSAT. All \(j+1\) free reports survive on the satisfiable side. The product list contains their \(j\) consecutive products followed by the same list reversed. Duplicating coordinates gives an affine isomorphism with the \(j\)-edge path display on \(j+1\) reports, so describing all these products still needs \(2^{\lfloor(j+1)/2\rfloor}\) pieces. At \(j=32\) this is 65,536 pieces, whereas the single residual on the unsatisfiable side is certified by 562 evaluations. The negative instance has empty solution set. The lower bound here concerns the full separate-product display on its matched positive side.

## Several independently restricted product sums

Now supply arbitrary affine rows on \((R,P,T,W)\). Replace \(T\) in every row by \(\sum_e P_e\). Each row then consists of a product-coefficient vector, an affine form on \(R,W\), and a right-hand side. Gaussian-eliminate the product columns, carrying the entire row along. The \(k\) independent product rows remain. Every row whose product part has disappeared constrains \(R,W\), possibly by \(0=1\). For example \(P_{01}=0,\ P_{01}=1\) has product rank one and leaves an incompatible affine row. Solve these affine rows and substitute their Gaussian parameterization into the remaining rows and their product definitions. This gives \(k\) Boolean quadratics \(h_i(u)\) on \(s\) free bits. The parameterization is injective and each \(R,W\) gives exactly one \(P,T\).

For any Boolean \(z\), the indicator of \(z=0\) equals \((1+(-1)^z)/2\). Multiplying this identity and summing over \(u\) gives the number of full graph assignments as
\[
 2^{-k}\sum_{\lambda\in\mathbb F_2^k} S\left(\sum_i\lambda_i h_i\right),
 \qquad S(f)=\sum_{u\in\mathbb F_2^s}(-1)^{f(u)}.
\]
To compute each scalar sum, recover its square-free coefficients from weights at most two. When a product \(xy\) has coefficient one, write \(f=xy+xA(z)+yB(z)+C(z)\), with \(A,B\) affine. Direct summation over \(x,y\) gives \(S(f)=2S(C+AB)\). The remaining polynomial is again quadratic after Boolean square reduction. An affine remainder with nonzero linear part has sum zero by pairing opposite inputs. A constant remainder \(c\) on \(d\) remaining inputs has sum \((-1)^c2^d\). This proves the algorithm and its \(2^k\operatorname{poly}(\text{input length})\) bound, including integer arithmetic since partial sums need \(O(s+k+1)\) bits. If a witness is wanted, successively pin bits of \(R,W\) to any value with positive count. Those affine-only pins preserve the bound on \(k\).

For stars an even shorter argument handles arbitrary product rows with growing \(k\). Split on the center \(R_0=c\), replace each \(P_{0i}\) by \(cR_i\), and use \(T=\sum_i P_{0i}\). Both branches are linear systems. A consistent branch gives all the coordinates of a satisfying assignment in polynomial time.

## A 3-SAT instance on a single fixed path shape

Allow the restriction to mention the products of specific consecutive reports on the path. Let a source formula have \(v\) original variables and \(h\) clauses of three signed literals. Start the path with \(v\) reports for the original variables. Allocate four more consecutive reports \(A,B,C,D\) per clause. For its three literals let \(f_1,f_2,f_3\) be their falsity bits, with \(1+X\) for a positive occurrence and \(X\) for a negative occurrence. Supply exactly five affine rows per clause,
\[
  A=f_1,\qquad B=f_2,\qquad D=f_3,\qquad C=P_{AB},\qquad P_{CD}=0.
\]
Every consecutive pair on the whole path still has its defined product. The path products joining the original reports, the clause gadgets, and \(B\) to \(C\) occur only in the unrestricted total. In particular \(P_{AB}\) and \(P_{CD}\) lie on disjoint edges. An original assignment determines \(A,B,D\), then \(P_{AB}=f_1f_2\) and \(C=f_1f_2\). The last pin holds exactly when \(f_1f_2f_3=0\), which is exactly satisfaction of that clause. Conversely any full solution reads back a satisfying original assignment by these same five equations in every clause. Given satisfying originals all remaining reports, all path products and \(T\) are uniquely determined.

There are \(v+4h\) reports, \(\max(0,v+4h-1)\) consecutive products, and \(5h\) affine rows of width at most two. The sparse reduction uses \(O(v+h)\) coordinate names, row entries and word operations, or \(O((v+h)\log(v+h+2))\) bits to write explicit indices. The target instance supplies an explicit path roster. Guess its reports, compute the products and total and verify the linear rows in polynomial time. This establishes NP membership and, with the reduction, NP-completeness for this input model. The number of allowed original assignments is preserved as well. The window forming the product equations stays on the path while the supplied affine rows can relate distant indices.

For a concrete matched pair, take three variables and the eight clauses of all sign patterns. Each forbids exactly one assignment and together they forbid all eight. Replace the all-positive clause by a second copy of another sign pattern. The unique solution of the new formula is \(000\). Both encoded instances have 35 reports, 34 path products and 40 additional affine rows. A broken gadget that omits \(C=P_{AB}\) already accepts \(000\) for one all-positive clause by taking \(A=B=D=1,\ C=0\). This control distinguishes the real composite product check from two unrelated ANDs.

## Replay and certificate

Run from the repository root.

    python3 -B proofs/TERNARY-REPORT-JOINS-20261115-001B/TERNARY-REPORT-JOINS-20261115-001B-P001_interacting_products/check.py

The executable checker compares its own result with the saved JSON. For all 76 labelled simple graphs with at most four reports it compares the algebraic bounds with all affine point sets, testing the four-point equations separately for the scalar and simultaneous outputs. A disjoint-cover search additionally recovers the exact partitions on the selected small graphs. The two five-report controls each examine all 2,451 nonempty affine point sets. Separate dynamic programming tries all permitted parity queries on the small displays. Restriction tests cover 2,572 graph-and-affine-set pairs, 336 more random instances with free coordinates, and all 2,198 Boolean quadratics through four variables for the scalar sums. The complete counter is checked on 420 full-coordinate instances. Direct enumeration of the 3-SAT reduction examines 132,104 full report assignments across 73 source formulas. The four-report cell list, growing exact counts, constructive witnesses, reflected negative instances and broken-wire control are recorded in the replay output. [Reproducible checker](check.py) · [Numerical certificate](checks.json)

The public functions are available in the adjacent module. All bit masks use bit zero for the first report. Each pair \((\mathrm{mask},b)\) imposes parity of the selected bits equal to \(b\). The restricted single-checksum interface orders bits \(R,T,W\). The full-coordinate interfaces order them \(R,P,T,W\), with products in the given edge order. [Solver and reduction](solver.py)

| Entry point | Output |
|---|---|
| \(\texttt{polar_rank(n, edges)}\) | Rank over \(\mathbb F_2\) of the graph's alternating form |
| \(\texttt{decide(n, edges, restrictions, free_witnesses=0)}\) | SAT with all recovered coordinates, or an inconsistency reason and the tested residual size |
| \(\texttt{decide_star(n, restrictions, free_witnesses=0)}\) | Full-star SAT with a packed witness or UNSAT |
| \(\texttt{count_product_rows(n, edges, restrictions, free_witnesses=0)}\) | Exact model count, product-coefficient rank and number of scalar sums |
| \(\texttt{reduce_3cnf(v, clauses)}\) | Explicit path and sparse affine rows, represented as pairs of coordinate-index tuples and right-hand sides |
| \(\texttt{extend_3cnf(instance, original)}\) | Unique ambient point satisfying the wiring before testing the final product pins |
