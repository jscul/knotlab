# Pre-registration: the place held fixed, the form changed

Ticket `FOLLOWS-THE-FORM-20261125-001A` (sub-goal B335; assumptions A223, A244, A255 and A258; goals G15 with G18),
25 November 2026. Frozen with [the claim](../FOLLOWS-THE-FORM-20261125-001/claim.md),
[the definitions](../FOLLOWS-THE-FORM-20261125-001/definitions.md) (FF) and two data files: [the seeds](seeds.json)
and [what the drafter's probe saw](disclosed.json). The study's program is an independent reading on a shared growth
engine (FF 1): it is to be written from these texts by a helper that has not seen the drafter's probe programs.

## The question

On a start built from a first seed, one link distinction and a second seed, with the first seed and the place of the
link held fixed: does what the first seed's own descent makes differ with the form of the second seed? Is the
difference carried by the link? Does any of it enter after the first round? Is it more than a count at the held knot?
How far into the second seed does it see?

## In standard terms

The sensitivity of one subsystem's trajectory to the structure of a neighbouring subsystem, in a deterministic
growing system of constraints (a growing hypergraph), with the coupling site held fixed. The literature's names, from
memory: information transfer between patterns; signalling in growth models; in cellular automata, one pattern
"reading" another.

## Prior work in the program

Searches, run read-only on 25 November, each with `--until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`:

`python3 -B scripts/track.py objects "what the descent of one part of a built start makes depends on the form of the other part attached at a fixed place" --until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`

`python3 -B scripts/track.py objects "a second seed substituted at a fixed link; classes of second seeds by what the first seed's own births are" --until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`

`python3 -B scripts/track.py objects "how many knots deep into an attached chain a part's own births depend" --until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`

Top three rows:
1. `PARTS-MEET-AGAIN-20261124-001`, `READ-ORIGIN-20261120-001`, `SETTING-AS-REREAD-20261123-001`.
2. `SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001`, `PARTS-MEET-AGAIN-20261124-001`, `PLUS-ONE-20261118-001`.
3. `SUBST-NEST-20261112-001`, `CAP-CHAINS-20261119-001`, `PARTS-MEET-AGAIN-20261124-001`.

What they hold for this question:
- `PARTS-MEET-AGAIN-20261124-001`: one part's course differs with another part stopped, under laws that reach
  further; what crosses is whether the other part is there; "none depends on what the other part is". It varied
  presence, never form.
- `WHAT-A-BIRTH-CARRIES-20261125-001` (the direct predecessor, not in the top rows): the first pattern's first join
  receives two fresh distinctions and one more for each birth the second pattern makes that round; courses separate
  exactly where that count differs. Its second pattern varied only by which members a bar left usable. Its three
  probes of sub-goal B335 are the drafter's own; the third is what this study registers.
- `CAP-CHAINS-20261119-001` and `PLUS-ONE-20261118-001`: chains of offshoots under the cheapest parity growth. They
  describe what a chain grows into, not what a neighbour's descent makes of it.
- The other four are relatives in words only (marks on original knots; a structure for two setting births; a paid
  orientation in the learning line; substitution of blocks into knot patterns).

No record substitutes one form for another at a fixed place.

## Prior work outside the program (from memory, not checked)

Sensitivity to initial structure is the ordinary condition of deterministic growth systems, and nothing here is
claimed as new mathematics. What this adds is the measurement in this model: which features of an attached form a
part's own births depend on, under which laws, and how far in.

## Known before the runs (disclosed; the drafter's unreviewed probe, not the study's program)

The probe is `research/WHAT-A-BIRTH-CARRIES-20261125-001/checks/form_at_a_fixed_place/`, and a second version of it
written after the advisor's review for the readings FF 5b, FF 7 and FF 11 and the unlinked start. Both used ticket
B's engine and readings the drafter wrote; they agree on R\* and the number of classes in the 180 studies both ran.
Everything they saw is in `disclosed.json`, in this study's terms, for 270 studies under not-all-equal: families
`mixed` and `chains` with first seeds A to E, family `second` with first seeds F to J, 18 laws each.

- **Classes among the forms**: 3 to 22 on `mixed`; 2 to 30 on `second`. The bare start is a class of its own in all 270.
- **Unlinked** (run on `mixed` with A to E): every form is in the bare start's class in 90 studies of 90.
- **First told apart**, pairs of forms on `mixed` (18,375 a row): with no taking rule, in round 1 for 9,837 to 10,962,
  in round 2 or later for 1,096 (retiring), 1,096 (offshoots) and 3,047 (waiting); with the take of a sole candidate
  726, 772 and 3,115 in round 2 or later.
- **After the first round** (the wider records of round 1 the same): on `mixed`, 512, 512 and 2,051 of those pairs
  with no taking rule, and 350, 586 and 2,510 with the take; on `second` (9,990 a row), 502, 489 and 765, and 319,
  119 and 474. With the wider records the same through round 2 as well: none where short knots retire or make
  offshoots; 1,287 and 2,175 on `mixed` and 275 and 65 on `second` where they wait.
- **The count profile**: the class is a function of the held knot in 0 studies of 180; of the second seed's births
  by round in 2 of 180; of the two together in 56 of 90 on `mixed` and 13 of 90 on `second`.
- **The wider record** gives more classes than the own descent in 80 and 76 studies of 90, and never fewer.
- **Start knots**: under retiring and offshoots, a member in round 1 only, in every run, read to 9 rounds.
- **Fates** on the window: two or more of ends, steady, grows among the forms in 58 studies of 90 on `mixed` and 62
  of 90 on `second`. With no taking rule on `mixed`, every line that ends is taken up (372 runs) and none has no
  births; lines with no births appear on `second` (109 runs with no taking rule) and with the take (370 on `mixed`).
- **R\***: 9 in 75 studies of 90 on `mixed` and 73 of 90 on `second`; 2 to 7 in the rest, where the guard or the
  knot bound stops a run.
- **Depth** on `chains` (first seeds A to E): with no taking rule, pairs at depth 2 or more told apart in at most 4 of
  140 (4 of 80 at depth 4, under the cap of three with waiting); lengths 3 and 4 in 0 of 80 except 16 of 80 under
  FLOOR1 with waiting; 4 and 5 in at most 4 of 160. With the take of a sole candidate, lengths 4 and 5 in 48, 48 and
  80 of 160 under the ordinary count and 98 of 160 under the cap of three with waiting.
- **Checks the probe made**: renumbering on 150 runs (450 of 450 the same); the knot test on those runs (103,934
  verdicts, none failing).
- **The family `second` was itself a repeat**: fixed with three predictions before it was run; two held and one
  failed in one study of 90 (three or more classes everywhere: one study gives two).
- **Expectations of the drafter that failed**: that with no taking rule nothing would be told apart after round 1;
  that where short knots wait a change at every depth would be seen, later for deeper knots.
- **A reading of the drafter that the review corrected**: the probe's report said the first seed's line "ends"; with
  no taking rule on `mixed` every such line is taken up, not ended (above).
- **Not run by anything**: first seeds K to O; the family `fresh`; parity; the unlinked start on `fresh`.

## Settled by argument (not refereed)

Under CANCEL-RETIRE and CANCEL-OFFSHOOT a start knot acts in round 1 only. In round 1 every member either retires,
which bars its usable loose distinctions, or gives each of them to a birth, which makes it shared. A knot never
gains a loose distinction, a barred distinction stays barred and a holder never lets go. So no start knot is a member
after round 1. PR4 checks it. By itself it says little: anything after round 1 comes through made knots. C2 rests on
the wider record of round 1 being the same, not on this.

## What is supplied

The starts and every choice in them (A258); the laws, the take of a sole candidate among them (A255); the readings
FF 5 and FF 5b; the bounds FF 1; the thresholds below; the seed of the sample. The meeting of the two seeds is
supplied.

## What a result would and would not show

- **If C1 to C4 hold on the held-out material**: on built starts, what a first seed's descent makes differs with the
  form of the second seed, through the link, not by the first round alone, not by the held knot alone, and with
  different fates. It would not show this for parts the growth made, and it would not say what decides the classes.
- **If CU fails** (an unlinked form leaves the bare start's class): something other than the link carries a
  difference, and no other row can be read as registered.
- **If PN3 fails**: every later difference is the first round's, showing late; the earlier tickets' "a count handed
  over" would then cover it.
- **If PN7's second part fails** (the class is a function of the held knot with the second seed's births by round in
  most studies): what is seen is a count profile of the second seed. That would still be a result; it would be
  reported under that name.
- **If the replication rows fail** while the held-out rows hold: the drafter's reading and the study's differ, and
  the study reports its own, with the first differing study.
- **A positive is a statement about built starts under the listed laws.** K to O and the list of 207 were chosen
  after the probe from the same kinds of form, so a pass shows less than a pass on unlike material would. No
  weighting is named.

## Runs

One cap for the whole ticket: **60 minutes of wall time on at most 8 processes**, each under a memory cap of 6 GB.
Before each run a small part is timed at the run's own settings and the whole worked out. If the estimate passes the
cap, the run is cut to a prefix of its registered order (first seeds in alphabetical order, laws in the order of FF 1
with no taking rule first, second seeds in the order of the data file), the cut is recorded before the run, and what
is not run is reported as not run. Estimates from the probe, on ticket B's engine: 0.08 to 0.4 seconds a run.

| Run | What | Runs | Estimate (8 processes) |
| --- | --- | --- | --- |
| R0 | **Gate.** The three starts of FF 2 reproduced. A second growth of a seeded sample of 400 runs of R1 and R2 (seed 1): for laws with no taking rule, by the engine of `PARTS-MEET-AGAIN-20261124-001A`, same structure after every round up to renaming; for the take of a sole candidate, every take recomputed from the rule's words from the places at the start of its round. | 400 | 2 min |
| R1 | **Replication**, not-all-equal: `mixed` and `chains` with first seeds A to E, `second` with F to J, 18 laws. | 13,680 | 8 min |
| R2 | **Held out**, not-all-equal: `fresh` with first seeds K to O, 18 laws. | 5,490 | 4 min |
| R2u | **Unlinked control**: R2 with every start replaced by its unlinked start (FF 2). | 5,490 | 4 min |
| R3 | **Depth, held-out first seeds**, not-all-equal: `chains` with K to O, 18 laws. | 5,670 | 5 min |
| R4 | **The knot law swapped**: R2 under parity. | 5,490 | 4 min |
| R5 | **Controls.** Renumbering (FF 10): a seeded sample of 100 runs of R2 with no taking rule and 100 with the take (seed 2) and 100 of R4 (seed 7), three renumberings each (seeds 3, 4, 5). The knot test, every knot of every round, by ticket B's routine: a seeded sample of 200 runs of R2 and 100 of R4 (seed 6). | 1,200 | 7 min |

Cut order if the cap is near: R5's knot test to half, then R4, then R3. R0, R1, R2 and R2u are not cut.

The drafter's probe is run on the held-out material only after the study's outputs are in, as a second count.

## Predictions

"Seen" means seen in the drafter's probe, on other material unless the row is a replication. Replication rows are
exact; a single differing cell fails them. A row pools three rations and five first seeds (FF 6).

| # | Prediction | Kind | Fails when |
| --- | --- | --- | --- |
| G | R0: the three starts are as written; every sampled run has the same structure under the second growth, or every take is as the rule says | gate | any start differs, or any sampled run differs. A failed gate stops the ticket. |
| PR1 | R1: in each of the 270 studies R\* and the classes equal `disclosed.json` | replication | any study differs |
| PR2 | R1: the tables of first told apart, for `mixed` and for `second`, equal `disclosed.json` | replication | any cell differs |
| PR3 | R1: the depth table for `chains` equals `disclosed.json` | replication | any cell differs |
| PR4 | R1 and R2: under the 12 laws with retiring or offshoots, in every run of `mixed`, `second` and `fresh`, every start knot acts in round 1 only | by argument; seen | any start knot is a member after round 1 |
| PR5 | R1: the tables "after the first round", "fates on the window", "the count profile" and "R\*", for `mixed` and for `second`, equal `disclosed.json` | replication | any cell differs |
| CU | R2u: in each of the 90 studies every form is in the bare start's class | negative control; seen (90 of 90) | any form leaves the bare start's class. Then no row below is read as registered. |
| S1 | R2: the bare start is a class of its own in each of the 90 studies | sanity check: the bare start differs by construction | some form shares its class |
| S2 | R2: the classes among the forms number two or more in each of the 90 studies | sanity check | a study with one class |
| S3 | R3: under each law, a chain of one knot is told apart from a chain of two with the same first loose count, in all 20 pairs | sanity check: the held knot gains a partner | any pair not told apart |
| PN2 | R2: the classes among the forms number three or more in at least 81 of the 90 studies | seen (90 of 90, and 89 of 90) | more than 9 studies with fewer than three |
| PN3 | R2: in each of the four rows with retiring or offshoots, at least 50 of the 26,550 pairs of forms are told apart after the first round (FF 6) | seen (119 to 586) | a row with fewer than 50 |
| PN4 | R2: in each of the six rows between 45% and 95% of the pairs of forms are told apart at R\* | seen (59% to 85%) | a row outside that range |
| PN5 | R2: in at least 40 of the 90 studies the forms show two or more of the fates ends, steady, grows | seen (58 and 62 of 90) | fewer than 40 |
| PN6 | R4: under parity, the classes among the forms number three or more in at least 60 of the 90 studies | open: no scratch run, the drafter's guess | fewer than 60 |
| PN7 | R2: the class is not a function of the held knot in at least 81 of the 90 studies; and it is not a function of the held knot together with the second seed's births by round in at least 25 | seen (not a function of the held knot in 180 of 180; not of the two together in 34 and 77 of 90) | fewer than 81, or fewer than 25 |
| PD1 | R3: with no taking rule, for each of the 9 laws: pairs at each depth of 2 or more are told apart in at most 10%; lengths 3 and 4 in at most 30%; lengths 4 and 5 in at most 15% | seen with other first seeds (at most 5%, 20% and 2.5%) | any law and cell above its bound |
| PD2 | R3: with the take of a sole candidate, under the ordinary count (three treatments) and under the cap of three with waiting: lengths 4 and 5 are told apart in at least 15% of the pairs | seen with other first seeds (30% to 61%) | any of the four laws below 15% |
| C1 | R5: what the first seed's descent makes is the same under every renumbering | by the laws using no names; seen (450 of 450) | any renumbered run differs |
| C2 | R5: under not-all-equal no knot fails the knot test in the sampled runs. Under parity the count of failing knots is reported, with no prediction | seen under not-all-equal (none in 150 runs) | a failing knot under not-all-equal |

How the claim is judged: C1 by PN2 and PN4 with CU; C2 by PN3; C3 by PN7; C4 by PN5, with the split of "ends"
reported; C5 by PD1 and PD2. PN2 to PN7 are not conditioned on the knot test, which is a sampled check: a failing
knot under not-all-equal is reported with its study. Also reported, with no prediction: the classes by the wider
record; the distribution of R\* for every row; every table of R2 and R4 in the form of `disclosed.json`.

## Stop rule

Stop when every registered run within the cap is done and every prediction is judged, holds or fails, or is reported
as not run. No run is added after its outcome is seen.

## Words

First seed, second seed, link, site, held knot, bare start, unlinked start, what it makes, wider record, class, told
apart, fate, taken up: as in FF. "Ring" and "chain" are the record's words for seeds whose knots share distinctions
in a closed or an open row; no claim about space is made with them.

## What the advisor's pass changed

One pass by the advisor model (Claude Fable 5.2, no tools) on the first drafts; its answer was "Freeze after the
listed changes", with ten. The thread wrote them in and the advisor did not see the texts as frozen.

1. **C2 was unsound as worded.** A pair first told apart in round 2 could be one round-1 count held in a knot of both
   descents that the reading does not see. Added the wider record (FF 5b) and judged C2 on pairs whose wider records
   of round 1 are the same (PN3). "Through knots the growth made" is no longer part of the claim.
2. **A form or a count profile?** Added FF 11 and PN7, with a prediction.
3. **Ending or absorption.** Added the wider record's classes as a reported reading and split "ends" (FF 7). The
   second version of the probe showed that with no taking rule every line that ends on `mixed` is taken up.
4. **Fate windows.** Read on rounds R\* − 2 to R\* of the study; the claim and PN5 now say the same thing.
5. **PR4** now covers R2.
6. **FF 6** names its two horizons and the rows; the distribution of R\* is reported.
7. **Independence.** The texts now say "an independent reading on a shared engine", with the engine and BD2 pinned
   by hash in the contract.
8. **The unlinked start** added as a negative control (R2u, CU).
9. **The knot test** is said to be a sampled check on which no row is conditioned; renumbering samples added from R4
   and from the laws with the take.
10. **C5** is worded as counts on the listed chains within the rounds read.

Also from the pass: three rows are labelled sanity checks (S1 to S3); "fresh" is called held-out material of like
kind; FF 2, FF 4, FF 5 and FF 9 answer its questions to an implementer; the claim says "differs with" and "seed".
