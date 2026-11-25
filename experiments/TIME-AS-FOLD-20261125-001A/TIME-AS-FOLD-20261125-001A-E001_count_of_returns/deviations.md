# Deviations and readings, TIME-AS-FOLD-20261125-001A-E001

Written by the engine's author, who has not seen the drafter's prototype (the drafter's scratch
folders), the folder `research/TIME-AS-FOLD-20261125-001/advisor/`, or `survey.md`'s accounts of the
prototype's scripts. The frozen texts were read in the order of the brief: SD (`research/RING-IN-BALANCE-20261123-001/definitions.md`),
FD (`research/PARTS-MEET-AGAIN-20261124-001/definitions.md`), the claim, TD, the pre-registration and its data files,
then the reference engines named for the gates. Their SHA-256 sums were checked against `contract.json` before any code
was written; all match. `contract.json` and `identity.json` are not touched.

Citations: SD line n; FD section; TD section; PR the pre-registration. Each item gives the question, the reading taken
and why, and the runs it affects. Items 1 to 26 were written before any gate or registered run; every later item says
when it was written and what had been seen.

## Engine and independence

1. **Independence.** The engine (`tf_engine.py`), the knot tests (`tf_knots.py`), the series (`tf_series.py`) and the
   tests of a clock (`tf_tests.py`) are written from the frozen texts. The engine of the study of parts that meet again
   (`pm.py`, `knots.py`, `paired.py`) and its `deviations.md` were read, as the brief's reading list asks, before the
   engine was written; nothing is imported from them except in the gates. Before the gates, a development check grew
   the twelve named starts for 8 rounds under the control and under Q, MET, STEPS-1, STEPS-2, UP-TO-2 with the four
   choices on both engines (in the scratch folder, not a registered run): every knot equal once start knots keep the
   order of their stars (item 4). The drafter's prototype was not seen.
2. **Order of births and names** (FD 2.1) as written: the kept groups of three or more in lexicographic order of sorted
   members, then the pairs; then offshoots in increasing member name; a member gives its usable loose distinctions in
   increasing name to its joins, then (HOLD) keeps the next ones, then to its offshoots; new knots named in birth order;
   fresh distinctions named after the demand step in birth order, usable before barred.
3. **The structure after an earlier round is a view of the final one.** Holders only grow and are kept in order of
   acquisition (knot ids are in birth order), places are fixed at birth, and a barred distinction stays barred with the
   round at which it was barred; so the structure after round t is: knots made by t, holders made by t, distinctions
   barred by t. Traces, rosters for reading and the comparison runs' starting structures are taken from it.
4. **Start knots keep the order of their stars** as their list of places (a representation only; every rule reads places
   as a set or sorts them).
5. **A take never repeats** (FD 2.4): candidates already among the birth's inputs are removed before the choice (with the
   registered rules an offshoot's own input is loose and never eligible, and a join's candidates are held by no parent,
   so this never removes anything).
6. **Descent** (TD 2.3, TD 3.2, FD 4.2). The members after round t that descend from a part P after round s are the
   members of P still members and the knots made after s with a parent among P and its descendants. A member descended
   from P and also from another part descends from P (the letter of TD 2.3: "every member of Q descends from P"); the
   ring study's engine instead labels such a member "mixed". Implemented by labels (sets of parts of round s) passed
   from parents to children.
7. **Rosters read for the series are computed without the guard.** TD 1.7's guard cuts a round of growth short; the
   roster after the last round kept is read for the series even when it would have tripped the guard for the next
   round (it is not grown from). The limit of process time still applies to the run.
8. **A first return is searched while some member descends from P**; once none does, no later member can, and the part
   has no first return.
9. **STEPS-k, "exactly k parent steps above"** is the union over chains: a knot reached by some chain of exactly k
   parent steps. UP-TO-k is the union of levels 1 to k. (FD's text; the same reading as the engine of the study of parts
   that meet again, its item 7.)
10. **IN-TURN's index** counts every offshoot of the same parent in the round in birth order, whether or not the earlier
    ones took (FD 2.5, "the i-th offshoot of one parent in the round").

## Series, clocks and counts (TD 2)

