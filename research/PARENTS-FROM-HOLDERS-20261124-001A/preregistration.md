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
