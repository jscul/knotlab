# Decision: SLOW-LOOP-20261117-001

2026-11-17 · goals G15, G16 · takes sub-goal B191 (the owner's second stage) · computed, referee pending · result note
[slow_loop.md](slow_loop.md) · pre-registration [preregistration.md](preregistration.md) (frozen `8898f7117`) · stress cell (n =
12,800) done and folded in

**Headline.** A slow loop that changes the knot pattern between epochs of re-tuned Novelty+ was tested, with tie merges and shadow
knots that keep the allowed states, every probe and rebuild charged.
- **The eager loop pays where the pattern has local structure.** With the policy tuned on `local` window 10 (GO), charged work
  falls to 0.15 [0.12, 0.19] of the best fast rule on `local` w10 and to 0.23 [0.19, 0.30] on `local` w40, which GO never saw, at
  n = 3,200. At 12,800 it is 0.12 on w10. These are charged wins, CPU included, and 3.4 to 5.5 times better than tuned static
  probing.
- **The eager loop costs elsewhere:** 1.5 to 2.1 times as much on random and block patterns.
- **The transferred policy does nothing.** The policy tuned on `rand` and `block` (G) is the grid's laziest, at parity everywhere
  (0.84 to 1.09). By the frozen rule that is **reading 4, no charged win for G anywhere**.
- **The search's attention does not help.** The knots the search attends to most are no better probe targets than random knots,
  and random targets did as well or better at the eager policy (post hoc).
- **Shadow knots turned no cell into a win.**
- **All of it is known inference.** Both moves are probing with equivalent-literal substitution and learned implied clauses, and
  CaDiCaL solves the local patterns in 0.06 s.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: tie merges and shadow knots scheduled by the search's attention, policy tuned on random and block patterns | **Status:** Failed (frozen rule: no charged win for the transferred policy G), with a charged win for the oracle-tuned policy | G is lazy and at parity in all 10 cells; GO cuts charged work 4–8 times on both local patterns at 3,200 and 12,800 and loses 1.5–2.1 times on random and block |
| Local direction: changing the knot pattern during the search | Continue, toward a slow loop that sets its own eagerness from how fast its moves shrink the pattern | The gain is large where structure exists and grows with size; the obstruction is choosing eagerness without having tuned on the pattern. The probes' find rate does not tell the patterns apart, but the shrink rate nearly does (post hoc reading, below) |
| Broader exploration: structure-changing inference for satisfiability | Known alternatives | Failed-literal probing, equivalence substitution and inprocessing (CaDiCaL solves every local instance in 0.06 s, but needs 88 s on `rand` 3,200 against Novelty+'s 0.014 s); clause weighting, which also follows where a search stays violated, is untested here |
| G15 Learning: a point in a learned knot pattern, and G16 Learning the rules behind what a system allows | Obstruction learned | The fast loop's attention carries no information about where the structure can change; a slow loop's budget tuned where nothing can be found does not carry over to where much can |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A slow loop that earns its budget: eagerness set online from how fast its moves shrink the pattern | 2/3 — a policy tuned anywhere that is lazy where nothing shrinks and eager where much does; it would turn GO's oracle win into a transferred one | 3/3 — the engine, cells and tuning exist; one rule: the next slow budget is ρ_max times the classes merged per unit of slow work in the last epoch, over a threshold | Tune ρ_max and the threshold on `rand` and `block` 800, test on the held-out local and embedded cells at 3,200 → stop if R on `local` w10 3,200 stays above 0.5 or `rand` 3,200 costs more than 1.1 | Selected · not started |
| 2 | Weights, not structure: clause weighting (PAWS or SAPS, re-tuned) against the eager structure loop | 2/3 — decides whether changing structure beats the cheaper precedent that also follows where the search stays violated | 2/3 — a new search family in the engine and its own tuning; the cells exist | Add one weighting search, re-tune per cell, compare with GO on the five 3,200 cells → stop if weighting matches GO on the local cells | Alternative · deferred |
| 3 | The owner's full picture: the learned agent as the fast loop under a structure-changing slow loop | 3/3 — the owner's two loops together | 1/3 — the agent reads unsigned knots only and still loses on `local` (MEET-TRANSFER pending) | Give the agent signed reads, run it on GO's changed patterns → stop if it stays above 2 times Novelty+ there | Alternative · deferred (filed under B191) |
| 4 | A move static probing cannot make: changes that keep only satisfiability (eliminating a distinction into the knots of its shadow) | 2/3 — the only kind of move that could help on random patterns | 1/3 — elimination grows knots of four and more places, which the engine does not hold; prior work (bounded variable elimination) finds little on random patterns | Eliminate distinctions of up to two knots on `rand` 3,200 and run Novelty+ on the rest → stop if the charged total is not below 0.95 | Alternative · deferred |

Ratings.
- **#1.** It is the direct remedy for the obstruction found, and the code needs one rule. Its bound is one tuning and one test
  like this study's (about 2 CPU-hours). It moves G15 and G16 only as a capability in scheduling, since the moves stay known
  inference. The probes' find rate would not do: on `block` they find 0.1 ties per target and the eager loop loses, while on
  window 40 they find 0.013 and it wins, because there each tie cascades (94% of the distinctions merged). The shrink rate nearly
  separates them: 300 to 1,500 classes merged per 10^6 slow incidences where GO paid, against 160 or less where it lost. The one
  exception is `embed` 800 (456, a loss), where the search alone is already cheap. This reading is post hoc, which is why it is a
  direction and not a finding.
- **#2.** It is the advisor's unrun comparator, and without it a structure win cannot be said to beat weighting.
- **#3.** It is the owner's picture in full, but its fast half still fails on the local patterns where the slow half pays.
- **#4.** The moves would be new to this engine, but the literature expects little on random patterns.

**Corrections:** none to earlier claims. The deviations from this study's own frozen text are listed in the note: a re-tuning grid
extended at its edges, an analysis edit that had not applied, and the CaDiCaL interrupt.
**Goals:** checkpoint row added (G15, G16; obstruction learned); B191 marked taken by this epic, with its first attempt and the
filed direction #3; G15's Stands on, Open and Lines updated; no goal changed.
**Assumptions:** added A90 (the reading of the owner's slow loop as changes to the pattern that keep its allowed states, at the
knots the search attends to most) and A91 (charged work counts both loops and every rebuild), both Assumed. Relied on A88 and A89.
**Basket:** the learning line's untaken items (B155, B154, B157, B162, B166, B169 and 14 more) belong to the paused point-learner
line and test neither loop of the navigating agent; MEET-TRANSFER's result is pending. So #1 stands.
**Advisor:** Fable 5.2 reviewed the draft design and said "freeze with changes". All eight were taken except the clause-weighting
arm, now direction #2 ([advisor_review.md](advisor_review.md)). It was not used after the results.
**Stress test:** the n = 12,800 cell (S4, registered `SLOW-LOOP-S4`) finished before the close and is folded in.
**Post hoc (not frozen):** RNDO (registered `SLOW-LOOP-H1`), static probing tuned on `local` w10 (it came out the same setting as
ST), and the one-epoch attention diagnostic.
**Referee:** pending; hand-off below.

## Referee hand-off

A fresh session should recheck, without this thread's reasoning:

1. **The gate.** Rerun `check.py`. Read `slow_engine.c`:
   - `propagate`: a refutation is sound, and three incidences are charged per knot read;
   - `tie_probe` and `shadow_triple`: which relation each refuted pattern gives;
   - `sl_reduce`: the tie cascade, and a knot dropped only when it always holds;
   - the signed incremental counts in `flip` and `bm`.

   Check that with every sign 0 the fast loop reproduces SCALE-MEMORY's engine (G6), and that the mutant gate G4 would catch a
   wrong parity.
2. **The headline**, recomputed with independent code from `artifacts/.../test/results.jsonl`: per cell and arm the median over
   instances of five-run geometric means of `work`, R against the better of NOV and PS re-chosen per resample (99%), the frozen
   verdicts, and decision reading 4. Also GO's charged wins on `local` w10 and w40 at 3,200 (R_W and R_CPU), and the stress cell.
3. **Charging.** Check that `work` counts everything the slow loop does:
   - probes (three per knot read, plus the assumed distinctions);
   - target selection (the visited list and the sort), the cascade, the canonicalization, and the new handle's 3m.

   Check that a slow arm's flips equal NOV's from the same initial state until the first move.
4. **Fairness.**
   - Novelty+ and probSAT were re-tuned per cell on disjoint tuning instances (`retune/`, `retune2/`), and the grid extension
     only added settings.
   - The slow arms use the cell's NOV setting.
   - G and ST were tuned on the same instances with the same score (`policy/`, `choose.py`), and GO on `local` w10 800 only.
   - Test seeds 7,100,000 and up appear in no tuning stage.
5. **The attention reading.** From `test/` and `posthoc/`:
   - moves per target for G, RND, GO and RNDO;
   - the selection cost behind G's slow work per target;
   - `attention_diag.json`.

   Check the claim that P6 held by its letter only (RND's extra rebuilds).
6. **CDCL.** The interrupt did not fire. Check the wall-time reading of P9 and P10.
7. **Prior work.** Rerun `track.py objects-gate research/SLOW-LOOP-20261117-001/preregistration.md`, do one search of your own,
   and check the literature named (probing, equivalence reasoning, inprocessing, R+AdaptNovelty+, structure in local search).
8. **Words.** Check the glossary's words: tie class, shadow, distinction, knot, meeting pattern. Flag any spatial word used for
   the program's own objects.

## Final report as sent

2026-11-17, in the project thread (position and directions tables as above, shortened for the owner):

> **Result: changing the knot structure while the search runs pays a lot where the pattern has local structure, but only when the
> slow loop is eager, and the search's own attention is no help in choosing where to change it.**
>
> - **The eager loop.** It spends as much on finding ties as on searching. It cut the total work, every probe and rebuild
>   charged, to 0.15 of the best tuned Novelty+ on the local pattern, and to 0.23 on a second local pattern it never saw, at 3,200
>   distinctions (0.12 at 12,800). That beats probing everything first by 3 to 5 times.
> - **Where it costs.** On random and block patterns it costs 1.5 to 2 times as much, because there is nothing to find.
> - **The tuned policy.** Tuned on those patterns, the slow loop learned to do almost nothing, so by the rule I froze in advance
>   the transferred policy has no win anywhere.
> - **Attention.** The knots the search keeps returning to are no better places to change the structure than random knots.
> - **The added knots.** The derived knots (your "braid") never turned a cell into a win.
> - **What is known.** Both moves are known inference (probing and merging equivalent variables), and CaDiCaL solves the local
>   patterns in 0.06 s.
>
> **Is it worth continuing?** Yes, in one narrow form. How fast the moves shrink the pattern nearly tells the two kinds of
> pattern apart here, so a slow loop that earns its budget from that should keep the gain and lose the cost. That's next (#1).
> How often probes find something does not tell them apart.
>
> **Corrections:** none. **Goals:** checkpoint added, no goal changed. **Assumptions:** A90 (the reading of your slow loop) and A91
> (how it is charged) added. Referee pending.
