# Readings and deviations, GUARD-CAP-AND-HOLD-20261124-001A-E001

Written by the engine's author (the helper agent that wrote the engine of `LOCAL-ROUND-20261123-001A`) after the gate
(run 1) and before any registered search (runs 2 to 6). The SHA-256 sums of the four frozen texts and of the reference
engine were checked against `contract.json` before any code was written, and they matched. `lr_reference.py` checks
the engine's sum again on every import. No frozen text, earlier study's file or the reference engine was changed.
"GCH" is `research/GUARD-CAP-AND-HOLD-20261124-001/definitions.md`, "LR" the earlier study's definitions, and "the
pre-registration" `research/GUARD-CAP-AND-HOLD-20261124-001A/preregistration.md`.

## The engine

1. **Copied, then extended.** `lr_core.py`, `lr_reference.py`, `lr_laws.py`, `lr_search.py` and `test_lr.py` were
   copied from `experiments/LOCAL-ROUND-20261123-001A/.../` and extended here; the originals are untouched. The earlier
   study's unit checks (`test_lr.py`) pass on the extended modules. The extended engine also reproduces exactly the
   earlier study's key counts on eight of its runs (R1, R2, R3 on D2(4,3) under (RATION-3, CANCEL-WAIT): 67,353,
   65,803 and 65,791; two-knot (FLOOR1, CANCEL-RETIRE) R1: 400; three-knot (FLOOR1, CANCEL-OFFSHOOT) R1 at round 3:
   9,260; the control on the cycle of eight: 8,207, and on the two-knot start at round 3: 4,247; T(3) on D2(4,3): 515).
   The earlier study's R0 and R3L are not used here and were not carried over.
2. **The representation is unchanged.** A run's knots are named by their images under m, and a state is the memo key
   (images, barred images) (earlier study's deviations, items 1 and 2). The key stays valid here: each image fixes a
   knot's parents, its fresh count and the number of its places barred at birth (GCH section 2), and under holding what
   a stayer still holds is its h0 less its children.
3. **The earlier study's readings carry over** where they apply: items 3 (a knot does not meet itself), 6 (barrings
   only for knots born by round r), 7 (barrings made all at once, then read again), 9, 10, 13 (T(d)), 14 (the control),
   16 (the closing bit), 17 (seeds, x-last orders over every knot that exists by round 1), 24 (groups of three or more)
   and 26 (numbering in listings). Item 8 is extended in item 7 below.

## The cap and the fillers (GCH sections 1 and 2)

4. **The engine's own complete round, "computed through the plan".** One reading (LR 2.1, steps 1 to 4, with GCH
   section 3 item 1 under HOLD) of the live roster, with its present holdings and met sets. The births are those of
   that reading, with that reading's D, f and usable counts. Short members retire under CANCEL-RETIRE, with their
   usable distinctions barred; waiters and stayers keep what they hold. The closing exception applies to a lone birth
   that takes every loose distinction. The shared definitions' step 6 is never used by the engine. Only the reference
   uses it, and the gate compares the two.
