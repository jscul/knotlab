"""Referee R1 for SPACE-ORDER-20261117-001: recompute every registered case with the referee's own propagation code.

  .venv/bin/python -B referee_recompute.py run [workers]   -> referee_recompute_runs.jsonl
  .venv/bin/python -B referee_recompute.py summary         -> referee_recompute.json

The instances (weave, role-preserving swaps, demands, planted state, held order) are rebuilt with the study's generator and
seeds, since they are what the frozen predictions were read on. Everything measured on them is the referee's: the atoms
(referee_core), k* (incremental closure), rounds and phases (least labels by generalized Dijkstra, not the study's
reachability phases), steps apart, the avalanche, the free share and, for the two-demand law on the weave, the post hoc reading
against the trigger. Each case is compared with the study's stored result.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import referee_core as C

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = ROOT / "experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases"
RUN = ROOT / "artifacts/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/run"
OUT = HERE / "referee_recompute_runs.jsonl"
SIZES = {24: 20, 48: 20, 96: 15, 192: 10, 384: 6}


def _job():
    spec = importlib.util.spec_from_file_location("so_job", E / "job.py")
    job = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(job)
    return job


def instance(job, law, pat, L, s):
    """The study's instance, rebuilt step by step as its build() and run() draw it."""
    W = job.W
    rng = np.random.default_rng(job.seed_of(f"{law}:{pat}:{L}:{s}"))
    K = W.weave(L)
    m = len(K)
    state = choice = None
    if law == "nae":
        state = W.zero_energy_sweeps(K, W.three_class_state(L), job.SWEEPS, rng)
        if pat == "R6":
            K, _ = W.role_swaps(K, W.nae_roles(K, state), 5 * m, rng)
    else:
        choice = rng.integers(0, 3, m)
        if pat == "R6":
            role = np.zeros((m, 3), dtype=np.int64)
            role[np.arange(m), choice] = 1
            K, _ = W.role_swaps(K, role, 5 * m, rng)
    order = rng.permutation(L * L)
    return K, choice, state, order


def free_share(knots, state):
    n = len(state)
    free = np.ones(n, bool)
    for t in knots.tolist():
        for p in range(3):
            v = t[p]
            u, w = [t[q] for q in range(3) if q != p]
            if state[u] == state[w] == 1 - state[v]:
                free[v] = False
    return float(free.mean())


def one(case):
    law, pat, L, s = case
    job = _job()
    K, choice, state, order = instance(job, law, pat, L, s)
    n = L * L
    atoms = C.nae_atoms(K, state) if law == "nae" else (C.two_demand(K, choice) if law == "two" else C.one_demand(K, choice))
    at = C.Atoms(n, atoms)
    nb = C.neighbours(K, n)
    k, _ = at.k_star(order)
    r1 = C.reading(at, nb, order[:k])
    r0 = C.reading(at, nb, order[:max(1, k - 1)])
    out = {"law": law, "pat": pat, "L": L, "s": s, "k_star": int(k),
           "at": {x: r1[x] for x in ("set", "R", "P", "D")}, "at_minus": {x: r0[x] for x in ("set", "R", "P", "D")},
           "avalanche": (r1["set"] - r0["set"]) / n, "P_ge_D": bool(r1["P"] >= r1["D"] and r0["P"] >= r0["D"]),
           "twin_same_role_counts": None}
    if law == "nae":
        out["free_share"] = free_share(K, state)
        out["planted_nae"] = bool(all(min(state[u] for u in t) != max(state[u] for u in t) for t in K.tolist()))
    if law == "two" and pat == "W":
        ph = r1["phase"]
        st = C.steps_from(nb, [order[k - 1]])
        sel = (ph < C.INF) & (ph > 0)
        out["posthoc"] = {"far_from_trigger": int(st[ph < C.INF].max()),
                          "corr": float(np.corrcoef(st[sel], ph[sel])[0, 1]),
                          "slope": float(np.polyfit(st[sel], ph[sel], 1)[0]),
                          "share_phase_eq_steps": float(np.mean(ph[sel] == st[sel])),
                          "share_phase_within_2": float(np.mean(np.abs(ph[sel] - st[sel]) <= 2)),
                          "eccentricity": int(st.max())}
    return out


def run(workers):
    done = set()
    if OUT.exists():
        for line in open(OUT):
            r = json.loads(line)
            done.add((r["law"], r["pat"], r["L"], r["s"]))
    cases = [(law, pat, L, s) for L in sorted(SIZES, reverse=True) for law in ("two", "one", "nae") for pat in ("W", "R6")
             for s in range(SIZES[L]) if (law, pat, L, s) not in done]
    with Pool(workers) as p, open(OUT, "a") as f:
        for r in p.imap_unordered(one, cases):
            f.write(json.dumps(r) + "\n")
            f.flush()


