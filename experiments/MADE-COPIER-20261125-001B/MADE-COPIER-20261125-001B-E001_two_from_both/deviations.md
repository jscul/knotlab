# Deviations and readings, MADE-COPIER-20261125-001B-E001

Written by the engine's author, who wrote the fold study's engine and ticket A's engine and has not seen the drafter's
scratch folder or the study's advisor folder. The frozen files (PB, DB, ticket B's claim, the two data files, D, FD, SD)
match the SHA-256 sums of `contract.json`; this was checked before any code was written. The fold engine (`pm.py`,
`knots.py`, `paired.py`) and ticket A's engine (`mc.py`) are imported and not changed for ticket B; what ticket B needs
beyond them is in this folder (`mcb.py`).

Citations: "PB" the pre-registration; "DB s.i" ticket B's definitions; "D", "P" ticket A's; "FD", "SD" the fold study's
and the shared definitions. Items 1 to 24 were written before any registered run of ticket B.

## The engine

1. **The guard (DB 3.9).** The fold engine's limits `pm.GUARD` are multiplied by ten when `mcb.py` is imported, in that
   process only; the fold engine's file is not edited. Bounds: 8 rounds, 10 under CAP-3(t); a run stops after the
   first round past 2,000 knots (the fold engine's knot bound, set to 2,000).
2. **Ticket A's engine is used as it stands**, including its tie code after its deviations 40, 43 and 45 (ticket B
   reads no ties) and its knot tests (D 8; ticket A's deviation 10 for comparison runs).
3. **"The same" (SD lines 29–30, DB 2.5).** A part's form is decided exactly: a graph with one vertex per member coloured
   by (h, k) (and, for the marked roster, by its descent mark) and one per inclusion-maximal met set in the part;
   candidates are bucketed by invariants and the Weisfeiler-Lehman hash and decided by an exact isomorphism test, never
   by a hash. A roster (marked or not) is the same as another exactly when the multisets of its parts' forms agree,
   since its parts are the components of the relation joinable; that is how rosters are compared (PB3, PB4, PB13's R3).
   Form classes are numbered within each job (one law and knot law); across jobs they are merged by the same exact test.
4. **Y's form (DB 3.3)** is the form of the part Y's members form in Y alone at round 0 (starts_b.json, "alone", e
   barred); X's form likewise from X alone. Each kind's X alone and Y alone are checked to have one form.
5. **Parts the same as Y's form** are counted with any members, start knots included, for the conditions (a) to (d)
   and the per-round counts ("of any descent", DB 3.7). **Descended from both** requires every member descended from
   both (D 2.6 with s = 0); a part of Y's form whose members have more than one descent is **mixed**.
6. **Descent** is ticket A's (D 2.6): the start's members of X are descended from X only and Y's from Y only; the start's
   dead knots, and the start's common knot of X and Y, from neither; a made knot from X only, Y only or both by its
   parents.
7. **The round t of a case (DB 3.5)** is the first round t, through T, after which there are at least two parts of Y's
   form each descended from both and no knot descended from Y only (Y's members included) is a member (SD line 91 read
   for that set). The first round with two such parts is reported with it, also when the knots descended from Y only
   have not ended. **How they ended**: for each knot of that set that was a member at some round, the round after which
   it was no longer one: "barred when it retired" if it retired in that round; "gave its last to a birth that closed" if
   it was a parent of an implied birth of that round; otherwise "gave every usable loose distinction to births".
8. **T (DB 3.8)** for CB-1 is the last round reached by run A, B_X, Y alone and X alone; for (c), the last round reached
   by run A and the run with each other member. A round whose roster meets the guard is "not read" in that run, and a
   condition is read on the rounds that are read (the rounds not read are counted with each verdict).
9. **The conditions.** (a) B_X is ticket A's B_X with s = 0 (run A's start with every usable loose distinction of X's
   members barred); (b) Y alone and (d) X alone are starts_b.json's alone starts; B(i) is reported. A condition holds
   when the count of parts of Y's form is below two at every round 1 to T that is read.
10. **(c) for the other-member swap.** The run with each other member Y′ is the start with the same X, Y′ and the same
    start's meeting: the listed start "X + Y′ / W-other" where it exists, otherwise "X + Y′ / W" (the meeting with the
    first member), since for a kind other than two-23, pairs-3 and pairs-4 the other member is carried to the first by a
    renaming of the start roster onto itself (DB 2.3).
