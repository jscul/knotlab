# Deviations and readings, MADE-COPIER-20261125-001C-E001

Written by the engine's author, a helper that has not seen the drafter's prototype or its outputs (the scratch folder
named in PC, "Known before the runs") or the epic's `advisor/` folder. The frozen texts (PC, DC, the claim, D, DB, FD,
SD) and the two data files match the SHA-256 sums of `contract.json`; this was checked before any code was written. The
fold engine (`pm.py` `3aa69b5b...`, `knots.py` `9138ae86...`, `paired.py` `70a691de...`) and ticket A's `mc.py`
(`c7891c8d...`) are imported unchanged; every run records their sums.

Citations: "PC" the pre-registration; "DC s.i" ticket C's definitions; "D", "DB", "FD" and "SD line n" as in DC. Each
item says where the text leaves a choice, the reading taken (the one closest to the letter), and the runs it affects.
Items 1 to 34 were written before any registered run (before the gate R0); each later item says when it was written.

## The engine

1. **The growth is the fold engine's**, `pm.Run` with its `round_step`, called with a chooser (`ctx['chooser']`) for
   every take; the law's own choice rule is never used (every take of MET and STEPS-1 goes to the chooser, FD 2.4).
   The states after each round are kept by reference: `pm.Run` copies the state before every round and never changes
   one afterwards (only its member cache `cand` is pruned when a roster is read, which changes nothing read).
2. **The guard** (DC 1.5, "DB 3.9's rule"): `pm.GUARD`'s limits are multiplied by ten at import, as DB 3.9 says; the
   fold engine's file is unedited. A round the guard stops is not read (the engine's own stop).
3. **The fully masked kind (DC 4.1).** The fold engine gives no hook to remove candidates before the take. At import
   this engine replaces the module attribute `pm.take_candidates` by a wrapper that calls the engine's own function
   and returns its lists unchanged, except while a fully masked continuation grows: then, for a birth with a parent in
   X and its descendants, every candidate held at the start of the round by a knot of Y and its descendants is
   removed, and the reverse. The sides are the fold engine's mask sides (FD 4.2, extended in each round's demand step
   by every new knot with a parent on a side, so at a round's takes they are the sides at the start of that round). A
   birth left with no candidate makes no take and no call. The file `pm.py` is not changed. Tested: inactive, the
   wrapper gives growths equal to the engine's own function (test_mcc.json).
4. **The holder weighting** reads h, the number of holders of each candidate at the start of the round, from the
   state after the previous round (the engine forms takes before any knot of the round is made, so it is the same).
5. **Seeds under the holder weighting.** DC 1.4: "under the holder weighting `|T2` is put last of all". Reading: the
   growth's seed ends in `|T2`; a continuation's seed is the growth's seed without `|T2`, then `|<kind>|<s>|<i>`, then
   `|T2`. The pair sampling's seed is DC 2.2's literal `<the growth's seed> + '|P|<s>'` (the growth's seed with its
   `|T2`). Affects R2 only.
6. **The pair rule (DC 2.2).** The lexicographic list of ordered pairs is in the order of (X's smallest member, Y's
   smallest member), which is the order of the parts' indices in the roster (parts are sorted, disjoint). With more
   than eight, `random.Random(<seed> + '|P|<s>').sample(pairs, 8)` on that list; the eight are then put back in that
   order (the order changes no seed and no reading). "Removed by wholly apart": ordered pairs with X made, Y another
   part, in the same class. **The scratch's rule** (gate R0 only, PC "Known before the runs": "the first eight parts
   by name, at most eight pairs a round"): the first eight parts in order of smallest member; among them the ordered
   pairs with X made and wholly apart, in lexicographic order; the first eight.
7. **A made pattern** (DC 2.1): every member made after round 0 (`made > 0`).
8. **The meeting round** (DC 2.3, FD 4.3): the first round t > s after which some member of X and its descendants and
   some member of Y and its descendants lie in one part (a member of both counts). Sides are kept round by round from
   the birth records (FD 4.2: a new knot is on a side when a parent is).
9. **The roster read for readings and pairs** is the fold engine's roster with no mask: members with h and k
   (`pm.live_members`), met sets (`pm.met_sets`), maximal met sets (`pm.maximal_sets`), parts as the components of
   joinable (two members in one maximal met set). The groups (cliques) are not formed for a roster that is only read,
   so the guard's clique and group counts are not taken there; its incidence and pair counts are. Tested equal to
   `pm.roster_of` (members, h, k, maximal met sets, parts, classes) on 417 states (test_mcc.json).
10. **Readings in masked continuations** are read on the structure's own roster, with no mask: DC 4.1 and FD 5.6 put
    the mask "in the round and in its demand step" only.
