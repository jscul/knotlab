# After both exist, can the far pattern change the switch receiver's course?

Epic `SECOND-SWITCH-20261126-001`, a successor of
[`SWITCH-RECEIVERS-20261126-001`](../SWITCH-RECEIVERS-20261126-001/decision.md) under the owner's standing rule. It
takes that close's second direction ("a second switch") ahead of its first, because the first would add a ration made
by hand, and the program's rule prefers shrinking a scaffold to adding one. A check by the thread, not a registered
study; computed; referee pending. Program: [`second.py`](second.py).

## What is read

- **Receivers:** the switch kind under each cap k = 3 to 7 (three mutually sharing knots, the site holding k − 2 loose
  distinctions, the other two holding two), joined by a meeting through two link knots (d = 3).
- **Far ends:** the two-knot start sited at a knot holding two loose distinctions (it switches the receiver at round 7),
  the one-knot start (three loose) and a stub (neither does).
- **Changes after both exist:** after round t₀ = 3 to 10, one more loose distinction (and, separately, one barred) at
  each of the five members of the far end's own knots nearest the receiver's own knots in sharings (a choice: a
  scaffold, as in the short-again study's second change).
- **The horizon:** after round 3 and after round 6, one more loose distinction at up to three members, not the
  receiver's own, at each sharing distance s = 1 to 8 from its own knots: how far away a change can be and still be
  heard.
- **The far end's distance**, round by round: sharings from the receiver's own knots to the nearest member of the far
  end's own knots.
- 24 rounds or 6,000 knots; births compared by knots' names by making, up to the last round both runs read. "Not
  heard" means not through the rounds read, at the distance stated.
- **Slow or fast:** the receiver is in its slow way in a round when its own births equal those with a stub at the far
  end, and in its fast way otherwise.

## Taken from the advisor's review

[Question](advisor_question.md), [answer](advisor_answer.md). It expected the first prediction I was considering
("some such change is heard") to fail, since a change at two rounds a step from 7 to 14 sharings needs up to 28
rounds and the way may lengthen faster than that; it asked for the far end's distance every round, nulls stated with
their round and distance, a failure criterion fixed in advance, the slow and fast ways defined before the run, a
change at a knot in between at the same distance as a contrast (the horizon), and the ordinary count reported as empty
if nothing can be heard by construction. All taken. Not taken: the severed line and the chain of differing knots
(needed only if a far change is heard).

## Expected (written before the full run, after one trial: the cap of three, the one-knot far end, 48 changes, none heard)

1. **No change at the far end's own knots set after round 3 is heard through round 24**, for any receiver, far end,
   sign or t₀. One heard change at t₀ ≥ 3 refutes this.
2. **The horizon is short.** A change after round 3 is heard from knots up to some distance s* ≤ 4 and not beyond, at a
   round no earlier than t₀ + s.
3. **The far end recedes.** Its distance from the receiver's own knots grows by one or more every round from round 3.
4. **Under the ordinary count nothing is heard**, by construction (no knot is short after the start): reported as
   empty, not as a confirmation.

## What was found

All 18 runs were read (five caps and the ordinary count, three far ends; 9 to 24 rounds: the runs with the two-knot
far end reach 6,000 knots at rounds 9 to 23 under caps of four to seven). Tables: [`second_table.md`](second_table.md)
([`tally.py`](tally.py) on `second_runs.jsonl.gz`).

1. **No change at the far end's own knots made after round 3 is heard by the receiver**: 0 of 496 (both signs, t₀ = 3 to
   10, every cap, the ordinary count), through the rounds read. Under caps of four to seven the one-knot far end has no
   own members left after round 3 (it has stopped), so it offers two changes each; with a stub there are none.
2. **The far end recedes one sharing a round.** In every run in which the far end still has own members, the nearest of
   them is 7 sharings from the receiver's own knots after round 1, 9 or 10 after round 3, and one more after every
   round from then on (one more in each of 6 to 21 rounds, in all 7 such runs): 30 after round 24 under the cap of
   three.
