"""Checks for LATTICE-REACH-20261109-001A. Reach is read with lattice_lib.reach (rows of walk counts until the next lies in the span of
the earlier ones: exact, no lag cutoff) on loopnet_lib networks of tori of every shape. Checks 4 and 5 are computations, not theorems.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import collections
import hashlib
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LATTICE = ROOT / "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate"
RESCUE = ROOT / "proofs/RESCUE-MAP-20261109-001A/RESCUE-MAP-20261109-001A-P001_short_loops_rescue"
sys.path.insert(0, str(LATTICE))
sys.path.insert(0, str(RESCUE))
import lattice_lib as T  # noqa: E402
import rescue_lib as R  # noqa: E402

LN = T.LN
OUT = {}
T0 = time.time()
ODD, EVEN = 81, 48
DIGON = {"square": [(1, 1), (1, -1)], "triangular": [], "honeycomb": [(1, 0), (0, 1), (1, -1)]}
ROT = {"square": lambda v: (-v[1], v[0]), "triangular": lambda v: (v[0] - v[1], v[0]), "honeycomb": lambda v: (-v[0] - v[1], v[0])}
MIRRORS = {"square": [lambda v: (v[1], v[0]), lambda v: (-v[1], -v[0])],
           "triangular": [lambda v: (v[1], v[0]), lambda v: (v[0] - v[1], -v[1]), lambda v: (-v[0], v[1] - v[0])],
           "honeycomb": [lambda v: (v[1], v[0]), lambda v: (-v[0] - v[1], v[1]), lambda v: (v[0], -v[0] - v[1])]}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def hnf_lattices(N):
    for p in range(1, N + 1):
        if N % p == 0:
            for q in range(p):
                yield ((p, 0), (q, N // p))


def index(B):
    return abs(B[0][0] * B[1][1] - B[0][1] * B[1][0])


def contains(B, v):
    (a, b), (c, d) = B
    det = a * d - b * c
    x, y = v
    return (x * d - y * c) % det == 0 and (y * a - x * b) % det == 0


def invariant(B, f):
    return contains(B, f(B[0])) and contains(B, f(B[1]))


def torus(kind, B):
    """(rot, edges, pts) of the torus, or None if a contact joins a ring to itself; edge e is (type, point) by its position"""
    Q = R.Quotient(B)
    N = index(B)
    pts = sorted({Q.red((i, j)) for i in range(-2 * N, 2 * N + 1) for j in range(-2 * N, 2 * N + 1)})
    assert len(pts) == N
    if kind != "honeycomb":
        dirs = R.DIRS[kind]
        h = len(dirs) // 2
        edges, eid = [], {}
        for v in pts:
            for d in dirs[:h]:
                w = Q.red((v[0] + d[0], v[1] + d[1]))
                if w == v:
                    return None
                eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
                edges.append((v, w))
        return {v: [eid[(v, d)] for d in dirs] for v in pts}, edges, pts
    verts = [(p, s) for p in pts for s in (0, 1)]
    edges, rot = [], {v: [None] * 3 for v in verts}
    for p in pts:
        for k, q in enumerate((p, Q.red((p[0] - 1, p[1])), Q.red((p[0], p[1] - 1)))):
            rot[(p, 0)][k] = rot[(q, 1)][k] = len(edges)
            edges.append(((p, 0), (q, 1)))
    return rot, edges, pts


def reach_task(args):
    """contact level: rings each origin contact type never needs; ring level: rings the origin ring(s) never need"""
    kind, B = args
    t = torus(kind, B)
    if t is None:
        return kind, B, None
    rot, edges, pts = t
    sizes, contacts = LN.network(rot, edges, 2)
    ins = T.in_sets(sizes, contacts)
    verts = sorted(rot, key=repr)
    ring = {v: i for i, v in enumerate(verts)}
    rc = {ring[v]: rot[v] for v in rot}
    masks = {X: sum(1 << e for e in cs) for X, cs in rc.items()}
    origin = (0, 0)
    ntypes = R.TYPES[kind]
    cache = {}

    def needs(c):
        if c not in cache:
            u = T.reach(ins, c)[0]
            cache[c] = {X for X, m in masks.items() if u & m}
        return cache[c]
    o_rings = [(origin, 0), (origin, 1)] if kind == "honeycomb" else [origin]
    types = sorted(set(rot[o_rings[0]][:ntypes])) if kind != "honeycomb" else rot[(origin, 0)]
    contact_miss = max(len(rc) - len(needs(c)) for c in types)
    worst_need = min(len(needs(c)) for c in types)
    most_need = max(len(needs(c)) for c in types)
    ring_miss = max(len(rc) - len(set().union(*[needs(c) for c in rot[v]])) for v in o_rings)
    return kind, B, {"rings": len(rc), "contact miss": contact_miss, "ring miss": ring_miss, "fewest rings a contact needs": worst_need,
                     "most rings a contact needs": most_need}


# ---------- check 2: the power 2^r - 1 on odd square tori
def kstar_task(B):
    Q = R.Quotient(B)
    N = index(B)
    pts = sorted({Q.red((i, j)) for i in range(-2 * N, 2 * N + 1) for j in range(-2 * N, 2 * N + 1)})
    pos = {p: i for i, p in enumerate(pts)}
    if any(Q.red(d) == (0, 0) for d in ((1, 0), (0, 1))):
        return B, None
    sub = lambda v: {Q.red((s * v[0], s * v[1])) for s in range(N)}
    A, Bd = sub((1, -1)), sub((1, 1))
    if len(A) == 1 or len(Bd) == 1:
        return B, None
    e = 1
    while True:
        if all(Q.red((e * p[0], e * p[1])) == (0, 0) for p in pts):
            break
        e += 1
    r = 1
    while pow(2, r, e) != 1:
        r += 1
    k = 2 ** r - 1

    def mul(F, G):
        out = [0] * N
        for i, a in enumerate(F):
            if a:
                for j, b in enumerate(G):
                    if b:
                        out[pos[Q.red((pts[i][0] + pts[j][0], pts[i][1] + pts[j][1]))]] ^= 1
        return out
    Lp = [0] * N
    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        Lp[pos[Q.red(d)]] ^= 1
    res = [0] * N
    res[pos[(0, 0)]] = 1
    base = Lp
    while k:
        if k & 1:
            res = mul(res, base)
        base = mul(base, base)
        k >>= 1
    want = [0 if (p == (0, 0) or ((p in A) != (p in Bd))) else 1 for p in pts]
    return B, res == want


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)
    with Pool(20) as pool:
        jobs = {k: [(k, B) for N in range(1, ODD + 1) for B in hnf_lattices(N) if N % 2 or N <= EVEN]
                for k in ("square", "triangular", "honeycomb")}
        res = {k: pool.map(reach_task, j, chunksize=4) for k, j in jobs.items()}
        # 1: digon tori have finite feedback
        dig = {}
        for k in res:
            rows = [(B, r) for _, B, r in res[k] if r and any(contains(B, v) for v in DIGON[k])]
            dig[k] = {"digon tori": len(rows), "most rings any contact needs": max([r["most rings a contact needs"] for B, r in rows], default=0),
                      "of these, composing everywhere": sum(1 for B, r in rows if r["contact miss"] == 0),
                      "largest composing everywhere (rings)": max([r["rings"] for B, r in rows if r["contact miss"] == 0], default=0)}
        ok1 = (dig["triangular"]["digon tori"] == 0 and dig["square"]["most rings any contact needs"] <= 6
               and dig["honeycomb"]["most rings any contact needs"] <= 14)
        check("1_digon_tori_have_finite_feedback", ok1, dig)
        # 2: the power 2^r - 1 on odd square tori
        kj = [B for N in range(3, 50, 2) for B in hnf_lattices(N)]
        kr = pool.map(kstar_task, kj, chunksize=4)
        tested = [ok for B, ok in kr if ok is not None]
        check("2_odd_square_tori_power_2r_minus_1", all(tested), {"tori": len(tested), "failures": [B for B, ok in kr if ok is False]})
    # 3 and 4: odd index, computed
    odd = {}
    for k in res:
        rows = [(B, r) for _, B, r in res[k] if r and index(B) % 2 == 1 and index(B) >= 3]
        exc = []
        for B, r in rows:
            digon = any(contains(B, v) for v in DIGON[k])
            pinned = k == "honeycomb" and B[0][1] == 0 and B[1] == (0, B[0][0]) and B[0][0] % 3 != 0
            predicted = not digon and not pinned
            if (r["contact miss"] == 0) != predicted:
                exc.append([list(map(list, B)), r])
        odd[k] = {"tori": len(rows), "composing everywhere": sum(1 for B, r in rows if r["contact miss"] == 0),
                  "ring level everywhere": sum(1 for B, r in rows if r["ring miss"] == 0), "exceptions to the rule": exc}
    known = [[[[7, 0], [6, 9]]], [[[63, 0], [8, 1]]], [[[63, 0], [54, 1]]]]
    check("3_computed_odd_index_rule", not odd["square"]["exceptions to the rule"] and not odd["triangular"]["exceptions to the rule"]
          and sorted(e[0] for e in odd["honeycomb"]["exceptions to the rule"]) == sorted(k[0] for k in known), odd)
    # 5: even index, computed: how often, and no rule by the lattice mod 16, the group's 2-part or the mirrors
    even = {}
    for k in res:
        rows = [(B, r) for _, B, r in res[k] if r and index(B) % 2 == 0 and not any(contains(B, v) for v in DIGON[k])]

        def cls16(B):
            (a, b), (c, d) = B
            return frozenset(((i * a + j * c) % 16, (i * b + j * d) % 16) for i in range(16) for j in range(16))

        def two_part(B):
            (a, b), (c, d) = B
            g = math.gcd(math.gcd(a, b), math.gcd(c, d))
            v = lambda n: (n & -n).bit_length() - 1
            return v(g), v(index(B) // g)

        def ambiguous(key):
            seen = collections.defaultdict(set)
            for B, r in rows:
                seen[key(B)].add(r["contact miss"] == 0)
            return sum(1 for s in seen.values() if len(s) > 1), len(seen)
        even[k] = {"tori": len(rows), "composing everywhere": sum(1 for B, r in rows if r["contact miss"] == 0),
                   "classes mod 16 with both verdicts (of all)": ambiguous(cls16),
                   "2-parts with both verdicts (of all)": ambiguous(two_part),
                   "mirror counts with both verdicts (of all)": ambiguous(lambda B: sum(invariant(B, f) for f in MIRRORS[k]))}
    check("4_computed_even_index_has_no_rule_by_these_invariants",
          all(v["classes mod 16 with both verdicts (of all)"][0] > 0 and v["2-parts with both verdicts (of all)"][0] > 0 for v in even.values()), even)
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "LATTICE-REACH-20261109-001A", "checks": OUT, "status": "passed" if allok else "failed",
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
