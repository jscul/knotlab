# Referee brief TWO-PATTERNS-R1

For an independent referee, at the owner's request of 26 November 2026. You are refereeing one closed study of this
repository: `TWO-PATTERNS-20261126-001`, "two lasting patterns in one start: does one know what the other is". It
was closed at commit `9b6dad2e0c`; all its results are computed and marked "referee pending". Its register entry is
A277 in `docs/ASSUMPTIONS.md`. A successor study (`SHORT-AGAIN-20261126-001`) has since changed four lines of
`bench/bench.py` (`git diff 9b6dad2e0c HEAD -- research/TWO-PATTERNS-20261126-001/bench/bench.py`): referee the
record as closed, say whether that change touches any recorded count, and do not referee the successor.

**Order of work.** The headline first: "no mark is first heard by a pattern's own knots after round 6" in 2,441
bench cases and 17,809 census cases, and its stated reason, "under the ordinary count no new knot is short, so by
a meeting a pattern's own knots cannot feel the other" (own births equal those with a stub in 36 of 36 bench
readings and 1,980 of 1,980 census readings). Then the counts of the tables and the cases not run, then the table
of two lines, then the toy's check, then wording. If time is short, a complete check of the headline and its
reason is worth more than a thin pass over everything; say plainly what you did not reach.

**Points beyond the hand-off's.**
- Write your own growth from the record's definitions (the ordinary count, the rations, the treatments of a short
  knot, the meeting and the bare shared distinction as joins, the stub, the mark) and regrow a sample of bench and
  census cases with a stated seed; compare every round's counts with the recorded runs (`*.jsonl.gz`). Where you
  fall back on the study's engine, say so and say what you checked it against.
- "No mark is first heard after round 6": count how many recorded cases could have contradicted it at all (cases
  read past round 6, marks not already heard by round 6, marks whose distance from a pattern's own knots allows a
  hearing after round 6 at one step a round). The decision itself says the furthest mark was five steps away; judge
  whether the claim is a finding or forced by the depth of the marks, and say so.
- "Own births equal those with a stub": check that the stub is a fair control (that it could have differed), that
  "equal" compares the right records (names by making, not by numbering), and whether the stated reason (no
  cancelled join without a short knot) is an argument that holds in general or a reading of these cases.
- The census merges two launches: check the merge, the 54 cases stopped by the clock, and whether any count is
  stated as if those cases were negatives.
- The table of two lines (`bench/table_check.py`, `bench/table_mark.py`): n(n + 1) knots of both after n rounds,
  parents one place back, balls 1, 5, 13, 25, 41. Recount from your own growth, and check whether "the record's own
  mechanism" is an accurate credit (search the record with `python3 -B scripts/track.py objects`).
- The toy's check (`/home/jscul/prespatial-org/scripts/check-two-patterns.mjs`, read only): is it a comparison of
  two engines written apart, or of one engine with itself? Do not write in that checkout; copy what you need into
  your folder.
- Scaffolds (A277 and the decision's Scaffolds line): the stub, the mark, the sites, the joins, the rations. For each
  result, say whether it survives a different choice of each scaffold it depends on, so whether it is about the
  model or about the scaffold. If a cheap change of one scaffold is feasible (another kind of mark, another site, a
  different stub), run it on a small sample and report it.

## Your job

1. **Read the hand-off.** `research/TWO-PATTERNS-20261126-001/referee_handoff.md` lists each claim, where its code
   and data are, and the points the author asks a referee to press. Read what it links: `decision.md`,
   `bench/README.md`, `census/README.md`, `toy/README.md`, `owner_request.md`, `report_1.md`. Read `AGENTS.md`
   ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's reading or analysis modules.
3. **Press.** Take the points above and the hand-off's, then look for what they do not list:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (the bench's "Expected"
     section was written after one case had been seen);
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "is a function of" claim that almost nothing could have contradicted (count the cases that
     could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains (a count, the first round, a numbering, a name);
   - a headline, summary, guide passage or goals row that says more than the tables do;
   - earlier work in the program that already has the result: search with `python3 -B scripts/track.py objects`.
4. **Report.** Write `research/TWO-PATTERNS-20261126-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/TWO-PATTERNS-20261126-001/referee-R1/`. Edit no other file. Do not
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
