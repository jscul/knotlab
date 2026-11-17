# Decision: WHERE-NEXT-20261116-001

2026-11-16 · goals G15, G16 · takes `FOLD-TRANSFER-20261114-001#2` · computed, referee pending · result note
[where_next.md](where_next.md) · pre-registration [preregistration.md](preregistration.md) (frozen `a341054e5`)

**Verdict (frozen rule).** Clean loss on the primary cell (`rand` n = 3200: R = 1.07 [0.90, 1.21] against re-tuned
Novelty+) and on both secondary cells (`rand` n = 12800: 2.43 [1.73, 4.29]; `local` n = 3200: 55 [31, 95]). Memory helps on the
primary cell (M = 0.37 [0.31, 0.44]). No marginal-cost win anywhere (N* infinite). At the training sizes the learned agent with
memory took 0.45 and 0.60 times the flips of the best hand-written rule by the frozen protocol (corrected 2026-11-17: about 0.71
and 0.77 on the referee's five-run estimates against a widely re-tuned Novelty+, 1.3 to 1.4 times fewer; Narrowing): a learned
mechanism that works where it was trained and
does not carry over.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a learned where-and-what agent with memory against tuned rules on planted not-all-equal knot patterns | **Status:** Failed (clean loss by the frozen rule), with a training-size win | It beats every rule 1.7–2.2 times in flips at n = 200 and 800 through memory, but ties at 4 times the training size, loses 2.4 times at 16 times, loses 3–55 times on an unseen meeting pattern, and costs 4–8 times more per flip |
| Local direction: learned memory for choosing where and what to act on | Continue | The memory gain is large and real where trained; whether its failure to carry over is the step-counted features or the idea is decided by one cheap retraining |
| Broader exploration: learned search for satisfiability | Known alternatives | Learned variable selection (Yolcu and Póczos 2019; Interian and Bernardini 2023) and learned branching (Graph-Q-SAT) also win in steps on their training distribution and lose in time or at scale; scale-free hand-written memory (Novelty+, 1997–99) remains the rule to beat |
| G15 Learning: a point in a learned knot pattern, and G16 Learning the rules behind what a system allows | Capability gained and obstruction learned (for memory reads counted in steps, trained at n ≤ 800; corrected 2026-11-17) | First learned policy in the program that beats tuned search at matched instances (flips, training sizes); first measured limit on carrying it to larger sizes and other meeting patterns |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Scale-free memory: does the learned memory carry over when it reads no step counts? | 2/3 — decides whether a learned memory transfers; a positive result is a learned rule beating Novelty+ at every size | 3/3 — the engine, trainer and test cells exist; change the memory reads to ranks and ages over n, train on mixed sizes 200–3200 | Retrain L3 with scale-free memory on mixed sizes and rerun `rand` 3200 and 12800 and `local` 3200 → stop if R at 12800 is above 1.2 again | Selected · not started |
| 2 | Where with exact ground truth: does a learned where go to the knot that constrains the one it is on? | 2/3 — isolates the where-choice, which added little here, on patterns whose constraining knot is known | 2/3 — the nested patterns of `DIRECT-REACH-20261115-001` give exact least bonds at every depth (referee pending); the task still has to be framed as a where-question | Frame one task whose correct next knot is the least-bond partner, train the where-scorer, test at deeper levels → stop if it does no better than the nearest-knot rule | Alternative · deferred |
| 3 | Mutating knot structures to cut the agent's work (sub-goal B191) | 3/3 — the owner's metacognition picture, a slow loop shaping the fast one | 1/3 — no structure move defined yet that keeps the allowed states and differs from clause learning | Define one state-preserving structure move and a slow loop choosing where to apply it, against clause learning at matched cost → stop if the charged total never beats the fast loop alone | Alternative · deferred (B191) |

Ratings. #1 is the cheapest discriminator between "learned memory does not transfer" and "these features do not transfer", and
the study already holds its code and cells. #2 fits the coordinator's suggestion of the nested-pattern family: its exact least
bonds would say which knot the agent should turn to, but those patterns are about bonds across levels, not about finding a
state, so a task must be defined first. #3 is the owner's second stage and stays a sub-goal until the fast loop carries over.

**Corrections:** none. No earlier claim was found wrong; the fold line record's "the navigating agent is untested" is now
answered for its first half (memory and where), with structure mutation still untested.
**Goals:** checkpoint row added (G15, G16; capability gained and obstruction learned); G15's Stands on, Open and Lines updated; no
goal changed.
**Assumptions:** relied on the canonical knot law (K1–K3; not-all-equal passes); added A88 (the owner's navigating agent read as
focused local search over violated knots, reading) and A89 (learned search judged by work per unseen instance against re-tuned
rules, measure). This study does not bear on A21 (learning changes the law): here the agent's weights learn and its flips change
only the state.
**Basket:** the learning line's untaken items (B155, B154, B157, B162, B166 and 11 more) belong to the paused point-learner
line; none tests a navigating agent, so #1 stands.
**Advisor:** Fable 5.2 reviewed the draft design before freezing ([advisor_review.md](advisor_review.md)); its changes (curriculum,
learner gate, non-zero first layer, sticky and focused-Metropolis rules, re-tuned comparators, flip-only caps, one primary
cell, break-even count) are all in the frozen design. Not used after the results.
**Referee:** pending; hand-off below.

## Referee hand-off

A fresh session should recheck, without this thread's reasoning:

1. **The gate and the engine.** Rerun `check.py`; read `nae_engine.c` for the incremental counts, the violated list, each
   rule's definition (WalkSAT, probSAT, Novelty+, greedy-where, sticky, focused Metropolis) and the policy's feature computation;
   check that every arm uses the same initial state per instance (`test_job.run_seed`).
2. **The headline.** From `artifacts/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next/test/results.jsonl` and
   `stress/results.jsonl`, recompute the median flips per cell and arm, R with the best rule re-chosen per resample, and M, with
   independent code; confirm the verdicts above.
3. **Leakage.** Instance seeds: training 1,000,000+, validation 2,000,000+, test 3,000,000+ (`rand`) and 3,500,000+ (`local`),
   re-tuning 4,000,000+ and 4,500,000+; check no test instance was used in training, validation or tuning.
4. **Fairness.** That the re-tuned comparators searched the stated neighbourhoods; that the grid widening before training
   (recorded) only enlarged the hand-written side's choices; that caps were identical across arms in each cell.
5. **Prior work.** Run `python3 -B scripts/track.py objects-gate research/WHERE-NEXT-20261116-001/preregistration.md` (its
   "Prior work in the program" section), one search of its own in other words, and a literature check of the claim that no
   learned violated-clause selection with memory has been compared at charged cost with re-tuned rules.
6. **Words.** The notes use the glossary's words (distinction, knot, meeting pattern, overlap); flag any spatial word used for
   the program's own objects.

## Final report as sent

2026-11-16 23:53 UTC, in the project thread:

> **Result: your agent's memory works and is learnable, but what it learned doesn't carry over to bigger or different patterns
> yet. By the rule I froze in advance, that is a clean loss at scale.**
>
> On the sizes it trained on, the agent with memory needed about half the flips of the best hand-written rule, Novelty+. Without
> memory, the same agent was 2.7 to 3.3 times worse. At 4 times its training size it only tied Novelty+. At 16 times, and on the
> local pattern it never saw, it lost. Each of its steps also costs 4 to 8 times more computing, so it never saved time. Learning
> where to go next added little.
>
> (Position table, next-directions table, Corrections, Goals and Assumptions lines as in this note; next step: Continue, selected
> #1, memory that doesn't count steps, starting next.)
>
> My guess about why it doesn't transfer: its memory counts steps, and at larger sizes the same number of steps means something
> different. Novelty+'s memory only compares which distinction was flipped most recently, which works at any size. That's what #1
> tests.

**Correction to the report as sent (2026-11-17, referee R1, logged in `docs/CORRECTIONS.md`).** "About half the flips" at the
training sizes should read "about 0.7 to 0.8 times the flips (1.3 to 1.4 times fewer)" on the referee's five-run estimates
against a widely re-tuned Novelty+ (Narrowing); the loss at scale is scoped to memory reads counted in steps, trained at n ≤ 800
(Narrowing, wording). The primary-cell loss is firmer (R = 1.10 [1.02, 1.19]); P2 would narrowly have held (Not a block).
