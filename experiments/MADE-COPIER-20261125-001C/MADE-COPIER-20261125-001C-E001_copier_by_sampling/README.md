# MADE-COPIER-20261125-001C, experiment E001: a copier by sampling

The engine and runs of the frozen study `MADE-COPIER-20261125-001C` (a copier by sampling: how often a growth, with
every take sampled under a stated weighting, makes a pattern that leaves two of what it meets, more often than its
controls allow). Written from the frozen texts alone: the pre-registration (`research/MADE-COPIER-20261125-001C/
preregistration.md`, "PC"), ticket C's definitions and claim, the definitions of tickets A and B, the fold study's and
the shared definitions, and the data files `starts_c.json` and `cases_c.json`. Its author has not seen the drafter's
scratch prototype or its outputs. Every reading where the text left a choice is in [deviations.md](deviations.md),
written before the run it affects.

The growth is the fold study's engine
(`experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/`: `pm.py`, `knots.py`,
`paired.py`), imported unchanged, with ticket A's `mc.py` for its descents and tie classes; their SHA-256 sums are
checked by every run. Four module attributes are set at import, the files unedited: the guard's limits multiplied by
ten (DB 3.9), and three exact equivalents for speed or for the fully masked kind, each checked against the engine's
own function (deviations 3, 39, 40, 41). COPY-LAW(t) is the fold study's name for (FLOOR1, t, RELEASE), not a law of
copying. `contract.json` and `identity.json` are the study's own files and are not changed here.

## Files

| File | What it holds |
| --- | --- |
| `mcc.py` | the engine: census, laws, seeds, samplers, the roster read, pairs, descents, the readings, ties birth by birth, the continuations of the five kinds, the knot test, the tests' statistics |
| `study.py` | one sampled growth analysed: pairs, readings, cases, the first stage at 100, the confirmation, counts by form; output helpers and the memory cap |
| `test_mcc.py` | unit tests on hand cases and against the engines (`test_mcc.json`) |
| `gate.py` | R0, the gate (`gate_R0.json`, `gate_R0_case_listing.json`, `gate_R0_cases.jsonl`) |
| `controls.py` | R0b, the controls of the rate rule (`controls_R0b.json`) |
| `replay_disclosed.py` | the disclosed numbers of R0b replayed at the scratch's bounds (`replay_disclosed.json`) |
| `runs.py` | the census runs R1a to R1d and R2 (`<run>.jsonl.gz`, one record per sampled growth) |
| `r8.py`, `r9.py`, `r7.py` | R8 (renamed starts, sampled), R9 (the knot test at every round), R7 (the exact renaming check) |
| `r3.py` | R3, the confirmations, m counted over the main runs read before any confirmation (`R3.json`) |
| `tidy.py` | rewrites a run's record file as one gzip member (each growth once) and records its wall times (`run_times.json`) |
| `summarize.py` | every prediction's verdict, the rates and zero bounds, the knot tests and renaming checks: `summary.json`, `summary.md` |

Results are written to `artifacts/MADE-COPIER-20261125-001C/MADE-COPIER-20261125-001C-E001_copier_by_sampling/`.

## How to run

The interpreter is the workspace's `.venv` (`/home/jscul/p-vs-np-contact-first/.venv/bin/python`), with `-B`, in this
folder. Every worker caps its address space at 6 GB. In the registered order:

```
python -B test_mcc.py
python -B gate.py --procs 6            # R0
python -B controls.py --procs 6        # R0b
python -B replay_disclosed.py
python -B runs.py R1b --procs 6        # then R1a (with its registered size), R8, R9, R2, R1c, R1d
python -B r8.py --procs 6
python -B r9.py --procs 6
python -B runs.py R2 --procs 6
python -B runs.py R1c --procs 6
python -B runs.py R1d --procs 6
python -B r7.py --procs 6
python -B r3.py --procs 6              # R3, after every main run
python -B summarize.py
```

`runs.py <run> --prefix N` reads the first N starts of the run's order (a registered half or quarter when a run is cut
for time, deviations 42 onward); `--append` resumes a run whose records are complete rows.

## Sizes run (the owner's rule: no run past about an hour; deviations 42 to 57)

| Run | Registered | Run | Why |
| --- | --- | --- | --- |
| R1b | 2,000 starts | first 1,000 (half) | timed at 56 min, ran slower; cut at 6.6 min (dev 43) |
| R1a | 3,344 starts | first 836 (quarter) | timed at 2.7 h whole (dev 47) |
| R8 | 219 starts | first 110 (half) | timed at 72 min (dev 49) |
| R9 | 7,287 growths | all | dev 50 |
| R2 | 500 starts | all | dev 51 |
| R1c | 1,000 starts | first 250 (quarter) | half chosen on timing, then cut to the quarter mid-run (dev 52, 53) |
| R1d | 120 starts | first 30 (quarter) | run whole on timing; single growths of 30 to 60 min; stopped past the hour (dev 55) |
| R7 | 158 checks | all | resumed after a memory stop (dev 56, 57) |

`R1d_beyond_quarter.jsonl.gz` holds R1d's growths of starts 30 to 119 that were written before it was stopped; they are
not part of the size run and enter no rate or verdict.
