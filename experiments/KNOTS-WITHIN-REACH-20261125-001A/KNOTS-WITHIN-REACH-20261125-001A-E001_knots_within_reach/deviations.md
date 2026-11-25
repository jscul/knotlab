# Deviations and readings, KNOTS-WITHIN-REACH-20261125-001A-E001

Written by the engine's author, who has not seen the drafter's prototype or its outputs, nor the epic's `advisor/`
folder. The frozen texts are unchanged; their SHA-256 sums were checked against `contract.json` before any code was
written (all match), as were the fold study's `pm.py` (`3aa69b5b...`) and `knots.py` (`9138ae86...`), which are
imported unchanged (the hash is checked again at every import).

Citations: "SD line n" the shared definitions of `RING-IN-BALANCE-20261123-001`; "FD s.i" the fold study's
definitions; "KD s.i" this epic's definitions; "PR" the pre-registration. Each item gives the question, the reading
taken and why, and the runs it affects. Items are written before the run they affect; each says when.

## Written before run 0

1. **The guard (KD 7.4).** The fold engine's `pm.GUARD` holds that study's limits; KD 7.4 multiplies them by ten. The
   values are set on the imported module at import (`kwr.py`): pairs and groups 200,000, births 200,000, distinctions
   4,000,000, incidences 20,000,000, maximal cliques 2,000,000. The file `pm.py` is not edited. A guard stop leaves the
   round unread: `pm.round_step` may raise after it has begun to change the structure (in the demand step or at the
   fresh-distinction guard), so the driver undoes that round exactly (knots, holders, barring, candidates, the span) and
   the run ends after the last round read. All runs.
2. **The knot bound.** "100 rounds, 50,000 knots" is read as the fold engine's convention: a run stops after the first
   round that leaves more than 50,000 knots, and that round is read. So L8 from one knot stops after round 65 with
   50,116 = C(68, 3) knots; its kept range from the start knot is [0, 65], which contains KD 8.4's [0, 64]. All runs.
3. **The laws T1 to T8 (claim section 2).** "Q, MET, STEPS-1 or STEPS-2 ... on CAP-3(RETIRE) (T1–T4) or COPY-LAW(RETIRE)
   (T5–T8)" is read in the order written: T1 Q, T2 MET, T3 STEPS-1, T4 STEPS-2 on (CAP-3, CANCEL-RETIRE, RELEASE); T5 to
   T8 the same on (FLOOR1, CANCEL-RETIRE, RELEASE). T9 is CARRY on CAP-3(RETIRE), T10 CARRY on COPY-LAW(RETIRE), both under
   OLDEST. The base law of T1–T4 and T9 is L6, of T5–T8 and T10 is L3. Runs 4, 4b, 4c.
4. **Uniform takes (KD 7.1).** One `random.Random` per run, seeded by KD 2.4 with class `takes:1` or `takes:2`; each take,
   in the engine's birth order (its `chooser` hook, called birth by birth with the candidate list sorted by name),
   draws `rng.choice(candidates)`. Runs 4, 4b.
5. **RATIO for births per round.** KD 3.5 states RATIO on S, the new knots at step r of H. For b(t), which is itself the
   number of new knots in round t, RATIO is read on b: b(t + 1) >= x b(t) on [a, z] with z - a >= 8. For H and P it is
   read on the increments S(r) = F(r) - F(r - 1), r >= 1. "Rising" (UNDECIDED) is read the same way on the same
   sequence. Runs 1, 2.
6. **Earlier segments (KD 3.6).** After the final segment [a, z], the exact readings (POWER, LINREC) are looked for on the
   final segment of [r0, a - 1], then of the part before that, and so on, nearest first; the search stops at the first
   prefix whose end has no exact reading. BOUND and RATIO are not listed as earlier segments ("exact readings"). Runs 1,
   2.
7. **The doubling reading (KD 3.7, a swap).** Maximal runs of consecutive r >= 4 with |eps(r) - j| <= 0.3 for one whole j,
   searched from the largest r with 2r inside the range downward; a run is kept when it spans a doubling (its last r is
   at least twice its first), and is reported as [a, 2z]. All kept runs are listed, nearest the end first. This
   reproduces KD 3.7's two examples (C(r + 3, 3) first within 0.3 of 3 at r = 13; [4, 38] for the Ring(33, 2) made-knot
   count), both in the unit tests. Runs 1, 2 (re-read only).
