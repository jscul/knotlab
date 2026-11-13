# Codex specification: proved rates of a ray-bond DP (PROVED-RATE-20261113-001A)

You are computing, not designing. Follow this specification exactly. If anything is ambiguous or seems wrong, do not resolve it:
write the question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from the repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex/` (call it CODEX below). Do not modify,
  move or delete any other file. Do not run git commands that change anything (no add, commit, stash, checkout, reset).
- Use `.venv/bin/python -B` (Python 3.13 with numpy and python-sat). Use at most 8 processes at a time.
- Do not read or use anything outside the repository.

## Inputs (read-only)

- `experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py` (call it BD). It defines
  `families_one_def()` (the 664 families as `(idx, defs)`), `run_family(defs, smax)` and the constants `INF`, `SMAX`.
- `artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl`: one record per family (`idx`,
  `L` the list of least ray-bond sizes for s = 1, 2, … as computed, `INF` = 10^9 meaning none; records with `unfinished` true have
  no `L`).

## What run_family computes (read its source; reproduce it exactly)

For a family `defs` (one definition with 3 ports), `run_family` builds, inside closures: the start layer (a dict from nodes to
costs, after "block 0" over all subsets `W` of block 0's distinctions that contain at least one of the ports 0, 1, 2); the middle
transition `advance(F, Gf, W, last=False)` for every subset `W` of the block's own distinctions (indices 3 .. V-1, including the
empty set), cost `len(W)`; and the closing `advance(F, Gf, W, last=True)` for every non-empty subset `W` of those distinctions,
accepting when `0 in F' and 0 not in G'`, cost `len(W)`. A node is a pair `(F, Gf)` of frozensets of integers. L(s) = min over
start nodes n (cost c), over walks of exactly s − 1 middle transitions from n (costs summed), and over accepting closings, of the
total cost; `INF` if none.

## Task, per family (all 664; parallelise over families)

1. **Refactor a copy** of `run_family`'s logic into your own module in CODEX exposing: `start_nodes(defs) -> {node: cost}`,
   `middle(defs, node) -> list of (W, node2, cost)` over all W, `close(defs, node) -> min accepting closing cost or INF`. Use the
   same tables and the same `advance`; do not change the semantics.
2. **Build the reachable graph**: breadth-first from the start nodes by `middle`, up to 2,000,000 nodes. Record `complete` = true
   when the frontier empties before the cap.
3. **Gate**: from the graph, recompute L(s) for s = 1 .. len(record L) by min-plus dynamic programming over layers (cost per node,
   s − 1 middle steps, then `close`) and check equality with the record. Report every mismatch (family, s, yours, record).
4. **Rate**: on the graph restricted to nodes that are reachable from a start node and from which some node with `close < INF` is
   reachable (the trimmed graph), compute the strongly connected components; for each component that contains at least one cycle,
   its minimum cycle mean by Karp's algorithm, as an exact fraction (integer costs). λ = the minimum over components (None if the
   trimmed graph has no cycle). Report λ as a fraction string "p/q" and as a float. Record whether the graph was complete; a
   capped graph's λ is reported but marked "partial".
5. **Bounded for every depth (sufficient test)**: for each node m of the trimmed graph, follow the empty-W transition
   (`W = []`, cost 0) until a node repeats; this gives a cycle. `bounded_all` = true if for some m every node of its empty-W cycle has
   `close < INF`. Also report `zero_mean` = true if λ = 0.
6. Record per family: `idx`, number of nodes, `complete`, `gate_ok` (and mismatches), `lambda` (string and float, or None),
   `bounded_all`, `zero_mean`, seconds.

## Outputs (all inside CODEX)

- Your code (any files).
- `rates.jsonl`: one JSON object per family as in 6.
- `summary.json`: counts of complete graphs; gate mismatches (total); λ distribution (counts per fraction); counts of
  `bounded_all`; counts of `zero_mean` without `bounded_all`; and the same split by the record's class, where the class of a record
  is: "bounded" if its `L` (finite values) is constant over the last 8 computed depths and its length < 30 (the original run stopped
  on a repeat); "rising" if it has 30 values and the last exceeds the first; "flat" if it has 30 values and the last equals the first;
  "capped" otherwise (fewer than 30 values without a stop on a repeat, or `unfinished`). Use exactly these definitions.
- `REPORT.md`: what you ran, timings, any deviation, and "Ambiguities".

Stop when every family is done or has been given up after 20 minutes of computation (mark it `timeout`). Do not interpret results.
