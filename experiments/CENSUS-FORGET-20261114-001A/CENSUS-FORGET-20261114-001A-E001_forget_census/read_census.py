"""CENSUS-FORGET-20261114-001A, the thread's reading: shares by stratum, by count and by weight (draws), Wilson intervals; P1 outside
EVERY-RAY's sampled G families; the gates (EVERY-RAY consistency, FREE-TARGET reproduction, audit). Writes reading.json."""
import gzip, json, math, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, "../../.."))
draws = Counter(json.loads(x)["key"] for x in gzip.open(os.path.join(R, "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz"), "rt"))
rows = {}
for x in open(os.path.join(HERE, "full/results.jsonl")):
    r = json.loads(x); rows[r["case"]] = r["result"]
def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k/n; d = 1+z*z/n; c = p+z*z/(2*n); h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (round((c-h)/d, 4), round((c+h)/d, 4))
def stratum(r):
    return "chain" if r["chain"] else ("c>=2" if r["c"] >= 2 else "c=1 other")
out = dict(families=len(rows), draws=sum(draws[k] for k in rows))
tab = {}
for s in ("chain", "c>=2", "c=1 other", "all"):
    ks = [k for k, r in rows.items() if s == "all" or stratum(r) == s]
    n = len(ks); w = sum(draws[k] for k in ks)
    v = Counter(rows[k]["verdict"] for k in ks); vw = Counter()
    for k in ks: vw[rows[k]["verdict"]] += draws[k]
    tab[s] = dict(families=n, draws=w, by_count={a: dict(n=b, share=round(b/n, 4), wilson=wilson(b, n)) for a, b in v.items()},
                  by_weight={a: dict(draws=b, share=round(b/w, 4), wilson=wilson(b, w)) for a, b in vw.items()})
out["strata"] = tab
EV = os.path.join(R, "experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample")
sel = json.load(open(os.path.join(EV, "selection.json")))
G300 = set(sel["G"])
p1 = [k for k, r in rows.items() if not r["chain"] and r["c"] >= 2 and k not in G300]
w = sum(draws[k] for k in p1); wc = sum(draws[k] for k in p1 if rows[k]["verdict"] == "certified")
out["P1"] = dict(families=len(p1), draws=w, certified_draws=wc, share=round(wc/w, 4), wilson=wilson(wc, w),
                 certified_families=sum(rows[k]["verdict"] == "certified" for k in p1))
lo, hi = out["P1"]["wilson"]
out["P1_verdict"] = "holds" if lo >= 0.08 and hi <= 0.25 else ("fails" if hi < 0.08 or lo > 0.25 else "undecided")
# gates
ev = {}
for name in ("G.jsonl", "N.jsonl", "B.jsonl", "B_resume.jsonl", "phase2.jsonl"):
    p = os.path.join(EV, name)
    if os.path.exists(p):
        for x in open(p):
            r = json.loads(x); ev[r["key"]] = r
bad = [k for k, r in ev.items() if r.get("class_path") == "bounded" and k in rows and rows[k]["verdict"] == "certified"]
out["gate_consistency"] = dict(checked=sum(k in rows for k in ev), forgetting_and_bounded_over_paths=len(bad), passed=not bad, examples=bad[:3])
FT = os.path.join(R, "experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex")
ft = {}
for x in open(os.path.join(FT, "full/results.jsonl")):
    r = json.loads(x); ft[r["case"]] = r["result"]
def ft_r(res): return (res.get("semigroup") or {}).get("r")
agree = sum(1 for k, res in ft.items() if k in rows and rows[k].get("r") == ft_r(res)); cert = sum(1 for k in ft if k in rows and rows[k]["verdict"] == "certified")
out["gate_reproduction"] = dict(families=len(ft), in_census=sum(k in rows for k in ft), same_r=agree, certified=cert, passed=(agree == len(ft) and cert == 43))
mism = [k for k, r in rows.items() if r.get("verdict") == "certified" and r.get("audit_mismatches")]
out["gate_audit"] = dict(certified=sum(r["verdict"] == "certified" for r in rows.values()), with_mismatch=len(mism), passed=not mism)
out["r_distribution"] = dict(sorted(Counter(r["r"] for r in rows.values() if r.get("r") is not None).items()))
out["r_distribution_nonchain"] = dict(sorted(Counter(r["r"] for r in rows.values() if r.get("r") is not None and not r["chain"]).items()))
out["empty_relation_families"] = sum(bool(r.get("empty_relation")) for r in rows.values())
CEN = os.path.join(R, "experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex")
g = [json.loads(x) for x in open(os.path.join(R, "experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/gates_full/validation_last.jsonl"))]
k224 = {x["key"] for x in g}
out["the_224"] = dict(Counter(rows[k]["verdict"] for k in k224 if k in rows))
json.dump(out, open(os.path.join(HERE, "reading.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "strata"}, indent=1))
for s, t in tab.items(): print(s, t["families"], t["draws"], {a: (b["draws"], b["share"], b["wilson"]) for a, b in t["by_weight"].items()})
