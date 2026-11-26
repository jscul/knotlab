# What decides the class: a check after the registered study

Sub-goal B335, 26 November 2026 (UTC), after the registered study `FOLLOWS-THE-FORM-20261125-001` closed. Its
decision note left one soft spot, "what decides the class where the count profile does not", and the owner said to go
ahead with it. **This is a check by the thread, not a registered study.** Nothing was registered beforehand; the one
expectation written at the head of the program before its first run failed; every number here was seen before it
was written down. One program, on the shared growth engine. An advisor model read the first tables, and its points
changed the reading and added two tabulations (below).
[The program](profile.py) · [its driver](drive_profile.py) · [the tables' program](table.py) ·
[the later readings](after.py) · [two second seeds side by side](pair.py) ·
outputs: [345 second seeds](every_seed.jsonl.gz), [the registered family](registered_family.jsonl.gz),
[the swap pairs](swap_family.jsonl.gz) · tables: [345 second seeds](tables_every_seed.txt),
[the registered family](tables_registered_family.txt), [the later readings](after.txt) ·
the advisor: [question](advisor_question.md), [answer](advisor_answer.md)

**The registered study's sentence "in 49 of the 90 studies the class is decided by a count profile of the second
seed" is withdrawn as a reading: the number stands, but almost no pair of forms could have contradicted it. On 345
second seeds that profile decides the class in 3 studies of 267. None of the tallies tried that forget how many
steps each knot is from the held knot decides what the first seed's descent makes: each of the 92 pairs with the
same knots at other steps is told apart in some study. Of the 141 pairs that agree out to two steps, none is told
apart where nothing is taken and short knots retire or make offshoots (12,690 comparisons, each read to round 9),
and 19 comparisons are where they wait. And in 23 studies of 270 two second seeds with the same knots at the same
steps, differing only in which knot is a partner of which, are told apart.**

> **After the referee's report, 26 November 2026** ([report R1](../../referee-R1/report.md); confirmed with fixes).
> The referee recounted every table here and regrew a pair with the same registered profile and different classes
> in each of the 264 studies where the profile fails, six studies in full, and ten swap comparisons. Three
> statements of this note were narrowed, and the text is changed where they stood: "follows the second seed's knots
> by their steps" (all 345 seeds differ in those counts, so whether they are enough cannot be asked there); "the
> 141 pairs differ only in loose counts three or four steps out" (64 of them set a chain of four against a chain of
> five); and "nothing could have contradicted" the registered reading (245 pairs could have). The report as sent,
> at the end, is kept as sent.

The words are the registered study's ([definitions](../../definitions.md)). A start is a **first seed**, one
**link** distinction and a **second seed** that holds the link on its **held knot**. A **study** is one law and one
first seed with every second seed of a family; two second seeds are in one **class** when the first seed's own
descent makes the same births in every round through the last round all runs of the study reached, and are **told
apart** otherwise. A **profile** of a second seed **decides** the class in a study when no two second seeds with the
same profile are told apart. Two knots are **partners** when they share a distinction; a **step** is from a knot to
a partner.

## What the registered study said, and what does not stand

The registered prediction (PN7) was that the class is not a function of the held knot in at least 81 studies of 90,
and not of the held knot with the number of births the second seed's own descent makes each round in at least 25.
It held: 90 and 41. Both numbers stand; this check's program reproduces them, and the last common round and the
number of classes, in 90 studies of 90.

The result, the decision note, the guide and the report to the owner then read the other 49 studies as "what is seen
is a count profile of the second seed; 'form' is too large a word". That does not follow. Among the 60 held-out
second seeds the profile takes 44 to 60 values in a study. In the 49 studies, 245 of 86,730 pairs of second seeds
share a profile, and in three of them none does: only those 245 could have contradicted the reading. A profile that
nearly names each seed decides almost anything.

## What was read

- **Second seeds**: 345, one for each form up to renaming: the 138 forms of the three families grown before the
  registered study's freeze, and the whole written list of 207 from which its 60 held-out seeds were sampled. So the
  60 are among them, and none of this is held-out material. They have one to five knots (234 have four): chains, rings
  of three or four, and a knot with three partners that share nothing among themselves. In 251 the farthest knot is at most two steps from the held
  knot.
