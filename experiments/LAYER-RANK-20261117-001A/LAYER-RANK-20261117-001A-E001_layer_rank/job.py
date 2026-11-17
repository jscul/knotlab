"""Shared-runner job for LAYER-RANK-20261117-001A-E001.

mf          the infinite-width recursion Q_{L+1}(r) = Q_L(r) - q_L(r)^2 / 2 to
            L = 10^5, with fixed-rank limits, the tie product and the profile;
val         exact simulation at w = 2^17 (d <= 4096) and 2^20 (d <= 1024)
            against the recursion;
w1024       w = 1024 to d = 4096, 50 samples: largest rank, p, all-false share;
collapse    w = 64 ... 1024 to d = 100 w, 40 samples each: rank against L on
            samples whose true fraction fixed at 1.
"""

import hashlib
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layer_rank as LR  # noqa: E402

MF_CPS = [10 ** k for k in (1, 2, 3)] + [3000, 10000, 30000, 100000]


def seed_of(label):
    return int.from_bytes(hashlib.sha256(("LR:" + label).encode()).digest()[:8], "little")


def cases():
    yield "mf", {"kind": "mf"}
    for e, dmax in ((17, 4096), (20, 1024)):
        for s in range(3):
            yield f"val-w{e}-s{s}", {"kind": "val", "e": e, "d": dmax, "s": s}
    for s in range(50):
        yield f"w1024-s{s}", {"kind": "w1024", "s": s}
    for w in (64, 128, 256, 512, 1024):
        for s in range(40):
            yield f"collapse-w{w}-s{s}", {"kind": "collapse", "w": w, "s": s}


def meanfield_full(L_max):
    a = np.zeros(4)
    a[0] = 0.5
    rows = {}
    for L in range(1, L_max + 1):
        if a[-1] > 1e-300 or a[-2] > 1e-300:
            a = np.concatenate([a, np.zeros(len(a))])
        p = a.sum()
        Acum = np.concatenate([[0.0], np.cumsum(a)[:-1]])
        AND = 2 * a * Acum
        AND[1:] += a[:-1] ** 2
        b = a.copy(); b[1] += b[0]; b[0] = 0.0
        tail = b.sum() - np.cumsum(b)
        OR = b ** 2 + 2 * b * tail + 2 * b * (1 - p)
        new = 0.5 * AND + 0.5 * OR
        if L >= 2:  # the cumulative form, checked against the full recursion
            Q, Qn = np.cumsum(a), np.cumsum(new)
            assert np.allclose(Qn, Q - 0.5 * a ** 2, atol=1e-14), "cumulative identity"
        a = new
        if L in MF_CPS:
            pt = a.sum(); f = a / pt; r = np.arange(len(f))
            mu = float((f * r).sum()); sd = float(np.sqrt((f * (r - mu) ** 2).sum()))
            F = np.cumsum(f)
            tie = float((f ** 2).sum())
            rr = max(1, int(round(math.sqrt(L) / 2)))
            rows[L] = {"p": float(pt), "mean": mu, "sd": sd, "tie": tie, "mean_times_tie": mu * tie,
                       "L_F1": float(L * F[1]), "L_F2": float(L * F[2]),
                       "profile_at_half_front": float(f[rr] * L / (2 * rr)),
                       "max_rank_support": int(np.nonzero(f > 1e-12)[0].max())}
    return rows


def run(case_id, pl):
    kind = pl["kind"]
    if kind == "mf":
        return {"rows": meanfield_full(100000)}
    if kind == "val":
        w = 2 ** pl["e"]
        cps = [c for c in (8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096) if c <= pl["d"]]
        sim = LR.simulate(w, pl["d"], np.random.default_rng(seed_of(case_id)), cps)
        mf = LR.meanfield(pl["d"], cps)
        return {"w": w, "sim": sim, "mf": {L: {"mean": mf[L]["mean"], "sd": mf[L]["sd"]} for L in cps}}
    if kind == "w1024":
        cps = [64, 256, 1024, 2048, 4096]
        return {"sim": LR.simulate(1024, 4096, np.random.default_rng(seed_of(case_id)), cps)}
    w = pl["w"]
    d = 100 * w
    cps = [int(w * f) for f in (1, 2, 5, 10, 20, 40, 60, 80, 100)]
    return {"w": w, "sim": LR.simulate(w, d, np.random.default_rng(seed_of(case_id)), cps)}
