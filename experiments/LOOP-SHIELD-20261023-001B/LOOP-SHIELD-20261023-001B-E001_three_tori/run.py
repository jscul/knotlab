#!/usr/bin/env python3
"""Producer for LOOP-SHIELD-20261023-001B-E001: lone odd lines on thin and cubic 3-tori in all eight twists.

A 3-torus Lx x Ly x Lz carries the cubic lattice; each edge has its lattice offset in Z^3, and the twist q in {0,1}^3 acts on an edge
by q.offset mod 2. Every sampled orientation is classified in all eight twists by lineev.c (compiled here with gcc -O2), which also
counts, for each pair of twists, the samples in which both have a lone line of the same class; these joint counts give exact variances
for differences between twists. Monte Carlo rows run on worker threads, each chunk with its own seed (the first 8 bytes of
sha256("loop-shield/<label>/<chunk>")). Checks: the 3 x 3 torus and the 2 x 2 x 2 3-torus are enumerated exhaustively, and a slice
of masks of 3 x 2 x 2 is enumerated exactly for the checker's replay.

    python3 -B run.py    writes raw_rows.jsonl (row by row) and result.json under artifacts/
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "LOOP-SHIELD-20261023-001B" / HERE.name
WORKERS = min(24, os.cpu_count() or 1)
ROSTER = [  # (family, label, kind, sizes, mode, amount): mode exh enumerates masks [0, amount), mc draws amount samples
    ("F_check", "torus 3x3 s=0", "torus", (3, 3, 0), "exh", 1 << 18),
    ("F_check", "2x2x2", "torus3", (2, 2, 2), "exh", 1 << 24),
    ("F_check", "3x2x2 slice", "torus3", (3, 2, 2), "exh", 40000),
    ("F_thin", "3x2x2", "torus3", (3, 2, 2), "mc", 1_000_000_000),
    ("F_thin", "3x3x2", "torus3", (3, 3, 2), "mc", 500_000_000),
    ("F_thin", "4x3x2", "torus3", (4, 3, 2), "mc", 500_000_000),
    ("F_thin", "4x4x2", "torus3", (4, 4, 2), "mc", 500_000_000),
    ("F_cubic", "3x3x3", "torus3", (3, 3, 3), "mc", 1_500_000_000),
]
MIN_EVENTS = 1000          # a class is decision-bearing on a row when its lone lines, summed over the twists odd on it, reach this
Z_DIFFERS, Z_EQUAL, Z_SYMMETRY = 5.0, 2.0, 4.0


def torus2(Lh, Lv, s):
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
    return Lh * Lv, edges


def torus3(L1, L2, L3):
    vid = lambda x, y, z: x + L1 * (y + L2 * z)
    edges = []
    for z in range(L3):
        for y in range(L2):
            for x in range(L1):
                u = vid(x, y, z)
                edges.append((u, vid((x + 1) % L1, y, z), ((x + 1) // L1, 0, 0)))
                edges.append((u, vid(x, (y + 1) % L2, z), (0, (y + 1) // L2, 0)))
                edges.append((u, vid(x, y, (z + 1) % L3), (0, 0, (z + 1) // L3)))
    return L1 * L2 * L3, edges


def spec(kind, sizes):
    V, edges = (torus2 if kind == "torus" else torus3)(*sizes)
    K = len(edges[0][2])
    twists = list(product((0, 1), repeat=K))
    text = "\n".join([f"{V} {len(edges)} {K}"] + [f"{u} {w} " + " ".join(map(str, o)) for u, w, o in edges]
                     + [str(len(twists))] + [" ".join(map(str, a)) for a in twists]) + "\n"
    return text, twists, V, len(edges)


def parse(out):
    sectors, joint = {}, {}
    for line in out.splitlines():
        p = line.split()
        if p[0] == "sector":
            d = {"lines": {}}
            for item in p[2:]:
                k, v = item.rsplit("=", 1)
                if k.startswith("w:"):
                    d["lines"][k[2:]] = int(v)
                else:
                    d[k] = int(v)
            sectors[int(p[1])] = d
        else:
            joint[(int(p[1]), int(p[2]))] = {k[2:]: int(v) for k, v in (item.rsplit("=", 1) for item in p[3:])}
    return sectors, joint


def merge(acc, part):
    sectors, joint = part
    for s, d in sectors.items():
        a = acc[0].setdefault(s, {"lines": {}})
        for k, v in d.items():
            if k == "lines":
                for c, n in v.items():
                    a["lines"][c] = a["lines"].get(c, 0) + n
            else:
                a[k] = a.get(k, 0) + v
    for key, d in joint.items():
        a = acc[1].setdefault(key, {})
        for c, n in d.items():
            a[c] = a.get(c, 0) + n


def seed(label, chunk):
    return int.from_bytes(hashlib.sha256(f"loop-shield/{label}/{chunk}".encode()).digest()[:8], "big")


def run_row(binary, text, label, mode, amount):
    pieces = WORKERS * 8
    step = -(-amount // pieces)
    if mode == "exh":
        jobs = [("exh", str(i * step), str(min(amount, (i + 1) * step))) for i in range(pieces) if i * step < amount]
    else:
        jobs = [("mc", str(seed(label, i)), str(min(amount, (i + 1) * step) - i * step)) for i in range(pieces) if i * step < amount]

    def one(j):
        return parse(subprocess.run([binary, *j], input=text, capture_output=True, text=True, check=True).stdout)

    acc = ({}, {})
    with ThreadPoolExecutor(WORKERS) as ex:
        for part in ex.map(one, jobs):
            merge(acc, part)
    return acc


def norm(c):
    return c if next(v for v in c if v) > 0 else tuple(-v for v in c)


def symmetries(sizes):
    """Axis permutations of the box that preserve its side lengths (reflections fix every twist mod 2 and every axis class)."""
    return [p for p in permutations(range(3)) if all(sizes[p[i]] == sizes[i] for i in range(3))]


def comparisons(row):
    """For each class with lone odd lines: the twists odd on it and every pairwise comparison with an exact z."""
    twists = [tuple(a) for a in row["twists"]]
    N = row["sectors"]["0"]["n"]
    counts, joint = {}, {}
    for s, d in row["sectors"].items():
        for c, n in d["lines"].items():
            counts[(twists[int(s)], tuple(map(int, c.split(","))))] = n
    for key, d in row["joint"].items():
        s, t = map(int, key.split(","))
        for c, n in d.items():
            joint[(twists[s], twists[t], tuple(map(int, c.split(","))))] = n
    syms = symmetries(row["sizes"])
    out = []
    for c in sorted({c for (_a, c) in counts}):
        odd = [a for a in twists if sum(p * q for p, q in zip(a, c)) & 1]
        total = sum(counts.get((a, c), 0) for a in odd)
        if not total:
            continue
        rec = {"class": list(c), "events": total, "decision_bearing": total >= MIN_EVENTS,
               "counts": {"".join(map(str, a)): counts.get((a, c), 0) for a in odd}, "pairs": []}
        for i, a in enumerate(odd):
            for b in odd[i + 1:]:
                na, nb = counts.get((a, c), 0), counts.get((b, c), 0)
                nab = joint.get((a, b, c), joint.get((b, a, c), 0))
                pa, pb, pab = na / N, nb / N, nab / N
                var = N * (pa + pb - 2 * pab - (pa - pb) ** 2)
                z = (na - nb) / math.sqrt(var) if var > 0 else (0.0 if na == nb else math.inf)
                rel = math.sqrt(var) / max(1, (na + nb) / 2)
                sym = any(norm(tuple(c[p[k]] for k in range(3))) == c and tuple(a[p[k]] for k in range(3)) == b for p in syms) \
                    if len(c) == 3 else False
                rec["pairs"].append({"twists": ["".join(map(str, a)), "".join(map(str, b))], "counts": [na, nb], "joint": nab,
                                     "z": round(z, 3) if math.isfinite(z) else "inf", "relative_se": round(rel, 5),
                                     "symmetric": sym})
        out.append(rec)
    return out


def cross_class(row):
    """Symmetries that move one class to another: count(a, c) and count(pi a, pi c) must agree (conservative z, no joint term)."""
    twists = [tuple(a) for a in row["twists"]]
    N = row["sectors"]["0"]["n"]
    counts = {}
    for s, d in row["sectors"].items():
        for c, n in d["lines"].items():
            counts[(twists[int(s)], tuple(map(int, c.split(","))))] = n
    out = []
    for p in symmetries(row["sizes"]):
        for (a, c), n in sorted(counts.items()):
            pc = norm(tuple(c[p[k]] for k in range(3)))
            pa = tuple(a[p[k]] for k in range(3))
            if pc == c or (a, c) > (pa, pc):
                continue
            m = counts.get((pa, pc), 0)
            var = n + m
            out.append({"twists": ["".join(map(str, a)), "".join(map(str, pa))], "classes": [list(c), list(pc)], "counts": [n, m],
                        "z": round((n - m) / var ** 0.5, 3) if var else 0.0, "decision_bearing": n + m >= MIN_EVENTS // 2})
    return out


def analyse(rows):
    report, fails_sym, unrelated = [], [], []
    for r in rows:
        if r["family"] not in ("F_thin", "F_cubic"):
            continue
        comps = comparisons(r)
        cross = cross_class(r)
        report.append({"label": r["label"], "family": r["family"], "classes": comps, "cross_class_symmetry": cross})
        for q in cross:
            if q["decision_bearing"] and abs(q["z"]) >= Z_SYMMETRY:
                fails_sym.append((r["label"], q["classes"], q["twists"], q["z"]))
        for rec in comps:
            for p in rec["pairs"]:
                z = math.inf if p["z"] == "inf" else abs(p["z"])
                if p["symmetric"] and rec["decision_bearing"] and z >= Z_SYMMETRY:
                    fails_sym.append((r["label"], rec["class"], p["twists"], p["z"]))
                if not p["symmetric"] and rec["decision_bearing"] and r["family"] == "F_thin":
                    unrelated.append({"row": r["label"], "class": rec["class"], "twists": p["twists"], "z": p["z"],
                                      "relative_se": p["relative_se"]})
    differs = [u for u in unrelated if u["z"] == "inf" or abs(u["z"]) > Z_DIFFERS]
    equal = [u for u in unrelated if u["z"] != "inf" and abs(u["z"]) < Z_EQUAL and u["relative_se"] < 0.02]
    cubic = [p for rec in next((x["classes"] for x in report if x["family"] == "F_cubic"), []) for p in rec["pairs"]
             if not p["symmetric"] and (p["z"] == "inf" or abs(p["z"]) > Z_DIFFERS)]
    return {"rows": report, "symmetry_failures": fails_sym, "unrelated_comparisons": len(unrelated),
            "unrelated_differ": len(differs), "unrelated_equal_resolved": equal, "cubic_unrelated_differ": len(cubic)}


def controls(rows):
    fails = []
    for r in rows:
        twisted = [any(a) for a in r["twists"]]
        n0 = r["sectors"]["0"]["n"]
        for s, d in r["sectors"].items():
            if d["c"] + d["x"] + sum(d["lines"].values()) != d["n"] or d["n"] != n0:
                fails.append(f"totals {r['label']} twist {s}")
            if d["mis"]:
                fails.append(f"swap-invariance test {r['label']} twist {s}")
            if not twisted[int(s)] and d["inv"]:
                fails.append(f"untwisted flagged {r['label']}")
    return fails


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / "raw_rows.jsonl"
    if raw.exists():
        raw.unlink()
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="lineev-"))
    binary = str(build / "lineev")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "lineev.c")], check=True)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rows = []
    try:
        for fam, label, kind, sizes, mode, amount in ROSTER:
            text, twists, V, E = spec(kind, sizes)
            sectors, joint = run_row(binary, text, label, mode, amount)
            row = {"family": fam, "label": label, "kind": kind, "sizes": list(sizes), "mode": mode, "amount": amount,
                   "vertices": V, "edges": E, "twists": [list(a) for a in twists],
                   "sectors": {str(s): sectors[s] for s in sorted(sectors)},
                   "joint": {f"{a},{b}": joint[(a, b)] for a, b in sorted(joint)}}
            rows.append(row)
            with open(raw, "a") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
            print(fam, label, mode, amount, round(time.time() - started), flush=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    fails = controls(rows)
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "rows": len(rows), "compiler": gcc, "workers": WORKERS}
    a = analyse(rows) if not fails else None
    if a is not None and a["symmetry_failures"]:
        fails.append("symmetric comparisons differ")
    result["controls_ok"], result["control_failures"] = not fails, fails
    if fails:
        result["verdict"] = "invalid"
    else:
        result["analysis"] = a
        if a["unrelated_comparisons"] == 0:
            result["verdict"] = "inconclusive"
        elif a["unrelated_differ"] == a["unrelated_comparisons"]:
            result["verdict"] = "supported"
        elif a["unrelated_equal_resolved"]:
            result["verdict"] = "refuted"
        else:
            result["verdict"] = "mixed"
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds") if k in result}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
