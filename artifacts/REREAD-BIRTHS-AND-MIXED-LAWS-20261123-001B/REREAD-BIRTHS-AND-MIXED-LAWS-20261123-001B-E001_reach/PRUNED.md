# Pruned and compressed outputs: REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001

Nothing was deleted except the two timing chunks of `grow_t1.py` (tag `test`, regenerable; deviations item 18). To keep the
folder under 20 MB the line files were compressed with `gzip -9` after every script that reads them had run (76 MB
before, 3.6 MB after):

- `starts.jsonl.gz` (founder starts, written by `build_targets.py`);
- `t1_c2_*.jsonl.gz`, `t1_c3_*.jsonl.gz` (one line per history, `grow_t1.py`);
- `t1_hits_c2_*.jsonl.gz`, `t1_hits_c3_*.jsonl.gz` (tables proportional to the target's and hidden excesses, in full);
- `verify_excess_*.jsonl.gz` (full enumeration of the new hidden excesses, `verify_excess.py`).

`report.py` reads the compressed files directly. The other scripts read the plain `.jsonl` names: run
`gunzip artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/*.jsonl.gz`
before running `grow_t1.py`, `t2.py`, `verify_excess.py`, `verify_t2.py`, `seven_reasons.py` or `gates.py` again, or
regenerate them with the commands of `research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/results_draft.md`. The empty
`*_killed_by_limit.log` files are kept as the record of runs stopped by the ten-minute limit (deviations item 17).
