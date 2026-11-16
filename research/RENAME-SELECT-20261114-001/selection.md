# Which training-perfect program should the learner keep?

On November 14, 2026 (Pacific), a task-local selector chose an exactly correct program in **52 of 60** pools of programs that all fit the 18 training examples. Keeping the shortest chose 27. Always trusting every label renaming chose 36. Adding the frozen crossing to the search produced one more certified return under the fitted selector, at **37% more logical work per correct return** before acquisition. Directly checking each training-perfect program as it appeared had the lowest cost per return in this finite test. [Frozen design](preregistration.md) · [Machine-readable results](../../artifacts/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/result.json)

## How the selector chose

All ten tasks classify three labels, each 0, 1 or 2, and each has exactly nine yes inputs out of 27. All ten differ from the previous all-equal-or-all-different task. For every task the same 18 inputs train the search, and the other nine stay hidden. Three seeds and two search languages gave 60 candidate pools. Both languages have the same elementary instructions. One can also call the previously learned 12-flip crossing. Each pool was collected at a fixed 49,184 proposals. It included every distinct program that fit all training rows, in order of first occurrence. There were 152,112 such entries across the pools. A fully correct program was present in 55 pools. All three selectors ranked exactly the same programs within a pool. [Tasks, truth tables and raw-only feasibility witnesses](problems.py) · [Candidate stream](../../experiments/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/stream.py)

For each of five ways to rename labels, the learner compared pairs of training inputs related by that renaming. It trusted a renaming when there were at least two distinct changed pairs, both yes and no answers occurred among the observations, and the answers agreed on every compared pair. Each retained renaming could carry an observed answer to a new input. The learner ranked programs by agreement with those votes and broke ties by the old shortest rule. It fitted these decisions anew from the 18 examples. The rule for testing a renaming was supplied. No selector received the formula, task ID, true symmetries or fresh answers. If the votes provided no information, the fitted rule fell back to length. This tests induction in a fixed family of label permutations. [Selector and estimator](../../experiments/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/selection.py)

| True renamings, including the identity | Pools | With an exact candidate | Keep shortest | Always trust renaming | Fit renamings |
| --- | ---: | ---: | ---: | ---: | ---: |
| All six | 18 | 17 | 12 | 17 | 17 |
| Three | 12 | 12 | 1 | 8 | 12 |
| Two | 12 | 12 | 3 | 11 | 12 |
| Identity alone | 18 | 14 | 11 | 0 | 11 |
| **Total exact choices** | **60** | **55** | **27** | **36** | **52** |

The fitted selector gained 25 exact choices and lost none relative to shortest in this panel. It got 520 of 540 held answers right, compared with 430 for shortest and 460 for unconditional renaming. For the direct question about choosing between **two** programs, take every pair within a pool in which exactly one program is correct on all 27 inputs. Give each eligible pool equal weight. Fitted renaming picked the correct member **93.0%** of the time, shortest **69.1%**, and unconditional renaming **87.9%**. There were 55 pools with such a pair. Distinct programs that compute the same classifier can occur more than once, and these pairs share both training sets and programs.

On the seven tasks that genuinely admitted at least one nonidentity renaming, the accepted changes transported training answers to all nine unseen inputs. Whenever an exact candidate was available on those tasks, the fitted rule selected one (41 of 41 pools). On two tasks where every nonidentity renaming changed some answer, the rule found no supported renaming and reverted to shortest. The tenth task, described below, fooled it.

One task requires the third value to be zero if the first two are equal, and to be the remaining label if the first two differ. Renaming 1 and 2 together preserves its answers. In the ordinary search with seed 101, a seven-flip program and a nine-flip program both fit all 18 observed answers. On the unseen input `(0,2,1)`, the seven-flip program said no. The nine-flip program said yes and passed all nine held cases. The selector identified the exchange of 1 and 2 from training, and took the longer program.

## When the evidence cannot distinguish two answers

The learner identified the true set of renamings on nine of the ten tasks. The exception was deliberate. One task says yes exactly when the first two labels agree. Its twin gives the same answer on 25 of 27 inputs, reversing only `(1,1,1)` and `(1,0,0)`. Both inputs were withheld. The 18 observations, candidate banks, fitted renamings, votes and blind choices were identical in all six matched seed/language comparisons. Each changed-label run scored 7/9 under fitted renaming, even though two of those pools contained a fully correct program. A learner using just those observations cannot guarantee the right choice on both tasks. A paid exact check could distinguish them.

There are only three unused globally rename-invariant nine-positive predicates in this particular three-input domain, the three pair equalities. Simultaneous renaming partitions the inputs into one set of three and four sets of six. A union with nine inputs must pick the set of three and one of the sets of six. The earlier experiment had already used the fourth possibility. All seven label-sensitive targets in this panel depend on all three inputs. All ten have independently constructed solutions using 4–32 ordinary flips within the 36-flip horizon. A missing exact candidate is a search limitation at this budget.

## What it cost to return a checked program

Each deployed method ran from scratch with a fresh candidate stream and caches and stopped only after its verifier accepted a program or it exhausted its budget. Fitted and shortest could submit up to four previously untried candidates at each of six fixed checkpoints. The direct method submitted every new training-perfect program immediately. The verifier had access to the nine remaining true answers. It checked in a fixed order and rejected at the first mismatch. It supplied only pass or fail. A yes certifies all 27 possible inputs because the submitted program had already passed all 18 training inputs. The unassisted choices in the preceding section were fixed without a verifier. [Deployment and exact checker](../../experiments/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/job.py)