11. **Ties (parity) read birth by birth.** D 3.3 reads ties by a basis of the allowed states. Under every law of the
    family (parity, IMPLIED), by S1 and S3 (D 6.1, 6.3; PC, Settled 7) a made distinction is tied to an existing place
    v exactly when it is the one fresh distinction f of a birth not implied and the sum of that birth's inputs and v
    lies in the span of the rules before its round; the tie then holds at every later round. The engine reads ties so
    (canonical residues over the fold engine's span), and the eligible places of Y (free, tied to no place of X after
    round s) by the same residues over the rules after round s. Checked against `mc.ties_parity` (a basis of the
    allowed states) on every round of 60 sampled growths: 15,819 checks, no difference (test_mcc.json). The values
    readings of the gate's two comparisons and of every case are also so read.
12. **The values readings with three or more** usable loose made distinctions tied to one v: "both from X" when at
    least two of them are descended from X only; "one from both" when at least one is from X only and one from both;
    "both from both" when at least two are from both; ticket A's reading when there are at least two and at least one
    is from X only or from both (ticket A's dev 8); Y's own when at least two are from Y only. A made distinction's
    descent is its maker's (its one holder while it is loose).
13. **Y's own in values** (DC 4.2, D 3.5) is read on the same places of Y as the reading (free, tied to no place of X
    after round s), the places D 3.3 names.
14. **Values under not-all-equal are not read** (DC 3.2: values both from X "under parity only"; the reported values
    readings "the same"). PC7 is checked instead on every not-all-equal growth of the main runs: the tie classes of the
    structure at its last round read are computed (`mc.ties_nae`, every claimed tie confirmed by a solver); by S1 two
    distinctions tied at some round are tied at the last, so no tie class at the last round means no values reading
    at any round.
