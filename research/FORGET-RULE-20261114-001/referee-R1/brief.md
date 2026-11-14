# Referee brief FORGET-RULE-R1 (from the coordinator, 2026-11-14, Codex-assisted)

**The epic.** `FORGET-RULE-20261114-001`: commits e75be4409 (split freeze), 4a37c96d4 (rules and held-out predictions) and 5b8f91852
(result). It is the thread's own code, so the recheck uses fresh code.

**Claims.**
- **Rule N, proved necessary.** An identity cycle blocks forgetting.
- **Rule A, proved sufficient.** Separation in the peeled layered composite, decided by a finite automaton, with the free-from-above
  flag and a generic start.
- **Held out.** 0 violations; A covers 36.7%; with no identity cycle, 2,096 of 2,096 chains and 93.6% of non-chains forget.
- **Rule D** is refuted by a gadget.

**The owner's points.**
- (1) A's soundness, especially the free-from-above flag and climbing paths.
- (2) The several-definition premise.
- (3) The generic-start fix before the held-out read.

**The coordinator's point.**
- (4) A brute-force counterexample search outside the census.