8. **POWER, exactly.** POWER(j) is decided by finite differences in integers: the least j in 0..3 whose longest final
   segment of degree at most j has at least j + 8 values; the j-th difference there is then non-zero (a smaller degree
   would have been found first), and F identically 0 is no POWER. The m-phase form (m = 2, 3, 4, least m first, then
   least j) groups r by its residue mod m (the residue of r itself) and needs every residue class on the common final
   segment to be of degree exactly j with at least j + 8 values. LINREC(k) solves the k equations of the last 2k terms
   exactly; a singular system gives no LINREC(k); the reported root is the root of largest modulus (real when it is).
   BOUND(j) takes, for the end z, the least a >= 4 with z >= 8a and max F/r^j <= 2 min F/r^j on [a, z], decided in
   Fractions. All runs.
9. **Parity derived (Settled 4).** Runs 1 and 2 grow under not-all-equal. The driver records, before every round, the
   number of loose distinctions and whether any is barred, and marks the first round with a birth that takes every loose
   distinction of the structure, none barred: by Settled 4 the parity run equals the not-all-equal run before that round
   and has ended at it. The parity readings are derived from this mark. Runs 1, 2, 3.
10. **The weave W_99 (KD 8.3).** "The six-regular one-pair weave of 99 x 99, two knots per square of the drawn grid" is
    built as the record builds it (`SPACE-ORDER-20261117-001A ... weaves.py`, `weave(L)`, read, not imported): the
    distinctions are the 99² grid points with both coordinates taken mod 99, and each square gives two knots of three
    places, [v(i,j), v(i+1,j), v(i,j+1)] and [v(i+1,j), v(i,j+1), v(i+1,j+1)]; every distinction lies in six knots. Two
    knots meet when they share a grid point, so each knot meets twelve others. Its 16 knots examined use KD 2.4's seed
    text `KWR|W_99|control|nae|control` (it is not in named_starts.json and has no law; `control` stands for the law).
    Run 0.
11. **The order-test controls on T_12 (KD 8.6, 8.7).** T_12 has 6,144 leaves and about 1.9 x 10^7 pairs of leaves.
    kappa is counted exactly, in integers, by an inside-outside count over the tree (no product formula used), from
    three source leaves (the first, the last, and the one a third of the way, by name) to every other leaf: 18,429
    pairs. Every automorphism of T_12 (swapping the subtrees below any knot) carries a pair of leaves to a pair with the
    same hs, and the automorphisms carry any leaf to any other, so kappa is checked for one pair of every hs class from
    each source and the order test over every pair of leaf pairs is counted from the numbers of leaf pairs at each hs:
    pairs with equal hs are tied, pairs with unequal hs concordant when |kappa| strictly falls with hs. The known tie
    (8.7) is two leaf pairs at hs 4 in different subtrees. Run 0.
12. **Floats only rule out.** In the gate (KD 4) a candidate (z, j) is ruled out with floats when a knot's ratio exceeds 2
    by more than a relative 10^-9 (float error is far below that); every gate that holds is confirmed in Fractions on
    its range, and a is stepped up if the exact check disagrees. BOUND, POWER, LINREC, RATIO and the gate's spread are
    exact. Runs 0, 1, 2.
