# What a saved fold changed for a second learner

The second learner returned a correct new rule on **32/32 tasks** with the saved fold and on **32/32** without it. Prioritizing the fold reduced the number of proposed programs checked from **136 to 129**. Learning all 32 rules took **11.243 seconds with the fold** when charged for its acquisition, compared with **0.101 seconds without it**. Even with acquisition already paid for, the run using the fold took **0.186 seconds**. The experiment ran on November 15, 2026. [Preregistration](preregistration.md) · [Bound results](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/result.json)

Both learners received the same five labeled rows on a four-input task or seven on a five-input task. They could fit a rule using AND, OR and XOR, with each input used exactly once. One learner could also try the saved seven-NAND circuit `F(x,y,z) = (x AND y) XOR z` as one operation in search. It could use that operation once, including inside another expression. Both learners could express the same 243 four-input and 3,933 five-input functions. Each held rule depended on every input, so the earlier three-input answer could only be a component. The 32 targets represent distinct functions even after renaming the inputs at each size. [Task construction](panels.py) · [Learner](../../experiments/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/learner.py)

For the primary pair, search returned the first program consistent with the supplied examples. We gave the learner with the fold a search order that tried programs containing it first. The primitive program order was identical in both arms. A checker compiled each proposal into physical NAND gates and returned the first input on which its answer was wrong. The learner added that observation and revised its program. A successful check executed the program on all 16 or 32 inputs. Every row and gate actually visited on every attempt was charged. [Physical checker and median selector](../../experiments/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/protocol.py)

## Which tasks benefited

| Task selection | Tasks | Checks without fold | Checks with fold | Tasks requiring fewer / equal / more checks with fold |
| --- | ---: | ---: | ---: | ---: |
| Rules chosen to contain the fold | 8 | 33 | 26 | 6 / 1 / 1 |
| Matched changes that exclude it | 8 | 33 | 36 | 0 / 6 / 2 |
| Sampled without conditioning on fold availability | 16 | 70 | 67 | 5 / 7 / 4 |
| **All** | **32** | **136** | **129** | **11 / 14 / 7** |

The neutral sample was drawn uniformly over classes under input renaming, then a labeled representative was chosen. Seven of those 16 rules admitted the fold. The learner used it in the final programs for all eight selected positive rules and all seven applicable neutral rules. Across the full panel, the first guesses were exact for three tasks in each arm. On the 576 initially unlabeled input rows, those guesses answered 392 correctly with the fold and 384 without it. After counterexample feedback, each method answered all **768/768** rows correctly. [Panel with labels and matched changes](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/panel.json) · [Per-task results](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/result.json)

For example, the same five starting labels fit both `a OR (c XOR (d AND b))` and `a OR ((c XOR d) AND b)`. The two answers differ on only two of the sixteen inputs. The first rule can use `a OR F(d,b,c)`. Prioritizing the fold reduced its checks from five to four. On the matched rule, prioritizing it increased the checks from two to four. [Recorded proposal and counterexample sequences](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/results.jsonl)

## Total work to return the programs

| Selection and library | Candidate checks | Input rows checked | NAND evaluations in checks | New learner, including setup | Including original acquisition |
| --- | ---: | ---: | ---: | ---: | ---: |
| First consistent, primitives | 136 | 1,645 | 18,143 | 0.1013 s | 0.1013 s |
| First consistent, fold available | 129 | 1,415 | 16,551 | 0.1858 s | 11.2435 s |
| Median function, primitives | 102 | 1,358 | 15,161 | 0.0985 s | 0.0985 s |
| Median function, fold available | 102 | 1,358 | 15,683 | 0.1870 s | 11.2447 s |

The upstream charge was **11.0577 seconds**. This includes the earlier parser training case (2.3595 s), the original fit that chose the binary operations and probe budget (8.6407 s), and materializing and certifying the particular folded program on its source wiring (0.0575 s). We used the recorded training durations and checked the archived circuit against a fresh execution of its planning and certification steps. The transferred circuit occupied 66 bytes on disk. Both downstream paths included setting up their catalogues, acquiring initial labels, revising hypotheses, running each check and serializing the accepted programs. Checkpoint transfer was local. [Source provenance and elapsed-time ledger](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/source_cost.json)

The timing values are medians over three fresh processes per method, each solving the full set with its catalogues shared across tasks. The primary downstream ranges were 0.0925–0.1043 s without the fold and 0.1853–0.1866 s with it. Catalogue setup used 0.0843 s and 0.1763 s, respectively. The implementation compiled all read-once candidates on setup and charged duplicates. It executed 105,705 NAND operations on packed truth tables when building the primitive catalogues and 181,391 with the fold. A packed operation evaluates a whole group of inputs at once. The checker evaluates one input at a time, as counted in the table above.

Even with catalogues already built, fitting and checking the mixed set took 8.35 ms without the fold versus 9.44 ms with it. On the eight positive tasks alone, those warm times were 2.04 ms without and 1.35 ms with it. Every fold call expanded to the original seven gates. The simple primitive expansion of AND followed by XOR takes six gates with the common NAND compiler. [Catalogue work, checker calls and raw timing observations](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/results.jsonl)

To test what the inherited search order contributed, we also tried choosing the middle remaining function in a common ordering of all possible truth tables. This learner used the first failing input and the higher-index inputs the checker had already confirmed. The two libraries then made exactly the same predictions and received exactly the same counterexamples on all 32 tasks. There were 102 checks in either arm. With this fixed ordering, the extra NAND in the saved implementation accounted for 522 additional gate evaluations during checking. On the observed mixed panel, inheriting the fold biased search toward some correct answers sooner. The cost of finding and verifying the complete set of new rules was lower with the primitives alone. [Paired results and common-order control](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/result.json)

## Reproduction

An independent replay matched all 12 trials, comprising 384 task runs and 1,407 proposed programs checked. It also tried a second control that kept the primitive search order fixed and substituted saved-fold implementations wherever available. Both arms then made 136 identical guesses. Physically checking them took 18,682 NAND evaluations with the fold and 18,143 with primitives. The following command verifies the saved comparison from the repository root. [Independent audit](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/audit.json) · [Audit implementation](audit.py)

```sh
.venv/bin/python -B research/FOLD-REUSE-20261115-001/audit.py
```

The complete replay below uses a new output directory. It recovers the actual saved fold from the prerequisite records and charges their original times. The scientific costs exclude creating test fixtures and recording the independent audit for every arm. [Source export](source_fold.py) · [Frozen file fingerprints](../../artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/freeze.json)

```sh
s=FOLD-REUSE-20261115-001
f=${s}-E001_second_learner
out=$(mktemp -d)
.venv/bin/python -B "research/$s/source_fold.py" --out "$out"
.venv/bin/python -B "research/$s/assess.py" bind --out "$out"
.venv/bin/python -B scripts/longrun.py launch "experiments/$s/$f/job.py" --out "$out" --unit fold-reuse-replay --param "data_dir=$out" --workers 1 --max-cases-per-worker 1 --case-timeout 180 --case-mem 1G --mem-max 2G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$out" --foreground --limit 12
.venv/bin/python -B "research/$s/assess.py" collect --out "$out"
.venv/bin/python -B "research/$s/audit.py" --out "$out"
```
