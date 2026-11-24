# Deviations and readings, COPYING-PARTS-20261123-001A-E001

Written by the helper agent before the gate and runs 1 to 6 were started. Nothing had been computed with the engine
when sections C0 to C15 were written. The frozen files (`research/RING-IN-BALANCE-20261123-001/definitions.md`,
`research/COPYING-PARTS-20261123-001A/preregistration.md`, this folder's `contract.json`) are unchanged; their SHA-256
sums were checked against `contract.json` before any code was written (definitions e7c001a4..., pre-registration
cb02eb0c...).

Every run uses ticket A's engine, `experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/
engine.py` (SHA-256 2c6eac56..., committed in 6f434dbcd4 and unchanged in the working tree). It is imported, not copied
and not changed: ticket A's folder is appended to `sys.path` and only `engine` is imported from it. Every output file
records the engine's SHA-256. Each section below gives the question, the reading taken and why. Nothing here changes a
definition or a prediction. Where a prediction depends on a reading, both readings are computed and reported.

## C0. Ticket A's readings relied on

So that "returns", "comes apart", "the same", the kinds of outcome and the knot tests mean what they meant in ticket A,
its readings (its `deviations.md`) are taken over unchanged:

- A-D1: the cut method counts a knot as passing when it is not a cut vertex in the usual sense.
- A-D2: a met set does not contain its own common knot. This is built into the engine.
- A-D3: a part is past its start when none of its members meets a member.
- A-D4: a member after round t that was a member after round t - 1 descends from itself. It waited, or under HOLD it kept
  what its cancelled groups would have taken. Otherwise it descends from its parents.
- A-D5: a part whose members descend from two parts of round s is mixed. It is neither the return nor a part given off.
  The number of mixed parts is recorded for every run.
- A-D6: returns are searched for every part past its start after every round s, each with its least t. They are listed
  by least s, then least t. The census kind of a run is the first kind that applies over the whole run. "Has a return of
  such a kind" means that such a return exists within the run, whatever the run's kind.
- A-D9: the round in which the structure first passes the knot bound is completed and kept, and the run stops after it.
- A-D10: a run is grown through all its rounds even after a stall or a jam.
- A-D18: the knot test is run on the start (round 0) and after every round. The parity extension test is run for every
  round.
- A-D19: births compared between two runs means that, round by round, the groups, the short members, the cancelled
  groups, the waiting members, the closing flag and every birth (id, parents, distinctions taken, kind, D, f, usable,
  barred) are equal.
- A-D22: any part counts as returning, however small.

## C1. A two-knot part, and N(t)

*Reading.* A part of the live roster after round t is a two-knot part when it has exactly two members, it is past its
start (A-D3), each member has h = 2 and k = 0, and its inclusion-maximal met sets are the one set of those two members
(for a part of two members this is the same as "some met set contains both"). N(t) is the number of such parts of the
roster after round t. N(0) is read on the start.

## C2. The bound on knots

*Question.* The pre-registration says "A run is cut off at 20,000 knots" and "A run that passes the bound on knots is
read through its last complete round". The task brief says "through the last complete round before the 20,000-knot
bound". Under A-D9 the engine completes and keeps the round in which the structure first passes the bound. That round is
complete, but its structure is past the bound.

*Reading for the verdicts (C2-a).* A-D9: the passing round is complete and is read.

*Also computed (C2-b).* Each check is reported again over the rounds whose structure has at most 20,000 knots (1,500 in
run 5). The C2-b range is the C2-a range with at most its last round removed. A check that holds on C2-a therefore holds
on C2-b. Both verdicts are printed wherever they could differ.

## C3. P1, P2 and P3: the range of t, and P1's returns

*Reading.* t0 is the first round with N(t0) > 0, and R is the last round read (C2). P1's recurrence is checked for
t0 <= t <= R - 2, P2's for t0 + 1 <= t <= R - 2, and P3's for t0 + 2 <= t <= R - 2. P1's first sentence: for every
two-knot part Y after every round s with s + 2 <= R, the engine's return of Y (its least t, A-D6) is at t = s + 2, it
gives off exactly one part, and that part is the same as Y. A two-knot part after a round s > R - 2 cannot be checked and
is counted as unchecked. "Each of the three starts" means the three starts of run 1.

## C4. P4

*Reading.* "Gives the same roster as FLOOR0 at every round": under each treatment, the whole live roster after every
round 0 to 12 under FLOOR1, and under ONE-FEWER, is the same as under FLOOR0 by the definitions' sameness (the engine's
exact test). Also reported, with no verdict attached: whether the full round records are identical (A-D19), and the same
comparison over run 1's rounds. "Every birth receives a fresh distinction" means f >= 1 for every birth of rounds 1 to
12. For the knot test, every knot passes both parity methods and the methods agree at rounds 0 to 12. The extension test
must hold for rounds 1 to 12, and the closing flag must never be set. All checks cover the two small starts under the
nine laws (run 2).

## C5. P5 and the not-all-equal test "to round 10 or 600 knots"

*Reading.* Under each of the nine laws the run is repeated with the not-all-equal knot law, and its births are compared
with the parity run (A-D19) at every round from 1 to 12. The not-all-equal test (SAT, every assignment of every knot's
places) is run on round 0 and after every round r <= 10 whose structure has at most 600 knots. That is, the test stops
at round 10 or at the first round past 600 knots, whichever comes first. Rounds not tested are listed.

## C6. P6

*Reading.* "Every knot passes at every round" means both parity methods pass every knot at rounds 0 to 12. "With
offshoots the round-1 joins fail from round 4" means that under (ONE-FEWER, CANCEL-OFFSHOOT) every join made in round 1
passes at rounds 1 to 3 and fails at every round from 4 to 12. Other failing knots are listed separately. "Every knot
that fails does so in the round in which a birth without a fresh distinction is made" is checked under all nine laws:
for every knot that fails at some round, some birth of the round in which it first fails received f = 0. Run 3 lists
every birth with f = 0 (round, parents, demand) and every failing knot with its first failing round and every round at
which it fails.

## C7. "Copies itself", and P7

*Reading.* A part Y (after round s, past its start) copies itself when its return (least t, A-D6) gives off at least one
part that is the same as Y. Every part after every round is searched, however small (A-D22). P7 fails when some run of
the laws named in P7, on either small start, has a part that copies itself within its 16 rounds.

## C8. NO-OFFSHOOT together with CANCEL-OFFSHOOT (run 4, P7)

*Question.* Run 4 asks for "each of the nine laws with NO-OFFSHOOT", which includes the three laws with CANCEL-OFFSHOOT.
The engine's `Law` refuses that combination ("not defined together", because ticket A's list never combined them). The
definitions place NO-OFFSHOOT in step 5, which concerns members that are not short. CANCEL-OFFSHOOT is in step 3, which
concerns short members. Read literally, the combination is defined: a short member makes an offshoot from each of its
usable loose distinctions (step 3), and a member that is not short makes no offshoot, its remaining distinctions being
barred (step 5).

*Reading C8-a (verdict on the engine as it stands).* The combination is not defined. Those three laws are not run, and
P7's "under NO-OFFSHOOT" covers the six others.

*Reading C8-b (literal).* The combination is run. The engine's `Law` is constructed with an admitted treatment, and its
`treatment` attribute is then set to `CANCEL-OFFSHOOT`. The engine's round code (`_apply_round`) handles both branches
as written and is not changed. Only the constructor's refusal is bypassed. P7 is reported under both readings.

## C9. P8

*Reading.* A run satisfies P8 when it has a part Y after some round s (past its start) with five members, every member
with h = 3, and some member lying in two of Y's inclusion-maximal met sets of three members, whose return is at
t = s + 1 and gives off at least one part the same as Y. Each of the six runs (RATION-3, each of the three treatments,
each small start) must have one. Also reported for each run: k of the members, the full family of met sets (whether it
is exactly two sets of three sharing one member), the members and common knots of the first such part, and every part
of five members that copies itself.

## C10. P9

*Reading.* Under (FLOOR0, HOLD) with each treatment, on each small start, "the two-knot part still copies itself"
means that some two-knot part (C1) copies itself (C7). The three recurrences are checked for every n from 8 to 16 (the
last round of run 4). The prediction fails when a recurrence fails at some n >= 8. The descent of a member under HOLD
follows A-D4.

## C11. P10

*Reading.* For each of the nine laws with FILLERS, on each small start, the live roster after round 4 has no member. It
must also have none after every later round to 16. The round at which each run stopped is reported.

## C12. Run 5: the census

*Enumeration.* The enumeration is written again here from ticket B's description (B-D1), not imported. The meeting
graphs are the connected graphs of networkx's graph atlas on 3, 4 and 5 vertices. Each knot has a loose count from 0 to
3, with degree plus loose count at least 3 on every knot and at least one live knot. A tuple is kept when it is the least
of its orbit under the graph's automorphisms. The stars are one shared distinction for each edge, in sorted edge order,
then the loose distinctions of knot 0, knot 1 and so on. The counts must be 19, 200 and 3,157. Beyond the counts, the
identities (atlas index, tuple), their order, and the starts set aside are compared with the earlier census's records.
The earlier census's `census/results.jsonl.gz` is read for the start identities and the `set_aside` flags only. A start
is set aside when some knot fails either parity method at round 0.

*Runs.* Each start that is not set aside is run under (FLOOR0, FLOOR1) x (CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT)
to round 10, cut off past 1,500 knots (A-D9). "A part copies itself" is read as in C7, and the size of the smallest such
part is recorded. "Any knot fails the parity knot test at any round" is checked after rounds 1 to the last round read.
The test stops after the first round with a failing knot. That round, and the number and kinds of the failing knots at
it, are recorded. The number of dead knots of a start is the number of its knots with loose count 0. In the tables each
start counts once under each law. They are lower bounds, given the bounds on rounds and knots. The C2-b variant (only
rounds with at most 1,500 knots) is also tabulated.

## C13. Run 6

*Reading.* Under each of the two laws, every return of a part of seven or nine members is grouped by sameness class.
For each class the report gives its first (s, t), its members with h and k, its inclusion-maximal met sets with their
common knots, the parts given off, whether it copies itself, and the births of one period that descend from it (the
small trace).

## C14. The gate's trace

*Reading.* The traced part is the first two-knot part, by least member numbers, of Ring(5, 3) after round 2 under FLOOR0.
Its descendants are followed through rounds 3 and 4 (the two rounds asked for), and further through rounds 5 and 6 so
that the settled statement's account of what j does can be checked under each treatment. For every birth descending from
the part, the trace gives its kind, parents, D, f, usable and barred counts, and whether it is short in the next round.
It also gives the groups, the cancelled groups and the waiting and retiring members among the part's descendants, and
the parts the descendants form after each round. Checked against the first settled statement:

- Round s + 1 has exactly three births. One is a join j of both members, with D = 2 and f = 1. The others are one
  offshoot of each member, each with D = 1 and f = 2.
- In round s + 2, j is short and both groups (each offshoot with j) are cancelled. Each offshoot makes two offshoots,
  which form a two-knot part joinable only through that offshoot: its one met set has that offshoot as its only common
  knot.
- What j does depends on the treatment. Under retire, j retires and makes nothing, then or later. Under offshoot, j
  makes one offshoot, which is a part of one member after round s + 2 and makes a two-knot part in round s + 3. Under
  wait, j waits in round s + 2, is in no group in round s + 3, makes one offshoot there, and that offshoot makes a
  two-knot part in round s + 4.

The same checks are also run, without the printed trace, on the first two-knot part of Ring(5, 3) under FLOOR1 and under
ONE-FEWER, because the settled statement names all three rations.

## C15. Determinism

*Reading.* Every script is run again in a fresh process with another PYTHONHASHSEED, writing to a separate folder. The
JSON outputs are compared with the `resources` and timing fields removed.

## C16. P9's verdict (added after run 4; it changes no computation)

*What happened.* Under (FLOOR0, CANCEL-WAIT, HOLD), on both small starts, no part copies itself, and the run jams (two-knot
start at round 7, three-knot start at round 6). N(n) = 0 for every n >= 2. The cause, read from the round records (it is
not an engine fault): j is short in every round. Each group {j, oa} is therefore cancelled in every round, and oa holds
its distinction for good under HOLD, so it stays a member. Its offshoot ooa then makes two offshoots whose common knot
ooa also meets oa. Their met set is {oa, o1, o2}, so they join the stuck part instead of forming a two-knot part.

*Question.* The decision rule judges each prediction by its "Fails when" column. For P9 that column reads "a recurrence
fails from round 8 on". Under waiting the recurrence N(n) = 2 N(n - 3) holds from round 8 on, but only because both
sides are 0. The prediction's own sentence also says that "the two-knot part still copies itself".

*Reported.* (a) The registered "Fails when" condition: no recurrence fails at any n from 8 to 16, so P9 does not fail
under the decision rule. (b) The full statement: the first clause fails under (FLOOR0, CANCEL-WAIT, HOLD) on both small
starts, and the waiting recurrence holds only because N = 0. Both are printed by summarize.py. The summary line gives
(b) as the substantive result.

## C17. Runs shortened by the bound on knots (added after the runs)

Each of these runs passed 20,000 knots before its last registered round. Under A-D9 it was read through the round that
passed the bound, and under C2-b through the round before.

- Run 1: every run. The round that passed the bound was 15 to 23, depending on start and law. `run1.json` gives
  `rounds_done` and `last_round_under_cap` for each run.
- Run 4: the RATION-3 runs, at rounds 11 to 13.
- Run 6: (RATION-4, CANCEL-OFFSHOOT) at round 9 (37,735 knots) and (RATION-4, CANCEL-RETIRE) at round 10 (32,415
  knots), against 12 rounds registered.

Run 5 cut off 616 FLOOR0 and 727 FLOOR1 runs with offshoots past 1,500 knots, and none under the other treatments. In
run 5 the C2-a and C2-b counts are equal.

## C18. Run 5 was run twice (added after the runs)

The first full run of `run5.py` was followed by an addition of three descriptive fields:

- `copy_two_knot`: whether a two-knot part copies itself.
- `kt_zero_fresh_in_fail_round`: whether a birth with f = 0 was made in the first failing round.
- The peak memory of the largest worker.

Run 5 was then run again. Every count of the first run's tables (copy, knot-test failures, cut-offs, kinds, smallest
copying part, first failing round) is equal in the second. The second run's files are the ones kept.

## C19. Mixed parts in run 5 (added after the runs)

Seven census runs record a mixed part (A-D5). Six are on atlas graph 36 with loose counts [2,2,3,1,1], [2,3,3,1,1] and
[3,2,2,1,1], each under FLOOR0 and FLOOR1 with CANCEL-WAIT. The seventh is on atlas graph 43 with [2,1,1,3,3] under
(FLOOR0, CANCEL-WAIT). In every case both parts whose descendants merge are not past their start: they hold start
knots that meet each other. Such parts are never searched for returns, so no return, copy or count is affected. Past
the start no mixed part occurred.
