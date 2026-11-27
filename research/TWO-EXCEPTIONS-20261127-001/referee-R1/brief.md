# Referee brief TWO-EXCEPTIONS-R1

You are refereeing one study of this repository, `TWO-EXCEPTIONS-20261127-001`, at the owner's standing request. Keep it
lean: well under an hour of compute in all.

## The question

`research/TWO-EXCEPTIONS-20261127-001/README.md` claims, without growing: (1) on every sample start where the order lemma
for extended nodes fails (`research/CHAIN-COUNT-20261127-001/proof.md`, Lemma X), the first families that break it are
of two kinds only, the chained-twin family and the lift split; (2) the share of accepted starts in the proved class
N1-N3, and of each exception, under the weightings `tree+` and `grow` at seven to eleven knots (the table there). Is
each right? Is the classifier in `shapes.py` sound (could a third kind be labelled as one of the two)? Do the counts
depend on the caps?

## Steps

1. **Answer it yourself first**, with your own code in your folder (do not import `shapes.py`, `counts.py`, `ext.py`,
   `order.py` or `twins.py`): rebuild the node core and the extended nodes, find the first failing round on the failing
   sample starts and the referees' witnesses listed in `referee_witnesses.jsonl`, and describe the families yourself.
   Redraw a part of the counts (another seed is welcome) and check the class shares.
2. **Then read the study** and compare: every count, the classifier, the caps, and whether "nothing else seen" is worded
   within its evidence. Try to find a start whose first failure is neither kind.

## Stop

Stop when you can give a verdict. Write `research/TWO-EXCEPTIONS-20261127-001/referee-R1/report.md`: the first line after
the title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); then
what holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a
block), the exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/TWO-EXCEPTIONS-20261127-001/referee-R1/`. Edit no other file. Do not commit,
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