- **First seeds**: all fifteen of the registered study. **Laws**: its eighteen (three rations; short knots retire,
  make offshoots or wait; no taking rule, or the take of a sole candidate), under not-all-equal.
- **Studies**: 270, of 59,340 pairs each. 267 finished. Three, all under the ordinary count with offshoots and the
  take, were stopped at a limit of fifteen minutes and are **not run**.
- **Profiles**, each tallied over the studies: in how many it decides the class, how many pairs share it, and how
  many of those are told apart.
- **The swap pairs**, added on the advisor's point: chains of five held at the middle knot, in 27 pairs that have
  the same knots at the same steps and differ only in which end knot is the partner of which neighbour of the held
  knot. 270 studies, all finished.

## What was found

Of all 15,843,780 pairs, 74.3% are told apart. Each row below is to be read against that.

| Profile of the second seed | Decides the class in | Pairs that share it | Of those, told apart |
| --- | --- | --- | --- |
| The held knot (its places, loose count and number of partners) | 0 of 267 | 1,907,982 | 867,229 (45.5%) |
| The held knot and how many births the second seed's descent makes each round (the registered profile) | 3 of 267 | 51,359 | 13,843 (27.0%) |
| The held knot and what those births are, each round | 45 of 267 | 23,348 | 3,553 (15.2%) |
| The held knot and every knot of the seed by its loose count and number of partners, not by its steps from the held knot | 30 of 267 | 24,564 | 8,209 (33.4%) |
| The seed out to one step from the held knot | 32 of 267 | 212,532 | 30,887 (14.5%) |
| The seed out to two steps | 211 of 267 | 37,647 (the same 141 pairs in every study) | 2,571 (6.8%) |
| The seed out to three steps | 256 of 267 | 4,272 (the same 16 pairs) | 34 (0.8%) |

- **The registered profile does not decide the class.** It does in 3 studies, each with three or six classes. With
  the registered study's held-out first seeds it does in 2 studies of 89, and 4,542 of the 17,297 pairs that share it are
  told apart (26.3%, against 72.2% of all pairs there). Sharing the profile makes two second seeds likelier to fall
  in one class under the weighting "each pair of the 345 once"; it does not put them there.
- **Neither does what the second seed's births are**, each by kind, parents, places, fresh distinctions and takes:
  45 studies of 267.
- **Neither does the seed's own knots with their steps forgotten.** 92 pairs in each study are built from the same
  knots, each with the same loose count and number of partners, and differ in where those knots are. 8,209 of the
  24,564 comparisons are told apart, at least one in 237 studies of 267, and each of the 92 pairs in some study. One pair read birth by birth, under the ration
  "just enough for three places" with short knots retiring and a first seed of one knot: a chain of four held at its
  end with loose counts 1, 1, 2, 2 and the same with 1, 2, 1, 2. In the first the knot next to the held knot owes two joins and has one loose
  distinction, so it retires, and the first seed's knot makes four offshoots. In the second it has two, its join
  with the first seed's knot is made, a birth of both seeds, and the first seed's knot makes three offshoots.
- **A profile that adds the births of both seeds nearly decides it** (220 studies of 267; 303 of 19,917 pairs told
  apart). That is not a description of the second seed. Those births are outcomes of the same meeting, and in the
  pair above one of them is the difference. The births of both with the held knot, without the second seed's own
  births, decide the class in 99 studies of 267.
- **Out to two steps, with no taking rule.** 141 pairs agree out to two steps from the held knot and differ beyond:
  77 only in loose counts three or four steps out, and 64 by setting a chain of four against a chain of five. (The
  two-step profile counts every partner of a knot it includes, those beyond two steps among them.) Where short knots
  retire or make offshoots none of them is told apart in any of 90 studies, each read to round 9. Where short knots
  wait, 19 comparisons are, in 2 studies of 45, first in rounds 3 and 4: 11 of the first kind and 8 of the second.
  One step is not enough: it decides the class in 24 studies of 135.
