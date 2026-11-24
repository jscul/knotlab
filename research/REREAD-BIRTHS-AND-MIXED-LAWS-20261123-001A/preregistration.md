# A growth law in which a short knot pays with a shared distinction: pre-registration

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A` of epic `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` (direction 1 of `THIRD-HOLDER-20261123-001`; G18), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test is unchanged.

## The question

Under ordinary growth a knot that owes more loose distinctions than it holds stalls the whole round, and no distinction ever gets a third holder. The third-holder study found that a birth taking a distinction already held twice is the one move a hidden excess needs. State that move as a growth law in its least form, a short knot pays the rest with shared distinctions, and class it: do old words still extend, do the recorded sources change, what do the starts that used to stall do, how many holders arise, what becomes of the tables that came from stalling, and does a change still spread at a bounded pace?

## In standard terms

A variant of a synchronous graph-rewriting rule in which a resource shortfall is met by re-using an edge end, so that hyperedge degree is no longer bounded by two; tested for preservation of solutions (every solution of the old constraint system extends), for the removal of a global veto, and for a finite speed of propagation of a local change.

## Prior work in the program

`python3 -B scripts/track.py objects "growth law in which a short knot pays with a shared distinction and the round does not stall" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`python3 -B scripts/track.py objects "growth rule variant removing the global stall third holder degree three" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`python3 -B scripts/track.py objects "starts that stall at once under ordinary growth" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`REVIEW-LEADS-20261123-001` — a relative: its audit showed that no ordinary event gives a knot a distinction or repairs a shortage, its ticket A read the operator test on the same sparse draws, and its both-laws ticket imposed two laws on every knot, which is not the mixing studied here.
`FORBIDDING-JOIN-20261120-001` — a relative: rival fresh-count laws; they never pay with a shared distinction.
`TOUCH-CENSUS-20261118-001` — same population in part (small arrangements grown by the cheapest parity growth); it measured dimension.
`WHOLE-STAGE-SETTINGS-20261120-001` — same object for test (d): the smallest two-sided stall and the smallest parity closing, with edits as settings and weights fixed on the start.
`THIRD-HOLDER-20261123-001` — the source of both studies: the move (a birth that takes a distinction already held twice) and the structures with a hidden excess whose reachability is asked here.
`TICK-BIRTHS-AND-SCARCITY-20261121-001` — a relative: shortage under one-birth-at-a-time rules, where an unpaid proposal is dropped; here it is paid with a shared distinction.
`JOINT-PARENTS-AND-ERASURE-20261120-001` — unrelated object.

Seen before this freeze: nothing under this rule or this census. The results of the third-holder study are known.

## Prior work outside the program

None found for this law.

## Settled by construction (stated, not tested)

On a round in which no knot is short, the rule is ordinary growth. A birth with a fresh distinction extends every old word under either law. Under parity a birth with no fresh distinction extends every old word only if the parity of what it takes is implied by the old knots; with a distinction held three times the sum of all knots no longer leaves the loose distinctions alone, so the ordinary shortcut (a sole birth that takes every loose distinction is implied) is no longer valid and is replaced below by the implication itself.

## What is supplied

The rule; the choice of which shared distinction a short knot pays (two conventions and, on small cases, every choice); the replaced closing test; the samples and seeds; the readings of test (d); the measure of pace. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Rule R.** Groups, demand and fresh counts as in ordinary growth (the recorded operator on the present end). A live knot that owes more distinctions than it has loose ones pays the rest with distinctions it shares, each of which gains a holder. A payment is never a distinction that another parent of the same birth holds or pays. The round stalls only if some knot still cannot pay (a residual stall).
- **Which shared distinction.** Convention O: the knot's oldest shared distinction that is allowed; convention N: its newest. On starts of at most 8 knots every allowed choice is enumerated for the first two rounds.
- **Closing under R.** A parity birth receives no fresh distinction only when the parity of what it takes is implied by the old knots, tested by elimination. Otherwise it receives max(D, 3 − p, 1). Not-all-equal births always receive a fresh distinction.
- **(a) Extension.** On every history of at most 22 distinctions per stage, every allowed word of a stage extends to the next, under each law, by enumeration.
- **(b) Recorded sources.** The seven recorded sources of the review-leads epic's ticket A, to its horizons, under R and under ordinary growth.
- **(c) Starts that stall.** The 1,024 sparse draws per law of that ticket (seed 2026112301), 744 of which stall at once under ordinary growth: under R with each convention, 12 rounds or 5,000 knots: residual stalls, growth kind, the largest number of holders of a distinction, the first failing step of the operator test, and whether the two conventions give the same numbers of births per round.
- **(d) The stalling set-ups.** The smallest two-sided stall and the smallest parity closing of the whole-stage-settings study, with its edits as settings, its readings and its weights on the start, under ordinary growth and under R. For each rule and each side: whether the side's outcome depends on its own edit and whether it depends on the far edit. A four-correlation value is reported only where the own-edit dependence is present.
- **(e) Pace.** For 200 funded draws (the first 200 of test (c) that take at least one round under ordinary growth), one loose distinction is added at one knot drawn by seed 2026112330. Distance is the number of shared-distinction steps between knots of the start; a later knot has the least distance of its founder ancestors. Births are matched between the two histories as in the influence-cone study. For each round t, the largest distance of a changed birth.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Checks of the code: with no knot short, R reproduces ordinary growth on the seven recorded sources and on the 280 funded draws per law; the elimination test agrees with the ordinary shortcut on every closing met under ordinary growth. | any fails |
| P1 | Every old word extends at every birth under R with the replaced closing test, both laws. | one word fails to extend |
| P2 | Some of the 744 starts still stall at once under R (a knot can owe more than it holds in all), and fewer than half do. | none stalls, or half or more do |
| P3 | Some distinction reaches four or more holders within the horizon, and the two conventions differ in births per round on some start. | neither happens |
| P4 | Under R neither stalling set-up gives a side whose outcome depends on the far edit; under ordinary growth both do. | a far-edit dependence under R, or none under ordinary growth |
| P5 | On histories with no residual stall the largest distance of a changed birth at round t is at most 3t + 3 under R; under ordinary growth some draw has a changed birth at round 1 beyond distance 6, through a stall. | the bound fails under R, or no such draw exists |

## Runs and stop rule

One script per test. The study stops when the five tests are done. It reports, beside the predictions, how many rounds and births under R involve a payment with a shared distinction. Every run stays under ten minutes and under 12 GB; work is split into runs and nothing is stopped by the clock. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed both designs cold before this freeze (`research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/advisor/question.md`, `answer.json`). Its strongest objections here: test (d) is not the same experiment once the stall is gone, so 'at most 2' could hold only because nothing depends on the edits; extension fails at a parity closing when a distinction has three holders; 'no start stalls' is not forced; and a pace bound of t + 1 is too tight because adjacency already spans two steps and demand looks one round ahead. Changes: test (d) records own-edit and far-edit dependence under both rules, the closing test is replaced by the implication itself, residual stalls are counted and predicted, and the pace bound is loosened with distance fixed on the start.
