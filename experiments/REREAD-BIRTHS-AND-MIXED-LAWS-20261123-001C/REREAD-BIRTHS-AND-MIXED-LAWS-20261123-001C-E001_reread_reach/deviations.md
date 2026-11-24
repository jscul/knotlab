# Deviations, readings and limits: REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001

Nothing in "Definitions (frozen)", "Predictions (frozen)" or "Runs and stop rule" of
`research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/preregistration.md` (sha256 4887595485b9...065a, as in
`contract.json`) was changed. Section A was written after the code and its timing chunks (B1; their outputs were
inspected and showed no gain and no hidden score within 10^-6 of 2 on the 130 starts they covered) and before the
study's runs; it lists every place where the note leaves a choice and the reading taken. Section
B, added during and after the runs, lists limits met and anything found after values were seen. Recorded code is
imported by path and never edited: ticket B's `common.py` and `verify_excess.py`, ticket A's `rlaw.py` (sha256
29aa3d91...d8f8 at the start of this work, equal to the freeze; every script asserts it at start), and through them the
recorded `end_operator.py` and the review-leads `lib.py`. One allocation step of `rlaw.Growth.plan_with` is copied
(marked COPIED in `cstudy.round1_input_sets`). Ticket B's outputs are read compressed; nothing in another ticket's
folder is written.

## A. Readings fixed before the study's runs

1. **Starts and classes.** The 49,961 founder starts of ticket B (`starts.jsonl.gz`), with their targets, laws and
   observers (`common.start_stars`). Two-holder: `max_holders` at most 2 (12,147); three-holder: the rest (37,814).
   Stalled: ticket B's history ends in a whole-round stall (`outcome == 'stall'` in its `t1_c3` lines; the same in
   `t1_c2`), 6,312 and 21,575, all at round 1. Starts with more than 20 distinctions at stage 0 were not grown by ticket
   B and are not stalled; they are not in arm 1, and the two-holder ones with no hidden excess are in arm 2.
2. **The engine.** `rlaw.Growth(stars, 'nae', 'R', convention)`: rule R on full holdings, the not-all-equal structure
   rule (every birth has at least one fresh distinction; no closing), as the note's "a fresh distinction for every
   birth". Rounds are planned with no knot cap (`plan(max_births=None)`): the study's own stop is ticket B's, checked
   before each round: after 3 rounds, or once a stage has more than 20 distinctions (that stage is kept and tested). A
   start with no live knot makes no round (`closed`). `rlaw.USE_C` is set to False so that the engine never builds its
   C search into ticket A's artifact folder; the Python search is the same algorithm (ticket A deviations B1).
