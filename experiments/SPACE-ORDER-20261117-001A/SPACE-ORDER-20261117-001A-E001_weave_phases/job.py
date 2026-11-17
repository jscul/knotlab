"""Shared-runner job for SPACE-ORDER-20261117-001A-E001.

Three laws on the weave W(L) and on its role-preserving shuffled twin R6:
  one   each knot demands one member (uniform per knot);
  two   each knot demands two members (one uniform free member per knot);
  nae   not-all-equal from a planted state (30 zero-energy sweeps from the
        three-class state); the twin swaps only members of equal value and
        equal role (odd member or one of the equal pair).
Held = first k of a uniform order (with planted values for nae); k* = least k
setting half the distinctions.  At k* and k* - 1: rounds R, phases P, the
largest steps apart D from the held set to a set distinction, the avalanche
(set fraction at k* minus at k* - 1); Strahler number = phase checked at
L <= 48.  At fixed held fractions 0.05, 0.1, 0.2: R and P.
"""

import hashlib
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import weaves as W  # noqa: E402
A = W.A
_spec = importlib.util.spec_from_file_location("sequential_wall_job", os.path.join(W.SW, "job.py"))
SWjob = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SWjob)

SIZES = {24: 20, 48: 20, 96: 15, 192: 10, 384: 6}
SWEEPS = 30
FRACS = (0.05, 0.1, 0.2)


def seed_of(label):
    return int.from_bytes(hashlib.sha256(("SO:" + label).encode()).digest()[:8], "little")


def cases():
    for law in ("two", "one", "nae"):
        for pat in ("W", "R6"):
            for L, cnt in SIZES.items():
                for s in range(cnt):
                    yield f"{law}-{pat}-L{L}-s{s}", {"law": law, "pat": pat, "L": L, "s": s}
    for s in range(5):
        yield f"sweepcheck-L48-s{s}", {"law": "sweepcheck", "L": 48, "s": s}


def build(law, pat, L, s):
    rng = np.random.default_rng(seed_of(f"{law}:{pat}:{L}:{s}"))
    K = W.weave(L)
    m = len(K)
    if law == "nae":
        state = W.zero_energy_sweeps(K, W.three_class_state(L), SWEEPS, rng)
        if pat == "R6":
            K, _ = W.role_swaps(K, W.nae_roles(K, state), 5 * m, rng)
        return K, None, state, rng
    choice = rng.integers(0, 3, m)
    role = np.zeros((m, 3), dtype=np.int64)
    role[np.arange(m), choice] = 1
    if pat == "R6":
        K, _ = W.role_swaps(K, role, 5 * m, rng)
    trip = W.one_demand_atoms(K, choice) if law == "one" else W.two_demand_atoms(K, choice)
    return K, trip, None, rng


def measure_atoms(K, trip, n, held, check):
    p = A.Pattern(n, trip, held)
    f, _, R = A.native_rounds(p)
    _, ph, P = A.untangling_phases(p)
    out = {"k": int(len(held)), "set": int(f.sum()), "R": int(R), "P": int(P)}
    dist = W.steps_from(K, n, held)
    out["D"] = int(dist[f].max()) if f.any() else 0
    out["P_ge_D"] = bool(P >= out["D"] or out["D"] == 0)
    if check:
        r = A.rank(p)
        fin = r < A.INF
        out["strahler_equals_phase"] = bool(np.array_equal(fin, f) and np.array_equal(r[fin], ph[fin]))
    return out


def measure_nae(K, n, held, state, check):
    val, R = W.nae_rounds(K, n, held, state)
    _, ph, P = W.nae_phases(K, n, held, state)
    setm = val >= 0
    out = {"k": int(len(held)), "set": int(setm.sum()), "R": int(R), "P": int(P)}
    dist = W.steps_from(K, n, held)
    out["D"] = int(dist[setm].max()) if setm.any() else 0
    out["P_ge_D"] = bool(P >= out["D"] or out["D"] == 0)
    if check:
        rk = W.nae_rank(K, n, held, state)
        out["strahler_equals_phase"] = bool(np.array_equal(rk[setm], ph[setm]))
    return out


def run(case_id, pl):
    if pl["law"] == "sweepcheck":
        L = pl["L"]
        rng = np.random.default_rng(seed_of(f"sweep:{L}:{pl['s']}"))
        K = W.weave(L)
        s30 = W.zero_energy_sweeps(K, W.three_class_state(L), SWEEPS, rng)
        s300 = W.zero_energy_sweeps(K, s30, 270, rng)
        return {"free30": W.free_spin_fraction(K, s30), "free300": W.free_spin_fraction(K, s300)}
    law, pat, L, s = pl["law"], pl["pat"], pl["L"], pl["s"]
    n = L * L
    K, trip, state, rng = build(law, pat, L, s)
    order = rng.permutation(n)
    check = L <= 48
    res = {"law": law, "pat": pat, "L": L, "n": n}
    if law == "nae":
        res["free_fraction"] = W.free_spin_fraction(K, state)
        k_star, _ = W.nae_incremental_k_star(K, n, order, state)
        meas = lambda held, chk=False: measure_nae(K, n, held, state, chk)
    else:
        k_star, _ = SWjob.incremental_k_star(n, trip, order)
        meas = lambda held, chk=False: measure_atoms(K, trip, n, held, chk)
    res["k_star"] = int(k_star)
    res["at_k_star"] = meas(order[:k_star], check)
    res["at_k_star_minus_1"] = meas(order[:max(1, k_star - 1)], check)
    res["avalanche"] = (res["at_k_star"]["set"] - res["at_k_star_minus_1"]["set"]) / n
    res["fracs"] = {str(a): meas(order[:max(1, int(round(a * n)))]) for a in FRACS}
    return res