11. **"Past its start" as a filter on series** (TD 2.2). With the filter, a part's first return is searched only when the
    part is past its start (SD line 85: "A part Y ..., past its start, returns ..."); a qualifying Q need not itself be
    past its start (SD does not ask it), and the series ends at a Q that is not, since its own return is not searched.
    Without the filter every part is searched.
12. **"A clock giving parts off at four ticks"** (the census's column, P3, P8, P9): primary, a series of parts of two or
    more members with four consecutive equal periods after some t_j, each of the four ticks t_{j+1} to t_{j+4} giving
    parts off; reported beside it, a clock (four equal periods somewhere) that gives parts off at four or more of its
    ticks anywhere. "A series giving parts off at two ticks or more": any series (any size). "A clock of 4 equal
    ticks": a series of parts of two or more members with four consecutive equal periods.
13. **Series starts** (TD 2.4): every searched part that is not the followed first return of an earlier part starts a
    series; a part that qualifies at a first return but is not followed (a copy) starts its own series. A part followed
    from two earlier parts is in both series.
14. **The greatest-name convention** (TD 8's swap of "the least-name convention for the series"): the series follows
    the qualifying part whose smallest member name is greatest.
15. **Direct meetings** (TD 2.3) are reported for each return as the number of pairs of members of the returned part
    that share a distinction, and how many of those pairs lie in no maximal met set of the part (not carried).
16. **Start knots acting** (P2): the start knots descended from the series' first part (they can only be members of it)
    that are parents of some birth in a round of the series (after t_0, through its last tick); for STEPS-k, the knots
    descended from the first part that are parents of a birth in those rounds and have no ancestor exactly k parent
    steps above them. P2 is checked on the laws of the count (COPY-LAW(t) with Q, MET, MET's offshoot clause alone,
    STEPS-1, UP-TO-2; fresh by distinct inputs; main group and demand-before-takes group, which under FLOOR1 grow the
    same) and, with its own bound, on STEPS-2 under COPY-LAW(t).

## The knot test (TD 7)

17. **Parity at every round.** Under IMPLIED every birth either receives a fresh distinction (held by it alone, so it
    forbids no earlier state) or has a row in the span of the rows before its round (so it forbids none either): every
    round extends, and the allowed states on the distinctions of any earlier round never change. A knot's verdict is
    therefore the same at every round from its birth. Each method is computed once per knot and that verdict is the
    verdict at every round: ranks at the knot's birth round, on the matrix left after peeling (deleting a knot with a
    column outside the removed set held by it alone, with that column, leaves rank(H) - rank(H without the knot's
    columns) unchanged); kernel from a basis of the allowed states built knot by knot (one bit column per distinction;
    columns of earlier distinctions never change unless a knot without a fresh distinction is not IMPLIED, which is
    counted as a "cut" and reported). The extension of every round is checked exactly (every birth has a fresh
    distinction or is IMPLIED). The literal test (both methods on the whole matrix at every round, no peeling) is run
    on every run A of at most 300 knots at every round and compared.
18. **Not-all-equal at every round.** Under not-all-equal every birth here receives a fresh distinction (FLOOR1 and CAP-3
    give at least one; under FILLERS a barred fresh distinction is still held by its knot alone), so FD 7's statement
    applies: a knot's verdict at any round after its birth is its verdict at every later round. The birth method is run
    on every knot made after round 0 (start knots directly at round 0); the direct test on every knot of at most 12
    places at the last round grown (which, by FD 7, is its test at every round from its birth), compared with the birth
    method. On every run A of at most 300 knots the direct test is also run at every round.
19. **Peeling for one knot** is found from one peeling of the whole structure per round: a knot that cannot be removed
    when the columns of I may not be used is either in the structure's own core or is reached from a knot whose own
    column at its removal lies in I, through columns shared with earlier-removed knots; peeling is then repeated within
    those candidates only. This is exact (checked against plain peeling and brute force, `knot_checks.json`).

## The tests of a clock (TD 3 to 6, run 4)

20. **Bars in the order r = 1, 2, 3** (TD 4.6): after a bar at which both claims are decided failures (C: clause 1 fails
    or an own knot after the lag; C-iii: equal through two periods), the later bars are not run and are reported "not
    run: both claims decided". B'(r) and Ball(r) are run for each bar at which B(r) is run; B'(r) when parts are given
    off at that tick (otherwise nothing is barred and it is run A), Ball(r) when several parts qualify (otherwise it is
    B(r)).
21. **Comparison runs are shared and their time is charged to each test** (TD 1.7's limit, "600 seconds of process time
    for each run A and each test"). B(r) depends on the test only through what it bars; a run is grown once for all
    tests that bar the same knots after the same round, and its process time is added to each such test's time with
    the test's own analysis. A test whose total passes 600 seconds is unfinished. Each comparison run is itself grown
    under a 600-second limit.
22. **Through a meeting** (TD 4.4): X's trace in M(r) equals its trace in B(r) over the same rounds as the claim's
    clause (two periods after the bar for C-iii, four for C), through the last round B(r) reached, M(r) having reached
    it too.
23. **The lag** (TD 5.2): the least L, 0 <= L <= 2 periods, such that B(r) is grown through t_{j+r} + L + 2 periods, X
    makes no own knot in B(r) in any round after t_{j+r} + L that is grown, and run A makes at least one own knot of X in
    each of the two periods after t_{j+r} + L. Which of the three (ended, all members wait, closed) is read at B(r)'s
    last round.
24. **TD 4.6 is applied as written.** C fails when clause 1 fails in run A or, for some r, X makes an own knot in B(r)
    later than round t_{j+r} + 2 periods; C holds when every clause holds and both runs are grown through
    t_{j+r} + 4 periods for every r (the knot test and the numberings are checked after, in runs 5 and 7); every other
    test is undecided, with the clause that kept it from holding reported. The same for C-iii. "Ruled out by the
    treatment" (the claim, section 5) is a label added, under (CANCEL-OFFSHOOT, RELEASE, not-all-equal, no FILLERS), to a
    test in which no B(r) that was run makes a joint knot after its bar; the test is still run in full and keeps its
    TD 4.6 verdict.
25. **What made the meeting** (TD 6.2): in run A, the first round after the bar, through the first differing round, at
    which a member of X's side and a member of P_{j+r}'s side are joinable in the roster read for that round or in its
    demand roster (the round replayed from the structure before it); the common knots of the met sets holding a member
    of each side, each classed as FD 5.7. "Knots the growth made" when one of them was made after round 0.
26. **Clocks tested once** (run 4): clocks of one run are grouped by the number of members of their parts, their whole
    tuple of periods, and the parity of their first round t_0; the one tested is the one whose first part has the least
    smallest member name.

## The gates (written before them; items 27 and 28 completed after them, before any registered run)

27. **G1.** (a) Knot for knot: the twelve named starts and the 227, the control under every base law (the seven of
    `rules.json`), both knot laws, 18 rounds, knot bound 4,000, the guard, on both engines; compared: every knot's places
    (as ordered lists), parents, round and kind, every distinction's barred state, the rounds grown and the stop, and
    per round the births, joins, offshoots, stall, closing, short members, and every birth's demand, fresh, usable,
    barred and inputs. (b) The census: `bref.census_starts` for 3 to 6 knots, `bref.census_stars`; a start is set aside
    when a knot fails the parity knot test (ranks and kernel) on the start; RING-LAW under parity (the ring study's
    census ran under parity; IMPLIED and the ring engine's literal closing agree on these connected structures with two
    holders, FD 2.8), 10 rounds, knot bound 1,500; "a tick giving parts off" is a tick of some series (TD 2.4) with a part
    given off (TD 2.7), with and without "past its start". **G2**: run as the frozen files were (8 rounds, knot bound
    1,500, the guard); "most holders" read over the knots made by each round; two-knot parts as the study of parts that
    meet again defines them (parts past their start of two members with h = 2, k = 0 lying in one met set); classes as
    FD 1.6. **G3**: parts are drawn (seed 2026112503) from runs of run 1's list grown for the gate (five named starts,
    every base law, seven rules, OLDEST, not-all-equal, 8 rounds); a renamed copy permutes and renumbers the members;
    an altered copy changes one h or k, drops or adds one member of a met set, moves h between two members, merges two
    met sets or splits one (seven kinds in turn), on parts of at most 7 members, and is kept only when brute force over
    every member bijection finds it not the same.
28. **The sameness test changed after a gate, before any registered run.** In the first run of G3 the test used VF2
    for parts of more than six members; a supplement to G3 (renamed copies of 300 drawn parts of 7 to 40 members) did
    not finish in 600 seconds with it on highly symmetric parts. It now uses networkx's VF2++ (`vf2pp_is_isomorphic`)
    with the same colours; parts of at most six members are compared by renamings within signature classes, as before.
    G3 was rerun (passed, every renamed copy accepted and every altered copy rejected by both paths, and the 300 large
    renamed copies accepted); G1b, the only other gate that reads sameness, was rerun with the final test (passed, the
    same counts). G1a and G2 do not read sameness. Seen before this item: the first runs of G1a, G1b, G2 and G3, all of
    which passed.

## Runs 1 to 3 (written after the gates passed, before any registered run)

29. **The order of run 1's registered items**, used if a run must be cut to a prefix: the group as registered (the
    control and the thirteen rules) first, then the taking laws with the fresh count by parents, then with demand taken
    before the takes; within a group, the starts in the order of `starts.json`, the base laws and the rules in the order
    of `rules.json`, the choices OLDEST, NEWEST, IN-TURN, BY-COUNT (MET's join clause alone without IN-TURN), the knot
    laws not-all-equal then parity. The greatest-name convention is read on the same runs as the group as registered
    (it changes the reading of the series, not the growth), for every taking law.
30. **"The round at which a ring member's offshoot first takes"** (run 3): ring members are the start's members and the
    members of every part that is the same as the start's whole roster at a round where it returns; the round is the
    first at which an offshoot of one of them takes. The first round with any take, and with any offshoot's take, are
    reported beside it.
31. **Every run A is grown and read under one limit** of 600 seconds of process time (growth and the reading of its
    series with and without the filter, and under the greatest-name convention where it is read); a run A that reaches
    it is unfinished and gives no series.
32. **The sameness test changed again, before any registered run** (written after a timing sample of run 1 of 180
    drawn items, seed 2026112505, in which one run's series could not be read: VF2++ did not finish on a part of 98
    members in 600 seconds). Parts of more than six members are now compared by joint colour refinement of the two
    coloured member/met-set graphs and individualisation with backtracking, each candidate mapping checked edge by edge
    at the end (exact). The first-return search now looks, for each part after round t, only at the parts of round s
    its members all descend from (the same result, fewer comparisons). G3 (named "vf2" in `g3.json` for the path of more
    than six members, now this one) and G1b were rerun with the final test and pass with the same counts. Seen before
    this item: the gates and the timing sample (its rows were not used for anything else).

## The comparisons, run 4 to run 7 (written while run 1 was growing, before its outputs were read)

33. **Comparing with compare.json's census table** (P3, P9, the census rows): exact numbers over runs finished in both.
    A run listed in compare.json's "unfinished" is dropped from my counts; a cell in which one of my runs is unfinished
    is reported as not comparable. The prototype's census grew MET's join clause alone with all four choices (288 and
    384 runs per ration in its table) while run 1 registers three (IN-TURN is OLDEST for a join, TD 1.4): in the
    comparison my OLDEST runs of that rule are counted twice. "bound exceeded" is read as the number of runs cut short by
    the knot bound.
34. **Run 5: a case and its survival.** A case is a law (base law, rule, choice, knot law, group) and a start with a test
    of run 4 (either pass) in which C-iii holds, or C holds before the knot test and the numberings. Under a numbering,
    the case survives when some test of the renamed run (its clocks tested once as dev 26, j = 0 and 1, every X) meets
    the same sense. The number of numberings that differ up to the start's own symmetries is the number of different
    named starts they give (each knot, in knot order, as the set of names of its distinctions): two numberings that give
    the same named start give the same run.
35. **The first draft's near case** (Y a one-member series, no case under TD 2.5) is run as a supplement under every
    numbering of the two-knot start (L1, COPY-LAW(CANCEL-OFFSHOOT), OLDEST and IN-TURN, both knot laws), with one-member
    series of four equal periods taken as Y and everything else as run 4, only for the comparison with the disclosed
    112 of 240; it decides no prediction.
36. **Run 6's swaps**: names reversed = the start's distinctions named in decreasing order of label (FD's swap; knots as
    given); order of births reversed (dev 21); demand taken before the takes; fresh by parents; HOLD in place of
    RELEASE; the ration FLOOR1 against CAP-3 (the treatment kept); the other knot law. Each swapped run is read as run 5
    reads a numbering.
37. **Run 7 on comparison runs**: the knots made after the round at which each comparison run leaves run A (earlier
    knots are run A's and keep its verdicts: the structure through that round is run A's, barring changes no allowed
    state, and every later round extends, dev 17 and 18), by the same methods: under parity at every round (by
    extension), under not-all-equal at the last round.
38. **The prototype's column "bound exceeded"** (written after run 1's census was compared with compare.json). Item 33
    read it as runs cut short by the knot bound; the counts disagree in almost every cell (for instance 0 against 452 on
    the 227 under the control), and the pre-registration's own sentence "the count's bound exceeded in 8 runs under Q,
    2 under STEPS-1, 6 under STEPS-2 and 4 under UP-TO-2" matches compare.json's cells fbp|Q|FLOOR1 (8), fbp|STEPS-1|
    FLOOR1 (2), fbp|STEPS-2|FLOOR1 (6), fbp|UP-TO-2|FLOOR1 (4). So the column counts runs in which some series has more
    ticks that give parts off (or have copies) than its bound. Under my count of start knots acting (item 16) the
    numbers still differ (the prototype's count of acting knots is not disclosed); the column decides no prediction (P2
    is judged on the laws of the count, where no series exceeds the bound under my stricter count), and its difference
    is reported as a difference of reading. Runs cut short by the knot bound are reported in their own column.
