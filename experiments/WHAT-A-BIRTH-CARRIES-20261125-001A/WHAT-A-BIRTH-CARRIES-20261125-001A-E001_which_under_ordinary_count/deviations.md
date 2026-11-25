# Deviations and readings, WHAT-A-BIRTH-CARRIES-20261125-001A-E001

Written by the engine's author, who has not seen the drafter's prototype, its outputs, or the `advisor/` folder of the
epic. The frozen files are unchanged; their SHA-256 sums were checked against `contract.json` before any code was
written (and `common.check_frozen()` checks them again at the start of every script). Citations: SD line n (the shared
definitions), FD s.i (the fold study's definitions), D s.i (the copier study's), RD s.i (this study's), PR (the
pre-registration). Each item says the question, the reading taken and why, and which runs it affects. Items 1 to 22
were written before run G.

## The engine and run G

1. **The round is written again, and checked against the fold engine.** RD 1.1 asks for FD 2 exactly; the brief allows
   the fold engine `pm.py` to be imported unchanged. Because RD 3.3 needs values the fold engine does not record (each
   candidate's supplier, the members of each demand group), `wbc.py` writes the round again from SD steps 1 to 8 and
   FD 2, and run G compares it with `pm.py` (imported read-only) on the 648 runs of RD 5.3. The guard's numbers are
   `pm.GUARD`, the knot test is `knots.py` (FD 7), both unchanged.
2. **Run G's laws.** "3 treatments" (RD 5.3) is read as the three of RD 1.3: CANCEL-RETIRE, CANCEL-OFFSHOOT,
   CANCEL-WAIT, all with RELEASE and the IMPLIED closing; "3 takes" as no taking rule, MET(OLDEST), MET(NEWEST). The
   fold engine's seven named starts are `pm.STARS` (Ring(5,3), Ring(7,3), D2(5,3), two-knot, three-knot,
   three-knot-larger, generator7); made-2 to made-6 are as written (made-2 is the same start as the two-knot start; it
   is kept, so that the count is 648). Compared after every round: every knot's places (in order), parents, round made,
   kind and barred flags; each birth's kind, parents, inputs, takes, D, p, f, implied flag and fresh names; the groups
   and the short members; the closing; the stop and the guard's round and limit. The guard's "where" strings are
   written differently by the two engines and are not compared.
3. **The guard's checks are made in the fold engine's order** (incidences, a lower bound on pairs from the most members
   holding one distinction, C(m, 2) for the largest met set, pairs as they accumulate, maximal cliques as they are
   found, groups; then joins, births, the demand roster in the same order, and distinctions), so that "on which limit"
   (RD 3.3, item 8) is the same as the fold engine's. A stop happens exactly when some count passes its limit.
4. **The gate listing is read as rounds 1 to 3, with the knot test through round 3.** The listing gives rounds 1 and 2
   birth by birth, round 3 as a count, and "knot test: 80 verdicts" and "53 verdicts", which are the knot counts of
   rounds 0 to 3 summed (2 + 8 + 17 + 53 and 2 + 8 + 14 + 29). Under the registered bounds the a = 4 run stops at the
   guard in round 4 (pairs in the demand roster), but the a = 1 run reads a fourth round (105 joins; 5,460 pairs, under
   the guard). The listing is compared through round 3 only, with its knot test made on the run cut at round 3; the
   a = 1 run's fourth round is reported, not compared. (Seen before this item was written: a smoke run of the two
   listed cases, rounds and stops only.)
5. **Symmetric numberings (S2, RD 5.3).** No selection is given for the 100 pairs. Drawn with
   `random.Random('WBC-20261125-G-symmetric-pairs')`: h in {3, 4}, an underlying numbering, one of its marked entries,
   take and knot law, and a permutation σ that fixes e and permutes X's two loose names among themselves and Y's h loose
   names among themselves (not the identity). The second listing writes each knot's places as σ of the first's, in the
   same positions: the same named start (checked), places listed in another order. The marks (the usable names) are
   kept: the numbering is the same, so the marked entry is the same. Compared: every structure (places as sets),
   holders, bars, parents, kinds, rounds, every birth's inputs as a set, takes, D, p, f, implied, every value used at
   X's births, the course invariants through rounds 2 to 4, the meeting round and the stop.
