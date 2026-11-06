"""Fixtures of the pattern-1 checkpoint: K2 and the digon, built by the projector construction."""
import math
import time

import numpy as np

import pc_core as PC  # noqa: E402  (puts cp_lib on the path)
import cp_lib as C  # noqa: E402
from pc_core import (Comp, BraidLayout, Diagram, cohomology, obstruction_bimap, counts_from_bimaps, evaluate, P, R,
                     smith_diagonal, rank_mod, EPS, PITCH, MARG)
from pc_build import multiplicities, leaf_projector, leaf_band_sum, leaf_simple, y_graph

CHI = {"x": 3, "y": 2, "t": 6}          # slot characters zeta, zeta^2, zeta^3
TYPE = {"x": PC.T31, "y": PC.S61, "t": PC.K52}


def leaf_height(chi):
    m = multiplicities(chi)
    copies = sum(m)
    return 0.6 + copies * (2 * MARG + 2 * EPS) + PITCH * sum(j * mj for j, mj in enumerate(m)) + 0.3


class Base:
    """K0 = connected sum of the summands (in order) as a braid closure, with tall gaps where leaves will sit"""

    def __init__(self, slots, leaves_per_summand, gap_choice=None):
        self.slots = slots                                  # e.g. ["x", "x", "y", "t"]
        words = [TYPE[s] for s in slots]
        self.word, self.n = C.connected_sum(words)
        self.offsets, self.cranges = [], []
        off, cr = 0, 0
        for w, nn in words:
            self.offsets.append((off, off + nn - 1))
            self.cranges.append((cr, cr + len(w)))
            off += nn - 1
            cr += len(w)
        self.leaves_per_summand = leaves_per_summand
        self.gap_choice = gap_choice                        # summand -> (k, q)

    def layout(self):
        gaps = {}
        for i, (k, q) in self.gap_choice.items():
            h = sum(leaf_height(CHI[self.slots[i]]) + 1.5 for _ in range(self.leaves_per_summand[i])) + 2.0
            gaps[k] = max(gaps.get(k, 1.0), h)
        return BraidLayout(self.word, self.n, gaps)


def arc_functionals(L, choices, chis):
    """for each summand i with (k, q): the functional c -> c(arc at q) - c(arc at q + 1) on H^1(chi) of K0 (6-surgery),
    as vectors over the computed basis"""
    K = Comp("K", L.pts, 1, 6, "knot")
    D = Diagram([K])
    rels = D.crossing_rels + D.framing_rels()
    out = {}
    bases = {}
    for chi in set(chis.values()):
        H, _, _ = cohomology(len(D.gens), rels, D.psi, chi)
        bases[chi] = H
    for i, (k, q) in choices.items():
        lo, hi = L.gap(k)
        ym = (lo + hi) / 2
        ga = D.locate(0, (float(q), ym, 0.0))
        gb = D.locate(0, (float(q + 1), ym, 0.0))
        chi = chis[i]
        out[i] = [int((h[ga] - h[gb]) % P) for h in bases[chi]]
    return out, {chi: len(H) for chi, H in bases.items()}


def choose_arcs(base):
    """first (k, q) per summand (k inside its crossing range, q, q + 1 inside its strands) such that the arc
    functionals of the summands sharing a slot character are linearly independent"""
    chis = {i: CHI[s] for i, s in enumerate(base.slots)}
    cands = {}
    for i in range(len(base.slots)):
        (plo, phi), (clo, chi_) = base.offsets[i], base.cranges[i]
        cands[i] = [(k, q) for k in range(clo, chi_) for q in range(plo, phi)]
    # try candidates summand by summand, keeping the independence of each character group
    choice = {}
    for i in range(len(base.slots)):
        for kq in cands[i]:
            trial = dict(choice)
            trial[i] = kq
            # layout with unit gaps suffices for arc identities
            L = BraidLayout(base.word, base.n)
            f, dims = arc_functionals(L, trial, chis)
            group = [j for j in trial if chis[j] == chis[i]]
            M = np.array([f[j] for j in group])
            if rank_mod(M) == len(group):
                choice[i] = kq
                break
        assert i in choice, f"no arc pair for summand {i}"
    return choice


