# Referee brief FACTOR-WEIGHTS-20261126-001-R1

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute). You are refereeing
`FACTOR-WEIGHTS-20261126-001` (whether the record's weightings factor over knots, the one way out of the separability
argument of `THIRD-READER-20261126-001`), closed 26 November. Read its decision, README and preregistration, register
entry A304, the definitions of `TWO-COUNTINGS-20261125-001`, and `AGENTS.md`.

**Order of work.** Rebuild independently:
1. Part A: on a seeded sample of small grown census starts, the two countings (from the finish; from the start with
   rounds as stages, renormalised under the cut arms) against the rank-one test for pairs no knot holds together, and the
   one-stage control that should fail. Is "every weighting the model makes factors over knots" right, and is anything in
   the record (the waiting engine, the cut arms, start values) a counterexample?
2. Part B: on the third-layer referee's three rings of four, the restricted e under the three treatments, the local
   flips, and the controls (one of which failed as predicted by the advisor).
3. Part C: the event-ready square on sampled starts (13 of 300 with one shared pair, none with two), and the repeated-name
   bug in the frozen run.
4. Whether "this line stops" follows, and whether any claim of novelty is made where the literature has the result
   (Markov random fields; graph-state separability).
Say what you did not reach.

## Your job

Write `research/FACTOR-WEIGHTS-20261126-001/referee-R1/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/FACTOR-WEIGHTS-20261126-001/referee-R1/`. Edit no other file. Do not
  commit, stage, stash, reset, switch branches or push. Other sessions are working in this checkout: do not stop
  any process you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 8 worker processes and 16 GB in all. Time a small part at the
  exact configuration before any run. A run finishes in about an hour, two at the outside: cut a longer one to a
  stated prefix or to a sample with a stated seed, and report what was not run as "not run". Use the repository's
  `.venv/bin/python`.
- **Independence.** The study was drafted and closed by another agent. A refutation is as welcome as a
  confirmation; do not soften a finding, and do not invent one.
- **Words.** Use the glossary's words: distinction, knot, shared distinction, loose distinction, sample, weighting.
  Say "knot". Do not name the program's own objects by words from a space of two or three dimensions. Never call
  anything typical, rare or likely without naming its weighting. Do not use a study label or a start number without
  saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or
  breaking cryptography, write nothing about it in the repository and say so in your final message only.
- **No claims** about physics, minds, living things, time or space from this work.

When the report is written, end with a final message of at most fifteen lines: the verdict, each fix with its
verdict in one line, and what was not run.
