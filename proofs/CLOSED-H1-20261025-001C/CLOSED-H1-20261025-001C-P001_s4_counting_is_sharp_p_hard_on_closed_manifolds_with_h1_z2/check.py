"""Check for CLOSED-H1-20261025-001C-P001: S4 counting is #P-hard on closed manifolds with first homology Z/2.

Standard library only. Parts:
  1. conventions: pi1 of p-surgery on a knot is the knot group modulo mu^p lambda, with lambda the preferred longitude; the counts
     |Hom(pi1 S3_p(K), S4)| are computed by brute force over every S4 homomorphism of the knot group; known values: S3_2(trefoil) has
     the binary octahedral group as pi1 (58 homomorphisms to S4: 1 + 9 + 24 + 24), S3_6(trefoil) = L(2,1) # L(3,2) (90 = 10 x 9);
     first homology of S3_p(K) is Z/p;
  2. the bookkeeping: the counts split by the class of the meridian image as 1 + 3 + T + F_c2 (p = 2) and 1 + 3 + T + F_1 (p = 4),
     with no 3-cycle terms;
  3. the identities: C2 + C4 = 8 + 3T and 3 C2(K) + C2(K # 3_1) = 16 + 12 T on a zoo of knots including tripled alternating diagrams,
     a gadget knot and connected sums; the trefoil's peripheral numbers (5 transposition lifts, 4-cycle lifts 1 with trivial and 4 with
     longitude c^2, for a fixed meridian);
  4. controls: dropping the 4-cycle terms, or using the blackboard longitude instead of the preferred one, breaks the identities;
     a virtual knot breaks the first identity.
Writes result.json next to this file with --write."""
import itertools
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

ELEMS = list(itertools.permutations(range(4)))
IDX = {p: i for i, p in enumerate(ELEMS)}
MUL = [[IDX[tuple(ELEMS[a][ELEMS[b][i]] for i in range(4))] for b in range(24)] for a in range(24)]
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
NAMES = {(1, 1, 1, 1): "identity", (2, 2): "double transposition", (3, 1): "3-cycle", (2, 1, 1): "transposition", (4,): "4-cycle"}


# ------------------------------------------------------------------------------------------------------------ knots
def gauss_from_braid(word, nstrands):
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
    assert all(c == 2 for c in Counter(v[0] for v in visits).values()) and len(visits) == 2 * len(word)
    return visits


def gauss_from_plane_graph(n, edges, rot):
    succ = {(rot[v][i], v): rot[v][(i + 1) % len(rot[v])] for v in range(n) for i in range(len(rot[v]))}
    pred = {(succ[key], key[1]): key[0] for key in succ}
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
    assert len(comps) == 1
    dirs = {(e, ov): d for e, ov, d in comps[0]}
    return [(e, ov, 1 if dirs[(e, True)] == dirs[(e, False)] else -1) for e, ov, d in comps[0]]


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


def gadget_edge(k):
    """the host edge replaced by k parallel copies of S(e, P(e, S(e, e)))"""
    N, ne, rot = 2, [], {0: [], 1: []}
    for j in range(k):
        a, b, i0 = N, N + 1, len(ne)
        N += 2
        ne += [(0, a), (a, 1), (a, b), (b, 1)]
        rot[0].append(i0)
        rot[a] = [i0 + 1, i0 + 2, i0]
        rot[b] = [i0 + 3, i0 + 2]
    rot[1] = [x for j in reversed(range(k)) for x in (4 * j + 3, 4 * j + 1)]
    return N, ne, rot


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


def colourings(U, cr, m, preferred=True):
    """all homomorphisms with rho(arc 0) = m; yields the longitude (preferred, or blackboard if preferred=False)"""
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
            out.append(MUL[P][ppow(val[0], -writhe)] if preferred else P)
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


def peripheral(code, preferred=True):
    """Counter over (class name, meridian image, longitude image) for all homomorphisms of the knot group to S4"""
    U, cr = wirtinger(code)
    tally = Counter()
    for ct, cls in CLASSES.items():
        for m in cls:
            for lam in colourings(U, cr, m, preferred):
                tally[(ct, m, lam)] += 1
    return tally


def surgery_count(tally, p):
    return sum(n for (ct, m, lam), n in tally.items() if MUL[ppow(m, p)][lam] == E0)


def split(tally, p):
    out = Counter()
    for (ct, m, lam), n in tally.items():
        if MUL[ppow(m, p)][lam] == E0:
            key = NAMES[ct]
            if ct == (4,):
                key += ", longitude " + ("1" if lam == E0 else "c^2" if lam == MUL[m][m] else "other")
            out[key] += n
    return dict(out)


