# Referee brief REORDER-CONFIRM-R1

For an independent referee, 26 November 2026. You are refereeing one closed ticket of this repository:
`REORDER-CONFIRM-20261126-001`, "is the sign about the model or about the order we supply?", a frozen confirmation of the
reordering-sign study. Every prediction is recorded as held; all results are computed and marked "referee pending".

**What to check, in order of what rests on it.**
- The account of why the predecessor's P7 failed: the identity K_i K_j = K_j K_i (-1)^{n_i n_j} for the stated births, and that the
  listing is a convention while the commit order is not.
- P2: with the stated start, births and real readers, the carrying commit orders are exactly the n cyclic shifts of the creation
  order at n = 3 to 6, and creation order = commit order is exact on all 4^n cells. Rebuild at least n = 5 with your own code.
- P3: the crossing criterion for general schedules (real flip: crossing pairs are all pairs up to a split; complex flip i g_x g_y:
  none up to a split), and the shares counting schedules equally at n = 3 to 6. Recount the shares independently.
- P5 (start signs, 48 of 128 at four readers), P6 (eight pair sign rules; phases), P8 (reader conventions).
- The verdict "the sign is about the order supplied, not the model": does the evidence support it, is anything native missed (a rule
  of the program's growth records that would fix the schedule), and is "the sign is a local adjustment at every reader" right?
- Wording: anything in results.md that says more than the receipt.
- The scaffold test: for each result, model or scaffold.

Budget: exact small computations; keep it under an hour.

## Your job

1. **Read the hand-off.** The records are `research/REORDER-CONFIRM-20261126-001/preregistration.md` (frozen at commit
   `8515665ca6`), `results.md` beside it, and the code and receipt in
   `artifacts/REORDER-CONFIRM-20261126-001/REORDER-CONFIRM-20261126-001-E001_schedules/`. Read the predecessor's
   `research/REORDER-SIGN-20261126-001/results.md` and its referee report `referee-R1/codex/report.md` for context. Read `AGENTS.md`
   ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's `engine.py` or `check.py`; build the fermionic model from the definitions.
3. **Press.** Take the points above and the hand-off's, then look for what they do not list:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (the advisor's review before the freeze is in
     `research/REORDER-CONFIRM-20261126-001/advisor/`; the predecessor's referee had already found the four-reader cyclic class);
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "is a function of" claim that almost nothing could have contradicted (count the cases that
     could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains (a count, the first round, a numbering, a name);
   - a headline, summary, guide passage or goals row that says more than the tables do;
   - earlier work in the program that already has the result: search with `python3 -B scripts/track.py objects`.
4. **Report.** Write `research/REORDER-CONFIRM-20261126-001/referee-R1/report.md`:
   - first line after the title, the verdict: **Confirmed**, **Confirmed with fixes** or **Refuted**, and whether
     there is a **Block**;
   - **What holds**, claim by claim, each with the count you obtained and whether you rebuilt it or only read it;
   - **The fixes**, each with its verdict (**Block**: what the study stood on is false; **Narrowing**: true only in a
     smaller scope or for another reason; **Not a block**: wording or credit), the exact sentence and file to change,
     and the evidence;
   - **Scaffolds**: per result, model or scaffold, and what you swapped;
   - **What was not run**, never as a negative;
   - **How it was checked**: your files, and the commands that rerun them.
   Keep the report to what a reader needs to act on it. Put tables of counts in JSON files beside it.

## Rules

- **Where you write.** Only inside `research/REORDER-CONFIRM-20261126-001/referee-R1/`. Edit no other file. Do not
  commit, stage, stash, reset, switch branches or push. Other sessions are working in this checkout: do not stop
  any process you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 8 worker processes and 16 GB in all. Time a small part at the
  exact configuration before any run. A run finishes in about an hour, two at the outside: cut a longer one to a
  stated prefix or to a sample with a stated seed, and report what was not run as "not run". Use the repository's
  `.venv/bin/python`.
- **Independence.** The study was drafted and closed by another agent. A refutation is as welcome as a
  confirmation; do not soften a finding, and do not invent one.
- **Words.** Use the glossary's words: distinction, knot, shared distinction, loose distinction, sample, weighting.
  Say "knot". Do not name the program's own objects by words from a space of two or three dimensions. Never call
  anything typical, rare or likely without naming its weighting. Do not use a study label or a start number without
  saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or
  breaking cryptography, write nothing about it in the repository and say so in your final message only.
- **No claims** about physics, minds, living things, time or space from this work.

When the report is written, end with a final message of at most fifteen lines: the verdict, each fix with its
verdict in one line, and what was not run.
