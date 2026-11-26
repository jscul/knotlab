# Referee brief TIME-AS-FOLD-R1

For an independent referee, at the owner's request of 26 November 2026. You are refereeing one closed study of this
repository: `TIME-AS-FOLD-20261125-001`, "time as a fold: a made pattern that counts another's returns". It has one ticket
(A), computed and marked "referee pending".

**Order of work.** The negative first (no case under any law in 88,299 tests): could a case have been found, that
is, does a planted case pass the reading? Then the cases found only under supplied numberings, the failed
prediction, and the knot-test failures the result reports.

## Your job

1. **Read the hand-off.** `research/TIME-AS-FOLD-20261125-001/referee_handoff.md` lists each claim, its evidence class, where its code
   and data are, and the points the author asks a referee to press. Read what it links: the claim, the definitions,
   each pre-registration, each result, the decision note, the deviations. Read `AGENTS.md` ("Canonical foundation",
   "Research discipline", "Guardrails") and the glossary at the end of `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's reading or analysis modules. For the growth itself, write your own from the frozen
   definitions where that is feasible and compare it with recorded runs on a sample; where you reuse a shared growth
   engine, say so in the report and say what you checked it against.
3. **Press.** Take the points the hand-off lists, then look for what it does not list:
   - a prediction judged kindly, or a threshold or reading changed after results were seen;
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "is a function of" claim that almost nothing could have contradicted (count the cases that
     could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains (a count, the first round, a numbering, a name);
   - a headline, summary, guide passage or goals row that says more than the tables do;
   - earlier work in the program that already has the result: run
     `python3 -B scripts/track.py objects-gate <the pre-registration>` and search with `python3 -B scripts/track.py objects`.
4. **Report.** Write `research/TIME-AS-FOLD-20261125-001/referee-R1/report.md`:
   - first line after the title, the verdict: **Confirmed**, **Confirmed with fixes** or **Refuted**, and whether
     there is a **Block**;
   - **What holds**, claim by claim, each with the count you obtained;
   - **The fixes**, each with its verdict (**Block**: what the study stood on is false; **Narrowing**: true only in a
     smaller scope or for another reason; **Not a block**: wording or credit), the exact sentence and file to change,
     and the evidence;
   - **What was not run**, never as a negative;
   - **How it was checked**: your files, and the commands that rerun them.
   Keep the report to what a reader needs to act on it. Put tables of counts in JSON files beside it.

## Rules

- **Where you write.** Only inside `research/TIME-AS-FOLD-20261125-001/referee-R1/`. Edit no other file. Do not commit, stage, stash,
  reset, switch branches or push. Other sessions are working in this checkout: do not stop any process you did not
  start, and stop your own only by process number.
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
