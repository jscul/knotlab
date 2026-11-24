# A round read locally: what stands

Epic `LOCAL-ROUND-20261123-001` (sub-goal B323; goals G5 with G18), closed 2026-11-24. One frozen study, computed, scientific
referee pending. [Ticket A: result](../LOCAL-ROUND-20261123-001A/results.md) ·
[pre-registration](../LOCAL-ROUND-20261123-001A/preregistration.md) · [definitions](definitions.md) ·
[referee hand-off](referee_handoff.md) · [advisor review before the freeze](advisor/README.md) ·
[the thread's checks](checks/)

## The answer

The study of the ring that returns left one thing supplied inside a part: its members had to read together, and a law in
which every knot reads again after each birth jammed. The question was whether births can be made one at a time, each knot
reading only a few steps around itself and only what is built, and still build what the complete rounds build in every
order.

1. **They can, given a record of who was made from whom.** Call a knot weaned when its parents have finished giving, and
   its brood the knots made alongside it. A knot that waits until its whole brood is weaned, and then replays the round on
   the brood as it was at birth, builds what the complete rounds build: in every order where the search finished, and in
   every sampled and partly searched order elsewhere, with waiting, without it, and under ordinary growth.
2. **Four steps are enough on the cycles.** Reading only the knots within four holder steps gives the same on cycles of 4, 6,
   8 and 12 members through dead knots. The reading does not grow with the structure there.
3. **Each further wait costs a step.** Where one knot has to wait three times, a guard that checks three steps fails at the
   thirteenth birth, and the least distance that works is six. The advisor found this start by hand before the freeze; the
   thread followed it by hand, and two independent programs then confirmed it.
4. **With no waiting, a knot needs only its own parents to have finished.** That guard matched in every order that finished
   where a short knot retires or makes offshoots, and under ordinary growth.
5. **Reading what is there now does not work.** The record's birth-by-birth law and the idea as first stated (read the
   present part) both fail within a few births, because the present roster mixes knots of different rounds.
6. **The record's guard is safe and incomplete.** The depth guard of the serial-repairs study never builds anything wrong
   and matches wherever nothing waits; under waiting it stops early.

Fourteen predictions and a gate were frozen. The gate and eleven predictions hold; three hold in part, because a search over
every order reached its cap before finishing, with no mismatch found. None fails.

## What it does and does not show

The advisor put it this way before the freeze, and the result bears it out: the parent relation, with the rule that a knot
spends everything in one act, carries the round. A brood is exactly one part's round, and the law replays that round on the
record.

- **Shown:** nobody has to keep the round. No scheduler says "now everyone reads"; each knot decides from what is built
  around it, and a parent's death is the signal that it has finished.
- **Not shown:** that the round can be done without; that the holders alone would do, with no record of parents; that the
  reading stays bounded when knots wait again and again.
- **Not covered:** knots that hold instead of releasing, the fillers, the cap of three, starts where a knot that acts meets
  a knot that waits, and anything beyond the rounds searched.

In the literature's words this is a synchronizer: a way to run a step-by-step rule on a network with no common clock, by
local waiting. What the study adds is the least distance these growth laws must read, and that waiting is what makes it
grow.

## Scaffolds, and what survived their swaps

| Scaffold | Swapped for | Survived? |
| --- | --- | --- |
| The guard | parents weaned; their brood-mates weaned too; the brood all-weaned; reading within d steps; the present part; the record's depth guard | The brood all-weaned always matched. The narrower guards fail under waiting, the first at 7 births and the second at 13. |
| The ration and treatment (A224) | a fixed three with waiting; just enough for three places, the short knot retiring or making offshoots; ordinary growth | Yes: the brood guard matched under each. |
| The start | cycles of 4 to 12 through dead knots, the ring of five, two small starts, a lone knot, the seven-knot generator, the cycle of eight with three extra dead knots | Yes, except the start-clause counterexample, where every law fails at the second birth. |
| The written record of parents | not swapped | Everything rests on it. The depth guard, which reads depth to supplied first knots instead, stops under waiting. |
| The start clause | not swapped | It is wrong where a start knot that acts meets one that waits. |
| The rule for a second reading | not swapped | Supplied with the laws. |
| The release rule | not swapped | Holding was not run. |

So the result is about these supplied laws and their supplied record, not about the model: it says that the order of births
within a part need not be supplied, and names what has to be supplied in its place.

## Assumptions relied on

A104 (the complete round as the reference), A224 (the added rules), A228 and A229 (the owner's pictures of time, which this
bears on), A237 (rounds part by part), and the two entries added by this study (the written record of parents; the start
clause with the rule for a second reading).

## Limits

Finite and computed: twenty pairs of start and law; with waiting, to round 1 on the cycles and rings and in sampled orders to
round 3; of 193 registered searches over every order, 126 finished. That the brood guard is exact at every round rests on an
argument in the definitions, written for the referee and not proved. The thread set a time budget that the pre-registration
did not have; the one prediction it touched was run again to the registered cap, with no mismatch.

## Final report as sent (2026-11-24 19:08 UTC)

