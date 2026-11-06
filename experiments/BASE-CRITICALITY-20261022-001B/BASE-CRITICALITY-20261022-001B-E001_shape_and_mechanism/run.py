#!/usr/bin/env python3
"""Producer for BASE-CRITICALITY-20261022-001B-E001: shape, rotation and the percolation mechanism.

Confirmatory Monte Carlo over the roster frozen in contract.json. A not-all-equal relation NAE(h_u, x_e, h_v) sits on
every edge of a torus grid (or of a decorated torus, or a cubic 3-torus); joints h are hidden and spokes x are fair
bits. For each torus the producer counts consistent samples and reports E = -log2 of the consistent fraction. Square
tori are judged by two solvers: limited backtracking on the not-all-equal tables, and strongly connected components on
the recoloured instance built directly from the spokes. On axis-aligned tori with one odd side it also records directed
up- and down-crossings of the cut cylinder, and on the ratio-4/3 family an independent bond-percolation sampler.
Self-contained; imports nothing from the proofs.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import math
import random
import resource
import sys
import time
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "BASE-CRITICALITY-20261022-001B" / HERE.name

NAE = [((0, 1), (1, 1)), ((1, 1), (1, 0))]          # spoke 0 forbids (0, 0); spoke 1 forbids (1, 1)
PARITY = [((1, 0), (0, 1)), ((0, 1), (1, 0))]


# ------------------------------------------------------------------ surfaces

def hnf(v1, v2):
    """Basis (p, 0), (q, r) of the lattice spanned by v1, v2, with 0 <= q < p and r > 0."""
    (a, b), (c, d) = v1, v2

    def egcd(x, y):
        if y == 0:
            return x, 1, 0
        g, s, t = egcd(y, x % y)
        return g, t, s - (x // y) * t

    g, s, t = egcd(b, d)
    if g < 0:
        g, s, t = -g, -s, -t
    q0 = s * a + t * c
    p = abs((d // g) * a - (b // g) * c)
    return p, q0 % p, g


def lattice_torus(v1, v2):
    p, q, r = hnf(v1, v2)

    def canon(x, y):
        beta = y // r
        y -= beta * r
        x -= beta * q
        return x % p, y

    coords = [(x, y) for y in range(r) for x in range(p)]
    index = {c: k for k, c in enumerate(coords)}
    edges = []
    for (x, y) in coords:
        u = index[(x, y)]
        for dx, dy in ((1, 0), (0, 1)):
            edges.append((u, index[canon(x + dx, y + dy)]))
    return len(coords), edges, [(x + y) % 2 for (x, y) in coords]


def axis_torus(a, b):
    """a rows (i), b columns (j); vertical edges first, then horizontal."""
    idx = lambda i, j: (i % a) * b + (j % b)
    edges = [(idx(i, j), idx(i + 1, j)) for i in range(a) for j in range(b)]
    edges += [(idx(i, j), idx(i, j + 1)) for i in range(a) for j in range(b)]
    return a * b, edges, [((v // b) + (v % b)) % 2 for v in range(a * b)]


def decorate(nv, edges, blocks):
    out, n = [], nv
    for (u, v) in edges:
        chain = [u] + list(range(n, n + len(blocks) - 1)) + [v]
        n += len(blocks) - 1
        for k, par in enumerate(blocks):
            out += [(chain[k], chain[k + 1])] * par
    return n, out


def cubic(a, b, c):
    idx = lambda i, j, k: ((i % a) * b + (j % b)) * c + (k % c)
    edges = []
    for i in range(a):
        for j in range(b):
            for k in range(c):
                u = idx(i, j, k)
                edges += [(u, idx(i + 1, j, k)), (u, idx(i, j + 1, k)), (u, idx(i, j, k + 1))]
    return a * b * c, edges


def bipartite(nv, edges):
    adj = [[] for _ in range(nv)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    col = [None] * nv
    for s in range(nv):
        if col[s] is not None:
            continue
        col[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if col[w] is None:
                    col[w] = 1 - col[u]
                    stack.append(w)
                elif col[w] == col[u]:
                    return False
    return True


# ------------------------------------------------------------------ solver 1: limited backtracking on the tables

def consistent_tables(nv, edges, mats):
    adj = [[] for _ in range(nv)]
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k, 0))
        adj[v].append((u, k, 1))
    val = [None] * nv

    def propagate(start, a, changed):
        val[start] = a
        changed.append(start)
        stack = [start]
        while stack:
            u = stack.pop()
            for w, k, side in adj[u]:
                M = mats[k]
                if side == 0:
                    allowed = [c for c in (0, 1) if M[val[u]][c]]
                else:
                    allowed = [c for c in (0, 1) if M[c][val[u]]]
                if val[w] is None:
                    if not allowed:
                        return False
                    if len(allowed) == 1:
                        val[w] = allowed[0]
                        changed.append(w)
                        stack.append(w)
                elif val[w] not in allowed:
                    return False
        return True

    for v in range(nv):
        if val[v] is not None:
            continue
        ok = False
        for a in (0, 1):
            changed = []
            if propagate(v, a, changed):
                ok = True
                break
            for w in changed:
                val[w] = None
        if not ok:
            return False
    return True


# ------------------------------------------------------------------ solver 2: components of the recoloured instance

def consistent_recoloured(nv, edges, g, x):
    succ = [[] for _ in range(2 * nv)]

    def clause(p, q):                      # p or q; literal 2v is tau_v = 1, 2v + 1 is tau_v = 0
        succ[p ^ 1].append(q)
        succ[q ^ 1].append(p)

    for (u, v), xe in zip(edges, x):
        if g[u] != g[v]:
            tail, head = (u, v) if g[u] == 1 - xe else (v, u)
            clause(2 * tail + 1, 2 * head)
        else:
            c = xe ^ g[u]
            if c == 0:
                clause(2 * u, 2 * v)
            else:
                clause(2 * u + 1, 2 * v + 1)
    n = 2 * nv
    index = [-1] * n
    low = [0] * n
    on = [False] * n
    comp = [-1] * n
    stack, counter, ncomp = [], 0, 0
    for root in range(n):
        if index[root] != -1:
            continue
        work = [(root, 0)]
        while work:
            node, i = work.pop()
            if i == 0:
                index[node] = low[node] = counter
                counter += 1
                stack.append(node)
                on[node] = True
            descended = False
            nbrs = succ[node]
            for j in range(i, len(nbrs)):
                w = nbrs[j]
                if index[w] == -1:
                    work.append((node, j + 1))
                    work.append((w, 0))
                    descended = True
                    break
                if on[w] and index[w] < low[node]:
                    low[node] = index[w]
            if descended:
                continue
            if low[node] == index[node]:
                while True:
                    w = stack.pop()
                    on[w] = False
                    comp[w] = ncomp
                    if w == node:
                        break
                ncomp += 1
            if work:
                parent = work[-1][0]
                if low[node] < low[parent]:
                    low[parent] = low[node]
    return all(comp[2 * v] != comp[2 * v + 1] for v in range(nv))


def parity_criterion(nv, edges, x):
    adj = [[] for _ in range(nv)]
    for (u, v), xe in zip(edges, x):
        adj[u].append((v, xe))
        adj[v].append((u, xe))
    h = [None] * nv
    for s in range(nv):
        if h[s] is not None:
            continue
        h[s] = 0
        queue = [s]
        while queue:
            u = queue.pop()
            for w, xe in adj[u]:
                if h[w] is None:
                    h[w] = h[u] ^ xe
                    queue.append(w)
                elif h[w] != h[u] ^ xe:
                    return False
    return True


# ------------------------------------------------------------------ crossings of the cut cylinder (axis tori)

def crossings(a, b, edges, g, x):
    nv = a * b
    out = [[] for _ in range(nv)]
    for (u, v), xe in zip(edges, x):
        if g[u] == g[v]:
            continue                       # the seam: wrap-around vertical edges across the odd side
        if g[u] == 1 - xe:
            out[u].append(v)
        else:
            out[v].append(u)
    bottom = range(0, b)
    top = set(range((a - 1) * b, a * b))
    botset = set(bottom)

    def reaches(sources, targets):
        seen = set(sources)
        dq = deque(sources)
        while dq:
            w = dq.popleft()
            if w in targets:
                return True
            for z in out[w]:
                if z not in seen:
                    seen.add(z)
                    dq.append(z)
        return False

    return reaches(list(bottom), top), reaches(list(top), botset)


def percolation_crosses(a, b, edges, g, rng):
    nv = a * b
    adj = [[] for _ in range(nv)]
    for (u, v) in edges:
        if g[u] == g[v]:
            continue
        if rng.random() < 0.5:
            adj[u].append(v)
            adj[v].append(u)
    top = set(range((a - 1) * b, a * b))
    seen = set(range(b))
    dq = deque(range(b))
    while dq:
        w = dq.popleft()
        if w in top:
            return True
        for z in adj[w]:
            if z not in seen:
                seen.add(z)
                dq.append(z)
    return False


# ------------------------------------------------------------------ measuring

def estimate(good, n):
    p = good / n
    if good == 0:
        return p, None, None
    se_p = math.sqrt(p * (1 - p) / n)
    return p, -math.log2(p), se_p / (p * math.log(2))


def measure(family, label, nv, edges, samples, g=None, axis=None, size=None, extra=None):
    t0 = time.time()
    rng = random.Random(f"{family}-{label}")
    good = agree = up = down = both = good_both = 0
    for _ in range(samples):
        x = [rng.randrange(2) for _ in edges]
        ok = consistent_tables(nv, edges, [NAE[xe] for xe in x])
        good += ok
        if g is not None:
            agree += ok == consistent_recoloured(nv, edges, g, x)
        if axis is not None:
            u, d = crossings(axis[0], axis[1], edges, g, x)
            up += u
            down += d
            both += u and d
            good_both += ok and u and d
    p, E, se = estimate(good, samples)
    row = {"family": family, "label": label, "vertices": nv, "edges": len(edges), "samples": samples, "consistent": good,
           "P": p, "E": E, "se_E": se, "E_lower_bound": (math.log2(samples) if good == 0 else None),
           "solvers_agree": agree if g is not None else None, "size": size, "seconds": round(time.time() - t0, 1)}
    if axis is not None:
        row.update({"up": up, "down": down, "both": both, "consistent_and_both": good_both})
    if extra:
        row.update(extra)
    print(json.dumps({k: row[k] for k in ("family", "label", "E", "se_E", "E_lower_bound", "seconds")}), flush=True)
    return row


def slope(points):
    """Weighted least squares of E against log2(size); points are (size, E, se)."""
    xs = [math.log2(s) for s, _, _ in points]
    ys = [e for _, e, _ in points]
    ws = [1 / se ** 2 for _, _, se in points]
    W = sum(ws)
    xm = sum(w * x for w, x in zip(ws, xs)) / W
    ym = sum(w * y for w, y in zip(ws, ys)) / W
    sxx = sum(w * (x - xm) ** 2 for w, x in zip(ws, xs))
    b = sum(w * (x - xm) * (y - ym) for w, x, y in zip(ws, xs, ys)) / sxx
    return b, math.sqrt(1 / sxx)


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows, failures = [], []

    # controls
    for a in (16, 32):
        nv, edges, g = axis_torus(a, a)
        r = measure("control_bipartite", f"{a}x{a}", nv, edges, 2000, g=g, size=a)
        rows.append(r)
        if r["consistent"] != r["samples"] or r["solvers_agree"] != r["samples"] or not bipartite(nv, edges):
            failures.append(f"bipartite control {a}")
    for a in (3, 5):
        nv, edges, g = axis_torus(a, a)
        rng = random.Random(f"parity-{a}")
        agree = 0
        for _ in range(500):
            x = [rng.randrange(2) for _ in edges]
            agree += consistent_tables(nv, edges, [PARITY[xe] for xe in x]) == parity_criterion(nv, edges, x)
        rows.append({"family": "control_parity", "label": f"{a}x{a}", "samples": 500, "agree": agree})
        if agree != 500:
            failures.append(f"parity control {a}")
    if failures:
        return finish(rows, failures, started, contract)

    # F1 shape and F4 coupling
    shapes = {"2/3": [(9, 6), (15, 10), (27, 18), (45, 30)], "4/3": [(9, 12), (15, 20), (27, 36), (45, 60)],
              "2": [(9, 18), (15, 30), (27, 54), (45, 90)], "4": [(9, 36), (15, 60), (27, 108), (45, 180)]}
    for ratio, sizes in shapes.items():
        for a, b in sizes:
            nv, edges, g = axis_torus(a, b)
            extra = None
            if ratio == "4/3":
                rng = random.Random(f"F4-{a}x{b}")
                extra = {"percolation_up": sum(percolation_crosses(a, b, edges, g, rng) for _ in range(6000)),
                         "percolation_samples": 6000}
            rows.append(measure(f"F1_{ratio}", f"{a}x{b}", nv, edges, 6000, g=g, axis=(a, b), size=a, extra=extra))

    # F2 rotation
    for a in (17, 25, 33, 41):
        nv, edges, g = lattice_torus((a, 0), (0, a))
        rows.append(measure("F2_square_axis", f"{a}x{a}", nv, edges, 6000, g=g, size=a))
    for c, d in ((12, 5), (24, 7), (20, 13), (35, 12), (30, 17)):
        nv, edges, g = lattice_torus((c, d), (-d, c))
        rows.append(measure("F2_square_rotated", f"({c},{d})", nv, edges, 6000, g=g, size=round(math.hypot(c, d), 2)))
    for a in (13, 17, 25):
        nv, edges, g = lattice_torus((a, 0), (0, 2 * a))
        rows.append(measure("F2_long_axis", f"{a}x{2 * a}", nv, edges, 6000, g=g, size=a))
    for c, d in ((12, 5), (20, 13), (24, 7)):
        nv, edges, g = lattice_torus((c, d), (-2 * d, 2 * c))
        rows.append(measure("F2_long_rotated", f"({c},{d})", nv, edges, 6000, g=g, size=round(math.hypot(c, d), 2)))

    # F3 shear
    for m in (3, 5, 9, 13):
        nv, edges, g = lattice_torus((3 * m, 0), (m, 6 * m))
        rows.append(measure("F3_shear", f"m={m}", nv, edges, 6000, g=g, size=3 * m))
    nv, edges, g = lattice_torus((27, 0), (-9, 54))
    rows.append(measure("F3_mirror", "m=9", nv, edges, 6000, g=g, size=27))

    # F6 gadgets
    for blocks, sizes, n in (([1, 1, 1], (9, 17, 25, 33), 6000), ([2, 2, 2], (9, 17, 25, 33), 6000),
                             ([2], (3, 5, 7, 9), 20000), ([3], (3, 5, 7, 9), 20000), ([3, 3, 3], (3, 5, 7, 9), 20000)):
        for a in sizes:
            nv0, edges0, _ = axis_torus(a, a)
            nv, edges = decorate(nv0, edges0, blocks)
            rows.append(measure(f"F6_{blocks}", f"{a}x{a}", nv, edges, n, size=a))

    # F7 cubic
    for a, b in ((3, 2), (3, 4), (3, 6), (5, 2), (5, 4), (5, 6)):
        nv, edges = cubic(a, b, b)
        rows.append(measure("F7_cubic", f"{a}x{b}x{b}", nv, edges, 100000, size=b, extra={"height": a}))

    # F8 wide (exploratory)
    for a in (9, 15):
        for r in (4, 6, 8):
            nv, edges, g = axis_torus(a, r * a)
            rows.append(measure("F8_wide", f"{a}x{r * a}", nv, edges, 20000, size=a, extra={"ratio": r}))

    for r in rows:
        if r.get("solvers_agree") is not None and r["solvers_agree"] != r["samples"]:
            failures.append(f"solver disagreement {r['family']} {r['label']}")
    return finish(rows, failures, started, contract)


def finish(rows, failures, started, contract):
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not failures, "control_failures": failures,
              "rows": len(rows)}
    if not failures:
        fam = {}
        for r in rows:
            fam.setdefault(r["family"], []).append(r)
        shape = {}
        for ratio in ("2/3", "4/3", "2", "4"):
            pts = [(r["size"], r["E"], r["se_E"]) for r in fam[f"F1_{ratio}"]]
            b, s = slope(pts)
            resid = []
            for r in fam[f"F1_{ratio}"]:
                q = r["consistent_and_both"] / r["both"]
                resid.append((r["size"], q, math.sqrt(q * (1 - q) / r["both"])))
            rb, rs = slope(resid)
            shape[ratio] = {"E": [round(r["E"], 4) for r in fam[f"F1_{ratio}"]], "se_E": [round(r["se_E"], 4) for r in fam[f"F1_{ratio}"]],
                            "mean_E": sum(p[1] for p in pts) / len(pts), "slope": b, "slope_se": s,
                            "consistent_given_two_way": [round(q, 4) for _, q, _ in resid], "residual_slope": rb, "residual_slope_se": rs}
        means = [shape[k]["mean_E"] for k in ("2/3", "4/3", "2", "4")]
        H_shape = all(abs(shape[k]["slope"]) <= 0.05 for k in shape) and all(x < y for x, y in zip(means, means[1:]))
        shape_refuted = any(abs(shape[k]["slope"]) > 0.05 + 3 * shape[k]["slope_se"] for k in shape)

        def mean_se(rs):
            m = sum(r["E"] for r in rs) / len(rs)
            se = math.sqrt(sum(r["se_E"] ** 2 for r in rs)) / len(rs)
            return m, se
        sq_axis, sq_axis_se = mean_se(fam["F2_square_axis"])
        sq_rot, sq_rot_se = mean_se(fam["F2_square_rotated"])
        lg_axis, lg_axis_se = mean_se(fam["F2_long_axis"])
        lg_rot, lg_rot_se = mean_se(fam["F2_long_rotated"])
        d1, s1 = sq_rot - sq_axis, math.hypot(sq_axis_se, sq_rot_se)
        d2, s2 = lg_rot - lg_axis, math.hypot(lg_axis_se, lg_rot_se)
        H_rotation = abs(d1) <= 0.06 and abs(d1) <= 3 * s1 and abs(d2) <= 0.06 and abs(d2) <= 3 * s2
        rotation_refuted = abs(d1) > 0.06 + 3 * s1 or abs(d2) > 0.06 + 3 * s2

        sh = fam["F3_shear"]
        bsh, ssh = slope([(r["size"], r["E"], r["se_E"]) for r in sh])
        m9 = next(r for r in sh if r["label"] == "m=9")
        mir = fam["F3_mirror"][0]
        H_shear = abs(bsh) <= 0.05 and abs(mir["E"] - m9["E"]) <= 3 * math.hypot(mir["se_E"], m9["se_E"])

        coupling = []
        for r in fam["F1_4/3"]:
            p1 = 1 - r["up"] / r["samples"]
            p2 = 1 - r["percolation_up"] / r["percolation_samples"]
            se = math.sqrt(p1 * (1 - p1) / r["samples"] + p2 * (1 - p2) / r["percolation_samples"])
            coupling.append({"size": r["size"], "no_up_crossing": round(p1, 4), "percolation_no_crossing": round(p2, 4),
                             "z": round((p1 - p2) / se, 3) if se > 0 else 0.0})
        H_coupling = all(abs(c["z"]) <= 4 for c in coupling)

        def value(r):
            return r["E"] if r["E"] is not None else float("inf")
        mech = {}
        for key in ("[1, 1, 1]", "[2, 2, 2]", "[2]", "[3]", "[3, 3, 3]"):
            rs = fam[f"F6_{key}"]
            mech[key] = [None if r["E"] is None else round(r["E"], 4) for r in rs]
        sub_ok = all(value(fam[f"F6_{k}"][-1]) <= 0.02 and value(fam[f"F6_{k}"][-1]) <= value(fam[f"F6_{k}"][0]) for k in ("[1, 1, 1]", "[2, 2, 2]"))

        def increasing(rs):
            vals = [value(r) for r in rs]
            ok = True
            for x, y in zip(vals, vals[1:]):
                if math.isinf(x):
                    ok &= math.isinf(y)
                else:
                    ok &= y > x
            return ok
        super_ok = all(increasing(fam[f"F6_{k}"]) for k in ("[2]", "[3]", "[3, 3, 3]"))
        H_mechanism = sub_ok and super_ok
        cub = fam["F7_cubic"]
        h3 = [r for r in cub if r["height"] == 3]
        h5 = [r for r in cub if r["height"] == 5]
        H_cubic = increasing(h3) and increasing(h5)
        wide = {}
        for a in (9, 15):
            rs = [r for r in fam["F8_wide"] if r["size"] == a and r["E"] is not None]
            if len(rs) >= 2:
                xs = [r["ratio"] for r in rs]
                ys = [r["E"] for r in rs]
                xm, ym = sum(xs) / len(xs), sum(ys) / len(ys)
                wide[str(a)] = {"E": [round(y, 4) for y in ys], "ratios": xs,
                                "slope_per_unit_ratio": sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / sum((x - xm) ** 2 for x in xs)}
        primary = {"H_shape": H_shape, "H_rotation": H_rotation, "H_shear": H_shear, "H_coupling": H_coupling,
                   "H_mechanism": H_mechanism, "H_cubic": H_cubic}
        verdict = "supported" if all(primary.values()) else ("refuted" if shape_refuted or rotation_refuted else "closed-null")
        result.update({
            "F1_shape": shape,
            "F2_rotation": {"square_axis_mean": sq_axis, "square_rotated_mean": sq_rot, "square_difference": d1, "square_difference_se": s1,
                            "long_axis_mean": lg_axis, "long_rotated_mean": lg_rot, "long_difference": d2, "long_difference_se": s2},
            "F3_shear": {"E": [round(r["E"], 4) for r in sh], "slope": bsh, "slope_se": ssh, "mirror_E": mir["E"], "m9_E": m9["E"]},
            "F4_coupling": coupling,
            "F6_gadgets": mech,
            "F7_cubic": {r["label"]: (None if r["E"] is None else round(r["E"], 4)) for r in cub},
            "F8_wide": wide,
            "primary": primary,
            "secondary_residual_flat": all(abs(shape[k]["residual_slope"]) <= 0.05 for k in shape),
            "verdict": verdict,
        })
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    (OUT / "raw_rows.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in result if k in ("controls_ok", "primary", "verdict", "wall_seconds")}, indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