15. **The knot test (DC 8)**: every knot of a growth at its last round read: parity by both methods of the fold engine
    (`knots.parity_test`); not-all-equal by the fold engine's `test_run` at the last round (the birth method on every
    made knot, start knots directly, and the direct test on every knot of at most 12 places). In a continuation the
    knots made after round s are counted (by Settled 7 a knot's verdict is fixed in its round, and the knots made by
    round s are the growth's); under parity the test is of the whole structure. A failure is dated by its round made
    and classified by kind, number of parents, whether it took a distinction (step 5′), whether its birth was implied.
16. **Levels.** "A test at level α" passes when its p-value is at most α.
17. **Form, Y's form and "the same"** are SD lines 29–30 as the fold engine reads them (`paired.roster_graph`): a
    graph of members coloured by (h, k) and one vertex per maximal met set in the part, compared by exact isomorphism
    after cheap invariants. "Containing a member made after round s": `made > s`.
18. **Cases.** A pair is a case of each reading (form, from both, values both from X; and the reported values with one
    from both, both from both, ticket A's) that is met at a round t at or after its meeting round in the growth; one
    case per pair and reading. A growth "holds a case" of a reading under a law when any of its pairs is one.
19. **The first stage's events (DC 4.3).** q₁: in the continuation with nothing barred, the reading met at a round at
    or after the continuation's own meeting round (none: not met); q₁ at any round reported. q₀: with Y barred, met at
    any round after s. q_Y: with X barred, Y's own of the reading's kind (form kind for form and from both; values
    kind for the values readings) at any round after s. q_M, q_T: masked and fully masked, met at any round after s. A
    continuation stopped by the knot bound, the guard or a residual stall is read through its last round read.
20. **The unmet pairs (DC 4.6)**: a pair with no meeting round by the last round read; its reading counted when met at
    any round after s.

## The controls of the rate rule (R0b)

21. **Bounds.** R0 runs at the scratch's bounds, as PC says. R0b, whose bounds PC does not state, runs at the registered
    bounds (8 rounds, at most 500 knots, DC 1.5), those of the main test it controls.
22. **Level of a control's confirmation.** The controls count toward nothing (DC 4.7) and are read before m exists; each
    is confirmed, or not, at level 0.01 (a family of its own), with every p-value reported, so that 0.01/m can be read
    once m is known.
23. **The seeds of the design cells** (made-2, made-4), which DC 4.7 does not give: the machinery control's form,
    `C|A|<design>|<ration>|<treatment>|<taking rule>|parity|0`, with the taking rule always written (`MET` or
    `STEPS-1`); continuations as DC 1.4 (the growth's seed then `|<kind>|<s>|<i>`). X, Y and s = 1 are the design's
    (ticket A's starts.json).
24. **The readings of the negative controls.** The design cells and made-2 are read in the claimed readings (form, from
    both, values both from X). On made-2 Y's form is X's, so the form reading, which requires Y's form not to be X's
    (DC 3.2), is never met there; the form reading without that condition ("two parts of Y's form, every member from X
    only") is also read on made-2 as a control row and must not be confirmed either. The ten scratch MET form cases are
    read in the form reading.
25. **The planted case (DC 4.7).** The growth of index 13 is regrown at the registered bounds and the pair taken as
    listed after round 3 (checked: X and Y are those parts). Each arm reads the form reading (and Y's own form kind) at
    100 continuations of each of nothing barred, Y barred and X barred (i = 0 to 99), and then 1,000 further of each of
    the five kinds (i = 100 to 1,099); arm 2 places into every kind, the masked kinds included. Whether a continuation
    is placed is decided by `random.Random(<its seed> + '|PLANT').random() < 0.5`; r is its meeting round if it has
    one, else the growth's (4); the placed state is read once, at round r, and its readings are added to that round's.
    "Arm 1 must pass at 100 and be confirmed": confirmed at level 0.01 (item 22). "Arms 2 and 3 must not pass": not
    pass at 100; they are also read at 1,000 and reported.
26. **The machinery control.** The event (Y's own values, both from Y only) at any round after s in each of the
    continuations with nothing barred and with Y barred; one one-sided Fisher test at 0.01 at i = 0 to 99, and one at
    i = 100 to 1,099.

## The runs

27. **"Fails when".** The brief and the contract judge each prediction by its "Fails when" entry; PC's table of
    predictions has no such column. Reading: each prediction fails when its statement, as written in PC's table, is
    false on the runs read; a prediction about a run not run is "not run".
28. **R8's starts.** PC's R8 row reads "each start of three and four knots ... the 219" with 55,188 growths (219 × 6 ×
    42), under parity; three of the 219 are set aside under parity (DC 1.1). Reading: R8 runs on all 219, as its row
    says, and its tests are also reported on the 216 not set aside.
29. **R9's growths.** PC's R9 row counts "4,599 of R1a" (219 × 21); R1a has growths only of the 216 three- and
    four-knot starts not set aside (4,536). R9 regrows those, and R1b's growths of the three- and four-knot starts in
    R1b's prefix.
30. **R7's renamings**: "reversed": knots in reversed order and distinction labels in reversed order (label of rank j
    to the label of rank n − 1 − j); "perm": `rnd = random.Random('C|rename|<start id>|perm')`, the knot order
    shuffled by `rnd.shuffle` and then the labels by `rnd.shuffle` on the sorted labels; "shift": each label to the next
    in sorted order and the last to the first; "knots": the knot order alone shuffled with
    `random.Random('C|rename|<start id>|knots')`; "distinctions": the labels alone with `...|distinctions`. The names
    in R8's seeds (`|R8|<renaming>`) are `none`, `reversed`, `perm`, `shift`, `knots`, `distinctions`.
31. **R7's four-knot checks, "7 each".** PC: "the first 2 four-knot starts under the holder weighting with MET,
    STEPS-1 under both weightings, and HOLD (7 each)". Reading: seven checks a start, under FLOOR1 with
    CANCEL-OFFSHOOT (COPY-LAW(CANCEL-OFFSHOOT), the fold study's name, not a law of copying): (holder, MET), (take by
    take, STEPS-1), (holder, STEPS-1), and HOLD with each of (take by take, MET), (holder, MET), (take by take,
    STEPS-1), (holder, STEPS-1). The class compared is the Weisfeiler–Lehman hash (6 iterations) of the graph PC
    names; two distributions are equal when they give every class the same exact chance.
32. **The counts by form (DC 7)** key a form by its invariants (members, (h, k) of each, sizes of the maximal met sets)
    and the Weisfeiler–Lehman hash of its graph; two forms with one key are counted together. Every reading uses exact
    isomorphism (item 17).
33. **The zero bounds by stratum (DC 4.5).** A stratum's bound is 3/N with N its starts read (every start read once, or
    a prefix of the order, whose restriction to a stratum is a uniform sample of it without replacement); under the
    labelled weighting multiplied by max w / w̄ over the stratum's starts read.
34. **PC6's "holds at most one loose distinction"**: h + k of each member of Y after round s (usable and barred loose
    distinctions).

## After the gate's first pass (written before its rerun; nothing else had run)

The gate's first pass (census, order, round-0 ties, the 96 cases, the two values comparisons) agreed on the census,
the order, the set-aside flags, the labelled weights, the round-0 ties, and, for 95 of the 96 cases, s, X, Y, the
meeting round, the round met and the count of 20 with Y barred. Three things differed; each was found and is explained
here. No reading of a registered run is changed by them.

35. **The scratch's count of 20 with X barred, for form cases, is not DC 4.2's Y's own.** In 26 form cases my count
    (DC 4.2: two parts the same as Y's form, each containing a member made after round s, **every member descended
    from Y only**) was lower than the listed one. Every listed count of the 92 form cases, the 26 included, equals the
    count of continuations with two parts of Y's form of **any descent** (each containing a member made after round s):
    in these cases the second part of Y's form came from a third part's line ("neither"). The registered runs read DC
    4.2's event, as frozen; it is stricter than the scratch's, so q_Y is lower and a case passes the X-barred comparison
    more easily (it leans toward a positive). The gate lists both counts for every case (`gate_R0_case_listing.json`)
    and labels the class `yform_any` (reported in the gate only). The values cases' counts agree with DC 4.2's event.
36. **Case 87 of cases_c.json is listed as a form case, but its Y's form is X's form**: X = {11, 12} and Y = {13, 14},
    each two members holding two usable loose distinctions in one met set (the two-knot part), on `n5-g47-21201` under
    FBP(CANCEL-RETIRE), parity. DC 3.2's form reading requires Y's form not to be X's, so it is not a case here. Under
    the form reading without that condition it is met at round 6 with meeting round 4, as listed. PC's sentence "None
    has Y's form the same as X's" ("Known before the runs") is therefore false for this one case; the gate lists it and
    compares its counts of 20 under that reading.
37. **cases_c.json's `values_case_index`** counts the four values cases (0 to 3), not the list `cases`: its 3 is
    `cases[8]` (`n4-g15-3113`, the start the entry names), not `cases[3]` (a form case on `n3-g6-322`). The data file's
    note "Indices into 'cases' count from 0" does not hold for this field. The first pass read `cases[3]`; the gate now
    resolves the ordinal and checks the start.

## After R0 and R0b (written before any main run)

R0 passed with items 35 to 37 explained. R0b passed: the machinery control passes at 100 and at 1,000, the planted arm
1 passes at 100 and is confirmed, arms 2 and 3 do not pass, no negative control is confirmed (`controls_R0b.json`).

38. **R0b's numbers differ from PC's disclosed ones only by the bounds.** At the registered bounds (dev 21) the
    machinery control gives 85 and 95 of 100 (made-4, made-5) against 0, and the planted pair's own rates are 5, 20
    and 0 of 100; PC discloses 78, 86 and (2, 16, 0), measured at the scratch's bounds. Read again at the scratch's
    bounds with the same seeds and calls, they are exactly 78, 86 (against 0), and 2, 16, 0 with 99 of 100
    continuations meeting (`replay_disclosed.json`). No verdict differs.
39. **The parity knot test on a reduced structure** (written after timing a prefix of R1b, before any main run). On
    growths whose ration gives many fresh distinctions (ORD under CANCEL-WAIT: one growth of R1b's prefix held
    1,262,949 distinctions), the fold engine's parity test took 66 s a structure. The engine's two methods are now
    applied to a structure with the same verdicts for every knot: each knot keeps its shared places and the first of
    its loose places, the other loose places dropped, the kept distinctions renumbered. The argument: a knot holding a
    loose distinction constrains no other knot (every solution of the other rules extends to it, by its loose place),
    and its own verdict is whether its shared places are free together under the other rules, whatever the number of
    its loose places (with k ≥ 1 loose places the allowed states on its places are the pairs (a, l) with a allowed on
    its shared places and l of the right parity: all even assignments exactly when every a is allowed). Checked against
    the fold engine's test on the whole structure, and against every assignment on small drawn structures
    (test_mcc.json), and on the three largest structures of R1b's prefix (equal verdicts; 0.26 s against 123 s).
    R9 tests every knot at every round with the engine's test on the whole structure, unreduced.
40. **The take candidates computed once per parent within a round** (written after timing a prefix of R1a, before any
    main run). In R1a's timed prefix (40 starts, 840 growths), 2.1 process-seconds a growth, against PC's 0.121, and
    94% of it under ORD with CANCEL-RETIRE or CANCEL-WAIT, nearly all inside the fold engine's `take_candidates`, which
    recomputes a parent's met knots (`S.meets`) for each of its births (61,416 births of one round, parents holding
    up to 590,000 places). The takes of a round are all formed on the structure at the start of the round, which no
    take changes, so the wrapper of dev 3 now computes, for MET, STEPS-1 and STEPS-2, each parent's met knots and an
    offshoot's candidates before its own inputs are removed once per round, and for a join tests "held by no parent"
    as "no holder of d is a parent" (the same thing). Every other taking rule goes to the engine's function. Checked:
    in a verification mode every call is compared with the engine's own function (equal on every birth of growths of
    every law on a sample of census starts, the ORD laws included; test_mcc.json); the growths and the gate are
    unchanged (R0 rerun on this code below). On the growth timed it cut a round from 492 s to 11 s. The rounds the
    guard stops are still computed by the engine up to its stop.
41. **St.row built in one pass** (written before any main run). Under parity the fold engine builds each new knot's
    row (`St.row`, its places as the bits of an integer) by one shift and OR per place; with 3.5 million distinctions
    that took 75 s of one growth. The method is replaced at import by one that sets the same bits in a byte array
    and converts once (rows of fewer than 64 places use the engine's own); the integer is the same. Checked on 300
    rows against the engine's (test_mcc.json); one growth of R1b's timed prefix went from 95 s to 28 s. R0 and R0b,
    run before items 40 and 41, were rerun after item 40 and gave identical files; item 41 changes no value.
42. **R1b's size** (written before R1b ran). Timed on the first 60 starts of its order (1,260 growths, load average
    about 30 on 24 cores, code of item 40, before item 41): 0.48 process-seconds a growth, so about 56 minutes for the
    registered 2,000 starts on 6 processes; item 41 removes about a third of that time on the slowest growths. R1b is
    run at its registered size, the first 2,000 starts of the parity list. Its records are written as each growth
    ends; progress is logged every 2,000 growths.
43. **R1b cut to its registered first half** (written at 02:32, after stopping R1b, before resuming it). R1b was started
    at 02:24:48 at its registered size on the estimate of item 42. At 6.6 minutes it had written 4,000 growths, at
    0.10 s a growth of wall time (load average about 36 on 24 cores; each worker got about 65% of a core), so the full
    2,000 starts would have taken about 70 minutes, past the owner's hour. It was stopped then, by its own process
    numbers, and cut to its first half, the first 1,000 starts of the parity list (DC 1.5's registered half, a prefix
    fixed at this point and not by what had finished). The 4,000 rows written are complete rows of the first 191
    starts, all in that half, and are kept; the run is resumed on the rest of the half (`--prefix 1000 --append`). Its
    zero bound for the size run is 3/1,000 = 0.30% under the census weighting (PC's 0.15% was for 2,000 starts); the
    second 1,000 starts of R1b are not run. R9 reads R1b's growths of the starts of three and four knots in this
    half.
44. **R9's size is its own** (written before R9 ran). R9 grows its growths again from their seeds, so it does not
    depend on what R1a and R1b ran: it reads, at its registered size, R1a's growths of the 216 starts of three and four
    knots read under parity (dev 29) and R1b's growths of the starts of three and four knots in R1b's registered
    prefix (the first 2,000 of the parity list), whatever the size run of R1a and R1b (dev 43). A structure of more than
    50,000 distinctions is tested at that round by the fold engine's methods on the reduced structure of dev 39 (said
    in R9's records, `reduced_rounds`); every other structure on the whole structure.
45. **521 of R1b's growths regrown** (written at 03:20, after it). The record file of R1b held a gzip member cut
    mid-block (the first start of R1b, stopped by its process numbers, item 43) followed by the resumed run's member.
    My first reader lost the rows decoded inside the piece where the cut member failed (521 rows, of starts 127 to
    190 of the order), and the file was rewritten from what it read before this was seen. The reader now keeps
    everything decodable before a cut and finds the next member by its header and first record (tested on a
    member cut after a flush and followed by a new one: every row recovered). The 521 growths were grown again from
    their seeds (`runs.py R1b --prefix 1000 --append`, 54 s), the same deterministic rows, and the file rewritten as one
    member of the 21,000 rows of R1b's half.
46. **R1a's size** (written before R1a's rest ran). R1a is first timed on its first 40 starts of the parity list (840
    growths), written into R1a's own record file, since every registered prefix of R1a contains them; its size run is
    then chosen from that measure, before the rest runs, as the largest registered prefix (the whole, a half, a
    quarter, an eighth ...) whose estimate fits the hour, and the rest of that prefix is run with `--append`.
47. **R1a cut to its registered first quarter** (written at 03:26, after timing its first 40 starts, before the rest
    ran). The first 40 starts (840 growths, 03:20:45 to 03:25:29, load average 18 to 22): 423 process-seconds for 839
    growths and one growth not read (n5-g42-11133 under ORD(CANCEL-RETIRE) with MET: it passed the 6 GB cap after about
    280 s), 0.84 process-seconds a growth in all. Estimates on 6 processes: the whole R1a (3,344 starts) 2.7 hours, its
    half 82 minutes, its quarter 41 minutes. R1a is run on its first quarter, the first 836 starts of the parity list
    (17,556 growths); the other three quarters are not run. Zero bound for the size run: 3/836 = 0.36% under the
    census weighting (PC's 0.090% was for every start). A growth that passes the memory cap is reported "not read
    (memory cap)", never as a negative, and its start is left out of N for that law.
48. **R1a finished its quarter** (written at 09:20, after a pause of the helper, before R8). R1a's quarter ended at
    04:07:34 (46.2 minutes of wall time in two parts). Of its 17,556 growths 17,553 are read; three passed the 6 GB
    cap and are "not read (memory cap)": n5-g51-01013 and n5-g41-30201 under ORD(CANCEL-OFFSHOOT), n5-g45-33333 under
    ORD(CANCEL-RETIRE), all with MET (n5-g42-11133, which passed the cap in the timed part, was read when grown again in
    the rest). The record file was whole; it is rewritten with each growth once (a read row kept over an error row).
49. **R8 cut to its first half** (written before R8 ran). Timed at 09:19 on a sample of its jobs (2 three-knot and 14
    four-knot starts drawn with `random.Random('timing r8')`, every renaming and law: 4,032 growths, load average 9
    to 21): 0.18 and 0.49 process-seconds a growth on three- and four-knot starts, so about 72 minutes for the 219
    starts on 6 processes. R8 is run on the first half of its starts in census order, the first 110 (the 19 three-knot
    starts and the first 91 four-knot starts: 27,720 growths, about 34 minutes); the other 109 starts are not run. Its
    tests are the same, with each start's side read on those 110 starts (and again on those of them not set aside).
50. **R9 at its registered size** (written before R9 ran). Timed at 10:11 on 420 of its 7,287 jobs drawn with
    `random.Random('timing r9')` (load average 8 to 11): 0.47 process-seconds a growth, about 10 minutes on 6 processes.
    R9 runs at its size (dev 44).
51. **R2 at its registered size** (written before R2's rest ran). Timed on its first 15 starts (630 growths, written
    into R2's record file; 10:22:59 to 10:24:23, load average 7 to 11): 0.42 process-seconds a growth, so about 25
    minutes for the 500 starts on 6 processes. R2 runs at its registered size; its rest with `--append`.
52. **R1c cut to its registered first half** (written before R1c's rest ran). Timed on its first 15 starts of the
    full order (315 growths written into R1c's record file; 10:47:05 to 10:48:59, load average about 8): 1.60
    process-seconds a growth (the ORD laws' rounds that end at the guard, as in R1a; the last-round tie check of dev 14
    14 s in all), so about 93 minutes for the registered 1,000 starts and 47 for its half. R1c is run on its first
    half, the first 500 starts of the full order (10,500 growths); the second 500 are not run. Zero bound for the size
    run: 3/500 = 0.60% under the census weighting (PC's 0.30% was for 1,000).
53. **R1c cut to its registered first quarter** (written at 11:22, after stopping R1c, before resuming it). R1c's half
    (item 52) ran from 10:49:28; its pace fell from 0.27 s a growth of wall time (its timed part) to 0.6 s (1,000
    growths in 608 s up to 11:18), so the half would have taken about 90 minutes in all. It was stopped at 11:21 by its
    own process numbers (its parent first; five orphaned workers then, by their numbers) and cut to its first
    quarter, the first 250 starts of the full order (5,250 growths): a registered prefix fixed now, not by what had
    finished. The 4,314 growths read so far are all of the first 206 starts, inside the quarter, and are kept; the run
    is resumed on the rest of the quarter. Zero bound for the size run: 3/250 = 1.2% under the census weighting. The
    other three quarters of R1c are not run.
54. **R1d at its registered size** (written before R1d's rest ran). Timed on its first 6 starts (126 growths written
    into R1d's record file; 11:45:57 to 11:47:59): 1.83 process-seconds a growth, about 13 minutes for its 120 starts
    on 6 processes. R1d runs at its registered size; its rest with `--append`.
55. **R1d cut to its registered first quarter, after it passed the hour** (written at 13:08, after stopping R1d). R1d
    was run at its registered size (item 54) from 11:48:10 on a timing of 1.83 process-seconds a growth. Single
    growths under ORD(CANCEL-WAIT) with STEPS-1 and not-all-equal then took 1,931 s and 2,557 s (the fold engine's
    rounds that end at the guard, and the not-all-equal knot test on structures of hundreds of thousands of
    distinctions), and at 12:52 two workers had been on one growth each for more than 40 minutes, with no end in sight.
    The run passed the hour at 12:48. An interrupt to its parent at 12:52 (to have the rows it had received written)
    took no effect, since the parent handles it only when a result arrives, and none arrived in 14 minutes; it was
    stopped at 13:07 by its process numbers. Rows received after its last flush (at 2,100 growths) are lost. R1d is cut
    to its first quarter, the first 30 starts of the full order (630 growths), all of which were in the file: a
    registered prefix, fixed now. Its half lacks two growths (n5-g35-12223 and n5-g48-11031 under ORD(CANCEL-WAIT)), the
    second of which took 1,931 s, and the first of which was still running after more than an hour. The 1,596 rows of
    starts 30 to 119 that were written are kept apart in `R1d_beyond_quarter.jsonl.gz`, computed but not part of the
    size run, and enter no rate or verdict. Zero bound for the size run: 3/30 = 10% under the census weighting. The
    other three quarters of R1d are not run. This is a cut after the hour, against the brief's rule (a run is not to be
    cut by the clock): it is reported as such.
56. **R7 at its registered size** (written before R7 ran). Timed at 13:08 on 12 of its 158 checks' enumerations of
    the start itself (4 of each label, drawn with `random.Random('timing r7')`): at most about 53 minutes on 6
    processes, an upper estimate, since the five renamed starts reuse the depth found on the start (the search
    through more than 30,000 histories is made once). R7 runs at its registered size: 108 + 14 + 36 checks.
57. **R7 resumed after a memory stop** (written at 13:37, before resuming). R7 started at 13:08:59; at 13:36 one
    enumeration passed the 6 GB cap inside the fold engine's clique enumeration, and the error, raised in the parent,
    stopped the run, after 157 of its 158 enumerations of the start itself had been written. The enumeration kept
    every history's state until the end; it now reduces each history at once to its class and exact chance (the same
    distributions), and a memory error is written as a row "not read (memory cap)" instead of stopping the run. R7 is
    resumed on what it has not written (the rows written are kept: the same deterministic enumerations). A check
    whose enumeration passes the cap is reported "not read (memory cap)", never as equal or unequal.
58. **One R7 check not read** (written at 14:10, after stopping it). After the resumption of item 57 every enumeration
    was written except the start's own enumeration of one check (parity, three knots, n3-g6-233 under
    ORD(CANCEL-OFFSHOOT) with MET: its histories reach rounds whose rosters have up to the guard's 2,000,000 cliques;
    it had passed the memory cap once). It had run 31 minutes when R7 reached an hour (27.9 + 31.3 minutes), and was
    stopped then by its process numbers. That check (with its five renamings) is "not read"; the other 157 are
    complete. R7's summary is written from its rows (`r7.py --analyse-only`).
59. **R3 in full** (written before R3 ran). m, counted over the main runs as read (R1a's quarter, R1b's half, R1c's
    quarter, R1d's quarter, R2 whole) before any confirmation: 5 cases of a claimed reading pass at 100 (four form
    cases of R1b, one of R1d), so each is confirmed at 0.01/5 = 0.002; m' = 0 (no case of a reported reading passes at
    100). R1d's growths beyond its quarter (one of them holds a form case that passes at 100) are not part of the size
    run and are not counted. Timed: under a minute.
60. **R3's result fires the conditional runs; they are held** (written at 14:15). All five cases that pass at 100 are
    confirmed at 0.01/5 (`R3.json`), each "through joining", none "needing the meeting", each in a growth with no
    failing knot: four form cases on three growths under RATION-2(CANCEL-RETIRE) with STEPS-1, parity (Y the two-knot
    part), and one under CAP-2(CANCEL-RETIRE) with STEPS-1, not-all-equal (Y a lone member holding one). In each the
    meeting runs through a start knot (DC 6: "supplied" in the third question). No first-pattern form has confirmed
    cases for two second-pattern forms, so there is no candidate (DC 5.1) and stage 2 (R4) is not triggered. A
    confirmed case of a claimed reading triggers R5 and R6 (PC "Runs"); the brief asks that the coordinator be told
    first, so they are not run here.

## The conditional runs (written on the coordinator's word, 2026-11-25 afternoon, before R5 ran)

61. **R5 and R6: readings** (`cond.py`).
    - **R5's growths.** DC 1.3's swaps: the 42 laws with HOLD for RELEASE and the 21 with STEPS-2 for STEPS-1, parity,
      on the starts of three and four knots and the first 300 five-knot starts of the order (starts_c.json's list);
      HOLD with MET under not-all-equal on the starts of three and four knots. Under parity the 3 set-aside starts
      are skipped (DC 1.1, as in every census run); PC's count of 37,296 includes them, so R5 has 37,107 growths.
      Seeds: DC 1.4's (`|STEPS-1|HOLD`, `|HOLD`, `|STEPS-2`). Every reading, case and first stage as in R1.
    - **R5's order** (for a prefix cut; the coordinator's): part A, the 219 starts of three and four knots in DC
      1.5's order, each under HOLD's 42 laws and STEPS-2's 21 (parity, each list in DC 1.3's order) and then HOLD
      with MET under not-all-equal (21); then part B, the 300 five-knot starts in order, each under the 63 parity
      laws. A cut keeps all of part A and a prefix of part B's starts; which of HOLD and STEPS-2 ran on what is
      then said.
    - **R6's growths**: as R9's (dev 44), R1a's 216 and R1b's 131 starts of three and four knots under their 21
      laws, grown again from their seeds (the same growths), every pair read (no eight sampled), each case's first
      stage at 300 continuations of kinds `BN3`, `BY3`, `BX3`, i = 0 to 299 (DC 4.4). Its order: the starts of three
      and four knots in DC 1.5's order (the parity list), each under R1a's 21 laws and then, when in R1b's prefix,
      R1b's 21.
    - **The conditional family** (DC 4.4): the cases of a claimed reading passing the first stage in R5 (at 100)
      and in R6 (at 300), all counted before any confirmation (m_c), each confirmed on 1,000 further continuations
      of the five kinds (i = 100 to 1,099) at 0.01/m_c; the reported readings in their own family. R6 regrows R1's
      growths, so a case of R1 may reappear there; it is counted in the conditional family again, at its own
      first stage.
    - **A time limit on each growth** (the coordinator: no run past its hour, no repeat of R1d's overrun). Each
      growth, with its first-stage continuations, runs under a wall-time limit of 600 seconds, fixed now for every
      growth alike; one that passes it is recorded "not read (time limit)", as a growth past the memory cap is,
      never as a negative, and its count is reported. This leaves out the slowest growths (those with the largest
      structures, or a case whose continuations are slow); the bias is stated with every bound.
62. **R5 at its registered size** (written before R5 ran). Timed at 14:18 on 300 of its 37,107 jobs drawn with
    `random.Random('timing R5')` (load average under 3), at its exact settings: about 21.5 minutes on 6 processes, of
    which HOLD with MET under not-all-equal is 104 of 129 process-minutes (1.36 s a growth); the parity swaps 0.02 to
    0.09 s a growth. R5 runs whole: HOLD (42 laws) and STEPS-2 (21) on the 216 three- and four-knot starts and the 300
    five-knot starts, parity; HOLD with MET on the 219 three- and four-knot starts, not-all-equal.
63. **R5's result, and R6 at its registered size** (written before R6 ran). R5 ran whole, 14:19:13 to 15:03:57 (44.7
    minutes): 37,102 of 37,107 growths read, 5 not read (3 past the time limit, under ORD with HOLD and MET,
    not-all-equal; 2 past the memory cap, under ORD with HOLD and MET, one of each knot law); 10 cases of a claimed
    reading pass the first stage. R6 timed at 15:04 on 300 of its 7,287 jobs drawn with `random.Random('timing R6')`:
    5 minutes for its growths; the sample held one case, so its first stage at 300 is undersampled, and with about
    150 cases at about 45 s each the whole is about 25 minutes. R6 runs whole, under the same time limit.
64. **R6's result, and the conditional family's confirmations** (written before they ran). R6 ran whole, 15:05:34 to
    15:16:32: all 7,287 growths read, 105 cases, 4 passing the first stage at 300 (2 form, 2 of ticket A's values
    reading). The conditional family, counted over R5 and R6 before any confirmation: m_c = 12 claimed cases (R5's 10,
    R6's 2), each confirmed at 0.01/12; m_c' = 2 reported cases, each at 0.005. Confirmations as R3's (1,000 of each
    of the five kinds, i = 100 to 1,099), written to `Rcond.json`; timed from R3 (5 cases in 22 s): a minute or two.
65. **The conditional family's result** (written at 15:18, after it). All 12 claimed cases are confirmed at 0.01/12,
    each "through joining" and in a growth with no failing knot: R5's 10 (form, s = 1, under CANCEL-RETIRE: STEPS-2
    with RELEASE under FLOOR1, FBP and CAP-2, and HOLD with STEPS-1 under FBP and RATION-2), two of which (FBP with
    HOLD and STEPS-1, n3-g6-223 and n4-g16-1123) need the meeting (none of 1,000 with Y barred and none fully masked);
    and R6's 2 form cases (RATION-2(CANCEL-RETIRE) and FLOOR1(CANCEL-OFFSHOOT), both STEPS-1). The 2 reported cases
    (ticket A's values reading, the scratch's two values cases) are not confirmed: "with Y's births, not through a
    meeting". In every confirmed case the meeting runs through a start knot (DC 6: supplied in the third question).
    No law has a first-pattern form with confirmed cases for two second-pattern forms: no candidate, so stage 2 (R4)
    does not fire.
