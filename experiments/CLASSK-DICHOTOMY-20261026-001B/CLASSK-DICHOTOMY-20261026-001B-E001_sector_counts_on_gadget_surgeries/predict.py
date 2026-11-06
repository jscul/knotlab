"""Predictions for CLASSK-DICHOTOMY-20261026-001B-E001 (computed before the frozen run, from the gadget models only).

Closed r-surgeries: the sector-k kernel count is (free factor) x (template count) of CLASSK-DICHOTOMY-20261026-001A, Theorem A.
Knot exteriors: the gadget model extended by u, the class of H^1(X; F_p), and the u-pairing u ^ e_i ^ e'_i between the slot
coordinate e_i of each base summand and its partner e'_i in the inverse character, present exactly when the single twist knot
has a nonzero u-pairing at that character (CALIBRATION); the count is the generic obstruction count on that model. This
encodes the claims (i) that Y-moves with leaves of linking number zero do not change the u-pairing and (ii) that it is block
diagonal over the summands of the base.
Run: .venv/bin/python predict.py  (writes predictions.json next to this file)
"""
import itertools
import json
import sys

import numpy as np

from ck_specs import FIXTURES, CALIBRATION, groups_for, L


def gadget_of(fx):
    p, r, S, knots, gname, n, E, roles, fedges = fx
    return L.Gadget(S, n, E, r, p)


def summand_roles(gad, fx):
    """for each gadget coordinate a: the knot of the base summand it belongs to and its character exponent"""
    p, r, S, knots, gname, n, E, roles, fedges = fx
    out = {}
    for a, (th, lab) in enumerate(gad.coords):
        kind = lab[0]
        role = "x" if kind == "x" else ("y" if kind in ("y", "p") else "t")
        out[a] = (knots[role], th)
    return out


def extended_model(gad, fx, with_u):
    """coordinates (theta, label) and the alternating tensor of the extended model"""
    p, r = gad.p, gad.r
    coords = list(gad.coords)
    d = len(coords)
    ext = list(coords)
    iu = None
    if with_u:
        iu = len(ext)
        ext.append((0, ("u",)))
    partner = {}
    for a, (th, lab) in enumerate(coords):
        if (-th) % r != th:
            partner[a] = len(ext)
            ext.append(((-th) % r, ("partner",) + tuple(lab)))
    D = len(ext)
    T = np.zeros((D, D, D), dtype=np.int64)
    T[:d, :d, :d] = gad.T
    if with_u:
        roles = summand_roles(gad, fx)
        for a, b in partner.items():
            knot, th = roles[a]
            if CALIBRATION[(p, knot, th)]:
                tri = (iu, a, b)
                for perm in itertools.permutations(range(3)):
                    sgn = 1
                    for i in range(3):
                        for j in range(i + 1, 3):
                            if perm[i] > perm[j]:
                                sgn = -sgn
                    T[tri[perm[0]], tri[perm[1]], tri[perm[2]]] = (T[tri[perm[0]], tri[perm[1]], tri[perm[2]]] + sgn) % p
    coords_of = {}
    for a, (th, lab) in enumerate(ext):
        coords_of.setdefault(th, []).append(a)
    return ext, T, coords_of


def model_count(G, gad, fx, k, with_u):
    """generic sector-k obstruction count on the (extended) model: variables x_i in V_{k bexp_i}, tests in V_{-k aexp_j}"""
    p, r = G.p, G.r
    ext, T, coords_of = extended_model(gad, fx, with_u)
    I = [i for i in range(G.dB) if (k * G.bexp[i]) % r in coords_of]
    groups, var = [], {}
    for i in I:
        g = []
        for a in coords_of[(k * G.bexp[i]) % r]:
            var[(i, a)] = len(var)
            g.append(var[(i, a)])
        groups.append(g)
    forms = []
    for j in range(G.dA):
        rho = (k * G.aexp[j]) % r
        if rho == 0 or (-rho) % r not in coords_of:
            continue
        for c in coords_of[(-rho) % r]:
            f = {}
            for i in I:
                for i2 in I:
                    if i >= i2:
                        continue
                    v = G.kappa_entry(i, i2, j)
                    if not v:
                        continue
                    for a in coords_of[(k * G.bexp[i]) % r]:
                        for b in coords_of[(k * G.bexp[i2]) % r]:
                            t = int(T[a, b, c])
                            if t:
                                key = (var[(i, a)], var[(i2, b)])
                                f[key] = (f.get(key, 0) + v * t) % p
            f = {key: v for key, v in f.items() if v}
            if f:
                forms.append(f)
    if not groups:
        return 1
    cnt, _, _ = L.count_bilinear_zeros(p, groups, forms)
    return cnt


def predict():
    out = {}
    for fname, fx in FIXTURES.items():
        p, r, S, knots, gname, n, E, roles, fedges = fx
        gad = gadget_of(fx)
        d = L.base_dims(gad.summand_counts(), r)
        dims_closed = {e: d.get(e, 0) for e in range(1, r)}
        dims_knot = dict(dims_closed)
        dims_knot[0] = 1
        rows = {}
        for gname_, G in groups_for(fname).items():
            closed, knot = {}, {}
            for k in range(r):
                free = G.p ** sum(d.get(k * e % r, 0) for e in G.bexp if k * e % r and (k * e % r) not in set(gad.S))
                tc = L.template_count(G, gad, k)
                closed[k] = free * tc
                mc = model_count(G, gad, fx, k, with_u=False)
                assert mc == closed[k], (fname, gname_, k, mc, closed[k])
                knot[k] = model_count(G, gad, fx, k, with_u=True)
            rows[gname_] = {"closed": closed, "knot": knot}
        out[fname] = {"dims_closed": dims_closed, "dims_knot": dims_knot, "groups": rows}
        print(fname, "predicted", flush=True)
    return out


if __name__ == "__main__":
    res = predict()
    from pathlib import Path
    (Path(__file__).resolve().parent / "predictions.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print("written predictions.json")
