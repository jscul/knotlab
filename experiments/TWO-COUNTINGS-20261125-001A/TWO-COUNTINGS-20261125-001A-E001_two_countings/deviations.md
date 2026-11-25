# Readings and deviations, TWO-COUNTINGS-20261125-001A-E001

Written by the engine's author, who has not seen the drafter's prototype or anything it produced beyond what the
pre-registration ("PR"), the definitions ("TD"), the claim, the knot-test finding and the data files disclose. Each item
was written before the part it affects was run. Items are numbered in the order they were written; none was changed
after a value was seen (a later correction would be a new item that names the one it replaces).

## General (written before any code)

1. **Interpreter.** Everything runs under `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B` (Python 3.13.3). The
   canonical command is run exactly as TD 10 and the finding give it, `-m knotlab check --cnf ... --loops ...
   --contact ... --witnesses ... --json`, with `PYTHONPATH=tools` from the repository root, with that interpreter in
   place of `python3`. The checker's code is imported or run unchanged.
2. **Exact arithmetic.** Weights are `fractions.Fraction`; the score's inner sums are taken in Python or numpy integers
   over the common denominator of the four tables, with an assertion that no value approaches the int64 range (the
   arithmetic is then exact integer arithmetic; the score is returned as a Fraction).
3. **The score over all two-valued functions (TD 4.4).** Before enumerating, record values whose rows are proportional
   (for one own setting a, the vectors (P_a0(u, ·), P_a1(u, ·)) are positive multiples of each other) are merged, and
   likewise the other side's columns. This is an exact reduction, not a change of the class: for any fixed functions of
   the other side, the best value at u is the sign of a sum that has the same sign at every value of a merged class, and
   the absolute values of proportional columns add. The method is otherwise TD's: every pair (f0, f1) on the side with
   fewer (merged) values, f1 fixed to +1 on its first value, the other side's best response Σ_v |σ_0 L_0(v) + σ_1 L_1(v)|,
   the four placements of the minus sign. Gate (part 1): the merged method equals the unmerged enumeration on the gate
   structures.
4. **The score is the signed maximum.** E00 + E01 + E10 − E11 maximized over the four placements of the minus sign and
   over the class, with no absolute value (the letter of TD 4.4). Over all two-valued functions the class is closed under
   negating one function, so this equals the maximum of the absolute value; over parities (no constant, not closed under
   negation) it is the signed maximum as written. A parity outcome is (−1)^(sum of the chosen record bits).
5. **Record values.** For own setting a, an observer's record values are the values with nonzero weight under (a, 0) or
   (a, 1).
6. **Change from the other's setting** (TD 4.3) is the total-variation distance between an observer's record
   distributions under the other's two settings, for each own setting; the largest over both observers and both own
   settings is reported, and "hidden" means it is 0 exactly.
7. **The common stage s of TD 9** is the last stage common to the four histories before the setting knots; the counting
   may start at any common stage s′ ≤ s (h0), and every such s′ is run and reported. Fresh distinctions of a setting knot
   are its places not held in S_s.
8. **The lost-weight rule, checked.** "Whether a state is lost, at any stage, depends on its part on S_s alone" is checked
   as: for every setting pair, every allowed state o of S_s keeps either all or none of its weight under counting from
   s′ (renormalising aside), and the set of kept o is the same for all four setting pairs.
9. **Option pairs (TD 4.1).** An option pair (o0, o1) of the first observer means its setting knot is nae(x1, o0, za) at
   a = 0 and nae(x1, o1, za) at a = 1; likewise nae(y1, p_b, zb) for the second observer. Records stay those of TD 4.2.
10. **The knot test (TD 10).** The induced relation of a knot is the set of assignments of its places, in the order
    written, that extend to an allowed state of the whole structure; `knotlab.knots.check_knot` is called on it with
    loops = its places but the last and contact = its last place, the forgetting reading (as the finding's "How to
    rerun"). K1–K3 under forgetting treat every variable alike, so the split does not change a verdict. In the canonical
    command a parity rule is the clauses forbidding each assignment of its places of the wrong parity, and a
    not-all-equal rule the two clauses (all places) and (all places negated); every other distinction of the structure
    is a witness. "On its own": `check_knot` on the rule's own relation. "In the whole" for a start means the start
    taken alone.
11. **Projection and the canonical checker compared.** For every canonical check, the checker's `allowed` table must
    equal the projection's induced relation and its verdict the projection's verdict; any disagreement is listed.

## Part 1 and the early knot test (written before part 1 ran)

12. **Brute force.** Every assignment of every distinction of a structure, each knot tested directly; compared with the
    engine's stage-by-stage enumeration (backtracking on the start, then each stage's fresh distinctions enumerated
    for each old state), state by state, and completion count by completion count.
