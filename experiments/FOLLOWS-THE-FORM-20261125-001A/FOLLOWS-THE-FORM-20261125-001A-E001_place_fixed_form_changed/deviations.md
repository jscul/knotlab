# Readings and deviations

Ticket `FOLLOWS-THE-FORM-20261125-001A`, experiment `FOLLOWS-THE-FORM-20261125-001A-E001`. Each entry says when it was
written relative to the runs. Entries 1 to 27 were written on 25 November 2026 after reading the frozen texts and the
engines' interfaces and before any registered run (R0 included); the program was tried only on single starts while it
was written (the probe of the engine's interface on the start B with `one:2`, and the timing parts of entry 28 onward).

## Readings of the frozen texts (before any run)

1. **Order of laws.** "Laws in the order of FF 1 with no taking rule first" is read as: the taking rule outermost
   (none, then MET-SOLE), then the ration in FF 1's order (FLOOR1, CAP-3, ORD), then the treatment in FF 1's order
   (CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT). FF 1 does not say whether the ration or the treatment varies
   faster; ration outer is the order FF 1 names them in.
2. **Registered order of runs.** The three keys of the cut order are read as nested, outermost first: first seeds in
   alphabetical order, then laws (entry 1), then second seeds in the order of the data file. Within a study the bare
   start comes first (FF 6 lists it first). In R1, where the first seeds A to E carry two families, the families come
   between the first seed and the law, in the order R1's row lists them (`mixed`, then `chains`). For R0's
   population the runs of R1 come before those of R2.
3. **Samples.** "Python's `random.Random(seed).sample` over the runs in registered order": one `random.Random(seed)`
   instance per named seed, its `.sample(population, k)` calls made in the order the text lists the samples, each
   population the list of runs in registered order.
   - R0, seed 1: `rng.sample(R1 + R2, 400)`.
   - R5 renumbering, seed 2: `rng.sample(R2 runs with no taking rule, 100)`, then `rng.sample(R2 runs with the take,
     100)` with the same instance; seed 7: `rng.sample(R4, 100)`.
   - R5 knot test, seed 6: `rng.sample(R2, 200)`, then `rng.sample(R4, 100)` with the same instance.
4. **Renumberings (FF 10).** Renumbering j = 1, 2, 3 uses one `random.Random(s)` instance, s = 3, 4, 5, consumed over
   the 300 sampled runs in this order: the R2 runs with no taking rule (in sample order), the R2 runs with the take, the
   R4 runs. For each run: the list of the start's names is shuffled (name i goes to the i-th entry of the shuffled
   list), then each knot's place list is shuffled (knots in their order), then the order of the knots is shuffled;
   which knots are the first seed's and which the second's is carried along. Compared with the unrenumbered run:
   rounds read, the stop, and what the first seed's descent makes through every round read (not only through R\*);
   the wider record and the second seed's own births are compared too and reported, not predicted.
5. **The bare start in R2u.** The bare start has no second seed, so "every start replaced by its unlinked start"
   leaves it as it is; it is grown again as a run of R2u (5,490 runs, as registered).
6. **Start knots in the roster (FF 8, PR4).** A start knot is a member of round t's roster when the engine's record of
   round t lists it among the members (rounds 1 to the last read). The roster that the round after the last read would
   start with is also read, on the final structure (a start knot holding a usable loose distinction there). PR4 fails
   if either shows a start knot after round 1. "Every run" includes the bare starts.
7. **Pairs, classes.** Classes are taken at the study's R\* on all its runs; "classes among the forms" leave the bare
   start out. Every pair count (first told apart, after the first round, told apart at R\*, depth) is over pairs of
   forms, never with the bare start, as the disclosed counts are (18,375 = 15 x C(50, 2)).
8. **First told apart.** For a pair, r is the smaller of the two rounds read; the pair is first told apart in the
   least round t <= r whose multiset differs; else "never" if r = L of the study, else "not read further".
9. **After the first round** (FF 6) and the disclosed table's last column: a pair first told apart in round 2 or later
   whose wider records of round 1 are the same; and, for the last column, a pair first told apart in round 3 or later
   whose wider records of rounds 1 and 2 are the same.
10. **Count profile (FF 11).** The held knot is (its number of places in the start = its length in the seed plus one,
    the number of its distinctions held by no other knot of the seed, the number of other knots of the seed sharing a
    distinction with it). The second seed's births by round is the vector of the counts of births of the second and
    not of the first, rounds 1 to R\*. "Both" is the pair of the two. "A function of" is judged over the forms of the
    study (the bare start has no profile), with the classes among the forms at R\*.
11. **Fates (FF 7).** Read for each form (the bare start left out, as the disclosed counts are 50 a study); in a study
    with R\* < 4 every form is "not read". The labels are the disclosed table's: "ends, no births", "ends, taken up",
    "steady", "grows", "shrinks", "other", "not read". For PN5 a study counts when its forms show at least two of the
    three: ends (either kind), steady, grows.
