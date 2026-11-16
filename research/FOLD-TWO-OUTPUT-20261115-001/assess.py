"""Recompute widths, circuit metrics and complete paired costs from raw scientific receipts."""
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILY = HERE.name + "-E001_joint_tables"
sys.path.insert(0, str(ROOT / "experiments" / HERE.name / FAMILY))
from job import ACQUISITION, DEFAULT, METHODS, encoded, load, sha


def middle(rows):
    return {key: median([r.get(key, 0) for r in rows]) for key in set().union(*(r.keys() for r in rows))}


def measure(task, grade, row):
    result = row["result"] or {}
    verify = row["certificate"] or {}
    group = tuple(sorted(result.get("triple") or ()))
    exact = row["failure"] is None and verify.get("exact", False)
    right_width = exact and verify["width"] == grade["width"]
    return Counter(
        tasks=1, exact=int(exact), correct_width=int(right_width),
        width1=int(exact and verify["width"] == 1), width2=int(exact and verify["width"] == 2),
        classes2=int(exact and verify["classes"] == 2), classes4=int(exact and verify["classes"] == 4),
        uses_planted_group=int(exact and group == tuple(sorted(grade["triple"]))),
        table_rows=verify.get("verified_assignments", 0), output_bits=verify.get("verified_output_bits", 0),
        physical_gates=verify.get("gates", 0), shared_gates=verify.get("shared_gates", 0),
        active_gates=verify.get("active_gates", 0), shared_taps=verify.get("shared_summary_wires", 0),
        shared_intermediate_returns=int(verify.get("shared_summary_wires", 0) > 0),
        any_shared_gate_returns=int(verify.get("shared_gates", 0) > 0),
        fold_uses=result.get("fold_uses", 0), returns_using_fold=int(result.get("fold_uses", 0) > 0),
        cpu_ns=row["cpu_ns"], wall_ns=row["wall_ns"], init_cpu_ns=row["init_cpu_ns"],
        synth_cpu_ns=row["synth_cpu_ns"], verify_cpu_ns=row["verify_cpu_ns"],
        verify_wall_ns=row["verify_wall_ns"], return_bytes=row["return_bytes"])


