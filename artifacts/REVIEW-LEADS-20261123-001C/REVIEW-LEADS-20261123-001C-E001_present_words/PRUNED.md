# What was pruned from this folder before the commit

Done by the thread on 2026-11-23, after the study had finished and its summaries were written. Nothing here changes a result.

- **Removed:** 89 files `pairs_*_hidden.npz` (67M in all). Each held the hidden old tables of one block of pairs, an intermediate that `pairs.py` writes and `extras.py` reads. The block summaries `pairs_*_summary.json` and the logs are kept and hold every count and maximum reported. Rerunning `pairs.py` on the side tables regenerates the removed files exactly (the runs are deterministic).
- **Compressed with gzip:** the side-table lists of the extended class (`sides_c1_k4_i5.json`, `sides_c2_k4_i5.json`) and of the targeted pools (`sides_c*_t6*.json`). Run `gunzip` on them before rerunning a script that reads them. The census class (`sides_c1_k3_i3.json`, `sides_c2_k3_i3.json`) is left as written.
