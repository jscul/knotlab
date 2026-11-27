# Referee brief TOY-PHASE-R1

For an independent referee. You are refereeing one closed study of this repository: `TOY-PHASE-20261127-001`. It
places the program's model against Spekkens's toy theory and the phase groups of Coecke, Edwards and Spekkens, on objects
the record already has: one three-place parity knot; the four-knot closure ordinary parity growth makes from the
three-knot ring, with its three readers; the birth-sign study's coherent constructions; the sibling study's two-reader
score; and, as a stress test, the four-readings study's 115 stored operator certificates. It claims that a parity knot is
exactly one toy bit, that growth's even closure is a toy state under all 216 reader assignments and a stabilizer state
under none, that the odd close needs reads whose product squares to −1 (a phase of order four), that no operation on a
knot's values gives one, and that inside the stabilizer part the two-reader score stays at 2.

**Your main task is to break the placement**: recompute every count with your own code, look for an assignment,
pairing, phase choice or certificate where a claim fails, and say where a claim is stated beyond what was computed or
follows from the definitions alone (the study names its own tautologies in "Settled by construction"; check that list
is complete and that nothing on it is reported as a finding).

## Your job

1. **Read the hand-off.** `research/TOY-PHASE-20261127-001/decision.md` states each claim; the design, frozen
   predictions, review before the freeze and results are in `README.md`; the code is `toy_phase.py` and
   `stress_certificates.py`; the outputs are `results.json` and `stress_certificates.json`. Read what they link: the
   no-whole-state fixture (`research/NO-WHOLE-STATE-20261126-001/fixture.py`), the birth-sign study
   (`experiments/BIRTH-SIGN-WEIGHT-20261127-001A/BIRTH-SIGN-WEIGHT-20261127-001A-E001_closing_sign/run.py` and
   `result.md`, and `experiments/BIRTH-SIGN-WEIGHT-20261127-001C/BIRTH-SIGN-WEIGHT-20261127-001C-E001_local_questions/result.md`),
   and the four-readings certificates
   (`artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json`). The advisor was
   unavailable; an independent reviewer checked the design by hand before the freeze (README, "Review before the
   freeze"). Read `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `toy_phase.py` or
   `stress_certificates.py`. The closure is four knots you can write down; check it once against the archived growth
   engine `research/FORBID-EDITS-20261126-001/forbid.py`. You may read the certificates' JSON. In particular:
   - the toy-state test and the Spekkens rule it applies (2016, pairwise commuting known questions); check whether the
     2007 knowledge-balance rule, applied with other readers' reads taken into account, gives the same 7 of 15 pairings;
   - the 216 Pauli assignments: commuting knot operators, product −1, no state for the even law, one for the odd law,
     and its 64 probabilities against the target;
   - the 1,080 pure toy states and the best score 3/4;
   - the 32 phase choices of P4 and the claim that without a state phase no scored context is certain;
   - the birth-sign constructions rebuilt from that study's stated definitions (a question multiplies by the sign of its
     value, then applies its change), and the 5/8 control;
   - the 60 two-qubit stabilizer states, the sibling preparation (reduced to span{11, (01 + 10)/√2} per reader), Landau's
     identity and the 2√2 claim for reads X and Z on both sides;
   - the 115 certificates: holder commutation, the −1 product, the toy reading's even holders, the reordering cost.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (the design was revised after
     the review but before the run: check the freeze commit against the results);
   - a "no operation", "every", "under none" or "whatever the growth law" claim stated beyond the objects computed (the
     involution argument is for one knot or one reader's four states: say whether a larger value permutation could square
     to an allowed change, and whether that would matter);
   - a control that could not have failed;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`) or goals row that says more than the tables do;
   - earlier work in the program that already has the result: rerun `python3 -B scripts/track.py objects-gate
     research/TOY-PHASE-20261127-001/README.md` and one search of your own in other words.
4. **Report.** Write `research/TOY-PHASE-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/TOY-PHASE-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. Everything here is small: the study's own run takes seconds. Use the repository's
  `.venv/bin/python`.
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
