"""Checker for LOGIC-CIRCLE-20261107-001A-P001 (polygons: the circle of a periodic or line-arrangement law and its pi).

Finite validation of proof.md; it does not replace the proofs. Writes result.json next to this file.
Run: python3 -B check.py   (needs numpy)"""
from __future__ import annotations
import json, math, random, sys, time
from fractions import Fraction
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import circle_lib as cl

LAVES_DEGREES = {"4.4.4.4": [4], "3.3.3.3.3.3": [3], "6.6.6": [6], "3.6.3.6": [3, 6], "3.12.12": [3, 12], "4.8.8": [4, 8],
                 "4.6.12": [4, 6, 12], "3.4.6.4": [3, 4, 6], "3.3.4.3.4": [3, 4], "3.3.3.4.4": [3, 4], "3.3.3.3.6": [3, 6]}
# pi of the circle of the parity law on each tiling ("A": the Archimedean tiling, "L": its Laves dual) and the number of sides
EXPECTED = {
    ("A", "4.4.4.4"): (Fraction(4), 4), ("L", "4.4.4.4"): (Fraction(4), 4),
    ("A", "3.3.3.3.3.3"): (Fraction(3), 6), ("L", "3.3.3.3.3.3"): (Fraction(3), 6),
    ("A", "6.6.6"): (Fraction(3), 6), ("L", "6.6.6"): (Fraction(3), 6),
    ("A", "3.6.3.6"): (Fraction(3), 6), ("L", "3.6.3.6"): (Fraction(3), 6),
    ("A", "3.12.12"): (Fraction(3), 6), ("L", "3.12.12"): (Fraction(3), 6),
    ("A", "4.8.8"): (Fraction(4), 4), ("L", "4.8.8"): (Fraction(10, 3), 8),
    ("A", "4.6.12"): (Fraction(3), 6), ("L", "4.6.12"): (Fraction(16, 5), 12),
    ("A", "3.4.6.4"): (Fraction(3), 6), ("L", "3.4.6.4"): (Fraction(3), 6),
    ("A", "3.3.4.3.4"): (Fraction(10, 3), 8), ("L", "3.3.4.3.4"): (Fraction(10, 3), 8),
    ("A", "3.3.3.4.4"): (Fraction(11, 3), 6), ("L", "3.3.3.4.4"): (Fraction(7, 2), 6),
    ("A", "3.3.3.3.6"): (Fraction(3), 6), ("L", "3.3.3.3.6"): (Fraction(16, 5), 12),
}
EXCESS_BOUND = 10   # |delta - 2 ||x||_P| on every sampled pair (Theorem 1 gives some constant; 10 is what the patches need)

def lat(g, p):
    return np.linalg.solve(np.array([g.a1, g.a2]).T, p)

def laws():
    out = []
    for mk in cl.ARCHIMEDEAN:
        g = mk()
        h = cl.dual(g)
        key = g.name.split()[0]
        out.append((("A", key), g, h))   # law on g; its bonds are cycles of h
        out.append((("L", key), h, g))   # law on h; its bonds are cycles of g
    return out

def check_structure():
    rows, ok = [], True
    for mk in cl.ARCHIMEDEAN:
        g = mk()
        key = g.name.split()[0]
        conf_ok = all(cl.canonical_conf(c) == cl.canonical_conf(cl.EXPECTED[key]) for c in cl.face_sizes_at_vertices(g))
        h = cl.dual(g)
        deg_ok = sorted(set(cl.degrees(h))) == LAVES_DEGREES[key]
        ok &= conf_ok and deg_ok
        rows.append({"tiling": g.name, "vertex_configuration_ok": conf_ok, "dual_degrees": sorted(set(cl.degrees(h))), "dual_degrees_ok": deg_ok})
    return ok, rows

def polygon_report(P):
    return [[str(x), str(y)] for x, y in P]

def check_table(L):
    ok, rows = True, []
    for key, law, other in L:
        P = cl.velocity_polygon(other)
        pi = cl.self_pi(P)
        rational = all(isinstance(c, Fraction) for v in P for c in v)
        symmetric = set(P) == {(-x, -y) for x, y in P}
        exp_pi, exp_sides = EXPECTED[key]
        golab = Fraction(3) <= pi <= Fraction(4) and ((pi == 3) <= (len(P) == 6)) and ((pi == 4) <= (len(P) == 4))
        good = rational and symmetric and pi == exp_pi and len(P) == exp_sides and golab
        ok &= good
        rows.append({"law": f"{key[0]} {key[1]}", "knot_sizes": sorted(set(cl.degrees(law))), "sides": len(P), "pi": str(pi),
                     "pi_float": float(pi), "circle_polygon_lattice_coords": polygon_report(P), "ok": bool(good)})
    return ok, rows

