# Pruned and compressed outputs: REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001

- The line files were written compressed by the scripts themselves (`arm1_<class>_*.jsonl.gz`,
  `arm1_gains_<class>_*.jsonl.gz`, `arm2_all_*.jsonl.gz`); every script reads them compressed. Nothing was compressed
  afterwards.
- Deleted: the development outputs of two timing chunks of `arm1.py` (tag `test`, starts 0 to 30 of the two-holder list
  and 0 to 100 of the three-holder list), two timing chunks of `arm2.py` (tag `test`, starts 0 to 200 and 11,500 to
  11,700) and one timing chunk of `gates.py --part g1two` (starts 0 to 20 of the 500); all regenerable, none read by a
  later script (deviations B1).
- Kept as the record of the first run of the scorer check (before arm 1's drawn tables were added to it):
  `gates_scorer_first.json`, `gates_scorer_first.log`.
- The folder is under 20 MB.