11. **CB-1, CB-2 and their failures (DB 4).** CB-1 holds when the round t exists through T and (a), (b) and (d) hold.
    A failure is "by argument" for the six members of Settled 4 under COPY-LAW(t) (CB-1) and for CB-2 under COPY-LAW(t)
    (Settled 4), and for everything under MET with COPY-LAW(t) (Settled 5); otherwise "by census", with its failed
    clauses: "no round with two" (no round through T with two parts of Y's form each descended from both), "the knots
    descended from Y only not ended", "(a)", "(b)", "(d)" (and "(c)" for CB-2). A failure is "on (b) alone" when (b) is
    among its clauses and every other clause is (d) or (a) where (a) is (b) (W1 to W3, and W4 for Y other than pairs-3
    and pairs-4: PB, Settled 6). The census is run for the members excluded by argument too, as a check of the argument
    (PB5). The per-law class's forms are not named by Settled 4, so their failures are by census.
12. **The class forms among the other parts** at a case's round are the eight kinds' forms, counted by descent.
13. **PB13.** R0 is, for each round, the multiset of forms of the parts descended from both. R1 counts distinct R0
    lists across the eight Y of one X, law, start's meeting and knot law; R2 lists the forms that appear descended from
    both with one Y and at no round with any other Y′ of the eight. R3 is the first round after which run A's whole
    roster (unmarked) is the same as the roster after some round of an alone run of the same base law and knot law: the
    eight kinds' X alone and Y alone and the per-law class's forms alone. "Forms present twice" are forms with two or
    more parts descended from both after some round.
14. **The per-law class (PB15).** Each form's part (starts_b.json, labels from 100) is Y; its Y alone is that part with
    e barred; its starts with every X and start's meeting are built by DB 2.3's rule, with the builder that reproduces
    the 343 listed starts exactly (checked in the unit tests). Read: CB-1 and PB13's lists.

## Runs B1, B2 and B5

15. **One job per base law and knot law** (B1, B2), each reading all its starts, so that (c), R1 and R2, which compare
    runs of different starts, use one numbering of forms.
16. **B2's HOLD set** is the 256 starts under HOLD with the same readings; its alone runs are under HOLD too.
17. **PB3 (B5).** A step is a round t − 1 to t of a run whose two rosters are read; its key is the law, the knot law,
    the release, whether round t closes, and the marked roster after round t − 1; a conflict is a key seen with two
    different marked rosters after round t. Counted per law and knot law and summed.
18. **PB4.** The 78 and 189 round-0 classes of rosters_b.json are labels; they are compared as partitions of the 256
    starts. "Same as alone" is compared start by start. Starts with the same marked round-0 roster are compared, under
    each law and knot law, by their marked rosters after every round.
19. **PB8.** The parity run and the not-all-equal run of a start are compared structure for structure through the round
    before the parity run's first closing (through the last round when it never closes, the two reaching the same
    round). The registered count is under RELEASE (1,536 pairs); HOLD is reported.
20. **PB2** is read under RELEASE, structure for structure at every round (the registered 1,536 pairs).
21. **PB5** is read on every run of B5 under COPY-LAW(t), RELEASE and HOLD: every knot made after round 0 at every
    round; every part whose members are all made.

## Run B4 (PB1)

22. **The renaming check.** For each listed renamed start, both runs are grown under the law; the renaming of DB 7 is
    built round by round: the starts by an exact isomorphism of their labelled incidence (any isomorphism of the two
    starts is a renaming σ); a new knot to a birth of the same kind, parents' images, fresh count and usable count; each
    input from a parent to the image birth's input from that parent's image (which permutes the parent's usable loose
    distinctions, as DB 7 allows); fresh distinctions in order. It is then verified knot by knot (round made, kind,
    places) and distinction by distinction (barred), so a "renaming" is an exact isomorphism, never a hash. Where it
    cannot be built (as under MET), the two structures are compared by invariants, a difference proving them
    different, and otherwise by an exact isomorphism search. "Names reversed" is built with the fold engine's
    reverse_names. The MET control is read under the ten renamings, and the count over the eight of version 1 is the
    one compared with the disclosure (1,860 of 3,456).

## Run B3 (arm 2)

23. **Ticket A's designs (DB 3.0)**: the twelve of run 2, each with its own s; Y's form is the form of the part Y's
    members form in Y alone (D 4.6) after round s under the run's law; made-2-exchanged's X alone and Y alone are those
    of ticket A's deviation 44; the class is 𝒴_made (made-3 to made-6, control made-2) or 𝒴_start (one-2, one-3, two-23,
    two-33, three-222, control two-22); (c) is read in run A of each other member's design (D 4.4, ticket A's deviation
    21); B_X is D 4.3. The 256 starts under MET are read as in B1, with their alone runs under the MET law.
