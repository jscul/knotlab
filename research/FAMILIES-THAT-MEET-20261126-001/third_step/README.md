# How far a cap lets one side feel the other

Third step of `FAMILIES-THAT-MEET-20261126-001`, at the owner's word ("Let's take on 'How far a cap lets one side
feel the other'"), 26 November 2026. A check by the thread, not a registered study: its expectations were written
into [`reach.py`](reach.py) before the first run, and nothing else was frozen. Everything here is computed on the
starts and rounds named, except one argument, which is marked. Independent referee pending.
[First step](../first_step/README.md) · [second step](../second_step/README.md) · [the owner's request](../owner_request.md)

## The answer

On the generator study's start, with laws under which a birth takes nothing:

- **Without a cap nothing was felt.** No knot is ever short (0 short members in 27 starts; the ordinary count gives
  a new knot at least what it will be owed), the two families stay joined, and the first family's side is the same
  whatever lies beyond the second family's original, through the 8 or 9 rounds read (27 of 27 pairs).
- **With a cap one side can change the other, but only while a group still joins them, and the cap ends that.**
  Where short knots retire or make offshoots, the last group joining the two sides is in round c − 2 and none is
  left in round c − 1, for every cap c from 4 to 9 and every start read that far (106 of 106). In the 763 rounds
  read after a start's sides had come apart, no group joins them again.
- **A change one step beyond the second family's original is felt at caps of 9, 10 and 12** (26 of 27 pairs, from
  rounds 5, 6 and 7 to 8), and, where short knots wait, at caps of 6 and 8 (5 of 6 pairs). At caps of 4 to 8 with
  retiring or offshoots it is not felt, and given the argument below it never will be (30 of 30 pairs).
- **A change two or three steps beyond was felt in no pair** (0 of 162). In 82 of those pairs both starts were read
  until their sides had come apart with everything outside the second family the same, knot for knot; given the
  argument below they stay the same in every later round. In the other 80 the sides were still joined when the
  reading stopped (18 without a cap, 36 at caps of 10 and 12, 24 with waiting at caps of 6 to 9, 2 at cap 9 with
  offshoots): there the change was not seen in the 7 to 11 rounds read, and no more is claimed. At caps of 10 and
  12 those rounds are too few to have shown it either way.

So the cap that lets one side feel the other is also what parts them. Seen from this start, a cap gives the two
families a few rounds in which a change can cross, and a change has to be near to arrive in them.

## What was built and read

The start is the generator study's 21 knots (nine live originals v, r1, r2, r3, s, t, b0, b1, b2; twelve candidate
pairs, each met through one spent knot; [`../first_step/price.py`](../first_step/price.py), `source`), with a tail
hung on b2, the second family's own original: b2 – q1 – … – qd, the first d − 1 new originals in two pairs each,
and the last one, qd, carrying m rings of four originals, so that it is in 1 + 2m pairs. For one d the three starts
m = 1, 2, 3 are the same out to d − 1 steps beyond b2 and differ only at step d. The second step had changed what
lies one step beyond b2; here that change is moved out.

A knot's side is read from its original ancestors. The **second side** is every knot with b2 or an original of the
tail among them. The **first family's side** is every knot with b1 among them and nothing of the second side: this
is the side the first two steps read. The **rest** has neither, and **outside** means the first side and the rest
together. The first side's births in a round are read as the sorted list of (kind, number of parents, number of
places, fresh distinctions); two starts differ in a round when those lists differ.

Laws: not-all-equal knots, nothing taken, the ordinary count or a cap of 4, 5, 6, 7, 8, 9, 10 or 12 on the fresh
distinctions of a birth (the scaffold of this epic, register entry A274), and each of the three treatments of a
short knot (it retires, it makes only offshoots, it waits). With d = 1, 2, 3 and m = 1, 2, 3 that is 243 starts and
243 pairs of starts.

**Expectations, written before the first run, and how they fared.**

1. *Under the ordinary count the first side is the same for the three values of m at every d.* Held: 27 of 27
   pairs, 8 or 9 rounds.
