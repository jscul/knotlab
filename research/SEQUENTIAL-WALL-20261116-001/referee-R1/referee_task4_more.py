"""Task 4, larger samples: 100 circuits per family, to judge whether the
study's medians (10 samples) sit inside the sampling spread.  Compares the
referee's per-sample largest sigma with the study's per-sample values (data
read from the registered run's results.jsonl) by Mann-Whitney and by the
spread of medians of 10 resampled from the referee's 100.
"""

import json
import os
import sys
import time

import numpy as np
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_core as C  # noqa: E402
from referee_task4_circuits import measure  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUN = os.path.join(ROOT, "artifacts", "SEQUENTIAL-WALL-20261116-001A",
                   "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases", "run", "results.jsonl")
N = 100


def study_values():
    d = {}
    with open(RUN) as fh:
        for line in fh:
            r = json.loads(line)
            c = r["case"]
            if c.startswith(("circ-", "unl-")) and r["status"] == "ok":
                d.setdefault(c.rsplit("-s", 1)[0], []).append(r["result"])
    return d


def summarize(ours, theirs, rng):
    ours = np.array(ours, float)
    theirs = np.array([x for x in theirs], float)
    meds10 = np.median(rng.choice(ours, size=(20000, 10), replace=True), axis=1)
    vals, cnt = np.unique(meds10, return_counts=True)
    return {"ours_n": len(ours), "ours_median": float(np.median(ours)),
            "ours_hist": {str(int(v) if v == int(v) else v): int(c) for v, c in zip(*np.unique(ours, return_counts=True))},
            "study_values": theirs.tolist(), "study_median": float(np.median(theirs)),
            "mannwhitney_p": float(mannwhitneyu(ours, theirs, alternative="two-sided").pvalue),
            "median_of_10_distribution": {str(v): round(c / 20000, 3) for v, c in zip(vals, cnt)}}


def main():
    t0 = time.time()
    rng0 = np.random.default_rng(5)
    st = study_values()
    out = {"layered": {}, "unlayered": {}}
    for w in (256, 1024):
        for d in (8, 16, 32, 64):
            sig, P, ok = [], [], True
            for s in range(N):
                rng = np.random.default_rng(np.random.SeedSequence([7733, 1, w, d, s]))
                inputs, layers = C.layered_circuit(w, d, rng)
                n, A, hm = C.layered_to_atoms(inputs, layers)
                r = measure(n, A, hm, 1 + d * w + np.arange(w))
                ok &= r["sigma_equals_phase"]
                if r["out_true"] > 0:
                    sig.append(r["out_max_sigma"])
                P.append(r["P"])
            key = f"w{w}-d{d}"
            th = [r["out_max_rank"] for r in st["circ-" + key] if r["out_true"] > 0]
            out["layered"][key] = summarize(sig, th, rng0)
            out["layered"][key]["alive"] = len(sig)
            out["layered"][key]["sigma_equals_phase_all"] = bool(ok)
            out["layered"][key]["P"] = summarize(P, [r["P"] for r in st["circ-" + key]], rng0)
            print(key, {k: v for k, v in out["layered"][key].items() if k != "P"}, flush=True)
    for g in (1024, 4096):
        sig, ok = [], True
        for s in range(N):
            rng = np.random.default_rng(np.random.SeedSequence([7733, 2, g, s]))
            inputs, gates = C.unlayered_circuit(256, g, rng)
            n, A, hm = C.unlayered_to_atoms(inputs, gates)
            r = measure(n, A, hm, 1 + 256 + np.arange(g))
            ok &= r["sigma_equals_phase"]
            sig.append(r["out_max_sigma"])
        th = [r["out_max_rank"] for r in st[f"unl-g{g}"]]
        out["unlayered"][str(g)] = summarize(sig, th, rng0)
        out["unlayered"][str(g)]["sigma_equals_phase_all"] = bool(ok)
        print(g, out["unlayered"][str(g)], flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "referee_task4_more.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
