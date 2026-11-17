# Decision: EARN-BUDGET-20261117-001

2026-11-17 · goals G15, G16 · takes `SLOW-LOOP-20261117-001#1` (sub-goal B191) · computed, **stress test pending** (n = 12,800),
referee pending · result note [earn_budget.md](earn_budget.md) · pre-registration [preregistration.md](preregistration.md) (frozen
`fd9e95c8d`; charge corrected before the test, `13ae23679`)

**Headline.** A structure-changing slow loop that earns its budget from how much its own merges shrink the pattern was tuned on
`rand`, `block` and `local` w10 at n = 800 and tested on fresh instances at 3,200.
- **It is safe:** 3% overhead on every structure-poor pattern.
- **It wins** on the never-run primary (`local` w15 at density 3.5: 0.56 [0.51, 0.68], CPU 0.61), on `local` w20 (0.75) and on
  `local` w10 (0.56). It beats the best fixed batched budget tuned the same way.
- **It ramps too slowly.** The fixed budget tuned on each cell itself reaches 0.16 to 0.18, a regret of 3.4 to 4.1 times. It never
  leaves its floor on `local` w40, where ties are rare but cascade.
- **Without a local pattern in tuning it does not carry over** (Erb at parity).
- **By the frozen rule this is reading 2:** it works, but earning is not shown to matter, since E/GO = 1.65 > 1.5 on `local` w10.
- **What is known.** The moves and the principle are known (probing, equivalent-literal substitution, productivity-driven
  inprocessing), and CaDiCaL solves these local patterns in at most 0.06 s.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: an earned budget (doubling and halving on the share merged per unit of slow cost) for the structure-changing slow loop | **Status:** Partially successful | Reading 2: charged wins on the unseen primary and two other local patterns, about 3% overhead on all structure-poor ones, better than the fixed batched budget; but 3.4–4.1 times the per-cell oracle, nothing on `local` w40, no transfer from structure-poor tuning |
| Local direction: scheduling structure changes by their own yield | Continue, toward pricing a batch of moves before paying for its rebuild | The ramp is the obstruction. A rebuild waits for 3% of the classes and the budget doubles once per rebuild, so rare cascading ties (w40) are never tried and dense ones (w20) are tried late |
| Broader exploration: inprocessing schedules for satisfiability | Known alternatives | CDCL solvers schedule inprocessing by effort relative to search and by productivity; CaDiCaL solves every local instance here in 0.06 s; clause weighting is untested here |
| G15 Learning: a point in a learned knot pattern, and G16 Learning the rules behind what a system allows | Capability gained | The first slow loop in the program tuned on some meeting patterns that wins on unseen ones without costing on structure-poor ones; the eagerness it would need is learned only where the gain already shows |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Price a batch before rebuilding: predict the shrink of the pending ties with the tie cascade alone, and set the budget from the predicted yield, jumping to the top on the first productive batch | 2/3 — would close most of the 3–4 times regret and reach `local` w40, a structure loop that is eager where it pays and lazy elsewhere | 3/3 — the cascade (`sl_reduce`) already runs without the handle; one rule; the same cells and tuning | Add the priced rule, tune on the same three patterns at 800, test on the ten 3,200 cells and a new pattern → stop if E′/GbO stays above 1.5 on the local cells or the structure-poor cost exceeds 5% | Selected · not started |
| 2 | Tune where the gain exists: tune the schedule at n = 3,200, or scale its floor with n | 1/3 — a tuning fix; it shows whether size, not the rule, made E cautious | 3/3 — rerun the policy stage at 3,200 | Tune E at 3,200 on the three patterns, test on the same cells → stop if E/GbO stays above 2 | Alternative · deferred |
| 3 | Weights, not structure: clause weighting (PAWS or SAPS, re-tuned) against the eager structure loop | 2/3 — decides whether changing structure beats the cheaper precedent that also follows where the search stays violated | 2/3 — a new search family in the engine and its own tuning | As `SLOW-LOOP-20261117-001#2` → stop if weighting matches the eager structure loop on the local cells | Alternative · deferred (`SLOW-LOOP-20261117-001#2`) |
| 4 | The owner's full picture: the learned agent as the fast loop under a structure-changing slow loop | 3/3 — the owner's two loops together | 1/3 — the agent reads unsigned knots only and still loses on `local` | As `SLOW-LOOP-20261117-001#3` | Alternative · deferred (under B191) |

Ratings.
- **#1.** It attacks the measured cause of the regret: the doublings counted (0 on w40, a median of 4 on w20) show the ramp, not
  the moves, limiting E. Pricing a batch costs one cascade per epoch, which the engine already has. Its bound is one tuning and one
  test like this study's, about 2 CPU-hours. It moves G15 and G16 as scheduling capability only.
