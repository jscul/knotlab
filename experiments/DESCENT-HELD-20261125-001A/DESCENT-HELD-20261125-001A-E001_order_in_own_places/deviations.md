# Readings taken where the frozen texts leave a choice (DESCENT-HELD-20261125-001A-E001)

Written by the engine's author (a second program, written without seeing the drafter's prototype) from the
pre-registration, the note, DH and SD. Each item was written BEFORE the part it affects was run. "SD" =
research/RING-IN-BALANCE-20261123-001/definitions.md (by line); "DH" = research/DESCENT-HELD-20261125-001/definitions.md;
"PR" = research/DESCENT-HELD-20261125-001A/preregistration.md. Items added later carry the part they precede.

## Written before part 0

1. **The engine.** `dh_engine.py` is this run's own complete round, written from SD steps 1-8 (lines 34-77) and DH 3.2.
   It imports `compute_groups` from `lr_core.py` (as the pre-registration says) for step 1 and nothing else of the round.
   The order of new knots and the names of knots and distinctions follow DH 1.4 (`lr_core.own_round`): groups in sorted
   order, each member giving its last usable loose place in place order; then offshoots by member, last usable place
   first; new knots numbered on from the last knot; fresh distinctions numbered on, knot by knot in that order. The gate
   (part 0 (a)) checks this against `own_round`, names included.
2. **Order of a new knot's fresh distinctions** (names only, SD lines 76-77): the usable ones first, then those FILLERS
   bars, then (barred forms) the s added barred ones. Under NEXT3-PLACES (usable) with FILLERS the first min(F + s, D) are
   usable and the rest barred.
3. **Shortness** is counted on usable loose places (h(u), SD line 22 and DH 3.2): a member is short when it owes more than
   its usable loose count. Barred places never count in h, never make a knot a member, and never create a meeting.
4. **HOLD** (SD line 53): a member that is not short keeps as many usable loose places as the number of its cancelled
   groups and makes offshoots from the rest (`own_round`'s `keep = cc[u]`; the reading named in PR part 0 (d)). A short
   member under CANCEL-WAIT waits under HOLD as under RELEASE.
5. **The closing exception** (SD lines 63-66, own_round): a round is closing when it makes exactly one birth and, after
   that birth's taken distinctions become shared, the structure has no loose distinction at all (barred ones count as
   loose). It acts only under parity. Registered reading (DH 3.2 step 5): the closing knot receives nothing (F = 0, s = 0);
   the s it "would" receive, for condition (d), is computed by DH 3.2 steps 2-4 with F = 0 (and z_F = 0). Swap: F = F_B(p, D)
   and s recomputed on it.
6. **When a run ends** (DH 1.1): after round R; after the first round after which the structure has more than N knots;
   after a round that stalls (STALL); or after a round that changes nothing (no birth and no newly barred distinction). That
   last round is executed and recorded with 0 births; it is not counted in the run's number of rounds that changed
   something. Kind of end: "R", "N", "stalled", "stopped" (the round found no member), "jammed" (members, no birth, nothing
   changed). Swap (part 8): end at the first round with no birth. Because the swap's run is the registered run cut at its
   first round with no birth, the swap's census counts are computed exactly from the registered runs' per-round records.
7. **Parent steps** (DH 0.3) from the engine's record of parents. **Counted** (DH 4.5 (b), P11): some new knot has two
   parents with different parent steps. **(b′) fails**: some new knot has two parents whose parent steps differ by a number
   not divisible by 3. **Greatest difference** (DH 4.6): over births and their parents, child's parent steps less the
   parent's; "by round": that maximum over the births of each round.
8. **LQ's condition fails** (DH 4.5; LQ's reading quoted in its results, line 97): in some round a start knot is short under
   CANCEL-WAIT (it waits) and a start knot it meets is a parent of a birth of that round. Under HOLD a member keeping places
   for cancelled groups is not waiting (SD step 6 keeps the two apart).
9. **The fives stamp** (P11): each knot's parent steps counted in fives; at a shared place of x whose other holder is y the
   prediction "a parent place" exactly when (v(x) − v(y)) mod 5 is 1 or 2. "Fives right on" is every shared place right in
   the run's last structure (the stamp and the kinds are fixed at birth, so this is every structure). The table's numbers
   (501 of 510) are counts among the counted starts; the count over all starts is reported beside it.
