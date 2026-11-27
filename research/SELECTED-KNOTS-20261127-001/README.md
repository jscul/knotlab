# Which second-layer knots does growth itself select?

Epic `SELECTED-KNOTS-20261127-001`, at the coordinator's go-ahead after the third-layer referee. A check by the thread,
not a registered study; computed. The sections down to "Frozen" were committed before the frozen runs.


> **Referee R1: refuted, three Blocks** ([report](referee-R1/report.md)). **Block:** "the tree's nodes are the knots
> growth selects, meeting only as a tree": on the three-ring start of rings of four, the same nine whole-held places
> (six families, three rings) support eleven minimal relations, all passing K1 to K3, and two independent sets of four
> that give the same 32 states: the tree, and a set with three four-place knots (p1, q1, R2, R3; R1, p2, q2, R3;
> R1, R2, p3, q3) meeting pairwise in a cycle through three different ring facts; a preference for shorter equations
> would pick the tree, if growth supplied one. **Block:** the pair cost is d + 2 + 2t only for the direct route; the exact
> cost is the least sum of direct costs along a chain of families (a funded nine-knot start costs 10 against 12 at round
> 1, a seventeen-knot start 26 against 28 at round 5; `TREE-PROOF-20261127-001` states the chain form). **Block:** "every
> fact of the layer above is read by one of them": the test used the span of the knots' class facts, not one knot; on
> six five-knot rings two of seven upper class facts need more than one tree knot, though all are sums of local facts.
> **What holds:** the fixed-scale cluster result (all 6,871 family-sum costs and all 3,465 rows at each scale).
> **Narrowings:** 863 of the tree's 1,187 listed equations are two-place equalities; the frozen all-round pair
> prediction failed (positive rounds are a restriction made after); under the shortest changes 505 of 2,498 later
> stages keep a family sum; the shift is one round per two distinctions.

## The question

The third-layer referee (`THIRD-LAYER-20261126-001`, R1: refuted) showed two second-layer knots sharing a fact on three
rings of four knots, and a third-layer knot under a reading it chose. The coordinator: which second-layer knots does
growth itself select, stated so that no reading of ours chooses them; is that set fixed by the start and the law alone;
do the selected knots meet as first-layer knots do; does a third-layer fact held by no part exist without a chosen
reading?

## Reproduced first

- **The shared fact** ([`overlap.py`](overlap.py), [`overlap.json`](overlap.json)): on three rings of four knots (split
  attachments, double links), the rings' loose groups R, S, T and the first ring's two families' round-1 fresh
  distinctions P, Q take 8 joint values, two rules (R + S + T and P + Q + R, each of the four even triples), at rounds 1
  to 6 (linear algebra, checked by a solver per tuple to round 4); least flips 15, 15, 15, 13, 13 at round 5; at the
  scale of twelve all five are class facts held by no part at rounds 5 and 6, with no single-knot class fact at all;
  removing any of the 18 start laws frees only the first rule, and any of the 6 laws of the first ring's round-1 births
  only the second.
- **The chosen-reading third layer, as algebra** ([`third_algebra.py`](third_algebra.py),
  [`third_algebra.json`](third_algebra.json)): from the referee's 29 masks on the thirteen ring facts, the 18 chosen knots
  hold and generate every relation (17 independent; 4,096 states); the layer's least changes are the referee's ten of
  size 4, of rank 10; the layer-three class facts have dimension 2; the three named facts are kept by every least change
  and bound by one rule, each flipped by a change of five; the two extra knots hold. The physical carriers at round 24
  were not rerun.

## The advisor's statement ([question](advisor/question.md), [answer](advisor/answer.md))

