# Two countings of a structure's allowed states, side by side: pre-registration

Ticket `TWO-COUNTINGS-20261125-001A` of epic `TWO-COUNTINGS-20261125-001` (sub-goal B324; assumptions A240, A71, A73,
A110, A185, A239; goals G17 with G18). The engine is written by a helper who has not seen the drafter's prototype, from
this text ("PR"), [the claim](../TWO-COUNTINGS-20261125-001/claim.md), [the definitions](../TWO-COUNTINGS-20261125-001/definitions.md)
("TD"), [the knot-test finding](../TWO-COUNTINGS-20261125-001/knot_test_finding.md), [the table](../TWO-COUNTINGS-20261125-001/table.json),
the shared definitions ([SD](../RING-IN-BALANCE-20261123-001/definitions.md)) and those of the study of parts that meet
again ([FD](../PARTS-MEET-AGAIN-20261124-001/definitions.md)), and the data files beside this text: [structures.json](structures.json)
(33 structures), [construction_orders.json](construction_orders.json) (1,200 orders), [census_index.json](census_index.json)
(100 census starts). It may import read-only the fold study's engine and knot test
([pm.py](../../experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py),
[knots.py](../../experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/knots.py)), the
canonical checker in `tools/knotlab`, and the archives named below. The canonical K1–K3 test is unchanged. No claim is
made about physics, physical space or time, living things or minds.

**Frozen on 2026-11-25 (UTC), after the advisor's two passes and before the study's code is written.**

## The question

The owner, 23 November 2026 ([decision note](../SETTING-AS-REREAD-20261123-001/decision.md), line 4): "random can have
any combination of settings and starting positions." Asked which counting that means
([his answers](../TWO-COUNTINGS-20261125-001/owner_request.md), lines 33–35 and 53–54), he answered first that "Our
reality, is random. It's not chosen", and then: "I'm not sure, this is one of those, we can pursue whichever is most
interesting and document the choice as reversible in the future if it unlocks some ability later." Neither counting
is his. By his answer on this fork the thread takes counting from the finish as its working choice, reversible; not
tested here (A240). This ticket reports every count under both countings, side by side, and registers what would
reverse the choice (claim, section 9). The filed stop: the table of the record's weighted statements under both
countings, and a law that decides the counting or a reason none of the recorded laws does (the reason is in the
claim, section 6, by argument).

## In standard terms

