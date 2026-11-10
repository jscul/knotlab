#!/usr/bin/env python3
"""Checks for LEARN-RISE-20261110-001A: swapping the atoms' roles by learning at a rise.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
PYTHONHASHSEED=0. A configuration is a pair of bit masks (law over the 3n sides, state over the n points). Moves: a state flip, or a learning
step (a sign change on a side of a violated line or with an end at an even face). W is recomputed when a configuration is taken from the
queue; neighbours are scored by local differences. Breadth first, at most 300,000 configurations, W <= floor + 2 throughout."""
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
DEPS = ["proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py",
        "proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/LEARN-RISE-20261110-001/preregistration.md"]
CAP = 300000


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


class Space:
    def __init__(self, K, S):
        self.n, self.V = K.n, K.V
        self.pt = K.pt
        self.corners = [[(i, c) for (i, c) in K.corners_at[v]] for v in range(K.V)]
        self.ends = [[(S.vert[K.lines[i]][(k + 1) % 3], S.vert[K.lines[i]][(k + 2) % 3]) for k in range(3)] for i in range(K.n)]
        self.lines_of_point = [[(i, k) for i in range(K.n) for k in range(3) if K.pt[i][k] == p] for p in range(K.n)]
        self.faces_of_point = [sorted({v for (i, k) in self.lines_of_point[p] for v in self.ends[i][k]}) for p in range(K.n)]

    def lit(self, s, x, i, k):
        return ((x >> self.pt[i][k]) & 1) ^ ((s >> (3 * i + k)) & 1)

    def viol(self, s, x, i):
        return self.lit(s, x, i, 0) == self.lit(s, x, i, 1) == self.lit(s, x, i, 2)

    def agree(self, s, x, v):
        return sum(self.lit(s, x, i, (c + 1) % 3) == self.lit(s, x, i, (c + 2) % 3) for (i, c) in self.corners[v])

    @staticmethod
    def fw(a):
        return 2 * (a // 2) + (a % 2 == 0)

    def full(self, s, x):
        vi = [self.viol(s, x, i) for i in range(self.n)]
        ag = [self.agree(s, x, v) for v in range(self.V)]
        return vi, ag, 2 * sum(vi) + sum(self.fw(a) for a in ag)

    def neighbours(self, s, x, vi, ag, w):
        out = []
        for p in range(self.n):
            y, d = x ^ (1 << p), 0
            for i in {i for (i, _) in self.lines_of_point[p]}:
                d += 2 * (self.viol(s, y, i) - vi[i])
            for v in self.faces_of_point[p]:
                d += self.fw(self.agree(s, y, v)) - self.fw(ag[v])
            out.append(("flip", s, y, w + d))
        even = {v for v in range(self.V) if ag[v] % 2 == 0}
        sites = {3 * i + k for i in range(self.n) if vi[i] for k in range(3)}
        sites |= {3 * i + k for i in range(self.n) for k in range(3) if self.ends[i][k][0] in even or self.ends[i][k][1] in even}
        for e in sites:
            i, k = divmod(e, 3)
            t, d = s ^ (1 << e), 2 * (self.viol(s ^ (1 << e), x, i) - vi[i])
            for v in self.ends[i][k]:
                d += self.fw(self.agree(t, x, v)) - self.fw(ag[v])
            out.append(("learn", t, x, w + d))
        return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    LL = load("layers_lib", DEPS[0])
    LH = load("law_holds", DEPS[1])
    L = load("steer_lib", DEPS[2])
    ST, SL = LL.ST, LL.SL
    rows = []
    for kk, orbits in ((2, None), (3, 1)):
        S = SL.octahedral_sphere(kk)
        sph = L.Sphere(S, f"K_{kk}")
        reps, _ = ST.G.line_orbits(S)
        for l0 in reps[:orbits] if orbits else reps:
            dist = ST.G.line_distance(S, l0)
            at = {d: min(t for t, dd in dist.items() if dd == d) for d in (1, 2, 3)}
            x0 = sph.flat_state(sph.K.lines.index(l0))
            for d in (1, 2, 3):
                Y = LL.Layered(S, sph.s0, x0)
                Y.grow(l0)
                Y.grow(at[d])
                Y.learn(4)
                K = Y.K()
                P = Space(K, Y.S)
                levels = [Y.face_level(v) for v in range(K.V)]
                s_int = sum(b << e for e, b in enumerate(Y.s))
                x_int = sum(b << p for p, b in enumerate(Y.x))
                vi, ag, w = P.full(s_int, x_int)
                floor2 = abs(K.chi)
                assert w == floor2
                start = (s_int, x_int)
                prev, dq = {start: None}, deque([start])
                found = None
                while dq and len(prev) < CAP:
                    s, x = dq.popleft()
                    vi, ag, w = P.full(s, x)
                    if w == floor2 and any(ag[v] == 3 and levels[v] == "atom 0" for v in range(K.V)):
                        found = (s, x)
                        break
                    for kind, t, y, w2 in P.neighbours(s, x, vi, ag, w):
                        if w2 <= floor2 + 4 and (t, y) not in prev:
                            prev[(t, y)] = ((s, x), kind)
                            dq.append((t, y))
                row = {"sphere": f"K_{kk}", "l0": l0, "second atom at distance": d, "configurations": len(prev), "capped": found is None and len(prev) >= CAP,
                       "reached atom 0": found is not None}
                if found:
                    kinds, node = [], found
                    while prev[node] is not None:
                        node, kind = prev[node]
                        kinds.append(kind)
                    s_end = [(found[0] >> e) & 1 for e in range(3 * K.n)]
                    row.update({"moves": len(kinds), "learning steps": kinds.count("learn"), "flips": kinds.count("flip"),
                                "roles at the end": [LH.atom_role(K, Y, s_end, j) for j in (0, 1)],
                                "roles at the start": [LH.atom_role(K, Y, Y.s, j) for j in (0, 1)]})
                rows.append(row)
                print(round(time.time() - T0, 1), row, flush=True)
    r1 = all(r["reached atom 0"] and r["roles at the end"] == ["line", "transparent"] for r in rows)
    r2 = all(r.get("learning steps", 0) >= 1 and r.get("flips", 0) >= 1 and (r["sphere"] != "K_2" or r["moves"] <= 20) for r in rows if r["reached atom 0"])
    check("1 R1, R2 (computed): from each start, whether the unit reaches atom 0, the path, and the atoms' roles at the end", True,
          {"R1 as stated": r1, "R2 as stated": r2, "rows": rows})
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info"), sort_keys=True) != json.dumps(fresh[k]["info"], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
