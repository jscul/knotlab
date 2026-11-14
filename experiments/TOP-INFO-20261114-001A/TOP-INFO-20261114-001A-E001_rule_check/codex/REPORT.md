# Is reading the whole rule: census computation

Scope: ticket `TOP-INFO-20261114-001A`, experiment `E001_rule_check`. All authored files and outputs stay in this CODEX directory. Source data and implementations are read in place. No Git command, publication, tracker change, external research, or definition change was performed.

## Current result

Check 1 is computed for the full supplied population from READ-RULE’s retained exact tie summaries, using the theorem’s existential quantifier. Checks 2–4 are implemented; the shared-runner smoke results below are partial and do not establish full census predictions. The full run is prepared and unlaunched for the thread.

Final population: 5789 in scope and 175 out of scope. In scope, 5,067 are window-bounded, seven more have a bounded path-DP certificate, 632 are growing, and 83 are undecided. Out of scope, 129 are window-bounded and 46 undecided. This resolves READ-RULE’s earlier 90-versus-83 ambiguity by using the supplied final path certificates.

## What was built

- `top_data.py` reuses READ’s byte-offset index and streamed CARRY SHA-256 receipt, verifies file size/mtime, reads one original record at a time, and applies the seven path-DP bounded certificates. `catalog.json` stores metadata and selections, without copying source relations.
- R uses “some repeating state in which the knot’s position is carried and the exception fails.” Existing `any_state_survives` flags supply the full check; `checks.py` also recomputes the flags from exact projections on each completed smoke family.
- Plain pinning compares the exact joint projection count with the product of its two marginal counts. Bond-pinning searches shattered subsets on both sides, without the size-six restriction. Searching maximal shattered sides suffices for existence: extending a witnessing side preserves non-fullness of the union. It does not infer bond-pinning from plain correlation.
- `two_block.py` retains all main-block distinctions in the transfer state and identity partition, treats word depth zero as the same copy when main is S, and uses whole-block contexts at each direct initial call. Later transfer composition is CARRY’s unchanged operation. Every candidate bond contains a main port and an end-own distinction; all proper one-variable deletions must be full.
- `two_block_brute.py` independently unfolds the raw syntax through the target’s children and enumerates its exact CNF projection. It also checks independent bond minima and recovers CARRY’s original port-only projection. It is callable for any supplied family; it does not choose the unspecified official 30-family sample.
- `job.py` and `summarize.py` preserve caps and missing cells, compute cross-tabs, both family and draw-weight shares, G and T1–T3, and the requested hiding screen. Full key/residue lists are in the JSON outputs.

## Frozen execution and controls

The full job has 5,964 pinning cases, 961 two-block cases (every 761 not-already-bounded family, plus the first 200 bounded families in sha256("TOP:" + key) order), and the first 100 certified-forgetting families in the same order: 7,025 cases. Both scope populations are included. Selection code is independently checked by `verify.py`.

Use `.venv/bin/python -B`. The prepared runner has one worker, a 3 GB case ceiling and 5 GB total ceiling, retaining headroom below the requested approximate 8 GB total. The foreground runner uses a parent and one worker. Numerical libraries have one thread. Internal inherited limits are 585 seconds and 2,800,000,000 bytes per case; Q has the same 200,000 stored-state/2,000-level caps and bond size at most six. Independent unfolding retains CARRY’s caps of 15,000 variables, 100,000 clauses, 25,000 copies and 1,048,576 projection rows.

Depth `s` in the code is CARRY’s word length; absolute copy depth is `s + wrapper`. The forgetting comparison is therefore `2 + floor(s/r)`, equivalently `2 + floor((absolute_depth-wrapper)/r)`. Overlapping eventual congruences and available finite prefix cells are compared for `U2 <= U` whenever both are finite. A finite repeating U2 is checked at a sufficiently late representative against the forgetting lower bound. `> 6` is an exhausted bounded search, not a finite bound or a growth proof.

The independent pinning controls pass the advisor’s 26-state hiding example (plain pinned, no bond-pinning), full-product, opposite-pair and NAE controls, plus all 255 nonempty complement-closed relations on four distinctions against exhaustive minimal-support enumeration. See `controls.json`.

