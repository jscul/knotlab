"""Checks for SHARED-SUBDIVISION-20261029-001B-P001 (the exact two-dimensional laws).

Each family's solution set on the L-torus is certified without enumeration: every configuration of the predicted set satisfies all
triangles, and the transfer-matrix count equals the size of the predicted set.

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 Newman-Moore (parity on up triangles, both parities): N(L) for L = 1..12 from the cellular automaton x -> (1 + S) x + b agrees
    with the transfer-matrix count; N(2m) = N(m)^2 for m = 1..6; at scale 2 the restriction to the coarse sites is onto the coarse
    solutions with N(m) extensions each (L = 2..12 even); at scale 3 it is not (L = 9, 12); with zero padding no nonzero row is
    fixed by 1 + S (widths up to 14)
  2 Baxter-Wu (parity on all triangles): two triangles sharing an edge force their opposite vertices equal; the torus solutions are
    the colour-class patterns of the right parity when 3 divides L and the constant b otherwise (L = 2..12); exact at scale 2 with
    one extension each (L = 6, 8, 10, 12), not at scale 3 (L = 9, 12)
  3 line collapse (twisted not-all-equal, the six exact pairs): one orbit of the representative under the point group of the lattice
    and complement; walls persist upward for the representative; the torus solutions are exactly the configurations constant along
    one lattice direction, 2^L of them (L = 2..12); exact at scale 2 (L = 6, 8, 10, 12) and scale 3 (L = 9, 12) with 2^(L - L/k)
    extensions each; no projection onto an up or down triangle is a knot (L = 3..12); on the plane, the half-lines from rows 0 and 1
    satisfy every triangle of a 24 x 24 box and differ in one site
  4 the twelve exact three-excluded pairs: one orbit; their solution sets equal the Baxter-Wu sets of one parity (L = 2..11); the
    representative's extra tuple extends to the patches of radius 1, 2 and 3
  5 every exact rule of ticket A falls in one of these families on the 2- to 11-tori, and its projection onto a triangle is a knot
    only in the Baxter-Wu and Newman-Moore families
  6 controls: the wall lemma fails for not-all-equal; the half-line violates parity on all triangles; scale 3 breaks the
    Newman-Moore correspondence on the 12-torus
Run: python3 -B check.py [--write]   (numpy; a few minutes)"""
import hashlib, itertools, json, os, sys, time
from collections import Counter

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import shared_lib as S  # noqa: E402
out, ok_all = {}, True
cube = S.cube
EVEN = frozenset(t for t in cube if sum(t) % 2 == 0)
ODD = frozenset(cube) - EVEN


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1500], flush=True)


def R(excl):
    return frozenset(cube) - {tuple(t) for t in excl}


def rule_from_label(lbl):
    up_s = lbl.split(" up ")[1].split(" down ")[0]
    dn_s = lbl.split(" down ")[1] if " down " in lbl else None
    return R(eval(up_s)), (R(eval(dn_s)) if dn_s else None)


def torus_ok(L, rule, g):
    Rup, Rdn = rule
    for i in range(L):
        for j in range(L):
            if tuple(g[q % L][p % L] for p, q in S.up(i, j)) not in Rup:
                return False
            if Rdn is not None and tuple(g[q % L][p % L] for p, q in S.dn(i, j)) not in Rdn:
                return False
    return True


_COUNTS = {}


def count(L, rule):
    k = (L, rule[0], rule[1])
    if k not in _COUNTS:
        _COUNTS[k] = int(round(S.solution_count(L, *rule)))
    return _COUNTS[k]


def certified(L, rule, predicted):
    """the predicted set is exactly the solution set: all predicted configurations satisfy the rule, and the count matches"""
    return all(torus_ok(L, rule, g) for g in predicted) and count(L, rule) == len(predicted)


def nm_set(L, b):
    out_ = set()
    for r in range(1 << L):
        rows = [[(r >> i) & 1 for i in range(L)]]
        for _ in range(L):
            x = rows[-1]
            rows.append([x[i] ^ x[(i + 1) % L] ^ b for i in range(L)])
        if rows[L] == rows[0]:
            out_.add(tuple(tuple(row) for row in rows[:L]))
    return out_


