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
