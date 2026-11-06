"""Check for DICHOTOMY-3D-20261025-001A-P001: root fillings separate the order-16 collision.

Standard library only. The closed doubles, their faces and the mirror-label propagation come from the check of
HARD-3D-20261025-001B (loaded by path). Parts:
  1. the model: mirror-label consistency equals per-edge commutation, and parallel copies carrying different gadgets
     (fin, root fillings) collapse to the convolution of their weights;
  2. closed counts with k fins and one doubled root filling per edge, fitted in k: the top coefficient equals the
     chromatic identity of the index-p theorem (the order-16 dihedral group and its relatives, p = 2 and p = 3);
  3. the trivial-action cases with fins alone (all non-abelian anyons of dimension p; fluxes outside A for p = 3);
  4. the index-p data of every group used;
  5. controls.
Writes result.json next to this file."""
import importlib.util
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_B = ROOT / "proofs/HARD-3D-20261025-001B/HARD-3D-20261025-001B-P001_closed_doubles_count_pairs_of_colourings/check.py"
_spec = importlib.util.spec_from_file_location("hard3d_closed_doubles_check", _B)
HB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HB)
GRAPHS = HB.GRAPHS


# ------------------------------------------------------------------------------------------------------------------ groups
class Group:
    def __init__(self, name, els, mul):
        self.name = name
        self.els = list(els)
        self.n = len(self.els)
        ix = {g: i for i, g in enumerate(self.els)}
        self.M = [[ix[mul(a, b)] for b in self.els] for a in self.els]
        self.e = next(i for i in range(self.n) if all(self.M[i][j] == j for j in range(self.n)))
        self.I = [next(j for j in range(self.n) if self.M[i][j] == self.e) for i in range(self.n)]
        self.C = [[b for b in range(self.n) if self.M[a][b] == self.M[b][a]] for a in range(self.n)]
        self.Z = [a for a in range(self.n) if len(self.C[a]) == self.n]

    def pw(self, a, k):
        x = self.e
        for _ in range(k):
            x = self.M[x][a]
        return x

    def conj(self, h, a):
        return self.M[self.M[h][a]][self.I[h]]

    # adapter for the HARD-3D-20261025-001B propagation code
    def adapter(self):
        class A:
            pass
        a = A()
        a.els = list(range(self.n))
        a.e = self.e
        a.mul = lambda x, y: self.M[x][y]
        a.inv = lambda x: self.I[x]
        return a


def metacyclic(m, r, n, name):
    assert pow(r, n, m) == 1 % m
    els = [(x, y) for y in range(n) for x in range(m)]
    return Group(name, els, lambda a, b: ((a[0] + pow(r, a[1], m) * b[0]) % m, (a[1] + b[1]) % n))


def dicyclic(N, name):
    els = [(k, j) for j in (0, 1) for k in range(2 * N)]

    def mul(a, b):
        (k1, j1), (k2, j2) = a, b
        if j1 == 0:
            return ((k1 + k2) % (2 * N), j2)
        if j2 == 0:
            return ((k1 - k2) % (2 * N), 1)
        return ((k1 - k2 + N) % (2 * N), 0)
    return Group(name, els, mul)


def alternating4():
    els = [p for p in itertools.permutations(range(4))
           if sum(1 for i in range(4) for j in range(i + 1, 4) if p[i] > p[j]) % 2 == 0]
    return Group("A4", els, lambda p, q: tuple(p[q[i]] for i in range(4)))


def z3_wreath_z3():
    els = [(a, b, c, s) for s in range(3) for a in range(3) for b in range(3) for c in range(3)]

    def mul(x, y):
        v = y[:3]
        for _ in range(x[3]):
            v = (v[2], v[0], v[1])
        return ((x[0] + v[0]) % 3, (x[1] + v[1]) % 3, (x[2] + v[2]) % 3, (x[3] + y[3]) % 3)
    return Group("Z3 wr Z3", els, mul)


