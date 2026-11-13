"""REACH-CENSUS-20261113-001A, the thread's reading after the referee (R1): the carried-port split of the census's first-ray classes.
A fixed ray carries a top port forever when, with T_1 the copy-1 port positions holding a port of main and T_{k+1} = {j : a_j in T_k}
for the ray call's arguments a, the sets T_k stay non-empty (iterated to a fixed point). Reproduces the referee's 99/32 last-call
split on the 224. Writes carried_split.json (counts by draws and distinct families, by fate cell)."""
import gzip, json, os, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "../../.."))
A = os.path.join(R, "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census")
sys.path.insert(0, os.path.join(HERE, "codex"))
import reach_dp as DP

def carried(prep, ray):
    main, S, e, r = prep.blocks(ray)
    sig = {j: a for j, a in enumerate(S["calls"][r][1]) if a < 3}
    if prep.S == prep.main:
        T = set(sig)
    else:
        T = {j for j, a in enumerate(main["calls"][e][1]) if a < main["k"]}
    for _ in range(16):
        T = {j for j, a in sig.items() if a in T}
    return bool(T)

fam = {}
for x in gzip.open(os.path.join(A, "families.jsonl.gz"), "rt"):
    r = json.loads(x); fam[r["key"]] = r
persist = ("bounded", "grows", "mixed by residue", "unresolved")
flag = {}
for k, r in fam.items():
    if r["class"] in persist and r["class"] != "unresolved":
        flag[k] = "carried" if carried(DP.Preparation(json.loads(k)), "first") else "uncarried"
out = defaultdict(Counter); dist = defaultdict(Counter)
for x in gzip.open(os.path.join(HERE, "codex/draws.jsonl.gz"), "rt"):
    d = json.loads(x); r = fam[d["key"]]
    if r["class"] not in persist:
        continue
    cell = "forever" if d["fate"] == "forever" else ("limit-only" if r.get("usual_limit_alive") else "dead")
    c = r["class"] if r["class"] == "unresolved" else f'{r["class"]}, {flag[d["key"]]}'
    out[cell][c] += 1; out["all"][c] += 1
for k, r in fam.items():
    if r["class"] in persist:
        dist["all"][r["class"] if r["class"] == "unresolved" else f'{r["class"]}, {flag[k]}'] += 1
lc = Counter()
for x in gzip.open(os.path.join(A, "alt_growing664_families.jsonl.gz"), "rt"):
    r = json.loads(x)
    lc[f'{r["class"]}, {"carried" if carried(DP.Preparation(json.loads(r["key"])), "last") else "uncarried"}'] += 1
res = dict(draws={c: dict(v) for c, v in out.items()}, distinct=dict(dist["all"]), last_call_on_224=dict(lc))
json.dump(res, open(os.path.join(HERE, "carried_split.json"), "w"), indent=1)
print(json.dumps(res, indent=1))

# the 3,000-family last-call sample: first-call class against last-call class, with the last-call ray's carried flag
first = {k: r["class"] for k, r in fam.items()}
m = Counter()
for x in gzip.open(os.path.join(A, "alt_families.jsonl.gz"), "rt"):
    r = json.loads(x)
    if first[r["key"]] == "grows" and r["class"] == "bounded":
        m["grows -> bounded, last-call " + ("carried" if carried(DP.Preparation(json.loads(r["key"])), "last") else "uncarried")] += 1
res["alt_sample_grows_to_bounded"] = dict(m)
json.dump(res, open(os.path.join(HERE, "carried_split.json"), "w"), indent=1)
print(dict(m))
