"""Check for CLOSED-H1-20261025-001A-P001: independent replay of BOUNDED-H1-20261025-001A.

Standard library only; imports nothing from the producer's check. Written in the same session (V1 independence). Parts:
  1. diagrams: the alternating diagram of a plane graph, rebuilt from ports and corners, alternates, has 1 + dim B(G) components
     (dim B computed from the cut space) and determinant |Delta(-1)| equal to the spanning-tree count;
  2. bicycle law: for G with tripled edges, brute-force S4 transposition colourings of the Wirtinger presentation equal
     sum_phi 2^(c(H_phi) + dim B(H_phi)) and the twelve-state sum 2^-n sum_z prod (1 - 2[z' = nu(z)]);
  3. links: with edges subdivided, brute-force counts equal 2^-n 4^m Z_Potts(G; 12, 1/2);
  4. gadgets and knots: the gadget S(e,P(e,S(e,e))) summed over internal states has matrix 68J + 32I - 8N; substituted into hosts
     with odd spanning-tree count it gives knots for odd parallel powers and links for even ones; brute-force counts of the knots
     equal 2^-N 68^(km) sum_ij N_ij ((25/17)^i (15/17)^j)^k;
  5. interpolation: doubling the edges outside a spanning tree makes the tree count odd and keeps P(H, 12); the Vandermonde solve over
     odd powers recovers P(H, 12), computed by the subset expansion;
  6. controls: the law without the bicycle term fails; a wrong Potts parameter is rejected; a wrong gadget matrix is rejected.
Writes result.json next to this file with --write."""
import itertools
import json
import math
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------------------------------------------------------ S4
ELEMS = list(itertools.permutations(range(4)))
IDX = {p: i for i, p in enumerate(ELEMS)}
MUL = [[IDX[tuple(ELEMS[a][ELEMS[b][i]] for i in range(4))] for b in range(24)] for a in range(24)]
E0 = IDX[(0, 1, 2, 3)]
INV = [next(b for b in range(24) if MUL[a][b] == E0) for a in range(24)]
TRANSP = [i for i, p in enumerate(ELEMS) if sum(p[k] != k for k in range(4)) == 2]
assert len(TRANSP) == 6
CONJ = [[MUL[MUL[INV[o]][x]][o] for o in range(24)] for x in range(24)]     # CONJ[x][o] = o^-1 x o


# --------------------------------------------------------------------------------------------------------- plane graphs
def plane(points, edges):
    n = len(points)
    rot = {u: sorted((e for e, (a, b) in enumerate(edges) if u in (a, b)),
                     key=lambda e: math.atan2(points[edges[e][0] + edges[e][1] - u][1] - points[u][1],
                                              points[edges[e][0] + edges[e][1] - u][0] - points[u][0])) for u in range(n)}
    return n, list(edges), rot


def cyc(n):
    return n, [(i, (i + 1) % n) for i in range(n)], {i: [i, (i - 1) % n] for i in range(n)}


def theta(k):
    return 2, [(0, 1)] * k, {0: list(range(k)), 1: list(reversed(range(k)))}


def tripled(G, k=3):
    n, E, rot = G
    ne, idx = [], {}
    for e, (u, v) in enumerate(E):
        idx[e] = list(range(len(ne), len(ne) + k))
        ne += [(u, v)] * k
    return n, ne, {v: [x for e in rot[v] for x in (idx[e] if E[e][0] == v else idx[e][::-1])] for v in range(n)}


def subdivided(G):
    n, E, rot = G
    ne = [x for e, (u, v) in enumerate(E) for x in ((u, n + e), (n + e, v))]
    nrot = {v: [2 * e if E[e][0] == v else 2 * e + 1 for e in rot[v]] for v in range(n)}
    nrot.update({n + e: [2 * e, 2 * e + 1] for e in range(len(E))})
    return n + len(E), ne, nrot


