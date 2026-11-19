# How the required reading order grows

Let $J$ count ordinary junctions at the observed positive-age stage and $n$ its literal binary distinctions. $K(T)$ is the least cardinality of a genuine bond containing every distinction in $T$, with infinity for an absent bond. The comparison always uses one specified permutation fixing each distinction at every live junction. An old-only failure persists under every renaming of later distinctions.

## A fixed next pair can require order proportional to $J^{2/3}$

For every sufficiently large $r$ there is a first reached stage with $J=\Theta(r^{3/2})$ ordinary junctions and $n=\Theta(r^2)$ distinctions. It preserves all current readings through $r$ under the indicated renaming, while two old distinctions and their image have different readings at the next complete round. This gives necessary orders $\Omega(J^{2/3})$ and $\Omega(\sqrt n)$ respectively. The starts allow repeated ordinary meetings. The section on sparse shields below proves matching upper bounds for this particular mechanism.

**A branch of present price $m^2$ on $8m-1$ ordinary sites besides its root.** Take $m=2^d-1$, $d\ge4$. Index $i,j$ by the nonzero vectors of $\mathbf F_2^d$. The scalar product here only specifies a finite list of ordinary incidences. The growth rule receives their resulting parity stars.

At one shield root $H$ introduce $m-1$ live sites $A_t$, two live sites $b_{i,0},b_{i,1}$ per $i$, and a private live site $z_j$ per $j$. Join $H$ to each $A_t$ by $m$ distinct names and to every $b$ by one. For each $j$ introduce two older, exhausted sites meeting $z_j$. The first also meets all the $A_t$. The second meets precisely the $b_{i,\langle i,j\rangle}$ with $i\ne j$. Give each initially live site exactly one separate loose name per occurrence in the following first-round groups:

$$
X_j=\{z_j\}\cup\{A_t:\text{all }t\}\cup
       \{b_{i,\langle i,j\rangle}:i\ne j\},
\qquad Y_i=\{b_{i,0},b_{i,1}\}.
$$

To verify the groups, all $A,b$ sites have common neighbor $H$. Each $z_j$ has only its two private neighbors, so the maximal candidate cliques are the full $A,b$ set and the individual $X_j$. The former is backed and each $X_j$ is unbacked. For different $i,k$, each of the four dot-product patterns occurs $2^{d-2}$ times before omitting $j=0,i,k$. At least one witness of every pattern survives. Thus every pair of base sites is covered by some $X_j$ except $b_{i,0},b_{i,1}$ for the same $i$. These remaining pairs grow as $Y_i$. There are no offshoots.

At age one all $X_j$ share each $A_t$. The $Y_i$ have disjoint parent sets, and $Y_i$ has candidate relation with $X_j$ exactly for $j\ne i$. Consequently the full $X$ clique is backed. The $m$ other maximal cliques

$$
G_i=\{Y_i\}\cup\{X_j:j\ne i\}
$$

are unbacked, since neither $b_{i,0}$ nor $b_{i,1}$ is used by all $X_j$, $j\ne i$. Every candidate pair is covered by a $G_i$, including any pair of different $X$ sites since $m\ge3$. The demand at the birth of $X_j$ is therefore $m-1$, and the demand at $Y_i$ is one. Their fresh counts are exactly those demands. At age two all pairs $G_i,G_k$ share some $X_j$ with $j\ne i,k$, yet no old parent belongs to every $G_i$. The sole group in this branch is the full set of $m$ sites. Each $G_i$ consequently receives one fresh distinction. Its successor, the single cap, also has one fresh distinction. With at least two branches in the connected source no group consumes every global loose distinction. The fewest count at a nonimplied junction with $p$ parents and demand $q$ is $\max(q,3-p,1)$, giving exactly the counts above. No two live sites from different branches have a common parent. [Complete round rule](../EXTEND-ROUND-20261119-001/extend_round.md)