- **#2.** Cheap, but it only shows how much of the caution was the tuning size.
- **#3 and #4** are carried from SLOW-LOOP unchanged.

**Corrections:** none to earlier claims from this study. SLOW-LOOP's referee fixes were folded in separately (`1dbe6ffee`, four
entries in `docs/CORRECTIONS.md`), and this study corrected its own charge before the test (a deviation, listed in the note).
**Goals:** checkpoint row added (G15, G16; capability gained); G15's Stands on and Open updated; no goal changed.
**Assumptions:** added A92 (a slow loop's eagerness is earned by doubling and halving its budget on the share of the pattern its
batched merges remove per unit of slow cost), Assumed. Relied on A90 and A91, whose history records the corrected charge.
**Basket:** as at SLOW-LOOP's close: the learning line's untaken items belong to the paused point-learner line. MEET-TRANSFER is
still running. So #1 stands.
**Advisor:** Fable 5.2 reviewed the draft design and said "freeze with changes". All were taken ([advisor_review.md](advisor_review.md)).
It was not used after the results.
**Stress test pending:** T2, `local` w20 and `heavy` at n = 12,800 (registered `EARN-BUDGET-T2`).
**Referee:** pending; hand-off below.

## Referee hand-off

1. **The gate.** Rerun `check.py` (G0–G10).
   - Read the earned budget and batching in `slow_loop.py` (`run_slow`: `earn`, `batch`, `pend_ties`, the q update) and charge v2
     (`_sortcost`, `fl_set_sortlog`).
   - Check that the earned budget's moves are sound (G1, G4, G7 include it) and that v2 adds only the sorting (G10).
2. **The headline**, recomputed with independent code from `artifacts/.../test/results.jsonl`:
   - per cell and arm, the median of five-run geometric means of `work`, and R against the better of NOV and PS (99%, re-chosen
     per resample);
   - the frozen verdicts and decision reading 2;
   - the regret E/GbO, and Erb and ErbL on `local` w10.
3. **The deviation.** Check the ordering of the runs against `13ae23679`:
   - policy tuning and the first half of the oracle reran under v2 before the test launched;
   - `policies.json` and `oracle_policies.json` come from the v2 runs;
   - no test case predates them.
4. **Fairness.**
   - Novelty+ and probSAT were re-tuned per cell (`retune/`), and the edge settings are reported.
   - The slow arms use the cell's NOV setting.
   - E, Erb, Gb, Gm and ST were tuned on the same instances with the same score, and the tie rule was applied as declared.
   - GbO was tuned on each cell's tuning instances, disjoint from the test's.
5. **The ramp diagnosis.** From `test/`, E's `rho_top`, `doublings` and `rebuilds` per cell, against the claim that the ramp, not
   the moves, limits it. The cascade on `local` w40 under GbO (98 classes left) is evidence that the moves are there.
6. **CDCL.** The wall-time reading.
7. **Prior work.** Rerun `track.py objects-gate research/EARN-BUDGET-20261117-001/preregistration.md`, and check the claims about
   inprocessing schedules in Lingeling, CaDiCaL and Kissat against their sources. The pre-registration says which were not
   verified.
8. **Words.** As in SLOW-LOOP.

## Final report as sent

2026-11-17, in the project thread (position and directions tables as above, shortened for the owner):

> **Result: a slow loop that earns its budget from how much its own changes shrink the pattern is safe everywhere and wins on new
> local patterns, but it ramps up too slowly to take most of the gain.**
>
> - **Where it wins.** Tuned on three patterns at 800 distinctions, it cut total work to 0.56 of tuned Novelty+ on a local
>   pattern nothing had touched before the freeze, and to 0.75 and 0.56 on two others, at 3,200 distinctions. Computing time
>   fell too.
> - **Where it costs.** On random and heavy-tailed patterns it costs about 3%, and it beats a fixed budget tuned the same way.
> - **Why the gain is partial.** A fixed budget tuned on each pattern itself reaches 0.16 to 0.18, so earning leaves 3 to 4 times
>   on the table. The rule starts cautious and doubles only once per rebuild. On the window-40 pattern, where ties are rare but
>   each one cascades, it never got started.
> - **Without a local pattern in tuning,** it doesn't carry over.
> - **The frozen verdict.** By the frozen rule it "works, but earning is not shown to matter", because it stays more than 1.5
>   times the eager loop on the local pattern.
> - **Next.** Price a batch of changes before paying for the rebuild (#1).
>
> **Also:** the first study's referee confirmed it with one Narrowing. The eager loop's wins are about 0.24–0.30 and 0.46–0.60 when
> every cost is counted, still wins. I logged that and three minor fixes as corrections.
>
> **Corrections:** four, all on the first study (one Narrowing, three Not a block). **Goals:** checkpoint added, no goal changed.
> **Assumptions:** A92 added (how the slow loop earns its budget). Stress test at 12,800 and referee pending.
