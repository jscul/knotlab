# Referee brief NATIVE-CARRY-R1

For an independent referee. You are refereeing one closed study of this repository: `NATIVE-CARRY-20261128-001`.

The objects:
- The **candidate cells** of a set S of knots are every unheld pair of distinctions (x, y) whose four holders are
  distinct and all in S. Together they are S's **whole choice**.
- S is a **whole-choice set** (provisional word) when it has a cell and every pair of knots is a **cross pair** (one
  knot holding x, one holding y) of an even number of its cells. Then the whole choice commutes with nothing selected.
- A whole-choice set is **minimal** when no proper subset of its knots is one. Its **sign** is the closing sign of its
  whole choice.

It claims:
- **By hand.**
  - The closing sign of any choice is the parity of crossing chord pairs with the knots on a circle.
  - Exchanging two neighbouring knots changes it by the number of cells at their pair.
  - A formula gives that number from the meeting multiplicities.
  - Outerplanar patterns give only even sets.
  - Four mutually meeting knots and K_{2,3} are odd sets; the ring of five's closure is not a set.
  - The literature's Petersen graph is a ten-knot odd minimal set.
- **G.** These fixtures hold. The formula equals a direct count at every pair of every pattern examined. Every set's sign
  is order-free. The commutation-at-birth study's 145 round-1 closures with a state (53 odd) reproduce.
- **P1.** Through seven knots (the atlas, and four- and five-knot patterns with doubled meetings), the only odd minimal
  sets have the cells of four mutually meeting knots or of K_{2,3}.
- **P2.** All 1,028 odd minimal sets at the 1,819 census-start closures, 173 census types and 1,283 sampled closures
  are of those two kinds.
- **P3.** 152 of the 1,177 census closures where birth choices attain odd have an odd minimal set; the other 1,025 need
  a selection. Census types: 149 of 173.

**Your main task is to break the hand items, the classification, the counts and their reading.**
- Check items 1–4 by hand.
- Rebuild the sets, signs and kinds with exact code of your own.
- Say whether "growth's pattern alone carries the readers' contradiction only as four mutually meeting knots or K_{2,3}"
  says more than the evidence, given the subset cut at the 24 closures above twelve knots and the seven-knot bound of the
  abstract classification.

## Your job

1. **Read the hand-off.** `research/NATIVE-CARRY-20261128-001/decision.md` states each claim, and `README.md` holds the
   design, the frozen predictions, the review and the results. The code is `nativecarry.py`, which imports the
   even-orientation study's `evenorient.py` for growth and starts only. The outputs are `summary.json`, `gates.json`,
   `abstract.json` and `rows.jsonl.gz`.
   - Read the commutation-at-birth study (`research/LOCAL-COMMUTE-20261127-001/`), whose natural birth rule and
     outerplanarity criterion this study refines.
   - Read the cross-pair study's order count (`research/CELL-SIGN-20261127-001/README.md`, item 1).
   - Read `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
     `publication/knotlab/INTUITIONS.md` first (the new entry "Whole-choice set").
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `nativecarry.py`,
   `evenorient.py` or `cellsign.py`. You may call the archived engine through `research/FORBID-EDITS-20261126-001/forbid.py`
   (`grown`, `supports_of`, `sampled`, `extension`), and you may reuse the earlier referees' independent code if you say
   so. In particular check:
   - the abstract classification, and whether an eight-knot odd minimal set other than the two kinds exists (a
     bounded search suffices);
   - the populations' minimal sets and their kinds, and the 24 closures above twelve knots, reading them fully if you
     can;
   - the 152 and the 1,025, against the commutation-at-birth study's verdicts;
   - the census types.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after the results were seen (compare the freeze
     commit `76187954b` with the closing one);
   - whether "whole choice" (all unheld pairs) is the right reading at later-round closures, where birth choices allow
     fewer;
   - whether the weighting (one vote per closure or type; one per set of knots) is stated wherever a count is given;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`), goals row, assumption entry (A318) or glossary
     entry that says more than the tables do;
   - earlier work, in the program and in the literature (crossing parity; Kleitman; Conway–Gordon and Sachs; the
     outerplanarity obstructions). Rerun `python3 -B scripts/track.py objects-gate research/NATIVE-CARRY-20261128-001/README.md`,
     plus one objects search of your own and a full-text search.
4. **Report.** Write `research/NATIVE-CARRY-20261128-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/NATIVE-CARRY-20261128-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. The study's own run took 191 seconds on one thread. Use the repository's `.venv/bin/python`.
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
