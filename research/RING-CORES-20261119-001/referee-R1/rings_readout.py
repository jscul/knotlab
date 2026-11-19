"""Read-out of runs/referee-rings (job_rings.py) into referee_rings.json.

  .venv/bin/python -B research/RING-CORES-20261119-001/referee-R1/rings_readout.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    R = {}
    for line in open(ROOT / "runs/referee-rings/results.jsonl"):
        r = json.loads(line)
        assert r["status"] == "ok", (r["case"], r["error"])
        R[r["case"]] = r["result"]
    W = defaultdict(Counter)
    maxrate = {}
    fails = []
    for cid, res in R.items():
        if cid.startswith("W-"):
            L = int(cid[2:4])
            for k, v in res["counts"].items():
                if k == "words":
                    W[L][k] = v
                else:
                    W[L][k] += v
            maxrate[L] = max(maxrate.get(L, 0), res["max rate"] or 0)
            fails += res["failures"]
    S = Counter()
    bad = []
    for cid, res in R.items():
        if cid.startswith("S-"):
            for k, v in res["counts"].items():
                S[k] += v
            bad += res["bad"]
    tot = Counter()
    for L, c in W.items():
        for k, v in c.items():
            tot[k] += v
    out = {"words by length": {L: dict(c) for L, c in sorted(W.items())}, "words, totals": dict(tot),
           "fastest rate by length": dict(sorted(maxrate.items())), "word failures": fails,
           "G (completeness)": R["G"], "S (small starts, grown)": dict(S), "S failures": bad, "C (census, within five places)": R["C"]}
    (HERE / "referee_rings.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "words by length"}, indent=1)[:5000])


if __name__ == "__main__":
    main()
