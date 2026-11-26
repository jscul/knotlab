# Two patterns that stay linked under a cap: can the far one then change the receiver's course?

Epic `LINKED-UNDER-CAP-20261126-001`, direction 1 of the close of
[`SECOND-SWITCH-20261126-001`](../SECOND-SWITCH-20261126-001/decision.md), under the owner's standing rule. A check by
the thread, not a registered study; computed; referee pending. Program: [`linked.py`](linked.py).

## Why

Under caps of three to seven the switch receiver and 43 far ends come apart into parts sharing no distinction by
round 3, and nothing the far end does afterwards is heard; under one fewer than asked with waiting, a first change kept
two patterns linked and a second was heard. Are there pairs under a cap that stay linked, and is the link what lets a
later change through?

## What is read

- **Pairs:** the switch kind of each cap k = 3 to 7 (three mutually sharing knots, the site holding k − 2 loose
  distinctions, the others two) against each of the 646 census starts as the far end, 24 rounds or 6,000 knots; and,
  under the cap of three, each of the 646 census starts as receiver against the five senders of the switch census, 16
  rounds or 3,000 knots. A meeting through two link knots; waiting.
- **Linked**, per round: a member of the far end's own knots in a part linked (a member of each holding one
  distinction) to a part holding a member of the receiver's own. (The advisor's widest reading, "linked through any
  knot", is not a condition: the start's shared distinctions are never lost, so every knot of a joined start is tied to
  every other through some chain of holders in every round.)
- **Changes after both exist:** after round t₀ = 3, 5, 8, one more loose distinction at each of up to five members of the
  far end's own knots, nearest the receiver in sharings, in a part linked to the receiver's; and, as the control, at up
  to five in parts not linked. The first round after t₀ the receiver's own births differ.

## Taken from the advisor's review

