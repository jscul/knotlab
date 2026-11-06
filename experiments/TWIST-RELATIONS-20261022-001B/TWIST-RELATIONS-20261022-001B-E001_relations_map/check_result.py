#!/usr/bin/env python3
"""Independent check of the twist-relations map; imports no producer code.

Parses raw_rows.jsonl, the frozen contract and result.json. It checks the roster, recomputes the controls, every statistic (in
exact integer arithmetic from the joint type patterns) and every decision, and compares with result.json. The 3 x 3 rows are compared
with the exact fractions of TWIST-RELATIONS-20261022-001A-P001. The 7 x 5 torus is replayed in pure Python with its own
classification (reachability closure and a lattice union-find): per-sector type frequencies and the three odd-line differences must
agree. A deliberately wrong pairing (sector (1,0) against sector (0,1) for the class (1,0) mod 2, which is odd in one and even in the
other) must be rejected by more than 6 standard errors (power).

    python3 -B check_result.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/TWIST-RELATIONS-20261022-001B" / HERE.name
EXACT = ROOT / "proofs/TWIST-RELATIONS-20261022-001A/TWIST-RELATIONS-20261022-001A-P001_harmonic_structure/result.json"

ROSTER = {("F_exact", 3, 3, 0): 2000000, ("F_exact", 3, 3, 1): 2000000,
          ("F_odd", 7, 5, 0): 30000000, ("F_odd", 8, 8, 0): 30000000, ("F_odd", 10, 6, 0): 30000000, ("F_odd", 12, 8, 3): 30000000,
          ("F_odd", 9, 7, 2): 30000000, ("F_odd", 12, 12, 0): 20000000, ("F_odd", 16, 10, 5): 20000000, ("F_odd", 24, 24, 0): 4000000,
          ("F_shear", 12, 8, 0): 30000000, ("F_shear", 12, 8, 2): 30000000, ("F_shear", 12, 8, 4): 30000000, ("F_shear", 12, 8, 6): 30000000,
          ("F_rect", 48, 32, 0): 1200000, ("F_rect", 96, 64, 0): 600000, ("F_rect", 64, 32, 0): 1200000, ("F_rect", 128, 64, 0): 600000,
          ("F_rect", 96, 32, 0): 1200000, ("F_rect", 192, 64, 0): 600000, ("F_conf", 64, 32, 32): 1200000, ("F_conf", 128, 64, 64): 600000,
          ("F_harm", 64, 64, 0): 600000, ("F_harm", 64, 64, 8): 600000, ("F_harm", 64, 64, 16): 600000, ("F_harm", 64, 64, 24): 600000,
          ("F_harm", 64, 64, 32): 600000, ("F_harm", 128, 64, 0): 300000, ("F_harm", 128, 64, 16): 300000, ("F_harm", 128, 64, 32): 300000,
          ("F_harm", 128, 64, 48): 300000, ("F_harm", 128, 64, 64): 300000}


def decode(index):
    out = []
    for _ in range(4):
        index, r = divmod(index, 5)
        out.append(r)
    return out


def stat(row, f):
    """Exact mean and standard error of an integer per-sample statistic over the joint pattern."""
    n, s1, s2 = row["samples"], 0, 0
    for k, v in row["joint_types"].items():
        x = f(decode(int(k)))
        s1 += x * v
        s2 += x * x * v
    mean = Fraction(s1, n)
    var = Fraction(s2, n) - mean * mean
    return float(mean), math.sqrt(float(var) / n)


def odd(t, q):
    return {1: (2, 4), 2: (3, 4), 3: (2, 3)}[q].__contains__(t[q]) if q else False


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# ------------------------------------------------------------------ independent replay

def lattice(Lh, Lv, s):
    edges = []
    for u in range(Lh * Lv):
        x, y = u % Lh, u // Lh
        edges.append((u, y * Lh + (x + 1) % Lh, ((x + 1) // Lh, 0)))
        if y + 1 < Lv:
            edges.append((u, u + Lh, (0, 0)))
        else:
            X = x - s
            a = X // Lh
            edges.append((u, X - a * Lh, (a, 1)))
    return edges


def sector_type(V, edges, o, p):
    pa, pb = p
    tw = bool(pa or pb)
    n = 2 * V if tw else V
    adj = [0] * n
    ts = []
    for (u, w, (a, b)), bit in zip(edges, o):
        t = (a * pa + b * pb) & 1
        ts.append(t)
        if not tw:
            adj[u if bit else w] |= 1 << (w if bit else u)
        elif bit:
            adj[2 * u] |= 1 << (2 * w + t)
            adj[2 * w + 1 - t] |= 1 << (2 * u + 1)
        else:
            adj[2 * w + t] |= 1 << (2 * u)
            adj[2 * u + 1] |= 1 << (2 * w + 1 - t)
    reach = [adj[i] | (1 << i) for i in range(n)]
    changed = True
    while changed:                       # closure by repeated relaxation (a different schedule from the proof check)
        changed = False
        for i in range(n):
            r, acc, j = reach[i], reach[i], 0
            m = r
            while m:
                low = m & -m
                j = low.bit_length() - 1
                acc |= reach[j]
                m ^= low
            if acc != r:
                reach[i], changed = acc, True
    root = list(range(V))
    off = [(0, 0)] * V
    lat = {}

    def find(x):
        dx = dy = 0
        while root[x] != x:
            dx += off[x][0]
            dy += off[x][1]
            x = root[x]
        return x, (dx, dy)

    for (u, w, (a, b)), t in zip(edges, ts):
        i, j = (2 * u, 2 * w + t) if tw else (u, w)
        if not ((reach[i] >> j) & 1 and (reach[j] >> i) & 1):
            continue
        (ru, pu), (rw, pw) = find(u), find(w)
        d = (pu[0] + a - pw[0], pu[1] + b - pw[1])
        if ru == rw:
            if d != (0, 0):
                lat.setdefault(ru, []).append(d)
        else:
            root[rw], off[rw] = ru, d
            lat.setdefault(ru, []).extend(lat.pop(rw, []))
    kind, cls = 0, None
    for g in lat.values():
        if not g:
            continue
        if any(g[i][0] * g[j][1] - g[i][1] * g[j][0] for i in range(len(g)) for j in range(i + 1, len(g))):
            return 1
        x, y = g[0]
        k = gcd(abs(x), abs(y))
        cls = (x // k % 2, y // k % 2)
        kind = 2
    if kind == 0:
        return 0
    return {(1, 0): 2, (0, 1): 3, (1, 1): 4}[cls]


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "raw_rows.jsonl").read_text().splitlines()]
    assert contract["status"] == "Frozen" and result["experiment_id"] == contract["experiment_id"] and len(rows) == result["rows"]
    got = {(r["family"], r["Lh"], r["Lv"], r["s"]): r["samples"] for r in rows}
    assert got == ROSTER, set(got.items()) ^ set(ROSTER.items())
    by = {}
    for r in rows:
        by.setdefault(r["family"], []).append(r)

    # controls
    fails = []
    for r in rows:
        n = r["samples"]
        assert sum(r["joint_types"].values()) == n
        for q in range(4):
            assert sum(v for k, v in r["joint_types"].items() if decode(int(k))[q] == 0) == r[f"c{q}"]
            assert sum(v for k, v in r["joint_types"].items() if decode(int(k))[q] == 1) == r[f"x{q}"]
        for q in (1, 2, 3):
            if r[f"mis{q}"]:
                fails.append(f"test disagreement {r['label']} sector {q}")
            c, x = r[f"c{q}"], r[f"x{q}"]
            if abs(c - x) > 4 * math.sqrt(c + x):
                fails.append(f"duality {r['family']} {r['label']} sector {q}")
            # inconsistency (swap-invariant component) = cross + odd winding, exactly
            inc = sum(v for k, v in r["joint_types"].items() if decode(int(k))[q] == 1 or odd(decode(int(k)), q))
            assert inc == r[f"inv{q}"], (r["label"], q)
        if r["mis0"] or r["inv0"]:
            fails.append(f"untwisted sector flagged {r['label']}")
    assert fails == result["control_failures"] and result["controls_ok"] == (not fails)
    assert not fails, fails

    # the 3 x 3 rows against the exact fractions of the proof
    ex = json.loads(EXACT.read_text())["checks"]["exhaustive"]
    exact_dev = []
    for r in by["F_exact"]:
        e = ex[f"3x3 s={r['s']}"]
        n = r["samples"]
        for q, key in enumerate(("00", "10", "01", "11")):
            p = float(Fraction(e["P_contractible"][key]))
            exact_dev.append(abs(r[f"c{q}"] / n - p) / math.sqrt(p * (1 - p) / n))
            for cls, cnt in e["odd_lines"][key].items():
                pl = cnt / 262144
                obs = r[f"classes{q}"].get(cls, 0) / n
                exact_dev.append(abs(obs - pl) / math.sqrt(pl * (1 - pl) / n))
    assert max(exact_dev) <= 5, exact_dev

    # primary: odd-line identity
    pairs = (("(1,0): sector 10 - sector 11", lambda t: (t[1] == 2) - (t[3] == 2)),
             ("(0,1): sector 01 - sector 11", lambda t: (t[2] == 3) - (t[3] == 3)),
             ("(1,1): sector 10 - sector 01", lambda t: (t[1] == 4) - (t[2] == 4)))
    zs, rec = [], {t["label"]: t for t in result["odd_line"]["tori"]}
    for r in by["F_odd"]:
        for name, f in pairs:
            m, se = stat(r, f)
            z = m / se if se else 0.0
            assert close(m, rec[r["label"]][name]["difference"]) and close(se, rec[r["label"]][name]["sigma"], 1e-6)
            zs.append(abs(z))
    odd_acc, odd_rej = all(z <= 4 for z in zs), any(z > 6 for z in zs)
    assert (odd_acc, odd_rej) == (result["odd_line"]["accepted"], result["odd_line"]["decisively_rejected"])
    wrong = max(abs(stat(r, lambda t: (t[1] == 2) - (t[2] == 2))[0] / stat(r, lambda t: (t[1] == 2) - (t[2] == 2))[1]) for r in by["F_odd"])
    assert wrong > 6, wrong

    # primary: shear independence
    sh = sorted(by["F_shear"], key=lambda r: r["s"])
    pb = sh[0]["classes1"].get("1,0", 0) / sh[0]["samples"]
    shear_z = []
    for r, c in zip(sh[1:], result["shear_independence"]["comparisons"]):
        p = r["classes1"].get("1,0", 0) / r["samples"]
        z = (p - pb) / math.sqrt(p * (1 - p) / r["samples"] + pb * (1 - pb) / sh[0]["samples"])
        assert c["s"] == r["s"] and close(z, c["z"], 1e-7)
        shear_z.append(z)
    sh_acc, sh_rej = all(abs(z) <= 4 for z in shear_z), any(abs(z) > 6 for z in shear_z)
    assert (sh_acc, sh_rej) == (result["shear_independence"]["accepted"], result["shear_independence"]["decisively_rejected"])

    # secondary: rectangles and the rotated square
    D = lambda t: (t[0] == 0) - (t[1] == 0) - (t[2] == 0) + (t[3] == 0)
    rect_ok, rect_vals = True, []
    for aspect in sorted({r["Lh"] / r["Lv"] for r in by["F_rect"]}):
        small, large = sorted((r for r in by["F_rect"] if r["Lh"] / r["Lv"] == aspect), key=lambda r: r["Lv"])
        (d1, s1), (d2, s2) = stat(small, D), stat(large, D)
        dinf, sinf = 2 * d2 - d1, math.sqrt(4 * s2 * s2 + s1 * s1)
        rect_ok &= abs(dinf) <= 3 * sinf
        rect_vals.append((aspect, round(dinf, 5), round(sinf, 5)))
        match = next(a for a in result["rectangle_additivity"]["aspects"] if close(a["aspect"], aspect))
        assert close(match["D_inf"], dinf) and close(match["sigma"], sinf, 1e-6)
    assert rect_ok == result["rectangle_additivity"]["accepted"]
    conf = sorted(by["F_conf"], key=lambda r: r["Lv"])
    Dp = lambda t: (t[0] == 0) + (t[2] == 0) - (t[1] == 0) - (t[3] == 0)
    (a1, b1), (a2, b2) = stat(conf[0], Dp), stat(conf[1], Dp)
    dinf, sinf = 2 * a2 - a1, math.hypot(2 * b2, b1)
    rs = result["rotated_square"]
    assert close(dinf, rs["D_orthogonal_inf"]) and close(sinf, rs["sigma"], 1e-6) and (abs(dinf) <= 3 * sinf) == rs["accepted"]
    da, sa = stat(conf[1], D)
    assert (abs(da) > 10 * sa) == rs["axis_basis_far_from_zero"]

    # verdict
    verdict = "supported" if odd_acc and sh_acc else ("refuted" if odd_rej or sh_rej else "closed-null")
    assert verdict == result["verdict"]
    assert result["primary"] == {"odd_line_accepted": odd_acc, "shear_independence_accepted": sh_acc}
    assert result["secondary"] == {"rectangle_additivity_accepted": rect_ok, "rotated_square_accepted": rs["accepted"]}

    # independent replay of 7 x 5
    rec75 = next(r for r in by["F_odd"] if (r["Lh"], r["Lv"], r["s"]) == (7, 5, 0))
    edges = lattice(7, 5, 0)
    rng = random.Random("twist-relations-replay")
    m = 6000 if len(sys.argv) < 2 else int(sys.argv[1])
    counts = {}
    diffs = [0, 0, 0]
    for _ in range(m):
        o = [rng.getrandbits(1) for _ in edges]
        t = [sector_type(35, edges, o, p) for p in ((0, 0), (1, 0), (0, 1), (1, 1))]
        for q in range(4):
            counts[(q, t[q])] = counts.get((q, t[q]), 0) + 1
        for i, (_name, f) in enumerate(pairs):
            diffs[i] += f(t)
    n = rec75["samples"]
    worst = 0.0
    for q in range(4):
        for ty in range(5):
            obs = sum(v for k, v in rec75["joint_types"].items() if decode(int(k))[q] == ty) / n
            p = counts.get((q, ty), 0) / m
            worst = max(worst, abs(p - obs) / math.sqrt(max(obs * (1 - obs), 1e-6) * (1 / m + 1 / n)))
    assert worst <= 5, worst
    print(f"checked: {len(rows)} rows, verdict {verdict}; odd-line max |z| {max(zs):.2f} over {len(zs)} tests (wrong pairing {wrong:.0f} sigma); "
          f"shear z {[round(z, 2) for z in shear_z]}; rectangles (aspect, D_inf, sigma) {rect_vals}; rotated square orthogonal D_inf "
          f"{dinf:+.5f} +- {sinf:.5f}, axis D {da:+.4f}; exact 3x3 max deviation {max(exact_dev):.2f} sigma; replay 7x5 ({m} samples) worst "
          f"{worst:.2f} sigma, odd-line differences {diffs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
