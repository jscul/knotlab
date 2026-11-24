# Can a knot tell its parents from its children by what is built near it? What stands

Epic `PARENTS-FROM-HOLDERS-20261124-001` (the first step of sub-goal B325; goals G5 with G18), closed 2026-11-24, at the
owner's request of that day. One frozen study, computed, scientific referee pending.
[Ticket A: result](../PARENTS-FROM-HOLDERS-20261124-001A/results.md) ·
[pre-registration](../PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md) · [referee hand-off](referee_handoff.md) ·
[advisor review before the freeze](advisor/README.md) · [the thread's checks](checks/thread_checks.txt)

## The answer

Births made one at a time build what the complete rounds build if each birth records its parents. The two holders of a
shared distinction do not say which of them is the parent. The owner asked for the first step of the open question:
search the structures already built for places that are alike within d holder steps, one leading to a parent and one
not, and stop at a rule that recovers the parents or at a pair no bounded reading tells apart.

1. **The search ends at the second stop.** In the half-built states that arise when births are made one at a time, there
   are places to a parent and places to a child that a renaming of the whole structure exchanges, under every law tried.
   No look at the structure tells them apart, at any distance. The smallest such state has two knots: a knot and its first
   offshoot, each with one shared place and three loose ones.
2. **On structures built by complete rounds it depends on what a short knot leaves behind.** Where it retires, its barred
   place is a mark, and a rule looking two holder steps out recovers every parent. Where it makes offshoots, nothing marks
   the two sides, and the distance needed is exactly one less than the round: a proof by hand, by the advisor, confirmed at
   every round to twelve and by the thread's own program. Under a fixed three with waiting and under ordinary growth the
   distance needed grew with the round as far as the search went.
3. **One finished structure keeps no trace of its order.** The lone four-place knot under ordinary growth stops after four
   rounds as 16 knots that all look alike; a renaming swaps the start knot with one of its offshoots.

So a law that makes births one at a time cannot find the parents from the structure alone in every state it meets:
something has to be written. The sub-goal as it was worded, a law with no record at all, is closed off for such laws. What
is left of it is how little has to be written.

Eight predictions and three checks of the code were frozen. The checks hold. Two predictions fail: that a rule exists on the
whole first population where a short knot retires (it exists on complete rounds and not on the half-built states), and
that no whole structure has a renaming exchanging a parent place with another (the finished structure above does).

## Scaffolds, and what survived their swaps

| Scaffold | Swapped for | Survived? |
| --- | --- | --- |
| What counts as "everything within d holder steps" | two coarser looks | Yes: no least distance changes. |
| The structures searched | the same starts grown to about 2,000 knots or twelve rounds, the thread's addition | The finding on half-built states does not depend on it; the findings on complete rounds are stated with the count of places whose look reaches neither a start knot nor a member. |
| The laws that built the structures (A104, A224) | four laws | The answer differs by law, and the result says how. |
| The record of parents (A242) | used only as the answer checked against | Not swapped: it is what the study is about. |

## Assumptions relied on

A242 (every birth writes its parents), with a history line for this study; A104 and A224 for the laws.

## Limits

Finite and computed: four laws, twenty starts, distances 1 to 6, structures of up to about 2,000 knots. That no fixed
distance is enough is proved for one law and is a trend over eleven or twelve rounds for two others. The test for
renamings of whole structures covered 8 of the 20 final structures as registered, and the last round under its bound as
an addition. Whether one written mark per knot would be enough was not tested.

## Final report as sent (2026-11-24 22:47 UTC)

The first step of B325 has reached its stop and is closed, referee pending. **It ends at your second stop: there are pairs that no reading of the structure tells apart, so a law that makes births one at a time cannot find the parents from what is built alone.**

- **Half-built states can hide the parents completely.** After the first birth from a lone four-place knot there are two knots, each with one shared place and three loose ones, and nothing in the structure says which came first. The search found such pairs under every law: a place leading to a parent and a place leading to a child, exchanged by a renaming of the whole structure. These are the states in which the guard has to decide.
- **On structures built by complete rounds it depends on what a short knot leaves behind.**
  - Where it retires, its barred place is a mark, and a rule looking two steps out gives every one of about 18,000 places correctly.
  - Where it makes offshoots, nothing marks the two sides. The advisor proved by hand before the freeze that the distance needed is then exactly one less than the round; the search confirmed it at every round to twelve, and so did a separate program of my own.
  - Under a fixed ration of three with waiting, and under ordinary growth, the distance needed grew with the round as far as the search went. That is a trend over eleven or twelve rounds, not a proof.
- **One finished structure keeps no trace of its order.** The lone four-place knot under ordinary growth stops after four rounds as 16 knots that all look alike. A renaming swaps the start knot with one of its own offshoots.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the search for look-alike places, one to a parent and one not | **Status:** Successful | It reached the stop you set, with exact pairs; two of my predictions failed and both failures are informative. |
| Local direction — doing without the record of who was made from whom | Continue, reworded | No record at all is closed off for births made one at a time; what is open is how little has to be written. |
| Broader exploration — growth laws compared | Known alternatives | The fold study's cheapest laws are being costed partly by how much of this record they use. |
| Long-term goal — G5 Dynamics, with G18 Comparing growth laws | Obstruction learned | The before and after of a growth is not always in what it builds: half-built states, and one finished structure, do not hold it. |

The two failed predictions: I expected a rule on everything already built where a short knot retires, and it exists only on complete rounds; and the advisor expected no finished structure to have a renaming that swaps a parent with a child, and one does.

**Next step:** Research directions — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Parts that meet again, the fold study | 3/3 — the first reader the growth makes, if one exists | 3/3 — frozen; its engine is being written | Its registered runs → its registered stop | Selected · started |
| 2 | The least record: how little has to be written for the parents to be found | 3/3 — says what "the logic comes before time" costs in these laws | 2/3 — the search program exists; the mark has to be chosen | Give each knot one mark, set when it has made its last birth, and rerun the search on the half-built states → stop at a distance with no look-alike pair, or a pair the mark does not separate | Alternative · deferred |
| 3 | A proof that no fixed distance is enough under a fixed three with waiting and under ordinary growth | 2/3 — turns two trends into theorems | 2/3 — the proved case shows the method | Find a pair that stays alike until the look reaches the live roster → stop at a proof or a rule | Alternative · deferred |

1. Already running at your request.
2. This is B325 after its first step; I have added the result and this next step to its entry. It needs your go-ahead only in the sense that the fold study and the copier lead are ahead of it.
3. Would settle the two laws the search left as trends.

**STOP on this objective.** You asked for the first step only, and it is done.

**Corrections:** none.
**Goals:** one checkpoint row (G5, G18: obstruction learned); no goal changed. Sub-goal B325 has a note with the result and its reworded next step.
**Assumptions:** no new entry. A history line on A242: the record of parents cannot be replaced by any look at the structure in every state; whether a smaller record would do is untested. Still uncommitted in the tracker, with the earlier ones.
**Scaffolds:** what counts as "everything within d steps" was swapped for two coarser versions with no change. The structures grown further were my addition to what you asked for; the headline does not depend on them.
**Basket:** direction #1 already taken; B325's next step (3/3, 2/3) and direction #3 (2/3, 2/3) deferred.
