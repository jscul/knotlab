# Referee brief LINKED-UNDER-CAP-R1

For an independent referee, at the owner's standing request. You are refereeing one closed study of this repository:
`LINKED-UNDER-CAP-20261126-001`, "two patterns that stay linked under a cap: can the far one then change the
receiver's course after both exist?". It is closed and its results are computed and marked "referee pending". Its
register entries are A224, A277 and A282 in `docs/ASSUMPTIONS.md`. Its growth engine and readings are those of
`SHORT-AGAIN-20261126-001`, `SWITCH-RECEIVERS-20261126-001` and `SECOND-SWITCH-20261126-001` (refereed; do not referee
those, but say if a fault in their programs changes a count here).

**Order of work.** "Once, then never" first (a change after both exist heard in 112 of 112 linked switch-kind pairs, a
second in none of 293), then the census's necessity count (0 of 64,527 unlinked), then the rest.

**Points beyond the hand-off's.**
- Write your own growth, parts, classes and "linked" reading from the record's definitions; regrow a sample of pairs
  with a stated seed and compare round by round, then the second pass on a sample of linked pairs.
- "A second change is never heard": is it placed where a hearing could arrive within the rounds read (t0 + s + 1 ≤ 32)?
  Try other places for the second change (other linked members, the far end's site, a member nearer the receiver) and
  other rounds; one heard second change refutes the claim.
- Why does the first change end the link? Trace one pair if feasible.
- Scaffolds (A224, A277, A282): the meeting, the caps, the place and sign of the change; a cheap swap where feasible.

## Your job

1. **Read the hand-off.** `research/LINKED-UNDER-CAP-20261126-001/referee_handoff.md` lists each claim, where its code and
   data are, and what to press. Read what it links: `decision.md`, `README.md`, the advisor's question and answer,
   and the predecessor's `research/SHORT-AGAIN-20261126-001/JAM.md` (the switch's first finding). Read `AGENTS.md` ("Canonical foundation", "Research
   discipline", "Guardrails") and the glossary at the end of `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's reading or analysis modules.
3. **Press.** Take the points above and the hand-off's, then look for what they do not list:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (the jam study's rule was
     the second pass ("Sent again") was designed after the first two caps of the census had been read; check its
     expectations were written before it ran and are graded as written);
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "exactly" claim that almost nothing could have contradicted (count the cases that could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains (a count, the first round, a numbering, a name);
   - a headline, summary, goals row or register line that says more than the tables do;
   - earlier work in the program that already has the result.
4. **Report.** Write `research/LINKED-UNDER-CAP-20261126-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/LINKED-UNDER-CAP-20261126-001/referee-R1/`. Edit no other file. Do not
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
