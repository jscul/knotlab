"""Referee R1 for JOIN-GROWTH-20261118-001 (own growth code; the study's case list, job.cases(), and its computed knot sizes in
results.json are read as data, nothing of its growth, recurrence or scoring code is run).

  ../../../.venv/bin/python -B referee_join.py <part> [args] > referee_join_<part>.json      (from this directory)

Parts:
  validate      the lean engine (lean.py) against the referee's full engine (FIRST-KNOT-R1) on six starts of four families.
  regrow        the starts of families A, B (except the unread chord), E and the 48 P7 joins of D, regrown by the lean engine to
                80 rounds or MAXJ junctions (run with 60,000 for time and memory): per-round counts against the study's on every
                common round, and the predicted annihilator re-scored by the frozen rule on the referee's own counts (streamed to
                referee_join_regrow.jsonl).
  n9s3          the P1 start the pre-registration lists but job.py does not run (a lone adjunct with s = 3 on the ring of nine).
  tworing NAME  one two-ring join grown past the study's horizon (junction cap from the environment, default 2,500,000).
  posthoc       the post hoc section: the bare chains of three to six and the fork regrown to the study's cap and their stated
                annihilators re-scored on the referee's counts; one of the three cases the refined law left unsettled (two rounds
                tested) grown one round further, to round 20.
  fit NAME      the forecasts and fits for the two-ring counts: lambda and C with alpha fixed at -3/2 on the study's rounds, the
                forecast of every later round, and alpha left free on all rounds.
"""
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT / "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins"
RES = ROOT / "artifacts/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/results.json"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
import lean as L  # noqa: E402
import referee_first as RFK  # noqa: E402
import referee_touch as RT  # noqa: E402


def study_cases():
    sys.path.insert(0, str(EXP))
    import job  # the study's case list, read as data
    return dict(job.cases())


def stars_for(payload, sizes):
    n = payload["n"]
    M = [[0] * n for _ in range(n)]
    for a, b in payload["edges"]:
        M[a][b] += 1
        M[b][a] += 1
    return RT.stars(sizes, M)


def grow_lean(stars, rounds=80, maxj=250000, tmax=None):
    G = L.Lean(stars)
    out = "alive"
    t0 = time.time()
    for _ in range(rounds):
        r = G.step()
        if r != "ok":
            out = r
            break
        if len(G.bits) > maxj:
            out = "cap"
            break
        if tmax and time.time() - t0 > tmax:
            out = "time"
            break
    return G, out


def frozen_score(p, c):
    d = len(p) - 1
    bad = [t for t in range(d, len(c)) if sum(p[k] * c[t - d + k] for k in range(d + 1)) != 0]
    t0 = (max(bad) - d + 1) if bad else 0
    tested = len(c) - (t0 + d)
    if t0 <= 12 and tested >= 3:
        return "holds", t0, tested
    if t0 <= 12:
        return "unsettled", t0, tested
    return "fails", t0, tested


def part_validate():
    cs = study_cases()
    res = json.load(open(RES))["cases"]
    out = {}
    for cid, maxj in (("A1-n7-s1", 30000), ("A5-n5-a1-b2", 30000), ("D-D-at-r1-a2-b1", 30000), ("D-P1-none-a1-b1", 30000),
                      ("C-5-5-K", 20000), ("E-D-s2", 20000)):
        st = stars_for(cs[cid], res[cid]["sizes"])
        G1, o1 = grow_lean(st, maxj=maxj)
        G2 = RFK.Start(st)
        o2 = "alive"
        for _ in range(80):
            r = G2.step(RFK.fewest, None, None)
            if r != "ok":
                o2 = r
                break
            if len(G2.bits) > maxj:
                o2 = "cap"
                break
        c1, c2 = G1.counts(), G2.counts()
        m = min(len(c1), len(c2))
        out[cid] = {"lean rounds": len(c1) - 1, "full rounds": len(c2) - 1, "counts equal on common rounds": c1[:m] == c2[:m],
                    "lean zero-demand junctions": G1.zero_demand, "outcomes": [o1, o2]}
    return out


