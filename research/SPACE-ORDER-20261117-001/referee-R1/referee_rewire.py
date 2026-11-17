"""Referee R1 for SPACE-ORDER-20261117-001: A96's challenge, run. Does the phase count follow steps apart or short cycles?

  .venv/bin/python -B referee_rewire.py run [workers]   -> referee_rewire_runs.jsonl
  .venv/bin/python -B referee_rewire.py summary         -> referee_rewire.json

The two-demand law on the weave after a fraction eps of the twin's 5m role-preserving swaps (eps * m swaps; eps = 0 is the
weave, eps = 5 the study's twin). A few swaps keep almost all short cycles (the share of co-knotted pairs that lie in two knots,
1 on the weave) while adding long-range shortcuts that collapse steps apart. All code, instances and seeds are the referee's own.

Per case: the share of pairs in two knots; the largest steps apart (eccentricity from the trigger, and from a random
distinction); k*/n; at k*: rounds R*, phases P*, the largest steps apart D* from the held set, and the trigger's eccentricity
over the set distinctions.
"""
from __future__ import annotations

import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import referee_core as C

HERE = Path(__file__).resolve().parent
OUT = HERE / "referee_rewire_runs.jsonl"
EPS = (0.0, 0.002, 0.01, 0.05, 0.25, 5.0)
SIZES = {96: 4, 192: 4, 384: 3}


def seed(*parts):
    return int.from_bytes(hashlib.sha256(("referee-rewire:" + ":".join(map(str, parts))).encode()).digest()[:8], "little")


def one(case):
    L, eps, s = case
    rng = np.random.default_rng(seed(L, eps, s))
    K = C.weave(L)
    m, n = len(K), L * L
    free = rng.integers(0, 3, m)
    role = np.zeros((m, 3), dtype=np.int64)
    role[np.arange(m), free] = 1
    if eps > 0:
        K = C.role_swaps(K, role, int(round(eps * m)), rng)
    # invariants of a role-preserving swap: every distinction keeps its count of knots in each role
    cnt0 = np.zeros((n, 2), int)
    np.add.at(cnt0, (C.weave(L).ravel(), role.ravel()), 1)
    cnt1 = np.zeros((n, 2), int)
    np.add.at(cnt1, (K.ravel(), role.ravel()), 1)
    pair2, npairs = C.pair_multiplicity(K)
    at = C.Atoms(n, C.two_demand(K, free))
    nb = C.neighbours(K, n)
    order = rng.permutation(n)
    k, _ = at.k_star(order)
    r = C.reading(at, nb, order[:k])
    ph = r["phase"]
    setm = ph < C.INF
    st = C.steps_from(nb, [order[k - 1]])
    rnd = C.steps_from(nb, [int(rng.integers(0, n))])
    sel = setm & (ph > 0)
    corr = float(np.corrcoef(st[sel], ph[sel])[0, 1]) if sel.sum() > 2 and st[sel].std() > 0 else None
    return {"L": L, "eps": eps, "s": s, "role_counts_kept": bool(np.array_equal(cnt0, cnt1)), "pair_in_two": pair2,
            "pairs": npairs, "ecc_trigger": int(st.max()), "ecc_random": int(rnd.max()), "k_star_frac": k / n,
            "set_frac": r["set"] / n, "R": r["R"], "P": r["P"], "D": r["D"], "trigger_ecc_over_set": int(st[setm].max()),
            "corr_phase_steps_trigger": corr}


def run(workers):
    done = set()
    if OUT.exists():
        for line in open(OUT):
            r = json.loads(line)
            done.add((r["L"], r["eps"], r["s"]))
    cases = [(L, e, s) for L in sorted(SIZES, reverse=True) for e in EPS for s in range(SIZES[L]) if (L, e, s) not in done]
    with Pool(workers) as p, open(OUT, "a") as f:
        for r in p.imap_unordered(one, cases):
            f.write(json.dumps(r) + "\n")
            f.flush()


def summary():
    rs = [json.loads(line) for line in open(OUT)]
    tab = {}
    for L in SIZES:
        for e in EPS:
            xs = [r for r in rs if r["L"] == L and r["eps"] == e]
            if not xs:
                continue
            med = lambda k: float(np.median([x[k] for x in xs]))
            tab[f"L{L} eps{e}"] = {"samples": len(xs), "roles_kept": all(x["role_counts_kept"] for x in xs),
                                   "pair_in_two": round(med("pair_in_two"), 4), "ecc": med("ecc_random"),
                                   "k_star_frac": round(med("k_star_frac"), 5), "P": med("P"), "R": med("R"), "D": med("D"),
                                   "trigger_ecc": med("trigger_ecc_over_set"),
                                   "P_over_trigger_ecc": round(float(np.median([x["P"] / max(1, x["trigger_ecc_over_set"])
                                                                                for x in xs])), 3),
                                   "corr": [None if x["corr_phase_steps_trigger"] is None else
                                            round(x["corr_phase_steps_trigger"], 3) for x in xs]}
    (HERE / "referee_rewire.json").write_text(json.dumps(tab, indent=1))
    for k, v in tab.items():
        print(k, v)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    else:
        summary()