def check_karp(L, rng):
    worst = 0.0
    for key, law, other in L:
        P = cl.velocity_polygon(other)
        for _ in range(16):
            w = (rng.uniform(-1, 1), rng.uniform(-1, 1))
            h_poly = max(float(v[0]) * w[0] + float(v[1]) * w[1] for v in P)
            h_karp = cl.max_mean_cycle(other, w)
            worst = max(worst, abs(h_poly - h_karp))
    return worst < 1e-9, worst

def bond_samples(law_dual, P, R, npairs, rnd, far_only=False):
    """Exact bond distances (least cycles of the dual) from a central variable to sampled variables."""
    fs = [(float(a), float(b)) for a, b in cl.facets(P)]
    idx, adj, pos, elist = cl.patch(law_dual, R)
    latc = np.array([lat(law_dual, (pos[a] + pos[b]) / 2) for a, b in elist])
    c0 = min(range(len(elist)), key=lambda k: np.linalg.norm(latc[k] - np.array([0.3, 0.2])))
    a, b = elist[c0]
    cand = []
    for k in range(len(elist)):
        x = latc[k] - latc[c0]
        if len({a, b, *elist[k]}) < 4 or np.max(np.abs(x)) > R - 4:
            continue
        nx = max(fa * x[0] + fb * x[1] for fa, fb in fs)
        if far_only and nx < R:
            continue
        cand.append((k, x, nx))
    out = []
    dist_ab = cl.bfs_from(adj, [a, b])
    for k, x, nx in rnd.sample(cand, min(npairs, len(cand))):
        L_ = cl.min_cycle_through(adj, elist, c0, k)
        c, d = elist[k]
        out.append({"delta": L_ - 1, "two_norm": 2 * nx, "lower": 2 * min(dist_ab[c], dist_ab[d]) + 1, "x": x})
    return out

def check_bonds(L, rnd):
    ok, rows = True, []
    for key, law, other in L:
        P = cl.velocity_polygon(other)
        smp = bond_samples(other, P, 9, 40, rnd)
        exc = [s["delta"] - s["two_norm"] for s in smp]
        lower_ok = all(s["delta"] >= s["lower"] for s in smp)
        good = lower_ok and max(abs(e) for e in exc) <= EXCESS_BOUND
        ok &= good
        rows.append({"law": f"{key[0]} {key[1]}", "pairs": len(smp), "excess_min": round(min(exc), 3), "excess_max": round(max(exc), 3),
                     "lower_bound_holds": bool(lower_ok), "ok": bool(good)})
    return ok, rows

def check_far(L, rnd):
    ok, rows = True, []
    for key, law, other in L:
        if key not in (("L", "4.6.12"), ("A", "3.3.3.3.6"), ("L", "3.12.12")):
            continue
        P = cl.velocity_polygon(other)
        smp = bond_samples(other, P, 18, 30, rnd, far_only=True)
        exc = [s["delta"] - s["two_norm"] for s in smp]
        good = max(abs(e) for e in exc) <= EXCESS_BOUND
        ok &= good
        rows.append({"law": f"{key[0]} {key[1]}", "pairs": len(smp), "min_two_norm": round(min(s["two_norm"] for s in smp), 2),
                     "max_two_norm": round(max(s["two_norm"] for s in smp), 2), "excess_min": round(min(exc), 3),
                     "excess_max": round(max(exc), 3), "ok": bool(good)})
    return ok, rows

def grid_rows(n, W, gam, rnd, npairs, factor=2):
    G = cl.grid_law(n, W, gam)
    adj, elist, epos = G["adj"], G["elist"], G["epos"]
    c0 = min(range(len(elist)), key=lambda k: np.linalg.norm(epos[k]))
    a, b = elist[c0]
    cand = [k for k in range(len(elist)) if len({a, b, *elist[k]}) == 4 and np.linalg.norm(epos[k]) < W - 5]
    diffs, cont = [], []
    for k in rnd.sample(cand, min(npairs, len(cand))):
        L_ = cl.min_cycle_through(adj, elist, c0, k)
        sep, same = cl.separating(G, c0, k)
        diffs.append((L_ - 1) - (factor * sep + (1 if same else 3)))
        x = epos[k] - epos[c0]
        cont.append((L_ - 1) - 2 * sum(abs(float(Nj @ x)) for Nj in G["N"]))
    return diffs, cont

