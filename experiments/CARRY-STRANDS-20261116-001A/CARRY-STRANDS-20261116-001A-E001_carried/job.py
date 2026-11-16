"""Shared-runner job for CARRY-STRANDS-20261116-001A-E001.

Phases P, doubling rounds T and states visited of the w-carry law, keep and
spend-only, against the Strahler number sigma (the forcing law's phase count)
and propagation's rounds R, on small random atom patterns at the sample's own
jump, layered (widths 2, 3, 4, 16, 32) and unlayered random circuits,
ladders, pyramids and subdivided trees.
"""

import hashlib
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import strands as S  # noqa: E402
A = S.A
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("sequential_wall_job", os.path.join(S.SW, "job.py"))
SWjob = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SWjob)  # for incremental_k_star

CAP = 4_000_000
RAND = {64: 20, 128: 20, 256: 20, 512: 20, 1024: 20, 2048: 10, 4096: 10}


def seed_of(label):
    return int.from_bytes(hashlib.sha256(("CS:" + label).encode()).digest()[:8], "little")


def cases():
    for n, cnt in RAND.items():
        for s in range(cnt):
            yield f"rand-n{n}-s{s}", {"kind": "random", "n": n, "s": s}
    for width in (4, 16, 32):
        for d in (8, 16, 32, 64):
            for s in range(10):
                yield f"lay-w{width}-d{d}-s{s}", {"kind": "layered", "width": width, "d": d, "s": s}
    for width, depths in ((2, (4, 8, 16)), (3, (4, 6, 8))):
        for d in depths:
            for s in range(5):
                yield f"narrow-w{width}-d{d}-s{s}", {"kind": "narrow", "width": width, "d": d, "s": s}
    for g in (256, 1024):
        for s in range(10):
            yield f"unl-g{g}-s{s}", {"kind": "unlayered", "g": g, "s": s}
    for k in (8, 32, 128):
        yield f"ladder-{k}", {"kind": "ladder", "k": k}
    for h in (4, 5, 6, 7, 8, 9, 10, 12):
        yield f"pyramid-{h}", {"kind": "pyramid", "h": h}
    for d in (4, 6):
        for ell in (4, 16):
            yield f"subtree-d{d}-l{ell}", {"kind": "subtree", "d": d, "ell": ell}


def subdivided_tree(d, ell):
    """Complete binary tree of atoms of height d over held leaves, each edge
    replaced by a chain of ell rules (atoms with one held helper g)."""
    g = 0
    n = 1
    level = list(range(n, n + 2 ** d))
    n += 2 ** d
    held = [g] + level
    atoms = []

    def chain(u):
        nonlocal n
        for _ in range(ell):
            atoms.append((u, g, n))
            u = n
            n += 1
        return u
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            x, y = chain(level[i]), chain(level[i + 1])
            atoms.append((x, y, n))
            nxt.append(n)
            n += 1
        level = nxt
    return A.Pattern(n, atoms, held), level[0]


def measure(p, ws, focus=None, laws=("spend", "keep")):
    f, _, R = A.native_rounds(p)
    sig = A.rank(p)
    fin = sig < A.INF
    out = {"n": p.n, "m": p.m, "R": int(R), "sigma_max": int(sig[fin].max()) if fin.any() else 0,
           "forced": int(f.sum()), "laws": {}}
    if focus is not None:
        out["sigma_focus"] = int(sig[focus]) if sig[focus] < A.INF else -1
    newly = fin & ~p.held
    w1 = None
    for w in ws:
        for law in laws:
            if w == 1 and law == "keep":
                continue
            key = f"w{w}{'k' if law == 'keep' else ''}"
            try:
                r = S.carried_phases(p, w, keep=(law == "keep"), max_states=CAP)
            except S.StateCap as e:
                out["laws"][key] = {"cap": int(e.args[0])}
                continue
            assert np.array_equal(r["forced"], f)
            rec = {"P": r["P"], "T": r["T"], "L": r["L"], "states": r["states"]}
            if focus is not None:
                rec["phase_focus"] = int(r["phase"][focus])
            if w == 1:
                w1 = r
                sizes = [int((r["phase"] == t).sum()) for t in range(1, r["P"] + 1)]
                rec["phase_sizes"] = sizes
            if law == "keep" and newly.any():
                gain = r["phase"][newly] < np.ceil(sig[newly] / w)
                rec["keep_gain_fraction"] = float(gain.mean())
                if w1 is not None and w1["P"] >= 4:
                    sizes = [int((w1["phase"] == t).sum()) for t in range(1, w1["P"] + 1)]
                    narrow = 1 + int(np.argmin(sizes[:-2]))
                    before = newly & (w1["phase"] <= narrow)
                    after = newly & (w1["phase"] > narrow)
                    g_all = r["phase"] < np.ceil(sig / w)
                    rec["keep_gain_before"] = float(g_all[before].mean()) if before.any() else None
                    rec["keep_gain_after"] = float(g_all[after].mean()) if after.any() else None
            out["laws"][key] = rec
    return out


def run(case_id, pl):
    kind = pl["kind"]
    if kind == "random":
        n = pl["n"]
        rng = np.random.default_rng(seed_of(f"rand:{n}:{pl['s']}"))
        trip = A.random_pattern(n, 3.0, rng)
        order = rng.permutation(n)
        k_star, _ = SWjob.incremental_k_star(n, trip, order)
        res = measure(A.Pattern(n, trip, order[:k_star]), (1, 2, 3) if n <= 256 else (1, 2))
        res["k_star"] = int(k_star)
        return res
    if kind in ("layered", "narrow"):
        rng = np.random.default_rng(seed_of(f"{kind}:{pl['width']}:{pl['d']}:{pl['s']}"))
        inputs, layers = A.alternating_circuit(pl["d"], pl["width"], rng, p_one=0.5, mixed=True)
        p, ids = A.circuit_to_atoms(inputs, layers)
        if kind == "narrow":
            res = measure(p, (2 * pl["width"],), laws=("keep",))
        else:
            res = measure(p, (1, 2, 3) if p.n <= 140 else (1, 2))
        res.update({"width": pl["width"], "d": pl["d"]})
        return res
    if kind == "unlayered":
        rng = np.random.default_rng(seed_of(f"unl:{pl['g']}:{pl['s']}"))
        inputs, gates = A.unlayered_circuit(32, pl["g"], rng)
        p, node, vals = A.unlayered_to_atoms(inputs, gates)
        return measure(p, (1, 2))
    if kind == "ladder":
        p, top = A.ladder(pl["k"])
        return measure(p, (1, 2), focus=top)
    if kind == "pyramid":
        p, top = A.pyramid(pl["h"])
        return measure(p, (1, 2, 3, 4) if pl["h"] <= 9 else (1, 2, 3), focus=top)
    p, top = subdivided_tree(pl["d"], pl["ell"])
    return measure(p, (1, 2, 3) if pl["d"] <= 4 else (1, 2), focus=top)
