#!/usr/bin/env python3
"""Checks for LOOP-LOCK-20261112-001A (research/LOOP-LOCK-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part rule|overlap|summary [--write]
rule: for the 45 harmonies (P <= 16), the step relation T and its loopless girth; the closed chain of k knots, k = 2 to 12, locked
(every shared copy equal to the first, place by place, in every state) against "k < girth"; the open chain of k knots, k = 2 to 12,
free (some shared copy differs from the first in some state) against "T has a step other than staying put". overlap: the harmonies
whose closed chain of 3 locks or whose girth is finite and at most 6: figure eights (two loops through one copy), thetas (two loops
sharing a knot), the one-shift rings of 4 to 12, and the drawn three-copy nestings of levels 1 to 3: which loops' copies lock and the
copies tied to the root. summary: the frozen items. Referee: the background referee thread (referee pending)."""
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("loop_lib.py", "check.py")] + \
       ["proofs/ENDLESS-BLOCK-20261112-001A/ENDLESS-BLOCK-20261112-001A-P001_endless_blocks/endless_lib.py",
        "research/LOOP-LOCK-20261112-001/preregistration.md"]
KS = range(2, 13)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def rule_job(n):
    import loop_lib as L
    h = L.E.harmonies()[n]
    W, R, T = L.relation(h)
    g = L.loopless_girth(T, len(W))
    nonloop = any(u != w for (u, w) in T)
    rows = []
    for k in KS:
        C = L.E.closed_chain(k)
        shared = [2 * j for j in range(k)]
        lc = L.locked(C, h, [shared])
        O = L.E.open_chain(k)
        oshared = [2 * j for j in range(k + 1)]
        lo = L.locked(O, h, [oshared])
        rows.append({"k": k, "closed locked": lc[0], "predicted closed locked": g is None or k < g,
                     "open free": not lo[0], "predicted open free": nonloop})
    return {"n": n, "orbits": h["orbits"], "P": h["P"], "states": len(W), "R": len(R), "T": len(T), "loopless girth": g,
            "a step other than staying": nonloop, "rows": rows}


def overlap_job(n):
    import loop_lib as L
    h = L.E.harmonies()[n]
    W, R, T = L.relation(h)
    g = L.loopless_girth(T, len(W))
    out = {"n": n, "orbits": h["orbits"], "P": h["P"], "loopless girth": g, "rows": []}
    for k1, k2 in ((3, 3), (3, 4), (3, 6), (4, 6), (6, 6)):
        P, A, B = L.figure_eight(k1, k2)
        la, lb = L.locked(P, h, [A, B])
        out["rows"].append({"pattern": "figure eight %d+%d" % (k1, k2), "loop A locked": la, "loop B locked": lb,
                            "predicted A": g is None or k1 < g, "predicted B": g is None or k2 < g})
    for k, m in ((3, 3), (3, 4), (4, 4), (4, 6), (6, 6)):
        P, A, B = L.theta(k, m)
        la, lb, lab = L.locked(P, h, [A, B, sorted(set(A) | set(B))])
        out["rows"].append({"pattern": "theta %d+%d" % (k, m), "loop A locked": la, "loop B locked": lb, "both locked together": lab,
                            "A alone locks": g is None or k < g, "B alone locks": g is None or m < g})
    P, X, Y = L.crossed()
    lx, ly, lxy = L.locked(P, h, [X, Y, sorted(set(X) | set(Y))])
    alone1 = L.locked((P[0], P[1][:4]), h, [X])[0]
    alone2 = L.locked((P[0], P[1][4:]), h, [Y])[0]
    out["rows"].append({"pattern": "crossed loops 4+4", "loop 1 alone locks": alone1, "loop 2 alone locks": alone2, "union locked": lxy})
    for nn in (5, 7, 9):
        P, sh, A, B = L.circulant(nn)
        uA = L.locked((P[0], A), h, [sh])[0]
        uB = L.locked((P[0], B), h, [sh])[0]
        cls = L.tie_classes(P, h, sh)
        out["rows"].append({"pattern": "circulant %d" % nn, "loop A alone locks": uA, "loop B alone locks": uB,
                            "classes in the union": None if cls is None else len(cls), "shared copies": nn})
    O = L.E.open_chain(8)
    cls = L.tie_classes(O, h, [2 * j for j in range(9)])
    out["rows"].append({"pattern": "control: open chain of 8", "classes": None if cls is None else len(cls), "shared copies": 9})
    for r in range(4, 13):
        P = L.E.ring(r)
        tied = L.tied_to_root(P, h)
        out["rows"].append({"pattern": "ring of %d" % r, "lives": tied is not None, "copies tied to the root": None if tied is None else len(tied), "copies": r - 1})
    for lev in (1, 2, 3):
        import importlib.util
        spec = importlib.util.spec_from_file_location("subst_lib_g", ROOT / "proofs/SUBST-NEST-20261112-001A/SUBST-NEST-20261112-001A-P001_block_substitution/subst_lib.py")
        S = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(S)
        P = S.gasket(lev)
        tied = L.tied_to_root(P, h)
        out["rows"].append({"pattern": "three-copy nesting level %d" % lev, "lives": tied is not None, "copies tied to the root": None if tied is None else len(tied), "copies": P[0] - 1})
    return out