13. **Known 1–3** are reproduced as pre-registered: the 11-knot structure's nine option pairs under both countings
    (from the start = the 11-knot structure as its own start, the two setting knots one stage), the (s1, s2) movement;
    the smallest gain from the part, from after the rule-Q round and from the finish; the 7-, 8- and pencil 9-knot
    structures from the start and from the finish. A gate number that differs stops the run.
14. **The sign assignments' index** (part 3, used in part 8's P8): bit i of the index (i = 0..8) belongs to the i-th
    parity knot of "eleven (start)" in file order; bit 1 = odd, bit 0 = even. The file's own signs are one of the 512.
15. **Ties (P8).** "The tie between x2 and x3 is an inequality" means x2 ≠ x3 in every allowed state of the start; an
    equality means x2 = x3 in every one.

## Part 2 (written after part 1 and the early knot test, before part 2 ran)

16. **The parity score in two forms.** (i) Signed, R 4 (the letter of TD 4.4; the primary column). (ii) The absolute
    value |E00 + E01 + E10 − E11| maximized over the same choices (equivalently, the parity class with each observer's
    outcomes also negated as a whole). Disclosed: a timing probe on one rule-R record before part 2, run to size the
    part, gave 29/18 signed, 127/63 in the absolute form and 127/63 over all two-valued functions, against the record's
    127/63; so the records' parity scores were taken in the absolute form. Both forms are reported; P1 compares a
    recorded number with the score under the record's own definition (all two-valued functions, and the parity score in
    the absolute form), and a recorded number counts as reproduced when it equals the all-functions score or the
    absolute parity score, which is said for each. The lemma's verdict (P2) uses all two-valued functions and the signed
    parity score; the absolute parity score is bounded by the all-functions score, so the verdict is the same with it.