2. *For d = 1 the first side differs between values of m at caps of 6 to 9 at least, and not at 4 or 5.* Held in
   part. Not at 4 or 5: right. At 9: right. At 6, 7 and 8 it differs only where short knots wait, and at 7 not
   even then in the 9 rounds read. I had taken the second step's finding to carry over; it does not, because
   there the second family's original was itself in four pairs.
3. *For d = 2 and d = 3 it differs at some cap from 6 to 12, later than for d = 1 by a round or more a step*
   (held weakly). Failed: no pair differs. The change does travel in by about a step a round, as expected, but it
   never reaches a group that joins the sides (below).

## What was found

Each cell compares the three starts m = 1, 2, 3 two at a time. "differs r": the first side first differs in round
r. "same for good (apart by a, read to n)": both starts were read to round n, in both no group joined the sides
from round a on, and everything outside the second side was the same knot for knot in every round read. "same to
n": the same through the n rounds both starts read, with the sides still joined. The table is
[`reach_deep_table.md`](reach_deep_table.md), made by [`tally_deep.py`](tally_deep.py) from
[`reach_deep.jsonl.gz`](reach_deep.jsonl.gz); every pair is in [`reach_deep_pairs.json`](reach_deep_pairs.json).

| steps beyond b2 | pairs | differ | same for good | same in the rounds read, sides still joined |
|---|---|---|---|---|
| 1 | 81 | 31 | 36 | 14 |
| 2 | 81 | 0 | 40 | 41 |
| 3 | 81 | 0 | 42 | 39 |

Where the one-step change is felt:

| cap | short knots retire | make offshoots | wait |
|---|---|---|---|
| none | same to 8 | same to 8 | same to 8 |
| 4 | same for good (apart by 3) | same for good (apart by 3) | same for good (apart by 7) |
| 5 | same for good (apart by 4) | same for good (apart by 4) | same for good (apart by 6) |
| 6 | same for good (apart by 5) | same for good (apart by 5) | differs 7 in two pairs; m = 2 and 3 same to 10 |
| 7 | same for good (apart by 6) | same for good (apart by 6) | same to 9 |
| 8 | same for good (apart by 7) | same for good (apart by 7) | differs 7 or 8 |
| 9 | differs 5 | differs 5 | differs 5 |
| 10 | differs 6 | differs 6 | differs 6 |
| 12 | differs 7 or 8 | differs 7 in two pairs; m = 1 and 2 same to 7 | differs 7 or 8 |

The round in which the sides come apart (the first round, from the second on, with no group holding a knot of the
outside together with a knot of the second side; every group of the round is counted, kept or cancelled), over the
nine starts of each cap and treatment:

| cap | retire | offshoots | wait |
|---|---|---|---|
| none | never in the rounds read | never | never |
| 4 | 3 | 3 | 7 |
| 5 | 4 | 4 | 6 |
| 6 | 5 | 5 | not by round 10 or 11 |
| 7 | 6 | 6 | not by round 9 or 10 |
| 8 | 7 | 7 | not by round 8 or 9 |
| 9 | 8 | 8 in seven starts; two read to round 7 only (m = 3 at one and at two steps) | not by round 7 to 9 |
| 10, 12 | not by round 8 | not by round 7 or 8 | not by round 7 or 8 |

"Round c − 1" is what was counted, for caps of 4 to 9. I have not looked for its reason and do not claim it for
other caps or other starts.

## Why: where a change can pass, and why it stops

**One round of the law** ([the engine](../../../experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/eng.py),
`play_round` and `build_roster`). A member is a knot with a loose distinction. Two members are joinable when some
knot meets both, and the round's groups are sets of joinable members. A member owed more joins than it has loose
distinctions is short, and every group with a short member is cancelled. A member that is not short gives one
loose distinction to each of its kept groups (a join) and one to an offshoot of its own for each that is left
over. A new knot is given as many fresh distinctions as the joins it will be owed (and enough to hold three
distinctions at least), cut to the cap.

