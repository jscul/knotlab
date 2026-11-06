"""Check for CLOSED-H1-20261025-001B-P001: the two connected quandles of order 6 colour every knot equally.

Standard library only. Parts:
  1. groups: GL(2,3) acts on the four lines of F3^2, giving GL(2,3) -> PGL(2,3) = S4 with kernel {I, -I}; every pair of lifts of a
     transposition t and of the double transposition z commuting with it anticommutes; lifts of a 4-cycle and of its square commute
     (control);
  2. quandles: the Galkin quandles G(Z2, 0) and G(Z2, 1) (Clark-Elhamdadi-Hou-Saito-Yeatman, Def. 3.4) are isomorphic to the
     conjugation quandles of transpositions and of 4-cycles of S4, and not crosswise;
  3. knots: for every knot of a zoo (braid closures, alternating diagrams of plane graphs with and without tripled edges, connected sums,
     random braids), every S4 colouring whose meridian lies over a fixed S3 transposition is enumerated with its preferred longitude;
     (a) transposition longitudes are 1; (b) over every S3 colouring, each of the four meridian values over it (two transpositions, two
     4-cycles) is taken by the same number of lifts, with one longitude per meridian value (the half-lives-half-dies image is a graph
     over the meridian); (c) the totals for the two quandles agree, and 3-colourable knots have non-trivial 4-cycle colourings;
  4. controls: the same Gauss word with one crossing sign flipped is a virtual knot whose two counts differ; the classical trefoil word
     gives equal counts; the 4-cycle longitudes take both values on the zoo, so (b) is not vacuous.
Writes result.json next to this file."""
import itertools
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------------------------------------------------------ S4
ELEMS = list(itertools.permutations(range(4)))
IDX = {p: i for i, p in enumerate(ELEMS)}
MUL = [[IDX[tuple(ELEMS[a][ELEMS[b][i]] for i in range(4))] for b in range(24)] for a in range(24)]   # a*b = a after b
E0 = IDX[(0, 1, 2, 3)]
INV = [next(b for b in range(24) if MUL[a][b] == E0) for a in range(24)]


def ppow(a, k):
    r = E0
    if k < 0:
        a, k = INV[a], -k
    for _ in range(k):
        r = MUL[r][a]
    return r


def cycle_type(a):
    p, seen, t = ELEMS[a], set(), []
    for i in range(4):
        if i not in seen:
            L, j = 0, i
            while j not in seen:
                seen.add(j)
                j = p[j]
                L += 1
            t.append(L)
    return tuple(sorted(t, reverse=True))


CLASSES = defaultdict(list)
for _a in range(24):
    CLASSES[cycle_type(_a)].append(_a)
PAIRINGS = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]


def pairing_of(g):
    """the pairing of {0,1,2,3} fixed by g (its image in S3 = S4/V4 for transpositions and 4-cycles), or None"""
    p = ELEMS[g]
    fixed = [i for i, ((a, b), (c, d)) in enumerate(PAIRINGS)
             if {frozenset((p[a], p[b])), frozenset((p[c], p[d]))} == {frozenset((a, b)), frozenset((c, d))}]
    return fixed[0] if len(fixed) == 1 else None


T0 = IDX[(1, 0, 2, 3)]                                        # the transposition (01)
COSET = [g for g in range(24) if cycle_type(g) in ((2, 1, 1), (4,)) and pairing_of(g) == pairing_of(T0)]
C0 = next(g for g in COSET if cycle_type(g) == (4,))          # a 4-cycle over the same S3 element
Z0 = next(g for g in CLASSES[(2, 2)] if MUL[g][T0] == MUL[T0][g])
assert len(COSET) == 4 and sorted(cycle_type(g) for g in COSET) == [(2, 1, 1), (2, 1, 1), (4,), (4,)]


