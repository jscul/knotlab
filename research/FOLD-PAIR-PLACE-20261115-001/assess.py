"""Reconstruct paid search comparisons for a pair-first locator and its atomic control."""
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILY = HERE.name + "-E001_pair_first"
DEFAULT = ROOT / "artifacts" / HERE.name / FAMILY
sys.path.insert(0, str(ROOT / "experiments" / HERE.name / FAMILY))
from job import METHODS, read, sha


def summarize(rows):
    return {k: median([r.get(k, 0) for r in rows]) for k in set().union(*(r.keys() for r in rows))}


def score(out):
    design = read(out / "design.json")
    if any(sha(out / name) != wanted for name, wanted in design["data"].items()):
        raise ValueError("bound dataset changed")
    tasks = read(out / "panel.json")
    grades = read(out / "grades.json")
    streams, logical = defaultdict(dict), defaultdict(dict)
    work_sums, cell_sums = defaultdict(list), defaultdict(list)
    errors = []
    pin = set()
    for line in (out / "results.jsonl").read_text().splitlines():
        receipt = json.loads(line)
        if receipt["status"] != "ok":
            raise RuntimeError(f"unresolved runner failure: {receipt['case']}")
        run = receipt["result"]
        method, cache, rep = run["method"], run["cache"], run["repeat"]
        pin.add(run["affinity"])
        source = out / run["file"]
        if sha(source) != run["sha256"] or rep in streams[cache, method]:
            raise ValueError("invalid or duplicate receipt")
        with gzip.open(source, "rt") as f:
            rows = [json.loads(s) for s in f]
        counts, costs = Counter(), Counter()
        cells = defaultdict(Counter)
        decisions = []
        for task, row in zip(tasks, rows, strict=True):
            if row["id"] != task["id"]:
                raise ValueError("public input sequence changed")
            result = row["result"]
            exact = result["status"] == "exact" and result["truth"] == task["truth"] and result["circuit"] is not None
            if not exact:
                errors.append((rep, cache, method, row["id"]))
            work = result.get("work", {})
            timing = result.get("timing", {})
            hist = result.get("template_computed_arg_histogram", [0, 0, 0, 0])
            counts.update(work)
            item = dict(tasks=1, exact=int(exact), cpu_ns=row["cpu_ns"], wall_ns=row["wall_ns"],
                        search_cpu_ns=timing.get("search_cpu_ns", 0),
                        verify_ns=round(timing.get("verification_seconds", 0) * 1e9),
                        build_ns=round(timing.get("build_seconds", 0) * 1e9),
                        template_uses=result.get("template_uses", 0), nands=result.get("expanded_NANDs") or 0,
                        uses_two_or_more=sum(hist[2:]), verified_rows=work.get("verification_rows", 0))
            costs.update(item)
            grade = grades[row["id"]]
            for key in (str(grade["depth"]), grade["kind"], f"{grade['depth']}-{grade['kind']}"):
                cells[key].update(item)
            test_keys = [k for k in work if k in ("binary_placement_trials", "ternary_placement_tests",
                         "placement_group_trials", "placement_group_failures") or
                         (("pair" in k or "extension" in k) and k.endswith(("_trials", "_failures")))]
            decisions.append((tuple((k, work[k]) for k in sorted(test_keys)), item["template_uses"], tuple(hist)))
        costs.update(startup_ns=run["startup_ns"], startup_cpu_ns=run["startup_cpu_ns"],
                     paid_ns=run["startup_ns"] + costs["wall_ns"],
                     paid_cpu_ns=run["startup_cpu_ns"] + costs["cpu_ns"])
        streams[cache, method][rep] = costs
        logical[cache, method][rep] = decisions
        work_sums[cache, method].append(counts)
        for k, value in cells.items():
            cell_sums[cache, method, k].append(value)
    if len(pin) != 1:
        raise ValueError("worker affinity varied between methods")
    methods = {"cold": {}, "warm": {}}
    for cache, n in (("warm", 8), ("cold", 2)):
        for method in METHODS:
            all_rows = streams[cache, method]
            if set(all_rows) != set(range(n)) or len(work_sums[cache, method]) != n:
                raise ValueError("missing or duplicate method stream")
            if any(logical[cache, method][i] != logical[cache, method][0] for i in range(n)):
                raise ValueError("repeated search changed choices")
            if method.endswith("-named") and logical[cache, method] != logical[cache, method.replace("-named", "-flat")]:
                raise ValueError("equal-information named and inlined search differed")
            summary = summarize(list(all_rows.values()))
            summary["paid_cpu_repeats_ns"] = [all_rows[i]["paid_cpu_ns"] for i in range(n)]
            summary["paid_wall_repeats_ns"] = [all_rows[i]["paid_ns"] for i in range(n)]
            summary["work"] = summarize(work_sums[cache, method])
            summary["cells"] = {k: summarize(v) for (cc, mm, k), v in cell_sums.items() if cc == cache and mm == method}
            methods[cache][method] = summary
    warm = methods["warm"]
    primitive = min(("reference-primitive", "triple-primitive", "atomic-primitive"), key=lambda m: warm[m]["paid_cpu_ns"])
    b = warm[primitive]
    comparisons = {}
    for m, v in warm.items():
        pct = 100 * (1 - v["paid_cpu_ns"] / b["paid_cpu_ns"])
        cpu_wins = sum(x < y for x, y in zip(v["paid_cpu_repeats_ns"], b["paid_cpu_repeats_ns"], strict=True))
        wall_wins = sum(x < y for x, y in zip(v["paid_wall_repeats_ns"], b["paid_wall_repeats_ns"], strict=True))
        comparisons[m] = dict(percent_cpu_saved=pct, paired_cpu_wins=cpu_wins, paired_wall_wins=wall_wins,
                              lower_wall=v["paid_ns"] < b["paid_ns"], lower_marginal_cpu=v["cpu_ns"] < b["cpu_ns"])
    g = comparisons["guided-named"]
    passed = (not errors and g["percent_cpu_saved"] >= 10 and g["paired_cpu_wins"] >= 6 and g["lower_wall"]
              and g["lower_marginal_cpu"] and comparisons["guided-flat"]["lower_marginal_cpu"])
    return dict(tasks=len(tasks), measured_returns=sum(v["tasks"] for s in streams.values() for v in s.values()),
                affinity=next(iter(pin)), failures=errors, benchmark=primitive, fold_gate=passed,
                comparisons=comparisons, methods=methods, design_sha256=sha(out / "design.json"))


if __name__ == "__main__":
    out = Path(sys.argv[1]).resolve() if sys.argv[1:] else DEFAULT
    result = score(out)
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("tasks", "measured_returns", "benchmark", "fold_gate")}, indent=2))
