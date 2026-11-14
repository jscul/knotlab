"""TIE-CYCLE-20261114-001A, the one held-out reading of stage 2's H1-H4 (and the training figures by the same code). Writes
heldout.json."""
import hashlib, json, math, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; R = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(R / "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex"))
import ties as T
import reach_dp as DP
rows = {}
for x in open(R / "experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl"):
    r = json.loads(x); rows[r["case"]] = r["result"]
def half(k): return "train" if int(hashlib.sha256(("TIE:" + k).encode()).hexdigest()[:8], 16) % 2 == 0 else "heldout"
def ncyc(prep):
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
def wilson(k, n, z=1.96):
    p = k/n; d = 1+z*z/n; c = p+z*z/(2*n); h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (round((c-h)/d, 4), round((c+h)/d, 4))
res = {}
for part in ("train", "heldout"):
    keys = [k for k in rows if half(k) == part]
    tab = Counter(); h1 = []; h3 = []; resid = Counter(); beyond = Counter(); capped_settled = 0; parity_only = 0; ok = 0
    for k in keys:
        v = rows[k]; d = T.classify_full(v["R_i"])
        if d["status"] != "ok":
            tab[("semigroup cap",)] += 1; continue
        ok += 1
        strat = ("chain" if v["chain"] else "nonchain") + ("/1def" if v["n_defs"] == 1 else "/multi")
        tab[(strat, "tie" if d["tie_cycle"] else "no tie", v["verdict"])] += 1
        if d["tie_cycle"] and v["verdict"] == "certified": h1.append(k)
        if d["tie_cycle"] and v["verdict"] == "capped": capped_settled += 1
        if d["tie_cycle"] and v["verdict"] != "certified" and not ncyc(DP.Preparation(json.loads(k))): beyond[strat] += 1
        if v["verdict"] in ("certified", "non-forgetting"):
            if (v["verdict"] == "certified") != (not d["idempotent_types"]): h3.append(k)
        if d["parity_cycle"] and not d["tie_cycle"]: parity_only += 1
        if (not v["chain"]) and (not d["tie_cycle"]) and v["verdict"] == "non-forgetting":
            resid[tuple(d["idempotent_types"])] += 1
    nt = {}
    for kind in ("chain", "nonchain"):
        f = sum(c for (s, t, vv), c in [(k3, c) for k3, c in tab.items() if len(k3) == 3] for _ in [0] if s.startswith(kind) and t == "no tie" and vv == "certified")
        n = sum(c for (s, t, vv), c in [(k3, c) for k3, c in tab.items() if len(k3) == 3] for _ in [0] if s.startswith(kind) and t == "no tie" and vv in ("certified", "non-forgetting"))
        nt[kind] = dict(n=n, forget=f, share=round(f/n, 4) if n else None, wilson=wilson(f, n) if n else None)
    rtot = sum(resid.values()); order_only = resid.get(("order",), 0)
    res[part] = dict(families=len(keys), decided=ok, H1_violations=len(h1), ties_beyond_identity=dict(beyond), H3_violations=len(h3),
                     no_tie=nt, residual_types={"|".join(k) or "none": c for k, c in resid.items()}, residual=rtot,
                     residual_order_only=order_only, residual_order_share=round(order_only/rtot, 4) if rtot else None,
                     capped_settled_by_tie=capped_settled, parity_without_tie=parity_only,
                     table={"|".join(k): c for k, c in sorted(tab.items())})
ho = res["heldout"]
v = {"H1": "holds" if ho["H1_violations"] == 0 else "fails",
     "H2": "holds" if (ho["no_tie"]["chain"]["share"] == 1.0 and 0.915 <= ho["no_tie"]["nonchain"]["share"] <= 0.955) else "fails",
     "H3": "holds" if ho["H3_violations"] == 0 else "fails",
     "H4": "holds" if (ho["residual_order_share"] or 0) >= 0.80 else "fails"}
res["verdicts"] = v
json.dump(res, open(HERE / "heldout.json", "w"), indent=1)
for p in ("train", "heldout"):
    print(p, json.dumps({k: res[p][k] for k in ("families", "decided", "H1_violations", "ties_beyond_identity", "H3_violations", "no_tie", "residual", "residual_types", "residual_order_share", "capped_settled_by_tie", "parity_without_tie")}))
print(v)
