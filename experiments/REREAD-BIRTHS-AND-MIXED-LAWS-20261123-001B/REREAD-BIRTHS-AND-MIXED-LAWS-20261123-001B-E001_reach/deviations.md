# Deviations, readings and limits: REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001

Every definition in "Definitions (frozen)" and "Predictions (frozen)" of
`research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/preregistration.md` is unchanged. Where the note could be read two
ways, the reading taken is listed here. One statement of the note's "Settled by construction" section was checked and
found false beyond the first round (item 4); the frozen version is the primary run and a second version is reported
beside it, with both sets of numbers. Nothing was tuned after values were seen. Code is in this folder; outputs in
`artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/`. Recorded
code is imported or copied, never edited; each copy is marked COPIED in the file that holds it (`common.py`,
`verify_excess.py`).

## Readings taken

1. **Targets.** All 292 entries of THIRD-HOLDER-20261123-001B's `structures_found.json`, in file order (target id = list
   position). The seven-knot structure of its result note is entry 0, the pencil 9-knot structure entry 291, the 18-knot
   structure entry 290; all three are in the list, so the list is the whole target set. Entries are distinct as knot lists;
   no further identification up to renaming was made. Each target's table of old allowed words is computed here (by
   contraction, equal to full enumeration on all 292).
2. **Founder starts with a distinction held three or more times.** 252 targets have one, and 37,814 of the 49,961 founder
   starts keep all its holders. The recorded `end_operator.from_stars` accepts one or two holders only. Reading: every two
   holders of a shared distinction meet (`common.from_stars_ext`); on the 12,147 starts with at most two holders it gives
   exactly the recorded function's end (gate E1). Ordinary growth itself never makes a third holder.
