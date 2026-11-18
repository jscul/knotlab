"""Shared-runner job for BOND-METRIC-20261118-001B-E001: the triangle inequality for bond distance."""
import itertools
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metriclib as M  # noqa: E402

LANGS = {k: v for k, v in M.LANGUAGES.items() if k != "parity"}  # the eight non-parity languages
SHARD = 400  # triple sets per case


def triple_sets(n, k, linear=False):
    """Every set of k distinct triples on n distinctions covering all n, in a fixed order."""
    out = []
    for ts in itertools.combinations(itertools.combinations(range(n), 3), k):
        if M.covers(ts, n) and (not linear or M.meet_at_most_once(ts)):
            out.append(ts)
    return out


def cases():
    for n in range(4, 8):
        for k in range(2, 5):
            m = len(triple_sets(n, k))
            for s in range(0, m, SHARD):
                yield f"parity-n{n}-k{k}-s{s // SHARD}", {"kind": "parity", "n": n, "k": k, "lo": s, "hi": min(m, s + SHARD)}
    for i in range(40):
        yield f"parity-rand-{i}", {"kind": "parity-rand", "seed": 7000 + i}
    for name in LANGS:
        for n in range(4, 8):
            for k in range(2, 5):
                m = len(triple_sets(n, k))
                for s in range(0, m, SHARD):
                    yield f"lang-{name}-n{n}-k{k}-s{s // SHARD}", {"kind": "lang", "law": name, "n": n, "k": k, "lo": s,
                                                                  "hi": min(m, s + SHARD)}
    for n in (7, 8):
        for k in range(3, n + 1):
            m = len(triple_sets(n, k, linear=True)) if n == 7 else None
            if n == 7:
                for s in range(0, m, SHARD):
                    yield f"nae-once-n7-k{k}-s{s // SHARD}", {"kind": "once", "n": 7, "k": k, "lo": s, "hi": min(m, s + SHARD)}
            else:
                yield f"nae-once-n8-k{k}", {"kind": "once8", "n": 8, "k": k}
    for L, W in ((3, 3), (3, 4), (4, 4), (4, 5)):
        yield f"weave-{L}x{W}", {"kind": "weave", "L": L, "W": W}
    for i in range(40):
        yield f"mixed-rand-{i}", {"kind": "mixed-rand", "seed": 8000 + i}


def read(n, knots, keep_corr=False):
    """Triangle failures of b and of b - 1 on one base, with the first example of each and, if asked, an exact test of whether
    every pair whose long side is infinite is correlated, with the least such |C|."""
    st = M.states(n, knots)
    if len(st) == 0:
        return None
    D = M.bond_matrix(n, st)
    v1 = M.violations(D, n, 0)
    v2 = M.violations(D, n, 1)
    r = {"v_b": len(v1), "v_b1": len(v2), "inf_fail": sum(1 for v in v1 if v[5] == math.inf)}
    if v1:
        r["ex_b"] = [list(v1[0][:3]), [None if t == math.inf else t for t in v1[0][3:]]]
    if v2:
        r["ex_b1"] = [list(v2[0][:3]), [None if t == math.inf else t for t in v2[0][3:]]]
    if keep_corr and v1:
        longs = {(x, z) for x, y, z, _, _, l in v1 if l == math.inf}
        if longs:
            r["inf_all_correlated"] = all(M.correlated(st, x, z) for x, z in longs)
            r["corr_inf"] = min(abs(M.correlation(st, x, z)) for x, z in longs)
    return r


def summarise(rows, meta):
    """rows: (law tuple labels, triples, reading)."""
    out = {"bases": 0, "failing_b": 0, "failing_b1": 0, "triples_b": 0, "inf_triples": 0, "examples_b": [], "examples_b1": [],
           "min_abs_corr_inf": None, "inf_all_correlated": True, "failing_once": 0, "example_once": None}
    for labels, ts, r in rows:
        if r is None:
            continue
        out["bases"] += 1
        out["triples_b"] += r["v_b"]
        out["inf_triples"] += r["inf_fail"]
        if r["v_b"]:
            out["failing_b"] += 1
            if M.meet_at_most_once(ts):
                out["failing_once"] += 1
                if out["example_once"] is None:
                    out["example_once"] = {"knots": [[l, list(t)] for l, t in zip(labels, ts)], "triple": r["ex_b"]}
            if len(out["examples_b"]) < 3:
                out["examples_b"].append({"knots": [[l, list(t)] for l, t in zip(labels, ts)], "triple": r["ex_b"]})
        if r["v_b1"]:
            out["failing_b1"] += 1
            if len(out["examples_b1"]) < 3:
                out["examples_b1"].append({"knots": [[l, list(t)] for l, t in zip(labels, ts)], "triple": r["ex_b1"]})
        if "corr_inf" in r:
            c = r["corr_inf"]
            out["min_abs_corr_inf"] = c if out["min_abs_corr_inf"] is None else min(out["min_abs_corr_inf"], c)
            out["inf_all_correlated"] &= r["inf_all_correlated"]
    out.update(meta)
    return out


