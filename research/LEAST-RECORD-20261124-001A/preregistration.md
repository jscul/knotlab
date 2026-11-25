# How little has to be written for a knot to find its parents? Pre-registration

Ticket `LEAST-RECORD-20261124-001A` of epic `LEAST-RECORD-20261124-001` (sub-goal B325 after its first step; goals G5 with
G18). Frozen on 2026-11-24, after the advisor's cold review and before the study's code is written. The code is the search
program of `PARENTS-FROM-HOLDERS-20261124-001`, extended by its author from this text. It uses that study's
[pre-registration](../PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md) ("the earlier text") for the words look,
alike, confusable pair, parent place and holder step, and [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md)
("the shared definitions", cited by line). The canonical K1–K3 test is unchanged.

## The question

Births made one at a time build what the complete rounds build if each birth records its parents (assumption A242). The
search before this one found that the parents cannot be found from what is built alone: in half-built structures a place
leading to a parent and a place leading to a child can be exchanged by a renaming of the whole structure. So something has
to be written. The owner gave the go-ahead on 24 November 2026 for the next step: how little?

The study writes one **stamp** on each knot, tries stamps of two values, of three, and larger, and asks for each whether
the parents can then be found by a look of bounded distance in every structure reached. ("The least record" of the
epic's title is this: the smallest thing written that will do.)

## In standard terms

Orienting the links of an anonymous network with labels of constant size: which labelling of the nodes lets every node tell
its predecessors from its successors by looking a bounded distance? Each from memory, the literature's, not checked:
where every link joins consecutive ranks the network is graded, and the rank modulo three is the layer counter of
self-stabilizing unison and phase clocks (Couvreur, Francez and Gouda, 1992); in the words of proof-labelling schemes
(Korman, Kutten and Peleg, 2010) it is a constant-size certificate of a layered orientation, where a general acyclic
orientation needs labels that grow with the network.

## Definitions

- **Look, alike, confusable pair, parent place, holder step**: as the earlier text. A look now also shows the stamp of every
  knot it shows, and nothing of a knot farther than d. A renaming must keep stamps. "Mark" stays the earlier text's word
  for loose and usable, loose and barred, or shared.
- **A half-built structure** is a structure after some birth of a run that makes births one at a time. (The shared
  definitions use "state" for an allowed assignment; it is not used here.)
- **Generation** (shared definitions, line 121, there for one birth at a time; used here for complete rounds as well):
  start knots have generation 0, and a new knot has generation one more than the greatest generation of its parents. Under
  waiting a knot's generation is not its round of birth.
- **A stamp** is a value written on a knot by whoever runs the growth, at the event named, and never changed except as
  stated. The stamps tried:

| Stamp | Values | What is written | What the writer needs | An old knot rewritten? |
| --- | --- | --- | --- | --- |
| NONE | 1 | nothing | — | no |
| NOT-MEMBER | 2 | whether the knot has no usable loose place | nothing: every look already shows it | — |
| HAS-CHILD | 2 | whether the knot has made at least one birth | the birth, at the parent | yes, once |
| JOIN | 2 | whether the knot has two or more parents | its own birth | no |
| START-KNOT | 2 | whether the knot is a start knot | knowledge no birth has: it comes with the start | no |
| GENERATION-MOD-2 | 2 | the knot's generation modulo 2 | its parents' stamps | no |
| GENERATION-MOD-3 | 3 | the knot's generation modulo 3 | its parents' stamps | no |
| HAS-CHILD with START-KNOT | 4 | both | as above | yes, once |
| PARENT-COUNT | grows with the law | the number of the knot's parents | its own birth | no |
| GENERATION | grows with the growth | the knot's generation | its parents' stamps | no |

- A new knot writes a generation stamp as one more than its parents' stamps, which needs the parents of one birth to have
  equal generations. Where they differ, the stamp is computed from the true generation and the birth is counted.
- **With a stamp shown, a rule of distance d recovers the parents** on a population when the population has no confusable
  pair at distance d. The rule is then stated and checked against every chosen place.
- **The cost of a stamp** is the row of the table: its number of values, the least distance at which a rule recovers the
  parents, what the writer needs, and whether an old knot is rewritten. The result reports the table; a stamp is called
  **a stamp of fewest values** only among those that recover the parents under the stated condition.
- **Left out, as a different question:** a stamp on places. One bit on each place of a knot, saying whether the knot took
  it at birth, is the full record of parents, read at distance 0. It is the baseline: one bit per place of each knot.

## Prior work in the program

Searches, each with `--until 2026-11-24 --exclude LEAST-RECORD-20261124-001`:

`python3 -B scripts/track.py objects "two shared places, one leading to a parent and one not, alike within d holder steps" --until 2026-11-24 --exclude LEAST-RECORD-20261124-001`

`python3 -B scripts/track.py objects "a mark written on each knot, generation modulo three, orientation recovered from marks" --until 2026-11-24 --exclude LEAST-RECORD-20261124-001`

`python3 -B scripts/track.py objects "generation of a knot, the simulator's record of who was made from whom" --until 2026-11-24 --exclude LEAST-RECORD-20261124-001`

- `PARENTS-FROM-HOLDERS-20261124-001` — the same object with no stamp: its populations, its look and its program are used
  here, and its result is the row NONE.
- `LOCAL-ROUND-20261123-001` — the source: its guards use a written record of parents; a stamp that recovers the parents
  could stand in for that record. Its brood argument is what the main prediction rests on.
- `INFLUENCE-CONE-20261120-001` — unrelated (how far one change reaches under ordinary growth).
- `FEEDER-PAYOFF-REVERSAL-20261121-001`, `TWO-BIT-ROWS-20261112-001` — unrelated (a learned preference; rows of two
  distinctions under another growth).
- `TWO-READERS-ONE-SURVIVING-SIGN-20261121-001` — a relative in kind only: a record of three values kept across turns and
  read back as a meter, in another setting.
- `NAE-GROWTH-20261119-001` — unrelated (the cheapest growth under not-all-equal).
- `RING-IN-BALANCE-20261123-001` — the shared definitions, where the generation is defined as the simulator's record and
  "not read from the structure".

## Prior work outside the program

As under "In standard terms". What this would add is whether the growth laws here are graded in that sense, in which
structures they are not, and what a stamp of two values can and cannot do. Not searched further.

## Known before the freeze (disclosed)

Nothing was run for this study. From the earlier search: with no stamp, half-built structures hold confusable pairs at
every distance under every law, the smallest with two knots; on complete rounds a rule exists at distance 2 under
(FLOOR1, CANCEL-RETIRE) and none of any fixed distance under (FLOOR1, CANCEL-OFFSHOOT).

Hand work, by the thread and then by the advisor in its review; none of it run:

- **NOT-MEMBER is already visible** (the thread; the advisor agrees). A knot has made its last birth, or retired, or never
  held a usable loose place, exactly when it has no usable loose place now. The thread had proposed this as the first
  stamp to try, in its report on the earlier search, before seeing that it adds nothing.
- **HAS-CHILD fails with three knots** (the advisor). Take the two-knot start `[[0,1,2],[0,3,4]]` after the first offshoot
  of its first knot A. The second start knot B and the offshoot each have three places, one shared with A and two loose,
  and neither has made a birth. Swapping them renames the whole structure and keeps HAS-CHILD. It carries B's place to A,
  which is between start knots, onto the offshoot's place to A, which is a parent place. START-KNOT and
  GENERATION-MOD-2 separate that pair.
- **HAS-CHILD adds nothing on the complete rounds of the proved case** (the advisor). Under (FLOOR1, CANCEL-OFFSHOOT) from
  the two-knot start a knot has made a birth exactly when it is no member, so the proved pair survives with the same
  threshold.
- **GENERATION-MOD-3 should recover every parent at distance 1 wherever births have parents of equal generations** (the
  thread). The other holder of a shared place is then a parent exactly when its stamp is one less, modulo 3, and two start
  knots that share a place have equal stamps.
- **GENERATION-MOD-2 cannot work at any distance in two cases** (the advisor). Where births have parents of equal
  generations, the stamp is fixed by its value at the centre, so it adds one bit and no more. Under ordinary growth, in
  the finished structure of 16 knots from the lone four-place knot, a renaming fixes a round-1 knot and exchanges its
  parent with one of its children, and keeps every generation's parity. Under (FLOOR1, CANCEL-OFFSHOOT) the proved pair,
  moved to a knot far from the start, still exchanges a parent with a child.
- **No two-valued stamp is known to work, and none is ruled out in general** (the advisor). A two-valued word with no
  mirror symmetry, written by generation modulo six, might work at a distance of about five; the advisor could not make
  that sound, and its writer would need a look of that distance. Left open, not run.
- **On the start-clause counterexample births have parents of unequal generations** (the thread, traced by the advisor).
  In round 1 its first knot is short and waits while the knots it meets act. In round 2 it is in one group of four with
  three round-1 joins. That join has parents of generations 0, 1, 1 and 1 and generation 2, and the modulo-3 rule reads its
  place to the start knot the wrong way from both sides. It cascades: the start knot's offshoot and that join are joinable
  in round 3.

## Settled by construction (stated, not tested)

- **Equal generations** (a proof sketch by the advisor, for the referee). Under the release rule every knot acts in at
  most one round and spends everything, so a member has no children. A common knot of two members is therefore, for each
  of them, a parent, or a start knot that meets it. If it is a parent of both, they were born in its one round with equal
  generations, by induction. If both are start knots, both have generation 0. The remaining case is the only leak: a start
  knot that waited while a start knot it meets acted, joined with that knot's child. Groups are pairwise joinable, so
  groups of three or more are covered. So every birth's parents have equal generations **wherever no start knot waits in a
  round in which a start knot it meets acts**. Where no knot waits at all (a short knot retires or makes offshoots, and
  ordinary growth) the generation is the round of birth.
- Given equal generations, a child's generation is exactly one more than each parent's, and the modulo-3 rule is correct.
- GENERATION recovers the parents at distance 1 everywhere: a parent has a smaller generation than its child.
- A stamp that is a function of what the look already shows within distance d changes no class of looks at distance d or
  more. On complete rounds this covers NOT-MEMBER, and HAS-CHILD wherever a knot has made a birth exactly when it is no
  member.
- If the parents are recovered exactly from a look, the guards of the one-birth-at-a-time study can use the recovered
  parents in place of the written record and decide the same.

## What is supplied

Everything the earlier search supplied, and here: every stamp, and who writes it and when; the reading of cost as a table;
the populations; the condition under which the main prediction is made. A stamp is written by whoever runs the growth.
Nothing in the growth laws writes or looks at one.

## What a result would and would not show

- **If GENERATION-MOD-3 recovers the parents at distance 1**, the plain sentence is the advisor's: if every new knot
  writes one of three values, one step on from its parents' value, any knot can tell parents from children by comparing
  values with its neighbours. This works because under these laws all parents of a birth are equally many births from the
  start, except where a waiting start knot meets one that acts. The value is the order of descent cut down to three
  values. The growth does not supply it; the study would show how small the record can be, not that it can be done
  without.
- **A failure of every two-valued stamp tried** would show that one bit per knot of these kinds is not enough, not that no
  bit is.
- Nothing here bears on whether the round can be done without.

## Populations

- **P1 and P2** of the earlier text, unchanged: the structures of the one-birth-at-a-time study after each complete round
  and after every birth of twenty sampled orders; and the same starts grown to about 2,000 knots or twelve rounds.
- **The condition**, computed for each start and law from its complete rounds: whether, in some round, a start knot waits
  while a start knot it meets acts. The starts are split into those where it never happens and those where it does. The
  thread expects the second set to be the start-clause counterexample alone.
- **P3, holding** (reported): the reference structures of `GUARD-CAP-AND-HOLD-20261124-001` under its four laws with
  holding, on the cycle of four through dead knots, the ring of five, and the two-knot and three-knot starts, after each
  of rounds 1 to 6 (or to the round the growth ends).
- In half-built structures of P1 a birth that the complete rounds do not make can occur only where the earlier guard
  mismatched, which was on the start-clause counterexample; such births are counted.

## Runs (frozen)

1. **Checks of the code before any run.** (a) The earlier study's three checks still pass with the stamp NONE. (b) With a
   stamp that is the same on every knot, every class of looks is unchanged. (c) On the structure A = `[0,1,2]`,
   B = `[0,3,4]`, a1 = `[1,5,6]`, a2 = `[2,7,8]`, J = `[5,7,9]`, with a1 and a2 offshoots of A and J their join, the
   generations are 0, 0, 1, 1, 2, and the kinds of every shared place come out as stated here by hand. (d) A stamp changed
   on one knot four steps from the centre is unseen at distances 1 to 3 and seen from 4.
2. **Every stamp of the table**, on P1 and P2, distances 1 to 6: the classes of looks, the classes holding a parent place
   and a place that is not one, split as before (within one structure; across rounds; across starts), the least distance
   with no confusable pair overall and by round, and two guard counts: the chosen places whose look holds no start knot
   and no member, and, among those, the ones whose look holds no place shared by two start knots.
3. **Generations.** For every birth of every structure: whether its parents have equal generations, and the greatest
   difference between a child's generation and a parent's, by law and start, with the condition of each start.
4. **Where a rule recovers the parents with a stamp shown:** the rule, stated and checked against every chosen place.
5. **Where none does:** the confusable pair with the fewest knots, written out with its renaming.
6. **The starts where the condition fails**, separately: every stamp, and GENERATION modulo one more than twice the
   greatest difference found in run 3.
7. **P3**, with NONE, GENERATION-MOD-3 and GENERATION, and run 3's counts.

## Predictions (frozen)

Hand predictions that were not run are marked (b), with whose hand; a check is true by construction or by a stated proof
sketch; (c) is open.

| # | Prediction | Fails when |
| --- | --- | --- |
| Checks | The four checks of run 1 hold. | any fails |
| P1 (b, the thread's; a check of the advisor's proof sketch) | On every start where the condition holds, under every law, in every structure of P1 and P2, every birth's parents have equal generations, and with GENERATION-MOD-3 shown the rule "the other holder is a parent exactly when its stamp is one less, modulo 3" recovers the parents at distance 1. | a birth with parents of unequal generations there, or a place the rule gets wrong there |
| P2 (b, the thread's, traced by the advisor) | The condition fails on the start-clause counterexample and on no other registered start. There a birth of round 2 has parents of generations 0 and 1, and the modulo-3 rule gets its place to the start knot wrong. | the condition fails elsewhere, or holds there |
| P3 (a check) | With GENERATION shown the parents are recovered at distance 1 everywhere, P3 included. | a place it gets wrong |
| P4 (a check) | NOT-MEMBER changes no class of looks at any distance. | a class changes |
| P5 (b, the advisor's) | HAS-CHILD leaves a confusable pair at every distance in the three-knot structure described above, and changes no class of looks on the complete rounds of the two-knot start under (FLOOR1, CANCEL-OFFSHOOT). | the three-knot pair is separated, or a class changes there |
| P6 (b, the advisor's) | GENERATION-MOD-2 leaves a confusable pair at every distance from 1 to 6: under ordinary growth in the finished structure of 16 knots, and under (FLOOR1, CANCEL-OFFSHOOT) on the grown structures of twelve rounds at distances up to 4 at least. | no such pair in the finished structure, or none at some distance from 1 to 4 under the second law |
| P7 (c) | START-KNOT, JOIN, PARENT-COUNT and HAS-CHILD with START-KNOT: the least distance with a rule, by law and population, with both guard counts and the least distance by round. Reported. | not applicable |
| P8 (c; the thread and the advisor expect none) | Whether any stamp of two values in the table recovers the parents, with a guard count that is not zero, on every structure of every start where the condition holds. Reported. | not applicable |
| P9 (b, the advisor's lean) | Under holding (P3) some birth has parents whose generations differ, and the modulo-3 rule fails there. | every birth's parents have equal generations under holding |

A result that fails is reported as it is.

## Runs and stop rule

- **Stop**: when every stamp of the table has its row of costs on P1 and P2, split by the condition, and either a stamp of
  fewest values that recovers the parents where the condition holds is named with its rule, or every stamp other than
  GENERATION has a confusable pair written out. The headline is quantified by the condition and by law; where the
  condition fails the result says what does work there.
- **A rule found only where every look reaches a start knot or a member is not counted.** A stamp is said to recover the
  parents at a distance only if the guard count there is not zero, and for GENERATION-MOD-2 only if the second guard count
  is not zero.
- **One program.** The earlier study's search program, extended by its author. Its checks are those of run 1.
- **Resources.** Each run under ten minutes and 8 GB on one process where it can be; anything longer in a background unit
  with a memory cap and a row in the long-running index. No time budget replaces a stated bound.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor** (Claude Fable 5.2, no tools) reviewed the first draft cold before the freeze
  (`../LEAST-RECORD-20261124-001/advisor/`). It turned the main prediction's argument into a proof sketch with one named
  leak, and asked that the condition be computed for every start in place of an exception made by name. It showed by hand
  that the stamp "has made a birth" fails with three knots, and that the generation modulo 2 cannot work at any distance in
  two named cases. It replaced "least" as a single order by a table of costs, named the stamp on places as a different
  question, added the second guard count and the stamp JOIN, and found that "mark" was already the earlier text's word, so
  what is written here is a "stamp".
