"""Referee R1 for WEAVE-LAWS-20261117-001 (own code; nothing imported from the study).

  .venv/bin/python -B referee_laws.py > referee_laws.json

1. L1 on all 34 three-place knots: the Fourier degree of each knot's allowed set, against "excludes one complementary pair".
2. Row transfer matrices of the twelve laws on the weave (up knot (v(i,j), v(i+1,j), v(i,j+1)), down knot (v(i+1,j), v(i,j+1),
   v(i+1,j+1)), places in that order), widths 3..12:
   - the live part (rows on an infinite path), and its strongly connected components. A 0/1 matrix has spectral radius exactly 1
     when every non-trivial component is a single cycle, and above 1 when some component is not: an exact test of "frozen";
   - for the others, the top eigenvalues (dense up to 1,024 live rows, else Arnoldi from a random start, two starts compared):
     states per distinction, transfer gap in log base 3, gap x width;
   - exact torus counts trace(T^L) for L <= 7.
3. The agreeing-signs law against NAE at every width (the holonomy: its gauge to NAE needs an even width).
4. Which transfer modes a single distinction feels (OR at widths 6, 9, 10; hard hexagons at 10): the spectral amplitudes of
   its correlation along the transfer axis, and whether |C(r)| falls at every step.
5. A light census: OR at n = 4, 5, 6 (every knot set), the first collision of not-exactly-two (n = 5) and parity (n = 4).
"""
from __future__ import annotations

import itertools
import json
import math

import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigs

LAWS = {
    "NAE": ({(0, 0, 0), (1, 1, 1)},) * 2,
    "signed NAE, place 2 odd": ({(0, 1, 0), (1, 0, 1)},) * 2,
    "signed NAE, place 1 odd": ({(1, 0, 0), (0, 1, 1)},) * 2,
    "signed NAE, place 3 odd": ({(0, 0, 1), (1, 1, 0)},) * 2,
    "NAE up, place 1 odd down": ({(0, 0, 0), (1, 1, 1)}, {(1, 0, 0), (0, 1, 1)}),
    "NAE up, place 3 odd down": ({(0, 0, 0), (1, 1, 1)}, {(0, 0, 1), (1, 1, 0)}),
    "OR": ({(0, 0, 0)},) * 2,
    "not-exactly-two": ({(0, 1, 1), (1, 0, 1), (1, 1, 0)},) * 2,
    "parity": ({(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)},) * 2,
    "distance-two, place 1 odd": ({(0, 0, 0), (0, 1, 1)},) * 2,
    "distance-two, place 2 odd": ({(0, 0, 0), (1, 0, 1)},) * 2,
    "distance-two, place 3 odd": ({(0, 0, 0), (1, 1, 0)},) * 2,
}


def l1():
    states = list(itertools.product((0, 1), repeat=3))
    out = []
    for k in range(1, 5):
        for ex in itertools.combinations(states, k):
            if any(sum(a != b for a, b in zip(x, y)) == 1 for x, y in itertools.combinations(ex, 2)):
                continue
            allowed = [s for s in states if s not in ex]
            sgn = lambda s, S: math.prod(1 - 2 * s[i] for i in S)
            deg = max((len(S) for r in range(4) for S in itertools.combinations(range(3), r)
                       if sum(sgn(s, S) for s in allowed) != 0), default=0)
            comp = len(ex) == 2 and all(a != b for a, b in zip(*ex))
            out.append((ex, deg, comp))
    return {"knots": len(out), "degree_le_2": sum(d <= 2 for _, d, _ in out),
            "degree_le_2_iff_complementary_pair": all((d <= 2) == c for _, d, c in out)}


def transfer(w, law):
    up, down = law
    R = 1 << w
    b = (np.arange(R)[:, None] >> np.arange(w)[None, :]) & 1
    T = np.ones((R, R), dtype=bool)
    for i in range(w):
        x0, x1 = b[:, i][:, None], b[:, (i + 1) % w][:, None]      # row j: (i, j), (i+1, j)
        y0, y1 = b[:, i][None, :], b[:, (i + 1) % w][None, :]      # row j+1: (i, j+1), (i+1, j+1)
        for p in up:
            T &= ~((x0 == p[0]) & (x1 == p[1]) & (y0 == p[2]))
        for p in down:
            T &= ~((x1 == p[0]) & (y0 == p[1]) & (y1 == p[2]))
    return T


