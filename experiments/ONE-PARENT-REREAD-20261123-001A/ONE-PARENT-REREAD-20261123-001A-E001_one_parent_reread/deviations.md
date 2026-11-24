# Deviations, readings and limits: ONE-PARENT-REREAD-20261123-001A-E001

Nothing in "Definitions (frozen)", "Predictions (frozen)" or "Runs and stop rule" of
`research/ONE-PARENT-REREAD-20261123-001A/preregistration.md` (sha256 36ecc92c...6e8c, as in `contract.json`) was
changed. Section A was written after the code and a few development runs (A0) and before the study's runs; it lists
every place where the note leaves a choice and the reading taken. Section B, added during and after the runs, lists
limits met and anything found after values were seen.

Recorded code is imported by path and never edited: ticket A's `rlaw.py` of the re-read epic (sha256 29aa3d91...d8f8,
asserted by `qlaw.py` at every import) and `words.py`; ticket C's `cstudy.py`, `arm1.py` and `gates.py`; through them
ticket B's `common.py` and `verify_excess.py`, the recorded `end_operator.py` and the review-leads `lib.py`; the
recorded scorer `docs/prompts/missed_leads_checks/finished_weighting_chsh.py` (loaded as ticket B does). Two methods of
`rlaw.Growth` are copied into `qlaw.QGrowth` and changed, each marked COPIED. Other tickets' outputs are read
compressed; nothing is written outside this experiment family, its artifact folder and the draft result.

## A0. Development runs made before this section

Each under `timeout 600 prlimit --as=12884901888`. (1) Rule Q (both conventions) and re-reading switched off on the
seven sources under not-all-equal, printed only: knots per stage, re-reading births per round, holders. (2) The
recorded driver against re-reading switched off on the seven sources under not-all-equal, printed only: equal on all
seven. (3) Rule Q on the 280 funded draws per law with exact fresh counts in every round: one history raised a
MemoryError at 12 GB (a round before a capped round received fresh counts in the thousands per birth); this is why A6
uses ticket A's next-round cap shortcut. (4) The same with the shortcut, printed only: outcomes and timing (seen:
under parity 78 (O) and 75 (N) of the 280 close; 7 (O) and 3 (N) histories per law end with the cap; the largest
number of holders in the slowest histories was 4 or 5). (5) The number of round-1 choices on every tenth census part
(most at most 8; one above 64). (6) `q_census.py` with tag `dev` on positions 1290 to 1300 and 0 to 50; its files were
inspected (one liftable part, start 2990, gains 55/27 at stage 1 in the mixed arm when one of its two re-reading births
is not-all-equal and the other parity, and 31/15 at stage 3; no uniform-arm gain in those 60 parts; every stage-1 gain
lost under the control) and deleted. No definition or reading below was changed after these runs, except that A6 was
chosen because of (3), and A7 was written after (4) showed capped histories; both readings of A7 are reported.

## A. Readings fixed before the study's runs

1. **The engine.** `qlaw.QGrowth`, a subclass of `rlaw.Growth` (full holdings; groups read from full holdings by
   rlaw's exact `Groups`, whose Python search is used: `rlaw.USE_C = False`, so nothing is built in ticket A's folder).
   `plan` is rlaw's under rule "ordinary" (a short knot stalls the round; there is no rule R) followed by rule Q's
   allocation; `_finish` is rlaw's with the fresh count's `3 - i` read with i the number of inputs. The parent is
   constructed with its rule "R" only so that it keeps the GF(2) span of the old knots for the parity elimination test.
   `reread=False` switches re-reading off.
2. **"Shares at the start of the round".** A parent shares a distinction when it holds it and the distinction has two or
   more holders when the round starts (its own loose distinctions handed out earlier in the same round do not count;
   ticket A, reading A2). **Oldest / newest** are the smallest / largest name (ticket A, A3). Names: in the sources and
   draws, meetings first, then each knot's loose distinctions (`lib.source_from`); in the census, ticket B's numbering
   (first appearance along the start's knots in the target's order); fresh distinctions take the next names in birth
   order. Under a convention every re-reading birth of one parent in one round takes the same distinction, the
   parent's oldest (O) or newest (N) shared one.
