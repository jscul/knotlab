# Referee brief CAPPED-CORES-R1

You are refereeing one study of this repository, `CAPPED-CORES-20261127-001`, at the owner's standing request. Keep it
lean: well under an hour of compute in all.

## The question

`research/CAPPED-CORES-20261127-001/README.md` certifies, without growing, what the node cores over the cap are: of 221
certified capped cores under `tree+` and `grow`, 219 grow by a steady factor, one finishes by the "subset pattern", none
repeats. Is the subset-pattern certificate proved (a rank whose m births all share one parent is followed by all their
sets of k + 1, ending after 2^m - m - 1 more births)? Is the repeat test sound (does an isomorphic parent incidence
between consecutive ranks really force the round rule to repeat)? Are the counts right, and is "unending is shown for
none" the right reading? Is the intuition (growth constants of cluster counts on the unrolled map of a piece with two or
more cycles) testable as stated?

## Steps

1. **Answer it yourself first**, with your own code in your folder (do not import `certify.py` or the study's code): prove
   or refute the two certificates, rebuild the node core of a few capped starts (redraw them from the stated seed) and
   classify them; try to certify unbounded growth for one.
2. **Then read the study** and compare every count and claim.

## Stop

Stop when you can give a verdict. Write `research/CAPPED-CORES-20261127-001/referee-R1/report.md`: the first line after
the title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); then
what holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a
block), the exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/CAPPED-CORES-20261127-001/referee-R1/`. Edit no other file. Do not commit,
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
