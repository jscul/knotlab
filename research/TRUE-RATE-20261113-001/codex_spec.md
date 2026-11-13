# Codex specification: proved true rates with side branches (TRUE-RATE-20261113-001A)

You write and validate code; you do **not** run the full computation (the thread launches it). If anything is ambiguous, do not
resolve it: write it under "Ambiguities" in `REPORT.md` and skip only the affected part.

## Rules

- Repository root `/home/jscul/p-vs-np-contact-first`. Write **only** inside
  `experiments/TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates/codex/` (CODEX). Change nothing else; no git command
  that changes anything. `.venv/bin/python -B`. Every command in the foreground, finished within 20 minutes; at most 3 processes and
  8 GB in total (another job shares the machine).
- Reuse read-only: `experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex/true_bond.py` (TB: its
  `FamilyDP`, summaries, combination, generic table, `study_families`), its `REPORT.md` and `thread_settled_validation.py` (the
  depth convention is the uniform truncation), and
  `experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex/graph_algorithms.py` (Karp, components).
  Study set and reference values: `artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl`
  (226 families; `L`, `L_ray` per s = 1..12, `null` where not reached).

## Task (per family)

1. **Uncapped generic table.** TB's least-cost table of side-subtree summaries, without the cost cap, iterated to its least fixed
   point (no new summary and no lower cost); stop with `closed = false` past 200,000 summaries or the family's time limit.
2. **Ray-summary graph.** Nodes: summaries of the subtree of a ray copy C_j that contains the target (an own distinction of C_s
   chosen), taken at the copy's ports. Base nodes (at C_s): every choice of C_s's own members containing at least one own distinction,
   with **every** SELF call of C_s treated as a side call (side summaries from the table). Edges (one step up, depth-independent): from
   a node at the ray child, combine with C_j's own chosen members and side summaries of C_j's other SELF calls, cost = own members +
   side costs. Keep partial summaries over all of C_j's environment until every child is joined; never deduplicate before projecting
   to the ports. Acceptance: TB's root test (a top port chosen; some combination empty; every one-forgotten combination non-empty), with
   its cost. Build all nodes reachable from the base nodes (cap 2,000,000; `complete` when the frontier empties).
3. **Gate.** From the graph, L(s) = min over base node, s middle steps up to C_0 and acceptance (min-plus by layers), for s = 1..12;
   it must equal the reference `L` wherever the reference is not null. Report every mismatch.
4. **Rate.** Trim to nodes reachable from a base node and co-reachable to acceptance; strongly connected components; Karp's minimum
   cycle mean per cyclic component; λ_true = the minimum, exact fraction. Also: `zero_cycle` (a zero-weight cycle in the trimmed
   graph), `acyclic` (no cycle: bonds stop at large s), `trimmed_nodes`.
5. **Fallback** when the table or graph is not closed: λ over the listed part only, marked `upper_bound` (it can only overstate λ).
6. Per family JSON: `idx`, `closed`, `table_size`, `complete`, `nodes`, `trimmed_nodes`, `gate_ok`, mismatches, `lambda_true`
   (string, float), `zero_cycle`, `acyclic`, `upper_bound`, `seconds`, `peak_mb`, `status`.

## Validation (report each)

- The gate on 10 small families of the study set (all closed and complete).
- A hand-made family with no side calls: λ_true must equal PROVED-RATE's λ (its `rates_all.jsonl`) for that family if it is in the
  study set; otherwise construct one from the study set by removing side calls in a copy and compare against BD's ray DP rate.
- The 4 families whose reference deficit L_ray − L reaches 3 by depth 7 (find them in the reference): report λ_true, λ_ray.

## Deliverables (inside CODEX)

`true_rate.py` (module), `run_rate.py --workers N --only IDX... --seconds-limit S --output NAME` (append one JSON line per family,
skip done ones), `validation.json`, a smoke run on 5 families with time and peak memory (`smoke.jsonl`), and `REPORT.md` (what was
written, validation, smoke timings, an estimate for all 226 at 3 workers, deviations, "Ambiguities").
