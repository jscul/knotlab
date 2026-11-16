# Which part of a logical rule can the next task reuse?

On 2026-11-14 we replayed four source searches from Lesson 4.7. We gave the next learner the resulting local tables and the order of the copies. We withheld which of two distinctions each copy passed on. One target answer per copy identified the entire joined function on this panel. A plain truth-table learner given the same information made exactly the same queries. This is an exploratory, reproducible result about transfer within a specified family.

| Copies | External input assignments per task | Distinct target functions | Target labels used per task | Correct predictions on all remaining inputs |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 32 | 4 | 2 | 120 / 120 |
| 3 | 128 | 8 | 3 | 1,000 / 1,000 |
| 4 | 512 | 16 | 4 | 8,128 / 8,128 |

Every target came from the complete signed constraints, with the internal distinctions quantified away. A separate implementation checked both output values under every external input. Each query had a binary answer, so distinguishing 16 functions requires four answers in the worst case. The four-copy learner reached that bound on every task. To choose queries, it evaluated all 16 supplied alternatives on all 512 inputs in advance. The label savings come with that computation and a strong restriction on the possible targets. A single changed answer at an unqueried input preserved the query transcript and defeated its prediction on every target tested.

## What the fold kept

The four sources were the original bare-pattern seeds 9000–9003. None was selected for its result in this experiment. All four reproduced their original first stop and the read after the disturbance. They took 51,400 search steps and 91 probes in total. The source examples acted as a stopping test. A later audit found no demonstrated advantage of example-guided source search over blind search. [Source audit](../SEARCH-AUDIT-20261112-001/search_audit.md)

We enumerated 256 candidate states per source. Eight states were allowed in each. Three input distinctions determined the value at read 5 and also at read 6. On seed 9000 the inputs `000` and `011` both give 0 at read 5. At read 6 they give 1 and 0 respectively. For each of the four sources, collapsing inputs by the first read leaves two classes. Retaining both reads requires four distinguishable classes. Even the best predictor using read 5 alone gives the right value at read 6 for only six of eight uniformly weighted inputs.

This gives the compression analogy a quantitative meaning. One fixed-width bit suffices for read 5, while two suffice and are necessary for perfect recovery of both reads. Under uniform inputs the four joint outcomes occur 3, 3, 1 and 1 times. Their Shannon entropy is about 1.811 bits per sample. This latter number concerns average coding of repeated observations. The exact class count concerns which distinctions a later logical task can still use. [3Blue1Brown on entropy](https://www.youtube.com/watch?v=l6DKRf-fAAM)

## What was supplied

The chain shape, copy boundaries, input places and two possible reads were given. The learner inferred the hidden choices from requested target outputs. For all-5 wiring ordinary XOR gives every answer directly. A deliberately corrupted entry in the first source table made 4, 16 and 64 external predictions wrong at lengths two, three and four. Breaking the first join allowed both terminal values on every external input.

The earlier whole-pattern search found the five-input task in all ten runs and reached the time cap in all ten seven-input runs. Here separate, already found local laws sufficed for the designated joined tasks. The training data and prior information differ between those comparisons, so no wall-clock speedup over that search follows. The plain-table control matched this learner on all 96 target queries. Earlier work on learning libraries of reusable programs provides a stronger reference for discovering the abstractions themselves. [Original joined experiment](../SHARED-COUNT-20261111-001/shared_count.md) · [DreamCoder](https://dspace.mit.edu/entities/publication/86d768ab-558f-4fb1-b92e-9288de643ccb)

A related experiment trained an agent to choose a local fold on the parity read. With sight and action reach fixed at one rule-to-rule step, the frozen policy applied the supplied fold two or three times on longer chains after an investigator chose a length-independent way to report the available action budget. [History, radius comparisons and repeated-fold results](../LOCAL-RULE-ACTIONS-20261114-001/local_agent.md)

## Reproduce

From the research checkout:

```sh
PYTHONHASHSEED=0 .venv/bin/python -B experiments/FOLD-TRANSFER-20261114-001/FOLD-TRANSFER-20261114-001-E001_hidden_reads/job.py
```

The command replays the four source searches and recomputes the raw and compressed predictions, query histories, counterexamples and stored digests. The original complete run took 71 seconds including setup; the three target panels after setup used under a tenth of a second in total on this host. The independent whole-pattern checker was written within this research task. [Frozen design](preregistration.md) · [Raw results](../../artifacts/FOLD-TRANSFER-20261114-001/FOLD-TRANSFER-20261114-001-E001_hidden_reads/results.jsonl) · [Independent checker](whole_pattern.py)
