# The fold studies: what was measured, and what is still untested

Recorded 2026-11-16 · **Line open** · root `FOLD-TRANSFER-20261114-001` and its 21 descendant studies · goals G15, G16 ·
evidence: computed (finite experiments), each replayed by a Codex sub-agent audit, **not refereed**.

## What the line asked

The line grew out of the owner's question of 2026-11-15 about publication risk and faster self-improvement of learning systems,
and his idea of logic that "folds upward" by compression. It asked two things. Can a local learner find a fold, a compression that
keeps exactly what a later reader needs? And does reusing a learned fold make learning the next rule cheaper, once the fold's own
training and the checking of every returned program are paid for?

## What was measured

**The first answer is yes on small tasks.** Frozen learners chose the fewest bits a later reader needed and changed that choice
correctly when the wiring changed; a learned selector picked programs that generalize far more often than "keep the shortest".
**On the second, the total-cost comparison was negative at the sizes tried.** In every study that charged training and checking,
the learned or supplied fold lost to, or tied, an ordinary solver that searches primitive gates and caches its work, on tasks of
3 to 9 inputs where exact search is nearly free. That matches the earlier learning line, where none of 91 learned cases found its
target faster than blind draws ([learning line](../LEARN-NOTE-20261110-001/learning_line.md)), and it is a statement about these
sizes, not about the idea.

## What these studies did not test

The owner's idea is an agent that reads the context at a logical knot, learns to move between knots and act on their loops, keeps
a memory of the steps it has taken (for example with a sequence model), treats moving to a knot as activating it, and mutates the
knot structures to improve results; the reversible moves ("braids" and "untangling") are ways of building that structure. None of
the 22 studies tested this:

- **Choosing where to go.** Only `LOCAL-RULE-ACTIONS` had an agent, a tabular Q-learner at a fixed starting position on a chain of
  three to five signed rules, choosing when to fold its neighbours; moving its point of view was left open. In `STRAND-RETURN` and
  `WIRED-FOLD` the order and movement rules were supplied, and a supplied interpreter decided which records to visit.
- **Memory of earlier steps.** No policy saw its own history; each acted on its current local view.
- **Mutating structures.** `ATOMIC-FOLD` mutated whole programs of Boolean gates, not knot structures.
- **Knots.** The objects were Boolean rules, circuits and truth tables; no study stated its objects as relations and checked them
  with `knotlab check` (K1–K3).

That question stays open, and is the line's main direction.

## The studies

| Study | Class | Result |
| --- | --- | --- |
| [`FOLD-TRANSFER-20261114-001`](transfer.md) | supported | Keeping both local reads identified all 28 joined targets; a plain table learner over the same candidates matched every query. |
| [`LOCAL-RULE-ACTIONS-20261114-001`](../LOCAL-RULE-ACTIONS-20261114-001/local_agent.md) | supported | Sight and action reach both matter; a policy fitted on three-rule chains solved all longer starts given a supplied cue; a hand-written policy tied. |
| [`ATOMIC-FOLD-20261114-001`](../ATOMIC-FOLD-20261114-001/atomic_folds.md) | supported | Reward-guided search was no better than blind (2/18 against 5/18); whole-program mutation found an exact two-bit fold in 18/18 against 5/18. |
| [`WIRED-FOLD-20261114-001`](../WIRED-FOLD-20261114-001/frozen_policy.md) | supported | One frozen policy followed every rewiring; 54,144/55,296 answers, all errors on two unfamiliar menus where it kept too few bits. |
| [`STRAND-RETURN-20261114-001`](../STRAND-RETURN-20261114-001/strand_returns.md) | supported | Two systems with the same separate value lists give opposite answers after the inverse move; a reader that may still undo needs two bits. |
| [`BRAID-ACTIONS-20261114-001`](../BRAID-ACTIONS-20261114-001/braid_actions.md) | supported | Atomic programs learned a reversible move and its inverse; the frozen reader answered 2,792,448/2,792,448 reads and used minimum width on 605/606 wirings. |
| [`BRAID-REUSE-20261114-001`](../BRAID-REUSE-20261114-001/transfer.md) | supported | Reusing the move took 3.8% fewer candidates but 27.6% more gate work; every training-selected program scored 3/9 on new inputs. |
| [`RENAME-SELECT-20261114-001`](../RENAME-SELECT-20261114-001/selection.md) | supported | Learned renaming evidence chose an exact program in 52/60 pools against 27/60 for shortest; with the move, 37% more work per correct return. |
| [`BIT-DECODER-20261114-001`](../BIT-DECODER-20261114-001/decoder.md) | supported | A frozen NAND decoder answered all 344,064 held questions; its sender reached the minimum on 150/168 wirings. |
| [`GROUP-SENDER-20261115-001`](../GROUP-SENDER-20261115-001/group_sender.md) | supported | Switching groups of questions together took six-bit cases to four; 80/96 minima, 92/96 with a second learned rule. |
| [`ANSWER-COMPOSE-20261115-001`](../ANSWER-COMPOSE-20261115-001/answer_composition.md) | supported | Three bits where three suffice and four where four are needed, on every layout; a cached lookup compiler still cost less at all 20 operating points. |
| [`FOLD-REUSE-20261115-001`](../FOLD-REUSE-20261115-001/fold_reuse.md) | obstructed | The fold cut checks from 136 to 129 but took 11.243 s with its acquisition against 0.101 s without it. |
| [`FOLD-GATE-20261115-001`](../FOLD-GATE-20261115-001/gated_stream.md) | refuted | Over 32,768 held rules, 31.065 s against 12.403 s; no break-even at any point. |
| [`FOLD-DEPTH-20261115-001`](../FOLD-DEPTH-20261115-001/scaling.md) | supported | A supplied fold saved trials at depths three and four on recurring rules, and none when the input count was held at nine. |
| [`FOLD-DISCOVERY-20261115-001`](../FOLD-DISCOVERY-20261115-001/transfer.md) | refuted | The learned fold cost 63.1 ms on 24 unseen rules against 21.5 ms for cached primitives. |
| [`FOLD-PLACEMENT-20261115-001`](../FOLD-PLACEMENT-20261115-001/placement.md) | supported | A hint naming the right three inputs cut tests from 1,842 to 739, for primitives and fold alike. |
| [`FOLD-PAIR-PLACE-20261115-001`](../FOLD-PAIR-PLACE-20261115-001/pair_placement.md) | refuted | Blind search found all 168 fold uses but took 128.8 ms against 123.4 ms, losing all eight paired runs. |
| [`FOLD-TWO-OUTPUT-20261115-001`](../FOLD-TWO-OUTPUT-20261115-001/two_outputs.md) | refuted | Two output tables showed when one shared bit suffices; the fold took 106.8 ms against 99.8 ms. |
| [`TRIPLE-ORDER-20261115-001`](../TRIPLE-ORDER-20261115-001/triple_order.md) | refuted | A learned ordering found the right triple first more often but cost 594.8 ms with training against 291.6 ms. |
| [`PROBE-WITNESS-20261115-001`](../PROBE-WITNESS-20261115-001/local_witnesses.md) | refuted | Short local certificates were exact and reusable, at 442.4 ms against 304.8 ms. |
| [`PARENT-FOLD-20261115-001`](../PARENT-FOLD-20261115-001/parent_fold.md) | refuted | After a consumer edit, the fold tied ordinary repair: 398.4 ms against 397.0 ms, four wins in eight. |
| [`PAIR-PROOF-20261115-001`](../PAIR-PROOF-20261115-001/shared_proofs.md) | refuted | A frozen local policy was exact on 72 new edits but took 4.995 s with training against 0.477 s. |

