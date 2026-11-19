# A meet-once matching that changes after a complete round

Seven starting junctions grow to twelve with 23 distinctions. At that reached stage the transposition $(0\;2)$ fixes every distinction of every live junction and matches the bond distances of all 253 pairs. At the next stage pair $(0,1)$ has distance 2 and its image $(2,1)$ has distance 3. All of 0, 1 and 2 were already shared at the start. No choice of fresh names or pairing of loose names can affect that entry. The two sides of the comparison are the same arrangement. Its identity still extends. [Seven-start certificate](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/construct_7.json)

## The seven-junction history

Use the classical incidence multigraph to calculate the parity relations. Junctions are vertices. Shared distinctions join their two holders, and loose ones meet a single outside vertex $o$. Ordinary junctions meet each other at most once throughout these histories. A cut is a sum of the junction equations. A bond is a nonempty cut minimal under inclusion, equivalently a cut with two connected shores. If $K(x,y)$ is the size of a smallest bond through both distinctions, their bond distance is $K(x,y)-1$.

The ordinary subgraph called a diamond in graph theory has four junctions $s,t,a,b$ and five distinctions $sa,sb,ta,tb,ab$, numbered 0 through 4 in that order. The entire supports of $a,b$ are their three displayed distinctions. Only $s,t$ meet the rest of the arrangement. Add three junctions numbered 4, 5, 6, each meeting only $s$ and each holding two loose distinctions. Give $t$ two loose distinctions as well. Every starting arity is between three and five.

The three junctions meeting $s$ form all three two-parent groups, since they share the witness $s$. On the other side, the two loose distinctions at $t$ each supply a separate one-parent junction. Here are all the new supports as returned by the fewest-count rule.

| Round | New supports on the $s$ side | New supports on the $t$ side |
| --- | --- | --- |
| First | {8,10,16}, {9,12,17}, {11,13,18} | {14,19,20}, {15,21,22} |
| Second | {16,17,18,23} | {19,21,24,25}, {20,26,27}, {22,28,29} |

At the second round, the first three additions have pairwise witnesses 4, 5 and 6, and no single witness for all three. Their three-parent group consumes 16, 17 and 18 and produces the single fresh distinction 23. Once this happens, the entire portion on the $s$ side has boundary {0,1,23}. Its projected relation allows 000, 011, 101 and 110, passing K1–K3 under forgetting. Every reached live support is disjoint from 0 and 2. At the starting stage the transposition already preserves the pair table, but moves the support of live $t$.

## The full table

Let $X$ be the exterior graph obtained by removing the five displayed distinctions and the vertices $a,b$, keeping $s,t,o$. Assume $X$ is connected and let $\lambda$ be the minimum size of a cut of $X$ separating $s$ from $t$. For the first-round stage, there are two edge-disjoint paths in $X$ from $s$ to $t$ through $o$. Use two different starting neighbors of $s$, two different first-round left additions, and the two separate one-parent additions at $t$. Exactly two connections leave $t$ in $X$. Hence $\lambda=2$. After the second round, 23 is the only connection from the $s$ portion to $o$, giving $\lambda=1$.

A bond meeting an exterior distinction and a diamond distinction must separate $s,t$. If both terminals lay on the same shore, the opposite connected shore would lie entirely in one part of the graph. When the terminals are separated, each part restricts to a cut with both shores connected to their respective terminals. Conversely any two such cuts, one in each part, join to give a bond. The four possible terminal-separating cuts inside the diamond are

$$
\{sa,sb\},\quad \{ta,tb\},\quad \{sa,tb,ab\},\quad \{sb,ta,ab\}.
$$

When the terminals are together, a bond meeting a diamond distinction is the star of $a$, the star of $b$, or the four-distinction boundary of $\{a,b\}$. The latter is feasible because $X$ joins $s$ to $t$. These lists give the following bond sizes for the four distinctions $sa,sb,ta,tb$.

| Pair | $K$ |
| --- | --- |
| Two meeting at $a$ or $b$ | $3$ |
| Two meeting at $s$ or $t$ | $\min(4,2+\lambda)$ |
| One at each terminal, with different interior endpoints | $\min(4,3+\lambda)$ |
| Any of the four paired with $ab$ | $3$ |
| Any of the four paired with an exterior distinction $z$ | $2+$ the least size of a terminal-separating bond of $X$ containing $z$, with no common bond if none exists |

At $\lambda=2$, swapping just $sa$ and $ta$ preserves every entry. At $\lambda=1$, it exchanges a same-terminal pair with the pair $sb,ta$. Exactly four unordered pairs change, namely $(0,1),(0,3),(1,2),(2,3)$. In particular, the upper bound 2 for the new distance of $(0,1)$ comes from a true three-place parity relation. The lower bound 3 for $(1,2)$ uses every possible bond. At the reached stage the transposition changes the parity equations. Its effect on the star of $s$ is to add the two-distinction word $\{sa,ta\}$, whereas the smallest bond through that pair has size three.

## Other starts and replay

