"""Checks for SIGNED-3D-20261029-001B-P001 (what the twist sees of a three-manifold).

On sampled ordered triangulations of closed orientable three-manifolds (random order-preserving face pairings of 1 to 4 tetrahedra, as in
TWIST-3D-20261025-001A, at most 12 edges; first homology by Smith normal form):
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the cubic form two ways: for every mod-2 1-cocycle a, the triple cup product sum_t a01 a12 a23 (the law's exponent) equals the Bockstein
    form sum_t a01 b123 with b = (delta of the 0/1 lift of a)/2 (Steenrod: a u a = Sq^1 a = rho beta a); the value depends only on the class
  2 linearity (Wu): l(a + b) = l(a) + l(b) for every pair of classes, so D(M) = sum over H^1(M; Z/2) of (-1)^l(a) is |H^1| or 0
  3 the twelve state sums of SIGNED-3D-20261029-001A, normalized by (lambda^3/mu)^V lambda^(-T), equal 1, 1, 2, |H^1|/2, |H^1|/2, |H^1|, 1 for
    the counting laws and D/2, D/2, (D + |H^1|)/2, (D + |H^1|)/2, D for the twisted ones
  4 the linking-form rule: with cyclic first homology Z/n, D = 1 for n odd, 0 for n = 2 mod 4, 2 for n = 0 mod 4; with H_1 = Z, D = 2
  5 the twist separates manifolds with the same homology: among samples with H_1 = (Z/2)^2 (|H^1| = 4) both D = 0 and D = 4 occur, while
    every counting law takes the same value on them
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (standard library and the libraries of ticket A; about a minute)"""
import hashlib, importlib.util, itertools, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ADIR = os.path.join(ROOT, "proofs/SIGNED-3D-20261029-001A/SIGNED-3D-20261029-001A-P001_one_twist_and_nothing_else")
sys.path.insert(0, ADIR)
import signed3d_lib as L  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "twist3d_check", os.path.join(ROOT, "proofs/TWIST-3D-20261025-001A/TWIST-3D-20261025-001A-P001_twists_add_nothing_to_counting/check.py"))
tw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tw)

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

EDGES4 = L.EDGES4
EI = {e: k for k, e in enumerate(EDGES4)}


def tet_signs(T, pairing):
    sign = {0: 1}
    adj = {}
    for (t, i), (u, j) in pairing:
        adj.setdefault(t, []).append((u, i, j))
        adj.setdefault(u, []).append((t, j, i))
    stack = [0]
    while stack:
        t = stack.pop()
        for u, i, j in adj.get(t, []):
            if u not in sign:
                sign[u] = -sign[t] * (-1) ** i * (-1) ** j
                stack.append(u)
    return sign


def sample(n, seed=20261029, cap=10):
    rng = random.Random(seed)
    samples, per, attempts = [], {}, 0
    while len(samples) < n and attempts < 300000:
        attempts += 1
        T = rng.randint(1, 4)
        faces = [(t, i) for t in range(T) for i in range(4)]
        rng.shuffle(faces)
        pairing = [(faces[k], faces[k + 1]) for k in range(0, 4 * T, 2)]
        if not tw.is_manifold(T, pairing):
            continue
        free, tors, V, E = tw.homology(T, pairing)
        if E > 12:
            continue
        key = (free, tuple(tors))
        if per.get(key, 0) >= cap:
            continue
        per[key] = per.get(key, 0) + 1
        samples.append((T, pairing, free, tors, V, E))
    return samples