13. **Integer arithmetic for the growing end.** The counts of allowed states are sums of products of the knots'
    weights after their loose places are summed (ge.py's header). They are computed by variable elimination on
    residues modulo the largest primes below 2^31 (numpy int64: a product of two residues is below 2^62, a sum of two
    such products below 2^63), with enough primes that their product exceeds 2^(distinctions + 4) > 4Z, and rebuilt
    exactly by the Chinese remainder theorem; signed values are read in the symmetric range. No float enters a count.
    Runs 0, 5.
14. **kappa from the pinned sums.** For two members u, v, gamma Z = 2(Z00 - Z01) (the global flip) and N(a != b) =
    (Z - gamma Z/((2^lu - 1)(2^lv - 1)))/2, which is the sum for N(a != b) split by linearity over u's and v's loose
    places (the derivation of Lemma N; it is checked to be an integer on every pair). So kappa is not computed by
    applying Lemma N as an assumption: check I compares Z, gamma Z and N(a != b) with enumeration of every state on every
    stage of at most 20 distinctions, and a second contraction with a and b explicit (`direct_N`) agrees on the run 0
    stages; check N compares Lemma N itself with enumeration for every loose distinction of each member there. The
    loose distinction read for a member is its lowest-named loose one. Runs 0, 5.
15. **Checks E, F, R, I, N in run 0 ("on the named starts").** E, F and R on the 17 named starts under L0, L1, L3, L6,
    L7 and L9 (RELEASE) and L3 and L6 under HOLD, 50 rounds (F compares H after round 40 with H after round 50 from every
    start knot and 8 made knots of class (b)); R's round statement only under its treatments with RELEASE. I and N on
    every stage of at most 20 distinctions after rounds 0 to 4 of the 17 named starts and the 219 three- and four-knot
    census starts under L0, L1, L3, L6, L7 (the named starts alone have few such stages). E and F are repeated in runs 1
    and 2 as registered, and R on every run of run 2.
16. **The member shuffle's size (KD 5.7).** "Exact over all permutations when every part has at most 8 members": the
    permutations are those of the product of the parts' permutation groups, which can be far larger than 8! when
    several parts have 6 to 8 members. Reading: exact enumeration when the product of the parts' factorials is at most
    8! = 40,320; otherwise 2,000 permutations drawn with KD 2.4's seed class `shuffle` (one generator per run, used in
    order of rounds). The shuffle is computed for the key delta with |kappa| and |gamma| as X. Run 5.
17. **A control that does not read as registered: KD 8.8, counted from made knots (found in run 0, before any other
    run).** KD 8.8 says: "counted from a made knot of round t >= n with l >= n, H = 2r² + 2r + 1 for r <= n - 1 and
    n(2r + 1) for r >= n". In the first run 0 (Ring(n, 2) under L0 grown 3n rounds, every made knot of rounds n to
    s_min - n checked), every start knot read KD 8.8 exactly, but only half the made knots did (45 of 90 at n = 9, 120
    of 240 at n = 15, 561 of 1,122 at n = 33). The listing: a made knot of round t reads 2r² + 2r + 1 for r <= n - 1 and
    n(2r + 1) for n <= r <= t, and when t < l the count beyond r = t rises by n a step, H = n(t + r + 1) (the count from
    the knot has reached the start after t holder steps and grows only toward the members). Every made knot with
    t >= l reads KD 8.8 on its whole kept range; every made knot with t < l fails it from r = t + 1. So KD 8.8's
    statement lacks the upper end r <= t; the engine is not at fault (start knots and all r <= min(t, l) agree). The
    control now reports three lines per n: start knots as registered; made knots as registered on the whole kept range
    (the count that passes); made knots as registered on [0, min(t, l)] and n(t + r + 1) beyond. Run 0 was then stopped
    and the thread that froze the study informed, as the brief requires, before run 2. The text is not edited.
18. **The run 4b probe.** "One case, capped at 10 minutes": Ring(5, 3) under T1, 3 rounds, the identity numbering, every
    choice of the uniform takes enumerated (at most 10^5 histories) and its structures grouped up to renaming (the
    structure with its birth record as a labelled graph; Weisfeiler-Lehman hashes, then exact isomorphism tests within a
    hash). Within the same 10 minutes the histories of every registered case (two-knot, three-knot, Ring(5, 3) under T1
    to T8) are counted at the identity numbering, smallest first, to estimate run 4b's size (histories x 4n numberings x
    seconds per history). Run 4b runs if that estimate fits its registered 10 minutes on the processes allowed; a case
    over 10^5 histories is "not finished".

## Written after run 0, before run 2

