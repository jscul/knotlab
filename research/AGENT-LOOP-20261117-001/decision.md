# Decision: AGENT-LOOP-20261117-001

2026-11-17 · goals G15, G16 · takes sub-goal B191 (`SPEC-MERGE-20261117-001#1`, the coordinator's go-ahead) · computed, referee
pending · result note [agent_loop.md](agent_loop.md) · pre-registration [preregistration.md](preregistration.md) (frozen
`cf3982921`)

**Headline.** The learned agent was run as the fast loop under the proof-based slow loop, with its memory carried across every
change of the pattern.
- **Carrying the memory made no difference.** Against restarting, carried memory was 0.99 to 1.01 on local patterns and 0.89 to
  1.02 on block patterns, every interval reaching 1. That held where half to nine tenths of the search came after the first change.
- **On local patterns the slow loop helps the agent enormously,** cutting its flips to 0.02 to 0.06 and its charged work to 0.07
  to 0.18. But there the loop does nearly all the work: alone, it shrinks 3,200 distinctions to about 100 to 200 classes. Then the
  agent finishes in the same number of flips as Novelty+ (0.98 to 1.00), at 1.4 to 1.75 times the work.
- **On block patterns the agent is the better searcher** (0.51 to 0.65 of Novelty+'s flips under the same loop). That lead is its
  own, and the loop adds little to it on the cell never run before (0.83 to 0.85, short of the frozen 0.8) while raising its work.
- **The frozen verdicts:**
  - memory, "no difference shown" on both families;
  - loop, reading 4 on local (the loop helps the agent; the agent adds nothing over Novelty+ under it);
  - loop, reading 5 on block (the agent beats Novelty+ under the loop in flips; the loop does not help the agent).
- **As said up front,** no charged-time win over Novelty+ under the same loop: 1.9 to 3.8 times its CPU. No `rand` cell won.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the learned agent under the proof-based slow loop, memory carried or restarted | **Status:** Failed (no mechanism gain beyond the parts) | Memory: no difference shown; loop: reading 4 on local, 5 on block; every state checked |
| Local direction: B191, the slow loop that changes the knot pattern (four studies) | Practically exhausted in this form; paused for the stock-take | Structure changes pay only where proofs find structure, and there any fast loop finishes equally |
| Broader exploration: learned local search with inprocessing | Known alternatives | Failed-literal probing, equivalent-literal substitution and inprocessing scheduling cover the line's moves; CaDiCaL solves these patterns in 0.05 s |
| G15 Learning: a point in a learned knot pattern, and G16 Learning the rules behind what a system allows | Obstruction learned | A learned agent's memory survives a change of the pattern without harm and without use; its lead and the loop's do not compound |

Under the table:
- **What the attempt leaves unresolved.** Whether a learner trained through changes would use carried memory. Dr never saw a
  rebuild in training, and the carry rule is one of many.
- **What the retired form keeps.** The slow loop's local-pattern wins, the agent's block-pattern lead, and the gates and driver.
- **The bridge to G15** that is missing: a learned point whose memory does work after its pattern changes.

**Next step:** Research directions — selected: #1 (awaiting go-ahead; the line stops here for the stock-take with John)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Train the agent through changes: learning episodes run under the slow loop, with carried memory | 2/3 — the one untested part of the owner's picture: a learner that learns to use memory across a change | 2/3 — MEET-TRANSFER's trainer, SIGNED-NAV's handle and this driver exist; several CPU-hours of training | Train on `block` 2.5 at n = 800 with the loop's rebuilds in every episode, then carry against restart on `block` w40 at 3,200, five runs, both seeds → stop if carry/restart stays within 0.9 to 1.1 | Selected · awaiting go-ahead |
| 2 | Read what the slow loop leaves: the 100 to 200 class remainder of a local pattern | 2/3 — ties the owner's "untangling" back to the program's own objects | 1/3 — no measure chosen yet for what a remainder is | Dump the remainders of 10 `local` w30 instances, and compare their meeting counts and density with planted `rand` patterns of that size → stop if they look like random patterns | Alternative · deferred |
| 3 | Small, high-precision speculative rounds with a check per merge, where proofs find nothing | 1/3 — the referee's open corner (precision 0.98 on `rand` 3.0); a win would be small, since search there is easy | 3/3 — the evidence, the pair probe and SPEC-MERGE's driver exist | Rounds of 4 to 16 merges, each checked by a bounded pair probe, only when stuck, on `rand` 3.0 at 3,200 → stop if R stays above 1 | Alternative · deferred |
| 4 | Full pivot: pause B191 and return to the idle goals | not rated — a choice for the stock-take | — | The coordinator's portfolio review with John | Alternative · deferred |

Ratings.
- **#1** is the most direct remaining test of the metacognition picture. This study shows the carry rule does no harm, so a
  learner can be trained with it. Its main uncertainty is whether any memory can matter when the loop leaves a small remainder
  (local) or proves little (block).
  - **Bound:** one training run and one test like this one, about 3 to 5 CPU-hours.
  - **Done so far:** nothing beyond this study.
- **#2** turns the line toward the program's own questions, but it has no well-posed measure yet.
- **#3** closes the one corner SPEC-MERGE left open, for a small prize.
- **#4** is the stock-take's own option.

**Corrections:** none to earlier claims. Two departures from this study's frozen text are listed in the note: the prior-work
cut-off, rerun with the freeze date, and the epic names. Check C2 failed: `local` w30 had room.
- **Folded in during this study (7eddc5dcf):** SPEC-MERGE's referee, five entries in `docs/CORRECTIONS.md` (three Narrowings, two
  Not a block).

**Goals:** checkpoint row added (G15, G16; obstruction learned); G15's Stands on and Open updated; B191 marked paused for the
stock-take; no goal changed.

**Assumptions:** added two, both Assumed:
- A94: an agent's memory across a change of the pattern is SIGNED-NAV's carry rule. Carry equalled restart here, which tests only
  this rule.
- A95: flips are read under the same proofs per flip and charged work under the same share of work on proofs.

Relied on A90 and A91.

**Advisor:** Fable 5.2 reviewed the second draft and said "freeze with changes". Its twelve points were taken, one in part (the
statistic kept as the line's convention) ([advisor_review.md](advisor_review.md)). It was not used after the results.

**Referee:** pending; hand-off below.

## The line, for the stock-take

Sub-goal B191 asks whether a slow loop that changes the knot pattern under a fast search cuts the search's work (the owner's
metacognition idea of 2026-11-16, "braids and untangles"). Four studies ran on 2026-11-17, all on planted not-all-equal patterns,
computed, with both loops charged.

| Study | Question | Result | Refereed |
| --- | --- | --- | --- |
| `SLOW-LOOP-20261117-001` | Do structure changes that keep the allowed states (proved ties, implied knots), applied between runs of Novelty+, cut the total work? | Yes on local patterns when eager (0.24 to 0.30 and 0.46 to 0.60 fully charged, CPU wins), no on random and block (1.5 to 2.1 times); the search's attention is no guide to where to probe | yes, with fixes |
| `EARN-BUDGET-20261117-001` | Can the loop earn its eagerness from what its changes remove? | Safe (3% where nothing is found) and a win on an untouched local pattern (0.56; 0.18 at 12,800), but 3 to 4 times short of the best fixed setting per pattern, because it ramps too slowly | yes, wording only |
| `SPEC-MERGE-20261117-001` | Can unproved changes, chosen from the search's own co-flip evidence, pay? | No. The evidence is real (about 0.1 above random pairs; tied 2.5 times as often on local), but unproved merges never paid. Only the check for contradictions filtered wrong ones; undoing on a stall was blind | yes, with fixes |
| `AGENT-LOOP-20261117-001` (this) | Does the learned agent, with memory carried across changes, make the two loops worth more than their parts? | No. Memory makes no difference; the loop helps the agent on local patterns, where any search then finishes equally; the agent's lead on block patterns is its own | pending |

**What the line established.**
1. **Changing the pattern by proved ties pays exactly where propagation proves many ties.** Those are the local patterns, where
   the slow loop alone shrinks 3,200 distinctions to about 100 to 200 classes. On random patterns near the threshold it proves
   nothing, and its probing is pure cost.
2. **Where it pays, the fast loop hardly matters.** Novelty+ and the learned agent finish the remainder in the same flips, and the
   cheaper fast loop wins in work.
3. **Unproved changes need a check of their own.** The search's progress after a change is no such check.
4. **A learned agent's memory can be carried through a change of the pattern without harm, but here without use.**
5. **The agent's lead on hard-to-search patterns is its own.** The loop neither creates it nor multiplies it.

**What is known mathematics.**
- **The moves are classical:**
  - failed-literal probing;
  - equivalent-literal substitution;
  - the implied knots, which are learned or resolvent clauses.
- **Scheduling them by yield** is the inprocessing of Lingeling and CaDiCaL (Järvisalo, Heule and Biere 2012).
- **The neighbours of the speculative moves** are multilevel refinement (Walshaw 2002), backbone-guided local search (Zhang 2004)
  and survey-propagation decimation.
- **CaDiCaL** solves the local patterns in about 0.05 s.
- **What is the program's own:**
  - the reading of the owner's slow loop (A90);
  - charging both loops in one count (A91);
  - the measurements;
  - carrying a learned agent's memory through a substitution, which the program did not find measured in the literature.

  None of it goes beyond what an inprocessing solver does.

**What I would do next.**
- **If the line continues,** train the agent through changes (#1). It is the one part of the owner's picture not yet tested, and
  this study shows the carry rule is safe to train with.
- **If it does not,** the line's results stand as a measured account of when a structure-changing loop pays. Then I would pause
  B191 and return to the idle goals (#4).
- **I would not run** more variants of the slow loop itself. Four studies found the same boundary, that proofs pay where
  propagation finds structure, and a further variant is unlikely to move it.

## Referee hand-off

1. **The gates.** Rerun `check.py` (A1–A4), and read `agent_loop.py`:
   - the two budget rules and the slow loop alone;
   - the carry and restart paths at a rebuild;
   - the charge of the carry's mapping and the new handles;
   - the mapping back to the original distinctions.

   Check that the loop never reads the planted state (only the A2 gate does), and that every reported state is checked on the
   original knots.
2. **The headline,** recomputed from `test/`:
   - M1 to M4 per seed and cell, the room per cell and budget, and the family verdicts;
   - the two frozen verdicts;
   - R against F, with the capped-run rule;
   - the `rand` identity (500 of 500).
3. **Fairness.**
   - **The budgets.** Is the per-flip budget (3 × 50 incidences per flip) a fair matched-proof comparison, and is EARN-BUDGET's
     rule fair in work?
   - **The agent's charge.** Is its work, its engine's incidence count with reads included, comparable to Novelty+'s?
   - **Seeds.** Do the agent alone and every arm start from the same initial states? The note says they do, checked on 5 seeds.
4. **M4 in work.** Check the reading that it measures the dilution of a bounded probing cost (it passes on `rand`, where nothing is
   proved).
5. **The calibration disclosure.** Check that the first cells (`local` w30, `block` w40) were not run before `cf3982921`, and that
   the predictions and checks are scored as frozen.
6. **Prior work.** Rerun `track.py objects-gate research/AGENT-LOOP-20261117-001/preregistration.md` with the freeze date, and
   search for memory transfer of learned local search under problem reformulation.
