#!/usr/bin/env python3
"""Independent check of the shape scan; imports no producer code.

Parses raw_rows.jsonl and the frozen contract, recomputes every estimate and decision with its own code, and compares
them with result.json. The Coulomb-gas family is re-implemented (checked first against Arguin's percolation values),
the recorded best fit is re-evaluated, and an independent grid must find no point with chi-square per degree of
freedom below 10. Three small tori are replayed in pure Python with a different method: consistency of fair
not-all-equal by unit propagation; the contractible fraction of the twisted cyclic edges by an explicit strong-component
search; untwisted wrapping. A deliberately tightened scale tolerance must change the verdict.
"""

from __future__ import annotations

import cmath
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/NAE-INVARIANT-20261022-001B/NAE-INVARIANT-20261022-001B-E001_shape_scan"


# ------------------------------------------------------------------ Coulomb gas, written afresh

def eta2(tau: complex) -> float:
    q = cmath.exp(2j * math.pi * tau)
    p = 1
    for n in range(1, 400):
        p *= 1 - q ** n
    return abs(cmath.exp(2j * math.pi * tau / 24) * p) ** 2


def gauss(m, mp, g, tau, e2):
    tR, tI = tau.real, tau.imag
    return math.sqrt(g / tI) / e2 * math.exp(-math.pi * g * ((m * tI) ** 2 + (mp - m * tR) ** 2) / tI)


class Torus:
    def __init__(self, Lh, Lv, s, obs=None, n=None):
        self.Lh, self.Lv, self.s, self.n = Lh, Lv, s, n
        self.tau = complex(s / Lh, Lv / Lh)
        self.e2 = eta2(self.tau)
        self.obs = obs
        self.cache = {}

    def par(self, a, b):
        return (a * self.Lh + b * (self.s + self.Lv)) & 1

    def probs(self, g, eo, ee, R=14, A=4, K=12):
        if g not in self.cache:
            self.cache[g] = sum(gauss(m, mp, g, self.tau, self.e2) * (-1) ** math.gcd(m, mp)
                                for m in range(-R, R + 1) for mp in range(-R, R + 1))
        w0 = self.cache[g] / 2
        wind = {}
        for a in range(A + 1):
            for b in range(-A, A + 1):
                if math.gcd(a, b) != 1 or (a == 0 and b != 1):
                    continue
                e = eo if self.par(a, b) else ee
                wind[(a, b)] = sum(gauss(-k * b, k * a, g, self.tau, self.e2) * (math.cos(math.pi * e * k) - (-1) ** k)
                                   for k in range(-K, K + 1) if k)
        T = 2 * w0 + sum(wind.values())
        return w0 / T, {c: v / T for c, v in wind.items()}


def chi2(tori, g, eo, ee):
    tot = 0.0
    for t in tori:
        p0, wind = t.probs(g, eo, ee)
        for key, p in (("P0", p0), ((1, 0), wind[(1, 0)]), ((0, 1), wind[(0, 1)]), ((1, 1), wind[(1, 1)]), ((1, -1), wind[(1, -1)])):
            p = min(max(p, 0.0), 1.0)
            tot += (t.obs[key] - p) ** 2 / max(max(p, 1e-5) * (1 - p) / t.n, 1e-12)
    return tot


# ------------------------------------------------------------------ independent replays

