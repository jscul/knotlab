"""Bounded probe UT3-TWIST-PROBE-20261025-001: does the lifting obstruction of G = UT3(F4) x| <h> grow on closed 3-manifolds with
bounded first homology? Standard library only. Reads frozen checks read-only (knot diagrams, surgery presentations, Smith form,
Gauss sums, brute force); writes probe_output.json next to this file.

G: N = UT3(F4) as (x,y,z) with (x,y,z)(u,v,w) = (x+u, y+v, z+w+x*v); h n h^-1 = alpha(n).
  hard action  alpha(x,y,z) = (w^2 x, w^2 y, w z)   (the probe target)
  easy action  alpha(x,y,z) = (w x, y, w z)          (control: metabelian)
A = Z(N) = F4 (twisted by psi: pi1 -> C3), N/A = F4^2. For each character psi the probe computes, on a balanced surgery presentation:
  D       = dim_F2 of the space L of lifts of psi to G/A (twisted cocycles),
  ambient = dim_F2 H^2(P; A_psi) = coker of the twisted coboundary on A-cochains,
  span    = dim_F2 of the span, in H^2(P; A_psi), of the obstruction classes o(c), c in L (from the quadratic coefficient vectors),
  liftable = #{c in L : o(c) = 0} (Gauss sums over the characters of the span),
  and |Hom(pi1 M, G)| = sum_psi liftable(psi) * |Z^1(P; A_psi)|, checked against brute force where feasible."""
import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SLA = load("sl23_a_check", "proofs/SL23-BOUNDED-20261025-001A/SL23-BOUNDED-20261025-001A-P001_sl23_counting_is_polynomial_with_bounded_homology/check.py")
CHC = load("closed_c_check", "proofs/CLOSED-H1-20261025-001C/CLOSED-H1-20261025-001C-P001_s4_counting_is_sharp_p_hard_on_closed_manifolds_with_h1_z2/check.py")
CHB = load("closed_b_check", "proofs/CLOSED-H1-20261025-001B/CLOSED-H1-20261025-001B-P001_two_connected_quandles_of_order_6_colour_every_knot_equally/check.py")


def fmul(p, q):
    a, b, c, d = p & 1, p >> 1, q & 1, q >> 1
    return ((a & c) ^ (b & d)) | (((a & d) ^ (b & c) ^ (b & d)) << 1)


W, W2 = 2, 3
F4 = [0, 1, 2, 3]
ALPHA = {"hard": lambda n: (fmul(W2, n[0]), fmul(W2, n[1]), fmul(W, n[2])),
         "easy": lambda n: (fmul(W, n[0]), n[1], fmul(W, n[2]))}


def make_group(alpha):
    def apow(n, e):
        for _ in range(e % 3):
            n = alpha(n)
        return n

    def nmul(a, b):
        return (a[0] ^ b[0], a[1] ^ b[1], a[2] ^ b[2] ^ fmul(a[0], b[1]))

    def mul(g1, g2):
        return nmul(g1[:3], apow(g2[:3], g1[3])) + ((g1[3] + g2[3]) % 3,)
    Ns = [(x, y, z) for x in F4 for y in F4 for z in F4]
    assert all(alpha(nmul(a, b)) == nmul(alpha(a), alpha(b)) for a in Ns for b in Ns)
    assert all(apow(n, 3) == n for n in Ns)
    return SLA.Group([(x, y, z, e) for x in F4 for y in F4 for z in F4 for e in range(3)], mul)


def facts(G):
    comm = lambda a, b: G.M[G.M[a][b]][G.INV[G.M[b][a]]]
    Gp = sorted(G.gen([comm(a, b) for a in range(G.n) for b in range(G.n)]))
    GGp = G.gen([comm(a, b) for a in range(G.n) for b in Gp])
    return {"order": G.n, "|Z(G)|": len(G.center()), "|G'|": len(Gp),
            "G' abelian": all(G.M[a][b] == G.M[b][a] for a in Gp for b in Gp), "[G,G'] = G'": set(GGp) == set(Gp)}


