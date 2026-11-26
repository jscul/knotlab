# Referee brief TWO-RECEPTIONS-R2 (the parity addendum)

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute). You are
refereeing one addendum of a closed study of this repository: section C of
`research/TWO-RECEPTIONS-20261126-001/README.md` ("Parity's shortage"), committed at `0e332122a3`, with `parity.py`,
`parity_runs.jsonl.gz`, `parity_table.md` and the decision's updated row 1. The rest of the study was refereed in
`referee-R1/report.md` (read it: its first Block is the reason for this addendum).

**Claims.** Under the ordinary count with the parity knot law, with no take and with each recorded take, in the
census's 100 receivers (seed 20261126) against five senders joined by a meeting through two link knots: no knot made
after the start is short in any of 3,221 pairs read (279 not run); no far change after round 3 is heard after round 6;
the only hearings are the cross-part take's, in rounds 4 and 5. And the decision's reading: "in these joined starts
the parity knot law adds no route", so "nothing the recorded laws make has carried a change to a pattern's own knots
late and from afar in these joined starts".

**Order of work.** Check that the parity law was in force in the runs (implied births occur at all? count them), that
the shortage reader counts what it says, and whether the joined starts could make an implied birth that is owed a join
(why the R1 witness's shortage does not appear); then a seeded regrowth of a sample of pairs with your own code; then
whether the decision's reading says more than the counts.

## Your job

Write `research/TWO-RECEPTIONS-20261126-001/referee-R2/report.md`: first line after the title, the verdict
(**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts
and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and
file, and the evidence; what was not run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/TWO-RECEPTIONS-20261126-001/referee-R2/`. Edit no other file. Do not
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