6. **Suppliers.** RD 3.3 item 5 gives each candidate "the knot that supplies it". A candidate may be held by several
   knots that qualify (for a join, several common knots of its parents; for an offshoot, several knots its parent
   meets). Reading: every such knot is a supplier; the candidate's entry carries the set, and in attribution a differing
   candidate is replaced by all its suppliers.

## Patterns, bars, descent

7. **Y is Y_h, the h round-1 offshoots of Y's start knot, barred or not.** RD 2.1 names Y_h as the h offshoots; RD 2.3
   bars some of them. D 2.6 makes a knot made by round s "from Y only when it is a member of Y". Reading: all h are
   Y's knots and are "from Y only", whether barred or not; their descendants are the same either way (a barred member
   makes nothing). It matters only where a knot of X's descent takes a barred member's round-1 input (shared with Y's
   start knot): that take is then a meeting (RD 3.4) and the barred member is a knot of Y's descent in attribution. In
   the cells with a ≥ 1 the meeting is predicted at round 2 by a demand group, before any such take could matter; the
   a = 0 cells are where it can decide the meeting round, and every reported meeting says how it was found (group,
   demand group, take).
8. **When the bars are placed.** After round 1 and before round 2's roster (RD 2.3: "after round 1"). The structure
   kept as "after round 1" (for the loose counts of RD 3.1 and the knot test) includes the bars. Bars change no allowed
   state.
9. **X's start knot and Y's.** In made-h, h ≥ 3, X's start knot is the knot with three places and Y's the knot with
   h + 1 (RD 2.1), whichever is listed first; X is the two round-1 offshoots of the first, Y the h of the second; e is
   the one distinction both hold.

## What is read

10. **The canonical form (RD 3.1).** An exact isomorphism test, VF2 (networkx 3.6.1, `GraphMatcher` with node and edge
    labels), inside classes of an invariant (the numbers of knots and nodes, the multiset of node labels, and a
    Weisfeiler-Lehman hash, 4 iterations) that sorts them first; equal invariants never decide equality. The labelled
    structure is reduced exactly before the test: a distinction held by only one knot of the course has no link but
    to that knot, so it is written as a label on that knot (the multiset of such labels, each its origin and barred
    flag); a distinction held by two or more of the course's knots stays a node. Parent arcs are written as edges of
    their own type; since a knot's label holds its round and a parent is always of an earlier round, the direction is
    kept. Knot labels: round made, kind, number of places, and (usable, barred) loose counts after each round from
    max(round made, s) to R. Distinction labels: existing after round s; fresh of a knot from X only; fresh of any
    other knot; and barred at round R.
11. **The values used at X's births (RD 3.3) and their pairing between two runs.** Members and births pair by answers
    (RD 3.2). Groups have no answer of their own: a group of run A is paired with the group of run B whose members from
    X only answer A's (and, among several such, by rank in group order); this pairs (x, y) with (x, y′) when y and y′
    are two different knots from Y only, whose values (size and descents) RD compares. Entries of one step left without
    a pair are then paired by rank in that step's order, and any left over is paired with nothing. The order of
    entries is run A's (the run with the smaller a, RD 3.3), with B's left-over entries at the end of their step.
    **The differing part** of an entry: for a group, its members with no answer among the paired group's; for a member
    and for its act, the members of the groups containing it (its owing is read from them); for a birth, its parents
    with no answer among the paired birth's, or, when the parents answer, the parents that gave the loose inputs that
    differ; for a take, the candidates (each with its suppliers) with no answer in the other list, or, when the lists
    agree, the taken distinctions that differ, each replaced by its suppliers; for a demand, the members of its demand
    groups other than itself (its partners) with no answer among the other's. An entry paired with nothing has all its
    elements as its differing part. **Step 7** compares p, then the implied flag, then f; a difference in the implied
    flag is round-wide (RD 4.3). **Step 8** holds the closing (some birth of the round implied); there is no stall
    (no STALL treatment), and a round stopped by the guard is not read, so it has no entries.