# ------------------------------------------------------------------------------------------------------- part 1: GL(2,3)
def gl23():
    mats = [((a, b), (c, d)) for a, b, c, d in itertools.product(range(3), repeat=4) if (a * d - b * c) % 3]
    lines = [(1, 0), (0, 1), (1, 1), (1, 2)]

    def norm(v):
        x, y = v[0] % 3, v[1] % 3
        k = next(k for k in (1, 2) if ((x * k) % 3, (y * k) % 3) in lines)
        return ((x * k) % 3, (y * k) % 3)

    def act(M, v):
        return norm((M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1]))

    def mmul(A, B):
        return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) % 3 for j in range(2)) for i in range(2))

    proj = {M: IDX[tuple(lines.index(act(M, v)) for v in lines)] for M in mats}
    return mats, proj, mmul


def part1():
    mats, proj, mmul = gl23()
    I2 = ((1, 0), (0, 1))
    mI = ((2, 0), (0, 2))
    surj = sorted(set(proj.values())) == list(range(24))
    kernel = sorted(M for M in mats if proj[M] == E0) == sorted([I2, mI])
    fibres = Counter(proj.values())
    inv = {M: next(N for N in mats if mmul(M, N) == I2) for M in mats}
    homom = all(proj[mmul(A, B)] == MUL[proj[A]][proj[B]] for A in mats for B in mats)

    def comm(A, B):
        return mmul(mmul(A, B), mmul(inv[A], inv[B]))
    anti, ctrl = True, True
    for t in CLASSES[(2, 1, 1)]:
        z = next(g for g in CLASSES[(2, 2)] if MUL[g][t] == MUL[t][g])
        for A in (M for M in mats if proj[M] == t):
            for B in (M for M in mats if proj[M] == z):
                anti &= comm(A, B) == mI
    for c in CLASSES[(4,)]:
        for A in (M for M in mats if proj[M] == c):
            for B in (M for M in mats if proj[M] == MUL[c][c]):
                ctrl &= comm(A, B) == I2
    ok = len(mats) == 48 and surj and kernel and set(fibres.values()) == {2} and homom and anti and ctrl
    return {"order": len(mats), "onto S4": surj, "kernel {I,-I}": kernel, "homomorphism": homom,
            "lifts of t and z anticommute (all pairs, all t)": anti, "control: lifts of c and c^2 commute": ctrl, "ok": ok}


# ------------------------------------------------------------------------------------------------------ part 2: quandles
def part2():
    def galkin(c):
        mu = {0: 2, 1: -1, 2: -1}
        tau = {0: 0, 1: 0, 2: c}
        els = [(x, a) for x in range(3) for a in range(2)]
        return els, {(p, q): ((2 * q[0] - p[0]) % 3, (-p[1] + mu[(p[0] - q[0]) % 3] * q[1] + tau[(p[0] - q[0]) % 3]) % 2)
                     for p in els for q in els}

    def conj(cls):
        return cls, {(x, y): MUL[MUL[INV[y]][x]][y] for x in cls for y in cls}

    def n_iso(A, B):
        (ea, oa), (eb, ob) = A, B
        return sum(1 for perm in itertools.permutations(eb)
                   if all(dict(zip(ea, perm))[oa[(x, y)]] == ob[(dict(zip(ea, perm))[x], dict(zip(ea, perm))[y])]
                          for x in ea for y in ea))
    rows = {}
    for c in (0, 1):
        for name, cls in (("transpositions", CLASSES[(2, 1, 1)]), ("4-cycles", CLASSES[(4,)])):
            rows[f"G(Z2,{c}) ~ {name}"] = n_iso(galkin(c), conj(cls))
    ok = (rows["G(Z2,0) ~ transpositions"] > 0 and rows["G(Z2,1) ~ 4-cycles"] > 0
          and rows["G(Z2,0) ~ 4-cycles"] == 0 and rows["G(Z2,1) ~ transpositions"] == 0)
    return {"isomorphism counts": rows, "ok": ok}


