#!/usr/bin/env python3
"""Independent check of TRIPLE-SHIELD-20261023-001A-E001; imports no producer code.

Reads the frozen contract, rows.jsonl and result.json, and:
- checks the roster (tori, placements, the 4 x 4 representatives), the totals 2^(2LM) and the torus-agreement counter;
- types the placements from the census with its own rule;
- recomputes the fitting twists of every row by brute force over hidden assignments (numpy), and from them the dual pairs;
- recomputes the torus contradiction counts of every placement and twist on 3 x 3 exactly, by its own dynamic program over the
  visible bits (bitsets of hidden assignments);
- checks single configurations against the producer's program: random ones and, on every torus, configurations that the
  program counts as lone lines, located by bisection. Each event is certified with a solver (PySAT, Glucose 3): a cylinder has
  an assignment when some cyclic cover of the torus along it, of at most 16 sheets, has one; it has none when a strip of 24
  periods has none;
- enumerates the lattice symmetries of each torus with its own code and decides explicitly, triangle by triangle, whether a
  symmetry followed by some change of hidden values e (any function on the vertices, found by brute force) relates two
  worlds: every triangle's allowed patterns must correspond, up to complement. This class of maps contains the producer's
  (symmetry, vertex flip) maps. From it the checker recomputes which dual pairs are explained and checks that every placement
  maps onto a 4 x 4 representative;
- recomputes P1 to P4 and the verdict from the frozen decision rule.

    .venv/bin/python -B check_result.py [artifact directory]
"""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
import tempfile
from itertools import product
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "artifacts/TRIPLE-SHIELD-20261023-001A" / HERE.name
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
TORI = [("F_seen", 3, 3), ("F_fresh", 3, 4), ("F_fresh", 4, 3), ("F_fresh", 4, 4)]
TWISTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
CLASSES = [(1, 0), (0, 1), (1, 1)]
UPO = ((0, 0), (1, 0), (1, 1))
DNO = ((0, 0), (0, 1), (1, 1))
COVERS, STRIP = 16, 24
RANDOM_PER_TWIST, BLOCK, BLOCKS = 2, 256, 6


def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def canon(R):
    return min(R, comp(R))


def own_type(R, kind):
    if kind == "three":
        return "three"
    dep = [k for k in range(3) if any((R >> p & 1) != (R >> (p ^ (1 << k)) & 1) for p in range(8))]
    if bin(R).count("1") == 6 and len(dep) == 2:
        return "orientation" if dep in ([0, 1], [1, 2]) else "diagonal-clause"
    return "shared-coin"


def qs(q):
    return f"{q[0]}{q[1]}"


# ------------------------------------------------------------------ the torus

def triangles(L, M):
    """Corner lattice points of triangle 2(jL + i) + t (t = 0 up, 1 down), base point in the fundamental domain."""
    return [[(i + a, j + b) for a, b in offs] for j in range(M) for i in range(L) for offs in (UPO, DNO)]


def vid(p, L, M):
    return (p[1] % M) * L + p[0] % L


