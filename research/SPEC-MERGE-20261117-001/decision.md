# Decision: SPEC-MERGE-20261117-001

2026-11-17 · goals G15, G16 · takes sub-goal B191 (direction A gated by D, the coordinator's go-ahead) · computed, referee pending
· result note [spec_merge.md](spec_merge.md) · pre-registration [preregistration.md](preregistration.md) (frozen `8147c8202`)

**Headline.** Speculative merges, chosen from the fast search's own co-flip evidence, made without proof when it is stuck and
undone when it does not then improve, never paid.
- **The evidence is real.** Pairs the search keeps moving together agree with the planted relative values 0.66 to 0.75 of the
  time on random patterns, against 0.55 to 0.63 for random pairs. On the local pattern they are provably tied 2.5 times as often.
  This is the first signal from the fast loop's history that predicts structure.
- **But it is too often wrong.** On random patterns, at a precision of about 0.7, unproved merges cost 1.17 to 2.26 times
  Novelty+.
- **The undo is blind.** On the local pattern it threw away 85% of wholly correct rounds and kept 9% of wrong ones.
- **No speculative arm won anywhere.** On the local pattern the proof-based eager loop was 9 to 20 times better than any of them.
- **By the frozen rule this is reading 5: no win anywhere.** No publication-hold question arose.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: speculative merges on co-flip evidence with undo on stalls, Novelty+ as the fast loop | **Status:** Failed (reading 5: no win anywhere) | Gate D passed on both families, but every speculative arm lost on every random cell (1.17–4.40) and none won on `local` w10 (best 1.41); the undo does not detect wrong merges |
| Local direction: changes to the pattern that are not proofs | Retire in this form; keep the evidence | Unproved merges need precision near 1, which the evidence reaches only where proofs already work; the co-flip signal itself is worth keeping as a guide for what to prove |
| Broader exploration: speculative structure changes for local search | Known alternatives | Multilevel refinement, backbone-guided search and survey-propagation decimation; none needed here to explain the result, and none was beaten |
| G15 Learning: a point in a learned knot pattern, and G16 Learning the rules behind what a system allows | Capability gained; obstruction learned | The fast loop's own history carries structural information (first such signal); acting on it without proof fails because the remaining error rate is fatal and progress-based undo cannot see it |

**Next step:** Research directions — selected: #1 (awaiting go-ahead; the coordinator is taking stock with John)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The learned agent as the fast loop under the proof-based slow loop, its memory carried across rebuilds | 3/3 — the owner's two loops together, the agent reading the knots and the slow loop reshaping them | 2/3 — SIGNED-NAV's signed-knot engine and handle API exist (`AgentHandle.run`, `state`, `carry`); the agent's per-flip cost (4–14 times Novelty+'s CPU here) is the obstacle | Drive EARN-BUDGET's eager batched loop with Dr through `AgentHandle`, carry against restart, on `local` w10/w20 and `rand` at 3,200 against the same loop with Novelty+, five runs → stop if R against that loop stays above 1.5 on the local cells | Selected · awaiting go-ahead |
| 2 | Co-flip evidence as the target for proofs: probe the pairs the search keeps moving together | 2/3 — the first useful signal from the fast loop's history, used where it is safe; could cut the proof-based loop's probing cost | 3/3 — the evidence, the pair probe and the proof-based loop exist | Replace Gpr's random targets with the most stable pairs and probe them, on `local` w10/w20 and `rand` → stop if moves found per probe work do not rise by 1.5 times or charged work does not fall | Alternative · deferred |
| 3 | A per-merge check for speculative merges (a bounded pair probe or a short local search on the merged knots) | 1/3 — would make speculation safer, but where it can be checked it can usually be proved | 2/3 — the pieces exist | Check each speculative merge with a bounded probe before keeping it → stop if precision on `rand` stays below 0.95 | Alternative · deferred |
| 4 | Weights, not structure: clause weighting against the structure loops | 2/3 | 2/3 | As `SLOW-LOOP-20261117-001#2` | Alternative · deferred |

Ratings.
- **#1** is the coordinator's requested row and the owner's picture in full. Its concreteness rose from 1/3 to 2/3 now that the
  signed engine and the memory-carrying handle exist and have replayed real tie-merge sequences. What is still needed:
  - a driver like `run_slow` that calls `AgentHandle` and charges the agent's reads;
  - carry against restart as the first comparison;
  - the agent's CPU per flip, which decides any charged verdict.

  Its bound is one study like this one, about 2 CPU-hours.
- **#2** keeps the one positive finding of this study, but it is scheduling again.
- **#3** and **#4** are weaker.

**Corrections:** none.
**Goals:** checkpoint row added (G15, G16; capability gained and obstruction learned); G15's Stands on and Open updated; no goal
changed.
**Assumptions:** added A93 (a speculative change is judged by whether the search then gets below its pre-change best), overturned
by this study's round log. A90's history notes that changes which do not keep the allowed states were tested and did not pay.
**Basket:** as before; the learning line's other items belong to the paused point-learner line.
**Advisor:** Fable 5.2 reviewed the draft design and said "freeze with changes", all taken ([advisor_review.md](advisor_review.md)).
It was not used after the results.
**Referee:** pending; hand-off below.

## Referee hand-off

1. **The gates.** Rerun `check.py` (S1–S5). Read `spec_merge.py`:
   - the stability update;
   - the acting rule (stuck, merge, undo against the pre-round best, undo on contradiction);
   - the activity-matched random control;
   - the rebuild charge.

   Check that the loop never reads the planted state, and that every reported state is checked on the original knots.
2. **Gate D,** recomputed from `gate/results.jsonl`, including the found-solution agreement and the pass rules.
3. **The headline,** recomputed from `test_fixed/` and `test_tuned/`: R against the better of NOV and NOVt (99%), the verdicts,
   reading 5, the evidence ratios, and the publication-hold check (no random win).
4. **The undo table,** from the runs' `round_log` (right or wrong against the planted state, kept or undone).
5. **Fairness.**
   - the comparator settings (NOVt from EARN-BUDGET's tuning instances);
   - the fast loop's Novelty+ (0.7, 0.01), as the coordinator asked;
   - the tuned settings from `policy/`, on instances disjoint from the test's;
   - the two-part test on the same instances.
6. **Prior work.** Rerun `track.py objects-gate research/SPEC-MERGE-20261117-001/preregistration.md`, and check the neighbours named
   (Walshaw 2002, Zhang 2004, survey-propagation decimation).

## Final report as sent

2026-11-17, in the project thread (shortened for the owner):

> **Result: merging distinctions on the search's own evidence, without proof, doesn't pay. The evidence is real, but too often
> wrong on random patterns, and undoing a merge when the search stalls can't tell good merges from bad.**
>
> - **The evidence.** Pairs the search keeps moving together agree with the hidden solution about 70% of the time on random
>   patterns, against about 58% for random pairs. On the local pattern they are provably tied 2.5 times as often. That's the
>   first time the search's own history has predicted structure.
> - **On random patterns,** merging them unproved costs 1.2 to 2.3 times Novelty+, since about 30% of the merges are wrong.
> - **On the local pattern,** the proof-based loop is 9 to 20 times better than any speculative one.
> - **The undo** threw away 85% of correct rounds and kept 9% of wrong ones. So by the rule I froze in advance, there is no win
>   anywhere.
>
> **Next, if you want it:** your learned agent as the fast loop under the proof-based slow loop, with its memory carried across
> rebuilds. The engine for that now exists (#1).
>
> **Corrections:** none. **Goals:** checkpoint added. **Assumptions:** A93 added and overturned (judging a merge by whether the
> search then improves). Referee pending.
