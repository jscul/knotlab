"""Checks for COUNT-SYSTEMS-20261110-001A: the reduction chain behind the bounded-depth Frege lower bound for the sphere's count.
LeftPigeon (pigeons 0 .. N, holes 1 .. N, maps f and g) reduces to SINK by succ = f, pred = g; COUNT-TFNP-20261107-001A's construction
reduces SINK to one-sided grid Sperner; FLAT-STATES-20261107-001B reduces that to the octahedral knot sphere (its own checks, m = 3 to 6).

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import hashlib
import importlib.util
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TUBE = ROOT / "proofs/COUNT-TFNP-20261107-001A/COUNT-TFNP-20261107-001A-P001_one_sided_grid_sperner_is_ppads_hard"
sys.path.insert(0, str(TUBE))
spec = importlib.util.spec_from_file_location("tube_lib", TUBE / "tube_lib.py")
T = importlib.util.module_from_spec(spec)
sys.modules["tube_lib"] = T
spec.loader.exec_module(T)
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def to_sink(N, f, g):
    """SINK on nodes 0 .. N: succ(u) = f(u) for every pigeon u, pred(v) = g(v) for every hole v, and node 0 (pigeon 0, no hole) has no
    predecessor"""
    succ = [f[u] for u in range(N + 1)]
    pred = [None] + [g[v] for v in range(1, N + 1)]
    for u in range(1, N + 1):
        if succ[u] == u and pred[u] == u:     # a self-loop is neither a sink nor a source: drop it, as the drawing has no loops
            succ[u] = pred[u] = None
    return succ, pred


def left_pigeon_violation(f, g, x):
    return g[f[x]] != x


def instances(N):
    for f in itertools.product(range(1, N + 1), repeat=N + 1):
        for gv in itertools.product(range(N + 1), repeat=N):
            yield f, (None,) + gv


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    # 1. LeftPigeon -> SINK: every SINK answer is a pigeon x with g(f(x)) != x
    ok, n_inst, n_sol = True, 0, 0
    for N in (1, 2, 3):
        for f, g in instances(N):
            succ, pred = to_sink(N, f, g)
            sols = [v for v in range(N + 1) if T.is_sink_solution(succ, pred, v)]
            n_inst += 1
            n_sol += len(sols)
            ok &= bool(sols) and all(left_pigeon_violation(f, g, v) for v in sols)
    check("1_left_pigeon_reduces_to_sink", ok, {"instances (N = 1, 2, 3, every f and g)": n_inst, "SINK answers checked": n_sol})

    # 2. composed with COUNT-TFNP-20261107-001A: every counterclockwise full triangle of the grid decodes to a left-pigeon violation
    rng = random.Random(20261110)
    ok2, n2, tri = True, 0, 0
    for N, sample in ((2, None), (3, 40)):
        L = T.layout(N + 1)
        insts = list(instances(N))
        if sample:
            insts = rng.sample(insts, sample)
        for f, g in insts:
            succ, pred = to_sink(N, f, g)
            col, route, clash, cr = T.colouring(L, succ, pred)
            full = [t for t, o in T.full_triangles(col, L["m"]) if o == 1]
            n2 += 1
            tri += len(full)
            ok2 &= not clash and bool(full)
            for t in full:
                j = T.triangle_node(L, t)
                v = T.back_map(succ, pred, j)
                ok2 &= T.is_sink_solution(succ, pred, v) and left_pigeon_violation(f, g, v)
    check("2_composed_with_the_grid_sperner_reduction", ok2,
          {"instances (N = 2: all 72; N = 3: 40 random)": n2, "counterclockwise full triangles decoded": tri,
           "grid side for N = 2 and 3": [T.layout(3)["m"], T.layout(4)["m"]]})

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "COUNT-SYSTEMS-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