12. **What it makes (FF 5).** An entry is (kind, number of parents, number of places, f, number of takes); the number
    of places is the length of the newborn's place list in the engine's structure, checked equal to its loose
    distinctions plus its takes plus f at every birth. The parents are the engine's `parents`, checked to be the knots
    that each gave it one loose distinction.
13. **Bounds.** R_max = 10 for the family `chains` (R1's chain studies and R3) and 9 otherwise; the knot bound 3,000
    (`eng.Run(..., knot_bound=3000)`); the guard at ticket B's limits (multiplier 1).
14. **PR1.** Compared exactly: R\* and the partition of the study's runs into classes (bare start written "(none)"),
    as a set of sets of names. The disclosed "runs read by round" is compared too and reported, not part of PR1.
15. **PR2, PR5.** Each cell of each table compared exactly with `disclosed.json`; a key present on one side only
    counts as a differing cell (a missing key is read as 0 only for reporting the value).
16. **Depth (FF 9).** The loose counts of a chain are read from its knots (checked against its name); depth i is the
    knot i steps from the held knot, the first knot. Pairs at depth i: same length, counts equal except at index i,
    where one has 2 and the other 3. Lengths n and n + 1: the longer chain's first n counts equal the shorter's. Told
    apart: in different classes at the R\* of the pair's own study. Pooled over the first seeds of the run, per law.
17. **S3.** The cell "1 against 2 knots" of R3's depth table, per law (20 pairs a law over K to O); it holds when all
    20 are told apart under each of the 18 laws.
18. **PD1, PD2.** Per law. PD1: each of the cells depth 2, depth 3, depth 4 at most 10% (inclusive), "3 against 4
    knots" at most 30%, "4 against 5 knots" at most 15%, for the 9 laws with no taking rule. PD2: "4 against 5 knots"
    at least 15% (inclusive) under (sole, ORD, each treatment) and (sole, CAP-3, CANCEL-WAIT).
19. **PN3.** "Told apart after the first round" (FF 6) counted per row over pairs of forms; a row needs at least 50.
20. **PN4.** Per row: pairs of forms in different classes among the forms at R\*, divided by all pairs of forms of the
    row (26,550); it holds when every row is within 45% to 95%, inclusive.
21. **PN2, PN6, S2.** The number of classes among the forms at R\*.
22. **CU.** In each R2u study: every form's run is in the class of the bare start (the same make through R\* of the R2u
    study).
23. **C2, the knot test.** Ticket B's routine as its `read.py` calls it for a full test:
    `knots.test_run(run.snaps, run.law)` with the engine's law (every knot at every round 0 to the last read). A failing
    knot is an entry of its `fails`; its `disagree` and `untested` are reported apart and are not failures.
24. **R0, second growth (no taking rule).** The fold engine `pm` grows the same start
    (`pm.Run(pm.from_stars(stars), pm.Law(ration, treatment, release='RELEASE', knot_law, closing='IMPLIED',
    take=None), rounds=R_max, knot_bound=3000)`), as ticket B's `gate.py` drives it. Compared after every round:
    places, parents, made, kind and barred, exactly (the two engines number knots and distinctions alike), and the
    rounds read and the stop. A Weisfeiler-Leman invariant (4 iterations, over knots and distinctions with knot labels
    (made, kind, number of parents) and distinction labels (barred, number of holders), and parent links) is also
    computed for each round; if the exact comparison failed where the invariant agreed, the run would be reported as
    "not distinguished by the invariant", and the gate judged on the invariant, stated as such.
