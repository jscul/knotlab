# Deviations and readings, MADE-COPIER-20261125-001A-E001

Written by the engine's author, who wrote the fold study's engine and has not seen the drafter's scratch folder
(`scratchpad/copier_survey/`) or the study's `advisor/` folder. The frozen files (P, D, the claim, the owner's arm, the
three data files) and the fold study's definitions match the SHA-256 sums of `contract.json`; this was checked before any
code was written. The fold engine (`pm.py` `3aa69b5b...`, `knots.py` `9138ae86...`, `paired.py` `70a691de...`) is
imported unchanged.

Citations: "P" the pre-registration; "D s.i" this study's definitions; "FD s.i" the fold study's; "SD line n" the shared
definitions. Every item says where the text leaves a choice, the reading taken, and which runs it affects. Items 1 to 16
were written before any registered run; each later item says when it was written.

## The engine

1. **The growth code is the fold engine, imported.** The fold engine as it stands includes its own later repairs (its
   deviations 19, 39 and 43: a cache of ancestor levels kept for each structure, the way's first step, and an earlier check of the pairs
   guard that changes no stop, checked there on 1,344 runs). The gate P0 compares runs grown through this study's
   wrapper with runs grown by the fold engine's `pm.Run` directly; as P says, this tests only the wiring.
2. **Renamings (D 4.5).** n1 is the fold engine's "names reversed" (`from_stars(..., reverse_names=True)`); n2, n3 and n4
   are the label maps of starts.json applied to every label before naming. Barred labels of a start (X alone, Y alone) are
   barred by name after naming.
3. **Descent (D 2.6)** is read from X and its descendants and Y and its descendants (FD 4.2, the fold engine's
   `side_of`). Knots placed by hand (D 3.6) count as made after round s and descended from neither.
4. **Which Y the form reading compares with.** D 3.1 compares with "Y as it was after round s". Y's members are made in
   round 1 on the made designs, so their places depend on the ration (two loose places each under FLOOR1, up to three
   under CAP-3). Reading: in a run of design d under law L, the reference for Y is design d's Y after round s in run A
   of d under L; the references for the other members Y′ of the class (condition 2, the census of the form classes and
   the parts by descent) are Y′ after round s in run A of design Y′ under the same law L. On the designs with Y present
   from round 0 (s = 0) the reference does not depend on the law.
5. **"The same" (SD lines 29–30)** is decided as in the fold study: a graph with one vertex per member coloured by
   (h, k) and one per maximal met set of the roster lying in the part, compared by an exact isomorphism test after
   cheap invariants.
6. **Ties under not-all-equal (D 3.3).** Allowed states are sampled with a solver (24 samples, each under random values
   for up to three distinctions, seeded per round); distinctions are grouped by their values across the samples taken
   relative to the first sample (equal and unequal fall in one group, with a sign); every claimed tie is confirmed by a
   solver call (an allowed state breaking it refutes it, is added to the samples, and the grouping is redone). So every
   reported tie is proved and every pair reported untied has a state that separates it. Under parity ties come from a
   basis of the allowed states (the kernel of H), as D says: equal coordinate vectors, frozen when zero.
7. **The built-structure reading (D 3.2).** Y's knots are Y's members and every knot holding a place of a member, with
   all their places (D 2.4). A renaming maps them one to one onto a set K′ of knots made after round s; the places
   correspond when, place by place, the set of K′-knots holding it (under the knot map), whether a holder lies outside
   K′, loose, and barred (for loose places) agree. Such a place map exists exactly when the multisets of these four
   values agree, which is what is tested. The search maps knots in an order in which each shares a place with an
   earlier one, among knots of the same signature (places, loose places, barred places) that share places with the
   images of earlier knots in the same number; distinct sets K′ are counted; it stops at two sets with no common knot or
   at 10,000 distinct sets. Counting mode counts distinct sets up to 10,000.
8. **The values reading (D 3.3).** A made distinction is a fresh distinction of a knot made after round s (a name at or
   after the number of distinctions after round s); its descent is its maker's (its first holder). Usable and loose: one
   holder, not barred. A place v is read when it is a place of Y (held by a member of Y after round s), not frozen
   after round s, and tied to no place of X after round s (ties read after round s). With three or more usable loose made
   distinctions tied to one v, "two made by X" holds when at least one of them is descended from X only or from both;
   all are listed with their descents and signs. Places of X are read the same way for P9.
