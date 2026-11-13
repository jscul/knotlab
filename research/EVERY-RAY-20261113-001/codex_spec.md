# Codex specification: the least bond over all descending paths (EVERY-RAY-20261113-001A)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it: write the
question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from the repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/` (CODEX below). Modify, move or delete no
  other file. Run no git command that changes anything.
- Use `.venv/bin/python -B`. At most **3 processes** at a time; keep total memory under about 8 GB. Another study shares the
  machine. Touch no process you did not start.
- Repository material only. Do not read `experiments/TRUE-BOND-20261113-001A/` or `experiments/TRUE-RATE-20261113-001A/`.
- **Do not run the full job.** Write the code, run the validation and smoke below, and stop. The full run is launched by the thread
  from your runner, so it must be resumable and independent of your session.

## Inputs (read-only)

- The reach census: `experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/` — `reach_dp.py`
  (the inlined ray DP, `Preparation`, `FamilyDP`, `settled`, `build_graph`, `classify`, caps, `INF`), `run_census.py` (the resumable
  runner), `validation.py`, `brute_check.py` (the independent brute force), `summarize.py`, `g3_keys.json`, and under its `full/`
  the family records; the draws `draws.jsonl.gz`. Reuse this code; the object differs only in the middle transition.
- `experiments/SHORT-DESC-.../dlang.py` (L), `experiments/LIMIT-STATE-.../census.py` (LS, `usual`, `relation_clauses`).
- The reach census's `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz`
  (one record per distinct family: `key`, `class`, `lambda`, `L_ray`, `complete`, …).

## The object

For a family, after inlining as in the census: the ray definition **S**, and its SELF calls S_1, …, S_c (c of them), each on three
of S's distinctions. A **descending path** chooses, at every level, one S_i to make the next copy; a **fixed-index ray** always
chooses the same one. **L_path(s)** is the least bond, over all descending paths, between a distinction of C_0 (main) and an own
distinction of the depth-s copy, with members restricted to the chosen copies' own distinctions. (The census's L_ray is L_path
restricted to the first-index ray.)

## The DP (generalise the census's middle transition)

Use the census's node = (F, Gf) over the 8 states of a copy's three ports, its start block (main) and closing block unchanged.
The **middle transition is a min over which SELF call continues**: from a node, for each S_i, for each subset W of S's own
distinctions, take the census `advance` with S_i as the ray call (its three arguments the outgoing interface) and **every other SELF
call S_j (j≠i) read as the limit relation G[S]** (a side call), cost |W|; the edge goes to the resulting node. Build the reachable
graph by breadth-first search over all these edges. Then, exactly as the census: recompute L_path(s) for s = 1..30 by min-plus
layers; trim to nodes reachable from a start and co-reachable to an accepting closing; λ_path by Karp (exact fraction, None if the
trimmed graph has no cycle); the referee's exact residue test (`exact_eventual_bound`) for eventual boundedness; and the per-family
classes exactly as the census (grows / bounded / mixed by residue / lost at large depths / none at any depth / unresolved), now on
this graph.

**DP soundness — check explicitly (see Validation V1).** The (F, Gf) node must carry nothing tied to the call index: a copy's
incoming interface is always its three ports, and S_i's three arguments are how this copy's states feed the child's ports. Verify
on three cases that the generalised `advance` agrees with a direct recomputation: (a) two SELF calls sharing an argument
distinction; (b) one SELF call repeating a distinction on two ports; (c) a non-chosen SELF call read as G[S], matching the census's
own side reading.

**Caps (asymmetric).** 12 distinctions per block, 300,000 nodes, 300 seconds. Branching multiplies nodes by c, so a cap-out
concentrates where boundedness is likeliest: a capped or timed-out or over-block family is **unresolved**, never grows; record it
with its SELF-call count. A positive certificate (bounded_all or eventually_bounded) on an incomplete graph still gives **bounded**
(the census rule).

## Population (per family)

Apply the census's settled classes first. **S1 (limit dead), S2 (no copy), S3 (S has no own distinctions) are path-independent**:
carry the census's verdict. **S4 is not path-independent** (it was defined against the first ray call), so recompute it over all
paths: a family is settled only if every own distinction of S lies in no K call of S, in no non-TOP side call, and in **no SELF
call's arguments at all** (not just the first). Run the DP on every family that is not S1/S2/S3 and has **at least two SELF calls**
(c ≥ 2); for c = 1 carry the census L_ray and class (one ray; L_path = L_ray), marked `one_ray`. Record for every family: key, c,
classes along the first ray (from the census) and over all paths (this run), λ_path, the exact-test fields, L_path(1..30), whether
its bounded verdict needs a **mixed** path (no single fixed-index ray is bounded — test each fixed-index ray with the census DP),
whether the zero-mean cycle uses a **pass-through** SELF call (arguments a permutation of S's own ports 0,1,2), the families that
have **no first-ray bond but a persisting bond over paths** (census class none/lost on the first ray, but grows/bounded here), and
seconds, nodes, complete, status.

## Gates (run in validation)

- **G-reg (regression, not validation).** On 500 one-SELF-call families, the DP with c = 1 gives the census's graph, λ and class.
- **G-last.** On the 224 one-definition first-ray growers, L_path(s) ≤ the last-call fixed-index ray's L_ray(s) at every recorded
  depth (recompute the last-call ray here with the census DP, do not read the stress-test file), and ≤ the census first-ray L_ray(s).
- **G-brute (independent).** A brute force that shares no code with the DP: unfold the family to depth s as a flat NAE instance
  (every descending path's copies present), and for the least bond search enumerate member sets and test each with
  `PYTHONPATH=tools python3 -B -m knotlab check` (or a direct satisfiability enumeration over the unfolded distinctions, ≤ 22),
  taking the minimum over which depth-s copy is the target. It must reproduce L_path(s) for s = 1..s_max, with s_max per family the
  preperiod plus period of its Karp graph (not a fixed depth), on a stratified panel of 120 families: at least 10 of each
  over-paths class where available, at least 40 with several definitions, and at least 20 with c ≥ 3. Report every disagreement (a
  DP value over 7 agrees with "none up to 7").
- **G-node.** The three soundness cases (a,b,c) above agree with a direct recomputation.

## Smoke run

Sections on 1,000 families drawn by `random.Random(1113).sample` from the sorted keys of the c ≥ 2, non-S1/S2/S3 families. Report
timings by over-paths class and by c, memory peak, and the projected full-run time on 3 workers. Do not report class shares from the
smoke (write them only to its file).

## Runner and summary (for the thread's full run)

- `run_paths.py --workers N --out DIR`: all c ≥ 2 non-S1/S2/S3 families, one JSON line each, resumable (skip keys already in the
  output), each family in a worker process with the caps; a worker past 3 GB stops that family as unresolved. Also carries over the
  census verdict for c = 1 and S1/S2/S3 families (from `families.jsonl.gz`) so the summary joins the whole population.
- `summarize_paths.py DIR`: joins the draws with the records and writes `summary.json` with, among families that have a persisting
  bond on some path (the population), by count and by A79 draw weight, split by first-ray class and by c:
  - the over-paths class shares (grows / bounded / mixed by residue / lost / none / unresolved), unresolved against the class (low)
    and for it (high), with a 95% bootstrap over draws (2,000 resamples, `Random(20261113)`, linear quantiles, shared stream);
  - among first-ray growers with c ≥ 2: the share now bounded over paths (point, and the failure threshold of prediction P1), and
    the same **excluding the 224 one-definition growers**;
  - the count of bounded verdicts that need a **mixed** path (no fixed-index ray bounded);
  - the count of families with **no first-ray bond but a persisting bond over paths**;
  - growers over paths (λ_path > 0): their count, and the count whose SELF calls are **inequivalent under S's symmetries** (not a
    duplicate or a port-permutation image of another), and whether any zero-mean bounded cycle uses a **pass-through** call;
  - λ_path's distribution, and the unresolved share by c.
  Shares by count are exact; the prediction verdicts use the draw-weight bands.

## Outputs (all in CODEX)

Your code; `gates.json` (every gate with every mismatch); `smoke_families.jsonl`, `smoke_summary.json`; `REPORT.md` (what you ran,
exact full-run commands, timings, memory, deviations, Ambiguities). Do not interpret results.
