# Independent recomputation and critique: FORGET-RULE-20261114-001

You are an independent referee's assistant. The study's code is the thread's own (no coding agent), so a fresh implementation from
the written rules is the independent check. The most valuable thing is a **search for a counterexample to Rule A**.

## Rules for this task

- **Do not open or import any `.py` under** `experiments/FORGET-RULE-20261114-001A/`. You may read its JSON (`heldout.json`,
  `gadget_control.json`), `research/FORGET-RULE-20261114-001/{forget_rule.md, preregistration.md, advisor_review_answer.md}`, the
  earlier referee code `research/FREE-TARGET-20261114-001/referee-R1/codex/relations_audit.py` and
  `research/CENSUS-FORGET-20261114-001/referee-R1/codex/` (fresh code for per-call relations and the exact forgetting decision; you
  may reuse it), the census records `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz`,
  CENSUS-FORGET's results `experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl`
  (data only), and the input modules (dlang, LIMIT-STATE's census).
- Write **only** inside `research/FORGET-RULE-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 60 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/FORGET-RULE-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

1. **Implement Rule A yourself** from the stage-2 text of the pre-registration (state: a partition σ of a copy's ports induced by
   everything above in the stretch, the set M of blocks connected to the stretch's top, the set F of ports untouched from above;
   start from a generic copy; on each call, peel knots or side relations full on every two coordinates that hold a distinction in no
   other remaining constraint, the distinction being an own distinction not among the call's arguments or a port in F; join σ with
   the remaining components; verdict: no cycle among reachable states with M non-empty). Implement the **exact** forgetting decision
   (per-call relations and the semigroup, or reuse the referee code above). Then **search for a counterexample**: a family that
   Rule A certifies but that does not forget. Search small families **outside the census** (random and exhaustive small one- and
   two-definition descriptions in the A79 language, varied blocks, side calls, ports in F, cycles that climb back up), as many as
   time allows, and report the counts and any counterexample with its full description.
2. **Rule N.** Check its proof, and test it on the same families (no family with an identity cycle on port positions forgets).
3. **The proof of Rule A.** Judge in particular: (a) is peeling a port in F exact in the whole stretch composite, given that the
   automaton never revisits upper layers (does skipping upward cascades only make it conservative)? (b) does top-down tracking of the
   partition induced by everything above see every connecting path, including those that go down and climb back? (c) is the generic
   start needed, and does it fix the first version's 8 several-definition false certificates? (d) Rule A proves rectangularity only:
   say which of its conclusions also need the gap argument, and that the gap argument's scope (copies of S reached through S calls;
   see `research/CENSUS-FORGET-20261114-001/referee-R1/report.md`) applies to them.
4. **The held-out read.** From `heldout.json` and the census records, recount H1–H4 (0 violations of N or A; A's 36.7% coverage; the
   2,096 chains and 765 of 817 non-chains without an identity cycle that forget) with your fresh rules where feasible.

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
