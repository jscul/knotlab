# Referee brief SECOND-SWITCH-R1

For an independent referee, at the owner's standing request. You are refereeing one closed study of this repository:
`SECOND-SWITCH-20261126-001`, "after both exist, can the far pattern change the switch receiver's course?". It is
closed and all its results are computed and marked "referee pending". Its register entry is A282 in
`docs/ASSUMPTIONS.md`. Its growth engine is that of `SHORT-AGAIN-20261126-001` and its receivers those of
`SWITCH-RECEIVERS-20261126-001`, which have their own referee jobs (do not referee those; say if a fault in their
programs changes a count here).

**Order of work.** The coming apart first (it is the stated reason), then the negative's counts, then the contrast
under one fewer, then the rest. Say plainly what you did not reach.

**Points beyond the hand-off's.**
- Write your own growth and your own reading of parts and of linked parts from the record's definitions; regrow a
  sample of the runs with a stated seed and compare round by round.
- Is the fold study's argument (stated there for laws with takes) sound for these laws with nothing taken and short
  knots that wait, and is "linked" (a member of each part holding one distinction) the right test for "share
  nothing"? If the argument has a gap, find a case.
- Is "not heard" ever censored by the knot bound before a hearing could have arrived (count those cases)?
- Scaffolds (A282, A224, A277): for each result, model or scaffold, with a cheap swap where feasible.

## Your job

1. **Read the hand-off.** `research/SECOND-SWITCH-20261126-001/referee_handoff.md` lists each claim, where its code and
   data are, and what to press. Read what it links: `decision.md`, `README.md`, the advisor's question and answer,
   and the predecessor's `research/SHORT-AGAIN-20261126-001/JAM.md` (the switch's first finding). Read `AGENTS.md` ("Canonical foundation", "Research
   discipline", "Guardrails") and the glossary at the end of `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's reading or analysis modules.
3. **Press.** Take the points above and the hand-off's, then look for what they do not list:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (the jam study's rule was
     the note's reason changed after the first table: receding first, then coming apart once far ends that keep a
     waiting member were also not heard; check that each stated reason is supported by the runs it cites);
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "exactly" claim that almost nothing could have contradicted (count the cases that could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains (a count, the first round, a numbering, a name);
   - a headline, summary, goals row or register line that says more than the tables do;
   - earlier work in the program that already has the result.
4. **Report.** Write `research/SECOND-SWITCH-20261126-001/referee-R1/report.md`:
   - first line after the title, the verdict: **Confirmed**, **Confirmed with fixes** or **Refuted**, and whether
     there is a **Block**;
   - **What holds**, claim by claim, each with the count you obtained and whether you rebuilt it or only read it;
   - **The fixes**, each with its verdict (**Block**: what the study stood on is false; **Narrowing**: true only in a
     smaller scope or for another reason; **Not a block**: wording or credit), the exact sentence and file to change,
     and the evidence;
   - **Scaffolds**: per result, model or scaffold, and what you swapped;
   - **What was not run**, never as a negative;
   - **How it was checked**: your files, and the commands that rerun them.
   Keep the report to what a reader needs to act on it. Put tables of counts in JSON files beside it.

## Rules

- **Where you write.** Only inside `research/SECOND-SWITCH-20261126-001/referee-R1/`. Edit no other file. Do not
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
