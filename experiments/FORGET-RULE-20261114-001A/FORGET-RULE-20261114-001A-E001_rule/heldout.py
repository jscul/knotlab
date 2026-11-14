"""FORGET-RULE-20261114-001A, the one held-out evaluation (stage 2's H1-H4), and the training figures recomputed by the same code.
Writes heldout.json."""
import hashlib, json, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
R = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(R / "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex"))
import rule_A as A
import reach_dp as DP
rows = {}
for x in open(R / "experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl"):
    r = json.loads(x); rows[r["case"]] = r["result"]
def half(k): return "train" if int(hashlib.sha256(k.encode()).hexdigest()[:8], 16) % 2 == 0 else "heldout"
def n_cyclic(prep):
    S = prep.flat(prep.S); adj = {i: set() for i in range(3)}
    for c, a in S["calls"]:
        if c == prep.S:
            for k, x in enumerate(a):
                if x < 3: adj[x].add(k)
    color = {}
    def dfs(u):
        color[u] = 1
        for v in adj[u]:
            if color.get(v) == 1 or (color.get(v) is None and dfs(v)): return True
        color[u] = 2; return False
    return any(color.get(u) is None and dfs(u) for u in range(3))
res = {}
for part in ("train", "heldout"):
    keys = [k for k in rows if half(k) == part]
    t = Counter(); h1 = []; h2 = []; rbound = Counter()
    for k in keys:
        v = rows[k]; prep = DP.Preparation(json.loads(k))
        strat = ("chain" if v["chain"] else "nonchain") + ("/1def" if v["n_defs"] == 1 else "/multi")
        nc = n_cyclic(prep); a = A.decide(json.loads(k))
        t[(strat, "N-cyclic" if nc else "N-acyclic", "A" if a["rule_A"] else "notA", v["verdict"])] += 1
        if nc and v["verdict"] == "certified": h1.append(k)
        if a["rule_A"] and v["verdict"] != "certified": h2.append(k)
        if a["rule_A"] and v.get("r") is not None: rbound[v["r"] <= a["r_bound"]] += 1
    forget = Counter(); cover = Counter(); nac = Counter(); nacf = Counter()
    for (strat, n, a, verdict), c in t.items():
        if verdict == "certified":
            forget[strat] += c
            if a == "A": cover[strat] += c
        if n == "N-acyclic" and verdict in ("certified", "non-forgetting"):
            kind = strat.split("/")[0]; nac[kind] += c
            if verdict == "certified": nacf[kind] += c
    res[part] = dict(families=len(keys), H1_violations=len(h1), H1_examples=h1[:3], H2_violations=len(h2), H2_examples=h2[:3],
                     r_within_bound=dict(rbound),
                     coverage={s: dict(certified=forget[s], by_A=cover[s], share=round(cover[s]/forget[s], 4) if forget[s] else None) for s in sorted(forget)},
                     coverage_total=round(sum(cover.values())/sum(forget.values()), 4),
                     N_acyclic_forgetting={k: dict(n=nac[k], forget=nacf[k], share=round(nacf[k]/nac[k], 4)) for k in nac},
                     table={"|".join(k): c for k, c in sorted(t.items())})
tr, ho = res["train"], res["heldout"]
v = {}
v["H1"] = "holds" if ho["H1_violations"] == 0 else "fails"
v["H2"] = "holds" if ho["H2_violations"] == 0 and ho["r_within_bound"].get(False, 0) == 0 else "fails"
ok3 = 0.30 <= ho["coverage_total"] <= 0.42 and all(abs(ho["coverage"][s]["share"] - tr["coverage"][s]["share"]) <= 0.08 for s in ho["coverage"])
v["H3"] = "holds" if ok3 else "fails"
v["H4"] = "holds" if ho["N_acyclic_forgetting"]["chain"]["share"] >= 0.99 and ho["N_acyclic_forgetting"]["nonchain"]["share"] >= 0.90 else "fails"
res["verdicts"] = v
json.dump(res, open(HERE / "heldout.json", "w"), indent=1)
print(json.dumps({p: {k: res[p][k] for k in ("families", "H1_violations", "H2_violations", "r_within_bound", "coverage", "coverage_total", "N_acyclic_forgetting")} for p in ("train", "heldout")}, indent=1))
print(v)
