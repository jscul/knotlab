# Referee brief GRADED-ORDER-R1

You are refereeing one study of this repository, `GRADED-ORDER-20261126-001`, at the owner's standing request. Keep it
lean: well under two hours of compute in all.

## The question

A start's growth under ordinary growth (the look-alike study's growth, `research/LOOK-ALIKE-20261126-001/alike.py`) was
read round by round from the start's finite map by the late-views study's graded-order reading
(`research/LATE-VIEWS-20261126-001/late.py`, class `GeneralPiece`, `predict(..., general=True)`): the valid sets of the
map ordered by inclusion, a birth's parents the valid sets it covers, its fresh distinctions the valid sets covering it
plus one per chain. Is it true that the reading gives every round of a start, in both readings and under both knot laws,
exactly when no valid set (of rank two or more) has two parents that share no parent and no two round-1 group cells share
two knots? Where it fails, why?

## Steps

1. **Answer it yourself first**, with your own code in your folder (you may call the growth and the reading as
   black boxes, but write your own flags, sampling and comparison): draw fresh starts of your own (another seed, and if
   you can another weighting or eight knots), grow them, and test the claim both ways.
2. **Then read the study**: `research/GRADED-ORDER-20261126-001/README.md`, `decision.md`, `graded.py`, the samples and
   scores (`fresh7_*.jsonl`, `grown_*.jsonl`, `scored_*.jsonl`, `replays.jsonl`), register entry A301 in
   `docs/ASSUMPTIONS.md`, and the advisor's answer. Compare: the flags' code, the deduplication, the scoring, every
   prediction's verdict, and the statement to prove.
3. **Press hardest on** a start where the claim fails in either direction, and on whether the statement to prove and the
   order lemma are stated right.

## Stop

Stop when you can give a verdict. Write `research/GRADED-ORDER-20261126-001/referee-R1/report.md`: the first line after
the title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); then
what holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a
block), the exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/GRADED-ORDER-20261126-001/referee-R1/`. Edit no other file. Do not commit,
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
