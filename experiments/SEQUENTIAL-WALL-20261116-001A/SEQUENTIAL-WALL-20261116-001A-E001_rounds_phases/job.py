"""Shared-runner job for SEQUENTIAL-WALL-20261116-001A-E001.

Random atom patterns: n distinctions, m = 3n atoms with three distinct
uniform distinctions, held set = the first k distinctions of a uniform random
order.  The closure grows with k; k* is the least k whose closure holds at
least half the distinctions (the sample's own jump, found exactly by one
incremental closure).  At k*, k* - 1, k* + offsets (fractions of n), the
mean-field jump alpha_mf = 0.098251 and fixed held fractions, we record native
rounds R, phases P, the closure, the size each phase adds and (at k* and
k* - 1) the rank by relaxation and the largest log2 fringe.

Structured families: chain, ladder, pyramid, balanced tree.  Circuits:
layered (each gate AND or OR with chance 1/2, fan-in two from the layer below)
and unlayered (each gate reads two random earlier nodes), as atom patterns,
with R, P, the dual law's phase count and the largest rank at the output.
"""

import hashlib
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import atoms as A  # noqa: E402

C = 3.0
ALPHA_MF = 0.098251  # mean-field tangency at c = 3: x* = (1 - sqrt(1/3))/2, alpha* = 1 - (1 - x*) exp(3 x*^2)
SIZES = {10: 40, 12: 40, 14: 30, 16: 20, 18: 12, 20: 8}  # log2 n: samples
OFFSETS = [-0.03, -0.01, -0.003, -0.001, 0.001, 0.003, 0.01, 0.03]
ALPHAS = [0.03, 0.06, 0.2, 0.4]


def seed_of(label):
    return int.from_bytes(hashlib.sha256(("SW:" + label).encode()).digest()[:8], "little")


def cases():
    for e, s_count in SIZES.items():
        for s in range(s_count):
            yield f"rand-n{e}-s{s}", {"kind": "random", "e": e, "s": s}
    for L in (64, 256, 1024, 4096):
        yield f"chain-{L}", {"kind": "chain", "L": L}
    for k in (8, 32, 128, 512):
        yield f"ladder-{k}", {"kind": "ladder", "k": k}
    for h in (8, 32, 128, 256):
        yield f"pyramid-{h}", {"kind": "pyramid", "h": h}
    for d in (4, 8, 12, 16):
        yield f"tree-{d}", {"kind": "tree", "d": d}
    for w in (64, 256, 1024):
        for d in (8, 16, 32, 64, 128, 256):
            for s in range(10):
                yield f"circ-w{w}-d{d}-s{s}", {"kind": "circuit", "w": w, "d": d, "s": s}
    for g in (1024, 4096, 16384, 65536):
        for s in range(10):
            yield f"unl-g{g}-s{s}", {"kind": "unlayered", "g": g, "s": s}


def incremental_k_star(n, trip, order):
    """Least k with |closure(order[:k])| >= n/2, by one incremental closure."""
    a, b, c = trip[:, 0], trip[:, 1], trip[:, 2]
    m = len(a)
    dem = np.concatenate([a, b])
    atom_of = np.concatenate([np.arange(m), np.arange(m)])
    srt = np.argsort(dem, kind="stable")
    ptr = np.searchsorted(dem[srt], np.arange(n + 1))
    need_l = [2] * m
    ptr_l = ptr.tolist()
    lists_l = atom_of[srt].tolist()
    c_l = c.tolist()
    forced_l = [False] * n
    size = 0
    for k, v0 in enumerate(order.tolist(), start=1):
        stack = [v0]
        while stack:
            v = stack.pop()
            if forced_l[v]:
                continue
            forced_l[v] = True
            size += 1
            for j in lists_l[ptr_l[v]:ptr_l[v + 1]]:
                need_l[j] -= 1
                if need_l[j] == 0 and not forced_l[c_l[j]]:
                    stack.append(c_l[j])
        if 2 * size >= n:
            return k, size
    return n, size


