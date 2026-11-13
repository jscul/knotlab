"""BOND-DEPTH-R1: the normaliser of the repeat detector across levels. Runs the study's run_family with one line instrumented
(the minimum state cost mn is recorded at every level) on a few small families of each class; prints mn by level against L(s)."""
import importlib.util, inspect, json, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds"
os.chdir(ROOT)
s = importlib.util.spec_from_file_location("bd", D / "census.py"); B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
src = inspect.getsource(B.run_family).replace("mn = min(layer.values())", "mn = min(layer.values()); MN.append(mn)")
ns = dict(B.__dict__); ns["MN"] = []
exec(src, ns)
rows = [json.loads(x) for x in open(ROOT / "artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl")]
fams = dict(B.families_one_def())
def kind(r):
    if r.get("rate"): return "bounded"
    L = [x for x in r["L"] if x < B.INF]
    return "rising" if L and L[-1] > L[len(L) // 2] else "flat"
out = []
for k in ("rising", "flat", "bounded"):
    pick = sorted([r for r in rows if r.get("L") and kind(r) == k], key=lambda r: r.get("states", 0))[:3]
    for r in pick:
        ns["MN"].clear()
        res = ns["run_family"](fams[r["idx"]], smax=12)
        out.append(dict(kind=k, idx=r["idx"], L=res["L"], mn=list(ns["MN"]), rate=res["rate"]))
        print(json.dumps(out[-1]), flush=True)
json.dump(out, open(Path(__file__).with_name("result_mn.json"), "w"), indent=1)