25. **R0, takes (the take of a sole candidate).** For every birth of every round read of a sampled run with the take,
    the candidates are recomputed from the rule's words on the structure at the start of the round (the engine's
    `snaps[t-1]`, with holders rebuilt from the place lists by this program): for an offshoot of parent p, the
    distinctions with two or more holders held by a knot that p meets and not held by p; for a join, those with two or
    more holders held by a knot that meets every parent and held by no parent (FD 3.3, MET's clauses; BD2 2.1). The
    birth takes the candidate if there is exactly one, else nothing; compared with the engine's `takes`. For sampled
    runs with no taking rule it is also checked that no birth took anything.
26. **Processes.** Each run set is split into 8 chunks by index modulo 8 in the registered order; 8 processes, one per
    chunk, each under `RLIMIT_AS` = 6 GB; no other process works during a run set. Wall time of a run set: from the
    launch of its chunks to the end of the last.
27. **Wider record classes.** Reported for R1 and R2 (no prediction): the number of classes among the forms by the
    wider record at R\*, and the number of studies where it is greater than, equal to, or less than the number by the
    own descent.

## Timings, estimates and cuts (each written before the run it concerns)

28. **R0** (written before R0). Timed: 16 of the 400 sampled runs in one process, 0.054 s a run, so about 3 s on 8
    processes (the probe's estimate was 2 min). Cap used so far: about 1 s of timing. No cut.
29. **R0 result before R1** (written after R0, before R1): R0 took 10.4 s of wall time on 8 processes. **R1**
    (written before R1): timed a systematic sample (every 100th run of the registered order, 137 runs) in one process,
    0.027 s a run, slowest 0.57 s; estimate 0.8 min on 8 processes. Cap used so far: under 1 min. No cut.
30. **R1 result on time; R2** (written after R1, before R2). R1 took 193.7 s of wall time on 8 processes, against
    the 0.8 min estimate: its sum of run seconds was 976 s, 899 of them under the take with ORD (one run of 68.5 s),
    and the systematic sample had missed that tail. Estimates from here are also scaled from R1's measured sums.
    R2: a systematic sample of 220 runs (every 25th), 0.064 s a run, slowest 3.9 s, so 0.7 min on 8 processes; scaled
    from R1 (its 2,280 runs under the take with ORD took 899 s; R2 has 915), about 2 to 3 min. Cap used so far:
    about 4 min of 60. No cut.
31. **R2 on time; R2u** (written after R2, before R2u). R2 took 144.6 s of wall time (sum of run seconds 444 s; two
    runs of 94 s and 102 s set the wall). R2u: a systematic sample of 220 runs, 0.038 s a run (0.4 min on 8
    processes); allowing for single long runs as in R2, about 2 to 3 min. Cap used so far: about 6.5 min. No cut.
32. **R2u on time; R3** (written after R2u, before R3). R2u took 55.2 s of wall time. R3: a systematic sample of 227
    runs, 0.058 s a run (0.7 min on 8 processes); R1's chain studies (5,670 runs, the same count) took a sum of
    562 s with runs up to 68.5 s, so about 1.5 to 3 min. Cap used so far: about 7.7 min. No cut.
33. **R3 on time; R4** (written after R3, before R4). R3 took 69.5 s of wall time. R4: a systematic sample of 220
    runs under parity, 0.064 s a run, slowest 3.9 s, the same as R2's sample; by R2's measured wall, about 2.5 min.
    Cap used so far: about 9.2 min. No cut.
34. **R4 on time; R5** (written after R4, before R5). R4 took 146.7 s of wall time. R5 timed (3.6 min of wall time
    in one process, counted against the cap): 30 renumbering jobs, 0.01 s a job (900 jobs: 0.2 min of one process);
    12 knot-test jobs, 17.8 s a job, slowest 122 s (300 jobs: 89 min of one process, about 11 min on 8 processes,
    more with imbalance; the probe's estimate was 7 min). Cap used so far, timings included: about 16 min of 60, so
    about 44 min left; the estimate is within it and the registered cut (the knot test to half) is not made. For
    balance only, the knot-test jobs are given to the 8 processes longest first by a size predicted from the original
    run (final knots times rounds read); the renumbering jobs by index modulo 8. This changes no result.
35. **R5 cut during the run** (written at 00:05 UTC on 26 November, 14 min into R5, after the renumbering was
    complete and before any further knot test was started; honestly: after the run had begun, not before it). The
    estimate of entry 34 was wrong: its 12 timed knot-test jobs missed the largest runs, and two single knot tests (of
    a 3,770-knot run and a 1,986-knot run under ORD) each took more than 11 min, the direct test of every knot of up to
    12 places at every round dominating. At that point 900 of 900 renumbering jobs and 241 of 300 knot-test jobs were
    done, and the cap used was about 28.5 min of 60 (R0 to R4 10.3 min, timings 4.5 min, R5 13.7 min). The remaining
    jobs would pass the cap, so the registered cut is applied: **R5's knot test to half**, a prefix of each sample in
    sample order (the first 100 of the 200 R2 runs, jobs 900 to 999; the first 50 of the 100 R4 runs, jobs 1100 to
    1149). C2 is judged on the knot tests of that half that finish within the cap; any job of the half not finished is
    reported "not run". Knot tests outside the half that had already finished (114) are reported apart, not as part
    of the registered row; the 36 outside the half not yet run are "not run". To finish the half, the process of chunk
    3 (on a small job outside the half) is stopped by its process number, the process of chunk 0 keeps its job in
    progress (job 941, in the half), and 7 new processes take the other 22 jobs of the half, longest first by the
    predicted size; 8 processes in all. Every R5 process is stopped at 00:33 UTC at the latest, leaving the cap's last
    minutes for the readings; a result is kept only for a job that finished, and a job finished twice is counted once.
36. **R5 closed** (written after R5, before the final readings). R5 took 2,536.6 s of wall time (23:50:47 to
    00:33:04 UTC): the 7 added processes finished the 22 jobs of the half they took by 00:12:01; job 941 (the knot
    test of `R2|nae|fresh|L|none|ORD|CANCEL-WAIT|ring:3,1,3,1@0`, a run of 3,770 knots read through 9 rounds) had not
    finished at the deadline after 42 min and its process was stopped by its process number: it is "not run". The
    renumbering is complete (900 of 900). The cap used for the ticket: R0 to R4 620 s, R5 2,537 s, timing parts about
    270 s, readings about 30 s: about 57.6 min of 60. No run was added after its outcome was seen.
