You are advising on the design of a small computational study before it runs. Be concrete and critical; at most
600 words; a numbered list ranked by importance. Do not praise.

## The growth law (enough to judge the design)

Knots hold distinctions. A distinction held by one knot only is that knot's loose distinction; a member is a knot
with a loose distinction. One round: two members are joinable when some knot shares a distinction with both; groups
are maximal sets of pairwise joinable members with no common holder, else pairs. Each group makes a join (a new knot
whose parents are its members); each member gives one loose distinction to each of its joins and one to an offshoot
(a one-parent knot) for each loose distinction left over. Under the ORDINARY COUNT a new knot receives fresh
distinctions f = max(D, 3 - p, 1), D its demand (joins it will be in next round), p its parents; so no knot is ever
short. Rations other than the ordinary count (a cap of three; one fewer than the ordinary count) leave knots short,
and a short knot's joins are cancelled while it waits. Inside a proved class a knot of round t is a connected cluster
of t + 1 members of a "map of joins" (its universal cover), so round t's births are the knots at about t steps from
the start. A proved bound: a change d steps away can first show in round d (fresh counts) or d + 1 (which births).

## The study

# How much of a change arrives

Epic `HOW-MUCH-ARRIVES-20261126-001`, at the coordinator's go-ahead on the first direction of the report that
delivered Chapter 11 of the guide ([the request](owner_request.md)). A check by the thread, not a registered study;
computed; referee pending. This file was begun before the full run: the sections "The design" and "Expected" were
written then, after the pilot below, and reviewed by the advisor before anything else was run.

## Why

