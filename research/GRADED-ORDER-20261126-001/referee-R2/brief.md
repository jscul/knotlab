# Referee brief GRADED-ORDER-R2

You are refereeing the second part of one study of this repository, `GRADED-ORDER-20261126-001`, at the owner's standing
request. Keep it lean: well under two hours of compute in all.

## The question

Ordinary growth (the look-alike study's growth, `research/LOOK-ALIKE-20261126-001/alike.py`) is claimed to be read from
a start's finite map as follows: build the births of the start's finite core round by round with the rule of Lemma R
(`proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md`, items 1 and 3), starting from the
round-1 groups, each birth a node; then count births along endless chains and the relay of a finished piece as
`research/LATE-VIEWS-20261126-001/late.py` does. Is it right on every start of the late-views class, both readings, both
knot laws? Where it fails, why? And is this argument right: "if no two core births of one round share two parents C and D
with a chain based at a point of a common parent of C and D, the core's births are the round rule iterated on core
births alone"?

## Steps

1. **Answer it yourself first**, with your own code and argument in your folder (you may call the growth as a black box;
   write your own core construction, chain counting and comparison): test the reading on starts you draw yourself
   (another seed or weighting, and eight knots or more), and try to prove or refute the argument.
2. **Then read the study**: `research/GRADED-ORDER-20261126-001/README.md` (from "The order lemma and a reading for the
   exception" on), `decision.md`, `order.py`, `twins.py`, `witness_nodes.py`, the held-out samples and scores
   (`held*_*.jsonl`, `nodesg_*.jsonl`, `held_tally.txt`). Compare: the construction, the relay rule, every count, the
   proof steps and what is marked proved or computed, and whether it reduces to the identification of
   `proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/proof.md` inside that class.
3. **Press hardest on** a start where the reading fails other than the two recorded misses, and on the decoupling
   argument.

## Stop

Stop when you can give a verdict. Write `research/GRADED-ORDER-20261126-001/referee-R2/report.md`: the first line after
the title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); then
what holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a
block), the exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/GRADED-ORDER-20261126-001/referee-R2/`. Edit no other file. Do not commit,
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
