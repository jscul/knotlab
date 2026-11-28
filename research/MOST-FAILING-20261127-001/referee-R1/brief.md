# Referee brief MOST-FAILING-R1

For an independent referee. You are refereeing one closed study of this repository: `MOST-FAILING-20261127-001`. At
each of the 1,177 closures where birth choices attain an odd close (the commutation-at-birth study,
`LOCAL-COMMUTE-20261127-001`, as refereed), the birth choices form a binary linear code over the decidable pairs (one
parity check per pair of knots) and the closing sign is a linear functional on it. The study takes the birth choices with
the most failing pairs and asks whether the sign is the same on all of them. It claims: forced at 948 of 1,177 (even 588,
odd 360, free 229); counting failing pairs once per holder type gives odd 619, even 241, free 317; on the 173 census types,
one vote per type, 49 odd, 60 even, 64 free; the control (fewest failing pairs above none) forces even at 1,152; round by
round at the 86 later closures, 19 odd and 67 even; and the reviewer's hand cases (starts 17, 24, 43, 57, the wheels of
four and five) as stated.

**Your main task is to break these counts and their reading**: rebuild the codes, maxima and minima with your own code
(exact search, not the author's integer programs), check the verdicts closure by closure, and say whether "the selected
sign belongs to the principle, not the structure" says more than the tables do.

## Your job

1. **Read the hand-off.** `research/MOST-FAILING-20261127-001/decision.md` states each claim; the design, predictions,
   review and results are in `README.md`; the code is `most_failing.py` (which imports the earlier study's
   `local_commute.py` for the birth choices); the outputs are `summary.json`, `gates.json`, `results.jsonl` and
   `census_types.jsonl`. Read the earlier study's decision and its referee report
   (`research/LOCAL-COMMUTE-20261127-001/decision.md`, `referee-R1/report.md`), whose birth choices this study uses. Read
   `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `most_failing.py` or
   `local_commute.py`; you may call the archived engine through `research/FORBID-EDITS-20261126-001/forbid.py`
   (`grown`, `starts`, `supports_of`) and reuse the earlier referee's independent code in
   `research/LOCAL-COMMUTE-20261127-001/referee-R1/` if you say so. In particular:
   - the code at each closure (decidable pairs, parity checks) and its dimension;
   - the maximum and minimum weights and the sign verdicts, by an exact method of your own (enumeration where the code is
     small, branch and bound or a different solver elsewhere);
   - the holder-type count (two pairs count once when their members have the same holders) and the round-by-round maximum
     (note its tie-break, the first optimum, is a scaffold: say whether another tie-break changes any verdict);
   - the 173 census types, read as finished closed patterns;
   - the hand cases.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (compare the freeze commit
     `f0f40eec13` with the closing one);
   - a verdict that depends on the knot order, the tie-break or the time limit;
   - "the direction follows the counting": is the holder-type count a fair alternative, or a different question;
   - whether the weighting (one vote per census start against one per type) is stated wherever a share is given;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`), goals row or assumption entry (A315) that says more
     than the tables do;
   - earlier work in the program that already has the result: rerun `python3 -B scripts/track.py objects-gate
     research/MOST-FAILING-20261127-001/README.md`, one objects search of your own in other words, and a full-text search.
4. **Report.** Write `research/MOST-FAILING-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/MOST-FAILING-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. The study's own run took about three minutes. Use the repository's `.venv/bin/python`.
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