def gadget_substitute(H, k):
    """replace every edge (u, v) of H by k parallel copies of S(e, P(e, S(e, e))): u-a, a-v, a-b, b-v per copy"""
    n, E, rot = H
    N, ne = n, []
    at_tail, at_head, inner = {}, {}, {}
    for e, (u, v) in enumerate(E):
        at_tail[e], at_head[e] = [], []
        for j in range(k):
            a, b = N, N + 1
            N += 2
            i0 = len(ne)
            ne += [(u, a), (a, v), (a, b), (b, v)]
            at_tail[e].append(i0)
            at_head[e].append([i0 + 3, i0 + 1])            # seen from v: b-v before a-v
            inner[a] = [i0 + 1, i0 + 2, i0]                # ccw at a: towards v, towards b, towards u
            inner[b] = [i0 + 3, i0 + 2]
    nrot = {}
    for v in range(n):
        nrot[v] = []
        for e in rot[v]:
            if E[e][0] == v:
                nrot[v].extend(at_tail[e])
            else:
                nrot[v].extend(x for pair in reversed(at_head[e]) for x in pair)
    nrot.update(inner)
    return N, ne, nrot


# ------------------------------------------------------------------------------------------- diagrams from ports and corners
def alternating_diagram(n, edges, rot):
    """ports (e, v, +-); the corner at v joins (e, v, +) to (succ_v(e), v, -); strand (e,u,+)-(e,w,+) over, (e,u,-)-(e,w,-) under.
    Returns signed Gauss codes, one per component: (crossing, over?, sign)."""
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
    dirs = {(e, ov): d for comp in comps for e, ov, d in comp}
    return [[(e, ov, 1 if dirs[(e, True)] == dirs[(e, False)] else -1) for e, ov, d in comp] for comp in comps]


def wirtinger(codes):
    """arcs, crossings (over, in, out, sign) in traversal order, component by component"""
    arcs, cr = 0, []
    for code in codes:
        k = max(i for i, x in enumerate(code) if not x[1])
        code = code[k + 1:] + code[:k + 1]
        U = sum(1 for x in code if not x[1])
        over, sign, order, a = {}, {}, [], 0
        for c, ov, s in code:
            sign[c] = s
            if ov:
                over[c] = a
            else:
                order.append((c, a, (a + 1) % U))
                a += 1
        cr.append([(c, arcs + i, arcs + j, sign[c]) for c, i, j in order])
        arcs += U
        for c in over:
            pass
    # over arcs may lie on other components: resolve after all components are numbered
    return arcs, cr


def wirtinger_full(codes):
    base, over_arc, comps = 0, {}, []
    for code in codes:
        k = max(i for i, x in enumerate(code) if not x[1])
        code = code[k + 1:] + code[:k + 1]
        U = sum(1 for x in code if not x[1])
        a, order = 0, []
        for c, ov, s in code:
            if ov:
                over_arc[c] = base + a
            else:
                order.append((c, base + a, base + (a + 1) % U, s))
                a += 1
        comps.append(order)
        base += U
    return base, [[(over_arc[c], i, j, s) for c, i, j, s in order] for order in comps]


def pairing(g):
    """the pairing of {0,1,2,3} preserved by the transposition g: its image in S4/V4"""
    p = ELEMS[g]
    return next(i for i, ((a, b), (c, d)) in enumerate(PAIRS)
                if {frozenset((p[a], p[b])), frozenset((p[c], p[d]))} == {frozenset((a, b)), frozenset((c, d))})


PAIRS = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
OVER_LABEL = {}                                  # labels of transpositions over each pairing
for _g in TRANSP:
    OVER_LABEL.setdefault(pairing(_g), []).append(_g)
# the label of a conjugate depends only on the labels (V4 is normal); read it off the table, checking independence of choices
LAB_CONJ = {}
for _x in TRANSP:
    for _o in TRANSP:
        key, val_ = (pairing(_x), pairing(_o)), pairing(CONJ[_x][_o])
        assert LAB_CONJ.setdefault(key, val_) == val_


