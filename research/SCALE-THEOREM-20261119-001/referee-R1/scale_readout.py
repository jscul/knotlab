"""Read-out of runs/referee-scale-theorem (job_scale.py) into referee_scale_theorem.json: the study's table recomputed from the
referee's own classes and readings (labelled shares, as the note gives them, and shares weighted to distinct arrangements by the
recorded |Aut| / n!), agreement with SCALE-THEOREM's and SCALE-SHARE's per-sample records, and the regrowth.

  .venv/bin/python -B research/SCALE-THEOREM-20261119-001/referee-R1/scale_readout.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SS = ROOT / "artifacts/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/results.json"
LABEL = {"0": "closes", "exp": "exponential"}


def main():
    by = defaultdict(list)
    reg = defaultdict(list)
    closing = Counter()
    expo = []
    for line in open(ROOT / "runs/referee-scale-theorem/results.jsonl"):
        r = json.loads(line)
        assert r["status"] == "ok"
        n = int(r["case"][3:5])
        by[n] += r["result"]["rows"]
        reg[n] += r["result"]["regrown"]
        for i, c, counts in r["result"]["one loose or none"]:
            closing[(c, counts[1] == "closed" or (len(counts) > 2 and counts[2] == "closed" and counts[1] in (0, 1)))] += 1
        expo += [[r["case"]] + x[:2] for x in r["result"]["exponential"]]
    ss = json.loads(SS.read_text())["shares"]
    out = {"by size": {}, "agreement": Counter(), "one loose or none, closes at round 1": {str(k): v for k, v in closing.items()},
           "exponential in the class, counts to round 12": expo}
    A = out["agreement"]
    for n in sorted(by):
        rows = by[n]
        s = Counter()
        w = Counter()
        for i, c, D, mech, th, pr, why, ssc, integ, wt, opk in rows:
            A["integrity (m, open per knot) holds"] += integ
            A["samples"] += 1
            mine = "stall" if c == "stall" else ("out" if c.startswith("out") else "in")
            A["class equals the study's theorem class"] += mine == th
            A["stall equals SCALE-SHARE's stall"] += (c == "stall") == (ssc == "stall")
            lab = None if D is None else LABEL.get(D, f"dimension {D}")
            if mine == "in":
                A["in the class"] += 1
                A["prediction equals the study's"] += lab == pr
                A["mechanism equals the study's"] += (mech or None) == (why if pr == "dimension 2" else None) or pr != "dimension 2"
                base = ssc.split(" [")[0]
                A["prediction equals the cluster rule, labels as recorded"] += lab == ssc
                A["prediction equals the cluster rule, 'exponential' read as 'ring (exponential)'"] += \
                    (lab == "exponential" and base == "ring (exponential)") or lab == ssc
                if lab != ssc:
                    A[f"differs from the cluster rule: {lab} / {ssc}"] += 1
            for key in ([c] if mine != "in" else ["in", f"in: {c}", f"in: {lab}"] + ([f"in: dim 2 by {mech}"] if D == "2" else [])):
                s[key] += 1
                w[key] += wt
            s[f"cluster: {mine}: {ssc}"] += 1
            s["opk sum"] += opk
        ns = len(rows) - s["stall"]
        grow = s["in"] - s["in: closes"]
        nsw = sum(x[9] for x in rows if x[1] != "stall")
        growth_w = w["in"] - w["in: closes"]
        lab_ss = ss[str(n)]["labelled"]
        g_ss = {k: v for k, v in lab_ss.items() if k not in ("stall", "closes", "out of scope")}
        d3 = sum(v for k, v in s.items() if k.startswith("in: dimension ") and int(k.split()[-1]) >= 3)
        out["by size"][n] = {
            "samples": len(rows), "non-stalling": ns, "in the class": s["in"],
            "in, share of non-stalling": round(s["in"] / ns, 4),
            "out (S3) / (S4), share of non-stalling": [round(s["out (S3)"] / ns, 4), round(s["out (S4)"] / ns, 4)],
            "in the class: closes / dim 1 / dim 2 / exp, share of the class": [round(s[f"in: {k}"] / s["in"], 4) for k in
                                                                                ("closes", "dimension 1", "dimension 2", "exponential")],
            "in the class: one loose / none": [s["in: one loose"], s["in: none"]],
            "growers in the class": grow, "dimension 3 or more in the class": d3,
            "dim 2 among the class's growers": round(s["in: dimension 2"] / grow, 4),
            "dim 2 mechanism (relay / two chains / both), share of dim 2": [
                round(s[f"in: dim 2 by {k}"] / s["in: dimension 2"], 4) for k in ("relay", "two chains", "relay and two chains")],
            "SCALE-SHARE, dim 2 among all growers (labelled)": round(g_ss.get("dimension 2", 0) / sum(g_ss.values()), 4),
            "weighted to distinct arrangements: in, share of non-stalling": round(w["in"] / nsw, 4),
            "weighted: dim 2 among the class's growers": round(w["in: dimension 2"] / growth_w, 4) if growth_w else None,
            "dimension 3 and 4 samples (cluster rule): inside / outside the class": [
                sum(v for k, v in s.items() if k.startswith("cluster: in: dimension ") and int(k.split()[-1][0]) >= 3),
                sum(v for k, v in s.items() if k.startswith("cluster: out: dimension ") and int(k.split()[-1][0]) >= 3)],
            "mean open places per knot / sqrt(5/n)": [round(s["opk sum"] / len(rows), 4), round((5 / n) ** 0.5, 4)],
            "regrown (agree / total)": [sum(x[2] for x in reg[n]), len(reg[n])],
        }
    out["agreement"] = dict(A)
    (HERE / "referee_scale_theorem.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["agreement"], indent=1))
    print(json.dumps(out["one loose or none, closes at round 1"]))
    for n, b in out["by size"].items():
        print(n, json.dumps(b))
    for e in expo:
        print(e)


if __name__ == "__main__":
    main()
