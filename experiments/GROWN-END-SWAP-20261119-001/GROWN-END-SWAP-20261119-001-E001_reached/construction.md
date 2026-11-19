# A reached growing-end matching that fails one round later

Start with six junctions. After one complete round, exchanging distinctions 0 and 2 fixes the bond distance of all 210 unordered pairs and the whole support of every live junction. After a second complete round, distinctions 0 and 1 have distance 2 and their images 2 and 1 have distance 3. All four central distinctions were already shared at the start. Every fresh naming and every permitted re-pairing of loose distinctions leaves this discrepancy in place. The two successors are the same arrangement, so their identity still gives an unmarked isometry. [Literal certificate](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json)

## The two rounds

Number the junctions of the start in the order shown. Each row constrains the listed distinctions to even parity.

| Junction | Number | Support |
| --- | ---: | --- |
| M | 0 | 0, 1, 2, 3 |
| A | 1 | 0, 1, 4, 5 |
| B | 2 | 2, 3, 13, 14 |
| S | 3 | 4, 6, 9, 10 |
| D | 4 | 5, 6, 7, 8, 11 |
| E | 5 | 7, 8, 12 |

The first round uses S and D together through their common neighbor A, and S and E through D. It adds the junctions on {9,11,15} and {10,12,16}. B supplies its two loose distinctions to separate junctions on {13,17,18} and {14,19,20}. The live junctions are now precisely these four additions. The maximal common-neighbor sets of live junctions with at least two members consist of the first two additions and the last two. The transposition (0 2) fixes every distinction in all four supports. At the six-junction start it already preserves the pair table, but moves the support of the live junction B. The first round is where this particular swap first preserves the growing end as well.

The second round joins 15 and 16 with the single fresh distinction 21. It also adds the supports {17,19,22,23}, {18,24,25} and {20,26,27}. The complete left portion now attaches to M by 0 and 1 and has only one remaining loose distinction, 21. Its boundary {0,1,21} is a genuine three-place parity knot. Its projected allowed states are 000, 011, 101 and 110, and the canonical forgetting test passes K1–K3. A boundary containing 1 and 2 always contains 0 and 3 as well. The four-place support of M attains that bound. Before this second round the left portion had two separate loose distinctions, 15 and 16.

There is also a distinction at the level of the full allowed-state relations. At the reached stage the image of A's physical equation contains 1 and omits 0. Every equation in the span contains both or neither, since 0 and 1 have the same two holders. Thus the marked map does change the equations, even though it preserves every reached pair distance. The established continuation result for an equation-space isomorphism remains applicable under its own hypothesis. [Earlier one-round result](../../../research/EXTEND-ROUND-20261119-001/extend_round.md)

## Why the full table changes on exactly four pairs

For this proof use the classical incidence multigraph. Its vertices are the junctions and an outside vertex $o$. Each distinction gives an edge between its two holders, with $o$ as the second endpoint of each loose distinction. Sums of the junction equations give exactly the cuts. Their inclusion-minimal nonempty supports are the cuts whose two shores are connected, called bonds. Thus the exact bond distance for a pair is $K-1$, where $K$ is the least size of a bond containing both. A pair in no common bond keeps that reading under any size-preserving correspondence of its candidate bonds.

Suppose M has exactly $m$ parallel distinctions $P$ to A and $m$ parallel distinctions $Q$ to B, with $m \ge 2$. Assume that the graph $Y$ left by deleting M is connected. Write $\lambda$ for the least number of edges of $Y$ crossing a cut separating A and B. Three facts determine what happens under the exchange of one member of $P$ with one member of $Q$.

1. A bond through one member of each set contains all $2m$ members. The cut around M attains $2m$.
2. For distinct members of the same set, $K = m + \min(m, \lambda)$. A bond crossing both sets has size at least $2m$. A bond crossing just that set separates A and B in $Y$ and has size at least $m+\lambda$. A minimum A–B cut of $Y$ has connected shores. Any component detached from its own terminal could otherwise be moved across to decrease the cut. Adjoining M to either shore realizes $m+\lambda$ through the selected set. The cut around M realizes $2m$.
3. Fix a distinction $z$ outside $P \cup Q$. A bond through $z$ and a member of $P$ or $Q$ must separate A and B. If A and B were together, M would form its entire opposite shore and the bond would omit $z$. Move M to the opposite shore. Its only neighbors on either shore form a single vertex, so both shores remain connected. This move exchanges the two sets of $m$ crossings, preserves $z$ and preserves the size. It is its own inverse. Hence $K(p,z) = K(q,z)$ for every $p \in P$ and $q \in Q$, also for fresh $z$ at any later stage satisfying the same hypotheses.

The transposition therefore preserves the entire table exactly when $\lambda \ge m$. In the six-junction construction $m=2$. After the first round, the two paths A–D–6–$o$ and A–S–7–$o$ share no edge. The paths B–8–$o$ and B–9–$o$ share no edge either. Together they give two edge-disjoint A–B paths in $Y$. Cutting the left portion's two loose distinctions gives the matching upper bound. After the next round that portion has only one outward distinction, and $Y$ remains connected. The values of $\lambda$ are therefore 2 and 1. The only successor pairs whose distances change under the swap are (0, 1), (0, 3), (1, 2), and (2, 3).

## Frozen controls and scope

| Start | Junction counts | Distinction counts | Reached pairs checked | Successor pairs checked | Successor discrepancies |
| --- | --- | --- | ---: | ---: | ---: |
| Six-junction deduction | 6, 10, 14 | 15, 21, 28 | 210 | 378 | 4 |
| Seven-junction prediction | 7, 11, 15 | 16, 22, 29 | 231 | 406 | 4 |
| Eleven-junction prediction | 11, 15, 17 | 24, 28, 30 | 378 | 435 | 4 |

The seven- and eleven-junction starts appeared in the frozen preregistration. The six-junction simplification was specified before execution. In the seven-junction start, separate common neighbors A and W support the two left joins. In the eleven-junction start both sides use that same five-junction arrangement. All three have reached the same drop from two independent connections to one after deleting M, all fix their reached growing ends pointwise, and all four discrepancies involve previously shared distinctions. For the six- and seven-junction starts the right side has two one-parent additions in the first round. The eleven-junction start uses only two-parent additions in each of its rounds. [Seven-junction certificate](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_7.json) · [Eleven-junction certificate](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_11.json)

The six-junction construction also gives a failure for every starting junction count of at least six, with all starting arities between three and five and at most two shared distinctions per pair of junctions. For any positive integer $k$, add a path of $k$ exhausted junctions between A and E. Use a single shared distinction on its first link from A and two shared distinctions on every remaining link, including the last one to E. A and E now each have arity five. The first new junction has arity three and every other new junction has arity four. Deleting any old vertex leaves the new path attached through A or E. Deleting an interior vertex leaves its segments attached to the connected old graph. Every added distinction belongs to a cycle, using either its parallel mate or the old route from E back to A. Each start therefore remains open, has no forced distinction, and every junction support remains a bond.

Each added junction meets at most one initially live junction, E, and none meets a live junction after the first round. The sets of live junctions met by one junction and the loose counts are unchanged, so the same two complete rounds occur. The entire added path stays in the left portion. Both disjoint paths and the two successive cuts used above remain valid. The least possible starting size and the case in which every two junctions meet at most once remain separate questions.

From the repository root, run `.venv/bin/python -B experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct.py --check`. It applies the archived complete-round law twice to each starting list and compares all bond distances under the stated map, including each successor entry involving a fresh distinction. [Replay code](construct.py) · [All parent sets, fresh lists and disagreements](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_results.json)