12. **The linking knots (RD 3.5).** A met set "holds both a knot descended from X and one descended from Y" when some
    member of it is descended from X (from X only or from both) and some member is descended from Y; a knot from both
    counts as each. FD 5.7's class of a linking knot w: an ancestral common knot when, for some such met set of w, w is
    a recorded ancestor of a member u descended from X and of a member v descended from Y in it, and not the parent of
    both; otherwise "a knot the growth made that is no ancestor of both" when w was made after round 0; otherwise "a
    start knot that is no recorded ancestor of both" (through a start knot).
13. **The same meeting (RD 3.6).** The same meeting round; the same set of linking knots by answers; and the same
    births of X (births with a parent from X only), by answers, in rounds 2 to the meeting round, each with its kind,
    parents, loose inputs, takes and implied flag, and, in rounds before the meeting round, also D, p and f.
14. **Attribution is cut at the compared prefix.** Values are compared in rounds 2 to the compared prefix of the pair's
    two cells (RD 4.2); the first differing round, entry and class are kept for every pair, and a pair counts in a
    class when its courses differ through the compared prefix. Pairs whose courses do not differ are reported with
    their first differing entry, if any, apart.
15. **Handed in one value / composed / no difference (RD 4.4).** The compared prefix of the reading at fixed h is the
    longest prefix every run of the cells a = 1 … h at that h reached, for the take and knot law (RD 4.2 speaks of two
    cells; here there are h). A position is (round, step, the answers of its group, member or birth); a run in which
    the position does not occur gives it the value "absent". A position induces P when the partition of the a-marked
    entries over ν by its value equals P exactly. Every inducing position is listed; the first in step-major order
    names the verdict. Reported with it: whether the demand alone (the number D, without the descents of the partners)
    induces P, so that "the law hands a count over" (RD 4.4) is stated only when a count does it.
16. **FD's trace is reported in counts.** RD 3.1 asks for FD's trace and the joint births with every course. Each run
    record holds, for every round from 2, the births all of whose parents are descended from X, counted by (kind,
    number of parents, D, f), and the number of joint births (a parent descended from X and a parent descended from
    Y). FD's renamed trace is not written out.
17. **Run 1b against run 1.** "Run 1b equals run 1 under not-all-equal" (Q1) is decided by a fingerprint (BLAKE2b) of
    every structure after every round (places, bars, parents, kinds, rounds made) and the stop, compared entry by entry
    with run 1's run of the same entry, take and knot law.
18. **The negative control's h = 4 entries.** "One per cell" is read as the first entry of each cell in
    `numberings.json`'s list (the registered numbering, with the first a names left usable).
19. **The planted control's cells and run 2.** made-5 and made-6 have no marked lists; for 0 < a < h the a usable
    members are those whose inputs are the a smallest of Y's loose names on the registered numbering. In P and run 2,
    made-5 is run A and made-6 run B, start knots answering by order and start distinctions by name (RD 5.2).
20. **Q1's check.** Every short member of every round from 2 is listed with its round made; "only after an implied
    birth" is checked as: some earlier round of the same run had an implied birth.
21. **S4 is checked on every run of runs 1, 1b and 2**, a = 0 included (M = 0): J, the round-2 join of X's two members,
    exists; its candidates are exactly [e]; it takes e; D = f = 2 + M; it has 5 + M places; it is not implied; the
    number of round-2 births with a parent among Y's usable members is M; each takes one place of Y's start knot; Y's
    start knot meets J and each of them; every demand group holding J is a pair; J's partners are X's two round-2
    offshoots and those births; each of J's loose inputs has only its parent as another holder. S3's statements and
    S5's are read on the registered numbering.
