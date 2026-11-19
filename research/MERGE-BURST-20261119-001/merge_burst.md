# What explosive starts do after their merge

Epic `MERGE-BURST-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `EXPLOSIVE-20261119-001#1`. Goal G17.
It is framed by A110: blow-up is expected, and the question is what a sample of the explosive kind typically does. **Referee
pending.**

**Record.**
- **Pre-registration:** [preregistration.md](preregistration.md), frozen in commit `c75c3199d` after a pilot on the closed case
  (disclosed).
- **The run:** the shared runner (`MERGE-BURST-B1`, `runs/merge-burst`, 16 cases, all ok). Each start ran in its own child, limited
  to 6 GB and 15 minutes.
- **Code:** [mblib.py, job.py, merge.py](../../experiments/MERGE-BURST-20261119-001B/MERGE-BURST-20261119-001B-E001_stages/).
- **Results:** [results.json](../../artifacts/MERGE-BURST-20261119-001B/MERGE-BURST-20261119-001B-E001_stages/results.json).
- **The advisor** checked the design before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **Of the 15 stopped explosive starts, one more ends, and the other 14 could not be followed far enough.** None was shown to keep
  growing.
- **The one that ends** has six knots of 6, 6, 4, 7, 6 and 3 places.
  - In round 8 a single group of 974 parents merges almost everything, leaving 781 live junctions that all lie in one block.
  - From there the growth is that block's: every subset of the 781 joins exactly once.
  - That is C(781, 2) = 304,590 junctions in the next round, then 79,091,870, and so on.
  - It closes after 780 more rounds, having made about 2⁷⁸¹ junctions.
  - So it does not grow without bound, but its burst is finite only in the strict sense. The engine ran out of memory before it
    could grow even the first of those rounds, so this reading is computed, not checked by growth.
- **The other 14 never reach a stage that can be read.** Every one stopped by round 5 to 8 (10 by memory, 4 by time), with groups of
  12 to 446 parents.
  - At every stage the reduced map still has two maximal blocks sharing two knots, so it is outside even the reduced class.
  - The growth keeps building overlapping groups faster than they merge.
  - None of them had a merge event yet.
- **The control**, the closed case, reads and checks exactly: one block of 9, then 36, 84, 126, 126, 84, 36, 9 and 1 junctions.
- **"Explosive" means a ×3 jump in the counts seen before a stop** (EXPLOSIVE's referee R1), not growth without bound.
- **What a sample of the kind does, so far.**
  - Of 16 explosive starts, 2 are read, and both end after one merge and a binomial burst of one block, one of 9 junctions and one
    of 781.
  - 14 are unread within the limits.
  - The sample is EXPLOSIVE's, under its weighting. Nothing here generalises to the kind.
- **What is proved, what is computed, what is open.**
  - **Proved (refereed):** the stage identity and the branch system.
  - **The study's hypothesis, shared by both readings:** a block equal to or inside another changes nothing. The control's
    growth supports it; there is no proof yet.
  - **Computed on that hypothesis:** start-04's reading.
  - **Open:** the 14.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| R1 | the branch system's count equals every grown check round | **held** | the control, 8 of 8 rounds; start-04 read but unchecked (0 rounds; the engine's memory) |
| R2a | every first reading is a single maximal block | **held** | 2 of 2 (blocks of 9 and 781) |
| R2b | (risky) every start that reaches a reading closes | **held** | 2 of 2 |
| R3 | at least 5 of the 15 reach a reading | **failed** | 1 of 15 |
| R4 | where the next stage is in the reduced class, its reading agrees | **held (vacuous)** | no next stage was in the class: after the control's burst round its 36 pairs form cycles of three blocks |

4 of 5 held. R3's failure is the finding: the reading reaches almost none of the kind within these limits. R2a and R2b rest on two
readings.

## Assumptions

- **A110** gets a history line: two of 16 explosive starts are read, both finite after one merge, and 14 are unread within 6 GB
  and 15 minutes. Status unchanged.
- **A109** gets a history line: the explosive kind is not yet catalogued. Status Under challenge.
- **A new entry is not added.** The reduction is stated in the pre-registration as this study's hypothesis, and direction 2 below
  is to prove it.

## Known results, and what this adds

- **Known.** A complete block of m points has C(m, k) connected sets of size k (the Boolean lattice).
- **What this adds.** Two explosive starts read to their end through one merge, and the reduction to maximal blocks as the way in.
  It also locates the wall: overlapping groups that keep two maximal blocks sharing two knots.

## Limitations

