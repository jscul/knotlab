"""End-to-end gadget instances: search Borromean insertion windows on a base knot for a configuration equal to a gadget up to a
change of basis, then compare the knot's obstruction kernels with the prediction and its count with the gadget value."""
import itertools
import math
import cp_lib as C


def potts(n, edges, Q, v):
    return sum(math.prod(1 + v * (s[a] == s[b]) for a, b in edges) for s in itertools.product(range(Q), repeat=n))


def window_data(G, word, n, k):
    p = G.p
    U, rels, arc = C.presentation(word, n, G.r)
    gam = pow(G.a * G.b % p, p - 2, p)
    H3 = [C.cohomology(U, rels, z, 1, p)[0] for z in (G.a, G.b, gam)]
    data = [((L, o), C.leaf_sets(G, H3, arc, [L], [o], k)[0]) for L in range(len(word)) for o in range(n - 3 * k + 1)]
    return data, [len(h) for h in H3]


def two_form(lam_a, mu_b, lam_c, p):
    """if the middle functionals are proportional to one s, the insertion's form is s (x) omega with omega alternating; returns
    (s, omega) or None"""
    nz = [mv for mv in mu_b if any(mv)]
    if not nz:
        return None
    s = nz[0]
    i0 = next(t for t in range(len(s)) if s[t])
    coef = []
    for mv in mu_b:
        c = mv[i0] * pow(s[i0], p - 2, p) % p
        if any((mv[t] - c * s[t]) % p for t in range(len(s))):
            return None
        coef.append(c)
    d = len(lam_a[0])
    om = [[0] * d for _ in range(d)]
    for (s1, s2, s3), sg in C.PERMS:
        if coef[s2]:
            for i in range(d):
                for j in range(d):
                    om[i][j] = (om[i][j] + sg * coef[s2] * lam_a[s1][i] * lam_c[s3][j]) % p
    return s, om


def run_case(G, summands, k, mode, graph_n, graph_m, graph):
    """mode 'alt3': all characters equal, gadget = alternating 3-form on the digon (two spans meeting in a line);
    'case4': x = test character, triangle; 'case2': x = y character, triangle (planes pairwise spanning 4, all three 5)"""
    p = G.p
    word, n = C.connected_sum(summands)
    data, dims = window_data(G, word, n, k)
    found = None
    if mode == "alt3":
        sp = [(w, C.rref([list(v) for v in ls[0]], p)[0]) for w, ls in data]
        sp = [(w, s) for w, s in sp if len(s) == 3]
        for (w1, s1), (w2, s2) in itertools.combinations(sp, 2):
            if w1[0] != w2[0] and C.rank(s1 + s2, p) == 5:
                found = [w1, w2]
                break
        expect = p ** (2 * graph_m - graph_n) * potts(graph_n, graph, p ** 3, p * p - 1)
    else:
        items = []
        for w, ls in data:
            tf = two_form(ls[0], ls[1], ls[2], p) if mode == "case4" else two_form(ls[0], ls[2], ls[1], p)
            if tf and C.rank(tf[1], p) == 2:
                items.append((w, tf[0], C.rref(tf[1], p)[0]))
        for (w1, s1, P1), (w2, s2, P2), (w3, s3, P3) in itertools.combinations(items, 3):
            if len({w1[0], w2[0], w3[0]}) < 3 or C.rank([s1, s2, s3], p) < 3:
                continue
            if (C.rank(P1 + P2, p), C.rank(P1 + P3, p), C.rank(P2 + P3, p), C.rank(P1 + P2 + P3, p)) == (4, 4, 4, 5):
                found = [w1, w2, w3]
                break
        expect = (p ** (graph_m - graph_n) if mode == "case4" else p ** graph_m) * potts(graph_n, graph, p * p, p - 1)
    if not found:
        return {"strands": n, "dims": dims, "configuration": None, "ok": False}
    r = C.steer_test(G, word, n, found, k)
    return {"strands": n, "dims (x, y, test)": dims, "configuration (level, offset)": found, "generators": r["U"], "N": r["N"],
            "gadget value": expect, "mismatching a": r["mismatches"][1], "ok": r["N"] == expect and r["mismatches"][1] == 0}