9. **The meeting round (D 2.3)** is the fold engine's "one part again" round in run A: the first round after s with a
   member of X and its descendants and a member of Y and its descendants in one part.
10. **Knot tests of comparison runs** at their last round read, as the fold study's item 18: under parity every knot by
    both methods; under not-all-equal the knots made after round s by the birth method and, at most 12 places,
    directly, while knots made by round s keep run A's verdict (the structure through round s is run A's, barring and
    masks change no allowed state). X alone, Y alone, the third-pattern runs, the replacement runs and the renamed runs
    are runs A of their own starts and are tested as runs A.
11. **PO1.** The allowed states restricted to a set of existing distinctions can only shrink as knots are added, so
    "the same after every later round" is decided by comparing round t with the last round read: parity by the rank of
    the set's coordinate vectors over the basis, not-all-equal by the number of assignments of the set that extend
    (a solver call per assignment), over the 12 smallest names when the set has more (reported so). Its second clause is
    checked on every input of every birth.
12. **T and the comparisons (D 7.1).** Traces are compared through T, the last round reached by every run the reading
    names (for the courses: run A, B(i), B_X, M and M_Y; for (iii) also X alone and Y alone).
13. **The state of a pattern at a round (PO8, and the owner's arm).** "ended at round r", "makes a birth in the last
    round read", "every member left waits", or "members left, no birth" (D 7.2, 7.3), read at round T.
14. **The two-knot part (P3, run 3)** is the pattern of two members holding two usable loose distinctions each and
    nothing barred, lying in one met set (the record's definition); "the same as the two-knot part" is decided by the
    sameness of item 5 against that pattern.
15. **"Takes from the other" (D 7.5)** is decided on the rule takes (step 5′) only; a birth's descent and a holder's descent are
    those of D 2.6, read in the structure of the last round read (a knot's descent never changes after it is made).
16. **Placed by hand (D 3.6).** The new knots are made after round 3 (their round is 3, no parents); the knots placed for
    Y's members hold usable loose distinctions where Y's members did and so are members; the further new knot and
    the last new knot hold no usable loose distinction. The counts before and after the placing are read on the same
    structure after round 3.

## Run G and run R (written before they ran)

17. **The 600 drawn structures (P, run G).** `random.Random('2026112505')`; for each: the number of knots uniform in 2
    to 7, the number of distinctions uniform in 4 to 11, each knot's places 3 to min(5, that number), drawn without
    repetition, unused distinctions dropped and the rest renamed in order. Ties are compared with every assignment
    (classes, frozen distinctions, and the sign of every pair in a class), under both knot laws; a structure with no
    allowed state is compared as such.
18. **Sameness and renamings against brute force.** Each drawn structure is grown one round under
    COPY-LAW(CANCEL-OFFSHOOT) (the fold study's name for (FLOOR1, CANCEL-OFFSHOOT, RELEASE), not a law of copying)
    with MET(OLDEST), parity. Every part of the roster after round 1 (of at most seven members)
    is a stated pattern; sameness is compared with every other part by every one-to-one map of members; the renamings of
    the part's knots (its members and every knot holding a place of a member) among the knots made in that round are
    counted by the search and by every injective map, where there are at most 300,000 maps (the rest are counted as too
    large). In addition to the registered check, positives are made on the first 200 drawn structures, wherever the
    roster after round 1 has a part (105 of them): knots repeating that part's knots are placed by hand as D 3.6 places
    them; the search must find exactly one renaming among the placed knots and the form reading exactly one part.
19. **Run R.** The parity structures' parts are read alone (the listed knots only; a distinction held once among them is
    an end). Parts with a frozen distinction or fewer than two ends are counted and not read (P's disclosure counts them
    so). The 80,811 labelled structures are rebuilt here: one to three knots of three or four places, knots and places
    in order, each place loose or paired with one place of another knot. The counterexample's join is the knot
    {7, 8, 9}, 9 fresh.
20. **A fault in my first run of the controls, repaired, rerun** (written after the first gate run). The placing by
    hand first repeated Y's knots as they stood after round 3, not as they were after round s (D 2.4, D 3.6), so the
    knots placed for Y's members held shared places and were not members: both counts stayed at 0 and P14 failed. The
    placing now takes Y's knots, places, holders and barred marks after round s and adds them to the structure after round 3. Rerun:
    P14 holds. No other gate part used the placing.

## Run 2 (written before it ran)

21. **One job per law.** Run 2 is run law by law (a base law, MET or STEPS-1, a rule, a knot law: 144 laws), each job
    growing all twelve designs, so that the references of the class members (item 4), condition 2's counts and the
    replacement runs are read under the same law. The replacement run with Y′ (D 4.4) is run A of design Y′: the made
    designs differ only in knot 1, and the designs with Y present from round 0 only in Y's members and z.
22. **Masked runs (D 4.7).** M is used for both patterns (D: "M_Y (the same as M)"); M′ makes Y and its descendants
    joinable with nothing; M′_Y makes X and its descendants joinable with nothing.
23. **Takes against the course (PO4).** The first take between the patterns in either direction (X from Y or Y from
    X, D 7.5) is set against the first differing round of the course; joint takes are reported apart.
24. **Reading (iii).** T_iii adds X alone and Y alone to T; X's course in run A is compared with X's course in X alone on
    traces renamed by first appearance through T_iii; the course comparisons of (iii) are made at T_iii.
25. **Two users (D 3.3).** When run A has two usable loose made distinctions tied to a place of Y made by X, run A is
    grown again to 8 rounds under the same law; the two of the first such reading are "taken by different births" when
    both are taken after the round seen and the births taking them are not the same; whether both are still tied to v
    at round 8 is reported.
26. **The fourth mark (D 5.3, P17)** is read between class members only (6 pairs per law on the made designs, 10 on the
    designs with Y present from round 0, P17's 864 and 1,440), on X's trace renamed by first appearance through the
    last round both runs reached.
27. **Condition 2 and the parts by descent.** In run A of every design, at every round after s, the parts the same as
    each member Y′ of the class (any descent) are counted by descent, with Y′'s reference from Y′'s run A under the same
    law. The control designs (made-2, made-2-exchanged, two-22) are read against the class too.
28. **X alone.** With the course, the parts the same as Y in X alone are counted at every round (to say whether two
    parts the same as Y are X's own course).

## Run 4 (items 29 to 32 written after the replay of the 33 take lists and before every choice was run)

29. **The replay (P8a)** grows rounds 1 to s with no take asked and then, round by round, gives each take the listed
    name (a listed name that is not a candidate, or a list left over, is reported as a failure of the list). Run 4's
    laws are written with MET(OLDEST) as the fold engine names them; under every choice the law's own rule is never
    used, since every take is decided by the chooser (FD 2.5's ALL-CHOICES; D 2.7).
30. **The values reading in run 4 is read birth by birth** (S1 and S3, P "Settled by construction"): under parity a
    birth with one fresh distinction f has f tied to a place v exactly when the sum of its inputs and v lies in the span
    of the rules before its round; a birth with two or more fresh distinctions, or none, ties nothing to v; and, by S1,
    a tie to v is the same at every later round. This is exact for the laws of run 4 (FLOOR1 and CAP-3 with IMPLIED), and
    it is checked against the full basis of D 3.3 on every history with two of a place of Y made by X, on every 97th
    history, and on all 33 replayed lists (no disagreement on the lists). Under not-all-equal (made-2) ties are read with
    the solver at the last round of each history and carried back by S1.
31. **Every choice (D 2.7).** Histories are counted depth first up to 60,000 (rounds s + 1 to s + 4, a history ending
    early when the growth stops, passes 500 knots or meets the guard); at most 60,000 are all read, otherwise 20,000 are
    drawn with the seed and calls D 2.7 gives. A history is counted once for each kind of case it shows at some round
    (whose place: Y or X; who made the two: made by X, by Y only, by neither). Every history with two of a place of Y
    made by X has every knot tested at every round (both parity methods); "the first three" are the first three such
    histories with every knot passing, in the order read.
32. **PO8's states** are those of item 13, read at round s + 4 (or the last round of a history that ends earlier).

## Runs 3 and O (written before they ran)

33. **Run 3's pairs (D 4.8).** For each s from 0 to 4 (and less than the last round read), every part X of the roster after
    round s the same as the two-knot part (item 14) and every other part Y that is not the same as X and lies in another
    class (wholly apart), whose meeting round (item 9) is at most 7. The fold study's smallest case gives no pair here:
    its second part is itself the same as the two-knot part. The n4 renaming of the fold study's starts, which
    starts.json does not list, is drawn by D 4.5's procedure with the pair start's name; that procedure reproduces all
    twelve n4 maps starts.json lists. Run A's knot tests are made once per run and shared by its pairs.
34. **Run O (D 7.9).** D0: the distinctions held by X and its descendants after round s + 1 (the ten smallest names if
    more). The first round t ≥ s + 2 at which the restricted allowed states differ from those after round t − 1 is found
    by the measure of item 11 (rank, or the number of extending assignments; containment makes an equal measure an
    equal set). "Removing those births' knots" removes the knots of the births of round t that receive nothing and are
    not implied, and the measure is compared with round t − 1's. The knot test is read at round t on every knot (both
    parity methods; under not-all-equal directly, as FLOOR0 and ONE-FEWER need). Under not-all-equal the tie classes
    containing a made distinction are read at every round (S1 does not hold under these rations).

## Run 5 (items 35 to 39 written before any of run 5 ran)

35. **Run 2's cases and their swaps.** A case is a design and law of run 2 whose run A has two of Y made by X in a
    reading at some round read (values: two usable loose made distinctions tied to one place of Y, at least one made by
    X; form and built structure: two, every member or knot descended from X only). The controls (made-2,
    made-2-exchanged, ystart-two-22) are swapped too and reported apart. Each swap changes one thing of the case's law
    (P, run 5's row): each other rule; each other of the nine base laws; each renaming registered for the design
    (starts.json; made-2-exchanged has n1 and n4); the order of births reversed; demand before the takes; HOLD; STEPS-1
    for MET (MET for STEPS-1); the other knot law. A swap "survives" as D 4.5 says for a renaming: run A under the swap
    has two of Y in the same reading, made by X, at some round read. Each swap's run A is knot-tested at every round.
36. **Run 3's cases (P, run 3's row: n1 and n4 only).** X and Y of a run-3 case are parts after round s; under a
    renaming the growth (and so the parts) may differ. Reading: the case survives a renaming when the renamed run has a
    pair of D 4.8 at the same s whose Y is the same as the case's Y (SD sameness, against the case's Y after round s in
    the case's own run) and which has two of Y in the same reading, made by X.
37. **Run 4's cases are the 33 registered take lists.** The histories every choice finds are counted (P8b, P9), not
    listed; the take lists are run 4's listed cases. A take list has no rule, so the swaps that name a rule (the other
    rules; STEPS-1 for MET) do not apply. The others (the other base laws, the renamings registered for the design, the
    order of births reversed, demand before the takes, HOLD, the other knot law) are made with D 7.8's translation, the
    only rule the text gives for carrying a take list to another run: births answer births of the same round and kind
    whose parents answer (offshoots by their number among that parent's offshoots of the round, in the round's birth
    order), start knots by their order, start distinctions by label (through the renaming's label map; n1 keeps the
    labels), fresh distinctions of answering births in order; a birth with no answer, a translated take that is not a
    candidate, or a listed take left with no take to answer gives "the list does not apply from round t". Rounds 1 to s
    are part of the list's run as the replay grows them (no take is asked there). The swapped run is read in values
    through the list's rounds. The translation applied to the list's own start and law gives the list's own run on all
    33 lists (checked in every job, reported as "identity").
38. **Reading (iv) (D 7.8).** Rounds read: 6 under a stated rule (the case's run), the list's rounds under a take list.
    T is the last round reached by both the run with Z and the run with Z barred. The places of Y and of Z are those of
    their members in the start with Z (with Z barred, Z's members are no members, so Z's places are read from the start
    with Z). Two of Z (clause c) is the values reading of D 3.3 with Z for Y: two usable loose made distinctions tied to
    one place of Z, at least one descended from X, descents read for X and Z (D 2.6). Under a take list the run with Z
    barred takes as the run with Z does (D 7.8's rule; with Z barred no birth has a parent among Z). Whether the list
    applies is reported for each of the two runs; each run that applies is read through its own last round, and (a) to
    (d) are read, at T, only for a third pattern under which both runs apply (otherwise "the list does not apply" for
    that Z, with the round). Ties are read with the full basis (parity) or the solver (not-all-equal) at every round.
39. **The form arm's swaps.** The form arm's runs are the six base laws CAP-3(t) and FBP(t) × MET and STEPS-1 × four
    rules × both knot laws × the 11 designs (made-2 to made-6 and the six designs with Y present from round 0); each is
    run under n1, n3, n4, the order of births reversed, demand before the takes and HOLD (6,336 runs). Under a renaming
    every design and every class member's reference is renamed alike (item 4). Read: the form reading by descent at every
    round and the parts the same as each member of the class, for the counts of each swap and condition 2.

## Changes to the engine while runs 1, 2 and 4 ran (written when made, before runs 3, 5, 6 and O)

40. **The not-all-equal ties, faster, the same result.** Item 6's confirmation loop refuted one claimed tie per pass and
    then regrouped every distinction; it now checks every claim of a pass, adds every separating state found, and
    regroups once. The loop still ends only on a pass in which the solver confirms every claim, the first sample is
    the same, and so the partition and the signs are the same. Runs 1, 2 and 4 were started with the earlier code and
    keep it; runs 3, 5, 6 and O use this one. Checked: both codes give identical classes and signs on 33 structures
    (every round of four grown runs under not-all-equal and of the Fano piece grown seven rounds), 17 times faster.
41. **Knot tests count failures by kind.** The brief of the knot tests also counts every failing knot by kind (join,
    offshoot), so that P10's "only at joins" can be read when a run has more failures than the twelve listed. Runs 1,
    2 and 4 list twelve; any of their runs with more than twelve failures is regrown for the count.
42. **Runs 1 and 2 resumed with the faster code.** Run 1 (766 of 918 runs written) and run 2 (75 of 144 laws
    written) were stopped by their process numbers, their result files rewritten as complete files of the rows written, and
    both resumed (`--append`) on the rest with item 40's code. Each row is one complete run or law, so no row is mixed.
43. **Item 40, a second time: memory** (written after run O's first start, before its rerun). Run O's first start
    ran out of memory in one run (made-2, ONE-FEWER(CANCEL-OFFSHOOT), MET(IN-TURN), not-all-equal), where FLOOR0 and
    ONE-FEWER leave large tie classes and item 40's pass kept one full state per refuted claim. The states are now
    kept as bit masks and at most 64 separating states are added before the classes are formed again; the loop still
    ends only on a pass in which the solver confirms every claim, so the partition and the signs are unchanged
    (identical on the same 33 structures, and compared with the original code on run O's structures where the
    original finishes). Run O was stopped by its process numbers and rerun from the start (and stopped again, item
    45); runs 3 and 6 and run 5's cases, take lists and reading (iv) used item 40's code (run 6 started 23 seconds
    before this change, by the files' times).

## After runs 1 to 3 (written before the run it names)

44. **X alone and Y alone for made-2-exchanged.** starts.json's "alone" has no entry for made-2-exchanged, and run 2
    first read X alone and Y alone only for the designs it lists. P's run 2 row names X alone and Y alone for every
    design, and D 4.6 defines them for the made designs: the start knot of the pattern alone, with the shared
    distinction 0 barred. For made-2-exchanged (`[[0,3,4],[0,1,2]]`, X the offshoots of knot 0) that is X alone
    `[[0,3,4]]` with 0 barred, X = {1, 2}, and Y alone `[[0,1,2]]` with 0 barred, Y = {1, 2}, s = 1. A supplementary run
    (`run2_exchanged_alone.py`) regrows made-2-exchanged under the 144 laws with these and replaces its X alone, Y alone
    and reading (iii) fields; nothing else of run 2 changes (run A is regrown and checked equal).
45. **Item 40, a third time: diverse states** (written after run O's second start stalled, before its third). On run O's
    largest structures (FLOOR0 and ONE-FEWER give up to about 71,000 distinctions) the solver's states, found with its
    saved phases, were nearly alike, so the first samples grouped almost every distinction together and the
    confirmation took very many passes. Every solver call is now made under random phases (seeded per round), and states
    are kept as byte arrays. The loop and its ending are unchanged, so the partition and the signs are the same (an
    allowed state's own values do not enter a class or a sign: two tied distinctions agree, or disagree, in every allowed
    state). Checked: unit tests rerun (all pass); against every assignment on 696 structures (the 600 drawn structures
    of run G and 96 grown from the Fano piece and the record's counterexample under four base laws, 39 tie classes
    among them), no mismatch; against item 40's and the original code on 41 grown structures of run O's and run 2's
    laws, identical wherever those finish within 60 seconds (all but one structure of 71,394 distinctions, which this
    code finishes in under a second). Run O was stopped by its process numbers and rerun from the start with this code,
    and run 5's form arm after it.
46. **Run 4 resumed with item 45's code.** Run 4 was started with the original tie code (item 6), which its
    not-all-equal enumerations use at the last round of every history; on made-2 under CAP-3(CANCEL-OFFSHOOT) that made
    one enumeration take more than an hour. It was stopped by its process numbers after 8 of its 72 enumerations had
    been written (each row one complete enumeration) and resumed (`--append`) on the other 64 with item 45's code, which
    gives the same tie classes. The parity enumerations do not use that code (dev 30).
47. **A round whose roster meets the guard is not read** (written after the first pass of the form arm's swaps, before
    its errored laws were rerun). P's bounds: a run's roster is "read where the fold engine's guard allows, otherwise
    reported 'not read'". My first code let the guard's stop in a roster end the whole job; no job of runs 1 to 3, 5's
    cases, take lists and reading (iv), 6 or O met it (none wrote an error), but some laws of the form arm's swaps did.
    Now a round whose roster meets the guard is reported "not read" in the form reading and in the parts the same as
    each member, and the run's other rounds are read; the form arm's laws written with that error are rerun
    (`run5.py form --append`) and replace their error rows.
48. **Run 4 resumed once more, with six workers** (written when done). With the other runs finished, run 4 (14 of 72
    enumerations written, each row complete) was stopped by its process numbers and resumed (`--append`) with six
    worker processes instead of three; nothing else changed.
49. **Run 4: whether there are more than 60,000 histories is decided by a lower bound first** (written before run 4's
    third resumption). D 2.7 counts the histories depth first and reads them all when there are at most 60,000. Every
    structure reached after round s + 2 (then s + 3) that has not stopped leads to at least one history, so the number
    of such structures, with the histories that stop earlier, is a lower bound; when it passes 60,000 so does the count,
    and the enumeration is drawn, as before. Otherwise the histories are counted to the end exactly as before. The
    decision, and so every result, is unchanged (the counts 16, 32 and 9 of three enumerations read in full are
    reproduced); under CAP-3(CANCEL-OFFSHOOT) on made-2 the decision now takes 86 seconds instead of more than an hour.
    Run 4 (29 of 72 enumerations written) was stopped by its process numbers and resumed (`--append`).
50. **P10 on run 4's failing knots** (written before it ran). Run 4 tests every knot of every history with two of a
    place of Y made by X, at every round, but kept the failing knots' kinds only for the histories it listed. The drawn
    histories under COPY-LAW(CANCEL-OFFSHOOT), parity (the only ones with two), are drawn again with the same generator
    and calls (`run4_fails.py`), so they are the same histories (checked: the number with two is run 4's for every
    design), and every failing knot is listed with its kind, inputs and fresh count.

## Added after the freeze (on the thread's instruction, from the design advisor; changes no frozen text and no run)

51. **Added after the freeze: a wider family of numberings for every case that passes the registered renamings**
    (written before `run7_numberings.py` ran). Passing n1 to n4 does not show that the takes are not fixed by names. So
    every case of run 5 that passes the renamings registered for its design (here: made-4, FBP(CANCEL-OFFSHOOT),
    STEPS-1(NEWEST), form, under each knot law, which passes n1, n3 and n4) is also run, same law, rule and reading, under
    the 4n numberings of its start of n distinctions (made-4 has 7, so 28): the n shifts of the order of its
    distinctions (shift i: the distinction at position i named first, the order otherwise kept cyclically), each as given
    or reversed, with the start knots as given or reversed. X and Y are carried to the renumbered run by what they are
    (knots made in round 1 by their parent and their order among that parent's offshoots). Reported: the numberings run,
    the distinct named starts among them (distinct up to the start's own symmetries), how many it passes, and any
    condition on names visible in which pass. A case that fails any one is reported "under a supplied numbering"; one
    that passes the registered renamings is reported "passes the registered renamings (n1, n3, n4)", and its "what fixed
    the takes" is "not decided by the registered test" unless it passes every numbering run. Output `run7_numberings.json`,
    apart from the registered runs' outputs. No change to a registered verdict or to the stop rule.