The literature's words. A constraint network grows by adding constraints with new variables. Two distributions on its
solutions: the uniform distribution on the final solution set, and the sequential distribution (uniform on the initial
solutions, each solution's mass then split equally among its extensions at each step). They agree exactly when every
extension count is constant (the record's theorem). On a CHSH test whose settings are added constraints, the
sequential distribution with a start before the settings, under the lemma's hypotheses, is a local hidden-variable
model (measurement independence holds by construction); the uniform distribution on each final network is a model
with measurement dependence (post-selection).

## Prior work in the program

Searches, each with `--until 2026-11-25 --exclude TWO-COUNTINGS-20261125-001`, run read-only on 25 November:

`python3 -B scripts/track.py objects "uniform weighting of the finished structure against equal division of each old word among its completions" --until 2026-11-25 --exclude TWO-COUNTINGS-20261125-001`

Top rows: UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001 (used: the agreement theorem), REVIEW-LEADS-20261123-001
(row 7, a relative), PARENTS-FROM-HOLDERS-20261124-001 (unrelated object).

`python3 -B scripts/track.py objects "hidden four-correlation excess with births as settings under the control weighting" --until 2026-11-25 --exclude TWO-COUNTINGS-20261125-001`

Top rows: THIRD-HOLDER-20261123-001 (used), REVIEW-LEADS-20261123-001 (used: row 4), FOUR-READINGS-20261120-001 (a
relative: one common weighting, bound 2).

`python3 -B scripts/track.py objects "whether a growth law fixes the weighting of allowed states" --until 2026-11-25 --exclude TWO-COUNTINGS-20261125-001`

Top rows: REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001 (used: its round-1 gains and rule R's parts), READ-ORIGIN-20261120-001
(a weighting of starts: unchanged by the counting), SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001 (squared amplitudes:
outside both countings).

The record has run the two countings side by side in at least ten studies (the table's rows marked "from the record").

Epics of the top three rows of each search: `UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001`, `REVIEW-LEADS-20261123-001`, `PARENTS-FROM-HOLDERS-20261124-001`, `THIRD-HOLDER-20261123-001`, `FOUR-READINGS-20261120-001`, `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`, `READ-ORIGIN-20261120-001`, `SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001`.

## Prior work outside the program (from memory; not checked)

Pearle (1970), Garg and Mermin (1987) on post-selection; Hall (2010, 2011), Barrett and Gisin (2011) on measurement
dependence; Wharton and Argaman (2020) on weightings over whole histories. Uniform sampling against random sequential
construction of a combinatorial structure is folklore. What this adds: the comparison on the program's grown knot
structures, the settings read as births, the order classification, and the knot test in the whole structure on the
line's structures.

## Known before the runs (disclosed)

From the drafter's prototype (not this study's engine), exact rationals unless said.

1. The 11-knot structure, option pair (x2, x3) against (y2, y3): counting from the finish 20/9, hidden; from the start
   2, hidden. The other eight option pairs: 19/9 or 37/18 against 2. (s1, s2) moves by 1/3 from the finish, not at all
   from the start (it is in no record).
2. The smallest gain of ONE-PARENT-REREAD-20261123-001A: from the part and from after the rule-Q round, 2 hidden; from
   the finish, 61/30 hidden.
3. THIRD-HOLDER-20261123-001B's 7-knot (19/9), 8-knot (20/9) and pencil 9-knot (20/9) structures: 2, hidden, from the
   start.
4. The 512 sign assignments of the 11-knot structure's nine parity knots: 128 give the hidden 20/9 from the finish
   (the record's count); all 512 give 2, hidden, from the start (557 s on one process, both countings).
5. A keyed setting on the 11-knot structure (all 16 functions g): the second record changes by up to 2/9 from the
   finish (pooled), by 0 from the start.
6. The order classification on `eleven_registered_400`: 104 orders have both setting knots bringing only their own
   fresh distinction for both settings; all 104 score 2 and are hidden (all 104 lose weight at other knots, equally
   across the setting pairs). Of the other 296: 182 at 2, hidden; 66 above 2, hidden (largest 104/45, order 11); 48
   above 2, not hidden. This order classification was defined after the first version's runs and the advisor's review.
7. The examples of TD 8.2, from the start: E0 2; E1 20/9 hidden; E2 104/45 hidden; E3 7/3 (renormalised), second
   record changed by 1/6; E4 17/6, both records changed by 1/3; E5 11/4 (renormalised), first record changed by 1/4;
   E6 5/2, first record changed by 1/4; E7 5/2, first record changed by 1/4, no weight lost. E1 breaks the premise and
   E2 also breaks h4's first clause, so neither is a single break. Two other h2 candidates (nae(x1, x2 or x3, w), w = h1
   or h2) lose weight equally across settings and give 2.
8. **The whole-stage 9/4**, classified from its record, no compute: outside the lemma's form, its settings being edits
   adding a loose distinction to a named holder ([decision](../WHOLE-STAGE-SETTINGS-20261120-001/decision.md), line 27);
   it fails the analogue of h3′ ("Ordinary growth funds the round exactly when x=u and y=v ... Otherwise the entire
   round stalls", ibid.), so what one side's setting adds, including every birth it causes, depends on the other's; its
   start types are equally weighted and their states uniform for every setting pair
   ([pre-registration](../WHOLE-STAGE-SETTINGS-20261120-001/preregistration.md), line 21); the same under both countings
   (parity).
9. The knot test in the whole structure ([finding](../TWO-COUNTINGS-20261125-001/knot_test_finding.md)): the 11-knot
   structure's two four-place parity rules fail K2 (in all 512 sign assignments); the smallest gain's first setting knot
   fails K2 at a = 0; the 8-knot structure's even(y1,y2,y3,s1) fails K2; the 7-knot, pencil 9-knot and 18-knot
   structures pass (the 18-knot by projection only). The canonical checker agreed with projection on 287 knots.
10. The agreement census, 3 rounds, 19 three-knot, 200 four-knot and 300 sampled five-knot starts: under parity no growth
    parted. Under not-all-equal, of the starts that make a birth, the countings parted by round 3 on every one except 2
    four-knot and 3 five-knot starts under RING-LAW (their births one-input or forced); the prototype left undecided 0
    to 25 growths per law and size (25 at most, RING-LAW on five knots).
11. P9 timing pass: the counting-from-the-start pair table of a FREEDOM-CLOCKS-C type of width 7 to 16, by enumeration,
    took 0.0 to 1.6 s (12 types); no verdict was computed.
12. Canonical checker timing pass (as a helper would run it, one command per knot, load 10): 0.14 to 0.25 s per knot at
    16 distinctions, 0.83 s at 18; the 287 knots of the structures of at most 20 distinctions took 57 s on one process.
    The thread has seen single checks of 16 to 18 distinctions take over a minute each under heavier load; part 8 is
    sized for both.

## Settled by construction (engine checks, not predictions)

- No pattern the growth makes depends on the counting (value-blind laws).
- Renaming carries both countings; factorization of a round; counting from the start keeps earlier weights; parity
  births with a fresh distinction keep the two countings one.
- Under the lemma's hypotheses the score is at most 2 for any class of outcome functions and exactly 2 when the class
  contains a constant.
- The ceiling of THIRD-HOLDER-20261123-001A is 2 at ratio 1.
- The agreement rule of TD 7.3 on 100 census starts (part 9).

## What is supplied

The countings; uniform weight on a start's states; hand-built structures as their own starts (construction orders as
a disclosed swap); equal division at a birth (its swap is the other counting); ν uniform in pooled rows; each study's
settings, observers (a supplied list of distinctions; nothing observes), records and outcome classes; the laws; the
census starts and rounds. Every weighting here is supplied; each table row says whether its structure was grown by a
law or written by hand.

## What a result would and would not show

- Would show which of the record's weighted statements found by the listed searches change between the two countings,
  and by how much, side by side; that table is what makes the working choice cheap to reverse.
- Would test the lemma on every registered setting structure and on one example per hypothesis, and list which rules of
  the line's structures are knots in the whole structure (correction candidates).
- Would not show which counting is right, or anything of the owner's picture beyond his answers; would say nothing
  about physics.

## The run (one run; registered order; each part capped; a cut part reports its prefix, and a prediction on a cut part
is judged on the prefix and marked cut)

| Part | Items | Time (measured unless said) |
| --- | --- | --- |
| 1. Gates | brute-force enumeration against the engine's own method on the 11-knot and smallest-gain structures; Known 1–3 reproduced | under 1 min |
| 2. Lemma tests | 11-knot, 9 option pairs (TD 4.1); smallest gain at its 3 stages; 7-, 8-, pencil 9-knot; 18-knot, its 512 start states enumerated exactly (SAT with blocking clauses), completions per setting pair; the two 10-knot starts with their three rule-Q births made by Q-ALL (every third-birth choice; pooled and per history); REVIEW-LEADS-20261123-001C's 8/3 case as written in its [results draft](../REVIEW-LEADS-20261123-001C/results_draft.md), line 74; the 8 gaining parts and all 27 parts with laws handed out of ONE-PARENT-REREAD-20261123-001A at their gaining choices, from `artifacts/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/census_gains_c_*.jsonl.gz`; rule R's 7 three-holder parts of REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C from `artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/`; keyed settings on the 11-knot (16 g) and 18-knot (256 g) structures; both countings, every common stage, both outcome classes (TD 4.4) | 11-knot pairs about 8 s; the 18-knot, 10-knot, 8/3 and keyed parts estimated at seconds to a minute each; the 35 parts estimated 5 min; cap 15 min on six processes |
| 3. The 512 sign assignments | 512 × 4 finished structures, both countings, all two-valued functions; split over six processes | 557 s on one process; about 2 min on six |
| 4. Examples | E0–E7 of TD 8.2 | under 30 s |
| 5. P9 | FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C's 194 not-all-equal types (definition: [results](../FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C/results.md), lines 3 and 7, and its table at line 17; data: `artifacts/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C-E001_pair_births/census_cases.json.gz`, entries with first status "births", 183, and `disconnected.json`, 11): each type's stage counted from its source (one round), the pair table of weights of disagreement, and whether two types with one table have different next birth counts (`next_birth_count`), named and under one consistent renaming as the record compares | 0.0–1.6 s per type of width at most 16 (timing pass); 9 types of width 23 to 64 by an exact elimination method, unmeasured; cap 15 min on six, in archive order |
| 6. Order classification | the 1,200 orders of construction_orders.json (two lists for the 11-knot test, one for the smallest gain) | 0.3 s per order; about 1 min on six |
| 7. Grow again | the smallest gain's part and the first 10 starts of census_index.json, each under its 4n renumberings (TD 7.1), grown under Q-OLDEST and Q-NEWEST through 3 rounds | estimated 3 min on one |
| 8. Knot test | projection (`check_knot` on the induced relation) on every structure of parts 2–4, duplicates removed (about 3,000 structures, most from part 3); the canonical command on every knot of the 33 structures of structures.json of at most 20 distinctions and of the finished structures newly built in part 2 of at most 20 distinctions, in this order: the 11-knot, 8-knot and smallest-gain structures, then structures.json order, then part 2's; no knot test on census growths | projection about 1 min; canonical checks at the measured 0.2–0.8 s per knot, 287 knots for the 33 (57 s on one) and an estimated 2,000 to 6,000 for part 2's structures (about 5 to 10 min on six); cut: new structures are not started after 20 min of wall time, the rest marked "canonical check not run (cut)" with their projection verdicts kept |
| 9. Engine check | the agreement rule of TD 7.3 on the 100 starts of census_index.json, the six laws, both knot laws, 3 rounds; counts reported | 0.13 s per growth, 1,200 growths, about 3 min on one |

**Total on six processes**, at the measured rates: about 20 minutes (parts 2, 5 and 8 dominate). With every cap reached
(15 + 15 + 20 min and the rest), at most about 60 minutes. No exception is requested.

## Predictions

Marks as the advisor set them: replication of scratch, replication of the record, by argument, real. Engine checks are
listed apart (above).

| # | Prediction | Mark | Fails when |
| --- | --- | --- | --- |
| P1 | Counting from the finish reproduces every recorded number of parts 2 and 3 | replication of scratch on Known 1–4; replication of the record elsewhere | a number differs |
| P2 | The structures of part 2 not yet measured meet the hypotheses of TD 9, and every structure of parts 2 and 3 that meets them scores at most 2 for both outcome classes (exactly 2 over all two-valued functions) with both records hidden. Verdict per structure: hypotheses met and at most 2 / hypotheses met and above 2 (the lemma or the engine is wrong) / a hypothesis fails (which one, score reported) | by argument; real only for "the unmeasured structures meet the hypotheses" | a structure meets them and scores above 2 |
| P3 | Each example E1–E7 gives a score above 2 or a record changed by the other's setting | replication of scratch | an example gives 2 and hidden |
| P4 | Every order of part 6 in which both setting knots bring only their own fresh distinction, for both settings, scores 2 and is hidden | replication on the 400; by argument on the 800 | one such order scores above 2 or is not hidden |
| P6a | Under Q-OLDEST or Q-NEWEST, some renumbered start of part 7 grows a finished structure that differs from the one grown from the start as given, after carrying the renaming back | real | every renumbering grows the same finished structure |
| P6b | Where the finished structures are the same after carrying the renaming back, counting from the start gives the same weighting carried back; where they differ, "no comparison" | by argument (an engine check) | a weighting differs on the same structure |
| P7 | The 10-knot 55/27 becomes 2 counted from the start, per history and pooled | by argument | not |
| P8 | The two four-place rules of the 11-knot structure fail K2 in all 512 sign assignments, and the 128 at 20/9 are exactly those whose ties between x2 and x3 and between y2 and y3 are inequalities | replication of scratch | otherwise |
| P9 | The counting-from-the-start pair tables decide the next birth count on all 194 not-all-equal types, named and under one consistent renaming | real | two types with one table and different next birth counts |

Engine check in place of the first version's census prediction: for each growth of part 9 the verdict is the first round
whose product (TD 7.3) varies, decided exactly; later rounds report the total-variation distance between the countings
only; counts by law and knot law are reported. A failure is a bug.

## Stop rule

The nine parts in order, each capped; the study stops when they are done or cut. Reported: the table (both columns,
every row marked, the knot column), the lemma's verdicts, the examples, the order classification, P9, the grow-again
table, the knot-test table with the correction candidates, and the engine checks. Nothing is tuned after values are
seen; a changed definition is reported with both versions; deviations go in `deviations.md` of the experiment family.
Results are referee pending.

## Words

Counting from the finish; counting from the start; counting from stage s (a common stage); counting (the rule) and
weighting (its result); lost weight; change from the other's setting; start with its states; the first and second
observer (each a supplied list of distinctions; nothing observes); value-blind (the record has "flip-blind"); decides
the counting; keyed setting (the record's phrase; second candidate "a setting set by old values"). Proposed for the
glossary, for the owner's glossary pass: "weighting" extended from meeting patterns to states and histories.

## Later tickets, named and not designed

- The smallest gain of the rule-Q line among structures whose every rule is a knot in the whole structure: reopened,
  since the search winner's setting knot at a = 0 is not a knot there.
- A rule-Q birth that is not a knot in the whole structure: an observation about that law, to be classified on its own.

## What the advisor's passes changed

**The cold review: "Redesign smaller: one ticket, minutes of compute", ten required.**
- The lemma's hypotheses corrected (h0, h1′, h3′, h4 added); the whole-stage 9/4 classified.
- The order classification registered and checked on existing output; the first version's diagnosis of the orders was
  wrong and was replaced.
- The knot-test finding reported, with correction candidates and later tickets.
- The claim's fifth part split: the pattern statement settled, the restatement marked, the limit verdict removed and the
  limit parked.
- The table compiled from the record with fresh rows; the countings renamed; "far", "preparation" and "law" for a
  distribution replaced.
- The census run, the fair-reveal swap, the numbering run (but for "grow again") and three exception requests dropped.

**The last pass: "Freeze with the listed fixes; no further round", eight required.**
- Part 8 re-scoped (projection on all; the canonical checker on the 33 and new finished structures of at most 20
  distinctions); the 512 given their own part; the fifth part cut to P9; the total restated from a timing pass.
- The lemma: the record clause of h4, h1′ for two setting stages, the lost-weight rule, the lemma for setting knots
  only with the 9/4 apart, the old P10 moved to Known, two examples marked as not single breaks.
- The hypotheses in checkable form (TD 9); P2's three-way verdict.
- The orders and census starts shipped as data; the renumberings, option pairs, functions g, score methods and paths
  given in full.
- Prediction marks as the advisor's table; P5 an engine check with first-parting verdicts; P6 split.
- The reversal readings: one tested and not met, one defined against the 9/4, one tied to an event, one made
  one-directional; the two reasons merged with their cost; "not evidence for the choice".
- The knot-test finding narrowed ("a failing rule is not necessary for one"); the 18-knot pass marked by projection
  only; the knot column and the carried sentence added; the table's sweep sentence; the claim retitled.
