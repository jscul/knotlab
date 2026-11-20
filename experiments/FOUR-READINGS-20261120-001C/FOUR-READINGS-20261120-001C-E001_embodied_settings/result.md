# Exact six-mark comparisons, referee pending

With settings from the state, no not-all-equal full-register pass in the exhaustive census, construction or fresh sample gave a selected-bit score above two. The all-size results and the distinction between conditional and free indices are in the [study results](../../../research/FOUR-READINGS-20261120-001C/results.md). The [referee handoff](../../../research/FOUR-READINGS-20261120-001C/referee_handoff.md) names the remaining question and the hypothesis checks.

## Reproduce from the repository root

The main design digest is bound by contract.json. stress_addendum.json binds the prospective fourth archive input and its separate design. Use a fresh scratch directory for the shared runner. The 32 census shards each cover a size and holder count. The primary count used two worker processes, a 1 GiB case ceiling, and a 4 GiB service ceiling. The check completed in seconds.

```sh
study_dir=experiments/FOUR-READINGS-20261120-001C/FOUR-READINGS-20261120-001C-E001_embodied_settings
census_run=$(mktemp -d)
export OPENBLAS_NUM_THREADS=1
.venv/bin/python -B "$study_dir/observables.py"
.venv/bin/python -B scripts/longrun.py launch "$study_dir/job.py" --out "$census_run" --unit study-embodied-census --workers 2 --case-mem 1G --mem-max 4G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$census_run" --foreground --limit 20
.venv/bin/python -B scripts/longrun.py resume --out "$census_run"
.venv/bin/python -B scripts/longrun.py wait --out "$census_run"
.venv/bin/python -B "$study_dir/gather.py" "$census_run"
.venv/bin/python -B "$study_dir/pieces.py"
.venv/bin/python -B "$study_dir/samples.py"
.venv/bin/python -B "$study_dir/samples.py" --extra
.venv/bin/python -B "$study_dir/verify.py"
python3 -B scripts/track.py objects-gate research/FOUR-READINGS-20261120-001C/prior_work.md
```

The [output family](../../../artifacts/FOUR-READINGS-20261120-001C/FOUR-READINGS-20261120-001C-E001_embodied_settings) contains integer counts for all required mark projections, full-register changes and denominators. Census tables group identical 64-entry count arrays with multiplicities and separation band counts. Each group records one source with its six ascending local marks. All 36 within-side orders are scored, including both possible orders of response marks for each selector. The compressed records use gzip with fixed timestamp. The run also compares exact rational values against the inherited independent scalar scorer, re-enumerates leading examples, checks every two-terminal factor mathematically and numerically, replays both weightings on the supplied positive control, verifies all 16 projected knot laws through the canonical checker, and checks the structural totals by counting fixed presentations under all permutations of holders. Every census stage passed, and a neutral program referee is still pending.