3. **Names, oldest and newest.** Start distinctions are numbered as ticket B numbers them (order of first appearance
   along the start's knots in the target's order); fresh distinctions take the next numbers in birth order (the
   engine's). Convention O pays with the smallest allowed number, N with the largest (ticket A reading A3).
4. **Residual stall.** As ticket A (A4): some short knot finds no allowed distinction for one of its births; the round
   does not happen and the history ends there. Counted by class, convention and round.
5. **Every allowed round-1 choice** (two-holder stalled starts). A choice is one element of the product of
   `rlaw.Growth.allowed_choices` over the short knots: which births of a short knot receive a shared distinction and an
   injective assignment of allowed distinctions to them; loose distinctions of one knot are not permuted (ticket A
   A1). "At most 64" counts these full choices. With at most 64, every choice is grown (this includes the choices made
   by conventions O and N whenever those are complete). With more, 62 more are drawn: distinct, none equal to the
   choice of O or of N, each short knot's option index drawn uniformly and independently (so uniform over the product)
   by `numpy.random.default_rng([2026112350, target, start bitmask])`, one generator per start. A choice history plays
   round 1 with its choice and later rounds by convention O; when a later round of it has a short knot it is also grown
   with later rounds by N (kind `choiceN`), counted as a further history when its structure differs. The two
   convention histories are always counted as well, so a start with at most 64 choices has its O and N histories
   twice (once as conventions, once among the choices); the counts of histories say which.
6. **Law assignments.** Every newborn is even parity, odd parity or not-all-equal. With n newborns in the history:
   every assignment when 3^n is at most 4,096; otherwise 4,096 distinct assignments drawn by
   `numpy.random.default_rng([2026112351, target, start bitmask, kind, j])` (kind 0 = convention O, 1 = N, 2 = choice,
   3 = choiceN; j = the choice's position), one generator per history. Column j is the j-th newborn in birth order, and
   the assignment of a stage is the prefix of its newborns; a stage's tables are its distinct prefixes (ticket B's
   count). Founders keep the target's laws.
7. **Hidden excess and gain.** As ticket B: the table of old words on the target's six observer distinctions, every
   other distinction forgotten; the supplied setting births; equal weighting of finished words; hidden on both sides in
   exact integers; score screened in floating point and exact (fractions) for every hidden table within 1e-6 of 2 or
   above; a hidden excess is an exact score above 2. A gain is a hidden excess at a grown stage (round 1 or later) of a
   history whose start (stage 0, common to all its histories) has none.
8. **Paying birth and gain through a payment.** A paying birth takes at least one distinction that had two or more
   holders when its round started (checked equal to the engine's payment flags on every birth). For a gain at stage t,
   every paying birth among the stage's newborns is changed to even parity and the other laws kept (newborns of later
   rounds are not in the stage); the gain is through a payment when that table has no hidden excess.
9. **An exact reduction for speed** (arm 1, `arm1.effective_rows`). At stage t a newborn of round t holds fresh
   distinctions that no other knot holds yet, so summing them out gives a constant factor unless the newborn is
   not-all-equal with two or more parents. So every assignment's table equals, up to a positive constant, the table of
   its "effective" assignment (round-t newborns: not-all-equal with two or more parents kept, every other one even
   parity; earlier newborns as assigned), and hiding and score are unchanged by a constant. Tables are computed once
   per effective assignment and counted for every assignment. Every gain is recomputed by direct contraction with its
   actual assignment (asserted equal). Gate part g1 compares the reduced and direct counts on every table of the 500
   two-holder starts; gate part `stages` compares reduced, direct and word-by-word tables on 100 drawn stages.
10. **Row G, choices the note leaves.** Seeds chosen here: 2026112352 (500 two-holder starts), 2026112353 (500
    three-holder), 2026112354 (100 grown stages), 2026112355 (200 pairs), 2026112356 (tables for the scorer check). "Two-
    holder starts with no short knot in any round": drawn among the two-holder starts that do not stall under ordinary
    growth in ticket B (5,835; ordinary growth has no short knot in any round there), and each is checked to have no
    short knot under R. Compared with ticket B: its stars (by its `grow`), knots and distinctions per stage and outcome
    (its record), and per stage the numbers of tables, hidden tables and tables with a hidden excess under its
    three-law assignments (its seed, `common.assignments(..., k=3)`), by direct contraction. Grown stages for the
    word-by-word check: stages t >= 1 of arm 1's histories with at most 24 distinctions (ticket B's limit for the same
    gate), one assignment of the stage drawn; pairs: 200 distinct starts of arm 2's population, one T each drawn
    uniformly among its sets. "Allowed observer words never change": arm 1, every assignment at every grown stage
    against the same assignment one stage before; arm 2, every T against the start's table. The ten known starts:
    targets 135 to 144 without nae(y3,Bh1,Bh2,Bh3), T = {y3, Bh1, Bh2, Bh3}; also checked by enumerating every word of
    their four finished structures, and checked to have no short knot under R in any round.
11. **Arm 2's tables.** M and every M_T are computed from the start's allowed words, enumerated exactly by adding its
    knots one at a time (`cstudy.allowed_words`); M is asserted equal to ticket B's contraction on every start. The new
    table is 2M − M_T (the identity is checked word by word on the 200 pairs). The added knot's fresh distinction is
    named `fT` when written out.
12. **Classes of T.** Shared: two holders in the start (loose: one). Observers: inside one observer's three
    distinctions (T within {x1, x2, x3} or within {y1, y2, y3}); observer distinctions of one side only and others;
    observer distinctions of both sides; none (a partition). Origin, ordinary: T is the input set of a round-1 birth
    with two or more parents made by ticket B's `grow` (the recorded wrapper's placement of loose distinctions), with
    the size stop not applied so that starts with more than 20 distinctions also have a round 1; a start that stalls
    has none. Origin, rule R: T is the input set of a round-1 birth with two or more parents for some allowed choice,
    over every choice when there are at most 4,096 (a start with no short knot has one, and its sets are checked equal
    to the ordinary ones); a start with no allowed choice has none (decided); more than 4,096: not decided for every T
    of that start. A supplementary origin, not in the note, is reported beside it: some placement of the parents' loose
    distinctions gives a round-1 birth under ordinary growth that takes T.
13. **The known shape.** |T| = 4: three shared distinctions and one loose distinction that is an observer distinction.
14. **Smallest.** Arm 1: fewest knots at the gaining stage, then fewest distinctions, then the smallest exact score.
    Arm 2: fewest knots in the start, then fewest distinctions, then the smallest |T|, then the smallest score. "The
    least T that works": the smallest |T| among gains, with the counts at each size.
15. **The share beside ticket B's 34 of 7,957.** Ticket B's 7,957 are its three-holder starts that made at least one
    round under ordinary growth (13,205 histories made a round, 5,248 of them two-holder), and 34 of them gained. Here:
    of the 21,575 stalled three-holder starts, those that make at least one round under rule R (under O, under N, and
    under either), and how many of those gain.
