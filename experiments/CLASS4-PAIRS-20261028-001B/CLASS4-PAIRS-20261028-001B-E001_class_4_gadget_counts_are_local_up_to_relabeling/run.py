"""CLASS4-PAIRS-20261028-001B-E001: class-4 gadget counts are local up to a relabeling of layer-3 data (frozen contract:
contract.json).  Cases: free class 4 on (1, 1), (0, 1, 1), (1, 1, 1) at d = 5, p = 11, slots (1, 1, 2).  Controls: X1 the
cumulative design (K11); X2 free class 4 on (1, 2), slots (1, 2, 3), whose dual slot has layer-1 data.
Run: python3 -B run.py  (writes the artifact directory)"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from c4_lib import *  # noqa: E402
T0 = time.time()
ART = os.path.join(ROOT, "artifacts", "CLASS4-PAIRS-20261028-001B", os.path.basename(HERE))
os.makedirs(ART, exist_ok=True)
LOG = open(os.path.join(ART, "run_log.txt"), "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


CASES = [("K11", [1, 1]), ("K011", [0, 1, 1]), ("K111", [1, 1, 1])]
SHAPES = [("P3", 3, [(0, 1), (1, 2)]), ("skip", 3, [(0, 2)]), ("star", 4, [(0, 1), (0, 2), (0, 3)]),
          ("triangle", 3, [(0, 1), (0, 2), (1, 2)]), ("P3 reversed", 3, [(0, 2), (1, 2)]),
          ("C4", 4, [(0, 1), (1, 2), (2, 3), (0, 3)]), ("K4", 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])]
rng = np.random.default_rng(20261028)
rows, failures = [], []


def configs(nv, nvs, case_rng):
    s = case_rng.integers(0, 11, nvs)
    yield "diagonal", [s] * nv
    yield "off-diagonal", [case_rng.integers(0, 11, nvs) for _ in range(nv)]
    t = case_rng.integers(0, 11, nvs)
    yield "mixed", [t if v % 2 == 0 else case_rng.integers(0, 11, nvs) for v in range(nv)]


for name, gens in CASES:
    C = Case(gens, (1, 1, 2))
    nvs = len(C.low(C.VK, ("v", 0)))
    graphs = []
    for sname, nv, edges in SHAPES:
        for cname, states in configs(nv, nvs, rng):
            r = C.graph(nv, edges, states, rng); r.update({"shape": sname, "config": cname})
            graphs.append(r)
            log(name, sname, cname, json.dumps(r), f"({time.time() - T0:.0f}s)")
    ls = C.linear_structure(rng)
    log(name, "linear structure", json.dumps(ls), f"({time.time() - T0:.0f}s)")
    df = C.deficit(rng)
    log(name, "deficit", json.dumps(df), f"({time.time() - T0:.0f}s)")
    ok = (all(g["variety"] and g["affine"] for g in graphs) and all(g["A equal"] and g["b difference in column space"] and g["counts equal"] for g in graphs)
          and ls["vertex terms nonzero at zero private data (10 pairs)"] == 0 and ls["private rows nonzero at the diagonal (100)"] == 0
          and all(x["samples"] > 0 and x["not homogeneous-affine"] == 0 and x["flow not additive"] == 0 and x["flow has a slot-2-free term"] == 0 for x in ls["pairs"])
          and all(x["zero data solve"] and x["random data violating"] > 0 for x in df))
    rows.append({"case": name, "generators": gens, "graphs": graphs, "linear structure": ls, "deficit": df, "predictions hold": bool(ok)})
    if not ok: failures.append(name)

controls = []
Cc = Case([1, 1], (1, 1, 2), zero_jump=False)
cg = []
for sname, nv, edges in SHAPES[:4]:
    for cname, states in configs(nv, len(Cc.low(Cc.VK, ("v", 0))), rng):
        r = Cc.graph(nv, edges, states, rng); r.update({"shape": sname, "config": cname}); cg.append(r)
        log("X1", sname, cname, json.dumps(r), f"({time.time() - T0:.0f}s)")
m1 = all(g["A equal"] and g["b difference in column space"] for g in cg)
controls.append({"control": "X1 cumulative design (K11): count-locality must fail in some configuration", "rows": cg, "matched (locality everywhere)": m1})
C2 = Case([1, 2], (1, 2, 3))
ls2 = C2.linear_structure(rng)
log("X2", json.dumps(ls2), f"({time.time() - T0:.0f}s)")
m2 = all(x["not homogeneous-affine"] == 0 and x["flow not additive"] == 0 and x["flow has a slot-2-free term"] == 0 for x in ls2["pairs"]) and \
     ls2["private rows nonzero at the diagonal (100)"] == 0
controls.append({"control": "X2 free class 4 on (1, 2), slots (1, 2, 3) (dual slot with layer-1 data): the linear structure must fail somewhere",
                 "result": ls2, "matched (linear structure everywhere)": m2})
verdict = "invalid" if (m1 or m2) else ("supported" if not failures else "refuted")
res = {"experiment_id": "CLASS4-PAIRS-20261028-001B-E001", "verdict": verdict, "failures": failures, "controls": controls,
       "cases": len(rows), "seconds": round(time.time() - T0, 1)}
json.dump(rows, open(os.path.join(ART, "rows.json"), "w"), indent=1, default=str)
json.dump(res, open(os.path.join(ART, "result.json"), "w"), indent=1, default=str)
log("VERDICT", verdict, f"({time.time() - T0:.0f}s)")
