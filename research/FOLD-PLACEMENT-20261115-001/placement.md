# What changes when the solver knows one group of three

On November 15, 2026 we compared 48 exact Boolean rules at nine essential inputs. Blind repeated grouping returned 168 uses of the supplied operation, including 24 calls taking two or three computed arguments. The same search given a single group used 739 candidate tests against 1,842 blind. The blind named solver missed the prespecified time gate. Only the informed named solver passed. The [design](preregistration.md) therefore selected one further investigation at this width into finding a group from an ordinary pair.

| Method | Warm verified stream, elapsed | Warm verified stream, process CPU | Candidate tests | Repeated group tests |
| --- | ---: | ---: | ---: | ---: |
| Original direct primitives | 484.74 ms | 178.39 ms | 6,160 | 0 |
| Direct named fold, blind | 383.62 ms | 188.50 ms | 8,846 | 0 |
| Direct named fold, one group | 184.96 ms | 117.29 ms | 2,085 | 48 |
| Repeated grouping, blind primitives | 217.19 ms | 115.40 ms | 1,828 | 1,794 |
| Repeated grouping, hinted primitives | 280.81 ms | 109.04 ms | 725 | 691 |
| Repeated grouping, blind named fold | 206.63 ms | 110.76 ms | 1,842 | 1,794 |
| Repeated grouping, hinted named fold | 105.59 ms | 104.40 ms | 739 | 691 |
| Repeated grouping, blind inline fold | 208.32 ms | 113.97 ms | 1,842 | 1,794 |
| Repeated grouping, hinted inline fold | 234.50 ms | 111.38 ms | 739 | 691 |

The table gives medians of five complete streams. The previous unwrapped direct solver was slower here than a primitive solver that can repeatedly contract an anonymous group. The blind named solver's 4.9% reduction in elapsed time against that stronger comparator won two of five paired repeats. The hinted named arm's 51.4% elapsed saving won four of five, with a 9.5% CPU saving. The equivalent inline search took exactly the same placements as the named search. Its hinted elapsed time rose and its CPU fell. The size of the named arm's wall-clock saving is consequently unreliable. Resetting caches for every task also removed the apparent named wall-time win. All thirteen arms and the individual repeats are in the [paid results](../../artifacts/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs/result.json).

## What the hint told the solvers

A group contains just three sorted input indices. Each solver derives which of the eight local assignments can share one bit and builds the residual program from the target table. A row mask compares aligned residual functions for a candidate group, and the group is rejected as soon as there are three different residuals. There were **122 one-bit groups among 4,032 possible raw triples**, about 3.0%. The public hint was one of them in all 48 rules. With the repeated search it reduced candidate trials at depths two, three and four from 521, 723 and 598 to 218, 330 and 191 for both library arms. Primitives alone saved exactly the same 1,103 triple tests on the full panel.

The blind repeated library search used the saved operation 168 times. It joined two computed arguments in 22 calls and three in two more. Hinted search did so in 28 and three calls respectively. The blind raw-pair direct library solver made 151 calls, all with at most one computed argument. Within this experiment, the more general solver could bring independently computed subprograms together. Establishing their grouping took work. [Solver](../../experiments/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs/placement.py)

## Population and limits

The 24 positive cases exhaust the 13 four-copy functions up to input renaming. Only one positive structure has minimum four-copy height two, eight have minimum height three, and four have minimum height four. The associated 24 negative cases replace one site while preserving all nine inputs and the count of four AND and four XOR gates. Four out of eight edits per height change the local answer of the hinted group. Every negative excludes a complete cover by four unaltered copies. At depth four two edits change the output density. All 48 labelled truth tables are fresh relative to the 36 distinct archived nine-input functions. Four of eight middle-height and all four deepest positive structures already occur up to renaming in the archives. The depth-two cases repeat the same structure with new labels. The results file contains subgroup counts for each distinct structure. [Task construction and census](tasks.py)

Each of the 4,992 returns was verified over the original 512 assignments, including the balanced branch in which three computed answers supply the fourth operation. The given library costs zero acquisition in this diagnostic. All failed placements and physical verification are charged; the referee and fixture producer are outside both bills. The [frozen inputs and sources](../../artifacts/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs/design.json) bind the comparison. The scheduled design advisor reported its weekly usage limit. A separate referee checked the census and pointed out the depth aliases and the need for an equally informed primitive solver.

Independent scalar replay checked 2,555,904 program inputs and 61,341,696 individual NAND evaluations. Every emitted circuit had 24 NANDs. All 1,536 matched named/inline pairs had the same physical dependency structure, with different emission orders allowed. The referee independently recovered the 13 positive classes and minimum heights, the whole candidate-work ledger and the hint-only decision. [Independent replay and timing sensitivity](../../artifacts/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs/audit.json)

Run `python3 -B research/FOLD-PLACEMENT-20261115-001/assess.py` to reproduce the scores. To repeat the timed work in a fresh directory, run the experiment's `bind.py OUT`, then use `scripts/longrun.py launch` with its `job.py`, `--out OUT --unit fold-placement-replay --workers 1 --max-cases-per-worker 1 --case-timeout 120 --case-mem 1G --mem-max 2G --param data_dir=OUT --prepare-only`, followed by `python3 -B scripts/longrun.py run --out OUT --foreground`.
