# Which recorded signals an ordinary process can send: pre-registration

Ticket `REVIEW-LEADS-20261123-001E` of epic `REVIEW-LEADS-20261123-001` (takes B312; G18, with G5), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Sonnet sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged.

## The question

The stalling studies produced their tables and their signals by edits to a start: one loose distinction added to one of two existing knots, keyed to a setting or to an old value, or withheld. Which of those acts can an ordinary continuation of one lawful start perform, and what is left open inside one ordinary history that could serve as a setting?

## In standard terms

Which interventions of a Bell-type protocol are operations of the dynamics and which are changes of the initial condition; and which degrees of freedom the dynamics leaves undetermined.

## Prior work in the program

`python3 -B scripts/track.py objects "which signalling routes an ordinary process can perform edits adding a loose distinction" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "signalling local operations value-independent growth" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "recorded growth histories holdings never gain a distinction" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`INFLUENCE-CONE-20261120-001` — a relative: what an edit to the start changes later; an edit is a different start.
`WHOLE-STAGE-SETTINGS-20261120-001` — same object: the edits and signals audited here.
`NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001` — a relative: distant edits under a rival permission rule.
`SOLE-PAYMENTS-AND-SUCCESSOR-COUNTS-20261122-001` — a relative: fresh values free under both laws at fixed payments.
`UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001` — a relative: the weighting under which an allocation can matter.
`LOCAL-EDIT-POLICIES-20261123-001` — same object: the value-keyed policy audited here.
`READ-ORIGIN-20261120-001` — unrelated object.

Seen before this freeze, by the thread's own abstract checks of 2026-11-23 (`docs/prompts/missed_leads_checks/`, private): nothing.

## Prior work outside the program

None specific. The distinction between a change of initial condition and an operation inside a history is standard.

## Settled by construction (stated, not tested)

By the definition of ordinary growth a birth adds a knot and fresh distinctions and gives an old loose distinction a second holder; nothing else changes. The stored-value study proved that groups, grants and allocations do not depend on values. The replays below test the engine and the recorder against these, with injected faults that must be caught.

## What is supplied

The list of recorded routes; the replayed histories; the injected faults; the old distinctions whose distribution is compared. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Routes.** Every way a recorded table or signal was produced in the two stalling studies: a fixed address; an address keyed to an old value; withholding the spare; repairing a visible shortage on a free message; revealing the hidden labels; biasing the weight of a hidden type; the smallest parity closing.
- **Histories.** The concealed-shortage preparation in its four types; the smallest two-sided stall; the seven-knot source to 12 parent steps; the five-founder clock to six returns; the three archived explosive starts to 2,000 knots.
- **R1, holdings.** In each history every knot's set of distinctions is the same at every later stage as at its birth. Injected fault: one loose distinction added to an existing knot at the third step; the check must flag it.
- **R2, values.** For 64 lawful valued versions of each start per law (seed 2026112305), the births, their parents and their numbers of fresh distinctions are identical. Injected fault: the join veto of the written-bit study; the check must flag a difference.
- **R3, allocations.** On the seven-knot source to six steps, the five-founder clock to three returns and the smallest stall, for every knot that holds two or more loose distinctions and owes fewer payments than it holds, or owes payments to different children, enumerate every allocation at the first two funded steps. Record whether the later births (parents and fresh counts, up to renaming) change, and whether the number of allowed words and the joint distribution of all old distinctions change, under uniform present words and under the old-word weighting, under each law.
- **R4, groups.** Whether the proposed parent groups are a function of the holdings alone, by reading the engine and by two replays.
- **R5, order.** One replay of the recorded case in which the order of births under the recompute-after-every-birth rule decides whether a tick is lost.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Both injected faults are flagged; the unfaulted histories pass. | a fault is missed or a clean history is flagged |
| P1 | R1 and R2 hold on every history. | one fails |
| P2 | No allocation changes the later births. | one does |
| P3 | Under parity no allocation changes the old distinctions' distribution under either weighting. Under not-all-equal some allocation changes it under uniform present words and none changes it under the old-word weighting. | any part fails |
| P4 | The proposed groups are a function of the holdings. | they are not |

## Runs and stop rule

One script per check. The study stops when the five checks are done and the table of routes is filled: for each route, the act, and whether ordinary growth, an allocation, a fresh value or a serial order can perform it. Every run stays under ten minutes and under 12 GB; a longer run is not started, the partial result is reported instead. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the six designs cold before this freeze (`research/REVIEW-LEADS-20261123-001/advisor/`, question and answer kept). Its strongest objection here and the change made: R1 and R2 are definitional or already proved, so replaying histories made by the same generator tests only the recorder, and the list of freedoms conflated 'changes which births happen' with 'can serve as a setting': the setting of design C is an allocation, which leaves births unchanged and changes the weighting. Changes: injected faults were added, allocations are enumerated and compared on allowed-word distributions as well as births, group formation was added to the list, and allocation among loose distinctions that are not interchangeable is listed as a possible setting.
