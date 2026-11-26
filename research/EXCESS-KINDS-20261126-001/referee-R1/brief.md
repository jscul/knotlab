# Referee brief EXCESS-KINDS-R1

You are refereeing one study of this repository, `EXCESS-KINDS-20261126-001`, at the owner's standing request. Keep it
lean: well under two hours of compute in all.

## The question

For laws that read no values (every birth decided by which knots share which distinctions, never by a value), is every
table recorded in this repository whose CHSH value (or Mermin-type value) exceeds the classical bound of one of these
kinds: (a) separate responses whose counting multiplies an old state's weight by each reader's number of completions (a
local model with partial rejection); (b) a response depending on both readers' settings; (c) a supplied order, sign,
weighting or reading? Is there a recorded row that fits none? And is this claim true: if each reader's births take
inputs only from its own record and bring fresh distinctions of their own, and each old value of a reader's record is
completed at both of its settings or at neither, then no reader who chooses its setting as a function of its own
visible old values can leave the other reader's complete record unchanged unless the table at fixed settings has CHSH at
most 2?

## Steps

1. **Answer it yourself first**, with your own code and argument in your folder (never import the study's modules):
   try to prove or refute the claim; search the record (`research/`, `experiments/`, `proofs/`, `docs/CORRECTIONS.md`)
   for tables above the bound and class each one; build at least the seven-knot structure of
   `research/THIRD-HOLDER-20261123-001B/result.md` and test whether a reader keying its setting to its own old values
   changes the other's record.
2. **Then read the study**: `research/EXCESS-KINDS-20261126-001/README.md`, `inventory.md`, `decision.md`, `checks.py`
   and its output, register entry A296 in `docs/ASSUMPTIONS.md`, and the advisor's answers in the folder. Compare: every
   step of the proof, every row's kind and evidence, the claim about the whole-stage 9/4 table and the quantum set, the
   claim about counting from the finish (A240), and whether any row fits none.
3. **Press hardest on** a counterexample to the claim, a misclassed or missed row, and any row whose hypotheses fail so
   that it might fit none.

## Stop

Stop when you can give a verdict. Write `research/EXCESS-KINDS-20261126-001/referee-R1/report.md`: the first line
after the title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a
**Block**); then what holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block,
Narrowing, Not a block), the exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/EXCESS-KINDS-20261126-001/referee-R1/`. Edit no other file. Do not commit,
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
