# Sources that share one supply: pre-registration

Ticket `REVIEW-LEADS-20261123-001D` of epic `REVIEW-LEADS-20261123-001` (takes B313; G15, with G5 and G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Sonnet sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged.

## The question

Under one-birth-at-a-time growth a recorded clock can lose its tick for good when another birth spends the last distinction a tick needs. When two recorded sources draw on one donor knot, what decides which keeps ticking: the order of births, which source asks first, or the cost of a tick?

## In standard terms

Two periodic processes drawing on one non-renewable resource under an asynchronous (serial) update rule; which survives as a function of the update order and of the time of first demand.

## Prior work in the program

`python3 -B scripts/track.py objects "two sources sharing one donor which keeps ticking under one-birth-at-a-time growth" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "competition for a shared resource between periodic sources serial update" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "seven-knot source nine-knot source 21-knot clocks with attached consumer" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`SHARED-DONOR-AND-SIGN-RESPONSE-20261121-001` — a relative: two births paid by one donor under ordinary growth; counts unchanged.
`TICK-BIRTHS-AND-SCARCITY-20261121-001` — same object for one clock and an inert consumer under the two serial rules; this study replaces the consumer by a second source.
`LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001` — same object for one clock: an outside birth spends its last distinction; this study asks which of two sources loses.
`UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001` — unrelated object.
`SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001` — unrelated object.
`FRESH-DEMAND-20261120-001` — a relative: serial orders that change the outcome on seven-knot starts.
`FREEDOM-CLOCKS-AND-BIRTHS-20261120-001` — same population in part (the two clocks of the 21-knot structure).
`SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001` — same population in part (clocks with a third lasting structure) under ordinary growth.

Seen before this freeze, by the thread's own abstract checks of 2026-11-23 (`docs/prompts/missed_leads_checks/`, private): nothing.

## Prior work outside the program

None found for this growth law. In general a non-renewable shared resource goes to the first claimant under a serial schedule.

## Settled by construction (stated, not tested)

A knot's holdings never gain a distinction, so a donor is a finite supply. Under ordinary growth a stage in which some proposal cannot be paid stalls as a whole.

## What is supplied

The joint starts and their attachments; the two one-birth-at-a-time rules as the scarcity study implemented them; the marked tick of each source; the horizon. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Sources.** The seven-knot source, the nine-knot drawn source, the two clocks of the 21-knot structure, and the clock of the scarcity study, each with its recorded marked tick.
- **Joint start.** One donor knot of source X that pays into X's tick is made the same knot as one donor of source Y. It holds the loose distinctions both recorded histories take from it, less a shortfall s in {0, 1}. Both attachments of the scarcity study (on the tick's parents; on the other continuation) are used where they apply. Each joint start is written out and checked lawful before any growth is run, in a construction addendum that records the donor's loose count, each source's demand on it, and the step at which each first asks.
- **Rules.** Finish each funded parent step before recomputing proposals; recompute proposals after every birth. Both exactly as in the scarcity study's code. Ordinary growth is the control.
- **Branches.** Depth-first over every choice at a contested birth (two proposals needing the same last loose distinction), to 400 births or 12 completed parent steps, at most 20,000 branches per joint start, sampled by seed 2026112304 beyond that.
- **Lost for good.** A tick is lost for good when a parent it requires holds no loose distinction; the certificate is that parent and the birth that spent its last one.
- **Pairs.** At least one pair whose first demands on the donor fall in the same step and one staggered pair, chosen from the addendum before any growth.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: each source alone reproduces its recorded ticks under all three rules; with shortfall 0 under ordinary growth each source in a joint start ticks as it does alone. | any fails: report the first missing construction and stop |
| P1 | With shortfall 0 no source loses a tick in any branch under either rule. | a loss occurs |
| P2 | With shortfall 1 and staggered first demands, the source that asks first keeps ticking in every branch. | a branch in which the later asker keeps ticking and the earlier loses |
| P3 | With shortfall 1 and first demands in the same step, both outcomes occur among the branches. | every branch ends the same source |

## Runs and stop rule

One script writes the addendum; one grows the joint starts. The study stops after the chosen pairs, or at the first gate failure with the missing construction named. It reports, per joint start and rule, the donor's count, the demands, the first-ask steps, and the branches by outcome with certificates. Every run stays under ten minutes and under 12 GB; a longer run is not started, the partial result is reported instead. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the six designs cold before this freeze (`research/REVIEW-LEADS-20261123-001/advisor/`, question and answer kept). Its strongest objection here and the change made: A donor is a finite supply that cannot be refilled, so the outcome follows from its count, the two demands and who asks first, and 400 births cannot show a permanent loss without a certificate. Changes: those three numbers are recorded for every pair, branching is exhaustive at contested births only, permanence needs the exhausted-parent certificate, a same-step pair and a staggered pair are both required, and the predictions now say that the first asker wins.
