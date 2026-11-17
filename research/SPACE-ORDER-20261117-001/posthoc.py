"""Post-hoc reading (not pre-registered) for SPACE-ORDER-20261117-001.

For the two-demand law on the weave, rebuild each registered sample at k*,
take the trigger (the k*-th held distinction, whose addition sets the leap)
and compare each set distinction's phase with its steps apart from the
trigger; report P*, the largest steps apart from the trigger, the weave's
largest steps apart (2L/3), and the correlation of phase with steps.
python3 -B research/SPACE-ORDER-20261117-001/posthoc.py
"""
import importlib.util, json, os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
E = os.path.join(ROOT, "experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases")
spec = importlib.util.spec_from_file_location("so_job", os.path.join(E, "job.py"))
job = importlib.util.module_from_spec(spec); spec.loader.exec_module(job)
W, A = job.W, job.A
out = {}
for L, cnt in ((48, 6), (96, 6), (192, 4), (384, 3)):
    rows = []
    for s in range(cnt):
        n = L * L
        K, trip, _, rng = job.build("two", "W", L, s)
        order = rng.permutation(n)
        k_star, _ = job.SWjob.incremental_k_star(n, trip, order)
        p = A.Pattern(n, trip, order[:k_star])
        _, ph, P = A.untangling_phases(p)
        st = W.steps_from(K, n, [order[k_star - 1]])
        setm = ph >= 0
        far = int(st[setm].max())
        c = float(np.corrcoef(st[setm & (ph > 0)], ph[setm & (ph > 0)])[0, 1])
        slope = float(np.polyfit(st[setm & (ph > 0)], ph[setm & (ph > 0)], 1)[0])
        rows.append({"P": int(P), "far_from_trigger": far, "diameter": 2 * L // 3, "corr_phase_steps": c, "phases_per_step": slope})
    out[L] = rows
path = os.path.join(ROOT, "artifacts/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/posthoc.json")
json.dump(out, open(path, "w"), indent=1)
for L, rows in out.items():
    print(L, [(r["P"], r["far_from_trigger"], r["diameter"], round(r["corr_phase_steps"], 3), round(r["phases_per_step"], 2)) for r in rows])
