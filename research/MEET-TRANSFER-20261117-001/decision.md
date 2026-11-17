# Decision: MEET-TRANSFER-20261117-001

2026-11-17 · goals G15, G16 · takes `SCALE-MEMORY-20261116-001#1` · computed, referee pending · result note
[meet_transfer.md](meet_transfer.md) · pre-registration [preregistration.md](preregistration.md) (frozen `19c8b1ed1`,
2026-11-17 04:48 UTC)

**Headline.** With reads that count neither steps nor knots, the navigating agent carries over to meeting patterns it never trained
on. On the held-out `local` pattern it goes from 25 times worse than the best tuned rule to 0.83 times its flips at n = 3,200 and
0.66 at 800. In flips it beats the best rule on most held-out and training patterns: 0.61 on `block`, 0.72 on `heavy`. It loses on
the plain `rand` 2.1 pattern at 3,200 (1.60) and costs 1.5 to 9 times the CPU per instance. The reads do the carrying, not the mixed
training: a `rand`-trained agent with the same reads does as well on `local`.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: degree-normalized, step-free memory trained on mixed meeting patterns | **Status:** Partially successful | Usable inner loop on the held-out primary (R 0.83 [0.63, 1.09]) and three of four untouched cells; flips wins on `local` 800, `heavy` 3,200 and `block`; fails the bar on window 40 by one seed in four; loses on `rand` 2.1; no CPU win |
| Local direction: learned memory for choosing where and what to act on | Continue | The agent now beats well-tuned Novelty+ in flips across meeting patterns; seed variance and cost per step are what remain |
| Broader exploration: learned search for satisfiability | Known alternatives | Novelty+ stays the strongest hand-written rule here; the learned agent's flips advantage is real but costs 1.5 to 9 times the computing per instance |
| G15 Learning: a point in a learned knot pattern, and G16 Learning the rules behind what a system allows | Capability gained | First learned agent in the program that carries across meeting patterns and beats a well-tuned rule there in flips |

**Next step:** Research directions — selected: #2 (#1 offered to the slow-loop line, which owns B191: `SLOW-LOOP-20261117-001`,
`EARN-BUDGET-20261117-001`, and `SPEC-MERGE-20261117-001`, which took the owner's full picture)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | This learned agent as the fast loop of the structure-changing slow loop (B191, the owner's full picture) | 3/3 — the owner's metacognition picture, with a fast loop that now reads new structures | 3/3 — the slow-loop line has its loop and Novelty+ as fast loop; swap in Dr (or D) and rerun its paid comparison | Replace Novelty+ by Dr in the slow loop's charged comparison on its local and block cells → stop if the charged total is not below the Novelty+ fast loop's | Offered to the slow-loop line (coordinator decides the join) |
| 2 | A cheaper agent: turn the flips win into a CPU win | 2/3 — a real win where flips are 0.6 to 0.8 times (`block`, `heavy`, `local`) needs about 1.5 times the cost per step, not 3 to 9 | 3/3 — the weights exist; distil the where-and-what scores into a linear rule or cache the reads | Distil D into a linear score and rerun `block` and `heavy` 3,200 → stop if its flips rise above 1.2 times D's or its CPU stays above the best rule's | Selected · not started |
| 3 | Seed variance: select across more patterns | 1/3 — would remove the window-40 failure and the `rand` 2.1 loss | 3/3 | Train eight seeds and select by validation on all training patterns plus a held-out one → stop if the worst seed is still above 2 on window 40 | Alternative · deferred |

Ratings. #1 is the owner's goal and now has the fast loop it needed, but another line already owns the slow loop, so it is offered
there rather than duplicated. #2 is this thread's own next step: the only route to a real (CPU) win, and cheap. #3 is housekeeping.

**Corrections:** none.
**Goals:** checkpoint row added (G15, G16; capability gained); G15's Stands on and Open updated; no goal changed.
**Assumptions:** relied on A88 and A89 (the reading of the owner's agent and the measure), unchanged.
**Basket:** as before; #1 is sub-goal B191, owned by the slow-loop line, now with a learned fast loop to offer it.
**Advisor:** Fable 5.2 reviewed the draft and said a negative result would be uninterpretable without an oracle arm. Its changes are
in the frozen design: the oracle, untouched held-out families, an inner-loop bar, two-stage tuning and four seeds
([advisor_review.md](advisor_review.md)). Not used after the results.
**Referee:** pending; hand-off below.

## Referee hand-off

1. **The gate.** Rerun `check.py`, G6 especially (identity with SCALE-MEMORY's engine, which licenses reusing L3sm), and read flag 32
   in `nae_engine.c` and the `block` and `heavy` generators in `engine.py`.
2. **The comparators.** Recompute the two-stage tuning from `screen/`, `screen_edge/` and `confirm/`, and check that the best rule in
   each cell was well chosen (try a setting of your own off the grid on the primary cell).
3. **The headline.** From `test/results.jsonl`, recompute per cell the five-run per-instance geometric means, each seed's median, R
   with the best rule re-chosen per resample (99%), X, Y, Z, K and O, and the inner-loop bar with seed agreement. Confirm D's verdict
   ("usable on the primary only", by one seed on window 40) and that Dr meets the bar everywhere held out.
4. **Gates.** `gates.json`: whether D's arm-level G-learn on `rand` 2.1 (1.147) should be read per arm or per seed (three of four D
   seeds fail per seed).
5. **The flips wins**: `local` 800, `heavy` 3,200 and `block` 3,200 by the frozen tiers; check seed agreement and that CPU loses.
6. **Prior work** (`track.py objects-gate research/MEET-TRANSFER-20261117-001/preregistration.md`) and words.

## Final report as sent

2026-11-17 09:25 UTC, in the project thread (tables as above, shortened for the owner):

> **Result: your agent's memory now carries across meeting patterns it never trained on, and it beats a carefully tuned Novelty+
> in flips on most of them.** The change was in what the agent reads, not in how it was trained. On the held-out local pattern it
> takes 0.83× Novelty+'s flips at 3,200 and 0.66× at 800, against five runs per instance. The previous agent was 25× worse there.
> It also wins clearly in flips on a heavy-tailed pattern it never saw (0.72×) and on a clustered one (0.61×). It still loses on
> plain random patterns at 3,200 (1.6×) and costs 1.5 to 9× the computing per instance. The version trained only on random patterns
> does just as well on local.
>
> **For your second stage:** the agent now meets the bar I set for an inner loop. It meets it on the held-out pattern for the
> mixed-trained version, and on every held-out pattern for the version trained on random patterns only.
>
> **Corrections:** none. **Goals:** checkpoint added. **Assumptions:** unchanged. Referee pending.