| Method | Search actions | Exact returns of 30 | Programs submitted for checking | Millions of work units per correct return | Elapsed seconds per correct return |
| --- | --- | ---: | ---: | ---: | ---: |
| Keep shortest | Ordinary | 20 | 213 | 33.21 | 0.251 |
| Keep shortest | With crossing | 20 | 208 | 43.19 | 0.235 |
| Fit renamings | Ordinary | 26 | 152 | 18.87 | 0.143 |
| Fit renamings | With crossing | 27 | 161 | 25.88 | 0.142 |
| Check immediately | Ordinary | 27 | 3,525 | **13.79** | **0.109** |
| Check immediately | With crossing | 28 | 8,075 | 18.45 | 0.110 |

Each average divides the work of **all 30 attempts, including every failed attempt**, by the number of verified programs actually returned. Times cover a serial deployment from available training data through stopping, including proposals, ranking, checking, caches and interpreter overhead. They are observations from one host. The predeclared unit charges expanded Boolean computation, answer comparisons and specified label accesses. It counts the crossing's 60 gates per input at every invocation. It includes ranking computations even when they tested a candidate never submitted, all failed verifications, and the use of already-paid candidate predictions during checking. Host time also includes integer vote addition, sorting, and random proposal generation. Raw logs contain the component counts and all verification requests. [All 30 paired runs](../../artifacts/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/results.jsonl)

The two fitted-selector columns shared 26 successful episodes. Among those exact same tasks and seeds, ordinary search averaged 10.89 million units and reuse 16.83 million. Reuse was cheaper in 6 of the 26. Of the 27 programs it returned, six contained a crossing call. Failed episodes cost 207.50 million units in ordinary search and 257.73 million with the crossing. Direct checking had 26 successes in common. Ordinary search averaged 7.24 million and reuse 12.88 million on that intersection. On the 16 successes shared by the shortest rule, reuse was cheaper on average (4.08 versus 5.28 million). Its unsuccessful runs made reuse costlier per correct return over the whole panel.

Learning the original crossing took **98,336 proposals**, equivalent to at least **73,696,113 scalar actor gates** over its nine original inputs. Its historical implementation used packed translation tables and cached scores. Three fresh repeats of the original forward-only search produced the frozen instruction sequence in a median **0.308 seconds**. Charging this acquisition once across the 30 attempts raises the fitted crossing result to **at least 28.61 million units and 0.154 seconds per correct return**, compared with 18.87 million and 0.143 seconds for ordinary actions. For direct checking, the corresponding crossing figures are at least 21.08 million and 0.121 seconds. Its recurring logical cost was already higher with the acquisition treated as free. [Reacquisition measurement and implementation counts](../../artifacts/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/acquisition.json)

Direct checking benefited from access to nine inexpensive, exact answers. With ordinary actions, it spent 715,416 units on certification across all 30 attempts. Its savings came from stopping search earlier. As a sensitivity calculation, adding a flat fee of roughly 40,733 work units per program submitted to the verifier would erase its cost-per-return advantage over fitted renaming, with the observed choices and stopping points held fixed. That fee was not charged in the experiment. The evidence supports learning which renamings to trust within this panel. Reuse cost more per exact return on this task mix. Generalization to larger tasks remains open.

## Reproduction

Run from the repository root. The first command reads the recorded runs and recomputes blind outcomes, pairwise wins, per-task and per-seed results, shared-success costs, censoring, and the training-identical control.

```sh
python3 -B research/RENAME-SELECT-20261114-001/summarize.py
```

To repeat every search, selection and operational stop in a fresh output directory, use the same frozen seeds and the serial shared runner. The copied acquisition receipt is the common historical cost input. All program choices and cost counts have deterministic replay; elapsed seconds can vary.

```sh
study=RENAME-SELECT-20261114-001
family=${study}-E001_selector
dest=$(mktemp -d)
export OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0
.venv/bin/python -B scripts/longrun.py launch "experiments/$study/$family/job.py" \
  --out "$dest" --unit rename-select-replay --workers 1 --case-timeout 600 \
  --case-mem 2G --mem-max 4G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$dest" --foreground --limit 30
cp "artifacts/$study/$family/acquisition.json" "$dest/acquisition.json"
.venv/bin/python -B "research/$study/summarize.py" --raw "$dest/results.jsonl" \
  --out "$dest/result.json"
```

A repeat of cases `1ab7-101` and `f46b-211` reproduced the four candidate banks, all blind results, and the exact requests, stopping proposals, returned programs and work counts in all twelve operational deployments. The official run completed all 30 paired cases in about 50 seconds, including full-bank collection and scientific evaluation. [Source fingerprints recorded before the first target fit](../../artifacts/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/freeze.json)

An independent implementation reconstructed the 54 distinct candidate streams (2,655,936 proposals). The six remaining streams repeat the matched twin's training data, seeds and search language. The audit reproduced every bank, blind ranking, submitted program, failed check, stopping decision and operational cost ledger. [Audit results](../../artifacts/RENAME-SELECT-20261114-001/RENAME-SELECT-20261114-001-E001_selector/audit.json) · [Independent implementation](audit.py)

```sh
study=RENAME-SELECT-20261114-001
.venv/bin/python -B "research/$study/audit.py" \
  --results "artifacts/$study/${study}-E001_selector/results.jsonl"
```
