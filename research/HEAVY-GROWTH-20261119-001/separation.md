# Finite separation through actual parents

**The twelve undecided rosters have exact finite-depth continuation
bounds.** Start-01's age-eleven candidate diameter is exactly three,
although age ten has diameter two. Two specified legal age-eleven births
give the lower bound, and the parent-incidence formula gives the upper
bound. The resulting funded growth stays nonclosing through age thirteen.
Start-12 also stays nonclosing through age thirteen. These finite bounds alone
leave the eventual fates open. The whole-block and returning-pair tests settle
five of the twelve historical rows, including the supplied 08 roster. [Literal screen and witnesses](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/separation_archive.json) · [Combined per-start verdicts](decision.md#each-archived-start)

## What the incidence gives

Write \(G\) for the classical candidate graph of the old stage and
\(G^+\) for the candidate graph on its actual live children in a
nonclosing funded round. Each old candidate pair is contained in a
child, either a larger group or a residual pair. Each child's parents
are a clique of \(G\). Child candidates are precisely children sharing
a parent. See the established [two projections of the incidence](../GROWTH-CONTINUES-20261119-001/persistence.md#the-two-candidate-graphs).

For distinct children \(A,B\) in the same component, use their parent
sets to read the exact classical graph distance

\[
d_{G^+}(A,B)=1+\min_{a\in A,\ b\in B} d_G(a,b).
\]

A shortest walk in the bipartite incidence starts with a parent of
\(A\), runs between old parents, and finishes with a parent of \(B\).
Distances between old parents in the incidence are twice their
candidate-graph distances, because every old candidate pair has a
child and every child has pairwise candidates. Distances between
children in the incidence are also twice their candidate-graph
distances. This proves the formula, including the shared-parent case.

For connected stages of diameter \(D\ge 2\), the next diameter is
between \(D-1\) and \(D+1\). The upper bound uses the displayed
minimum. For the lower bound, take children of two antipodal junctions.
Those children are distinct, and every parent of one is within one
step of its anchor. The reached graphs remain noncomplete for at least
\(D-2\) further stages, and has at least \(D-1\) further nonclosing
transitions. A sole implied child would have used all live junctions,
which requires a complete old candidate graph. The loose-count rule
funds each reached stage on the stated pure trajectories.

More generally, start with a set of anchors at pairwise old distance
at least \(r+1\). Every choice of their descendant chains remains
distinct through \(r\) transitions and pairwise noncandidate through
\(r-1\). Apply the same one-step inequality to any two chains. As long
as there are two anchors, the earlier noncandidate pair precludes
global implication at every required step. For instance, starts 12
and 13 have 59 and 60 distinct age-eight births guaranteed by such
anchor sets. Their radius-two packings guarantee nine and eight
age-eight births that are pairwise noncandidate. The packings are
explicit greedy witnesses. [Anchor lists and thresholds](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/separation_archive.json)

## The twelve stages

| Start | Last archived age | Precursor diameter | Last diameter | Parents in the two verified groups | Their child distance | Nonclosing through age |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 01 | 10 | 2 | 2 | 325 and 3 | 3 | 13 |
| 02 | 9 | 2 | 2 | Common universal junctions | — | 10 |
| 05 | 9 | 2 | 2 | Common universal junctions | — | 10 |
| 06 | 7 | 5 | 4 | 4 and 7 | 3 | 10 |
| 07 | 7 | 5 | 5 | 5 and 12 | 5 | 12 |
| 08 | 9 | 2 | 2 | Common universal junctions | — | 10 |
| 09 | 6 | 5 | 5 | 5 and 6 | 5 | 11 |
| 10 | 7 | 4 | 3 | 6 and 160 | 2 | 9 |
| 11 | 7 | 4 | 3 | 6 and 111 | 2 | 9 |
| 12 | 7 | 6 | 6 | 8 and 5 | 6 | 13 |
| 13 | 7 | 6 | 6 | 5 and 6 | 5 | 12 |
| 15 | 8 | 4 | 3 | 83 and 278 | 3 | 11 |

The table uses the roster law for starts 08 and 15, which are outside
the earlier canonical parity gate. The large-group witnesses are
globally maximal and unheld, so they give actual distinct births.
Seven pairs have no cross-candidate parent pair. Starts 02, 05 and 08
each have 6,040 universal junctions. Every maximal clique contains
all of them, so every two admitted larger groups meet. A noncandidate
pair of children on those three stages would therefore have to use
at least one residual child. [Source qualification](../GROWTH-CONTINUES-20261119-001/starts.md)

For diameter, the literal radius-\(r\) ball about a junction is the
union of blocks reached in at most \(r-1\) moves from any block holding
it, where a move uses a nonempty intersection of blocks. Identical
block affiliations give identical positive-radius balls. The routine
checks those balls for every affiliation and records antipodes. For
child witnesses it extends at most twelve deterministic initial choices,
choosing among small eligible pools and capping each extension at
600 choices. After the first probe it added seeds spanning candidate
degrees, looked outside currently common holding blocks, and tried
regions farther from the first support. Every retained support was
verified for legal maximality and its exact distance to the other.
The 24 records are the latest literal stage and the immediate archived
precursor for every start. [Producer](../../experiments/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/separation_screen.py) ·
[Independent literal replay](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/separation_replay.json)

## Controls on indefinite continuation

Take six groups of four, each unheld because the holding blocks are
only pairs. Consecutive groups share one junction. Make the
intersection pattern a path in one control and a cycle in the
other, with a distinct shared junction at each overlap. Both controls
have two four-parent groups separated by at least two old candidate
steps. Each produces six pure children. In the first control the
children form a six-junction path and pure growth contracts it to a
sole implied birth. In the second the children form a six-junction
cycle with pair blocks and supply two per junction. That roster
repeats under the group rule and sustains noncandidate pairs. A
width-divergent control uses two separate canonical partnered
components and also has separated large groups. Its checked live
sizes are 12, 16, 20, 48, followed by the established partnered
induction. [Control outputs](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/separation_controls.json) ·
[Canonical partnered induction](../WALL-READ-20261119-001/wall_read.md)

An induction from distance would need to supply two legal descendant
supports at each step whose minimum parent distance is at least the
current distance between the selected children minus one. The
one-step support tests impose no such condition on the next pair of
groups. The shrinking path realizes the loss in the general bound.

Pure evolution can also lose distinctions between reached rosters.
Take the candidate graph of two four-junction cliques sharing a
single junction. Use all pair blocks in one roster. In the other,
replace the three pair blocks on the three unshared members of the
first clique with their triple. Every block in both rosters is a
proper subset of a maximal clique. Both have the same supply, the
same two unheld four-parent births and no residual pairs. They reach
the same nonclosing two-junction roster. The control builds a funded
predecessor for each input using the listed holding blocks as the
preceding junctions and verifies the prescribed births by literal
incidence. Every reaching birth has at least two parents. This
collision rules out a bijection argument on pure reached states.
[Explicit predecessors and common successor](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/separation_controls.json)