At age one route $m(m-1)$ disjoint paths through $H,A_t,X_j,O$, using one different root copy for each $j$ and a distinct loose name at $X_j$ for each $t$. Another $m$ use $H,b_{i,0},Y_i,O$. These account for all $m^2$ branch loose names. At age two use $H,b_{i,0},Y_i,G_i,O$ for $m$ disjoint paths, and all $m$ fresh names form a separating cut. At age three there is one path and one final loose name. The respective prices are exactly $m^2,m,1$.

All starting stars have size at least three. Deleting $H$ leaves every initial $A,b,z$ connected upwards to the exterior by a loose name or its successors. Each older private site meets such sites. At later ages every $X$ or $Y$ meets some $G$ and every $G$ meets the cap when that level exists. Deletion of another ordinary vertex leaves the $A,b$ attached to $H$. Each $z$ has two routes to these through its distinct private neighbors. Each private site meets several different $A$ or $b$, and each new site has at least two distinct parents with the stated downward routes. Thus a deletion away from $H$ leaves downward connections to $H$, and another branch connects the core to the exterior. The unchanged full core survives any one ordinary deletion using its remaining anchors, middles and shields. Every ordinary star is therefore a genuine bond. A single distinction cannot disconnect the graph either. A bridge at an ordinary endpoint would make that endpoint a cut vertex or leave it with degree one. Both alternatives have been excluded, so every distinction is on a cycle. Reversing the values along that cycle gives the distinction its other value at any solution. The literal replay checks both deletion properties.

**Insertion into the known core.** Use $I=r-1$, $s=4(r+2)$, $L=sr$ from the predecessor. Choose the least $m=2^d-1\ge\sqrt{8s}$ with $d\ge4$ and set $M=m^2$. Each of the $2s$ shield middles receives its own branch and has $M$ ordinary distinctions to its hub. The present proof in the predecessor identified the hubs and the outside. Their separating cost is at least $sM$. Every set of at most $r$ marked core links has a bond in the identified graph costing at most

$$
4L+2s+(I-1)(2s+4)+4(2L+I-1)+(r+1)(2M+I).
$$

At $M=8s$ this bound is strictly below $sM$. Increasing $M$ increases the threshold faster than the bound because $s>2(r+1)$. Hence the complete present readings through $r$ match. A marked branch contributes its own least separating cost through its marks in place of the virtual cost, identically on both sides. All live names and all names inside the branches are fixed. [Marked-component proof and two-terminal lifting](../LATER-BOND-READING-20261119-001/constructive-proof.md)

At the next round isolating the red hub together with all red shields costs $2L+s(I+m)$ and crosses the two red test spokes. The exchanged pair requires at least $4L$ on two edge-disjoint test circuits. For instance $r\ge256$ gives $m<2\sqrt{8s}+1<r+1$, so $I+m<2r$ and the first cost is strictly smaller. These are two ordinary old names.

The core has $I+6+2s$ ordinary sites. Each branch adds $6m-1$ starting sites and $2m$ first-round sites. Thus $J=I+6+16sm=\Theta(r^{3/2})$ at observation. Each branch contributes $3m^2+m$ starting ordinary links, $2m^2+m$ starting loose names and $m^2$ first-round fresh names, giving $6m^2+2m$ literal distinctions besides the core. The core itself uses $4(2L+I-1)+2s(M+I)$ names. Therefore $n=\Theta(r^2)$. The archived maximal-group and GF(2) verifier reproduces all three rounds in two-branch controls. Independent cut calculations in each literal branch give $225,15,1$ when $m=15$, and $961,31,1$ when $m=31$. The controls have respectively 119 and 247 age-one sites per branch, excluding its root. [Literal group and flow replay](../../experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/scale_square_branch.py) · [Measured counts and prices](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/scale_square_branch.json)

## A linear lower bound in junctions for retaining the same order

For every $r\ge2$, there is a reached stage with at most $137r+280$ ordinary junctions on which the permutation preserves every reading through $r$. One complete round later it still preserves every reading through $r-1$ on the identity extension to fresh names. An immutable $r$-set has a different reading. The source has $\Theta(r^2)$ literal distinctions, and admits ordinary junctions that meet more than once.