3. **In these readings nothing travels faster than one sharing a round.** Of the 110 changes heard in the horizon
   readings, every one is first heard at round t₀ + s or later (110 of 110; at t₀ + s in 2, one to three rounds later
   in 108).
4. **Near the receiver it still hears.** After round 3, changes at knots one to three sharings away are heard in most
   runs; under the cap of three with the one-knot far end (the receiver still in its slow way) after round 6, from as
   far as eight sharings. After the receiver has switched (the two-knot far end), changes after round 6 are heard
   from one sharing only, or not at all.
5. **The ordinary count:** nothing is heard, from any distance, in any reading: empty by construction (no knot is
   short after the start), not a confirmation.

**Every far end, and the ones that keep a waiting member** ([`recede.py`](recede.py), `recede_runs.jsonl.gz`;
[`waiting_far.py`](waiting_far.py), `waiting_far_runs.jsonl.gz`; added after the table above, to look for a far end
that does not recede). With each of the 646 receivers of the switch census as the far end of the cap-of-three switch
receiver: in 521 the far end's nearest own member recedes one sharing a round from round 3; in 44 the far end has
stopped by round 4; in 50 its nearest own member stops receding, and 41 of those keep an own member that waits at a
fixed 6 to 8 sharings through round 16. One more loose distinction, or one barred, at that waiting member after round
3, 5 or 8: **0 of 236 heard** through round 24. So receding is not the reason.

**The reason: the two have come apart.** ([`parts.py`](parts.py), `parts.json`.) In every one of the 43 far ends read
(the two of the first table and the 41 with a waiting member), from round 1, 2 or 3 on no member of the far end's own
knots is in a part of the roster linked to a part holding a member of the receiver's own (linked: a member of each
holds one distinction), through round 16. The fold study argued, and its runs bore out, that under laws whose births
take only what their own parents hold, parts that share nothing never become one part again
([PARTS-MEET-AGAIN-20261124-001](../PARTS-MEET-AGAIN-20261124-001/decision.md), item 1; referee pending there); the
laws here are such laws. So nothing the far end does after round 3 can reach the receiver; the far end's receding one
sharing a round is how that looks by sharings. What reaches the receiver is what the far end did before they came
apart, carried in the receiver's own part by the knots that descend from the line and from both: the switch.

Under one fewer than asked with waiting it is otherwise, and this explains the short-again study's second change: in
the three pairs read that heard one, the growth with the first change keeps a part linked to both patterns' own
members through round 12 (in the growth without it they come apart by round 4)
([AGAIN.md](../SHORT-AGAIN-20261126-001/AGAIN.md)).

What this adds to the fold study: under the caps, with a meeting, two joined patterns come apart within three rounds,
before the switch is heard; and a first change from afar, under one fewer with waiting, can keep them together.
The reading of own knots is A277's strict one; the parts argument does not depend on it.

## Expectations, and how they fared

1. *No far-end change after round 3 is heard.* Holds: 0 of 496.
2. *The horizon is short (s\* ≤ 4).* Fails for the cap of three with the one-knot far end after round 6 (heard from
   eight sharings); holds in the other runs (four at most, mostly one or two).
3. *The far end recedes by one or more a round from round 3.* Holds: exactly one a round, in every run that has far
   members.
4. *The ordinary count: empty by construction.* Holds.

## What this does not say

- One receiver kind for each cap, three far ends, d = 3, a change at the five nearest far members (a choice); 24
  rounds or 6,000 knots. "Not heard" is through the rounds read.
- The coming apart is read from 43 far ends against one receiver kind under the cap of three, not under the other
  caps; the fold study's argument that parts which share nothing never rejoin is its own,
  referee pending there.
- "Kept together under one fewer" is three pairs read, not a census.
- It does not say that two patterns cannot affect each other after the start: their joint descent hears changes
  near it (item 4). It says the other pattern's own knots cannot be the source.
