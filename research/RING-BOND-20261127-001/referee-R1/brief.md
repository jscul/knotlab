# Referee brief RING-BOND-R1

For an independent referee. You are refereeing one closed study of this repository: `RING-BOND-20261127-001`. It asks
four questions about relations among agreement readings under not-all-equal, which an earlier referee found on a grown
three-knot ring:
- whether growth singles out one of the three equivalent choices;
- whether the relation passes the knot test with no reading read at a single knot;
- whether such relations repeat with growth and on sampled starts, and bind again one layer up;
- what the same search finds under parity.

The study's frozen predictions, its runs and its reading are in `research/RING-BOND-20261127-001/`.

**Your main task is to break the conclusions.** Concretely:
- find a feature of the growth that does single out one choice;
- find a bond of the layer above (bonds taken as laws on their readings, binding again), on the ring or on any start,
  that the study's clusters miss;
- show that the bonds found before growth on census starts are artefacts of the definition (padding, readings that a
  knot reads in some other sense, holders that are not what holds the relation);
- show that the parity statement ("every parity bond is a consequence of sums of laws read through agreements") is
  false or empty.

## Your job

1. **Read the hand-off.** `research/RING-BOND-20261127-001/referee_handoff.md` lists each claim, its evidence class,
   where its code and data are, and the points the author asks a referee to press. Read what it links, including the
   advisor's entry for this study in `docs/ADVISOR_HIVEMIND.md` (its full answer; its last reply was cut off) and the
   earlier referee's report (`research/NAE-LAYER-20261127-001/referee-R1/report.md`, with `carrier_notes.md`). Read
   `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs (`out/`, `post/`) with code you write yourself in this
   folder. Do not import the author's `ringbond.py` or its callers. For the growth itself, either reuse the earlier
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
4. **Report.** Write `research/RING-BOND-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/RING-BOND-20261127-001/referee-R1/`. Edit no other file. Do not commit,
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