def _enumerate(flat, na, choices, step):
    """generic traversal-order enumeration: choices(arc) lists candidate values, step(in, over) the out value"""
    val = [None] * na
    sols = []

    def rec(k):
        if k == len(flat):
            sols.append(tuple(val))
            return
        o, i, j, s = flat[k]
        if val[i] is None:
            for x in choices(i):
                val[i] = x
                rec(k)
            val[i] = None
            return
        for x in ([val[o]] if val[o] is not None else choices(o)):
            new_o = val[o] is None
            if new_o:
                val[o] = x
            nv = step(val[i], x)
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
    return sols


def count_transposition_colourings(codes):
    """brute-force enumeration in two layers: all colourings by the three pairings (images in S4/V4), then over each one all
    choices of one of the two transpositions above every arc; no linear algebra, potentials or bicycle spaces are used"""
    na, comps = wirtinger_full(codes)
    flat = [x for comp in comps for x in comp]
    labellings = _enumerate(flat, na, lambda a: (0, 1, 2), lambda i, o: LAB_CONJ[(i, o)])
    total = 0
    for lab in labellings:
        total += len(_enumerate(flat, na, lambda a: OVER_LABEL[lab[a]], lambda i, o: CONJ[i][o]))
    return total


# ------------------------------------------------------------------------------------------------------------ graph algebra
def n_components(n, E):
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    c = n
    for u, v in E:
        a, b = f(u), f(v)
        if a != b:
            par[a] = b
            c -= 1
    return c


def f2_basis(vectors):
    basis = []
    for x in vectors:
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return basis


def bicycle_dim(n, E):
    """dim of (cut space) ∩ (cut space)^perp = cut-space dimension minus the rank of its Gram matrix over F2"""
    stars = [sum(1 << i for i, (a, b) in enumerate(E) if (a == v) != (b == v)) for v in range(n)]
    basis = f2_basis(stars)
    gram = [sum(1 << j for j, b in enumerate(basis) if bin(a & b).count("1") % 2) for a in basis]
    return len(basis) - len(f2_basis(gram))


