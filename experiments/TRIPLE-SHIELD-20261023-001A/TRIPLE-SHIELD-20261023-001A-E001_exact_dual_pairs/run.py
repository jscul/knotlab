#!/usr/bin/env python3
"""Producer for TRIPLE-SHIELD-20261023-001A-E001: exact dual pairs for line contradictions of twisted tiling worlds.

The worlds are the 54 tiling placements of TRIPLE-TWIST-20261023-001B-E001: on the triangles of an L x M triangular torus (no shear),
a fair visible bit chooses the gauged allowed patterns R or their complements. For every placement, torus and twist, every
configuration of the visible bits is enumerated (tshield.c), and four kinds of event are counted:
- the torus contradicts;
- the cylinder cover that keeps a class c closed contradicts, for c = (1,0), (0,1), (1,1) (deck coordinates);
- lone line along c: that cylinder contradicts and the other two do not;
- cross: the torus contradicts and no cylinder does.
A twist fits when a doubly allowed assignment exists (every triangle's pattern allowed for both bits), found here by brute force.
For each class c, the twists that are odd on c relative to every fitting twist form a dual pair {q, q + PD(c)}; the test compares
their lone-line counts. A pair is explained by symmetry when a lattice symmetry of the torus followed by a vertex flip (image)
maps the placement to itself, c to +-c and one twist of the pair to the other; these maps form a group and preserve every count.

Placement types: orientation (a single clause of two literals on the square-lattice pair (a,b) or (b,c) of each triangle: the
two-literal orientation world), diagonal-clause (a single clause on (a,c)), shared-coin (other two-literal placements: several
clauses per triangle share its bit) and three (neither two-literal nor parity).

Control: on each torus and in each of the three classes, the lone-line counts of placement 63 equal the lone-loop counts of the
square-lattice orientation model (labels.c, a different program and model), in the twist shifted by (L mod 2, M mod 2).

    python3 -B run.py    writes rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "TRIPLE-SHIELD-20261023-001A" / HERE.name
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
WORKERS = min(24, os.cpu_count() or 1)
TORI = (("F_seen", 3, 3), ("F_fresh", 3, 4), ("F_fresh", 4, 3), ("F_fresh", 4, 4))
TWISTS = ((0, 0), (0, 1), (1, 0), (1, 1))
CLASSES = ((1, 0), (0, 1), (1, 1))
CHUNK = 1 << 24
NB = {(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1)}
UP = [(0, 0), (1, 0), (1, 1)]
DN = [(0, 0), (0, 1), (1, 1)]


# ------------------------------------------------------------------ placements

def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def canon(R):
    return min(R, comp(R))


def depends(R):
    return [k for k in range(3) if any(((R >> p) & 1) != ((R >> (p ^ (1 << k))) & 1) for p in range(8))]


def placement_type(R, kind):
    if kind != "pair":
        return kind
    d, size = depends(R), bin(R).count("1")
    if len(d) == 2 and size == 6:
        return "orientation" if set(d) in ({0, 1}, {1, 2}) else "diagonal-clause"
    return "shared-coin"


# ------------------------------------------------------------------ symmetry

def apply(g, v):
    return (g[0][0] * v[0] + g[0][1] * v[1], g[1][0] * v[0] + g[1][1] * v[1])


def point_group():
    out = []
    for a, b, c, d in product((-1, 0, 1), repeat=4):
        g = ((a, b), (c, d))
        if abs(a * d - b * c) == 1 and {apply(g, v) for v in NB} == NB:
            out.append(g)
    return out


def image_perm(g, tri):
    """Type (0 up, 1 down) of the image of a triangle under g, and where each corner goes."""
    pts = [apply(g, v) for v in tri]
    for b in pts:
        for t, offs in enumerate((UP, DN)):
            T = [(b[0] + o[0], b[1] + o[1]) for o in offs]
            if set(T) == set(pts):
                return t, [T.index(p) for p in pts]
    raise ValueError("not a triangle")


def perm_rel(R, pi):
    out = 0
    for p in range(8):
        if R >> p & 1:
            q = [0, 0, 0]
            for k in range(3):
                q[pi[k]] = (p >> k) & 1
            out |= 1 << (q[0] | q[1] << 1 | q[2] << 2)
    return out


def torus_group(L, M):
    G = []
    for g in point_group():
        a1, a2 = apply(g, (L, 0)), apply(g, (0, M))
        if all(v[0] % L == 0 and v[1] % M == 0 for v in (a1, a2)):
            G.append((g, ((a1[0] // L, a2[0] // L), (a1[1] // M, a2[1] // M))))
    return G


def act_twist(q, D):
    det = (D[0][0] * D[1][1] - D[0][1] * D[1][0]) & 1
    assert det == 1
    Di = ((D[1][1] & 1, D[0][1] & 1), (D[1][0] & 1, D[0][0] & 1))
    return tuple((q[0] * Di[0][k] + q[1] * Di[1][k]) & 1 for k in range(2))


def act_class(c, D):
    return (D[0][0] * c[0] + D[0][1] * c[1], D[1][0] * c[0] + D[1][1] * c[1])


def norm_class(c):
    return c if (c[0], c[1]) > (0, 0) else (-c[0], -c[1])


def flip_pattern(R, pat):
    return sum(1 << (p ^ pat) for p in range(8) if R >> p & 1)


FLIPS = ((0, 0), (1, 0), (0, 1), (1, 1))


def image(R, g, ab):
    """Placement after the lattice symmetry g followed by the vertex flip ab (None if up and down triangles disagree).

    The flip changes the hidden value of every vertex (i, j) of the fundamental domain with alpha i + beta j odd. Relative to
    the first corner, an up triangle's corners flip by (0, alpha, alpha + beta) and a down triangle's by (0, beta,
    alpha + beta). The result is a placement when the images of up and down triangles carry the same relations up to
    complement. On the torus the flip is a gauge by a function that is not periodic when alpha L or beta M is odd, so it adds
    (alpha L, beta M) mod 2 to the twist; it fixes classes.
    """
    a, b = ab
    pats = ((a << 1) | ((a ^ b) << 2), (b << 1) | ((a ^ b) << 2))
    rels = []
    for src in (UP, DN):
        t, pi = image_perm(g, src)
        rels.append(flip_pattern(perm_rel(R, pi), pats[t]))
    return canon(rels[0]) if rels[0] in (rels[1], comp(rels[1])) else None


def act(R, q, c, L, M, g, D, ab):
    """Image of (placement, twist, class up to sign) under g then the flip ab, or None."""
    Ri = image(R, g, ab)
    if Ri is None:
        return None
    qi = act_twist(q, D)
    return Ri, (qi[0] ^ (ab[0] * L & 1), qi[1] ^ (ab[1] * M & 1)), norm_class(act_class(c, D))


def explained(R, L, M, c, q1, q2):
    """Does a torus symmetry followed by a vertex flip take (R, q1, c) to (R, q2, +-c)? These maps form a group."""
    target = (canon(R), q2, norm_class(c))
    return any(act(R, q1, c, L, M, g, D, ab) == target for g, D in torus_group(L, M) for ab in FLIPS)


def placement_orbit(R, L, M):
    return {Ri for g, _D in torus_group(L, M) for ab in FLIPS for Ri in [image(R, g, ab)] if Ri is not None}


# ------------------------------------------------------------------ fitting twists (brute force)

def fits(R, L, M, q):
    """Is there a doubly allowed assignment (every triangle's gauged pattern in R and in its complement)?"""
    U = R & comp(R)
    V = L * M
    tris = []
    for j in range(M):
        for i in range(L):
            for offs in (UP, DN):
                corners, gauge = [], []
                for (di, dj) in offs:
                    ii, jj = i + di, j + dj
                    k1, k2 = ii // L, jj // M
                    corners.append((jj % M) * L + ii % L)
                    gauge.append((q[0] * k1 + q[1] * k2) & 1)
                tris.append((corners, gauge))
    for h in range(1 << V):
        if all(U >> sum((((h >> c[k]) & 1) ^ g[k]) << k for k in range(3)) & 1 for c, g in tris):
            return True
    return False


# ------------------------------------------------------------------ runs

def run_counts(binary, R, L, M, q):
    total = 1 << (2 * L * M)
    step = min(CHUNK, total)
    jobs = [(R, L, M, q, lo, min(total, lo + step)) for lo in range(0, total, step)]
    return jobs


def label_lone_loops(binary, L, M):
    """Lone-loop counts of the square-lattice orientation model on the L x M torus, per twist and axis class (labels.c)."""
    edges = []
    for y in range(M):
        for x in range(L):
            u = y * L + x
            edges.append((u, y * L + (x + 1) % L, (1 if x == L - 1 else 0, 0)))
            edges.append((u, ((y + 1) % M) * L + x, (0, 1 if y == M - 1 else 0)))
    text = "\n".join([f"{L * M} {len(edges)} 2"] + [f"{u} {w} {a} {b}" for u, w, (a, b) in edges] + ["4"]
                     + [f"{a} {b}" for a, b in TWISTS]) + "\n"
    E = len(edges)
    total = 1 << E
    pieces = WORKERS * 8
    step = -(-total // pieces)
    ranges = [(i * step, min(total, (i + 1) * step)) for i in range(pieces) if i * step < total]

    def one(r):
        return subprocess.run([binary, "exh", str(r[0]), str(r[1])], input=text, capture_output=True, text=True, check=True).stdout

    counts = {}
    with ThreadPoolExecutor(WORKERS) as ex:
        for out in ex.map(one, ranges):
            for line in out.splitlines():
                if line.startswith("sector"):
                    continue
                _l, s, rest = line.split(maxsplit=2)
                lab, n = rest.rsplit("=", 1)
                key = (TWISTS[int(s)], lab)
                counts[key] = counts.get(key, 0) + int(n)
    lone = {}
    for (q, lab), n in counts.items():
        if lab == "-":
            continue
        parts = []
        for part in lab.split("|"):
            rows = [tuple(int(v) for v in ch.split(",")) for ch in part[2:-1].split("][")]
            parts.append((part[0] == "o", rows))
        for c in CLASSES:
            if any(o for o, _r in parts) and all(all(r[0] * c[1] - r[1] * c[0] == 0 for r in rows) for _o, rows in parts):
                lone[(q, c)] = lone.get((q, c), 0) + n
    return lone


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    rows_path = OUT / "rows.jsonl"
    if rows_path.exists():
        rows_path.unlink()
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="tshield-"))
    tbin, lbin = str(build / "tshield"), str(build / "labels")
    subprocess.run(["gcc", "-O2", "-o", tbin, str(HERE / "tshield.c")], check=True)
    subprocess.run(["gcc", "-O2", "-o", lbin, str(HERE / "labels.c")], check=True)
    census = [json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()]
    tiling = [(r["R"], placement_type(r["R"], r["kind"])) for r in census if r["class"] == "TILING"]
    # orbit representatives for 4 x 4 (torus symmetries and uniform vertex flips, which fix every twist there)
    reps, seen = [], set()
    for R, _t in tiling:
        if R in seen:
            continue
        orb = placement_orbit(R, 4, 4)
        seen |= orb
        reps.append(min(orb))
    fails, records = [], []
    try:
        for fam, L, M in TORI:
            todo = [(R, t) for R, t in tiling if (L, M) != (4, 4) or R in reps]
            jobs = []
            for R, _t in todo:
                for q in TWISTS:
                    jobs += run_counts(tbin, R, L, M, q)

            def one(j):
                R, L_, M_, q, lo, hi = j
                out = subprocess.run([tbin, str(R), str(L_), str(M_), str(q[0]), str(q[1]), str(lo), str(hi)],
                                     capture_output=True, text=True, check=True).stdout.split()
                return (R, q), list(map(int, out))

            sums = {}
            with ThreadPoolExecutor(WORKERS) as ex:
                for key, vals in ex.map(one, jobs):
                    acc = sums.setdefault(key, [0] * 10)
                    for k in range(10):
                        acc[k] += vals[k]
            lone_ref = label_lone_loops(lbin, L, M)
            for R, t in todo:
                counts = {q: sums[(R, q)] for q in TWISTS}
                fit = [q for q in TWISTS if fits(R, L, M, q)]
                rec = {"family": fam, "L": L, "M": M, "R": R, "type": t, "fitting": [list(q) for q in fit],
                       "counts": {"".join(map(str, q)): {"n": v[0], "unsat": v[1], "cyl": v[2:5], "lone": v[5:8], "cross": v[8], "mism": v[9]}
                                  for q, v in counts.items()},
                       "pairs": []}
                for ci, c in enumerate(CLASSES):
                    odd = [q for q in TWISTS if all((((q[0] ^ f[0]) * c[0] + (q[1] ^ f[1]) * c[1]) & 1) for f in fit)] if fit else []
                    pd = (c[1] & 1, c[0] & 1)
                    if len(odd) == 2:
                        q1, q2 = odd
                        assert tuple(a ^ b for a, b in zip(q1, pd)) == q2
                        rec["pairs"].append({"class": list(c), "twists": ["".join(map(str, q1)), "".join(map(str, q2))],
                                             "lone": [counts[q1][5 + ci], counts[q2][5 + ci]],
                                             "cyl": [counts[q1][2 + ci], counts[q2][2 + ci]],
                                             "explained_by_symmetry": explained(R, L, M, c, q1, q2)})
                    elif odd:
                        fails.append(f"odd twists not a dual pair {L}x{M} R={R} c={c}: {odd}")
                if R == 63:
                    shift = (L % 2, M % 2)
                    rec["control_63"] = []
                    for ci, c in enumerate(CLASSES):
                        for q in TWISTS:
                            qq = tuple(a ^ b for a, b in zip(q, shift))
                            rec["control_63"].append([list(c), "".join(map(str, q)), counts[q][5 + ci], lone_ref.get((qq, c), 0)])
                records.append(rec)
                with open(rows_path, "a") as f:
                    f.write(json.dumps(rec, sort_keys=True) + "\n")
            print(fam, f"{L}x{M}", len(todo), "placements", round(time.time() - started), flush=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    # controls
    for rec in records:
        for qs, v in rec["counts"].items():
            if v["n"] != 1 << (2 * rec["L"] * rec["M"]):
                fails.append(f"orientations {rec['L']}x{rec['M']} R={rec['R']} {qs}")
            if v["mism"]:
                fails.append(f"torus tests disagree {rec['L']}x{rec['M']} R={rec['R']} {qs}")
        for c, qs, mine, ref in rec.get("control_63", []):
            if mine != ref:
                fails.append(f"placement 63 against the orientation model {rec['L']}x{rec['M']} c={c} {qs}: {mine} vs {ref}")
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails[:40],
              "rows": len(records), "workers": WORKERS, "orbit_representatives_4x4": reps}
    if fails:
        result["verdict"] = "invalid"
    else:
        p1_fail, p2_fail, p3_fail, p4_fail = [], [], [], []
        tally = {}
        for rec in records:
            fit = [tuple(q) for q in rec["fitting"]]
            for qs, v in rec["counts"].items():
                q = tuple(int(ch) for ch in qs)
                if q in fit and v["unsat"]:
                    p1_fail.append([rec["L"], rec["M"], rec["R"], qs, "fitting twist contradicts"])
                for ci, c in enumerate(CLASSES):
                    if v["cyl"][ci] and not all((((q[0] ^ f[0]) * c[0] + (q[1] ^ f[1]) * c[1]) & 1) for f in fit):
                        p1_fail.append([rec["L"], rec["M"], rec["R"], qs, f"cylinder along {c} contradicts in a twist even on it"])
            for p in rec["pairs"]:
                key = (rec["family"], rec["type"])
                t = tally.setdefault("/".join(key), {"pairs": 0, "nonzero": 0, "explained": 0, "unexplained_equal": 0, "unexplained_unequal": 0})
                t["pairs"] += 1
                nz = any(p["lone"])
                t["nonzero"] += nz
                if p["explained_by_symmetry"]:
                    t["explained"] += 1
                    continue
                if not nz:
                    continue
                equal = p["lone"][0] == p["lone"][1]
                t["unexplained_equal" if equal else "unexplained_unequal"] += 1
                row = [rec["L"], rec["M"], rec["R"], p["class"], p["twists"], p["lone"]]
                if rec["family"] == "F_fresh" and rec["type"] == "three" and equal:
                    p3_fail.append(row)
                if rec["family"] == "F_fresh" and rec["type"] == "shared-coin" and equal:
                    p4_fail.append(row)
            if rec["type"] == "orientation":
                for p in rec["pairs"]:
                    if p["lone"][0] != p["lone"][1]:
                        p2_fail.append([rec["L"], rec["M"], rec["R"], p["class"], p["twists"], p["lone"], "orientation pair unequal"])
        result["summary"] = {"P1_cylinder_parity_and_fitting": not p1_fail, "P1_failures": p1_fail[:20],
                             "P2_orientation_worlds_shield": not p2_fail, "P2_failures": p2_fail[:20],
                             "P3_no_unexplained_equal_three_place": not p3_fail, "P3_exceptions": p3_fail[:40],
                             "P4_no_unexplained_equal_shared_coin": not p4_fail, "P4_exceptions": p4_fail[:40],
                             "tally": tally}
        if p1_fail or p2_fail:
            result["verdict"] = "refuted"
        elif not p3_fail and not p4_fail:
            result["verdict"] = "supported"
        else:
            result["verdict"] = "partially supported"
    result["wall_seconds"] = round(time.time() - started, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