def stored():
    d = {}
    for line in open(RUN / "results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok" or r["case"].startswith("sweepcheck"):
            continue
        law, pat, L, s = r["case"].split("-")
        d[(law, pat, int(L[1:]), int(s[1:]))] = r["result"]
    return d


def summary():
    st = stored()
    rs = [json.loads(line) for line in open(OUT)]
    mism = []
    for r in rs:
        o = st[(r["law"], r["pat"], r["L"], r["s"])]
        same = (r["k_star"] == o["k_star"] and all(r["at"][x] == o["at_k_star"][x] for x in ("set", "R", "P", "D"))
                and all(r["at_minus"][x] == o["at_k_star_minus_1"][x] for x in ("set", "R", "P", "D")))
        if not same:
            mism.append({"case": [r["law"], r["pat"], r["L"], r["s"]], "referee": [r["k_star"], r["at"], r["at_minus"]],
                         "study": [o["k_star"], {x: o["at_k_star"][x] for x in ("set", "R", "P", "D")},
                                   {x: o["at_k_star_minus_1"][x] for x in ("set", "R", "P", "D")}]})
    T = {}
    for r in rs:
        T.setdefault((r["law"], r["pat"], r["L"]), []).append(r)
    med = lambda xs: float(np.median(xs))
    tab = {}
    for (law, pat, L), xs in sorted(T.items()):
        n = L * L
        row = {"samples": len(xs), "k_star_frac": med([x["k_star"] / n for x in xs]), "P": med([x["at"]["P"] for x in xs]),
               "R": med([x["at"]["R"] for x in xs]), "D": med([x["at"]["D"] for x in xs]),
               "P_over_D": med([x["at"]["P"] / max(1, x["at"]["D"]) for x in xs]),
               "P_over_R": med([x["at"]["P"] / max(1, x["at"]["R"]) for x in xs]), "avalanche": med([x["avalanche"] for x in xs])}
        if law == "nae":
            row["free_share"] = med([x["free_share"] for x in xs])
            row["planted_nae_all"] = all(x["planted_nae"] for x in xs)
        if law == "two" and pat == "W":
            row["posthoc"] = {k: [round(x["posthoc"][k], 3) for x in xs] for k in xs[0]["posthoc"]}
        tab[f"{law}-{pat}-L{L}"] = row
    g = lambda law, pat, L, k: tab[f"{law}-{pat}-L{L}"][k]
    sl = lambda a, b, ya, yb: float(np.log(yb / ya) / np.log(b / a))
    V = {"P_ge_D_all": all(x["P_ge_D"] for x in rs),
         "T1": {"P_slopes": [sl(96, 192, g("two", "W", 96, "P"), g("two", "W", 192, "P")),
                             sl(192, 384, g("two", "W", 192, "P"), g("two", "W", 384, "P"))],
                "R_slopes": [sl(96, 192, g("two", "W", 96, "R"), g("two", "W", 192, "R")),
                             sl(192, 384, g("two", "W", 192, "R"), g("two", "W", 384, "R"))],
                "P_over_R_384": g("two", "W", 384, "P_over_R"), "kfrac_48": g("two", "W", 48, "k_star_frac"),
                "kfrac_384": g("two", "W", 384, "k_star_frac")},
         "T2": {"kfrac": [g("two", "R6", L, "k_star_frac") for L in SIZES],
                "R_ratio": g("two", "R6", 384, "R") / g("two", "R6", 96, "R"),
                "P_24_384": [g("two", "R6", 24, "P"), g("two", "R6", 384, "P")]},
         "T3": g("two", "W", 384, "P") / g("two", "R6", 384, "P"),
         "T4": [g("two", "W", L, "P_over_D") for L in (96, 192, 384)],
         "O1": [g("one", "W", 384, "avalanche"), g("one", "R6", 384, "avalanche")],
         "O2": [g("one", "R6", 384, "P") - g("one", "R6", 24, "P"), sl(192, 384, g("one", "W", 192, "P"), g("one", "W", 384, "P"))],
         "O3": [g("one", "R6", L, "k_star_frac") for L in (96, 192, 384)],
         "N1": [g("nae", "W", 384, "avalanche"), g("nae", "R6", 384, "avalanche")],
         "N2": max(g("nae", pat, L, "P") for pat in ("W", "R6") for L in SIZES),
         "N3": [g("nae", "W", L, "free_share") for L in (48, 96, 192, 384)]}
    out = {"cases": len(rs), "mismatches": mism, "verdict_inputs": V, "table": tab}
    (HERE / "referee_recompute.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"cases": len(rs), "mismatches": len(mism), "V": V}, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    else:
        summary()
