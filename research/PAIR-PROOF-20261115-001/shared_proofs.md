# A single local proof for several triples

## The reproduced observation

The 36 two-bit parent edits have 2,100 eligible triples in total. The exact output programs and original gates are the completed parent experiment's physical-piece rendering. Exhaustive replay gave the following counts. A triple appears once per edit even when several proofs exclude it.

| Source of the observations | Two-bit edits | One-bit control edits |
| --- | ---: | ---: |
| Any pair and any new outside setting | 2,099 / 2,100 | 2,064 / 2,100 |
| First original setting per pair, same three original corners | 1,818 / 2,100 | 1,875 / 2,100 |
| First original setting per pair, choose three of those four edited corners | 1,920 / 2,100 | 1,996 / 2,100 |

In one seven-signal circuit, fixing the other signals to zero and varying signals 0 and 1 gave output pairs 00, 10, 01 and 10. The first three observations suffice for all five triples containing signals 0 and 1. For each such triple the receiving circuit sees the same outside signals, so a one-bit message could yield at most two different answers. The proof gives a lower bound on that candidate triple's width. A complete result also requires a feasible program and a lower bound for every other candidate.

The single uncovered triple on the two-bit stream was signals 1, 5 and 6 on parent `b13f98358274ef9a6e8881ce492e83a4`. The edited circuit has four distinct residual classes on that triple, although no two-signal face produces three distinct joint outputs there. This is also the chosen minimum triple, whose full class count needs verification anyway. Therefore fresh proofs can cover **all 2,064 alternatives** in the two-bit search. Across the one-bit controls, exactly the 36 genuinely one-bit triples remain uncovered in the exhaustive scan.

Offline optimization enumerated the best attainable group coverage at each pair-test budget. It found a minimum full cover totaling 445 successful pair tests across the two-bit edits. Offline choice is supplied free only in the ideal diagnostics. The timed solver must read the advised corners, obtain three distinct actual output labels, return a checkable witness and verify both the circuit and the minimum.

## What the proofs bought on the saved circuits

The same 445 is also minimal if the ideal chooser needs to cover only alternatives to the returned triple. Form a bookkeeping graph with one vertex per signal and one edge for each pair without a returned witness. Each triangle is then an uncovered triple. At most the returned triple may remain. With no triangle, a graph on `m` vertices has at most `floor(m²/4)` edges. With a single triangle, each of the other vertices contributes at most one edge to its three vertices, and the other vertices induce a triangle-free graph. This gives at most `3 + (m−3) + floor((m−3)²/4)` edges. At the observed sizes 7, 8 and 9, the latter bound is smaller. For 35 edits the triangle-free bound suffices, and for the remaining edit the unavoidable returned triple forces the single-triangle bound. Subtracting the applicable bound from the number of pairs on each circuit gives 445 in total. Each of the 36 executed full covers attained its own bound.

Every method returned the exact two-bit minimum on 36 edits and the exact one-bit minimum on the 36 controls. The checker compared both outputs of the returned NAND circuit on all 43,008 raw assignments across the two-bit edits and another 43,008 across the controls. Both ordinary solvers reuse public history. The compact ordinary solver can stop an alternative comparison as soon as it sees three distinct residuals. Proof solvers use the same exact cutoff on every alternative left open.

In the first eight paired timing blocks, each method bought its own history and returned all 36 two-bit circuits. “Misses” below are executed edited tests that failed to give three distinct outputs. The packed methods also charge their search across possible outside settings. Times are median whole-stream process CPU on one pinned core.

| Strategy on the 36 two-bit edits | Checked shared proofs | Failed edited tests | Alternative triples checked exactly | Total CPU |
| --- | ---: | ---: | ---: | ---: |
| Ordinary, using its original cached comparisons | 0 | 0 | 2,064 | 325.9 ms |
| Compact ordinary, stop on a third residual | 0 | 0 | 2,064 | 335.9 ms |
| Reuse the three original rows first | 556 | 305 | 246 | 364.7 ms |
| Reuse the original four-row setting | 610 | 223 | 144 | 366.6 ms |
| Reuse four-row settings, then scan remaining pairs with packed tests | 713 | 223 | 0 | 352.9 ms |
| New tests at fixed all-zero or all-one outside settings | 493 | 1,234 | 362 | 348.7 ms |
| Split ordered signals by parity and test pairs within each half | 442 | 0 | 6 | 334.1 ms |
| Ideal full cover, successful settings supplied | 445 | 0 | 0 | 334.5 ms |
| Ideal partial cover, allow two exact fallback checks | 443 | 0 | 2 | 320.4 ms |

Original discovery actually searched 1,020 signal pairs, saved 912 witnesses and found none on 108. The three-row method spent median 9.5 ms finding them and 8.1 ms independently validating them on each stream of 36 parents before any edited rechecks. The verifier then checked each returned edited certificate once and unioned the triples it excluded. Proofs and exact fallback always used the current edit. Of all 912 old proofs on two-bit edits, 599 still distinguished three outputs on those exact three rows. Only 447 retained the literal three old output labels. Sound reuse requires the former. The solver could skip old proofs whose triples were already covered.

