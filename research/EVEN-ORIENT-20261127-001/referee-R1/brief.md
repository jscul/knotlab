# Referee brief EVEN-ORIENT-R1

For an independent referee. You are refereeing one closed study of this repository: `EVEN-ORIENT-20261127-001`.

The objects:
- A **minimal strict choice** is a set of failing pairs (x, y) of unheld values, each value in at most one pair, every
  pair of knots a **cross pair** (one knot holding x, one holding y) of an even number of them, with no proper
  sub-collection doing the same.
- Each failing pair has a **cycle** a, c, b, d (x held by a and b; y by c and d).
- **Covered twice** means every cross pair is in exactly two failing pairs. The cycles then make a closed cell structure
  (the cross-pair study, A318).
- **Orientable** means cyclic orders listing every pair of knots equally often each way.

It claims:
- **Items 1–4, by hand.**
  - A non-orientable even choice covered twice needs six failing pairs, with three kinds at six: (a) a seven-knot
    projective plane, (b) a six-knot Klein bottle, and (c) a second six-knot Klein bottle (the literature's names).
  - A birth takes one distinction from each parent, so doubled meetings at a grown closure join start knots only.
  - The join rule bars the birth (c) would need from a census start.
- **G.** The enumeration (every labelled minimal choice covered twice on four to six knots, and on seven knots through
  seven pairs: 622,841 structures) finds no non-orientable even choice with at most five pairs. The census-start closures
  reproduce the cross-pair referee's replay, and every doubled meeting at every grown closure joins start knots.
- **P1.** Every non-orientable even choice on at most six knots, or with at most six pairs on seven, puts two values on
  one pair of knots. So with at most one value per pair of knots the fewest is seven.
- **P2.** The built starts B1 and B2 close in one round holding (b) and (a). B3, census start 6830, stalls with no birth
  from its knots 0, 1 and 3. Measured: B4, one more distinction, closes holding (c).
- **P3 and P4.** 3 of 1,283 closures grown from sampled starts of six to eight knots (the extension's weighting) have a
  non-orientable even minimal strict birth choice; none of the 1,819 census-start closures does.
- **The reading.** The exactness of "odd exactly when not orientable" on growth's census closures belongs to the census
  starts' bounds (five knots, twelve distinctions), through the birth and join rules, not to growth.

**Your main task is to break the hand items, the enumeration, the counts and that reading.**
- Check items 1–4 by hand.
- Rebuild the enumeration, the built starts' growth and the listings with exact code of your own.
- Say whether the reading says more than the evidence. In particular: is (a)'s exclusion from the census closures
  argued or only observed; is the B3/B4 contrast the join rule; and is "growth makes them" shown beyond the built and
  sampled starts?

## Your job

1. **Read the hand-off.** `research/EVEN-ORIENT-20261127-001/decision.md` states each claim, and `README.md` holds the
   design, the frozen predictions, the review and the results. The code is `evenorient.py`, which imports the cross-pair
   study's `cellsign.py` for cycles, sign, orientation, separation and structure. The outputs are `summary.json`,
   `gates.json`, `abstract.json`, `built.json`, `extension.jsonl`, `second_sample.jsonl`, `census_starts.jsonl` and the
   `*_nonorientable_even.json` files.
   - Read the cross-pair study's decision and its referee report (`research/CELL-SIGN-20261127-001/`), whose direction 2
     this study took up.
   - Read the guide's account of growth by the joining rule: `publication/knotlab/INTUITIONS.md`, lesson 8.1, "In the
     records' words".
   - Read `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
     `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `evenorient.py`
   or `cellsign.py`. You may call the archived engine through `research/FORBID-EDITS-20261126-001/forbid.py` (`grown`,
   `supports_of`, `sampled`, `extension`, `canonical`), and you may reuse the earlier referees' independent code if you
   say so. In particular check:
   - the enumeration's completeness on six knots, and the classes at six and seven knots, including the five in P1's
     scope;
   - kinds (a), (b) and (c), and whether every non-orientable even choice below seven pairs puts two values on one pair
     of knots;
   - the built starts B1–B4: their holdings, their growth (births and parents), and what their closures hold; why B3
     stalls;
   - the three sampled closures and their choices; the census-start closures under birth and whole choices;
   - the seeds and the weighting of the sampled starts.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after the results were seen (compare the freeze
     commit `dfa155dd8` with the closing one);
   - a verdict that depends on the separation's choices or on coverage above two;
   - whether the weighting (one vote per draw or census start; one per labelled choice; one per class) is stated
     wherever a count is given;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`), goals row or assumption entry (A318, A319) that says
     more than the tables do;
   - earlier work, in the program and in the literature (small quadrangulations of the projective plane and the Klein
     bottle, their parity and colouring). Rerun `python3 -B scripts/track.py objects-gate research/EVEN-ORIENT-20261127-001/README.md`,
     plus one objects search of your own and a full-text search.
4. **Report.** Write `research/EVEN-ORIENT-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/EVEN-ORIENT-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. The study's own run took 351 seconds on one thread (seven knots through seven pairs took 153 s).
  Use the repository's `.venv/bin/python`.
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