24. **Renamings of a case of arm 2** (DB 1.2): D 4.5's registered renamings for ticket A's designs; for a start of DB 2,
    n1 (names reversed), n2 (label 1000 to −1) and n4 (D 4.5's procedure with the start's key as `design`). A case
    survives a renaming when the renamed start's run A has a round t and its B_X has fewer than two parts of Y's form at
    every round read. No case was predicted; this is read only if one is found.

## During the gate (written when made)

25. **B4's comparison where the renaming cannot be built** (MET, the control). The first start of B4 spent more than ten
    minutes in an exact isomorphism search on large structures under MET. It was stopped (its own processes) and rerun
    from the start with: invariants first, then the Weisfeiler-Lehman hash of the labelled incidence (a different hash
    proves the two different, since isomorphic structures have equal hashes; an equal hash decides nothing), then the
    exact search within 60 seconds, "not refuted" when it does not finish (PB, run B4). The runs with no taking rule are
    decided by the renaming built and verified (item 22), as before. Written as the rerun started.
26. **B5 rerun with one more count**: the steps whose marked roster before has no member, to read the difference from
    the disclosed step count. Nothing else changed; the first B5 results are replaced.

## Added after the freeze (on the thread's instruction, from the design advisor; changes no frozen text and no run)

27. **Added after the freeze: wider numberings where a taking rule is in force** (written before B3 ran). Every case of
    arm 2 (MET) that passes the renamings registered for its design is also run, same law, rule and reading, under a
    wider family of numberings of its start: a start of at most six distinctions, every order of its distinctions, each
    with the start knots as given and reversed; otherwise the 4n numberings (the n shifts of the order of its n
    distinctions, each as given or reversed, with the start knots as given or reversed). Reported apart, in a file of
    its own; a case that fails any is "under a supplied numbering"; one that passes the registered renamings is reported
    as "passes the registered renamings", and its "what fixed the takes" is "not decided by the registered test" unless
    it passes every numbering run. If no case of arm 2 passes the registered renamings, nothing is run and that is
    recorded here. Arm 1 has no taking rule; DB 7's renaming statement covers it (checked in B4) and nothing is added.
    *Recorded after B3:* no run of arm 2 (72 jobs, ticket A's twelve designs in each, 15,714 starts of DB 2 read, 2,718
    not run under the cut of item 32) has two parts the same as Y each descended from both, so there is no case of arm
    2, none passes its registered renamings (item 24: read only if a case is found), and no numbering was run
    (`post_freeze_numberings.json`).
28. **B4 under MET (the control), within the hour's limit** (written before the third start of B4, after the owner's
    limit of about one hour per run). Under MET the renaming cannot be built, and an exact search on the symmetric
    structures of these runs did not finish (more than ten minutes for one renamed start). The control's registered
    count is of renamed runs that differ, so under MET only a proof of difference is sought, round by round
    (invariants, then the Weisfeiler-Lehman hash of the labelled incidence); a run proven different at some round is
    "differs", any other "not proven different" (a run reported so is not shown to be the same). With no taking rule
    the renaming is built and verified as before (item 22); a round where it could not be built would be searched
    exactly for 10 seconds (VF2++), "not refuted" if unfinished. Timed: a MET job under COPY-LAW(CANCEL-OFFSHOOT) 2 s,
    under CAP-3(CANCEL-OFFSHOOT) 196 s, a job with no taking rule about 1 s; 48 jobs on 4 processes, about 15 minutes.

## Runs B1, B2, B3 (timed before they ran)