def build_fixture(slots, edges, wdir, unbalanced_edge=None, simple=False, verbose=True):
    """slots: summand types; edges: list of (u, v, y, t) summand indices. Returns (components, info)."""
    nleaves = {i: 0 for i in range(len(slots))}
    for (u, v, y, t) in edges:
        for i in (u, v, y, t):
            nleaves[i] += 1
    base = Base(slots, nleaves)
    base.gap_choice = choose_arcs(base)
    L = base.layout()
    comps = [Comp("K", L.pts, 1, 6, "knot")]
    # place leaves top-down inside each chosen gap
    tops = {}
    for i, (k, q) in base.gap_choice.items():
        lo, hi = L.gap(k)
        tops[i] = [hi - 1.0]
    def next_top(i):
        t = tops[i][-1]
        h = leaf_height(CHI[slots[i]])
        tops[i].append(t - h - 1.5)
        return t
    leaves, roots, info = [], [], {"choice": base.gap_choice, "word": base.word, "n": base.n, "edges": []}
    for e, (u, v, y, t) in enumerate(edges):
        ku, qu = base.gap_choice[u]
        kv, qv = base.gap_choice[v]
        tu, tv = next_top(u), next_top(v)
        wind = None
        if unbalanced_edge == e:
            # one turn of the connecting band around the strand right of b_u, inside u's gap below the leaves
            lo, hi = L.gap(ku)
            wind = (float(qu + 2), lo + 0.5, 1, 1)
        mult = [1, 0, 0, 0, 0, 0] if simple else None
        lf, _, inf = leaf_band_sum(f"l{e}", float(qu), tu, float(qv), tv, CHI["x"], wdir, 6.0 + 2.0 * e, wind=wind,
                                   mult=mult)
        trip = [lf]
        for i, s in ((y, "y"), (t, "t")):
            k, q = base.gap_choice[i]
            top = next_top(i)
            lf2, _, inf2 = leaf_projector(f"{s}{e}", float(q), top, CHI[s], wdir, mult=mult)
            trip.append(lf2)
        r = [(inf["root_mid"][0], inf["root_mid"][1])]
        for lf2 in trip[1:]:
            x0, y0, _ = lf2.pts[0]
            r.append((x0, y0))
        ymid = sum(y for _, y in r) / 3
        B = y_graph(e, (-12.0, ymid, 20.0 + 12.0 * e), r, 24.0 + 12.0 * e)
        comps += trip + B
        info["edges"].append({"tops": (tu, tv), "roots": r})
    info["layout_y"] = L.y
    return comps, info, L, base


def surgery_counts(comps, label="", verbose=True):
    t = time.time()
    D = Diagram(comps)
    rels = D.crossing_rels + D.framing_rels()
    U = len(D.gens)
    Lm = D.lk.copy()
    for i, c in enumerate(comps):
        Lm[i, i] = c.framing
    sd = [d for d in smith_diagonal(Lm.tolist()) if d != 1]
    psi_ok = all(sum(D.psi[g] * s for g, s in rel) % R == 0 for rel in rels)
    H = {}
    for chi in (3, 2, 6, 4, 5):
        H[chi], _, _ = cohomology(U, rels, D.psi, chi)
    sectors = {}
    for sec, (a, b, c) in {"psi^1 (zeta, zeta^2, zeta^3)": (3, 2, 6), "psi^5 (zeta^5, zeta^4, zeta^3)": (5, 4, 6)}.items():
        Ha, Hb, Hc = H[a], H[b], H[c]
        B12 = obstruction_bimap(U, rels, D.psi, a, b, Ha, Hb)
        B13 = obstruction_bimap(U, rels, D.psi, a, c, Ha, Hc)
        B23 = obstruction_bimap(U, rels, D.psi, b, c, Hb, Hc)
        sectors[sec] = counts_from_bimaps(B12, B13, B23, len(Ha), len(Hb), len(Hc))
    cl = Lm[1:, 1:]
    sd_cl = [d for d in smith_diagonal(cl.tolist()) if d != 1] if len(cl) else []
    out = {"components": len(comps), "crossings": len(D.crossings), "generators": U, "relators": len(rels),
           "min_depth_gap": round(D.min_dz, 4), "H1_invariant_factors": sd, "clasper_only_H1_factors": sd_cl,
           "psi_well_defined": psi_ok, "meridian_psi": int(D.psi[D.mu[0]]),
           "dims": {chi: len(H[chi]) for chi in H}, "sectors": sectors, "seconds": round(time.time() - t, 1)}
    if verbose:
        print(label, out, flush=True)
    return out


def leaf_functionals(K, leaves, chis=(3, 2, 6, 4, 5)):
    """functional of each leaf (read at its position 0) on H^1(S^3_6(K0); chi), all leaves killed (forgotten)"""
    comps = [K] + [Comp(l.name, l.pts, 0, None, "leaf") for l in leaves]
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