19. **Run 2's items and swaps.** Registered items, in order: the 17 named starts of named_starts.json (in file order,
    the bare rings Ring(n, 2) among them) under L0, L6, L7 at T = 66 and 2T = 132; the seven bare rings under L0 at 264
    and 528; the first 50 five-knot starts of the registered order, then the 9 small starts of run2_small_starts.json, under
    L0, L6, L7 at 66 and 132: 235 items (470 gates). Each item is grown once to 2T + 10 rounds (check F at T and 2T) or to
    its end or bound; everything at round T is read on the structure after round T (the knots made by then, places
    being fixed at birth). Not-all-equal only; parity is derived by Settled 4 (R 9). The samples of classes (b), (c),
    (d) and `members` at 2T use the same seed text as at T (KD 2.4 has no round in it), so they are drawn again from
    the candidates after round 2T. When the run stopped with no member, s_min is undefined: classes (b) to (d) are
    empty and only the start knots are examined, with l = the greatest hs. Swaps, after the registered items: HOLD
    under L3 and L6 on the named starts at 66 and 132; bounds of 60 rounds (2T = 120) and 20,000 knots under L0, L6, L7
    on the named starts; on every registered item, re-read: parent steps (H and the gate from the knots examined), the
    retired knots counted and not stepped through (L6), every live knot as the roster for P, the gate's thresholds z >= 4a,
    C/c <= 3 (scaling 1.5 is applied in the report), BOUND and the doubling reading per knot, class (d) beside.
20. **P9 names L1, which run 2 does not run.** P9: "The roster count P under L1, L6, L7 ... on run 2's runs"; run 2's
    laws are L0, L6, L7. Reading: P9 is judged on L6 and L7 of run 2 as registered, and L1 is grown on run 2's starts
    (66 and 132 rounds, the roster count only, no gate) as a supplement labelled "P only", so that P9's verdict is given
    both on L6, L7 alone and with L1.
21. **Run 5: pairs in different parts while the roster is not past its start.** KD 5.5 sets delta = infinity for pairs
    in different parts only when the roster is past its start; KD 5.8's strata (i) to (v) give no place to a pair in
    different parts of a roster not past its start (possible under waiting, where two waiting start knots still meet).
    Such pairs are put in a sixth stratum (vi), reported apart and never pooled, with their delta outcomes. Pair readings
    (kappa, gamma, rho) are computed for pairs within one part (strata i, iii, iv, v), which is what the comparisons,
    L-W, betweenness and the shuffle use. A stage is a structure after a round t >= 1 that made at least one birth;
    after the growth ended later rounds repeat the last structure and are not stages. Stratum (i-3) needs both multisets
    {lambda_u, lambda_v} and {sigma_u, sigma_v} equal (each separately, the letter of KD 5.8). Betweenness counts each
    unordered {u, w} with each v between once; L-W fails on a stage when some pair with strictly smaller ws has |gamma|
    not strictly larger (ties in |gamma| count as failures, by the letter), and the strict reversals are reported beside.
    The smallest stage at a level is ordered by (knots, distinctions, round, start index).
22. **Run 4b does not run (the probe).** In the first probe the exact grouping up to renaming (labelled-graph
    isomorphism tests) ran over 10 minutes on the probe case without finishing, and was stopped (its own process). The
    probe was rewritten to time the enumeration alone: Ring(5, 3) under T1, T2, T3 and T4 each pass 36,000 histories within
    60 s at the identity numbering (about 1.6 ms a history), so the probe case alone (80 numberings, up to 10^5
    histories each) needs more than three hours before any grouping, against run 4b's registered 10 minutes. Run 4b
    is therefore not run and Settled 3 is reported "argued, unchecked", as PR provides. The probe's record is
    `run0_probe.json`.
23. **The parity knot test on large taking-free structures (run 3).** The fold engine's two parity methods (ranks and
    kernel, by Gaussian elimination in Python integers) are too slow on structures of up to 50,000 knots. With every
    distinction held at most twice (taking-free laws, KD 1.6), both quantities have exact graph forms (ktest.py's
    header): the rank difference is 1 + (components of G - u without the outside vertex) - (the same in G), and the
    kernel projection's rank is deg(u) - (components of G - u that u reaches). They are computed by two different
    algorithms (components of G - u for each knot tested; one articulation-point search), and both were checked in run
    0 against the engine's parity_test on 27,763 knots (249 failing) of grown and drawn two-holder structures: no
    disagreement (`run0_ktest.json`). Run 4 (three or more holders) uses the engine's parity_test itself.

