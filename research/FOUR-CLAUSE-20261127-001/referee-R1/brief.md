# Referee brief FOUR-CLAUSE-R1

For an independent referee. You are refereeing one closed study of this repository: `FOUR-CLAUSE-20261127-001`. It
measures how often ordinary not-all-equal growth makes the four-clause form of the step one layer up (six agreements on
disjoint carriers in three pairs; four bonds on (A0,B0,C0), (A0,B1,C1), (A1,B0,C1), (A1,B1,C0); one pair read "both", two
read "either"), found earlier by `UPPER-GROWN-20261127-001`'s referee on census start 420. On 600 held-out census starts
through round 2 (full search up to 19 distinctions) it finds one start with such a step (census 5260, round 2), all four
births needed: 1 of 408 starts with a grown stage read.

**Your main task is to break the count**: find steps the search misses on the stages read (other role assignments,
patterns the pairing misses, the 60-pattern cap), estimate the frequency on the 211 larger stages the cap left out, and
check whether census start 5260's step is real (independent enumeration and law deletions).

## Your job

1. **Read the hand-off.** `research/FOUR-CLAUSE-20261127-001/decision.md` states each claim; the code is `fourclause.py` and
   `census_four.py`, the data `out/`; read the UPPER-GROWN referee report (its four-clause witness). Read what it links, including the
   previous referee's report and witness (`research/RING-BOND-20261127-001/referee-R1/report.md`, `layer_witness.json`,
   `layer_notes.md`); no advisor was consulted. Read
   `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs (`out/`, `post/`) with code you write yourself in this
   folder. Do not import the author's `fourclause.py`, `census_four.py`, `boxes.py` or `ringbond.py`. For the growth itself, either reuse the earlier
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
4. **Report.** Write `research/FOUR-CLAUSE-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/FOUR-CLAUSE-20261127-001/referee-R1/`. Edit no other file. Do not commit,
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
