"""Checks for GROW-PLAIN-20261109-001B. Networks are built in tube coordinates and read through loopnet_lib (the plain first need by
PLAIN-TIME-20261108-001A's plain_lib.verdicts: exact). Persistence is read through the half-turn about each contact.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import collections
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAIN = ROOT / "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census"
sys.path.insert(0, str(PLAIN))
import plain_lib as P  # noqa: E402

LN = P.LN
OUT = {}
T0 = time.time()
NMAX = 60

# ring a of a tube lists its contacts counterclockwise as (type, position); the contact (t, a) joins the rings in JOIN[t] offsets
TUBES = {
    # the twist tube of (2, 1): position a = x - 2y; E = h(a) to a + 1, N = v(a) to a - 2, W = h(a - 1), S = v(a + 2)
    "square twist (2, 1)": {"slots": lambda a: [(0, a), (1, a), (0, a - 1), (1, a + 2)], "join": {0: 1, 1: -2}, "first": 4},
    # the triangular tube of (1, -1): position a = x + y; directions (1,0), (1,1), (0,1) step +1, +2, +1
    "triangular sqrt 3 (1, -1)": {"slots": lambda a: [(0, a), (1, a), (2, a), (0, a - 1), (1, a - 2), (2, a - 1)],
                                  "join": {0: 1, 1: 2, 2: 1}, "first": 3},
}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tube_torus(name, N):
    """rot, edges of the tube's torus of N rings (rings 0..N-1), and the contact keys (type, position mod N)"""
    tb = TUBES[name]
    keys = sorted({(t, a % N) for a in range(N) for t, _ in [(s[0], 0) for s in tb["slots"](a)]})
    eid = {k: i for i, k in enumerate(keys)}
    edges = [(a, (a + tb["join"][t]) % N) for (t, a) in keys]
    rot = {a: [eid[(t, p % N)] for t, p in tb["slots"](a)] for a in range(N)}
    return rot, edges, keys


def ladder_torus(n, t=0):
    """the ladder <(0, 2), (n, t)>: rings (i, s), s in Z_2, i in Z_n with (n, s) identified with (0, s + t)"""
    def ring(i, s):
        k, i = divmod(i, n)
        return (i, (s + k * t) % 2)
    verts = [(i, s) for i in range(n) for s in (0, 1)]
    edges, eid = [], {}
    for (i, s) in verts:
        for d in ((1, 0), (0, 1)):
            w = ring(i + d[0], s + d[1])
            eid[((i, s), d)] = len(edges)
            edges.append(((i, s), w))
    rot = {}
    for (i, s) in verts:
        E = eid[((i, s), (1, 0))]
        Nn = eid[((i, s), (0, 1))]
        W = eid[(ring(i - 1, s), (1, 0))]
        S = eid[(ring(i, s - 1), (0, 1))]
        rot[(i, s)] = [E, Nn, W, S]
    return rot, edges


def on_time(rot, edges):
    sizes, contacts = LN.network(rot, edges, 2)
    n, out, rc = P.network_map(sizes, contacts)
    for tgt in range(n):
        v = P.verdicts(n, out, rc, tgt)
        if v["rings late"] or v["rings never"]:
            return False
    return True


