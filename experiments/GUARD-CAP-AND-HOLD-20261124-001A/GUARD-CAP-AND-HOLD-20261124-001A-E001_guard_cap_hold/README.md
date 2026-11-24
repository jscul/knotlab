# GUARD-CAP-AND-HOLD-20261124-001A-E001: the guard under the cap of three and under holding

This is the engine and the runs for the frozen pre-registration
`research/GUARD-CAP-AND-HOLD-20261124-001A/preregistration.md`, with the definitions of
`research/GUARD-CAP-AND-HOLD-20261124-001/definitions.md`. It is the engine of `LOCAL-ROUND-20261123-001A`, copied
here and extended by its author; the earlier folders are untouched. The reference engine (ticket A of
`RING-IN-BALANCE-20261123-001`) is imported unchanged, and its SHA-256 sum is checked on import. Readings and the gate's
finding on D are in `deviations.md`.

## Files

| File | What it is |
| --- | --- |
| `lr_core.py` | Groups, the plan (LR 2.1 with the cap's D, the fillers, holding: stayers, the waiters' and stayers' roster, idle parts), starts, and the engine's own complete round computed through the plan |
| `lr_reference.py` | Runs the reference engine; the last round R (GCH 3 item 6); barred-at-birth counts and demands from its records; the match by earliest round |
| `lr_laws.py` | R1, R2, R3, the repaired guard R3′ ("has given"), T(d) and the control; why a reference knot was never made |
| `lr_search.py` | The comparison: every order (two million keys, checked at the end of a level, no time budget), sampled, x-last; listings |
| `gch_configs.py` | The registered runs as data |
| `gch_gate.py` | Run 1, the gate: D, f, usable and barred counts and stayers compared; three altered controls; the start clause asserted |
| `gch_run.py` | One run (start, law family, cutoff, guard) with the three kinds of order |
| `gch_run_all.py` | Runs 2 to 4: 386 runs, at most 6 at a time, each capped at 8 GB |
| `gch_knottest.py` | Run 5, the knot test |
| `gch_summarize.py` | The verdicts, the holding table, where the stop rule falls |
| `test_lr.py` | The earlier study's unit checks, unchanged; they pass on the extended modules |
| `test_gch.py` | Unit checks of this study's additions |

Outputs are in `artifacts/GUARD-CAP-AND-HOLD-20261124-001A/GUARD-CAP-AND-HOLD-20261124-001A-E001_guard_cap_hold/`:
- `gate.json`;
- `runs/<run>.json`, one per run;
- `logs/<run>.log`;
- `run_all.log`;
- `knot_test.json`;
- `listings/*.json`;
- `summary.json` and `summary.md`.

## Rerunning

Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`, from this directory.

```bash
python -B test_lr.py && python -B test_gch.py     # unit checks
python -B gch_gate.py                             # run 1
python -B gch_run_all.py                          # runs 2-4 (python -B gch_run_all.py --list prints every command)
python -B gch_knottest.py                         # run 5
python -B gch_summarize.py                        # verdicts
```

To make one run alone:

```bash
python -B gch_run.py --start 'D2(4,3)' --family CAP3W --cutoff 1 --law R3 --id 'CAP3W-D2(4,3)__r1__R3'
```

The law families are:
- CAP3W = (CAP-3, CANCEL-WAIT, RELEASE);
- CAP3WF = the same with FILLERS;
- CAP3H = (CAP-3, CANCEL-WAIT, HOLD);
- R3H = (RATION-3, CANCEL-WAIT, HOLD);
- F1RH = (FLOOR1, CANCEL-RETIRE, HOLD);
- F1OH = (FLOOR1, CANCEL-OFFSHOOT, HOLD).

The guard `R3P` is R3′.
