# Does the frozen crossing help on a new three-input task?

November 14, 2026 Pacific. This study compares a primitive-only search with the same search allowed to call a previously learned crossing. The input is three labels, each 0, 1 or 2. A correct program leaves the third register at zero exactly when **all three inputs are equal or all three are different**. The other outputs are unrestricted. For example, `(2,2,2)` and `(1,0,2)` must produce a yes, while `(1,0,1)` must produce a no. The feedback gives a score only on this endpoint. [Frozen target, split and search](preregistration.md)

The earlier crossing exchanges two register positions and can transpose 1 and 2 in a label. It transports each label's zero/nonzero distinction to the other register. A fixed sequence made solely of crossing calls can therefore report only whether one of the original inputs was zero. None of those three observables solves the task. There are at least two primitive-only strategies. One accumulates the first and second labels into the third modulo three. Another accumulates the second into the first before adding the result to the third. Either takes eight allowed guarded flips (40 elementary Boolean operations) and satisfies all 27 cases. Their intermediate and final scratch states differ. These witnesses were checked independently and were hidden from the learner. [Independent replay and witnesses](independent.py)

Each arm has the same starting population, training cases, terminal reward, mutation and selection rules, common random draws and a 36-expanded-flip limit. The optional call expands to the exact 12 guarded flips learned previously (60 Boolean operations). In both arms the raw actions are available on every ordered pair of registers. Every run spends 196,640 candidate evaluations, even if it samples a program with a perfect training score much earlier. The target, held success criterion, five seeds and budget were recorded before running the search. [Earlier operation and learning comparison](../BRAID-ACTIONS-20261114-001/braid_actions.md)

Six of the eighteen training inputs and three of the nine held inputs are positive. Every allowed program permutes the 27 joint states, so its final register is zero on exactly nine. A training-perfect program must therefore predict three held positives, with 84 possible three-element choices. Under the balanced split, a perfect training score can coexist with held scores of 3, 5, 7 or 9 out of 9. This count describes the information in the split and makes no uniformity assumption about the search.

## Acquisition and execution units

Learning the final reusable **forward** program used 98,336 candidate evaluations in the original guided run. A different 24-step program first reached the maximum reward at proposal 1,500. The final 12-step program first appeared at proposal 51,610, and the original search ran to its fixed budget. Executing all proposed programs over the original nine legal states cost 13,810,500 guarded-flip applications, equivalent to **73,696,113 elementary Boolean operations**. The packed implementation applied 1,534,500 byte-table translations to construct the programs' images, and computed scores on 27,551 distinct images. Historical wall time was recorded for the combined forward, inverse and neutral arms, so a standalone historical forward time is unavailable. Undo training and research validation are excluded from the marginal cost of acquiring this forward operation. [Reconstructed acquisition costs](../../artifacts/BRAID-REUSE-20261114-001/BRAID-REUSE-20261114-001-E001_transfer/acquisition.json)

## What the searches found and kept

All ten runs sampled a program correct on the 18 training inputs and all 9 held-out inputs. All ten runs ultimately selected a five-flip program correct on the 18 training inputs and only **3 of the 9 held-out inputs**. For example, every selected program said no to `(0,1,2)` and `(2,2,2)`, even though both require yes. Each candidate program was selected by training score with shorter expanded length breaking ties. A correct candidate in the search history therefore did not give this learner a reliable way to choose it.

In each pair of columns, **raw** permits guarded bit flips and **reuse** also permits the frozen crossing. An exact candidate is correct on all 27 inputs. Its first occurrence was identified after training. Gates count expanded Boolean operations applied across the 18 training inputs up to and including that candidate.

| Seed | Held answers of selected program, raw / reuse (of 9) | Candidates to first exact, raw / reuse | Expanded gates to first exact, raw / reuse | Crossing calls in first exact reuse program |
| ---: | :---: | ---: | ---: | ---: |
| 17 | 3 / 3 | 6,820 / 5,670 | 5,742,918 / 7,451,982 | 0 |
| 29 | 3 / 3 | 8,169 / 6,931 | 6,240,816 / 6,578,478 | 1 |
| 43 | 3 / 3 | 8,151 / 8,151 | 7,136,856 / 8,462,574 | 0 |
| 59 | 3 / 3 | 6,630 / 6,630 | 4,948,848 / 7,310,844 | 0 |
| 71 | 3 / 3 | 4,173 / 5,261 | 3,081,096 / 4,849,146 | 0 |