16. **Full enumeration of gains.** Every gain written in full whose four finished structures have at most 26
    distinctions before the setting births is enumerated word by word (`verify_excess.brute_joint_all`, then
    `evaluate_joint`); always the smallest gain of each arm when one exists.
17. **Processes.** Each run with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` (the machine is
    shared), at most six at once, each under `timeout 600 prlimit --as=12884901888`.

## B. Limits and findings during the runs

1. **Development runs.** Before section A was written, two timing chunks of `arm1.py` (tag `test`: 30 two-holder and
   100 three-holder starts) and two of `arm2.py` (tag `test`: starts 0 to 200 and 11,500 to 11,700) were run to size
   the chunks; their outputs were inspected (format, outcomes, hidden counts; no gain and no hidden score within
   10^-6 of 2 in any of them) and deleted. No definition or reading was changed after that inspection; the reduction
   of A9 was chosen for speed, from a cost estimate, before any table was computed, and is exact. After section A, one
   timing chunk of `gates.py --part g1two` (20 starts, passed) was run and deleted before the full part was run. Two
   inline scale probes (rule R on every 20th stalled two-holder and every 50th three-holder start, structures and choice
   counts only, no tables) wrote nothing.
2. **An interactive inspection imported another ticket's module.** `cstudy` puts the folders of ticket A, ticket B, the
   review-leads ticket A and the ordinary engine ahead of this folder on the import path. One inspection command typed
   `import gates` and so loaded `experiments/REVIEW-LEADS-20261123-001A/.../gates.py`, not this folder's. That file
   only defines functions under a `__main__` guard; nothing ran and nothing was written (modification times of that
   ticket's and ticket B's artifact folders checked, all older than this work). Since then this folder's `gates.py` is
   loaded by path when imported (`report_c.py` does so), and the report script is named `report_c.py` because ticket
   B's folder has a `report.py`. The modules this study's scripts import by name (`arm1`, `arm2`, `cstudy`) have no
   namesake in those folders (checked), and every run was a script run, so no study run was affected.
3. **The scorer check was run twice.** Its first run compared the evaluator with the recorded scorer on arm 1's gain
   tables, arm 2's gain tables and 1,000 drawn arm-2 tables, but not on the 1,000 drawn arm-1 tables its own docstring
   promised. Those were added and the part rerun from `verify_jobs.txt`; both runs agree on every table. The first run
   is kept as `gates_scorer_first.json` and `.log`.
4. **No later round had a short knot.** In every history of arm 1, payments happen at round 1 only; rounds 2 and 3
   have no short knot and no paying birth. So the reading of A5 for later rounds (convention O, and N when short) never
   applied, and no `choiceN` history exists. Convention O's own round-1 choice is a residual stall at 216 two-holder
   starts and N's at 197; 190 starts have no allowed choice at all, so at 26 starts some choice pays every birth while
   convention O does not.
5. **Runs near the limit, and enumeration runs stopped by it.** No run of either arm reached the ten-minute limit; the
   slowest, `arm1.py --cls two --lo 5000 --hi 6000`, took 533 s. The full enumerations of arm 1's gains at 27
   distinctions were first queued ten tables per run (`verify_jobs.txt`, from a timing of one 25-distinction table
   while the machine was less loaded): five such runs (items 1797 to 1847) reached the limit and wrote nothing (marked
   FAILED in `verify_runs.log`). After the fourth failure I stopped the queue's dispatcher by hand (no new run was
   started; the six runs already going were left to finish or reach the limit; the fifth failure was one of them). The
   other runs of that queue finished. The 50 tables of the failed runs and the 32 not yet started were then run five per
   run (27 distinctions) and one per run (29 distinctions) from `verify_jobs_redo.txt` (`verify_runs_redo.log`).
6. **Gains written in full.** `arm1.py` writes at most 50 gain tables per stage and history in full and counts all.
   One stage reached the cap (start 43892, convention N, 108 gains, 50 written); 214 of the 321 gain tables are written.
   Descriptions of the paying newborns in the draft are of the 214.
7. **The engine's hash** was checked by every script at its start and at the end of the work: unchanged
   (`summary.json`, `rlaw_sha256`). Other files of ticket A changed during this work (its `deviations.md`,
   `summarize.py` and artifacts `tables.md`, `PRUNED.md`, `summary.json`), written by the sub-agent finishing ticket A;
   none is read here, and nothing of ticket A was touched by this study.
8. **Full enumeration not done** for 157 of arm 1's 321 gain tables: the 50 written tables of one stage of 32
   distinctions (start 43892 under N) and the 107 gain tables counted but not written in full (cap of item 6). Every
   one of the 321 was recomputed by direct contraction with its actual assignment. All 1,746 gains of arm 2 and the
   other 164 of arm 1 were enumerated and agree.
