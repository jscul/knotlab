"""GROW-STUCK-20261110-001 stress test, one size past ticket A (K_2 to K_5): GROW-r on K_6 at one line of each line orbit, r = 2 and 3.
Pass when r = 3 grows once at the dissonance and resolves in 3 sign changes, r = 2 never resolves, and W >= |chi|/2 throughout.
Writes stress_test.json beside this file."""
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if os.environ.get("PYTHONHASHSEED") != "0":
    os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
sys.path.insert(0, str(ROOT / "proofs/GROW-STUCK-20261110-001A/GROW-STUCK-20261110-001A-P001_a_learner_that_grows_only_when_stuck"))
import stuck_lib as S_  # noqa: E402
spec = importlib.util.spec_from_file_location("steer_lib", ROOT / "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
S = S_.SL.octahedral_sphere(6)
sph = L.Sphere(S, "K_6")
reps, _ = S_.G.line_orbits(S)
rows, ok = [], True
for l0 in reps:
    x = sph.flat_state(sph.K.lines.index(l0))
    for r in (2, 3):
        rec = S_.grow_r(S, sph.s0, x, r, cap_growths=2)
        row = {"l0": l0, "r": r, "growths": len(rec["growths"]), "first growth at l0": rec["growths"][0]["line"] == l0,
               "resolved": rec["resolved"], "sign changes": rec["sign changes"], "floor": rec["floor respected"], "W": rec["W"], "chi": rec["chi"]}
        ok &= row["floor"] and row["first growth at l0"] and (
            (r == 3 and row["growths"] == 1 and row["resolved"] and row["sign changes"] == 3) or (r == 2 and not row["resolved"]))
        rows.append(row)
        print(row, flush=True)
(HERE / "stress_test.json").write_text(json.dumps({"sphere": "K_6", "orbits": len(reps), "pass": bool(ok), "rows": rows}, indent=1) + "\n")
print("pass", ok)