**The passage.** So a knot of the outside that is made and supplied alike in two starts can act differently only
through one of its own groups: a group that is kept in one start and not in the other. Its join becomes an
offshoot. Three programs read this by naming every knot by how it was made, so that a knot has the same name in
both starts: [`cross.py`](cross.py) counts the groups, [`decide.py`](decide.py) names the cause of each birth that
one start has and the other lacks, and [`front.py`](front.py) compares the starts knot by knot for every sort of
knot. At cap 9 with retiring, m = 1 against m = 2:

| | one step (d = 1) | two steps (d = 2) | three steps (d = 3) |
|---|---|---|---|
| knots made from b2 and not the tail first differ between the starts | round 4 | round 6 | not by round 8 |
| groups joining the outside and the second side, by round (both starts together) | 4, 12, 32, 88, 232, 498, 186, then none | 4, 12, 32, 88, 232, 588, 316, then none | the same as at two steps |
| of them, groups holding a second-side member that is short in one start only, or there in one start only | 56 in round 5, 276 in round 6, 142 in round 7 | none in any round through 9 | none through 8 |
| … with no other member short | 48 in round 5 | none | none |
| births the outside has in one start only, in the first round it differs | 48 in round 5, all offshoots: 28 on the first side, 20 in the rest | none through 9 | none through 8 |

