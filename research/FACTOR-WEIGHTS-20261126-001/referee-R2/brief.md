# Referee brief FACTOR-WEIGHTS-20261126-001-R2 (supplementary)

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute). A first referee
(R1, in `research/FACTOR-WEIGHTS-20261126-001/referee-R1/`, running separately; do not read or touch its folder) checks
the study as a whole. Your one job: **break "every weighting the model makes factors over knots"** (read the study's
decision, README, preregistration and `countings.py`, the definitions of `TWO-COUNTINGS-20261125-001`, and `AGENTS.md`).
The study checked it exhaustively only on growths of at most two rounds and at most 14 distinctions. Try:
- more rounds (three to six) and larger structures, by an argument from the engines' code or by sampling words (a
  seeded sample) rather than enumerating them;
- the recent line's engine with waiting (`research/SHORT-AGAIN-20261126-001/ring_line.py` and the engine it loads), the
  forbidding arms, takes that give a distinction a third holder, and any other recorded growth law or counting;
- the rank-one test itself (is it the right test of factoring for readers no knot joins?).
Report a counterexample with its smallest case, or the argument and checks that the statement survives, and its exact
scope.

## Your job

Write `research/FACTOR-WEIGHTS-20261126-001/referee-R2/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/FACTOR-WEIGHTS-20261126-001/referee-R2/`. Edit no other file. Do not
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