def smith_invariants(rows, ncols):
    """invariant factors of Z^ncols / rowspace (0 for each free summand), by Smith normal form"""
    M = [r[:] for r in rows]
    m, invs, t = len(M), [], 0
    while t < min(m, ncols):
        nz = [(abs(M[i][j]), i, j) for i in range(t, m) for j in range(t, ncols) if M[i][j]]
        if not nz:
            break
        _, i, j = min(nz)
        M[t], M[i] = M[i], M[t]
        for row in M:
            row[t], row[j] = row[j], row[t]
        done = False
        while not done:
            done = True
            for i in range(t + 1, m):
                if M[i][t]:
                    q = M[i][t] // M[t][t]
                    M[i] = [a - q * b for a, b in zip(M[i], M[t])]
                    if M[i][t]:
                        M[t], M[i] = M[i], M[t]
                        done = False
            for j in range(t + 1, ncols):
                if M[t][j]:
                    q = M[t][j] // M[t][t]
                    for row in M:
                        row[j] -= q * row[t]
                    if M[t][j]:
                        for row in M:
                            row[t], row[j] = row[j], row[t]
                        done = False
            if done:
                bad = next(((i, j) for i in range(t + 1, m) for j in range(t + 1, ncols) if M[i][j] % M[t][t]), None)
                if bad:
                    M[t] = [a + b for a, b in zip(M[t], M[bad[0]])]
                    done = False
        invs.append(abs(M[t][t]))
        t += 1
    return [d for d in invs if d != 1] + [0] * (ncols - len(invs))


def h1_invariants(code, p):
    """H1 of p-surgery: abelianized Wirtinger relations and the abelianized relation mu^p lambda"""
    U, cr = wirtinger(code)
    rows = []
    for o, i, j, s in cr:
        r = [0] * U
        r[j] += 1
        r[i] -= 1
        rows.append(r)
    r = [0] * U
    r[0] += p - sum(s for *_, s in cr)
    for o, i, j, s in cr:
        r[o] += s
    rows.append(r)
    return smith_invariants(rows, U)


def zoo():
    Z = {}
    for name, (w, ns) in {"3_1": ([1, 1, 1], 2), "4_1": ([1, -2, 1, -2], 3), "5_2": ([1, 1, 1, 2, -1, 2], 3),
                          "6_1": ([1, 1, 2, -1, -3, 2, -3], 4), "8_18": ([1, -2] * 4, 3), "8_19": ([1, 2] * 4, 3)}.items():
        Z[name] = gauss_from_braid(w, ns)
    cyc3 = (3, [(0, 1), (1, 2), (2, 0)], {0: [0, 2], 1: [1, 0], 2: [2, 1]})
    edge = (2, [(0, 1)], {0: [0], 1: [0]})
    path = (3, [(0, 1), (1, 2)], {0: [0], 1: [0, 1], 2: [1]})
    tri_pend = plane([(0, 0), (2, 0), (1, 1.5), (1, 3)], [(0, 1), (1, 2), (2, 0), (2, 3)])
    pretzel = plane([(0, 0), (4, 0), (1.3, 1), (2.7, 1), (1.3, 0), (2.7, 0), (1.3, -1), (2.7, -1)],
                    [(0, 2), (2, 3), (3, 1), (0, 4), (4, 5), (5, 1), (0, 6), (6, 7), (7, 1)])
    Z["P(3,3,3)"] = gauss_from_plane_graph(*pretzel)
    for name, G in (("edge", edge), ("path", path), ("C3", cyc3), ("triangle+pendant", tri_pend)):
        Z[f"D({name}^(3))"] = gauss_from_plane_graph(*tripled(G))
    Z["gadget knot D((edge[S(e,P(e,S(e,e)))])^(3))"] = gauss_from_plane_graph(*tripled(gadget_edge(1)))
    Z["3_1 # 8_18"] = connected_sum(Z["3_1"], Z["8_18"])
    return Z


