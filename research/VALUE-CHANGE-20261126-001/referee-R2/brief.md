# Referee brief VALUE-CHANGE-20261126-001-R2 (supplementary)

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute). A first referee
(R1, in `research/VALUE-CHANGE-20261126-001/referee-R1/`, running separately; do not read or touch its folder) checks the
study as a whole. You answer three questions only, about the study `VALUE-CHANGE-20261126-001` (read its decision,
README, preregistration, `css.py`, `rings.py`, register entry A300 in `docs/ASSUMPTIONS.md`, and `AGENTS.md`):

1. **Break "sends no signal".** The study says its square of certainty for readers who share no knot (one reader
   holding rings 0 and 2, the other ring 1, a middle reader reading changes whose record sorts the table) signals
   nothing. Try to break it: with the middle's record used to sort, can either reader's sorted record depend on the
   other reader's setting? Does the middle's record depend on the readers' settings? Build the full tables on one
   family and check every marginal, sorted and unsorted.
2. **Break "sits at the quantum value".** Is the table a quantum one (realised by a state and commuting local reads), is
   the game's value 1 the quantum maximum, and is anything in the study above what a quantum state allows?
3. **Is the coherent state supplied?** The study weights every allowed state equally and relates every two equally (the
   equal superposition). Does that follow from the equal counting the model already uses (the counts fix only the
   weights of single states), or is it one more supplied choice? Name the other states with the same counts (the
   mixture, other phases) and whether any of them gives the square.
The three supplied pieces the study names are the coherent state, combined questions (a change of one set read with a
value of another) and the middle reader who sorts; keep them named in every statement.

## Your job

Write `research/VALUE-CHANGE-20261126-001/referee-R2/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/VALUE-CHANGE-20261126-001/referee-R2/`. Edit no other file. Do not
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