- **With the take of a sole candidate the first seed's descent is told more.** The same 141 pairs are told apart in
  54 studies of 132 (2,552 of 18,612), most of them in round 1 or 2. The 16 pairs that agree to three steps, chains
  of five that differ in the loose count of the far end, are told apart in 10 studies, all under the cap of three with
  waiting.
- **Which knots are partners, the steps being the same.** In the 345 seeds this cannot be asked: no two of them
  have the same knots at the same steps, so there "form" and "counts by steps from the held knot" are one thing. The
  swap pairs can be asked. They are told apart in 23 studies of 270 (198 of 7,290 pairs): in 14 of the 45 studies
  with no taking rule where short knots wait (108 pairs, under "just enough for three places" and the cap of three), and in
  9 of the 45 under the ordinary count with the take. Where short knots retire or make offshoots and nothing is
  taken, never (0 of 2,430).

## What this shows and does not show

- **Shown.** The registered study's main statement stands without that tempering: on built starts, what a first
  seed's own descent makes differs with the second seed in ways that the counts of the second seed's births tried
  here do not decide. Where the second seed's knots are the same and their steps from the held knot differ, the
  pair is told apart in some study, all 92. Whether the knots by their steps are enough cannot be asked on the 345
  seeds, since no two share them. The swap pairs ask it, and under some laws the answer is no: which knots are
  partners matters where the steps are the same. That is the first case on this line of a difference that counts
  by steps do not decide.
- **Not shown: that two steps is how far a law sees.** The statement rests on 141 pairs of 59,340, and 251 of the
  345 seeds have every knot within two steps. In all 345 seeds every knot three or more steps out has a loose
  distinction, so no pair differs in whether an existing far knot can take part in round 1. Longer seeds, or far
  knots with no loose distinction, may show more. No argument is written for it.
- **Not shown: that anything reads a form in a fuller sense.** In the pair read birth by birth the whole difference
  is one comparison at one knot, whether it can pay the joins it owes. That the form gets through because that
  comparison is made knot by knot is a reading of one pair, not a result.
- **The meeting is supplied**, as in the registered study: the two seeds share a start distinction. Nothing here
  bears on two parts the growth made.

## The advisor's points

The first tables went to an advisor model with five proposed statements. Its answer changed four:

1. The refutation of the registered reading needs no registration, but should be given on the registered first
   seeds as well (2 studies of 89) and beside its baselines (74% of all pairs told apart).
2. "No tally of counts decides" was false as drafted: the profile with the births of both decides in 220 studies.
   The objection to it is that those births are outcomes, which is now what the note says.
3. "The seed to two steps decides the class" was as thinly tested as the reading being withdrawn: 141 pairs, the
   same in every study, differing only in far loose counts. It is now stated as that.
4. A horizon could produce the table if a difference travelled a step a round. Checked afterwards: where short knots
   retire or make offshoots and nothing is taken every study reaches round 9 and the farthest knot is four steps
   out; and with the take the far differences show in round 1 or 2.
5. "Form" was again too large a word: the tables showed that a tally without steps fails, not that which knots are
   partners matters. The advisor asked for a profile of counts by steps. In the 345 seeds it equals the form, so the
   swap pairs were built to ask it.

## Limits

- **A check.** No pre-registration and no referee; one program, which shares the growth engine with the registered
  study. It agrees with the registered record on the registered family (the last common round, the number of
  classes and both parts of PN7, 90 studies of 90), and its first sweep and its rerun agree on every tally.
- **Seen material.** 138 of the 345 forms were grown before the registered study's freeze and the 60 held-out seeds
  are among the rest.
- **Small seeds of three kinds.** Chains, small rings and one knot with three partners, of at most five knots.
- **Not run**: three studies of 270 on the 345 seeds, all under the ordinary count with offshoots and the take. The
  stop is not at random: those are the laws under which runs grow fastest.
- **The swap pairs** are one construction of 27 pairs. No expectation was written for them.
- **Percentages over pairs** weight the studies by how many pairs share a profile there; the counts of studies are
  beside them.

## How to rerun

