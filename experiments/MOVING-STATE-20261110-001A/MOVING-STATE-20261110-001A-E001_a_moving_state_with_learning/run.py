"""MOVING-STATE-20261110-001A-E001: a moving state with learning (exploratory; see contract.json).

A challenge of A26. On the atom spaces of ATOM-LAYERS-20261110-001A, each round the W-lowering learner (sight 3) takes a step if one lowers the
dissonance weight W; otherwise the state flips one point, chosen uniformly among the flips that do not raise W. F searches, with the law
fixed, every state reachable from a genus-2 floor state by flips that keep W at the floor, and records where the unit then sits.
Writes artifacts/MOVING-STATE-20261110-001A/MOVING-STATE-20261110-001A-E001_a_moving_state_with_learning/run/result.json."""
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
OUT = ROOT / "artifacts/MOVING-STATE-20261110-001A/MOVING-STATE-20261110-001A-E001_a_moving_state_with_learning/run"
T0 = time.time()


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def levels_of(defs):
    return sorted({lv for (_, lv), c in defs.items() if c})


def run_M(Y, rng, rounds=150, r=3):
    ST = LL.ST
    s, x = list(Y.s), list(Y.x)
    K = Y.K()
    visited, flips, steps = set(), 0, 0
    for _ in range(rounds):
        w = ST.weight2(K, s, x)
        visited.update(levels_of(Y.defects_of(s, x)))
        if w == 0:
            break
        e = ST.search(Y.S, K, s, x, r)
        if e is not None:
            s[e] ^= 1
            steps += 1
            continue
        ok = []
        for p in range(K.n):
            x[p] ^= 1
            if ST.weight2(K, s, x) <= w:
                ok.append(p)
            x[p] ^= 1
        if not ok:
            break
        x[rng.choice(ok)] ^= 1
        flips += 1
    visited.update(levels_of(Y.defects_of(s, x)))
    return ST.weight2(K, s, x) / 2, steps, flips, sorted(visited), levels_of(Y.defects_of(s, x))


def floor_component(Y, cap=20000):
    ST = LL.ST
    K = Y.K()
    w0 = ST.weight2(K, Y.s, Y.x)
    start = tuple(Y.x)
    seen, dq = {start}, deque([start])
    hosts = Counter()
    while dq and len(seen) < cap:
        x = list(dq.popleft())
        viol, agree = ST.tally(K, Y.s, x)
        for v in range(K.V):
            if agree[v] == 3:
                hosts[Y.face_level(v)] += 1
        for p in range(K.n):
            x[p] ^= 1
            t = tuple(x)
            if t not in seen and ST.weight2(K, Y.s, x) == w0:
                seen.add(t)
                dq.append(t)
            x[p] ^= 1
    return len(seen), dict(hosts), len(seen) >= cap


def main():
    global LL
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    LL = load("layers_lib", "proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py")
    L = load("steer_lib", "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
    ST, SL = LL.ST, LL.SL

    def defects_of(self, s, x):
        old_s, old_x = self.s, self.x
        self.s, self.x = s, x
        try:
            return self.defects()
        finally:
            self.s, self.x = old_s, old_x
    LL.Layered.defects_of = defects_of
    rng = random.Random(71)
    rows = []
    for k in (2, 3):
        S = SL.octahedral_sphere(k)
        sph = L.Sphere(S, f"K_{k}")
        reps, _ = ST.G.line_orbits(S)
        for l0 in reps:
            dist = ST.G.line_distance(S, l0)
            at = {d: min(t for t, dd in dist.items() if dd == d) for d in (1, 2, 3)}
            x = sph.flat_state(sph.K.lines.index(l0))
            for name, lam in [("away (d = 2)", [at[2]]), ("away (d = 2 and 3)", [at[2], at[3]]),
                              ("at l0 and d = 1", [l0, at[1]]), ("at l0 and d = 2", [l0, at[2]]), ("at l0 and d = 3", [l0, at[3]])]:
                Y = LL.Layered(S, sph.s0, x)
                for l in lam:
                    Y.grow(l)
                if name.startswith("at l0"):
                    Y.learn(4)
                K = Y.K()
                row = {"sphere": f"K_{k}", "l0": l0, "atoms": name, "genus": len(lam), "floor": abs(K.chi) / 2,
                       "W start": ST.weight2(K, Y.s, Y.x) / 2, "start levels": levels_of(Y.defects())}
                res = [run_M(Y, rng) for _ in range(10)]
                row["M"] = {"final W": Counter(r[0] for r in res), "mean learning steps": sum(r[1] for r in res) / 10,
                            "mean flips": sum(r[2] for r in res) / 10,
                            "levels visited (union)": sorted({lv for r in res for lv in r[3]}),
                            "end levels": Counter(", ".join(r[4]) for r in res)}
                if name.startswith("at l0"):
                    size, hosts, capped = floor_component(Y)
                    row["F"] = {"states": size, "capped": capped, "unit at": hosts}
                rows.append(row)
                print(round(time.time() - T0, 1), row["sphere"], l0, name, dict(row["M"]["final W"]), row["M"]["levels visited (union)"],
                      row.get("F"), flush=True)
    g1 = [r for r in rows if r["atoms"] == "away (d = 2)"]
    g2a = [r for r in rows if r["atoms"] == "away (d = 2 and 3)"]
    fl = [r for r in rows if r["atoms"].startswith("at l0")]
    s1 = all(r["M"]["final W"] == Counter({0.0: 10}) for r in g1)
    s2 = all(r["M"]["final W"] == Counter({1.0: 10}) for r in g2a)
    both_atoms = [all(any(h == "atom %d" % j for h in r["F"]["unit at"]) for j in (0, 1)) for r in fl]
    freed = any(0.0 in r["M"]["final W"] for r in g1) or any(1.0 in r["M"]["final W"] for r in g2a)
    moved = any(any(h != r_end for h in r["F"]["unit at"]) for r in fl for r_end in [None]) and any(
        len(r["F"]["unit at"]) > 1 for r in fl)
    RES = {"rows": rows, "decisions": {
        "S1: every genus-1 away run resolves": s1,
        "S2: every genus-2 away run reaches the floor": s2,
        "S3: every floor component holds the unit inside both atoms": all(both_atoms),
        "floor components holding the unit inside both atoms": sum(both_atoms), "of": len(fl),
        "floor components reaching an upper face": sum(1 for r in fl if "upper" in r["F"]["unit at"]),
        "A26: a stuck run freed by the moving state": freed,
        "A26: a frozen unit reaches more than one place": moved,
    }}
    RES["seconds"] = round(time.time() - T0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")
    print(json.dumps(RES["decisions"], indent=1))


if __name__ == "__main__":
    main()
