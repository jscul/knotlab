#!/usr/bin/env python3
"""Independent check of the three-place census; imports no producer code (standard library only).

Parses rows.jsonl, result.json, the contract and the scoping file, and:
- recomputes every class, the kinds, the summary counts, P1-P4 and the verdict from the rows;
- with its own geometry and its own solver (unit propagation and branching):
  - confirms every claimed doubly allowed assignment on the 4 x 6 and 6 x 6 tori, and every claimed absence on them, for all 120
    placements;
  - replays the sample streams (same seeding rule) and confirms, for every LOCAL placement, that the first contradicting planar sample
    of the radius-4 patch really contradicts, and for 12 TILING placements that the radius-4 patch samples never contradict;
  - replays the core streams of 15 placement-twists and recomputes the minimal contradicting sets by deletion, comparing sizes and
    winding ranks with the producer's.

    python3 -B check_result.py
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B" / HERE.name
TWISTS = ((0, 0), (0, 1), (1, 0), (1, 1))
TORI = ((4, 6, 0), (6, 4, 0), (6, 6, 0), (7, 7, 0), (5, 7, 2))


def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def kind(R):
    pats = [p for p in range(8) if R >> p & 1]
    if all(R >> ((a & b) | (b & c) | (a & c)) & 1 for a in pats for b in pats for c in pats):
        return "pair"
    if all(R >> (a ^ b ^ c) & 1 for a in pats for b in pats for c in pats):
        return "parity"
    return "three"


def stream(*key):
    return random.Random(int(hashlib.sha256(repr(key).encode()).hexdigest()[:16], 16))


def tri_torus(L, M, S, alpha, beta):
    """Own construction: lattice points (i, j) of the fundamental domain; neighbours reduced by the deck translations (L, 0) and (S, M)."""
    def red(i, j):
        k2 = j // M
        i -= k2 * S
        j -= k2 * M
        k1 = i // L
        return (i - k1 * L, j), (k1, k2)

    num = lambda p: p[0] + L * p[1]
    out = []
    for j in range(M):
        for i in range(L):
            for steps in (((1, 0), (1, 1)), ((0, 1), (1, 1))):
                pts, offs = [(i, j)], [(0, 0)]
                for di, dj in steps:
                    q, o = red(i + di, j + dj)
                    pts.append(q)
                    offs.append(o)
                gauge = tuple((alpha * o[0] + beta * o[1]) % 2 for o in offs)
                edges = [(num(pts[0]), num(pts[1]), offs[1]), (num(pts[0]), num(pts[2]), offs[2]),
                         (num(pts[1]), num(pts[2]), (offs[2][0] - offs[1][0], offs[2][1] - offs[1][1]))]
                out.append(((num(pts[0]), num(pts[1]), num(pts[2])), gauge, edges))
    return L * M, out


def hex_patch(r):
    ids = {}
    for q in range(-r, r + 1):
        for w in range(-r, r + 1):
            if abs(q + w) <= r:
                ids[(q, w)] = len(ids)
    out = []
    for (q, w), a in ids.items():
        for (d1, d2) in (((1, 0), (1, 1)), ((0, 1), (1, 1))):
            b = ids.get((q + d1[0], w + d1[1]))
            c = ids.get((q + d2[0], w + d2[1]))
            if b is not None and c is not None:
                out.append(((a, b, c), (0, 0, 0), [(a, b, (0, 0)), (a, c, (0, 0)), (b, c, (0, 0))]))
    return len(ids), out


def encode(tris, rels):
    cls = []
    for (cs, g, _e), rel in zip(tris, rels):
        for p in range(8):
            if not rel >> p & 1:
                cls.append(tuple((-(cs[k] + 1)) if ((p >> k) & 1) ^ g[k] else cs[k] + 1 for k in range(3)))
    return cls


def satisfiable(n, cls):
    """Unit propagation with watched counting replaced by plain scans; branching on the most frequent free variable."""
    occ = {}
    for c in cls:
        for l in c:
            occ[abs(l)] = occ.get(abs(l), 0) + 1
    order = sorted(occ, key=lambda v: -occ[v])
    val = {}

    def lit(l):
        v = val.get(abs(l))
        return None if v is None else v == (l > 0)

    def unit(trail):
        while True:
            moved = False
            for c in cls:
                free, done = None, False
                nfree = 0
                for l in c:
                    s = lit(l)
                    if s:
                        done = True
                        break
                    if s is None:
                        nfree += 1
                        free = l
                if done:
                    continue
                if nfree == 0:
                    return False
                if nfree == 1:
                    val[abs(free)] = free > 0
                    trail.append(abs(free))
                    moved = True
            if not moved:
                return True

    def go():
        trail = []
        if unit(trail):
            v = next((v for v in order if v not in val), None)
            if v is None:
                return True
            for b in (True, False):
                val[v] = b
                if go():
                    return True
                del val[v]
        for v in trail:
            del val[v]
        return False

    return go()


def rank(tris, idx):
    parent, pot, gens = {}, {}, []

    def find(v):
        acc = (0, 0)
        while parent[v] != v:
            acc = (acc[0] + pot[v][0], acc[1] + pot[v][1])
            v = parent[v]
        return v, acc

    for k in idx:
        for u, w, off in tris[k][2]:
            for v in (u, w):
                parent.setdefault(v, v)
                pot.setdefault(v, (0, 0))
            (ru, pu), (rw, pw) = find(u), find(w)
            d = (pu[0] + off[0] - pw[0], pu[1] + off[1] - pw[1])
            if ru == rw:
                if d != (0, 0):
                    gens.append(d)
            else:
                parent[rw], pot[rw] = ru, d
    if not gens:
        return 0
    a, b = gens[0], None
    for g in gens[1:]:
        if a[0] * g[1] - a[1] * g[0] != 0:
            b = g
            break
    return 1 if b is None else 2


def minimal(n, tris, rels):
    keep = list(range(len(tris)))
    i = 0
    while i < len(keep):
        trial = keep[:i] + keep[i + 1:]
        if not satisfiable(n, encode([tris[k] for k in trial], [rels[k] for k in trial])):
            keep = trial
        else:
            i += 1
    return keep


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    scoping = json.loads((HERE / "scoping_classes.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "rows.jsonl").read_text().splitlines() if l.strip()]
    problems = []
    expected = [R for R in range(256) if R != comp(R) and R < comp(R)]
    if [r["R"] for r in rows] != expected:
        problems.append("placements differ")
    # classes from the rows
    for r in rows:
        tiles = any(v["doubly_allowed"] for v in r["tori"].values())
        local = any(r["patch_contradictions"].values())
        cls = {(True, False): "TILING", (False, True): "LOCAL", (True, True): "BOTH", (False, False): "NONE"}[(tiles, local)]
        if cls != r["class"] or kind(r["R"]) != r["kind"]:
            problems.append(f"class or kind of {r['R']}")
    # own geometry: doubly allowed assignments on the 4 x 6 and 6 x 6 tori
    agree = total = 0
    for r in rows:
        R, Rb = r["R"], comp(r["R"])
        for (L, M, S) in ((4, 6, 0), (6, 6, 0)):
            for (a, b) in TWISTS:
                n, tris = tri_torus(L, M, S, a, b)
                mine = satisfiable(n, encode(tris, [R & Rb] * len(tris)))
                total += 1
                agree += mine == r["tori"][f"{L}x{M}s{S}({a},{b})"]["doubly_allowed"]
    if agree != total:
        problems.append(f"doubly allowed assignments disagree on {total - agree} of {total}")
    # replayed planar samples
    n4, p4 = hex_patch(4)
    local_ok = local_tot = 0
    tiling_quiet = 0
    tiling_rows = [r for r in rows if r["class"] == "TILING"][:12]
    for r in rows:
        R, Rb = r["R"], comp(r["R"])
        rng = stream("patch", R, 4)
        if r["class"] == "LOCAL":
            if r["patch_contradictions"]["4"] == 0:
                continue
            local_tot += 1
            for _ in range(200):
                x = [rng.randint(0, 1) for _ in p4]
                if not satisfiable(n4, encode(p4, [Rb if xi else R for xi in x])):
                    local_ok += 1
                    break
        elif r in tiling_rows:
            quiet = True
            for _ in range(200):
                x = [rng.randint(0, 1) for _ in p4]
                if not satisfiable(n4, encode(p4, [Rb if xi else R for xi in x])):
                    quiet = False
                    break
            tiling_quiet += quiet
    if local_ok != local_tot:
        problems.append(f"replayed local certificates: {local_ok} of {local_tot}")
    if tiling_quiet != len(tiling_rows):
        problems.append("a replayed tiling placement contradicted on the radius-4 patch")
    # replayed cores
    replay = []
    for r in rows:
        if r.get("cores"):
            for key, v in r["cores"].items():
                if v["cores"]:
                    replay.append((r["R"], key, v["cores"]))
    replay = replay[::max(1, len(replay) // 15)][:15]
    core_agree = core_tot = 0
    for R, key, cores in replay:
        Rb = comp(R)
        dims, tw = key.split("(")
        L, rest = dims.split("x")
        M, S = rest.split("s")
        a, b = int(tw[0]), int(tw[2])
        L, M, S = int(L), int(M), int(S)
        n, tris = tri_torus(L, M, S, a, b)
        rng = stream("core", R, L, M, S, a, b)
        found = 0
        tries = 0
        while found < min(3, len(cores)) and tries < 800:
            tries += 1
            rels = [Rb if rng.randint(0, 1) else R for _ in tris]
            if satisfiable(n, encode(tris, rels)):
                continue
            k = minimal(n, tris, rels)
            want = cores[found]
            core_tot += 1
            core_agree += len(k) == want["size"] and rank(tris, k) == len(want["lattice"])
            found += 1
    if core_agree != core_tot:
        problems.append(f"replayed cores disagree on {core_tot - core_agree} of {core_tot}")
    # predictions and verdict from the rows
    pred_local = {R for R, c in scoping["classes"].items() if c == "LOCAL"}
    local = {str(r["R"]) for r in rows if r["class"] == "LOCAL"}
    both = [r for r in rows if r["class"] == "BOTH"]
    fit_contra = [r["R"] for r in rows for v in r["tori"].values() if v["doubly_allowed"] and v["contradictions"]]
    contractible = [r["R"] for r in rows if r.get("cores") for v in r["cores"].values() for c in v["cores"] if not c["lattice"]]
    p1 = not both and not fit_contra and not contractible
    p2 = all(r["class"] in ("LOCAL", "TILING") for r in rows) and local == pred_local
    p3 = True
    for r in rows:
        if str(r["R"]) not in set(scoping["group_H"]):
            continue
        for (L, M, S) in TORI:
            fits = [r["tori"][f"{L}x{M}s{S}({a},{b})"] for (a, b) in TWISTS]
            if all(f["doubly_allowed"] for f in fits) or not any(f["doubly_allowed"] for f in fits):
                p3 = False
            if any(not f["doubly_allowed"] and f["contradictions"] == 0 for f in fits):
                p3 = False
    lines = sum(1 for r in rows if r["kind"] == "three" and r.get("cores") for v in r["cores"].values() for c in v["cores"]
                if len(c["lattice"]) == 1)
    verdict = "invalid" if not result["controls_ok"] else ("refuted" if not p1 else ("supported" if p2 and p3 and lines else "partially supported"))
    if verdict != result["verdict"]:
        problems.append(f"verdict {verdict} vs producer {result['verdict']}")
    if lines != result["summary"]["P4_line_cores_in_three_place_placements"]:
        problems.append("line count differs")
    print(json.dumps({"problems": problems, "doubly_allowed_checked": total, "local_certificates_replayed": local_tot,
                      "tiling_patches_replayed": len(tiling_rows), "cores_replayed": core_tot, "verdict": verdict,
                      "contract_status": contract["status"]}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