def label(R):
    return "".join(str(int(p in R)) for p in range(8))


def run(case_id, p):
    kind = p["kind"]
    if kind == "parity":
        rows = []
        for ts in triple_sets(p["n"], p["k"])[p["lo"]:p["hi"]]:
            for ls in itertools.product((M.P0, M.P1), repeat=p["k"]):
                rows.append(([label(R) for R in ls], ts, read(p["n"], list(zip(ls, ts)))))
        return summarise(rows, {"n": p["n"], "k": p["k"]})
    if kind == "parity-rand":
        rng = random.Random(p["seed"])
        rows = []
        while len([r for r in rows if r[2] is not None]) < 50:
            n = rng.randint(8, 12)
            k = rng.randint(3, 12)
            ts = sorted({tuple(sorted(rng.sample(range(n), 3))) for _ in range(k)})
            ls = [rng.choice((M.P0, M.P1)) for _ in ts]
            rows.append(([label(R) for R in ls], ts, read(n, list(zip(ls, ts)))))
        return summarise(rows, {})
    if kind == "lang":
        laws = M.orders(LANGS[p["law"]])
        rows = []
        for ts in triple_sets(p["n"], p["k"])[p["lo"]:p["hi"]]:
            for ls in itertools.product(laws, repeat=p["k"]):
                rows.append(([label(R) for R in ls], ts, read(p["n"], list(zip(ls, ts)), keep_corr=True)))
        return summarise(rows, {"law": p["law"], "n": p["n"], "k": p["k"]})
    if kind == "once":
        rows = [([label(M.NAE)] * p["k"], ts, read(7, [(M.NAE, t) for t in ts], keep_corr=True))
                for ts in triple_sets(7, p["k"], linear=True)[p["lo"]:p["hi"]]]
        return summarise(rows, {"n": 7, "k": p["k"]})
    if kind == "once8":
        tr = list(itertools.combinations(range(8), 3))
        rows, rings = [], {}

        def rec(start, chosen, used):
            if len(chosen) == p["k"]:
                if len(used) == 8:
                    r = read(8, [(M.NAE, t) for t in chosen], keep_corr=True)
                    rows.append(([label(M.NAE)] * p["k"], tuple(chosen), r))
                    g = M.shortest_ring(chosen)
                    key = f"{g}:{'fail' if r and r['v_b'] else 'pass'}"
                    rings[key] = rings.get(key, 0) + 1
                return
            for i in range(start, len(tr)):
                if all(len(set(tr[i]) & set(u)) <= 1 for u in chosen):
                    rec(i + 1, chosen + [tr[i]], used | set(tr[i]))
        rec(0, [], set())
        return summarise(rows, {"n": 8, "k": p["k"], "shortest_ring_by_outcome": rings})
    if kind == "weave":
        L, W = p["L"], p["W"]
        idx = lambda i, j: (i % L) * W + (j % W)
        ts = sorted({tuple(sorted({idx(i, j), idx(i + 1, j), idx(i, j + 1)})) for i in range(L) for j in range(W)} |
                    {tuple(sorted({idx(i + 1, j), idx(i, j + 1), idx(i + 1, j + 1)})) for i in range(L) for j in range(W)})
        ts = [t for t in ts if len(t) == 3]
        r = read(L * W, [(M.NAE, t) for t in ts], keep_corr=True)
        return summarise([([label(M.NAE)] * len(ts), ts, r)], {"L": L, "W": W, "knots": len(ts)})
    if kind == "mixed-rand":
        rng = random.Random(p["seed"])
        rows, once = [], {"once": [0, 0], "not": [0, 0]}
        while len([r for r in rows if r[2] is not None]) < 50:
            n = rng.randint(6, 9)
            k = rng.randint(3, 8)
            ts = sorted({tuple(sorted(rng.sample(range(n), 3))) for _ in range(k)})
            if not M.covers(ts, n):
                continue
            ls = [rng.choice(M.PNB) for _ in ts]
            r = read(n, list(zip(ls, ts)))
            rows.append(([label(R) for R in ls], ts, r))
            if r is not None:
                key = "once" if M.meet_at_most_once(ts) else "not"
                once[key][0] += 1
                once[key][1] += bool(r["v_b"])
        return summarise(rows, {"bases_and_failing_by_meeting": once})
    raise ValueError(kind)
