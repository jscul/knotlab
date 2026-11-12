#!/usr/bin/env python3
"""Checks for ENDLESS-BLOCK-20261112-001A (research/ENDLESS-BLOCK-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part every|lagged|one|summary [--write]
every (E1): 45 harmonies (P <= 16) bound by their own knots in every order on one knot, a chain of 4 and a closed chain of 3: states
(capped) and ties of the root. lagged (E2): the closed chain of 3 with lag s on one cycle member, s = 0..P-1: lives, states against
Fix(S^g), g = gcd(P, s), and ties inside the root copy. one (O1): one order, on one knot, two knots sharing two, closed chains of 3, 4
and 6, the rings of 6 and 7, and open chains of 9, 12 and 18 knots (the closed chains unrolled three times): lives, states (capped),
the root's ties inside and outside its copy, and cycle-born ties (tied on the closed chain, untied on the unrolled chain for both lifts
of the partner). summary: the frozen items. Referee: the background referee thread (referee pending)."""
import hashlib
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("endless_lib.py", "check.py")] + \
       ["proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series/nest_lib.py",
        "research/ENDLESS-BLOCK-20261112-001/preregistration.md"]
CAP = 20000


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def ties_of(E, h, Ppat, mode, lags=None, roots=None):
    cl, nv, var = E.build(Ppat, h, mode, lags)
    P = h["P"]
    out = {}
    for i in (roots if roots is not None else range(P)):
        t = E.tie_set(cl, nv, var(0, i))
        if t is None:
            return None
        inside = sorted((v - 1) % P for v in t if (v - 1) // P == 0)
        outside = sorted(((v - 1) // P, (v - 1) % P, r) for v, r in t.items() if (v - 1) // P != 0)
        out[i] = {"inside": inside, "outside": outside}
    return out


def every_job(n):
    import endless_lib as E
    h = E.harmonies()[n]
    rows = []
    for name, Ppat in (("one knot", (3, [(0, 1, 2)])), ("chain of 4", E.open_chain(4)), ("closed chain of 3", E.closed_chain(3))):
        cl, nv, var = E.build(Ppat, h, "every order")
        c = E.count(cl, nv, CAP)
        t = ties_of(E, h, Ppat, "every order", roots=[0])
        all_equal = t is not None and all((v, 0, 0) in t[0]["outside"] for v in range(1, Ppat[0]))
        rows.append({"pattern": name, "states": c, "harmony states": len(E.N.states(h)), "every copy equal to the root at place 0": all_equal})
    return {"n": n, "orbits": h["orbits"], "P": h["P"], "rows": rows}


def lagged_job(n):
    import endless_lib as E
    h = E.harmonies()[n]
    P = h["P"]
    rows = []
    for s in range(P):
        Ppat = E.closed_chain(3)
        cl, nv, var = E.build(Ppat, h, "every order", {0: (s, 0, 0)})
        c = E.count(cl, nv, CAP)
        g = math.gcd(P, s)
        pred_lives = any(g % p == 0 for p in E.min_periods(h))
        t = ties_of(E, h, Ppat, "every order", {0: (s, 0, 0)}, roots=[0]) if c else None
        rows.append({"lag": s, "g": g, "lives": bool(c), "predicted lives": pred_lives, "states": c,
                     "predicted states (Fix of the shift by g)": E.fixed_count(h, g), "inside the root copy": t[0]["inside"] if t else None})
    return {"n": n, "orbits": h["orbits"], "P": P, "rows": rows}


def one_job(n):
    import endless_lib as E
    h = E.harmonies()[n]
    P = h["P"]
    rows = []
    pats = [("one knot", (3, [(0, 1, 2)])), ("two sharing two", E.two_sharing_two())] + \
           [("closed chain of %d" % k, E.closed_chain(k)) for k in (3, 4, 6)] + [("ring of %d" % r, E.ring(r)) for r in (6, 7)]
    own = ties_of(E, h, (1, []), "one order")
    for name, Ppat in pats:
        cl, nv, var = E.build(Ppat, h, "one order")
        c = E.count(cl, nv, CAP)
        t = ties_of(E, h, Ppat, "one order")
        row = {"pattern": name, "lives": t is not None, "states": c,
               "ties inside the root copy beyond the harmony's own": sorted({j for i in t for j in t[i]["inside"]} - {j for i in own for j in own[i]["inside"]}) if t else None,
               "root's ties outside its copy": sum(len(t[i]["outside"]) for i in t) if t else None}
        if name.startswith("closed chain"):
            k = int(name.split()[-1])
            U = E.open_chain(3 * k)
            tu = ties_of(E, h, U, "one order", roots=None)
            # the root (copy 0 of the closed chain) lifts to the middle copy 2k of the unrolled chain; copy v lifts to 2k + v and 2k + v - 2k
            born = []
            tc = ties_of(E, h, Ppat, "one order")
            if tc is not None and tu is not None:
                cl_u, nv_u, var_u = E.build(U, h, "one order")
                for i in range(P):
                    tt = E.tie_set(cl_u, nv_u, var_u(2 * k, i))
                    for (v, j, r) in tc[i]["outside"]:
                        lifts = [2 * k + v, 2 * k + v - 2 * k]
                        tied_somewhere = any(tt is not None and var_u(L, j) in tt for L in lifts)
                        if not tied_somewhere:
                            born.append([i, v, j, r])
            row["cycle-born ties (closed chain vs unrolled chain)"] = born
        rows.append(row)
    return {"n": n, "orbits": h["orbits"], "P": P, "rows": rows}


def run_part(part):
    import endless_lib as E
    n = len(E.harmonies())
    job = {"every": every_job, "lagged": lagged_job, "one": one_job}[part]
    with Pool(12) as pool:
        return {"rows": pool.map(job, range(n), chunksize=1)}


def summary():
    ev = json.loads((HERE / "result_every.json").read_text())["checks"]["result"]["rows"]
    lg = json.loads((HERE / "result_lagged.json").read_text())["checks"]["result"]["rows"]
    on = json.loads((HERE / "result_one.json").read_text())["checks"]["result"]["rows"]
    lag_cells = [r for h in lg for r in h["rows"]]
    one_cells = [(h["orbits"], r) for h in on for r in h["rows"]]
    born = [(o, r["pattern"], len(r["cycle-born ties (closed chain vs unrolled chain)"])) for o, r in one_cells if r.get("cycle-born ties (closed chain vs unrolled chain)")]
    return {
        "E1 every order: states equal the harmony's, every copy equal": all(r["states"] == r["harmony states"] and r["every copy equal to the root at place 0"] for h in ev for r in h["rows"]),
        "E2 lagged: lives as predicted": [sum(r["lives"] == r["predicted lives"] for r in lag_cells), len(lag_cells)],
        "E2 lagged: states equal Fix of the shift by g": [sum(1 for r in lag_cells if r["lives"] and r["states"] == r["predicted states (Fix of the shift by g)"]), sum(1 for r in lag_cells if r["lives"])],
        "O1 one order: lives on every pattern (the diagonal)": all(r["lives"] for o, r in one_cells),
        "O1 one order: no tie inside a copy beyond the harmony's own": all(not r["ties inside the root copy beyond the harmony's own"] for o, r in one_cells if r["lives"]),
        "O1 harmonies whose single knot already ties copies": sorted({"+".join(o) for o, r in one_cells if r["pattern"] == "one knot" and r["root's ties outside its copy"]}),
        "O1 cells with cycle-born ties (reach from a whole loop)": born,
        "O1 rings of 6 and 7 differ (states)": sorted({"+".join(h["orbits"]) for h in on if len({r["states"] for r in h["rows"] if r["pattern"].startswith("ring")}) > 1}),
    }


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if "--write" in sys.argv:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")


if __name__ == "__main__":
    main()