3. **Order and loose distinctions.** Births in rlaw's order (groups of three or more sorted, then pairs, then one-parent
   births); each parent hands out its loose distinctions in that order, the last listed first (rlaw, `lib.grow`). A
   one-parent birth whose parent shares a distinction takes that loose distinction and one shared distinction; its
   star is (loose, shared, fresh...). A one-parent birth whose parent shares nothing is an ordinary birth. A birth with
   two or more parents takes one loose distinction of each parent, as in ordinary growth; it never re-reads. A
   "re-reading birth" below is a birth that took a shared distinction; "sibling births" are the re-reading births of one
   parent in one round.
4. **Fresh counts and demand.** max(D, 3 - i, 1) with i the number of inputs (2 for a re-reading birth, so max(D, 1)).
   D is rlaw's lookahead demand from the round's input sets: every birth provisionally live with one opening, every
   knot holding a taken distinction at the start of the round witnesses the births that take it, and births taking a
   common distinction witness each other; so the old holders of a re-read distinction witness the birth that took it
   (the new meetings). Under parity (test (b)) a birth gets no fresh distinction exactly when the GF(2) vector of what it
   takes lies in the row span of every knot of the stage before the round (every knot even parity), rlaw's elimination
   test as under its rule R; several births of one round may be implied. Under not-all-equal (tests (a), (c)) no birth
   is implied. With re-reading switched off, parity uses the same elimination test.
5. **Stall.** Any short knot stalls the round and ends the history (outcome `stall`), recorded with whether each short
   knot was born under the rule. "No knot born under rule Q is ever short" is judged on every rule-Q history of (a),
   (b) and (c): after round 1 only newborns hold loose distinctions, so any stall after round 1 is a newborn being short;
   round 1 has the groups of ordinary growth, and every source, funded draw and census part makes its round 1. A round
   stopped by the cap is not tested for a shortage (the recorded rule caps first); such rounds are counted.
6. **Horizon and cap in (a) and (b).** `rlaw.Growth.run(12, 5000)`: a round that would take the structure above 5,000
   knots is not taken and the history ends with `cap` (the recorded rule). Rule Q runs with ticket A's next-round cap
   shortcut (`bound_next=True`, ticket A deviations B2): when the lookahead of a round has more groups than the room
   left under the cap, the next round is certain to be capped, the round is taken with fresh counts max(3 - i, 1) (0 if
   implied), flagged `fresh_lower_bound`, and the history ends with `cap`. The argument of ticket A holds under rule Q:
   when every birth of a round is live, the next round's witnessed sets read from full holdings are exactly the
   lookahead's (an old knot witnesses the births that took a distinction it holds; a newborn the other takers of its
   inputs; fresh distinctions are loose). Births per round, holders, outcome, growth kind and the operator test (fresh
   distinctions are pendant in the knot-distinction pattern) do not depend on those fresh counts. Reason: A0 (3).
   Re-reading switched off in row G runs with exact fresh counts in every round (`bound_next=False`), as the recorded
   driver computes its lookahead in full.
7. **"Alive at 12 rounds" (P6).** Primary reading: the history reaches its horizon, 12 rounds or 5,000 knots, without
   closing or stalling (outcome `horizon` or `cap`); the cap is the study's own limit. Strict reading beside it: outcome
   `horizon` only (12 rounds made, a live knot remains). Both are reported, for ordinary growth and for rule Q, and P6
   is judged under each. (Written after A0 (4); see A0.)
8. **P5.** H(t) is the largest number of holders of a distinction at stage t (stage 0 = the draw, stage t after round
   t). "Some draw has a distinction with at least eight holders by round 12": some funded draw, under either law, with
   H(t) >= 8 for some t <= 12 under convention O. "No draw's largest number of holders grows after round 3": for every
   funded draw under either law, under convention N, H(t) <= H(3) for every stage t > 3 that the history has (a history
   that ends before stage 4 cannot grow after round 3). Both laws pooled, as the note pools them; each law reported.
