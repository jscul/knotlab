#!/usr/bin/env python3
"""Checks for COMPOSITE-FN-20261110-001C: points interact only through a shared line (B112; research/COMPOSITE-FN-20261110-001/
preregistration.md, ticket C).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0, random.Random(112). Fresh composites: the outer host K_2 with two composites C(3, leaf) (K_3 with two leaves at its l0
and its farthest line), for the Fano and thin (2,1,2) leaves; floors written by the frozen search toward the four addresses from the
class where every leaf is transparent; at each floor 150 pairs of flipped points at distance 2 or more and 50 at distance 1 (two points
are at distance 1 when they share a line). Classes and the rule D as in MANY-POINTS-20261110-001B."""
import hashlib
import importlib.util
import json
import os
import random
import sys
import time
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(NA))
T0 = time.time()
OUT = {}
SEQ = "proofs/ADDRESS-SEQ-20261110-001A/ADDRESS-SEQ-20261110-001A-P001_writing_in_sequence"
MPB = "proofs/MANY-POINTS-20261110-001B/MANY-POINTS-20261110-001B-P001_two_points_at_once/check.py"
NC = "proofs/NEST-ATOMS-20261110-001C/NEST-ATOMS-20261110-001C-P001_a_two_level_address/check.py"
DEPS = [SEQ + "/seq_lib.py", MPB, NC, "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "research/COMPOSITE-FN-20261110-001/preregistration.md"]
TARGETS = [(0, 1, 2), (0, 2, 3), (0, 1, 3), (1, 2, 3)]


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


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    Q = load("seq_lib", DEPS[0])
    MB = load("mp_b", MPB)
    NCm = load("nest_c", NC)
    import spaces_lib as SP
    N = SP.N

    def role(K, Y, s, j):
        lines, outer, _ = Y.parts[j]
        return N.group_role(K, s, lines, outer)
    Q.LH.atom_role = role
    rng = random.Random(112)
    rows = []
    for leaf in ("Fano", "thin"):
        C3 = [SP.composite(3, SP.ATOMS[leaf], SP.lines_of(3)) for _ in range(2)]
        O = SP.outer_with(C3)
        K = O.K()
        Y = NCm.Shim(O, K)
        P = Q.C.Space(K, O.S)
        floor2 = abs(K.chi)
        levels = [Y.face_level(v) for v in range(K.V)]
        start = next(s for s in O.classes(K) if all(role(K, Y, s, j) == "transparent" for j in range(4)))
        model = K.sat(start)[1]
        cur = (sum(b << e for e, b in enumerate(start)), sum(int(model[p] > 0) << p for p in range(K.n)))
        adj = {p: set() for p in range(K.n)}
        for i in range(K.n):
            for a in K.pt[i]:
                adj[a] |= set(K.pt[i]) - {a}

        def dist(p, q):
            d, dq = {p: 0}, deque([p])
            while dq:
                u = dq.popleft()
                if u == q:
                    return d[u]
                for v in adj[u]:
                    if v not in d:
                        d[v] = d[u] + 1
                        dq.append(v)
        faces_of = {p: set(O.S.vert[K.points[p]]) for p in range(K.n)}
        allpairs = [(p, q) for p in range(K.n) for q in range(p + 1, K.n)]
        near = [pr for pr in allpairs if q_in(adj, pr)]
        far = [pr for pr in allpairs if not q_in(adj, pr)]
        for target in TARGETS:
            F, _ = Q.search_from(Y, K, P, cur, set(target), 4, levels)
            addr = Q.acting(K, Y, F[0], 4)
            sample = [("distance 2 or more", pr) for pr in rng.sample(far, 150)] + [("distance 1", pr) for pr in rng.sample(near, 50)]
            single = {}

            def D_of(p):
                if p not in single:
                    cfg = (F[0], F[1] ^ (1 << p))
                    single[p] = (MB.descend(P, *cfg, floor2), P.full(*cfg)[2])
                return single[p]
            for cat, (p, q) in sample:
                (Dp, stp, _), wp = D_of(p)
                (Dq, stq, _), wq = D_of(q)
                base = (F[0], F[1] ^ (1 << p) ^ (1 << q))
                wpq = P.full(*base)[2]
                I = ((wpq - floor2) - (wp - floor2) - (wq - floor2)) / 2
                row = {"leaf": leaf, "floor": target, "category": cat, "p": p, "q": q, "distance": dist(p, q),
                       "share a face": bool(faces_of[p] & faces_of[q]), "I": I}
                if stp or stq:
                    row["class"] = "single-stuck"
                elif I < 0:
                    row["class"] = "cancel"
                elif I > 0:
                    row["class"] = "bind"
                else:
                    shared = bool(set(Dp) & set(Dq))
                    ok, (end, (_, _, wend)) = MB.grid_ok(P, base, Dp, Dq)
                    endok = wend == floor2 and Q.acting(K, Y, end[0], 4) == addr
                    row["class"] = "independent" if (not shared and ok and endok) else "meet"
                rows.append(row)
            print(round(time.time() - T0, 1), leaf, target, dict(Counter((r["category"], r["class"]) for r in rows if r["leaf"] == leaf and r["floor"] == target)), flush=True)
    far_rows = [r for r in rows if r["category"] == "distance 2 or more"]
    near_rows = [r for r in rows if r["category"] == "distance 1"]
    summary = {"distance 2 or more": dict(Counter(r["class"] for r in far_rows)),
               "distance 2 or more, sharing a face": dict(Counter(r["class"] for r in far_rows if r["share a face"])),
               "distance 1": dict(Counter(r["class"] for r in near_rows))}
    check("1 two points on fresh composites, by distance (computed)", True, {"summary": summary, "pairs": len(rows),
          "distance 2 or more and not independent": [(r["leaf"], r["floor"], r["p"], r["q"], r["class"], r["I"]) for r in far_rows if r["class"] != "independent"][:20]})
    L1 = all(r["class"] == "independent" for r in far_rows)
    L2 = sum(r["class"] in ("cancel", "bind", "meet") for r in near_rows) >= 0.5 * len(near_rows)
    OUT["predictions"] = {"L1: every pair at distance 2 or more independent": L1, "L2: at least half of distance-1 pairs interact": L2,
                          "failure: a pair at distance 2 or more not independent": not L1}
    print(json.dumps(summary), json.dumps(OUT["predictions"]), flush=True)
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


def q_in(adj, pr):
    return pr[1] in adj[pr[0]]


if __name__ == "__main__":
    main()