def bw_set(L, b):
    if L % 3 == 0:
        pats = [v for v in itertools.product((0, 1), repeat=3) if sum(v) % 2 == b]
        return {tuple(tuple(v[(i - j) % 3] for i in range(L)) for j in range(L)) for v in pats}
    return {tuple(tuple(b for _ in range(L)) for _ in range(L))}


def line_sets(L, rule):
    """configurations constant along one of the three lattice directions that satisfy the rule"""
    found = set()
    for c in itertools.product((0, 1), repeat=L):
        for g in (tuple(tuple(c[i] for i in range(L)) for j in range(L)),            # constant along (0, 1)
                  tuple(tuple(c[j] for i in range(L)) for j in range(L)),            # constant along (1, 0)
                  tuple(tuple(c[(i + j) % L] for i in range(L)) for j in range(L))):  # constant along (1, -1)
            if torus_ok(L, rule, g):
                found.add(g)
    return found


def restrict(g, k):
    m = len(g) // k
    return tuple(tuple(g[k * j][k * i] for i in range(m)) for j in range(m))


def projection_test(fine, coarse, k):
    img = Counter(restrict(g, k) for g in fine)
    cs = set(coarse)
    return {"onto": set(img) == cs, "extra": len(set(img) - cs), "extensions": sorted({img[c] for c in cs}) if cs else []}


def tri_projection(sols, tri):
    return {tuple(g[q % len(g)][p % len(g)] for p, q in tri) for g in sols}