class Lattice:
    def __init__(self, Lh, Lv, s):
        self.Lh, self.Lv, self.s, self.V = Lh, Lv, s, Lh * Lv
        self.edges = []      # (v, w, offset (a, b))
        for v in range(self.V):
            x, y = v % Lh, v // Lh
            self.edges.append((v, y * Lh + (x + 1) % Lh, ((x + 1) // Lh, 0)))
            if y + 1 < Lv:
                self.edges.append((v, v + Lh, (0, 0)))
            else:
                # (x, Lv) = (x - s, 0) + w2: wrap (q = 1) then fold x - s into [0, Lh)
                X = x - s
                r = X // Lh
                self.edges.append((v, X - r * Lh, (r, 1)))

    def par(self, a, b):
        return (a * self.Lh + b * (self.s + self.Lv)) & 1


def propagate_world(lat, spokes):
    nb = [[] for _ in range(lat.V)]
    for (v, w, _o), x in zip(lat.edges, spokes):
        nb[v].append((w, x))
        nb[w].append((v, x))
    val = [-1] * lat.V
    for v in range(lat.V):
        if val[v] >= 0:
            continue
        done = False
        for start in (0, 1):
            trial, stack, ok = {v: start}, [v], True
            while stack and ok:
                u = stack.pop()
                for w, x in nb[u]:
                    if trial[u] == x:
                        need = 1 - x
                        have = trial.get(w, val[w] if val[w] >= 0 else None)
                        if have is None:
                            trial[w] = need
                            stack.append(w)
                        elif have != need:
                            ok = False
                            break
            if ok:
                for u, b in trial.items():
                    val[u] = b
                done = True
                break
        if not done:
            return False
    return True


def scc(n, adj):
    """Iterative Tarjan; returns component labels."""
    index, low, comp, on, st = [-1] * n, [0] * n, [-1] * n, [False] * n, []
    c = nc = 0
    for r in range(n):
        if index[r] >= 0:
            continue
        work = [(r, 0)]
        index[r] = low[r] = c; c += 1; st.append(r); on[r] = True
        while work:
            v, i = work[-1]
            if i < len(adj[v]):
                work[-1] = (v, i + 1)
                w = adj[v][i]
                if index[w] < 0:
                    index[w] = low[w] = c; c += 1; st.append(w); on[w] = True
                    work.append((w, 0))
                elif on[w]:
                    low[v] = min(low[v], index[w])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    while True:
                        w = st.pop(); on[w] = False; comp[w] = nc
                        if w == v:
                            break
                    nc += 1
    return comp


def contractible(lat, chosen):
    """True when every cluster of the chosen edges has a trivial homology image."""
    parent, pot = list(range(lat.V)), [(0, 0)] * lat.V

    def find(u):
        acc = (0, 0)
        path = []
        while parent[u] != u:
            path.append(u)
            u = parent[u]
        for node in reversed(path):
            p = pot[node]
            acc = (acc[0] + p[0], acc[1] + p[1])
            pot[node] = acc
            parent[node] = u
        return u

    for (v, w, off), use in zip(lat.edges, chosen):
        if not use:
            continue
        rv, rw = find(v), find(w)
        pv, pw = pot[v], pot[w]
        d = (pv[0] + off[0] - pw[0], pv[1] + off[1] - pw[1])
        if rv == rw:
            if d != (0, 0):
                return False
        else:
            parent[rw] = rv
            pot[rw] = d
    return True


def replay_twisted_contractible(Lh, Lv, s, n, seed):
    lat = Lattice(Lh, Lv, s)
    rng = random.Random(seed)
    contr = 0
    for _ in range(n):
        spokes = [rng.getrandbits(1) for _ in lat.edges]
        adj = [[] for _ in range(2 * lat.V)]
        for (v, w, _o), x in zip(lat.edges, spokes):
            adj[2 * v + x].append(2 * w + 1 - x)
            adj[2 * w + x].append(2 * v + 1 - x)
        comp = scc(2 * lat.V, adj)
        chosen = [comp[2 * v + x] == comp[2 * w + 1 - x] for (v, w, _o), x in zip(lat.edges, spokes)]
        contr += contractible(lat, chosen)
    return contr / n


def replay_untwisted_either(Lh, Lv, s, n, seed):
    lat = Lattice(Lh, Lv, s)
    rng = random.Random(seed)
    wrap = 0
    for _ in range(n):
        bits = [rng.getrandbits(1) for _ in lat.edges]
        adj = [[] for _ in range(lat.V)]
        for (v, w, _o), b in zip(lat.edges, bits):
            (adj[v].append(w) if b else adj[w].append(v))
        comp = scc(lat.V, adj)
        chosen = [comp[v] == comp[w] for (v, w, _o) in lat.edges]
        wrap += not contractible(lat, chosen)
    return wrap / n


# ------------------------------------------------------------------ recomputation

def wls(xs, ys, ses):
    w = [1 / s ** 2 for s in ses]
    S = sum(w); Sx = sum(a * b for a, b in zip(w, xs)); Sy = sum(a * b for a, b in zip(w, ys))
    Sxx = sum(a * b * b for a, b in zip(w, xs)); Sxy = sum(a * b * c for a, b, c in zip(w, xs, ys))
    D = S * Sxx - Sx ** 2
    return (Sxx * Sy - Sx * Sxy) / D, (S * Sxy - Sx * Sy) / D, math.sqrt(Sxx / D), math.sqrt(S / D)


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "raw_rows.jsonl").read_text().splitlines()]
    assert contract["status"] == "Frozen" and len(rows) == result["rows"] and result["controls_ok"]
    ngz = contract["predictions"]["ngz_values"]
    by = {}
    for r in rows:
        by.setdefault(r["family"], []).append(r)

    # estimates and controls
    for r in rows:
        if r["mode"] != "twisted":
            continue
        n = r["samples"]
        assert r["contr"] + r["cross"] + r["wind_odd"] + r["wind_even"] == n
        assert sum(r["classes"].values()) <= r["wind_odd"] + r["wind_even"]
        if r["family"] == "control_bipartite":
            assert r["cons"] == n
            continue
        assert r["mismatch"] == 0 and r["inc_scc"] == r["inc_topo"] == n - r["cons"]
        assert abs(r["contr"] - r["cross"]) <= 4 * math.sqrt(r["contr"] + r["cross"]), r["label"]
        assert r["cons"] == r["contr"] + r["wind_even"]          # Theorem 5 of the proof, row by row
        p = r["cons"] / n
        assert abs(-math.log2(p) - r["E"]) < 1e-12
        assert abs(math.sqrt((1 - p) / (n * p)) / math.log(2) - r["se_E"]) < 1e-12

    # H_shape and H_rotation
    def last_two(fam):
        fr = sorted(by[fam], key=lambda r: r["Lh"] * r["Lv"])
        return fr[-2], fr[-1]

    def shape_ok(allow):
        ok = True
        for fam in ("F_sq11", "F_r53", "F_r3", "F_r2s", "F_r2l", "F_r4s", "F_r4l", "F_sh11", "F_sh10"):
            a, b = last_two(fam)
            ok &= abs(b["E"] - a["E"]) <= 3 * math.hypot(a["se_E"], b["se_E"]) + allow
        pr = {}
        for L in (129, 257):
            two = [r for r in by["F_sq10"] if r["Lh"] == L]
            pr[L] = (sum(r["E"] for r in two) / 2, 0.5 * math.sqrt(sum(r["se_E"] ** 2 for r in two)))
        ok &= abs(pr[257][0] - pr[129][0]) <= 3 * math.hypot(pr[257][1], pr[129][1]) + allow
        return ok

    assert shape_ok(0.02) == result["H_shape"]["holds"]
    sq = max(by["F_sq11"], key=lambda r: r["Lh"])
    rot_ok = True
    for fam in ("F_rot21", "F_rot32"):
        w = [1 / r["se_E"] ** 2 for r in by[fam]]
        m = sum(a * r["E"] for a, r in zip(w, by[fam])) / sum(w)
        rot_ok &= abs(m - sq["E"]) <= 3 * math.hypot(math.sqrt(1 / sum(w)), sq["se_E"]) + 0.02
    assert rot_ok == result["H_rotation"]["holds"]

    # H_family: known answer, recorded optimum, independent grid
    perc = Torus(1, 1, 0)
    p0, wind = perc.probs(2 / 3, 2 / 3, 2 / 3)
    assert abs(p0 - 0.30954) < 2e-4 and abs(wind[(1, 0)] - 0.16942) < 2e-4 and abs(wind[(1, 1)] - 0.020980) < 2e-5
    tori = []
    for fam in ("F_sq11", "F_r53", "F_r3", "F_r2s", "F_r2l", "F_r4s", "F_r4l", "F_sh11", "F_sh10"):
        r = max(by[fam], key=lambda r: r["Lh"] * r["Lv"])
        tori.append(r)
    tori += [r for r in by["F_sq10"] if r["Lh"] == 257]
    T = []
    for r in tori:
        obs = {"P0": r["contr"] / r["samples"]}
        for c in ((1, 0), (0, 1), (1, 1), (1, -1)):
            obs[c] = r["classes"].get(f"{c[0]},{c[1]}", 0) / r["samples"]
        T.append(Torus(r["Lh"], r["Lv"], r["s"], obs, r["samples"]))
    dof = 5 * len(T) - 3
    bf = result["H_family"]["best_fit"]
    c_rec = chi2(T, bf["gs"], bf["e_odd"], bf["e_even"])
    assert abs(c_rec - result["H_family"]["chi2"]) <= 1e-6 * max(1.0, c_rec), (c_rec, result["H_family"]["chi2"])
    grid_min = min(chi2(T, 0.5 + gi / 16, oi / 8, ei / 8) for gi in range(9) for oi in range(9) for ei in range(9))
    holds = result["H_family"]["chi2"] / dof >= 10
    assert holds == result["H_family"]["holds"]
    if holds:
        assert grid_min / dof >= 10
    assert grid_min >= result["H_family"]["chi2"] - 1e-6

    # H_class
    mass = sorted(by["F_mass"], key=lambda r: r["Lh"])
    (L1, r1), (L2, r2) = (mass[-2]["Lh"], mass[-2]), (mass[-1]["Lh"], mass[-1])
    M1, M2 = r1["m1"] / r1["samples"], r2["m1"] / r2["samples"]
    s1 = math.sqrt((r1["m2"] / r1["samples"] - M1 ** 2) / r1["samples"])
    s2 = math.sqrt((r2["m2"] / r2["samples"] - M2 ** 2) / r2["samples"])
    df = math.log(M2 / M1) / math.log(L2 / L1)
    sdf = math.hypot(s1 / M1, s2 / M2) / math.log(L2 / L1)
    a_ok = abs(df - ngz["fractal_dimension"]) <= 3 * sdf + 0.02
    u = next(r for r in by["F_untwisted"] if r["Lh"] == 256)
    n = u["samples"]
    cl = {tuple(map(int, k.split(","))): v for k, v in u["classes"].items()}
    vals = {"either": 1 - u["contr"] / n,
            "one_direction": ((u["cross"] + sum(v for (a, b), v in cl.items() if a)) / n + (u["cross"] + sum(v for (a, b), v in cl.items() if b)) / n) / 2,
            "both": (u["cross"] + sum(v for (a, b), v in cl.items() if a and b)) / n}
    refs = {"either": ngz["wrap_either"], "one_direction": ngz["wrap_one_direction"], "both": ngz["wrap_both"]}
    b_ok = all(abs(vals[k] - refs[k]) <= 3 * math.sqrt(vals[k] * (1 - vals[k]) / n) + 0.01 for k in vals)
    arms = by["F_arms"][0]

    def expo(chunks, col):
        tot = sum(c["samples"] for c in chunks)
        pts = [(math.log(R), math.log(sum(c["survival"][str(R)][col] for c in chunks) / tot)) for R in (16, 32, 64, 128, 256, 512)]
        mx = sum(p[0] for p in pts) / 6
        my = sum(p[1] for p in pts) / 6
        return -sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)

    ch = arms["chunks"]
    xb = expo(ch, 2)
    jk = [expo(ch[:i] + ch[i + 1:], 2) for i in range(len(ch))]
    sb = math.sqrt((len(jk) - 1) / len(jk) * sum((j - sum(jk) / len(jk)) ** 2 for j in jk))
    c_ok = abs(xb - 5 / 24) > 3 * sb
    box = by["F_box"][0]
    d_ok = abs(box["central_cyclic"] / box["central_edges"] - 0.5) <= 0.005
    assert (a_ok and b_ok and c_ok and d_ok) == result["H_class"]["holds"]
    assert abs(xb - result["H_class"]["arm_exponents"]["both"]["exponent"]) < 1e-4

    # candidates
    pairs = {}
    for L in (65, 129, 257):
        two = [r for r in by["F_sq10"] if r["Lh"] == L]
        pairs[L] = (sum(r["E"] for r in two) / 2, 0.5 * math.sqrt(sum(r["se_E"] ** 2 for r in two)))
    Einf, _sl, sE, _ss = wls([1 / L for L in pairs], [v[0] for v in pairs.values()], [v[1] for v in pairs.values()])
    assert abs(Einf - result["candidates"]["half_bit"]["E_inf"]) < 1e-4
    assert (abs(Einf - 0.5) <= 3 * sE) == result["candidates"]["half_bit"]["accepted"]
    cyl = sorted(by["F_cyl65"], key=lambda r: r["Lv"])
    _i, sl, _a, sls = wls([r["Lv"] / r["Lh"] for r in cyl], [r["E"] for r in cyl], [r["se_E"] for r in cyl])
    x, xs = sl * math.log(2) / (2 * math.pi), sls * math.log(2) / (2 * math.pi)
    assert abs(x - result["candidates"]["sixteenth"]["x"]) < 1e-4
    assert (abs(x - 1 / 16) <= 3 * xs + 0.001) == result["candidates"]["sixteenth"]["accepted"]
    assert (abs(xb - ngz["beta_over_nu"]) <= 3 * sb + 0.005) == result["candidates"]["arms_equal_cluster"]["accepted"]

    # verdict
    primary = {"H_shape": shape_ok(0.02), "H_rotation": rot_ok, "H_family": holds, "H_class": a_ok and b_ok and c_ok and d_ok}
    assert primary == result["primary"]
    if all(primary.values()):
        assert result["verdict"] == "supported"

    # independent replays
    replay = {}
    for (Lh, Lv) in ((9, 9), (9, 8)):
        rec = next(r for r in by["F_small"] if (r["Lh"], r["Lv"]) == (Lh, Lv))
        lat = Lattice(Lh, Lv, 0)
        rng = random.Random(f"replay-{Lh}x{Lv}")
        m = 4000
        good = sum(propagate_world(lat, [rng.getrandbits(1) for _ in lat.edges]) for _ in range(m))
        p, q = good / m, rec["cons"] / rec["samples"]
        assert abs(p - q) <= 5 * math.sqrt(q * (1 - q) * (1 / m + 1 / rec["samples"])), (p, q)
        replay[f"consistency {Lh}x{Lv}"] = (round(p, 4), round(q, 4))
    rec = next(r for r in by["F_small"] if (r["Lh"], r["Lv"]) == (9, 9))
    m = 2000
    p, q = replay_twisted_contractible(9, 9, 0, m, 99), rec["contr"] / rec["samples"]
    assert abs(p - q) <= 5 * math.sqrt(q * (1 - q) * (1 / m + 1 / rec["samples"])), (p, q)
    replay["contractible 9x9"] = (round(p, 4), round(q, 4))
    rec = next(r for r in by["F_untwisted"] if r["Lh"] == 17)
    p, q = replay_untwisted_either(17, 17, 0, m, 101), 1 - rec["contr"] / rec["samples"]
    assert abs(p - q) <= 5 * math.sqrt(q * (1 - q) * (1 / m + 1 / rec["samples"])), (p, q)
    replay["untwisted either 17x17"] = (round(p, 4), round(q, 4))

    # tightened tolerance changes the verdict
    assert shape_ok(-1.0) is False
    print(f"checked: {len(rows)} rows, verdict {result['verdict']}, primary {primary}, family chi2/dof "
          f"{result['H_family']['chi2'] / dof:.1f} (independent grid min {grid_min / dof:.1f}), d_f {df:.4f}+-{sdf:.4f}, "
          f"wrapping {[round(v, 4) for v in vals.values()]}, both-arm exponent {xb:.4f}+-{sb:.4f}, half-bit E_inf {Einf:.4f}+-{sE:.4f}, "
          f"x {x:.4f}+-{xs:.4f}; replay {replay}; tightened tolerance rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