class Tri:
    """an ordered triangulation: tetrahedra as lists of global edge ids in local order, signs, counts"""

    def __init__(self, T, pairing):
        vd, ed, fd, verts, edges, faces = tw.build(T, pairing)
        ei = {e: k for k, e in enumerate(edges)}
        self.T, self.V, self.E = T, len(verts), len(edges)
        self.tet = [[ei[ed.find((t, a, b))] for a, b in EDGES4] for t in range(T)]
        self.sign = tet_signs(T, pairing)
        # every face of every tetrahedron as (edge ab, edge bc, edge ac) in its own vertex order
        self.faces = [[(self.tet[t][EI[(a, b)]], self.tet[t][EI[(b, c)]], self.tet[t][EI[(a, c)]]) for a, b, c in L.FACES4] for t in range(T)]
        vi = {v: k for k, v in enumerate(verts)}
        self.edge_ends = {}
        for t in range(T):
            for a, b in EDGES4:
                self.edge_ends[ei[ed.find((t, a, b))]] = (vi[vd.find((t, a))], vi[vd.find((t, b))])

    def cocycles(self):
        out = []
        for x in itertools.product((0, 1), repeat=self.E):
            if all((x[p] + x[q] + x[r]) % 2 == 0 for fs in self.faces for p, q, r in fs):
                out.append(x)
        return out

    def coboundaries(self):
        out = set()
        for g in itertools.product((0, 1), repeat=self.V):
            out.add(tuple((g[a] + g[b]) % 2 for a, b in (self.edge_ends[e] for e in range(self.E))))
        return out

    def l_cup(self, a):
        """sum over tetrahedra of a01 a12 a23 (the twisted law's exponent)"""
        return sum(a[tt[EI[(0, 1)]]] * a[tt[EI[(1, 2)]]] * a[tt[EI[(2, 3)]]] for tt in self.tet) % 2

    def l_bockstein(self, a):
        """sum over tetrahedra of a01 b123, b = (integer coboundary of the 0/1 lift of a)/2 on the face 123"""
        s = 0
        for tt in self.tet:
            d = a[tt[EI[(2, 3)]]] - a[tt[EI[(1, 3)]]] + a[tt[EI[(1, 2)]]]
            assert d % 2 == 0
            s += a[tt[EI[(0, 1)]]] * ((d // 2) % 2)
        return s % 2

    def l_star(self, a):
        """a wrong cubic: sum over tetrahedra of a01 a02 a03 (the star of vertex 0), used as a control"""
        return sum(a[tt[EI[(0, 1)]]] * a[tt[EI[(0, 2)]]] * a[tt[EI[(0, 3)]]] for tt in self.tet) % 2

    def state_sum(self, W):
        tot = 0
        for lab in itertools.product((0, 1), repeat=self.E):
            p = 1
            for t, tt in enumerate(self.tet):
                p *= W[(self.sign[t], tuple(lab[k] for k in tt))]
                if p == 0:
                    break
            tot += p
        return tot


samples = sample(80)
LAWS = {"all 0": L.law(L.SUPPORTS["all 0"]), "all 1": L.law(L.SUPPORTS["all 1"]), "all equal": L.law(L.SUPPORTS["all equal"]),
        "even cocycles": L.law(L.ZEVEN), "odd cocycles": L.law(L.ZODD), "even or odd": L.mixed(False, False), "free": L.law(L.SUPPORTS["free"]),
        "even twisted": L.law(L.ZEVEN, L.twist_even), "odd twisted": L.law(L.ZODD, L.twist_odd), "mixed, even twisted": L.mixed(True, False),
        "mixed, odd twisted": L.mixed(False, True), "mixed, both twisted": L.mixed(True, True)}
FACT = {"all 0": (1, 1), "all 1": (1, 1), "all equal": (1, 1), "even cocycles": (1, 2), "odd cocycles": (1, 2), "even or odd": (1, 2),
        "free": (2, 16), "even twisted": (1, 2), "odd twisted": (1, 2), "mixed, even twisted": (1, 2), "mixed, odd twisted": (1, 2),
        "mixed, both twisted": (1, 2)}

c1 = c_cls = c2 = c3 = c4 = True
c5 = {}
rows, star_bad = [], 0
for T, pairing, free, tors, V, E in samples:
    tri = Tri(T, pairing)
    Z = tri.cocycles()
    B = tri.coboundaries()
    h1 = len(Z) // len(B)
    assert h1 == 2 ** (free + sum(1 for d in tors if d % 2 == 0))
    # 1: the two formulas agree on every cocycle, and depend only on the class
    for a in Z:
        c1 &= tri.l_cup(a) == tri.l_bockstein(a)
    reps, seen = [], set()
    for a in Z:
        if a in seen:
            continue
        coset = {tuple((x + y) % 2 for x, y in zip(a, b)) for b in B}
        seen |= coset
        reps.append(a)
        vals = {tri.l_bockstein(x) for x in coset}
        c_cls &= len(vals) == 1
        star_bad += len({tri.l_star(x) for x in coset}) > 1
    # 2: linearity over classes
    lval = {a: tri.l_bockstein(a) for a in reps}
    for a, b in itertools.combinations_with_replacement(reps, 2):
        s = tuple((x + y) % 2 for x, y in zip(a, b))
        c2 &= tri.l_bockstein(s) == (lval[a] + lval[b]) % 2
    D = sum((-1) ** lval[a] for a in reps)
    c2 &= D in (0, h1)
    # 3: the twelve state sums
    want = {"all 0": 1, "all 1": 1, "all equal": 2, "even cocycles": h1 / 2, "odd cocycles": h1 / 2, "even or odd": h1, "free": 1,
            "even twisted": D / 2, "odd twisted": D / 2, "mixed, even twisted": (D + h1) / 2, "mixed, odd twisted": (D + h1) / 2,
            "mixed, both twisted": D}
    got = {}
    for name, W in LAWS.items():
        lam, mu = FACT[name]
        got[name] = tri.state_sum(W) * (lam ** 3 / mu) ** tri.V * lam ** (-tri.T)
        c3 &= abs(got[name] - want[name]) < 1e-9
    # 4: the linking-form rule for cyclic homology
    if free == 0 and len(tors) <= 1:
        n = tors[0] if tors else 1
        c4 &= D == (1 if n % 2 else (0 if n % 4 == 2 else 2))
    if free == 1 and not tors:
        c4 &= D == 2
    key = f"Z^{free} + {list(tors)}"
    c5.setdefault(key, set()).add((h1, D, tuple(round(got[n], 6) for n in ("all equal", "even cocycles", "odd cocycles", "even or odd", "free"))))
    rows.append((key, T, h1, D))

types = sorted({r[0] for r in rows})
report("1 the cubic form two ways: triple cup product = Bockstein formula on every cocycle; constant on classes", c1 and c_cls,
       {"samples": len(samples), "homology types": types, "every cocycle agrees": c1, "class function": c_cls})
report("2 a -> a^3 is linear on H^1(M; Z/2) (Wu), so D(M) is |H^1| or 0", c2, {"pairs of classes checked on every sample": c2})
report("3 the twelve normalized state sums equal their formulas in |H^1| and D", c3, {"samples": len(samples)})
cyc = {k: sorted({d for kk, t, h, d in rows if kk == k}) for k in types}
report("4 linking-form rule: cyclic H_1 = Z/n gives D = 1 (n odd), 0 (n = 2 mod 4), 2 (n = 0 mod 4); H_1 = Z gives 2", c4, {"D by homology type": cyc})
z22 = sorted(c5.get("Z^0 + [2, 2]", set()))
counting_same = len({v[2] for v in z22}) == 1
sep = {d for h, d, v in z22} == {0, 4}
report("5 the twist separates manifolds with H_1 = (Z/2)^2 that every counting law identifies", sep and counting_same,
       {"(|H^1|, D, counting values) for H_1 = (Z/2)^2": [list(map(str, v)) for v in z22], "tetrahedra of those samples":
        sorted({(t, d) for k, t, h, d in rows if k == "Z^0 + [2, 2]"})})

# ---------------------------------------------------------------- 6 controls
ctrl = {}
ids = L.identities()
Wstar = {(s, l): (0 if l not in L.ZEVEN else (-1 if (l[0] and l[1] and l[2]) else 1)) for s in (1, -1) for l in L.LABS}
ctrl["the star cubic (-1)^(x01 x02 x03) on even cocycles fails the move identities"] = not L.direct_ok(ids, Wstar, 1, 2)
ctrl["the star cubic is not a function of the class on some sample"] = star_bad > 0
ctrl["some sample has H_1 = Z/2, where the twist vanishes"] = any(k == "Z^0 + [2]" and d == 0 for k, t, h, d in rows)
report("6 controls fire", all(ctrl.values()), ctrl)

out["rows"] = rows
out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIGNED-3D-20261029-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