9. **Growth kind.** The recorded `lib.growth_kind` (any stall reads stalled; bounded when births per round never exceed
   the largest of the first four rounds; growing otherwise) and the kind from births per round alone (stalled only with
   no birth) are both reported. **Operator test**: `lib.first_failing_stage` on the stars and knots per stage
   (planarity of the knot-distinction pattern, in the literature's word); with three or more holders it is a reading of
   the pattern only, as in ticket A.
10. **Funded draws.** `lib.p3_draws()` (seed 2026112301); funded under a law when the recorded driver's history (12
    rounds, 5,000 knots) neither stalls at once nor lacks a birth (ticket A's gate): 280 per law (checked). Every knot of
    a draw has the run's law (parity: even at every knot).
11. **(a)** is run under not-all-equal only, as frozen. Row G's check with re-reading switched off is run on the seven
    sources and on the funded draws under both laws.
12. **Census population.** Ticket B's two-holder founder starts (`max_holders` at most 2) with no hidden excess at stage
    0 whose c3 record does not end in `stall`: 5,761 (4,826 grown to more than 20 distinctions, 348 grown for three
    rounds, and 587 with more than 20 distinctions at stage 0, in ticket B's record). The stop is checked before every
    round ("for 3 rounds or until a stage passes 20 distinctions", as tickets B and C), so the 587 make no round; they are
    counted and have no grown stage. The 6,312 two-holder starts with no hidden excess that stall are counted; row G
    (part `stalled`) confirms that each stalls at round 1 under rule Q too.
13. **Census growth.** `qcen.grow_census`: rule Q with the not-all-equal structure rule (every birth at least one fresh
    distinction, no closing, as ticket C), exact fresh counts, no knot cap, stop as A12 (the stage that passes 20
    distinctions is kept and tested). Founders keep the target's laws and signs.
14. **Round-1 choices.** Round 1 has the groups of ordinary growth, so its births and parents do not depend on the
    choice. Its re-reading births are its one-parent births whose parent shares a distinction; each chooses among its
    parent's shared distinctions independently; a full choice is one element of the product, and "at most 64" counts
    these. At most 64: every choice. More: 62 more drawn, distinct, none equal to the choice of O or of N, each birth's
    option uniform and independent, by `numpy.random.default_rng([2026112370, target, start bitmask])`, one generator
    per part (ticket C's rule, this study's seed). Histories: convention O and convention N (every round by the
    convention), and one choice history per choice (round 1 by the choice, later rounds by convention O, as the brief
    says). So with at most 64 choices O's round-1 choice is grown twice (identical histories) and N's round-1 choice
    also as a choice history with later rounds by O; histories are counted by kind and as distinct structures per part.
    A part with no re-reading birth at round 1 has one (empty) choice.
15. **Mixed arm.** Every assignment of even parity, odd parity or not-all-equal to the n newborns of a history when 3^n
    is at most 4,096; otherwise 4,096 distinct assignments drawn by `numpy.random.default_rng([2026112371, target,
    start bitmask, kind, position])` (kind 0 = convention O, 1 = N, 2 = choice; position = the choice's index), one
    generator per history. Column j is the j-th newborn in birth order; the assignment of a stage is the prefix of its
    newborns; a stage's tables are its distinct prefixes (tickets B and C). **Uniform arm**: the one assignment with every
    newborn not-all-equal. Both arms use the same histories.
16. **Weighting, records, hidden, score, hidden excess, gain.** Ticket B's evaluator (`cstudy.Eval`): the table of
    allowed words on the target's six observer distinctions with every other distinction forgotten; the supplied
    setting births; every allowed word of the finished structure counted equally; hidden on both sides decided in exact
    integers; score screened in floating point and exact (fractions) for every hidden table within 1e-6 of 2 or above;
    a hidden excess is an exact score above 2. A gain is a hidden excess at a grown stage (t >= 1); every census part has
    none at stage 0 (asserted).
17. **Reduction for speed** (ticket C deviations A9, re-read for rule Q). At stage t a newborn of round t holds fresh
    distinctions that no other knot holds, so its factor summed over them is a positive constant unless it is
    not-all-equal with two or more INPUTS (a re-reading one-parent birth has two). So each table equals, up to a positive
    constant, the table of its effective assignment: round-t newborns not-all-equal with two or more inputs kept, every
    other round-t newborn even parity, earlier newborns as assigned. Ticket C's `arm1.effective_rows` is called with this
    set of kept columns. Every gain is recomputed by direct contraction with its actual assignment (asserted equal).
    Re-verified in row G: part `reduction` (direct against reduced on every prefix row of every stage of every history
    of the 27 liftable parts and 200 drawn parts) and part `stages`.
18. **Control.** For every gain at stage 1 (either arm): the stage-1 knots with the shared input removed from every
    re-reading birth of round 1, fresh distinctions and every law kept; the gain is lost when that table has no hidden
    excess. The note defines the control for stage 1 only; later gains have none.
19. **Classes of a gain.** By round: its stage t. By choice: the sibling class of each round up to t (`same`: every
    parent with two or more re-reading births in the round gave them one distinction; `different`: some parent's
    siblings took different ones; `single`: no parent has two re-reading births). By laws: the laws of the re-reading
    births among the stage's newborns. By fresh counts: their numbers of fresh distinctions.
20. **P2** is judged on the convention histories (O and N), where sibling births take one distinction. Choice
    histories in which every round-1 sibling class is `same` are reported beside it, not judged.
21. **P3**: "hidden at exactly 2 at stage 0" = the part's stage-0 table is hidden and its exact score is 2.
22. **P4**: the 27 liftable parts are ticket C's arm-2 lines with a non-empty `gains`. "Gains at round 1 for some choice
    and assignment" = some mixed-arm table at stage 1 of some history of the part is a hidden excess. "No other part gains
    at any stage" is judged on the mixed arm; uniform-arm gains are reported for P1 and P2.
23. **Smallest gain of each arm**: fewest knots at the gaining stage, then fewest distinctions, then the smallest exact
    score, then part order (ticket C's reading A14). It is written in full and verified by enumerating every word of its
    four finished structures (`cstudy.full_check`, ticket B's `verify_excess.brute_joint_all`); so is every gain written
    in full whose stage has at most 26 distinctions. Gains are written in full for at most 50 tables per stage, history
    and arm (all counted, each with its class).
24. **Row G seeds chosen here** (not fixed by the note): 500 parts 2026112372; 100 grown stages 2026112373; reduction
    sample 2026112374; scorer sample 2026112375; other-newborn law combinations in the added-knot check 2026112376.
25. **Row G, the checks the note names, as read.**
    - "Equals the recorded driver": stars, knots per stage and outcome equal to `lib.grow` (12 rounds, 5,000 knots), on
      the seven sources and on the 280 funded draws, under each law.
    - "Ticket B's stages and numbers of tables with a hidden excess on 500 drawn parts": parts drawn from the 5,761;
      compared: stars (ticket B's `grow`), knots and distinctions per stage and outcome (its record), and per stage the
      numbers of tables, hidden tables and tables with a hidden excess under its three-law assignments (its seed), by
      direct contraction.
    - "100 drawn grown stages": stages t >= 1 of the rule-Q census histories with at most 24 distinctions, one drawn
      mixed-arm assignment each, direct contraction against ticket B's `brute_table`.
    - "Every round of (b) with at most 22 distinctions": every round t to t+1 of every rule-Q history of (b) whose stage
      t has at most 22 distinctions (ticket A's `words.Stage.extends`, exact because the births of a round have disjoint
      fresh distinctions); rounds with lower-bound fresh counts are not covered. Also run on (a) and reported.
    - "Allowed observer words never change": every grown stage of every census history, both arms, every assignment,
      against the same assignment's prefix one stage before (stage 0: the part's table).
    - "A stage-1 table with exactly one not-all-equal re-reading birth that has one fresh distinction, every other
      newborn parity": every history of every growing census part, every round-1 re-reading birth with one fresh
      distinction, the other round-1 newborns even or odd (every combination when at most 64, else 64 drawn); after
      division by the gcd, compared with ticket C's table 2M - M_T for T = the birth's two inputs (ticket C's
      `gates.table_with_T`), and with the table ticket C stored where it stored one. By direct contraction.
    - "Every stage-1 gain is lost under the control": every stage-1 gain of either arm (A18).
    - Beside the frozen checks: the evaluator against the recorded scorer `evaluate(M)` on every gain table written in
      full, every control table and 1,000 drawn census tables.
26. **Processes.** Every run under `timeout 600 prlimit --as=12884901888` from the repository root with
    `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`, at most six at once. Line files are gzip-compressed
    where large.

## B. Limits and findings during the runs

1. **Runs.** Two queues (`jobs_1.txt`, 34 runs; `jobs_2.txt`, 8 runs) through `run_jobs.sh`, at most six at once, each
   under the wrapper of A26; every run ended with status 0 and none came near the limit (slowest: re-reading switched
   off on the sources under parity, 145 s; census chunk 0 to 1,000, 134 s). Nothing was stopped and nothing rerun. Logs:
   `artifacts/.../logs/jobs_*_runs.log` and one log per run. `q_report.py` was run six times (`logs/report_*.log`):
   the second run added cross tables (gains by stage, siblings, laws and score; per part; the reverse direction of P6;
   outcome pairs), the third the numbers of item 6, the fourth the count of gains that first appear at a later stage,
   the fifth and sixth the checks of item 7; no number of an earlier run changed.
2. **(a): stars differ where only the last round's fresh counts do.** For `knots21_two_clocks` (no re-reading birth in
   any round) rule Q's stars differ from ordinary growth's only because the round before the cap was taken with
   lower-bound fresh counts (A6); its knots per stage, births and holders are those of ordinary growth. The same flag
   is on the last round of every capped rule-Q history of (a) and (b) (4 of 7 sources per convention; 7 (O) and 3 (N)
   draws per law); nothing reported depends on those fresh counts.
3. **(c): 587 parts make no round** (A12); their O and N histories are among the 30,868 histories (1,174 histories with
   stage 0 only). The 6,312 stalled parts stall at round 1 under rule Q with the recorded operator's shortages, under
   both conventions (row G, part `stalled`).
4. **(c): later rounds.** Re-reading births occur in rounds 2 and 3 too (4,747 and 7,524), each with one fresh
   distinction; no history stalled; so A5's reading was never needed in (c).
5. **P6 reading.** Under the primary reading (A7) 13 histories fail (parity: 8 under O, 5 under N; all closings), under
   the strict one 33 (those 13 and 20 capped histories). P6 fails under both; nothing depends on the choice.
6. **Read after the results, by commands that wrote nothing, then added to `q_report.py` (`summary.json`, key
   `extra`):** the known values on the ten parts of the exploration (uniform arm, both births not-all-equal, exactly 2 in
   34 of 40 choices and 31/15 or 61/30 in 6; both parity exactly 2 in all 160 tables); where the 24 parts hidden at
   exactly 2 that are not liftable stay (exactly 2 at every grown stage); the largest hidden score of the 5,710 other
   parts (1.692 in floating point, mixed arm); holder growth in (b) after round 1; the operator test's first failing
   step ordinary against rule Q; one closing case of P6 (arm 3, draw 17).
7. **Read after the results while checking the draft, then added to `q_report.py` (`extra`):** every control table is
   hidden at exactly 2; the 24 non-liftable parts at exactly 2 have every assignment enumerated and all 288 uniform-arm
   tables hidden at exactly 2; how the bounded draws of (b) end (births in round 12); the contracted-table total; and,
   for the 1,296 mixed-arm gains that first appear at stage 3, one part (3072, convention O) whose stage-3 table under
   five law combinations was compared with its stage-1 tables; which distinction each re-reading birth of the two
   archive starts of (a) took in each round; how the 48 parity draws with no re-reading birth end. First-draft
   sentences corrected before hand-off: the 27 liftable parts have 4 newborns and 81 assignments (not 5 and 243); the
   largest holders under O at the last stage run from 8 to 14 (not 9 to 14); archive_start-00 under N ends with 8 births
   a round, not one; the 48 parity draws without a re-reading birth close at round 1 (40) or 2 (8), not all at round 2.
8. **The engine's hash** was checked at every import of `qlaw.py` and by every row-G and report output
   (`rlaw_sha256`): unchanged.
9. **Not done.** Full enumeration of every choice and assignment: 1,377 growing parts rest partly on 4,096 drawn law
   assignments in some histories and 10 on 62 drawn round-1 choices (more than 64 choices, at most 128); the mixed arm's
   "no other part gains" is partly a sample there. The uniform arm has no drawn assignment; its only draws are the
   choices of those 10 parts. The control is defined for stage-1 gains only and was not computed for later gains.
