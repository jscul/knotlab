"""REACH-CENSUS-R2: an independent recount of the carried split on one-definition families (main = the ray definition, first
SELF call), by draws and by fate cell, from families.jsonl.gz and the replayed draws. Multi-definition families are counted
separately and not re-tested here."""
import gzip, json
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census"
DRAWS = ROOT / "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz"


def carried(args):
    T = {j for j, a in enumerate(args) if a < 3}            # copy-1 positions holding a top port
    for _ in range(16):
        T = {j for j, a in enumerate(args) if a in T}
    return bool(T)


fam = {json.loads(x)["key"]: json.loads(x) for x in gzip.open(A / "families.jsonl.gz", "rt")}
persist = {"bounded", "grows", "mixed by residue"}
flag = {}
for k, r in fam.items():
    defs = json.loads(k)
    if r["class"] in persist and len(defs) == 1:
        first = [tuple(a) for c, a in defs[0][2] if c == "SELF"][0]
        flag[k] = "carried" if carried(first) else "uncarried"
out = defaultdict(Counter)
for x in gzip.open(DRAWS, "rt"):
    d = json.loads(x)
    r = fam[d["key"]]
    if r["class"] not in persist:
        continue
    cell = "forever" if d["fate"] == "forever" else ("limit-only" if r.get("usual_limit_alive") else "dead")
    c = f'{r["class"]}, {flag[d["key"]]}' if d["key"] in flag else f'{r["class"]}, several definitions'
    out[cell][c] += 1
    out["all"][c] += 1
res = {cell: dict(sorted(v.items())) for cell, v in out.items()}
for cell, v in res.items():
    bu, gu = v.get("bounded, uncarried", 0), v.get("grows, uncarried", 0)
    bc = v.get("bounded, carried", 0)
    v["one-definition: grows share among uncarried"] = round(gu / (bu + gu), 4) if bu + gu else None
    v["one-definition: carried share of bounded"] = round(bc / (bc + bu), 4) if bc + bu else None
print(json.dumps(res, indent=1))
json.dump(res, open(Path(__file__).with_name("result_split.json"), "w"), indent=1)