# ----------------------------------------------------------------------------------------------------------------- weights
def w_fin(Gr):
    """W(lam, mu) = #{(tau, kappa) in C(lam)^2 : [tau, kappa] = mu}, as rows indexed by mu"""
    M, I = Gr.M, Gr.I
    rows = []
    for lam in range(Gr.n):
        row = [0] * Gr.n
        C = Gr.C[lam]
        for t in C:
            for k in C:
                row[M[M[M[t][k]][I[t]]][I[k]]] += 1
        rows.append(row)
    return rows


def w_root(Gr, p, sign):
    """Dehn filling of a parallel copy along lambda mu^(-sign p): W(lam, mu) = [lam = mu^(sign p)]"""
    rows = []
    for lam in range(Gr.n):
        row = [0] * Gr.n
        for mu in Gr.C[lam]:
            x = Gr.pw(mu, p)
            if sign < 0:
                x = Gr.I[x]
            if x == lam:
                row[mu] = 1
        rows.append(row)
    return rows


def identity(Gr):
    return [[1 if mu == Gr.e else 0 for mu in range(Gr.n)] for lam in range(Gr.n)]


def conv(Gr, f, g):
    """(f * g)(lam, mu) = sum over x in C(lam) of f(lam, x) g(lam, x^-1 mu): the digon collapse of two parallel copies"""
    M, I = Gr.M, Gr.I
    out = []
    for lam in range(Gr.n):
        C = Gr.C[lam]
        fr, gr = f[lam], g[lam]
        row = [0] * Gr.n
        for mu in C:
            row[mu] = sum(fr[x] * gr[M[I[x]][mu]] for x in C if fr[x])
        out.append(row)
    return out


def edge_weight(Gr, k, extra=()):
    W = identity(Gr)
    for X in extra:
        W = conv(Gr, W, X)
    F = w_fin(Gr)
    for _ in range(k):
        W = conv(Gr, W, F)
    return W


# ------------------------------------------------------------------------------------------------------------ closed counts
def faces_and_sides(edges, rot):
    F = HB.faces_of(edges, rot)
    side = {d: fi for fi, face in enumerate(F) for v, d in face}
    outer = max(range(len(F)), key=lambda i: len(F[i]))
    return F, side, outer


def closed(Gr, graph, W):
    """sum over y in G^V and face labels s (outer face pinned to e) of prod_e W(y_v^-1 y_u, s_f' s_f^-1); y_0 pinned and
    multiplied by |G| (left translation of y fixes every lambda and mu)"""
    n, edges, rot = graph
    F, side, outer = faces_and_sides(edges, rot)
    bounded = [f for f in range(len(F)) if f != outer]
    E = [(u, v, side[(e, 0)], side[(e, 1)]) for e, (u, v) in enumerate(edges)]
    M, I, e0 = Gr.M, Gr.I, Gr.e
    tot = 0
    for yr in itertools.product(range(Gr.n), repeat=n - 1):
        y = (e0,) + yr
        rows = [W[M[I[y[v]]][y[u]]] for (u, v, f0, f1) in E]
        s = [e0] * len(F)
        for sig in itertools.product(range(Gr.n), repeat=len(bounded)):
            for f, x in zip(bounded, sig):
                s[f] = x
            w = 1
            for (u, v, f0, f1), r in zip(E, rows):
                w *= r[M[s[f1]][I[s[f0]]]]
                if not w:
                    break
            tot += w
    return tot * Gr.n


def closed_propagated(Gr, graph, copy_weights):
    """the same count over the configurations of HARD-3D-20261025-001B (mirror labels propagated, nothing pinned), with
    one weight per edge"""
    n, edges, rot = graph
    A = Gr.adapter()
    tot = 0
    for y, s, side in HB.configurations(A, n, edges, rot):
        w = 1
        for e, (u, v) in enumerate(edges):
            lam = Gr.M[Gr.I[y[v]]][y[u]]
            mu = Gr.M[s[side[(e, 1)]]][Gr.I[s[side[(e, 0)]]]]
            w *= copy_weights[e][lam][mu]
            if not w:
                break
        tot += w
    return tot


