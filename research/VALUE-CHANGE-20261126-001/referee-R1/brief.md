# Referee brief VALUE-CHANGE-20261126-001-R1

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute; cut a longer check
to a seeded sample and report the rest as not run). You are refereeing the study `VALUE-CHANGE-20261126-001` (reading a
change: whether it is native, and what it gives separated readers on joined-ring starts), closed 26 November. Read its
decision, README and preregistration, register entry A300 in `docs/ASSUMPTIONS.md`, the rule-R study
`EVENTUAL-R-20261126-001` (refereed) and `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails").

**Order of work.** Rebuild independently, with code you write:
1. Part A: the commutation conditions on settled pairs of births to six rounds (sample a part if needed), the fifth
   class, and the claim that every structure with six rounds of births fails under rule R; the eight- and sixteen-knot
   closures under the two symmetry restrictions; the per-knot lists on the ten closers.
2. Part C: the separability argument (is it right? a counterexample?), e on the separated pairs with the middle unread,
   read for values and read for changes, and the square: are its nine cells certainties of the sorted state, do its rows
   and columns commute, and is the game's win really certain against 8 of 9 for a list of values?
3. Part B and the verdict: whether "nothing native reads a change", "a list of values reproduces values and changes read
   alone", and the event-ready reading of the middle (not communication) are worded within their evidence; whether any
   claim of novelty is made where the literature has the result.
Say what you did not reach.

## Your job

Write `research/VALUE-CHANGE-20261126-001/referee-R1/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/VALUE-CHANGE-20261126-001/referee-R1/`. Edit no other file. Do not
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
