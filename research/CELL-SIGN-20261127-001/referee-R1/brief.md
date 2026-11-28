# Referee brief CELL-SIGN-R1

For an independent referee. You are refereeing one closed study of this repository: `CELL-SIGN-20261127-001`.

The objects:
- A **commuting choice** is a set of failing pairs (x, y) of unheld values, with every pair of knots a cross pair of an
  even number of failing pairs. A **cross pair** of (x, y) is a pair of knots, one holding x and one holding y.
- Each failing pair has a **cycle** a, c, b, d (x held by a, b; y by c, d).

The study proves, by hand (item 1 of its README), that the closing sign is Σ L(s) mod 2 under any cyclic and reference
orders. Here L(s) counts the cycles listing the pair of knots s in its reference order.

It claims:
- the identity on all 2,499,769 choices of its populations and 80,005 from random patterns;
- that orientable, weakly even and two-colourable choices close even;
- the literature's fixtures: Klein grids odd exactly when n is odd, the subdivided cube modulo the antipodal map odd
  exactly when k is odd, the projective grids even;
- the encoded-readers referee's coverage table, reproduced;
- P1: every minimal strict odd choice covered twice has Euler count 1 or 0 once its pinched knots are separated. At the
  grown closures that is 4,423 with 1 and 4 with 0; at the census types, 4,464 with 1 and 1,726 with 0;
- measured: all 1,846 minimal strict even choices at the grown closures are orientable, against 6,694 of 15,620 at the
  census types, and planarity does not explain the difference.

**Your main task is to break the proof, the counts and their reading.**
- Check item 1 and its consequences by hand.
- Rebuild the cycles, orders, orientability and separation with exact code of your own, not the author's.
- Recount closure by closure.
- Say whether "on growth's closures, the readers' contradiction is exactly the impossibility of orienting the cycles"
  says more than the tables do.

## Your job

1. **Read the hand-off.** `research/CELL-SIGN-20261127-001/decision.md` states each claim, and `README.md` holds the
   design, the frozen predictions, the review and the results. The code is `cellsign.py`, which imports the encoded-readers study's
   `decode.py` and the readers study's `readers.py`. Its
   outputs are `summary.json`, `gates.json`, `results.jsonl`, `census_types.jsonl` and `fixtures.json`.
   - Read the encoded-readers study's decision and referee report (`research/ENCODED-READERS-20261127-001/`, especially
     `referee-R1/cells.json` and `report.md` fix 8).
   - Read the literature it credits: Mohar, Simonyi and Tardos on odd quadrangulations, Lemma 6.1.
   - Read `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
     `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `cellsign.py`,
   `decode.py`, `readers.py` or `local_commute.py`. You may call the archived engine through
   `research/FORBID-EDITS-20261126-001/forbid.py` (`grown`, `starts`, `supports_of`), and you may reuse the earlier
   referees' independent code if you say so. In particular check:
   - the order count on a sample of each population, and on your own constructions of the fixtures;
   - orientability, two-colourability, the separation of pinched knots and the separated Euler counts;
   - P1 and P3 at every closure and type;
   - whether the two census types at the cap (171 and 172) change any conclusion.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after the results were seen (compare the freeze
     commit `f7bf89cadb` with the closing one);
   - a verdict that depends on the orders, the separation's choices, or the attachment at pairs of knots covered four
     times;
   - whether the weighting (one vote per census start; one per choice; one per type) is stated wherever a count is
     given;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`), goals row, assumption entry (A318) or glossary
     entry (cross pair; Orientable and Euler count extended) that says more than the tables do;
   - earlier work, in the program and in the literature (odd quadrangulations, parity proofs of contextuality and
     cohomology). Rerun `python3 -B scripts/track.py objects-gate research/CELL-SIGN-20261127-001/README.md`, plus one
     objects search of your own and a full-text search.
4. **Report.** Write `research/CELL-SIGN-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/CELL-SIGN-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. The study's own run took 1,799 seconds on one thread; a sample suffices for the 2.4 million
  small-code choices. Use the repository's `.venv/bin/python`.
- **Independence.** Another agent drafted and closed the study. A refutation is as welcome as a confirmation. Do not
  soften a finding, and do not invent one.
- **Words.** Use the glossary's words: distinction, knot, shared distinction, loose distinction, sample, weighting.
  Say "knot". Do not name the program's own objects by words from a space of two or three dimensions, except the
  literature's names, each marked once as the literature's. Never call anything typical, rare or likely without naming
  its weighting. Do not use a study label or a start number without saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or
  breaking cryptography, write nothing about it in the repository and say so in your final message only.
- **No claims** about physics, minds, living things, time or space from this work.