[Question](advisor_question.md), [answer](advisor_answer.md). Taken: predictions per cap with numbers; the round the
link ends; the delay from change to hearing; and the narrow and wider readings of "linked" kept apart (above). Not
taken: a group holding members of both parts as a third reading (a group lies within one part by definition of parts);
a rerun under another order of giving distinctions (the record's "up to renaming" argument covers it).

## Expected (written before the full run, after a trial of ten far ends against the cap-of-three switch kind)

Trial: of ten far ends, six are never linked to the receiver after round 1 or 2; four stay linked to round 2, 3 or 4,
and then the far end has no own members left; no far change was heard.

1. **Few stay linked.** For each cap, at most 32 of the 646 far ends (5%) are linked to the switch kind after round 8,
   and at most 6 (1%) after round 16. Under the cap of three, at most 1% of the 3,230 receiver pairs are linked after
   round 16.
2. **Unlinked, never heard.** No change made where the two are not linked, in the round it is made, is heard. One
   exception refutes "the link is necessary".
3. **Linked, mostly heard.** Of the changes made where the two are linked in that round and still linked three rounds
   later, more than half are heard.

## Sent again (second pass, written before it was run, after the first two caps of the census had been read)

Read so far: under the cap of three, 28 of the 646 far ends stay linked to the switch kind through round 16, and
changes at their linked far members after round 3, 5 or 8 are heard at rounds 13, 17 and 23; 0 of 8,170 changes at
unlinked far members are heard. So the question of the original direction can be asked: can the far pattern change
the receiver's course after both exist, and again, and again? Program: [`again_linked.py`](again_linked.py). In each
pair that stays linked through round 16, a change after round 3, then one after round 7 in the growth with the first,
then after round 11, then after round 15 (each at the far end's own member in a linked part nearest the receiver),
read to round 32 or 10,000 knots.

Expected:

1. In every such pair under the cap of three, the first three changes are each heard, at about t₀ + s + 1 (s the
   change's sharings from the receiver's own knots), so a signal is sent and received three times.
2. The fourth (after round 15) is heard where the read reaches t₀ + s + 1 within 32 rounds, and not otherwise
   (reported as not read).

## What was found

All 6,460 pairs were read: each cap's switch kind against the 646 far ends (caps three to seven, 24 rounds or 6,000
knots), and the 646 receivers against the five senders under the cap of three (16 rounds or 3,000 knots); none was
stopped by the clock. The run was stopped once when its shell's time ran out, at 1,938 pairs, and resumed for the rest
([`drive2.py`](drive2.py)). Tables: [`linked_table.md`](linked_table.md) ([`tally.py`](tally.py) on
`linked_runs.jsonl.gz`); the second pass, `again_linked_runs_caps36.jsonl.gz` and
`again_linked_runs_receivers.jsonl.gz`.

| pairs | linked after round 3 / 8 / 16 | changes at linked far members heard (of) | at far members not linked (of) |
|---|---|---|---|
| cap of three, switch kind × 646 far ends | 167 / 28 / 28 | 124 of 471 | 0 of 8,170 |
| cap of four | 186 / 28 / 28 | 96 of 1,225 | 0 of 6,974 |
| cap of five | 197 / 28 / 28 | 48 of 1,747 | 0 of 6,308 |
| cap of six | 202 / 28 / 28 | 28 of 1,917 | 0 of 6,005 |
| cap of seven | 205 / 28 / not read (runs end at rounds 9 to 14) | 0 of 2,000 (cut by the knot bound) | 0 of 5,864 |
| cap of three, 646 receivers × 5 senders | 334 / 181 / 181 | 8 of 1,846 | 0 of 31,206 |

1. **No change at a far member outside the receiver's linked parts is heard: 0 of 64,527.** The link is necessary, as
   the referee of the second-switch study argued from the local law.
2. **Where linked, a change the far pattern makes after both exist is heard.** Every hearing comes from a pair still
   linked three rounds after the change: 304 of the 2,022 such changes. For the switch kinds under the caps of three and
   four, 124 of 144 and 96 of 144; under five and six, 48 of 294 and 28 of 283; under seven none could be read; among
   the census receivers, 8 of 879, all by the switch kind or one other four-knot receiver. 272 of the 304 are first heard
   at round t₀ + s + 1 (s the change's sharings from the receiver's own knots): after round 3, 5 or 8 from 9, 11 or 14
   sharings, heard in rounds 13, 17 and 23.
3. **The same 28 far ends stay linked to the switch kind at every cap from three to six**; the 181 linked census pairs
   are 153 receivers with the middle-sited path and 28 with the switch receiver as sender. What holds the link is the
   part the two make together: in three pairs read, every member of the linked class is new each round (16, 42, 84,
   142 members at rounds 4, 8, 12, 16) and none waits.

**Sent again.** In each of the 293 pairs linked through round 16 (112 switch-kind pairs under caps three to six, 181
census pairs), a change after round 3, then after 7, 11 and 15, each in the growth with the ones before:

- The first is heard in all 112 switch-kind pairs (at round 13) and in 7 of the 181 census pairs (the switch kind and
  one other).
- **No second change is heard in any of the 293.** After the first change the two lie in unlinked classes from round 6
  to round 10 in 289 pairs, and in the other 4 (one far end under each cap) the far end has no members left after round
  5. So sending the change ends the link it was sent along, whether or not it was heard.

So under a cap, by a meeting, a far pattern can change the receiver's course after both exist, but once: the change
cuts the link. This is the second branch of the stop of the short-again study's first direction ("the line passes once
and stops: the line is spent by use"), now in linked pairs that grow, not in a jam.

## Expectations, and how they fared

1. *Few stay linked: at most 32 after round 8, at most 6 after round 16, per cap.* The first holds (28); the second
   fails (28 under caps three to six; 181 of 3,230 census pairs, against at most 1%).
2. *Unlinked, never heard.* Holds: 0 of 64,527.
3. *Linked and still linked three rounds later, more than half heard.* Holds for the switch kinds under caps three and
   four (124 of 144, 96 of 144); fails under five and six and for the census receivers; 304 of 2,022 in all.
4. *Sent again: each pair hears three changes in a row.* Fails in all 293: the first change ends the link.

## What this does not say

- The link and the hearing are read for one join (a meeting through two link knots), five senders or one receiver
  kind per cap, a change at the nearest linked far member, 24 or 32 rounds; under the cap of seven the knot bound ends
  the runs before a hearing could be read (not a negative).
- Why the change ends the link is not traced; the link is held by knots both patterns make together, new each round.
- It rests on the caps (A224, A282), the meeting and the strict reading of own knots (A277). Under the ordinary count
  a barred distinction one sharing away is heard (the referee of the second-switch study), so "nothing without a cap"
  holds only for additions.
