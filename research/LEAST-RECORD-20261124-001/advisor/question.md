You are the design advisor for a small pre-registered computational study in a research program on "knot growth". Review the design COLD, before it is frozen. You have no tools; everything is below: (1) the draft pre-registration, (2) the pre-registration of the study it extends (frozen; it defines look, alike, confusable pair, parent place), (3) the result of that study, (4) the shared definitions of the growth (cited by line), (5) the part of an earlier study's definitions that states the "brood argument". Do hand work where it helps and say that it is hand work. Be adversarial.

Background in three sentences. Growth proceeds in complete rounds; a new knot takes one loose distinction from each of its parents and receives fresh ones; the two holders of a shared distinction do not say which is the parent. An earlier search showed that the parents cannot be found from the structure alone (in half-built states a place to a parent and a place to a child can be exchanged by a renaming of the whole structure). This study writes one mark on each knot and asks how small a mark is enough.

Word rules of the program: one word for each meaning; no words from a space of two or three dimensions for the program's own objects; a new word must not reuse a stem the record uses otherwise or have a settled outside meaning the program might cite in another sense.

Answer under these numbers, in short lines, no preamble:
1. **P1's argument.** Is it true that under RELEASE, where no start knot that acts meets a start knot that waits, every birth's parents have equal generations (generation as in the shared definitions, line 121)? Check: the start (members that meet members, as on Ring(5,3)); CANCEL-WAIT (a waiter joins later: with whom, and of what generation?); CANCEL-OFFSHOOT and CANCEL-RETIRE; ordinary growth with groups of three or more; the half-built states of births made one at a time. Is P1' right about the start-clause counterexample (its stars are `[[1,2,3,7,8],[1,4,9,10],[2,5,11,12],[3,6,13,14],[4,15,16],[5,17,18],[6,19,20]]`, law (RATION-3, CANCEL-WAIT, RELEASE): knot 0 is short in round 1 and waits; in round 2 it joins)? Give a counterexample to P1 by hand if you can find one among the registered starts (the cycles D2(n,3), Ring(5,3), the two-knot start [[0,1,2],[0,3,4]], the three-knot start [[0,1,2,3],[0,1,4,5],[2,3,6,7]], the lone four-place knot, the seven-knot generator of the shared definitions lines 152-153, the cycle of eight with three extra dead knots).
2. **The marks.** Is "DONE is already visible" right in every state, including half-built ones and knots that wait? Is the claim about GIVEN (P4) right: does the proved look-alike pair under (FLOOR1, CANCEL-OFFSHOOT) survive when every knot shows whether it has given? Is P5 right, and can you settle by hand whether GEN-2 recovers the parents at some larger distance under any law? Is there a two-valued mark I have missed that plainly works (for example one written on the child rather than the parent), or an argument that no two-valued mark on knots can work in general?
3. **"Least".** Is "the fewest values a mark can take" the right order? Should who writes the mark, and when, be part of the cost (GIVEN is written on an old knot by a later event; GEN-3 is written once by the new knot from its parents' marks; START comes with the start)? Is a mark on places rather than on knots a different question that should be named and left out?
4. **Design.** Anything undefined or impossible to implement; any prediction true by construction, undecidable by the registered runs, or that you expect to fail; anything that would make the result an artifact (the earlier study guarded against small structures by counting the places whose look holds no start knot and no member).
5. **Scope.** What would "GEN-3 recovers the parents at distance 1" honestly show, given that the mark is written by hand and is itself a count of rounds of descent? Give the plain sentence for the owner. What is its name in the literature (cite from memory, marked as such)?
6. **Words.** mark; DONE, GIVEN, START, TOOK, GEN-2, GEN-3, GEN; "recovers the parents"; "the least mark".


# (1) DRAFT PRE-REGISTRATION OF THIS STUDY

# How little has to be written for a knot to find its parents? Pre-registration

Ticket `LEAST-RECORD-20261124-001A` of epic `LEAST-RECORD-20261124-001` (sub-goal B325 after its first step; goals G5 with
G18). Frozen on 2026-11-24, after the advisor's cold review and before the study's code is written. The code is the search
program of `PARENTS-FROM-HOLDERS-20261124-001`, extended by its author from this text. It uses that study's
[pre-registration](../PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md) ("the earlier text") for the words look,
alike, confusable pair, parent place and holder step, and [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md)
("the shared definitions", cited by line). The canonical K1–K3 test is unchanged.

## The question

Births made one at a time build what the complete rounds build if each birth records its parents (assumption A242). The
search before this one found that the parents cannot be found from what is built alone: in half-built states a place
leading to a parent and a place leading to a child can be exchanged by a renaming of the whole structure. So something has
to be written. The owner gave the go-ahead on 24 November 2026 for the next step: how little?

The study writes one **mark** on each knot, tries marks of two values, of three, and larger, and asks for each whether the
parents can then be found by a look of bounded distance in every state reached.

## In standard terms

Orienting the links of an anonymous network with labels of constant size: which labelling of the nodes lets every node tell
its predecessors from its successors by looking a bounded distance? In the literature's words a proof-labelling scheme, or
local certification, of an orientation (Korman, Kutten and Peleg, 2010; cited from memory, not checked); the three-valued
mark below is the literature's counter modulo three, which orients a link when its two ends differ by one.

## Definitions

- **Look, alike, confusable pair, parent place, holder step**: as the earlier text. A look now also shows the mark of every
  knot it shows, and a renaming must keep marks.
- **Generation** (shared definitions, line 121): start knots have generation 0, and a new knot has generation one more
  than the greatest generation of its parents.
- **A mark** is a value written on a knot by whoever runs the growth, at the event named. It is never changed except as
  stated. The marks tried, with the number of values each can take:

| Mark | Values | What is written | When, and by whom |
| --- | --- | --- | --- |
| NONE | 1 | nothing | the earlier study |
| DONE | 2 | whether the knot has made its last birth or retired | on the knot, at its last birth or when it is barred |
| GIVEN | 2 | whether the knot has made at least one birth | on the parent, at its first birth |
| START | 2 | whether the knot is a start knot | with the start |
| GEN-2 | 2 | the knot's generation modulo 2 | on the new knot, at its birth, from its parents' marks |
| GEN-3 | 3 | the knot's generation modulo 3 | on the new knot, at its birth, from its parents' marks |
| GIVEN+START, GIVEN+DONE | 4 | both | as above |
| TOOK | grows with the law | the number of the knot's parents | on the new knot, at its birth |
| GEN | grows with the growth | the knot's generation | on the new knot, at its birth, from its parents' marks |

- A new knot can write GEN-2, GEN-3 and GEN from marks it meets at its birth: one more than the greatest mark of its
  parents. For GEN-2 and GEN-3 that needs the parents of one birth to have equal generations, or the greatest is not
  defined modulo 2 or 3; where they differ the mark is computed from the true generation and the case is counted.
- **A mark recovers the parents at distance d** on a population when, with that mark shown, the population has no confusable
  pair at distance d. The rule is then stated, and checked against every chosen place.
- **The least mark** is one with the fewest values that recovers the parents at some distance from 1 to 6 on every state
  of both populations, under every law.

## Prior work in the program

Searches, each with `--until 2026-11-24 --exclude LEAST-RECORD-20261124-001`:

`python3 -B scripts/track.py objects "two shared places, one leading to a parent and one not, alike within d holder steps" --until 2026-11-24 --exclude LEAST-RECORD-20261124-001`

`python3 -B scripts/track.py objects "a mark written on each knot, generation modulo three, orientation recovered from marks" --until 2026-11-24 --exclude LEAST-RECORD-20261124-001`

`python3 -B scripts/track.py objects "generation of a knot, the simulator's record of who was made from whom" --until 2026-11-24 --exclude LEAST-RECORD-20261124-001`

- `PARENTS-FROM-HOLDERS-20261124-001` — the same object with no mark: its populations, its look and its program are used
  here, and its result is the row NONE.
- `LOCAL-ROUND-20261123-001` — the source: its guards use a written record of parents; a mark that recovers the parents
  could stand in for that record.
- `INFLUENCE-CONE-20261120-001` — unrelated (how far one change reaches under ordinary growth).
- `FEEDER-PAYOFF-REVERSAL-20261121-001`, `TWO-BIT-ROWS-20261112-001` — unrelated (a learned preference; rows of two
  distinctions under another growth).
- `TWO-READERS-ONE-SURVIVING-SIGN-20261121-001` — a relative in kind only: a record of three values kept across turns and
  read back as a meter, in another setting.
- `NAE-GROWTH-20261119-001` — unrelated (the cheapest growth under not-all-equal).
- `RING-IN-BALANCE-20261123-001` — the shared definitions, where the generation is defined as the simulator's record and
  "not read from the structure".

## Prior work outside the program

Counters modulo three are the standard constant-size way to orient the links of a network in which every link joins
consecutive levels (used in self-stabilizing spanning trees and in synchronizers; Awerbuch 1985; cited from memory). What
this would add is whether the growth laws here have that property, in which states, and what a mark of two values can and
cannot do. Not searched further.

## Known before the freeze (disclosed)

Nothing was run for this study. From the earlier search: with no mark, half-built states hold confusable pairs at every
distance under every law, the smallest with two knots; on complete rounds a rule exists at distance 2 under
(FLOOR1, CANCEL-RETIRE) and none of any fixed distance under (FLOOR1, CANCEL-OFFSHOOT).

Hand reasoning by the thread, not run:

- **DONE is already visible.** Under the release rule a knot that has made its last birth has no usable loose place, and a
  retired knot's loose places are barred; a knot that has not finished has a usable loose place. So DONE is a function of
  what a look already shows. The thread proposed DONE as the first mark to try, in its report on the earlier search,
  before seeing this.
- **GIVEN separates the smallest pair** (a knot and its first offshoot: only the first has given) but adds nothing far from
  the live roster, where every knot has given.
- **GEN-3 should recover every parent at distance 1.** By the brood argument of the one-birth-at-a-time study, under the
  release rule the knots that can join are made in one round from parents of one generation, so every birth's parents have
  equal generations, and a child's generation is exactly one more than each parent's. Then the other holder of a shared
  place is a parent exactly when its mark is one less, modulo 3; and two start knots that share a place have equal marks.
- **GEN-3 should fail on one registered start.** The brood argument needs that no start knot that acts meets a start knot
  that waits. On the start built to break that (the start-clause counterexample of the one-birth-at-a-time study), a start
  knot waits one round and then joins knots of generation 1. That join has parents of generations 0 and 1, its own
  generation is 2, and the rule reads its place to the start knot the wrong way from both sides.
- **GEN-2 cannot do the same at distance 1**: both a parent and a child differ from a knot by one, so both have the other
  value. Whether a longer look repairs it is not settled by hand.

## Settled by construction (stated, not tested)

- GEN recovers the parents at distance 1: a parent has a smaller generation than its child, and two start knots have the
  same. This is a check.
- If a mark is a function of what the look already shows within distance d, adding it changes no class of looks at
  distance d or more.
- If the parents are recovered exactly from a look, the guards of the one-birth-at-a-time study can use the recovered
  parents in place of the written record and decide the same.

## What is supplied

Everything the earlier search supplied, and here: every mark, and who writes it and when; the reading of "least" as the
fewest values; the populations. A mark is written by whoever runs the growth. Nothing in the growth laws writes or looks
at one.

## What a result would and would not show

- **A mark of few values that recovers the parents** would show how small a record can stand in for the written parents in
  the states searched, and, if it is GEN-3, that a new knot can write it from the marks of its own parents with no other
  knowledge. It would not show that the growth supplies such a mark: it is written by hand.
- **A failure of every two-valued mark** would show that one bit per knot of these kinds is not enough, not that no bit is.
- Nothing here bears on whether the round can be done without, or on the record a law with holding would need, beyond the
  one open item below.

## Populations

- **P1 and P2** of the earlier text, unchanged: the structures of the one-birth-at-a-time study after each complete round
  and after every birth of twenty sampled orders; and the same starts grown to about 2,000 knots or twelve rounds.
- **P3, holding** (reported without a prediction): the reference structures of `GUARD-CAP-AND-HOLD-20261124-001` under its
  four laws with holding, after each round it compared.

## Runs (frozen)

1. **Checks of the code before any run.** The earlier study's three checks still pass with the mark NONE. With a mark that is
   the same on every knot, every class of looks is unchanged. With GEN, a hand-built structure of five knots gives the
   kinds stated here by hand.
2. **Every mark of the table**, on P1 and P2, distances 1 to 6: the classes of looks, the classes holding a parent place
   and a place that is not one, split as before (within one structure; across rounds; across starts), the least distance
   with no confusable pair, and the count of chosen places whose look holds no start knot and no member.
3. **Equal generations.** For every birth of every structure: whether its parents have equal generations. Reported by law.
4. **Where a mark recovers the parents:** its rule, stated and checked against every chosen place.
5. **Where it does not:** the confusable pair with the fewest knots, written out with its renaming.
6. **P3**, with NONE, GEN-3 and GEN.

## Predictions (frozen)

Hand predictions that were not run are marked (b); a check is true by construction; (c) is open.

| # | Prediction | Fails when |
| --- | --- | --- |
| Checks | The checks of run 1 hold. | any fails |
| P1 (b, the thread's, by the brood argument) | On every state of P1 and P2 other than those of the start-clause counterexample, under every law, every birth's parents have equal generations, and GEN-3 recovers the parents at distance 1 by the rule "the other holder is a parent exactly when its mark is one less, modulo 3". | a birth with parents of unequal generations there, or a place the rule gets wrong there |
| P1′ (b, the thread's) | On the start-clause counterexample some birth has parents of generations 0 and 1, and GEN-3's rule gets that knot's place to the start knot wrong. Whether GEN-3 still recovers the parents there at some larger distance is reported. | every birth there has parents of equal generations |
| P2 (a check) | GEN recovers the parents at distance 1. | a place it gets wrong |
| P3 (a check, by the argument above) | DONE changes no class of looks at any distance. | a class changes |
| P4 (b, the thread's) | GIVEN removes the two-knot pair, and under (FLOOR1, CANCEL-OFFSHOOT) it still leaves a confusable pair at every distance from 1 to 6 on the grown structures of eight or more rounds. | the two-knot pair stays, or some distance has no pair there |
| P5 (b, the thread's) | GEN-2 does not recover the parents at distance 1 under any law. | it does under some law |
| P6 (c) | For START, GEN-2 beyond distance 1, GIVEN+START, GIVEN+DONE and TOOK: the least distance with no confusable pair, by law and population. Reported. | not applicable |
| P7 (c) | Whether any mark of two values recovers the parents on every state under every law. Reported. The thread expects none does. | not applicable |
| P8 (c) | Under holding (P3): whether every birth's parents have equal generations, and whether GEN-3 still recovers the parents. Reported. | not applicable |

A result that fails is reported as it is.

## Runs and stop rule

- **Stop**: when every mark of the table has its verdict on P1 and P2, and either the least mark is named with its rule, or
  every mark below GEN has a confusable pair written out. This is the stop of the sub-goal's note (a distance with no
  look-alike pair on every state, or a pair the mark does not separate), taken over the whole table.
- **One program.** The earlier study's search program, extended by its author. Its checks are those of run 1.
- **Resources.** Each run under ten minutes and 8 GB on one process where it can be; anything longer in a background unit
  with a memory cap and a row in the long-running index. No time budget replaces a stated bound.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor** (Claude Fable 5.2, no tools) reviews this text cold before the freeze.


# (2) THE EARLIER STUDY'S PRE-REGISTRATION (frozen)

# Can a knot tell its parents from its children by what is built near it? Pre-registration

Ticket `PARENTS-FROM-HOLDERS-20261124-001A` of epic `PARENTS-FROM-HOLDERS-20261124-001` (the first step of sub-goal B325
only; goals G5 with G18). Frozen on 2026-11-24, after the advisor's cold review and before the study's code is written. The code is written by a helper agent
from this text alone. It uses [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("the shared
definitions", cited by line) and the words of
[the one-birth-at-a-time study](../LOCAL-ROUND-20261123-001/definitions.md) ("LR"). The canonical K1–K3 test is unchanged.

## The question

Births made one at a time can build what the complete rounds build, if each birth records its parents (assumption A242).
The two holders of a shared distinction do not say which of them is the parent. The owner asked on 24 November 2026 for
the first step of the open question only: "on the structures already built, search for pairs of knots that agree on
everything within d holder steps but differ in who their parents are, for d from 1 to 6. Stop at a rule that recovers the
parents on every structure reached, or at a pair no bounded reading tells apart."

No law is proposed and nothing is grown by a new rule. This is a search on structures that the recorded laws build.

## In standard terms

Whether an orientation of the links of a network can be recovered by a local rule: for each link at a node, is it
determined, by the unlabelled neighbourhood of radius d around the node, whether the link goes to a predecessor or to a
successor? In the literature's words this is local symmetry breaking in a network without identifiers; two nodes with
isomorphic radius-d neighbourhoods cannot be told apart by any rule of that radius (the literature's views and covering
arguments, Angluin 1980; cited from memory, not checked).

## Definitions

- **Structure, place, loose, usable, barred, shared, start knot, holder step, holder-step distance**: as the shared
  definitions and LR section 1.1. Every distinction in the structures used here has one or two holders.
- **The record of parents** is written by each birth (LR section 1.1). It is what the search is checked against, and it
  is not part of what is looked at.
- **The kind of a shared place.** Let a be a place of knot x that is shared with knot y. It is a **parent place** of x when
  y is a parent of x (x took a from y). Otherwise it is **not a parent place**: a child place (y took a from x), or a place
  shared by two start knots. The two main kinds are "parent place" and "not a parent place"; a child place against a
  place between start knots is reported separately and is not the question.
- **What is looked at within d holder steps of x**, with the place a chosen: the knots at holder-step distance at most d
  from x; for each of them its places, each marked as loose and usable, loose and barred, or shared; which places of
  these knots are one and the same distinction; for a shared place whose other holder is farther than d, only that it is
  shared; which knot is x; which place is a. No names, no rounds and no record of parents. Two choices are made here: a
  distinction shared by two knots that are both at distance d is seen as one distinction; and when two shared places lead
  to one and the same knot farther than d, that they lead to the same knot is not seen.
- Two such looks are **alike** when a one-to-one renaming of knots and of distinctions carries one onto the other: x to x,
  the chosen place to the chosen place, every mark kept.
- **A confusable pair at distance d** is two chosen places, one a parent place and one not, whose looks within d are
  alike. The owner spoke of pairs of knots; the pair here is of places, each on its knot, which is the same question asked
  place by place. Pairs are reported in three groups: on one knot or within one structure; across two rounds of one
  start; across two starts of one law. A pair across starts shows only that a rule would have to know the start.
- **A rule of distance d recovers the parents** on a population when the population has no confusable pair at distance d.
  The table from looks to kinds is then well defined on it. Where a rule exists the result also states the simplest
  description found that gives the same table, and says that the description is the thread's.
- **Two coarser looks**, as swaps: without the usable-or-barred mark (loose is loose); and with knots only as live or dead
  and their numbers of places (no record of which loose places are barred).

## Prior work in the program

Searches, each with `--until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`:

`python3 -B scripts/track.py objects "which holder of a shared distinction is the parent, read from the structure within a bounded distance" --until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`

`python3 -B scripts/track.py objects "two knots alike within d holder steps, isomorphic neighbourhoods, automorphism" --until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`

`python3 -B scripts/track.py objects "recognise the original knots from holdings, depth to the first knots, direction of descent" --until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`

- `LOCAL-ROUND-20261123-001` — the source of the question: its guards read a written record of parents, and its report
  names doing without that record as the open direction; its structures are the first population here.
- `ONE-PARENT-REREAD-20261123-001`, `SETTING-AS-REREAD-20261123-001`, `THIRD-HOLDER-20261123-001` — unrelated (births that
  take a distinction that is already shared; a different question about holders).
- `KEEP-READ-20261118-001`, `COPY-READ-20261118-001` — relatives in method only: local pictures of knots compared, under
  another growth and for another question.
- `SERIAL-REPAIRS-20261120-001` — a relative: its guard recovers the order of births from depth to the first knots,
  looking at the whole structure, on starts whose first knots can be recognised; it argues, without running it, that four
  to five holder steps suffice once the direction of each parent step is available. This study asks whether that
  direction is available locally.
- `DIRECT-REACH-20261115-001`, `LOOSE-NAMES-AND-SPENT-JOINS-20261120-001` — unrelated (reach along a chain of bonds; named
  births under ordinary growth).
- `READ-ORIGIN-20261120-001` — a relative: whether the first knots can be recognised from holdings.

## Prior work outside the program

Angluin's work on local and global properties of networks of processors (1980) and the theory of views (Yamashita and
Kameda) say that nodes with the same view cannot be distinguished by a deterministic local rule; orienting an anonymous
network is a standard problem there. Cited from memory and not checked; not searched further. What this would add is the
answer for the structures these growth laws build, where the start and the live roster break the symmetry at some distance.

## Known before the freeze (disclosed)

Nothing was run for this study. Known from the record: the structures of the first population and their records of
parents (the one-birth-at-a-time study and its reference engine). Hand reasoning by the thread, not run:

- At distance 1 confusable pairs are expected everywhere: a knot sees only its neighbours' places and marks.
- Far from the start and from the live roster, growth under a fixed ration is regular (every offshoot receives the same,
  every join the same), so a look that reaches neither may be the same from a parent's side and from a child's side. The
  thread could not settle by hand whether the short cycles that joins make (two parents, their common knot and their
  join) tell the two sides apart.
- On a small structure a look of a few steps reaches the start or the live roster, which are not alike, so a rule may
  exist there for a reason that does not carry to larger structures.

Hand work by the advisor in its review, not run:

- **Just enough for three places, the short knot making offshoots, from the two-knot start: a confusable pair at every
  distance.** Every knot there has three places. Each parent with its two offshoots and their join makes a cycle of four
  holder steps, and each of the four has one more shared place leading to another such cycle; the two start knots fit the
  same pattern. After round R the structure is everything within R steps of the start in that pattern. On an offshoot of a
  start knot, the place shared with that start knot (a parent place) and the place shared with its join (a child place)
  are exchanged by the renaming that swaps the start knot with the join. The pair is confusable exactly when d ≤ R − 2, so
  at distance 6 from round 8, and the least distance that tells it apart is R − 1.
- **The same ration with the short knot retiring:** the join keeps a barred place, which marks one side of every such
  cycle, so a rule at distance 2 or 3 is expected.
- **A fixed three with waiting, on the cycle of four through dead knots:** no pair found by hand. Every knot other than a
  start knot has three more places than parents, so a look shows each knot's number of parents; the advisor leans, with
  low confidence, toward a rule existing on the population.

## Settled by construction (stated, not tested)

- If two looks within d are alike, no rule that uses only what is within d can give them different kinds. So a confusable
  pair at distance d is a proof that no rule of distance d recovers the parents on a population holding that pair.
- A confusable pair at distance d is also one at every smaller distance.
- Being alike is certified both ways: a confusable pair is reported only with an explicit renaming that is checked place
  by place; "no confusable pair" is reported only when every two looks of different kinds are told apart by a quantity
  that any renaming must keep, or by an exhaustive search for a renaming that finds none. Any such quantity is computed on
  the extracted look alone, never on the whole structure, which would see one step too far at the look's rim.

## What is supplied

The laws that built the structures (assumptions A104, A224), the starts, and here: what counts as "everything within d
holder steps" (the look defined above, with two coarser swaps); the populations and their bounds; the reading of "a pair no
bounded reading tells apart" in the stop rule. The record of parents (A242) is used only as the answer the search is
checked against.

## What a result would and would not show

- **A rule at some distance** would show that on the structures searched the record of parents could be replaced by a look
  of that distance. It would not show that the same rule works on larger structures or under other laws, unless it comes
  with an argument.
- **A confusable pair at distance 6 whose least separating distance grows with the structure** would show that no fixed
  distance up to 6 is enough on these structures, and would be evidence that none is. A pair of places exchanged by a
  renaming of a whole structure would be a pair that no look tells apart on that structure at all.
- Neither shows anything about a law that would write less than the full record, for example only the round of birth.

## Populations

- **P1, the structures already built.** For each of the twenty pairs of start and law of the one-birth-at-a-time study
  (its `gate.json`), the reference structure after each complete round up to the last round it compared. And, for the law
  R3 at each cutoff, the structure after every birth of each of the first 20 sampled orders (seeds 0 to 19), built with
  that study's engine.
- **P2, the same grown further** (the thread's addition; the owner asked for the structures already built, and on those a
  look of a few steps reaches the start or a member). The same twenty pairs grown by the reference engine to the first round after which the
  structure has more than 2,000 knots, or to 12 rounds, whichever comes first; the structure after each round. Every knot
  of each final structure is tested under parity by both methods of the reference engine, and under not-all-equal where
  the structure has at most 600 knots.
- Pairs are searched within each structure and across all structures of one law (structures under different laws are
  not compared with one another).
- **The count that guards against an artifact.** For each law, round and distance: the number of chosen places whose look
  holds no start knot and no member. A rule found where that number is zero shows nothing about larger structures, and
  the result says so.

## Runs (frozen)

1. **Checks of the code before any run.** (a) On 200 drawn small structures (at most 8 knots within the look), being alike by
   the code equals being alike by trying every renaming. (b) The advisor's pair, as a check with an exact threshold: on the two-knot start under
   (FLOOR1, CANCEL-OFFSHOOT, RELEASE) after round R, for R from 4 to 9, the two places named above are confusable exactly
   for d ≤ R − 2. (c) A planted difference: one barred mark
   changed four steps from x is not seen at distances 1 to 3 and is seen from distance 4.
2. **P1**, distances 1 to 6, the full look and the two coarser looks: the number of chosen places of each kind, the number
   of classes of looks, the number of classes holding places of two kinds, and for each law the least distance with no
   confusable pair, if any.
3. **P2**, the same, by round of the structure.
4. **For each law and each distance with a confusable pair in P2:** the pair whose two knots are farthest from the start
   and from every member, written out (the two knots, their rounds of birth, those distances, the renaming), with the
   least distance at which it is told apart, up to 10. And for one pair of each law, followed from round to round where
   the same two places exist: that least distance as a function of the round.
5. **Whole-structure renamings.** For each final structure of P2 with at most 2,000 knots: whether some renaming of the
   whole structure onto itself carries a parent place to a child place.
6. **Where a rule exists** at some distance on P1 and P2 for a law: the table of looks, and the simplest description of it
   that the code's author can state and check against every place.

## Predictions (frozen)

Hand predictions that were not run are marked (b), with whose hand; (c) is open, reported without a prediction.

| # | Prediction | Fails when |
| --- | --- | --- |
| Checks | The three checks of the code hold, the second with its exact threshold d ≤ R − 2. | any fails |
| P1 (b, the thread's) | At distance 1 there is a confusable pair under every law in P2. | some law has none |
| P2 (b, the advisor's, with a proof by hand) | Under (FLOOR1, CANCEL-OFFSHOOT, RELEASE) there is a confusable pair at every distance from 1 to 6 once the structure has eight rounds, and for the advisor's pair the least distance that tells it apart is R − 1 at round R. No rule of a fixed distance recovers the parents there. | some distance from 1 to 6 has no confusable pair on that law's P2 structures of eight or more rounds, or the threshold is not R − 2 |
| P3 (b, the advisor's expectation) | Under (FLOOR1, CANCEL-RETIRE, RELEASE) a rule exists at distance 2 or 3 on P1 and P2: the barred place of a retired join tells the two sides apart. | a confusable pair at distance 3 |
| P4 (c; the advisor leans toward a rule, with low confidence) | Under (RATION-3, CANCEL-WAIT, RELEASE): whether a rule exists at some distance up to 6 on P2. Reported, with the count of places whose look holds no start knot and no member. | not applicable |
| P5 (c) | On P1 alone: the least distance with no confusable pair for each law, if there is one, with the same count. Reported. | not applicable |
| P6 (c) | Under ordinary growth, where what a knot receives follows the demand: whether a rule exists at some distance up to 6 on P2. Reported. | not applicable |
| P7 (c) | The two coarser looks: whether they change any least distance. Reported. | not applicable |
| P8 (b, the advisor's) | No whole structure has a renaming onto itself that carries a parent place to a place that is not one: the parent is always the holder nearer the start. | one does |

A result that fails is reported as it is.

## Runs and stop rule

- **Stop**, in the owner's words: at a rule that recovers the parents on every structure reached, or at a pair no bounded
  reading tells apart. Read here, for each law: either some distance from 1 to 6 has no confusable pair on P1 and P2 (the
  rule is then stated, with the count that guards against an artifact); or a confusable pair is followed from round to
  round and the least distance that tells it apart grows with the round, which is what "no bounded reading tells it
  apart" means on structures that keep growing. A confusable pair at distance 6 alone does not meet the second.
- **Resources.** Each run under ten minutes and 8 GB on one process where it can be; anything longer in a background unit
  with a memory cap and a row in the long-running index. No time budget replaces a stated bound.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor** (Claude Fable 5.2, no tools) reviewed this text cold before the freeze
  (`../PARENTS-FROM-HOLDERS-20261124-001/advisor/`). It proved by hand that one of the three laws the first draft lumped
  together has a confusable pair at every distance, expected a rule under the second and could not settle the third, so
  the prediction is now split by law. It supplied the planted check with an exact threshold, the count that guards
  against an artifact, the reading of the stop rule (a pair followed across rounds, not a pair at distance 6), the two
  main kinds of place, and the rule that a separating quantity is computed on the look alone.


# (3) THE EARLIER STUDY'S RESULT

# Can a knot tell its parents from its children by what is built near it? Result

Ticket `PARENTS-FROM-HOLDERS-20261124-001A` (the first step of sub-goal B325; goals G5 with G18), 2026-11-24. Computed
with code written from the frozen text; scientific referee pending. [Pre-registration](preregistration.md) ·
[code and its recorded readings](../../experiments/PARENTS-FROM-HOLDERS-20261124-001A/PARENTS-FROM-HOLDERS-20261124-001A-E001_parents_from_holders/deviations.md) ·
[the thread's own checks](../PARENTS-FROM-HOLDERS-20261124-001/checks/thread_checks.txt)

**Not in general, and where it matters most, not at all. In the half-built states that arise when births are made one at a
time, there are places leading to a parent and places leading to a child that no look at the structure can tell apart,
however far it goes: a renaming of the whole structure exchanges them. The smallest has two knots. On structures built by
complete rounds the answer depends on the law. Where a short knot retires, two steps are enough, because the retired knot
keeps a barred mark. Where it makes offshoots, no fixed distance is enough, by a proof found by hand and confirmed at every
round. Under a fixed ration of three with waiting, and under ordinary growth, the distance needed grew with the structure
as far as the search went. One finished structure keeps no trace of its order of birth at all.**

## What was searched

A shared place of a knot is a **parent place** when its other holder is one of the knot's parents. A **look** within d
holder steps of a knot is everything built there once names, rounds and the record of parents are dropped. Two places
are a **confusable pair** at distance d when one is a parent place, the other is not, and their looks are alike. Such a
pair proves that no rule that looks only that far can tell the two apart.

Two populations, four laws. **Already built:** the structures of the one-birth-at-a-time study, after each complete round
and after every birth of twenty sampled orders. **Grown further** (the thread's addition): the same starts grown by
complete rounds to about 2,000 knots or twelve rounds.

## Verdicts

| # | Verdict | What was found |
| --- | --- | --- |
| Checks | Hold | The comparison agrees with trying every renaming on 6,579 pairs of small looks. The advisor's pair has its exact threshold at every round from 4 to 9. A mark planted four steps away is unseen at distances 1 to 3 and seen from 4, 60 times of 60. |
| P1 | Holds | At distance 1 there is a confusable pair under every law. |
| P2 | Holds | Just enough for three places, the short knot making offshoots: a confusable pair at every distance from 1 to 6, and for the advisor's pair the least distance that tells it apart is exactly one less than the round, at every round from 2 to 12. No fixed distance recovers the parents there. |
| P3 | **Fails**, on the half-built states only | The same ration with the short knot retiring. On every structure built by complete rounds there is a rule at distance 2, and it is not an artifact of small structures (6,396 of the places it is checked on see neither a start knot nor a member). But among the half-built states there are confusable pairs at every distance, so no rule exists on the whole first population, which is what was predicted. |
| P4 | Open, reported | A fixed three with waiting. On the grown structures no pair is left at distance 5 or 6, but there every look reaches a start knot or a member, so this shows nothing. Round by round the least distance that works grows: 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5. |
| P5 | Open, reported | On the first population no law has a rule at any distance, because of its half-built states. On its complete rounds alone the least distances are 4, 2 and 2 for the three laws with a fixed ration, and none for ordinary growth. |
| P6 | Open, reported | Ordinary growth: no rule at any distance up to 6 on the grown structures; the least distance that works grows with the round, reaching 6 at rounds 11 and 12. |
| P7 | Open, reported | The two coarser looks change no least distance. |
| P8 | **Fails** | One finished structure does have a renaming that carries a parent place to a child place: the lone four-place knot under ordinary growth, which stops after four rounds with 16 knots of four places each and every distinction shared (in the literature's words, the graph of the four-dimensional hypercube). A renaming swaps the start knot with one of its offshoots. The other seven finished structures tested have none. |

## The three findings

1. **Half-built states can hide the parents completely.** After the first birth from the lone four-place knot there are
   two knots, each with one shared place and three loose ones. Nothing in the structure says which was first. The search
   found such pairs, exchanged by a renaming of the whole structure, under every law: 115, 8, 49 and 12 of them at
   distance 6 for the four laws. These are the states in which the guard of the one-birth-at-a-time study has to decide,
   and there the record of parents cannot be replaced by any look at what is built.
2. **On complete rounds it depends on what a short knot leaves behind.**
   - *It retires:* its barred place marks which side of each small cycle of knots came later, and a rule of five short
     steps, looking two holder steps out, gives every one of 18,030 places correctly.
   - *It makes offshoots:* every knot has three places and every small cycle looks the same from both sides. The advisor
     proved by hand that an offshoot's place to its parent and its place to its join stay alike until the look reaches the
     live roster, so the distance needed is one less than the round. The search confirms this exactly at every round, and
     so does the thread's own separate program for rounds 3 to 6.
   - *A fixed three with waiting, and ordinary growth:* the distance needed grew by about one every two rounds as far as
     the structures went. This is evidence that no fixed distance is enough, not a proof.
3. **A structure that closes can forget its order.** When the lone four-place knot's growth stops, every knot looks like
   every other. What was the start and what was made last cannot be told from the structure.

## What this does and does not show

- **It answers the first step of the open question as asked**, at its second stop: there are pairs that no bounded reading
  tells apart, and in half-built states none at all. A law that makes births one at a time cannot find the parents from the
  structure alone in every state it meets.
- **It does not show that the full record is needed.** Something has to be written, but perhaps much less: for instance
  one mark that a knot has finished giving, as the barred place of a retired knot already is under one of these laws. That
  was not tested.
- **It does not show unbounded growth of the distance** under a fixed three with waiting or under ordinary growth: there it
  is a trend over eleven or twelve rounds, and a single followed pair is in the end told apart by how far it is from the
  start.
- **The rule at distance 2 is a rule for complete rounds under one law.** It fails on 11,933 of 183,070 places of the
  half-built states, as it must.

## Deviations and limits

- **Two parts of the frozen text could not be run as written** (the engine's author reported both before the affected
  runs). The test for renamings of whole structures was bounded at 2,000 knots, and the grown structures stop just past
  2,000, so 12 of the 20 final structures were outside it; the last round under the bound was tested as an addition. And
  the instruction to state a rule "where one exists on both populations" applies to no law; the rule above is stated for
  the complete rounds, where it does exist.
- **P8 and the run that tests it were worded differently** by the thread ("a place that is not one" against "a child
  place"). The one case found fails both.
- **The first version of the first check was too easy** (most of its alike pairs were a look compared with itself). The
  engine's author strengthened it and reran it before the registered runs, and added 4,000 harder pairs checked against a
  separate matcher.
- **The 42 readings** taken by the engine's author are recorded with the code. The ones that matter: the half-built states
  are those of all 27 runs of the earlier study's widest guard, each counted once; a look is compared only through
  quantities computed on the look itself.
- **The knot test.** Every knot of the 20 final grown structures passes under parity by both methods; the four with at most
  600 knots also pass under not-all-equal. The other 16 were not run under not-all-equal, as registered.
- **Two runs took longer than ten minutes** (10 and 15 minutes), within their memory caps.
- **Evidence class:** exact computation, with one proof by hand (the advisor's) confirmed by two programs, and the
  thread's own check of the finished structure.
- **Scaffolds:** what counts as "everything within d holder steps" was swapped for two coarser looks, with no change. The
  populations and the laws that built them were not swapped beyond the four laws.


# (4) THE SHARED DEFINITIONS (frozen; line numbers as cited)

   1  # A ring in balance: definitions shared by the three studies
   2  
   3  Epic `RING-IN-BALANCE-20261123-001`, 2026-11-23. Frozen with the three pre-registrations, before any of the study's code is
   4  written. Tickets A, B and C cite this file and add only what is their own. The canonical K1–K3 test is unchanged. Words are the
   5  glossary's (Intuitions guide). The growth records' "junction" is a knot and their "growing end" is the live roster. Their
   6  "witness" is here a **common knot**, their "witnessed set" a **met set** and their "adjacent" **joinable**, because the glossary
   7  keeps witness for a helper variable and graph theory uses adjacent for what the program calls meeting.
   8  
   9  ## Structure
  10  
  11  - A **structure** is a finite set of knots, each holding a set of distinctions, its **places**. A distinction has one or two
  12    **holders**. It is **loose** with one holder and **shared** with two. Every knot of a start has at least three places, and so
  13    has every new knot except one that receives no fresh distinction (below).
  14  - Two knots **meet** when they share a distinction. A knot is **live** while it holds a loose distinction and **dead** otherwise.
  15  - A **start** is a structure given before any birth, written as its list of knots, each a list of distinction numbers (the
  16    records' stars).
  17  - A loose distinction is **usable** unless the law has **barred** it: a barred distinction stays loose and is never taken by any
  18    birth. (The Intuitions guide and the site call a barred distinction "never used".)
  19  
  20  ## The live roster
  21  
  22  - The **members** of the live roster are the knots holding at least one usable loose distinction. Write h(u) for the number of
  23    usable loose distinctions member u holds and k(u) for the number of barred ones. A knot holding only barred distinctions is
  24    live and is not a member.
  25  - A **met set** is the set of members that one knot of the structure meets, when it has at least two members. That knot is a
  26    **common knot** of those members; it may be dead or itself a member. Two knots with the same met set count once.
  27  - Two members are **joinable** when some met set contains both. A **part** of the live roster is a connected component of the
  28    relation joinable. The roster is **past its start** when no member meets a member (the records' positive age).
  29  - Two rosters, or two parts, are **the same** when a one-to-one renaming of members carries h, k and the family of
  30    inclusion-maximal met sets of one onto the other.
  31  
  32  ## One complete round
  33  
  34  A **law** is a knot law (parity or not-all-equal), a ration, a treatment and optional extras. One round, on real knots:
  35  
  36  1. **Groups.** First take every inclusion-maximal set of at least three pairwise joinable members that is contained in no
  37     single met set. Then take every joinable pair that is contained in none of the sets just taken. These are the groups
  38     ([ORDINARY-DYNAMICS-20261120-001](../ORDINARY-DYNAMICS-20261120-001/end_operator.md), "The operator on the present end", step 1).
  39  2. **Owing.** Member u owes one usable loose distinction to each group containing it. It is **short** when it owes more than
  40     h(u). Shortness is read once, here, for the whole round.
  41  3. **Treatment of a short member.**
  42     - STALL: if any member is short, no birth is made and the growth has stalled.
  43     - CANCEL-OFFSHOOT: every group containing a short member is cancelled; the short member makes an offshoot from each of its
  44       usable loose distinctions.
  45     - CANCEL-WAIT: every group containing a short member is cancelled; the short member **waits**: it makes nothing and keeps
  46       everything it holds.
  47     - CANCEL-RETIRE: every group containing a short member is cancelled; the short member **retires**: it makes nothing now or
  48       later, and its loose distinctions are barred.
  49  4. **Joins.** Each group that is kept makes one new knot, a **join**, whose parents are its members; it takes one usable loose
  50     distinction from each.
  51  5. **Offshoots and the release rule.** A member that is not short, after paying its kept groups, makes one new knot of one
  52     parent, an **offshoot**, from each usable loose distinction it has left. RELEASE (the default): this includes the
  53     distinctions that its cancelled groups would have taken. HOLD: it keeps those and makes offshoots only from the rest. With
  54     the extra NO-OFFSHOOT it makes no offshoot, and the distinctions an offshoot would have taken are barred.
  55  6. **Demand.** Count every new knot as a member holding one usable loose distinction, whatever it will receive, and keep every
  56     old member that still holds a usable loose distinction after steps 3 to 5 (one that waits; under HOLD, one that keeps what
  57     its cancelled groups would have taken) with what it holds. Form the groups of that roster as in step 1. The **demand** D of
  58     a new knot is the number of those groups that contain it.
  59  7. **Fresh distinctions (the ration).** A new knot with p parents and demand D receives f fresh distinctions, each loose and held
  60     by it alone. With q = max(D, 3 − p, 1), the ordinary count:
  61     - ORD: f = q. CAP-k: f = min(q, k). RATION-k: f = max(k, 3 − p).
  62     - ONE-FEWER: f = min(q, max(3 − p, 0, q − 1)). FLOOR0: f = max(3 − p, 0). FLOOR1: f = max(3 − p, 1).
  63     - **Closing exception** (parity only, every ration): a new knot that takes every loose distinction of the structure receives
  64       none; it may then have fewer than three places. It is then the round's only birth, nothing is barred and no old member
  65       keeps anything. Under not-all-equal there is no exception
  66       ([NAE-GROWTH-20261119-001](../NAE-GROWTH-20261119-001/nae_growth.md): the growth reads the knot law in this one place).
  67  8. **Extra FILLERS.** Of a new knot's f fresh distinctions, min(f, D) are usable and the rest are barred.
  68  
  69  The records' ordinary growth, the cheapest growth of lesson 8.1, is the law (ORD, STALL). **The two added rules** are the law
  70  (CAP-3, CANCEL-WAIT with RELEASE). **The three added rules** are (CAP-3, CANCEL-WAIT with RELEASE, FILLERS). They were added by
  71  hand (assumption A224, a scaffold); RELEASE is part of what was added. The pilot's program counted a short member by all its
  72  loose distinctions; the two readings agree, because a member holding a barred distinction owes exactly its usable count in
  73  the one round it acts. One barred distinction anywhere switches the closing exception off everywhere, since the exception needs
  74  a birth that takes every loose distinction there is.
  75  
  76  A distinction taken by a new knot becomes shared between its old holder and the new knot. Which of a member's usable loose
  77  distinctions goes to which birth makes no difference up to renaming.
  78  
  79  ## Kinds of outcome under complete rounds
  80  
  81  A run is one start grown under one law through a stated number of rounds, or until a stated number of knots. After each round:
  82  
  83  - The growth has **stopped** when the roster has no member, **stalled** (STALL only) when a member is short, and **jammed** when
  84    the roster has members and the round makes no birth.
  85  - A part Y of the roster after round s, past its start, **returns** at round t > s when the members after round t that descend
  86    from Y (through parents; a waiting member descends from itself) include a part that is the same as Y. The other parts those
  87    descendants form have **come apart** from Y, and Y **gives parts off** when there is at least one. Returns are searched with
  88    the least s first and then the least t, and t − s is the period.
  89  - The roster is **in balance** from round s with period T when at least one birth is made in every round and the whole roster
  90    after round t + T is the same as the whole roster after round t for every t ≥ s in the run. The structure still grows.
  91  - A part has **ended** when none of the knots descending from it is a member. It may still hold barred distinctions.
  92  - For a census a run is given one kind, the first that applies: stalled; jammed; stopped; a part returns giving parts off; a
  93    part returns giving none off; grows to the bound with no return found.
  94  
  95  ## One part at a time, and one birth at a time
  96  
  97  - **Part-round law.** A move is one complete round of one part: steps 1 to 8 applied to the members of that part alone, the
  98    other parts left as they are (the closing exception as stated: only for a birth that takes every loose distinction of the
  99    whole structure). The **own time** of a start knot is 0; a new knot's is one more than its parents'; and a member that
 100    waits through a move of its part gains one. So a member's own time is the number of moves its line of descent has taken
 101    part in. A **priority** chooses the part that moves next among the parts that would make a birth:
 102    - ALL-IN-TURN: every part once, then again; this is the complete round.
 103    - UNIFORM: each part with equal chance.
 104    - BY-MEMBERS: each part with chance in proportion to its number of members.
 105    - LARGEST: a part with the most members; SMALLEST: one with the fewest; ties uniform.
 106    - MOST-LOOSE: a part whose members hold the most usable loose distinctions in all; ties uniform.
 107    - LEAST-TIME: a part whose members have the least own time; ties uniform. This priority reads the history, not the structure.
 108  - **Birth-by-birth law** (the present-state reading of [ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md), with
 109    waiting). A move is one birth, and everything is read again after every move.
 110    1. Form the groups of the present roster as in step 1, with every knot allowed as a common knot (ANY) or only dead knots
 111       (DEAD). A group is **open** when no knot already made has all of its members among its parents.
 112    2. A member is short when it is in more open groups than h(u); a short member makes nothing. Under FIRST-COME, used only to
 113       check the engine against the record, no member counts as short.
 114    3. Every open group with no short member is a join move. A member that is not short and holds more usable loose distinctions
 115       than the number of open groups without a short member that contain it has an offshoot move. (Under FIRST-COME: every open
 116       group is a join move, and a member has an offshoot move when h(u) exceeds the number of open groups containing it.)
 117    4. The new knot receives max(3, 3 − p) fresh distinctions (RATION-3), or max(d, 3 − p, 1) (PRESENT-ORD), where d is the number
 118       of open groups containing it immediately after its birth, the new knot counted as a member before it receives anything.
 119       Closing exception, parity only: a move that takes every loose distinction of the structure, with d = 0 where d is read,
 120       receives none.
 121    5. Start knots have **generation** 0 and a new knot has generation one more than the greatest generation of its parents; a
 122       move's generation is the greatest generation of its parents. The next move is chosen uniformly among all moves (UNIFORM)
 123       or among the moves of least generation (BY-GENERATION), with joins first, offshoots first, or uniformly among those. The
 124       generation is the simulator's record of who was made from whom; it is not read from the structure.
 125    - A birth-by-birth run has **jammed at generation g** when no move of generation g or less is available and some member of
 126      generation g or less is short.
 127  
 128  ## The knot test
 129  
 130  - **Parity.** Each knot is the rule that its places have even parity. A knot with place set S passes K1–K3 in the whole
 131    structure when the allowed states of the structure, restricted to S, are exactly the even assignments of S. Two methods are
 132    run and must agree on every knot. Ranks: with H the matrix over the field of two elements with one row for each knot, the
 133    rank of H less the rank of H with the columns of S removed is one (the records' test, ORDINARY-DYNAMICS, `rulers.py`). Cut:
 134    in the graph with one vertex for each knot and one for the outside, an edge between the two holders of each shared
 135    distinction and an edge to the outside for each loose one, deleting the knot leaves the rest connected (the knot is not a cut
 136    vertex; the allowed states are the graph's cycle space).
 137  - **Not-all-equal.** Each knot is the rule that its places are not all equal. A knot passes when the assignments of S that
 138    extend to an allowed state of the whole structure are exactly the assignments that are not constant, decided by a SAT solver
 139    for each of the 2^|S| assignments (the records' test, ORDINARY-DYNAMICS, `source_cert.py`).
 140  - **Extension.** A round, or a move, extends when every allowed state of the structure before it is the restriction of an
 141    allowed state after it.
 142  
 143  ## Named starts
 144  
 145  - **Ring(n, a).** Knots 0 to n − 1. Knot i shares one distinction with knot i + 1 (mod n) and holds a loose distinctions.
 146    Ring(5, 3) is the start of the golden-ratio eddy.
 147  - **Cycle through dead knots, doubled, D2(n, a).** Members 0 to n − 1, each holding a loose distinctions, and dead knots
 148    w_0 to w_{n−1}; w_i shares two distinctions with member i and two with member i + 1 (mod n), so w_i has four places and its
 149    met set is {i, i + 1}.
 150  - **Cycle through dead knots that meet one another, DW(n, a).** As D2 with single meetings: w_i shares one distinction with
 151    member i, one with member i + 1, one with w_{i−1} and one with w_{i+1}.
 152  - **The seven-knot generator.** Stars [0,1,2,9,10,11], [0,1,3], [4,5,12,13,14], [6,7,15,16,17], [2,3,4,6,18,19,20], [7,8,21,22],
 153    [5,8,23,24] ([GENERATORS-20261120-001](../GENERATORS-20261120-001/source.md)).
 154  
 155  ## What is supplied by hand
 156  
 157  The complete round (assumption A104); every ration other than ORD, every treatment other than STALL, the release rule and both
 158  extras (A224); the part-round law, the birth-by-birth laws and every priority; the starts; the reading of a part as a thing (as
 159  in A125); the bounds on rounds, moves and knots; and each weighting named where a share is given. Each study says which of
 160  these it swaps.


# (5) FROM THE ONE-BIRTH-AT-A-TIME STUDY'S DEFINITIONS: weaned, brood, the brood argument, the start clause

is not the study's engine. What it showed is disclosed in the pre-registration, under "Known before the freeze".

## 1. What is read from the structure

### 1.1 Parents, children, places, holder-step distance

- **Parents.** Every birth writes, with the new knot, the set of knots it took a distinction from: its **parents**
  (definitions steps 4–5: a join's parents are its group, an offshoot's its one member). The **children** of a knot are the
  knots that have it among their parents. A start knot has no parents and is the child of none.
  - The parent relation is not a reading of the holders: a shared distinction has two holders and no order (definitions
    lines 11–13, 76). It is written by the birth, as the record's birth-by-birth law already reads it (definitions line 111).
    See section 5.
- **Places, loose, usable, barred, h(u), k(u), member, live, dead**: as the definitions, lines 11–24.
- **Holdings at birth.** For a knot x with parents, **h₀(x)** is its number of places less its number of parents. Each
  parent gave one distinction; the others x received at birth, whatever they are now: loose, barred, or shared with a child.
  For a start knot, h₀(x) is its number of places not shared with another start knot.
- **Holder-step distance.** One holder step crosses a shared distinction from one holder to the other
  ([SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/local_rule.md) line 7). The **holder-step distance** between two knots is
  the least number of holder steps between them.
- A rule **reads to holder-step distance d** from a knot when its decision is the same for any two structures that agree on
  every knot within holder-step distance d of it. Agreeing means: their places, which of those are loose, usable or
  barred, and their parent sets and children, together with the closing bit of section 2.4.

### 1.2 The start roster (what plays the part of parents for start knots)

The **start roster** has as members the start knots with h₀ ≥ 1, each with holding h₀. Its met sets are, for each start
knot, the set of start members it meets, when it has at least two. Any start knot may be a common knot here, a member
included, as in definitions step 1. It is the roster the first complete round reads; it never changes.

### 1.3 Weaned

A knot is **weaned** when none of its parents is a member of the present roster: its parents have finished giving. Every
start knot is weaned.

### 1.4 The brood

- The **brood** of a knot x with parents is the smallest set B containing x such that, for every knot in B and every parent
  of it, all children of that parent are in B. The **parents of the brood** are the parents of its knots. Knots of B that
  have since made births, retired or died stay in B.
- **A brood's roster at birth** has as members the knots of B with h₀ ≥ 1, each with holding h₀. Its met sets are, for each
  parent p of the brood, the members that are children of p, when there are at least two.
- A brood is **all-weaned** when every knot in it is weaned.
- **Why this set** (an argument for the referee, not a definition).
  - Under RELEASE a member that makes any birth spends every usable distinction in the one roster in which it acts. So all
    children of a parent are born in one complete round.
  - Past the start, a knot meets only its parents and its children, and a waiter meets only its parents. So a waiter is
    joinable only with brood-mates that still wait.
  - Hence an all-weaned brood's roster at birth is exactly the part the complete rounds read in the round after its births, with
    the holdings it had then. Its waiters' rosters (section 2.1, step 5) are the parts the complete rounds read in the
    rounds after that.

## 2. Plans, and how a birth is made

### 2.1 The plan of a roster

A **roster** here is a set of members, a holding for each, and a family of met sets. Its **plan** is read as follows.

1. **Groups and owing.** As definitions steps 1–2 (lines 36–40), with the roster's holdings.
2. **Treatment.**
   - STALL: if a member is short, the plan **stalls** and has no births.
   - CANCEL-OFFSHOOT: a short member's births are one offshoot from each of its holdings.
   - CANCEL-RETIRE: a short member **retires** in this plan.
   - CANCEL-WAIT: a short member **waits** in this plan.
3. **Births of the plan.** Every group containing a short member is cancelled. Each kept group is one planned join. Each
   member that is not short has as many planned offshoots as its holding less its kept groups (RELEASE).
4. **Fresh count of a planned birth with p parents.**
   - FLOOR1 and RATION-3: as definitions step 7, line 62.
   - ORD: f = max(D, 3 − p, 1). D is the number of groups containing the birth in a roster whose members are the plan's
     births, each with holding 1, and whose met sets are, for each member of the plan's roster, the births it is a parent
     of, when there are at least two. Under STALL no member keeps anything, so no old member enters this roster, and D is
     the birth's owing in the next roster.
   - The closing exception is not applied here (section 2.4).
5. **Waiters' recursion** (CANCEL-WAIT only).
   - The **waiters' roster** of a roster has as members its waiters, with holdings unchanged. Its met sets are the roster's
     met sets intersected with the waiters, kept when they have at least two.
   - Each part of the waiters' roster is read a second time by steps 1 to 5, and its own waiters' roster after that.
   - A part of any roster all of whose members are short is **all-short**: its members wait for ever and make no births. The
     recursion stops there.
   - A member's **acting roster** is the first roster of this sequence in which it is not short.
   - A waiter reads a second time against the waiters of its roster only, never against new knots. Past the start this is
     what the complete rounds read, by section 1.4.
6. **Status.** A member's **planned births** are the births of its acting roster that have it among their parents, with
   multiplicity. Its **status** is one of:
   - "acts", with those births;
   - "retires";
   - "its plan stalls";
   - "is in an all-short part".

### 2.2 Which roster a member reads

- **Start clause.** A start knot reads the start roster (section 1.2), at every moment. The start clause is exact only when
  no start knot that acts meets a start knot that waits.
  - On the start-clause counterexample of the pre-registration two readings are wrong. The waiter (knot 0) reads a waiters' roster of
    itself alone. And the brood's roster at birth of the children of knots 1–3 omits knot 0, which the complete rounds put
    in their part in round 2.
  - Ring(5, 3) satisfies the condition: no start knot is short there.
- Every other member reads its brood's roster at birth (section 1.4).

### 2.3 Births already made