def _regrow(args):
    cid, payload, row = args
    st = stars_for(payload, row["sizes"])
    G, out = grow_lean(st, maxj=int(os.environ.get("MAXJ", "250000")))
    c = G.counts()
    s = row["counts"]
    m = min(len(c), len(s))
    r = {"case": cid, "outcome": out, "rounds": len(c) - 1, "study rounds": len(s) - 1, "counts equal on common rounds": c[:m] == s[:m],
         "zero demand": G.zero_demand}
    if payload.get("annihilator"):
        r["frozen rule on the referee's counts"] = frozen_score(payload["annihilator"], c)
    return r


def part_regrow():
    """Streams one JSON line per start to referee_join_regrow.jsonl as it finishes, then summarizes."""
    cs = study_cases()
    res = json.load(open(RES))["cases"]
    keep = lambda cid: cid.startswith(("A", "B", "E", "D-D-", "D-K-")) and cid != "B-chord-02"
    jobs = [(cid, pay, res[cid]) for cid, pay in cs.items() if "counts" in res.get(cid, {}) and keep(cid)]
    rows = []
    with open(HERE / "referee_join_regrow.jsonl", "w") as fh, Pool(int(os.environ.get("WORKERS", "12"))) as pool:
        for r in pool.imap_unordered(_regrow, jobs):
            rows.append(r)
            fh.write(json.dumps(r) + "\n")
            fh.flush()
    holds = [r for r in rows if "frozen rule on the referee's counts" in r]
    return {"starts regrown": len(rows), "counts equal to the study's on every common round": sum(r["counts equal on common rounds"] for r in rows),
            "starts with a junction of demand zero (lean engine not exact there)": sum(r["zero demand"] > 0 for r in rows),
            "predicted annihilators": len(holds),
            "frozen rule on the referee's counts": {v: sum(1 for r in holds if r["frozen rule on the referee's counts"][0] == v) for v in ("holds", "unsettled", "fails")},
            "rows": sorted(rows, key=lambda r: r["case"])}


def part_n9s3():
    cs = study_cases()
    res = json.load(open(RES))["cases"]
    pay = dict(cs["A1-n9-s2"])
    pay["surplus"] = {k: v + 1 for k, v in pay["surplus"].items()}
    sizes = list(res["A1-n9-s2"]["sizes"])
    sizes[9] += 1                          # the adjunct (knot 9): one more listed surplus distinction
    st = stars_for(pay, sizes)
    G, out = grow_lean(st)
    c = G.counts()
    # x^(n + s + 1) = x^(s + 1) + (1 + x)^s with n = 9, s = 3: x^13 - x^4 - (1 + 3x + 3x^2 + x^3)
    p = [-1, -3, -3, -1, -1] + [0] * 8 + [1]
    lo, hi = 1.0, 3.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid ** 13 - mid ** 4 - (1 + mid) ** 3 < 0:
            lo = mid
        else:
            hi = mid
    return {"sizes": sizes, "outcome": out, "rounds": len(c) - 1, "junctions": len(G.bits), "counts (first 20)": c[:20],
            "predicted annihilator x^13 - x^4 - (1 + x)^3 (coefficients, constant first)": p,
            "frozen rule": frozen_score(p, c), "predicted rate": round(lo, 6), "last ratio": round(c[-1] / c[-2], 6),
            "zero demand": G.zero_demand}


def part_tworing(name):
    cs = study_cases()
    res = json.load(open(RES))["cases"]
    cap = int(os.environ.get("MAXJ", "2500000"))
    st = stars_for(cs[name], res[name]["sizes"])
    G = L.Lean(st)
    log = []
    t0 = time.time()
    for _ in range(40):
        r = G.step()
        log.append({"round": G.rounds, "junctions": len(G.bits), "seconds": round(time.time() - t0)})
        print(json.dumps(log[-1]), file=sys.stderr, flush=True)
        if r != "ok" or len(G.bits) > cap:
            break
    c = G.counts()
    s = res[name]["counts"]
    return {"case": name, "rounds": G.rounds, "junctions": len(G.bits), "counts": c, "study counts": s,
            "equal on the study's rounds": c[:len(s)] == s[:len(c)], "zero demand": G.zero_demand, "log": log}


def fit_fixed(c, lo, hi, alpha=-1.5):
    """log c(t) = log C + t log lam + alpha log t, least squares on rounds lo..hi (alpha fixed)."""
    xs = list(range(lo, hi + 1))
    ys = [math.log(c[t]) - alpha * math.log(t) for t in xs]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    return math.exp(b), math.exp(a)


