# Independent recomputation and critique: TRUE-RATE-20261113-001

You are an independent referee's assistant. The study's code was written by a coding agent (and one certificate script by the
thread), so your recomputation must be **fresh code written from the notes and the mathematics**.

## Rules for this task

- **Do not open or import anything under** `experiments/TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates/codex/`
  (the study's implementation, including `thread_carried_certificate.py`). You may read the notes, the study's data files under
  `artifacts/TRUE-RATE-20261113-001A/` (if any), the merged results it names, BRANCH-DEPTH's records under
  `artifacts/BRANCH-DEPTH-20261112-001*/` and its note `research/BRANCH-DEPTH-20261112-001/depth.md`, BOND-DEPTH's `census.py`
  (`families_one_def`), LIMIT-ONLY's `sample_*.jsonl.gz`, and dlang.
- Write **only** inside `research/TRUE-RATE-20261113-001/referee-R1/codex/`. No git commands that change state; no publishing.
- Use at most 3 processes and 10 GB, each command under about 15 minutes, the whole task under about 45 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`.
- Deliverable: `research/TRUE-RATE-20261113-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## The study (read these)

`research/TRUE-RATE-20261113-001/{true_rate.md, preregistration.md, codex_spec.md, advisor_certificate_*.md}`, especially the
section "The carried-port certificate (post hoc)", steps 1–4.

## Points to check

1. **The certificate, fresh.** For the ten families 262, 269, 302, 363, 579, 642, 662, 908, 975, 1144 (indices into
   `families_one_def()`), compute yourself: the bottomless port relation G; R_1 (the states of C_1's ports that extend through
   C_0's knots and its other calls read as G, with C_0's ports free); whether R_1 is all eight states; and by direct satisfiability
   on the subtree of C_1 truncated a few levels down (boundary calls as G) a bond of size 3 containing the carried top port, an own
   distinction of C_1 and a side-copy member. Then judge the shift argument of steps 1–4: does R_1 = all eight imply R_s = all
   eight for every s, and does the size-3 bond then give L(s) ≤ 3 at every depth? Watch the case where the port is carried through
   a cycle of positions rather than a fixed point.
2. **The carried-port test.** A top port is carried down the first ray when the first SELF call's map j ↦ a_j on port positions
   (a_j < 3) has a cycle. Recount, with your own code: carried families among the 226 (`lambda_float > 0`, complete) of
   `artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl` (said 20); and among BRANCH-DEPTH's
   432 bounded rules (said 320 carried, 112 not: 73 at exactly 3, 39 eventually 4).
3. **The mapping to BRANCH-DEPTH's records.** The study read BRANCH-DEPTH's per-rule outcomes through a map from the family index to
   (sample file, line + 1), "664 of 664 matched at offset 1". Verify independently that each matched record is the same rule (by
   comparing definitions, or by recomputing the record's key from the sample row), and recount BRANCH-DEPTH's outcomes on the 226
   (said 66 linear growth, 144 linear lower bound if a bond exists, 10 exactly 3, 6 unresolved).
4. **The 24 closed families.** If cheap, recompute λ_true for two or three of the 24 whose uncapped side table closed (said
   λ_true = λ_ray, all unshortened); otherwise say what the claim rests on.
5. **Prior work.** BRANCH-DEPTH had already read the members-anywhere bond on the same 664 rules before TRUE-BOND. Read TRUE-BOND's
   note (`research/TRUE-BOND-20261113-001/true_bond.md`): which of its claims (results, "open", novelty) does BRANCH-DEPTH's earlier
   result change, and should that be a Block or a Narrowing against TRUE-BOND?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