All ten arms used their full **196,640** candidate budget. None was censored for *sampling* an exact program. Every arm exhausted its budget without *returning* one under its frozen selection rule. Four of the five first exact programs in the reuse condition used only ordinary instructions. The fifth, for seed 29, contained a call and cost 86 gates per input at inference. The five programs selected with reuse all contained zero calls.

| Seed | First training-perfect candidate, raw / reuse | Its held answers, raw / reuse (of 9) | Full-budget expanded gates, raw / reuse | Training seconds, raw / reuse |
| ---: | ---: | :---: | ---: | ---: |
| 17 | 1,826 / 1,855 | 3 / 3 | 173,637,792 / 269,672,634 | 1.086 / 1.179 |
| 29 | 1,982 / 1,982 | 3 / 3 | 170,748,558 / 275,795,298 | 1.073 / 1.188 |
| 43 | 2,907 / 2,907 | 3 / 3 | 167,174,244 / 269,840,808 | 1.053 / 1.170 |
| 59 | 3,563 / 3,798 | 3 / 7 | 166,672,476 / 271,165,950 | 1.059 / 1.182 |
| 71 | 3,775 / 3,943 | 3 / 3 | 167,528,484 / 274,122,396 | 1.076 / 1.188 |

## Did acquisition pay back?

Through the first exact *sample*, raw search averaged **6,788.6 candidates** and reuse **6,528.6**. Reuse saved an average of 260 proposals (3.83%). It reached that sample earlier in two paired seeds, tied in two and arrived later in one. Across the five seeds the raw arm used 27,150,534 expanded gates to this point and reuse used 34,653,024, an increase of **27.63%**. Reuse cost more expanded gates in every pair. Each proposed crossing expanded to 60 gates per input, or 1,080 across training. Treating a call as a single unit would hide that expense.

Across the **actual fixed-budget fits**, both conditions evaluated 983,200 candidates. Raw search used 845,761,554 expanded program gates and reuse used 1,360,597,086, an increase of **60.87%** before acquisition. Their summed serial training times were 5.35 and 5.91 seconds here. Each training execution also used two fixed terminal readout gates per input, the same 35,395,200 additional gates per condition at full budget. One packed operation evaluated all 18 lanes. The run record separates packed program work, expanded work, terminal readout, fitness evaluations and subsequent held-out evaluation. [Full run and per-event counts](../../artifacts/BRAID-REUSE-20261114-001/BRAID-REUSE-20261114-001-E001_transfer/results.jsonl)

Dividing 98,336 acquisition proposals by the 260-proposal difference gives **379** hypothetical repetitions to break even on proposal counts alone, if a future evaluator could recognize each first exact candidate and if the same average savings recurred. The actual learner had no such evaluator. Expanded gate cost increased and both arms returned zero verified solutions, so the experiment demonstrates **no compute payback and no payback for delivering a correct program**. These five seeds are repetitions of one task. The result bears on the cost of reusing this crossing under this selection rule. It leaves acceleration of AI research open.

## Reproducing the comparison

An independent implementation reconstructed all 1,966,400 proposals from the seeds, replayed 60,283 training-perfect programs on held inputs (counting each distinct program once per arm), and reproduced the saved costs and training selections. It also reconstructed the one-time acquisition stage. A fresh run of the original training code reproduced all ten search trajectories, selected programs, first exact programs and gate counts. [Independent audit](../../artifacts/BRAID-REUSE-20261114-001/BRAID-REUSE-20261114-001-E001_transfer/audit.json) · [Per-seed results](../../artifacts/BRAID-REUSE-20261114-001/BRAID-REUSE-20261114-001-E001_transfer/result.json)

From the repository root, the following commands repeat the fits in a fresh directory and verify the results. Wall times vary between runs.

```sh
study=BRAID-REUSE-20261114-001
family=${study}-E001_transfer
output_dir=$(mktemp -d)
OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0 .venv/bin/python -B \
  "experiments/$study/$family/job.py" > "$output_dir/results.json"
.venv/bin/python -B "research/$study/independent.py" \
  --result "$output_dir/results.json" --write
```
