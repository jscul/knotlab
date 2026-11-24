# LOCAL-ROUND-20261123-001A-E001: one birth at a time from what is built

This is the engine and the runs for the frozen pre-registration
`research/LOCAL-ROUND-20261123-001A/preregistration.md`, written from it, from
`research/LOCAL-ROUND-20261123-001/definitions.md` and from the shared definitions of `RING-IN-BALANCE-20261123-001`.
The reference engine (ticket A of that epic) is imported unchanged; its SHA-256 sum is checked on import. Readings are
in `deviations.md`.

## Files

| File | What it is |
| --- | --- |
| `lr_core.py` | Groups (definitions step 1), plans (LR 2.1, with the waiters' recursion), starts, and this study's own complete round (for the gate) |
| `lr_reference.py` | Runs the reference engine; the last round R for a cutoff; the reference knot data |
| `lr_laws.py` | The laws R0, R1, R2, R3, T(d), R3L and the control, reading only the run's structure |
| `lr_search.py` | The comparison: match, cutoff, outcomes; every order (breadth-first over memo keys), sampled, x-last; listings |
| `lr_configs.py` | The registered runs as data |
| `lr_gate.py` | Run item 1, the gate |
| `lr_run.py` | One run (a start, a law family, a cutoff, a law), with the three kinds of order |
| `lr_run_all.py` | Every registered run, up to 8 processes at once |
| `lr_summarize.py` | Verdicts for P1-P14, the comparison with the disclosed numbers, the named replays |
| `test_lr.py` | Unit checks on structures built by hand |

Outputs are in `artifacts/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/`:
- `gate.json`;
- `runs/<run>.json`, one per run;
- `logs/<run>.log`;
- `listings/*.json`, birth-by-birth replays;
- `summary.json` and `summary.md`.

## Rerunning

Use the repository's Python, `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`, from this directory.

```bash
python -B test_lr.py                       # unit checks
python -B lr_gate.py                       # item 1: the gate (20 start and law pairs, 5 altered controls), under a second
python -B lr_run_all.py                    # items 2-4 and the P4 extra: 193 runs, 8 at a time, each capped at 8 GB
python -B lr_run_all.py --list             # the runs and their parameters
python -B lr_summarize.py                  # verdicts, comparisons, replays
```

Each run can also be made alone, for example:

```bash
python -B lr_run.py --start 'D2(4,3)' --ration RATION-3 --treatment CANCEL-WAIT --cutoff 1 --law R1 \
    --cap 10000000 --budget 420 --id 'D2(4,3)-R3W__r1__R1'
```

Run ids are `<row>__r<cutoff>__<law>` for the first table, `TD-<start>__r1__T(d)` for the family T(d),
`<row>-r3__<law>` for item 4, and `D2(6,3)-R3W__r1__R3L` for the extra run that P4 needs at n = 6.

## Budgets

The every-order searches are capped at ten million keys for the first table and one million for T(d) and item 4. They
also have a time budget: 420 s for the first table and 300 s otherwise. A search that reaches its cap or budget is
reported unfinished, with the number of births to which every order was searched. The sampled and x-last orders
always run in full.
