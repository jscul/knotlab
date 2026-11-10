#!/usr/bin/env python3
"""Checks for RISE-ESCAPE-20261110-001A: excursions out of an atom.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
PYTHONHASHSEED=0. Check 1 confirms E1 on every floor state; check 2 is the excursion search (computed). With the law fixed, a state is an
integer bit mask; W is recomputed from scratch when a state is taken from the queue and by local differences for its neighbours."""
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
DEPS = ["proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/RISE-ESCAPE-20261110-001/preregistration.md"]
CAP = 200000


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
    if not ok and not os.environ.get("NOEXIT"):
        sys.exit(1)


class Fast:
    """W for a fixed law as a function of the state's bit mask"""

    def __init__(self, K, s):
        self.n, self.V = K.n, K.V
        self.lines = [[(K.pt[i][k], s[3 * i + k]) for k in range(3)] for i in range(K.n)]
        self.corners = [[(K.pt[i][(c + 1) % 3], s[3 * i + (c + 1) % 3], K.pt[i][(c + 2) % 3], s[3 * i + (c + 2) % 3]) for (i, c) in K.corners_at[v]]
                        for v in range(K.V)]
        self.faces_of_point = [sorted({v for v in range(K.V) for (pa, _, pb, _) in self.corners[v] if p in (pa, pb)}) for p in range(K.n)]
        self.lines_of_point = [sorted({i for i in range(K.n) for (q, _) in self.lines[i] if q == p}) for p in range(K.n)]

    def agree(self, x, v):
        return sum(((x >> pa) & 1) ^ sa == ((x >> pb) & 1) ^ sb for (pa, sa, pb, sb) in self.corners[v])

    def viol(self, x, i):
        a, b, c = [((x >> p) & 1) ^ t for p, t in self.lines[i]]
        return a == b == c

    def w2(self, x):
        ag = [self.agree(x, v) for v in range(self.V)]
        return 2 * sum(self.viol(x, i) for i in range(self.n)) + sum(2 * (a // 2) + (a % 2 == 0) for a in ag)

    def w2_flip(self, x, w, p, ag=None, vi=None):
        y = x ^ (1 << p)
        for i in self.lines_of_point[p]:
            w += 2 * (self.viol(y, i) - (vi[i] if vi is not None else self.viol(x, i)))
        for v in self.faces_of_point[p]:
            a, b = (ag[v] if ag is not None else self.agree(x, v)), self.agree(y, v)
            w += 2 * (b // 2) + (b % 2 == 0) - 2 * (a // 2) - (a % 2 == 0)
        return y, w

    def unit_faces(self, x):
        return [v for v in range(self.V) if self.agree(x, v) == 3]


def search(F, x0, floor2, k, targets, levels):
    """BFS over (state, steps above the floor) with W <= floor + 2 and at most k consecutive steps above. targets: {name: set of levels};
    stops when every target has been met at a floor state. Returns ({name: found}, states seen, levels of the unit over floor states seen)"""
    start = (x0, 0)
    seen, dq = {start}, deque([(x0, 0, floor2)])
    hosts, found = Counter(), {name: False for name in targets}
    while dq and len(seen) < CAP:
        x, j, w = dq.popleft()
        ag = [F.agree(x, v) for v in range(F.V)]
        vi = [F.viol(x, i) for i in range(F.n)]
        if w == floor2:
            for v in range(F.V):
                if ag[v] == 3:
                    lv = levels[v]
                    hosts[lv] += 1
                    for name, tg in targets.items():
                        found[name] |= lv in tg
            if all(found.values()):
                break
        for p in range(F.n):
            y, w2 = F.w2_flip(x, w, p, ag, vi)
            if w2 > floor2 + 4:
                continue
            j2 = 0 if w2 == floor2 else j + 1
            if k is not None and j2 > k:
                continue
            key = (y, j2 if k is not None else 0)
            if key not in seen:
                seen.add(key)
                dq.append((y, key[1], w2))
    return found, len(seen), dict(hosts)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    LL = load("layers_lib", DEPS[0])
    L = load("steer_lib", DEPS[1])
    ST, SL = LL.ST, LL.SL
    rows, e1 = [], []
    for kk in (2, 3):
        S = SL.octahedral_sphere(kk)
        sph = L.Sphere(S, f"K_{kk}")
        reps, _ = ST.G.line_orbits(S)
        for l0 in reps:
            dist = ST.G.line_distance(S, l0)
            at = {d: min(t for t, dd in dist.items() if dd == d) for d in (1, 2, 3)}
            x = sph.flat_state(sph.K.lines.index(l0))
            for d in (1, 2, 3):
                Y = LL.Layered(S, sph.s0, x)
                Y.grow(l0)
                Y.grow(at[d])
                Y.learn(4)
                K = Y.K()
                floor2 = abs(K.chi)
                assert ST.weight2(K, Y.s, Y.x) == floor2
                e1.append(not ST.steps_at(Y.S, K, Y.s, Y.x))
                F = Fast(K, Y.s)
                levels = [Y.face_level(v) for v in range(K.V)]
                x0 = sum(b << p for p, b in enumerate(Y.x))
                home = {levels[v] for v in F.unit_faces(x0)}
                home_atom = next(lv for lv in home if lv.startswith("atom")) if any(lv.startswith("atom") for lv in home) else None
                other = {lv for lv in set(levels) if lv.startswith("atom") and lv != home_atom}
                row = {"sphere": f"K_{kk}", "l0": l0, "second atom at distance": d, "unit starts at": sorted(home)}
                targets = {"other atom": other, "upper level": {"upper"}}
                found, size, hosts = search(F, x0, floor2, None, targets, levels)
                row["unbounded"] = {"found": found, "states": size, "capped": size >= CAP, "unit at": hosts}
                for name in targets:
                    least = None
                    if found[name]:
                        for k in (2, 4, 6):
                            f2, s2, _ = search(F, x0, floor2, k, {name: targets[name]}, levels)
                            if f2[name]:
                                least = k
                                break
                    row[name] = {"reached (unbounded)": found[name], "least k of 2, 4, 6": least}
                rows.append(row)
                print(round(time.time() - T0, 1), row, flush=True)
    check("1 E1: every genus-2 floor state offers no learning step (no violated line, no even face)", all(e1), {"floor states": len(e1)})
    least = Counter()
    for r in rows:
        for name in ("other atom", "upper level"):
            v = r[name]
            least[(name, v["least k of 2, 4, 6"] if v["least k of 2, 4, 6"] else ("above 6" if v["reached (unbounded)"] else
                                                                                   "not reached" + (" (capped)" if r["unbounded"]["capped"] else "")))] += 1
    check("2 E2, E3 (computed): the least excursion length k at which the unit reaches the other atom or the upper level, by floor state", True,
          {"(target, least k)": {str(k): v for k, v in sorted(least.items(), key=str)}, "rows": rows})
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [kk for kk in OUT if kk != "seconds" and json.dumps(old.get(kk, {}).get("info"), sort_keys=True)
                != json.dumps(fresh[kk]["info"], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
