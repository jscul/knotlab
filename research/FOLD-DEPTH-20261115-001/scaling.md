# Using an unlocated operation repeatedly during program search

The supplied fold helped when the search tested two raw input positions together. On eight recurring rules per depth, ordinary primitive search took 187, 503 and 810 actual placement or factor tests at depths two, three and four. Directly testing for the supplied operation took 199, 336 and 716. The gain peaked at depth three, while the difference in paid search CPU time grew from about 0.05 to 1.41 to 5.10 ms per eight rules. The identically informed inlined library selected the same placements. The result qualified for the separate discovery test under the rule chosen before measurement. [Bound protocol](preregistration.md) · [All cells and costs](../../artifacts/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/result.json)

The earlier decoder learned two successive primitive operations, AND then XOR, and recovered its fourth answer from three on all 24 dependent layouts. Here that previously found operation, F(a,b,c) = (a AND b) XOR c, was supplied as a seven-NAND program at zero acquisition cost. Neither its locations nor how many calls would fit a task were revealed. [Earlier result](../ANSWER-COMPOSE-20261115-001/answer_composition.md) · [Source circuit](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/fold.json)

| Hidden composition depth | Trial count, primitive | Trial count, direct fold or inline | Search CPU, primitive | Search CPU, direct fold | Paired broken rules, primitive / direct fold |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 187 | 199 | 0.41 ms | 0.36 ms | 168 / 278 |
| 3 | 503 | 336 | 2.21 ms | 0.80 ms | 489 / 626 |
| 4 | 810 | 716 | 8.00 ms | 2.91 ms | 813 / 978 |

Each row totals eight distinct rules per condition. CPU time is the median of five cold runs. A trial is an actually executed candidate role or factor screen, including failed ones. One trial can cost different amounts. At depth four, five of eight recurring rules saved trials and seven saved search CPU. The direct solver found all two, three and four planted calls on each corresponding positive. On each negative it found one fewer call. Trying the template on the negatives increased trial counts at all three depths. Many role tests reject a candidate after inspecting a few bits. At depth four on recurring tasks, 616 of the 716 direct role trials were rejected by these early checks.

## How the search affected the result

The direct method considers any two inputs. Holding them at 00, 01, 10 and 11 gives four functions over the other inputs. If three are the same function h and the fourth is its complement, the pair can occupy the AND ports with h at the XOR port. Other tests admit either raw input at the XOR port. The solver recursively synthesizes h, and has a general fallback. The primitive competitor has its own one-input tests and the same access to general decomposition. A second strategy instead finds an XOR decomposition and an AND factor before testing the whole operation. On the same recurring tasks this raised the counts from the primitive 187/503/810 to 203/685/1,073. The ability to call a shorter program therefore depends on how candidate placements are found. [Target-blind general solver](../../experiments/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/solver.py) · [Direct matcher](../../experiments/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/peel.py)

The inline control searches the same operand groupings at every subproblem. It expands an accepted use into AND and XOR, taking six NANDs. The original saved program uses seven. Both templates make identical placement trials within each strategy. A separate warm pass kept public subproblem caches between rules of the same arity. On the main recurring eight at depth four the warm direct method used 694 trials against 748 for primitives.

On three paired cases per depth with nine genuinely essential inputs throughout, a planted leaf could itself be a primitive OR. Direct search on the positive cases took 1,110, 993 and 257 trials against 345, 597 and 227 for primitives. This test did **not** show a trial saving. The deepest three were a preselected subset of the primary panel, referenced once in the actual workload. The differences among input counts, how many operands are raw, and which structures were sampled limit the interpretation of these three depth points.

Across the 60 unique rules in the combined panel, the direct fold took 63.19 ms total with cold caches, against 73.21 ms for direct primitive search. Search accounted for about 38.75 and 48.26 ms respectively, and exhaustive verification about 6.37 and 6.53 ms. The more general factor search took 159.44 ms with the fold against 94.82 ms for primitives. Looking only at the main positive tasks would miss both the extra work on changed rules and the sensitivity to the search algorithm. Timings are host-specific.

## Coverage and replay

The public input is only the arity and full truth table. Every task has four equivalent hidden primitive expressions, including one that alternates spelling across levels. All source forms produce the same table before the solver sees it. The experiment tests semantic compression and synthesis and does not establish recognition of a rewrite in text. Each matched negative changes exactly one site. All 24 main pairs match essential input count, primitive gate count and output balance; 16 pairs also match the individual AND/XOR counts. At depths two, three and four the eight primary positives per depth span one, three and six structures up to renaming, respectively.

There were 60 unique targets, 16,896 target–input combinations per method per run, and 2,160 timed rule runs. All returned programs passed exhaustive verification. Every trial, including negative screening and cache lookup, remains in its method ledger. Five cold repeats and a warm pass were completed for each of six methods. Fixture construction and independent auditing are outside paid synthesis costs. [Task generator](tasks.py) · [Public case and source commitments](../../artifacts/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/freeze.json)

Recompute the metrics and the continuation decision from the stored results with this command.

```sh
python3 -B research/FOLD-DEPTH-20261115-001/assess.py
```

Independent replay of all 2,160 runs verified every returned physical program and every candidate-work counter. All 24 main negatives also excluded any complete read-once tree of the supplied F, including branching trees. The argument about all other ternary operations applies specifically to chains. [Independent audit](../../artifacts/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/audit.json)
