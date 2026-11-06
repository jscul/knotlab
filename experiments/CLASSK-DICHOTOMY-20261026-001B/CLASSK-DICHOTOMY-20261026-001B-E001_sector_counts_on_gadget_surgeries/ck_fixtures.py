"""Gadget fixtures for CLASSK-DICHOTOMY-20261026-001B: the projector construction of COPRIME-CLASS2-20261026-001D section 3
for the three slot patterns, and the extraction of twisted cohomology and cup-product classes from the actual surgeries
(closed r-surgery and knot exterior).

The base, arc choice, leaves, band sums and Y-graphs follow PATTERN1-CHECKPOINT-20261026-001-E001 pc_fixtures.py, with the
slot characters and summand knots passed in a Spec instead of fixed to (3, 2, 6) and (3_1, 6_1, 5_2).
"""
import time

import numpy as np

import ck_core as PC  # noqa: E402  (puts cp_lib on the path)
import cp_lib as C  # noqa: E402
from ck_core import (Comp, BraidLayout, Diagram, cohomology, obstruction_bimap, evaluate, smith_diagonal, rank_mod, EPS,
                     PITCH, MARG)
from ck_build import multiplicities, leaf_projector, leaf_band_sum, y_graph

T31, F41, K52, S61 = ([1, 1, 1], 2), ([1, -2, 1, -2], 3), ([1, 1, 1, 2, -1, 2], 3), ([1, 1, 2, -1, -3, 2, -3], 4)
KNOTS = {"3_1": T31, "4_1": F41, "5_2": K52, "6_1": S61}


class Spec:
    """field, slot characters (as F_p values) for the three leaf roles x, y, t, and the summand knot of each role"""

    def __init__(self, p, r, zeta, slot_exps, knots):
        self.p, self.r, self.zeta = p, r, zeta
        self.slot_exps = tuple(slot_exps)
        self.chi = {role: pow(zeta, e, p) for role, e in zip("xyt", slot_exps)}
        self.knot = {role: knots[role] for role in "xyt"}
        self.type = {role: KNOTS[knots[role]] for role in "xyt"}

    def configure(self):
        PC.configure(self.p, self.r, self.zeta)


def leaf_height(chi):
    m = multiplicities(chi)
    copies = sum(m)
    return 0.6 + copies * (2 * MARG + 2 * EPS) + PITCH * sum(j * mj for j, mj in enumerate(m)) + 0.3


class Base:
    """K0 = connected sum of the summands (in order) as a braid closure, with tall gaps where leaves will sit"""

    def __init__(self, spec, slots, leaves_per_summand, gap_choice=None):
        self.spec = spec
        self.slots = slots
        words = [spec.type[s] for s in slots]
        self.word, self.n = C.connected_sum(words)
        self.offsets, self.cranges = [], []
        off, cr = 0, 0
        for w, nn in words:
            self.offsets.append((off, off + nn - 1))
            self.cranges.append((cr, cr + len(w)))
            off += nn - 1
            cr += len(w)
        self.leaves_per_summand = leaves_per_summand
        self.gap_choice = gap_choice

    def layout(self):
        gaps = {}
        for i, (k, q) in self.gap_choice.items():
            h = sum(leaf_height(self.spec.chi[self.slots[i]]) + 1.5 for _ in range(self.leaves_per_summand[i])) + 2.0
            gaps[k] = max(gaps.get(k, 1.0), h)
        return BraidLayout(self.word, self.n, gaps)


def arc_functionals(L, choices, chis, r):
    K = Comp("K", L.pts, 1, r, "knot")
    D = Diagram([K])
    rels = D.crossing_rels + D.framing_rels()
    out, bases = {}, {}
    for chi in set(chis.values()):
        H, _, _ = cohomology(len(D.gens), rels, D.psi, chi)
        bases[chi] = H
    p = PC.P
    for i, (k, q) in choices.items():
        lo, hi = L.gap(k)
        ym = (lo + hi) / 2
        ga = D.locate(0, (float(q), ym, 0.0))
        gb = D.locate(0, (float(q + 1), ym, 0.0))
        out[i] = [int((h[ga] - h[gb]) % p) for h in bases[chis[i]]]
    return out


