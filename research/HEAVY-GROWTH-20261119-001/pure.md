# Two returns that force start-13 to grow

**The number of births on start-13 tends to infinity at least exponentially.** At age six, five junctions give two different returns of length four to the same ordered residual pair. Their choices can be concatenated in any order. For all integers $k\geq0$ and $0\leq r<4$, age $7+4k+r$ has at least $2^k$ births. Start-13 passes the canonical source audit and has already entered the regime with at least two parents at every birth. Thus all of these births count toward its heavy width. [Five-junction certificate](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/pure_witness.json) · [Earlier source and parent audit](../GROWTH-CONTINUES-20261119-001/starts.md)

## The rule for a turn

At a funded stage write $R$ for the residual pairs, the candidate pairs in no large legal group. Each $\{a,b\}\in R$ has a unique child $e_{ab}$ containing both parents and that child's literal roster is $\{a,b\}$. Every candidate pair appears in some child. At the next stage two children can join precisely when their parents intersect. They are held together by an old junction precisely when that junction belongs to all of their rosters. [Funded stage law](../../proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md)

For distinct $a,b,c$ with $ab,bc\in R$, the pair $e_{ab},e_{bc}$ is residual at the next stage **if and only if $a$ and $c$ are noncandidates**. To escape the block indexed by $b$, a group containing both children needs a third child missing $b$ and containing $a,c$. Such a child is impossible if $a,c$ are noncandidates. If $a,c$ are candidates, some child contains them. It must miss $b$, since the only child using $a,b$ is $e_{ab}$. These three children meet pairwise and have no common parent. Any maximal extension is a legal large group.

Make a finite directed graph whose states are the two orientations of each residual pair. A transition $(a,b)\to(b,c)$ is admitted when $a\ne c$ and $a,c$ are noncandidates. This is the complete test for two consecutive residual pairs to produce another residual pair under arbitrary outside growth.

**Iteration.** Replace each pair in an allowed old walk $x_0,\ldots,x_m$ by its two-parent child. Consecutive children are joined by a residual pair, by the turn test. Children two steps apart have disjoint parents. Indeed, the only further possible coincidence in $\{x_i,x_{i+1}\}$ and $\{x_{i+2},x_{i+3}\}$ would be $x_i=x_{i+3}$, making the required noncandidates $x_i,x_{i+2}$ candidates. This gives another allowed walk, one pair shorter. A periodic walk therefore persists with arbitrary outsiders. Every stage has incompatible junctions on that walk, which excludes an imposed single closing birth.

**Reading a finite walk back.** Every old walk of $m\geq1$ admitted pairs gives one birth $m$ rounds later. Two different unoriented old walks give different births. For $m=1$ the old pair is its child's roster. For $m=2$ the two distinct old pairs in that roster have a unique common endpoint. For greater $m$, the final birth names its two actual parents, the windows of length $m-1$ at the beginning and end of the walk. By induction each parent recovers its window up to reversal. The two parents have exactly one shorter parent in common, the middle window of length $m-2$. Their other shorter parents are two steps apart on the earlier lifted walk and are distinct. This identifies the joining end of each recovered window. Ordering the two windows fixes their orientations, leaving precisely the reversal of the full walk as the other choice. The no-backtracking condition excludes a nontrivial window equal to its own reversal.

In particular, two distinct first-return routes at a common state in one strongly connected component give exponentially many walks at all large lengths. If the returns have different lengths, repeat each to a common length. Append a fixed prefix of a return to fill the remainder. The first steps can be chosen different whenever the recurrent component has an internal branch. Even one cyclic component leading to a *different* cyclic component gives a linear lower bound: vary how many common-length periods occur before the passage between components.

**Exact limit of inherited two-parent walks.** Every oriented new residual pair between two old pair-children has the form $(e_{ab},e_{bc})$ for one old allowed transition. A further turn cannot attach both neighboring old pairs to the same end of the middle old pair, since those two children would meet at that end. Therefore the three old pairs must concatenate consistently. Conversely every two consecutive allowed old transitions lift to such a turn. The new directed graph restricted to pair-children is exactly the directed line graph of the old one. In particular it cannot acquire a first directed cycle using only those children. Children with more parents can generate one from scratch, as start-13 does.

## The literal six-pair check