def echelon(vectors):
    basis = []
    for v in vectors:
        v = v[:]
        for p, b in basis:
            if v[p]:
                v = [x ^ y for x, y in zip(v, b)]
        piv = next((i for i, x in enumerate(v) if x), None)
        if piv is not None:
            basis = [(p, [x ^ y for x, y in zip(b, v)] if b[piv] else b) for p, b in basis]
            basis.append((piv, v))
    return basis


def reduce(v, basis):
    v = v[:]
    for p, b in basis:
        if v[p]:
            v = [x ^ y for x, y in zip(v, b)]
    return v


def probe(G, ngen, rels, psi, section=lambda x, y: 0, max_span=16):
    def rel_vals(bits, avec=None):
        vals = []
        for g in range(ngen):
            x = bits[4 * g] | (bits[4 * g + 1] << 1)
            y = bits[4 * g + 2] | (bits[4 * g + 3] << 1)
            z = section(x, y) ^ (avec[g] if avec else 0)
            vals.append(G.E.index((x, y, z, psi[g] % 3)))
        out = []
        for r in rels:
            X, Y, Z, e = G.E[G.word(r, vals)]
            assert e == 0
            out.append((X, Y, Z))
        return out
    nv = 4 * ngen
    b2 = lambda v: [v & 1, v >> 1]
    f0 = rel_vals([0] * nv)
    cols = [rel_vals([int(t == i) for t in range(nv)]) for i in range(nv)]
    rows, rhs = [], []
    for ri in range(len(rels)):
        for comp in range(4):
            sel = (lambda tr: b2(tr[0])[comp]) if comp < 2 else (lambda tr: b2(tr[1])[comp - 2])
            rows.append([sel(cols[i][ri]) ^ sel(f0[ri]) for i in range(nv)])
            rhs.append(sel(f0[ri]))
    part, Kb = SLA.affine_solve_f2(rows, rhs, nv)
    D = len(Kb)
    zb = lambda rv: [b for (X, Y, Z) in rv for b in b2(Z)]
    z0 = zb(rel_vals(part))
    dcols = []
    for g in range(ngen):
        for bit in (1, 2):
            av = [0] * ngen
            av[g] = bit
            dcols.append([a ^ b for a, b in zip(zb(rel_vals(part, av)), z0)])
    im = echelon(dcols)
    point = lambda u: [(part[t] + sum(u[i] * Kb[i][t] for i in range(D))) % 2 for t in range(nv)]

    def ocls(u):
        rv = rel_vals(point(u))
        assert all(X == 0 and Y == 0 for X, Y, Z in rv)
        return reduce(zb(rv), im)
    o0 = ocls([0] * D)
    o1 = [ocls([int(t == i) for t in range(D)]) for i in range(D)]
    o2 = {(i, j): ocls([int(t in (i, j)) for t in range(D)]) for i in range(D) for j in range(i + 1, D)}
    lin = [[a ^ b for a, b in zip(o1[i], o0)] for i in range(D)]
    quad = {k: [a ^ b ^ c ^ d for a, b, c, d in zip(v, o1[k[0]], o1[k[1]], o0)] for k, v in o2.items()}
    span = echelon([o0] + lin + list(quad.values()))
    res = {"D": D, "ambient H2": 2 * len(rels) - len(im), "Z1(A)": 2 * ngen - len(im), "span": len(span),
           "quadratic span": len(echelon(list(quad.values()))), "o(0) = 0": not any(o0)}
    if len(span) <= max_span:
        def coords(v):
            c, w = [], v[:]
            for p, b in span:
                c.append(w[p])
                if w[p]:
                    w = [x ^ y for x, y in zip(w, b)]
            assert not any(w)
            return c
        c0, cl, cq = coords(o0), [coords(v) for v in lin], {k: coords(v) for k, v in quad.items()}
        acc = 0
        for chi in itertools.product((0, 1), repeat=len(span)):
            dot = lambda c: sum(a & b for a, b in zip(chi, c)) & 1
            acc += SLA.gauss_sum(D, {k for k, c in cq.items() if dot(c)}, {i for i in range(D) if dot(cl[i])}, dot(c0))
        res["liftable"] = acc // 2 ** len(span)
        res["count contribution"] = res["liftable"] * 2 ** res["Z1(A)"]
    return res


