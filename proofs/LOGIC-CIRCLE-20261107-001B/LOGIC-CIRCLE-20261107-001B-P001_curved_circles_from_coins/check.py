"""Checker for LOGIC-CIRCLE-20261107-001B-P001 (curved circles from coins).

Finite validation of proof.md; it does not replace the proofs, and it does not prove the cited limit theorem (Seppalainen
1997), whose constants it only compares with finite samples. Writes result.json next to this file.
Run: python3 -B check.py   (needs numpy, scipy, mpmath)"""
from __future__ import annotations
import json, math, random, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import split_lib as sl

def check_formula(rng, mode="strict"):
    """Theorem 1: breadth-first distance = |dx| + |dy| - longest strictly increasing chain of correctly oriented squares."""
    bad = tot = 0
    for p in (0.5, 0.25, 0.9):
        for _ in range(3):
            L = 36
            D = sl.environment(L, p, rng)
            adj, elist, idx = sl.graph(D)
            for u in ((18, 18), (5, 30), (30, 7)):
                d = sl.bfs(adj, idx(*u))
                if mode == "strict":
                    f = sl.formula_distances(D, u)
                elif mode == "weak":
                    f = weak_formula(D, u)
                else:
                    f = unoriented_formula(D, u)
                for x in range(L + 1):
                    for y in range(L + 1):
                        tot += 1
                        bad += d[idx(x, y)] != f[x, y]
    return bad, tot

def weak_formula(D, u):
    """Control: weakly increasing chains (a square may share a row or column with the previous one)."""
    out = sl.formula_distances(D, u).copy()
    L = D.shape[0]; ux, uy = u
    F = D[ux:, uy:]
    A, B = F.shape
    T = np.zeros((A + 1, B + 1), dtype=np.int32)
    for a in range(1, A + 1):
        for b in range(1, B + 1):
            T[a, b] = max(T[a - 1, b], T[a, b - 1]) + F[a - 1, b - 1]
    for wx in range(ux, L + 1):
        for wy in range(uy, L + 1):
            out[wx, wy] = (wx - ux) + (wy - uy) - T[wx - ux, wy - uy]
    return out

def unoriented_formula(D, u):
    """Control: read NE squares (the wrong orientation) in the NW quadrant."""
    out = sl.formula_distances(D, u).copy()
    L = D.shape[0]; ux, uy = u
    F = D[:ux, uy:][::-1, :]          # NE squares read in the NW quadrant: the wrong orientation
    T = sl.chain_table(F)
    for wx in range(0, ux + 1):
        for wy in range(uy, L + 1):
            out[wx, wy] = (ux - wx) + (wy - uy) - T[ux - wx, wy - uy]
    return out

def check_constants(rng):
    rows, ok = [], True
    n = 3000
    for p in (0.5, 0.25):
        F = (rng.random((2 * n, n)) < p).astype(np.int8)
        T = sl.chain_table(F)
        a, b = T[n, n] / n, T[2 * n, n] / n
        ga, gb = sl.g_strict(1, 1, p), sl.g_strict(2, 1, p)
        good = abs(a - ga) < 0.02 and abs(b - gb) < 0.02
        ok &= good
        rows.append({"p": p, "n": n, "chain_n_n_over_n": round(a, 4), "limit": round(ga, 4), "chain_2n_n_over_n": round(b, 4),
                     "limit_2_1": round(gb, 4), "ok": bool(good)})
    return ok, rows

