# A verified local bit after one consumer changes

On November 15, 2026, both the supplied fold and an unhinted ordinary solver returned the exact minimum on all 72 edits of 36 larger NAND circuits. When given the original physical piece, the fold kept its bit on all 36 preserving edits. It kept that bit and added one existing local wire on all 36 edits requiring two bits. Its median total was **398.361 ms CPU**, compared with **397.038 ms** for the fastest unhinted ordinary solver. Each was faster in four of eight paired timing blocks. The difference was 1.322 ms, about 0.33% of the ordinary total. The experiment did not establish a repeatable end-to-end saving.

## Which work changed

The stronger ordinary solver reads the same wiring and history. It tests which historical group's three inputs feed the changed connection. That test identified one group on all 72 edits, so the location hint carried little practical value here. It computes the minimum width before trying to build a program. If two bits are required, it can use any pair of existing local wires that separate assignments requiring different answers. Both methods share their gates between the two outputs.

| Outcome with original physical piece supplied | Fold | Unhinted ordinary |
| --- | ---: | ---: |
| Correct preserving edits | 36/36 | 36/36 |
| Candidate triples evaluated from truth tables on preserving edits | 0 | 36 |
| Joint residual columns read in those evaluations | 0 | 288 |
| Median CPU for the 36 verified preserving edits, excluding setup | 80.307 ms | 91.606 ms |
| Correct edits requiring two bits | 36/36 | 36/36 |
| Candidate triples evaluated on those edits | 2,100 | 2,100 |
| Joint residual columns read in those evaluations | 6,592 | 6,592 |
| Other groups independently checked to exclude a one-bit solution | 2,064 | 2,064 |
| Median CPU for the 36 verified two-bit edits, excluding setup | 144.417 ms | 137.688 ms |
| Median CPU from startup through all 72 verified returns | **398.361 ms** | **397.038 ms** |

When the bit survived, the fold established the one-bit cut by reusing the existing circuit. It skipped all 36 exact group evaluations. One bit was already the lower bound because each eligible signal affects both outputs. The ordinary solver needed one group evaluation per edit, then returned exactly the same physical program as the fold on all 36. When the bit failed alone, the fold could refine its two old classes by adding an existing bit. That yielded a feasible two-bit circuit immediately. Establishing global minimality still required excluding the other eligible triples. The ordinary procedure found an available pair on all 36 edits in 342 pair trials. The fold inspected 887 possible auxiliary-source occurrences and made additional attempts to reuse existing gate paths. These counters describe different operations.

The independent checker reused old raw NAND values whenever both predecessors identified an already verified expression. It also reused the unchanged upstream prefix and updated only the affected source gates. Every submitted raw circuit agreed with the edited source on every assignment. On **all 72 individual edits**, the supplied fold and the fastest ordinary solver incurred the same counts of raw NAND evaluations, matches to verified expressions and checks of narrower groups. Across the 36 preserving edits, each incurred 1,283 fresh raw evaluations and reused 933 downstream expressions. On the 36 two-bit edits each incurred 1,314 fresh evaluations and reused 1,071 downstream expressions. Each also reused 2,216 prefix gates in each stratum. Keeping the old bit means that a tap in the returned circuit carries its value. Importing a verified source expression into a newly materialized NAND circuit can give the tap a new wire number. Timing medians by phase are computed separately and need not add to the median whole-stream total.

## Gates, histories and matched changes

Three preselected generation seeds supplied 12 parents each. The original circuits had 144–198 NAND gates, two outputs and seven, eight or nine independently attainable intermediate signals. Nine to eleven raw inputs fed the shared prefix. The history contained three distinct triples and two complementary records for each. Both competitors paid to build and validate that history. Each edited version started from the same original, replacing one input of the same internal consumer. Both output functions changed on every edit. In 18 pairs both replacements could distinguish inputs having the same old bit when examined in isolation. The enclosing NAND masked that difference in one version of the pair.

The minimum covers every three-signal set on the declared frontier whose members affect both outputs. At a proposed group, two local assignments may receive the same message precisely when both outputs agree at every setting of the other signals. The verifier checks the reported number of distinct residuals, every necessary alternative and the physical cut. It also replays the resulting NAND program on the raw inputs. There were 86,016 circuit–input combinations across the 72 unique edits. The study measures communication width within this interface. The NAND gate count is constructed heuristically.

