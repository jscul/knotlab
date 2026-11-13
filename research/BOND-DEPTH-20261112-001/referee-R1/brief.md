# Referee brief BOND-DEPTH-R1 (from the coordinator, 2026-11-13, lean, Codex-assisted)

**The epic.** `BOND-DEPTH-20261112-001`, closed referee pending: pre-registration c717335c4, epic 559be58a8, goals and notebook
ebf95a2bd.

**Files.** The code is `experiments/BOND-DEPTH-20261112-001A/.../{census.py, helper_after_start.py}`. The data is `artifacts/.../{runs_merged.jsonl, raw/,
validation.json, summary.json}`.

**Claims** (all computed):
- **The method.** An exact ray DP, validated 120 of 120 against exhaustive search. Chains give steps + 2.
- **The census** (664 families, s to 30):
  - bounded exactly 204 (settling at 3: 173, 2: 30, 4: 1);
  - growing exactly 0;
  - undetermined 447 (403 full depth: 240 rising, 163 flat; 44 capped);
  - no ray bond 2, unfinished 11.
- **P1 failed** (bounded below half).
- **Run notes.** Helpers were added mid-run with `run_family` unchanged, and the last 11 families were stopped.

**Points to check.**
- The repeat detector, which may miss eventual periodicity.
- The ray restriction, and endpoint minimisation.
- Whether "growing exactly 0" is forced by the detector, and whether the 240 are genuinely linear.
- The helper change.
- What is settled by construction.

**Report.** Send the verdict, with fixes marked Block, Narrowing or Not a block.