def choose_arcs(base):
    """first (k, q) per summand such that the arc functionals of the summands sharing a slot character are independent"""
    chis = {i: base.spec.chi[s] for i, s in enumerate(base.slots)}
    cands = {}
    for i in range(len(base.slots)):
        (plo, phi), (clo, chi_) = base.offsets[i], base.cranges[i]
        cands[i] = [(k, q) for k in range(clo, chi_) for q in range(plo, phi)]
    choice = {}
    for i in range(len(base.slots)):
        for kq in cands[i]:
            trial = dict(choice)
            trial[i] = kq
            L = BraidLayout(base.word, base.n)
            f = arc_functionals(L, trial, chis, base.spec.r)
            group = [j for j in trial if chis[j] == chis[i]]
            M = np.array([f[j] for j in group])
            if rank_mod(M) == len(group):
                choice[i] = kq
                break
        assert i in choice, f"no arc pair for summand {i}"
    return choice


def build_fixture(spec, slots, edges, wdir=-1):
    """slots: summand roles in order ('x' vertex summands, 'y' and 't' edge summands); edges: (u, v, y, t) summand indices.
    One Y-graph per edge: the balanced band sum x_u - x_v (character chi_x), a pure leaf in summand y (chi_y) and one in
    summand t (chi_t)."""
    spec.configure()
    r = spec.r
    nleaves = {i: 0 for i in range(len(slots))}
    for (u, v, y, t) in edges:
        for i in (u, v, y, t):
            nleaves[i] += 1
    base = Base(spec, slots, nleaves)
    base.gap_choice = choose_arcs(base)
    L = base.layout()
    comps = [Comp("K", L.pts, 1, r, "knot")]
    tops = {}
    for i, (k, q) in base.gap_choice.items():
        lo, hi = L.gap(k)
        tops[i] = [hi - 1.0]

    def next_top(i):
        t = tops[i][-1]
        h = leaf_height(spec.chi[slots[i]])
        tops[i].append(t - h - 1.5)
        return t
    info = {"choice": {str(k): v for k, v in base.gap_choice.items()}, "word": base.word, "n": base.n, "edges": []}
    for e, (u, v, y, t) in enumerate(edges):
        ku, qu = base.gap_choice[u]
        kv, qv = base.gap_choice[v]
        tu, tv = next_top(u), next_top(v)
        lf, _, inf = leaf_band_sum(f"l{e}", float(qu), tu, float(qv), tv, spec.chi["x"], wdir, 6.0 + 2.0 * e)
        trip = [lf]
        for i, role in ((y, "y"), (t, "t")):
            k, q = base.gap_choice[i]
            top = next_top(i)
            lf2, _, inf2 = leaf_projector(f"{role}{e}", float(q), top, spec.chi[role], wdir)
            trip.append(lf2)
        roots = [(inf["root_mid"][0], inf["root_mid"][1])]
        for lf2 in trip[1:]:
            x0, y0, _ = lf2.pts[0]
            roots.append((x0, y0))
        ymid = sum(yy for _, yy in roots) / 3
        B = y_graph(e, (-12.0, ymid, 20.0 + 12.0 * e), roots, 24.0 + 12.0 * e)
        comps += trip + B
        info["edges"].append({"tops": (tu, tv), "roots": roots})
    return comps, info, L, base


