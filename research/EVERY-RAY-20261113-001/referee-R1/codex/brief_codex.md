# Independent recomputation and critique: EVERY-RAY-20261113-001

You are an independent referee's assistant. The study's code was written by a coding agent from a frozen spec, so your
recomputation must be **fresh code written from the spec and the mathematics**.

## Rules for this task

- **Do not open or import anything under** `experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/`
  **except the data folders** `codex/sample/` and `codex/gates_full/` (row files, JSON and logs only; no `.py`). Do not read the
  thread's `.py` files in the parent folder either. You may read `research/EVERY-RAY-20261113-001/{every_ray.md, preregistration.md,
  codex_spec.md, codex_spec_addendum.md, advisor_review_answer*.md}`, `sample_reading.json` in the experiment folder, the census
  records `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz`, the input modules the
  spec names (dlang, LIMIT-STATE's census, BOND-DEPTH's census), BRANCH-DEPTH's records under `artifacts/BRANCH-DEPTH-20261112-001*/`,
  and the earlier referee mapping `research/TRUE-RATE-20261113-001/referee-R1/codex/family_inventory.json`.
- Write **only** inside `research/EVERY-RAY-20261113-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 60 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/EVERY-RAY-20261113-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

1. **The uncarried bounded figure** ("200 of the 204 bounded over paths are bounded without a carried top port"). For as many of
   the 204 as time allows (all 50 that need a mixed path, then the rest, smallest first), find **yourself** an explicit eventually
   periodic path (a lasso of call choices from an entry) along which (i) no top port is carried (the top-port set T along the path
   becomes empty), and (ii) the least bond from a top port to an own distinction of the depth-s copy, with members on that path's
   distinctions and side calls read as the limit relation, is bounded at every depth: certify it exactly (for example by a repeat of
   the full cost vector on the lasso's period, checking every residue). Report how many you certify, their bounds, and any family
   where you cannot find such a path.
2. **A cross-check against BRANCH-DEPTH.** L_true ≤ L_path: if BRANCH-DEPTH proved linear growth of the members-anywhere bond for a
   one-definition rule, that rule cannot be bounded over paths. Map EVERY-RAY's one-definition sample families to BRANCH-DEPTH's
   rules (via definitions; the TRUE-RATE referee mapping may help) and report any contradiction, and how many sample families the
   check covers.
3. **The path DP on repeated and shared arguments.** The G-brute panel had 22 of 40 several-definition families. Recompute L_path at
   s = 1..3 (or as far as cheap) by direct enumeration of paths and direct satisfiability for about 15 more several-definition
   families, including SELF calls that share or repeat arguments, and compare with the sample rows.
4. **Unresolved and the bands.** Check that `sample_reading.json` keeps the 26 unresolved G families out of the class numerators and
   reads them both ways in the band, and that the Wilson intervals are computed as stated. Check that G-reg "as clarified" (9 graph
   mismatches, all several-entry, class and λ equal) follows the clarification frozen before the result, not a later loosening.
5. **The two code versions.** The owner patched a timer race in the DP mid-run; rows from the two versions are in separate files
   in `codex/sample/` (for example `B.jsonl` and `B_resume.jsonl`, and `phase2.jsonl`). Check that they agree wherever they overlap.
6. **Wording.** Is "grow along every path" worded as within the depths read and as a sample statement? Is anything worded beyond
   the sample?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
