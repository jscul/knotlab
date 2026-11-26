# Referee brief MADE-COPIER-R1

For an independent referee, at the owner's request of 26 November 2026. You are refereeing one closed study of this
repository: `MADE-COPIER-20261125-001`, "a made copier: a pattern that, on meeting a second pattern, makes a third
of the second's form". It has three tickets (A, B, C), all computed and marked "referee pending".

**Order of work.** Ticket C first: it carries the study's new positive claims (17 confirmed cases in which what a
part makes depends on the form of the part it meets, and the statement that none of them is a copier because each
has its cases for one second-pattern form and a start knot among the linking knots). Then tickets A and B, as far as
the compute rule allows. If time is short, a complete check of ticket C is worth more than a thin pass over all
three; say plainly what you did not reach.

**Points for ticket C beyond the hand-off's.**
- Recount the 17 cases from the raw records (`R3.json`, `Rcond.json` under the ticket's artifacts) and rerun at
  least four of them from the start with your own code: two of the main family, and the two that have a made knot
  among the linking knots.
- The confirmation levels (0.01 over the claimed cases, in two families): were both families and their levels fixed
  before the runs that fill them? Would the count of confirmed cases change under one family at one level?
- "Through joining" and "needing the meeting": check each on one case by hand from the birth records.
- The author records one fault of the engine's run (a run that passed the hour before it was cut, and one further
  case found outside a cut run's prefix). Judge whether either touches a verdict or a rate.
- One disclosed sentence of the pre-registration is recorded as false (one of 96 disclosed cases has both forms the
  same). Check that no count in the result depends on that case.

## Your job

1. **Read the hand-off.** `research/MADE-COPIER-20261125-001/referee_handoff.md` lists each claim, its evidence class, where its code
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
4. **Report.** Write `research/MADE-COPIER-20261125-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/MADE-COPIER-20261125-001/referee-R1/`. Edit no other file. Do not commit, stage, stash,
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