3. **Stop.** Growth runs round by round; after a round, a stage with more than 20 distinctions is kept and tested, and no
   further round is made; at most 3 rounds. Stage 0 (the founder start) is tested as a stage in T1 and in T2. A round
   that stalls (the engine's whole-round stall) or a start with no live knot ends the history. All founder starts hold a
   not-all-equal founder, so every target history uses the not-all-equal structure rule (checked: 0 starts without one).
4. **The parity sign of a newborn is not always a renaming (checked, false at stages 2 and 3).** The note settles by
   construction that "a newborn has a fresh distinction, so its parity sign is a renaming of that distinction: a
   newborn's law is parity or not-all-equal, two choices". `sign_check.py` compared, on every history of the ten
   targets of 7 knots and the pencil with at most 9 newborns (153 of their 185 histories, 361 stages; the 32 with more
   newborns were left out to keep 3^n small), the set of observer tables met under even / odd / not-all-equal with the
   set met under even / not-all-equal. At stage 0 (153 stages) and stage 1 (100) they are equal; at all 88 stage-2 and all
   20 stage-3 stages the three choices give tables the two choices do not (never the reverse), confirmed word by word
   on one stage (`sign_check.json`, `brute_force_confirmation`). The reason: a renaming of a newborn's fresh distinction
   also changes the knot of the next round that takes that distinction, and a not-all-equal knot with one place renamed is
   not a not-all-equal knot. So the frozen two-choice enumeration (**version c2**, primary) is run as written, and a second
   version (**c3**: even, odd or not-all-equal for every newborn, the same cap of 4,096 per history and the same draw rule)
   is run beside it for T1 and T2. Both are reported.
5. **Law assignments.** Column j of an assignment is the j-th newborn in birth order; the assignment of a stage is the
   prefix of the newborns born by then (distinct prefixes only). When 2^n (c3: 3^n) exceeds 4,096, 4,096 distinct
   assignments are drawn by `numpy.random.default_rng([2026112340, target id, start bitmask])` (c3:
   `[2026112340, 3, target id, start bitmask]`), one generator per history so each history is reproducible in any chunk.
   Drawn: 26 histories in c2 (13 newborns), 2,111 in c3.
6. **Which loose distinction a birth takes** (a scaffold the note leaves to the operator). The engine decides parents and
   fresh counts; the recorded wrapper (`REVIEW-LEADS-20261123-001A lib.grow`) hands each birth the last remaining loose
   distinction of each parent in the knot's listed order, and that rule is used. Loose distinctions of one founder are
   interchangeable for the engine but not for the observer table when one of them is an observer distinction. Other
   placements were **not enumerated**. They cannot change P1 (the support of the start's table does not depend on the
   placement, and growth keeps it). In 27 of the 34 histories with a new hidden excess (version c2), the smallest
   included, no founder holds two or more loose distinctions of which one is an observer distinction, so the rule made no
   choice that the table could see; in the other 7 it did, and other placements of those 7 were not tried.
7. **Founder laws.** Founders keep their target's law and sign. In the draws (T2), "under both laws" is read as every
   founder even parity, or every founder not-all-equal (ticket A's two laws; its settled statement uses even signs).
8. **Draws.** The 1,024 sparse draws of `lib.p3_draws(seed 2026112301)`; funded = the first round extends (not a stall,
   some live knot): 280 under each law, as recorded by ticket A. "The first two stages" = stage 0 and stage 1. Under even
   founders a round whose only birth takes every loose distinction is a closing birth when that newborn is parity: it
   receives no fresh distinction and its sign is the implied one (checked constant on all allowed words in all 61 cases);
   when it is not-all-equal the not-all-equal rule applies (fresh distinctions as the engine gives them). The parity and
   not-all-equal engines gave the same births on all 219 other first rounds under even founders.
9. **Gate part 3, "support never shrinks along any history".** Target histories: the support of the observer table at
   each stage is compared with the stage before under the same assignment of the earlier newborns, for every assignment
   of every history, both versions (`support_shrinks`, `support_changes` in the T1 lines). Draw histories: the allowed
   set on the start's distinctions after forgetting the fresh ones, stage 1 against stage 0, every assignment, both
   versions (`support_draws.py`; it uses that the round-1 newborns hold disjoint inputs, so the check reduces to each
   newborn's factor; stated in its docstring).
10. **Gate part 1** compares the computed table with the census's recorded table up to one of the 32 symmetries of the
    evaluation, because the census stored the table of its orbit representative (THIRD-HOLDER deviations item 3). The
    first run of `gates.py` required equality as stored and reported a failure of that extra clause on all 290 recorded
    tables, with the frozen clauses (score, hidden) passing 292 of 292; the corrected comparison matches all 290. The log
    of the first run was overwritten by the second; nothing else changed between the two runs.
11. **Gate part 2**: the 100 stages are drawn by `numpy.random.default_rng(2026112341)` among grown stages (t >= 1) of at
    most 24 distinctions, one random assignment each.
12. **P2 has a trivial failure, and the finding is read beside it.** 630 founder starts already have a hidden excess at
    stage 0 under the target's observers (a target that contains a smaller structure of the list, for example the
    seven-knot structure inside an 8-knot target). By the frozen wording P2 fails on them at stage 0. The result note
    therefore also reports the reading that carries the question: a hidden excess in a grown stage (t >= 1) of a start
    whose stage 0 has none ("new excess").
13. **T2 symmetry.** Each unordered observer choice (x2/x3 unordered, y2/y3 unordered, Alice and Bob exchangeable) is
    tested once and stands for 8 ordered choices. The 8 orientations were evaluated on 2,073 drawn tables per version
    (seed 2026112342): equal hiding and equal score in every one.
14. **T2 inheritance.** A hidden excess at a grown stage is called inherited when the same observer choice (same
    distinctions) already gives a hidden excess at stage 0 of the same history.
15. **Exact arithmetic.** Hiding is decided in integers (int64 products bounded, or Python integers for large entries).
    The score is screened in floating point and every hidden table with a float score of at least 2 - 1e-6 is scored
    exactly in fractions (`exact_best`); an excess is an exact score above 2. A table whose float score is below
    2 - 1e-6 has exact score at most 2 (the float error is below 1e-12). Proportionality is tested by exact
    cross-multiplication.
16. **Verification by full enumeration.** Every new hidden excess with at most 29 distinctions in its stage was verified by
    enumerating every word of its four finished structures (stage word, za, zb), with the stage's knots checked once per
    stage word and the setting births per (a, b, za, zb) (`verify_excess.brute_joint_all`); on stages of at most 22
    distinctions it was also compared with the separate enumeration of each finished structure (`brute_joint`, COPIED).
    The 32 tables of one history with 32 distinctions (start 20633) were not enumerated (each would take about
    4 x 10^9 words); they rest on the contraction, which agreed with full enumeration on the gate stages and on every
    stage that was enumerated. Result: c2, 322 of 354 tables enumerated, every one hidden with an exact score above 2 and
    equal to the contraction. `grow_t1.py` writes at most 50 tables of each kind (proportional, new excess) per stage in
    full and counts all; in c2 no stage reached that cap for new-excess tables (some did for proportional ones), in c3 957 of the 1,212 new-excess tables were written. c3: 857
    of the 957 enumerated, same result; the 100 on stages of 29 and 32 distinctions were not enumerated.
17. **Runs stopped by the limit.** The first verification attempts (one process per range, with the separate enumeration of
    each finished structure, and a second attempt while the shared machine carried a load near 16) reached the ten-minute
    limit and wrote nothing; their empty logs are kept as `verify_c2_*_killed_by_limit.log`. They were repeated in smaller
    runs (`verify_c2_jobs.txt`, at most six at once). There, the runs of two stages of 29 distinctions each reached the
    limit (five, marked FAILED in `verify_c2_runs.log`) or were stopped by hand once that was seen (three, two of them
    marked FAILED); all 16 were repeated one stage per run, three at once (`verify_c2_jobs_d29.txt`,
    `verify_c2_runs_d29.log`); all 16 finished. In c3 one run of ten stages of 26 distinctions reached the limit and was
    repeated as two runs of five (`verify_c3_jobs_redo.txt`); the shell holding the c3 queue reached its own 30-minute
    background limit and was stopped with five runs of stages of 27 distinctions unfinished or unstarted; those were run
    again from `verify_rest_jobs.txt` (`verify_rest_runs.log`). A first form of `support_draws.py` (contracting on every
    start distinction for every assignment) reached the limit and was replaced by the exact reduction of item 9. No other
    run was stopped.
18. **Development runs.** Two timing chunks of `grow_t1.py` (tag `test`) were run before the final runs and deleted;
    `measure_growth.py` (growth sizes only, no tables) was run to plan the chunks. One unwrapped check of item 4 was
    started without the time and memory wrapper and stopped after two minutes; it wrote nothing and was redone inside
    `sign_check.py`.
19. **Scripts.** "One script builds the targets and founder starts" = `build_targets.py`; "one grows and tests T1" =
    `grow_t1.py` (`--choices 2` primary, `--choices 3` second version); "one runs T2" = `t2.py` (`--pop targets` and
    `--pop draws`). Checks: `gates.py` (row G parts 1, 2 and E1 to E3), `sign_check.py` (item 4), `support_draws.py`
    (item 9), `verify_excess.py` and `verify_t2.py` (full enumeration), `seven_reasons.py` (the seven-knot founder starts),
    `report.py` (summary.json).