| Start | Junction counts | Distinction counts | Reached pairs matched | Next pairs checked | Next differences |
| --- | --- | --- | ---: | ---: | ---: |
| Seven | 7, 12, 16 | 16, 23, 30 | 253 | 435 | 4 |
| Eight | 8, 12, 16 | 18, 24, 31 | 276 | 465 | 4 |
| Ten | 10, 15, 20 | 21, 29, 38 | 406 | 703 | 4 |

In the eight-start, the first two left additions use parent pairs {4,5} and {4,6}. The second round takes these two additions together, with one fresh distinction. The ten-start also contracts two additions into one. Its starting terminal $s$ participates in both first-round left groups, and $t$ already has two distinct ordinary neighbors. All three cases give $\lambda=2$ and then 1, have pointwise-fixed reached live supports and permit no repeated ordinary meeting at any stage. The ten-start has one starting arity six. [Eight-start certificate](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/construct_8.json) · [Ten-start certificate](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/construct_10.json)

## A minimum for the five-distinction construction

Consider an open stage containing the displayed diamond with $a,b$ exhausted and with exactly their three displayed distinctions each. Both the reached arrangement and its next complete round must contain this fixed part. A change from $\lambda\ge2$ to $\lambda=1$ at any positive age needs at least six starting junctions, even if the diamond first became complete after the start. This bound concerns this particular way of changing a matching.

First consider an open successor and a one-edge $s$–$t$ cut of its exterior. Every new junction has at least one fresh distinction to $o$. If the single crossing were an inherited distinction, including a formerly loose distinction just taken by a new junction, every new junction would have to lie on the $o$ side. Project the cut back through the round. All previously shared crossings survive unchanged, and any previously loose distinction on the opposite shore already crossed to its recipient. The old cut would have at most one crossing. Consequently a drop from at least two requires that the single crossing be fresh, incident to the only new junction on the far shore. No ordinary edge of the exterior crosses. In particular an ordinary $s$–$t$ path already present at any earlier stage precludes such a drop. A closing round takes every loose distinction into its sole implied zero-fresh junction. It simply replaces the outside vertex as holder and keeps the old cut sizes.

When the diamond is present at the start, $s,t$ cannot both be initially live. They share the witnesses $a,b$, so one complete first-round group contains both and permanently connects them in the ordinary exterior. An initially exhausted terminal instead needs two distinct ordinary neighbors outside the diamond. It can never gain another distinction, and a terminal of exterior degree at most one has $\lambda\le1$ at every stage. Thus the four diamond sites already require at least two other starting sites.

The same lower bound covers a diamond first completed later. Every ordinary triangle exists by round one. Indeed, two older neighbors of its youngest vertex must have been adjacent live parents, and after any complete round the live vertices are coeval and independent. In an open history every new vertex has a fresh distinction. It remains loose or joins a younger vertex, and if it was introduced at round one that distinction cannot subsequently belong to a triangle. All three distinctions at $a$ and all three at $b$ belong to triangles. Both $a,b$ must therefore be starting sites. If neither terminal was present at the start, $a,b$ would form their own two-site component. By connectedness they would be the entire start, with no third site to witness a joint first-round addition.

Suppose just $t$ is a later junction. It must appear in round one to complete a triangle. Initially $a,b$ each have exactly one loose distinction, reserved for $t$. If $s$ was live, the candidate pair $s,a$ through $b$ must occur in some group. As $a$ can participate only once, that group was $t$, giving a permanent ordinary $s$–$t$ connection outside the diamond. If $s$ was exhausted, it needs two distinct ordinary exterior neighbors from the start. At a start with at most five sites, these account for both remaining sites. Any extra parent of $t$ then provides an ordinary path to $s$. With exactly the parents $a,b$, no other first-round addition can share either parent with $t$, since each used its sole loose distinction. The prospective demand at $t$ is zero, so a nonclosing two-parent birth has exactly one fresh distinction. From its birth onward $t$ has exterior degree one. This accounts for all possible positions of the terminals in a start of at most five sites.

There is a sharper bound when the diamond was present from the start and the drop must occur at the second round. With just six sites, both exterior neighbors needed by the exhausted terminal use the two available extra sites in its component. Each ordinary exterior component must contain a terminal by connectedness of the original start. The other terminal therefore stands alone in its own component, since an ordinary terminal-to-terminal path would persist. It produces only one-parent additions, each with at least two fresh distinctions. In the exhausted terminal's component, at most two starting sites are live, so the first round makes at most one addition with multiple parents. Any further addition there is also one-parent. At a new one-crossing cut, the entire previous loose frontier of the far component must be taken by its one new junction, at most one distinction from each parent. A one-parent first-round addition carrying two loose distinctions rules this out for its component. If the exhausted-terminal component has only one first-round addition, its entire frontier was already at most one or includes two loose distinctions of the same parent. It cannot give the drop either. Seven starting junctions attain the second-round bound.

The literal replay uses the archived complete-round law and compares every unordered pair by enumerating connected cuts on both shores. It independently measures $\lambda$ by a minimum cut after removing the five distinctions. Run the repository virtual environment on this family's replay script with the option `--check`. [Replay script](construct.py) · [Distances, complete rounds and cut counts](../../../artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/construct_results.json)

The separately written earlier lineage verifier also replayed the eight- and ten-start certificates. In each it found zero reached differences and four successor differences on previously shared distinctions. [Independent verifier](../../GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/verify.py)
