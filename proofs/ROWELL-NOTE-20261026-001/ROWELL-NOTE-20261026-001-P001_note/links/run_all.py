"""Run the link checks of the note (Section 'Links': S3 and odd dihedral groups are #P-hard on links).

Each script prints its checks and fails with an assertion on any mismatch. This driver runs them from this directory with
the workspace interpreter (numpy is needed), saves each output under logs/, and with --write records exit codes and the last
lines in links_result.json.

    python3 -B run_all.py [--write]        (about 5-10 minutes; the scripts use a process pool)
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VENV = ROOT / ".venv" / "bin" / "python"
PY = str(VENV) if VENV.exists() else sys.executable

RUNS = [
    ("test_fact2", [], "sector method against brute force; the sector formula 3^(1+d+e-r)"),
    ("test_fact2_stats", [], "how often d, e and r are nonzero in the sector formula"),
    ("test_cable", [], "Lemma A: parallel cables"),
    ("test_surgery", [], "Lemmas B and C: local knots; closed counts from cable counts"),
    ("potts_reduction", [], "Theorem: Potts(3, y = 2) from H_L(S3), five graphs end to end"),
    ("colouring_reduction", ["P3 (path)", "K3 (triangle)"], "proper 3-colourings from H_L(S3)"),
    ("dihedral_check", ["5"], "the same reduction for D_5"),
    ("dihedral_check", ["7"], "the same reduction for D_7"),
    ("nilpotent_aside", [], "aside: D4 and Q8 link counts depend only on linking numbers"),
    ("independent_spot_check", [], "separate brute force of L(0), L(1) for K2 and the linking matrix of L_Gamma"),
]


def main():
    t0 = time.time()
    rows = []
    (HERE / "logs").mkdir(exist_ok=True)
    for name, args, what in RUNS:
        t1 = time.time()
        run = subprocess.run([PY, "-B", f"{name}.py", *args], cwd=HERE, capture_output=True, text=True, timeout=7200)
        tag = name + ("_" + "_".join(a.split()[0] for a in args) if args else "")
        (HERE / "logs" / f"{tag}.log").write_text(run.stdout + ("\n--- stderr ---\n" + run.stderr if run.stderr else ""))
        lines = [l for l in run.stdout.strip().splitlines() if l.strip()]
        rows.append({"script": name, "args": args, "checks": what, "exit_code": run.returncode,
                     "last_lines": lines[-6:], "seconds": round(time.time() - t1, 1)})
        print(f"{'ok ' if run.returncode == 0 else 'BAD'} {tag:28s} {rows[-1]['seconds']:7.1f} s  {lines[-1] if lines else ''}")
    ok = all(r["exit_code"] == 0 for r in rows)
    out = {"schema_version": 1, "ok": ok, "interpreter": "workspace .venv" if PY == str(VENV) else "python3",
           "seconds": round(time.time() - t0, 1), "rows": rows}
    if "--write" in sys.argv:
        (HERE / "links_result.json").write_text(json.dumps(out, indent=2) + "\n")
    print("ALL OK" if ok else "FAILURES", out["seconds"], "s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