def cohomology_data(comps, spec, knot_group=False):
    """all twisted H^1 bases and cup-product classes of the surgery (closed) or of the knot exterior (knot_group): for every
    ordered pair (a, b) of characters with nonzero H^1 and a b nontrivial, the canonical classes of h_a^i u h_b^j"""
    spec.configure()
    p, r, z = spec.p, spec.r, spec.zeta
    t0 = time.time()
    D = Diagram(comps)
    framings = [None if (knot_group and ci == 0) else c.framing for ci, c in enumerate(comps)]
    rels = D.crossing_rels + D.framing_rels(framings)
    U = len(D.gens)
    psi_ok = all(sum(D.psi[g] * s for g, s in rel) % r == 0 for rel in rels)
    Lm = D.lk.copy()
    for i, c in enumerate(comps):
        Lm[i, i] = c.framing
    if knot_group:
        Lm = Lm[1:, 1:]
    sd = [d for d in smith_diagonal(Lm.tolist()) if d != 1] if len(Lm) else []
    chars = [pow(z, e, p) for e in range(r)]
    H = {}
    for e, chi in enumerate(chars):
        if e == 0 and not knot_group:
            continue
        H[e] = cohomology(U, rels, D.psi, chi)[0]
    dims = {e: len(h) for e, h in H.items()}
    bimaps, reducers = {}, {}
    for ea, Ha in H.items():
        for eb, Hb in H.items():
            if not Ha or not Hb or (ea + eb) % r == 0:
                continue
            et = (ea + eb) % r
            if et not in reducers:
                reducers[et] = PC.Reducer(PC.fox_matrix(U, rels, D.psi, chars[et], p).T, p)
            Bm = obstruction_bimap(U, rels, D.psi, chars[ea], chars[eb], Ha, Hb, red=reducers[et])
            bimaps[(ea, eb)] = Bm
    return {"U": U, "relators": len(rels), "crossings": len(D.crossings), "components": len(comps),
            "min_depth_gap": round(D.min_dz, 4), "psi_well_defined": psi_ok, "meridian_psi": int(D.psi[D.mu[0]]),
            "H1_invariant_factors": sd, "dims": dims, "bimaps": bimaps, "seconds": round(time.time() - t0, 1)}


def leaf_functionals(K, leaves, chis):
    """functional of each leaf (read at its position 0) on H^1(S^3_r(K0); chi), all leaves killed (forgotten)"""
    comps = [K] + [Comp(lf.name, lf.pts, 0, None, "leaf") for lf in leaves]
    D = Diagram(comps)
    rels = D.crossing_rels + D.framing_rels()
    for ci in range(1, len(comps)):
        base, narcs = D.arc_of[ci]
        rels += [[(base + a, 1)] for a in range(narcs)]
    out = {}
    for chi in chis:
        H, _, _ = cohomology(len(D.gens), rels, D.psi, chi)
        out[chi] = {comps[ci].name: [evaluate(D.lam[ci], h, D.psi, chi) for h in H] for ci in range(1, len(comps))}
    return out, D


# ------------------------------------------------------------------------------------------------ counting from the data

def measured_count(G, data, k, count_bilinear_zeros, use_beta=True):
    """sector-k kernel count of a class-(K) group G (ck_lib.KGroup with the same p, r and generator) from the measured cup
    classes: #{x = (x_i), x_i in H^1(chi_i^k) : [beta_*(x u x)] = 0}; trivial-character targets are skipped (H^2 = 0 there:
    closed manifolds with H1 = Z/r, and knot exteriors)"""
    p, r = G.p, G.r
    dims, bimaps = data["dims"], data["bimaps"]
    var, groups = {}, []
    theta = {}
    for i in range(G.dB):
        e = (k * G.bexp[i]) % r
        theta[i] = e
        d = dims.get(e, 0)
        g = []
        for a in range(d):
            var[(i, a)] = len(var)
            g.append(var[(i, a)])
        if g:
            groups.append(g)
    coef = G.beta if use_beta else {key: v * pow(2, p - 2, p) % p for key, v in G.kap.items()}
    forms = []
    for j in range(G.dA):
        rho = (k * G.aexp[j]) % r
        if rho == 0:
            continue
        vecs = {}
        for (i, i2, jj), b in coef.items():
            if jj != j:
                continue
            ea, eb = theta[i], theta[i2]
            if (ea, eb) not in bimaps:
                continue
            for (a, c), cl in bimaps[(ea, eb)].items():
                key = (var[(i, a)], var[(i2, c)])
                for col, val in enumerate(cl):
                    if val:
                        f = vecs.setdefault(col, {})
                        f[key] = (f.get(key, 0) + b * val) % p
        for col, f in vecs.items():
            f = {kk: v for kk, v in f.items() if v}
            if f:
                forms.append(f)
    if not groups:
        return 1
    cnt, nvar, ncov = count_bilinear_zeros(p, groups, forms)
    return cnt