## Written after the thread's reply to run 0, before run 2

24. **What KD 8.8's missing upper end touches in run 2 (checked before run 2).** Run 2 reads every gate, range and
    spread from the counts themselves; no formula of KD 8.8 enters any code. On Ring(33, 2) under L0 at 264 rounds,
    every class (b) knot examined (rounds 1 to 65) and 40 of the 64 class (c) knots have t < l, and none of them reads
    n(2r + 1) beyond its own round; all read n(t + r + 1) there, as item 17 found. Both forms are power 1, and the gate
    from the counts holds with j = 1 on [16, 132] (161 knots, spread 2.02, start knots 1.02), the disclosed figure of PR
    Known 2; so no registered verdict, kept range or disclosed range uses the unbounded form. The one registered sentence
    it touches is the claim's Claim 2 parenthetical "(H = n(2r + 1) beyond the ring's size)" (and KD 8.8 itself, and
    P6's "(b) sketch for the counts"): from a made knot that sentence holds only up to the knot's own round. The
    thread logs the correction to the frozen text; P6 is reported under both readings of "read j = 2 on [4, n - 1]"
    (each knot within a factor 2 on [4, n - 1]; the full gate with z >= 8a), each verdict labelled with its reading.
25. **P9's supplement.** The L1 runs of item 20 are labelled in the outputs "supplement added after the freeze" (kind
    "P only"); P9 is given on L6 and L7 alone and with L1.
26. **Processes and timing.** The machine's load is about 20 to 27 (three other engines): every run uses 4 processes,
    each capped at 6 GB, and each run's size is fixed from the timing of its first items under that load before the
    rest is run; a run that would pass an hour is cut to a registered prefix fixed before it continues.
27. **Run 2's timing and a guard stop (written after its first 24 items, before the rest).** The first 24 items took 71 s
    on 4 processes (load 32), so the 396 items (235 registered, the swaps and the P9 supplement) fit well within the
    hour; run 2 is run in full. In those items the guard of KD 7.4 stopped Ring(5, 3), D2(5, 3) (both after round 15,
    about 20,900 knots), Ring(7, 3) (after round 14) and the seven-knot generator (after round 13) under L0: the demand
    roster of the next round had more than 200,000 joinable pairs, so that round is not read. PR Known 12 says the
    golden-ratio eddy "passes 50,000 knots after round 17"; under the registered guard it does not get there. Their
    run 2 answer is "undecided" (T past the bound or the guard) under either reading.
28. **Run 5's order (written before run 5).** "Every census start" has no registered order. The items run the 219
    three- and four-knot starts in file order, then the 3,157 five-knot starts in the registered order of
    five_knot_order.json (`random.Random(202611251)`), with L0, L1, L3, L6, L7 within each start, so that a prefix cut for
    time leaves every small start and a uniform sample of the five-knot starts.
29. **Run 1 cut to a registered prefix (written after timing its first items, before the rest).** Under the load of the
    moment (28 to 30) the first 240 items (20 small starts, all 12 laws) took 147 s on 4 processes and 110 five-knot
    items (10 starts, 11 laws) 67 s: 0.61 s per item either way. The registered size (219 small starts x 12 laws and
    1,000 five-knot starts x 11 laws) would need about 2 h 20 min. Fixed before the rest of run 1 is run: the 219 three-
    and four-knot starts in full (every law) and the first 250 five-knot starts of the registered order of
    five_knot_order.json (every law but L8), about 55 min in all. The 250 are a uniform sample of the 3,157 five-knot
    starts; KD 7.5's estimators are applied with 3,157/250 in place of 3.157 (census weighting: (count among the 219 +
    12.628 x count among the 250)/3,376; labelled weighting likewise), and every share says it is over the 219 and the
    first 250. Of the 64 scratch starts, the 5 small ones and those of the 59 five-knot ones that fall among the first
    250 are in the prefix; the shares "without the 64" leave those out. The other 750 five-knot starts are not run.

## Written before run 4

