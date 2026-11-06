"""CLASS4-LOCALITY-20261028-001A-E001: class-4 gadget equations are exactly local in intrinsic layer-3 coordinates (frozen contract:
contract.json).  Cases: free class 4 on (1, 1), (0, 1, 1), (1, 1, 1) at d = 5, p = 11, slots (1, 1, 2).  Controls: two edges that are
not clean modulo gamma_4 (free class 4 on (0, 1, 2), edge (1, 2); free class 4 on (1, 2), edge (2, 1)).
Run: python3 -B run.py  (writes the artifact directory)"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from l4_lib import *  # noqa: E402
T0 = time.time()
ART = os.path.join(ROOT, "artifacts", "CLASS4-LOCALITY-20261028-001A", os.path.basename(HERE))
os.makedirs(ART, exist_ok=True)
LOG = open(os.path.join(ART, "run_log.txt"), "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


CASES = [("K11", [1, 1]), ("K011", [0, 1, 1]), ("K111", [1, 1, 1])]
SHAPES = [("P3", 3, [(0, 1), (1, 2)]), ("skip", 3, [(0, 2)]), ("star", 4, [(0, 1), (0, 2), (0, 3)]),
          ("triangle", 3, [(0, 1), (0, 2), (1, 2)]), ("P3 reversed", 3, [(0, 2), (1, 2)]),
          ("C4", 4, [(0, 1), (1, 2), (2, 3), (0, 3)]), ("K4", 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])]
CONFIGS = ("diagonal", "off-diagonal", "mixed", "parallel")
rng = np.random.default_rng(20261029)


def states_for(cname, nv, nvs, r):
    s = r.integers(0, 11, nvs)
    if cname == "diagonal": return [s] * nv
    if cname == "off-diagonal": return [r.integers(0, 11, nvs) for _ in range(nv)]
    if cname == "mixed": return [s if v % 2 == 0 else r.integers(0, 11, nvs) for v in range(nv)]
    w = r.integers(1, 11, nvs)
    lam = r.permutation(np.arange(1, 11))[:nv]
    return [(int(l) * w) % 11 for l in lam]


rows, failures = [], []
for name, gens in CASES:
    C = IntrinsicCase(gens, (1, 1, 2))
    nvs = len(C.low(C.VK, ("v", 0)))
    graphs = []
    for sname, nv, edges in SHAPES:
        for cname in CONFIGS:
            r = C.graph_int(nv, edges, states_for(cname, nv, nvs, rng), rng, prefer_slot1=(cname == "parallel"))
            r.update({"shape": sname, "config": cname}); graphs.append(r)
            log(name, sname, cname, json.dumps(r), f"({time.time() - T0:.0f}s)")
    pred = {"P1 variety and affine everywhere": all(g["variety"] and g["affine"] for g in graphs),
            "P2 linear parts equal everywhere": all(g["A equal"] for g in graphs),
            "P3 intrinsic constant parts equal everywhere": all(g["intrinsic constant parts equal"] for g in graphs),
            "P4 raw constant parts differ somewhere": any(not g["raw constant parts equal"] for g in graphs),
            "P5 slot-1 data off the diagonal in some parallel configuration": any(g["slot-1 data off the diagonal"] for g in graphs if g["config"] == "parallel")}
    ok = all(pred.values())
    if not ok: failures.append({"case": name, "failed": [k for k, v in pred.items() if not v]})
    rows.append({"case": name, "generators": gens, "graphs": graphs, "predictions": pred, "predictions hold": bool(ok)})
    log(name, "predictions", json.dumps(pred), f"({time.time() - T0:.0f}s)")

controls = []
for cname_, gens, slots in (("XA free class 4 on (0, 1, 2), edge (1, 2)", [0, 1, 2], (1, 2, 3)),
                            ("XB free class 4 on (1, 2), edge (2, 1)", [1, 2], (2, 1, 3))):
    Cc = IntrinsicCase(gens, slots)
    nvs = len(Cc.low(Cc.VK, ("v", 0)))
    cg = []
    for sname, nv, edges in SHAPES[:5]:
        for cname in CONFIGS[:3]:
            r = Cc.graph_int(nv, edges, states_for(cname, nv, nvs, rng), rng)
            r.update({"shape": sname, "config": cname}); cg.append(r)
            log(cname_[:2], sname, cname, json.dumps(r), f"({time.time() - T0:.0f}s)")
    on_var = [g for g in cg if g["variety"] and g["affine"]]
    matched = all(g["A equal"] and g["intrinsic constant parts equal"] for g in on_var)
    controls.append({"control": cname_ + ": intrinsic equality must fail in some configuration on the variety", "rows": cg,
                     "configurations on the variety": len(on_var), "matched (intrinsic equality everywhere on the variety)": bool(matched)})
verdict = "invalid" if any(c["matched (intrinsic equality everywhere on the variety)"] or c["configurations on the variety"] == 0 for c in controls) \
    else ("supported" if not failures else "refuted")
res = {"experiment_id": "CLASS4-LOCALITY-20261028-001A-E001", "verdict": verdict, "failures": failures,
       "controls": [{k: v for k, v in c.items() if k != "rows"} for c in controls], "cases": len(rows), "seconds": round(time.time() - T0, 1)}
json.dump(rows + [{"controls": controls}], open(os.path.join(ART, "rows.json"), "w"), indent=1)
json.dump(res, open(os.path.join(ART, "result.json"), "w"), indent=1)
log("VERDICT", verdict, f"({time.time() - T0:.0f}s)")
