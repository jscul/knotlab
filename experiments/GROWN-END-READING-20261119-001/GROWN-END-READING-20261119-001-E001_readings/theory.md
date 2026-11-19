# What pair and triple bond sizes recover

Two connected simple wired graphs agree on the minimum bond size of every pair and every triple and have different binary equation spaces. Their ranks are 231 and 232. In the second graph a particular permutation preserves all those readings and changes the equations. A positive result applies to a different family of genuinely reached stages. There, unique shortest bonds and a rank bound determine the full relations even with arbitrarily large exhausted junctions.

Use the ordinary graph representation of the finite parity equations, adding the outside vertex as the second holder of each loose distinction. Each junction imposes even parity on its support. The span of those equations is the binary cut space. It has rank equal to the number of ordinary junctions in a connected open arrangement. Indeed, the sum over an ordinary vertex set is its cut, and a nonempty ordinary set is a nonempty proper subset of the connected wired graph. A bond is a minimal nonempty cut. Write $K(S)$ for the smallest cardinality of a bond containing $S$, using infinity when no such bond exists. For two names the reported distance is $K-1$.

## A hidden equation in a simple wired graph

Take 21 index vertices $u_i$, with indices modulo 21. For each unordered pair of indices $i,j$, introduce a middle vertex $w_{ij}$ with one edge to $u_i$, one to $u_j$, and a named spoke $y_{ij}$ to a hub $h$. The first graph has 210 middle vertices, 232 vertices in total and 630 edge names. In the second graph keep every name and its middle endpoint but split $h$ into $h_0,h_1$. Write an unordered pair in its unique form $\{i,i+t\}$ with $1\le t\le10$. Its spoke goes to $h_0$ for $t\le5$ and to $h_1$ for $6\le t\le10$.

Each graph stays connected after deletion of any vertex. Deleting a hub retains the subdivided complete graph, and the other hub, when present, still has neighbors. Deleting $u_i$ leaves a subdivided complete graph on the remaining indices and each middle vertex incident with $u_i$ retains its other ordinary endpoint. Deleting one middle vertex removes just one original connection, and each hub retains many spokes. A common index vertex can serve as the wired exterior, giving connected ordinary presentations with genuine junction stars. There are no parallel edges. A two-name state difference would require parallel edges, since every endpoint of its support must have even degree. Thus every pair-flip reading is false in both graphs.

**Separating the hubs costs at least 105.** At each $i$ and each $t=1,\ldots,5$, take the path

$$
h_0,\ w_{i,i+t},\ u_i,\ w_{i,i+t+5},\ h_1 .
$$

Each middle vertex occurs in exactly one of the resulting 105 paths, by the unique orientation of its index pair. Thus the paths share no edge. Every bond of fewer than 105 names in the split graph puts its hubs together. Contracting them gives a bond on precisely the same names in the first graph. Conversely, lift a bond of the first graph with fewer than 105 names by putting the two hubs on the side of $h$. Once those boundary names are removed, the 105 disjoint paths ensure that the hubs remain connected in that shore. Any original connection through $h$ can therefore be restored inside it. The other shore is unchanged. The lists of bonds of sizes below 105 are identical.

**Every three marks have a small bond in the first graph.** The same argument works with one or two marks. Every marked name is a distinct incidence at a middle vertex. Construct a connected shore excluding $h$. If all three incidences of one middle vertex are marked, its singleton shore works. Otherwise there are at most three marked middle vertices, and at most one of them carries two marks.

Choose a set $P$ of index vertices as follows. If a middle has two marked index incidences, put both their endpoints in $P$. If its two marks are a spoke and one index incidence, exclude that index and put the other index in $P$. This forbids at most one index over the whole construction. For each marked middle still having no endpoint in $P$, add one of its two endpoints that is not forbidden. The resulting set has size at most the number of marks. Each chosen index was charged to a mark.