The balanced strategy illustrates both kinds of sharing. Its 442 certificates replaced 2,058 exact alternative checks. They requested 1,326 row observations in the verifier. Reusing rows across certificates reduced that to 826 distinct row reads.

### How much could choosing the tests save?

The advisory solver received only a legal pair, outside setting and optional three-corner mask. Searching for the best settings and combining them into menus took 2.479 and 4.738 CPU seconds offline. We donated both costs to the ideal chooser, which still paid to obtain each requested observation and to independently verify its circuit. These diagnostics bounded attainable coverage for budgets of different sizes and checked several executable policies, including abstention. They do not give the optimum CPU over every imaginable algorithm.

For a more favorable test, we chose a schedule separately for each known edit using eight initial timing blocks, froze the actual requests and ran eight more blocks. On the two-bit edits this schedule used **228 certificates** and avoided **1,143 of 2,064** alternative checks. It took **316.7 ms** versus **334.3 ms** for the fastest ordinary control in that repeat. The median paired saving was **26.2 ms**, with a win in **7/8** blocks. When both edits of each original were requested, the same choices took **447.8 ms** versus **401.7 ms** for ordinary and won **1/8**. The eight comparison blocks used the same circuits with independent timings. This result triggered the separate learned-policy experiment on previously unopened larger circuits. The menu's training on known edit timings is an optimistic diagnostic, distinct from training a policy to act on new circuits.

Complete coverage and low CPU were different objectives here. The balanced deterministic split left only six ordinary checks. For the compact ordinary baseline the entire minimum-selection phase cost median **8.3 ms** and alternative verification cost **5.5 ms** on the 36 edits. Together these consumed approximately **4.0%** of whole-stream CPU. Full edited verification cost **46.0 ms**, largely independent of the choice of tests. Importing and loading the stream, rebuilding or validating original histories, returning the physical circuit and checking the raw outputs remained chargeable. The observed 26.2 ms paired timing difference exceeds these two measured phases on the compact control. Whole-stream CPU varies between fresh processes, so the trials support pricing the decision on new circuits without attributing all of that difference to avoided comparisons.

The [initial timing receipts](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses/timing.json), [frozen per-edit timing repeat](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses/timing-selection/timing.json) and [gate result](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses/result.json) contain all methods, including run order and paired CPU differences.

The independent replay checked 464 full stream runs with 25,056 circuit returns across the timing repeats. All methods returned the same 72 distinct physical programs. The audit independently evaluated their outputs and minima, checked certificate rows and stale proofs, and reconstructed the timing choice from the first set of runs. [Independent saved-circuit audit](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses/audit.json)

## A frozen policy on new wiring

The follow-up uses 36 training parents and 36 separate held parents from the predecessor's reserved generator. Each set has 12 parents for each of 8, 9 and 10 frontier signals. Two independent edits per parent give a one-bit and a two-bit minimum. Sizes 8 and 9 also occurred in the original study. Size 10 is larger than any original circuit. All three sizes are represented during model training. Three held seeds have new wiring and output families. The blind generator requires the already-saved model and its exact hash.

The policy gets the changed pin and its replacement and can trace a configurable number of NAND connections. The testing harness strips the IDs and other edits. Training may compute proof success from its own circuits. At deployment the chooser supplies candidate tests, and the solver has to obtain and check the actual outputs. If a test fails, all uncovered groups remain eligible for exact search.

Each training fold held out an entire original circuit together with its two edits. Training compared four radii, scored the number of packed comparisons avoided against the work to request and check observations, and included abstention. It generated labels for 17,146 distinct pair/setting combinations on the training parents. The selected radius was **two** directed NAND fan-in steps from the three pin sources. The frozen rule requests the better-scoring half of the within-group pairs, with the outside setting and corner mask chosen from the learned table. This is a local, supervised choice with an operation-count training objective. The held assessment measures process CPU directly.

Creating and independently grading the training set took 3.8855 CPU seconds. The complete model-training process cost another 0.5890 seconds, including 0.3685 seconds in the fitting function. The one-time debit per prospective stream was therefore **4.4745 CPU seconds**. It includes the supervision and radius selection. Each deployment also pays to load the model and to run inference. Generating the held fixtures is a common evaluation expense. The [frozen model](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E002_local_policy/model.json), [fit record](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E002_local_policy/training-selection.json) and [whole training charge](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E002_local_policy/training-cost.json) precede the blind run.

### What transferred and what it cost

All seven methods returned a verified one-bit program on **36/36** preserving edits and a verified two-bit program on **36/36** breaking edits. The outputs of the raw NAND programs were checked on **172,032** input assignments across the 72 edits. The benchmark completed 112 whole-stream runs and 6,048 exact returns with zero failed runs. Repeated timings do not add independent circuits.

