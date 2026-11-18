"""Merge NAE-METRIC-B1 and score P1-P7.   .venv/bin/python -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[3] / "artifacts/NAE-METRIC-20261118-001B/NAE-METRIC-20261118-001B-E001_blocks"


def main(rundir):
    res = {}
    for line in open(Path(rundir) / "results.jsonl"):
        r = json.loads(line)
        res[r["case"]] = r
    failed = sorted(c for c, r in res.items() if r["status"] != "ok")
    ok = {c: r["result"] for c, r in res.items() if r["status"] == "ok"}
    pick = lambda pre: {c: v for c, v in ok.items() if c.startswith(pre)}
    cut = pick("cut-")
    cuts = {k: sum(v[k] for v in cut.values()) for k in ("bases", "sep_triples", "additivity_fail", "formula_fail", "metric_mismatch",
                                                        "count_checked", "count_fail")}
    cuts["by_family"] = {}
    for v in cut.values():
        f = cuts["by_family"].setdefault(v["family"], [0, 0, 0])
        f[0] += v["bases"]; f[1] += v["sep_triples"]; f[2] += v["additivity_fail"]
    cuts["examples"] = [e for v in cut.values() for e in v["examples"]][:3]
    rings = {c: v for c, v in pick("ring-").items()}
    ring_ok = all(v["n_off"] == 0 and v["violations"] == 0 and v["bonds_missing_a_third"] == v["m"] * (v["m"] - 1)
                  and v["max_b"] == v["m"] // 2 + 2 and (v["other_bonds_min_size"] is None or v["other_bonds_min_size"] >= v["m"] + 1)
                  for v in rings.values())
    cac = pick("cactus-")
    cactus = {k: sum(v[k] for v in cac.values()) for k in ("bases", "off", "violations")}
    blk = {}
    for c, v in pick("block-").items():
        key = f"n{v['n']}-k{v['k']}"
        b = blk.setdefault(key, {"blocks": 0, "failing": 0, "failing_without_double": 0, "graphlike_failing": 0, "examples": []})
        for k in ("blocks", "failing", "failing_without_double", "graphlike_failing"):
            b[k] += v[k]
        b["examples"] = (b["examples"] + v["examples"])[:2]
    cblk = {f"n{v['n']}-k{v['k']}": {k: v[k] for k in ("blocks", "failing", "failing_without_double", "linear_failing", "examples")}
            for c, v in pick("classblock-").items()}
    rows = [r for v in pick("graph-").values() for r in v["rows"]]
    graph = {}
    for r in rows:
        key = f"{'twisted' if r['twisted'] else 'plain'}|{'series-parallel' if r['series_parallel'] else 'K4 minor'}"
        g = graph.setdefault(key, [0, 0])
        g[0] += 1; g[1] += r["fails"]
    graph_fail_examples = [r for r in rows if r["fails"]][:4]
    sp9 = pick("sparse9-")
    sparse = {k: sum(v[k] for v in sp9.values()) for k in ("bases", "failing", "spanning_violations", "metric_mismatch")}
    gr = {**pick("grown-"), **pick("knotgrown-")}
    grown = {"cases": len(gr), "runs": sum(v["runs"] for v in gr.values()), "steps": sum(v["steps"] for v in gr.values()),
             "max_b": max((v["max_b"] for v in gr.values()), default=None), "brute_checked": sum(v["brute_checked"] for v in gr.values()),
             "brute_mismatch": sum(v["brute_mismatch"] for v in gr.values())}
    pred = {
        "P1": cuts["sep_triples"] > 0 and cuts["additivity_fail"] == 0,
        "P1b": cuts["count_checked"] > 0 and cuts["count_fail"] == 0,
        "P2": cuts["formula_fail"] == 0 and cuts["metric_mismatch"] == 0 and sparse["metric_mismatch"] == 0 and sparse["spanning_violations"] == 0,
        "P3": len(rings) == 14 and ring_ok,
        "P4": cactus["bases"] > 0 and cactus["off"] == 0 and cactus["violations"] == 0,
        "P5": sum(b["blocks"] for b in blk.values()) > 0 and sum(b["failing_without_double"] for b in blk.values()) == 0,
        "P6": graph.get("plain|series-parallel", [0, 0])[0] > 0 and graph.get("plain|series-parallel", [0, 1])[1] == 0,
        "P7": grown["steps"] > 0 and grown["max_b"] <= 2 and grown["brute_checked"] > 0 and grown["brute_mismatch"] == 0,
    }
    out = {"failed_cases": failed, "cases": len(res), "cuts": cuts, "rings": rings, "cactus": cactus, "blocks": blk, "class_blocks": cblk,
           "graph_like": graph, "graph_fail_examples": graph_fail_examples, "sparse9": sparse, "grown": grown,
           "predictions": {k: ("held" if v else "failed") for k, v in pred.items()}}
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "results.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("failed_cases", "cases", "predictions")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
