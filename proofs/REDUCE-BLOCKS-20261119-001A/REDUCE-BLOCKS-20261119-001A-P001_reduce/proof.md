# The growth reads only the down-closure of the live-neighbour sets

Status: Partial

Ticket `REDUCE-BLOCKS-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `MERGE-BURST-20261119-001#2`.
- **What it builds on.** `DOUBLE-IDENT-20261119-001A-P001`: Lemma M, the identification for multigraphs, and the structural implied
  test. `DEAD-CAP-20261119-001A-P001`: the branch system.
- **What it proves.** The hypothesis MERGE-BURST's two readings rest on.
- **How it was checked.** The advisor checked the statement before the freeze. Its points are folded in: shortage, the full
  invariant of the induction, connectedness, H(X)'s three constraints, and class membership as a per-stage premise. `hublib.py`,
  `job.py` and `merge.py` are the machine check, a separate algorithm in the same task.

## Setting

A start X is a connected presentation in which each distinction lies in one or two knots. Its live knots are those with open ≥ 1.
The **live-neighbour family** is F(X) = {N(w) ∩ live : w a knot of X}. Its **down-closure** is D(X) = {S ⊆ live : S ⊆ B for some B ∈
F(X)}. A **maximal block** is a set of F(X) with at least two points that lies inside no other.

## Lemma R (what the growth reads)

From round 1 on, the cheapest growth reads X only through three things:
- its live knots;
- their open counts;
- D(X).

Two starts that agree on these three grow identically from round 1: the same junctions, with the same parents and fresh counts,
round by round.

*Proof.*
1. **Round 1.** Two live knots u, v are candidates exactly when {u, v} ∈ D(X). A set S has a common neighbour exactly when
   S ∈ D(X). Valid sets are the sets of three or more live knots whose pairs lie in D(X) and which do not, so they depend only on
   D(X). So do the maximal valid sets and the candidate pairs they leave uncovered: the groups. Each live knot gives one loose
   distinction to each of its groups. Its leftover loose distinctions become offshoots, and how many there are is read from its open
   count.
   - **Shortage is a stall.** A live knot in more groups than it has loose distinctions has a shortage. The growth then stalls: no
     junction is made, and there is no tie-break. Whether a knot is short is read from its groups and its open count.
   - **Which loose distinction a group takes is immaterial.** A knot's loose distinctions are interchangeable, by the symmetry of
     DOUBLE-IDENT Lemma M, step 1.
2. **No round-0 knot stays live.** Every loose distinction of a round-0 knot is taken by a group's junction or an offshoot. A dead
   round-0 knot has no loose distinction, so it is no junction's parent.
3. **Later rounds read only parents.** A new junction shares exactly one distinction with each parent, that parent's loose
   distinction, and holds only fresh distinctions besides (DOUBLE-IDENT Lemma M, step 3). So at round t ≥ 1 the live knots are
   round t's junctions. Their neighbours are their parents, round t − 1's junctions, or round-0 live knots when t = 1.
   - Two of them are candidates exactly when they share a parent.
   - A set of them has a common neighbour exactly when its members share a parent.
   - So the state after round t is a function of (live, open, D(X)). Its junctions, each junction's parent set, and each junction's
     fresh count are all such functions, by induction. Round t + 1's groups are a function of that state.
4. **Fresh counts** are max(d, 3 − p, 1), or d when the junction is implied.
   - The demand d is the junction's number of groups next round, a function of the parent incidence.
   - The parent count p is read off the groups.
   - The implied test is structural: the junction takes every loose distinction of the presentation. In a connected presentation
     this equals GF(2) implication (DOUBLE-IDENT Lemma M(4)). The loose distinctions are exactly those of the live knots, so the test
     reads only the groups and the counts.
5. **Relays** are not a separate rule. They are the fresh counts of finished pieces (RELAY-IDENT Theorem 4), so item 4 covers them. ∎

**Hypothesis.** X is connected, as every start and every stage of a growth is. Connectedness is used only in item 4.

## Corollary 1 (the hub realization)

Let H(X) be the start built in four steps:
1. X's live knots, with the same open counts;
2. one dead hub per maximal block of X, sharing one distinction with each point of the block;
3. dead connectors that chain the hubs, with each live knot in no block hung on its own connector, so that H(X) is connected;
4. extra distinctions shared between dead knots, until every dead knot has three places.

**Its blocks.** H(X) obeys three constraints, as the advisor asked:
- one connector per live knot in no block;
- extra shares only between dead knots;
- a dead knot's places are at least three. A hub of a large block may have many more; no cap is needed.

No live knot of H(X) touches a live knot, and no connector touches two. So the sets N(w) ∩ live with two or more
points are exactly the hubs' blocks, X's maximal blocks. Then D(H(X)) = D(X). The live knots and open counts are X's by
construction. By Lemma R, X and H(X) grow identically from round 1.

## Corollary 2 (reading a stage through its maximal blocks)

By the stage identity (BREAK-EDDIES, refereed), a stage taken as a start is a start. Suppose its maximal blocks satisfy the class:
- no two sharing two points;
- no cycle of three of them;
- no stall;
- at least two loose distinctions.

Then H(stage) is in the proved class, and its growth is the stage's future. Class membership is a premise checked for each stage,
not a consequence of the lemma. DOUBLE-IDENT's identification and DEAD-CAP's branch
system count that future exactly. Neither uses a bound on places.

So MERGE-BURST's readings are proved:
- the closed case, a block of 9;
- start-04, a block of 781, closing after about 2⁷⁸¹ junctions.

## What the machine check must show (frozen before it runs)

| # | Check | Falsified by |
| --- | --- | --- |
| H1 | On every touch-census arrangement (26,441, stalls included), X and H(X) have equal per-round (parents, fresh) multisets for rounds 1 to 6, and stall or close at the same round | one arrangement |
| H2 | The same on 1,000 random starts of 6 to 13 knots within seven places, with no class filter, to round 6 or the child's limits; comparisons stopped by the limits counted apart | one start |
| H3 | The same on stages 1 to 6 of EXPLOSIVE's 16 explosive starts, 3 rounds each, against each stage's H | one stage |

## Validation

To be filled from the run.