def deck(p, L, M):
    return (p[0] // L, p[1] // M)


def gauge(p, q, L, M):
    d = deck(p, L, M)
    return (q[0] * d[0] + q[1] * d[1]) & 1


def fitting(R, L, M):
    """Twists with a doubly allowed assignment, by brute force over all hidden assignments."""
    V = L * M
    H = np.arange(1 << V, dtype=np.int64)
    U = R & comp(R)
    out = []
    for q in TWISTS:
        ok = np.ones(1 << V, dtype=bool)
        for P in triangles(L, M):
            pat = np.zeros(1 << V, dtype=np.int64)
            for k, p in enumerate(P):
                pat |= (((H >> vid(p, L, M)) & 1) ^ gauge(p, q, L, M)) << k
            ok &= ((U >> pat) & 1).astype(bool)
            if not ok.any():
                break
        if ok.any():
            out.append(q)
    return out


def torus_unsat_count(R, L, M, q):
    """Exact number of visible-bit configurations with no hidden assignment (dynamic program over bitsets)."""
    V = L * M
    H = np.arange(1 << V, dtype=np.int64)
    words = max(1, (1 << V) // 64)
    arr = np.full((1, words), np.uint64(0xFFFFFFFFFFFFFFFF))
    for P in triangles(L, M):
        pat = np.zeros(1 << V, dtype=np.int64)
        for k, p in enumerate(P):
            pat |= (((H >> vid(p, L, M)) & 1) ^ gauge(p, q, L, M)) << k
        a0 = np.packbits(((R >> pat) & 1).astype(np.uint8), bitorder="little").view(np.uint64)
        a1 = np.packbits(((comp(R) >> pat) & 1).astype(np.uint8), bitorder="little").view(np.uint64)
        arr = np.concatenate([arr & a0, arr & a1])
    return int((~arr.any(axis=1)).sum())


# ------------------------------------------------------------------ certificates for single configurations

def sheet(d, c):
    """t in d = s c + t u, where {c, u} is a basis of the deck lattice."""
    u = {(1, 0): (0, 1), (0, 1): (1, 0), (1, 1): (0, 1)}[c]
    det = c[0] * u[1] - c[1] * u[0]
    return (c[0] * d[1] - c[1] * d[0]) // det


def lifted_clauses(R, L, M, q, x, c, sheets, cyclic):
    """The world pulled back to the cover along c with the given number of sheets (cyclic) or to a strip of that many
    periods of the cylinder along c (not cyclic)."""
    var, clauses = {}, []
    for f, P in enumerate(triangles(L, M)):
        rel = comp(R) if (x >> f) & 1 else R
        g = [gauge(p, q, L, M) for p in P]
        corners = [(vid(p, L, M), sheet(deck(p, L, M), c)) for p in P]
        forbidden = [pat for pat in range(8) if not (rel >> pat) & 1]
        for m in range(sheets):
            vs = []
            for v, t in corners:
                key = (v, (t + m) % sheets if cyclic else t + m)
                vs.append(var.setdefault(key, len(var) + 1))
            for pat in forbidden:
                clauses.append([(-vs[k] if ((pat >> k) & 1) ^ g[k] else vs[k]) for k in range(3)])
    return clauses


def solvable(clauses):
    with Glucose3(bootstrap_with=clauses) as s:
        return s.solve()


def own_events(R, L, M, q, x):
    """(torus contradicts, [cylinder status per class: True contradicts, False has an assignment, None undetermined])."""
    if solvable(lifted_clauses(R, L, M, q, x, (1, 0), 1, True)):
        return False, [False, False, False]
    cyl = []
    for c in CLASSES:
        if not solvable(lifted_clauses(R, L, M, q, x, c, STRIP, False)):
            cyl.append(True)
        elif any(solvable(lifted_clauses(R, L, M, q, x, c, k, True)) for k in range(2, COVERS + 1)):
            cyl.append(False)
        else:
            cyl.append(None)
    return True, cyl


def program(binary, R, L, M, q, lo, hi):
    out = subprocess.run([binary, str(R), str(L), str(M), str(q[0]), str(q[1]), str(lo), str(hi)],
                         capture_output=True, text=True, check=True).stdout.split()
    return list(map(int, out))


def compare(binary, R, L, M, q, x, problems, stats):
    v = program(binary, R, L, M, q, x, x + 1)
    unsat, cyl = own_events(R, L, M, q, x)
    stats["configurations"] += 1
    if None in cyl:
        stats["undetermined"] += 1
        return
    lone = [int(cyl[k] and sum(cyl) == 1) for k in range(3)]
    mine = [1, int(unsat), *[int(b) for b in cyl], *lone, int(unsat and not any(cyl)), 0]
    if v != mine:
        problems.append(f"configuration {x} of R={R} on {L}x{M} twist {qs(q)}: program {v}, certificates {mine}")
    stats["lone_checked"] += sum(lone)


def find_lone(binary, R, L, M, q, rng):
    """A configuration the program counts as a lone line, located by bisection inside random aligned blocks."""
    total = 1 << (2 * L * M)
    for _ in range(BLOCKS):
        lo = rng.randrange(total // BLOCK) * BLOCK
        hi = lo + BLOCK
        if not sum(program(binary, R, L, M, q, lo, hi)[5:8]):
            continue
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if sum(program(binary, R, L, M, q, lo, mid)[5:8]):
                hi = mid
            else:
                lo = mid
        return lo
    return None


# ------------------------------------------------------------------ explicit maps

def own_point_group():
    nb = {(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1)}
    out = []
    for a, b, c, d in product((-1, 0, 1), repeat=4):
        if abs(a * d - b * c) == 1 and {(a * v[0] + b * v[1], c * v[0] + d * v[1]) for v in nb} == nb:
            out.append(((a, b), (c, d)))
    return out


def own_maps(L, M):
    """The lattice symmetries of the L x M torus."""
    return [g for g in own_point_group()
            if all((g[0][0] * w[0] + g[0][1] * w[1]) % L == 0 and (g[1][0] * w[0] + g[1][1] * w[1]) % M == 0
                   for w in ((L, 0), (0, M)))]


def class_image(g, c, L, M):
    w = (c[0] * L, c[1] * M)
    gw = (g[0][0] * w[0] + g[0][1] * w[1], g[1][0] * w[0] + g[1][1] * w[1])
    return (gw[0] // L, gw[1] // M)


_TRI, _BITS, _LOCAL = {}, {}, {}


def tri_index(L, M):
    """Triangles, and for each source triangle under each map: the target corners and where each source corner goes."""
    if (L, M) not in _TRI:
        tris = triangles(L, M)
        _TRI[(L, M)] = tris, {(vid(P[0], L, M), f & 1): f for f, P in enumerate(tris)}
    return _TRI[(L, M)]


def vertex_bits(V):
    if V not in _BITS:
        E = np.arange(1 << V, dtype=np.int64)
        _BITS[V] = [((E >> v) & 1).astype(np.uint8) for v in range(V)]
    return _BITS[V]


def local_table(R1, g1, R2, g2, to):
    """Values e at the target corners for which the triangle's allowed patterns correspond, up to complement."""
    key = (R1, g1, R2, g2, to)
    if key not in _LOCAL:
        valid = []
        for e in range(8):
            s, s0, s1 = [], [], []
            for h in range(8):
                hk = [(h >> k) & 1 for k in range(3)]
                s.append((R1 >> sum((hk[k] ^ g1[k]) << k for k in range(3))) & 1)
                h2 = [0, 0, 0]
                for k in range(3):
                    h2[to[k]] = hk[k] ^ ((e >> to[k]) & 1)
                p2 = sum((h2[m] ^ g2[m]) << m for m in range(3))
                s0.append((R2 >> p2) & 1)
                s1.append((comp(R2) >> p2) & 1)
            valid.append(s == s0 or s == s1)
        _LOCAL[key] = np.array(valid, dtype=np.uint8)
    return _LOCAL[key]


def map_ok(R1, q1, R2, q2, L, M, g):
    """Is there a function e on the vertices such that h'(g v) = h(v) + e(g v) carries every triangle's allowed patterns of
    world (R1, q1) onto those of its image triangle in world (R2, q2), up to complement? (e includes the vertex flips and the
    gauge that moves the transported twist onto its standard representative.)"""
    tris, index = tri_index(L, M)
    bits = vertex_bits(L * M)
    ok = None
    for P in tris:
        img = [(g[0][0] * p[0] + g[0][1] * p[1], g[1][0] * p[0] + g[1][1] * p[1]) for p in P]
        target = None
        for b in img:
            for t, offs in enumerate((UPO, DNO)):
                if {(b[0] + o[0], b[1] + o[1]) for o in offs} == set(img):
                    target = index[(vid(b, L, M), t)]
        P2 = tris[target]
        tv = [vid(p, L, M) for p in P2]
        to = tuple(tv.index(vid(p, L, M)) for p in img)
        table = local_table(R1, tuple(gauge(p, q1, L, M) for p in P), R2, tuple(gauge(p, q2, L, M) for p in P2), to)
        if not table.any():
            return False
        good = table[bits[tv[0]] | (bits[tv[1]] << 1) | (bits[tv[2]] << 2)]
        ok = good if ok is None else ok & good
        if not ok.any():
            return False
    return True


def own_explained(R, L, M, c, q1, q2, maps):
    for g in maps:
        if class_image(g, c, L, M) in (c, (-c[0], -c[1])) and map_ok(R, q1, R, q2, L, M, g):
            return True
    return False


# ------------------------------------------------------------------ main

def main() -> int:
    problems = []
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "rows.jsonl").read_text().splitlines() if l.strip()]
    census = [json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()]
    tiling = {r["R"]: own_type(r["R"], r["kind"]) for r in census if r["class"] == "TILING"}
    if contract["status"] != "Frozen" or len(tiling) != 54:
        problems.append("contract not frozen or census not 54 tiling placements")
    reps = result.get("orbit_representatives_4x4", [])
    by_torus = {}
    for r in rows:
        by_torus.setdefault((r["L"], r["M"]), []).append(r)
    for fam, L, M in TORI:
        got = sorted(r["R"] for r in by_torus.get((L, M), []))
        want = sorted(reps) if (L, M) == (4, 4) else sorted(tiling)
        if got != want:
            problems.append(f"roster {L}x{M}: {len(got)} rows, expected {len(want)}")
        for r in by_torus.get((L, M), []):
            if r["family"] != fam or r["type"] != tiling.get(r["R"]):
                problems.append(f"family or type of R={r['R']} on {L}x{M}")
            for q in TWISTS:
                v = r["counts"][qs(q)]
                if v["n"] != 1 << (2 * L * M) or v["mism"]:
                    problems.append(f"total or torus agreement R={r['R']} {L}x{M} {qs(q)}")
                if v["unsat"] < sum(v["lone"]) + v["cross"] or any(a < b for a, b in zip(v["cyl"], v["lone"])):
                    problems.append(f"inconsistent counts R={r['R']} {L}x{M} {qs(q)}")

    # fitting twists and dual pairs
    fit = {}
    for r in rows:
        L, M = r["L"], r["M"]
        f = fitting(r["R"], L, M)
        fit[(L, M, r["R"])] = f
        if sorted(map(list, f)) != sorted(r["fitting"]):
            problems.append(f"fitting twists R={r['R']} {L}x{M}: own {f}, rows {r['fitting']}")
        own_pairs = []
        for c in CLASSES:
            odd = [q for q in TWISTS if f and all((((q[0] ^ a) * c[0] + (q[1] ^ b) * c[1]) & 1) for a, b in f)]
            if len(odd) == 2:
                own_pairs.append((list(c), sorted(qs(q) for q in odd)))
        if own_pairs != [(p["class"], sorted(p["twists"])) for p in r["pairs"]]:
            problems.append(f"dual pairs R={r['R']} {L}x{M}: own {own_pairs}")
    print("fitting twists and pairs checked", flush=True)

    # exact torus counts on 3 x 3
    exact = 0
    for r in by_torus.get((3, 3), []):
        for q in TWISTS:
            n = torus_unsat_count(r["R"], 3, 3, q)
            exact += 1
            if n != r["counts"][qs(q)]["unsat"]:
                problems.append(f"3x3 torus count R={r['R']} {qs(q)}: own {n}, rows {r['counts'][qs(q)]['unsat']}")
    print("exact 3x3 torus counts", exact, flush=True)

    # single configurations
    stats = {"configurations": 0, "undetermined": 0, "lone_checked": 0, "lone_found": 0, "lone_searched": 0}
    with tempfile.TemporaryDirectory() as build:
        binary = str(Path(build) / "tshield")
        subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "tshield.c")], check=True)
        for r in rows:
            L, M = r["L"], r["M"]
            for q in TWISTS:
                key = f"{L}x{M}/{r['R']}/{qs(q)}"
                rng = random.Random(int(hashlib.sha256(key.encode()).hexdigest(), 16))
                for _ in range(RANDOM_PER_TWIST):
                    compare(binary, r["R"], L, M, q, rng.randrange(1 << (2 * L * M)), problems, stats)
                if sum(r["counts"][qs(q)]["lone"]):
                    stats["lone_searched"] += 1
                    x = find_lone(binary, r["R"], L, M, q, rng)
                    if x is not None:
                        stats["lone_found"] += 1
                        compare(binary, r["R"], L, M, q, x, problems, stats)
        print("single configurations", stats, flush=True)

    # explicit maps: explained pairs and the 4 x 4 representatives
    own_flags, disagreements = {}, []
    for r in rows:
        L, M = r["L"], r["M"]
        maps = own_maps(L, M)
        for p in r["pairs"]:
            q1, q2 = (tuple(int(ch) for ch in t) for t in p["twists"])
            e = own_explained(r["R"], L, M, tuple(p["class"]), q1, q2, maps)
            own_flags[(L, M, r["R"], tuple(p["class"]))] = e
            if e != p["explained_by_symmetry"]:
                disagreements.append([L, M, r["R"], p["class"], p["twists"], e])
    if disagreements:
        problems.append(f"explained flags differ on {len(disagreements)} pairs: {disagreements[:10]}")
    maps44 = own_maps(4, 4)
    uncovered = []
    for R in tiling:
        for q in TWISTS:
            if not any(map_ok(R, q, R0, q2, 4, 4, g) for g in maps44 for R0 in reps for q2 in TWISTS):
                uncovered.append((R, qs(q)))
    if uncovered:
        problems.append(f"placements not mapped onto a 4x4 representative: {uncovered}")
    print("maps checked", len(own_flags), "pairs; uncovered", uncovered, flush=True)

    # predictions and verdict
    controls_ok = not any(p.startswith(("total", "roster")) for p in problems)
    for r in rows:
        for c, q, mine, ref in r.get("control_63", []):
            if mine != ref:
                controls_ok = False
    p1 = p2 = p3 = p4 = True
    for r in rows:
        L, M, f = r["L"], r["M"], fit[(r["L"], r["M"], r["R"])]
        for q in TWISTS:
            v = r["counts"][qs(q)]
            if q in f and v["unsat"]:
                p1 = False
            for ci, c in enumerate(CLASSES):
                if v["cyl"][ci] and not all((((q[0] ^ a) * c[0] + (q[1] ^ b) * c[1]) & 1) for a, b in f):
                    p1 = False
        for p in r["pairs"]:
            equal = p["lone"][0] == p["lone"][1]
            if r["type"] == "orientation" and not equal:
                p2 = False
            if r["family"] != "F_fresh" or own_flags[(L, M, r["R"], tuple(p["class"]))] or not any(p["lone"]) or not equal:
                continue
            if r["type"] == "three":
                p3 = False
            if r["type"] == "shared-coin":
                p4 = False
    if not controls_ok:
        verdict = "invalid"
    elif not (p1 and p2):
        verdict = "refuted"
    elif p3 and p4:
        verdict = "supported"
    else:
        verdict = "partially supported"
    if verdict != result.get("verdict"):
        problems.append(f"verdict: own {verdict}, result {result.get('verdict')}")
    s = result.get("summary", {})
    for name, own in (("P1_cylinder_parity_and_fitting", p1), ("P2_orientation_worlds_shield", p2),
                      ("P3_no_unexplained_equal_three_place", p3), ("P4_no_unexplained_equal_shared_coin", p4)):
        if s.get(name) != own:
            problems.append(f"{name}: own {own}, result {s.get(name)}")
    print(json.dumps({"problems": problems[:40], "n_problems": len(problems), "own_verdict": verdict,
                      "P1": p1, "P2": p2, "P3": p3, "P4": p4, "exact_3x3_counts": exact, "single_configurations": stats,
                      "pairs_with_explicit_maps": len(own_flags)}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
