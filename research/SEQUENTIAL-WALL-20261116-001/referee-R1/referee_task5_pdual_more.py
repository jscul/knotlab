"""Task 5 bonus, larger samples: P_dual and min(P, P_dual) on layered circuits
(w = 1024, d = 16, 32, 64; 60 samples each), against the study's per-sample
values (data from the registered run's results.jsonl)."""

import json
import os
import sys
import time

import numpy as np
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_core as C  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUN = os.path.join(ROOT, "artifacts", "SEQUENTIAL-WALL-20261116-001A",
                   "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases", "run", "results.jsonl")


def main():
    st = {}
    for line in open(RUN):
        r = json.loads(line)
        if r["case"].startswith("circ-w1024-"):
            st.setdefault(r["case"].rsplit("-s", 1)[0], []).append(r["result"])
    out = {}
    t0 = time.time()
    for d, N in ((16, 60), (32, 60), (64, 40)):
        Pd, two = [], []
        for s in range(N):
            rng = np.random.default_rng(np.random.SeedSequence([7735, 1024, d, s]))
            inputs, layers = C.layered_circuit(1024, d, rng)
            n, A, hm = C.layered_to_atoms(inputs, layers)
            atoms = [tuple(x) for x in A.tolist()]
            unf, dph, pd = C.dual_law_py(n, atoms, np.flatnonzero(hm).tolist())
            _, _, P, _ = C.phases_np(n, A, hm)
            Pd.append(pd)
            two.append(min(P, pd))
        th = st[f"circ-w1024-d{d}"]
        thPd = [r["P_dual"] for r in th]
        thTwo = [r["two_sided"] for r in th]
        out[str(d)] = {"samples": N,
                       "P_dual_median": float(np.median(Pd)), "P_dual_hist": {str(v): int(c) for v, c in zip(*np.unique(Pd, return_counts=True))},
                       "study_P_dual": thPd, "study_P_dual_median": float(np.median(thPd)),
                       "P_dual_mannwhitney_p": float(mannwhitneyu(Pd, thPd).pvalue),
                       "two_sided_median": float(np.median(two)), "two_sided_hist": {str(v): int(c) for v, c in zip(*np.unique(two, return_counts=True))},
                       "study_two_sided": thTwo, "study_two_sided_median": float(np.median(thTwo)),
                       "two_sided_mannwhitney_p": float(mannwhitneyu(two, thTwo).pvalue)}
        print(d, out[str(d)], flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "referee_task5_pdual_more.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
