# Referee brief CYCLE-READ-R1

You are refereeing one study of this repository, `CYCLE-READ-20261127-001`, at the owner's standing request. Keep it
lean: well under two hours of compute in all.

## The question

Ordinary growth (the look-alike study's growth, `research/LOOK-ALIKE-20261126-001/alike.py`) is claimed to be read from
a start's finite map by the **node reading**: build the births of the start's core round by round with the rule of
Lemma R (`proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md`, items 1 and 3) from the
round-1 groups and offshoots, each birth a node; count births along endless chains with the binomial terms of
`research/LATE-VIEWS-20261126-001/late.py`; a piece relays exactly when its core finishes with one last birth holding the
whole piece and it holds no chains. Three claims:

1. **Pieces with a cycle.** On the starts the late-views study counts as having a piece with a cycle, the reading (core
   built to rank 25, no relay when the core does not finish, chains on a core that does not finish not read, cores over
   a cap of 5,000 births not read) agrees with growth in every round read under both knot laws on every start it reads
   that has no **chained twins**, and differs on every start with them.
2. **The twin exception.** The node reading fails exactly on starts with chained twins: two core births of one round
   sharing two parents C and D, with a chain base in the points of a common parent of C and D; and the first difference
   is at the round equal to the least rank of such twins. (A predecessor's referee proved that without chained twins
   the core's groups are those of the core alone; the chain counting is not proved.)
3. **How often a core is unending** under the named weightings (Part 3's table).

Is each right? Where does it fail, and why?

## Steps

1. **Answer it yourself first**, with your own code in your folder (you may call the growth as a black box; write your
   own twin flag and your own core construction, chain counting and comparison, without importing the study's
   `order.py` or `twins.py`): flag chained twins independently and test the twin exception on starts you draw yourself
   (another seed or weighting, and nine knots or more), including starts with chains and no twins, the case where the
   chain counting is what is tested. Try to find a start without chained twins on which the reading fails.
2. **Then read the study**: `research/CYCLE-READ-20261127-001/README.md` (its frozen design, the advisor's changes before
   the freeze, the results), `strata.py`, `tally.py`, `checks45.py`, the samples, scores and growths there, and the code
   it uses in `research/GRADED-ORDER-20261126-001/` (`order.py`: `NodePiece`, `predict_nodes`, `round_rule`; `twins.py`;
   `graded.py`: `draw_twins`, `sample_start`, `grow`). Compare: every count, the strata, the twin flags against yours,
   the caps (are they counts? do they change any verdict?), and the exclusion of earlier samples.
3. **Press hardest on** a miss outside chained twins (above all on starts with chains, where the chain counting is not
   proved), on a chained-twin start that agrees, and on whether the "unending" count depends on the caps chosen.

## Stop

Stop when you can give a verdict. Write `research/CYCLE-READ-20261127-001/referee-R1/report.md`: the first line after
the title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); then
what holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a
block), the exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/CYCLE-READ-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout: do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 8 worker processes and 16 GB in all. Time a small part at the exact
  configuration before any run. A run finishes in about an hour: cut a longer one to a stated prefix or to a sample with
  a stated seed, and report what was not run as "not run". Use the repository's `.venv/bin/python`.
- **Independence.** The study was drafted by another agent. A refutation is as welcome as a confirmation; do not soften
  a finding, and do not invent one.
- **Words.** Use the glossary's words (`publication/knotlab/INTUITIONS.md`, Glossary): distinction, knot, shared
  distinction, loose distinction, sample, weighting. Say "knot". Do not name the program's own objects by words from a
  space of two or three dimensions. Never call anything typical, rare or likely without naming its weighting. Do not use a
  study label or a start number without saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or breaking
  cryptography, write nothing about it in the repository and say so in your final message only.