The owner's lamp has two halves. A lamp twice as far away is seen later, and it delivers a quarter of the power.
Lesson 11.4 of the guide found the first half in the growth: a change spreads at most one step of the map of joins a
round ([Codex's study of how many rounds a change needs](../INFLUENCE-CONE-20261120-001/decision.md), proved, referee
pending). The second half was untested, because the record counts whether and when a change shows and never how much
of it arrives. This study counts it.

## Prior work in the program

`track.py objects` was searched for the share of births that differ after one change, the spread of a disturbance,
damage spreading, and a mark that changes a growth's rate, until 26 November 2026, excluding this epic.

- `INFLUENCE-CONE-20261120-001` (rows 1 to 4): the earliest round at which a change of loose count or of what is
  met can show, sharp; whether, not how much.
- `TWO-PATTERNS-20261126-001` and its referee: under the ordinary count, through a meeting, a pattern's own births
  equal those beside a stub; a mark on one of two two-knot parts gives a whole new table of what they make together;
  moving one loose distinction to the other knot changed 46 of 55 index pairs of that table.
- `SHORT-AGAIN-20261126-001`, `SWITCH-RECEIVERS-20261126-001`, `SECOND-SWITCH-20261126-001`,
  `LINKED-UNDER-CAP-20261126-001`: where a change is heard between patterns from more than one step, it is the end of
  a jam under a ration of one fewer, or a switch of one receiver kind under a cap; whether and when, not how much.
- `LATTICE-NET-20261108-001` (the process line, on a supplied board of rule-60 rings): influence spreads by the
  powers of a Laurent polynomial over GF(2), so cancellation thins it; a board, not the growth.
- `DOUBLE-IDENT-20261119-001`: the growth reads a start only through each knot's live neighbours and each live
  knot's open count.

No record measures how many of a round's births a change alters.

## The pilot (seen before this design was written)

Three starts under the ordinary count, 12 rounds, a mark (one more loose distinction) at each start knot; and four
starts with one loose distinction moved from one start knot to another. Seen:

- two three-place knots sharing a distinction (dimension two): a mark alters 1, 3, 1, 1, 2, 3, …, 9 births in
  rounds 1 to 12, of 5, 6, 5, 6, 8, …, 22; moving a distinction alters all but one each round;
- a bare ring of five (dimension one) and the golden-ratio ring of five: a mark or a move alters every birth from
  round 4 to 8 on, because the changed start grows a different kind of growth (a bare ring with one leftover grows
  one more knot each round; the eddy with one more leftover grows faster than the golden ratio).

## The design

**The measure.** A growth G and the same growth G′ with one change. At each round t, the births of each are named by
how they were made (kind, parents' names, number among equal births of the round, from the start knots' names, as on
the bench), with each birth's number of fresh distinctions and of places. The **damage** c(t) is the number of
births of G′ in round t with no identical birth in G that round (a difference of multisets), and c⁻(t) the reverse.
The **share** is s(t) = c(t)/n′(t), where n′(t) is the number of births of G′ in round t. A birth of round t is a
cluster of t + 1 members of the map of joins (lesson 8.1), so the round's births are the knots at about t steps from
the start: n′(t) is the count the lamp's sphere stands for.

**Verdicts,** read over the last four rounds read of a case with at least eight rounds:

- **dies out:** c(t) = 0 in all four;
- **weakens** (the lamp): c(t) > 0, c does not grow over the four rounds while n′ does (c(T) ≤ c(T − 3) and
  n′(T) > n′(T − 3)); the share then falls at least as one over n′;
- **takes over:** s(t) ≥ 0.95 in all four;
- **holds:** every other case with c growing; the report gives the last share.

A case whose n′ does not grow (a bare ring) is read by c alone: dies out, bounded (c(T) ≤ c(T − 3)), or grows.

**Setting A, the model: the ordinary count,** not-all-equal, nothing taken, no short knot ever (the treatment of
short knots is waiting and never acts). Starts of known kind:

| start | knots | kind of growth (counts per round) |
|---|---|---|
| ring5-bare | five knots in a ring, two loose each | dimension one: 5 a round |
| ring7-bare | seven knots in a ring, two loose each | dimension one: 7 a round |
| two-touching | two three-place knots sharing one distinction | dimension two: 4, 6, 8, … |
| chain3 | three three-place knots in a row | dimension two: 4, 6, 8, … |
| ring5-eddy | five knots in a ring, three loose each | golden ratio: 10, 15, 25, 40, … |
| generator7 | the generator study's seven knots | releases packets (lesson 8.7) |

Changes, each grown beside the unchanged start to round 16 or 20,000 knots:

1. **A mark at a start knot,** each start knot in turn.
2. **A move:** one loose distinction taken from one start knot and given to another, for every ordered pair of start
   knots with a loose distinction to give (the inventory of loose distinctions is kept).
3. **A mark at a made knot:** the growth is grown to round s, each knot made in round s is given one more loose
   distinction in turn, and the growth goes on beside the unmarked one; s = 2 and 4 (on the eddy and the generator,
   at most 40 marked knots a round, the first 40 in the order made). Read also the **descent share**: the share of
   G′'s births that have the marked knot among their ancestors, so the damage can be set against the knot's own
   descent.

**Setting B, supplied (scaffolds, named):** the two settings in which the record hears a change between patterns.

- **B1.** Two seven-knot generators joined by a meeting through d − 1 link knots, d = 1 to 8, under the ration of one
  fewer than the ordinary count with short knots waiting (assumption A278's ONE-FEWER; the jam of
  `SHORT-AGAIN-20261126-001`). Change: a mark at the far generator's site. Read: the damage and share in the near
  generator's own births, and the joint descent's, round by round to 16 rounds.
- **B2.** The switch receiver of `SWITCH-RECEIVERS-20261126-001` (three mutually sharing knots, sited at its knot
  holding one loose distinction) joined by a meeting through d − 1 link knots, d = 2 to 5, under the cap of three
  with waiting (assumption A224), to a far site holding two loose distinctions against one holding three (the
  study's two-knot and one-knot senders). Read: the damage and share in the receiver's own births between the two
  growths, round by round to 16 rounds.
- **B0.** Both under the ordinary count: the control, where a pattern's own births are known not to differ.

The question in B is the lamp's directly: does the damage in the receiving pattern's own births fall as d grows?

## Expected

Written before the full run, after the pilot.

1. **No case weakens.** In no setting does the damage stay bounded while the round's count grows. This is the
   headline expectation; one weakening case, in setting A, would be the lamp's second half found in the model.
2. **A mark at a start knot (A1):** takes over on the bare rings and the eddy (the mark changes the kind of growth),
   holds near one half on two touching knots, as in the pilot; on chain3 and the generator, holds.
3. **A move (A2):** takes over on the rings; on two touching knots and chain3, takes over or holds above 0.8.
4. **A mark at a made knot (A3), not seen:** holds or takes over; never weakens. The damage reaches beyond the marked
   knot's descent in some cases (a change can show in a birth with no changed ancestor, as the influence-cone study
   found), so the damage share exceeds the descent share there.
5. **Setting B:** under the ordinary count (B0) no damage in a pattern's own births. In B1 and B2 the damage in the
   receiving pattern's own births, once it arrives, does not fall with d: the share in the rounds after the first
   difference is the same, or larger, at larger d.

**Stop.** A case that weakens in setting A (the lamp found), or every setting read with none.

## Questions

1. Is "the share of a round's births that differ" the right reading of "how much of a change arrives" for the
   owner's lamp (a fixed output spread over a growing sphere, so a fixed patch gets less)? Name a better or
   additional reading if there is one (for example, damage counted only outside the changed knot's descent, or a
   sum of differences in fresh counts), and say what each verdict would then mean.
2. The pilot shows that a mark or a move at a start knot changes the KIND of growth (dimension or rate), so the share
   goes to one trivially. Is a change at a start a fair test of the lamp at all? Is the mark at a made knot (A3)
   the right fix, or should the change be one that keeps every count (a relabelling that moves which knots share)?
3. Are the verdict thresholds sound (four rounds, 0.95, "c does not grow while n' does")? What would misclassify?
4. Setting B: after a jam ends or a switch happens, the whole later growth differs, so "takes over" may be forced by
   construction. How should B be read so that it can show a weakening with d if there is one?
5. Known mechanisms to compare: damage spreading in Boolean networks and cellular automata (ordered, critical,
   chaotic), cancellation in linear automata over GF(2), conserved fluxes. Which is the right comparison, and what
   is its cheapest discriminating prediction here?
6. Which of the written expectations would you change before the run, and why?