39. **Run 4's clocks tested once, revised, and the masked runs' rounds** (written after a timing sample of run 4, 150
    runs drawn with seed 2026112506, before the registered run 4). (a) Item 26 grouped clocks by their whole tuple of
    periods, so the copies that start a new series at every tick (a part that copies itself, item 13) were tested as
    different clocks, the same form at shifted rounds: up to eleven clocks per run where the text's grouping ("the same
    number of members, the same periods and first rounds of the same parity are tested once") gives two or three. The
    grouping is now by the number of members, the set of period lengths, and the parity of t_0; the one tested is still
    the one whose first part has the least smallest member name. (b) A masked run M(r) is read only through
    t_{j+r} + 4 periods (both of its comparisons lie within it), so it is grown through that round (or the bound) and no
    further; every other comparison run is grown through the registered bound. (c) Masked runs are now cached by the
    bar's round, X and the part P_{j+r} (the sample's code cached them by the round and X only, which could have
    shared one masked run between two clocks with ticks at the same round; no registered output was produced with it).
40. **Run 4 is cut to a prefix** (the owner's limit of 25 November 2026: no run over about one hour of wall time; written
    after the second timing sample, before the registered run 4). Run 4 has 10,116 registered runs A (every run of runs 1
    to 3 with a clock taken without "past its start": 2,975 of run 1's group as registered, 3,334 with the fresh count
    by parents, 3,011 with demand before the takes, 486 of run 2, 310 of run 3). The sample (150 runs, seed 2026112506,
    6 processes) took 108 s of wall time, so the whole would take about 2 hours. What is run: the first 5,000 runs in the
    registered order (runs 1, 2, 3; within run 1 the order of item 29): all 2,975 of the group as registered and the
    first 2,025 of the 3,334 with the fresh count by parents, about an hour. Not run: the other 1,309 runs with the fresh
    count by parents, the 3,011 with demand before the takes, and every test on the runs of runs 2 and 3. What the
    prefix can show: every verdict on the primary laws and the second arm as registered (P5, P6, P12, P15, P16 are judged
    on the group as registered); what it cannot: the tests of the swaps of the fresh count (in part) and of demand, and
    of the 227 and the ladder, which are reported "not run", never as a negative. The second pass of run 4 is run on the
    tests of the prefix. The remainder's command line is in README.md.

