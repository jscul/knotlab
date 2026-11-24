# Deviations and readings, RING-IN-BALANCE-20261123-001A-E001

Written by the engine's author before the registered runs A1 to A7 were started. The frozen files
(`definitions.md`, `preregistration.md`, `contract.json`) are unchanged; their SHA-256 sums were checked against
`contract.json` before any code was written. Every place below is one where the frozen text left a choice, or where a
literal reading would make a check meaningless; for each: the question, the reading taken, and why. Nothing here changes
a definition or a prediction; where a prediction depends on a reading, both readings are computed and reported.

The ambiguities in D7 and D8 were noticed while building the engine: a development check of Ring(5, 3) under the two
added rules for 12 rounds (and under the three for 20), not one of the registered runs, showed the round-1 part
returning at round 3. That check had already reproduced the disclosed pilot counts (5/1, 10/1, 15/6, 25/6, 35/11,
50/11, 65/16 and 5/1, 10/1, 15/6, 10/1, 15/6).

## D1. The cut method when the outside has no edge

*Question.* The definitions state the cut method as "deleting the knot leaves the rest connected (the knot is not a cut
vertex; the allowed states are the graph's cycle space)". In a structure with no loose distinction (possible only after
a closing birth) the outside vertex has no edge, so "the rest" is never connected and every knot would fail, while the
rank method (and the cycle-space statement) makes such a knot pass whenever the rest of the knots stay connected.

*Reading.* A knot passes the cut test when it is not a cut vertex in the standard sense: all its edges (to other knots or
to the outside) reach one connected component of the graph with the knot deleted. When the outside has an edge this is
word for word "deleting the knot leaves the rest connected", since the structure is connected. *Why.* It is the
parenthetical's reading and the one equal to the cycle-space statement that justifies the method. Affects only
structures with no loose distinction (the closing exception in A4).

## D2. A met set does not contain its common knot

*Reading.* A knot does not meet itself, so the met set of a knot that is itself a member does not contain it. *Why.*
"Two knots meet when they share a distinction." With this reading the ordinary-law gate numbers come out exactly
(Ring(5, 3): births 10, 15, 25, ...); with the other reading round 1 of Ring(5, 3) would have one group of five.

## D3. "Past its start" for a part

*Question.* The text defines "past its start" for the roster ("no member meets a member") and uses it of a part Y.
*Reading.* A part is past its start when none of its members meets a member. The roster-level flag is also recorded.

## D4. Descent of a member that keeps a usable distinction

*Reading.* A member after round t descends from itself when it was a member after round t − 1 (it waited, or under HOLD
kept what its cancelled groups would have taken), and otherwise from its parents (it was made in round t). *Why.* The text
names only waiting ("a waiting member descends from itself"); under HOLD a member that keeps its distinctions is in the
same position. Only A6 has HOLD.

## D5. Which parts "those descendants form"

*Reading.* A part of the roster after round t is formed by the descendants of Y when every one of its members descends
from Y and from no other part of the roster after round s. A part with members descending from two parts of round s is
counted as mixed and reported (`mixed_parts`); it is neither the return nor a part given off. Under RELEASE past the
start none is expected (settled by construction).

## D6. The census kind and "has a part that returns giving parts off"

*Reading.* Returns are searched for every part of every round s that is past its start, each with its least t; they are
listed by least s, then least t, and the first is reported as the run's return. The census kind is the first that
applies over the whole run: stalled (some round stalled), jammed (some round jammed), stopped, a part returns giving
parts off (some part does), a part returns giving none off, grows to the bound. P8's "has a part that returns giving
parts off" is read as the existence of such a return within the run, whatever the run's census kind; the kind is
reported beside it.

## D7. Which parts P3 is about (ambiguity in the frozen text)

*Question.* P3: "Under the two added rules every part that has come apart is the same, s rounds later, as every other at
the same s, and has s + 2 members, for s from 0 to 10 and n = 5, 7, 9." By the definition of "come apart", parts come
apart from **every** part that returns. Under the two added rules the part after round 1 (n joins and n offshoots, 2n
members) is past its start and returns at round 3, and the n parts it gives off have **three** members when they come
apart: they are P2's two-member parts one round later. The search order (least s first) makes this the run's first
return. Also, R = 12 and s up to 10 can be reached only by parts that came apart at round 2; but the parts present
after round 2 descend from the start, which is not past its start, so formally they have not come apart from anything
(the earliest formal coming apart is at round 3).

*Readings computed.*
- (P3-a, taken for the verdict) The parts P3 counts are the two-member parts that appear beside the part of the knots that
  waited, after every even round t0 = 2, 4, ..., 12: for t0 ≥ 4 these are exactly the parts given off when P1's part
  (the knots that waited in round t0 − 2) returns at t0 (P2); for t0 = 2 they are the n parts beside the first such part,
  which the start gives off in the same way although the start is not past its start. s is counted from t0.
- (P3-b, literal) Every part given off by any return found (including the odd-round returns), s counted from the round at
  which it came apart.

