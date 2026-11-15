# The ruler across levels on patterns with no cycle of knots

Proof note of `RULER-LEVEL-20261114-001A` (epic `RULER-LEVEL-20261114-001`; G17, with G1), 2026-11-15, written by Claude after
`LEVEL-REACH-20261114-001`'s census and its referee, and checked cold by the advisor model (`research/RULER-LEVEL-20261114-001/
advisor_answer.md`, whose repairs are taken). The canonical K1–K3 test is unchanged; every knot is a three-place not-all-equal knot on
three distinct distinctions. **Refereed** (RULER-LEVEL-R1, confirmed with fixes; the complete formula below is its).

## Setting

Distinctions are the addresses of lengths 0 to N; each knot lies within one level or joins a level n to the level n + 1 (the
`LEVEL-REACH-20261114-001` object). The **reach** L_k(s), s ≥ 1, is the least size of a bond (a minimal non-shattered set; members
anywhere) holding an address of level k and one of level k + s. A **cycle of knots** is a Berge cycle of the knot hypergraph (two
knots sharing two distinctions included). A **descending chain** from level k to level k + s is a sequence of s knots, the i-th meeting
the (i − 1)-th, with a member at level k + i − 1 and a member at level k + i.

## Theorem A** (no cycle of knots)

If the pattern on levels 0 to N has no cycle of knots, then for every k and s ≥ 1 with k + s ≤ N, L_k(s) = D_k(s) + 2, where D_k(s) is
the fewest knots on a path of knots from a level-k address to a level-(k + s) address (D_k(s) ≥ s); in particular:
- if some descending chain joins level k to level k + s, L_k(s) = s + 2;
- if a path joins the levels but no descending chain does, L_k(s) = D_k(s) + 2 > s + 2 (*added after the referee*: e.g. knots
  {0, 00, 01}, {00, 10, 11}, {10, 000, 001} at N = 3 give a three-knot path and reach 5);
- if no path of knots joins level k to level k + s, there is no such bond.

*Proof.* By `RANDOM-FATES-20261112-001B`'s T1 (proved, refereed): in a finite Berge-acyclic 3-uniform hypergraph, two vertices at
hypergraph distance d in one component have least bond (least restricted set whose proper subsets are unrestricted, over all sets)
exactly d + 2, and vertices in different components lie in no bond. A knot spans at most one level step, so any path of knots from
level k to level k + s has at least s knots, and the distance between a level-k and a level-(k + s) address is at least s; a
descending chain gives distance exactly s. The minimum over all pairs is therefore s + 2. ∎ (The proof uses neither fullness nor any
monotonicity in N.)

## Theorem A (one tree-type placement)

A description whose only placement is ((g, plain), (h₁, appending 0), (h₂, appending 1)), with g, h₁, h₂ any automorphisms of the
binary tree of addresses, gives at every N a **full binary tree across levels**: no knot within a level; every knot has one address at a
level n and two at n + 1; every address of levels 0 to N − 1 is the upper member of exactly one knot, every address of levels 1 to N
the lower member of exactly one. Hence it has no cycle of knots, descending chains exist from every level, and L_k(s) = s + 2 for every
k and s ≥ 1 with k + s ≤ N.

*Proof.* The knot at w (length n < N) is {g(w), h₁(w)0, h₂(w)1}: three distinct addresses (by level and last letter), distinct knots
for distinct w. g is a bijection of each level, so each level-n address is the upper member of exactly one knot; v0 is a lower member
only of the knot at h₁⁻¹(v), v1 only of that at h₂⁻¹(v). No cycle of knots: the deepest address on a cycle would need two knots at or
above it, but it is the lower member of exactly one knot and the upper member only of knots reaching below it (the advisor's
argument). The pattern is connected (every address ascends to the root). Descending chains follow the tree from any address of level
k; "descendant" here is in the knot tree, not by prefix (the parent of v0 is g(h₁⁻¹(v)), not v). Apply Theorem A**. ∎

## Where it applies in the census, and where it does not

From `LEVEL-REACH-20261114-001`'s registered descriptions at depth 9 (`exploratory/census_forest.py`, computed):

| Outcome | No cycle of knots, chains at every s | No cycle, some s without a chain | With cycles |
| --- | --- | --- | --- |
| chained (ruler) | 299 | 0 | 158 |
| no bond | 0 | 170 | 18 |
| no join | 0 | 77 | 106 |
| direct | 0 | 0 | 100 |
| other | 0 | 0 | 73 |
| undecided, dead | 0 | 0 | 287 |

Every acyclic description has the outcome Theorem A** gives (a check of the code, not evidence for the theorem). Of the 457 chained
descriptions 299 are acyclic (394 of the 605 chained weight among W_R draws); 117 have Theorem A's form, so they are rulers at every
depth, not only at depth 9. All direct, other, undecided and dead descriptions have cycles of knots.

**Within-level knots can shorten the profile** (*narrowed after the referee from "cycles break the ruler both ways": every failure
shortens, none lengthens; five of the six cases are reproduced from their keys, the sixth is logged only*). Random descriptions with one
tree-type placement and one to three within-level placements (`exploratory/tree_plus_within.py`, levels 0 to 6, top level 1, s = 1..3,
80 samples): 51 rulers, 6 not ([3, 3, 4] twice, [3, 4, 4] twice, [3, 3, 3], [2, 2, 2]), 21 undecided, 2 dead; each reproduced case has a
within-level knot holding two siblings of the tree (computed, exploratory).

## Open

The 158 chained descriptions with cycles: why their reach is still s + 2 over the four levels read. The advisor's discriminator, not
tested: no cycle of knots passes through two members of one knot of the chain. Composition of joining knots is not automatic in general
(`LEVEL-REACH-20261114-001`'s referee's three-level example), so any such statement needs its own upper and lower bound.

## Checks

`check.py`: Theorem A's structure (a full binary tree across levels) on 2,000 random one-placement descriptions at N = 8, all passing;
the reach census's exact search gives [3, 4, 5] on 20 of them at N = 5, top level 1. Theorem A** rests on T1 of
`RANDOM-FATES-20261112-001B` (proved, refereed); nothing here is new beyond its application.

## Prior work

`RANDOM-FATES-20261112-001B` T1 (the program's), the knots-alone ruler (`RULER-20261111-001`) and the number line from logic
(`LOGIC-AXIS-20261107-001`); Berge acyclicity (classical). Ours: the application across levels of addressed patterns, Theorem A's
structure, the census accounting and the counterexamples. Classification: known-with-delta.