## After run 4 (written after run 4's prefix was seen, before runs 5 to 7)

41. **Run 4's second pass** ("a test with no failure decided and some bar undecided is run again"): read per test, both
    claims together: a test qualifies only when neither C nor C-iii has a decided failure. C failed (decided) in every
    test of the prefix, so no test qualified and the second pass ran nothing. (Read per claim instead, the C-iii tests
    left undecided would have qualified; every one of them is undecided because a difference seen within two periods is
    not reproduced by the masked run, which more rounds cannot change.) **The test with X barred** is compared over the
    rounds both runs reached: run A cut short by the knot bound can end Y's ticks earlier than the run with X barred
    (which has fewer knots), and such an extra tick is not a change of Y's series. **P15's form**: Y a three-member series
    of period 3 rounds that returns fewer times with X barred (X of any size; the disclosure itself gives X of three,
    five or seven members).

## After runs 5 and 6 (written after their outputs were seen)

42. **Run 5's survival under dev 34 tests one clock of each form, and this matters.** In the renamed runs the clock of
    a form whose first part has the least smallest member name is tested (dev 26 and 39, applied as run 4 applies them);
    under a numbering another clock of the same form can have an X that meets C-iii while the least-named one has none.
    Seen on Ring(5,3) with BY-COUNT under the numbering "shift 1, distinctions reversed": of the three clocks of three
    members and period 3, the second ([81, 97, 98]) has two tests in which C-iii holds and the tested one ([80, 95, 96])
    none. This is the whole of the difference from compare.json's "shifts" rows on Ring(5,3) and Ring(5,4) with BY-COUNT
    (32 and 16 numberings under each knot law in which the prototype, which tested every series, passes and run 5 does
    not), and possibly of the few on D2 and DW with OLDEST. TD 5.4's "some (Y', X') in the run under that numbering" reads
    more naturally as every clock of the run; the grouping is run 4's economy and itself uses names. Run 5 as run is kept
    and reported as recorded (dev 34); a supplementary reading, every clock of the renamed run tested, is run on the
    numberings of the STEPS-2 cases that did not pass, and reported beside it. Neither reading changes "survives every
    registered numbering": every STEPS-2 case fails under at least one under both (the prototype's counts are themselves
    below the number run). Run 6 used the same grouping; it is reported with this caveat.