def assess(out):
    design = load(out / "design.json")
    if any(sha(out / n) != d for n, d in design["data"].items()):
        raise ValueError("changed bound data")
    tasks = {p: load(out / (p + ".json")) for p in ("primary", "sensitivity")}
    grades = load(out / "grades.json")
    streams = defaultdict(dict)
    partition = defaultdict(list)
    ops = defaultdict(list)
    steps = defaultdict(dict)
    fingerprints, decisions = {}, {}
    failures = []
    for line in (out / "results.jsonl").read_text().splitlines():
        event = json.loads(line)
        if event["status"] != "ok":
            raise ValueError("unresolved worker failure retained in " + event["case"])
        s = event["result"]
        key = s["panel"], s["cache"], s["arm"]
        rep = s["repeat"]
        if rep in streams[key] or s["cpu"] != design["cpu"]:
            raise ValueError("duplicate or non-matching worker")
        fp = out / s["file"]
        if sha(fp) != s["sha256"]:
            raise ValueError("raw receipt changed")
        with gzip.open(fp, "rt") as data:
            rows = [json.loads(l) for l in data]
        total, work = Counter(), Counter()
        cells = defaultdict(Counter)
        paid_cumulative = [s["startup_cpu_ns"]]
        program_identity, selected = [], []
        for task, raw in zip(tasks[s["panel"]], rows, strict=True):
            if task["id"] != raw["id"]:
                raise ValueError("public order changed")
            grade = grades[s["panel"]][task["id"]]
            m = measure(task, grade, raw)
            if not (m["exact"] and m["correct_width"]):
                failures.append((event["case"], task["id"], raw["failure"]))
            total.update(m)
            for label in (str(task["n"]), grade["kind"], f"{task['n']}-{grade['kind']}"):
                cells[label].update(m)
            result = raw["result"] or {}
            work.update({k: v for k, v in result.get("work", {}).items() if type(v) in (int, float)})
            paid_cumulative.append(paid_cumulative[-1] + m["cpu_ns"])
            choice = [result.get(k) for k in ("triple", "width", "class_count")]
            selected.append(choice)
            program_identity.append([choice, result.get("circuit"), result.get("summary_wires"), m["fold_uses"]])
        if key in fingerprints and fingerprints[key] != encoded(program_identity):
            raise ValueError("different programs across repeated streams")
        fingerprints[key], decisions[key] = encoded(program_identity), selected
        total.update(startup_cpu_ns=s["startup_cpu_ns"], startup_wall_ns=s["startup_wall_ns"],
                     paid_cpu_ns=total["cpu_ns"] + s["startup_cpu_ns"],
                     paid_wall_ns=total["wall_ns"] + s["startup_wall_ns"])
        streams[key][rep] = total
        steps[key][rep] = paid_cumulative
        ops[key].append(work)
        for label, cell in cells.items():
            partition[key + (label,)].append(cell)
    methods = {}
    for panel, cache, count in (("primary", "warm", 10), ("primary", "cold", 5), ("sensitivity", "warm", 2)):
        label = f"{panel}-{cache}"
        methods[label] = {}
        for arm in METHODS:
            key = panel, cache, arm
            runs = streams[key]
            if set(runs) != set(range(count)):
                raise ValueError("incomplete run matrix for " + str(key))
            v = middle(list(runs.values()))
            v["cpu_repeats_ns"] = [runs[i]["paid_cpu_ns"] for i in range(count)]
            v["wall_repeats_ns"] = [runs[i]["paid_wall_ns"] for i in range(count)]
            v["work"] = middle(ops[key])
            v["groups"] = {k[-1]: middle(vs) for k, vs in partition.items() if k[:3] == key}
            methods[label][arm] = v
        if decisions[panel, cache, "named"] != decisions[panel, cache, "flat"]:
            raise ValueError("matched named/inline interface selection differs")
    warm = methods["primary-warm"]
    baseline = min(("reference", "dag-first", "primitive"), key=lambda a: warm[a]["paid_cpu_ns"])
    b = warm[baseline]
    comparisons = {}
    for arm, row in warm.items():
        comparisons[arm] = dict(
            cpu_saved_pct=100 * (1 - row["paid_cpu_ns"] / b["paid_cpu_ns"]),
            wall_saved_pct=100 * (1 - row["paid_wall_ns"] / b["paid_wall_ns"]),
            paired_cpu_wins=sum(x < y for x, y in zip(row["cpu_repeats_ns"], b["cpu_repeats_ns"], strict=True)),
            paired_wall_wins=sum(x < y for x, y in zip(row["wall_repeats_ns"], b["wall_repeats_ns"], strict=True)),
            lower_steady_cpu=row["cpu_ns"] < b["cpu_ns"])
    guide = comparisons["named"]
    primary_failures = [f for f in failures if f[0].startswith("primary-")]
    qualifies = (not primary_failures and warm["named"]["fold_uses"] > 0 and 10 * warm["named"]["paid_cpu_ns"] <= 9 * b["paid_cpu_ns"] and
                 guide["paired_cpu_wins"] >= 8 and guide["wall_saved_pct"] > 0 and guide["lower_steady_cpu"]
                 and comparisons["flat"]["lower_steady_cpu"])
    previous = load(ACQUISITION)
    historical = {"pool_cpu_ns": previous["cpu_ns"], "pool_wall_ns": previous["wall_ns"],
                  "historical_winner_was_supplied": False,
                  "cpu_if_charged_ns": warm["named"]["paid_cpu_ns"] + previous["cpu_ns"],
                  "wall_if_charged_ns": warm["named"]["paid_wall_ns"] + previous["wall_ns"]}
    trajectories = {}
    for a in (baseline, "named"):
        trajectories[a] = [median(x) for x in zip(*steps["primary", "warm", a].values(), strict=True)]
    gaps = [x + previous["cpu_ns"] - y for x, y in zip(trajectories["named"], trajectories[baseline], strict=True)]
    historical["first_cpu_break_even_with_pool"] = next((i for i in range(1, len(gaps)) if gaps[i] <= 0), None)
    historical["last_cpu_gap_with_pool_ns"] = gaps[-1]
    return dict(design_sha256=sha(out / "design.json"), controls=list(METHODS), benchmark=baseline,
                methods=methods, comparisons=comparisons, qualifies_for_paid_learning=qualifies,
                all_failures=failures, primary_tasks=len(tasks["primary"]), sensitivity_tasks=len(tasks["sensitivity"]),
                measured_returns=sum(r["tasks"] for by_rep in streams.values() for r in by_rep.values()),
                total_assignments=sum(r["table_rows"] for by_rep in streams.values() for r in by_rep.values()),
                total_verified_bits=sum(r["output_bits"] for by_rep in streams.values() for r in by_rep.values()),
                pool_sensitivity=historical)


if __name__ == "__main__":
    out = Path(sys.argv[1]).resolve() if sys.argv[1:] else DEFAULT
    result = assess(out)
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("primary_tasks", "sensitivity_tasks", "measured_returns", "benchmark",
                                            "all_failures", "qualifies_for_paid_learning")}, indent=2))
