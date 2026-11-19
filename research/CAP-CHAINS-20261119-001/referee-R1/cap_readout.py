"""Read-out of the referee's CAP-CHAINS runs (job_cap.py) into referee_cap.json:
runs/referee-cap1 (C, G), runs/referee-cap2 (F), runs/referee-cap4 (A, every graph to 13 knots), runs/referee-cap6 (X, with dead
knots too).

  .venv/bin/python -B research/CAP-CHAINS-20261119-001/referee-R1/cap_readout.py
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(run):
    out = {}
    for line in open(ROOT / "runs" / run / "results.jsonl"):
        r = json.loads(line)
        if r["status"] == "ok":
            out[r["case"]] = r["result"]
    return out


def main():
    c1, c2, c4, c6 = load("referee-cap1"), load("referee-cap2"), load("referee-cap4"), load("referee-cap6")
    A = Counter()
    by_n = {}
    for cid, res in c4.items():
        n = int(cid[2:4])
        row = by_n.setdefault(n, Counter())
        for k, v in res.items():
            A[k] += v
            row[k] += v
    small = Counter()
    for n, row in by_n.items():
        if n <= 12:
            small["assignments, to 12 knots"] += row["assignments"]
        if 2 <= n <= 9:
            for k, v in row.items():
                if k.startswith("simple"):
                    small[f"{k}, 2 to 9 knots"] += v
    fam = {}
    for k, v in c2["F"].items():
        fam[k] = {x: v.get(x) for x in ("knots", "largest knot", "dead knots", "class", "reading", "most rays in a piece",
                                         "rays per piece", "agrees with the relayed model to round 8",
                                         "light engine equals the GF(2) engine to round 6", "recurrence", "counts")}
    out = {"G (graphs)": {k: v for k, v in c1["G"].items() if k != "edge lists"}, "C (six-cycles)": c1["C"],
           "X (census)": c6["X"], "A (assignments and simple starts), totals": dict(A),
           "A, the study's ranges": dict(small), "A by knots": {n: dict(r) for n, r in sorted(by_n.items())}, "F (families)": fam}
    (HERE / "referee_cap.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("A by knots", "F (families)")}, indent=1))


if __name__ == "__main__":
    main()