Put a marked middle on the chosen shore whenever its spoke is marked or none of its marked index endpoints lies in $P$. Place other marked middles on the opposite shore. At each middle with a single index mark this puts it opposite the marked endpoint. With two index marks both endpoints are in $P$, and with a spoke and an index mark the marked index is outside $P$. Every mark therefore crosses. Each marked middle placed on the chosen shore touches a member of $P$.

Choose an index $r$ appearing in no marked middle. Add $u_r$ and the unmarked middle $w_{ir}$ for every $u_i\in P$ to the chosen shore. It is connected through $u_r$. The opposite shore is connected through $h$, since all its middle vertices meet $h$ and each of its index vertices retains a middle neighbor. The latter vertices have degree 20 and at most six middles were placed across. The cut is consequently a bond. If $p=|P|\le3$, the $p+1$ chosen index vertices contribute at most $20(p+1)$ crossings before adding middle vertices. The $p$ connecting middles each have two chosen endpoints, decreasing that count by one each. Each chosen marked middle has at least one chosen endpoint and can increase the count by at most one. Thus the bond has size at most $20(p+1)-p+3\le80$. The single-middle case has size three.

Every pair and triple consequently attains its minimum among the shared bonds below 105. All 198,135 pair readings and all 41,476,260 triple readings agree name by name. The rank increases by one because there is one extra vertex and both graphs are connected.

**A self-permutation.** Swap indices 2 and 3 and act on names accordingly, keeping the respective type of each incidence or spoke. This is an automorphism of the unsplit graph. By equality of the readings it is also a pair- and triple-table isometry of the split graph. It fixes the individual edge $u_0w_{01}$. In the split graph an equation supported only on spokes must put all indices and middles together, since removing all spokes leaves the connected subdivided complete graph on them. Its support is empty, all spokes at $h_0$, all at $h_1$, or their union. The permutation changes the support at $h_0$: $\{3,8\}$ has offset 5 and maps to $\{2,8\}$ of offset 6, while $\{0,1\}$ of offset 1 remains fixed. The image is therefore none of the four possible supports. This demonstrates failure of equation-space recovery in a single simple graph even when one attachment name is fixed. A specified growing history and a matched growing end require further argument.

For the symbolic check, any set of at most three marks uses at most six ordinary indices. The unsplit graph admits all their permutations. The replay checks the literal shore construction for every one of the 45 singleton, 990 pair and 14,190 triple choices formed on six indices. It verifies both connected shores, every marked crossing, and all 105 disjoint paths. The largest sizes it produces are 40, 60 and 80, respectively. These are sizes of exhibited bonds, and the equality of minima uses the common short-bond proof above. [Symbolic replay](theory_check.py) · [Recorded checks](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/theory_check.json)

## A local equation and a rank test

Given a pair $p=\{x,y\}$ with finite $K(p)=k$, form the set

$$
U(p)=p\ \cup\ \{z\notin p:K(p\cup\{z\})=k\}.
$$

This is exactly the union of the minimizing bonds for $p$. Each member belongs to some such bond, and each such bond contributes every member. If and only if $|U(p)|=k$, there is a unique minimizing support. Its parity equation is forced in every presentation with the same readings. A triple of reading 3 and a pair of reading 2 also give their own equations immediately. A larger union records distinct possible minimizing supports. Its full parity does not follow from this test.

Add all these forced words to the equations of the observed live junctions. If they span the starting equation space, every self-permutation preserving the readings and the marked end preserves that space. For comparison with a different presentation, the same argument gives inclusion. An independent upper bound on the rival rank supplies equality.

For example, let $m$ be the width, $L$ the number of loose distinctions, $r$ the number of live junctions, and $h$ the sum of their arities. All rivals matching the growing end have exactly $2m-L-h$ incidences at exhausted junctions. With the ordinary minimum arity three their ranks are at most

$$
r+\left\lfloor(2m-L-h)/3\right\rfloor .
$$