Take the weighted core of the predecessor's sharp hierarchy. Its $I=r-1$ ordinary anchors, two hubs, four test middles, $s=4(r+2)$ shield middles per hub, test weights $L=sr$ and hub-to-shield weights $M=8s$ are fixed. The exchange interchanges two test middles at different hubs and fixes all shields. Give the shield-to-outside links prices $M$. The predecessor proves that all readings through $r$ agree. If every price becomes one, the two red test spokes and their image have different readings. For these compressed graphs a mark specifies a link type. Multiple names in a parallel bundle force its same crossing. [Parameter family and current and later bounds](../LATER-BOND-READING-20261119-001/constructive-proof.md)

Lower the $2s$ shield prices individually from $M$ to one, in a fixed order. Let $e$ be the first change for which equality through order $r$ fails. Existence follows from the endpoints. If a query contains $e$, the cost of every admissible bond through it decreases by exactly $M-1$ in both readings. Such a query cannot first fail at this change. A failing compressed query therefore consists entirely of other link types.

**Literal one-round realization.** Treat the former outside vertex as an ordinary core junction. Keep every link other than $e$ at its current price, using that many parallel ordinary distinctions. Remove $e$ and attach two copies of the predecessor's linear-size branch, one at each of its two ordinary poles. Their only common vertex is now the actual wired outside. Together they constitute a two-terminal piece $Q$. Each branch has separating price $M$ at age one and one at age two. The two consecutive branches in $Q$ hence have joint separating price $M$ and then one. Both branches have loose distinctions, so neither new cap takes all loose distinctions of the connected source. The ordinary core connects the two poles after deletion of $e$. Deletion of a core junction leaves the rest connected by the remaining shields, middles and anchors. The branch deletion argument from the predecessor applies when either pole or an internal branch junction is removed. All starting stars are genuine. [Compact two-round branch](../LATER-BOND-READING-20261119-001/constructive-proof.md)

For a mixed current query, its marks in $Q$ require a connected separating cut there. Replace those marks by $e$ in the host and add the least separating cost through the marks minus $M$. Both sides of the permutation have exactly the same surcharge, including infinity. A query wholly inside $Q$ is fixed. A query wholly in the host uses the usual cost-$M$ substitution. This proves the full literal current matching. The failed new query avoids $e$, so choose one direct old name per type. Its age-two reading is exactly the new compressed reading. All its names were already fixed by the old permutation or have their specified old images.

For completeness, one price change preserves all orders below $r$ at every subsequent stage confined to $Q$ on the identity extension. For a host query $X$, write $A(X)$ for its least cost with $e$ uncut and $B(X)$ for the least host cost, excluding $e$, when $e$ crosses. The present reading is $\min(A(X),B(X)+M)$ and the marked reading on $X\cup\{e\}$ is $B(X)+M$. When $|X|\le r-1$ both values transfer. At new price $q\le M$ its reading is the smaller of the first present value and the second reduced by $M-q$. If a query also contains marks in $Q$, the corresponding $B(X)$ transfers and the marked branch cost is the same. These statements include absent bonds. This proves the first failing new order is exactly $r$. [Two-terminal substitution and persistence](../LATER-BOND-READING-20261119-001/boundary-proof.md)

The now-ordinary core has $I+7+2s$ sites. The two active branches add $2(2M+1)$ sites by observation, giving $J=I+9+2s+4M=137r+280$. There are $2sI$ ordinary shield-anchor distinctions alone. The whole width is bounded by $4(2L+I-1)+2s(M+I)+(2s-1)M+2(7M-5)=O(r^2)$. This yields a linear worst-case lower bound in current $J$ for preserving the current order at the next step, and hence for carrying all future orders. It does not give a fixed future-pair failure for $r>2$.

The matching linear upper bound in $J$ follows directly from the affine equations for a cut. Given a source bond $B$, select from $B$ at most $J$ names whose incidence columns span those of $B$. Crossing these selected names fixes the value on all columns of $B$ since their required values occur jointly. Any source bond through them therefore contains $B$ and equals it. Its size is $K(T)$. For every name outside $B$, the reading on $T$ together with that name is higher or absent. Consequently every minimizing rival bond through $T$ lies in the named $B$ and has its full size. It equals $B$. Thus readings through $J+1$ force the source cut space into any matching rival. For a self-permutation the ranks agree and this is equality. The identical equation space and growing end carry future rounds. This proves $\Theta(J)$ for the same-order and all-future worst cases over unrestricted starts. [Equation transport](../EXTEND-ROUND-20261119-001/extend_round.md)

