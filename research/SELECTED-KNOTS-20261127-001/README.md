# Which second-layer knots does growth itself select?

Epic `SELECTED-KNOTS-20261127-001`, at the coordinator's go-ahead after the third-layer referee. A check by the thread,
not a registered study; computed. The sections down to "Frozen" were committed before the frozen runs.

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