30. **Run 4's readings.** Greatest holder steps from a start knot: the largest finite number of steps from it to a knot
    of its connected structure, after round 1 to 10, 25, 50, 100, under holder steps (a step between two holders of one
    distinction, whatever its number of holders), (a) parent steps, (b) holder steps through distinctions of at most two
    holders only, (c) the weighted step (m - 1 through a distinction of m holders, least total). "Held by hubs" needs
    rounds 50 and 100: a run that ended before round 100 is "ended"; a run stopped by the knot bound or the guard before
    round 100 is "undecided (round 100 not reached)", never a negative. "The hubs make it so": held under holder steps and
    not under (b) or (c). The base law's greatest holder steps (L6 for T1-T4 and T9, L3 for T5-T8 and T10) come from the
    base law grown on the same start and knot law. Lambda_t's least number of distinctions in one rule is exact when its
    rank is at most 20 (every non-zero combination); above 20 the least weight of an echelon basis vector is reported
    and labelled an upper bound. Tied pairs: two loose distinctions with equal signatures over a basis of the allowed
    states (equal in every allowed state), held by two different knots, each tested by the engine's parity_test on the
    stage; the holder steps between those knots are reported. Check P: on every stage of run 4 under parity with at most
    20 distinctions, every pair of distinctions has rho = 0 or 1/2 by enumeration, and rho = 0 exactly for equal
    signatures. The knot test: every knot after round 25 (or the last round) and 100 knots made later (class
    `later-knots`), by the birth method at birth under not-all-equal (start knots directly) and by the engine's two parity
    methods on the last structure under parity.

## Written after run 4, before run 3 (after the stop and the thread's restart)

31. **Run 3's direct comparison.** Timed on run 3's first items: the birth method costs about 0.01 s a knot even on
    structures of 20,000 knots, but the direct test on the whole structure costs 3 to 14 s for a knot of 10 to 12
    places (2^10 to 2^12 solver calls; under ORD a knot's fresh count is its demand, so the sampled knots of run 2's L0
    runs have 5 to 18 places). Reading: in run 3 every sampled knot is tested by the birth method, the registered test of
    the sample; the direct test, which KD 6.1 asks for on knots of at most 12 places to compare the two, is run on the
    sampled knots of at most 6 places only. The two methods were compared on every knot of every stage of run 5 (more
    than 300,000 knots, no disagreement) and in run 0's checks. The birth method's view of the structure before a
    knot's round is the prefix of knots made by then, with the holder lists unfiltered (`run3._Prefix`), which is what
    `knots.jointly_free` and `knots.nae_direct` read.
32. **Process notes.** (1) The first timing of run 3 (60 items, about 10 minutes with none finished) was stopped, its
    process numbers taken from a listing matched on "run3.py" (the listing a minute before showed only my own
    processes); its empty output was removed. (2) A second timing script was stopped by its own process numbers from a
    pattern that also matched my own tool shell. Neither touched another session's process. The brief asks for the
    process numbers I launched; both lists contained only those.
33. **Run 3 cut to a registered prefix (written after timing 42 of its items, before the run).** 42 items took 105 s
    on 4 processes (load 15 to 21): run 2's runs about 20 s each on one process, run 1's about 6 s. The registered size
    (235 run-2 runs and 2,628 run-1 runs of the small starts, both knot laws) would need about 2 hours. Fixed before the
    run, in run 3's order: all 235 of run 2's registered runs, then run 1's runs of the first 100 three- and four-knot
    starts in file order (all 12 laws each), 1,435 runs, about 52 minutes. The other 1,428 run-1 runs (119 small starts)
    are not run; nothing is said of them.
34. **Run 3 resumed on 6 processes (written at the resumption).** After 1,073 s on 4 processes run 3 had done 400 of
    its 1,435 fixed items, slower than timed (run 1's items about 3.6 s each, wall), which would have taken it to about
    80 minutes. The load having fallen to about 11, run 3 was stopped (its own process numbers), its file rewritten to
    its 476 complete records (the incomplete gzip member left by the stop dropped; a copy kept in the scratch folder),
    and resumed on 6 processes with the same fixed prefix of 1,435 items, so as to finish within about an hour of its
    start. Items in flight at the stop were run again from the start.
