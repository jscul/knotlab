"""Descriptive tables for RANDOM-FATES-20261112-001A from the census's runs (after the run; no prediction is tested here).

Reads artifacts/.../runs.jsonl (and runs_u300core.jsonl when present) and writes describe.json beside this file.
Run from the repository root: .venv/bin/python -B research/RANDOM-FATES-20261112-001/describe.py
"""
import json
import os
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
A = os.path.join(ROOT, "artifacts", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census")
recs = []
for name in ("runs.jsonl", "runs_u300core.jsonl"):
    p = os.path.join(A, name)
    if os.path.exists(p):
        recs += [json.loads(l) for l in open(p)]
by = defaultdict(list)
for r in recs:
    by[r["label"]].append(r)
out = {"runs": len(recs)}


def share(xs):
    xs = list(xs)
    return round(sum(1 for x in xs if x) / len(xs), 3) if xs else None


def prof(reads, d):
    sizes = [s for r in reads for (_, _, s, _) in r.get("bond_profile", {}).get(str(d), [])]
    if not sizes:
        return None
    return {"pairs": len(sizes), "ruler": share(s == d + 2 for s in sizes), "shortcut": share(s is not None and s < d + 2 for s in sizes),
            "none": share(s is None for s in sizes)}


# U: the way to the end
U = {}
for n in (50, 100, 200, 300):
    rs = by.get(f"U{n}", [])
    e = {"runs": len(rs), "death_density_median": float(np.median([r["density"] for r in rs])),
         "death_density_q10_q90": [float(np.quantile([r["density"] for r in rs], x)) for x in (0.1, 0.9)]}
    cores = [r for r in rs if "core_knots" in r]
    if cores:
        e["core_share_of_knots_median"] = float(np.median([r["core_knots"] / r["death_knot"] for r in cores]))
        e["core_distinctions_share_median"] = float(np.median([r["core_distinctions"] / n for r in cores]))
        e["cores"] = len(cores)
    rd = [r for r in rs if "reads" in r]
    pts = {}
    for key in ("f0.5", "f0.75", "f0.9", "k50", "k20", "k10", "k5", "k3", "k2", "k1"):
        xs = [r["reads"][key] for r in rd if key in r["reads"]]
        if not xs:
            continue
        p = {"largest_share_median": float(np.median([x["largest_class"] / x["n_used"] for x in xs])),
             "largest_share_q25_q75": [float(np.quantile([x["largest_class"] / x["n_used"] for x in xs], z)) for z in (0.25, 0.75)],
             "tied_share_median": float(np.median([x["tied_distinctions"] / x["n_used"] for x in xs])),
             "tie_free": share(x["tied_pairs"] == 0 for x in xs),
             "tie_reach_median": float(np.median([x["tie_reach"] for x in xs]))}
        if any("bond_profile" in x for x in xs):
            p["d3"] = prof(xs, 3)
            p["d2"] = prof(xs, 2)
        if any("faithful" in x for x in xs):
            p["faithful"] = share(x.get("faithful") for x in xs if "faithful" in x)
        pts[key] = p
    e["points"] = pts
    U[f"U{n}"] = e
out["U"] = U

# growth processes
G = {}
for lab in sorted(by):
    if lab.startswith("U"):
        continue
    rs = by[lab]
    e = {"runs": len(rs), "alive_at_horizon": share(not r["dead"] for r in rs)}
    dead = [r for r in rs if r["dead"]]
    if dead:
        e["knots_at_end_median"] = float(np.median([r["knots"] for r in dead]))
        e["distinctions_at_end_median"] = float(np.median([r["n_at_death"] for r in dead]))
        e["core_knots_median"] = float(np.median([r["core_knots"] for r in dead]))
        e["core_span_median"] = float(np.median([r["core_index_span"] for r in dead]))
        e["core_share_of_knots_median"] = float(np.median([r["core_knots"] / r["knots"] for r in dead]))
    rd = [r for r in rs if "reads" in r]
    pts = {}
    for key in ("end", "k50", "k20", "k10", "k5", "k1"):
        xs = [r["reads"][key] for r in rd if key in r["reads"] and r["reads"][key].get("state")]
        if not xs:
            continue
        p = {"bases": len(xs), "largest_share_median": float(np.median([x["largest_class"] / x["n_used"] for x in xs])),
             "largest_median": float(np.median([x["largest_class"] for x in xs])),
             "tied_share_median": float(np.median([x["tied_distinctions"] / x["n_used"] for x in xs])),
             "tie_reach_median": float(np.median([x["tie_reach"] for x in xs])),
             "max_knots_on_pair_median": float(np.median([x["max_knots_on_pair"] for x in xs])),
             "pairs_in_two_or_more_share": float(np.median([x["pairs_in_two_or_more"] / max(1, x["co_knotted_pairs"]) for x in xs]))}
        if any("bond_profile" in x for x in xs):
            p["d2"] = prof(xs, 2)
            p["d3"] = prof(xs, 3)
            balls = [b for x in xs for b in x.get("step_balls", [])]
            p["step_ball_median"] = [float(np.median([b[r] for b in balls])) for r in range(6)]
        pts[key] = p
    e["points"] = pts
    G[lab] = e
out["growth"] = G
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "describe.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True)[:200])