def fit_free(c, lo, hi):
    """log c(t) = a + b t + alpha log t, least squares on rounds lo..hi."""
    import numpy as np
    t = np.arange(lo, hi + 1, dtype=float)
    A = np.stack([np.ones_like(t), t, np.log(t)], axis=1)
    y = np.log(np.array([c[int(x)] for x in t], dtype=float))
    sol, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    return math.exp(sol[1]), sol[2], float(np.max(np.abs(A @ sol - y)))


def part_fit(name):
    d = json.load(open(HERE / f"referee_join_tworing_{name}.json"))
    c = d["counts"]
    T = len(c) - 1
    S = len(d["study counts"]) - 1
    out = {"case": name, "rounds grown": T, "study's last round": S}
    lam, C = fit_fixed(c, 8, S)
    out["alpha = -3/2 fitted on rounds 8.." + str(S)] = {"lambda": round(lam, 5)}
    out["forecasts of the later rounds (alpha = -3/2)"] = {t: {"forecast": round(C * lam ** t * t ** -1.5), "grown": c[t],
                                                             "relative error": round((C * lam ** t * t ** -1.5 - c[t]) / c[t], 5)}
                                                         for t in range(S + 1, T + 1)}
    for a in (-1.0, -2.0, 0.0):
        lam2, C2 = fit_fixed(c, 8, S, alpha=a)
        out[f"same forecast with alpha = {a}"] = {t: round((C2 * lam2 ** t * t ** a - c[t]) / c[t], 5) for t in range(S + 1, T + 1)}
    lamf, alf, res = fit_free(c, 8, T)
    out["alpha free, rounds 8.." + str(T)] = {"lambda": round(lamf, 5), "alpha": round(alf, 4), "max log residual": round(res, 6)}
    lamf2, alf2, res2 = fit_free(c, 10, T)
    out["alpha free, rounds 10.." + str(T)] = {"lambda": round(lamf2, 5), "alpha": round(alf2, 4), "max log residual": round(res2, 6)}
    out["successive ratios"] = [round(c[t] / c[t - 1], 5) for t in range(2, T + 1)]
    # under c ~ C lam^t t^alpha, the ratio r(t) = lam (1 - 1/t)^(-alpha): solve for alpha from three consecutive ratios
    est = []
    for t in range(6, T):
        r1, r2 = c[t] / c[t - 1], c[t + 1] / c[t]
        # r2 / r1 = ((t / (t + 1)) / ((t - 1) / t)) ^ alpha
        q = math.log((t / (t + 1)) / ((t - 1) / t))
        est.append([t, round(-math.log(r2 / r1) / q, 3)])
    out["local alpha from three consecutive rounds t - 1, t, t + 1"] = est
    late = {}
    for lo in (12, 13, 14):
        for a in (-1.0, -1.25, -1.5, -1.75):
            lam3, C3 = fit_fixed(c, lo, S, alpha=a)
            late[f"rounds {lo}..{S}, alpha {a}"] = {t: round((C3 * lam3 ** t * t ** a - c[t]) / c[t], 5) for t in range(S + 1, T + 1)}
    out["forecast errors from late windows (relative)"] = late
    return out


# ---------------------------------------------------------------- the post hoc section


PH = EXP / "posthoc"


def ring_edges(n):
    return [(i, (i + 1) % n) for i in range(n)]


def chain_payload(n, depth):
    edges = ring_edges(n) + [(0, n)] + [(n + i, n + i + 1) for i in range(depth - 1)]
    return {"n": n + depth, "edges": edges}