Two implementation fixtures, a self-holding main and a wrapper with multiple direct entries, are recorded in `validation.json`; all 60 covered words through s=3 agree in their entire two-block projection, independent bond minimum and recovered old port-only projection. These fixtures validate implementation and do not fill the unselected official brute30 gate.

## Computed counts

Runner records read from `census_full`: 7025 / 7025 cases (5964 pinning, 961 two-block, 100 forgetting). Pending: 0. Failed runner records: 0.

| Scope and stratum | Families bounded on a residue without R | Draw weight | Such residues |
| --- | ---: | ---: | ---: |
| in:O | 93 | 93 | 93 |
| in:nine_exception_families | 9 | 9 | 9 |
| in:others | 486 | 541 | 494 |
| out:O | 3 | 3 | 3 |
| out:others | 22 | 22 | 22 |

The strata “O”, “nine exception families”, and “others” are disjoint. A family appears once per listed stratum, with every qualifying residue retained in `summary.json`. A partial window certificate is listed only for its bounded Q residues. READ’s carried-set residue period and the Q-window period are both retained, rather than silently identifying them.

| Check | Status | Observed violations / failures | Remaining or unavailable |
| --- | --- | ---: | ---: |
| G: R | pass | 0 | 0 |
| G: bond_pinning | pass | 0 | 0 |
| G: upper_comparison | pending | 0 | 84 |
| G: forgetting | pass | 0 | 0 |
| G: brute_force | skipped_ambiguity | 0 | official sample unspecified |

Overall G: **inconclusive**. T1: **pass**; T2: **fail**; T3: **fail** (9 of the 83 formerly undecided newly bounded on every residue; threshold 10). Missing runs are pending; actual caps count as prescribed in T1–T3.

Hiding screen completed matches: 48. Full lists and incomplete candidates are retained. G2 not certified is the requested operational criterion; when G2 is capped it does not prove a non-rectangular long product. Absence of a two-block bond refers to the search through size six.

## Timings and validation

Recorded worker computation: 33329.807 seconds summed over the read runner records. Maximum recorded worker high-water RSS: 1,222,836,224 bytes. Final metadata/summary aggregation: 0.767 seconds. Source-index provenance and its original streaming time are reused, not counted as new computation.

The pinning controls took about 0.04 seconds; the two independent unfolding fixtures took about 26 seconds together. `validation.json` preserves actual timings and resource measurements. The per-case runner records retain timings, caps and memory measurements; `frozen_sources.json` binds local code and source machinery. A full job has more than ten minutes of census work and is deliberately left to the shared runner. The 20-case smoke is validation only, with its retained output available for inspection.

Empirical checks do not discharge Theorem P′, the two-block bound, or localisation proof obligations. No mathematical theorem is inferred from an incomplete census.

## Ambiguities

1. **Which 30 census families and selection rule are intended for the separate brute-force gate?** The specification freezes SHA-256 ordering for the 200 bounded and 100 forgetting controls, but supplies no selection of the 30 brute families. No official sample is chosen. Only that official sample and its G component are skipped; the complete per-family independent comparison is implemented and two explicit engineering fixtures were checked.

The prior R quantifier ambiguity is explicitly resolved by the user’s “some state” instruction. The old population discrepancy is resolved by the final path-DP certificates. READ’s conditional-product storage-cap ambiguity and undefined descriptive counterexample classifier do not affect this study. The user’s explicit `U2 <= U` comparison resolves the preregistration’s less precise “agrees” wording.

## Thread launch commands

The full service has not been launched and no run has been registered. From the repository root, after reviewing the retained smoke records:

```sh
.venv/bin/python -B scripts/longrun.py resume --out experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex/census_run
.venv/bin/python -B scripts/longrun.py status --out experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex/census_run --json
.venv/bin/python -B scripts/longrun.py wait --out experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex/census_run
.venv/bin/python -B experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex/summarize.py --run census_run
.venv/bin/python -B experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex/verify.py
```

The thread handles any registration outside CODEX. Supplying the intended brute30 selection remains necessary before that official gate can be completed. Until then, even a successful full numerical run leaves G inconclusive.