At age six start-13 has 868 sites and 280 maximal holding blocks. Start from the ordered pair $(85,105)$. Either return continues through $178,824,85,105$ or through $179,824,85,105$. For every row below the common candidates of its two sites, counting those sites themselves, form exactly the indicated single old holding block. Every clique through the pair is therefore held, which proves that the pair really is residual on the whole stage.

| Pair | Holding block | Common candidates including the pair |
|---|---:|---:|
| 85, 105 | 82 | 52 |
| 85, 824 | 2 | 116 |
| 105, 178 | 20 | 53 |
| 105, 179 | 20 | 53 |
| 178, 824 | 81 | 120 |
| 179, 824 | 81 | 120 |

Sites 85 and 178 do not share a block, nor do 85 and 179 or 105 and 824. These three checks cover all two-step turns, including the join between consecutive returns. There are $2^k$ choices of $k$ returns. Each resulting walk starts with $85\to105$ and none of its steps is $105\to85$, even after appending up to three steps of the first return. Thus reversal identifies none of the counted walks. The reading-back proposition gives the announced bound in every round. At the previous age the full stage had nine residual pairs and zero allowed turns. The five sites in the new witness have incoming parent counts $7,7,7,7,8$. [Direct literal replay and controls](../../experiments/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/pure_turns.py)

## What the archive test decides

The exact walk test found recurrent components at ages six and seven on start-13. At age six the two components each have 36 ordered-pair states and 75 internal transitions. At age seven each has 75 states and 162 internal transitions. The screen checked 145 explicit stage rows over the sixteen fixed starts, 144 with the complete residual pairs. It also covers the remaining 00 and 04 tails symbolically. In the full-block layer every pair of sites is compatible, so there is no admitted turn. In each subsequent complete subset layer, every candidate pair participates in the legal group for its union. Prior complete counts, full source qualifications, and per-stage limits are linked in the record. [Full screen](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/pure_archive.json) · [Source panel](../GROWTH-CONTINUES-20261119-001/starts.md)

At start-03 age eight all 1,241 residual pairs give 376 directed transitions and an acyclic graph. Its longest admitted walk uses five old pairs. The complete earlier rows on 03 and 14 also have no cycle. For 14 at age eight, the additional screen certifies 9,963 residual pairs. It includes **every** residual pair with a two-parent endpoint (9,951 pairs) and checks pairs inside each of 192 raw blocks of size two through 300 for a common neighborhood contained in that block. The resulting 8,848 transitions are acyclic. Only one possible additional pair could close a cycle with a walk through this known subgraph. Sites 121265 and 159070 together with 121197 form an unheld compatible triple, so that pair is covered. Cycles involving two or more other residual pairs remain possible.

For the two-parent endpoint calculation, if $e_{cx}$ and a different child $P$ meet at $c$, no other child uses both $c,x$. Their pair is therefore residual exactly when $x$ is incompatible with every member of $P\setminus\{c\}$. Any compatible counterexample $y$ provides a child through $x,y$ missing $c$ and hence an unheld triple. This equality makes the stated subgraph coverage exact even without a census of all 10,049,025,081 candidate pairs on 14.

The absence of a recurrent turn does not decide closure. For instance, the funded partnered start of order three has no residual pair at its first stage and grows indefinitely, while a single held block closes. A cone on a four-cycle with its four triangular facets held supplies the converse control. Its residual turns circulate around the four-cycle even with the universal cone site present. The cone has trivial filled fundamental group and its universal site prevents every everywhere-displacing renaming. Both negative and positive controls were replayed under the literal group rule. [Partnered theorem](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md)

There is also a simple exact test for a full block in the immediate successor of a connected pure stage. A universal site common to all residual pairs is in every unheld maximal group by maximality. All children then use that site. Conversely, if all children use a site, every old site participates in some group, so this site is universal and lies in every residual pair. The last archived stages of 06, 07, 12 and 15 each have zero universal sites. This excludes an immediate common parent there. A pairwise-intersecting successor can still have no common parent.

## Replay

The short certificate rebuilds start-13 directly from the committed literal start. The all-stage screen can also use the digest-checked physical exports from the previous study. The figure requires neither a count nor an enumeration of the age-seven groups.

```sh
.venv/bin/python -B experiments/HEAVY-GROWTH-20261119-001/*/pure_turns.py
.venv/bin/python -B experiments/HEAVY-GROWTH-20261119-001/*/pure_turns.py --screen --exports /var/tmp/hub-sample-20261119
```

[Source and reconstruction of the physical exports](../HUB-GUIDED-SAMPLE-20261119-001/inputs.md)
