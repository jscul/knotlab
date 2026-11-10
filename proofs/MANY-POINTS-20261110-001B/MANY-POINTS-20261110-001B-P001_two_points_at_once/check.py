#!/usr/bin/env python3
"""Checks for MANY-POINTS-20261110-001B: two points at once (research/MANY-POINTS-20261110-001/preregistration.md, ticket B).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0, random.Random(3). Space (b) of NEST-ATOMS-20261110-001 for the Fano and thin (2,1,2) leaves; four floors written by the
frozen search; 40 sampled pairs of flipped points per category per floor. For each pair: the interaction I, the grid of the deterministic
rule D's two move sequences (every interleaving), the class (independent, meet, cancel, bind, single-stuck), and the address after M1
from both flips and from one."""
import hashlib
import importlib.util
import itertools
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(NA))
T0 = time.time()
OUT = {}
SEQ = "proofs/ADDRESS-SEQ-20261110-001A/ADDRESS-SEQ-20261110-001A-P001_writing_in_sequence"
NC = "proofs/NEST-ATOMS-20261110-001C/NEST-ATOMS-20261110-001C-P001_a_two_level_address/check.py"
DEPS = [SEQ + "/seq_lib.py", NC, "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py", "research/MANY-POINTS-20261110-001/preregistration.md"]
TARGETS = [(0, 1, 2), (0, 2, 3), (0, 1, 3), (1, 2, 3)]
CATS = ["different composites", "same composite", "outer pair", "outer and composite"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def descend(P, s, x, floor2, cap=60):
    """the rule D: the move lowering W most, first listed on ties, until the floor or stuck"""
    moves = []
    for _ in range(cap):
        vi, ag, w = P.full(s, x)
        if w == floor2:
            return moves, False, (s, x)
        best = None
        for m in P.neighbours(s, x, vi, ag, w):
            if m[3] < w and (best is None or m[3] < best[3]):
                best = m
        if best is None:
            return moves, True, (s, x)
        kind, t, y, _ = best
        moves.append(("x", (x ^ y).bit_length() - 1) if kind == "flip" else ("s", (s ^ t).bit_length() - 1))
        s, x = t, y
    return moves, P.full(s, x)[2] != floor2, (s, x)


def apply(cfg, m):
    s, x = cfg
    return (s, x ^ (1 << m[1])) if m[0] == "x" else (s ^ (1 << m[1]), x)


def sites(P, vi, ag):
    even = {v for v in range(P.V) if ag[v] % 2 == 0}
    out = {3 * i + k for i in range(P.n) if vi[i] for k in range(3)}
    out |= {3 * i + k for i in range(P.n) for k in range(3) if P.ends[i][k][0] in even or P.ends[i][k][1] in even}
    return out


def grid_ok(P, base, Dp, Dq):
    """every step of every interleaving of Dp and Dq from base is a legal move that does not raise W; returns (ok, end configuration)"""
    nodes = {}
    for i in range(len(Dp) + 1):
        for j in range(len(Dq) + 1):
            cfg = base
            for m in Dp[:i] + Dq[:j]:
                cfg = apply(cfg, m)
            nodes[(i, j)] = (cfg, P.full(*cfg))
    ok = True
    for (i, j), (cfg, (vi, ag, w)) in nodes.items():
        st = None
        for (di, dj, m) in ((1, 0, Dp[i] if i < len(Dp) else None), (0, 1, Dq[j] if j < len(Dq) else None)):
            if m is None:
                continue
            if m[0] == "s":
                st = sites(P, vi, ag) if st is None else st
                if m[1] not in st:
                    ok = False
            if nodes[(i + di, j + dj)][1][2] > w:
                ok = False
    return ok, nodes[(len(Dp), len(Dq))]


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    Q = load("seq_lib", DEPS[0])
    NCm = load("nest_c", NC)
    import spaces_lib as SP
    N = SP.N

    def role(K, Y, s, j):
        lines, outer, _ = Y.parts[j]
        return N.group_role(K, s, lines, outer)
    Q.LH.atom_role = role
    rng = random.Random(3)
    rows, summary = [], {}
    for leaf in ("Fano", "thin"):
        O = SP.outer_with([SP.C2(leaf), SP.C2(leaf)])
        K = O.K()
        Y = NCm.Shim(O, K)
        P = Q.C.Space(K, O.S)
        floor2 = abs(K.chi)
        levels = [Y.face_level(v) for v in range(K.V)]
        start = next(s for s in O.classes(K) if all(role(K, Y, s, j) == "transparent" for j in range(4)))
        model = K.sat(start)[1]
        cur = (sum(b << e for e, b in enumerate(start)), sum(int(model[p] > 0) << p for p in range(K.n)))
        where = {p: ("outer" if O.path[K.points[p]] == () else "C%d" % (O.path[K.points[p]][0] + 1)) for p in range(K.n)}
        pts = {w: [p for p in range(K.n) if where[p] == w] for w in ("outer", "C1", "C2")}
        pairs_by = {"different composites": [(p, q) for p in pts["C1"] for q in pts["C2"]],
                    "same composite": [pr for w in ("C1", "C2") for pr in itertools.combinations(pts[w], 2)],
                    "outer pair": list(itertools.combinations(pts["outer"], 2)),
                    "outer and composite": [(p, q) for p in pts["outer"] for q in pts["C1"] + pts["C2"]]}
        for target in TARGETS:
            found, _ = Q.search_from(Y, K, P, cur, set(target), 4, levels)
            F = found
            addr = Q.acting(K, Y, F[0], 4)
            sample = {c: rng.sample(pairs_by[c], 40) for c in CATS}
            single = {}

            def D_of(p):
                if p not in single:
                    cfg = (F[0], F[1] ^ (1 << p))
                    single[p] = (descend(P, *cfg, floor2), P.full(*cfg)[2])
                return single[p]
            for c in CATS:
                for p, q in sample[c]:
                    (Dp, stp, _), wp = D_of(p)
                    (Dq, stq, _), wq = D_of(q)
                    base = (F[0], F[1] ^ (1 << p) ^ (1 << q))
                    wpq = P.full(*base)[2]
                    I = ((wpq - floor2) - (wp - floor2) - (wq - floor2)) / 2
                    row = {"leaf": leaf, "floor": target, "floor acting": addr, "category": c, "p": p, "q": q, "I": I,
                           "moves p": len(Dp), "moves q": len(Dq)}
                    if stp or stq:
                        row["class"] = "single-stuck"
                    elif I < 0:
                        row["class"] = "cancel"
                    elif I > 0:
                        row["class"] = "bind"
                    else:
                        shared = bool(set(Dp) & set(Dq))
                        ok, (end, (_, _, wend)) = grid_ok(P, base, Dp, Dq)
                        endok = wend == floor2 and Q.acting(K, Y, end[0], 4) == addr
                        row.update({"shared moves": shared, "every order legal and not raising W": ok, "end at the floor with the address": endok})
                        row["class"] = "independent" if (not shared and ok and endok) else "meet"
                    s2, x2, w2 = Q.m1(P, base[0], base[1], floor2, rng)
                    row["held after two"] = w2 == floor2 and Q.acting(K, Y, s2, 4) == addr
                    s1, x1, w1 = Q.m1(P, F[0], F[1] ^ (1 << p), floor2, rng)
                    row["held after one"] = w1 == floor2 and Q.acting(K, Y, s1, 4) == addr
                    rows.append(row)
            print(round(time.time() - T0, 1), leaf, target, addr, dict(Counter((r["category"], r["class"]) for r in rows if r["leaf"] == leaf and r["floor"] == target)), flush=True)
    for c in CATS:
        rc = [r for r in rows if r["category"] == c]
        cls = Counter(r["class"] for r in rc)
        held2 = sum(r["held after two"] for r in rc) / len(rc)
        held1 = sum(r["held after one"] for r in rc) / len(rc)
        summary[c] = {"pairs": len(rc), "classes": dict(cls), "independent share": round(cls.get("independent", 0) / len(rc), 3),
                      "held after one": round(held1, 3), "held after two": round(held2, 3), "held ratio": round(held2 / held1, 3) if held1 else None,
                      "mean I among cancel and bind": round(sum(r["I"] for r in rc if r["class"] in ("cancel", "bind")) / max(1, sum(r["class"] in ("cancel", "bind") for r in rc)), 3)}
    check("1 two points at once (computed): classes and the address by category", True, {"summary": summary})
    ind = {c: summary[c]["independent share"] for c in CATS}
    OUT["predictions"] = {
        "B1: at least 90% of different-composite pairs independent": ind["different composites"] >= 0.9,
        "B2: independence higher for different composites than for the same composite and for outer pairs":
            ind["different composites"] > ind["same composite"] and ind["different composites"] > ind["outer pair"],
        "B3: held after two at least 0.9 of held after one in every category": all((summary[c]["held ratio"] or 0) >= 0.9 for c in CATS),
        "failure: under 50% different-composite independent, or a held ratio under 0.5": ind["different composites"] < 0.5 or any((summary[c]["held ratio"] or 0) < 0.5 for c in CATS),
        "stop: every category at least 90% independent": all(v >= 0.9 for v in ind.values())}
    print(json.dumps(summary, indent=1), json.dumps(OUT["predictions"], indent=1), flush=True)
    OUT["rows"] = rows
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info") if isinstance(old.get(k), dict) and "info" in old.get(k, {}) else old.get(k), sort_keys=True)
                != json.dumps(fresh[k]["info"] if isinstance(fresh[k], dict) and "info" in fresh[k] else fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