## What the other comparisons showed

| Solver | Triple hint, original public ordering | Full physical piece, same public ordering for all arms within this run |
| --- | ---: | ---: |
| Ordinary, prioritizes existing physical cuts | 589.617 ms | 578.236 ms |
| Ordinary, also buys and retains an optimized original circuit | 657.804 ms | 630.937 ms |
| Ordinary physical-cut search, given the location | 556.655 ms | 551.006 ms |
| Ordinary, evaluates widths first, no hint | **415.288 ms** | **397.038 ms** |
| Ordinary, evaluates widths first, given the location | 414.462 ms | 396.821 ms |
| Supplied verified fold | **420.528 ms** | **398.361 ms** |

In the original ordering, supplying the three-input location left two complementary physical records to choose from. The fold selected the complement in 18 parents. Nine of those needed semantic reconstruction on the preserving edit. Their count explains why distinguishing a location from a physical record mattered. The first eight paired runs gave the fold five wins despite its higher whole-stream median. A single, separately recorded timing sensitivity on the same ordering gave it four of eight wins, 426.971 ms versus 407.423 ms. The pooled 16 runs gave 423.728 ms versus 410.371 ms. The full-piece rendering listed the earlier physical wire first within *each* group's two slots, preserving all inputs, gates, edits and group positions. Its source binding checked that the hinted group now supplied the actual original bit on all 36 parents. The six algorithms and the checker were identical across renderings. All methods then retained the ability to use generic wiring and the original DAG. The two renderings reuse the same tasks.

The whole-stream CPU clock starts before solver imports and public input loading and includes original validation, failed proposals, edit propagation, global search, construction, raw linking, independent verification and serialization. Each timing block uses a fresh process on one pinned CPU. Private grading, common task generation and writing research traces fall outside all solver clocks. The first registered stream finished 4.6 seconds after the run configuration was created. Across the three timing comparisons the measured method CPU was 73.19 seconds. The main implementation effort before the first measurement was the shared incremental engine and the verifier for the linked raw program.

An independent replay imported neither solver nor paid checker. For each of the two history orderings it covered 3,744 returns, including the ordinary arm's purchased original circuits, and 4,472,832 raw assignments across those returns. It reused replay results only for identical programs bound to the same actual targets. The replay independently recovered each minimum, each raw output, the timing totals and the unique location from public wiring on 72/72 edits. On the 36 two-bit edits both leading methods returned a tap carrying the old bit or its complement. Literal preservation of the old numeric wire ID together with its full upstream definition occurred on one of the 36 edits of each kind. [Combined audit](../../artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/audit.json)

Neither location hint met the registered speed criterion. The larger training and blind streams were left unopened and no learner was trained. The cheaper step observed in this experiment was accepting an existing one-bit circuit on a preserving edit. The expensive remaining step on a two-bit edit was establishing that every other eligible triple also needs at least two bits. The result is bounded to these generated circuits, the available local history and this edit mix.

The physical-cut and common-subexpression controls follow existing circuit-synthesis practice. This experiment measures verified intermediate width and repair latency. [Mishchenko, Chatterjee and Brayton, *DAG-Aware AIG Rewriting*](https://people.eecs.berkeley.edu/~alanmi/publications/2006/dac06_rwr.pdf)

The secondary design-advisor CLI could not authenticate. The separate reviewer identified the inexpensive dependency-based location control before the stream was opened. The study used that executable control and separate raw-circuit replay.

## Replay

The public circuits, oracle locations, grades, source bindings and every raw returned program are stored together. The primary and full-piece analyses can be recomputed without running or training a solver.

```sh
python3 -B research/PARENT-FOLD-20261115-001/assess.py
python3 -B research/PARENT-FOLD-20261115-001/assess.py --artifacts artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/explicit-piece
python3 -B experiments/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/test_parent_checker.py
python3 -B research/PARENT-FOLD-20261115-001/audit.py --artifacts artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits --include-rendering artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/explicit-piece
```