10. **Places and their kinds** (DH 4.1-4.2, PH/LQ words): each shared distinction gives two places, one for each holder. Kind
   from the record: "a parent place" (the other holder is a parent), "a child place" (the other holder is a child), "a
   place between two start knots". The place rule predicts "a parent place" exactly when κ(y) ≡ κ(x) − 1 (mod 3). "Right on
   a run" is checked on the start and on the structure after every round. For the place-count forms (and NEXT3-BARRED
   without retiring) every count is fixed at birth and shared places only accumulate, so the last structure decides it;
   with retiring under NEXT3-BARRED every round's structure is checked. The closing knot's places are included in
   "right on" and in the joint stratum (the literal "right on every structure"); P3 needs (d), which excludes runs where
   they could be wrong.
11. **Arm R runs and the place rule.** P3-P6 are judged on arm-W runs only (the three count forms); conditions (a), (c), (d)
   are defined for a count form. Base-law runs report (b), (b′), LQ's condition, and, for information, the place rule with
   κ = number of places (nothing written).
12. **Condition (a)** (DH 4.5): every two start knots that meet have the same number of places counted in threes (the
   place-count forms; census condition (a) of P11); under NEXT3-BARRED it is met (no start knot has a barred place). For a
   handed-in structure that carries barred places (part 2, deliberately) (a) is read with κ = b.
13. **Condition (c)**: under NEXT3-BARRED, some knot has δ(u) ≢ 0 (mod 3), δ(u) the barred places retiring added to u (a knot
   retires at most once, since it is then never a member). Under the place-count forms (c) is met.
14. **"The first birth at which (b′) fails"** (P4, DH 1.4): the first round with a birth whose parents' parent steps disagree
   in threes, and the multiset of all such births of that round; P4 requires every one of them to be counted at DH 3.2
   step 3.
15. **Census** (DH 9.1): `cpcensus.starts(n)` and `cpcensus.stars` for n = 1..5 (and 6), imported unchanged; census index =
   position in the concatenation for n = 1..5 (start 133 is W1, 64 is W2, 62 is W2b, checked in part 0). `cpcensus` imports
   `cpcommon` only for `ROOT`; a stub module holding `ROOT` is put in its place, so that ticket A's engine (which `cpcommon`
   imports) is not loaded into this program. `cpcensus.py` itself is unchanged.
16. **Kept under parity**: every start knot passes the parity test, both methods of `knots.parity_test` agreeing.
   Not-all-equal runs use every start (DH 7).
17. **Weightings** (DH 9.2): the labelled weight of a start is n!/|Aut|, |Aut| the number of automorphisms of its graph
   (`cpcensus.autos`) that keep every loose count (σ with loose[σ(v)] = loose[v] for all v). A labelled share is the sum
   of weights counted over the sum of weights in the population.
18. **Numberings** (part 0 (g), DH 8): "5 bases" is not named; this run takes the first five base laws in `laws.json`
   order (R3W, F1O, F1R, ORD, C3W), parity. A numbering gives each distinction a new label and each knot a new position;
   each knot's places are then listed in the order of the new labels (so that the order of distinctions reaches the
   engine's choice of which place goes to which birth). The registered lists are read as: new position i is old knot
   `knots[i]`, old label d gets new label `dist[d]`. The 4n numberings: the sorted labels shifted by j (j = 0..n−1), as
   given or reversed, give the new labels in order; knots as given or reversed. Every numbering of the four starts of at
   most six distinctions is tested by an exact isomorphism test (part 0 (g), as registered); the 4n and the 200 registered
   numberings of the five others are run as an extra with the signature of DH 8.2, labelled so, if time allows.
