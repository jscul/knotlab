"""Checks for REROUTE-20261109-001B: re-routing keeps persistence, lines read their distance plainly, and on the square contact graph
small rings are late. Networks are dart permutations (reroute_lib.py); persistence is read as in FLIP-RULE-20261109-001B-E001 (even return
counts to length E + 1, exact) and the plain first need by shortest routes (reroute_lib.late_pairs, cross-checked against
PLAIN-TIME-20261108-001A's plain_lib.verdicts on small tori).

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import collections
import hashlib
import importlib.util
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import reroute_lib as RR  # noqa: E402

P = RR.P
spec = importlib.util.spec_from_file_location("run", ROOT / "experiments/FLIP-RULE-20261109-001B/FLIP-RULE-20261109-001B-E001_small_maps/run.py")
R1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R1)
SQUARE = range(3, 33)
OTHERS = range(3, 21)
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def plain_late(sig):
    n, out = len(sig) // 2, [[sig[2 * c] >> 1, sig[2 * c + 1] >> 1] for c in range(len(sig) // 2)]
    rc = RR.rings(sig)
    return sum(P.verdicts(n, out, rc, t)["rings late"] + P.verdicts(n, out, rc, t)["rings never"] for t in range(n))


def chmutov(sig, S):
    """boundary components of the spanning ribbon subgraph on the contacts S (the vertices of Chmutov's partial dual)"""
    sub, isolated = {}, 0
    for r in RR.cycles(sig):
        ds = [d for d in r if d >> 1 in S]
        if not ds:
            isolated += 1
        for i, d in enumerate(ds):
            sub[d] = ds[(i + 1) % len(ds)]
    seen, comps = set(), 0
    for d in sub:
        if d not in seen:
            comps += 1
            x = d
            while x not in seen:
                seen.add(x)
                x = sub[x ^ 1]
    return comps + isolated


def lines_task(args):
    kind, n, cls = args
    sig, rot, edges, B = RR.lattice(kind, n)
    cl = RR.classes(kind, rot)
    s = RR.reroute(sig, set().union(*[cl[k] for k in cls]))
    if not RR.is_network(s):
        return args, None
    rs = RR.rings(s)
    balls = RR.ring_graph_balls(s, n - 1, roots=[0])[0]
    pers = R1.persistent(s) if len(s) // 2 <= 300 else None
    return args, {"rings": len(rs), "ring sizes": sorted(set(len(r) for r in rs)), "balls 2r + 1": balls == [min(2 * r + 1, len(rs)) for r in range(n)],
                  "persistent": None if pers is None else all(pers), "late": RR.late_pairs(s), "no single fastest way": RR.late_pairs(s, single=True)}


def base_point(edges, e):
    return edges[e][0]


def box_target(edges, cs, n, k):
    """for a ring whose contacts lie in a box of side 2^k - 2 (on the n x n torus), the target H(p) of Theorem 3, else None"""
    pts = [base_point(edges, e) for e in cs]
    x0, y0 = pts[0]
    xs = [((x - x0 + n // 2) % n) - n // 2 for x, y in pts]
    ys = [((y - y0 + n // 2) % n) - n // 2 for x, y in pts]
    if max(xs) - min(xs) > 2 ** k - 3 or max(ys) - min(ys) > 2 ** k - 3:
        return None
    return ((x0 + min(xs) - 2 ** k - 1) % n, (y0 + min(ys) - 2 ** k - 1) % n)


def theorem3_task(args):
    k, mode, seed = args
    n = 2 ** (k + 3)
    sig, rot, edges, B = RR.lattice("square", n)
    s = sig
    if mode == "rerouted":
        rng = random.Random(seed)
        F = RR.face_moves(sig)
        S = set()
        for _ in range(3 * n * n):
            T = S.symmetric_difference(rng.choice(F))
            if RR.is_network(RR.reroute(sig, T)):
                S = T
        s = RR.reroute(sig, S)
    H = {v: rot[v][0] for v in rot}
    rs = RR.rings(s)
    small = [(cs, box_target(edges, cs, n, k)) for cs in rs]
    small = [(cs, t) for cs, t in small if t is not None]
    rng = random.Random(seed + 1)
    sample = small if len(small) <= 120 else rng.sample(small, 120)
    late = 0
    for cs, t in sample:
        dist, par, low = RR.routes_to(s, H[t])
        m = min(dist[e] for e in cs)
        late += not any(par[e] for e in cs if dist[e] == m)
    return args, {"torus side": n, "rings": len(rs), "rings in a box of side 2^k - 2": len(small), "read": len(sample), "late at the predicted target": late}


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    # 1. Theorem 1 on random maps, and the maps sharing a contact graph are the re-routings (every map to three contacts)
    rng = random.Random(20261109)
    same, chm, tried = 0, 0, 0
    for _ in range(3000):
        E = rng.randint(2, 9)
        p = list(range(2 * E))
        rng.shuffle(p)
        sig = tuple(p)
        S = {c for c in range(E) if rng.random() < 0.5}
        s2 = RR.reroute(sig, S)
        tried += 1
        same += RR.arcs(s2) == RR.arcs(sig) and R1.persistent(s2) == R1.persistent(sig)
        chm += len(RR.cycles(s2)) == chmutov(sig, S)
    share = True
    for E in (1, 2, 3):
        by = collections.Counter(tuple(RR.arcs(p)) for p in itertools.permutations(range(2 * E)))
        share &= set(by.values()) == {2 ** E}
    check("1_rerouting_keeps_the_contact_graph_and_persistence", same == tried and chm == tried and share,
          {"random maps re-routed at random sets": tried, "contact graph and every persistence unchanged": same,
           "rings = boundary components of the ribbon subgraph on S (Chmutov's partial dual)": chm,
           "every map to three contacts shares its contact graph with exactly 2^E maps": share})

    # 2-3. lines read their distance plainly
    jobs = [("square", n, cls) for n in SQUARE for cls in ((0,), (1,))]
    jobs += [("triangular", n, (k,)) for n in OTHERS for k in range(3)] + [("honeycomb", n, cls) for n in OTHERS for cls in ((0, 1), (0, 2), (1, 2))]
    jobs += [(kind, n, ()) for kind in ("square", "triangular", "honeycomb") for n in (4, 5, 6)]
    with Pool(16) as pool:
        res = dict(pool.map(lines_task, sorted(jobs, key=lambda j: -j[1]), chunksize=1))
        t3 = dict(pool.map(theorem3_task, [(2, "lattice", 0), (2, "rerouted", 1), (2, "rerouted", 2), (3, "rerouted", 3)], chunksize=1))
    cross = all(RR.late_pairs(RR.lattice(kind, n)[0]) == plain_late(RR.lattice(kind, n)[0]) for kind in ("square", "triangular", "honeycomb") for n in (4, 5))
    sq = {"%s %d %s" % j: res[j] for j in jobs if j[0] == "square" and j[2]}
    ok2 = all(v is not None and v["rings"] == 2 * j[1] and v["ring sizes"] == [2 * j[1]] and v["balls 2r + 1"] and v["late"] == 0
              and v["no single fastest way"] == 0 and v["persistent"] in (True, None) for j, v in res.items() if j[0] == "square" and j[2])
    late_n = sorted({j[1] for j, v in res.items() if j[0] == "square" and j[2] and v and v["late"]})
    check("2_square_lines_read_their_distance_plainly", ok2 and cross,
          {"tori": "n x n, n = 3 to 32, re-routed at every horizontal or every vertical contact", "late sizes": late_n,
           "fast reading agrees with plain_lib.verdicts (n = 4, 5, three lattices)": cross,
           "n = 32": sq["square 32 (1,)"]})
    others = {j: v for j, v in res.items() if j[0] != "square" and j[2]}
    ok3 = all(v is not None and v["rings"] == 2 * j[1] and v["balls 2r + 1"] and v["late"] == 0 and v["no single fastest way"] == 0
              for j, v in others.items())
    check("3_triangular_and_honeycomb_lines_read_their_distance_plainly", ok3,
          {"tori": "n x n, n = 3 to 20: triangular re-routed at one direction class, honeycomb at two",
           "networks read": len(others), "late": sum(v["late"] for v in others.values() if v),
           "ring sizes": sorted({s for v in others.values() if v for s in v["ring sizes"]}),
           "base tori (not re-routed) late pairs, n = 4 to 6": {"%s %d" % (j[0], j[1]): res[j]["late"] for j in jobs if not j[2]}})

    # 4. Theorem 3: the even box, and small rings late at the predicted target
    lemma = {}
    for k in (2, 3):
        n = 2 ** (k + 3)
        sig, rot, edges, B = RR.lattice("square", n)
        dist, par, low = RR.routes_to(sig, rot[(0, 0)][0])
        box = [rot[(x, y)][t] for x in range(2 ** k + 1, 2 ** (k + 1) - 1) for y in range(2 ** k + 1, 2 ** (k + 1) - 1) for t in (0, 1)]
        lemma[k] = {"torus side": n, "contacts in the box": len(box), "with an odd count": sum(par[e] for e in box)}
    ok4 = all(v["with an odd count"] == 0 for v in lemma.values()) and all(v["late at the predicted target"] == v["read"] and v["read"] > 0
                                                                           for v in t3.values())
    check("4_small_rings_are_late_on_the_square_contact_graph", ok4,
          {"lemma: shortest-route counts to H(0, 0) in the box [2^k + 1, 2^(k+1) - 2]^2": lemma,
           "rings in a box of side 2^k - 2, read at the predicted target": {"k = %d, %s, seed %d" % a: v for a, v in t3.items()}})

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "REROUTE-20261109-001B", "checks": OUT, "status": "passed" if allok else "failed",
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