def main(write):
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = {p: h for p, h in man["parent_bindings"].items()
           if hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() != h}
    report("0 dependency artifacts bound by hash", not bad, {"parents": len(man["parent_bindings"]), "mismatched": bad})
    resA = json.load(open(os.path.join(ROOT, [p for p in man["lineage"]["parents"] if p.endswith("result.json")][0])))
    exact_rules = [r["rule"] for r in resA["rules"] if r["exact at scale 2"] or r["exact at scale 3"]]

    # 1 Newman-Moore
    d1, ok1 = {}, True
    for b, Rel in ((0, EVEN), (1, ODD)):
        rule = (Rel, None)
        NM = {L: nm_set(L, b) for L in range(1, 13)}
        N = {L: len(NM[L]) for L in NM}
        cert = all(certified(L, rule, NM[L]) for L in range(2, 13))
        sq = all(N[2 * m] == N[m] ** 2 for m in range(1, 7))
        sc2 = {L: projection_test(NM[L], NM[L // 2], 2) for L in range(2, 13, 2)}
        sc3 = {L: projection_test(NM[L], NM[L // 3], 3) for L in (9, 12)}
        ok1 &= cert and sq and all(v["onto"] and v["extra"] == 0 and v["extensions"] == [N[L // 2]] for L, v in sc2.items())
        ok1 &= all(not (v["onto"] and v["extra"] == 0) for v in sc3.values())
        d1[f"b={b}"] = {"N(L), L=1..12": [N[L] for L in range(1, 13)], "certified L=2..12": cert, "N(2m) = N(m)^2": sq,
                        "scale 2": sc2, "scale 3": sc3}
    bit = lambda v, i, w: (v >> i) & 1 if 0 <= i < w else 0
    fin = all(any(bit(v, i, w) != bit(v, i + 1, w) for i in range(-1, w)) for w in range(1, 15) for v in range(1, 1 << w))
    ok1 &= fin
    d1["with zero padding no nonzero finitely supported row is constant (so not fixed by 1 + S)"] = fin
    report("1 Newman-Moore", ok1, d1)

    # 2 Baxter-Wu
    d2, ok2 = {}, True
    rh = all(s[0] == s[3] for s in itertools.product((0, 1), repeat=4)
             for Rel in (EVEN, ODD) if (s[0], s[1], s[2]) in Rel and (s[1], s[2], s[3]) in Rel)
    ok2 &= rh
    d2["two triangles sharing an edge force the opposite vertices equal"] = rh
    for b, Rel in ((0, EVEN), (1, ODD)):
        rule = (Rel, Rel)
        cert = {L: certified(L, rule, bw_set(L, b)) for L in range(2, 13)}
        sc = {}
        for (L, k) in ((6, 2), (8, 2), (10, 2), (12, 2), (9, 3), (12, 3)):
            res = projection_test(bw_set(L, b), bw_set(L // k, b), k)
            sc[f"L={L} k={k}"] = res
            exact = res["onto"] and res["extra"] == 0 and res["extensions"] == [1]
            ok2 &= exact if k == 2 else not (res["onto"] and res["extra"] == 0)
        ok2 &= all(cert.values())
        d2[f"b={b}"] = {"certified L=2..12": cert, "exactness": sc}
    report("2 Baxter-Wu", ok2, d2)

    # 3 line collapse
    rep = (R([(0, 1, 1), (1, 0, 0)]), R([(0, 1, 1), (1, 0, 0)]))
    key = lambda rl: (tuple(sorted(rl[0])), tuple(sorted(rl[1])))
    twisted = [rule_from_label(r) for r in exact_rules
               if r.startswith("S1") and len(eval(r.split(" up ")[1].split(" down ")[0])) == 2]
    orbit = {key(S.transform(rep, g, gi, f)) for g, gi in S.G for f in (0, 1)}
    one_orbit = len(twisted) == 6 and {key(t) for t in twisted} <= orbit
    walls = all(si == ri and si1 == ri1 for ri, ri1, si, si1 in itertools.product((0, 1), repeat=4)
                if (ri, ri1, si) in rep[0] and (ri1, si, si1) in rep[1] and ri != ri1)
    ok3 = one_orbit and walls
    lines, scales, knots = {}, {}, {}
    for t in twisted:
        lbl = f"up {S.excl(t[0])} down {S.excl(t[1])}"
        LS = {L: line_sets(L, t) for L in range(2, 13)}
        lines[lbl] = all(len(LS[L]) == 2 ** L and certified(L, t, LS[L]) for L in range(2, 13))
        sc = {}
        for (L, k) in ((6, 2), (8, 2), (10, 2), (12, 2), (9, 3), (12, 3)):
            res = projection_test(LS[L], LS[L // k], k)
            sc[f"L={L} k={k}"] = res
            ok3 &= res["onto"] and res["extra"] == 0 and res["extensions"] == [2 ** (L - L // k)]
        scales[lbl] = sc
        knots[lbl] = any(S.is_knot(tri_projection(LS[L], tri)) for L in range(3, 13) for tri in (S.up(0, 0), S.dn(0, 0)))
        ok3 &= lines[lbl] and not knots[lbl]
    half = lambda j0: (lambda i, j: 1 if (i == 0 and j >= j0) else 0)
    hl = S.check_in_box(rep[0], rep[1], half(0), 12) and S.check_in_box(rep[0], rep[1], half(1), 12)
    diff = sum(1 for i in range(-12, 12) for j in range(-12, 12) if half(0)(i, j) != half(1)(i, j))
    ok3 &= hl and diff == 1
    report("3 line collapse (twisted not-all-equal)", ok3,
           {"six pairs in one orbit of the representative": one_orbit, "walls persist (representative)": walls,
            "solutions exactly the 2^L line-constant configurations (L = 2..12)": lines, "exactness": scales,
            "some triangle projection is a knot": knots, "half-lines from rows 0 and 1 satisfy a 24 x 24 box": hl,
            "sites where they differ": diff})

    # 4 three-excluded
    tex = [rule_from_label(r) for r in exact_rules
           if r.startswith("S1") and len(eval(r.split(" up ")[1].split(" down ")[0])) == 3]
    rep3 = tex[0]
    orb3 = {key(S.transform(rep3, g, gi, f)) for g, gi in S.G for f in (0, 1)}
    ok4 = len(tex) == 12 and {key(t) for t in tex} <= orb3
    eq = {}
    for t in tex:
        lbl = f"up {S.excl(t[0])} down {S.excl(t[1])}"
        match = [b for b in (0, 1) if all(certified(L, t, bw_set(L, b)) for L in range(2, 12))]
        eq[lbl] = match
        ok4 &= len(match) == 1
    ext = {r: extra_extends(patch(r), rep3) for r in (1, 2, 3)}
    ok4 &= all(ext.values())
    report("4 three-excluded rules", ok4, {"twelve pairs in one orbit": len(tex) == 12 and {key(t) for t in tex} <= orb3,
                                           "Baxter-Wu parity whose solution sets they equal (L = 2..11)": eq,
                                           "the representative's extra tuple extends to the patch of radius r": ext})

    # 5 synthesis
    fam, ok5 = {}, True
    for lbl in exact_rules:
        t = rule_from_label(lbl)
        kinds, knotty = set(), []
        for L in range(2, 12):
            if t[1] is None:
                cand = [("Newman-Moore", nm_set(L, b)) for b in (0, 1)]
            else:
                cand = [("Baxter-Wu", bw_set(L, b)) for b in (0, 1)] + [("line-constant", line_sets(L, t))]
            hit = next(((name, P) for name, P in cand if P and certified(L, t, P)), None)
            kinds.add(hit[0] if hit else "?")
            if hit and L >= 3:
                knotty.append(S.is_knot(tri_projection(hit[1], S.up(0, 0))))
        fam[lbl] = {"family": sorted(kinds), "triangle projection is a knot (L = 3..11)": knotty}
        ok5 &= len(kinds) == 1 and "?" not in kinds and (kinds != {"line-constant"} or not any(knotty))
    report("5 synthesis: families and knots", ok5, {"exact rules": len(exact_rules), "rules": fam})

    # 6 controls
    NAE = frozenset(cube) - {(0, 0, 0), (1, 1, 1)}
    wall_nae = all(si == ri and si1 == ri1 for ri, ri1, si, si1 in itertools.product((0, 1), repeat=4)
                   if (ri, ri1, si) in NAE and (ri1, si, si1) in NAE and ri != ri1)
    half_par = S.check_in_box(EVEN, EVEN, half(0), 6)
    res3 = projection_test(nm_set(12, 0), nm_set(4, 0), 3)
    report("6 controls", (not wall_nae) and (not half_par) and not (res3["onto"] and res3["extra"] == 0),
           {"walls persist for not-all-equal": wall_nae, "half-line satisfies parity on all triangles": half_par,
            "Newman-Moore at scale 3 on the 12-torus": res3})

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status, "checks": {"ok": ok_all, **out},
                   "seconds": round(time.time() - T0, 1)}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


def patch(r):
    def hexd(p, q):
        dx, dy = p[0] - q[0], p[1] - q[1]
        return max(abs(dx), abs(dy), abs(dx + dy))
    centre = S.up(0, 0)
    tris = []
    for i in range(-r - 2, r + 3):
        for j in range(-r - 2, r + 3):
            for kind, t in (("up", S.up(i, j)), ("dn", S.dn(i, j))):
                if all(min(hexd(v, c) for c in centre) <= r for v in t):
                    tris.append((kind, t))
    return tris


def extra_extends(tris, rule):
    """the rule's extra up tuples (allowed by the rule, not by its parity) all extend to the whole patch"""
    Rup, Rdn = rule
    par = EVEN if len(Rup & EVEN) == 4 else ODD
    extra = sorted(Rup - par)
    verts = sorted({v for _, t in tris for v in t})
    idx = {v: k for k, v in enumerate(verts)}
    cons = [(tuple(idx[v] for v in t), Rup if kind == "up" else Rdn) for kind, t in tris]
    by = {k: [] for k in range(len(verts))}
    for c in cons:
        for k in c[0]:
            by[k].append(c)
    res = []
    for tup in extra:
        val = [None] * len(verts)
        for v, x in zip(S.up(0, 0), tup):
            val[idx[v]] = x
        free = [k for k in range(len(verts)) if val[k] is None]

        def ok(k):
            return all(tuple(val[u] for u in vs) in Rel for vs, Rel in by[k] if all(val[u] is not None for u in vs))

        def rec(n):
            if n == len(free):
                return True
            k = free[n]
            for x in (0, 1):
                val[k] = x
                if ok(k) and rec(n + 1):
                    return True
            val[k] = None
            return False
        res.append(all(ok(k) for k in range(len(verts)) if val[k] is not None) and rec(0))
    return bool(res) and all(res)


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv) else 1)