5. **h0 and "barred at birth".** h0 = places − parents − places barred at birth, read for every law. Where nothing is
   barred at birth this is LR's h0. The number of places barred at birth is taken from the reference's round records
   (each birth's `barred`), not from the final barred state, because under CANCEL-RETIRE a retirement also bars
   distinctions. On the run's side it is f − u, both from the plan (GCH section 2).
6. **The match** uses the images of the parents, f, and the number of places barred at birth, with the earliest round
   first and then the least number (GCH section 2 and section 3, item 7). The rule is used for every law; where all
   candidates are born in one round, as under RELEASE, it is LR's least-numbered rule.
7. **An allowed birth is a triple** (parents, f, usable fresh count). The sampled and x-last orders choose uniformly
   among the distinct triples allowed (this extends the earlier item 8). Under holding, one member can have offshoots
   planned in two readings with two fresh counts, and both may be allowed at once.
8. **Made births are subtracted by kind** (LR 2.3, read with GCH section 3, item 3). A plan's births form a multiset
   keyed by (parents, f, usable), counted over every reading. A planned birth of a kind is made, up to its number, by
   knots with exactly those parents, that fresh count and that number of places barred at birth. Under RELEASE this is
   LR's rule, since each kind there has one fresh count. Under holding the same join could be planned in two readings,
   and it is then counted twice.

## Holding (GCH section 3)

9. **Idle parts** are tested in every reading, the first one included, under every treatment ("a reading of a part
   that plans no birth and no retirement"). Under RELEASE with waiting an idle part is exactly LR's all-short part.
   It is labelled `allshort` when every member is short and `idle` otherwise. Its stayers and waiters are recorded for
   that reading and are not read again.
10. **Stayers.** A member that is not short has its holding less all its groups (kept and cancelled) as planned
    offshoots, and keeps one distinction for each cancelled group. With at least one kept it is a stayer, and the
    waiters' and stayers' roster carries it with what it kept. Under CANCEL-RETIRE and CANCEL-OFFSHOOT only stayers are
    carried.
11. **The barring match under holding.** LR's rule ("m(x) holds barred distinctions in the reference and has no children
    there") would call every retirement of a stayer that had made children a mismatch. Under holding, a barring of x
    matches when m(x) is recorded as retiring in a round of the reference and every reference child of m(x) is already
    an image, so that the barred count is the reference's. Under RELEASE a retiring knot has no children, and this is
    LR's rule.
12. **A stayer that retires in a later reading** (CANCEL-RETIRE under holding) is barred only when every birth planned
    for it in an earlier reading has been made and the guard allows the barring. Otherwise the barring would bar the
    distinctions those births take; under the complete rounds it acts in one round and retires in a later one.
13. **The last round R** (GCH section 3, item 6) is used for every law. It equals LR's rule under RELEASE, where a part
    with no birth in the next round is all-short. "A part in which the reference's round R + 1 makes no birth and bars
    nothing" is read as a part of the roster after round R that holds no parent of a birth of round R + 1 and no knot
    retiring in round R + 1.

## The repaired guard (GCH section 4)

14. **"Has given".** A parent p has given when it is no member of the present roster, or when all of these hold:
    - every parent of every knot of p's brood has given (recursively; for a start knot the brood is the start roster);
    - every birth planned for p in every reading is made (by kind, item 8);
    - p's last status in the readings of its brood is idle (`idle` or `allshort`).

    R3′ allows a remaining birth, or a barring, when every parent of every knot of the brood of the birth's parents (or
    of the knot barred) has given. A start-knot birth has no brood parents and is always allowed.

## The control under the new laws

15. The control's plan is one reading (LR section 3, control, step 5): waiters and stayers are given nothing further.
    Under FILLERS a layer knot's holding is its places not shared with a knot of depth k − 1, less its places barred
    at birth, read as for h0 in GCH section 2. LR's control is frozen only for laws without fillers.

## The comparison and the searches

16. **Every order** is a breadth-first search over memo keys with a cap of two million keys and no time budget, as the
    pre-registration requires. The cap is checked when a level is complete, so a search can pass it by up to one level.
    The search is not stopped at its first mismatch, which ends only its own branch. The least number of births to a
    mismatch is exact when it is found at level n + 1 after levels 0 to n were expanded.
17. **An order that underbuilds** reports the first reference knot never made. Among the reference knots whose parents
    are all images and born by round r and which are not images, this is the earliest born, then the least numbered.
    It also reports why its birth was not allowed, which is one of:
    - a parent holds no usable distinction;
    - it is not a remaining birth of the plan its parents read, with the plan's status of the parents;
    - under R1 or R2, which knot is not weaned and which of its parents is still a member;
    - under R3, which parent of the brood is still a member;
    - under R3′, which parent of the brood has not given, and why;
    - for the control, the layer.

    Every-order searches report the reasons aggregated over their terminal keys, with up to 20 examples.
18. **The stop rule.** Every registered run is made (the pre-registration: "the study stops when every registered run
    is done"). The summary also says where, for each law family, the owner's stop rule would have stopped. No run past
    that point changes a verdict.
19. **(RATION-3, CANCEL-WAIT, HOLD) on the two-knot and three-knot starts** is run. The disclosed table marks it "not
    run" before the freeze, but run 4 names all four starts for all four laws.
20. **P8's "the runs equal those with RELEASE"** is checked on the two small starts at cutoffs 1 and 3, which both law
    families run. The outcomes of every kind of order and the key counts must be equal.
21. **The knot test (run 5)** is made on the reference after round max(6, R), with R the largest last round of the
    cutoffs registered for the pair: parity by both methods, and not-all-equal for structures of up to 600 knots, with
    the births of every round compared with parity's (parents, D, f, usable, barred). A knot made at a mismatch is tested
    in the run's own structure, rebuilt from the least mismatching order with real distinctions, by both parity methods
    and, up to 600 knots, by not-all-equal.

## The gate (run 1): what it found, and why the searches go on

22. **A bookkeeping error, found and repaired before any search.** At first the plan did not record the stayers of a
    part whose reading is idle, while the reference records them (`held`). The gate failed on (CAP-3, CANCEL-WAIT, HOLD)
    at round 2 for that reason alone. The plan now records them (GCH section 3, item 1: "a stayer in this reading").
    After the repair (CAP-3, CANCEL-WAIT, HOLD) passes on every start, D included.
23. **D under (RATION-3, CANCEL-WAIT, HOLD) differs from the reference's, and this is the frozen definition.** On D2(4,3)
    and Ring(5,3) from round 3, and on the two small starts from round 4, the reference's demand of some births is
    larger than the plan's. For every such birth, in every round, the gate checks that:
    - the reference's D equals the groups of new knots alone plus the groups that also hold an old member;
    - the plan's D equals the groups of new knots alone, birth for birth;
    - the old members are stayers (in round 3) and waiters (later), which meet the new knot's parent.

    GCH section 1 says this: "Under holding it does not hold in general: a stayer's older child that is still a member
    shares a met set with its newer child, and the demand found here leaves that group out." Example: on D2(4,3), each
    staying round-1 offshoot o_i meets its child c_i, so c_i's met set in the reference's demand roster is
    {g1, g2, g3, o_i}, and each of c_i's offshoots has D = 3 where the plan has 2.

    Under every other law, D agrees in every round compared. Under (RATION-3, CANCEL-WAIT, HOLD) the comparison without D
    agrees in every round: the structure, f, the usable and barred counts and the stayers. So the Gate prediction, which
    includes D, is reported as **failing on D under (RATION-3, CANCEL-WAIT, HOLD), as GCH section 1 foresees, and holding
    in every other respect and under every other law**. The searches go on. Under RATION-3 without fillers, D enters
    neither f nor the usable count, so it changes no plan's births. The match of every search uses parents, f and the
    barred count, which agree. The coordinator may rule otherwise.

## Noticed after the registered runs (written after them; no code or reading was changed because of them)

24. **R3 also mismatches under the FLOOR1 holding laws.** P9 expected R1, R2 and R3 to underbuild by the definition of
    weaned, and R3′ to mismatch. R1, R2, R3 and R3′ all mismatch: on the two-knot start through round 4 (8 births), and
    on the three-knot start through round 3 (6 births); they underbuild one cutoff earlier. The cause is the scaffold of
    GCH section 3, item 4, not the guard:
    - A stayer that gives in two rounds (on the two-knot start, knot 8 makes 12 in round 3 and 16 in round 4) holds
      nothing afterwards. It is then no member, so its children are weaned and R3 lets their brood act.
    - That brood's roster at birth reads the two children as one round's roster, and plans a join of them (12, 16). The
      complete rounds never make that join.

    The listing is `listings/hold_F1RH_TWO-KNOT_r4_R3.json`, and the same holds for the other cells.
25. **Searches over ten minutes.** T(4), T(5) and T(6) on D2(6,3) under the cap (cutoff round 1) took 839 s, 919 s and
    1,395 s, each reaching the cap of two million keys at 25 of 36 births. They ran in the background under the launcher,
    each with its own 8 GB cap. No other run took more than 446 s.
26. **"match" for an unfinished every-order search** in the summary's tables means that no order differs to the number
    of births searched; the row says how far ("every order to N births (cap ...)").
