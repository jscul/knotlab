"""Gates for WEAVE-HEIGHTS-20261118-001B-E001.   .venv/bin/python -B checks.py   (writes checks_output.json)"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402

W = job.W
out = {}


def gate(name, ok, detail=""):
    out[name] = {"pass": bool(ok), "detail": detail}
    print("PASS" if ok else "FAIL", name, detail)


gate("forward", job.forward((0, 0), (1, 0)) and job.forward((1, 0), (0, 1)) and job.forward((0, 1), (0, 0)) and not job.forward((1, 0), (0, 0)),
     "the knot u(0, 0) is a forward 3-cycle")
r = job.check(frozenset({("u", 0, 0), ("d", 0, 0)}), 2)
gate("two-knot", r["states_vs_omega_fail"] == 0 and r["omega_checked"] == 1 and r["level_knots"] == 0 and r["dd_fail"] == 0 and r["lone_fail"] == 0
     and r["criterion_fail"] == 0 and r["flag_fail"] == 0 and r["convex_fail"] == 0 and r["triangle_fail"] == 0,
     "10 states = 2 x 5 choices; every check clean on the lone double meeting")
r = job.check(W.parallelogram(3, 3), 8)
gate("parallelogram", r["lone_fail"] == 0 and r["level_knots"] == 0 and r["criterion_fail"] == 0 and r["states_vs_omega_fail"] == 0,
     "3 x 3 parallelogram: lone-distinction lemma, no level knot, the criterion set by set, the state count")
gate("disc-test", W.is_disc({("u", 0, 0), ("d", 0, 0)}) and not W.is_disc({("u", 0, 0), ("u", 1, 1)}), "two knots meeting twice is a disc; two meeting once only is not")
json.dump(out, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in out.values()) else "SOME FAIL")