At one step the cause is named birth for birth ([`decide_d1_cap9_retire_m1_m2.json`](decide_d1_cap9_retire_m1_m2.json)):
the 48 offshoots that only the start with two rings has come from 33 parents; each parent is a member of both
starts, short in neither, with the same loose distinctions; each makes exactly as many more offshoots as it has
groups kept in the other start and not in this one; and every one of those 48 groups is not kept because a knot
made from b2 (and not from the tail) is short in the start with two rings. At two steps the change reaches the
knots made from b2 two rounds later (16 such members differ in round 7, 192 in round 8, 1,440 in round 9), but
none of them is ever in a group with a knot of the outside, and from round 8 no group joins the sides at all.
([`trace.py`](trace.py) lists the first side's 28 births with every short partner of their parents.)

The first side and the whole outside tell the same story in every pair: in the 31 pairs that differ, the outside,
compared knot for knot with fresh counts, first differs in the same round as the first side's coarser list; in the
other 212 neither differs in any round read.

**Apart for good (an argument, referee pending).** Under a law that takes nothing:

1. A loose distinction given to a birth goes to that one child and to no other, and nobody else ever comes to hold
   it. So a member that has not yet acted shares distinctions only with its parents, and two children of one parent
   share nothing with each other directly.
2. A member acts in one round only: it gives away every loose distinction it has, or it retires and they are
   barred, or it waits and gives none. A knot that has acted or retired is no longer a member. So all the children
   of one parent are born in one round.
3. Hence, from the second round on, two members are joinable only when they are children of one parent, born in
   the same round. (In the first round the members are the originals, which meet through the start's spent knots;
   none of them is short there, each having as many loose distinctions as pairs.)
4. A group joining the sides therefore holds a child L of some parent w on the outside and a child K of w on the
   second side, and K is the join of a group that joined the sides, and was kept, in the round w acted. So once a
   round has no group joining the sides, kept or cancelled, no later round has one. (Members that were born
   earlier and are still waiting were joinable in that round as well, and two joinable members are always together
   in some group.)
5. From then on every met set lies wholly on one side, so the outside's groups, its short knots, its births and
   their fresh counts are fixed by the outside alone. (A fresh count reads the groups among the round's births and
   the waiting members; a birth and a waiting member never share a parent.) Two starts whose outside is the same
   when their sides come apart, in its knots by name, their fresh counts, and so in which members have acted and
   which still wait, therefore have the same outside in every later round.

This is the settled statement that parts act alone past their start and that the descendants of two parts are
never joinable
([`RING-IN-BALANCE-20261123-001A`](../../RING-IN-BALANCE-20261123-001A/preregistration.md), lines 95 to 99;
[`PARTS-MEET-AGAIN-20261124-001`](../../PARTS-MEET-AGAIN-20261124-001/decision.md), item 1), said of the two sides;
the generator study's timing restriction is the same fact about families that supply all their own parents
([`GENERATORS-20261120-001`](../../GENERATORS-20261120-001/meeting.md)). Neither earlier statement has been
refereed, so "same for good" in this note always means: given this argument.

Three checks of it on what was run:

- In the 763 rounds read after a start's sides had come apart, no group joins them again.
- In every pair called "same for good" the outside is the same knot for knot in every round read, after the sides
  came apart as well as before.
- **The second side retired by hand** ([`ablate.py`](ablate.py), [`ablate.jsonl`](ablate.jsonl), the advisor's
  test). Seven starts, covering the three treatments, caps of 4 to 9 and one to three steps, were grown twice: whole,
  and with every member of the second side retired by hand in the round the sides came apart (57 to 4,353 members).
  In the 42 later rounds compared, the outside's 180,852 births are the same in both growths, knot for knot and
  fresh count for fresh count. Along the way every joinable pair of members from the second round on was tested for
  step 3: 864,842 pairs, each with a common parent and born in the same round.

## What this does not say

- **One start, and built.** The generator study's start with a tail built by hand. Nothing is said about starts
  drawn under a weighting.
- **Laws that take nothing.** Under a law that reaches further, parts that have come apart can meet again
  (`PARTS-MEET-AGAIN-20261124-001`), so "for good" does not carry over. A small trial of the engine's taking rules
  on two starts ([`take_trial.json`](take_trial.json)) is not a test of that: the three rules that take a sole
  candidate never took anything in 9 rounds, so the growth was the same, and the rule that takes the oldest or the
  newest candidate took at round 2 and the growth had ended by round 5.
- **The cap is a scaffold** (A274). The ordinary count is the law of the record; a cap of any size was added by
  this epic to see what shortness does.
- **Caps of 10 and 12 at two and three steps are undecided, and the reading there could not have decided them.**
  The sides were still joined at the 7 or 8 rounds read. At one step the change arrives in round 6 (cap 10) and
  round 7 or 8 (cap 12), and at two steps it reaches the knots made from b2 two rounds later than at one step, so
  an arrival would fall at or past the last round read. That nothing is felt at two steps is established, given
  the argument, only for caps of 4 to 9; whether a cap of 10 or more lets a two-step change through is open. A
  round there leaves 40,000 to 120,000 knots and the next would not fit in 8 GB.
- **Waiting.** With waiting the sides stay joined much longer (not apart by round 7 to 11 at caps of 6 and up),
  and nothing at two or three steps differed in those rounds either. "No group joins the sides" is enough for the
  sides to be apart for good but may not be needed: members that wait for ever in a group nobody can act in join
  the sides without passing anything. I did not sort the waiting groups this way. In the last round read, some
  group joining the sides was still kept in 43 of the 54 waiting starts at caps of 6 and up (all 36 at caps of 8
  to 12, 5 of 9 at cap 7, 2 of 9 at cap 6).
- **Differs, not how much.** The reading says whether the first side's births differ, round by round. It does not
  say that anything on the first side depends on *what* the second family is, only on what the cap did to it.

## After the advisor's review

The note was reviewed cold before it was committed ([question](advisor_question.md), [answer](advisor_answer.md)).
What changed: the count of pairs "same for good" at two and three steps (82; my question said 118, the number over
all three distances); the argument's unstated premises written in (steps 1 to 3 and the bracket in step 5); "given
the argument" added wherever "for good" is said; the count of groups joining the sides said to include cancelled
groups; the comparison of the whole outside, and not the first side only, reported for all 243 pairs and added to
`cross.py`; the cause at one step named birth for birth (`decide.py`) where the first draft matched two counts of
28; the null at caps of 10 and 12 called undecidable at this depth; the caveat on waiting; and the advisor's test
run (`ablate.py`).

## Runs

| pass | what | starts or studies | result |
|---|---|---|---|
| 1 | [`drive_reach.py`](drive_reach.py): three starts a study, compared on the rounds all three read, up to 9 rounds, no further round after 40,000 knots | 81 studies | 67 finished; 14 stopped by the memory cap of 8 GB ([`reach_runs.jsonl`](reach_runs.jsonl)) |
| 2 | [`drive_reach_second.py`](drive_reach_second.py): caps of 10 and 12 again, one structure in memory, no further round after 15,000 knots | 18 studies | 18 finished ([`reach_second.jsonl`](reach_second.jsonl)) |
| 3 | [`drive_deep.py`](drive_deep.py): each start its own run, a line a round, up to 14 rounds, no further round after 60,000 knots; pairs compared afterwards on the rounds both read | 243 starts | 49 read 14 rounds, 140 stopped at the knot bound, 49 by the memory cap with their rounds kept, 5 by the engine's guard; 7 to 14 rounds each; 3,491,231 first-side births read |

Pass 3 was written because pass 1 compared a pair only on the rounds its third start had also read, and lost a
whole study when one start passed the memory cap. The three passes agree wherever they overlap: 255 pair
comparisons from the 85 finished studies of passes 1 and 2, none disagreeing with pass 3. Every run was under a
memory cap of 8 GB with no swap and a stop at ten minutes; the whole of pass 3 took about nine minutes, three
starts at a time. Not run: any round past those limits.

To run again, from this folder, with `PROBE_ROOT` set to the repository:
`python3 -B drive_deep.py out.jsonl 3`, then `python3 -B tally_deep.py out.jsonl pairs.json`; and for the
comparisons by name, `python3 -B cross.py '{"d":2,"ration":"CAP-9","treatment":"CANCEL-RETIRE","rounds":9,"bound":40000,"ma":1,"mb":2}' --table`
(about 5 GB and ten seconds). `../first_step/make_engine_cap.py` writes the engine with the further caps first.

## Report as sent

Sent to the owner on 26 November 2026, with his question of the same hour answered first ("Have we successfully
completed a single instance of complex behavior using any sort of braiding of the logic? … What are we at in terms
of complexity from 1-10? And can you come up with some sort of roadmap to get us to a higher rating? I want to
start simulating stuff."). Headings are set one level down here.

### Your question: where we are, and a roadmap

**Yes for patterns that last, no for patterns that work on each other.** We can build a start by hand that makes a lasting pattern. We have no start in which two patterns keep acting on each other, and today's result says why the laws used so far cannot give one.

| Built so far | What it does | Standing |
| --- | --- | --- |
| A ring that returns | the same ring of knots comes back every few rounds and gives parts off each time | computed, referee pending |
| A part that copies itself | two knots become two such pairs every two rounds, at three rates | computed, referee pending |
| A source | seven knots that keep releasing lasting families under ordinary growth; two families released together make one joint knot, and what it holds depends on the start | the Codex line's study, refereed, stands |

**Rating: between 3 and 4 out of 10**, on this scale of mine: 1 one knot · 2 growth we can count · 3 patterns that last · 4 an imprint (what a pattern makes differs with what it grew next to) · 5 a signal (a lasting pattern changes another's course after both exist, and can do it again) · 6 a switch that can be chained · 7 switches with memory, a counter · 8 a start that builds a described structure · 9 one that copies itself from its description · 10 open-ended.

We hold 3. We hold 4 only thinly: the joint knot above, and today's one-step result under a cap. Nothing at 5: the copies never meet again, and the search for a copier that growth makes found none (refereed). The roadmap is the directions table below.

### The step you asked for: how far a cap lets one side feel the other

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — how far a change beyond the second family is felt on the first family's side | **Status:** Successful | One step out: felt at caps 9, 10 and 12 (26 of 27 pairs). Two or three steps out: felt in 0 of 162 pairs |
| Local direction — a cap, with laws under which a birth takes nothing | Practically exhausted | The cap that makes knots short also parts the families, by round c − 1 |
| Broader exploration — laws under which families keep acting on each other | Known alternatives | Waiting keeps them joined; laws that reach further rejoin parts |
| Long-term goal — G15 Learning, with G18 Comparing growth laws | Obstruction learned | Joined families feel each other only through short knots; parted ones never do |

Without a cap no knot is ever short, so nothing is felt although the families stay joined. With a cap, a short knot cancels its joins, and a neighbour on the other side makes an offshoot where it would have made a join. That is the only way a change crosses, and at one step I can name it birth for birth (48 offshoots, each in place of a join with a knot of the second family that is short in one start only). But where short knots retire or make offshoots, no group joins the two sides from round c − 1 on (caps 4 to 9, 106 of 106 starts), and parts that have come apart act alone from then on. So a change has a few rounds to cross and must be near.

"From then on" is an argument from two of my earlier studies, not yet refereed. I tested it by retiring the second family by hand once the sides were apart: the rest grew the same, knot for knot (7 starts, 180,852 births). At caps 10 and 12 the two- and three-step starts could not be read far enough to decide. Everything is on one built start. The advisor's review changed nine things before the commit, among them a miscount of mine (82 pairs, not 118).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A bench for two patterns (toward level 5) | 3/3 — first test of patterns that stay joined | 2/3 — engine and readings exist; the law is unknown | Join two of the three patterns in one start, 1 to 3 steps apart, under waiting and under two laws that reach further; read whether either's course differs from growing alone, and for how long → a pair that differs for good under a swap of ration, or every pair read | Selected · awaiting go-ahead |
| 2 | The bench as a toy on the site | 2/3 — it is how you simulate | 3/3 — playground and engine ports exist | Pick two patterns, a law and the steps apart; watch the rounds → it matches the bench on every case of #1 | Alternative · deferred |
| 3 | Search small starts for pairs that act on each other | 3/3 — finds what hand-building misses | 2/3 — census code exists; the reading is new | Every start of up to six knots under waiting, each pair of parts grown together and alone → the first pair that differs for good, or the census ends | Alternative · deferred |
| 4 | What the other is (level 5 proper) | 3/3 — the fold's own question | 1/3 — needs a pair from #1 or #3 | Swap the second pattern for another → two courses for two partners | Alternative · deferred |
| 5 | Does any cap let a two-step change through | 1/3 — closes today's open cell | 3/3 — same programs, smaller start | Read caps 10 to 14 to the round the sides part → one crossing or none | Alternative · deferred |

1. Every law we have used either never makes a knot short or parts the patterns, so staying joined is the missing ingredient. The engine already has waiting and the takes that reach further, and today's readings carry over; which law shows anything is the unknown. A table costs minutes of compute.
2. The same runs in the browser. It adds no result, so it follows #1.
3. The ring census already read 86,032 small starts for "returns"; this reads them for "differs together from alone".
4. Close to the generator study's open sub-goal B225, and it is where the made-copier study found nothing. It waits for a pair.
5. Cheap, but it only fills in a table about a scaffold.

Levels 6 and 7 wait for a level-5 pair: a switch is two such signals meeting. Say go, or reorder, and I'll start #1 and close this epic's record with today's verdict.

**Corrections:** none logged; the advisor's findings were fixed before anything left the session.
**Goals:** no checkpoint yet (the epic is still open); G15 and G18 unchanged.
**Assumptions:** A274 (a cap of any size) has a new history line; no new entry.
**Scaffolds:** the cap, the tail built on the second family's original, the reading of sides by original ancestors, and the choice that a birth takes nothing. Swapped: eight caps, three treatments, one to three steps, one to three rings. Not swapped: taking (the engine's sole-candidate takes never took on this start, and taking the oldest or newest ended the growth by round 5). The result is about this start under these laws.
**Basket:** the lead B337 carries the result; rows 3 and 4 are close to the generator study's open sub-goals B227 and B225, which now carry these ratings.