29. **Timing.** A small part of B1 (16 starts drawn with `random.Random(1)`, with the alone runs) took 1.5 to 3.8 seconds
    under four laws, about 0.2 seconds a start; a job of B1 (256 starts and the per-law class's starts, about 650) is
    then about 3 minutes, and B1's 12 jobs on 4 processes about 10 minutes; B2's two sets less. Nothing is cut.
30. **B3 timed** (before it ran). Per start of DB 2: about 4 seconds under FBP(CANCEL-OFFSHOOT) (mean of 36 starts, at
    most 11), 2.5 under CAP-3(CANCEL-OFFSHOOT), under 0.1 under retiring and waiting; ticket A's twelve designs about
    20 to 40 seconds a law. So a job (12 designs and 256 starts) takes up to about 20 minutes under FBP(CANCEL-OFFSHOOT)
    and 11 under CAP-3(CANCEL-OFFSHOOT), and the 72 jobs on 8 processes, the long ones first, about 35 minutes. Nothing
    is cut.
31. **B3 past the hour: the laws with offshoots under FBP and CAP-3** (written at 47 minutes of B3, when 5 of its 72
    jobs were written). The timing of item 30 was short: jobs under FBP(CANCEL-OFFSHOOT) took 17 to more than 47 minutes
    and under CAP-3(CANCEL-OFFSHOOT) about 19. So the 56 other jobs (retiring and waiting under CAP-3 and FBP, and the
    check row under COPY-LAW) are run now as a separate part (`b3.py --small --out b3_small.jsonl.gz`, one process,
    expected a few minutes), and the first part is stopped by its process numbers at 90 minutes if not finished: the
    jobs under the two laws with offshoots that are written by then are read, and the others are reported "not run"
    (never as a negative). What that can show: arm 2 under retiring and waiting in full, and under offshoots for the
    rules and knot laws whose jobs finished.
32. **B3 cut to fit the hour** (written before its third part ran). Stopped by their process numbers: the first part
    at 80 minutes (8 jobs written: FBP(CANCEL-OFFSHOOT) and CAP-3(CANCEL-OFFSHOOT) with MET(OLDEST) and MET(NEWEST),
    each knot law) and the second at 32 minutes (12 written: CAP-3(CANCEL-RETIRE) with every rule, CAP-3(CANCEL-WAIT)
    with OLDEST and NEWEST). Under IN-TURN and BY-COUNT with offshoots or waiting, single starts of DB 2 take more than two
    minutes each (timed: 5 of the first 5 sampled starts under CAP-3(CANCEL-WAIT), MET(IN-TURN)), so the registered
    run does not fit. The 52 jobs not written are run as a third part (`b3.py --skip-done b3.jsonl.gz,b3_small.jsonl.gz
    --budget 420 --out b3_cut.jsonl.gz`, 8 processes): in each, ticket A's twelve designs in full, the alone runs, then
    the 256 starts of DB 2 in their registered order (starts_b.json's) for 7 minutes; the start under way at the limit
    and every later one are "not run", with the count and the first not run reported. Bounds of rounds and knots are
    unchanged. What it can show: arm 2 on ticket A's designs under every registered law, and on the prefix of the
    starts read; it cannot show anything about the starts not run, which are not counted as negatives.
33. **Four jobs of B3 under MET(IN-TURN) with offshoots: exact form tests on large parts** (written before their
    rerun). In the third part, the jobs FBP(OFFSHOOT) and CAP-3(OFFSHOOT) with MET(IN-TURN), each knot law, ran past
    50 minutes; a trace shows exact isomorphism tests between large parts of equal Weisfeiler-Lehman hash that the
    search does not finish. Under MET the parts reach 616 members (FBP(OFFSHOOT)) and 648 (CAP-3(OFFSHOOT)) in the jobs
    written, while every form a reading of arm 2 reads (Y's form of each of ticket A's twelve designs, the eight
    kinds' forms) has at most 6 members. The third part was stopped by its process numbers at 56 minutes (48 of its 52
    jobs written, the file closed). A first timing of the rerun with each exact test limited to 10 processor seconds
    (VF2++) took 24, 44 and 69 seconds for the first three designs, the unfinished tests accumulating, so that limit
    alone does not fit. The four jobs are rerun (the fourth part: `b3.py --procs 4 --skip-done
    b3.jsonl.gz,b3_small.jsonl.gz,b3_cut.jsonl.gz --budget 420 --iso-seconds 10 --hash-above 24 --out
    b3_cut2.jsonl.gz`) with two changes to how forms are classed, in these four jobs only: a part of more than 24
    members (four times the largest form read) is put in a class by its invariants and Weisfeiler-Lehman hash alone,
    and each other exact test is limited to 10 processor seconds, an unfinished one counted as "undecided" with the
    part's size and the part put in a class of its own. Both are reported per job, with the largest form read. No
    verdict reads a class of more than 6 members, so none depends on either change; the counts of large forms in
    these jobs (the "counts" and "both forms" lists) are by hash and are not used. Tested in `test_mcb.py`
    (`t_iso_limit`). Timed with both changes (FBP(OFFSHOOT) and CAP-3(OFFSHOOT), MET(IN-TURN), not-all-equal): the
    twelve designs and the sixteen alone runs in 86 and about 115 seconds, no test unfinished; with the 7 minutes of
    starts a job is about 10 minutes, and the four on four processes about 10 minutes.