# ------------------------------------------------------------------------------------------- Gauss codes and Wirtinger data
def gauss_from_braid(word, nstrands):
    """visits (crossing, over?, sign); strands oriented downward; positive letter: left strand over"""
    visits, p = [], 0
    while True:
        for j, g in enumerate(word):
            i = abs(g) - 1
            if p in (i, i + 1):
                left = p == i
                visits.append((j, (left and g > 0) or (not left and g < 0), 1 if g > 0 else -1))
                p = i + 1 if left else i
        if p == 0:
            break
    return visits if all(c == 2 for c in Counter(v[0] for v in visits).values()) and len(visits) == 2 * len(word) else None


def gauss_from_plane_graph(n, edges, rot):
    """alternating diagram from ports (e, v, +-): the corner at v joins (e, v, +) to (succ_v(e), v, -); strand (e,u,+)-(e,w,+) is over;
    the crossing sign is + when both strands cross e in the same direction. Returns None unless the diagram is a knot."""
    succ = {(rot[v][i], v): rot[v][(i + 1) % len(rot[v])] for v in range(n) for i in range(len(rot[v]))}
    pred = {(succ[k], k[1]): k[0] for k in succ}
    comps, seen = [], set()
    for e0 in range(len(edges)):
        for s0 in (1, -1):
            if (e0, s0) in seen:
                continue
            comp, e, v, s = [], e0, edges[e0][0], s0
            while (e, s) not in seen:
                seen.add((e, s))
                w = edges[e][1] if v == edges[e][0] else edges[e][0]
                comp.append((e, s == 1, 0 if v == edges[e][0] else 1))
                e, v, s = (succ[(e, w)], w, -1) if s == 1 else (pred[(e, w)], w, 1)
            comps.append(comp)
    if len(comps) != 1:
        return None
    dirs = {(e, ov): d for e, ov, d in comps[0]}
    return [(e, ov, 1 if dirs[(e, True)] == dirs[(e, False)] else -1) for e, ov, d in comps[0]]


def connected_sum(a, b):
    off = 1 + max(v[0] for v in a)
    return list(a) + [(c + off, ov, s) for c, ov, s in b]


def wirtinger(code):
    k = max(i for i, v in enumerate(code) if not v[1])
    code = code[k + 1:] + code[:k + 1]
    U = sum(1 for v in code if not v[1])
    a, over, sign, order = 0, {}, {}, []
    for c, ov, s in code:
        sign[c] = s
        if ov:
            over[c] = a
        else:
            order.append((c, a, (a + 1) % U))
            a += 1
    return U, [(over[c], i, j, sign[c]) for c, i, j in order]


def colourings(U, cr, m):
    """all rho with rho(arc 0) = m and out = over^-s in over^s, with the preferred longitude based at arc 0"""
    cls = CLASSES[cycle_type(m)]
    writhe = sum(s for *_, s in cr)
    val = [None] * U
    val[0] = m
    out = []

    def rec(k):
        if k == U:
            P = E0
            for o, i, j, s in cr:
                P = MUL[P][ppow(val[o], s)]
            assert MUL[P][val[0]] == MUL[val[0]][P]
            out.append((tuple(val), MUL[P][ppow(val[0], -writhe)]))
            return
        o, i, j, s = cr[k]
        for x in ([val[o]] if val[o] is not None else cls):
            new_o = val[o] is None
            if new_o:
                val[o] = x
            g = ppow(x, s)
            nv = MUL[MUL[INV[g]][val[i]]][g]
            new_j = val[j] is None
            if new_j:
                val[j] = nv
            if val[j] == nv:
                rec(k + 1)
            if new_j:
                val[j] = None
            if new_o:
                val[o] = None
    rec(0)
    return out


# ------------------------------------------------------------------------------------------------------------- the zoo
def plane(points, edges):
    n = len(points)
    rot = {u: sorted((e for e, (a, b) in enumerate(edges) if u in (a, b)),
                     key=lambda e: math.atan2(points[edges[e][0] + edges[e][1] - u][1] - points[u][1],
                                              points[edges[e][0] + edges[e][1] - u][0] - points[u][0])) for u in range(n)}
    return n, edges, rot


