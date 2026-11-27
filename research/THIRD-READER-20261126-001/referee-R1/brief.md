# Referee brief THIRD-READER-20261126-001-R1

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute). You are refereeing
`THIRD-READER-20261126-001` (the middle of the joined-ring starts as a third reader, to remove the sorting of the
change-read study's square), closed 26 November. Read its decision, README and preregistration, register entry A302,
the change-read study `VALUE-CHANGE-20261126-001` (refereed twice) and `AGENTS.md`.

**Order of work.** Rebuild independently:
1. Part A: the separability argument for any number of readers whom no knot joins (right? counterexample? its stated
   scope: any amplitude that is a product of one factor per knot).
2. Part B: the triple counts g on the five families, and the three-reader game at round 0 (win 1 on three families, 3/4 on
   the loose chain). Try to break "no reader or pair of readers sees another's setting" and "at the quantum value".
3. Part C: the contact list (the middle hearing both ring settings) gives the same table: is that right, and does it
   settle that the game is no fairer than the sorted square?
4. Part D: the real-reads lemma and search (no game of certainty with positive amplitudes and real reads), and the
   positive control.
5. Part E: is there any place in ordinary growth where a birth's law depends on two allowed states of its parents?
Say whether the supplied pieces (the coherent counting state, combined questions, the middle reader, the quarter-turn
read) are named in every statement, and what you did not reach.

## Your job

Write `research/THIRD-READER-20261126-001/referee-R1/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/THIRD-READER-20261126-001/referee-R1/`. Edit no other file. Do not
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
