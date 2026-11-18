"""Shared-runner job for DOUBLE-MEET-20261118-001B-E001: weave patches."""
import itertools
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import weavelib as W  # noqa: E402

M, N = W.M, W.N
SHARDS = 12


def cases():
    for k in range(1, 12):
        for s in range(SHARDS if k >= 9 else 1):
            yield f"disc-k{k}-s{s}", {"kind": "disc", "k": k, "shard": s, "of": SHARDS if k >= 9 else 1}
    for k in range(1, 8):
        yield f"criterion-k{k}", {"kind": "criterion", "k": k}
    for i in range(40):
        yield f"random-{i}", {"kind": "random", "seed": 4000 + i}
    for a in range(2, 6):
        for b in range(a, 9):
            if a * b <= 16:
                yield f"par-{a}x{b}", {"kind": "par", "a": a, "b": b}


def discs_of_size(k):
    level = {W.normal({("u", 0, 0)}), W.normal({("d", 0, 0)})}
    for _ in range(k - 1):
        nxt = set()
        for T in level:
            for t in T:
                for nb in W.nbrs(t):
                    if nb not in T:
                        nxt.add(W.normal(set(T) | {nb}))
        level = nxt
    return sorted((T for T in level if W.is_disc(T)), key=lambda T: sorted(T))


def par_sites(x, kx, z):
    u, v = [w for w in W.verts(kx) if w != x]
    p, q = W.facing(x, kx, z)
    d1, d2 = (u[0] - x[0], u[1] - x[1]), (v[0] - x[0], v[1] - x[1])
    return {(x[0] + a * d1[0] + b * d2[0], x[1] + a * d1[1] + b * d2[1]) for a in range(p + 1) for b in range(q + 1)}


def judge(T):
    V, ix, D, S, lone, N_states = W.read(T)
    n = len(V)
    r = {"patches": 1, "pairs": 0, "bonded_off_steps": 0, "unbonded": 0, "unbonded_not_facing": 0, "facing_pairs": 0,
         "facing_bonded": 0, "same_class_unbonded": 0, "not_facing_unbonded": 0, "metric": 0, "metric_iff_no_unbonded": 0,
         "examples": [], "no_state": 0, "dd_fail": 0, "below_steps": 0, "within_par_bonded": 0, "within_par_pairs": 0,
         "bonded_facing_without_outside": 0}
    DD = W.height_distances(T)
    for a, b in itertools.combinations(V, 2):
        r["dd_fail"] += DD[a][b] + DD[b][a] != 3 * S[ix[a]][ix[b]]
    if N_states == 0:
        r["no_state"] = 1
        return r
    unb = set()
    for a, b in itertools.combinations(range(n), 2):
        r["pairs"] += 1
        if D[a][b] == math.inf:
            unb.add((V[a], V[b]))
        elif D[a][b] != S[a][b] + 1:
            r["bonded_off_steps"] += 1
            r["below_steps"] += D[a][b] < S[a][b] + 1
            if len(r["examples"]) < 2:
                r["examples"].append({"kind": "off", "patch": sorted(T), "pair": [V[a], V[b]], "b": D[a][b], "steps": S[a][b]})
    r["unbonded"] = len(unb)
    for x, z in unb:
        ok = (x in lone and z in lone and lone[x][0] != lone[z][0] and W.facing(x, lone[x], z) is not None
              and W.facing(z, lone[z], x) is not None)
        if not ok:
            r["unbonded_not_facing"] += 1
            if len(r["examples"]) < 4:
                r["examples"].append({"kind": "unbonded not facing", "patch": sorted(T), "pair": [x, z]})
    for x, z in itertools.combinations(sorted(lone), 2):
        unbonded = (x, z) in unb or (z, x) in unb
        if lone[x][0] == lone[z][0]:
            r["same_class_unbonded"] += unbonded
        elif W.facing(x, lone[x], z) is None or W.facing(z, lone[z], x) is None:
            r["not_facing_unbonded"] += unbonded
        else:
            r["facing_pairs"] += 1
            r["facing_bonded"] += not unbonded
            ps = par_sites(x, lone[x], z)
            outside = any(not all(w in ps for w in W.verts(t)) for t in T)
            if not outside:
                r["within_par_pairs"] += 1
                r["within_par_bonded"] += not unbonded
            if not unbonded and not outside:
                r["bonded_facing_without_outside"] += 1
    metric = not M.violations(D, n)
    r["metric"] = int(metric)
    r["metric_iff_no_unbonded"] = int(metric == (len(unb) == 0))
    return r


def merge_into(acc, r):
    for k, v in r.items():
        if k == "examples":
            acc.setdefault("examples", [])
            acc["examples"] = (acc["examples"] + v)[:6]
        else:
            acc[k] = acc.get(k, 0) + v
    return acc


def run(case_id, p):
    acc = {}
    if p["kind"] == "disc":
        Ts = discs_of_size(p["k"])
        for i, T in enumerate(Ts):
            if i % p["of"] == p["shard"]:
                merge_into(acc, judge(T))
        acc["k"] = p["k"]
        return acc
    if p["kind"] == "criterion":
        out = {"discs": 0, "sets": 0, "mismatch": 0}
        for T in discs_of_size(p["k"]):
            V = sorted({v for t in T for v in W.verts(t)})
            ix = {v: k for k, v in enumerate(V)}
            n = len(V)
            st = M.states(n, [(N.NAE3, tuple(sorted(ix[v] for v in W.verts(t)))) for t in sorted(T)])
            free = M.free_table(n, st)
            tight = W.tight_sets(V, W.height_distances(T))
            out["discs"] += 1
            for mask in range(1 << n):
                out["sets"] += 1
                constrained = any((m & mask) == m for m in tight)
                out["mismatch"] += constrained != (not free[mask])
        return out
    if p["kind"] == "random":
        rng = random.Random(p["seed"])
        done = 0
        while done < 12:
            T = {("u", 0, 0)}
            size = rng.randint(10, 26)
            while len(T) < size:
                t = rng.choice(sorted(T))
                nb = rng.choice(W.nbrs(t))
                if nb not in T and W.is_disc(T | {nb}):
                    T.add(nb)
                if rng.random() < 0.01:
                    break
            V = {v for t in T for v in W.verts(t)}
            if len(V) > 16 or len(V) < 10:
                continue
            merge_into(acc, judge(frozenset(T)))
            done += 1
        return acc
    if p["kind"] == "par":
        T = W.parallelogram(p["a"], p["b"])
        V, ix, D, S, lone, _ = W.read(T)
        unb = sorted((V[a], V[b]) for a, b in itertools.combinations(range(len(V)), 2) if D[a][b] == math.inf)
        corners = sorted(lone)
        return {"a": p["a"], "b": p["b"], "unbonded": [list(map(list, u)) for u in unb], "lone": [list(c) for c in corners],
                "off_steps": sum(1 for a, b in itertools.combinations(range(len(V)), 2) if D[a][b] != math.inf and D[a][b] != S[a][b] + 1)}
    raise ValueError(p["kind"])