- **The limits.** 6 GB and 15 minutes per start. The 14 unread may end, repeat or keep growing; nothing here decides which.
- **Start-04** is read on the reduction hypothesis and was not checked by growth.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze.
- **It sketched** the reduction's proof and named relays as its weak point.
- **It guessed** about 6 of 15 would be read. One was.
- **It tightened** R1 to R4. Its suggested engine-against-engine check was not adopted, because a reduced map is not a presentation.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: merge and burst | **Status:** Partially successful (4 of 5 held; R3 failed) | One more start ends, after a 974-parent merge and the burst of a 781-point block; 14 unread within the limits; none shown to keep growing |
| Local direction: the explosive kind (A109) | Research directions | The way in, reading from a reduced stage, works only once the overlapping groups have merged; most starts do not get there within reach |
| Broader exploration: what the cheapest growth builds | Known alternatives | Within five places, classified; past it, explosive starts that merge then burst, and many not yet readable |
| Long-term goal: G17 | Capability gained | What a sample of the explosive kind does, read where it can be, with the wall located |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A reading past the wall: the cover where maximal blocks share two knots (the case DOUBLE-IDENT excludes) | 3/3 — it would read the 14 | 1/3 — the tree-of-blocks cover is the wrong object there | find the right complex on the smallest unread start (start-03, six knots, round 7) → stop at one that predicts its next round, or a proof that none can | Alternative · proposed |
| 2 | Prove the reduction: blocks equal to or inside another change nothing | 2/3 — it makes the two readings proved | 3/3 — the advisor's sketch, with relays the one gap | write the round-1 and induction steps → stop at a proof, or a start where a contained block matters | Alternative · proposed |
| 3 | Prove the 2.3830 ceiling within five places | 2/3 | 2/3 | bound every branch system by the theta's → stop at a proof, or a start that beats it | Alternative · in the basket |

## Final report as sent (2026-11-19 19:07 UTC)

**Outcome:** Of the 15 stopped explosive starts, one more ends after a single merge and a burst. The other 14 couldn't be followed far enough, and none was shown to keep growing. In sampling terms: of the 16 explosive starts, the 2 that could be read both end the same way, one merge then the burst of one block, and 14 are unread. That's a sample under EXPLOSIVE's weighting; I'm not generalising from it. 4 of 5 frozen predictions held. Closed, referee pending.

- **How I read them.** I followed each start round by round in its own 6 GB, 15-minute process. After each round I reduced the stage's map to its largest blocks; blocks equal to or inside another add nothing. Once that reduced stage sat back in the proved class, the branch system counts the rest exactly, without building it.
- **The one that ends.** Six knots of 6, 6, 4, 7, 6 and 3 places.
  - In round 8 a group of 974 parents merges it into one block of 781 junctions.
  - From there every subset of the 781 joins once: 304,590 junctions next round, then 79 million, and so on.
  - It closes after 780 more rounds, about 2⁷⁸¹ junctions in all. That's finite, but only in the strict sense. The engine couldn't build even the next round, so this reading is computed, not checked by growth.
- **The control**, the case already closed, reads and checks exactly: a block of 9, then the burst 36, 84, 126, 126, 84, 36, 9, 1.
- **The 14 that couldn't be read** all stopped by round 5 to 8, 10 by memory and 4 by time, with groups of 12 to 446 parents. At every stage, two of their largest blocks still share two knots, which no current reading covers. None had a giant merge yet.
- **What's proved, computed, open.**
  - Proved and refereed: the stage identity and the branch system.
  - The study's hypothesis, which both readings rest on: equal or contained blocks change nothing. It's sketched by the advisor and supported by the control's growth, but not yet proved.
  - Computed on it: the 781-block reading.
  - Open: the 14.
- **The miss (R3).** I predicted at least 5 of 15 would become readable; only 1 did. That is the finding: the explosive kind mostly stays past the wall within these limits.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: merge and burst | **Status:** Partially successful (4 of 5 held; R3 failed) | One more start ends after a 974-parent merge and the burst of a 781-point block; 14 unread within the limits; none shown to keep growing |
| Local direction: the explosive kind (A109) | Research directions | Reading from a reduced stage works once groups have merged; most starts don't get there within reach |
| Broader exploration: what the cheapest growth builds | Known alternatives | Within five places, classified; past it, merge then burst where read, and a wall where maximal blocks share two knots |
| Long-term goal: G17 | Capability gained | What a sample of the explosive kind does, read where possible, with the wall located |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A reading past the wall, where maximal blocks share two knots (the case DOUBLE-IDENT excludes) | 3/3 | 1/3 | find the right complex on the smallest unread start (six knots, round 7) → stop at one that predicts its next round, or a proof none can | Alternative · proposed |
| 2 | Prove the reduction: equal or contained blocks change nothing | 2/3 | 3/3 | write the round-1 and induction steps, with relays the one gap → stop at a proof, or a start where a contained block matters | Alternative · proposed |
| 3 | Prove the 2.3830 ceiling within five places | 2/3 | 2/3 | bound every branch system by the theta's → stop at a proof, or a start that beats it | Alternative · in the basket |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A110 and A109 get history lines, both status unchanged. The reduction is recorded as this study's hypothesis in the pre-registration, not as a register entry, since direction 2 would prove it. **Basket:** `EXPLOSIVE-20261119-001#1` taken. **Advisor:** Fable 5.2, before the freeze, staying within its text. It sketched the reduction's proof, naming relays as the gap. It tightened R1–R4 (minimum checked rounds, split R2, a floor on merge events, a stability read). Its guess of about 6 readable of 15 was too high; 1 was. I didn't adopt its engine-against-engine check, because a reduced map isn't a presentation.

**Referee hand-off.** The decision note is `research/MERGE-BURST-20261119-001/merge_burst.md` and the code is `experiments/MERGE-BURST-20261119-001B/MERGE-BURST-20261119-001B-E001_stages/`. Please check:
- the reduction (`mblib.reduced`): equal and contained blocks dropped, and the class read on the maximal blocks;
- start-04's reading, a single 781-point block at round 8;
- that the 14 unread really fail on two maximal blocks sharing two knots, not on a reading slip.