def chromatic(graph, q):
    n, edges, rot = graph
    tot = 0
    for r in range(len(edges) + 1):
        for S in itertools.combinations(range(len(edges)), r):
            par = list(range(n))

            def find(x):
                while par[x] != x:
                    par[x] = par[par[x]]
                    x = par[x]
                return x
            k = n
            for i in S:
                a, b = find(edges[i][0]), find(edges[i][1])
                if a != b:
                    par[a] = b
                    k -= 1
            tot += (-1) ** r * Fraction(q) ** k
    return tot


def fit_top(counts, bases):
    """solve counts[k] = sum_j c_j bases[j]^k with the first len(bases) values; return (c, consistency of the rest)"""
    K = len(bases)
    rows = [[Fraction(b) ** k for b in bases] for k in range(K)]
    c = HB.solve(rows, [Fraction(x) for x in counts[:K]])
    rest = all(sum(cj * Fraction(b) ** k for cj, b in zip(c, bases)) == counts[k] for k in range(K, len(counts)))
    return c, rest


# ------------------------------------------------------------------------------------------------------------- index-p data
def index_p_data(Gr, A, sigma, p):
    """A: set of element indices (abelian normal of index p); sigma outside A"""
    M, I = Gr.M, Gr.I
    assert Gr.n == p * len(A)
    assert all(M[a][b] == M[b][a] for a in A for b in A)
    assert all(Gr.conj(h, a) in A for h in range(Gr.n) for a in A)
    assert sigma not in A
    pA = sorted({Gr.pw(a, p) for a in A})
    Ap = [a for a in A if Gr.pw(a, p) == Gr.e]
    comm_pA = sorted({M[I[x]][Gr.conj(sigma, x)] for x in pA})
    comm_A = sorted({M[I[x]][Gr.conj(sigma, x)] for x in A})
    return {"order": Gr.n, "p": p, "|A|": len(A), "|pA|": len(pA), "|A[p]|": len(Ap), "|[pA,G]|": len(comm_pA),
            "|[A,G]|": len(comm_A), "|Z|": len(Gr.Z)}


def case_of(d):
    if d["|[pA,G]|"] > 1:
        return "a"
    if d["|[A,G]|"] == d["p"]:
        return "b1"
    if d["p"] >= 3:
        return "b2"
    return "b3"


def derived_order(Gr):
    M, I = Gr.M, Gr.I
    S = {Gr.e}
    gens = {M[M[M[a][b]][I[a]]][I[b]] for a in range(Gr.n) for b in range(Gr.n)}
    frontier = [Gr.e]
    while frontier:
        new = []
        for x in frontier:
            for g in gens:
                y = M[x][g]
                if y not in S:
                    S.add(y)
                    new.append(y)
        frontier = new
    return len(S)