def characters(ngen, rels):
    E3 = [[sum(e for x, e in r if x == g) % 3 for g in range(ngen)] for r in rels]
    return list(SLA.span_mod(SLA.nullspace_mod(E3, ngen, 3), 3, ngen))


def power(code, k):
    c = code
    for _ in range(k - 1):
        c = SLA.connected_sum(c, code)
    return c


def run_manifold(G, code, p, brute=False, section=lambda x, y: 0):
    U, rels = SLA.surgery_presentation(code, p)
    h1 = CHC.h1_invariants(code, p)
    rows, total = {}, 0
    for psi in characters(U, rels):
        r = probe(G, U, rels, psi, section=section)
        total += r.get("count contribution", 0)
        rows[f"psi(meridian) = {psi[0]}"] = r
    out = {"generators": U, "H1 invariants": h1, "per character": rows, "|Hom(pi1, G)|": total}
    if brute:
        out["brute force"] = SLA.brute_surgery(G, code, p)
    return out


def main():
    t0 = time.time()
    out = {}
    GH, GE = make_group(ALPHA["hard"]), make_group(ALPHA["easy"])
    out["group facts"] = {"hard": facts(GH), "easy": facts(GE)}
    print(out["group facts"], flush=True)
    tre = SLA.gauss_from_braid([1, 1, 1], 2)
    f8 = SLA.gauss_from_braid([1, -2, 1, -2], 3)
    e18 = SLA.gauss_from_braid([1, -2] * 4, 3)
    fam = {}
    for label, base, ks in (("4_1", f8, (1, 2, 3)), ("3_1", tre, (1, 2, 3, 4)), ("8_18", e18, (1, 2, 3))):
        for k in ks:
            r = run_manifold(GH, power(base, k), 3, brute=(label in ("4_1", "3_1") and k <= 2))
            fam[f"hard, S3_3(({label})^#{k})"] = r
            pr = r["per character"]["psi(meridian) = 1"]
            print(f"hard {label}^{k}: H1 {r['H1 invariants']} D {pr['D']} ambient {pr['ambient H2']} span {pr['span']} "
                  f"liftable {pr.get('liftable')} total {r['|Hom(pi1, G)|']} brute {r.get('brute force')} ({time.time() - t0:.0f} s)", flush=True)
    for k in (1, 2, 3):
        r = run_manifold(GE, power(tre, k), 3, brute=(k <= 2))
        fam[f"easy, S3_3((3_1)^#{k})"] = r
        pr = r["per character"]["psi(meridian) = 1"]
        print(f"easy 3_1^{k}: D {pr['D']} ambient {pr['ambient H2']} span {pr['span']} total {r['|Hom(pi1, G)|']} brute {r.get('brute force')}", flush=True)
    sec = {}
    for k in (1, 2):
        a = run_manifold(GH, power(tre, k), 3)
        b = run_manifold(GH, power(tre, k), 3, section=lambda x, y: fmul(x, y))
        sec[f"(3_1)^#{k}"] = {"default section": [a["per character"][c]["span"] for c in a["per character"]],
                             "section z = x*y": [b["per character"][c]["span"] for c in b["per character"]],
                             "totals equal": a["|Hom(pi1, G)|"] == b["|Hom(pi1, G)|"]}
    out["section independence"] = sec
    print("section independence:", sec, flush=True)
    cyc = lambda n: (n, [(i, (i + 1) % n) for i in range(n)], {i: [i, (i - 1) % n] for i in range(n)})
    for n in (3, 5, 7):
        r = run_manifold(GH, CHB.gauss_from_plane_graph(*CHB.tripled(cyc(n))), 3)
        fam[f"hard, S3_3(D(C{n}^(3)))"] = r
        pr = r["per character"]["psi(meridian) = 1"]
        print(f"hard D(C{n}^(3)): H1 {r['H1 invariants']} D {pr['D']} ambient {pr['ambient H2']} span {pr['span']}", flush=True)
    out["manifolds"] = fam
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "probe_output.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print("done", out["seconds"], "s")


if __name__ == "__main__":
    main()
