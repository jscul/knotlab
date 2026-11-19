# Sharp steady growth rate of the five-place branch systems

**Standard statement.** Let \(J_t\) be the number of junctions born in complete round \(t\) of a finite connected DEAD-CAP start, with \(J_t=0\) after closure. Assume every initial junction holds at most five distinctions. Under (S0), (S3), (S4) and (S6′),

\[
 \limsup_{t\to\infty}J_t^{1/t}\ \le\ \lambda=2.3829757679\ldots,
 \qquad \lambda^3=4\lambda+4.
\]

The eleven-junction theta attains the bound as an ordinary limit. Thus the maximum of the individual asymptotic rates in this class is exactly \(\lambda\).

The hypotheses require enough opens for the first round, no first-round group of three or more, at most one distinct common neighbor of any two live junctions, and at least two loose distinctions in the start. Dead junctions participate as possible common neighbors. The cap applies to the initial supports. Starts with overlapping blocks or first-round groups excluded by these hypotheses lie outside this result. [Exact class hypotheses](../../DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/proof.md#setting)

**Nearest known result.** DEAD-CAP proves the branch equations, the counting identity and the theta's own rate. The open conjecture was the uniform upper bound over its freely varying systems. The proof below bounds each oriented branch at one common argument, including branches terminating in spares or a ray. [DEAD-CAP, Lemma 1 and Theorems 3–4](../../DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/proof.md) · [Recorded conjecture](../../../research/DEAD-CAP-20261119-001/dead_cap.md)

## What the cap permits

For a live point \(q\), let \(s_q\) be its number of opens in excess of its first-round demand \(d_q\). Its profile lists the sizes of the blocks containing it. DEAD-CAP proves

\[
 d_q=\sum_{D\ni q}(|D|-1),\qquad
 s_q+\sum_{D\ni q}|D|\le5.
\]

The possible profiles are empty, \(\{2\},\{3\},\{4\},\{5\},\{2,2\},\{2,3\}\). Each excess open gives one pendant. With at least three opens it is a spare with factor \(1+z\). With two opens it has one ray and factor \((1-z)^{-1}\). With one open it has two rays and factor \(1+z/(1-z)^2\). Their product is \(e_q(z)\). The two-ray case can occur only at a point in no block. For a block \(D\) entered at \(p\), the oriented branch series is

\[
 b_{p,D}(z)=\prod_{q\in D\setminus\{p\}}
  \left(1+z\, e_q(z)\prod_{F\ni q,\ F\ne D}b_{q,F}(z)\right).
\]

Its coefficients are nonnegative. Starting every branch at 1 and substituting the equation successively gives increasing series, agreeing with the unique formal solution to one more degree at each substitution.

## A uniform bound at the theta's critical argument

Let \(r=1/\lambda\) be the positive solution of \(4r^2(1+r)=1\). It lies strictly between 0 and \(1/2\). Set

\[
 U=\frac1{2r^2}=2(1+r),\qquad B=U^2,\qquad A=1+r B=2+1/r.
\]

Then \(1+rA=U\), so \(B=(1+rA)^2\). We will bound every branch through a two-point block by \(A\) at \(r\), and every branch through a three-point block by \(B\). The only mixed inequality requiring slack is

\[
 (1+r)A<B.
\]

Indeed, \(B-(1+r)A=(1+r)(2+4r-1/r)\), and \(2r+4r^2-1=r(1+2r)/(1+r)>0\). Also \(A>4\) and \(B>4\).

In one substitution, suppose the branch bounds hold for the previous iterate. For each other point \(q\) of the entered block \(D\), let \(E\) denote \(e_q(r)\) times the product over its other blocks. The following table gives every possibility involving two- or three-point blocks.

| Entered block \(D\) | Profile of \(q\) | Bound on \(E\) |
| --- | --- | --- |
| Three points | \(\{3\}\) | At most two spares, hence \(E\le(1+r)^2<A\). At two opens the demand uses both. |
| Three points | \(\{2,3\}\) | No pendants. The other block has two points, so \(E\le A\). |
| Two points | \(\{2,3\}\) | No pendants. The other block has three points, so \(E\le B\). |
| Two points | \(\{2,2\}\) | At most one spare. The other block has two points, so \(E\le(1+r)A<B\). |
| Two points | \(\{2\}\) | One open leaves nothing; two opens leave one one-ray pendant; three or four opens leave two or three spares. Thus \(E\le\max\{(1-r)^{-1},(1+r)^3\}<4<B\). |

A two-point branch has one factor and is at most \(1+rB=A\). A three-point branch has two factors and is at most \((1+rA)^2=B\). This includes both directions across a point of profile \(\{2,3\}\). The initial iterate 1 obeys the bounds, so they hold at every depth. Monotone convergence applied to the nonnegative coefficients yields the same finite upper bounds for the complete series at \(r\).

Every point of a four- or five-point block has that block as its whole profile, so the branch equations there contain no other branch variables. Pendants at these points give finite factors at \(r\). Points in no block have only their own pendant structure. Thus all oriented branches and all unmarked or marked pendant factors are finite at \(r<1\), in every piece of the start.

## Passing from branches to junction counts

For each point \(p\), DEAD-CAP's marked pendant factor \(e_p^+\) accounts for a marked point in its pendant structure or \(p\) itself. Its terms are finite at every real \(z\in(0,1)\). Consequently

\[
 P(r)=\sum_p r\,e_p^+(r)\prod_{D\ni p}b_{p,D}(r)<\infty.
\]

The pointing identity for \(t\ge1\) gives \((t+1)J_t^\circ=[z^{t+1}]P(z)\) for the births counted by the branches. A finite piece of size \(m\) with a relay adds \(k\) births at \(t=m-1+k\). There are finitely many pieces, so the relay contributions also satisfy \(\sum_{t\ge1}(t+1)J_t^{\rm relay}r^{t+1}<\infty\). Hence for the actual counts

\[
 \sum_{t\ge1}(t+1)J_t r^{t+1}<\infty.
\]

In particular \(\limsup J_t^{1/t}\le1/r\). The argument includes closing pieces, pieces with rays and periodic cores, with the multiplicative constants free to depend on the start.

## Attainment and the scope of the comparison

The theta's rank-two piece has six points of profile \(\{2,3\}\), no pendants, two three-point blocks and three two-point blocks. Its physical realization uses two dead three-place hubs, six five-place junctions and three three-place connectors. Write \(a(z)\) for its common branch through a two-point block and \(b(z)\) for its branch through a three-point block. The two orientations give \(a=1+zb\) and \(b=(1+za)^2\). Then \(u=1+za\) has nonnegative coefficients, is finite at \(r\), and obeys

\[
 u=1+z+z^2u^2.
\]

At \(r\) this quadratic has the double root \(u(r)=1/(2r^2)\). If the radius exceeded \(r\), differentiation there would give \((1-2r^2 u(r))u'(r)=1+2r u(r)^2>0\), although the left side is zero. Thus the radius of \(u\) is exactly \(r\).

One can also read the full limit directly. Put \(u_j=[z^j]u\). All \(u_j\) are positive and \(u_{i+j+2}\ge u_i u_j\). Hence \(d_n=u_{n-2}\) satisfies \(d_{n+m}\ge d_n d_m\) for \(m,n\ge2\). For fixed \(m\ge2\), write any sufficiently large \(n=km+j\), \(2\le j\le m+1\). Then \(d_n\ge d_m^k d_j\), giving \(\liminf d_n^{1/n}\ge d_m^{1/m}\). Taking the supremum over \(m\) and using the radius gives \(\lim u_j^{1/j}=1/r\). A theta point contributes \(zab\) to \(P\). Since \(b\) has constant term 1, the coefficient at \(t+1\) is at least \([z^{t+1}]za=u_{t+1}\). The pointing divisor \(t+1\) preserves the exponential rate. This gives \(\lim J_t^{1/t}=1/r\) for the theta itself. [Theta realization and equations](../../DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/proof.md#corollary-5-what-occurs-within-five-places)

The oriented series need not be bounded coefficient by coefficient by the theta's. For example, take a dead three-place hub meeting three five-place leaves, each with four opens. The leaves form a single held three-point block. There is no shortage, no valid triple and only one common neighbor per live pair. Each leaf has two spares. A branch through the block is \((1+z(1+z)^2)^2\), with coefficient 5 at \(z^2\). The corresponding theta series \((1+za)^2\) has coefficient 3. The critical-argument bound proved above accommodates this difference.