def run_part(part):
    import loop_lib as L
    n = len(L.E.harmonies())
    if part == "rule":
        with Pool(12) as pool:
            return {"rows": pool.map(rule_job, range(n), chunksize=1)}
    if part == "overlap":
        rule = json.loads((HERE / "result_rule.json").read_text())["checks"]["result"]["rows"]
        locking = [r["n"] for r in rule if any(x["closed locked"] for x in r["rows"])]
        others = [r["n"] for r in rule if r["n"] not in locking and r["loopless girth"] is not None and r["a step other than staying"]][:8]
        pick = locking + others
        with Pool(12) as pool:
            return {"harmonies": pick, "rows": pool.map(overlap_job, pick, chunksize=1)}


def summary():
    rule = json.loads((HERE / "result_rule.json").read_text())["checks"]["result"]["rows"]
    ov = json.loads((HERE / "result_overlap.json").read_text())["checks"]["result"]["rows"]
    cells = [x for r in rule for x in r["rows"]]
    rows8 = [x for h in ov for x in h["rows"] if x["pattern"].startswith("figure")]
    thetas = [(h["orbits"], x) for h in ov for x in h["rows"] if x["pattern"].startswith("theta")]
    return {
        "L1 closed chains: locked exactly when k < girth": [sum(x["closed locked"] == x["predicted closed locked"] for x in cells), len(cells)],
        "L2 open chains: free exactly when T has a step other than staying": [sum(x["open free"] == x["predicted open free"] for x in cells), len(cells)],
        "harmonies whose loops lock at some k in 2..12": [["+".join(r["orbits"]), r["loopless girth"]] for r in rule if any(x["closed locked"] for x in r["rows"])],
        "girths": sorted({r["loopless girth"] for r in rule if r["loopless girth"] is not None}),
        "O1 figure eights: each loop as it would alone (no spread through one copy)": [sum(x["loop A locked"] == x["predicted A"] and x["loop B locked"] == x["predicted B"] for x in rows8), len(rows8)],
        "O2 thetas: the advisor's rule (locks iff g > max(1 + shorter return, longer return))": [sum(1 for h in ov for x in h["rows"] if x["pattern"].startswith("theta") and x["both locked together"] == ((h["loopless girth"] is None) or h["loopless girth"] > max(1 + min(int(x["pattern"].split()[1].split("+")[0]) - 1, int(x["pattern"].split()[1].split("+")[1]) - 1), max(int(x["pattern"].split()[1].split("+")[0]) - 1, int(x["pattern"].split()[1].split("+")[1]) - 1)))), sum(1 for h in ov for x in h["rows"] if x["pattern"].startswith("theta"))],
        "O2 thetas: loops that do not lock alone but lock together": [["+".join(o), x["pattern"]] for o, x in thetas if x["both locked together"] and not (x["A alone locks"] and x["B alone locks"])],
        "O2 thetas: a locked loop locking the other": [["+".join(o), x["pattern"]] for o, x in thetas if (x["loop A locked"] and x["loop B locked"]) and (x["A alone locks"] != x["B alone locks"])],
        "O4 crossed loops: each fails alone, the union locks": [["+".join(h["orbits"]), h["loopless girth"]] for h in ov for x in h["rows"] if x["pattern"].startswith("crossed") and x["union locked"] and not x["loop 1 alone locks"] and not x["loop 2 alone locks"]],
        "O5 circulants: each loop fails alone, the union is one class (collective lock)": [["+".join(h["orbits"]), h["loopless girth"], x["pattern"]] for h in ov for x in h["rows"] if x["pattern"].startswith("circulant") and x["classes in the union"] == 1 and not x["loop A alone locks"] and not x["loop B alone locks"]],
        "control: open chains of 8 have every shared copy in its own class": all(x["classes"] == x["shared copies"] for h in ov for x in h["rows"] if x["pattern"].startswith("control") and x["classes"] is not None),
        "O3 rings and nestings: copies tied to the root": [["+".join(h["orbits"]), x["pattern"], x.get("copies tied to the root"), x.get("copies")] for h in ov for x in h["rows"] if x["pattern"].startswith(("ring", "three"))],
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
