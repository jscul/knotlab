"""Checks for PC-COUNT-20261110-001A: the functional pigeonhole principle on a bipartite graph G reduces to LeftPigeon, and through
COUNT-SYSTEMS-20261110-001A's chain to the sphere's count, by decision trees reading a pointer in at most max(3, hole degree) queries.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run

FPHP_G: pigeons 0 .. N, holes 1 .. N, a variable x_ph for each edge of G; clauses: every pigeon in a hole of its own, no pigeon in two holes,
no two pigeons in one hole. The reduction: f(p) is p's first hole with x_ph = 1 (hole 1 when none), g(h) the first pigeon with x_ph = 1
(pigeon 0 when none). A LeftPigeon answer x (g(f(x)) != x) is decoded by reading x's edges and then f(x)'s edges."""
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
CS = ROOT / "proofs/COUNT-SYSTEMS-20261110-001A/COUNT-SYSTEMS-20261110-001A-P001_bounded_depth_frege"
spec = importlib.util.spec_from_file_location("count_systems_check", CS / "check.py")
C = importlib.util.module_from_spec(spec)
sys.modules["count_systems_check"] = C
spec.loader.exec_module(C)
T = C.T
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def graphs(N, rng=None, sample=None, maxdeg=3):
    """bipartite graphs: each pigeon 0 .. N picks a nonempty set of at most maxdeg holes among 1 .. N"""
    choices = [c for r in range(1, min(maxdeg, N) + 1) for c in itertools.combinations(range(1, N + 1), r)]
    if sample is None:
        yield from itertools.product(choices, repeat=N + 1)
    else:
        for _ in range(sample):
            yield tuple(rng.choice(choices) for _ in range(N + 1))


def reduce_to_left_pigeon(N, G, x):
    """f and g from an assignment x {(p, h): 0/1} of G's edges, each value read with the queries it costs"""
    holes_of = {h: [p for p in range(N + 1) if h in G[p]] for h in range(1, N + 1)}
    f = [next((h for h in G[p] if x[(p, h)]), 1) for p in range(N + 1)]
    g = (None,) + tuple(next((p for p in holes_of[h] if x[(p, h)]), 0) for h in range(1, N + 1))
    return f, g, holes_of


def decode(N, G, holes_of, x, p):
    """a falsified clause of FPHP_G from a LeftPigeon answer p, and the variables read"""
    read = [(p, h) for h in G[p]]
    on = [h for h in G[p] if x[(p, h)]]
    if not on:
        return ("pigeon", p), read
    if len(on) > 1:
        return ("two holes", p, on[0], on[1]), read
    h = on[0]
    read += [(q, h) for q in holes_of[h] if q != p]
    other = [q for q in holes_of[h] if q != p and x[(q, h)]]
    return (("collision", h, p, other[0]) if other else None), read


def falsified(N, G, x, c):
    if c is None:
        return False
    if c[0] == "pigeon":
        return all(not x[(c[1], h)] for h in G[c[1]])
    if c[0] == "two holes":
        return x[(c[1], c[2])] and x[(c[1], c[3])]
    return x[(c[2], c[1])] and x[(c[3], c[1])]


def instances(N, G):
    edges = [(p, h) for p in range(N + 1) for h in G[p]]
    for bits in itertools.product((0, 1), repeat=len(edges)):
        yield dict(zip(edges, bits))


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    # 1. FPHP_G -> LeftPigeon: every answer decodes, within 3 + hole-degree reads, to a falsified clause of FPHP_G
    rng = random.Random(20261110)
    ok, n_g, n_x, n_ans, worst = True, 0, 0, 0, 0
    for N, sample in ((1, None), (2, None), (3, 300)):
        for G in graphs(N, rng, sample):
            n_g += 1
            for x in instances(N, G):
                f, g, holes_of = reduce_to_left_pigeon(N, G, x)
                ans = [p for p in range(N + 1) if C.left_pigeon_violation(f, g, p)]
                n_x += 1
                ok &= bool(ans)
                delta = max([3] + [len(v) for v in holes_of.values()])
                for p in ans:
                    c, read = decode(N, G, holes_of, x, p)
                    n_ans += 1
                    worst = max(worst, len(read) - delta)
                    ok &= falsified(N, G, x, c) and len(read) <= 3 + delta
    check("1_fphp_reduces_to_left_pigeon", ok, {"graphs (N = 1, 2 all; N = 3: 300 random)": n_g, "assignments": n_x,
                                                 "answers decoded": n_ans, "most reads beyond the hole degree": worst})

    # 2. composed with COUNT-SYSTEMS-20261110-001A's chain: every counterclockwise full triangle decodes to a falsified clause
    ok2, n2, tri = True, 0, 0
    L = T.layout(3)
    for G in graphs(2, rng, 12):
        xs = list(instances(2, G))
        for x in rng.sample(xs, min(6, len(xs))):
            f, g, holes_of = reduce_to_left_pigeon(2, G, x)
            succ, pred = C.to_sink(2, f, g)
            col, route, clash, cr = T.colouring(L, succ, pred)
            full = [t for t, o in T.full_triangles(col, L["m"]) if o == 1]
            n2 += 1
            tri += len(full)
            ok2 &= not clash and bool(full)
            for t in full:
                v = T.back_map(succ, pred, T.triangle_node(L, t))
                c, read = decode(2, G, holes_of, x, v)
                ok2 &= T.is_sink_solution(succ, pred, v) and C.left_pigeon_violation(f, g, v) and falsified(2, G, x, c)
    check("2_composed_with_the_chain_to_the_sphere", ok2, {"FPHP_G instances with N = 2": n2, "counterclockwise full triangles decoded": tri})

    # 3. the sizes of the chain: grid side m for SINK on N + 1 nodes, sphere K_k with k = 2m + 4, n = 4k^2 points
    rows = []
    for N in (2, 3, 4, 5, 6):
        m = T.layout(N + 1)["m"]
        k = 2 * m + 4
        rows.append({"N": N, "grid side": m, "k": k, "n": 4 * k * k, "N / n^(1/4)": round(N / (4 * k * k) ** 0.25, 3)})
    ratios = [r["N / n^(1/4)"] for r in rows]
    check("3_sizes_n_is_order_N_to_the_fourth", min(ratios) > 0.05 and ratios[-1] >= ratios[0] * 0.5, rows)

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "PC-COUNT-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
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