def predicted(Gr, d, graph, m):
    """the predicted top coefficient for the case of the index-p theorem"""
    n = graph[0]
    c = case_of(d)
    if c == "a":
        q = d["|[pA,G]|"] ** 2
        L = Fraction(d["|pA|"] ** 2, q)
        rho = d["|A[p]|"] ** 2
        return q, rho ** m * Fraction(Gr.n, d["|pA|"]) * d["|A[p]|"] * (L / d["|A|"]) ** n * chromatic(graph, q)
    if c == "b1":
        Gp = derived_order(Gr)
        q = (Gr.n // d["|Z|"]) * Gp
        return q, Fraction(d["|Z|"], Gp) ** n * chromatic(graph, q)
    if c == "b2":
        q = d["p"]
        return q, Fraction(d["|A|"]) ** n * chromatic(graph, q)
    raise ValueError("case b3 is not covered")


def bases_for(Gr, d, m):
    """products over the m edges of the per-edge fin factors |G|^2/dim^2 that surviving channels can carry: dimensions 1 and p
    in cases a and b1, and 1, p and |[A,G]| in case b2"""
    dims = [1, d["p"]] if case_of(d) in ("a", "b1") else [1, d["p"], d["|[A,G]|"]]
    factors = [(Gr.n // x) ** 2 for x in dims]
    vals = set()
    for combo in itertools.combinations_with_replacement(factors, m):
        prod = 1
        for x in combo:
            prod *= x
        vals.add(prod)
    return sorted(vals)


# --------------------------------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    out = {"parts": {}}
    ok_all = True

    # groups
    D16 = metacyclic(8, 7, 2, "D16")
    Q16 = dicyclic(4, "Q16")
    SD16 = metacyclic(8, 3, 2, "SD16")
    D32 = metacyclic(16, 15, 2, "D32")
    DIC12 = metacyclic(3, 2, 4, "Dic12 = Z3 x| Z4")
    Z7Z3 = metacyclic(7, 2, 3, "Z7 x| Z3")
    A4 = alternating4()
    D8 = metacyclic(4, 3, 2, "D8")
    M16 = metacyclic(8, 5, 2, "M16")
    WR = z3_wreath_z3()
    S3 = metacyclic(3, 2, 2, "S3")

    def cyc_A(Gr, gen_pred):
        return {i for i, g in enumerate(Gr.els) if gen_pred(g)}
    A_of = {
        "D16": (cyc_A(D16, lambda g: g[1] == 0), D16.els.index((0, 1)), 2),
        "Q16": (cyc_A(Q16, lambda g: g[1] == 0), Q16.els.index((0, 1)), 2),
        "SD16": (cyc_A(SD16, lambda g: g[1] == 0), SD16.els.index((0, 1)), 2),
        "D32": (cyc_A(D32, lambda g: g[1] == 0), D32.els.index((0, 1)), 2),
        "Dic12 = Z3 x| Z4": (cyc_A(DIC12, lambda g: g[1] % 2 == 0), DIC12.els.index((0, 1)), 2),
        "Z7 x| Z3": (cyc_A(Z7Z3, lambda g: g[1] == 0), Z7Z3.els.index((0, 1)), 3),
        "A4": (cyc_A(A4, lambda g: all(g[g[i]] == i for i in range(4))), A4.els.index((1, 2, 0, 3)), 3),
        "D8": (cyc_A(D8, lambda g: g[1] == 0), D8.els.index((0, 1)), 2),
        "M16": (cyc_A(M16, lambda g: g[1] == 0), M16.els.index((0, 1)), 2),
        "Z3 wr Z3": (cyc_A(WR, lambda g: g[3] == 0), WR.els.index((0, 0, 0, 1)), 3),
    }
    groups = {G_.name: G_ for G_ in (D16, Q16, SD16, D32, DIC12, Z7Z3, A4, D8, M16, WR)}

    # ---------------------------------------------------------------- part 4 first: index-p data (used by parts 2, 3)
    data = {}
    for name, (A, sig, p) in A_of.items():
        data[name] = index_p_data(groups[name], A, sig, p)
        data[name]["case"] = case_of(data[name])
    expect_case = {"D16": "a", "Q16": "a", "SD16": "a", "D32": "a", "Dic12 = Z3 x| Z4": "a", "Z7 x| Z3": "a", "A4": "a",
                   "D8": "b1", "M16": "b1", "Z3 wr Z3": "b2"}
    p4 = all(data[k]["case"] == v for k, v in expect_case.items())
    # the 2-power families: q = (N/4)^2 for order 2N
    fam = {k: data[k]["|[pA,G]|"] ** 2 for k in ("D16", "Q16", "SD16", "D32")}
    p4 &= fam == {"D16": 4, "Q16": 4, "SD16": 4, "D32": 16}
    out["parts"]["4_index_p_data"] = {"data": data, "ok": p4}
    print("part 4 index-p data:", {k: (v["case"], v["|[pA,G]|"]) for k, v in data.items()}, "ok" if p4 else "FAIL", flush=True)
    ok_all &= p4

    # ---------------------------------------------------------------- part 1: the model
    p1 = {"consistency_equals_commutation": {}, "mixed_digon_collapse": {}}
    ok1 = True
    for Gr in (S3, D8):
        Aad = Gr.adapter()
        for gname in ("single edge", "path", "C3", "theta3", "C4", "diamond", "triangle with pendant"):
            n, edges, rot = GRAPHS[gname]
            F, side, outer = faces_and_sides(edges, rot)
            cons = set()
            for y, s, sd in HB.configurations(Aad, n, edges, rot):
                cons.add((tuple(y), tuple(s[f] for f in range(len(F)) if f != outer)))
            comm = set()
            bounded = [f for f in range(len(F)) if f != outer]
            for y in itertools.product(range(Gr.n), repeat=n):
                for sig in itertools.product(range(Gr.n), repeat=len(bounded)):
                    s = [Gr.e] * len(F)
                    for f, x in zip(bounded, sig):
                        s[f] = x
                    good = True
                    for e, (u, v) in enumerate(edges):
                        lam = Gr.M[Gr.I[y[v]]][y[u]]
                        mu = Gr.M[s[side[(e, 1)]]][Gr.I[s[side[(e, 0)]]]]
                        if Gr.M[lam][mu] != Gr.M[mu][lam]:
                            good = False
                            break
                    if good:
                        comm.add((tuple(y), sig))
            same = cons == comm
            p1["consistency_equals_commutation"][f"{Gr.name} {gname}"] = [len(cons), same]
            ok1 &= same
    # mixed copies: thickened graph with one weight per copy versus the collapsed convolution
    cases = [(S3, "path", 2), (D16, "single edge", 2), (D8, "C3", 2)]
    for Gr, gname, p in cases:
        n, edges, rot = GRAPHS[gname]
        Wf, Wp, Wm = w_fin(Gr), w_root(Gr, p, +1), w_root(Gr, p, -1)
        gadgets = [Wf, Wp, Wm] if gname != "C3" else [Wf, Wp]
        k = len(gadgets)
        ne, nrot = HB.thicken(n, edges, rot, k)
        copy_w = [gadgets[i % k] for i in range(len(ne))]
        full = closed_propagated(Gr, (n, ne, nrot), copy_w)
        Wc = identity(Gr)
        for X in gadgets:
            Wc = conv(Gr, Wc, X)
        collapsed = closed(Gr, (n, edges, rot), Wc)
        p1["mixed_digon_collapse"][f"{Gr.name} {gname} x{k}"] = [full, collapsed, full == collapsed]
        ok1 &= full == collapsed
        print(f"part 1 mixed collapse {Gr.name} {gname} x{k}: {full} vs {collapsed}", flush=True)
    p1["ok"] = ok1
    out["parts"]["1_model"] = p1
    print("part 1 model:", "ok" if ok1 else "FAIL", round(time.time() - t0), "s", flush=True)
    ok_all &= ok1

    # ---------------------------------------------------------------- part 2 and 3: closed counts fitted in the number of fins
    plan = [
        ("D16", ("single edge", "path", "C3", "theta3", "C4", "diamond", "triangle with pendant")),
        ("Q16", ("single edge", "path", "C3", "theta3", "C4")),
        ("SD16", ("single edge", "path", "C3", "theta3", "C4")),
        ("D32", ("single edge", "path", "C3", "theta3", "C4")),
        ("Dic12 = Z3 x| Z4", ("single edge", "path", "C3", "theta3", "C4", "diamond")),
        ("Z7 x| Z3", ("single edge", "path", "C3", "theta3", "C4")),
        ("A4", ("single edge", "path", "C3", "theta3", "C4", "diamond")),
        ("D8", ("single edge", "path", "C3", "theta3", "C4", "diamond", "K4")),
        ("M16", ("single edge", "path", "C3", "theta3", "C4")),
        ("Z3 wr Z3", ("single edge", "path", "C3", "theta3")),
    ]
    p23 = {}
    ok23 = True
    for name, gnames in plan:
        Gr = groups[name]
        d = data[name]
        c = d["case"]
        extra = (w_root(Gr, d["p"], +1), w_root(Gr, d["p"], -1)) if c == "a" else ()
        cache = {}
        for gname in gnames:
            graph = GRAPHS[gname]
            m = len(graph[1])
            bases = bases_for(Gr, d, m)
            K = len(bases) + 2
            counts = []
            for k in range(K):
                if k not in cache:
                    cache[k] = edge_weight(Gr, k, extra)
                counts.append(closed(Gr, graph, cache[k]))
            coef, consistent = fit_top(counts, bases)
            q, pred = predicted(Gr, d, graph, m)
            good = consistent and coef[0] == pred
            p23[f"{name} {gname}"] = {"case": c, "q": q, "top coefficient": str(coef[0]), "predicted": str(pred),
                                      "bases": len(bases), "fit consistent": consistent, "ok": good}
            ok23 &= good
            print(f"part {'2' if c == 'a' else '3'} {name:16s} {gname:22s} case {c} q={q:<3} top {coef[0]} "
                  f"pred {pred} {'ok' if good else 'FAIL'} ({round(time.time() - t0)} s)", flush=True)
    out["parts"]["2_3_interpolation"] = {"rows": p23, "ok": ok23}
    ok_all &= ok23

    # ---------------------------------------------------------------- part 5: controls
    p5 = {}
    C4 = GRAPHS["C4"]
    m = 4
    # (i) fins only on the order-16 dihedral group: the coefficient of 64^(4k) is contaminated
    bases = sorted({16 ** m * 4 ** e for e in range(2 * m + 1)})
    counts = [closed(D16, C4, edge_weight(D16, k)) for k in range(len(bases) + 2)]
    coef, cons = fit_top(counts, bases)
    c64 = coef[bases.index(16 ** m * 4 ** m)]
    ident = 2 * Fraction(1, 2) ** 4 * chromatic(C4, 16)
    p5["fins only: coefficient of 64^(4k) on C4 vs identity 2 P(G,16)/2^n"] = [str(c64), str(ident), c64 != ident]
    # (ii) a doubled cube-root filling (order coprime to 16) changes nothing
    extra3 = (w_root(D16, 3, +1), w_root(D16, 3, -1))
    counts3 = [closed(D16, C4, edge_weight(D16, k, extra3)) for k in range(len(bases) + 2)]
    p5["cube-root filling pair gives the same counts as fins only"] = counts3 == counts
    # (iii) a single (undoubled) square-root filling: top coefficient differs from 2^m times the identity
    extra1 = (w_root(D16, 2, +1),)
    b2 = bases_for(D16, data["D16"], m)
    counts1 = [closed(D16, C4, edge_weight(D16, k, extra1)) for k in range(len(b2) + 2)]
    coef1, cons1 = fit_top(counts1, b2)
    target_doubled = Fraction(8) * Fraction(1, 2) ** 4 * chromatic(C4, 4)
    p5["single root filling: top coefficient vs 2^m times 8 P(G,4)/2^n"] = [str(coef1[0]), str(2 ** m * target_doubled),
                                                                          coef1[0] != 2 ** m * target_doubled]
    # (iv) wrong number of colours
    top = Fraction(p23["D16 C4"]["top coefficient"])
    wrong = 4 ** m * Fraction(8) * Fraction(1, 2) ** 4 * chromatic(C4, 16)
    p5["wrong q = 16 for the order-16 dihedral group rejected"] = top != wrong
    ok5 = (p5["fins only: coefficient of 64^(4k) on C4 vs identity 2 P(G,16)/2^n"][2]
           and p5["cube-root filling pair gives the same counts as fins only"]
           and p5["single root filling: top coefficient vs 2^m times 8 P(G,4)/2^n"][2]
           and p5["wrong q = 16 for the order-16 dihedral group rejected"])
    p5["ok"] = ok5
    out["parts"]["5_controls"] = p5
    print("part 5 controls:", p5, flush=True)
    ok_all &= ok5

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "DICHOTOMY-3D-20261025-001A-P001",
              "status": "Proved" if ok_all else "Partial", "checks": out}
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
