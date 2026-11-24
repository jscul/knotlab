# What was removed or compressed

- Removed: the six files of the development run of `q_census.py` with tag `dev` (positions 1290 to 1300 and 0 to 50),
  written before the study's runs and deleted once inspected (deviations A0 (6)). Nothing else was removed.
- Compressed: the census line files (`census_hist_c_*`, `census_parts_c_*`, `census_gains_c_*`) and the stored stage
  prefixes (`prefixes/*.jsonl.gz`) are written gzip-compressed. The line files of tests (a) and (b) (`sources.jsonl`,
  `draws_*.jsonl`) and the check outputs (`gate_*.json`) are small and plain.
- Every gain table is written in full in `census_gains_c_*` (no stage, history and arm reached the cap of 50).
- Folder size at the end: under 5 MB.
