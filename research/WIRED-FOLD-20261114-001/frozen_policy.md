# One frozen policy follows rewiring and sometimes folds too soon

Tested November 14, 2026 (Pacific). In this finite experiment the learned scan correctly located whichever two of four source rules fed the downstream reader. The one frozen encoder and decoder answered 54,144 of 55,296 questions (97.92%). Every error arose when the reader could ask either “does 1 survive?” or “does any value survive?” in either port order. The encoder sent one bit there. Those two questions have three possible joint answers and require two fixed payload bits. [Saved parameters](../../artifacts/WIRED-FOLD-20261114-001/WIRED-FOLD-20261114-001-E001_frozen_policy/checkpoint.json) · [Independent verification](../../artifacts/WIRED-FOLD-20261114-001/WIRED-FOLD-20261114-001-E001_frozen_policy/independent.json)

The sender receives four named rules, two inlet names and two possible questions. It chooses a physical packet length using only the two possible questions, before reading source values. After the sender commits its packet the receiver sees only that packet and the question actually asked. Rule labels, read order and framing are supplied. The finite search fits expressions over elementary Boolean gates, the starting accumulator bit and the common decoder from downstream training answers and a cost for payload bits. It uses a supplied sequential scan, two accumulator bits and an optional one-bit output. It learns no movement schedule. Training holds out half the eight-bit worlds, two source pairs and two reader menus. [Design and split](preregistration.md) · [Training implementation](../../experiments/WIRED-FOLD-20261114-001/WIRED-FOLD-20261114-001-E001_frozen_policy/job.py)

| Test | Correct answers | Physical output |
| --- | ---: | --- |
| All seven familiar menus, all worlds and wirings | 43,008 / 43,008 | 1 bit on three repeated-question menus, 2 on four distinct-question menus |
| Two unfamiliar menus, all worlds and wirings | 11,136 / 12,288 | 1 bit on both |
| Only unfamiliar menus, pairs **and** worlds | 1,856 / 2,048 | 1 bit throughout |
| Force the fitted two-bit path, all menus | 55,296 / 55,296 | 2 bits throughout |

The scan starts with both candidate values possible. For each source whose name matches an inlet it intersects the current possibilities with that source's allowed set. It ignores the values of the other two sources. The frozen receiver can answer every permitted question from the resulting two bits. A fresh fit reproduced all learned parameters, search counts and scores. Reordering the records in all 24 ways changed zero packets. Consistent fresh renamings also preserved the packets. Swapping the roles of the values 0 and 1 while transporting the corresponding questions exposed the asymmetric width decision. [Independent raw-record interpreter](independent.py) · [Deterministic replay](../../artifacts/WIRED-FOLD-20261114-001/WIRED-FOLD-20261114-001-E001_frozen_policy/replay.json)

In a matched example, A and B allowed only 0, and C and D allowed neither value. Keeping all four records fixed and rewiring AB to AC changed the answer to “does 0 survive?” from yes to no. Across all paired rewirings requiring a different true answer, the full sender changed its prediction in 20,370 of 21,276 comparisons. Reader compression accounts for the remaining end-to-end misses. An unmodified two-bit readout was perfect across all worlds and source choices.

The width controller learned to send two bits precisely when the two possible questions differed in whether they included 1. A different controller that compares both bits of the public masks agrees on every training menu. They disagree when one question tests 1 and the other tests either value. If only 0 survives, their answers must be no and yes. If nothing survives, their answers must both be no. For the first port order the learned packet was identical in these two cases. The training observations could not distinguish these candidate width rules, and the disclosed tie-break favored the smaller expression. [Training trace and held-out failures](../../artifacts/WIRED-FOLD-20261114-001/WIRED-FOLD-20261114-001-E001_frozen_policy/results.jsonl)

Here one bit suffices exactly when the two questions are identical. Distinct questions give three or four possible answer pairs. Using the learned one-bit path by force scored 50,688 / 55,296, the best possible shared-decoder one-bit accuracy for this distribution. Across all menus the actual mean was 13/9 payload bits. An exact policy using the minimum fixed width in every menu averages 5/3. Framing is free in both measures. Minimum width can still retain distinctions that two overlapping questions never ask about.

From the repository root, the first command replays the fit and the second checks a saved checkpoint against raw inputs independently.

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -B experiments/WIRED-FOLD-20261114-001/WIRED-FOLD-20261114-001-E001_frozen_policy/job.py
.venv/bin/python -B research/WIRED-FOLD-20261114-001/independent.py --checkpoint artifacts/WIRED-FOLD-20261114-001/WIRED-FOLD-20261114-001-E001_frozen_policy/checkpoint.json
```
