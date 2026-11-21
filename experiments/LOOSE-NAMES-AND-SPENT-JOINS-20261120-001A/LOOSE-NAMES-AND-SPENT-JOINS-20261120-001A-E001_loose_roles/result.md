# Exact pair readings at 29 names

The two 406-entry named tables uniquely determine the twenty loose names, ten named two-parent births of fresh price three, and the whole physical presentation and its founder. This holds among all positive-age ordinary not-all-equal histories separately under uniform words and recursive extension division. The compact proof and independent exhaustion agree. Every known current ordinary knot can also be oriented at every arity under recursive division. Independent referee pending. [Scientific report](../../../research/LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A/results.md) · [Referee handoff](../../../research/LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A/referee_handoff.md) · [Frozen contract](contract.json)

From the repository root, reproduce the target, conditional inversions, exhaustive predecessor accounting, and independent archived finite checks in this order. The conditional inversions read only the 406 rational entries and their weighting. The final physical pass verifies existence against the reference afterwards.

```bash
scope=LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A
study="experiments/$scope/$scope-E001_loose_roles"
ulimit -v 6291456
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python -B "$study/select_target.py"
.venv/bin/python -B "$study/target_weights.py"
.venv/bin/python -B "$study/replay_roles.py" uniform
.venv/bin/python -B "$study/replay_roles.py" inherited
.venv/bin/python -B "$study/verify_completion.py"
.venv/bin/python -B "$study/role_proof.py"
.venv/bin/python -B "$study/twin_checks.py"
```

A separate binary-factor implementation reproduced all 812 target rates. Its two 32-draw panels per law yielded 247 funded observations, all read under both weightings. The stronger local test assessed after the proof is recorded as a deductive replay of the same draws. [Sample weights, denominators and replay commands](../../../research/LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A/controls.md)
