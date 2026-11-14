# Codex specification: reading-theorem census checks (READ-RULE-20261114-001B)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it. Write the
question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex/` (CODEX). Modify, move or delete no other file.
  Run no git command that changes anything. `.venv/bin/python -B`, at most 2 processes and about 8 GB in total. Touch no process you
  did not start. Repository material only.
- If a computation needs more than about 10 minutes, write it as a shared-runner job (`docs/tooling/shared-runner.md`), smoke it
  with `--limit 20`, `launch --prepare-only`, and stop; the thread launches it.

## Read first

`research/READ-RULE-20261114-001/preregistration.md` (frozen: the statements, the census checks 1 to 4, gate G and predictions
Q1 to Q3) and `research/READ-RULE-20261114-001/advisor_review_answer.md`.

## Inputs (read-only; reuse, do not copy)

- CARRY-BOUND's code and results: `experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/` (`window.py`,
  `scope.py`, `inputs.py`, `direct.py`, `summarize.py`, `REPORT.md`). Full per-family records:
  `.../codex/window_full/results.jsonl` (3.5 GB; stream it, one JSON line per family, the "result" field). Digest:
  `artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz`.
- FREE-TARGET's `relations.py` (`compose`, `rectangular`, `semigroup`), via CARRY-BOUND's `inputs.py`.
- The x ≠ y gadget: `experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/gadget_control.py`.

## Tasks

1. **R1 coverage** (check 1): per family and per residue of the repeating part of the carried sets R_s, whether some carried
   position k has a knot {k, x, z} in S's flattened block with x own and z an own distinction occurring in no other constraint and in
   no call's arguments (any definition). Family flags: R1 on every residue; on some residues only. A second, separate implementation
   (`r1_check.py`, sharing no code with the first) recomputes the flags from the raw keys; they must agree on every family.
2. **R coverage and the exception** (check 2, gate G, Q1): per residue, the knots {k, x, z} at carried positions with x own. For each,
   using CARRY-BOUND's window states on that residue (the states in the repeating part of Q_s for that residue), whether {p, x} is
   tied, whether z is tied opposite to p, and whether z is tied opposite to x, where p is the carried main port (ties read from the
   exact window projection). R applies on a residue when some such knot avoids the exception in every state of that residue (state
   the choice you make for "every state"; if unclear, record it under Ambiguities). Gate: wherever R applies, U ≤ 3 there; R1-covered
   residues have U ≤ 3. Q1: list every family with a residue where such knots exist but every one meets the exception.
3. **Conditional rectangularity** (check 3, Q2): for r = 1 to 8 and every product of r SELF relations (length sets as in
   `relations.semigroup`, same caps), with the identity carry map of the word (start positions carried to end positions; track it
   with the word), test that for every assignment of the carried start coordinates and their equal end coordinates the slice is
   rectangular. Least r, or none up to 8, or capped. Report by CARRY-BOUND's stratum and verdict, by count and by draw weight, with
   Q2's share over the in-scope non-forgetting population (all 5,789 in scope; undecided = capped counts as not).
4. **The counterexample** (check 4, Q3): build (a) S(a, b, c) with own u, x, w and constraints NAE(a, u, u), NAE(a, x, b),
   NAE(c, x, w), SELF(a, u, x), main = S; and (b) the same with "u ≠ a" by the positive gadget of `gadget_control.py` (add the gadget's
   own distinctions to S). Write both in the census key format. If (a)'s repeated argument is not accepted by the shared machinery,
   say so and run what can be run. Run CARRY-BOUND's per-family window and growth (`window.py`'s family entry point) and its direct
   search (`direct.py`) at s = 1 to 6 on both. Report U(s), the growth certificates and L(s) per depth.

## Outputs

`results.json` (per family flags of tasks 1 to 3, compact), `counterexample.json`, `summary.json` (every count and share, Q1 to Q3
and gate G computed), `REPORT.md` (what was built, gates, timings, Ambiguities). Since this study's predictions are about checks
you compute, you may compute Q1 to Q3; the thread reads them once.
