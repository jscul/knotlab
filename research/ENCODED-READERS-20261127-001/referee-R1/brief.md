# Referee brief ENCODED-READERS-R1

For an independent referee. You are refereeing one closed study of this repository: `ENCODED-READERS-20261127-001`.
It works on the strict splits of the readers study (`READER-SPLIT-20261127-001`, as refereed): at each of 692 grown
closures, odd birth choices whose failing pairs are disjoint, every two knots' checks commuting. It defines a merge
(two failing pairs whose partners are held by the same two knots and whose other values share a knot become one pair),
argues that merges keep commutation and the closing sign, and asks whether every minimal strict split decodes, by some
sequence of merges, to the three-reader game (four mutually meeting knots, one pair per way of splitting them) or a ring
game (a knot meeting every knot of an odd ring, each pair (n−1)/2 steps on). It claims:
- every fewest strict split at the 692 closures decodes to exactly one base game (three-reader game at 675 closures,
  ring game of five at 15, both at 2), meeting no doubled pair and taking 1 − c merges through knots holding other
  values (c the knots holding values minus the pairs), and 2,102 fewest words at the 252 closures without an odd ring,
  as the earlier referee counted;
- P1 failed: of 4,803 minimal strict odd choices with at most eight pairs at the 692 closures, 4,799 decode and 4 (six
  pairs on six knots, at the closures grown from census starts 5136 and 6787) admit no merge;
- P2 held: all 1,139 strict odd choices at the 213 codes with at most 14 free choices are minimal and decode;
- measured: on the 115 census types with a strict split, 2,464 of 6,190 minimal choices decode, the rest in two
  irreducible shapes (six pairs on seven knots; eight pairs on seven knots); the literature's planarity of the
  pattern of meetings against split kinds (1,157 of 1,177 grown closures planar);
- after the results, not frozen: read as cells (each failing pair a cell on its four met pairs of knots), all five
  irreducible games are closed complexes, none orientable, with Euler characteristics 1, 1, 0, 1 and −1.

**Your main task is to break these counts and their reading**: rebuild the choices, the merges and the decoding with
exact code of your own (not the author's listings or search), check closure by closure, and say whether "every fewest
separated-reader game on growth's closures is the three-reader or ring-of-five game, encoded" says more than the
tables do.

## Your job

1. **Read the hand-off.** `research/ENCODED-READERS-20261127-001/decision.md` states each claim; the design, frozen
   predictions, review and results are in `README.md`; the code is `decode.py` (which imports the readers study's
   `readers.py`); the outputs are `summary.json`, `gates.json`, `results.jsonl`, `census_types.jsonl` and
   `fixtures.json`. Read the readers study's decision and its referee report (`research/READER-SPLIT-20261127-001/`,
   especially `referee-R1/shapes.md`), and `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails")
   and the glossary at the end of `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `decode.py`,
   `readers.py`, `most_failing.py` or `local_commute.py`; you may call the archived engine through
   `research/FORBID-EDITS-20261126-001/forbid.py` (`grown`, `starts`, `supports_of`) and reuse the earlier referees'
   independent code (`research/READER-SPLIT-20261127-001/referee-R1/`, `research/LOCAL-COMMUTE-20261127-001/referee-R1/`)
   if you say so. In particular:
   - the merge argument (items 1, 2 and 4 of the README) and the counting identity;
   - the decoding of every fewest split, and of the minimal choices with at most eight pairs;
   - the four failures on grown closures and the two census shapes: are they really irreducible (no merge, not a base
     game, minimal), and are they each one shape up to relabelling?
   - whether a minimal choice that the author's depth-first search failed to decode could decode by another sequence
     (the search remembers remainders; check it is complete);
   - the cell reading and its Euler characteristics, orientability and the pinched case.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (compare the freeze commit
     `ac89a0643d` with the closing one);
   - a verdict that depends on the caps (1,000 fewest, 2,000 per size, 20,000 search states, eight pairs) or the time
     limit;
   - whether the weighting (one vote per census start; one per choice; one per type) is stated wherever a count is
     given;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`), goals row or assumption entry (A317) that says
     more than the tables do;
   - earlier work, in the program and the literature (repetition codes, graph states, Arkhipov's theorem, square
     complexes): rerun `python3 -B scripts/track.py objects-gate research/ENCODED-READERS-20261127-001/README.md`, one
     objects search of your own, and a full-text search.
4. **Report.** Write `research/ENCODED-READERS-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/ENCODED-READERS-20261127-001/referee-R1/`. Edit no other file. Do not
  commit, stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any
  process you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. The study's own run took 129 seconds. Use the repository's `.venv/bin/python`.
- **Independence.** Another agent drafted and closed the study. A refutation is as welcome as a confirmation. Do not
  soften a finding, and do not invent one.
- **Words.** Use the glossary's words: distinction, knot, shared distinction, loose distinction, sample, weighting.
  Say "knot". Do not name the program's own objects by words from a space of two or three dimensions, except the
  literature's names, each marked once as the literature's. Never call anything typical, rare or likely without
  naming its weighting. Do not use a study label or a start number without saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or
  breaking cryptography, write nothing about it in the repository and say so in your final message only.
- **No claims** about physics, minds, living things, time or space from this work.