| Held strategy | Exact alternative checks avoided on the two-bit edits | Exact alternatives still checked | 36 two-bit edits, deployment CPU | 72 mixed edits, deployment CPU |
| --- | ---: | ---: | ---: | ---: |
| Original ordinary | 0 | 3,084 | 405.47 ms | **477.20 ms** |
| Compact ordinary | 0 | 3,084 | **373.90 ms** | 478.74 ms |
| Matched solver with no proof | 0 | 3,084 | 381.08 ms | 489.01 ms |
| Fixed all-zero or all-one outside settings | 2,569 | 515 | 418.02 ms | 520.58 ms |
| Deterministic split with packed setting search | **3,069** | **15** | 384.60 ms | 481.59 ms |
| Fixed choices from the policy's action menu | 2,015 | 1,069 | 413.02 ms | 501.05 ms |
| Frozen two-step policy | 741 | 2,343 | 406.90 ms | 520.26 ms |

The learner tried **288** pair/setting tests on the two-bit edits. **119** produced certificates and **169** missed. In the verifier, 357 certificate observations reduced to 292 distinct row reads after sharing. The one-bit controls required no alternative-group certificates. The held seed breakdown shows the number of successful proofs and how many exact comparisons they replaced. Each row contains 12 two-bit and 12 one-bit edits.

| Held seed | Exact answers | Successful learned proofs | Alternative exact checks avoided by the learner | Avoided by the deterministic split |
| --- | ---: | ---: | ---: | ---: |
| 281219 | 24/24 | 40 | 252 / 1,028 | 1,019 / 1,028 |
| 281227 | 24/24 | 39 | 237 / 1,028 | 1,022 / 1,028 |
| 281233 | 24/24 | 40 | 252 / 1,028 | 1,028 / 1,028 |

On the 36 two-bit cases, the learned method took **4.881 s including training** versus **0.374 s** for the fastest ordinary solver. On the 72 mixed cases it took **4.995 s** versus **0.477 s**. These are median whole-stream CPU times, with one training charge per prospective deployment. On paired runs, its median additional cost including training was **4.504 s** and **4.508 s** respectively. It reached no break-even prefix on either stream. Even with training donated, it lost **8/8** two-bit comparisons with compact ordinary, and **7/8** mixed comparisons with ordinary. Across seven methods the independently prepared held fixtures cost a common 4.089 s, outside each method's solver bill.

On fresh two-bit cases the compact solver spent **9.27 ms** selecting the minimum and **7.08 ms** verifying the alternatives. The learned approach spent **5.87 ms** making proposals, **17.59 ms** selecting and **9.90 ms** verifying alternatives, including **1.81 ms** replaying certificates. Both still had to initialize their history, build the physical program and check raw inputs. For the learned solver, cold startup was 110.75 ms, original solver and verifier histories were 45.80 and 100.58 ms, and full edited verification was 70.21 ms. Phase medians are measured separately.

**Decision.** Close this investigation of a learned pair/setting chooser for this circuit family and measured horizon. A single local proof really does replace multiple exact triple checks. The strongest simple deterministic split replaced almost all of them. The remaining exact comparisons are cheap enough that neither it nor the learned chooser beat the fastest ordinary solver on median whole-stream CPU. Evidence here concerns supervised test choice in bounded Boolean circuits. [Held results, per-seed work and prefix costs](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E002_local_policy/result.json)

## Checking these results

The held audit independently reconstructed all 72 unique physical programs, their output tables, admissible triples, minimum widths, and the successful proofs and remaining checks across all 6,048 timed returns. Repeating the fit from training alone reproduced the identical model bytes. The recorded model predates the held data. All inference calls used the permitted public inputs. The independent replay also reproduced the full training bill and verified there was no paid break-even. [Independent held audit](../../artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E002_local_policy/audit.json)

Run these commands from the repository root to reconstruct the saved-circuit coverage, summarize both timing blocks, apply the selection threshold and recompute the held results and training bill. Each auditor supplies a separately implemented raw/minimum replay.

```sh
.venv/bin/python -B research/PAIR-PROOF-20261115-001/coverage.py
python3 -B research/PAIR-PROOF-20261115-001/assess.py
python3 -B research/PAIR-PROOF-20261115-001/assess.py --dir artifacts/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses/timing-selection
python3 -B research/PAIR-PROOF-20261115-001/decision.py
python3 -B research/PAIR-PROOF-20261115-001/assess_policy.py
```

The [paid pair-proof contract](../../experiments/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E001_shared_witnesses/contract.json) and [local policy contract](../../experiments/PAIR-PROOF-20261115-001/PAIR-PROOF-20261115-001-E002_local_policy/contract.json) specify inputs and controls. Each artifacts directory holds the hash-bound design, process timing receipts and compressed individual returned programs.
