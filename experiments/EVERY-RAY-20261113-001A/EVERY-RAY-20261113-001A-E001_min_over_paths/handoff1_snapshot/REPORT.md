# EVERY-RAY-20261113-001A: computation hand-off

Status: implementation complete; requested smoke and executable validation gates in progress. The full run has not been launched.

All task writes are inside this directory. The reach census, its family archive, the draws, and its imported repository dependencies are read-only. No Git mutation was run. Neither forbidden experiment directory was read. Commands use `.venv/bin/python -B` from `/home/jscul/p-vs-np-contact-first`.

## Implementation

`paths_dp.py` reuses the census preparation, block maps, operation maps, min-plus layers, and exact Karp implementation. Its middle operations include every SELF call and every subset of S's own distinctions. The start uses the unchanged first entry. The closing reads every frontier call as its usual limit relation. Zero-cost successors are stored as a relation rather than the census's single successor. Exact residue certificates use explicit zero-cost cycle witnesses and retain all transitions before and after a cycle visit.

`run_paths.py` resumes one JSON line per family, preserves an interrupted tail before repair, and skips already recorded keys. The computing parent and at most two children are the only computing processes. A family has the specified 12-distinction, 300,000-node, 300-second, and 3 GB limits. The monitor reads only its own process IDs and stops a family above 7.5 GB aggregate resident memory. Carry-only rows preserve census evidence separately from their new zero work counts.

`smoke_paths.py` freezes `Random(1113).sample(sorted_eligible_keys, 1000)` before computing. Smoke class shares are written only to `smoke_summary.json`.

`summarize_paths.py` joins the whole archive and draws, records exact counts and missing records, and computes P1 with exact unresolved bands and a draw bootstrap. Requested summary fields whose denominators or symmetry definitions are unspecified remain explicitly pending. No scientific interpretation is made.

## Commands

Smoke (run in this task):

```bash
.venv/bin/python -B experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/smoke_paths.py --workers 3
```

Full run and summary (not run in this task; all output stays in CODEX):

```bash
.venv/bin/python -B experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/run_paths.py --workers 3 --out experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/full
.venv/bin/python -B experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/summarize_paths.py experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/full
```

The same full-run command resumes after the session ends. It does not depend on a background process from this hand-off.

## Validation and resources

Initial checks passed: Python parsing/imports; branching zero-cost cycle controls; a residue gap control; incomplete-graph positive-certificate and growth restrictions; safe analysis of an interrupted graph prefix; and exact equality to the census graph, start, closing and singleton zero successors on a one-SELF example with 1,562 nodes and 3,124 transitions.

Summary synthetic checks passed for linear quantiles, exact fractions, unresolved bands, original draw ordering, coverage, and pending ambiguous population fields. No bytecode was written.

Final gate counts, smoke timings, resident-memory peaks and the projection will be filled from the recorded outputs after execution.

The first smoke attempt recorded 68 families before interruption for a runtime repair. A worker received its 3 GB memory-stop signal during `guard_thread.join()` in cleanup and exited. Its unresolved error record and a second interrupted worker's unresolved record are preserved. Cleanup now ignores both memory signals before joining and restores their previous handlers afterwards. Actual SIGUSR1 and SIGUSR2 injection at that point passed. The runner now journals telemetry atomically at startup, after each result and on interruption, retaining attempt history and only its own process IDs. No scientific transition changed.

The first attempt's exact aggregate memory peak and final elapsed time were not retained by the old runner. `smoke_attempt_1.json` records that gap, the observed completed-family peak, and the last reported elapsed time (1,357.1 seconds). Later measured peaks must not be presented as the missing overall peak. The two error rows have no per-family duration; the final projection therefore gives explicit zero-time and nominal-300-second scenarios for those missing times instead of imputing one point.

The exact G-last selection is in `gate_last_keys.json`: 224 original LS keys all matched to complete archived census growers. There are 227 positive-rate PR reference rows; three are census-unresolved (indices 692, 847, 1018), and the manifest preserves their caps/statuses. They are not silently treated as growers.

## Ambiguities

1. **Start versus all paths.** Should the start remain the census's first main entry, as explicitly directed, or minimize over main entries? For a one-definition family main = S, selecting only the first start excludes other root choices already at depth 1. The prescribed middle-only DP is implemented without changing the start. G-last still makes its prescribed comparison to the census's last-call ray, whose start also changes; every failure is retained.
2. **G-brute depth.** What precisely is the “preperiod plus period of its Karp graph”? Karp supplies a cycle mean. The supplied code's period and onset are residue-certificate outputs, not a defined preperiod of a weighted min-plus sequence, and may be absent for growers. No substitute depth is chosen. The affected G-brute gate is skipped rather than replaced by a fixed-depth check.
3. **G-brute frontier and root.** Which constraints close the full-tree frontier, and should every main entry or only the prescribed first entry be eligible? No frontier or root policy is selected for the skipped gate.
4. **Main endpoint.** The census's unchanged start requires a member among main's ports. Does the object phrase “a distinction of C_0” instead permit an endpoint only among main's other distinctions? The DP retains the explicit unchanged census start; the independent brute requires an explicit endpoint policy.
5. **Fixed indices with several main entries.** When main differs from S and has several entries to S, how does an S SELF index choose a main entry? Nonfirst fixed-index diagnostics are skipped for affected families. A bounded first fixed ray is enough to certify `mixed_path_needed=false`; a missing diagnostic is never treated as unbounded.
6. **Symmetries.** Which automorphisms define S's port symmetries: its inlined call body, its allowed states, or G[S]? May own distinctions also be permuted? `symmetry_inequivalent` and the affected count remain pending. Literal duplicate counts are available independently.
7. **Population denominator.** Which unresolved families belong to the population defined as having a persisting bond? Are mixed-by-residue families included? How can none/lost receive nonzero class bands inside that population? The summary writes all raw joined counts, and skips the affected population shares instead of choosing a denominator.
8. **Population bootstrap frame and order.** Are draws resampled from the whole archive or conditional on population membership? Does “shared stream” mean common archive resamples for all cells, or sequential cell resamples, and in which order? Those class-share bootstrap endpoints are pending. The separately specified P1 frame is first-ray growers with c >= 2; its two tables share one `Random(20261113)` stream in the reported order, all followed by excluding the exact G-last keys, and use 2,000 resamples with linear quantiles.

## Deviations

No full job, ticket update, scope update, publication, or commit is performed. Only the affected ambiguous calculations are skipped. The specified DP and executable gates are retained even where their comparison exposes the start-block tension. No result is interpreted.