22. **Process.** Six processes at most, four while the load is above 18 (read with `uptime` before each run); each
    process caps its address space at 6 GB (`resource.setrlimit`).

## Written after run G, N and P passed, before run 1

23. **Jobs and their order (run 1, 1b).** A job is one underlying numbering ν with all 2^h marked entries over it
    (a = 0 … h), under one law, so that the pairs (ν, A, B) and the reading at fixed h and ν are made where the runs
    are. Jobs go in the registered order of PR's table: OLDEST not-all-equal, OLDEST parity, NEWEST not-all-equal,
    NEWEST parity; within each, h = 3 then h = 4, ν in `made_class` order. Within a ν the entries go by a and then in
    list order. A cut, had one been needed, would have been at a whole block (take, knot law, h).
24. **Run G's wall time.** PR's table gives "< 3 min, 1 process" for run G; it took 196 s on 4 processes, most of it
    the fold engine and this engine on Ring(5, 3) under ORD with MET(NEWEST) (up to 45 s for the two together). Its
    outcome is not affected.
25. **Seen before run 1 (a test of the pipeline, not a registered output).** To check that the writer and the
    analysis run end to end, the four laws were run on ν = 0 and ν = 1 of h = 3 and h = 4 into my scratch folder, and
    the analysis was read on them. Seen: the cell verdicts on those two numberings; under NEWEST the pair (h − 1, h)
    first differs at a round-3 birth whose parents answer one another, where an X-only parent gives a different one of
    its own fresh distinctions (its births come in another order, since Y's round-2 births are named differently), so
    the differing part is all from X only and item 11's reading classes it "unclassified". No reading was changed after
    this was seen. Also seen while timing: the sizes and times of single runs (the knot test, FD 7's birth method,
    takes up to 40 s on runs whose round-4 knots hold 700 to 870 places under NEWEST and not-all-equal).
26. **Sizing and the hour.** A timed sample of 25 jobs (random numberings, knot test included, 4 processes, load about
    20) gives about 9,000 CPU seconds for run 1, about 38 minutes on 4 processes; the load is above 18, so 4 processes.
    No cut is made. Fixed before the run: should run 1 pass 60 minutes of wall time, it is stopped (by its own process
    numbers) and what was written by then, a prefix of the registered order by whole jobs (`imap` returns jobs in
    order), is kept, the rest reported as not run.
27. **Import order (a fault repaired before run 1, no output affected).** `wbc.py` first put the fold engine's folder
    at the head of `sys.path`; that folder has its own `common.py`, which would have shadowed this folder's had it been
    imported after `wbc`. Every script here imports `common` first, so runs G, N and P were unaffected; the folder is
    now appended instead.

## Written after run 1 was stopped, before runs 1b and 2

28. **Run 1 was cut at the hour (item 26), not completed.** The load on the host rose from about 20 at the start to
    about 36, and the NEWEST not-all-equal h = 4 block cost 58 CPU seconds per job (10,784 s for 185 jobs; the sample
    of item 26 had given 21), almost all of it the knot test. At 60 minutes run 1 was stopped by SIGINT to its own main
    process (PID 2076135; its four workers, 2076141 to 2076144, ended with it); every output was closed properly and
    holds whole jobs only. **Run** (a prefix of the registered order, 965 of 1,320 jobs, 12,560 of 17,280 runs):
    OLDEST not-all-equal (h = 3 and 4, every numbering), OLDEST parity (every numbering), NEWEST not-all-equal h = 3
    (every numbering), NEWEST not-all-equal h = 4 on numberings 0 to 184 of 210. **Not run**: NEWEST not-all-equal
    h = 4 on numberings 185 to 209 (25 numberings, 400 runs), and NEWEST parity entirely (h = 3 and 4, 4,320 runs).
    Cells of NEWEST not-all-equal h = 4 are read over the 185 numberings run and stated so ("among 185 numberings run,
    25 not run"); they are not "whatever the numbering". Nothing of NEWEST parity is reported, and no prediction is
    judged on it. `analyze.py` rebuilds run 1's index from the per-run records (the index file is written only at a
    normal end) and keeps only jobs with all their records, pairs and readings.
29. **Runs 1b and 2.** Run 1b (h = 3 only) is estimated from run 1's own per-run times at about 2,000 CPU seconds;
    run with 3 processes, and run 2 (one process) beside it, 4 in all while the load is above 18. The hour rule of item
    26 holds for each: stopped at 60 minutes, the written prefix kept, the rest reported as not run.

## Written after every run, from what the runs showed (no reading changed)

30. **Found in the frozen texts.**
    - PR's sizing ("NEWEST, not-all-equal: 0.06 to 1.04 s, max 4.6"; run 1 "about 18 minutes") understates this
      engine's cost by far: the knot test (FD 7's birth method, `knots.py` unchanged) took up to 125 s on one run, and
      run 1 needed more than an hour at the host's load, so it was cut (item 28). The structures themselves are the
      fold engine's (run G).
    - RD 4.4 defines P over the marked entries; PR's Q3 speaks of "the partition of the a's". Under names, entries with
      the same a on one ν can have different courses: P had up to 8 classes over a = 1 … 4. RD's wording is followed.
    - S3's "every round-2 birth takes e" holds under OLDEST only: under NEWEST, X's round-2 offshoots take the other
      place of X's start knot (their D is 2, not 2 + M). Q2's NEWEST clause concerns J alone, which takes e (its sole
      candidate) under both takes.
    - Item 7's reading decides the meeting round of some a = 0 runs: there X's descendants take a barred Y member's
      round-1 input in round 3 (a meeting by a take, RD 3.4), so those runs meet at round 3; with Y read as only the
      usable members they would not meet. No prediction rests on a = 0 meetings.
    - No birth was implied in any run of runs 1, 1b or 2 under parity, so the parity clause of S1 was not exercised;
      no member was short after round 1 in any run.
