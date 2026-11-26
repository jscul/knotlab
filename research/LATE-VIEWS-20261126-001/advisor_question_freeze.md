I am about to freeze a prediction and would like a colleague's critical view before I do. Please answer in prose, under 900 words, and say plainly where you think I am wrong.

## Setting

A growth starts from a finite set of "knots" (each a set of distinctions; a distinction lies in one or two knots). Each round, live knots (knots with loose distinctions) that share a neighbour join, each giving one loose distinction to the new knot, and new knots receive fresh distinctions. A local reader sees, per round, the multiset of births read without names: sig0 = (number of parents, number of fresh distinctions), and sig1 = sig0 plus the sorted sig0 of the parents. A start's view settles at K when, from K on, each kind's count per round is the polynomial of degree at most D - 1 fitted through rounds K - D + 1..K (D its dimension).

Proved earlier (four identification theorems, refereed): in a class of starts, the births of round t are the connected sets of t + 1 points of an extended map X+: points are the live knots plus s = open - d "pendant points" per live knot, where d is its number of round-1 groups; each pendant point carries 0, 1 or 2 endless chains (as open is >= 3, 2, 1); blocks are N(w) & live for every knot w. A birth's parents are its points whose removal leaves it connected and holding a knot; its fresh distinctions are its outside neighbours. Under not-all-equal, a finite piece (no chain) "relays": the set of all its points gets one fresh distinction, and a point with two chains hangs from it. Under parity it closes when it is the start's only piece.

## What I built (late.py), and what it found on the starts of up to five knots

The finite part of each piece (live knots and pendant points: the core) is listed once. A connected set of the extended map is (C, E, a): a connected set C of the core holding a knot, a set E of the chains that leave C, and lengths a_e >= 1. Its kind depends only on (C, E) (for sig1, also on which chains have length exactly 1), so round t's count of each kind is a finite sum of binomial coefficients binom(t - size(C), |E| - 1). Nothing is grown.

Two extensions beyond the proved class, found by exploration on the census of up to four knots and kept:
1. Blocks are read as their distinct maximal sets (the refereed Lemma R says the growth reads only their down-closure). This takes in starts with two knots having two common neighbours.
2. Each round-1 group of three or more live knots (a clique of the "share a neighbour" relation that no block holds; the engine's round-1 groups) is a GROUP CELL: a valid set holds one knot of it or none, or all of it; its size is its number of points less g - 2 for each whole cell of g knots (a group is born in round 1); parents are valid subsets of size one less (one point removed, or a whole cell cut to one of its knots); fresh distinctions are its ways to grow by one (an outside point, the rest of a cell it meets once, a chain step). Blocks inside a cell are dropped. A block meeting a cell in m >= 2 knots is read as m - 1 filled cycles; any other cycle of the incidence graph puts the piece outside the predictor (rings: reported, not predicted).

Results, every round to 24, both readings, every census start up to its symmetries:
- Up to four knots: 181 of 181 starts of a dimension predicted and agree in every round.
- Five knots, not-all-equal: 1,554 predicted (1,547 of a dimension, dims 1 to 4, and 7 bursting starts labelled unread), all agree every round; 16 not predicted (a piece with a cycle: 1 dim 1, 8 dim 2, 3 exponential, 4 unread); 1,587 stall.
- Five knots, parity (the same predictor with the parity relay rule): all 1,547 predicted agree, including the 463 that close.
- Negative controls (five knots, not-all-equal): with the relay removed 698 starts differ; with the cells removed 986 differ (all of dimension 3 and 4 have a group cell); the not-all-equal predictor applied to parity growths fails on all 470 that close.
- A static settling bound follows from the formula: every count is a polynomial from round e0 = the largest size of a valid set (the round at which one birth holds a whole core, plus relay offsets) in sig0, and from e1 = max(size + |E|) in sig1, so K <= max(e + D - 1, D, 3). It holds on all 1,547 and 1,077 starts of a dimension, with equality in 742 (48%) and 272 (25%), slack at most 4 (5 with parents). An earlier study's bound from the largest block failed; another's held only for late starts.

## What I propose to freeze

Held-out: a fresh seeded sample of 2,000 six-knot census starts (82,656 in all), disjoint from 3,000 sampled earlier, grown to round 24 under both knot laws (being grown now, not opened).
P1. Every start the predictor accepts agrees with its grown view in every round read, in both readings, under both laws.
P2. Coverage reported, not predicted: the share of non-stalling starts accepted.
P3. The three negative controls fail on the held-out sample as they did on five knots.
P4. The static settling bound, reported as a consequence of P1 (it cannot fail where P1 holds), with its tightness.
Stop: one accepted start whose grown view differs in any round, in either reading or law; or none.

## Questions

1. Is P1 a real test, or is the predictor the growth in disguise? What would make it more than a re-implementation? (It reads the start's finite map once and sums binomials; the engine grows knots.)
2. The cell rule is a hypothesis found on small starts. Where would you expect it to fail first at six knots (two cells sharing a knot? a block meeting a cell in two knots? nested cells? cells meeting chains?), and should I stratify or enlarge the sample there?
3. Should I extend to pieces with a cycle (the unrolled cover, a transfer matrix along the ring, as you suggested before) before freezing, or freeze the tree case and do rings next?
4. Scaffolds: the readings, the census weighting with its seed, the knot law (swapped), and the 24-round horizon. Which should be swapped before claiming anything about the model, and how cheaply?
5. Is there a known mathematical object here (a known count of connected subsets of a tree with rays, polymer or animal enumeration with marked rays, cluster expansions) I should cite?
