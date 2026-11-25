# Is a pattern that leaves two of what it meets made among sampled growths? Pre-registration

Ticket `MADE-COPIER-20261125-001C` of epic `MADE-COPIER-20261125-001` (assumption A249, with A248, A71 and A110). The
code will be written by a helper agent that has not seen the drafter's prototype, from this text ("PC"), [ticket C's
claim](../MADE-COPIER-20261125-001/claim_c.md), [ticket C's definitions](../MADE-COPIER-20261125-001/definitions_c.md)
("DC"), [ticket A's definitions](../MADE-COPIER-20261125-001/definitions.md) ("D"), [ticket B's
definitions](../MADE-COPIER-20261125-001/definitions_b.md) ("DB"), [the fold study's
definitions](../PARTS-MEET-AGAIN-20261124-001/definitions.md) ("FD"), [the shared
definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("SD") and the data files of this folder
([starts_c.json](starts_c.json), [cases_c.json](cases_c.json)). The engine will extend the fold study's engine
(`experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py`) without editing it,
as ticket A's does. The canonical K1–K3 test is unchanged. Versions 1 and 2 of this text are filed in the advisor folder
as sent; where a reading changed, the change is said where it is made, and the last section says what the advisor's
passes changed. No claim is made about living things, minds, physics or time.

**Frozen on 2026-11-25 (UTC), after the advisor's two passes on this ticket and before its code is written.** The
frozen texts of tickets A and B are not changed by anything here.

## The question

The owner, 24 November 2026 (Pacific time; the record's tickets carry 25 November): "What if we need to statistically
hit a 'copier' like DNA and primordial soup?" His standing words for the study keep a law and a pattern apart: "a law is
the rule the growth follows (which knots join, what a new knot receives, what a short knot does); a copier is a pattern
the growth makes." Read (claim, section 1): under a stated family of laws with a taking rule, with the record's census
of small starts read (every start under parity with MET, prefixes of one random order under the other laws) and every
take sampled, how often does the growth make a pattern that, on meeting a second pattern the growth also made or kept,
leaves two of it more often than with the second pattern barred, than the second pattern leaves of its own, and than
when neither can join or take from the other, and is any one pattern seen doing so for several second patterns, again in
fresh growths? DNA and a primordial soup are his pictures; every pattern that meets here is descended from one supplied
start of three to five knots, and the meetings are made by the law's takes.

## In standard terms

In the literature's words, not the program's: each law with its takes sampled is a Markov process on finite states
(hypergraphs whose hyperedges carry a parity equation over the field of two elements or a not-all-equal condition,
together with their bars, retirements and record of parents), started from a stated distribution over small connected
starts; a sampled growth is one trajectory; a rate is the chance of an event under the process, estimated from
independent trajectories, a zero bounded by the rule of three; the continuations are a paired comparison of the process
continued from one state with nothing barred, with one component barred, with the other barred, with the two kept from
joining, and with the two kept from joining and from taking each other's distinctions; a case met more often with Y is a
difference of binomial proportions, first passed and then confirmed on fresh trajectories with a Bonferroni correction
for the number of cases tested. A candidate seen again would be what the origin-of-life literature calls, as the nearest
term in that literature, a **template replicator** (a pattern that leaves copies of patterns other than itself), as
against a pattern that copies itself, which the record already has.

## Prior work in the program

Searches, each with `--until 2026-11-25 --exclude MADE-COPIER-20261125-001`:

`python3 -B scripts/track.py objects "sampling very many growths for a pattern that copies another, the rate of growths in which it is made under a named weighting" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

`python3 -B scripts/track.py objects "takes sampled at random, every choice, the take-by-take weighting, histories with two made distinctions tied to one place" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

`python3 -B scripts/track.py objects "census of every start of up to five knots with single meetings, weighting of starts, labelled starts" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

What they return (run read-only by the drafter on 2026-11-24), one line each, in the order returned:

- First search.
  - `NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001/1`, `STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001/2`,
    `READS-HOLDERS-SOURCES-20261120-001/4` — weightings of named histories and states on other objects; not used.
  - `PARTS-MEET-AGAIN-20261124-001/2` — **used**: the law (MET) and the paired test; one part's course differs with
    another stopped, and "none depends on what the other part is".
  - `PARTS-MEET-AGAIN-20261124-001/1` — **used**: parts that share nothing never become one part without a taking rule
    (FD 3.1; claim, C-S4).
  - `ERASURE-AND-CLOSING-SIGNS-20261121-001/4` — rates under a founder weighting on other objects; not used.
  - `RING-IN-BALANCE-20261123-001/4` — the census and the laws on returning rings; the census is used (starts_c.json).
- Second search.
  - `PARTS-MEET-AGAIN-20261124-001/1`, `/2` — as above.
  - `WEIGHTINGS-20261119-001/1` — a relative: starts of 5 to 20 knots under seven weightings change a proved class's
    share; the reason every rate here names its weighting and has a swap.
  - `DISTANCE-INFO-20261117-001/1` — unrelated.
  - `ONE-PARENT-REREAD-20261123-001/1` — the same kind of law (rule Q) on other objects; every round-1 choice read.
  - `GROWTH-STATISTICS-20261121-001/2` — a relative: independent against adaptive sampling of later growth; not used.
  - `SHORT-DESC-20261112-001/1` — a relative: patterns sampled by short descriptions, a weighting of patterns, not of
    histories; a possible later weighting of starts.
- Third search.
  - `READ-ORIGIN-20261120-001/5`, `/3`, `/1`, `KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001/5`,
    `COPIES-AND-MEETINGS-20261120-001/7` — weighted panels of labelled trees and single-meeting starts on other
    questions; the labelled weighting is of the same kind; not used.
  - `MEET-GROW-20261118-001/1`, `PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001/2` — unrelated objects.

Also used, not returned in the top rows: `COPYING-PARTS-20261123-001/3` (the census of the part that copies itself: 85%
to 97% of the 3,344 starts under FLOOR1 with no taking rule, "under that one weighting"; no knot fails under FLOOR1),
and tickets A and B of this study (their settled statements S1, S2, S4 and S6, and ticket B's renaming statement).
`TIME-AS-FOLD-20261125-001` (planned, of the same date) appears among the other epics of each search and is not read.

The epics of the top rows of the three searches, by their IDs: `COPIES-AND-MEETINGS-20261120-001`,
`KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001`, `NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001`,
`PARTS-MEET-AGAIN-20261124-001`, `READ-ORIGIN-20261120-001`, `STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001` and
`WEIGHTINGS-20261119-001`.

## Prior work outside the program

Each from memory, the literature's, not checked:
- **Autocatalytic sets** (Kauffman, 1986; formalized by Hordijk and Steel as reflexively autocatalytic food-generated
  sets): in a random network of reactions with enough kinds of molecule and a fixed chance that a molecule speeds a
  reaction, a set that makes itself collectively appears with high probability under the literature's random weighting
  of reactions. A case of ticket B's reading here (two of Y left from both, only with X) would be one such reaction made
  by a growth, not a template copier.
- **Tierra** (Ray, 1991): a hand-written program that copies itself, in a shared memory of programs; parasites arose
  that copy themselves with another program's code for it. The closest case here is ticket B's reading: Y left twice by
  births of both.
- **Random programs meeting in pairs** (Agüera y Arcas and others, 2024, "BFF"): random byte programs, paired at random
  and run on their joined tape, give programs that copy themselves spontaneously after very many interactions, with no
  fitness given. Its instruction set has instructions that write a byte read elsewhere on the tape; no law here has such
  a step (the owner's premise), so a copier has to be a pattern the growth makes under laws that have none.

What this would add: under laws with no such step, on structures every piece of which passes the canonical knot test, a
rate, with its weighting, at which a made pattern leaves two of each of several second patterns it meets, or a bound on
that rate with the reasons the law gives for it. Not searched further.

## Known before the runs (disclosed)

The drafter wrote a scratch prototype (in its scratch folder, `c/`: version 1 `c_starts.py`, `c_proto.py`,
`c_census.py`, `c_resume.py`, `c_recheck.py`, `c_t2.py`, `c_rename_exact.py`, `c_stage2.py`, `c_rates.py`,
`c_rates_met.py`, `c_rates_vals.py`, `c_rates_form.py`, `c_rates_conf.py`, `c_conf_origins.py`, `c_conf_strict.py`,
`c_final.py`, `c_swapsum.py`; version 2 `c2_read.py`, `c2_posctl.py`, `c2_posctl_sum.py`, `c2_rename_exact.py`,
`c2_checks.py`, `c2_strata.py`; unreviewed; not the study's engine; its author does not write the study's code). It
imports the fold study's engine read-only and adds the readings of tickets A and B, the samplers and the continuations.
Everything it showed is listed here. "Seen" means seen in the prototype. Its bounds were 6 rounds and at most 300 knots,
against the registered 8 and 500. Two things in this text were chosen after the scratch was seen, and lean as said: the
taking rule STEPS-1 entered the family (it gives many more pairs: toward a positive), and the values reading claimed is
"values, both from X", defined after ticket A's looser values reading was seen to pass the first two comparisons with
its second distinction made by Y (toward a negative, since the looser reading is then only reported).

**What the gate cannot test.** As in ticket A: the growth code is the fold engine's, so an equality of runs with it
tests nothing new. What is written afresh and must be tested: the census list and its weights, the samplers and their
calls, the seeds, the pair rule, the readings with their descents, the continuations of the five kinds and their rates,
the two families, the stage-2 counts, the renamings of R7 and R8.

**The guard, read in the engines.** The fold engine's guard (`pm.py` lines 20–38) compares with fixed limits counts
taken at lines 397 (incidences), 407 and 508 (candidate pairs within the largest met set), 517–543 (joinable pairs,
summed met set by met set in name order), 466–468 (maximal cliques, counted by networkx's `find_cliques` on a graph
built in name order), 488 (groups), 789 and 820 (births) and 1005 (distinctions). Each count is a function of the state;
where the count is taken in name order (cliques, joinable pairs) the limit is passed exactly when the total passes it,
so whether a round is stopped does not depend on names (Settled 1, (g)). Ticket A's engine
(`experiments/MADE-COPIER-20261125-001A/MADE-COPIER-20261125-001A-E001_made_copier/mc.py` lines 560–612) has one search
whose order follows names and which stops at a bound: its search for renamings of Y's knots (built structure, D 3.2),
which ticket C does not read; its form reading uses the fold engine's guard (`mc.py` line 859).

**The census rebuilt** (`c_starts.py`). From the record's description: 19, 200 and 3,157 starts on three, four and five
knots, equal to the record's list in order, with the record's 32 set-aside flags (3 of four knots, 29 of five); every
start knot of the 32 fails the parity knot test at round 0 and passes the not-all-equal one. Labelled weights: 63, 2,786
and 254,454 over the census; 63, 2,774 and 253,724 over the 3,344 starts passing under parity; the five-knot starts hold
93.5% of the census weighting and 98.9% of the labelled one. **No tie at round 0 under not-all-equal** in any of the
3,376 starts (`c2_checks.py ties`; C-S2).

**The scratch census** (`c_census.py`, `c_resume.py`). The 21 laws with MET, both knot laws, takes under the
take-by-take weighting with the scratch's seeds `C|<start id>|<ration>|<treatment>|<knot law>|<i>`, the pair rule of FD
5.8 (the first eight parts by name, at most eight pairs a round). Starts: every start of three knots (indices 0 and 1)
and of four knots (indices 0 and 1 under parity; under not-all-equal index 1 for every start and index 0 for about a
third, the process being stopped for its cost); five-knot starts sampled, 150 under the census weighting
(`random.Random('2026112601|W1').sample(range(3157), 150)`) and 100 under the labelled weighting
(`random.Random('2026112601|W2').choices(range(3157), weights=labelled, k=100)`), index 0, under parity all 250 and
under not-all-equal about 142 of them per law (the process stopped; the jobs read are fixed by their place in the job
list, not by their outcome). In the labelled sample two starts were sampled twice and grown once (one seed), so that
sample gives 98 growths per law under parity. Sampled growths read, by stratum, under parity (per law): three knots,
all, twice each: 38; four knots, all, twice each: 394; five knots, census-weighting sample: 148; five knots, labelled
sample:
98. Under not-all-equal: 38, about 273, about 92, 49.
- **Pairs, by start size** (for PC1): under COPY-LAW(CANCEL-OFFSHOOT), three knots 36.8% (parity) and 44.7%
  (not-all-equal), four knots 51.3% and 46.9%, five knots 36.4% and 36.7%; under the other 20 MET laws pooled, at most
  1.1% on each size.
- **Pairs.** Growths with a pair in rounds 1 to 4: under COPY-LAW(CANCEL-OFFSHOOT) 303 of 671 under parity (45.2%) and
  196 of 450 under not-all-equal (43.6%); under each of the other 20 laws 0.3% to 4.5% under parity (the largest share
  under FBP(CANCEL-RETIRE), 30 of 671) and 0.2% to 2.9% under not-all-equal (the largest under RATION-2(CANCEL-RETIRE),
  13 of 451).
- **Why** (the run of DC 2.2's sampled pair rule, `c_t2.py T1`: parity, the starts of three and four knots, sample index
  0, 4,536 growths, 17,725 rounds 1 to 4 read): the roster had no part in 2,799 rounds (15.8%), one part in 14,747
  (83.2%) and two or more in 179 (1.0%), and every round with two or more parts had them wholly apart. Under
  COPY-LAW(CANCEL-OFFSHOOT) 122 of 864 rounds had two parts or more, under every other law at most 8 of 864; under the
  retiring treatment the roster was empty in 26% to 62% of rounds (the growth had ended).
- **The sampled pair rule** gave the same pairs as FD 5.8's in all 4,536 of those growths; three rounds had more than
  eight pairs.
- **Cases**: 96 (92 form, 4 ticket A's values reading; none from both, none of values both from X), in 80 growths: 93
  under COPY-LAW(CANCEL-OFFSHOOT) (50 under parity, 43 under not-all-equal), 3 under FBP(CANCEL-RETIRE), parity; by s: 2
  at s = 2, 28 at s = 3, 67 at s = 4 (counting the one start grown twice). The second patterns of the form cases: one
  member holding one loose distinction, joinable with none, in 87; two members holding one in 2; two holding two in 3.
  None has Y's form the same as X's. They are listed, with their counts, in [cases_c.json](cases_c.json).
- **Their first continuations, 20 with Y barred and 20 with X barred** (`c_recheck.py`): every form case was met again
  with Y barred (92 of 92; in the first 60 read, 3 to 17 of 20), and in 27 Y also left two of its own with X barred; of
  the values cases, 1 was met with Y barred and 3 had Y's own with X barred (1 to 3 of 20).
- **Their rates, form** (`c_rates_form.py`, every one of the 92 at 100 continuations of the first three kinds, i = 0 to
  99): with nothing barred met after the meeting in 2 to 71 of 100, with Y barred in 11 to 82; with Y barred at least as
  often as with nothing barred in 90 of the 92; none passes at 100 (the smallest one-sided p, 0.15).
- **Their rates, values** (ticket A's reading, at least one of the two from X; `c_rates_met.py`, `c_rates_vals.py`): at
  50 of each kind, (1, 1, 1), (3, 0, 4), (0, 0, 7) and (4, 0, 1) (nothing barred after the meeting, Y barred, Y's own);
  at 300, (19, 7, 7), (21, 0, 25), (2, 0, 24) and (20, 0, 5). The first and the last, read on 1,000 fresh continuations
  of each kind (`c_rates_conf.py`, sample indices 1,000 to 1,999): (83, 33, 33), one-sided Fisher p = 1.0 × 10⁻⁶ against
  each, and (58, 2, 13), p = 7 × 10⁻¹⁶ and 2 × 10⁻⁸: both pass the Y-barred and X-barred comparisons. The tied
  distinctions of the continuations that met it (`c_conf_origins.py`): in the second, one from X only and one from Y
  only in all 58; in the first, two from X only in 37, one from each in 42, three in 4. **Masked** (`c2_checks.py
  valmask`, 1,000 continuations with X and Y masked, the same indices): 89 and 85 of 1,000 meet the reading, against 83
  and 58 with nothing barred: **neither is met more often than with the members of X and Y unable to join**; the excess
  over the Y-barred control comes not from the joining; takes were not blocked (the fully masked kind of DC 4.1 was not
  run). In the second case all 58 continuations that met the reading had one distinction tied to Y's place made by a
  birth descended from X only and one by a birth descended from Y only; by ticket A's S3 the X-only birth's tie runs
  through its inputs (whether through a take was not read). In the first, of 83, 37 had both made by X-only births. Read
  as values, both from X (`c_conf_strict.py`; `c2_checks.py valmask`): (39, 33, 33), p = 0.27, masked 38; and (0, 2,
  13): neither passes the Y-barred comparison. That, and one of the two being Y's own, is why these two are not a
  copier; the masked result is not the reason. The other two cases were not read as values both from X at 1,000.
- **The unmet pairs** under COPY-LAW(CANCEL-OFFSHOOT): the form reading was met on 25 of 269 pairs that never met (9.3%)
  under parity and 8 of 165 (4.8%) under not-all-equal, against 46 of 843 (5.5%) and 43 of 519 (8.3%) of the met pairs
  after the meeting.
- **Again in the same growth** (one X form in two or more cases of one growth): 3 growths under parity and 4 under
  not-all-equal under COPY-LAW(CANCEL-OFFSHOOT), 1 under FBP(CANCEL-RETIRE). With no case met more often with Y the runs
  cannot tell whether a pattern that had one has another more often.
- **Zero, bounded, by stratum** (`c2_strata.py`): no case of the form reading passes at 100. Each law separately, at
  0.95, under the take-by-take weighting: three knots, census weighting, every start read twice: below 3/38 = 7.9%; four
  knots, census weighting, every start read twice: below 3/394 = 0.76% (parity) and about 3/273 = 1.1% (not-all-equal);
  five knots, census-weighting sample: below 3/148 = 2.0% (parity) and about 3/92 = 3.3% (not-all-equal); five knots,
  labelled sample: about 3/98 = 3.1% (parity) and 3/49 = 6.1% (not-all-equal), "about" because two starts sampled twice
  were grown once. These bound only cases the test can see (DC 4.4, power).
- **Knots** (`c2_checks.py kfail`, every failure classified): under not-all-equal no knot failed in any growth. Under
  parity 298 of the 14,091 growths (2.1%) had a failing knot, one knot each, under every one of the 21 laws (4 to 33
  growths per law). All 298 are joins failing in the round they are made: 151 joins of two parents that took a
  distinction (fresh); 145 joins of three to twelve parents with no take (fresh); 2 joins of five parents with no take
  whose birth was implied. Two of the 96 cases are in such growths.
- **C-S3's gap, checked** (`c2_checks.py members`; parity, the starts of three and four knots, index 0): under
  COPY-LAW(CANCEL-RETIRE) and COPY-LAW(CANCEL-OFFSHOOT) with MET and with STEPS-1, no growth of 219 had a member after a
  round t made before round t; under COPY-LAW(CANCEL-WAIT), 196 (MET) and 195 (STEPS-1) of 219 had one, and 20 and 25 an
  offshoot of a start knot holding two.

**The swaps on the starts of three and four knots** (`c_t2.py`, parity, sample index 0, 4,536 growths each, with DC
2.2's sampled pair rule and 20 continuations with Y and with X barred for every case):
- **The holder weighting** (`|T2`): growths with a pair 85 (1.9%) against 150 (3.3%) under the take-by-take weighting;
  under COPY-LAW(CANCEL-OFFSHOOT) 56 of 216 against 102; 2 cases (1 form, 1 values), both met with Y barred or with Y's
  own in their 20 of each kind.
- **HOLD for RELEASE** (`|HOLD`): growths with a pair 152; "wholly apart" removed 20 of 507 ordered pairs with X made; 6
  form cases, 5 met with Y barred; one, on `n4-g18-1233` under COPY-LAW(CANCEL-OFFSHOOT), was met in none of 20 with Y
  barred and Y's own in none of 20 with X barred, and then was met after the meeting in 1 of 200 continuations with
  nothing barred against 16 of 200 with Y barred (`c_rates.py`).
- **STEPS-1 for MET** (`|STEPS-1`): growths with a pair 2,494 (55%; 35% to 91% by law); rounds with two parts or more
  6,431 of 18,144 (35%); "wholly apart" removed none of 20,169 ordered pairs with X made; 310 rounds (in 224 growths)
  had more than eight pairs; 52 form cases (14 at s = 1, 14 at s = 3, 24 at s = 4), of second patterns of one member
  holding one (37), of two, three or four members holding two (14) and of mixed holdings (1); 50 met with Y barred. Two
  were met in none of 20 continuations with Y barred and had Y's own in none of 20 with X barred, nor in 50 of each (nor
  X alone, every part but X barred, two of Y's form in any of 50): on `n4-g14-1222` under RATION-2(CANCEL-RETIRE), X the
  two-knot part and Y three members holding two in two met sets of two, s = 1, meeting at round 2, two parts of Y's form
  from X only after round 6 and not after round 7; on `n4-g17-3232` under CAP-2(CANCEL-OFFSHOOT), X five members holding
  two, Y four in one met set, s = 3, meeting at round 4, two after round 6 only. **Both are one-history cases**: from
  the state after round s, the reading was met after the meeting in 0 of 200 continuations with nothing barred (the
  second: 1 of 200 with Y barred, 2 of 200 with Y's own). In 100 further growths of each start (sample indices 100 to
  199) no case of the same two forms.

**The rule for a case met more often with Y.** The prototype first called a case one that "needs the meeting" when its
reading was met in none of 20 continuations with Y barred and Y's own in none of 20 with X barred. The three cases that
passed it were one-history cases (at most 1 of 200 with nothing barred), and the two values cases that later passed the
Y-barred and X-barred comparisons at 1,000 were met as often or more with X and Y masked. So DC 4.3 and 4.4 compare
rates. **The fully masked kind (`|BT|`) and the rule that a confirmed case beat it were added after the scratch**, at
the advisor's last pass (a birth that takes a distinction held by a knot of Y meets that knot, SD line 14 and FD 1.2, so
the masked control alone tests only the joining). The change leans toward a positive: the fully masked kind blocks more
than the masked one, so a case beats it more easily. No scratch case of a claimed reading changes verdict by it: none
passed the Y-barred and X-barred comparisons.

**The controls of the rate rule, on ticket A's made designs** (`c2_posctl.py`, `c2_posctl_sum.py`; parity, the growth
through round 1 then 100 continuations of each of the four kinds, the 42 laws; 183 of the 210 cells read, the ORD laws
left out for cost after made-2 under ORD(CANCEL-OFFSHOOT) with MET). The claimed readings were met after the meeting
with nothing barred in 2 cells (form, 1 of 100 each: made-4 under RATION-2(CANCEL-OFFSHOOT) and FBP(CANCEL-OFFSHOOT),
both with STEPS-1), and ticket A's values reading in 2 (made-2 under COPY-LAW(CANCEL-OFFSHOOT) with MET, 5 of 100
against Y's own 5; made-5, 1 against 18). **No cell passes at 100: ticket A's designs under sampled takes give no
positive control for the form reading**, and none for values. Y's own (DC 4.2), read with nothing barred, is met often
in some cells (values both from Y only: made-5 and made-4 under COPY-LAW(CANCEL-OFFSHOOT) with STEPS-1, 86 and 78 of
100, against 0 with Y barred). R0b registers that as **the machinery control**, under its own rule (DC 4.7: it tests the
continuations, seeds, readings and test, not a copier, and its Y-barred side is empty by construction), and a **planted
case** beside it (DC 4.7), since the machinery control never exercises the meeting round, the form reading, descent from
X only, the X-barred test or the masked kinds. **The planted pair** was chosen from the 92 MET form cases read at 100
(`c_rates_form.py`): index 13 of cases_c.json met in 99 of 100 continuations with nothing barred, with the reading met
after the meeting in 2, with Y barred in 16 and Y's own in 0. With placements at chance 0.30 (the advisor's figure), a
simulation of the test on those rates (inline, in scratch) gives a pass at 100 in about 51% of trials; at 0.5, in 99.8%
(4,000 trials each); R0b registers 0.5. Negative controls: made-2 (Y's form is X's), the two design cells where form was
met, and ten of the 92 MET form cases by a registered sample.

**The exact renaming check** (`c_rename_exact.py`, version 1; `c2_rename_exact.py`, version 2; Lemma C-S1). Version 1:
36 starts (all 19 of three knots, the first 17 of four), six laws with MET, the take-by-take weighting, both knot laws,
two renamings: 425 checks, all equal; but 192 of them had a single history and so tested nothing about takes. Version 2,
with five renamings (knots and distinctions reversed; both permuted; the order of distinctions shifted by one; knots
alone; distinctions alone), the class compared including the birth record and barred marks, at most 30,000 histories: on
the three-knot starts and eleven laws (MET under both weightings of takes, STEPS-1 under both, HOLD; both knot laws),
243 checks, on the first 12 of the 19 starts, all equal under all five renamings; 101 had a single history; 420,087
histories in all, of which 419,986 hold a take with two or more candidates (142 checks), 419,773 two taking births in
one round (205 checks), 83,379 a join of three or more parents (57 checks) and 25 an implied birth (18 checks). On
four-knot starts (planned: the first 12) under the holder weighting with MET, STEPS-1 under both weightings, and HOLD
(both knot laws): 84 checks on 8 starts, all equal under all five renamings; 19 had a single history; 194,023 histories
in all, of which 194,004 hold a take with two or more candidates (65 checks), 193,964 two taking births in one round (75
checks), 22,711 a join of three or more parents (39 checks) and 175 an implied birth (7 checks). Both runs were stopped
for time, on the three-knot starts after 243 of 418 checks and on the four-knot starts after 84 of 168.

**Costs at the registered bounds** (`c2_time.py`, `c2_time_sum.py`; 8 rounds, at most 500 knots; starts in the order
`random.Random('C|time').sample(range(3376), 3376)`, each law of the 42 in order, index 0; every reading, the pairs, the
knot test, and for each case the first stage, 100 continuations of each of three kinds with their knot tests; each
timing run cut at 5 to 10 minutes, so the starts timed are a prefix of that order): parity, MET, 0.121 seconds a growth
(5,098 growths of 243 starts; 0.0088 cases a growth, 1.2 seconds a case's first stage); parity, STEPS-1, 0.421 (1,457
growths of 70 starts; 0.019 cases, 10.6 seconds); not-all-equal, MET, 0.449 (1,337 of 64; the knot test 0.35 of it);
not-all-equal, STEPS-1, 6.5 with the knot test at every round (101 growths of 5 starts), 2.7 and 3.6 with it at the last
round only, with and without the continuations' knot test (318 and 270 growths), single growths up to 400 seconds; the
holder weighting under parity, 0.108 (MET) and 0.316 (STEPS-1); HOLD under parity, 0.087 (MET) and 0.859 (STEPS-1);
STEPS-2 under parity, 0.396; HOLD with MET under not-all-equal, 0.482. Two timing processes that passed their budget on
one long growth were stopped by their numbers. These rates size the runs ("Runs"); R0b, R3, R6 and R7 are sized from the
scratch's other runs and marked estimated.

**What ran long.** The not-all-equal growths (0.4 to 3 seconds each, nearly all of it the knot test) made the census
take about two and a half hours on up to four processes, each under a memory cap of 7 GB; two of its four processes were
stopped before the end, as said. The run on ticket A's made designs took about 75 minutes on two processes (the ORD
laws, whose continuations reach the knot bound, were left out after one); the version-2 renaming checks ran about 70
minutes on two processes and 50 on four before they were stopped; each swap 15 to 45 minutes. Every process was stopped
by its own number.

**Not run by the drafter**: STEPS-1 on five-knot starts or under not-all-equal; STEPS-2; anything past round 6; the
counts by form (DC 7) beyond the number of forms left twice; the holder weighting under not-all-equal; the
built-structure reading; R8; the masked control on any case but the four values cases; the fully masked kind; the
planted case (only its power simulated); "not of the others" by growths.

## Settled by construction (stated, not tested)

Arguments of the drafter, not refereed; the runs check them.

1. **Lemma C-S1 (renaming, with takes sampled).** *Statement.* Let φ be a renaming of a start: a one-to-one map of its
   knots and a one-to-one map of its distinctions (any order of names; DC 1.1 names distinctions by label). For every
   law of the family and both swaps of the law, under the take-by-take and the holder weightings, the weighting of the
   sequence of states (DC 1.6: the structure with its barred marks, its retired knots, the birth record, the parity
   rules, the round number) grown from φ(start) is the image, under renamings extending φ, of the weighting grown from
   the start. So every event defined up to renaming (forms, descent, ties, the readings, the meeting round, the
   continuations of DC 4.1 with their kinds, pairs sampled uniformly by DC 2.2, the knot test) has the same chance, and
   every rate of DC 4.5 is the same for every numbering of the start. *Argument*, by induction on rounds, from two
   states S and S′ = ψ(S), ψ a renaming of states (knots and distinctions, keeping holders, bars, retirements, parents,
   kinds, rounds made):
   - (a) The roster, met sets, joinability, groups, parts, owing and short members are defined from the state without
     names (FD 1; SD lines 36–54: groups, owing, short and the three treatments are nameless), so ψ carries them; names
     enter a round only in which loose distinction goes to which birth and in HOLD's "first" (FD 2.1).
   - (b) **Rations.** FLOOR1, FBP, CAP-2, CAP-3, CAP-4, ORD and RATION-2 give a birth's fresh count as a function of p
     (its distinct inputs, or its parents under FBP) and its demand D only (the fold engine's `Law.fresh_count`); none
     uses names or the order of making.
   - (c) **Treatments, RELEASE and HOLD** use names only to say which usable loose distinction of a member goes to which
     birth, or is kept, or is barred. Two runs of the round from S and from S′ can therefore differ, beyond ψ, only by a
     permutation of each member's usable loose distinctions, and such a permutation is a renaming of the state,
     **because a loose distinction has one holder** (and a usable one is not barred): exchanging two of them keeps every
     holding, bar and birth record; a usable loose distinction is also in one knot's rule only, is never eligible (FD
     2.2) and enters no weight. Under a taking rule the step is unchanged, since step 5′ comes after the births are
     formed and a loose distinction is no candidate. The knot laws' indifference to the order of a knot's places is
     needed only so that ties and the knot test are carried too.
   - (d) **Takes.** Under MET, STEPS-1 and STEPS-2 a birth's candidates and their eligibility are read on the state at
     the start of the round and leave out only the birth's own inputs (FD 2.2, 2.4; the fold engine's step 5′: one list
     per taking birth, `take_candidates` read on the structure before the round); one birth's take changes no other
     birth's list. The take-by-take weighting gives each candidate of a list one over its length; the holder weighting a
     chance in proportion to its number of holders at the start of the round; both are read off the state, so ψ carries
     each list with its chances, and the takes of different births are independent. The order in which the takes are
     called changes which sample a seed gives, not the weighting.
   - (e) **Demand.** The round's takes change other births' demand (the demand roster is read after the takes, DC 1.6;
     the fold engine's step 6), and so their fresh count under ORD and CAP-k. Demand is a fixed function of the state
     and of the round's takes together, so it is carried.
   - (f) **Implied births** (parity, IMPLIED) are each tested against the parity rules before the round with their own
     inputs: carried. **Joins of three or more parents**: names enter only through birth order: carried. New knots and
     fresh distinctions are named in birth order; a renaming of them extends ψ.
   - (g) **The guard** (checked in the fold engine, `pm.py` lines 20–38, 389–548, 789, 820, 1005): it compares with a
     fixed limit the number of incidences, of candidate pairs within the largest met set, of joinable pairs, of maximal
     cliques, of groups, of births and of distinctions. Each is a function of the state. The cliques are counted by
     networkx's `find_cliques` on a graph built in name order, so the clique at which the count passes its limit depends
     on names, but the count passes the limit exactly when the number of maximal cliques does, which does not; the
     joinable pairs are counted met set by met set in name order, and the running count passes the limit exactly when
     the total does. So whether the guard stops a round does not depend on names, and "a round the guard stops is not
     read" is carried. (Ticket A's engine has a bound reached in name order in its search for renamings of Y's knots,
     `mc.py` lines 560–612; ticket C does not read built structure.)
   - (h) **Eight pairs sampled uniformly** (DC 2.2): carried in weighting. **Seeds** name the census's numbering: they
     change which sample is seen, not a rate.
   *Why ticket B's renaming statement is not cited for (a) and (c).* DB 7 states a conclusion for no taking rule and
   says that under a taking rule it fails in general; the failure came from choosing a candidate by name (OLDEST,
   NEWEST, IN-TURN, BY-COUNT). It does not say that the cancellation steps use no names; SD lines 36–54 and FD 2.1 do.
   With every take sampled, each candidate's chance is read off the state, and (d) replaces the step by name. *Status*,
   and the wording the result will use: "argued for every law of the family and both swaps (the drafter's outline, not
   refereed); checked on every history through round 3, or fewer where said, of [n] small starts under parity, up to a
   Weisfeiler–Lehman class, [M] of the checks holding a take with two or more candidates; and by sample at 8 rounds on
   one statistic" ([n] and [M] from R7; the statistic is R8's). "Exactly" is not used: the class is a Weisfeiler–Lehman
   hash, which can merge states that differ.
2. **C-S2, not-all-equal.** Ticket A's S6 (record: `READS-HOLDERS-SOURCES-20261120-001/2`): with at most two holders,
   every distinction can change alone, so a start of the census has no tie (checked on all 3,376: "Known before the
   runs"). A birth with a single distinct input receives at least two fresh distinctions (FLOOR1 and FBP max(3 − p, 1);
   CAP-k with k ≥ 2 and ORD at least max(3 − p, 1); RATION-2 at least 2, with p the distinct inputs, FD 2.7); a birth
   with one fresh distinction has two or more inputs, never all tied equal while nothing is tied; so by ticket A's S2
   (with S1) no made distinction is tied. S2 with three or more holders is unrefereed. None of the values readings is
   ever met under not-all-equal.
3. **C-S3, COPY-LAW with a taking rule.** Ticket A's S4 (under MET and STEPS-1): every knot made by a birth other than
   an offshoot of a start knot holds at most one loose distinction, and a knot's loose distinctions never grow in
   number. By D 2.6 X's own members are from X only, and one of them can be an offshoot of a start knot holding two (X
   is a made pattern, so its members are made after round 0, possibly in round 1). Under CANCEL-RETIRE and
   CANCEL-OFFSHOOT with RELEASE every member after round t was made in round t (checked: "Known before the runs"), so
   for t > s ≥ 1 the members of the two parts are made after round 1 by births with a made parent, and hold at most one
   loose distinction each; so do Y's members, whose form is theirs. **Argued for COPY-LAW(CANCEL-RETIRE) and
   COPY-LAW(CANCEL-OFFSHOOT) with MET and with STEPS-1** (four laws). Under CANCEL-WAIT, and under HOLD, a member made
   earlier can wait and sit in one of the two parts, so there the statement is **checked** by the runs, not argued.
4. **C-S4, no taking rule**: FD 3.1; ticket B.
5. **C-S5, the bound**: DC 4.5 (e^−3 < 0.05; ln(84/0.05) = 7.4 for all laws at once).
6. **C-S6, one connected start.** A birth takes only a distinction held by a knot its parent meets (MET) or by a parent
   of its parent (STEPS-1; STEPS-2 two parent steps up), all in its parent's connected structure, and its fresh
   distinctions are new; so each knot made lies in its parents' connected structure, and parts in different connected
   structures never become one part. The census's starts are connected.
7. **The knot test at the last round.** Under every law of the family (every birth receives a fresh distinction, or,
   under parity with IMPLIED, adds a rule already in the span), ticket A's S1 holds: the allowed states restricted to
   the distinctions that exist do not change in later rounds. A take adds a holder, but the taking birth brings its own
   fresh distinction, which nothing else holds, so every allowed state still extends; an implied birth adds a rule
   already in the span; barring and masking change no rule. So the allowed states restricted to a knot's places never
   change after its round, a knot's verdict is fixed in the round it is made, both ways, and testing every knot of a
   growth or a continuation at its last round read finds every failure. The departure from D 8 is smaller than it looks:
   D 8 already tests comparison runs at their last round only; growths lose the every-round test, which is kept on R1's
   growths of small starts (R9).
8. **Checks, true by construction**: a sampled history is a history of the law (every take is one of its candidates);
   the seeds fix every sample, so every growth and continuation replays.

## What is supplied

Everything FD 8, D and DB list that is used here, and: the census (its sizes and its set-aside rule); the census and
labelled weightings, the take-by-take and holder weightings, the seeds and the order of running; the family of laws and
its swaps; the pair rule with its limit of eight sampled; rounds 1 to 4 for s; the readings, values both from X among
them; the five kinds of continuation, K′, the three families and their levels; K; the stage-2 counts and level; the
bounds on rounds and knots; the run sizes; the controls of the rate rule, the planted case among them (placed by hand,
read and never grown, counted toward nothing). **No take is supplied**: every take is sampled. The weightings are
supplied, and each has a swap (the holder weighting run reduced, the swaps of the law conditional).

## What a result would and would not show

- **Verdicts, three questions** (DC 6). A case is made only when X and Y are made patterns, the knots through which they
  meet are made by births, and the takes are sampled.
- **The scale.** About 135,700 sampled growths of at most 8 rounds under the take-by-take weighting in the census runs
  (under parity, MET at every start once and STEPS-1 at 2,000 starts; under not-all-equal, MET at 1,000 and STEPS-1 at
  120), 21,000 under the holder weighting, about 160,000 with the checks; about three and a half hours ("Runs"). His
  "statistically" suggests very many tries; these are many short growths from starts of at most five knots, under one
  release rule, and every bound is stated in those terms.
- **What the study can say and cannot.** It can say whether sampling, at this scale and under these weightings, makes a
  case met more often with Y (his "hit", read) and a candidate seen again; it cannot say whether a copier can arise only
  by such chance, or that none can.
- **What follows a case**, whether the two left are met and left twice again, is read only where DC 5.3 ("again in the
  same growth") reads it, and stage 2 (DC 5.2) reads only whether the pair of forms comes back in fresh growths.
- **A candidate seen again** would show, under one law and one weighting of takes, a made pattern that leaves two of
  each of at least two second-pattern forms it meets, more often with them than without, in fresh growths of the same
  start. It would not show a copier for a registered class, under every law or weighting, past 8 rounds or the census's
  starts; nor that a copier must appear (a statement about a weighting, and a rate is one).
- **The expected negative** would show the sentence of DC 4.5 for its bounded event ("No growth held a case that passes
  at 100. Under the [weighting], the rate of growths holding one is below [bound] at 0.95, each law separately. Smaller
  differences are not bounded.", or its form when some pass and none is confirmed), with the bounds of the table in
  "Runs": under parity with MET 0.090% under the census weighting and 0.14% under the labelled one; with STEPS-1 0.15%
  and 0.23%; under not-all-equal with MET 0.30% and 0.47%; with STEPS-1 2.5% and 3.9%; for all 84 laws at once, 7.4 in
  place of 3. Both halves of the power sentence go with it: a zero speaks, at best, of cases about ten points above a
  control near zero; near one half it takes about 18 points, and a true difference of that size passes at 100 about half
  the time. It would not show that no law, start size or weighting can make one: six-knot and larger starts, other
  taking rules, HOLD and STEPS-2 (conditional), every pair (conditional) and longer growths are not read, and if the
  conditional runs do not run, the registered "not run" sentence of "Runs" is part of the result.
- **Ticket A's values reading** would show, where a case is confirmed, that after a meeting a place of Y is tied to two
  loose made distinctions more often than with Y barred, with its way (through joining or through takes); in the
  scratch's two cases one of the two was Y's own in some continuations, so it would not show that X leaves two of it.
- **For the owner, plainly** (the advisor's sentences, with the numbers of the registered sizes): "No pattern was built
  for the main runs. Under each of 84 laws, small starts of three to five knots were grown: every start under parity
  with the first taking rule, and starts taken in one random order under the others. Every take was sampled under a
  stated weighting, and we counted. The controls use built starts and one planted case, and count toward nothing." "We
  expect to find no pattern that leaves two of what it meets more often than the law leaves two with the second pattern
  barred, or than the second pattern leaves of its own." "That would put the rate, each law separately and under the
  census weighting, below about 1 growth in 1,100 under parity with the first taking rule, 1 in 670 with the second, 1
  in 330 under not-all-equal with the first and 1 in 40 with the second, for cases that pass our test. Under the
  labelled weighting the bounds are about 1.6 times weaker. It would not show that no copier can arise by chance: these
  are about 160,000 short growths from starts of at most five knots, under one release rule." "One thing was seen in the
  scratch, in two of four cases under one law: after a meeting, a place of Y is tied to two loose made distinctions more
  often than with Y barred. In one case one was always made by X's births and one by Y's own; in the other, in about
  half. It happens as often when X and Y cannot join; takes were not blocked. With both required to be made by X's
  births, it does not pass. It is not a copier."
- **Four larger runs** exist ("Runs"); none is asked for; the one that could be asked for is not-all-equal with STEPS-1
  at every start, after R1d, and only if R1d shows a case confirmed against the barred controls.

## Starts and files

[starts_c.json](starts_c.json): the census (3,376 starts in the record's order, with the labelled weight and the parity
set-aside flag) and the drafter's scratch samples. The starts' stars follow from the rule in the file.
[cases_c.json](cases_c.json): the drafter's 96 scratch cases with their counts, for the gate, and its two values
comparisons at 1,000.

## Runs

**The owner's rule on compute** (25 November 2026): a run finishes in about an hour on at most 6 processes; a longer one
is cut to a prefix of its registered order and what was not run is reported as "not run". Every run below is sized from
costs measured at the registered bounds (8 rounds, at most 500 knots; "Known before the runs"). Every run reads its
starts in the order of DC 1.5, a prefix of one uniform permutation of the census; a run cut for time is cut to its
registered first half or first quarter (DC 1.5), and a run stopped anywhere else is reported as leaning toward fast
starts. Every run writes one record per sampled growth (start, law, knot law, weighting of takes, sample index, seed,
rounds read, stop, knots, the pairs with their forms and s, the pairs "wholly apart" removed, the rounds with more than
eight pairs, every case with its rates and way, the knot test), and is registered in `docs/LONG_RUNNING.md` with
`scripts/track.py long-add` under a memory cap.

**The main runs**, in their order of running, most valuable first, so that if the study stops early what has run is a
registered prefix of this list (the claim then says which were not run; m is counted over the main runs read):

| Order | Run | What | Starts (prefix of the order) | Laws | Takes | Growths or items | Measured cost | Minutes on 6 processes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | R0 | The gate: the census list against starts_c.json; the samplers' calls (`randrange`; `choices` by holders at the start of the round; a single candidate also calls); the pair rule; the seeds' tokens; the drafter's 96 cases of [cases_c.json](cases_c.json) at the scratch's bounds (6 rounds, 300 knots) and pair rule, with their counts of 20 continuations with Y and with X barred; its two values comparisons at the scratch's sample indices 1,000 to 1,999 with their masked counts (written afresh, the readings, pairs and samplers must give them again, or the difference is found and explained) | — | — | — | — | — | 5 |
| 2 | R0b | The controls of the rate rule (DC 4.7): the machinery control (made-4 and made-5, its own rule); the planted case's three arms (index 13 of cases_c.json, chance 0.5); the negative controls (made-2 under the six COPY-LAW laws; the two design cells where form was met; the ten MET form cases of the registered sample) | ticket A's designs (research/MADE-COPIER-20261125-001A/starts.json); cases_c.json | as said, parity | take-by-take | about 2 machinery cells, 3 arms, 18 negative controls; about 30,000 continuations | 0.01 s a continuation of these small growths (scratch) | 10 |
| 3 | R1b | The census, STEPS-1, parity (the runs where the scratch's cases were) | the first 2,000 | the 21 with STEPS-1 | take-by-take | 42,000 | 0.421 s a growth | 49 |
| 4 | R1a | The census, MET, parity | every start (3,344), once | the 21 with MET | take-by-take | 70,224 | 0.121 | 24 |
| 5 | R8 | The renamed starts, sampled (Lemma C-S1 at 8 rounds; it reaches 8 rounds and the guard): each start of three and four knots and each of its five renamings of R7, sample index 0, seed suffix `\|R8\|<renaming>` (`\|R8\|none` for the start itself); growths and pairs only; for each law and renaming, the share of growths with a pair, start against renamed start, two-sided Fisher exact at level 0.05/210; and one test for each renaming pooled over the 42 laws, at 0.05/5. R8 sees only large differences (under most MET laws about 6 growths with a pair in 219) | the 219 | the 42, parity | take-by-take | 55,188 | about 0.07 | 11 |
| 6 | R9 | The knot test at every round (D 8's swap of DC 8) on R1a's and R1b's growths of the starts of three and four knots (those in R1b's prefix), grown again from their seeds | the 219 | the 42, parity | take-by-take | about 7,000 (4,599 of R1a, about 2,750 of R1b) | about 0.05 | 5 |
| 7 | R2 | The swap of takes, parity, reduced | the first 500 | the 42 | holder | 21,000 | 0.108 (MET), 0.316 (STEPS-1) | 12 |
| 8 | R1c | The census, MET, not-all-equal | the first 1,000 | the 21 with MET | take-by-take | 21,000 | 0.449 | 26 |
| 9 | R1d | The census, STEPS-1, not-all-equal (the one cell the scratch never saw; its timing is the least sure, single growths up to 400 seconds) | the first 120 | the 21 with STEPS-1 | take-by-take | 2,520 | about 3.1 | 22 |
| 10 | R7 | The exact renaming check (Lemma C-S1): every history of rounds 1 to 3 with its chance as an exact fraction, where there are at most 30,000, else of rounds 1 and 2, or of round 1; the start against five renamings (knots and distinctions reversed; both permuted by `random.Random('C\|rename\|<start id>\|perm')`; the order of distinctions shifted by one, each label to the next and the last to the first; knots alone, `…\|knots`; distinctions alone, `…\|distinctions`); the class compared is the state up to renaming, birth record and barred marks included, by networkx's `weisfeiler_lehman_graph_hash` with 6 iterations on the graph of knots (attribute kind, round made and retirement), distinctions (attribute barred), places and parent links (edge attributes). Reported: checks, histories, checks with a single history (no check of takes), and checked histories holding a join of three or more parents, an implied birth, two taking births in one round, and a take with two or more candidates | parity: the first 6 three-knot starts in census order under 18 laws (the seven rations with CANCEL-OFFSHOOT under both taking rules, and FLOOR1 with CANCEL-RETIRE and CANCEL-WAIT under both), take-by-take; the first 2 four-knot starts under the holder weighting with MET, STEPS-1 under both weightings, and HOLD (7 each); not-all-equal: the 18 laws on the first 2 of the six three-knot starts | as said | every history | 108 + 14 + 36 checks | 35 process-seconds a three-knot check, 145 a four-knot one (scratch) | 20 |
| 11 | R3 | The confirmations (DC 4.4): for every case of a claimed reading that passes at 100 in the main runs read, 1,000 fresh continuations of each of the five kinds, in the main family (m counted before any confirmation); the reported readings in their own family | as the cases | as the case | as the case | about 5,000 continuations a case; by chance alone about 1% of some 1,900 cases (from the scratch's case rates) pass at 100 | 0.004 to 0.3 s a continuation | up to 30 |

In all about three and a half hours (about 214 minutes), against version 2's seven. The scale: about 135,700 sampled
growths under the take-by-take weighting and 21,000 under the holder weighting in the census runs, about 160,000 with
the checks R7, R8 and R0b besides. R4 (stage 2) runs only if there is a candidate.

**The conditional runs**, run only if a case of a claimed reading is confirmed in the main runs (the trigger; a case
that only passes at 100 does not fire it, since chance alone will pass some among the cases), with an error family of
their own at 0.01, in which the cases that pass only at the 300 swap belong:
- **R5**, the swaps of the law: HOLD for RELEASE (the 42) and STEPS-2 for STEPS-1 (the 21), parity, on the 219 starts of
  three and four knots and the first 300 five-knot starts of the order; HOLD with MET under not-all-equal on the 219
  (37,296 growths; 0.087 to 0.859 s a growth; about 47 minutes).
- **R6**, every pair (no sampling of pairs), and the first stage's swap at 300 continuations of each kind, on R1a's and
  R1b's growths of the 219 starts (about 15 minutes).
- **R4**, stage 2 for every candidate (DC 5.2), as before.
If they do not run, the claim registers: **"Not run: HOLD, STEPS-2, every pair. The negative is under RELEASE, MET and
STEPS-1, with at most eight pairs read a round; [n] rounds had more. The drafter's scratch on the starts of three and
four knots (unreviewed, 6 rounds) saw no case met more often with Y under those swaps."** ([n] from R1.)

**The bounds of the registered sizes** (each law separately, at 0.95, for the bounded event of DC 4.5: a case that
passes at 100 when none passes, otherwise a confirmed case, with m tying the growths together):

| Run | Census weighting | Labelled weighting |
| --- | --- | --- |
| R1a (parity, MET; every start once) | 3/3,344 = 0.090% | 3 × 120 / 256,561 = 0.14% |
| R1b (parity, STEPS-1; 2,000 starts) | 3/2,000 = 0.15% | about 0.23% |
| R1c (not-all-equal, MET; 1,000 starts) | 3/1,000 = 0.30% | about 0.47% |
| R1d (not-all-equal, STEPS-1; 120 starts) | 3/120 = 2.5% | about 3.9% |
| R2 (holder, parity; 500 starts, the 42 laws) | 3/500 = 0.60% | about 0.94% |

For all 84 laws at once, 7.4 in place of 3. **Power, both halves** (DC 4.4): a zero speaks, at best, of cases about ten
points above a control near zero; where the control is near one half it takes about 18 points, and even then a true
difference of that size passes at 100 about half the time. "Under not-all-equal STEPS-1 is read on 120 starts, once
each; the bound there is 2.5%, about thirty times weaker than parity's with MET."

**Larger runs**: four exist (not-all-equal with STEPS-1 at every start, about 10 hours; parity with STEPS-1 at every
start, about 1.4 hours once and 2.7 twice; not-all-equal with MET at every start, about 1.5 hours; R7 at every start of
three and four knots, days); none is asked for. The one that could be asked for is not-all-equal with STEPS-1 at every
start, after R1d, and only if R1d shows a case confirmed against the barred controls.

## Predictions

Marks, as in tickets A and B: **seen** (in the drafter's scratch runs, at their smaller bounds, with the starts, laws
and knot laws named), **by argument** (a settled statement), **implied** (follows from another prediction), **check** (a
check of the engine), **reported** (no prediction). Where a prediction is marked seen only in part, the part not seen is
named. PC3 to PC5 are about the main runs; PC13 and PC15 are about the conditional runs, if they run.

| # | Prediction | Mark |
| --- | --- | --- |
| PC1 | Under MET, for each of the 20 laws other than COPY-LAW(CANCEL-OFFSHOOT), each knot law and each start size, at most 10% of R1's growths have a pair; under COPY-LAW(CANCEL-OFFSHOOT), between 20% and 55% on five-knot starts and between 25% and 65% on three and four, under each knot law | seen (other laws pooled: at most 1.1% on each size; COPY-LAW(CANCEL-OFFSHOOT): five knots 36.4% and 36.7%, four 51.3% and 46.9%, three 36.8% and 44.7%) |
| PC2 | Under STEPS-1, for each law, at least 20% of R1's growths have a pair on the starts of three and four knots | seen under parity (33% to 91% by law); five knots and not-all-equal not seen |
| PC3 | No confirmed case of a claimed reading (form, from both, values both from X) in the main runs (R1a to R1d, R2), under any law, knot law or weighting: CC-1 not found, each rate given as its bound with the registered sentence (DC 4.5) | seen under MET (both knot laws, all start sizes sampled) and under STEPS-1 and the holder weighting under parity on three and four knots; not seen under STEPS-1 on five knots or under not-all-equal |
| PC4 | No candidate seen again: CC-2 not found | implied by PC3 |
| PC5 | Under MET, no form case is confirmed | implied by PC3; seen (92 cases at 100: none passes) |
| PC6 | Under COPY-LAW(CANCEL-RETIRE) and COPY-LAW(CANCEL-OFFSHOOT), with MET and with STEPS-1, every member of Y in a form or from-both case holds at most one loose distinction; under COPY-LAW(CANCEL-WAIT) the same is checked | by argument (four laws, C-S3); check (two laws) |
| PC7 | Under not-all-equal no values reading is met | by argument (C-S2) |
| PC8 | From both: no case passes at 100 (its Y-barred, masked and fully masked controls are empty, so only Y's own tests it) | seen (no case of from both in any scratch run) |
| PC9 | Ticket A's values reading (reported, its own family; DC 4.4's rule): under COPY-LAW(CANCEL-OFFSHOOT) and parity some cases pass at 100 against Y barred and Y's own; whether any is confirmed rests on the fully masked control, with no prediction; a confirmed one, if any, is "through takes", not "through joining" | seen in part (2 of 4 cases pass the first two at 1,000; masked 89 and 85 of 1,000 against 83 and 58; fully masked not run) |
| PC10 | R7: the distributions are equal in every check | by argument (C-S1); seen (version 1: 425 checks, 192 with a single history; version 2: 243 checks on three-knot starts and 84 on four-knot starts, 120 with a single history) |
| PC11 | R8: for each law and renaming (parity), the share of growths with a pair does not differ between the starts and the renamed starts (two-sided Fisher exact, level 0.05/210), nor pooled over the laws for each renaming (level 0.05/5): no rejection | by argument (C-S1) |
| PC12 | R2: on the 500 starts common to R1 and R2 (the first 500 of the order, sample index 0), summed over the 42 laws, fewer growths with a pair under the holder weighting than under the take-by-take weighting | seen (85 against 150, parity, three and four knots, index 0) |
| PC13 | R5, if run: no confirmed case under HOLD or STEPS-2, in the conditional family | conditional (decided only if R5 runs); seen under HOLD (parity, three and four knots); STEPS-2 not run |
| PC14 | R9 and every run: under not-all-equal no knot fails; under parity, joins fail in the round they are made in some growths (counts by law and class reported); the every-round test of R9 finds no failure the last-round test misses | seen (298 failures, all joins in their own round); the last clause by argument (Settled 7) |
| PC15 | R6, if run: no confirmed case with every pair either | seen under MET on three and four knots (the pairs were the same in 4,536 growths); not seen under STEPS-1, where 310 of 18,396 rounds had more than eight pairs |
| PC16 | R0b: the machinery control passes at 100 and at 1,000; the planted case's arm 1 passes at 100 and is confirmed, arms 2 and 3 do not pass; no negative control is confirmed | seen in part (machinery: 86 and 78 of 100 against 0; designs: none of 183 cells passes at 100; MET form cases: none of 92); the planted arms not run (a simulation of arm 1 at chance 0.5 on the pair's rates passes at 100 in 99.8% of trials) |
| PC17 | Reported, with no prediction: the rates of cases (any), of cases that pass at 100 and of one-history cases; q₁ at any round; each case's way and its masked rate (two-sided); the unmet-pair rate; the counts by form; "again in the same growth"; how many starts make F and meet G under the census weighting; the pairs that "wholly apart" removes; the rounds with more than eight pairs; every rate over growths with no failing knot | reported |

**What would overturn them**: one confirmed case of a claimed reading (PC3), under any law; one candidate seen again
(PC4); a check of R7 or a test of R8 that differs (Lemma C-S1 would then be wrong, and every rate would depend on the
numbering); a planted arm 1 not confirmed, or a machinery control that fails (the test would not see what it should); an
every-round failure that the last-round test misses (Settled 7 would be wrong).

## Stop rule

The ticket closes when the main runs are read, in their registered order; if it stops earlier, what has run is a
registered prefix of that order, and the claim says which runs were not run. Every confirmed case is reported with its
verdicts, its rates and its way, and fires the conditional runs; stage 2 (DC 5.2) runs for every candidate; a candidate
seen again goes to the advisor and the owner before any further claim. No law, weighting or reading is added after the
runs without a new registration. The later ticket of the claim's section 1 (two census starts joined at round 0) is not
designed here.

## What the advisor's passes changed

**The cold review** (version 1 to version 2; "freeze after listed changes", thirteen required):
- The rate rule: rates from continuations, passed at 100 and confirmed at 1,000 with a family-wise level; the masked
  continuations added; "needs" kept for none of 1,000.
- Lemma C-S1 written as its own lemma, with the state named and the guard read in the engines; the renaming checks
  widened (five renamings, both weightings, HOLD, STEPS-1, coverage counts).
- Values claimed as both from X only; ticket A's reading given its own verdict; the post-hoc choice disclosed.
- Y's form not X's form; C-S3's gap closed by argument for four laws and checked for two; every knot failure classified.
- Zero bounds by stratum, the labelled weights over the starts read, no bound on met pairs; CC-2 made definite.
- The words: the weightings named in full; "passes at 100", "confirmed", "a candidate seen again", "the unmet pairs".
- His "primordial soup", read as one supplied start, its mixed form left to a later ticket; the scale, "need" and what
  follows a case said. Then, for the owner's rule on compute, every run sized from measured costs to about an hour.

**The last pass** (version 2 to version 3; "freeze with listed fixes", twelve required):
- The fully masked kind added; a confirmed case must beat Y barred, Y's own and fully masked; its way reported; "needs
  the meeting" redefined; the change disclosed as leaning toward a positive.
- A planted case added to the controls (its chance raised from 0.30 to 0.5 so that arm 1 passes at 100); the machinery
  control given its own rule; the claim says that no positive control made by the growth exists.
- Zero bounds on a prefix are 3/N whatever K; runs cut for time only to registered halves or quarters; the bounded event
  named; both halves of the power sentence.
- Main and conditional runs, with the trigger "a case of a claimed reading confirmed" and a family of their own; the
  registered "not run" sentence; about three and a half hours in all, most valuable first.
- C-S1's citation, step (c) and the allowed wording; R7's hash and exact fractions; Settled 7's sentence on takes; C-S2
  reworded; "not of the others" by growths; the predictions and the owner's sentences rewritten; the words fixed.