def live(T):
    keep = np.ones(len(T), bool)
    while True:
        S = T[np.ix_(keep, keep)]
        good = S.any(axis=1) & S.any(axis=0)
        if good.all():
            return S
        keep[np.flatnonzero(keep)[~good]] = False


def frozen_exact(S):
    """(spectral radius is exactly 1, number of non-trivial components); None when the live part is empty."""
    if len(S) == 0:
        return None, 0
    ncomp, lab = connected_components(sp.csr_matrix(S), directed=True, connection="strong")
    cyc = 0
    for c in range(ncomp):
        idx = np.flatnonzero(lab == c)
        sub = S[np.ix_(idx, idx)]
        e = int(sub.sum())
        if e == 0:
            continue
        if e != len(idx):
            return False, None
        cyc += 1
    return True, cyc


def top_eigs(S, k=8):
    if len(S) <= 1024:
        ev = np.linalg.eigvals(S.astype(float))
    else:
        M = sp.csr_matrix(S.astype(float))
        rng = np.random.default_rng(1)
        ev = eigs(M, k=k, which="LM", return_eigenvectors=False, tol=1e-12, maxiter=50000, v0=rng.random(len(S)))
        ev2 = eigs(M, k=k, which="LM", return_eigenvectors=False, tol=1e-12, maxiter=50000, v0=rng.random(len(S)))
        assert abs(np.sort(np.abs(ev))[-1] - np.sort(np.abs(ev2))[-1]) < 1e-8
    m = np.sort(np.abs(ev))[::-1]
    return m


def law_row(name, law, w):
    T = transfer(w, law)
    S = live(T)
    row = {"width": w, "live_rows": int(len(S))}
    fz, cyc = frozen_exact(S)
    row["spectral_radius_exactly_1"] = fz
    if w <= 7:
        P = np.linalg.matrix_power(T.astype(object), w)
        row["torus_states"] = int(sum(P[i, i] for i in range(len(T))))
    if fz is None:
        row["dead"] = True
        return row
    if fz:
        row["per_site"] = 1.0
        row["cycles"] = cyc
        return row
    m = top_eigs(S)
    top = m[0]
    mult = int(np.sum(m > top * (1 - 1e-9)))
    lam1 = next((x for x in m if x < top * (1 - 1e-9)), None)
    row.update(per_site=float(top ** (1 / w)), top_multiplicity=mult,
               gap=None if lam1 is None or lam1 <= 0 else float(math.log(top / lam1, 3)))
    if row["gap"] is not None:
        row["gap_x_width"] = row["gap"] * w
    return row


def coupled_modes(name, w, rmax=15):
    """Spectral decomposition of a single distinction's correlation along the transfer axis on the width-w cylinder:
    C(r) = sum_k a_k (lambda_k / lambda_0)^r, a_k = (l_0 X r_k)(l_k X r_0) / var, X = the value of distinction (0, row)."""
    T = transfer(w, LAWS[name]).astype(float)
    ev, Rv = np.linalg.eig(T)
    Li = np.linalg.inv(Rv)
    o = np.argsort(-np.abs(ev))
    ev, Rv, Li = ev[o], Rv[:, o], Li[o]
    x = (np.arange(len(T)) & 1).astype(float)
    m = ((Li[0] * x) @ Rv[:, 0]).real
    var = m * (1 - m)
    a = np.array([(Li[0] * x) @ Rv[:, k] * ((Li[k] * x) @ Rv[:, 0]) / var for k in range(len(ev))])
    first = next(k for k in range(1, len(ev)) if abs(a[k]) > 1e-10)
    C = [float(sum(a[k] * (ev[k] / ev[0]) ** r for k in range(1, len(ev))).real) for r in range(1, rmax + 1)]
    return {"width": w, "mean": float(m),
            "modes": [{"modulus": float(abs(ev[k])), "phase": float(np.angle(ev[k])), "amplitude": float(abs(a[k])),
                       "rate_log3": float(math.log(abs(ev[0]) / abs(ev[k]), 3))} for k in range(1, 9)],
            "first_coupled_mode": first, "gap_of_first_coupled_mode": float(math.log(abs(ev[0]) / abs(ev[first]), 3)),
            "correlation": C, "abs_correlation_monotone": all(abs(C[i + 1]) < abs(C[i]) for i in range(len(C) - 1))}


