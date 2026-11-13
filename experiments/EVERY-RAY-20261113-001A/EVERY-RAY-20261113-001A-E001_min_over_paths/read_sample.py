"""EVERY-RAY-20261113-001A, the thread's reading of the frozen sample (pre-registration, third clarification): P1 to P3 with Wilson
bands, phase-2 rows replacing capped ones. Writes sample_reading.json."""
import gzip, json, math, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "codex", "sample")
draws = Counter(json.loads(x)["key"] for x in gzip.open(os.path.join(HERE, "../../REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz"), "rt"))
def rows(name):
    p = os.path.join(S, name)
    return {json.loads(x)["key"]: json.loads(x) for x in open(p)} if os.path.exists(p) else {}
p2 = rows("phase2.jsonl")
def stratum(name, *extra):
    r = rows(name)
    for e in extra:
        r.update(rows(e))
    for k in list(r):
        if k in p2:
            r[k] = p2[k]
    return r
def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))
def band(rs, pred):
    n = len(rs); un = sum(r["class_path"] == "unresolved" for r in rs); k = sum(pred(r) for r in rs)
    wt = sum(draws[r["key"]] for r in rs); wk = sum(draws[r["key"]] for r in rs if pred(r)); wu = sum(draws[r["key"]] for r in rs if r["class_path"] == "unresolved")
    return dict(n=n, k=k, unresolved=un, low=round(k / n, 4) if n else None, high=round((k + un) / n, 4) if n else None,
                wilson_low_of_low=wilson(k, n)[0], wilson_high_of_high=wilson(k + un, n)[1],
                weight_low=round(wk / wt, 4) if wt else None, weight_high=round((wk + wu) / wt, 4) if wt else None)
out = {}
G = list(stratum("G.jsonl").values()); N = list(stratum("N.jsonl").values()); B = list(stratum("B.jsonl", "B_resume.jsonl").values())
out["sizes"] = dict(G=len(G), N=len(N), B=len(B), phase2=len(p2))
out["G_class_path"] = dict(Counter(r["class_path"] for r in G)); out["N_class_path"] = dict(Counter(r["class_path"] for r in N))
out["G_status"] = dict(Counter(r["status"] for r in G))
ineq = [r for r in G if r.get("symmetry_inequivalent")]; eq = [r for r in G if not r.get("symmetry_inequivalent")]
out["P1_verdict_reading"] = band(ineq, lambda r: r["class_path"] == "bounded")
lo, hi = out["P1_verdict_reading"]["wilson_low_of_low"], out["P1_verdict_reading"]["wilson_high_of_high"]
out["P1_verdict"] = "holds" if lo >= 0.75 else ("fails" if hi < 0.75 else "undecided")
out["P1_equivalent_call_families"] = dict(n=len(eq), class_path=dict(Counter(r["class_path"] for r in eq)))
out["P1_uncarried_reading"] = band(ineq, lambda r: r.get("bounded_split") == "bounded, uncarried")
out["P1_carried_only"] = sum(r.get("bounded_split") == "bounded, carried only" for r in ineq)
out["P1_mixed_path_needed"] = sum(bool(r.get("mixed_path_needed")) for r in ineq if r["class_path"] == "bounded")
out["P1_uncarried_class_of_growers_over_paths"] = dict(Counter(r.get("class_path_uncarried") for r in ineq if r["class_path"] == "grows"))
grow2 = [r for r in G + N if r["class_path"] == "grows" and r.get("symmetry_inequivalent") and r.get("complete")]
out["P2_inequivalent_growers_over_paths"] = len(grow2)
out["P2_verdict"] = "holds" if grow2 else "not found"
hit = [r for r in N if r["class_path"] in ("grows", "bounded", "mixed by residue")]
out["P3_hits"] = len(hit); out["P3_hit_classes"] = dict(Counter(r["class_path"] for r in hit)); out["P3_verdict"] = "holds" if hit else "not found"
out["P3_share"] = band(N, lambda r: r["class_path"] in ("grows", "bounded", "mixed by residue"))
out["B_bounded_split"] = dict(Counter(r.get("bounded_split") for r in B))
out["first_ray_carried_in_G"] = dict(Counter(bool(r.get("first_ray_carried")) for r in G))
json.dump(out, open(os.path.join(HERE, "sample_reading.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