43. **Run 7 is cut** (the owner's limit of one hour; timing sample of 120 runs A, seed 2026112507: 64 s of process time,
    14 s of wall time with 6 processes, so all 28,590 runs A of runs 1 to 3 take about 45 minutes). What is run: the knot
    test of every run A of runs 1, 2 and 3 (registered order), and of the comparison runs of a sample of run 4's runs A
    (seed 2026112508, as many as fit in about 20 minutes). Not run: the knot test of the runs A of runs 5, 5b and 6 (the
    renamed and swapped runs) and of the other comparison runs; they are reported "not run".

## After the stop of the session (written on 25 November after the thread's message, before the runs below)

44. **Run 7 on comparison runs, the sample fixed.** Every output file of runs 1 to 7 was checked whole after the
    session's stop (run 7 on runs A had finished all 28,590 runs in 64 minutes). A timing sample of 36 runs A of run 1
    with a clock (seed 2026112508) took 534 s of wall time with 6 processes (62 s of process time per run A, the most
    431 s). What is run: 100 runs A drawn with seed 2026112508 from the 5,000 of run 4's prefix, each with every comparison
    run of its tests, about 25 minutes; the timing sample's 36 are reported beside them. Not run: the comparison runs of
    the other 4,900 runs A of the prefix, and of every run A outside it.