def popcount(a):
    return np.bitwise_count(a).astype(np.int64)


def census_or():
    """Every set of OR knots on n labelled distinctions (one knot per triple; OR is symmetric), vectorised on 64-bit masks."""
    out = {}
    for n in (4, 5, 6):
        ks = list(itertools.combinations(range(n), 3))
        masks = [sum(1 << s for s in range(1 << n) if any((s >> a) & 1 for a in t)) for t in ks]
        rel = np.zeros(1 << len(ks), dtype=np.uint64)
        rel[0] = np.uint64((1 << (1 << n)) - 1)
        for j in range(len(ks)):
            rel[1 << j: 1 << (j + 1)] = rel[: 1 << j] & np.uint64(masks[j])
        rels = np.unique(rel)
        cols = [popcount(rels)]
        for u in range(n):
            cols.append(popcount(rels & np.uint64(sum(1 << s for s in range(1 << n) if (s >> u) & 1))))
        for u, v in itertools.combinations(range(n), 2):
            cols.append(popcount(rels & np.uint64(sum(1 << s for s in range(1 << n) if ((s >> u) ^ (s >> v)) & 1))))
        keys, counts = np.unique(np.stack(cols, axis=1), axis=0, return_counts=True)
        out[n] = {"knot_sets": int(len(rel)), "relations": int(len(rels)), "keys": int(len(keys)),
                  "colliding_groups": int((counts > 1).sum())}
    return out


def first_collision(law_excl, n, all_orders):
    ks = []
    for t in itertools.combinations(range(n), 3):
        for o in (set(itertools.permutations(t)) if all_orders else {t}):
            ks.append(sum(1 << s for s in range(1 << n) if tuple((s >> u) & 1 for u in o) not in law_excl))
    ks = sorted(set(ks))
    full = (1 << (1 << n)) - 1
    seen, fr = {full}, [full]
    while fr:
        nx = []
        for r in fr:
            for m in ks:
                q = r & m
                if q and q not in seen:
                    seen.add(q)
                    nx.append(q)
        fr = nx
    keys = {}
    for r in seen:
        sts = [s for s in range(1 << n) if (r >> s) & 1]
        k = (len(sts), tuple(sum((s >> u) & 1 for s in sts) for u in range(n)),
             tuple(sum(((s >> u) ^ (s >> v)) & 1 for s in sts) for u, v in itertools.combinations(range(n), 2)))
        keys.setdefault(k, []).append(r)
    return {"relations": len(seen), "keys": len(keys)}


def main():
    out = {"L1": l1(), "laws": {}}
    for name, law in LAWS.items():
        out["laws"][name] = [law_row(name, law, w) for w in range(3, 13)]
    nae = {r["width"]: r for r in out["laws"]["NAE"]}
    p2 = {r["width"]: r for r in out["laws"]["signed NAE, place 2 odd"]}
    out["agreeing_signs_vs_NAE"] = {w: {"same_per_site": abs(nae[w]["per_site"] - p2[w]["per_site"]) < 1e-9,
                                        "same_gap": nae[w].get("gap") == p2[w].get("gap") or
                                        (nae[w].get("gap") and p2[w].get("gap") and abs(nae[w]["gap"] - p2[w]["gap"]) < 1e-9)}
                                    for w in range(3, 13)}
    out["single_distinction_modes"] = {"OR": [coupled_modes("OR", w) for w in (6, 9, 10)],
                                       "not-exactly-two": [coupled_modes("not-exactly-two", 10)]}
    out["census"] = {"OR": census_or(),
                     "not-exactly-two n=5": first_collision(LAWS["not-exactly-two"][0], 5, False),
                     "not-exactly-two n=4": first_collision(LAWS["not-exactly-two"][0], 4, False),
                     "parity n=4": first_collision(LAWS["parity"][0], 4, False),
                     "distance-two n=4 (all orders)": first_collision({(0, 0, 0), (0, 1, 1)}, 4, True)}
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
