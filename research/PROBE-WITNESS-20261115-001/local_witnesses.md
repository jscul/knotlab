# A small witness against a one-bit summary

On November 15, 2026, the fixed two-setting method returned the exact minimum on **all 192 fresh rules**. All 96 shared rules used one bit, and the 96 matched rewires required two. The verifier accepted 2,729 compact exclusion witnesses. The method used **442.355 ms** of process CPU to return all verified programs, versus **304.787 ms** for the fastest exact primitive and **359.290 ms** for the existing four-cofactor heuristic. It lost all eight paired CPU comparisons to each. Calibration found additional witnesses when allowed to choose settings. The extra coverage supplied no repeatable total-CPU gain. The separate learner was not triggered. [Numerical results](../../artifacts/PROBE-WITNESS-20261115-001/PROBE-WITNESS-20261115-001-E001_fixed_probes/result.json)

## What three observations can prove

Assume three raw inputs feed a summary, and everything outside those inputs can see only that summary. Pick three settings of the local inputs. At the same fixed outside setting, read both output bits for each local setting. If the three results differ, a one-bit message is impossible. If they do not, try a second outside setting and compare the two-setting signatures. When all three signatures differ, any pair of local settings that shares its message is distinguishable by at least one of the observed outputs.

More generally, whenever a group needs more than one bit, **some** choice of at most two outside settings suffices to witness this. Pick three different residual functions. A setting distinguishing two of them either separates all three or leaves exactly two tied. A second setting distinguishing that tied pair finishes the witness. Finding useful settings from the tables is a separate computational cost. In this experiment the fixed choice is all outside inputs zero, followed when needed by all outside inputs one. [Design and decision rules](preregistration.md)

Each certificate identifies the group, three local input assignments, and which predetermined outside setting or settings to use. It contains no trusted answer values. It costs the verifier three or six original input rows, reading both outputs at each. Discovering a certificate can cost up to sixteen joint row lookups. The solver and verifier each reuse a previously observed global row across overlapping groups using their own task-local cache. A fresh task starts with fresh observations.

Here is one returned six-row certificate on a fresh seven-input rule (public identifier `a279af7c477fcfa3e75df0e9b7c642c7`). Input numbering starts at zero. Each table cell is the pair of output bits. Neither column by itself has three different entries. The ordered pair of columns distinguishes all three local states.

| Local inputs `(x3,x5,x6)` | All other inputs zero | All other inputs one |
| --- | --- | --- |
| 000 | 00 | 11 |
| 100 | 01 | 11 |
| 010 | 00 | 10 |

A witness that excludes one bit can still describe a group that attains the two-bit minimum. The solver therefore retains exact tests until it has a feasible narrow-enough incumbent, and sends every unresolved eligible candidate through the ordinary exact search as needed. The verifier checks the chosen group's class count and the physical program, confirms that every path from that group passes through the stated number of intermediate wires, and verifies every lower bound that the submitted witnesses leave open. A valid three-signature witness cannot discharge a requirement to exclude two bits. [Verifier](../../experiments/PROBE-WITNESS-20261115-001/PROBE-WITNESS-20261115-001-E001_fixed_probes/verifier.py)

## Tests and payment

The primary panel contains 96 fresh matched pairs. Within each pair one consumer's wiring changes. Each raw input matters to both outputs. Cases balance seven, eight and nine inputs and two local operations. Separate calibration uses 24 other pairs. The source fixes the panels independently of how many candidates the probes reject. The two panels exclude structures and truth-table families used by the previous ordering experiment under the declared input-renaming and output-exchange checks. The solver receives just the arity and the two complete Boolean truth tables. [Fixture generator](panels.py) · [Previous primitive and four-cofactor results](../TRIPLE-ORDER-20261115-001/triple_order.md)

All deployments pay for module and engine setup, probe attempts, cache management, construction and return of the witnesses, fallback, synthesis of both outputs, exact physical checks and verification of the exclusions. The primitive comparators can share intermediate gates across outputs. Evaluating the generator, writing private scientific traces and the independent final replay are shared research overhead outside each method's clock. Counterbalanced repeated timings use fresh processes, including fresh caches for each method, and the same preselected task order.

## What the fixed probes actually did

The fixed-probe solver returned the same chosen triple and the same physical NAND circuit as both its no-probe control and the archived generic primitive on every held rule. On the 192 held rules, the solver screened 4,867 candidate triples after it had established a sufficiently narrow feasible program. The probes excluded one bit on 3,724 and left 1,143 requiring exact fallback. The solver made 4,591 exact group checks in total, including the earlier checks needed to find feasible programs. On the shared rules 995 local exclusions were ultimately unnecessary for verification once a one-bit program was found. Their discovery cost was still paid.

On the 96 rewired rules the verifier had 5,504 alternative groups to check beyond the exact chosen group. It used the submitted witnesses for 2,729 and performed exact lower-bound checks on the remaining 2,775. Of the certificates actually returned, 1,369 used one outside setting and 1,360 used two. For discovery the solver made 49,014 joint-row requests, served by 13,721 distinct row reads and 35,293 reuses within tasks. The verifier independently checked 12,267 row references through 5,121 distinct reads and 7,146 reuses. These are probe observations; full physical-output verification still covered every original assignment.

As an offline coverage check, the two fixed settings could distinguish at least three classes for 8,802 of the 11,104 held triples for which one bit was impossible. The operational search only needs to ask this question on a subset of those triples. Across the four candidate pairs of settings, 10,622 of the 11,104 triples had at least one witness. These all-triples counts were computed outside the clock after deployment and played no part in the main method's choices.

