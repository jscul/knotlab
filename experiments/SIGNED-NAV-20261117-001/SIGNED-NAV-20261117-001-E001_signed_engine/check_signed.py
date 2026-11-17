"""Gates of SIGNED-NAV-20261117-001: the navigating agent's engine on signed not-all-equal knots.

  G-id    on unsigned patterns this engine reproduces MEET-TRANSFER's run for run (8 rules and the D, Dr, Dn and L3sm
          policies, four families, 12 instances): flips and incidences equal;
  G-zero  all-zero signs with a given initial state run exactly as the unsigned path with that state;
  G-gauge re-signing a random set of distinctions in every knot and flipping their initial values gives the same run for
          every rule and policy (flips, incidences equal; final states differ exactly by the re-signed set);
  G-small on 300 small planted signed instances every reported state satisfies every signed knot (brute force confirms each
          instance allows a state), CaDiCaL's model on the signed CNF checks, and incremental counts match recomputation;
  G-Dr    Dr's and D's policies, unchanged, on the signed patterns the slow loop rebuilt (capture_rebuilt.py): every run
          solves, every state satisfies the signed pattern, and the median flips are reported against Novelty+ on the same
          patterns (sensible: at most 3 times the better Novelty+ setting's).
Exits non-zero on any failure. Writes gates.json beside the captured patterns.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import engine as E  # noqa: E402

OLD = ROOT / "experiments/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer"
POL = json.loads((ROOT / "artifacts/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/policies.json").read_text())
REBUILT = ROOT / "artifacts/SIGNED-NAV-20261117-001/SIGNED-NAV-20261117-001-E001_signed_engine/rebuilt"
RULES = [("rw", ()), ("walksat", (0.5,)), ("probsat_poly", (1.8, 1.0)), ("probsat_exp", (2.5,)),
         ("novelty_plus", (0.7, 0.01)), ("greedy_where", (1.8, 1.0, 0.6)), ("sticky", (1.8, 1.0, 0.6)), ("fms", (0.5,))]
ARMS = ["D_s0", "Dr_s0", "Dn_s0", "L3sm_s0"]


def theta(arm):
    return np.load(POL[arm]["theta"]), int(POL[arm]["flags"])


def runs_for(inst, x0=None, seeds=(1, 2)):
    out = []
    for s in seeds:
        for a, prm in RULES:
            r = E.run(inst, a, prm, seed=s, max_flips=10**6, want_state=True, x0=x0)
            out.append((a, s, r["flips"], r["work"], r["state"]))
        for arm in ARMS:
            th, fl = theta(arm)
            r = E.run(inst, "policy", (), theta=th, flags=fl, seed=s, max_flips=10**6, want_state=True, x0=x0)
            out.append((arm, s, r["flips"], r["work"], r["state"]))
    return out


def main():
    fails, report = [], {}
    # G-id
    code = ("import sys, json, numpy as np; sys.path.insert(0, sys.argv[1]); import engine as E\n"
            "pol = json.loads(open(sys.argv[2]).read()); out = []\n"
            "for i in range(12):\n"
            "    fam, alpha, w = [('rand', 2.1, 10), ('local', 4.0, 10), ('block', 2.5, 20), ('heavy', 3.0, 10)][i % 4]\n"
            "    inst = E.planted(fam, 300, alpha, 980_000 + i, w=w)\n"
            "    for a, prm in " + repr(RULES) + ":\n"
            "        r = E.run(inst, a, prm, seed=i, max_flips=10**6); out.append([a, r['flips'], r['work']])\n"
            "    for arm in " + repr(ARMS) + ":\n"
            "        r = E.run(inst, 'policy', theta=np.load(pol[arm]['theta']), flags=int(pol[arm]['flags']), seed=i, max_flips=10**6)\n"
            "        out.append([arm, r['flips'], r['work']])\n"
            "print(json.dumps(out))\n")
    pf = ROOT / "artifacts/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/policies.json"
    res = []
    for d in (OLD, HERE):
        r = subprocess.run([sys.executable, "-B", "-c", code, str(d), str(pf)], capture_output=True, text=True, env=os.environ.copy())
        res.append(json.loads(r.stdout) if r.returncode == 0 else None)
        if r.returncode:
            fails.append("G-id run failed: " + r.stderr[-300:])
    same = res[0] is not None and res[0] == res[1]
    report["G-id"] = {"runs": len(res[1] or []), "identical": same}
    if not same:
        fails.append("G-id engines differ")
    print("G-id", report["G-id"], flush=True)

    # G-zero and G-gauge
    nz = ng = 0
    rng = np.random.default_rng(11)
    for i in range(8):
        fam, alpha, w = [("rand", 2.1, 10), ("local", 4.0, 10), ("block", 2.5, 20), ("heavy", 3.0, 10)][i % 4]
        base = E.planted(fam, 300, alpha, 981_000 + i, w=w)
        x0 = rng.integers(0, 2, base.n).astype(np.uint8)
        a = runs_for(base, x0=x0)
        z = runs_for(E.Instance(base.n, base.knots, signs=np.zeros((base.m, 3), np.uint8)), x0=x0)
        for p, q in zip(a, z):
            nz += 1
            if p[:4] != q[:4] or not np.array_equal(p[4], q[4]):
                fails.append(f"G-zero differs {p[:2]}")
        g = rng.integers(0, 2, base.n).astype(np.uint8)
        signs0 = rng.integers(0, 2, (base.m, 3)).astype(np.uint8)
        si = E.Instance(base.n, base.knots, signs=signs0)
        sg = E.Instance(base.n, base.knots, signs=signs0 ^ g[base.knots])
        u = runs_for(si, x0=x0)
        v = runs_for(sg, x0=x0 ^ g)
        for p, q in zip(u, v):
            ng += 1
            if p[:4] != q[:4] or not np.array_equal(p[4], q[4] ^ g):
                fails.append(f"G-gauge differs {p[:2]} {p[2]} {q[2]}")
    report["G-zero"] = {"runs": nz}
    report["G-gauge"] = {"runs": ng}
    print("G-zero", nz, "G-gauge", ng, "failures so far", len(fails), flush=True)

    # G-small
    nsol = nrun = 0
    bad = 0
    for i in range(300):
        n = int(np.random.default_rng(i).integers(8, 15))
        inst = E.planted_signed(n, 3.0, 990_000 + i)
        xs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(np.uint8)
        lit = xs[:, inst.knots] ^ inst.signs
        cnt = int(np.all((lit.sum(axis=2) % 3) != 0, axis=1).sum())
        if cnt < 1 or not inst.satisfied(inst.hidden.astype(np.uint8)):
            fails.append(f"G-small instance {i} has no allowed state")
        for a, prm in RULES:
            r = E.run(inst, a, prm, seed=i, max_flips=10**6, want_state=True)
            nrun += 1
            if not r["solved"] or not inst.satisfied(r["state"]):
                fails.append(f"G-small {a} on {i}")
            else:
                nsol += 1
        for arm in ARMS:
            th, fl = theta(arm)
            r = E.run(inst, "policy", (), theta=th, flags=fl, seed=i, max_flips=10**6, want_state=True)
            nrun += 1
            if not r["solved"] or not inst.satisfied(r["state"]):
                fails.append(f"G-small {arm} on {i}")
            else:
                nsol += 1
        if i < 100:
            c = E.cadical(inst, 10)
            if c["result"] is not True or not c["model_ok"]:
                fails.append(f"G-small cadical on {i}")
    for i in range(6):
        bad += E.selftest(E.planted_signed(300, 3.0, 995_000 + i), i, 10_000)
    if bad:
        fails.append(f"G-small {bad} incremental mismatches")
    report["G-small"] = {"runs": nrun, "solved_and_checked": nsol, "incremental_mismatches": bad}
    print("G-small", report["G-small"], flush=True)

    # G-Dr
    rows = []
    cap = 10**7
    for f in sorted(REBUILT.glob("*.npz")):
        d = np.load(f)
        inst = E.Instance(int(d["n"]), d["kv"], signs=d["ks"])
        row = {"pattern": f.name, "n": inst.n, "m": inst.m, "signed_knots": int((inst.signs.sum(axis=1) > 0).sum())}
        for name, algo, prm in (("novelty(0.7,0.01)", "novelty_plus", (0.7, 0.01)), ("novelty(0.8,0.01)", "novelty_plus", (0.8, 0.01))):
            fl = [E.run(inst, algo, prm, seed=100 + r, max_flips=cap)["flips"] for r in range(5)]
            row[name] = float(np.median(fl))
        for arm in ("Dr_s0", "Dr_s1", "D_s0", "D_s1", "D_s2", "D_s3"):
            th, fl_ = theta(arm)
            fl, ok = [], True
            for r in range(5):
                res = E.run(inst, "policy", (), theta=th, flags=fl_, seed=100 + r, max_flips=cap, want_state=True)
                ok &= bool(res["solved"]) and inst.satisfied(res["state"])
                fl.append(res["flips"])
            row[arm] = float(np.median(fl))
            row[arm + "_ok"] = ok
            if not ok:
                fails.append(f"G-Dr {arm} on {f.name} unsolved or wrong")
        best = min(row["novelty(0.7,0.01)"], row["novelty(0.8,0.01)"])
        row["Dr_ratio"] = float(np.exp(np.mean(np.log([row["Dr_s0"], row["Dr_s1"]]))) / best)
        row["D_ratio"] = float(np.exp(np.mean(np.log([row[f"D_s{k}"] for k in range(4)]))) / best)
        rows.append(row)
        print(f.name, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items() if k in ("n", "m", "signed_knots", "Dr_ratio", "D_ratio")}, flush=True)
    med_dr = float(np.median([r["Dr_ratio"] for r in rows]))
    med_d = float(np.median([r["D_ratio"] for r in rows]))
    report["G-Dr"] = {"patterns": rows, "median_Dr_ratio": med_dr, "median_D_ratio": med_d}
    if med_dr > 3:
        fails.append(f"G-Dr median Dr ratio {med_dr:.2f} above 3")
    print("G-Dr median ratio to the better Novelty+: Dr", round(med_dr, 2), "D", round(med_d, 2), flush=True)
    report["fails"] = fails
    (REBUILT.parent / "gates.json").write_text(json.dumps(report, indent=1, default=float))
    print("GATE", "PASS" if not fails else "FAIL")
    for f in fails[:20]:
        print("  ", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
