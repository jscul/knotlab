"""NATIVE-TARGET-20261110-001 stress test, one size past ticket A's run (thin tori to 40 points): torus(N, 1, 1) for N = 42, 44, 46,
50 SAT-found least states each with a random split (seed 1111), rules R0, R3, R4, R5 and R7 of ticket A's run.py with their budgets.
Pass when R4 and R5 resolve every run and beat R0's mean steps on each. Writes stress_test.json beside this file."""
import importlib.util
import json
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "experiments/NATIVE-TARGET-20261110-001A/NATIVE-TARGET-20261110-001A-E001_native_signals_that_steer_learning/run.py"

if os.environ.get("PYTHONHASHSEED") != "0":
    os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
spec = importlib.util.spec_from_file_location("native_run", RUN)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
H = R.H
rng = random.Random(1111)
rows = []
for N in (42, 44, 46):
    T = H.Torus(N, 1, 1)
    cnt = R.Counter_N(T)
    s0 = T.classes[T.forced[0]]
    xs = T.least_states_sat(s0, rng, 50)
    row = {"torus": T.name, "points": T.n, "starts": len(xs)}
    for rule, budget in (("R0", 50 * T.V * T.V), ("R3", 50 * T.V * T.V), ("R4", 20 * T.V), ("R5", 20 * T.V), ("R7", 50 * T.V * T.V)):
        ok_n, steps, bad = 0, [], 0
        for x in xs:
            s2, f, deg, l0, w0 = T.split(s0, x, rng.randrange(3))
            if rule == "R7":
                ok, st, mv = T.run_rule(f, deg, w0, "no_reversal", rng, budget)
            else:
                ok, st, mv = R.run(T, cnt, R.Conf(f, deg, s2), rule, rng, budget)
            if ok:
                ok_n += 1
                steps.append(st)
                bad += not R.replay_ok(T, s2, x, mv, s0)
        row[rule] = {"resolved": ok_n, "mean steps": round(sum(steps) / len(steps), 2) if steps else None, "replay failures": bad}
    rows.append(row)
    print(row, flush=True)
ok = all(r[k]["resolved"] == r["starts"] and r[k]["mean steps"] < r["R0"]["mean steps"] and r[k]["replay failures"] == 0
         for r in rows for k in ("R4", "R5"))
(HERE / "stress_test.json").write_text(json.dumps({"rows": rows, "pass": ok}, indent=1) + "\n")
print("pass", ok)