def measure(n, trip, held_idx, deep=False):
    p = A.Pattern(n, trip, held_idx)
    f, when, R = A.native_rounds(p)
    _, phase, P = A.untangling_phases(p)
    out = {"k": int(len(held_idx)), "closure": int(f.sum()), "R": int(R), "P": int(P),
           "phase_sizes": [int((phase == t).sum()) for t in range(1, P + 1)]}
    if deep:
        r = A.rank(p)
        fin = r < A.INF
        out["max_rank"] = int(r[fin].max())
        out["rank_equals_phase"] = bool(np.array_equal(r[fin], phase[fin]))
        lf = A.log2_fringe(p)
        out["max_log2_fringe"] = float(lf[fin].max())
    return out


def run_random(e, s):
    n = 2 ** e
    rng = np.random.default_rng(seed_of(f"rand:{e}:{s}"))
    trip = A.random_pattern(n, C, rng)
    order = rng.permutation(n)
    k_star, _ = incremental_k_star(n, trip, order)
    res = {"n": n, "e": e, "s": s, "k_star": int(k_star), "alpha_star": k_star / n}
    res["at_k_star"] = measure(n, trip, order[:k_star], deep=True)
    res["at_k_star_minus_1"] = measure(n, trip, order[:k_star - 1], deep=True)
    res["offsets"] = {}
    for off in OFFSETS:
        k = int(round(k_star + off * n))
        if 1 <= k <= n and k != k_star:
            res["offsets"][str(off)] = measure(n, trip, order[:k])
    res["alpha_mf"] = measure(n, trip, order[:max(1, int(round(ALPHA_MF * n)))])
    res["alphas"] = {}
    for al in ALPHAS:
        k = max(1, int(round(al * n)))
        res["alphas"][str(al)] = measure(n, trip, order[:k])
    return res


def run_structured(payload):
    kind = payload["kind"]
    if kind == "chain":
        p, top = A.chain(payload["L"])
    elif kind == "ladder":
        p, top = A.ladder(payload["k"])
    elif kind == "pyramid":
        p, top = A.pyramid(payload["h"])
    else:
        p, top = A.balanced_and_tree(payload["d"])
    f, _, R = A.native_rounds(p)
    _, phase, P = A.untangling_phases(p)
    _, _, Pd = A.dual_phases(p)
    r = A.rank(p)
    lf = A.log2_fringe(p)
    return {"n": p.n, "m": p.m, "R": int(R), "P": int(P), "P_dual": int(Pd), "rank_top": int(r[top]),
            "log2_fringe_top": float(lf[top]), "top_forced": bool(f[top])}


def circuit_measures(p, out_ids, ok):
    f, _, R = A.native_rounds(p)
    _, phase, P = A.untangling_phases(p)
    unf, _, Pd = A.dual_phases(p)
    r = A.rank(p)
    ro = r[out_ids]
    ro = ro[ro < A.INF]
    return {"R": int(R), "P": int(P), "P_dual": int(Pd), "two_sided": int(min(P, Pd)),
            "evaluation_matches": bool(ok), "forced_or_unforced_everywhere": bool(np.all(f | unf)),
            "out_true": int(len(ro)), "out_max_rank": int(ro.max()) if len(ro) else -1,
            "out_mean_rank": float(ro.mean()) if len(ro) else -1.0}


def run_circuit(w, d, s):
    rng = np.random.default_rng(seed_of(f"circ:{w}:{d}:{s}"))
    inputs, layers = A.alternating_circuit(d, w, rng, p_one=0.5, mixed=True)
    vals = A.evaluate_circuit(inputs, layers)
    p, ids = A.circuit_to_atoms(inputs, layers)
    f, _, _ = A.native_rounds(p)
    ok = all(np.array_equal(f[g], v) for g, v in zip(ids, vals))
    res = circuit_measures(p, ids[-1], ok)
    res.update({"w": w, "d": d, "s": s})
    return res


def run_unlayered(g, s):
    rng = np.random.default_rng(seed_of(f"unl:{g}:{s}"))
    inputs, gates = A.unlayered_circuit(256, g, rng)
    p, node, vals = A.unlayered_to_atoms(inputs, gates)
    f, _, _ = A.native_rounds(p)
    ok = bool(np.array_equal(f[node], vals))
    res = circuit_measures(p, node[256:], ok)
    res.update({"g": g, "s": s})
    return res


def run(case_id, payload):
    kind = payload["kind"]
    if kind == "random":
        return run_random(payload["e"], payload["s"])
    if kind == "circuit":
        return run_circuit(payload["w"], payload["d"], payload["s"])
    if kind == "unlayered":
        return run_unlayered(payload["g"], payload["s"])
    return run_structured(payload)