def tripled(G, k=3):
    n, E, rot = G
    ne, idx = [], {}
    for e, (u, v) in enumerate(E):
        idx[e] = list(range(len(ne), len(ne) + k))
        ne += [(u, v)] * k
    return n, ne, {v: [x for e in rot[v] for x in (idx[e] if E[e][0] == v else idx[e][::-1])] for v in range(n)}


def cyc(n):
    return n, [(i, (i + 1) % n) for i in range(n)], {i: [i, (i - 1) % n] for i in range(n)}


def zoo():
    Z = {}
    braids = {"3_1": ([1, 1, 1], 2), "4_1": ([1, -2, 1, -2], 3), "5_1": ([1] * 5, 2), "5_2": ([1, 1, 1, 2, -1, 2], 3),
              "6_1": ([1, 1, 2, -1, -3, 2, -3], 4), "6_2": ([1, 1, 1, -2, 1, -2], 3), "6_3": ([1, 1, -2, 1, -2, -2], 3),
              "7_1": ([1] * 7, 2), "8_18": ([1, -2] * 4, 3), "8_19": ([1, 2] * 4, 3), "10_124": ([1, 2] * 5, 3)}
    for name, (w, ns) in braids.items():
        Z[name] = gauss_from_braid(w, ns)
    edge = (2, [(0, 1)], {0: [0], 1: [0]})
    path = (3, [(0, 1), (1, 2)], {0: [0], 1: [0, 1], 2: [1]})
    tri_pend = plane([(0, 0), (2, 0), (1, 1.5), (1, 3)], [(0, 1), (1, 2), (2, 0), (2, 3)])
    tri_dbl = (3, [(0, 1), (0, 1), (1, 2), (2, 0)], {0: [3, 0, 1], 1: [1, 0, 2], 2: [2, 3]})
    pretzel = plane([(0, 0), (4, 0), (1.3, 1), (2.7, 1), (1.3, 0), (2.7, 0), (1.3, -1), (2.7, -1)],
                    [(0, 2), (2, 3), (3, 1), (0, 4), (4, 5), (5, 1), (0, 6), (6, 7), (7, 1)])
    Z["D(C3) = 3_1"] = gauss_from_plane_graph(*cyc(3))
    Z["D(C5) = 5_1"] = gauss_from_plane_graph(*cyc(5))
    Z["D(theta 3,3,3) = P(3,3,3)"] = gauss_from_plane_graph(*pretzel)
    for name, G in (("edge", edge), ("path", path), ("C3", cyc(3)), ("C5", cyc(5)), ("triangle+pendant", tri_pend),
                    ("triangle, doubled edge", tri_dbl)):
        Z[f"D({name}^(3))"] = gauss_from_plane_graph(*tripled(G))
    Z["3_1 # 3_1"] = connected_sum(Z["3_1"], Z["3_1"])
    Z["3_1 # D(C3^(3))"] = connected_sum(Z["3_1"], Z["D(C3^(3))"])
    rng = random.Random(20261025)
    found = 0
    while found < 6:
        ns = rng.choice([3, 4])
        w = [rng.choice([1, -1]) * rng.randint(1, ns - 1) for _ in range(rng.randint(7, 11))]
        code = gauss_from_braid(w, ns)
        if code is None:
            continue
        U, cr = wirtinger(code)
        if len(colourings(U, cr, T0)) > 1:      # keep 3-colourable ones
            Z[f"random braid {w}"] = code
            found += 1
    assert all(v is not None for v in Z.values())
    return Z


