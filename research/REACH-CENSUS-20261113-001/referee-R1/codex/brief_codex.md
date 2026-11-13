# Independent recomputation and critique: REACH-CENSUS-20261113-001

You are an independent referee's assistant. The study's code was written by a coding agent from a frozen spec, so your
recomputation must be **fresh code written from the spec and the mathematics**.

## Rules for this task

- **Do not open or import anything under** `experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/`
  (the study's implementation). You may read the spec, the notes, the study's data files under
  `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/`, the input modules the spec names
  (dlang, LIMIT-ONLY's and LIMIT-STATE's census, BOND-DEPTH's census), and the earlier referee code
  `research/PROVED-RATE-20261113-001/referee-R1/codex/recompute.py` (the exact residue test).
- Write **only** inside `research/REACH-CENSUS-20261113-001/referee-R1/codex/`. No git commands that change state; no publishing.
- Use at most 3 processes and 10 GB, each command under about 15 minutes, the whole task under about 60 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`.
- Deliverable: `research/REACH-CENSUS-20261113-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## The study (read these)

`research/REACH-CENSUS-20261113-001/{codex_spec.md, preregistration.md, reach_census.md, advisor_review_answer.md}`. Data:
`families.jsonl.gz` (one row per distinct family), `alt_families.jsonl.gz`, `alt_growing664_families.jsonl.gz`, `gate664.json*`,
`summary.json`, `run_info.json`, the crashed first run's `full_run_part1_crashed.log.gz` and
`summary_partial_after_crash_unread.json.gz`.

## Points to check

1. **The multi-definition path (new code).** Implement from the spec, yourself: inlining of non-self-holding definitions, the ray
   definition S, the entry call, the ray call, side calls read as G, and L_ray(s) for small s. Validate on a sample of
   **multi-definition** families, deliberately including some of the **largest blocks** (up to the 12-distinction cap), by an
   independent method: direct satisfiability on the truncated pattern, with members restricted to the ray's distinctions as the
   spec defines L_ray, for s = 1..3 (or as far as cheap). Compare with `L_ray` in `families.jsonl.gz`. Say whether large-block
   multi-definition families are adequately validated by the study's gates (G3 finished 139 of 150 panel families; the 11 largest
   did not finish).
2. **Classes on a sample.** For a sample of computed families (both one- and multi-definition, all classes), recompute the class
   (grows: λ > 0 on a complete graph; bounded: exact residue test; lost; none; mixed) and compare.
3. **The crash and rerun.** The first full run crashed at 110,262 of 124,572 families; the thread patched the runner in place and
   reran from scratch. With the data available (the crashed log, the unread partial summary, the final rows), check as far as
   possible that no family's result changed.
4. **Weights and counts.** Are the headline percentages shares of draws (each draw a sample of the description weighting), shares
   of A79 weight computed some other way, or counts of distinct families? Are they worded consistently? Recompute the headline
   shares (Conclusions 2–4) from the rows.
5. **Settled by construction or by the class.** S1–S4 (58.4% "no depth", 3.0% "no ray bond") are stated as settled. Is anything
   else settled by construction, in particular the roughly 70/30 bounded/grows split where a ray bond persists? Does any "typical"
   rest on a one-sided bound?
6. **The ray dependence.** Conclusion 7 (131 of 224 first-ray growers bounded along the last-call ray, at 3 to 5 members) was
   logged as a Narrowing against PROVED-RATE and BOND-DEPTH's readings. Check the 131 on a sample by your own method, and say
   whether it should be a Narrowing or a Block against those studies' published readings (read
   `research/PROVED-RATE-20261113-001/proved_rate.md` and `research/BOND-DEPTH-20261112-001/bond_depth.md`).
7. **Unresolved.** 813 draws unresolved (746 over the 12-distinction block cap): reported, not classified. Check they are kept out
   of the classes and enter the bands as stated.

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