def main():
    t0 = time.time()
    out, ok_all = {}, True
    tre = gauss_from_braid([1, 1, 1], 2)
    ttre = peripheral(tre)

    # part 1: conventions
    c1 = {"S3_2(3_1): 58 (binary octahedral)": surgery_count(ttre, 2) == 58,
          "S3_-2(3_1): 58": surgery_count(ttre, -2) == 58,
          "S3_6(3_1): 90 (L(2,1) # L(3,2))": surgery_count(ttre, 6) == 90,
          "S3_1(3_1): 1 (homology sphere)": surgery_count(ttre, 1) == 1,
          "H1(S3_p(K)) = Z/p (Smith form) for 3_1, 4_1, 8_18 and p = 2, 4": all(h1_invariants(code, p) == [p] for code in (tre, gauss_from_braid([1, -2, 1, -2], 3), gauss_from_braid([1, -2] * 4, 3)) for p in (2, 4)),
          "control: H1 of 0-surgery is Z": h1_invariants(tre, 0) == [0]}
    ok1 = all(c1.values())
    out["1_conventions"] = {"rows": c1, "ok": ok1}
    print("part 1:", c1, flush=True)
    ok_all &= ok1

    # trefoil peripheral numbers for a fixed meridian
    t0m = CLASSES[(2, 1, 1)][0]
    c0m = CLASSES[(4,)][0]
    tre_t = sum(n for (ct, m, lam), n in ttre.items() if m == t0m)
    tre_c1 = sum(n for (ct, m, lam), n in ttre.items() if m == c0m and lam == E0)
    tre_c2 = sum(n for (ct, m, lam), n in ttre.items() if m == c0m and lam == MUL[c0m][c0m])
    tre_ok = (tre_t, tre_c1, tre_c2) == (5, 1, 4)

    rows, ok3 = {}, tre_ok
    for name, code in zoo().items():
        tal = peripheral(code)
        T = sum(n for (ct, m, lam), n in tal.items() if ct == (2, 1, 1))
        C2, C4 = surgery_count(tal, 2), surgery_count(tal, 4)
        Cs = surgery_count(peripheral(connected_sum(code, tre)), 2)
        sp2, sp4 = split(tal, 2), split(tal, 4)
        F = sum(n for (ct, m, lam), n in tal.items() if ct == (4,))
        trans_long_trivial = all(lam == E0 for (ct, m, lam) in tal if ct == (2, 1, 1))
        book = (sp2.get("identity", 0) == 1 and sp2.get("double transposition", 0) == 3 and "3-cycle" not in sp2
                and sp2.get("transposition", 0) == T and sp4.get("transposition", 0) == T and "3-cycle" not in sp4
                and F == T and trans_long_trivial)
        r = {"T": T, "C2": C2, "C4": C4, "C2(K # 3_1)": Cs, "split p=2": sp2, "split p=4": sp4,
             "C2 + C4 = 8 + 3T": C2 + C4 == 8 + 3 * T, "3 C2 + C2(K#3_1) = 16 + 12T": 3 * C2 + Cs == 16 + 12 * T,
             "bookkeeping": book}
        r["ok"] = r["C2 + C4 = 8 + 3T"] and r["3 C2 + C2(K#3_1) = 16 + 12T"] and book
        rows[name] = r
        ok3 &= r["ok"]
        print(f"part 3 {name}: T={T} C2={C2} C4={C4} C2(K#3_1)={Cs} {'ok' if r['ok'] else 'FAIL'} ({time.time() - t0:.0f} s)",
              flush=True)
    out["3_identities"] = {"trefoil fixed-meridian numbers (t, c with 1, c with c^2)": [tre_t, tre_c1, tre_c2],
                           "rows": rows, "ok": ok3}
    ok_all &= ok3

    # part 4: controls
    c = {}
    name = "D(C3^(3))"
    r = rows[name]
    c["dropping the 4-cycle terms breaks C2 + C4 = 8 + 3T"] = (r["C2"] - r["split p=2"].get("4-cycle, longitude c^2", 0)) + \
        (r["C4"] - r["split p=4"].get("4-cycle, longitude 1", 0)) != 8 + 3 * r["T"]
    code = zoo()[name]
    talb = peripheral(code, preferred=False)
    Tb = sum(n for (ct, m, lam), n in talb.items() if ct == (2, 1, 1))
    c["blackboard longitude breaks the identity"] = surgery_count(talb, 2) + surgery_count(talb, 4) != 8 + 3 * Tb
    virt = [(0, True, 1), (1, False, 1), (2, True, -1), (0, False, 1), (1, True, 1), (2, False, -1)]
    talv = peripheral(virt)
    Tv = sum(n for (ct, m, lam), n in talv.items() if ct == (2, 1, 1))
    c["virtual knot breaks C2 + C4 = 8 + 3T"] = surgery_count(talv, 2) + surgery_count(talv, 4) != 8 + 3 * Tv
    ok4 = all(c.values())
    out["4_controls"] = {"rows": c, "ok": ok4}
    print("part 4 controls:", c, flush=True)
    ok_all &= ok4

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "CLOSED-H1-20261025-001C-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