def check_bonds(rng, factor=2):
    rows, ok = [], True
    dirs = [(1, 0), (1, 1), (2, 1), (1, 2), (-1, 1), (-2, 1), (3, 1)]
    for p in (0.5, 0.25):
        devs_by_n = {}
        for n in (20, 40, 80):
            L = 2 * n + 30
            D = sl.environment(L, p, rng)
            adj, elist, idx = sl.graph(D)
            eid = {}
            for k, (a, b) in enumerate(elist):
                eid[(a, b)] = k; eid[(b, a)] = k
            u = (L // 2, L // 2)
            e0 = eid[(idx(*u), idx(u[0], u[1] + 1))]
            dist_e0 = bfs_multi(adj, [idx(*u), idx(u[0], u[1] + 1)])
            devs = []
            for z in dirs:
                nz = max(abs(z[0]), abs(z[1]))
                w = (u[0] + round(n * z[0] / nz), u[1] + round(n * z[1] / nz))
                f = eid[(idx(*w), idx(w[0], w[1] + 1))]
                cyc = sl.min_cycle_through(adj, elist, e0, f)
                delta = cyc - 1
                dd = min(dist_e0[idx(*w)], dist_e0[idx(w[0], w[1] + 1)])
                pred = 2 * sl.c_shape((w[0] - u[0]) / n, (w[1] - u[1]) / n, p) * n
                lower_ok = delta >= 2 * dd + 1
                upper_ok = delta <= factor * dd + 8
                ok &= lower_ok and upper_ok
                devs.append(abs(delta / pred - 1))
                rows.append({"p": p, "n": n, "direction": z, "delta": delta, "dual_distance": dd, "predicted_2c": round(pred, 2),
                             "lower_bound_2d_plus_1": bool(lower_ok), "within_2d_plus_8": bool(upper_ok)})
            devs_by_n[n] = float(np.mean(devs))
        shrinking = devs_by_n[80] < devs_by_n[20]
        ok &= shrinking
        rows.append({"p": p, "mean_relative_deviation_by_n": {k: round(v, 4) for k, v in devs_by_n.items()}, "shrinking": bool(shrinking)})
    return ok, rows

def bfs_multi(adj, sources):
    from collections import deque
    dist = [-1] * len(adj); q = deque()
    for s in sources:
        dist[s] = 0; q.append(s)
    while q:
        x = q.popleft()
        for v, _ in adj[x]:
            if dist[v] < 0:
                dist[v] = dist[x] + 1; q.append(v)
    return dist

def check_shape(p_circle=0.5):
    """The curved part of the boundary of {c_p <= 1} in the open first quadrant: an arc of (s + t - (1 - p))^2 = 4 p s t,
    the circle (2s - 1)^2 + (2t - 1)^2 = 1 when p = 1/2; elsewhere c_p = max(s, t)."""
    worst_conic, worst_circle, worst_flat = 0.0, 0.0, 0.0
    for p in (0.5, 0.25, 0.1):
        for k in range(1, 2000):
            th = (math.pi / 2) * k / 2000
            s, t = math.cos(th), math.sin(th)
            c = sl.c_shape(s, t, p)
            s, t = s / c, t / c      # boundary point
            if p * s <= t <= s / p:
                worst_conic = max(worst_conic, abs((s + t - (1 - p)) ** 2 - 4 * p * s * t))
                if p == p_circle:
                    worst_circle = max(worst_circle, abs((2 * s - 1) ** 2 + (2 * t - 1) ** 2 - 1))
            else:
                worst_flat = max(worst_flat, abs(max(s, t) - 1))
    return worst_conic < 1e-12 and worst_circle < 1e-12 and worst_flat < 1e-12, (worst_conic, worst_circle, worst_flat)

def check_pi():
    import mpmath as mp
    mp.mp.dps = 30
    I = mp.quad(lambda u: u ** 2 * (1 + u ** 4) ** mp.mpf(-1.5), [1 / mp.sqrt(2), mp.sqrt(2)])
    closed = 2 + 6 / mp.sqrt(5) - 4 * mp.sqrt(2) * I
    numeric = sl.circle_pi(0.5)
    table = {str(p): round(sl.circle_pi(p), 5) for p in (0.0, 0.05, 0.1, 0.25, 0.5)}
    ok = abs(float(closed) - numeric) < 1e-6 and abs(table["0.0"] - 3) < 1e-6
    return ok, {"closed_form": float(closed), "polygonal": numeric, "I": float(I), "pi_by_p": table}

def check_voronoi_adjacent(rng):
    """Integrability lemma of Theorem 5: two Voronoi edges sharing a vertex have bond distance 2 (their duals lie on a
    Delaunay triangle)."""
    adj, elist, pts, tri = sl.voronoi_dual(30, rng)
    eid = {e: k for k, e in enumerate(elist)}
    worst, n = 0, 0
    for s in tri.simplices[:300]:
        a, b, c = sorted(s)
        e, f = eid[(a, b)], eid[(b, c)]
        # two edges of one triangle share a vertex: least cycle through both is the triangle
        cyc = triangle_cycle(adj, elist, e, f)
        worst = max(worst, cyc - 1); n += 1
    return worst == 2, {"pairs": n, "largest_delta": worst}

def triangle_cycle(adj, elist, e, f):
    (a, b), (c, d) = elist[e], elist[f]
    shared = ({a, b} & {c, d}).pop()
    x = a if b == shared else b
    y = c if d == shared else d
    # shortest x-y path avoiding the shared vertex and the two edges, plus the two edges
    from collections import deque
    dist = {x: 0}; q = deque([x])
    while q:
        v = q.popleft()
        for w, k in adj[v]:
            if w == shared or k in (e, f) or w in dist:
                continue
            dist[w] = dist[v] + 1; q.append(w)
    return dist[y] + 2

def main():
    t0 = time.time()
    rng = np.random.default_rng(20261107)
    random.seed(20261107)
    res = {}
    bad, tot = check_formula(rng)
    res["exact_formula"] = {"mismatches": int(bad), "targets": int(tot)}
    c_ok, res["seppalainen_constants"] = check_constants(rng)
    b_ok, res["bond_distances"] = check_bonds(rng)
    s_ok, res["shape_equations_max_error"] = check_shape()
    p_ok, res["pi"] = check_pi()
    v_ok, res["voronoi_adjacent_edges"] = check_voronoi_adjacent(rng)
    controls = {}
    bw, tw = check_formula(np.random.default_rng(1), mode="weak")
    controls["weak_chains"] = {"rejected": bool(bw > 0), "mismatches": int(bw)}
    bu, tu = check_formula(np.random.default_rng(2), mode="unoriented")
    controls["wrong_orientation_in_NW_quadrant"] = {"rejected": bool(bu > 0), "mismatches": int(bu)}
    sh_ok, errs = check_shape(p_circle=0.25)
    controls["circle_claimed_at_p_1_4"] = {"rejected": bool(not sh_ok), "max_errors": errs}
    b1_ok, _ = check_bonds(np.random.default_rng(3), factor=1)
    controls["bond_distance_equal_to_dual_distance"] = {"rejected": bool(not b1_ok)}
    res["controls"] = controls
    checks = {"exact_formula": bad == 0, "seppalainen_constants": c_ok, "bond_distances": b_ok, "shape": s_ok, "pi": p_ok,
              "voronoi_adjacent": v_ok}
    checks = {k: bool(v) for k, v in checks.items()}
    res["checks"] = checks
    res["all_checks_pass"] = all(checks.values())
    res["all_controls_rejected"] = all(bool(c["rejected"]) for c in controls.values())
    res["theorem_flags"] = {
        "exact_distance_formula": "argued-in-prose (Theorem 1); checked on 36,963 targets",
        "bond_distance_limit": "argued-in-prose (Theorems 2-3), conditional on the cited theorem of Seppalainen (1997)",
        "voronoi_round": "argued-in-prose (Theorem 5), conditional on the cited results of Vahidi-Asl and Wierman and Kingman's theorem",
    }
    res["runtime_seconds"] = round(time.time() - t0, 1)
    manifest = json.loads((HERE / "manifest.json").read_text())
    failures = [k for k, v in checks.items() if not v] + [f"control {k} not rejected" for k, v in controls.items() if not v["rejected"]]
    out = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
           "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
           "checks": checks, "failures": failures, "details": res}
    (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({"checks": checks, "controls": {k: bool(v["rejected"]) for k, v in controls.items()}, "runtime": res["runtime_seconds"]}, indent=1))
    return 0 if res["all_checks_pass"] and res["all_controls_rejected"] else 1

if __name__ == "__main__":
    sys.exit(main())