```bash
cd research/FOLLOWS-THE-FORM-20261125-001/checks/second_count && python3 -B make_engine.py   # writes eng.py there
cd ../what_decides_the_class
python3 -B drive_profile.py every_seed.jsonl 900 '[["every","KLMNOABCDEFGHIJ",9]]'      # about 21 minutes on 20 threads
python3 -B drive_profile.py registered_family.jsonl 900 '[["fresh","KLMNO",9]]'
python3 -B drive_profile.py swap_family.jsonl 900 '[["swap","KLMNOABCDEFGHIJ",9]]'
python3 -B table.py every_seed.jsonl
python3 -B after.py swap_family.jsonl every_seed.jsonl
python3 -B pair.py '{"ration":"FLOOR1","treatment":"CANCEL-RETIRE","take":null,"first":"K","show":3}' 'path:1,1,2,2@0' 'path:1,2,1,2@0'
```

## Report as sent (26 November 2026, about 03:50 UTC)

(Kept as sent. Three of its statements were narrowed by the referee the same day; see the note at the head.)

The check is in, and it removes the soft spot instead of confirming it. **The sentence I gave you, "in 49 of 90
held-out studies the difference is no more than a count profile", was wrong as a reading: among those 60 forms
almost no two share the profile, so nothing could have contradicted it. On 345 forms the profile decides the class in
3 studies of 267. What a first seed's descent makes follows the second seed's knots by their steps from the held
knot. And in 23 studies of 270 it tells apart two second seeds that differ only in which knots are partners.**

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the check of what decides the class | **Status:** Successful | The question is answered on these seeds. My one written expectation failed (that what the second seed's births are would decide the class: 45 studies of 267), and an advisor model caught my first draft overreaching again before it was recorded. |
| Local direction — built starts with a supplied link | Practically exhausted | The registered result stands without that tempering. What is left is how far out a law sees, which rests on 141 pairs and would sharpen the result, not change it. |
| Broader exploration — the owner's fold of emergence | Known alternatives | The same between two parts the growth made, meeting through a made knot (sub-goal B337); the copier line's case with a made meeting (B336). This check touches neither. |
| Long-term goal — G15, with G18 Comparing growth laws | No demonstrated advance | A wrong caveat is removed and one case added: which knots are partners matters where the steps are the same. The meeting is still supplied by the start. |

**Next step:** Research directions — none started; **STOP** on built starts until the referee has been through the
form study.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The same between two parts the growth made (B337) | 3/3 — the fold's own setting | 1/3 — no start or law in hand gives two made parts of different form at one made meeting; this check says how to read a made second part (its knots by their steps from the knot it meets through) | Search runs already made for two starts with like first parts and unlike second parts that meet through made knots only → one pair with what the first part makes differing, or none in what was searched | Held for the referee's report on the form study |
| 2 | How far out a law sees | 1/3 — sharpens "two steps", changes no question | 3/3 — the program exists | Second seeds with a far knot that has no loose distinction, and chains longer than five → a pair that agrees to two steps and is told apart where nothing is taken, or none | Alternative · deferred |
| 3 | An argument for the two steps where short knots retire or make offshoots | 2/3 — it would be the first proved statement on this line | 2/3 — round 1 is argued in the registered study; later rounds are not | Write the argument for round 2 → a proof for every round, or the round at which it fails | Alternative · deferred |
| 4 | Referee the form study and this check | 2/3 | 3/3 | Started the same day, at the owner's word → its report | In progress |

**STOP evidence:** the check's question is answered, and another sweep on built starts would repeat it. The next test
needs parts the growth made, and it builds on the form study, which no referee has yet read.

**Corrections:** one, logged (Not a block): "decided by a count profile in 49 studies of 90" is withdrawn as a
reading; the number and the registered prediction stand.
**Goals:** no checkpoint row, since no epic closed; notes on sub-goals B335 and B337. No goal changed.
**Assumptions:** A258 (built starts) gets a history line. No new entry and no status change.
**Scaffolds:** the list of second seeds (swapped: 60 for 345, and 27 swap pairs added); the first seed (all fifteen);
the profiles. What survived: that what the first seed's descent makes differs with the second seed. What did not:
the count-profile reading.
**Basket:** directions 2 and 3 noted on B335; none taken.