Thus whenever all exhausted junctions of the source are genuine ternary knots, matching the pair and triple readings and the growing end determines its equation space among unrestricted admissible rivals. Every exhausted star is visible as an actual three-name bond. The bound is attained, irrespective of the live arities. More generally, the same rank test applies when other forced supports supply the missing dimensions.

Equality of equation spaces and a matching of the growing end have an all-round consequence. The complete rule gives corresponding parent groups and fresh counts. Its new equations are precisely the transported old equations together with the matched new supports. The next ends match through the parent groups, so this argument repeats through every subsequent lawful round. This concerns continuations of the specified initial matching. A proof that a particular matching preserves only the next pair table would not establish that induction. [Equation transport in EXTEND-ROUND](../../../research/EXTEND-ROUND-20261119-001/extend_round.md)

## A reached family with unbounded arity

Take a simple $d$-regular ordinary graph $G$ on $n\ge3$ junctions. Assume every nontrivial cut of $G$ has at least $d$ edges and every two vertices have a common neighbor. Give each junction two loose distinctions. Complete graphs $K_n$ satisfy the hypotheses for every $n\ge3$. Each starting junction is a genuine bond because every other vertex has a connection to the outside after its removal.

**Claim.** At the first reached stage, its pair and triple readings and the marked end determine its equation space among all finite connected open parity arrangements matching those observations. Consequently any such matching admits equation-preserving extensions for all subsequent complete rounds.

All old junctions are pairwise candidates. Their full set is covered by no single common neighbor, since an ordinary vertex never meets itself. It is the unique maximal candidate set. The first round therefore makes one junction $H$ with all $n$ parents and one one-parent junction $U_i$ at each old junction $v_i$. The next candidate pairs are exactly $H,U_i$. The fewest-count rule gives $H$ exactly $n$ fresh names and each $U_i$ exactly two. All old junctions are now exhausted at arity $q=d+2$. The reached arity of $H$ is $2n$.

Write $a_i$ for the old input from $v_i$ to $H$, $b_i$ for its other old input, now at $U_i$, and $x_{ij}$ for an original $G$ edge. The architecture in this proof describes a source. A decoder can examine every pair of names without knowing that architecture.

**Shortest cuts through an old edge.** Suppose a cut separates the old vertices into sets of sizes $k$ and $n-k$. It costs at least $d$ old edges and at least $\min(k,n-k)$ of the $a$ names. The $n$ paths from the respective $v_i$ through $U_i$ to the outside share no edges. They give a further $\min(k,n-k)$ crossings. A cut of size $q=d+2$ splitting old vertices must therefore isolate exactly one of them, say $v_i$, among the old vertices. Both $H$ and the outside must be on the majority side to attain the two individual lower bounds. Every $U_j$ must also be there. Putting $U_i$ with $v_i$ costs its two loose names in place of $b_i$, and putting any other $U_j$ across adds three crossings. Hence every such cut is exactly the star of $v_i$. It is a bond since deleting $v_i$ leaves the remaining vertices connected through $H$ and the outside.

It follows that the two shortest bonds through $x_{ij}$ are the stars of $v_i$ and $v_j$. The former is the unique shortest bond containing both $x_{ij}$ and $a_i$. The equation test $U(\{x_{ij},a_i\})$ recovers it in every rival. Every old vertex has an ordinary neighbor, so every exhausted source star transfers. All live stars already transfer with the growing end.

**Upper bound on rival junctions.** Every cut through an $a_i$ also has size at least $q$. If the old vertices are split, use the preceding bound. Otherwise all old vertices lie opposite $H$. If the outside is with them, all $n$ fresh names of $H$ cross as well as its $n$ inputs. If the outside is with $H$, all $n$ routes through the $U_i$ cross in addition to those inputs. In both cases the cost is at least $2n\ge q$.

