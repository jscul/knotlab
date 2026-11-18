"""Shared-runner job for RIM-EXCESS-20261118-001B-E001: bond polygons and the excess of bond distance over steps apart + 1."""
import importlib.util
import itertools
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import polylib as P  # noqa: E402

W = P.W
M, N, nx = W.M, W.N, W.nx
_spec = importlib.util.spec_from_file_location("dm_job", ROOT / "experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches/job.py")
DM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DM)  # DOUBLE-MEET's discs_of_size, unchanged
SH = 12
START = frozenset([("d", 0, 1), ("d", 0, 2), ("d", 1, 0), ("d", 1, 1), ("d", 2, 0), ("d", 2, 1), ("u", 1, 1), ("u", 1, 2), ("u", 2, 1),
                   ("u", 2, 2), ("u", 3, 0), ("u", 3, 1)])  # the DOUBLE-MEET referee's twelve-knot disc


def cases():
    for k in range(3, 10):
        yield f"lemmaP-k{k}", {"kind": "lemmaP", "k": k, "shard": 0, "of": 1}
    for k in range(2, 10):
        sh = SH if k >= 8 else 1
        for s in range(sh):
            yield f"algo-k{k}-s{s}", {"kind": "algo", "k": k, "shard": s, "of": sh}
    for k in (11, 12):
        for s in range(SH):
            yield f"excess-k{k}-s{s}", {"kind": "excess", "k": k, "shard": s, "of": SH}
    for i in range(40):
        yield f"random-{i}", {"kind": "random", "seed": 6000 + i}
    for i in range(8):
        yield f"climb-{i}", {"kind": "climb", "seed": 6500 + i}


def lone_info(T, V):
    deg = {v: sum(v in W.verts(t) for t in T) for v in V}
    return {v: next(t for t in T if v in W.verts(t)) for v in V if deg[v] == 1}


def facing_both(lone, x, z):
    return (x in lone and z in lone and lone[x][0] != lone[z][0] and W.facing(x, lone[x], z) is not None
            and W.facing(z, lone[z], x) is not None)


def facing_pairs(T):
    V = sorted({v for t in T for v in W.verts(t)})
    lone = lone_info(T, V)
    return [(x, z) for x, z in itertools.combinations(sorted(lone), 2) if facing_both(lone, x, z)]


def shard(Ts, p):
    return [T for i, T in enumerate(Ts) if i % p["of"] == p["shard"]]


def run(case_id, p):
    kind = p["kind"]
    if kind == "lemmaP":
        out = {"discs": 0, "bonds": 0, "fail": 0}
        for T in DM.discs_of_size(p["k"]):
            V = sorted({v for t in T for v in W.verts(t)})
            ix = {v: i for i, v in enumerate(V)}
            n = len(V)
            st = M.states(n, [(N.NAE3, tuple(sorted(ix[v] for v in W.verts(t)))) for t in sorted(T)])
            DD = W.height_distances(T)
            out["discs"] += 1
            for mask in M.bonds(n, M.free_table(n, st)):
                pts = [V[i] for i in range(n) if mask >> i & 1]
                out["bonds"] += 1
                out["fail"] += P.min_cycle_weight(pts, DD) != 3 * (len(pts) - 2)
        return out
    if kind == "algo":
        out = {"discs": 0, "pairs": 0, "compared": 0, "mismatch": 0, "timeouts": 0, "examples": []}
        for T in shard(DM.discs_of_size(p["k"]), p):
            V, ix, D, S, lone, _ = W.read(T)
            out["discs"] += 1
            for a, b in itertools.combinations(range(len(V)), 2):
                out["pairs"] += 1
                true = None if D[a][b] == math.inf else D[a][b]
                got, s, to = P.pair_b_polygons(T, V[a], V[b], emax=6, time_limit=30)
                if to:
                    out["timeouts"] += 1
                    continue
                if true is not None and true - s - 1 > 6:
                    continue
                out["compared"] += 1
                if got != true:
                    out["mismatch"] += 1
                    if len(out["examples"]) < 3:
                        out["examples"].append({"patch": sorted(T), "pair": [V[a], V[b]], "true": true, "got": got})
        return out
    if kind == "excess":
        out = {"discs": 0, "pairs": 0, "excess_pairs": 0, "excess_not_facing": 0, "by_excess": {}, "max_excess": 0, "examples": [],
               "unbonded_not_facing": 0}
        for T in shard(DM.discs_of_size(p["k"]), p):
            V, ix, D, S, lone, _ = W.read(T)
            out["discs"] += 1
            for a, b in itertools.combinations(range(len(V)), 2):
                out["pairs"] += 1
                x, z = V[a], V[b]
                if D[a][b] == math.inf:
                    out["unbonded_not_facing"] += not facing_both(lone, x, z)
                    continue
                e = D[a][b] - S[a][b] - 1
                if e >= 1:
                    out["excess_pairs"] += 1
                    out["by_excess"][str(e)] = out["by_excess"].get(str(e), 0) + 1
                    out["max_excess"] = max(out["max_excess"], e)
                    if not facing_both(lone, x, z):
                        out["excess_not_facing"] += 1
                        if len(out["examples"]) < 3:
                            out["examples"].append({"patch": sorted(T), "pair": [x, z], "excess": e})
        return out
    if kind == "random":
        rng = random.Random(p["seed"])
        out = {"patches": 0, "facing_pairs": 0, "hist": {}, "max_excess": 0, "example": None}
        t0 = time.time()
        while out["patches"] < 4 and time.time() - t0 < 900:
            T = {("u", 0, 0)}
            size = rng.randint(20, 40)
            while len(T) < size:
                t = rng.choice(sorted(T))
                nb = rng.choice(W.nbrs(t))
                if nb not in T and W.is_disc(T | {nb}):
                    T.add(nb)
            out["patches"] += 1
            for x, z in facing_pairs(T):
                out["facing_pairs"] += 1
                b, s, to = P.pair_b_polygons(frozenset(T), x, z, emax=6, time_limit=20)
                key = "timeout" if to else ("none to 6" if b is None else str(b - s - 1))
                out["hist"][key] = out["hist"].get(key, 0) + 1
                if b is not None and b - s - 1 > out["max_excess"]:
                    out["max_excess"] = b - s - 1
                    out["example"] = {"patch": sorted(T), "pair": [x, z], "steps": s, "b": b}
        return out
    if kind == "climb":
        rng = random.Random(p["seed"])
        def score(T):
            best = -1
            for x, z in facing_pairs(T):
                b, s, to = P.pair_b_polygons(T, x, z, emax=6, time_limit=8)
                if b is not None:
                    best = max(best, b - s - 1)
            return best
        cur = START if p["seed"] % 2 == 0 else W.parallelogram(3, 4)
        cs = score(cur)
        best = (cs, sorted(cur))
        t0 = time.time()
        steps = 0
        while time.time() - t0 < 600:
            T = set(cur)
            for _ in range(rng.randint(1, 3)):
                if rng.random() < 0.6 and len(T) < 26:
                    t = rng.choice(sorted(T))
                    nb = rng.choice(W.nbrs(t))
                    if nb not in T and W.is_disc(T | {nb}):
                        T.add(nb)
                else:
                    t = rng.choice(sorted(T))
                    if len(T) > 3 and W.is_disc(T - {t}):
                        T.discard(t)
            T = frozenset(T)
            sc = score(T)
            steps += 1
            if sc >= cs or rng.random() < 0.1:
                cur, cs = T, sc
                if sc > best[0]:
                    best = (sc, sorted(T))
        return {"steps": steps, "best_excess": best[0], "best_patch": best[1]}
    raise ValueError(kind)