17. **The two 10-knot starts.** Round 1 under rule Q is made by the fold study's engine `pm.py`, unchanged: law (ORD,
    STALL, RELEASE) with take Q, not-all-equal newborns, every combination of the round's open choices given through its
    `chooser` hook (Q-ALL). The birth that takes x1 is the first observer's setting birth, the birth that takes y1 the
    second's; their takes are the settings, from the options the engine offers. The other birth (y2's in start A, y3's in
    start B) is the third birth; each of its choices is a separate history. A birth is the knot nae(its inputs in the
    engine's order, its fresh distinctions); fresh names za, zb, f3 (with suffixes if a birth had more than one).
    Option pairs: the first observer's three pairs of TD 4.1 against the second observer's two eligible options, the one
    earlier in TD 4.1's list (y2, y3, t) at b = 0: (y3, t) for start A and (y2, t) for start B. P7 is judged on (x2, x3)
    against that pair (the record's 55/27 pairs); the pairs with c are reported beside. Pooled: counting from the start
    and from stage s with ν uniform over the two third-birth histories; counting from the finish pooled by TD 3.5 and
    with ν uniform, both reported. The third birth sits in the setting stage (one round); in the mixed stages it goes
    with the second observer's setting knot (it is a birth of the second observer's live knot). For h3′ it is checked as
    a later knot (whether it holds fresh distinctions of both sides).
18. **The 8/3 case** (REVIEW-LEADS-20261123-001C, results_draft.md line 74), as written: the first observer's side
    odd(x1,x3,s1), odd(h1,h2,h3), even(x2,h1,h2,h3); the second's "the same with even(x1,x3,s1)", read with the second
    observer's names: even(y1,y3,s1), odd(k1,k2,k3), even(y2,k1,k2,k3). The start is these six knots; setting knots TD 4.1;
    records TD 4.2.
19. **The 8 gaining parts and the 27 parts with laws handed out** (ONE-PARENT-REREAD-20261123-001A): every record with
    t = 1 of `census_gains_c_*.jsonl.gz` ("at their gaining choices" read as the round-1 gains): arm `uniform`, the 8
    parts, 16 records; arm `mixed`, the 27 parts, 664 records (both conventions and every recorded choice). Each record is
    one history: the part is the record's knots less the last len(births[0]); stage 1 is those births; the setting knots
    of TD 4.1 are added. Every common stage is counted from (the part, and after the round), and the mixed stages. The
    table's T07 ("20 of the 27 sampled") is superseded by the pre-registration's "all 27".
20. **Rule R's 7 three-holder parts** (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C): every record of
    `arm1_gains_three_*.jsonl.gz` (214 records, all t = 1, 7 starts), read as in R 19 (start = the record's knots less the
    round's births).
21. **Keyed settings** (TD 4.5): the first observer keyed, g on its allowed old patterns of (x1, x2, x3); the second
    observer's setting fixed at each value; reported, the largest change of the second record between two functions g,
    under counting from the start and counting from the finish pooled (TD 4.5's normalisation), and against the constant
    functions. 11-knot: the 16 functions of its 4 allowed patterns; 18-knot: all 256 functions of the three old values
    (functions that agree on the allowed patterns give one history and are all run).
22. **The 18-knot's 512 start states** are also enumerated by SAT with blocking clauses (pysat, minisat22) and compared
    with the engine's enumeration; completions per setting pair are the engine's.
23. **Each record is a history**; duplicate structures are not removed for the scores (part 8 removes them).
24. **The P2 verdict** is given for every counting from a common stage s′ ≤ s of every structure and variant (and
    pooled), with the hypotheses checked per variant; the mixed stages and the finish get no lemma verdict (the finish
    breaks the premise; the mixed stage is not common to the four histories).

## Parts 4 and 6 (written while part 2 ran, before parts 4 and 6 ran)

25. **E2** is the order at index 11 of `eleven_registered_400` (the file's JSON list, indexed from 0); the order at
    index 10 (the eleventh, counting from 1) is reported beside and not judged. It is counted from the start (nothing)
    renormalised, as part 6. The lemma's hypotheses are not computed for construction orders: the lemma's form fixes a
    common stage before both setting knots, and an order's knots between the two setting knots fall outside it; TD
    8.2's "Breaks" column is not tested for E2.
26. **E3–E7** as TD 8.2 lists them, on the 11-knot start with the setting pair (x2, x3) against (y2, y3); the second
    observer's setting knot is TD 4.1's unless the row says otherwise; E4's two setting knots form one stage and both
    hold z (z fresh at that stage); E5's and E7's later knot is one later stage after the setting stage, E7's w fresh
    there. P3 is judged on counting from the start (renormalised where weight is lost), E1 on counting from the finish.
27. **Known 7's two other h2 candidates**, nae(x1, x2 or x3, w) with w = h1 or h2 and nothing fresh, are run with the
    first record (x1, x2, x3, w), by analogy with E3, beside the examples and not judged.
28. **Hypotheses of the examples** are checked as in part 2 (R 7, R 8). Where a check finds a break beyond the one TD
    8.2 lists, it is reported as found; TD 8.2's column is not a prediction.
29. **Orders** (TD 8.1): each knot of the order is one stage, bringing as fresh the distinctions no earlier knot holds;
    stage 0 is empty (one state); counting from the start renormalised, per setting pair. The 11-knot lists use indices
    0–10 for the knots of "eleven (start)" in file order, 11 and 12 for the TD 4.1 setting knots (options x2/x3 and
    y2/y3); the smallest-gain list uses 0–6 for the part, 7–8 for nae(y3,s2,f) and nae(y2,y1,g), 9–10 for the setting
    knots. Records TD 4.2.
30. **C5's class**: both setting knots bring only their own fresh distinction for both settings, i.e. every place of the
    setting knot other than za (zb), under both of that observer's settings, is held by an earlier knot of the order
    (the other observer's setting knot counts as earlier only for the places it holds under both of its settings). The
    verdict of an order uses all two-valued functions and hidden. P4 is judged on all 1,200 orders (the registered 400
    as replication, the other 800 as the argument's test), and reported per list.

## Parts 5, 7 and 9 (written after part 4, before parts 5, 7 and 9 ran)

31. **P9's types**: the 183 entries of `census_cases.json.gz` ["nae"] with first status "births" and the 11 entries of
    `disconnected.json` ["nae"]["cases"], in archive order. A type's stage is its `stage_rows`: the source rows, then one
    row per birth; a birth's old places are its names below `source_width`, its fresh distinctions the rest. Every knot is
    not-all-equal.
32. **Counting from the start on a stage** (one round from the source): the source's allowed states equally weighted;
    each birth's fresh distinctions uniform over the completions of its old part; births independent given the source
    state (disjoint fresh sets, TD 1.5). The pair table is the weight of disagreement for every pair of stage names in
    lexicographic order of (i, j), computed exactly by elimination over the source states (at most 2^8). Gates: the same
    elimination with counting from the finish must give the archive's `pair_counts` and `total_words`; and, for stages of
    at most 20 names, the counting-from-the-start table must equal the engine's history enumeration.
33. **"Named" and "under one consistent renaming"**: two types share a named table when their stage widths and their
    tables over the archive's stage names are equal; they share a table under renaming when some permutation of names
    carries one table onto the other (an exact weighted-graph isomorphism test, run within groups of equal invariants).
    The renaming comparison is the stronger: a conflict under the named comparison is also one under renaming. P9 fails
    when two types sharing a table have different `next_birth_count` (or different `next_status`).
34. **Grow again (part 7)**: the starts are the smallest gain's part (its own rules) and the first 10 starts of
    `census_index.json` (stars, every knot not-all-equal). TD 7.1's 4n renumberings: names in increasing order
    (strings by string order, integers by value); rotation k = 0..n−1, as is and reversed; knots as listed and reversed;
    position i named i. Each is grown by `pm.py` under (ORD, STALL, RELEASE) with take Q and choice OLDEST or NEWEST,
    not-all-equal newborns, through 3 rounds. "The start as given" is the renumbering k = 0, not reversed, knots as
    listed (it names each distinction by its rank, as the engine's own naming of the given start does). The finished
    structure is compared after carrying the renaming back: start distinctions by their original names, knots by their
    rule, new distinctions unnamed (an isomorphism of knots and distinctions fixing the start names). "Same history"
    additionally keeps the round each knot was made. Where the structures are the same, counting from the start (the
    rounds as stages) is computed for both and compared through the isomorphism when both have at most 60 distinctions
    and 2^20 allowed states; otherwise the comparison is "same by the renaming of the whole history" when the histories
    are the same, and "not decided (size)" when they are not.
35. **The engine check (part 9)**: the 100 starts of `census_index.json`; the six laws ORDINARY = (ORD, STALL), Q-OLDEST
    and Q-NEWEST (ORDINARY with take Q), RING-LAW = (CAP-3, CANCEL-WAIT, RELEASE), COPY-LAW(CANCEL-RETIRE) = (FLOOR1,
    CANCEL-RETIRE, RELEASE), and COPY-LAW(CANCEL-RETIRE) with MET(OLDEST); knot laws parity (every knot even, closing
    IMPLIED as the engine has it) and not-all-equal; 3 rounds, by `pm.py`. At round j the births' old places are their
    inputs that existed before round j and f_i their fresh counts. The verdict is the first round whose product of TD 7.3
    varies over the allowed old states, decided by enumerating the occurring patterns of (e_1, ..., e_m) with a SAT
    solver (pysat minisat22) and blocking clauses on the indicators of the births whose e_i varies, stopping as soon as
    two patterns give different products. Where the structure after the round has at most 60 distinctions and the
    enumeration at most 2^20 allowed states, both countings are also computed directly, and the rule's verdict must
    agree with them (a disagreement is a bug); after the first parting the total-variation distance between the
    countings is reported where it can be computed so, and "not computed (size)" otherwise.
36. **How part 7 compares structures** (written after timing probes, before part 7 ran; disclosed: the probes showed
    that networkx's isomorphism search does not finish in seconds on the census starts' grown structures, even for a
    structure against itself, and that some renumberings of census start 30 grow structures with a different
    Weisfeiler-Lehman hash under Q-OLDEST, which already bears on P6a). The comparison of R 34 is made in three exact
    steps: (i) **same history**: a key of every knot built from its rule, its round, its parents' keys, its inputs' keys
    (a start distinction by its original name, a new distinction by the key of the knot that made it) and its number of
    fresh distinctions, compared as multisets; equal keys mean the histories are the same up to renaming, hence the
    same finished structure and, by TD 7.1's renaming, the same counting from the start carried back; (ii) **different
    structure**: a Weisfeiler-Lehman hash (4 iterations) of the structure with start names, rules and folded private new
    distinctions as labels; different hashes mean different structures; (iii) otherwise the isomorphism search with a
    limit of 5 s; when it does not finish the row is "structure comparison not decided (search limit)" and counts as
    neither same nor different. Counting from the start is compared numerically, as R 34, only where the structures
    are the same and both histories have at most 60 distinctions and 2^20 states.
37. **Replaces the size limit of R 34 and R 36** (written after a timing probe failed on memory, before part 7 ran):
    counting from the start is enumerated for the numeric comparison only when the grown history has at most 24
    distinctions (the 2^20-state limit could not be checked before the enumeration had already passed the 6 GB cap on
    census start 30, 56 distinctions); otherwise R 36's step (i) decides. Disclosed: the same probe gave, for the
    smallest gain's part, 34 of 48 renumberings growing a different finished structure under each of Q-OLDEST and
    Q-NEWEST and 14 the same, with the same weighting by enumeration.

## The remainder of part 8 (written before it ran)

38. **Structures of part 8's remainder.** Projection on every structure of structures.json, every finished structure of
    part 2 (every item, variant and setting pair; every record), every record's start and stage after the round, the
    8/3 start, and part 4's finished structures, duplicates removed (a structure is its set of knots). Part 3's 2,560
    structures were tested by projection in part 3 itself (part3_signs.json). The canonical command: first the 33
    structures in structures.json order (the 16 of the 11-knot, 8-knot and smallest-gain structures reuse the early
    run's checks, the same command on the same structures), then part 2's finished structures in build order (items,
    then records), each of at most 20 distinctions; the 20-minute cut counts part 8's early run against the budget.

## The report (written before report.py ran)

39. **Table rows.** Rows T01–T07, T09–T11, T13, T15, T17, T18 and T36 are filled from this run's raw files and marked
    "recomputed here"; every other row is copied from table.json and marked "from table.json (not recomputed here)".
    "Changed by" is the counting-from-the-finish value less the counting-from-the-start value. The knot column of a
    recomputed row is "all" or "fails: ..." over the row's structures, with the method (canonical agreement, projection
    only, or the canonical check cut).
40. **A label in part2_lemma.json.** The keyed-setting key "attained by (g, g′) as bit strings over the patterns" writes
    each function with the most significant bit first: the last character is g of the lowest-numbered pattern (11-knot:
    of the first listed allowed pattern; 18-knot: of pattern 0, the integer with bit i = the value of the i-th of x1, x2,
    x3).

## After the run: what was cut, and what the frozen texts left open (no reading changed)

41. **Cut.** Part 8's canonical command was not started on 1,046 of the 2,578 registered structures (all of them
    finished structures of ONE-PARENT-REREAD's 27 parts with laws handed out, the last in build order) when part 8's
    20 minutes ran out; their projection verdicts are kept and marked "canonical check not run (cut)". Every other part
    ran in full within its count-based cut.
42. **Found in the frozen texts.** (a) TD 4.4's parity score has no absolute value, the records' parity scores have one
    (R 16). (b) TD 4.1 gives the second observer's options as y2, y3, t, which on the two 10-knot starts are not all
    eligible (one of y2, y3 is loose there); R 17 takes the options the engine offers. (c) TD 8.2's "Breaks" column
    lists one hypothesis per example; the checks find more for E4 (h1′'s third clause and h2 as well as h3′: the shared z
    is held by both setting knots and weight is lost) and E5 (h3′ as well as h4: the later knot holds za and zb). (d) The
    table's T07 asks for "20 of the 27 sampled", the pre-registration for all 27 (R 19). (e) The pre-registration's
    estimate of part 8's canonical checks (2,000 to 6,000 for part 2's structures) was low: part 2 built 2,545 new
    finished structures in the canonical list (2,578 candidates less the 33), about 1,700 of them of at most 20
    distinctions and not already checked, so the cut was reached.