# ------------------------------------------------------------------------------------------------------ part 3: the knots
def study(code):
    U, cr = wirtinger(code)
    per = defaultdict(lambda: defaultdict(Counter))      # S3 labelling -> meridian value -> Counter(longitude)
    for m in COSET:
        for vals, lam in colourings(U, cr, m):
            lab = tuple(pairing_of(v) for v in vals)
            per[lab][m][lam] += 1
    a_ok = all(lam == E0 for lab in per for m in per[lab] if cycle_type(m) == (2, 1, 1) for lam in per[lab][m])
    b_ok, long_c = True, Counter()
    for lab, d in per.items():
        sizes = {m: sum(d[m].values()) for m in COSET}
        b_ok &= len(set(sizes.values())) == 1 and all(len(d[m]) == 1 for m in COSET)
        for m in COSET:
            if cycle_type(m) == (4,):
                long_c["1" if E0 in d[m] else "c^2"] += 1
    nt = sum(sum(per[lab][T0].values()) for lab in per)
    nc = sum(sum(per[lab][C0].values()) for lab in per)
    nontriv_phi = [lab for lab in per if len(set(lab)) > 1]
    cos = (not nontriv_phi) or any(sum(per[lab][C0].values()) > 0 for lab in nontriv_phi)
    return {"crossings": len(cr), "S3 colourings over the meridian": len(per), "lifts with meridian t": nt,
            "lifts with meridian c": nc, "C[6,1] count": 6 * nt, "C[6,2] count": 6 * nc,
            "(a) transposition longitudes 1": a_ok, "(b) per S3 colouring": b_ok, "(c) totals equal": nt == nc,
            "3-colourable => non-trivial C[6,2] colouring": cos, "4-cycle longitude values over S3 colourings": dict(long_c),
            "ok": a_ok and b_ok and nt == nc and cos}


def main():
    t0 = time.time()
    out, ok_all = {}, True
    p1 = part1()
    out["1_gl23"] = p1
    print("part 1:", p1, flush=True)
    ok_all &= p1["ok"]
    p2 = part2()
    out["2_quandles"] = p2
    print("part 2:", p2, flush=True)
    ok_all &= p2["ok"]

    rows, ok3, longs = {}, True, Counter()
    for name, code in zoo().items():
        r = study(code)
        rows[name] = r
        ok3 &= r["ok"]
        longs.update(r["4-cycle longitude values over S3 colourings"])
        print(f"part 3 {name}: {r['crossings']} crossings, {r['S3 colourings over the meridian']} S3 colourings, "
              f"t {r['lifts with meridian t']} c {r['lifts with meridian c']}, longitudes of c {r['4-cycle longitude values over S3 colourings']} "
              f"{'ok' if r['ok'] else 'FAIL'} ({time.time() - t0:.0f} s)", flush=True)
    out["3_knots"] = {"rows": rows, "knots": len(rows), "ok": ok3}
    ok_all &= ok3

    c = {}
    word = [(0, True, 1), (1, False, 1), (2, True, 1), (0, False, 1), (1, True, 1), (2, False, 1)]
    U, cr = wirtinger(word)
    c["classical trefoil word: counts equal"] = len(colourings(U, cr, T0)) == len(colourings(U, cr, C0))
    virt = [(0, True, 1), (1, False, 1), (2, True, -1), (0, False, 1), (1, True, 1), (2, False, -1)]
    U, cr = wirtinger(virt)
    vt, vc = len(colourings(U, cr, T0)), len(colourings(U, cr, C0))
    c["virtual knot (one sign flipped): counts differ"] = vt != vc
    c["virtual knot counts (t, c)"] = [vt, vc]
    c["4-cycle longitudes take both values on the zoo"] = longs["1"] > 0 and longs["c^2"] > 0
    ok4 = c["classical trefoil word: counts equal"] and c["virtual knot (one sign flipped): counts differ"] and \
        c["4-cycle longitudes take both values on the zoo"]
    out["4_controls"] = {"rows": c, "ok": ok4}
    print("part 4 controls:", c, flush=True)
    ok_all &= ok4

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "CLOSED-H1-20261025-001B-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
