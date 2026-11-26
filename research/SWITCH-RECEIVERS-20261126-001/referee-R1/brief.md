# Referee brief SWITCH-RECEIVERS-R1

For an independent referee, at the owner's standing request. You are refereeing one closed study of this repository:
`SWITCH-RECEIVERS-20261126-001`, "which receivers switch their way of growing on what is at the far end of a line,
under a cap". It is closed and all its results are computed and marked "referee pending". Its register entries are
A282 and A224 in `docs/ASSUMPTIONS.md`. Its growth engine and joins are those of `SHORT-AGAIN-20261126-001`, which has
its own referee job (do not referee that study; say if a fault in its programs changes a count here).

**Order of work.** The census's headline first (six of 646 receivers switch under the cap of three, one kind, at round
2d + 1 when the far site holds two loose distinctions), then the rule's test at caps six and seven, then the
controls, then the rest. If time is short, a complete check of the headline and the rule is worth more than a thin
pass over everything; say plainly what you did not reach.

**Points beyond the hand-off's.**
- Write your own growth from the record's definitions (the ordinary count, caps of three to seven, the record's one
  fewer, waiting with release, the meeting through link knots, the stub) and regrow a sample of receivers with a
  stated seed; compare every round's own births with the recorded runs (`*.jsonl.gz`). Where you fall back on the
  study's engine, say so and say what you checked it against.
- "One kind": check that the six receivers' own births are really the same with every sender, and why five starts of
  four knots grow exactly as the three-knot one does (is a knot inert, or is the reading too coarse?).
- The filter "no own knot short before" and the bands (before d, d to 2d, after 2d): count how many receivers could
  have switched under each law (read after round 2d at all).
- The rule: is "the site has exactly k places" the right statement, or does another feature (the site's loose count,
  its sharings, the others' loose counts) sort the receivers as well? Try one or two other starts that fit or break
  the statement.
- Scaffolds (A282, A224, A277): for each result, say whether it survives a different choice of each scaffold it
  depends on (another set of senders, another join, another site), so whether it is about the model or about the
  scaffold. If a cheap swap is feasible, run it on a small sample and report it.

## Your job

1. **Read the hand-off.** `research/SWITCH-RECEIVERS-20261126-001/referee_handoff.md` lists each claim, where its code and
   data are, and what to press. Read what it links: `decision.md`, `README.md`, the advisor's question and answer,
   and the predecessor's `research/SHORT-AGAIN-20261126-001/JAM.md` (the switch's first finding). Read `AGENTS.md` ("Canonical foundation", "Research
   discipline", "Guardrails") and the glossary at the end of `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's reading or analysis modules.
3. **Press.** Take the points above and the hand-off's, then look for what they do not list:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (the jam study's rule was
     read from the first pass of the census and then tested on caps of six and seven; check that the note's rule
     section was written before `rule.py` ran, using the git history of the note if it helps);
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "exactly" claim that almost nothing could have contradicted (count the cases that could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains (a count, the first round, a numbering, a name);
   - a headline, summary, goals row or register line that says more than the tables do;
   - earlier work in the program that already has the result.
4. **Report.** Write `research/SWITCH-RECEIVERS-20261126-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/SWITCH-RECEIVERS-20261126-001/referee-R1/`. Edit no other file. Do not
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