def mulp(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def chain_annihilator(n, depth):
    """The stated post hoc annihilators (constant term first): bare chains of 3 (as the pair), 4 and 5, and 6."""
    if depth == 3:      # (x - 1)(x^(n+1) - x^n - x - 1)
        q = [-1, -1] + [0] * (n - 2) + [-1, 1]
    elif depth in (4, 5):   # (x - 1)(x^(n+2) - x^(n+1) - x^2 - x - 1)
        q = [-1, -1, -1] + [0] * (n - 2) + [-1, 1]
    elif depth == 6:    # (x - 1)(x^(n+3) - x^(n+2) - x^3 - x^2 - x - 1)
        q = [-1, -1, -1, -1] + [0] * (n - 2) + [-1, 1]
    return mulp([-1, 1], q)


def _posthoc_one(args):
    name, payload, sizes, study_counts, p, rounds, maxj = args
    st = stars_for(payload, sizes)
    G, out = grow_lean(st, rounds=rounds, maxj=maxj)
    c = G.counts()
    m = min(len(c), len(study_counts))
    r = {"start": name, "rounds": len(c) - 1, "study rounds": len(study_counts) - 1, "counts equal on common rounds": c[:m] == study_counts[:m],
         "zero demand": G.zero_demand}
    if p is not None:
        r["stated annihilator, frozen rule on the referee's counts"] = frozen_score(p, c)
    return r


def part_posthoc():
    jobs = []
    for f, (n, depth) in {"chain_5_3.json": (5, 3), "chain_7_3.json": (7, 3), "chain_9_3.json": (9, 3), "chain_5_4.json": (5, 4),
                          "chain_7_4.json": (7, 4)}.items():
        d = json.load(open(PH / f))
        jobs.append((f, chain_payload(n, depth), d["sizes"], d["counts"], chain_annihilator(n, depth), 80, 250000))
    for f, depth in (("tree_chain5_5.json", 5), ("tree_chain6_5.json", 6)):
        d = json.load(open(PH / f))
        jobs.append((f, chain_payload(5, depth), d["sizes"], d["counts"], chain_annihilator(5, depth), 80, 250000))
    d = json.load(open(PH / "tree_fork_5.json"))
    fork = {"n": 8, "edges": ring_edges(5) + [(0, 5), (5, 6), (5, 7)]}
    jobs.append(("tree_fork_5.json", fork, d["sizes"], d["counts"], [-1, -3, -3, -1, 0, 0, 0, 0, 1], 80, 250000))
    # the three post hoc cases left unsettled (two rounds tested past the order): grown further, the refined law (law 2) re-scored
    cs = study_cases()
    res = json.load(open(RES))["cases"]
    post = json.load(open(ROOT / "artifacts/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/posthoc.json"))["cases"]
    sys.path.insert(0, str(EXP))
    import posthoc as PHS    # the study's stated law-2 factors (read as data: the prediction under test)
    import job
    for cid in ("D-P1-at-r-a2-b2",):        # one of the three symmetric variants, grown one round past the study (memory)
        p = job.annihilator(5, PHS.predicted(cid, 2))
        jobs.append((cid, cs[cid], res[cid]["sizes"], res[cid]["counts"], p, 20, 10 ** 7))
    only = os.environ.get("ONLY")            # "chains" (the eight post hoc chains, trees and fork) or "dp1" (the long run alone)
    if only == "dp1" and os.environ.get("ALLOW_DP1") != "1":
        return {"skipped": "D-P1-at-r-a2-b2 to round 20 needs about 14 GB; deferred while the machine's memory is in use (set ALLOW_DP1=1)"}
    if only == "fork":                       # the fork alone, at a smaller cap (the full chains run hit its hour on it)
        cap = int(os.environ.get("MAXJ_FORK", "100000"))
        jobs = [tuple(list(j[:6]) + [cap]) for j in jobs if j[0] == "tree_fork_5.json"]
    if only == "chains":
        jobs = jobs[:-1]
    elif only == "dp1":
        jobs = jobs[-1:]
    rows = []
    with open(HERE / f"referee_join_posthoc_{only or 'all'}.jsonl", "w") as fh, Pool(int(os.environ.get("WORKERS", "2"))) as pool:
        for r in pool.imap_unordered(_posthoc_one, jobs, chunksize=1):      # streamed: a killed run keeps what finished
            rows.append(r)
            fh.write(json.dumps(r) + "\n")
            fh.flush()
    return {"rows": rows}


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"validate": part_validate, "regrow": part_regrow, "n9s3": part_n9s3, "posthoc": part_posthoc}.get(part)
    if f:
        print(json.dumps(f(), indent=1, default=str))
    else:
        print(json.dumps({"tworing": part_tworing, "fit": part_fit}[part](sys.argv[2]), indent=1, default=str))