## One changing link at orders two and three

In the predecessor's two-anchor, six-shield-per-hub core, the special-to-hub weight is two, the special-to-$v$ weight is three, each shield-to-hub weight is six, and all exterior prices begin at four. Change only the first red shield's price to one as above. The history has 31, 39 and 41 ordinary junctions at widths 202, 210 and 212. In the next round every pair still agrees. The three hub spokes at the special $a$ and at two other red shields, names $\{0,32,44\}$, have the same present reading 40 as their image $\{12,32,44\}$. The new readings are 37 and 40. Thus this loss genuinely needs a triple at the new stage.

The check enumerates all marked-middle representatives and both connected shores. Every moved order-$r$ query uses at most $r-1$ shield middles, and unmarked shields of the same color and price can be counted by how many lie on each side. For each count and outer sign pattern, all remaining labels are interchangeable. A separate order-two repricing has present pair readings 49 and 49 followed by 38 and 41. The literal archived round generator checks both histories, their exact parent sets, the joint terminal prices and all live supports. [Repricing and growth replay](../../experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/scale_telescope.py) · [Exact queries and stages](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/scale_telescope.json)

## A necessary quadratic cost for a broad shield construction

For disjoint two-terminal replacements sharing only fixed poles, a simpler counting obstruction requires no special host. Let $m$ virtual link prices fall by $d_i\ge0$ and keep their names fixed. For a host query $X$ the exact new cardinality is

$$
K_{\rm new}(X)=\min_{S\subseteq\{1,\ldots,m\}}
\left(K_{\rm old}(X\cup S)-\sum_{i\in S} d_i\right).
$$

Indeed, for every bond through $X$, its smallest score in the double minimization takes every changed link present in that bond. Compressed link marks can be imposed literally with one mark in a current minimum separating cut of each indicated piece. Hence an old-pair failure against current readings through $r$ requires at least $r-1$ changing links. This count applies to independent two-terminal replacements.

A stronger exclusion applies to the later pair comparison using two disjoint test circuits, even when red shields meet entirely different subsets of anchors. Consider four weight-$L$ incidences around each of two test circuits. The source marks one spoke at each of two red specials. The prescribed image meets one edge of each circuit, so every image bond costs at least $4L$ on test edges alone. The two test spokes are all the red hub's test incidences.

There are $s$ red shield sites. Shield $i$ meets the red hub by a bundle of positive cardinality $h_i$, meets $d_i$ distinct fixed ancillary sites by bundles totaling $a_i$, and has an independent two-terminal connection to the exterior of current separating cost $p_i$. Its next cost is an integer $1\le p_i'\le p_i$. The pieces share only the exterior, and their interiors are disjoint from the rest. All shield, ancillary and branch names are fixed by the permutation. Ancillary sites sit outside the canonical source shore containing the red hub with a chosen subset of its red shields. Require that these canonical shores and their complements are connected, as in the predecessor core. Set

$$
w_i=\min(h_i,a_i+p_i),\qquad w_i'=\min(h_i,a_i+p_i').
$$

Assume the canonical future source cut beats the image circuit bound, so $\sum_i w_i'<2L$. Assume all current readings through $r\ge3$ match. Then

$$
s\ge r-1,\qquad n\ge s(r-2),\qquad
\sum_i p_i\ge {r(r-2)\over2},\qquad
\sum_i\sqrt{p_i}\ge {(r-2)^{3/2}\over2}.
$$

