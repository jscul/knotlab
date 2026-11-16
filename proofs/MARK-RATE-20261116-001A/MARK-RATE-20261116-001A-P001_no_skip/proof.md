# No single skip: a member at every level

`MARK-RATE-20261116-001A-P001`, epic `MARK-RATE-20261116-001`, 2026-11-16. Written by Claude; the advisor model reviewed the argument
before the predictions were frozen (`research/MARK-RATE-20261116-001/advisor_design_answer.md`). Referee pending. Checks: `check.py`
(result in `result.json`). Setting, groups and block steps as in Theorem F
([proof](../../BLOCK-REACH-20261116-001A/BLOCK-REACH-20261116-001A-P001_forgetting_blocks/proof.md)): group j holds O_(k+j), the
side subtrees of the other children of O_(k+j−1), and the knots placed at O_(k+j−1); groups j − 1 and j share O_(k+j−1); a mark on
O_(k+j−1) belongs to group j − 1 only.

## Signature sets

For an orbit O of type t, marks are finitely many distinctions with prescribed values.
- An **up signature** of O is the set of O's assignments consistent with marks outside O's proper subtree (on O itself allowed),
  under the knots not placed at O or below.
- A **below signature** of O is the set of O's assignments consistent with marks strictly below O, under the knots placed at O or
  below.

U(t) and below(t) are the families of all nonempty such sets, over every finite marking, at the stable depth.

**Lemma S (closure).** The families are computed exactly by the recursion in `marks.py`. A below signature with marks below O is
the join, through O's block, of one down signature for each child orbit; a down signature allows pins on the child's own
coordinates as well. An up signature of a child is the join, through its parent's block, of an up signature of the parent with one
down signature for each other child, then pinned on the child's own coordinates. This follows from Theorem W: the blocks meet only
parent to child, so the marks in different parts interact only through the orbits they share. With r₀ = 0 the feasible sets are
the same at every remaining depth, so the families at any finite depth are subfamilies of these. The recursion takes, for each
type, the union over every context in which the type occurs, so U(t) is a superset of the achievable up signatures in any one
context.

## Theorem M (no single skip)

*Suppose r₀ = 0. Suppose that at every block step t → c, with relation T, every X in U(t) and every Y in below(c) meet T,
after X is cut to the values that extend through T to a feasible child and Y to T's image of the unmarked up-feasible values. Then
no bond skips a group. So for every k, every s ≥ 1 and every N ≥ k + s, L_N(k, s) ≥ s + 1.*

*Proof.* Let B be a bond with u at level k and v at level k + s, and suppose group i (1 ≤ i ≤ s − 1) holds no member of B. Let L be
the members in groups below i and R those in groups above i. By Theorem W, an assignment σ of B is allowed exactly when some x in
X(σ_L) and some y in Y(σ_R) satisfy (x, y) ∈ T_i, where:
- X(σ_L) is the up signature of O_(k+i−1) given σ_L;
- Y(σ_R) is the below signature of O_(k+i) given σ_R (R lies strictly below O_(k+i), since group i introduces O_(k+i));
- T_i is the step, with the side subtrees unmarked because they belong to group i.

Every pair in X × Y ∩ T survives the cut, so the cut changes nothing when the two sets meet. If a cut is empty, the marks of that
side are realised by no state, so that side is constrained by itself. That side is a proper subset of B (the other side is
nonempty), which contradicts B being a bond. Hence every σ is allowed, and B is free, a contradiction. So each of groups 1, …, s − 1
holds a member, and |B| ≥ 2 + (s − 1). A target outside u's subtree is handled as in Theorem F. ∎

*A failure says nothing definite.* The families range over all markings, while a bond needs both of its parts free. A pair that
misses T may come from a constrained part. A real skip may also cost members elsewhere: the half-rate patterns skip levels, and
their bonds still pay for it.

## Corollary M (computed; `research/MARK-RATE-20261116-001/run_census.py`)

The run covers the 779 small-orbit census descriptions with r₀ = 0, with 120 s each. Six went over the limit: 2 direct, 1 other and
3 undecided.

| Small-orbit descriptions | Pass (no level can be skipped) | Fail | Over the limit |
| --- | ---: | ---: | ---: |
| cyclic rulers, r = 1 | 31 | 0 | 0 |
| cyclic rulers, r = 2 | 55 | 48 | 0 |
| cyclic rulers, r = 3 | 0 | 18 | 0 |
| acyclic rulers, r = 1 | 197 | 0 | 0 |
| acyclic rulers, r = 2 or 3 | 0 | 48 | 0 |
| half-rate | 0 | 43 | 0 |
| no bond, other, undecided, direct | 289 | 44 | 6 |

The 31 with r = 1 already grew one member per level by Theorem F. So 55 cyclic rulers with r = 2 now have L_N(3, s) ≥ s + 1 at
every depth, where Theorem F proved only 1 + ⌈s/2⌉. In all, 86 of the 152 cyclic rulers with r₀ = 0 provably grow one member per level
at every depth. With Lemma U, those 86 have L_N(3, s) ∈ {s + 1, s + 2} for s ≤ 4 at every N ≥ 9.

The test is sound but coarse. It fails on every acyclic ruler with r ≥ 2, although these grow one member per level
(`RULER-LEVEL-20261114-001`): their bonds hold a member in every group, but the families also contain markings no bond uses.

*Checks.* 360 real signatures were checked (`gate_marks.py`): 180 up and 180 below, from random markings at depth 7 on 30
descriptions, computed by SAT from explicit placements. All lie in the computed families. Consistency gates
(`research/MARK-RATE-20261116-001/census_marks.json`):
- all 511 descriptions with r = 1 pass;
- none of the 43 half-rate descriptions passes;
- no passing description has a census value below s + 1.

## What is not proved

- **s + 2.** The advisor's thin families (one mark per group) or least-mark costs propagated by min-plus would give it, and would
  make failures quantitative. Neither is built.
- **The 66 cyclic rulers that fail,** and the acyclic ones with r ≥ 2 by this route. A refinement would require each part to be
  free.
- **Upper bounds for s > 4.**

## Dependencies

- `BLOCK-REACH-20261116-001A`: the groups, block steps, Theorem F's count and Lemma U.
- `DIRECT-REACH-20261115-001B`: Theorem W and the block computation.
- `LEVEL-REACH-20261114-001`: the census.
