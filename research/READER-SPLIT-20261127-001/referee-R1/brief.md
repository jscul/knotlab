# Referee brief READER-SPLIT-R1

For an independent referee. You are refereeing one closed study of this repository: `READER-SPLIT-20261127-001`. At
each of the 1,177 grown closures where birth choices attain an odd close (the commutation-at-birth study,
`LOCAL-COMMUTE-20261127-001`, as refereed), the birth choices form a binary linear code over the decidable pairs (one
parity check per pair of knots) and the closing sign is a linear functional on it. The study asks whether some odd
birth choice **splits into readers**: disjoint sets of distinctions with (i) every failing pair inside one reader and
(ii) no knot holding two distinctions of one reader; **strict** when the failing pairs are disjoint (each reader two
values that fail to commute). It claims: a strict split at 692 of the 1,177 closures (675 closing in round 1, 17 later), a split of either kind at 731, none at 446 (one vote per census start); fewest strict readers 3 at 423 closures, exactly those with four mutually meeting knots, 4 at 198, 5 at 66, 6 at 5; fewest readers of either kind 3 at 433, 4 at 242, 5 at 51, 6 at 5; the frozen prediction P1 (strict splits only where a knot meets every knot of an odd ring) refuted at 252 closures, while at the 440 with such a ring the fewest strict readers is its length; P2 (a split only of the other kind somewhere) at 39; the hand results H on those 440 closures and on the fixtures; whole choices giving the same splits as birth choices at the 86 later closures and none at the 10 where birth choices lose the odd close; on the 173 finished census types (one vote per type) 115 strict, all with an odd ring, 30 of the other kind only, 28 none; P4, every odd birth choice with the fewest failing pairs a strict split exactly at the 423; and, after the results, 198 of the 252 sharing one shape read as one reader encoded into two.

**Your main task is to break these counts and their reading**: rebuild the codes and search for splits with exact code
of your own (not the author's integer programs, satisfiability encodings or enumeration), check closure by closure,
build your own realization local to the readers for a sample of splits (or argue one exists another way), and say
whether "a game of certainty between separated readers" says more than the tables do.

## Your job

1. **Read the hand-off.** `research/READER-SPLIT-20261127-001/decision.md` states each claim; the design, frozen
   predictions, review and results are in `README.md`; the code is `readers.py` (which imports the earlier study's
   `local_commute.py` for the birth choices); the outputs are `summary.json`, `gates.json`, `results.jsonl`,
   `whole_only.jsonl`, `fixtures.json` and `census_types.jsonl`. Read the earlier studies' decisions and referee reports
   (`research/LOCAL-COMMUTE-20261127-001/`, `research/MOST-FAILING-20261127-001/`), and `AGENTS.md` ("Canonical
   foundation", "Research discipline", "Guardrails") and the glossary at the end of `publication/knotlab/INTUITIONS.md`
   first.
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `readers.py`,
   `most_failing.py` or `local_commute.py`; you may call the archived engine through
   `research/FORBID-EDITS-20261126-001/forbid.py` (`grown`, `starts`, `supports_of`) and reuse the earlier referees'
   independent code in `research/LOCAL-COMMUTE-20261127-001/referee-R1/` and `research/MOST-FAILING-20261127-001/referee-R1/`
   if you say so. In particular:
   - strict splits and their fewest readers, and splits of either kind and their fewest readers, at every closure;
   - the odd rings around a knot (README, item 1) and prediction P1 (odd rings only): look hard for a strict split at a
     closure without one, or with fewer readers than the shortest ring;
   - the hand results H (items 1–3 and 7), including the fixtures and the grown closures named there;
   - the certificate (items 5 and 6): is the readers' game as stated actually established by what `readers.py` checks?
   - whole choices at the 96 later closures, and the 173 finished census types.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (compare the freeze commit
     `4136dd3855` with the closing one);
   - a verdict that depends on the knot order, the knot left free in the certificate, the reader-label cap of 12 or the
     time limit;
   - whether "separated readers" is fair: different readers' values commute and each knot asks each reader at most one
     value, but knots join the readers (the third-reader study's separated readers are ones no knot joins), and the
     state and the signs of the values outside readers are supplied;
   - whether the weighting (one vote per census start; one per finished type) is stated wherever a share is given;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`), goals row or assumption entry (A316) that says more
     than the tables do;
   - earlier work in the program that already has the result: rerun `python3 -B scripts/track.py objects-gate
     research/READER-SPLIT-20261127-001/README.md`, one objects search of your own in other words, and a full-text
     search; and the literature (GHZ-type arguments on graph states of odd rings; the literature's odd wheels).
4. **Report.** Write `research/READER-SPLIT-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/READER-SPLIT-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. The study's own run took 162 seconds. Use the repository's `.venv/bin/python`.
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