## Cost to return verified programs

Each time is the median for a complete 192-rule warm deployment over eight counterbalanced runs. Each method starts with a fresh worker process. The search column includes probing and circuit construction. The total column also includes startup, initialization, return serialization and other paid dispatch. Component medians need not sum to the median total.

| Method | Exact group checks in search | Search and construction CPU (ms) | Verification CPU (ms) | Total CPU (ms) |
| --- | ---: | ---: | ---: | ---: |
| Same engine, exact only, packed verifier | 8,315 | 200.952 | 36.325 | **304.787** |
| Earlier lexical primitive with an output cache | 7,343 | 197.179 | 47.002 | 310.586 |
| Archived generic primitive with the new packed verifier | 8,315 | 209.343 | 38.952 | 310.907 |
| Archived fastest generic primitive with its original verifier | 8,315 | 205.358 | 47.169 | 315.298 |
| Existing four-cofactor heuristic | 5,896 | 231.585 | 56.842 | **359.290** |
| Independent primitive with full class enumeration | 11,200 | 268.101 | 73.916 | 379.960 |
| Fixed probes with the original full verifier | 4,591 | 302.895 | 48.976 | 429.746 |
| Fixed probes with same-witness verification | 4,591 | 303.115 | 51.122 | **442.355** |

The exact-only control and fixed probes emitted identical circuits on every task. Verifying those circuits with the same packed verifier cost 36.325 ms with an empty witness list and 51.122 ms with the submitted witnesses. Each local argument is short. Across a stream the two programs still build, decode, re-read and check thousands of records. The exact primitive can compare an entire remaining truth column at once using a shift and mask on a packed integer. Total elapsed medians were 1,029.700 ms for the matched exact control, 1,368.701 ms for four cofactors and 1,501.514 ms for fixed witnesses. CPU was the registered comparison on the shared host.

## Is selecting other probes worth learning?

The separate calibration panel contains 48 rules. Each diagnostic was given its scheme choices for free, then paid all raw reads, tests, circuit construction, serialization and verification. The cross-scheme diagnostic could select one of four pairs per triple or skip. Four single-scheme diagnostics could only skip futile probes. Their decisions came from full inspection of the calibration tables, so these are favorable measurements of the stated strategies. They do not establish an optimum over all choices.

| Calibration method | Witnesses used by verifier | Exact group checks in search | Total CPU (ms) |
| --- | ---: | ---: | ---: |
| Best fixed pair, all zeros / all ones | 725 | 1,079 | 150.086 |
| Free selection among four pairs, including skipping | 819 | 944 | 151.408 |
| Best fixed pair with free knowledge of when to skip, alternating bits | 701 | 1,124 | 146.057 |
| Same engine, always exact | 0 | 2,103 | 125.216 |
| Archived generic primitive | 0 | 2,103 | 111.883 |

Using all four schemes returned **94 additional useful witnesses** over the best fixed pair. It used 1.321 ms more CPU and won only 3 of 8 paired runs. It also lost 7 of 8 comparisons to the fastest single-scheme skipping strategy. The latter saved 4.029 ms versus the best always-probe pair in 6 of 8 runs, and cost 20.841 ms more than always-exact in all 8. Neither the context-selection nor the abstention criterion passed. The reserved training and evaluation panels stayed unopened. This result concerns the four tested setting pairs, the specified discovery order and these finite rule families.

## Replay

The 152 isolated streams ran on one pinned logical CPU of an Intel Core i7-13700KF with Python 3.13.3. The first measured stream finished 7.5 seconds after source binding. The largest worker used 25.7 MiB. The run returned 16,512 programs across the calibration, held and repeated deployments. The common physical verification covered 4,931,584 original assignments and 9,863,168 output values counting repeats, with zero failed returns. [Frozen source hashes](../../artifacts/PROBE-WITNESS-20261115-001/PROBE-WITNESS-20261115-001-E001_fixed_probes/design.json) · [Frozen data](../../artifacts/PROBE-WITNESS-20261115-001/PROBE-WITNESS-20261115-001-E001_fixed_probes/data-bound.json) · [Per-stream receipts](../../artifacts/PROBE-WITNESS-20261115-001/PROBE-WITNESS-20261115-001-E001_fixed_probes/results.jsonl)

The independent audit verified the original-row signatures, cache use, exact fallbacks, physical circuits and time aggregation. It covered all 96,008 submitted witness records across controls and repeats. Its scalar evaluator ran the 444 distinct physical task/program/cut combinations and matched repeated returns to those checked bindings. Both the main comparison and the calibration decision reproduced. [Audit receipt](../../artifacts/PROBE-WITNESS-20261115-001/PROBE-WITNESS-20261115-001-E001_fixed_probes/audit.json) · [Independent replay](audit.py)

From the repository root, rebuild the numerical report with `python3 -B research/PROBE-WITNESS-20261115-001/assess.py`. To repeat the comparison, set `out` to a fresh directory and use the following commands.

```bash
exp=experiments/PROBE-WITNESS-20261115-001/PROBE-WITNESS-20261115-001-E001_fixed_probes
python3 -B "$exp/prepare.py" bind "$out"
python3 -B "$exp/prepare.py" release "$out"
python3 -B scripts/longrun.py launch "$exp/job.py" --out "$out" --unit probe-witness-fixed --workers 1 --case-timeout 150 --case-mem 1G --mem-max 2G --max-cases-per-worker 1 --param "data_dir=$out" --prepare-only
python3 -B scripts/longrun.py run --out "$out" --foreground
python3 -B research/PROBE-WITNESS-20261115-001/assess.py "$out"
```