45. **The supplement of item 42, its result, and the same for run 6** (written after the supplement, before run 6's).
    With every clock of the renamed run tested, the STEPS-2 cases' verdicts under the 4n shifts equal compare.json's
    "shifts" rows in all 3,488 numberings, and 28 of the prototype's 30 cases pass all four numberings of the study of
    parts that meet again (Ring(5,4) with BY-COUNT passes 2), as disclosed; no case passes all 4n, so run 5b's condition
    is not met under either reading. Run 6 (308 runs, about 2 minutes) is read again the same way, every clock tested,
    and reported beside the run as recorded.
46. **Process notes (not readings).** (a) Run 1's output (52 MB compressed) is kept in eight parts,
    `run1_part1.jsonl.gz` to `run1_part8.jsonl.gz` (each under 7 MB), in the order written; every script that reads them takes the
    parts in order (`tf_common.jsonl`), and the census tables recomputed from the parts are identical to those computed
    from the single file. (b) `tf_unit_series.py` (a series with a known period, a part barred after a tick, own against
    joint knots, renumbered starts under the control) was written and run after the registered runs, as a check of the
    code they used; it passed. The knot tests were checked against brute force before any run (`knot_checks.json`).
    (c) The session stopped for about five and a half hours after run 7 on runs A had finished; nothing was running
    then, and no output was cut.
