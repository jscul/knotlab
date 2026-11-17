# Decision: SCALE-MEMORY-20261116-001

2026-11-17 · goals G15, G16 · takes `WHERE-NEXT-20261116-001#1` · computed, **stress test pending** (n = 51200), referee
pending · result note [scale_memory.md](scale_memory.md) · pre-registration [preregistration.md](preregistration.md) (frozen
`40cf4237c`, 2026-11-17 00:02 UTC)

**Headline.** Size-relative memory carries the navigating agent to parity with the best hand-written rule at 3,200 and 12,800
distinctions, not to a win. With step-counted memory it collapses (R 1.36 and 14.5); with memory that counts no steps it stays
at 0.82 to 0.94 in the frozen runs and 0.88 to 1.01 in the post hoc five-run check. The training-size margin (about 1.3 to 1.4
times) is mostly gone by 4 to 16 times the training sizes. By the frozen rule: inconclusive for the scale-free arms and for L3m
(corrected 2026-11-17: its seeds disagree), clean loss for the control L3c, learner failure for the memoryless one; no CPU win
anywhere; every arm still loses on the unseen local pattern. The frozen 0.82 at 12,800 rests on a comparator 10 to 15% weaker than
the best Novelty+ there (corrected 2026-11-17), so the five-run 0.92 to 0.94 is the better reading.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: scale-free memory and training at 3,200 for the navigating agent | **Status:** Partially successful | The collapse at scale is removed (S = 0.059) and the reads, not the training size, carry it (L3sm / L3s = 0.95); no flips win by the frozen rule (L3s 0.94 at 3,200, L3sm 0.82 [0.73, 0.91] at 12,800), and five runs put both near 1 |
| Local direction: learned memory for choosing where and what to act on | Continue, toward meeting-pattern transfer | On one meeting pattern learned memory now matches Novelty+ across a sixteen-fold size range; on another it still loses 4.7 to 29 times, with counts not normalized by degree |
| Broader exploration: learned search for satisfiability | Known alternatives | The learned agent rediscovers about what Novelty+'s scale-free age rule does; a margin over it at scale is not shown, and the cost per flip is about 5 times |
| G15 Learning: a point in a learned knot pattern, and G16 Learning the rules behind what a system allows | Capability gained | A learned memory that carries across size on one meeting pattern; the obstruction left is meeting-pattern transfer and cost |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Transfer across meeting patterns | 2/3 — the prerequisite for the owner's second stage: a fast loop that can read structures unlike its training ones | 3/3 — the engine and trainer exist; add degree-normalized counts and a mixed-pattern curriculum | Train fully scale-free, degree-normalized memory on `rand` and one more family, test on held-out `local` against Novelty+ with five runs per instance → stop if R on the held-out family stays above 2 | Selected · not started |
| 2 | Mutating knot structures to cut the agent's work (B191) | 3/3 — the owner's metacognition picture | 1/3 — needs a fast loop that reads new structures, or Novelty+ as the fast loop, and a structure move that keeps the allowed states and differs from clause learning | Define one state-preserving structure move with Novelty+ as the fast loop, against clause learning at matched cost → stop if the charged total never beats the fast loop alone | Alternative · deferred (B191) |
| 3 | Cheaper reads: distil the learned what-rule into a linear score | 1/3 — at parity in flips, a cheaper step only reaches a tie in CPU | 2/3 — the trained weights exist | Fit a linear score to L3sm's choices and rerun 12,800 → stop if its flips rise above 1.1 times L3sm's | Alternative · deferred |

Ratings. #1 is what B191 needs first: a slow loop that changes structures would be judged by a fast loop that cannot yet read
structures unlike its training ones. #2 stays the owner's goal, and could start with Novelty+ as its fast loop if #1 fails. #3
cannot give a CPU win while flips are at parity.

**Corrections:** none to earlier claims from this study (WHERE-NEXT's four corrections of 2026-11-17 were logged and signed off
separately).
**Goals:** checkpoint row added (G15, G16; capability gained); G15's Stands on and Open updated; no goal changed.
**Assumptions:** relied on A88 and A89 (WHERE-NEXT's reading of the owner's agent and its measure), unchanged.
**Basket:** as in WHERE-NEXT; the paused point-learner items do not test the navigating agent, so #1 stands.
**Advisor:** Fable 5.2 reviewed the first draft and said "don't freeze yet"; its seven changes are in the frozen design
([advisor_review.md](advisor_review.md)). Not used after the results.
**Stress test pending:** the n = 51200 cell (P5, the transfer cell of the mixed arms), registered `SCALE-MEMORY-P1`.
**Referee:** pending; hand-off below.

## Referee hand-off

1. **The gate.** Rerun `check.py`, G6 especially (run-for-run identity with WHERE-NEXT's engine, which licenses reusing its rule
   runs). Read the flag-16 code in `nae_engine.c`: ages relative to the knot's and the candidates' oldest, the violated fraction,
   never-flipped age t + 1.
2. **The headline.** From `artifacts/SCALE-MEMORY-20261116-001A/.../test/results.jsonl`, with WHERE-NEXT's `test/` and `stress/`,
   recompute per arm the geometric mean of the two seeds' medians, R with the best rule re-chosen per resample (99%), and S, T, C,
   I, K; confirm the verdicts and the diagnosis.
3. **The gates per arm** from the training logs (`gates.json`): G-learn against Novelty+ on the validation instances
   (`novelty_val_reference.json`), G-train for the mixed arms.
4. **The post hoc check** (`posthoc/`, `posthoc_summary.json`): agreed before the results were final, not frozen; check it is
   labelled so wherever it is used, and that it reran the agents with fresh seeds.
5. **Fairness.** Novelty+ at walk probability 0 was outside the frozen grids; the five-run check includes it. Check whether the
   frozen comparator was weaker than it should have been at 3,200 and 12,800.
6. **Prior work** (`track.py objects-gate research/SCALE-MEMORY-20261116-001/preregistration.md`) and words.

## Final report as sent

2026-11-17 04:30 UTC, in the project thread (position and directions tables as above, shortened for the owner):

> **Result: memory that doesn't count steps carries your agent to parity with the best hand-written rule at 4× and 16× its
> training size, but not to a win.** With step-counted memory the agent collapsed at larger sizes, to 1.4× and 15× Novelty+'s
> flips. With memory that reads each age against the oldest of the knot's three distinctions, it stays at 0.82 to 0.94 of
> Novelty+'s flips, and 0.88 to 1.01 on a five-run recheck. Training on bigger patterns added nothing once the memory was
> scale-free. It still costs about 5× the computing per step, and it still loses on the local pattern, where memory still hurts.
>
> **What this means for your second stage:** a slow loop that changes knot structures would put the agent on patterns it never
> saw, and that's exactly where it still fails. So #1 comes first.
>
> **Limits and pending work:** one kept step-counted read (it only understates the agent), counts not adjusted for how many knots
> meet at a distinction (this mainly weakens the local result), and single runs (the five-run check pulls the results toward
> parity). The 51,200 cell is still running and the referee is pending.
>
> **Corrections:** none new. **Goals:** checkpoint added. **Assumptions:** unchanged.
