# What was pruned from this folder

Done by the implementing sub-agent on 2026-11-23, after every run had finished and every summary, the gates (`gates.json`)
and the report (`report.json`, `structures_found.json`) were written. Nothing here changes a result. Every removed file is
regenerated exactly by the commands in `research/THIRD-HOLDER-20261123-001B/results_draft.md` (all runs are deterministic).

- **Compiled programs removed:** `chsh_kernel.so`, `sides_enum`, `pair_eval` (build outputs; the three `gcc` lines at the top
  of the commands rebuild them).
- **Inputs of the compiled pairing removed:** `pc_*.in` and `pc_*_reps.npz` (written by `pairs_c.py prep`).
- **Per-run lists removed:** `pc_*_run*.near` (old tables within 1e-9 of 2 per run, written by `pair_eval`; their merged and
  exactly checked content is in each `pc_*_summary.json`: counts, and every old table above 2 with its pair and structure).
  The per-run counts `pc_*_run*.json` and logs are kept.
- **Large side-table lists removed:** `sides_L_c2_k4_i5_h3.npz`, `sides_S_c1_k4_i5_h3.npz`, `sides_S_c2_k4_i5_h3.npz`,
  `sides_L_c2_k5_i5_h3.npz` (rerun `sides.py` / `sides_parts.py`), `sides_search_{L,S}_c{1,2}_all.npz` (rerun `search.py`),
  `sides_mixS.npz` (rerun `gates_mix.py` after the class-S listing). Their `.json` and `.log` files are kept. Kept as written:
  the side tables of every class of at most 3 knots, the two-holder 4-knot lists, `sides_L_c1_k4_i5_h3.npz`, and the four
  20,000-table search pools `sides_search_{L,S}_c{1,2}.npz`.
- `gates.py` part 2 and `report.py` read the removed 4-knot and 5-knot lists; regenerate them before rerunning those two.