## Limits of the evidence

- **Size.** Every task had 3 to 9 inputs, so at most 512 input assignments. Exact primitive search returns a verified program in
  fractions of a second at these sizes, which leaves a learner almost nothing to save. The line says nothing about sizes where
  plain search is expensive.
- **Pieces supplied by hand.** The reversible move reused in `BRAID-REUSE` and `RENAME-SELECT`, the wiring format, the search that
  tried learned operations in pairs (`ANSWER-COMPOSE`), the exact test of what must be kept and the circuit builder (from
  `FOLD-TWO-OUTPUT` on), and the original wire in `PARENT-FOLD`'s generous hint were given, not learned.
- **Review.** Each study's audit (its `audit.json`) is a replay by a Codex sub-agent. No study has a referee report, and the advisor
  model was not consulted.
- **Timing.** Costs are CPU on a shared host. The small gaps (`PARENT-FOLD`'s tie, `FOLD-TWO-OUTPUT`'s 7%) are within run-to-run
  variation; the large ones (`FOLD-GATE`, `FOLD-DISCOVERY`, `TRIPLE-ORDER`, `PAIR-PROOF`) are not.
- **Words.** The studies call a reversible relabelling of two three-valued distinctions, and its inverse, a "braid", "crossing",
  "strand" and "untangling". Those are drawing words under the program's word rule; the study records keep them as names, and this
  note means only the relabelling.
- **Publication risk.** No result here gives a learning method that saves total work at these sizes, so nothing changes the
  low-risk reading of the owner's 2026-11-15 question.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: reusing folds at 3 to 9 inputs | Measured | Minimal widths and rewiring learned; every paid comparison with plain search lost or tied. |
| Local direction: an agent that moves between knots | Open | Untested: no study let the agent choose where to go, remember its steps or mutate knot structures. |
| Learned folds where plain search is costly | Open | Untested; the only sizes where a fold could pay for itself. |

**Next step: Research directions.** Keep the line open, with the navigating agent first.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One paid fold test where plain search is expensive | 2/3 | 1/3 | Choose a rule family where cached primitive search takes seconds per rule, then rerun `FOLD-GATE`'s paid protocol → reassess if the fold loses again | Open |
| 2 | An agent that moves between knots, with memory of its steps and mutation of knot structures | 2/3 | 2/3 | State one knot network as K1–K3 relations, let a policy with its step history choose which knot to act on next, against a fixed-schedule baseline → reassess at the first paid comparison | Open |

**Corrections:** none to these studies; the published `BRAID-READOUT-20261114-001` decision linked to `STRAND-RETURN`, which was
unpublished until this commit (logged in `docs/CORRECTIONS.md`). **Goals:** G15 and G16, obstruction learned; checkpoint row
added. **Assumptions:** none added or changed. **Advisor:** not used.