def check_grids(rnd):
    ok, rows = True, []
    for n, W in ((2, 20), (3, 16), (4, 14), (5, 13), (7, 9)):
        gam = [rnd.random() for _ in range(n)]
        diffs, cont = grid_rows(n, W, gam, rnd, 60)
        good = min(diffs) >= 0 and max(diffs) <= 4 and max(abs(c) for c in cont) <= 2 * n + 6
        ok &= good
        rows.append({"families": n, "pairs": len(diffs), "delta_minus_2sep_plus_3_min": min(diffs), "max": max(diffs),
                     "delta_minus_2sum_abs_max": round(max(abs(c) for c in cont), 3), "ok": bool(good)})
    # de Bruijn's pentagrid with offsets summing to 1 (its dual tiling is a Penrose rhombus tiling)
    gam = [0.11, 0.23, 0.17, 0.31, 0.18]
    diffs, cont = grid_rows(5, 15, gam, rnd, 60)
    good = min(diffs) >= 0 and max(diffs) <= 4 and max(abs(c) for c in cont) <= 16
    ok &= good
    rows.append({"families": "5 (Penrose pentagrid, offsets sum 1)", "pairs": len(diffs), "delta_minus_2sep_plus_3_min": min(diffs),
                 "max": max(diffs), "delta_minus_2sum_abs_max": round(max(abs(c) for c in cont), 3), "ok": bool(good)})
    return ok, rows

def regular_pi(m):
    """Golab's pi of the regular m-gon (m even), computed as half its perimeter in its own norm."""
    V = [(math.cos(2 * math.pi * k / m), math.sin(2 * math.pi * k / m)) for k in range(m)]
    fs = []
    for i in range(m):
        (x1, y1), (x2, y2) = V[i], V[(i + 1) % m]
        det = x1 * y2 - x2 * y1
        fs.append(((y2 - y1) / det, (x1 - x2) / det))
    per = sum(max(a * (V[(i + 1) % m][0] - V[i][0]) + b * (V[(i + 1) % m][1] - V[i][1]) for a, b in fs) for i in range(m))
    return per / 2

def zonotope_polar_is_regular(n):
    """{x : sum_j |<x, n_j>| <= 1} for n equiangular unit normals: vertices equidistant and equally spaced."""
    N = [(math.cos(math.pi * j / n), math.sin(math.pi * j / n)) for j in range(n)]
    # the polar's vertices lie in the directions of the normals' perpendiculars... compute radial function at 2000 angles
    rad = []
    for k in range(4000):
        t = 2 * math.pi * k / 4000
        u = (math.cos(t), math.sin(t))
        rad.append(1 / sum(abs(u[0] * a + u[1] * b) for a, b in N))
    # a regular 2n-gon's radial function has period 2 pi / 2n
    shift = 4000 // (2 * n)
    return max(abs(rad[k] - rad[(k + shift) % 4000]) for k in range(4000)) < 1e-9 if 4000 % (2 * n) == 0 else None

def check_regular():
    ok, rows = True, []
    for n in range(2, 13):
        m = 2 * n
        val = regular_pi(m)
        formula = m * math.sin(math.pi / m) if n % 2 == 1 else m * math.tan(math.pi / m)
        good = abs(val - formula) < 1e-12
        reg = zonotope_polar_is_regular(n)
        if reg is not None:
            good &= reg
        ok &= good
        rows.append({"n_families": n, "sides": m, "pi": round(val, 12), "formula": "2n sin(pi/2n)" if n % 2 else "2n tan(pi/2n)", "ok": bool(good)})
    golden = 10 * math.sin(math.pi / 10)
    ok &= abs(golden - 5 / ((1 + math.sqrt(5)) / 2)) < 1e-12
    return ok, rows, golden

# ---------------------------------------------------------------- controls (each must be rejected)

