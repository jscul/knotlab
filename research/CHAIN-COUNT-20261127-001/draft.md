# Draft (for the advisor): the chain counting on node cores

Setting. A start of the late-views class whose pieces' cores finish (the node core: core births built by Lemma R's round
rule from the round-1 groups and offshoots; rank 0 = knots, rank 1 = round-1 groups and offshoots O_q = {w, q} for each
pendant point q of a live knot w; a pendant point q carries R(open_w) endless chains). An EXTENDED NODE is x = (C, a):
C a core node of rank >= 1, a a vector of lengths a_e >= 1 on a set E(a) of chains based at points of C; round |x| =
rank(C) + sum(a). Parents P(x): the shortenings x - e (e in E(a); drop e at length 1) and the lifts (T, a) for T a core
parent of C whose points hold every base of E(a) (for rank(C) = 1, the core parents are knots and appear only when a = 0).
Pure = a = 0 (a core node).

Target theorem. Without chained twins (two core nodes of one rank sharing two parents C, D with a chain base in the
points of a common parent of C and D), ordinary growth's round-t births are the extended nodes of round t, with parents P
and fresh counts children(C) + chains(points(C)), plus the relay of a finished chain-free piece.

Reduction (done, in the style of CHAIN-IDENT's proof of Theorem 1): by Lemma R the step from round t to t + 1 is the round
rule on round t's births plus one offshoot for each fresh distinction a birth has beyond its demand. So the theorem follows
from

  LEMMA X (order lemma for extended nodes). For every t >= 1, Lemma R's round rule applied to the extended nodes of round
  t (sharing a parent = P(x) meets P(x')) returns exactly the multiset {P(y) : y of round t + 1, |P(y)| >= 2},

and the fresh table: the extended nodes with one parent are exactly O_q and (O_q, {e: n}) (shown: a node of rank >= 2 has
points the union of its parents' points, so some parent holds q); d(O_q) = open_w - 1 even with cells (O_q's only parent is
w, so every family holding it shares w; its children are the uncovered pairs with the other rank-1 nodes at w), and
d((O_q, e:n)) = 1 for open_w = 1 or 2; so max(d, 3 - p, 1) = d + r in every case, as in CHAIN-IDENT's table.

Lemma X, what is shown:
- Sharing types for two round-t extended nodes: (S1) same core, a' = a - d_e + d_e'; (S2) core of one a core child of the
  other's, a' = a - d_e; (S3) same a, cores share a core parent holding B(a). So in a family that pairwise shares, the
  chain totals |a| take at most two consecutive values.
- Pure part (R2's argument transported): a non-pure node has at most one pure parent (C, when x = C + e at length 1), and
  if it has one, C holds a chain base. If a family without a common parent held two pure members A, B, it would hold two
  non-pure members C + e, D + e' with C != D both parents of A and B, sharing a non-pure parent, which must be (F, e:1) with
  F a common core parent of C, D holding base(e): chained twins. So, without chained twins, no group mixes two pure
  members, pure groups stay maximal, pure pairs stay uncovered: the pure part of Lemma X is the core's construction.
- (K1) P(y) pairwise shares, except possibly two lifts (T, b), (T', b), which share exactly when
  (*) T and T' have a common core parent holding B(b).
- (K2) If |P(y)| >= 3, P(y) has no common parent (case analysis on |E(b)| = 0, 1, >= 2).
- Within one chain total (case A): a family that pairwise shares lies in one core with vectors c + d_e (common parent (C, c),
  so no group) or c - d_e (the shortenings of (C, c)), or in one vector with cores pairwise sharing through parents holding
  the bases.

Open: (K3) every P(y) with E(b) != {} is maximal among families that pairwise share (and, for |P(y)| = 2, lies in no
group); (K4) every group and uncovered pair with a non-pure member is some P(y); and whether (*) can fail without chained
twins.

Computed (ext.py, static, no growth): Lemma X holds through round 10 on all 678 tree-piece sample starts without chained
twins and fails on all 56 with them; (*) holds on all 678, fails on 32 of the 56, always at a node of rank at least the
least rank of the chained twins.
