# Growth at every depth from forgetting blocks

`BLOCK-REACH-20261116-001A-P001`, epic `BLOCK-REACH-20261116-001`, 2026-11-16. Written by Claude; the advisor model reviewed the design
(`research/BLOCK-REACH-20261116-001/advisor_design_answer.md`). Referee pending. Checks: `check.py` (result in `result.json`). Words
follow the [Intuitions glossary](../../../publication/knotlab/INTUITIONS.md#glossary) (block, orbit, descent: 16 November 2026).

## Setting

As in `DIRECT-REACH-20261115-001B-P001` ([proof](../../DIRECT-REACH-20261115-001B/DIRECT-REACH-20261115-001B-P001_every_depth/proof.md)):
addressed not-all-equal patterns placed by automaton maps, the depth-N pattern P_N, the reach L_N(k, s) (least bond meeting level k and
level k + s, members anywhere), blocks of orbits meeting only parent to child (Theorem W), and, when orbits have at most four
addresses, finitely many orbit types and feasible sets F_ρ (the assignments of an orbit that extend to its ρ levels below) that stop
changing at ρ = r₀.

**Block step.** For an orbit O of type t at level n and one of its child orbits O′, the step relation at remaining depth ρ = N − n − 1
holds the pairs (assignment of O, assignment of O′) for which the block of O can be completed with every knot placed at O holding and
every other child orbit's subtree feasible with ρ levels below it (F_ρ). It does not restrict O′ by its own subtree.

## Theorem F (forgetting along blocks)

*Let r ≥ 1. Suppose that every composition of r consecutive block steps, along every path of orbit types and at every remaining depth,
is rectangular: the product of its two projections. Then L_N(k, s) ≥ 1 + ⌈s/r⌉ for every k, every s ≥ 1 and every N ≥ k + s. If this
holds at the stable remaining depth only, the bound holds for every N ≥ k + s + r₀ − 1.*

*Proof.* This is the splicing lemma of `BRANCH-DEPTH-20261112-001A`
([proof](../../BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/proof.md), Section 2), applied to a path of
blocks. Take a bond B of P_N with a member u at level k and a member v at level k + s.

*Case 1: v lies in the subtree of u's orbit O_k.* Let O_k, O_(k+1), …, O_(k+s) be the orbits on the path from O_k to v's orbit. Group 0
holds everything outside the proper subtree of O_k, including O_k; for j ≥ 1, group j holds O_(k+j), the side subtrees of the other
children of O_(k+j−1), and the knots placed at O_(k+j−1) (a block knot may touch several children, so it sits with all of them). The
interface between groups j − 1 and j is the assignment of O_(k+j); by Theorem W no other distinction is shared, and a group's
relation is the block step from O_(k+j−1) to O_(k+j) at remaining depth N − k − j. The splicing lemma uses only the window being
spliced: if groups i, …, i + r − 1 hold no member of B, and B has members on both sides, then the parts of B on the two sides are each
free (B is a bond), the actual incoming and outgoing values of the window lie in the projections of its composed relation, which is
rectangular, so the two realising states can be joined across the window and the union is free, contradicting that B is constrained.
Hence among groups 1, …, s − 1 no r consecutive groups are free of members of B (v is in group s, so every such window has members of B
on its right, and u is on its left). So B has at least ⌊(s − 1)/r⌋ members in groups 1, …, s − 1, besides u and v: |B| ≥ 2 + ⌊(s −
1)/r⌋ = 1 + ⌈s/r⌉. The windows used start at levels ≥ k and end above level k + s, so their remaining depths are at least N − k − s + 1;
at N ≥ k + s + r₀ − 1 they are all stable.

*Case 2: v lies outside that subtree.* Let O_b (level b < k) be the lowest orbit whose subtree holds both, and follow the path from O_b
down to v's orbit. u lies in a side subtree of the first step, so in group 1, and v in group k + s − b. The same count over groups 2, …,
k + s − b − 1 gives |B| ≥ 2 + ⌊(k + s − b − 2)/r⌋ ≥ 2 + ⌊(s − 1)/r⌋. Only descending steps are used. ∎

*Remarks.* A rectangular window stays rectangular, or empty, when lengthened, so the least r is well defined, and at stable depth the
sets of r-window compositions form an eventually periodic sequence: if none forgets before they repeat, no length forgets
("never forgets"). Rectangularity on all assignments is sufficient, not necessary (the lemma needs only the values actual states take
at the two cuts). Where Theorem W already shows no tie at any depth, the bound is max(3, 1 + ⌈s/r⌉).

## Lemma U (depth-9 bonds hold at every depth)

*If a set B of addresses lies at levels at most m, its projection in P_N (the assignments of B that extend to a state of P_N) is the
same for every N ≥ m + r₀. In particular a bond of P_9 with every member at level at most 9 − r₀ is a bond of every P_N, N ≥ 9, and
L_N(k, s) ≤ L_9(k, s) for that (k, s) and every N ≥ 9.*

*Proof.* By Theorem W the projection onto B is computed block by block over the orbits at levels ≤ m, and the pattern below level m
enters only through F_(N−m) at the orbits of level m, which is F_(r₀) for N − m ≥ r₀. ∎

## Corollary F (computed; `research/BLOCK-REACH-20261116-001/run_census.py`)

Of the `LEVEL-REACH-20261114-001` census's alive descriptions, 786 have orbits of at most four addresses (r₀ = 0 for 779, 1 for 7).
The least forgetting length at every remaining depth equals the one at stable depth in all 786.

| Census profile (depth 9, s = 1..4) | Small-orbit descriptions | Forget at every depth (r = 1 / 2 / 3) | Never forget |
| --- | ---: | --- | ---: |
| ruler [3, 4, 5, 6], no cycle of knots | 245 | 197 / 47 / 1 | 0 |
| ruler [3, 4, 5, 6], with cycles | 154 | 31 / 105 / 18 | 0 |
| half-rate [3, 3, 4, 4] | 43 | 0 / 19 / 24 | 0 |
| other: no bond of at most 10 members past s = 1 (13), [3, 4, 4, 5], [3, 4, 4, 4], [3, 4, 5, 5] | 16 | 5 / 8 / 1 | 2 |
| undecided | 8 | 0 / 0 / 6 | 2 |
| no bond | 278 | 278 / 0 / 0 | 0 |
| direct (constant) | 42 | 0 | 42 |

So every small-orbit ruler and half-rate description, 6 of the 8 undecided ones and 14 of the 16 others grow at least linearly at
every depth:
L_N(3, s) ≥ 1 + ⌈s/r⌉ for every s and N. Of the 46 that never forget, the 42 direct ones are bounded at every depth
(`DIRECT-REACH-20261115-001B`), and 4 are open (census profiles [3, 4, 4, 4], [3, 4, 5, 5] and two partly undecided). No small-orbit
description is known both to never forget and to grow.

By Lemma U every decided depth-9 value of the 786 is also an upper bound at every depth N ≥ 9 (all their depth-9 least bonds lie within
levels 9 − r₀). For s = 1..4 the reach at every depth N ≥ 9 therefore lies between 1 + ⌈s/r⌉ and the depth-9 value; the gap is 1 in
1,083 of the 1,596 ruler cells and 148 of the 172 half-rate cells, 2 or 3 in the rest.

*Checks.* 100 composed window relations at depth 7 equal SAT projections of the sub-pattern they describe (every knot placed under the
upper orbit and not under the lower one), and no decided census value is below the bound (`gate_forget.py`); the projections onto 158
depth-9 least bonds of 40 descriptions are equal at depths 9, 10 and 11 by SAT (`gate_upper.py`).

## What is not proved

- The exact rate. The lower bound is one below the census's rulers (s + 1 against s + 2) when r = 1, and its rate is 1/2 or 1/3
  when r = 2 or 3, while the census reads one member per level for every ruler over s = 1..4. Cyclic rulers forget more slowly than
  acyclic ones (r = 1 in 20% against 80%), so for them the bound proves growth but not the ruler's rate (backlog B180 stays open).
- Upper bounds for s > 4: Lemma U carries depth-9 bonds to every depth, not to every distance.
- The four small-orbit descriptions that never forget and are not direct.

## Dependencies

`BRANCH-DEPTH-20261112-001A` (the splicing lemma), `DIRECT-REACH-20261115-001B` (Theorem W and the block computation, checked against
SAT), `LEVEL-REACH-20261114-001` (the census and its pattern builder).