31. **Run 1b and run 1.** Run 1b's NEWEST parity runs have no run-1 counterpart (not run in run 1); they are reported
    as run 1b's own, never in place of run 1's.

## Written before the resumed part of run 1

32. **Run 1 resumed after its cut, for take-the-newest under parity only.** Asked for by the thread that froze the
    study, because the one cell with no prediction, (h − 1, h) under take-the-newest, had been read under not-all-equal
    only. The same code and law, the same jobs in the registered order (h = 3 in full, then h = 4, numberings in
    `made_class` order), 4,320 runs, 4 processes, written as the second part of run 1 (`run1r_*` files; `runs.py 1r`).
    Timed first, under the present load (about 19): 40 runs (h = 3 numbering 0; h = 4 numberings 0 and 84, the second
    drawn with `random.Random('WBC-20261125-time-newest-parity')`) took 0.006 s a run at h = 3 and 0.009 to 0.2 s a run
    at h = 4 (jobs of 0.2 to 3.3 s); with item 26's earlier sample (h = 4 jobs of 2.8 to 7.6 s) the whole is at most
    about 1,000 CPU seconds, about 4 minutes on 4 processes, so it is run in full. Fixed before it starts: should it
    still be running at 25 minutes, it is stopped by its own process number and the written prefix of that order is
    kept, the rest reported as not run. The 400 runs of take-the-newest under not-all-equal at h = 4 (numberings 185
    to 209) are not resumed and stay "not run". Course classes of the resumed part are its own (each law has its own
    classes, so nothing is compared across the two parts).
33. **After the resumed part (written after it ran).** It ran in full in 135 s of wall time (499 CPU seconds), 4,320
    runs, no stop. With it, item 31 no longer holds: run 1b's NEWEST parity runs (OFFSHOOT and WAIT) equal the resumed
    part's runs (RETIRE) on 1,920 of 1,920 by fingerprint, as S1 says they must when no member is short. Run 1 is now
    16,880 of its 17,280 runs; the 400 runs of item 28 (NEWEST not-all-equal, h = 4, numberings 185 to 209) stay not
    run, as the thread asked.