As functions, R = P + Q: the second rule is the identity of a fact and its two halves, made a knot only because the
facts sit on carriers of different generations. Given the places (the carried facts), the knots are the minimal
relations among them and nothing else is chosen; so the whole question is which places growth supplies. With growth's
own places (each family's distinctions of each generation) growth makes copies, not knots. At the level of facts there
is one thing growth does reveal: a **tree of families**. Let d(A, B) be the least number of shared distinctions on a route
of knots from a live knot of A to one of B in the start. The least change flipping A's and B's facts and no other's is
d + 2 + 2t at round t, so at a scale k the class facts among the families' sums are the parities constant on clusters of
families joined when d + 2 + 2t ≤ k: as rounds pass, the clusters split along the tree of single linkage by d, which the
start alone fixes. Its nodes, each a fact with its children's facts, are the second-layer knots growth selects; they
meet only as a tree; and every layer-three fact of that tree is read by one of its knots.

**Checked on the witness before the freeze** ([`tree.py`](tree.py)): d is 1 within a ring and 3 to 5 between; at rounds 0
to 4 every pair cost equals d + 2 + 2t, every family sum's least flip is its least crossing pair cost, and the class
facts at scales eight and twelve number exactly the clusters less one (0, 0, 2, 5, 5 at scale eight; 2 at round 4 at
scale twelve); the tree's places (six families, three rings) and four knots leave two layer-three facts, each read by
one knot.

## Frozen

**Sets.** The 1,000 census starts, the 900 held-out starts, the 400 sampled starts and the 33 built starts of
`THIRD-LAYER-20261126-001` (`twokinds.items`), each with at least two families; rounds 0 to 4 of ordinary parity growth,
until a round stalls, closes or passes 300 distinctions; family sums read where there are at most six families.

**Predictions** ([`tree.py`](tree.py)).
- **SK1.** For every pair of families, at every round read, the least change flipping their two facts and no other
  family's equals d + 2 + 2t.
- **SK2.** For every proper set of families, the least change flipping the sum of their facts equals the least pair
  cost from a family in the set to one outside it.
- **SK3.** At the scale of eight and at the scale of twelve (the scale is a scaffold; two are run), the family sums no
  change of at most k flips form a space of dimension equal to the number of clusters (families joined when
  d + 2 + 2t ≤ k) less one.
- **SK4.** With the tree's nodes as places and a knot at each node with two or more children, every layer-three class
  fact (a parity on the places' values that their own least changes keep) is read by a single knot of the tree.

**Read, no prediction.** Under the shortest changes (the other reading of a small change): how many family sums are
class facts, round by round.

**Stop.** SK1 to SK4 as predicted: the second-layer knots growth selects are the nodes of the families' tree, fixed by
the start, revealed by rounds at a given scale; they meet as a tree, and no third-layer fact held by no part arises
from them. A failure of SK1 to SK3 is a fact or a cost the tree does not explain, to be frozen and tested on its own; a
failure of SK4 is a third-layer candidate.

**What it would not show.** Selected knots under any other choice of places (the advisor's S1 and S3), the forbidding
cuts, rounds past 4, starts with more than six families for SK2 and SK3, and a proof of the pair cost.

## What was found

All frozen runs finished ([`score.py`](score.py), [`score.json`](score.json)); no deviation. 975 of the 2,333 starts have
two or more families; 3,489 rounds were read.

- **SK2, SK3 and SK4 held everywhere.** Every proper set of families' least flip equals its least crossing pair cost;
  at both scales (eight and twelve) the family sums that no change of at most k flips form a space of dimension
  exactly the number of clusters less one, on every row read (3,465 rows at each scale); and on every start, with the
  tree's nodes as places, every layer-three class fact is read by a single knot of the tree (156 starts have such
  facts; none has one held by no knot).
- **SK1 failed on 3 starts, at round 0 only** (a held-out eight-knot start and two sampled twelve-knot starts). There
  the cheapest change flipping two families crosses a third family through two of its loose distinctions (on the
  held-out start: 6 distinctions where d + 2 = 8). From round 1 the third family's loose distinctions are used up, the
  jump costs more, and the cost is d + 2 + 2t on every pair and round read. So the tree's distance is the start's own
  distance except where a route through a third family's loose distinctions is shorter at the start.
- **Under the other reading the tree mostly does not show.** With the shortest changes as the small changes, some
  family sum is a class fact on 105 of 928 census rows, 245 of 1,268 held-out rows and 69 of 216 sampled rows at rounds
  1 to 4 (on all 86 built rows). The tree is a feature of the scale reading; the pair costs it rests on are not tied
  to a reading.

**In the coordinator's parts.** (1) The referee's witness reproduces: two second-layer knots share a fact on three
rings of four, five facts held by no part at rounds 5 and 6; the chosen-reading third layer reproduces as algebra. (2)
[Refuted by R1, Block: one presentation, not a selection.] The second-layer knots growth itself selects, with no carriers chosen by us: the nodes of the tree of the start's
families joined by their distance d, each node's fact bound with its children's. The tree is fixed by the start and
the law (by the pair costs; with the round-0 exception above); the round and the scale only choose which level is seen,
two rounds per two distinctions [R1: one round per two distinctions]. The reading is a scaffold: under the shortest changes the tree is seen on a minority
of starts. (3) The selected knots meet as a tree, never in a loop; every fact of the layer above is read by one of
them, so no third-layer fact held by no part arises from what growth selects. A third layer needs places chosen by us,
as in the referee's construction.

**Not run.** The pair cost's proof; other choices of places; starts with more than six families for SK2 and SK3; the
forbidding cuts; rounds past 4.
