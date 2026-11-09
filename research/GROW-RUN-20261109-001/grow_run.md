# Growth while running

Epic `GROW-RUN-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `GROWN-DISTANCE-20261109-001` read the band law's torus stage by stage (A42) and selected, as its direction 1,
  backlog B24: let the band law act while the network runs. The coordinator gave the go-ahead on 2026-11-09, with the instruction to fall
  back to B23, growth chosen by the dynamics, if a running insertion breaks persistence quickly.
- **The question.** Insert a band into a running tube, its cells new open distinctions from that lag, and read the whole history as one
  space-time law. Does every contact keep binding both of its rings at every lag, for which insertion lags, and how does the damage
  spread?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **What the insertion has not reached is intact.** A ring whose first row has not yet flowed through the contacts the band cuts keeps its footprint as in the next stage, so every contact keeps binding it at every lag; every ring farther than the insertion lag from the cut, in time length, is such a ring. | proved; 0 of 6,240 such bindings fail | A |
| 2 | **The band is always bound.** Every contact binds the new band's rings at every lag, and an insertion at lag 0 is the next stage. | proved; 0 of 5,120 fail | A |
| 3 | **What it has reached mostly breaks.** Of 26,016 bindings of reached rings, 17,612 fail (68%). Over every insertion lag of 13 tubes, only lag 0 keeps every contact persistent in every case; overall 42 of 634 lags do for the lower and upper splits, 58 for copy and 64 for fresh. | computed, exact over every insertion lag | A, stress test |
| 4 | **The damage spreads at the speed of influence.** On the 3 × 8 tube the contacts that lose a binding fill the rows out from the band one row every 4 lags each way, the time length of a row at g = 2. | computed | A, stress test |
| 5 | **Only the young are bound.** With a band every 4, 8 or 16 lags on the 3 × 3 tube, after the fourth band only the newest band's rings keep every binding; the older rings keep 0 to 6 of their 12 to 36. | computed | A, stress test |

## Answer

Growth while running breaks persistence quickly, and causally. A band inserted at lag t0 leaves untouched every ring whose influence
has not reached the place it cuts, and binds its own rings at every lag, but most bindings of the rings it has reached fail. Only an
insertion at the very start, or at rare special lags, keeps every contact persistent. So the band law's "every stage balanced" is a
property of growth between runs, the stage reading of A42, and not of a law that grows in time. Per the coordinator's instruction the
line falls back to B23, growth chosen by the dynamics, which this result sharpens: grow only where influence has not yet arrived.

## Reading

**Interpretation, not a theorem.**
- **Growth has a past light cone.** An insertion rewires the cells the band cuts. Every ring whose first row has already flowed through
  them carries into the new network a mixture that the new returns no longer cancel, and its contacts' knots across time lapse at some
  later lag. Rings whose influence has not arrived are untouched. The persistent knots that survive a growth event are those outside its
  past, read in time length.
- **The newest band is the bound one.** Under continual growth each band is bound until the next one reaches it. A law that grows in time
  keeps its knots across time young.
- **The stage reading is load-bearing.** A42 is confirmed for stated reasons: it is the reading under which band growth keeps every
  contact persistent, and the whole-history reading of a law that grows in time does not.
- **Where growth could keep everything.** Only where nothing has arrived: at lag 0, or ahead of the light cone. On a closed tube every
  cut is reached by about the time of flight across it, so a growth rule that keeps persistence would have to stay ahead of influence.

## Lag cutoffs and census-only claims

- **No lag cutoff.** After the last insertion the network is fixed, so a contact's row is eventually periodic and every lag is read
  through one period; which insertion lags are clean is read through one period of the run's state, which fixes every lag.
- **Census-only.** Conclusions 3 to 5: which reached bindings survive, and the clean lags beyond 0, are listed, not explained.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Theorems 1 and 2 (1, 2) | 5 × 6 at g = 2 and 4 × 5 at g = 3, insertion lags 0 to 39, four splits (checked on 3 × 8, 4 × 6, 3 × 5) | pass: 0 of 10,200 bindings of rings not reached or of the band's rings fail; 20,752 of 27,560 reached bindings fail (75%) |
| Every insertion lag (3) | 4 × 5 and 5 × 4 at g = 2, 3 × 3 at g = 5 (13 tubes to 6 × 3) | pass: lag 0 clean in every case; lower split clean at lags 0 and 1 only on 4 × 5 and 5 × 4 (of 124), at 16 of 338 lags on 3 × 3 at g = 5 |
| The spread (4) | 3 × 10 at g = 2 and 3 × 8 at g = 3 (checked on 3 × 8 at g = 2) | pass: one row every 4 lags at g = 2 and every 6 lags at g = 3 each way, the time length of a row |
| Only the young are bound (5) | six bands at P = 6 and 10 (four at P = 4, 8, 16) | pass: only the newest band keeps every binding; every older ring keeps none |

The script is `stress_test.py` beside this note, its output `stress_test.json` and its log `stress_test_log.txt` (GROW-RUN-S1 in
`docs/LONG_RUNNING.md`, 44 minutes, folded in on 2026-11-09).

## Literature and provenance

- **Sources.** Additive cellular automata over GF(2) and their light cones (Martin, Odlyzko and Wolfram 1984); dynamics on time-varying
  graphs and reachability along time-respecting paths (temporal graphs).
- **Classification.** Known-with-delta. Linearity and causality are classical; the delta is the fate of the program's persistent knots
  across time under growth: intact outside the growth event's reach, mostly lapsed inside it.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), and the stage results of `GROW-NET-20261108-001`.
- **Challenged.** A42, a grown network is read stage by stage: confirmed for stated reasons.
- **Added.** A44, a band born while the network runs brings new open distinctions.
- **Scope.** Square tubes of rule-60 rings with law (12, 12) contacts, the band law, four splits of the cut contact.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with seven checks, including an exact census of every insertion lag and an independent reading by
  actual bits; one stress test.
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — growth while running | **Status:** Successful | The answer is exact: intact outside the insertion's reach (proved), mostly broken inside it (computed over every insertion lag) |
| Local direction — a law that grows in time | Full pivot | Growth while running breaks persistence quickly; the coordinator's fallback is B23 |
| Broader exploration — G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23), now with a candidate rule; handles from two bands (B22) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | A law that grows a network of persistent contacts must grow between runs, or only where its influence has not arrived |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), B24 marked taken. **Assumptions:** A42 confirmed for
stated reasons; A44 added.

- **What the attempt leaves open.** Which reached bindings survive and why; whether a growth rule that stays ahead of influence can grow
  forever; a reading of knots across time from the last growth event rather than the first row.
- **The missing bridge to the program's composed topology.** A growth rule the dynamics choose that keeps every contact persistent.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Growth chosen by the dynamics: grow where influence has not arrived (B23) | 3/3 — Major | 2/3 — Testable | On a running tube, insert each band only at a cut that no old ring's first row has reached, choosing the band's direction the same way, and run the rule as long as such cuts exist → a rule that grows forever with every contact persistent, and the dimension it grows, or the lag at which no such cut remains | Selected · the coordinator's fallback |
| 2 | Knots read from the last growth event (challenges A30's first row) | 2/3 — Substantial | 3/3 — Ready | Read binding against each cell's value at the latest insertion that reached it, and test whether every contact then persists under continual growth → a native reading under which growth in time keeps persistence, or a failure | Alternative · deferred |
| 3 | Which reached bindings survive | 1/3 — Minor | 2/3 — Testable | Split the 8,404 surviving bindings by the parity of the returns they carry across the cut → a criterion, or none | Alternative · deferred |
| 4 | Handles from two bands at once (B22) | 2/3 — Substantial | 1/3 — Stated | Glue a band pair across the n × m torus as a handle → a balanced genus-2 network, or none | Alternative · deferred |

1. **Growth where influence has not arrived.** Payoff 3: a rule chosen by the network's own dependence would make growth native and
   decide which way bands go, hence the dimension. Concreteness 2: the reached test is exact and cheap; the open part is whether such cuts
   last. Main uncertainty: on a closed tube every cut is reached within about the time of flight across it.
2. **Knots from the last growth event.** Payoff 2: it would make growth in time compatible with persistence, if the reading is native.
   Concreteness 3: a change of the binding test only. Uncertainty: whether a moving first row is a reading or a scheduler.
3. **Surviving bindings.** Payoff 1: explains the computed 32%. Concreteness 2.
4. **Two bands.** As in `GROWN-DISTANCE-20261109-001`.

**Recommendation.** Research directions, selected #1, the coordinator's fallback B23 in the sharpened form; stop it at a rule that grows
forever with every contact persistent, or at the lag when no unreached cut remains.

## Final report as sent

Sent to the owner on 2026-11-09 at 20:03 UTC and copied here verbatim.

**Growth while running (B24) is closed and published.** If the band law grows while the network runs, persistence breaks quickly. It breaks causally, from the growth outward. ([decision note](https://github.com/jscul/knotlab/blob/main/research/GROW-RUN-20261109-001/grow_run.md))

- **Proved:** a band inserted at lag t₀ leaves every ring its influence hasn't reached fully bound, and its own new rings are always bound.
- **Computed, exact over every insertion lag:** 68% of the bindings of rings it has reached fail. Only an insertion at lag 0 keeps every contact persistent on all 13 tubes. The damage spreads out from the band one row per row's time length. With a band every P lags, only the newest band stays bound.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: growth while running | Successful | Exact: intact outside the insertion's reach (proved), mostly broken inside it (computed) |
| Local direction: a law that grows in time | Full pivot | Persistence breaks quickly; your fallback is B23 |
| Broader exploration: G1 with G5 | Known alternatives | B23 with a candidate rule; B22 |
| Long-term goal: G1 Space from a law | Obstruction learned | Persistent growth must happen between runs, or only where influence hasn't arrived |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Growth chosen by the dynamics, where influence hasn't arrived (B23) | 3/3 | 2/3 | Insert a band only where it would keep every contact → a rule that grows forever, or the lag when no such place is left |
| 2 | Knots read from the last growth event | 2/3 | 3/3 | Re-base binding at each insertion → a native reading where growth keeps persistence, or a failure |
| 3 | Which reached bindings survive | 1/3 | 2/3 | Split the survivors by the returns they carry → a criterion |
| 4 | Handles from two bands (B22) | 2/3 | 1/3 | Unchanged |

**Corrections:** none. **Goals:** G1/G5 checkpoint, B24 taken, B23 selected (ratings raised). **Assumptions:** A42 confirmed (growth must come between runs), A44 added (new cells are open distinctions). **Long-running:** stress test GROW-RUN-S1 is still running and will be folded in.

Starting #1 now, as you asked. An early probe is not encouraging: on a 3 × 3 tube, "insert whenever it's safe" adds one band at lag 0 and then finds no safe lag in the next 80.