def bareiss(M):
    M = [r[:] for r in M]
    n = len(M)
    if n == 0:
        return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if M[i][k]), None)
            if sw is None:
                return 0
            M[k], M[sw] = M[sw], M[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def spanning_trees(n, E):
    L = [[0] * n for _ in range(n)]
    for u, v in E:
        if u != v:
            L[u][u] += 1
            L[v][v] += 1
            L[u][v] -= 1
            L[v][u] -= 1
    return bareiss([r[1:] for r in L[1:]])


def diagram_determinant(codes):
    na, comps = wirtinger_full(codes)
    rows = []
    for comp in comps:
        for o, i, j, s in comp:
            r = [0] * na
            r[o] += 2
            r[i] -= 1
            r[j] -= 1
            rows.append(r)
    return abs(bareiss([r[1:] for r in rows[1:]]))


def subset_sum(n, E, weight):
    return sum(weight(n_components(n, [E[i] for i in range(len(E)) if mask >> i & 1]), bin(mask).count("1"))
               for mask in range(1 << len(E)))


def potts(n, E, q, v):
    return subset_sum(n, E, lambda c, a: Fraction(q) ** c * Fraction(v) ** a)


def chromatic(n, E, q):
    return subset_sum(n, E, lambda c, a: (-1) ** a * q ** c)


def bicycle_sum(n, E):
    return sum(2 ** (n_components(n, H) + bicycle_dim(n, H))
               for phi in itertools.product(range(3), repeat=n) for H in [[(u, v) for u, v in E if phi[u] == phi[v]]])


# --------------------------------------------------------------------------------------------------------- twelve states
STATES = [(t, p, x) for t in (0, 1) for p in range(3) for x in (0, 1)]
NU = [STATES.index((1 - t, p, 1 - x)) for (t, p, x) in STATES]
M12 = [[1 - 2 * (NU[a] == b) for b in range(12)] for a in range(12)]


def twelve_state_sum(n, E, mat=M12):
    tot = 0
    for z in itertools.product(range(12), repeat=n):
        prod = 1
        for u, v in E:
            prod *= mat[z[u]][z[v]]
            if prod == 0:
                break
        tot += prod
    return Fraction(tot, 2 ** n)


def gadget_matrix():
    """sum over the internal states (a, b) of S(e, P(e, S(e, e))) = edges s-a, a-t, a-b, b-t"""
    return [[sum(M12[s][a] * M12[a][t] * M12[a][b] * M12[b][t] for a in range(12) for b in range(12)) for t in range(12)]
            for s in range(12)]


def pg_counts(n, E):
    """N_ij: number of z in Z12^V with i edges z_u = z_v and j edges z_v = nu(z_u)"""
    out = {}
    for z in itertools.product(range(12), repeat=n):
        i = sum(z[u] == z[v] for u, v in E)
        j = sum(z[v] == NU[z[u]] for u, v in E)
        out[(i, j)] = out.get((i, j), 0) + 1
    return out


# -------------------------------------------------------------------------------------------------------------- the main
def named_graphs():
    return {
        "edge": (2, [(0, 1)], {0: [0], 1: [0]}),
        "path": (3, [(0, 1), (1, 2)], {0: [0], 1: [0, 1], 2: [1]}),
        "C3": cyc(3), "C4": cyc(4), "C5": cyc(5), "theta2": theta(2), "theta3": theta(3),
        "K4": plane([(0, 0), (2, 0), (1, 2), (1, 0.7)], [(0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3)]),
        "diamond": plane([(0, 0), (1, 1), (1, -1), (2, 0)], [(0, 1), (1, 3), (3, 2), (2, 0), (1, 2)]),
        "triangle+pendant": plane([(0, 0), (2, 0), (1, 1.5), (1, 3)], [(0, 1), (1, 2), (2, 0), (2, 3)]),
        "C4+2 pendants": plane([(0, 0), (1, 0), (1, 1), (0, 1), (2, 1), (-1, 0)],
                               [(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (0, 5)]),
    }


def random_plane_graphs(count, rng, max_edges):
    out, tries = {}, 0
    while len(out) < count and tries < 10000:
        tries += 1
        pts = [(x, y) for y in range(3) for x in range(3)]
        E = [(pts.index((x, y)), pts.index((x + dx, y + dy))) for (x, y) in pts for dx, dy in ((1, 0), (0, 1), (1, -1))
             if (x + dx, y + dy) in pts and rng.random() < 0.5]
        used = sorted({v for e in E for v in e})
        if not E or len(E) > max_edges:
            continue
        rel = {v: i for i, v in enumerate(used)}
        E2 = [(rel[a], rel[b]) for a, b in E]
        if n_components(len(used), E2) != 1:
            continue
        out[f"random {len(out)} ({len(used)} vertices, {len(E2)} edges)"] = plane([pts[v] for v in used], E2)
    return out


def main():
    t0 = time.time()
    out, ok_all = {}, True
    rng = random.Random(20261025)
    graphs = named_graphs()
    graphs.update(random_plane_graphs(8, rng, 8))

    # part 1: diagrams
    p1, ok1 = {}, True
    for name, (n, E, rot) in graphs.items():
        codes = alternating_diagram(n, E, rot)
        alt = all(code[i][1] != code[(i + 1) % len(code)][1] for code in codes for i in range(len(code)))
        r = {"alternates": alt, "components": len(codes), "1 + dim B": 1 + bicycle_dim(n, E),
             "determinant": diagram_determinant(codes), "spanning trees": spanning_trees(n, E)}
        r["ok"] = alt and r["components"] == r["1 + dim B"] and r["determinant"] == r["spanning trees"]
        p1[name] = r
        ok1 &= r["ok"]
    out["1_diagrams"] = {"rows": p1, "ok": ok1}
    print(f"part 1 diagrams: {sum(r['ok'] for r in p1.values())}/{len(p1)} ok ({time.time() - t0:.0f} s)", flush=True)
    ok_all &= ok1

    # part 2: bicycle law and twelve states on tripled graphs
    p2, ok2 = {}, True
    for name, G in graphs.items():
        n, E, rot = G
        if n > 7:
            continue
        codes = alternating_diagram(*tripled(G))
        col = count_transposition_colourings(codes)
        law = bicycle_sum(n, E)
        twelve = twelve_state_sum(n, E)
        r = {"components": len(codes), "brute force": col, "bicycle law": law, "twelve-state": str(twelve),
             "ok": col == law == twelve}
        p2[name] = r
        ok2 &= r["ok"]
        print(f"part 2 {name}: {col} vs law {law} vs 12-state {twelve} {'ok' if r['ok'] else 'FAIL'} ({time.time() - t0:.0f} s)",
              flush=True)
    out["2_bicycle_law"] = {"rows": p2, "ok": ok2}
    ok_all &= ok2

    # part 3: links (subdivided)
    p3, ok3 = {}, True
    for name in ("edge", "path", "theta2", "C3", "theta3", "C4"):
        G = graphs[name]
        n, E, rot = G
        Gs = subdivided(G)
        codes = alternating_diagram(*tripled(Gs))
        col = count_transposition_colourings(codes)
        pred = Fraction(4) ** len(E) * potts(n, E, 12, Fraction(1, 2)) / Fraction(2) ** n
        beta1 = len(E) - n + 1
        r = {"brute force": col, "2^-n 4^m Z(G;12,1/2)": str(pred), "components": len(codes), "1 + beta1": 1 + beta1,
             "ok": col == pred and len(codes) == 1 + beta1}
        p3[name] = r
        ok3 &= r["ok"]
        print(f"part 3 {name}: {col} vs {pred}, components {len(codes)} {'ok' if r['ok'] else 'FAIL'} ({time.time() - t0:.0f} s)",
              flush=True)
    out["3_links"] = {"rows": p3, "ok": ok3}
    ok_all &= ok3

    # part 4: gadgets and knots
    MG = gadget_matrix()
    J = [[1] * 12 for _ in range(12)]
    expect = [[68 * J[a][b] + 32 * (a == b) - 8 * (NU[a] == b) for b in range(12)] for a in range(12)]
    p4 = {"gadget matrix = 68J + 32I - 8N": MG == expect}
    ok4 = p4["gadget matrix = 68J + 32I - 8N"]
    knots_ok = True
    for hname in ("edge", "path", "C3"):
        H = graphs[hname]
        for k in (1, 2, 3):
            N, E2, R2 = gadget_substitute(H, k)
            comps = len(alternating_diagram(*tripled((N, E2, R2))))
            knots_ok &= (comps == 1) == (k % 2 == 1)
    p4["odd powers give knots, even powers links (hosts edge, path, C3)"] = knots_ok
    ok4 &= knots_ok
    rows = {}
    for hname, k in (("edge", 1), ("edge", 3), ("path", 1), ("C3", 1)):
        H = graphs[hname]
        n, E, rot = H
        N, E2, R2 = gadget_substitute(H, k)
        codes = alternating_diagram(*tripled((N, E2, R2)))
        col = count_transposition_colourings(codes)
        Nco = pg_counts(n, E)
        b1, g1 = Fraction(25, 17), Fraction(15, 17)
        pred = Fraction(68) ** (k * len(E)) * sum(c * (b1 ** i * g1 ** j) ** k for (i, j), c in Nco.items()) / Fraction(2) ** N
        rows[f"{hname}, k={k}"] = {"knot": len(codes) == 1, "brute force": col, "prediction": str(pred), "ok": col == pred and len(codes) == 1}
        ok4 &= rows[f"{hname}, k={k}"]["ok"]
        print(f"part 4 {hname} k={k}: {col} vs {pred} {'ok' if col == pred else 'FAIL'} ({time.time() - t0:.0f} s)", flush=True)
    p4["end-to-end"] = rows
    p4["ok"] = ok4
    out["4_gadgets"] = p4
    ok_all &= ok4

    # part 5: interpolation
    p5, ok5 = {}, True
    for hname in ("K4", "C5", "diamond"):
        n, E, rot = graphs[hname]
        # spanning tree by BFS, then double the other edges (planar: parallel copy next to the original)
        seen, tree = {0}, set()
        frontier = [0]
        while frontier:
            u = frontier.pop()
            for e, (a, b) in enumerate(E):
                if u in (a, b):
                    w = b if a == u else a
                    if w not in seen:
                        seen.add(w)
                        tree.add(e)
                        frontier.append(w)
        Ed, rotd, cnt = [], {v: [] for v in range(n)}, {}
        for e, (a, b) in enumerate(E):
            cnt[e] = [len(Ed)] if e in tree else [len(Ed), len(Ed) + 1]
            Ed += [(a, b)] * len(cnt[e])
        for v in range(n):
            for e in rot[v]:
                rotd[v].extend(cnt[e] if E[e][0] == v else cnt[e][::-1])
        tau = spanning_trees(n, Ed)
        P0, Pd = chromatic(n, E, 12), chromatic(n, Ed, 12)
        Nco = pg_counts(n, Ed)
        m2 = len(Ed)
        cand = [(i, j) for i in range(m2 + 1) for j in range(m2 + 1 - i)]
        b1, g1 = Fraction(25, 17), Fraction(15, 17)
        bases = [b1 ** i * g1 ** j for i, j in cand]
        distinct = len(set(bases)) == len(bases)
        K = len(cand)
        A = [[bb ** k for bb in bases] + [sum(c * (b1 ** i * g1 ** j) ** k for (i, j), c in Nco.items())]
             for k in range(1, 2 * K, 2)]
        for c in range(K):
            pr = next(i for i in range(c, K) if A[i][c] != 0)
            A[c], A[pr] = A[pr], A[c]
            inv = 1 / A[c][c]
            A[c] = [x * inv for x in A[c]]
            for i in range(K):
                if i != c and A[i][c] != 0:
                    f = A[i][c]
                    A[i] = [x - f * y for x, y in zip(A[i], A[c])]
        recovered = sum(A[idx][K] for idx, (i, j) in enumerate(cand) if i == 0)
        knots = [len(alternating_diagram(*tripled(gadget_substitute((n, Ed, rotd), k)))) for k in (1, 3)]
        r = {"trees of doubled graph": tau, "P(H,12)": P0, "P(doubled,12)": Pd, "bases distinct": distinct,
             "recovered": str(recovered), "components for k = 1, 3": knots,
             "ok": tau % 2 == 1 and P0 == Pd and distinct and recovered == P0 and knots == [1, 1]}
        p5[hname] = r
        ok5 &= r["ok"]
        print(f"part 5 {hname}: tau {tau}, P(H,12) {P0}, recovered {recovered}, knots {knots} {'ok' if r['ok'] else 'FAIL'} "
              f"({time.time() - t0:.0f} s)", flush=True)
    out["5_interpolation"] = {"rows": p5, "ok": ok5}
    ok_all &= ok5

    # part 6: controls
    c = {}
    n, E, rot = graphs["C4+2 pendants"]
    no_bicycle = sum(2 ** n_components(n, [(u, v) for u, v in E if phi[u] == phi[v]]) for phi in itertools.product(range(3), repeat=n))
    c["law without the bicycle term fails on C4 + 2 pendants"] = no_bicycle != p2["C4+2 pendants"]["brute force"]
    n, E, rot = graphs["C3"]
    colC3 = p3["C3"]["brute force"]
    c["wrong Potts parameters rejected"] = all(colC3 != Fraction(4) ** len(E) * potts(n, E, q, v) / Fraction(2) ** n
                                               for q, v in ((6, Fraction(1, 2)), (12, Fraction(-1, 2)), (12, 1)))
    wrong = [[68 * J[a][b] + 32 * (a == b) + 8 * (NU[a] == b) for b in range(12)] for a in range(12)]
    c["wrong gadget matrix rejected"] = MG != wrong
    ok6 = all(c.values())
    out["6_controls"] = {"rows": c, "ok": ok6}
    print("part 6 controls:", c, flush=True)
    ok_all &= ok6

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "CLOSED-H1-20261025-001A-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
