# How often does ordinary growth make the four-clause step one layer up? What stands


> **Referee R1: confirmed with fixes, no Block** ([report](referee-R1/report.md)). The count reproduces: 1 of 408 under the
> cap. Searching the 211 omitted stages adds two (the second rounds of census starts 2439 and 3777, 14 patterns each):
> 3 of 426 funded starts (0.70%), 3 of 600 sampled (0.50%). **The explanation (the referee's finding, replayed by the
> thread, `post/chain_replay.py`):** the three positive stages are exactly those with a chain of eight three-place knots
> (consecutive knots sharing one distinction, no other pair sharing). A bare chain of eight three-place knots, with no
> ring and no growth, carries one pattern and three steps with every law needed; a chain of seven carries none; a chain
> of nine carries six. **Narrowings:** another assignment of the four clauses (one member of the "both" pair used three
> times) adds four steps on census start 426, round 2; the cap counted distinctions, not bonds; F3 met its threshold on
> one pattern only; persistence is guaranteed by the projection argument, so selection means "does growth distinguish
> competing readings". Credit: the four-clause form and its first witness are the earlier referee's.

`FOUR-CLAUSE-20261127-001`. Frozen in commit 59177ac458. Results are in `out/`. Referee pending.

**Answer: rarely, under the census weighting, on the stages read.** 600 held-out census starts were read at rounds 0
to 2, with the full search on stages of at most 19 distinctions.

| | Count |
| --- | --- |
| Starts | 600 |
| Starts with a grown stage read (round 1 or 2) | 408 |
| Stages read: round 0, 1, 2 | 600, 408, 233 |
| Stages not read, over 19 distinctions: round 1, 2 | 18, 193 |
| Originally read stages with the frozen alternating pattern | 1 (census start 5260, round 2) [R1: 3 of 426 funded starts with the omitted stages] |
| Steps (proper, free in pairs, not read at one lower bond) | 3, the three readings of that one pattern, all with a birth needed |

- **F1 held:** no step at round 0.
- **F2 failed:** 1 of 408 starts (0.25%) has a step with a birth needed, against a predicted 5% or more.
- **F3 held:** all 3 steps have seven upper words.

**The sampled step.** Census start 5260 has five knots, one of them with seven places. Ordinary growth gives nine knots
by round 2. Its six agreements are [2 = 8 = 10], [7 = 13], [0 = 1 = 5], [9 = 12 = 14], [3 = 4 = 11] and [6 = 15 = 16],
and they take four clauses. Each of the three readings of the pattern misses one upper word. Every law is needed except
the seven-place knot's, and all four births are needed.

**Reading.** Ordinary growth makes the step one layer up on sampled starts, not only on built ones:
- census start 420, found by the referee;
- census start 5260, found here;
- 1 of 408 under the census weighting, on stages of at most 19 distinctions through round 2.

Most of the larger round-2 stages, 193 of them, are not read. They have the most bonds, so the frequency there may
differ. That part is not run.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the four-clause step's frequency | **Status:** STOP (F1, F3 held; F2 failed) | 1 of 408 sampled starts, all births needed |
| Local direction: the step one layer up made by growth | Reached on sampled starts, rarely | Two sampled starts (420, 5260) and one built start; selection of readings open |
| Long-term goal: G17 with G18 | Advanced | The tower's next step is made by ordinary growth from sampled starts |

**Next step:** Research directions (the coordinator's call).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The larger round-2 and round-3 stages the cap left out, with a faster search restricted to readings on born distinctions (the projection argument makes it exact) | 3/3 | 2/3 | Time one 23-distinction stage; read the 193 → the frequency where bonds are many | Proposed |
| 2 | Does the step repeat: a third layer on the grown stages that carry the step | 3/3 | 1/3 | On census 420 and 5260, grow two more rounds and search upper patterns among upper readings → one, or none at a stated size | Proposed |
| 3 | Selection: on 420 and 5260 (no symmetry assumed), do some patterns persist or vanish with further rounds? | 2/3 | 3/3 | Grow each two more rounds; track each pattern → a rule, or none | Proposed |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** none added (A308, A309 cover the readings and the form; the four-clause form is the referee's).
**Scaffolds:**
- The four-clause form, not swapped against the box form here.
- The 19-distinction cap. It left out 211 grown stages, which are not run.
- The 60-pattern cap, never reached.

**Advisor:** not consulted (usage limit).