19. **Planted error** (part 0 (c)): on the 14 named starts under the 11 bases and the two barred forms, parity, at part 4's
   bounds; after the run one barred loose distinction is added to the first new knot x of round 2 (DH 1.4 order), the place
   rule's verdict at every shared place is compared before and after, and the set that changed is compared with the
   predicted set (x's places to its parents, from both sides; x's children's places to x).
20. **Shortness check** (part 0 (f)): on every round of the part-0 runs under the barred forms, the engine's short set is
   compared with an independent recomputation from the structure with h = usable loose count, and the rounds where the
   count of all loose places would give another short set (or other births) are counted, to show the check is exercised.
21. **The sixteen holding runs** (part 0 (d)): parity, 6 rounds (the record's bound: "through six rounds"), DH 1.1's
   stopping; births by round compared with every recorded event, the round that changed nothing included.
22. **The gate** (part 0 (a)): each of the twenty pairs of LOCAL-ROUND's gate.json (start by `lr_core.start_stars`, law as
   named, RELEASE), parity, 8 rounds or 3,000 knots, DH 1.1's stopping applied to both; after every round the lists of
   places, holders, barred marks and parents are compared. An extra (labelled so) compares HOLD with `own_round(release=
   'HOLD')` for the rations `own_round` has.
23. **M2** (DH 5.3, part 5): "a birth whose n is not one more, counted in threes, than some parent's" is read as: a new knot
   x and a parent y of x with n(x) ≢ n(y) + 1 (mod 3) (the place rule with κ = n wrong at x's place to y). The other
   reading (n(x) ≢ n(y) + 1 for every parent y) is reported beside it.

## Found while running part 0 (recorded before part 0 was run again)

28. **The planted error's "exactly" is too broad as worded** (hand_cases.json and PR, "The planted error"). By the place
   rule's arithmetic, with δ = κ(other holder) − κ(x) before the error, adding one barred place to x changes the verdict
   at x's own place exactly when δ ≡ 0 or −1 (mod 3), and at the other holder's place exactly when δ ≡ ±1. The predicted
   set (x's places to its parents from both sides, its children's places to it) is therefore exact where x's parents are
   one less and its children one more, counted in threes, which (a), (b′), (c) and (d) give, and need not be exact
   elsewhere. The first run of part 0 found 21 of 308 runs where the changed set is not the predicted one; in every one
   of them (a), (b′) or (c) fails (GEN7 and C8X3 under NEXT3-PLACES (barred): (a); SCC under NEXT3-BARRED with waiting:
   (b′); every start under FLOOR1 retiring with NEXT3-BARRED: (c)). The check is kept as worded and reported failing on
   those runs; beside it are reported (i) the check restricted to runs where the four conditions are met, and (ii) the
   formula above on every run. No code was changed to make the worded check pass. Part 0's other checks all passed, so
   the run goes on to parts 1 to 8 and the report states this.
29. **Part 0 (f)**: the deliberately wrong engine (shortness on every loose place) can have a member pay a group from
   places it does not have; that run is recorded as "the wrong engine gives other births" instead of stopping part 0.

## Found after part 1 (a diagnostic, not a change to any registered reading)

30. **The joint stratum and the closing knot's places.** With every place counted (item 10) the joint strata are 4 below
   the scratch values under the place-count forms and 30 below under NEXT3-BARRED. `diag_joint.py` re-ran the census
   runs with a closing birth under two other readings of DH 3.2 step 5 ("the place rule is not claimed at its places"):
   (X1) the closing knot's own places left out; (X2) both places of every distinction the closing knot holds left out.
   X2 gives every scratch value exactly (129/127, 133/133, 133/133, 133/133, 129/127, 129/127, 127/130; 2,838, 3,348, 90,
   3,348, 2,838, 2,838, 3,125); X1 gives one less under the place-count forms. The starts that move: census 13, 129, 208,
   3359 (place-count forms); 30 starts under NEXT3-BARRED (listed in part1_joint_closing.json). All three readings are
   reported; the registered reading of this run (item 10) is kept as the primary number. P3 is not affected: it needs (d),
   which every one of these runs fails.
31. **The six-knot sample was cut** at 1,165 of 3,000 starts by the registered 30-minute limit on part 1 (load 30-36 on
   24 cores, 4 processes). DH 9.3: a prefix of the sample's order is itself a sample. The other 1,835 are not run.

## Written during part 7, before its results were seen

32. **Part 7 ran past its registered 30-minute limit** (started 02:43:52, unfinished at 03:14:00, load 29-36 on 24
   cores with 4 processes; the not-all-equal test `nae_decomposed` does work proportional to the whole structure for each
   knot, so a run of 3,000 knots costs about 30 s in one process). Its program kept no prefix (one `pool.map`), so it
   was not stopped, which would have left nothing. Instead: the registered result is the prefix of jobs, in the
   registered order (part 4's runs by start, base and form, then part 6's), that had finished by the 30-minute mark, found
   by replaying the dispatch (jobs taken in order by the first free of the 4 workers, each job's own measured seconds);
   the jobs after that prefix are reported separately, labelled "run past the registered limit". Part 8 keeps a prefix
   if it is cut.
33. **That plan was replaced at 44 minutes** (before any part-7 result was seen): growing part 4's not-all-equal runs
   again showed structures of up to 14,056 knots (ORD with NEXT3-PLACES (usable): a round may pass the 3,000-knot bound
   once, and DH 7 tests that structure as it is) and knots of up to 51 places, where `nae_decomposed` needs up to 2^21
   solver calls for each piece touching up to 22 places. The first part-7 process would have run well past an hour
   (the brief's limit), so it was stopped (its own process numbers) with nothing kept. Part 7 was started again with every
   job submitted in the registered order and a 30-minute limit: the registered result is the longest leading prefix of
   finished jobs; jobs after the prefix that finished are reported separately; the others are "not run", with the
   command line and an estimate in the report.

## Written after the usage-limit stop, before part 8 was run again

34. **Part 7 stands as cut.** The relaunched part 7 finished at its registered 30-minute limit (03:57) and wrote a whole
   part7.json: the leading prefix of 818 of 1,244 runs, 154 later runs that finished (reported separately), 272 not run.
   It is not run again; the runs not run are reported "not run" with the command line and an estimate.
35. **Part 8's first run crashed** (09:15, machine idle, 6 processes) in its census segment: under the parents-differ
   swap one run's demand roster had a clique of more than about 1,000 members, and the imported Bron-Kerbosch
   (`lr_core.compute_groups`, unchanged) recursed past Python's default depth of 1,000; nothing was written. Part 8 is
   run again with the interpreter's recursion limit raised to 100,000 in its processes (Python 3.13 does not use the C
   stack for Python-to-Python calls; the imported module is unchanged), with any exception (RecursionError or
   MemoryError under the 6 GB cap) caught per run and recorded with its start, law and form, and with the named-start
   swaps written to part8.json before the census segment begins.

36. **Part 8's outcome** (recorded after it ran): the named-start swaps and the stopping swap finished; the census
   segment was cut at its 30-minute limit with census start 938 (five knots, stars
   `[[0,6,7],[0,1,2,3,8,9],[1,4,5],[2,4,10,11,12],[3,5,13,14,15]]`) unfinished, so the registered prefix is census starts
   0-937 (935 kept); the other 2,412 starts finished and are reported separately; start 938 is not run. No run raised
   an error.

## Written before part 2

24. **Prefix and subset structures** (DH 5.5): built as DH 4.4's parent-closed part of the structure after round 1 (each
   knot with all its places as at the end of round 1, a distinction with one holder in the part loose there, barred marks as
   at the end of round 1). Prefixes have at least one new knot. "Allowed start" (DH 1.2): every knot of at least three
   places, no barred distinction (two holders at most is true by construction). Isomorphism with a census start: the
   structure must have at most five knots, no two knots sharing two distinctions, and its graph with loose counts must
   equal the census start's up to a renaming of knots (an exhaustive canonical form). The ten "recorded" laws, parity.
25. **The restart control** (DH 5.4): parity. The structure after round t is handed in with its barred marks (a structure
   reached under retiring or FILLERS carries them; DH 1.2's statement is about what a start of the class may carry, and the
   control is about the round using only the present structure). The original run is grown to round t + 2 (or its end).
26. **Arm-W hand-ins** (P8): the place rule is applied to the handed-in structure itself, where every knot is a start knot
   and every shared place is "a place between two start knots"; "old parent places" are the places of round-1 new knots to
   their parents (from the new knot's side) and of the parents to them (from the parent's side). (a), (c) and (d) are
   those of the original run through round 1.

## Written before part 6

27. **Returns** (SD lines 85-88, DH 6.4): parity, 14 rounds. "Past its start" read on the roster after round s (no member
   meets a member). The members after round t that descend from Y: members after t that are members of Y or descend from
   one through the record of parents. A part of the roster after t all of whose members descend from Y is a candidate; the
   first candidate the same as Y (members renamed carrying h, k and the family of inclusion-maximal met sets, k counting
   every barred loose place) is the return. The renaming found is networkx's first isomorphism of the bipartite graph of
   members and inclusion-maximal met sets; q is reported for it, and whether some renaming gives a common q.

## Added by the thread after the run (changes no number)

37. **`part8.json` is stored gzipped** (`part8.json.gz`, 34 MB unpacked), so that no file of the record passes 20 MB.
    `dh_common.read_out` and `summarize.maybe` read either form; nothing else was changed, and `summary.json` and
    `summary.md` are the run's own.

