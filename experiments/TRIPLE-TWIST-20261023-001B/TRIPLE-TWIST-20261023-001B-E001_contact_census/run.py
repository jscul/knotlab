#!/usr/bin/env python3
"""Producer for TRIPLE-TWIST-20261023-001B-E001: the census of twisted three-place contacts.

A contact has a visible fair bit x and three hidden places, the corners (a, b, c) of a triangle of the triangular lattice. It
allows the patterns R (a set of patterns p = h_a + 2 h_b + 4 h_c) when x = 0 and the complements of R when x = 1, so flipping all
three places exchanges its two relations and a twist is well defined. A twist of class (alpha, beta) flips the polarity of a place
when the path from the triangle's first corner to it crosses a seam with odd weight; on a torus this is the twist cocycle of the class.

For each of the 120 placements (R up to complementation, R not self-complementary):
- a tiling certificate: a doubly allowed assignment (every triangle's pattern allowed for both values of x) on some roster torus in
  some twist;
- a contradiction certificate: a planar patch with fair random x that admits no assignment;
- per torus and twist: whether a doubly allowed assignment exists, and the number of contradicting samples among 200;
- for placements with a tiling certificate and contradictions on a torus: minimal contradicting sets of triangles (deletion,
  per-triangle selectors) on the 4 x 6 and 6 x 6 tori, with the period lattice of each set (its winding).
Kinds: pair (R closed under majority), parity (R closed under minority), three (neither).

    .venv/bin/python -B run.py    writes rows.jsonl and result.json under artifacts/ (needs the PySAT package)
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path

from pysat.solvers import Glucose3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "TRIPLE-TWIST-20261023-001B" / HERE.name
PATCH_RADII = (4, 6)
TORI = ((4, 6, 0), (6, 4, 0), (6, 6, 0), (7, 7, 0), (5, 7, 2))
CORE_TORI = ((4, 6, 0), (6, 6, 0))
SAMPLES = 200
CORES_PER_TWIST = 30
TWISTS = ((0, 0), (0, 1), (1, 0), (1, 1))


def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def closed(R, op):
    pats = [p for p in range(8) if R >> p & 1]
    return all(R >> op(a, b, c) & 1 for a in pats for b in pats for c in pats)


def kind(R):
    if closed(R, lambda a, b, c: (a & b) | (b & c) | (a & c)):
        return "pair"
    if closed(R, lambda a, b, c: a ^ b ^ c):
        return "parity"
    return "three"


def placements():
    out = []
    for R in range(256):
        if R != comp(R) and R < comp(R):
            out.append(R)
    return out


def rng_for(*key):
    return random.Random(int(hashlib.sha256(repr(key).encode()).hexdigest()[:16], 16))


# ------------------------------------------------------------------ geometry

def torus(L, M, S, alpha, beta):
    """Triangles as (corners, gauges, offsets of the three sides) on the L x M torus with shear S; side offsets are deck
    coordinates (k1, k2) for the translations (L, 0) and (S, M)."""
    def reduce(i, j):
        k2, j2 = divmod(j, M)
        i2 = i - k2 * S
        k1, i3 = divmod(i2, L)
        return (i3, j2), (k1, k2)

    def vid(p):
        return p[1] * L + p[0]

    tris = []
    for j in range(M):
        for i in range(L):
            for (d1, d2) in (((1, 0), (1, 1)), ((0, 1), (1, 1))):
                b, ob = reduce(i + d1[0], j + d1[1])
                c, oc = reduce(i + d2[0], j + d2[1])
                gb = (alpha * ob[0] + beta * ob[1]) & 1
                gc = (alpha * oc[0] + beta * oc[1]) & 1
                # sides a->b, a->c, b->c with offsets
                sides = [((i, j), b, ob), ((i, j), c, oc), (b, c, (oc[0] - ob[0], oc[1] - ob[1]))]
                tris.append(((vid((i, j)), vid(b), vid(c)), (0, gb, gc), [(vid(u), vid(w), off) for u, w, off in sides]))
    return L * M, tris


def patch(r):
    ids = {}
    for q in range(-r, r + 1):
        for w in range(-r, r + 1):
            if abs(q + w) <= r:
                ids[(q, w)] = len(ids)
    tris = []
    for (q, w), a in ids.items():
        for d1, d2 in (((1, 0), (1, 1)), ((0, 1), (1, 1))):
            b, c = ids.get((q + d1[0], w + d1[1])), ids.get((q + d2[0], w + d2[1]))
            if b is not None and c is not None:
                tris.append(((a, b, c), (0, 0, 0), [(a, b, (0, 0)), (a, c, (0, 0)), (b, c, (0, 0))]))
    return len(ids), tris


# ------------------------------------------------------------------ clauses and solving

def tri_clauses(corners, gauge, rel):
    cl = []
    for p in range(8):
        if rel >> p & 1:
            continue
        lits = []
        for k in range(3):
            raw = ((p >> k) & 1) ^ gauge[k]
            lits.append(-(corners[k] + 1) if raw else corners[k] + 1)
        cl.append(lits)
    return cl


def solvable(tris, rels):
    with Glucose3() as s:
        for (corners, gauge, _sides), rel in zip(tris, rels):
            for c in tri_clauses(corners, gauge, rel):
                s.add_clause(c)
        return s.solve()


def core(V, tris, rels):
    """A minimal contradicting set of triangles (deletion with selector literals), or None if satisfiable."""
    with Glucose3() as s:
        sel = [V + 1 + k for k in range(len(tris))]
        for k, ((corners, gauge, _sides), rel) in enumerate(zip(tris, rels)):
            for c in tri_clauses(corners, gauge, rel):
                s.add_clause(c + [-sel[k]])
        if s.solve(assumptions=sel):
            return None
        keep = list(range(len(tris)))
        i = 0
        while i < len(keep):
            trial = keep[:i] + keep[i + 1:]
            if not s.solve(assumptions=[sel[k] for k in trial]):
                keep = trial
            else:
                i += 1
        return keep


def lattice(tris, idx):
    """Hermite basis of the period lattice (deck coordinates) of the sides of the chosen triangles."""
    pot, par, gens = {}, {}, []

    def find(v):
        acc = (0, 0)
        while par[v] != v:
            acc = (acc[0] + pot[v][0], acc[1] + pot[v][1])
            v = par[v]
        return v, acc

    for k in idx:
        for u, w, off in tris[k][2]:
            for v in (u, w):
                if v not in par:
                    par[v], pot[v] = v, (0, 0)
            (ru, pu), (rw, pw) = find(u), find(w)
            d = (pu[0] + off[0] - pw[0], pu[1] + off[1] - pw[1])
            if ru == rw:
                if d != (0, 0):
                    gens.append(d)
            else:
                par[rw], pot[rw] = ru, d
    return hermite2(gens)


def hermite2(gens):
    m = [list(g) for g in gens if any(g)]
    out, r = [], 0
    for c in range(2):
        live = [i for i in range(r, len(m)) if m[i][c] != 0]
        if not live:
            continue
        while len(live) > 1:
            p = min(live, key=lambda i: abs(m[i][c]))
            for i in live:
                if i != p:
                    f = m[i][c] // m[p][c]
                    m[i] = [a - f * b for a, b in zip(m[i], m[p])]
            live = [i for i in range(r, len(m)) if m[i][c] != 0]
        p = live[0]
        m[r], m[p] = m[p], m[r]
        if m[r][c] < 0:
            m[r] = [-a for a in m[r]]
        for i in range(r):
            f = m[i][c] // m[r][c]
            m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return [tuple(row) for row in m[:r]]


# ------------------------------------------------------------------ controls

def brute(V, tris, rels):
    for h in range(1 << V):
        ok = True
        for (corners, gauge, _s), rel in zip(tris, rels):
            p = sum((((h >> corners[k]) & 1) ^ gauge[k]) << k for k in range(3))
            if not rel >> p & 1:
                ok = False
                break
        if ok:
            return True
    return False


def controls():
    fails, stats = [], {}
    # the solver agrees with brute force on the 3 x 3 torus
    rng = rng_for("control-brute")
    agree = 0
    for _ in range(200):
        R = rng.choice(placements())
        a, b = rng.choice(TWISTS)
        V, tris = torus(3, 3, rng.randrange(3), a, b)
        rels = [comp(R) if rng.randint(0, 1) else R for _ in tris]
        agree += solvable(tris, rels) == brute(V, tris, rels)
    stats["solver agrees with brute force (3 x 3 tori, 200 instances)"] = agree
    if agree != 200:
        fails.append("solver disagrees with brute force")
    # a full row of triangles winds once horizontally; one triangle does not wind
    V, tris = torus(6, 6, 0, 0, 0)
    row = [k for k in range(len(tris)) if k // (2 * 6) == 2]
    stats["lattice of a full row"] = [list(v) for v in lattice(tris, row)]
    stats["lattice of one triangle"] = [list(v) for v in lattice(tris, [0])]
    if lattice(tris, row) != [(1, 0)] or lattice(tris, [0]) != []:
        fails.append("lattice computation")
    # a contractible seam (the twist cocycle of a disc of vertices) on a planar patch: for a complement-closed contact the seamed
    # instance with x is the plain instance with x flipped on the triangles whose first corner is in the disc (so the two are
    # equisatisfiable); for a contact that is not complement-closed (x or 1-in-3) the seam creates contradictions
    V, plain = patch(5)
    ids = {}
    for q in range(-5, 6):
        for w in range(-5, 6):
            if abs(q + w) <= 5:
                ids[(q, w)] = len(ids)
    disc = {v for (q, w), v in ids.items() if max(abs(q), abs(w), abs(q + w)) <= 2}
    seamed = [(c, tuple(int(v in disc) ^ int(c[0] in disc) for v in c), s) for c, _g, s in plain]
    rng = rng_for("control-seam")
    same = 0
    for R in (45, 159, 127, 1, 22, 105):
        Rb = comp(R)
        for _ in range(50):
            x = [rng.randint(0, 1) for _ in plain]
            a = solvable(seamed, [Rb if xi else R for xi in x])
            b = solvable(plain, [Rb if (xi ^ int(c[0] in disc)) else R for xi, (c, _g, _s) in zip(x, plain)])
            same += a == b
    stats["complement-closed contacts: seamed and re-flipped plain instances equisatisfiable (300)"] = same
    if same != 300:
        fails.append("a contractible seam is not a gauge for complement-closed contacts")
    R0, R1 = sum(1 << p for p in (1, 2, 4)), 255
    u0 = sum(not solvable(plain, [R1 if rng.randint(0, 1) else R0 for _ in plain]) for _ in range(300))
    u1 = sum(not solvable(seamed, [R1 if rng.randint(0, 1) else R0 for _ in seamed]) for _ in range(300))
    stats["x or 1-in-3, planar patch r=5: contradictions of 300 without, with a contractible seam"] = [u0, u1]
    if not (u0 == 0 and u1 >= 30):
        fails.append("control not rejected: a contractible seam did not create contradictions for a contact that is not complement-closed")
    return fails, stats


# ------------------------------------------------------------------ census

def census_row(R):
    Rb = comp(R)
    row = {"R": R, "allowed_x0": [format(p, "03b")[::-1] for p in range(8) if R >> p & 1], "kind": kind(R)}
    contradictions = {}
    for r in PATCH_RADII:
        V, tris = patch(r)
        rng = rng_for("patch", R, r)
        contradictions[str(r)] = sum(not solvable(tris, [Rb if rng.randint(0, 1) else R for _ in tris]) for _ in range(SAMPLES))
    row["patch_contradictions"] = contradictions
    tori, tiles = {}, False
    for (L, M, S) in TORI:
        for (a, b) in TWISTS:
            V, tris = torus(L, M, S, a, b)
            doubly = solvable(tris, [R & Rb] * len(tris))
            tiles |= doubly
            rng = rng_for("torus", R, L, M, S, a, b)
            un = sum(not solvable(tris, [Rb if rng.randint(0, 1) else R for _ in tris]) for _ in range(SAMPLES))
            tori[f"{L}x{M}s{S}({a},{b})"] = {"doubly_allowed": doubly, "contradictions": un}
    row["tori"] = tori
    row["tiling_certificate"] = tiles
    row["contradiction_certificate"] = any(contradictions.values())
    row["class"] = {(True, False): "TILING", (False, True): "LOCAL", (True, True): "BOTH", (False, False): "NONE"}[
        (tiles, row["contradiction_certificate"])]
    row["fits_everywhere"] = all(v["doubly_allowed"] for v in tori.values())
    row["contradicts_on_tori"] = any(v["contradictions"] for v in tori.values())
    if row["class"] == "TILING" and row["contradicts_on_tori"]:
        cores = {}
        for (L, M, S) in CORE_TORI:
            for (a, b) in TWISTS:
                key = f"{L}x{M}s{S}({a},{b})"
                if tori[key]["doubly_allowed"]:
                    continue
                V, tris = torus(L, M, S, a, b)
                rng = rng_for("core", R, L, M, S, a, b)
                found, tries = [], 0
                while len(found) < CORES_PER_TWIST and tries < 4 * SAMPLES:
                    tries += 1
                    rels = [Rb if rng.randint(0, 1) else R for _ in tris]
                    k = core(V, tris, rels)
                    if k is None:
                        continue
                    found.append({"size": len(k), "lattice": [list(v) for v in lattice(tris, k)]})
                cores[key] = {"tries": tries, "cores": found}
        row["cores"] = cores
    return row


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    fails, cstats = controls()
    rows_path = OUT / "rows.jsonl"
    if rows_path.exists():
        rows_path.unlink()
    rows = []
    if not fails:  # the census runs only when the controls pass
        for R in placements():
            row = census_row(R)
            rows.append(row)
            with open(rows_path, "a") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
    scoping = json.loads((HERE / "scoping_classes.json").read_text())
    pred_local = {R for R, c in scoping["classes"].items() if c == "LOCAL"}
    group_h = set(scoping["group_H"])
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails, "control_stats": cstats,
              "placements": len(rows)}
    if fails:
        result["verdict"] = "invalid"
    else:
        classes = {str(r["R"]): r["class"] for r in rows}
        both = [r["R"] for r in rows if r["class"] == "BOTH"]
        fit_contradicts = [(r["R"], k) for r in rows for k, v in r["tori"].items() if v["doubly_allowed"] and v["contradictions"]]
        cores = [(r["R"], r["kind"], k, c) for r in rows if r.get("cores") for k, v in r["cores"].items() for c in v["cores"]]
        contractible = [(R, k) for R, _kd, k, c in cores if not c["lattice"]]
        p1 = not both and not fit_contradicts and not contractible
        local = {R for R, c in classes.items() if c == "LOCAL"}
        p2 = all(c in ("LOCAL", "TILING") for c in classes.values()) and local == pred_local
        p3_fail = []
        for r in rows:
            if str(r["R"]) not in group_h:
                continue
            for (L, M, S) in TORI:
                keys = [f"{L}x{M}s{S}({a},{b})" for (a, b) in TWISTS]
                fit = [r["tori"][k]["doubly_allowed"] for k in keys]
                if not any(fit) or all(fit):
                    p3_fail.append([r["R"], f"{L}x{M}s{S}", "twists do not split"])
                for k in keys:
                    if not r["tori"][k]["doubly_allowed"] and r["tori"][k]["contradictions"] == 0:
                        p3_fail.append([r["R"], k, "non-fitting twist without contradictions"])
        three_cores = [c for _R, kd, _k, c in cores if kd == "three"]
        lines = [c for c in three_cores if len(c["lattice"]) == 1]
        rank = {}
        for _R, _kd, _k, c in cores:
            rank[str(len(c["lattice"]))] = rank.get(str(len(c["lattice"])), 0) + 1
        quiet = [r["R"] for r in rows if r["class"] == "TILING" and not r["fits_everywhere"] and not r["contradicts_on_tori"]]
        result["summary"] = {
            "classes": {c: sum(1 for v in classes.values() if v == c) for c in ("LOCAL", "TILING", "BOTH", "NONE")},
            "kinds_by_class": {c: {k: sum(1 for r in rows if r["class"] == c and r["kind"] == k) for k in ("pair", "parity", "three")}
                               for c in ("LOCAL", "TILING")},
            "tiling_fits_everywhere": [r["R"] for r in rows if r["class"] == "TILING" and r["fits_everywhere"]],
            "tiling_never_contradicting_though_some_twist_does_not_fit": quiet,
            "local_set_differences_with_scoping": sorted((local ^ pred_local), key=int),
            "P1_tiling_forbids_planar_and_fitting_contradictions_and_cores_wind": p1,
            "P1_details": {"both_certificates": both, "contradictions_in_fitting_twists": fit_contradicts[:20],
                           "contractible_cores": contractible[:20]},
            "P2_dichotomy_and_local_set_as_scoped": p2,
            "P3_group_H_twist_decides": not p3_fail,
            "P3_failures": p3_fail[:40],
            "P4_line_cores_in_three_place_placements": len(lines),
            "cores_total": len(cores), "cores_three_place": len(three_cores), "core_ranks": rank,
        }
        if not p1:
            result["verdict"] = "refuted"
        elif p2 and not p3_fail and lines:
            result["verdict"] = "supported"
        else:
            result["verdict"] = "partially supported"
    result["wall_seconds"] = round(time.time() - started, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