The one-birth-at-a-time study has reached its stop and is closed, referee pending. **The answer is yes, with one thing supplied: each birth has to record which knots it came from.**

**What stands.** The code was written from the frozen design by a helper who never saw the first prototype, and the two programs agree on every verdict. Of 14 predictions, 11 hold, 3 hold in part and none fails.

- **The guard that works.** A knot acts once every knot made alongside it has parents that have finished giving. It then works out, from those knots as they were when made, what the complete round would have had it do. Births made one at a time under that guard built what the rounds build in every order searched: where knots wait, where none does, and under ordinary growth.
- **How far a knot has to read.** Four steps out, a step crossing one shared distinction, is enough on cycles of 4, 6, 8 and 12 knots joined through dead knots, so the reading does not grow with the structure there.
- **Waiting is what costs.** Each further time a knot has to wait, it must read further. On a start the advisor designed by hand, one knot waits three times. A guard that checks three steps then builds, at the thirteenth birth, something the rounds never make, and the least reading that works there is six steps.
- **With no waiting, less is needed.** It is enough that a knot's own parents have finished.
- **Reading what is there now fails.** The record's earlier birth-by-birth law, and my own first idea of reading the part as it stands, both go wrong within 1 to 17 births.
- **What this does not show.** The round has not gone: the law replays it from the record of parents. What has gone is the need for anyone to keep it. It is not shown that the record of parents can be done without, or that the reading stays bounded when knots wait again and again.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the frozen study of births made one at a time | **Status:** Successful | Its stop is met: a guard that matched the rounds in every order searched, with what it reads stated. |
| Local direction — local reading in place of the supplied round | Continue | Three things are open inside it: the record of parents, starts where a knot that acts meets one that waits, and knots that hold. |
| Broader exploration — growth laws compared | Known alternatives | The record's depth guard reads everything and stops early under waiting; your new study asks for laws under which parts meet again. |
| Long-term goal — G5 Dynamics, with G18 Comparing growth laws | Capability gained | The first law in the record that needs no scheduler inside a part, with the distance it must read measured. |

The three "in part" verdicts are searches over every order that reached their cap before finishing; none found a mismatch, and every sampled order matched.

**Next step:** Research directions — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Parts that meet again: your request of 24 November | 3/3 — the first reader the growth makes, if one exists | 2/3 — the laws and starts exist; the design is being drafted | Record check, then each start grown with and without the second part → stop at a part whose course depends on another, or at the least law that allows it, with its cost | Selected · started |
| 2 | The same guard with no record of who was made from whom | 3/3 — would remove the last thing handed to these laws | 1/3 — no construction is known | List pairs of knots alike within d steps but with different parents → stop at a rule that recovers the parents, or a pair no bounded reading separates | Alternative · deferred |
| 3 | A proof that the guard is exact at every round | 2/3 — turns the computed result into a theorem | 3/3 — the argument is written out | Write it for starts past their first round → stop at a proof or a counterexample | Alternative · deferred |
| 4 | What was left out: the cap of three as recorded, knots that hold, a start where a knot that acts meets one that waits | 2/3 — closes the gap to the ring that returns as recorded | 3/3 — the engine and the searches exist | Run the guard under those rules → stop at a match in every order searched, or at the first mismatch | Alternative · deferred |

1. Selected because you asked for it and it bears on G15; it connects to this result, since the record of parents measured here is what the cheapest law of that study would be handed. A helper is checking the record now and nothing is frozen.
2. The payoff is that the before and after would be read from the structure alone; the main uncertainty is whether any bounded reading can tell a parent from a child.
3. Cheap and solid, but it adds certainty, not a new capability.
4. Each of the three is a short run with the existing code; the start case needs a new rule first.

**STOP on this objective.** Its stop condition is met, so no successor on the same question is started; the thread's work goes to the study you asked for.

**Corrections:** none.
**Goals:** one checkpoint row (G5, G18: capability gained); no goal changed. One sub-goal added: B325, the same guard with no record of who was made from whom.
**Assumptions:** two new, both Assumed and both scaffolds: A242 (every birth writes its parents, and a law may read that record) and A243 (a start knot reads the start as given, and a knot that waited reads again only against those that waited with it). History lines on A104, A228, A229 and A237. From your message of today, A241 (knots that descend from one knot can be joined again through it), Under challenge by the new study. All of these, and the earlier pending entries, are still uncommitted in the tracker, behind other threads' numbers.
**Scaffolds:** the guard, the ration with its treatment and the start were swapped, and the guard that waits for the whole set of knots made together survived every swap but one: a start built so that a knot that acts meets a knot that waits, where every law fails at the second birth. The record of parents, the rule for start knots, the rule for a second reading and the release rule were not swapped. So this is a result about supplied laws with a supplied record, not about the model.
**Basket:** direction #1 taken (your request); B325 (3/3, 1/3) and directions #3 and #4 (2/3, 3/3) deferred.

One check is still running. I had given the helper a time budget that the pre-registration did not have, so the one prediction it touched (ordinary growth on the ring of five, every order) is being searched again to its registered cap; I'll add its numbers to the record when it ends. Lesson 8.1 of the guide now has the result, with "weaned" and "brood" in the glossary.
