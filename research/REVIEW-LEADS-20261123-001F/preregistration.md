# A rule that is both parity and not-all-equal: pre-registration

Ticket `REVIEW-LEADS-20261123-001F` of epic `REVIEW-LEADS-20261123-001` (takes B314; G18, with G5), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Sonnet sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged.

## The question

Either law alone allows every signal fraction at a returning receiver. The signal-fraction study's control imposed both laws at once from the quiet start and found the continuation forced. What does growth do when every knot's word must satisfy both: which valued starts continue, is the continuation unique, and what fraction of returns signal?

## In standard terms

A counting constraint: every constraint of arity three or four holds exactly two ones (two-in-three and two-in-four), and at higher arity an even number of ones that is neither none nor all. It is the conjunction of a parity and a not-all-equal constraint on the same variables and is not itself a knot.

## Prior work in the program

`python3 -B scripts/track.py objects "knots satisfying both parity and not-all-equal forced fresh values signal fraction" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "exactly two ones balanced constraint two-in-four deterministic continuation" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "five-founder clock valued starts returning receiver" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001` — same population and the source of this study: its control imposed both laws from the quiet start only.
`SOLE-PAYMENTS-AND-SUCCESSOR-COUNTS-20261122-001` — a relative: forced single writes under one law at a time.
`ONE-SIDED-PATH-SKETCH-20261115-001` — unrelated object.
`IDLE-PHASE-AND-TREE-CLOSURE-20261121-001` — unrelated object.
`FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001` — unrelated object.
`TICK-BIRTHS-AND-SCARCITY-20261121-001` — same population in part (the five-founder clock).
`CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001` — same population in part (return clocks).

Seen before this freeze, by the thread's own abstract checks of 2026-11-23 (`docs/prompts/missed_leads_checks/`, private): nothing beyond the recorded quiet-start control.

## Prior work outside the program

Exactly-k constraints are standard. Not found: this constraint on a growing read-twice structure.

## Settled by construction (stated, not tested)

The rule fails K2: forgetting one distinction of a three-place word leaves 01, 10 and 11 only, and of a four-place word excludes 000 and 111. So it is two knots on the same distinctions, and the study is about a counting constraint. With two inputs and one fresh distinction the fresh value is forced or impossible; with two inputs and two fresh, inputs 00 force 11 and inputs 11 force 00. The quiet start of the five-founder clock continues quiet (recorded).

## What is supplied

The rule; the reading that an old word with no lawful completion is removed; the sources, the enrolled receiver and the signal of the signal-fraction study; the horizon. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Rule.** Every knot's word has even parity and is not all equal. The structure grows by ordinary growth, unchanged.
- **Arms.** The rule; parity alone; not-all-equal alone; all on the same structures.
- **Structures.** The five-founder clock with the enrolled receiver of the signal-fraction study, to six returns. The seven-knot source to 8 parent steps or 300 knots. The nine-knot drawn source to 6 parent steps or 300 knots. The arities met are recorded.
- **Valued starts.** Every founder word lawful under the arm's rule if there are at most 4,096; otherwise 1,024 drawn by seed 2026112306.
- **Removal.** An old word with no lawful fresh completion at some birth is removed. Survivors are counted at every step.
- **Whole histories.** Two valued continuations of a start are the same history when a renaming of fresh distinctions that preserves every later holding carries one to the other. Histories are enumerated over every lawful completion and every allocation of loose distinctions to children.
- **Signal.** At a return of the enrolled receiver the newborn's two incoming values differ. The signal fraction of a history is the share of its six returns that signal.
- **Carried count.** The number of ones among the loose distinctions at each stage.
- **Null.** The fraction forced by counting alone, derived by hand for the five-founder clock and recorded before the run.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: the canonical checker reports that the rule fails K2 at three and four places; parity alone and not-all-equal alone reproduce the recorded range of fractions from 0 to 1 on the five-founder clock; the quiet start stays quiet under the rule. | any fails |
| P1 | Some lawful valued starts have no survivor within the horizon on each structure. | every start survives on some structure |
| P2 | Every surviving start of the five-founder clock has one signal fraction over all its histories. | a start with two fractions |
| P3 | Across surviving starts of the five-founder clock the signal fraction takes at most two values. | three or more values |

## Runs and stop rule

One script per structure. The study stops after the three structures and reports, per arm, survivors by step, histories per surviving start, the distribution of signal fractions with the counting null beside it, and the carried count by stage. Every run stays under ten minutes and under 12 GB; a longer run is not started, the partial result is reported instead. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the six designs cold before this freeze (`research/REVIEW-LEADS-20261123-001/advisor/`, question and answer kept). Its strongest objection here and the change made: The rule fails K2, so results are about a counting constraint, and fractions may be forced by counting alone; 'one signal fraction per start' is trivial when the continuation is unique; two completions stop being renamings once the fresh distinctions are paid to different children. Changes: the study is labelled as a counting constraint, parity-only and not-all-equal-only arms and a hand-derived counting null were added, the fraction is compared across surviving starts, and uniqueness is judged over whole histories.
