# Referee brief UPPER-GROWN-R1

For an independent referee. You are refereeing one closed study of this repository: `UPPER-GROWN-20261127-001`. It
asks where the step one layer up lives: six agreements on disjoint carriers whose eight triples are clauses, binding
three agreements of agreements (a "box"; found by the previous referee in `RING-BOND-20261127-001`). It reads every
simple connected cubic graph with up to twelve points as a closed system of three-place not-all-equal knots, and 1,000
sampled census starts with their grown stages through round 2. It concludes that boxes are common in closed
twelve-knot systems (49 of 85), absent below twelve, and absent from every grown stage read.

**Your main task is to break the conclusions**: find a box (or another step one layer up with disjoint carriers) on a
closed system of ten or fewer knots, on a multigraph or a system with four-place knots, or on a grown stage, above all
one needing a birth's law; show that the box definition or the search misses cases (the local search on the 351 large
stages, the box form itself); or show that the twelve-knot count is wrong.

## Your job

1. **Read the hand-off.** `research/UPPER-GROWN-20261127-001/referee_handoff.md` lists each claim, its evidence class,
   where its code and data are, and the points the author asks a referee to press. Read what it links, including the
   previous referee's report and witness (`research/UPPER-GROWN-20261127-001/referee-R1/report.md`, `layer_witness.json`,
   `layer_notes.md`); no advisor was consulted. Read
   `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs (`out/`, `post/`) with code you write yourself in this
   folder. Do not import the author's `boxes.py`, `cubic.py`, `census_boxes.py` or `ringbond.py`. For the growth itself, either reuse the earlier
   referee's independent `research/NAE-LAYER-20261127-001/referee-R1/growth_rule.py` or write your own. Say which, and
   what you checked it against.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after results were seen;
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "is a function of" claim that almost nothing could have contradicted (count the cases that
     could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains;
   - a headline, summary, guide passage or goals row that says more than the tables do;
   - earlier work in the program that already has the result: search with `python3 -B scripts/track.py objects`.
4. **Report.** Write `research/UPPER-GROWN-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/UPPER-GROWN-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 8 worker processes and 16 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. Time a small part at the exact configuration before any run. A run finishes in about an hour,
  two at the outside. Cut a longer one to a stated prefix or to a sample with a stated seed, and report what was not
  run as "not run". Use the repository's `.venv/bin/python`.
- **Independence.** Another agent drafted and closed the study. A refutation is as welcome as a confirmation. Do not
  soften a finding, and do not invent one.
- **Words.** Use the glossary's words: distinction, knot, shared distinction, loose distinction, sample, weighting.
  Say "knot". Do not name the program's own objects by words from a space of two or three dimensions. Never call
  anything typical, rare or likely without naming its weighting. Do not use a study label or a start number without
  saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or
  breaking cryptography, write nothing about it in the repository and say so in your final message only.
- **No claims** about physics, minds, living things, time or space from this work.