*Why P3-a.* P3 follows P1 and P2, its count s + 2 fixes two members at s = 0 (P2's parts), and "s from 0 to 10" within
R = 12 requires parts that came apart at round 2. P3-b is reported with its own verdict; under it the count s + 2 is
expected to fail for the odd-round returns by construction of the definition, not by any property of the growth. The
thread should decide which reading the frozen P3 meant.

## D8. P2 at t = 12

P2 needs the roster after round t + 2; with R = 12 it is checked for even t from 2 to 10. t = 12 is reported as not
checkable within the registered rounds (no deviation from the run length).

## D9. The cut-off at 6,000 knots (20,000 in A7)

*Reading.* The round in which the structure first passes the bound is completed and kept; the run stops after it.

## D10. Rounds after a stall or a jam

*Reading.* A run is grown through all R rounds even after it stalls or jams (such rounds make no birth and, under
CANCEL-WAIT or STALL, change nothing). *Why.* "A run is one start grown under one law through a stated number of
rounds", and P10 asks about "every later round of the run".

## D11. In balance

*Reading.* "At least one birth is made in every round" is read as every round of the run (rounds 1 to R). For a period T
the least s with roster(t + T) the same as roster(t) for every t ≥ s with t + T ≤ R is reported, with the number of
comparisons. P4's statement is checked directly as s = 1, T = 2.

## D12. P1's "the n knots that waited in round t form one part"

*Reading.* The set of members recorded as waiting in round t equals one part of the roster after round t, that part has n
members each with h = 3 (and k = 0), its inclusion-maximal met sets are n pairs forming one cycle of length n, and it is
the same (exact isomorphism) as the start's whole roster.

## D13. P4's ended parts

*Reading.* For each part that came apart at a round t0 ≤ 19 (a part coming apart at round 20 has no later round in the
run): exactly one knot made after t0 descends from it over the rest of the run; that knot was made in round t0 + 1 and
has no usable distinction; and no member after round t0 + 1 descends from the part. Checked for both populations of D7
(formal comings apart, and with the parts beside the first waiting part after round 2).

## D14. P5's "two parts after round 2 that each return every two rounds giving n/2 parts off"

*Reading.* Exactly two parts of the roster after round 2 return at round 4 giving n/2 parts off each, and for each of
them the returned part returns again two rounds later giving n/2 parts off, at every even round through 12.

## D15. P9

*Reading.* For Ring(n, 2) the roster after every round r ≥ 1 is the same as the roster after round 1, and that roster is
one part of n members each with h = 2 (k = 0).

## D16. P10

*Reading.* Every knot that waited in round 2 is short in round 3 and in every round up to 12 (D10 keeps the rounds
running after a jam), and no part returns giving parts off.

## D17. P11

*Reading.* There is a round s and a part after round s with n members each holding k usable loose distinctions that
returns at s + 2 giving parts off, and whose returned part returns again two rounds later giving parts off, at every
even step up to the last round of the run (2k + 8, or the cut-off). The chain found is reported.

## D18. Knot and extension tests: which rounds

*Reading.* The knot test is run on the start (round 0) and after every round; the extension test for every round. A2:
rounds 0 to 12; A4: rounds 0 to 6; A3: the not-all-equal test at rounds 0 to 6 (births compared through 12). The
extension test is implemented for parity only (none is registered under not-all-equal).

## D19. Births "compared with parity" in A3

*Reading.* Round by round, the full record of every birth (parents, distinctions taken, demand, fresh, usable, barred),
the groups, the short members and the closing flag under not-all-equal equal those under parity.

## D20. The part-round law (for ticket C; not used in ticket A's runs)

*Question.* In a move of one part, does the demand roster of step 6 contain the other parts' members as they stand?
*Reading (default).* No: steps 1 to 8 are applied "to the members of that part alone", so the demand roster holds the
moved part's new knots and its own old members that keep a usable distinction. The engine also offers
`demand_scope='all'`. Past the start under RELEASE the two agree (the new knots meet only their parents). Own time: a
new knot's is one more than the greatest of its parents'; a member of the moved part that keeps a usable distinction
gains one.

## D22. Added after the registered runs (changes no verdict)

- D7: under reading P3-a, P3 holds for n = 5, 7, 9 and every s from 0 to 10. Under the literal reading P3-b it fails at
  every s from 0 to 9 (member counts s + 2 and s + 3 mixed, because the odd-round returns give off P2's parts one round
  later). The verdict line reports both.
- D6 and P8: by the definition of a return, any part counts, however small. Every case that comes out against P8 is a
  part of one to three members copying itself (FLOOR0, FLOOR1, ONE-FEWER; e.g. on Ring(5, 3) under (FLOOR0,
  CANCEL-WAIT) the two offshoots of one round-1 offshoot return at round 4 giving off a copy of themselves and one
  waiting knot), or a part of 7 or 9 members under RATION-4 that appears identically on all three rings. The census in
  `a4.json` lists, for every run, the sizes of all parts that return giving parts off (`off_return_part_sizes`), so that
  a narrower reading, if the thread prefers one, can be read off without rerunning. No narrower reading was used for the
  verdict.
- D5: no run had a mixed part (289 runs checked).
- D1: no registered run produced a structure without loose distinctions; the reading of the cut method never decided a
  verdict.

## D21. Trace files

`a1_trace.json` and `extra_trace.json` give round 0 (the start) and then every round; besides the requested fields
they carry the sorted list of k (barred counts) and the number of knots, which the comparison may ignore.