def half_turns(name, N):
    """for every contact (t, a) of the tube's torus: the half-turn about it, ring p -> s - p (s the sum of its rings' positions) with
    slot i -> slot i + m/2, is a well-defined bijection of contacts that fixes it and exchanges its two rings"""
    tb = TUBES[name]
    m = len(tb["slots"](0))
    key = lambda c: (c[0], c[1] % N)
    for t in tb["join"]:
        a = 0
        s_ = (2 * a + tb["join"][t]) % N
        img = {}
        for p in range(N):
            sl, sl2 = tb["slots"](p), tb["slots"]((s_ - p) % N)
            for i in range(m):
                c, d = key(sl[i]), key(sl2[(i + m // 2) % m])
                if img.setdefault(c, d) != d:
                    return False
        if len(set(img.values())) != len(img) or img.get((t, 0)) != (t, 0):
            return False
    return True


def insertion_diff(name, N, j):
    """contacts (as ring pairs with their slots) of the torus of N rings, mapped into the torus of N + 1 by inserting a ring after j:
    which survive, which are cut, which are new; and whether rings away from the gap keep their cyclic order"""
    def contacts(M):
        rot, edges, keys = tube_torus(name, M)
        out = collections.Counter()
        for a in range(M):
            for slot, e in enumerate(rot[a]):
                out[(a, slot, tuple(sorted(edges[e])))] += 1
        return out, rot, edges
    old, rot0, e0 = contacts(N)
    new, rot1, e1 = contacts(N + 1)
    mp = lambda a: a if a <= j else a + 1
    mapped = collections.Counter({(mp(a), s, tuple(sorted(map(mp, pr)))): c for (a, s, pr), c in old.items()})
    kept = mapped & new
    cut = sum((mapped - new).values())
    added = sum((new - mapped).values())
    touched = sorted({a for (a, s, pr) in (mapped - new)} | {a for (a, s, pr) in (new - mapped)})
    return cut, added, touched


def task(args):
    name, N = args
    rot, edges, keys = tube_torus(name, N)
    return name, N, on_time(rot, edges), half_turns(name, N)


def ladder_task(args):
    n, t = args
    rot, edges = ladder_torus(n, t)
    return n, t, on_time(rot, edges)


def balls(name, R=12):
    tb = TUBES[name]
    steps = sorted({tb["join"][t] for t in tb["join"]} | {-tb["join"][t] for t in tb["join"]})
    dist, frontier = {0: 0}, [0]
    for r in range(1, R + 1):
        nxt = []
        for a in frontier:
            for s in steps:
                if a + s not in dist:
                    dist[a + s] = r
                    nxt.append(a + s)
        frontier = nxt
    return [sum(1 for d in dist.values() if d <= r) for r in range(R + 1)]


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)
    # 1: the tube tori are the lattice tori of RESCUE-MAP-20261109-001A
    import importlib.util
    spec = importlib.util.spec_from_file_location("rescue_check", ROOT / "proofs/RESCUE-MAP-20261109-001A/RESCUE-MAP-20261109-001A-P001_short_loops_rescue/check.py")
    RC = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "proofs/RESCUE-MAP-20261109-001A/RESCUE-MAP-20261109-001A-P001_short_loops_rescue"))
    spec.loader.exec_module(RC)
    same = {}
    for name, kind, v in (("square twist (2, 1)", "square", ((2, 1), None)), ("triangular sqrt 3 (1, -1)", "triangular", ((1, -1), None))):
        for N in range(3, 21):
            B = ((N, 0), (2, 1)) if kind == "square" else ((1, -1), (N, 0))
            lat = RC.on_time((kind, B))[2]
            rot, edges, keys = tube_torus(name, N)
            same["%s %d" % (name, N)] = [lat, on_time(rot, edges)]
    check("1_tube_tori_read_as_the_lattice_tori", all(a == b for a, b in same.values()), same)
    # 2: inserting one ring is a local rewiring
    diffs = {}
    for name in TUBES:
        for N in (8, 12, 20):
            for j in (0, 3, N - 1):
                cut, added, touched = insertion_diff(name, N, j)
                diffs["%s N=%d after %d" % (name, N, j)] = {"slots cut": cut, "slots added": added, "rings touched": touched}
    sq = [d for k, d in diffs.items() if k.startswith("square")]
    tr = [d for k, d in diffs.items() if k.startswith("triangular")]
    ok2 = all(len(d["rings touched"]) <= 5 for d in sq + tr)
    check("2_one_ring_inserted_is_a_local_rewiring", ok2, diffs)
    # 3: every stage on time and persistent
    with Pool(20) as pool:
        res = pool.map(task, [(name, N) for name in TUBES for N in range(3, NMAX + 1)], chunksize=2)
        lad = pool.map(ladder_task, [(n, t) for n in range(2, NMAX // 2 + 1) for t in (0, 1)], chunksize=2)
    stages = collections.defaultdict(dict)
    for name, N, ok, ht in res:
        stages[name][N] = [ok, ht]
    ok3 = all(all(v[0] == (N >= TUBES[name]["first"]) for N, v in stages[name].items()) and
              all(v[1] for N, v in stages[name].items()) for name in stages)
    ok3 &= all(ok for n, t, ok in lad)
    check("3_every_stage_on_time_and_persistent", ok3,
          {name: {"on time from": min(N for N, v in st.items() if v[0]), "late at": [N for N, v in st.items() if not v[0]],
                  "half-turn at every contact, stages read": sum(1 for v in st.values() if v[1])} for name, st in stages.items()}
          | {"ladders on time": sum(ok for n, t, ok in lad), "ladders read": len(lad)})
    # 4: the tubes' balls grow linearly
    bl = {name: balls(name) for name in TUBES}
    check("4_tube_balls_grow_linearly", all(b[r] == 4 * r + 1 for b in bl.values() for r in range(len(b))), bl)
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "GROW-PLAIN-20261109-001B", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same_ = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same_ else "DIFFERS from result.json")
        sys.exit(0 if same_ and allok else 1)


if __name__ == "__main__":
    main()
