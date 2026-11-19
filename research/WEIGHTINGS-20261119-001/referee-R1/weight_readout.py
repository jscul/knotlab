"""Read-out of runs/referee-weightings (job_weight.py) into referee_weightings.json.

  .venv/bin/python -B research/WEIGHTINGS-20261119-001/referee-R1/weight_readout.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    R = {}
    for line in open(ROOT / "runs/referee-weightings/results.jsonl"):
        r = json.loads(line)
        assert r["status"] == "ok", (r["case"], r["error"])
        R[r["case"]] = r["result"]
    W = Counter()
    by_kind = defaultdict(Counter)
    dis = []
    for cid, res in R.items():
        if not cid.startswith("W-"):
            continue
        kind = cid[2:].rsplit("-n", 1)[0]
        for k, v in res["counts"].items():
            W[k] += v
            by_kind[kind][k] += v
        W["samples"] += 2000
        by_kind[kind]["samples"] += 2000
        dis += res["disagreements"]
    L = Counter()
    for cid, res in R.items():
        if cid.startswith("L-"):
            for k, v in res["counts"].items():
                L[k] += v
    out = {"samples (W)": dict(W), "by weighting": {k: dict(v) for k, v in by_kind.items()}, "regrowth disagreements": dis,
           "configuration sampler (C)": {c: R[c] for c in ("C-3", "C-4") if c in R},
           "tree sampler (T)": {c: R[c] for c in ("T-5", "T-6") if c in R},
           "dead hub (H)": R.get("H"), "five-place lemma, trees of 3 to 18 knots (L)": dict(L)}
    (HERE / "referee_weightings.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "by weighting"}, indent=1)[:6000])


if __name__ == "__main__":
    main()