def control_wrong_dual(rnd):
    """Predict the 4.8.8 law's bond distances with the velocity polygon of 4.8.8 itself instead of its dual's."""
    g = cl.truncated_square(); h = cl.dual(g)
    P_wrong = cl.velocity_polygon(g)
    smp = bond_samples(h, P_wrong, 16, 40, rnd, far_only=True)
    exc = [s["delta"] - s["two_norm"] for s in smp]
    return max(abs(e) for e in exc) > EXCESS_BOUND, (round(min(exc), 2), round(max(exc), 2))

def control_factor_one(rnd):
    diffs, _ = grid_rows(5, 13, [0.11, 0.23, 0.17, 0.31, 0.18], rnd, 40, factor=1)
    return max(diffs) > 4, max(diffs)

def control_no_loops():
    g = cl.square()
    orig = cl.simple_cycles
    def skip_loops(gr, cap=2_000_000):
        for disp, length in orig(gr, cap):
            if length > 1:
                yield disp, length
    cl.simple_cycles = skip_loops
    try:
        P = cl.velocity_polygon(g)
    finally:
        cl.simple_cycles = orig
    return len(P) != 4 or (len(P) >= 3 and cl.self_pi(P) != 4), len(P)

def control_bad_tiling():
    g = cl.unit_distance_graph("bad snub square", ((1 + cl.S3) / cl.S2, 0), (0, (1 + cl.S3) / cl.S2),
                               [(math.cos(math.pi / 4 + math.radians(10) + j * math.pi / 2) / cl.S2,
                                 math.sin(math.pi / 4 + math.radians(10) + j * math.pi / 2) / cl.S2) for j in range(4)])
    try:
        conf = cl.face_sizes_at_vertices(g)
        ok = all(cl.canonical_conf(c) == cl.canonical_conf(cl.EXPECTED["3.3.4.3.4"]) for c in conf)
    except Exception:
        ok = False
    return not ok, len(g.edges)

def main():
    t0 = time.time()
    rnd = random.Random(20261107)
    rng = np.random.default_rng(20261107)
    L = laws()
    res = {}
    s_ok, res["structure"] = check_structure()
    t_ok, res["table"] = check_table(L)
    k_ok, res["karp_support_max_error"] = check_karp(L, rng)
    b_ok, res["bond_distances_radius_9"] = check_bonds(L, rnd)
    f_ok, res["bond_distances_far_radius_18"] = check_far(L, rnd)
    g_ok, res["line_arrangements"] = check_grids(rnd)
    r_ok, res["regular_polygons"], golden = check_regular()
    res["penrose_pi"] = golden
    controls = {}
    for name, fn in (("wrong_dual_polygon", lambda: control_wrong_dual(rnd)), ("factor_one_for_two", lambda: control_factor_one(rnd)),
                     ("cycle_enumeration_without_loops", control_no_loops), ("perturbed_snub_square", control_bad_tiling)):
        rejected, info = fn()
        controls[name] = {"rejected": bool(rejected), "detail": info}
    res["controls"] = controls
    checks = {"structure": s_ok, "exact_table": t_ok, "karp_support": k_ok, "bond_distances": b_ok, "far_bond_distances": f_ok,
              "line_arrangements": g_ok, "regular_polygons": r_ok}
    checks = {k: bool(v) for k, v in checks.items()}
    res["checks"] = checks
    res["all_checks_pass"] = all(checks.values())
    res["all_controls_rejected"] = all(c["rejected"] for c in controls.values())
    res["theorem_flags"] = {
        "periodic_circle_is_rational_polygon": "argued-in-prose (Theorem 1); computed for 22 laws",
        "pi_rational_for_periodic_laws": "argued-in-prose (Corollary 2); computed for 22 laws",
        "line_arrangement_bond_distance": "argued-in-prose (Theorem 3); sampled for n = 2, 3, 4, 5, 7 and the Penrose pentagrid",
    }
    res["runtime_seconds"] = round(time.time() - t0, 1)
    manifest = json.loads((HERE / "manifest.json").read_text())
    failures = [k for k, v in checks.items() if not v] + [f"control {k} not rejected" for k, v in controls.items() if not v["rejected"]]
    out = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
           "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
           "checks": checks, "failures": failures, "details": res}
    (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({"checks": checks, "controls": {k: v["rejected"] for k, v in controls.items()}, "runtime": res["runtime_seconds"]}, indent=1))
    return 0 if res["all_checks_pass"] and res["all_controls_rejected"] else 1

if __name__ == "__main__":
    sys.exit(main())
