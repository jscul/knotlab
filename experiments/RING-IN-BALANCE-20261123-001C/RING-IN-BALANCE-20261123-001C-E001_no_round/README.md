# RING-IN-BALANCE-20261123-001C-E001: with no round supplied

An independent engine for ticket C, written from the frozen
[definitions](../../../research/RING-IN-BALANCE-20261123-001/definitions.md) and
[pre-registration](../../../research/RING-IN-BALANCE-20261123-001C/preregistration.md) alone. It shares no code with any
other engine in the repository. Its readings of the frozen text are listed in [deviations.md](deviations.md).

| File | What |
| --- | --- |
| `growth.py` | structures on real knots, the named starts, the live roster (met sets, joinable, parts, groups), one complete round, and that round applied to one part |
| `part_round.py` | the part-round law with its seven priorities, own times, detection of returns, and the P2 comparison with complete rounds |
| `birth_by_birth.py` | the birth-by-birth law (ANY and DEAD, RATION-3 and PRESENT-ORD, waiting and FIRST-COME, the four orders), with parts kept incrementally and jams recorded; the search of every order for C3 |
| `iso.py` | colour-refinement hash and exact isomorphism test (every bijection it returns is verified) |
| `selfcheck.py`, `selfcheck_bbb.py` | self-checks |
| `run_c0.py` to `run_c3.py`, `summarize.py` | the registered runs and the verdicts |

Results go to `artifacts/RING-IN-BALANCE-20261123-001C/RING-IN-BALANCE-20261123-001C-E001_no_round/`.

## Commands

From this directory, with the workspace's environment:

```bash
PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python
$PY -B selfcheck.py engine        # group rule vs naive, met sets, matcher vs networkx, sameness, part rounds vs complete rounds
$PY -B run_c0.py trace            # c0_trace.json (gate G(a), for comparison with ticket A)
$PY -B selfcheck.py bbb           # incremental parts vs full recomputation; d2_4_trace.txt
$PY -B selfcheck.py determinism   # reruns identical (also across processes with different string-hash seeds)
$PY -B run_c0.py gate             # c0_results.json: G(b), G(c)
$PY -B run_c1.py 8                # c1_results.json, c1_log.txt (726 runs, 8 processes)
$PY -B run_c2.py 8                # c2_runs.jsonl, c2_log.txt (4,800 runs, 8 processes)
$PY -B run_c3.py                  # c3_results.json
$PY -B summarize.py               # summary.txt, summary.json: verdict lines
```

Each worker process is capped at 4 GB of address space.