**Several red-spoke marks.** Choose any $T$ of at most $t=r-2$ red shields. Mark their hub spokes as well as the two red test spokes. There is a source bond of cost $2L+\sum_{i\in T}h_i+\sum_{i\notin T}w_i$, by keeping each marked shield outside and optimizing the others. Its image costs at least $4L+\sum_{i\in T}h_i$. Thus $\sum_{i\notin T}w_i\ge2L>\sum_i w_i'$. More than $t$ indices must effectively drop, meaning $w_i>w_i'$. This proves $s\ge r-1$. It also gives, for every such $T$,

$$
\sum_i p_i\ \ge\ \sum_i(w_i-w_i')\ >\ \sum_{i\in T} w_i .
$$

**A low-degree shield forces a terminal side.** At one shield $x$, mark one name in each ancillary bundle and one name in a minimum separating cut of its branch, together with the two red test spokes. These are $d_x+3$ names. In any containing bond the exterior is opposite $x$, since the branch and the host are both marked. All ancillary neighbors are also opposite $x$. To connect $x$'s shore outside its branch it must stay with the red hub. Therefore each shield's hub-to-exterior route costs at least $\min(h_i,p_i)$, on distinctions disjoint from the two test circuits. The image pays at least $4L+\sum_i\min(h_i,p_i)$.

For the source canonical bond put $x$ with the red hub and optimize the other shields. The chosen branch mark attains its ordinary price. Its cost is $2L+\sum_i w_i+(a_x+p_x-h_x)_+$. Put $c_i=w_i-\min(h_i,p_i)=\min(a_i,(h_i-p_i)_+)$. The positive integer weights give $c_i+1\le w_i'$ because $c_i\le a_i$ and $c_i<h_i$. Consequently $\sum_i c_i+s<2L$. If $d_x+3\le r$, the equal-readings assumption forces

$$
(a_x+p_x-h_x)_+\ \ge\ 2L-\sum_i c_i\ >s .
$$

Otherwise $a_x\ge d_x\ge r-2$. In the first case $a_x+p_x>s$, and in the second case $a_x+p_x\ge r-2$. Each shield's ancillary names and at least $p_x$ actual names in its own piece are disjoint from those counted for other shields. This proves $n\ge s(r-2)$ without any uniformity of degrees, weights or prices.

For an effectively dropping shield $x$, $h_x\ge a_x+p_x'+1$ and $p_x\ge p_x'+1$. If $d_x\ge r-2$ then $w_x\ge a_x+2\ge r$. If $d_x<r-2$ then the preceding display implies $p_x>s+h_x-a_x\ge r$. Choose any $t$ effectively dropping shields. The total $\sum_i p_i$ is at least the sum of the $p_x$ of the second kind. By the several-mark inequality it exceeds the sum of the $w_x$ of the first kind. Taking the larger of these two bounds proves the claimed total-price inequality.

To prove the square-root sum bound, if at least $\lceil t/2\rceil$ shields have $p_i\ge t$, their contributions already suffice. Otherwise put them all in $T$. There are more than $t$ effective decreases in total. Add $\lceil t/2\rceil$ other effectively dropping shields to $T$ so that $|T|\le t$. Each added $i$ has $p_i<t$, so the preceding low-degree test forces $d_i\ge t$. Being effective, it has $w_i'=a_i+p_i'\ge t+1$. The several-mark inequality also gives

$$
\sum_{i\notin T}(w_i-w_i')>\sum_{i\in T}w_i'\ge t^2/2.
$$

All $i\notin T$ have $p_i<t$, whence $\sqrt{p_i}\ge(w_i-w_i')/\sqrt{t}$. Summing proves the remaining inequality.

For independent branches attached at exhausted roots, this last bound counts ordinary junctions at any positive-age observation. All current loose names end at newly created sites, and such a site meets each old site at most once. If branch $i$ has $o_i$ old sites besides its root and $\ell_i$ new sites, cutting the old-to-new links costs at most $(o_i+1)\ell_i\le(o_i+\ell_i)^2$. Each branch has $\ell_i\ge1$ and intersects the remaining system only at its root and the exterior. Thus $o_i+\ell_i\ge\sqrt{p_i}$. Branch interiors are disjoint, yielding $J\ge (r-2)^{3/2}/2$. The squared-price construction attains this order. In this architecture the worst necessary order for the fixed next-pair comparison is therefore $\Theta(J^{2/3})$ in ordinary junctions and $\Theta(\sqrt n)$ in distinctions.

When every counted branch contracts to a single unit at the next positive open stage there is a stronger junction bound. Take a minimum unit cut of one branch at that next stage and put its root away from the exterior. Every new site in the root shore has at least one fresh distinction to the exterior, so there is at most one such new site. If there is none, this shore already gives an old cut of cost at most one. If there is one, its fresh name uses the unique crossing, and moving the new site back to the exterior makes at most one old distinction cross per old live parent. The old price is therefore at most the number of live parents in that branch, provided each branch is active. Summing gives $J\ge r(r-2)/2$ under these additional hypotheses. Directly in the predecessor's compact branches there are exactly $p_i$ live sites per branch at age one.

The necessary width bound applies to arbitrary sparse choices of ancillary neighborhoods within this architecture. It leaves open whether another core or genuine multi-terminal coupling can beat $\Theta(\sqrt n)$ for a fixed future pair. The telescope proves a different worst-case statement in ordinary junctions.

## A five-mark upper bound when one terminal equation remains

This independent argument concerns static equation recovery. Suppose known rows contain the stars of every vertex except $u,v$, including the exterior as a vertex. Assume that all edge costs count literal distinctions, the connected graph has no one-distinction bond, and a trivalent low site $x$ has three distinct neighbors, two of them $u,v$. If current readings through order five agree then the one remaining source equation transfers to any rival containing the known rows. Equal rank gives full equality, in particular for a self-permutation. This bound is independent of the size of a minimum $u$–$v$ cut.

Choose a minimum $u$–$v$ cut $B$ of size $\lambda\ge2$. Exactly one incidence $f$ of $x$ crosses. One must cross because $x$ meets both terminals, and if two or more crossed then moving the low vertex would strictly reduce the separating cost. The cut $B^*=B\mathbin\triangle\delta(x)$ still separates $u,v$ and has size $\lambda+1$. It is a bond. Indeed, every cut is a disjoint union of bonds, obtained by repeatedly taking a minimal nonempty contained cut and removing it by binary addition. Any such decomposition here must include a $u$–$v$ separating bond of size at least $\lambda$. An additional bond would cost at least two.

Mark the two incidences of $x$ other than $f$, and choose $y\in B^*$ outside the star of $x$, possible because $\lambda\ge2$. Any source bond through those three marks omits $f$, or it would properly contain the star of $x$. Thus it separates $u,v$, and flipping $x$ back decreases its cost by one. The minimum is exactly $\lambda+1$. Its minimizing supports, flipped by $\delta(x)$, are precisely the minimum $u$–$v$ cuts containing $f,y$.

For these rooted minimum cuts, any collection of edge-crossing requirements is jointly possible if every pair is possible. For an elementary proof take a maximum integral flow from $u$ to $v$. Its residual graph characterizes minimum shores as successor-closed sets containing $u$ and avoiding $v$. Every link in a minimum cut is saturated and has one fixed crossing direction. Asking it to cross requires that its tail be in and its head be out. A family of such requirements is consistent exactly when no required-in vertex has a residual path to a required-out vertex. A violation uses at most two requirements. This remains true after imposing the common marks $f,y$. [Earlier minimum-cut reading proof](../../proofs/GROWN-END-READING-20261119-001A/GROWN-END-READING-20261119-001A-P001_transport/proof.md)

Take an arbitrary minimizing rival bond through the three mapped marks. Pull its names back. For each additional name, and each pair of them, the source has a size-$\lambda+1$ minimizing bond containing those marks by the common order-four and order-five readings. The name $f$ is absent. For names outside the star, flipping $x$ does not change their membership. The rooted compatibility argument therefore puts all pulled-back names in a single source minimum after reversing the flip. The two supports have equal size and coincide. Every such source cut separates $u,v$ and therefore has the missing coset modulo all the known vertex stars. One minimizing rival bond supplies that coset. This argument needs one trivalent neighbor and the specified one-dimensional remainder. It gives no general width upper bound.
