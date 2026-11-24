# A one-parent birth that also takes a distinction its parent shares: pre-registration

Ticket `ONE-PARENT-REREAD-20261123-001A` of epic `ONE-PARENT-REREAD-20261123-001` (direction 1 of `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`; G18 with G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test is unchanged.

## The question

The re-read epic found that growth supplies weight and no tie, and that a part with at most two holders per distinction that sits at exactly 2 gains a hidden excess from one not-all-equal birth on a loose distinction and a shared one of the same knot. Rule R of that epic re-reads only when a knot is short and never makes that birth. State the least law that makes it, a one-parent birth also takes a distinction its parent shares, and ask three things. With one law for every newborn, so that no law is handed to a birth, does a part gain a hidden excess? Does any part gain that one added knot could not lift? And what does the rule do to growth where one-parent births are common: how many holders arise, and does growth go on?

## In standard terms

A variant of a synchronous hypergraph-rewriting rule in which a new constraint with a single parent re-uses one variable of that parent, so that variable degree is not bounded; tested for the growth of variable degree and, on sub-networks of known examples, for projected relations on six designated variables that admit a CHSH value above 2 under exact no-signalling with a supplied post-selecting constraint, first with one constraint type for every new constraint and then with every assignment of types.

## Prior work in the program

`python3 -B scripts/track.py objects "growth law in which a one-parent birth also takes a distinction its parent shares" --until 2026-11-23 --exclude ONE-PARENT-REREAD-20261123-001`

`python3 -B scripts/track.py objects "growth rule variant in which a new constraint re-uses a variable of its parent, degree above two, recorded sources survive or change" --until 2026-11-23 --exclude ONE-PARENT-REREAD-20261123-001`

`python3 -B scripts/track.py objects "census of parts of structures with a hidden excess grown under a re-reading law" --until 2026-11-23 --exclude ONE-PARENT-REREAD-20261123-001`

`MEET-HIST-20261118-001` — unrelated object.
`COPIES-AND-MEETINGS-20261120-001` — a relative: one-knot launches under ordinary growth; it never re-reads.
`GENERATORS-20261120-001` — same population in part: the recorded sources.
`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` — the source of this study: rule R, the census of parts under ordinary growth and under rule R, and the census of one added knot, whose 27 liftable parts are read again here.
`TWO-BIT-ROWS-20261112-001` — unrelated object.
`OVERLAP-READ-20261111-001` — unrelated object.

Seen before this freeze, all by lookups in existing records and one exploratory check by the thread; no engine for the rule exists and nothing was run under it.
- Under ordinary growth the seven recorded sources make one-parent births at round 1 only (0, 1, 0, 0, 3, 6 and 8 of them, in six rounds), so the rule can change them only from there. Each of the 280 funded sparse draws makes one-parent births after round 1.
- In ticket C's census of one added knot, every one of the 27 liftable parts has four working sets made of the live knot's loose distinction and one of the same knot's shared distinctions (55/27 in four parts, 109/54 in 23).
- On ten of the 27 (`research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks/one_parent_reread_exploratory_v2.py`): when each of the part's two one-parent births takes one shared distinction of the parent and gets one fresh distinction, the part reaches 55/27 or 109/54, hidden, when exactly one birth is not-all-equal and the other even parity; with both parity it stays at 2; with both not-all-equal it stays at 2 in 34 of 40 cases and reaches 31/15 or 61/30 in six, in three parts, all with the two births taking different distinctions.

## Prior work outside the program

None found for this law.

## Settled by construction (stated, not tested)

A birth with a fresh distinction forbids no old word, so the allowed observer words never change under rule Q. Round 1 of any start has the same groups under rule Q as under ordinary growth, so a start that stalls at once makes no birth under rule Q, and a structure with no one-parent birth in any round is unchanged. A parity birth with a fresh distinction gives every old word the same number of completions; a not-all-equal birth with f fresh distinctions counts an old word 2^f times when what it takes is not all equal and 2^f − 1 times when it is, so its pull fades as f grows. With every newborn parity no part gains. Under convention O a child's oldest shared distinction is the one its parent re-read, so along a chain of one-parent births one distinction gains a holder every round: a common hub, in the foundation's word.

## What is supplied

The rule; the choice of which shared distinction is taken; the samples and seeds; for the census, the parts, the observers, the setting births and the equal weighting of finished words. In the mixed arm, the law given to each newborn as well. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Rule Q.** Groups, demand and stalls as in ordinary growth, read from full holdings as in ticket A of the re-read epic. A one-parent birth takes its parent's loose distinction and, when the parent shares a distinction at the start of the round, one such distinction, which gains a holder; a parent that shares nothing gives an ordinary birth. A birth with i inputs gets max(D, 3 − i, 1) fresh distinctions, where D is the lookahead demand computed from the holdings the round will leave, the new meetings of re-reading births included. In test (b) under parity, a birth whose parity is implied by the old knots (by elimination) gets no fresh distinction instead.
- **Which shared distinction.** Convention O: the parent's oldest shared distinction; convention N: its newest. Under a convention two births of one parent take the same distinction. In the census every round-1 choice is also run, each birth choosing among its parent's shared distinctions independently.
- **(a) Recorded sources.** The seven recorded sources of the review-leads epic's ticket A under not-all-equal, ordinary growth and rule Q with each convention, to 12 rounds or 5,000 knots: the number of re-reading births per round, knots per stage, growth kind, and the largest number of holders of a distinction at each round.
- **(b) Sparse draws.** The 280 funded sparse draws per law of that ticket (seed 2026112301), ordinary growth and rule Q with each convention, 12 rounds or 5,000 knots: outcome, births per round, growth kind, re-reading births per round, the largest number of holders at each round, and the first failing step of the operator test.
- **(c) Census of parts.** The parts with at most two holders per distinction and no hidden excess, of the re-read epic's ticket C, that do not stall at once (5,761; the 6,312 that stall are counted and not grown). Each is grown under rule Q, every birth with a fresh distinction as in ticket C, for 3 rounds or until a stage passes 20 distinctions, under conventions O and N and under every round-1 choice when there are at most 64, otherwise under 62 more drawn by seed 2026112370. Weighting, records, hidden, score and hidden excess as in ticket C. A gain is a hidden excess at a later stage of a part that has none.
- **Uniform arm.** Every newborn is not-all-equal. No law is given to a birth.
- **Mixed arm.** Each newborn is even parity, odd parity or not-all-equal: every assignment when there are at most 4,096, otherwise 4,096 drawn by seed 2026112371 with one generator per history. Reported apart from the uniform arm, as a scaffolded reading.
- **Control.** For each gain at stage 1: the same births and laws with the shared input removed from every re-reading birth.
- **The 27 liftable parts.** The parts that one added knot lifts in ticket C.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Checks of the code. With re-reading switched off the engine equals the recorded driver on the seven sources and the 280 funded draws per law, and gives ticket B's stages and numbers of tables with a hidden excess on 500 drawn parts. Tables agree with word-by-word enumeration on 100 drawn grown stages. Every old word extends on every round of (b) with at most 22 distinctions. Allowed observer words never change. No knot born under rule Q is ever short. A stage-1 table with exactly one not-all-equal re-reading birth that has one fresh distinction, every other newborn parity, equals ticket C's table for the added knot on the same set. Every stage-1 gain is lost under the control. | any fails |
| P1 | Uniform arm: some part gains a hidden excess at round 1 for some choice of the re-read distinctions. | none does |
| P2 | Uniform arm: under either convention, where both births of a parent take the same distinction, no part gains at round 1. | one does |
| P3 | In either arm, every part that gains at any stage is hidden at exactly 2 at stage 0. | a part below 2, or not hidden, gains |
| P4 | Mixed arm: all 27 liftable parts gain at round 1 for some choice and assignment, and no other part gains at any stage. | a liftable part does not gain, or another part gains |
| P5 | In (b) under convention O some draw has a distinction with at least eight holders by round 12; under convention N no draw's largest number of holders grows after round 3. | no draw reaches eight under O, or the number grows after round 3 in some draw under N |
| P6 | In (b) every funded draw that is alive at 12 rounds under ordinary growth is alive at 12 rounds under rule Q, with either convention and law. | one is not |

## Runs and stop rule

One script per test and one for the checks. The study stops when the three tests are done. It reports, beside the predictions: for each source which rounds have re-reading births and whether its knots per stage change; for the draws the counts by outcome and growth kind under each rule, with the weighting named (the sparse draws of the review-leads epic); for the census the numbers of parts, histories and tables, how many choices were enumerated in full and how many drawn, the gains by arm, round, choice and number of fresh distinctions of the re-reading births, and the smallest gain of each arm in full, verified by word-by-word enumeration. Every run stays under ten minutes and under 12 GB; work is split into runs and nothing is stopped by the clock. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the design cold before this freeze (`research/ONE-PARENT-REREAD-20261123-001/advisor/question.md`, `answer.json`). Its strongest objections: the predictions that some part gains and that the liftable parts gain were lookups in the existing census of one added knot; the gain seen in exploration rested on giving two sibling births different laws, which is supplied, so the headline should be one law for every newborn; the rule did not say what a parent with no shared distinction does, whether siblings take the same distinction, or whether the lookahead sees the new meetings; a holder a round under the oldest-first convention is true by construction; the prediction about the bounded clock had no mechanism. Changes: the lookups were made and are listed above (the clock has no one-parent birth, so that prediction was dropped); the uniform arm is the headline and the mixed arm is reported as scaffolded; the rule's three gaps are closed; the chain of holders moved to what is settled and the prediction is now the contrast between the conventions; a control removes the shared input; gains are reported by the number of fresh distinctions.
