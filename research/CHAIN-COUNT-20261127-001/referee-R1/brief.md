# Referee brief CHAIN-COUNT-R1

You are refereeing one proof of this repository, `CHAIN-COUNT-20261127-001`, at the owner's standing request. Keep it
lean: well under two hours of compute in all. The proof was written without its usual advisor review, so check every
step.

## The question

`research/CHAIN-COUNT-20261127-001/proof.md` claims: on a start of the late-views class whose node core (the start's core
births built by Lemma R's round rule from the round-1 groups and offshoots, `research/GRADED-ORDER-20261126-001/order.py`,
`NodePiece`) satisfies N1 (no chained twins), N2 (lifts meet) and N3 (base-holding families close), ordinary growth's
births of every round, with their parents and fresh counts, are the extended nodes defined there. Is it right? Is every
lemma (A, B, C, D, X, F) proved as stated, and does the induction close, including the implied rule and the relay? Do
N2 and N3 follow from N1?

## Steps

1. **Answer it yourself first.** Read the setting and the theorem only, then try to prove or refute it in your own
   folder: write your own construction of the node core and of the extended nodes (do not import `order.py`, `ext.py` or
   `twins.py`), and test the theorem against ordinary growth (`research/LOOK-ALIKE-20261126-001/alike.py`, as a black
   box) on starts you draw or build yourself, including starts with many group cells and with chains. Try hardest to
   build a start without chained twins on which N2 or N3 fails, and a start in the class on which the theorem fails.
2. **Then read the proof** line by line, with `research/CHAIN-COUNT-20261127-001/README.md`, `ext.py`, `convex.py` and
   the check outputs, and the sources it follows: `proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/proof.md`
   (Lemmas 4 and 5, the proof of Theorem 1), `proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md`
   (Lemma R) and `research/GRADED-ORDER-20261126-001/referee-R2/report.md` ("Why the conditional core theorem holds").
3. **Press hardest on** Lemma A's three sharing types, Lemma D's case analysis (two chain totals, and one total with one
   vector), the coverage argument used in Lemma F, and whether the class's conditions are really read off the start.

## Stop

Stop when you can give a verdict. Write `research/CHAIN-COUNT-20261127-001/referee-R1/report.md`: the first line after
the title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); then
what holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a
block), the exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/CHAIN-COUNT-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout: do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 8 worker processes and 16 GB in all. Time a small part at the exact
  configuration before any run. A run finishes in about an hour: cut a longer one to a stated prefix or to a sample with
  a stated seed, and report what was not run as "not run". Use the repository's `.venv/bin/python`.
- **Independence.** The proof was drafted by another agent. A refutation is as welcome as a confirmation; do not soften
  a finding, and do not invent one.
- **Words.** Use the glossary's words (`publication/knotlab/INTUITIONS.md`, Glossary): distinction, knot, shared
  distinction, loose distinction, sample, weighting. Say "knot". Do not name the program's own objects by words from a
  space of two or three dimensions. Never call anything typical, rare or likely without naming its weighting. Do not use a
  study label or a start number without saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or breaking
  cryptography, write nothing about it in the repository and say so in your final message only.