A bond through two different $b_i,b_j$ has size at least $q$ as well. If the old vertices are together, $U_i$ and $U_j$ are both opposite them. Their shore is disconnected unless it contains the outside. Separating the outside from all old vertices costs at least $n$ disjoint crossings through the $U_i$ and another $n$ through the inputs or fresh names of $H$. The case splitting the old vertices was settled above. The individual $b_i$ are open and appear in a bond of size three at $U_i$.

Consider any exhausted junction in a rival with the matched readings and end. Its support can use only $x$, $a$ and $b$ names. A star containing an $x$ or $a$ has size at least $q$, since any cut through that name contains a bond through it and the readings give the bound. A star supported only on $b$ names contains a bond. None of those names is a singleton bond, since each has a finite joint reading with another name. The contained bond uses at least two distinct $b$ names, so again the star costs at least $q$. The containment fact follows by decomposing any nonempty cut into disjoint bonds, taking a minimal subcut and repeating on the remaining binary sum.

The rival has exactly $nd+2n=nq$ exhausted incidences. They comprise two for each old ordinary edge and one for each $a$ and $b$. All other names are loose at the marked live junctions. The rival therefore has at most $n$ exhausted junctions. The forced source equations give rank $2n+1$, while the $n+1$ marked live junctions and this upper bound give rival rank at most $2n+1$. Equality of the equation spaces follows.

This family's comparison with arbitrary rival presentations is stronger than its self-permutation test. A pointwise-fixed end already identifies every $x_{ij}$ inside the same source from its pair readings. The only $a$ names with $K(x_{ij},a)=q$ are $a_i,a_j$, and there is at most one ordinary edge on that pair of vertices. The family thus proves the reach of the reconstruction method without establishing a need for triples in its self-permutation problem.

## Resolving an equation modulo the short bonds

A minimizer can also fix an equation modulo an already forced span. If every possible size-$k$ bond containing a pair with reading $k$ belongs to the same coset, one representative of that coset and the forced span are present in every rival. No individual support has to be selected.

For a concrete example, take $k$ internally disjoint paths between two junctions, with $k$ at least three. Allow any positive path lengths. This is an ordinary graph example. Internal degree-two vertices need not be admissible junctions in the growth experiment. A bond with the endpoints together takes two edges from one path. Its shore excluding the endpoints is a single interval of that path. A bond separating the endpoints takes exactly one edge from each path. All such choices have connected shores. Thus two names from the same path have pair reading 2, and a pair from different paths has reading $k$. This includes the graph $K_{2,k}$, whose entire first layer of bonds has size two.

The pair table alone determines the full equation space of any matching rival. Every pair in a path gives the same required two-name bond in both presentations. Any other rival bond meets at most one name in a path, since otherwise it properly contains a two-name bond. It has at least $k$ names from its cross-path reading and at most $k$ from this bound. It therefore takes exactly one name in each path. At least one such bond exists by any finite cross-path reading. All transversals differ by sums of the already forced two-name words, giving precisely one further dimension. No rival bond outside this span is possible. A singleton bond is excluded because every name has a finite reading with some other name.

## Literal checks

The replay grows three explicit starts with the archived rule, enumerates the reached bonds, constructs the complete finite pair and triple readings, and applies the local equation test to those readings. The program treats an absent table entry as having no finite common bond.

| Ordinary starting graph | Reached junctions | Exhausted arity | Largest live arity | Marked rank plus bonds of size at most 3 | Rank with unique minimizing supports | Physical rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| $K_3$ | 7 | 4 | 6 | 4 | 7 | 7 |
| $K_6$ | 13 | 7 | 12 | 7 | 13 | 13 |
| $K_{2,2,2}$ | 13 | 6 | 12 | 7 | 13 | 13 |

These checks exercise high exhausted stars that the marked equations and the short bonds leave undetermined by linear span alone. The arbitrary-rival and unbounded-size conclusions use the proof. [Replay code](theory_check.py) · [Exact results](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/theory_check.json)
