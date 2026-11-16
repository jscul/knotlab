"""Aggregate paid, paired deployment streams and the once-only official fit."""
from collections import Counter, defaultdict
import gzip
import json
from math import comb
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
E = HERE.parents[1] / "experiments" / HERE.name / (HERE.name + "-E001_rank_triples")
sys.path.insert(0, str(E))
from job import DEFAULT, METHODS, REPEATS, check_hashes, encoded, read, sha


def med_counters(runs):
    return {k:median(r.get(k, 0) for r in runs) for k in set().union(*(r.keys() for r in runs))}


def single(row, grade):
    res, cert = row["result"] or {}, row["certificate"] or {}
    exact = row["failure"] is None and cert.get("exact", False) and cert["width"] == grade["width"]
    trace, work = res.get("search_audit", {}), res.get("work", {})
    attempts = trace.get("attempts", ())
    rank = trace.get("first_minimum_rank")
    if trace:
        trials = len(attempts)
    else:
        trials = work.get("triple_trials", work.get("group_trials", 0))
    width = cert.get("width")
    c = Counter(tasks=1, exact=int(exact), width1=int(width == 1), width2=int(width == 2),
                table_rows=cert.get("verified_assignments",0), output_bits=cert.get("verified_output_bits",0),
                gates=cert.get("gates",0), shared_gates=cert.get("shared_gates",0), trials=trials,
                best_possible_trials=1 if grade["width"] == 1 else comb(row["n"],3),
                first_rank_sum=rank or 0, rank_observed=int(rank is not None), first_is_best=int(rank == 1),
                ordering_prepare_cpu_ns=trace.get("ordering_prepare_cpu_ns",0),
                ranking_cpu_ns=trace.get("ranking_cpu_ns", 0), policy_called=int(bool(trace.get("ranking_called"))), cached_proposals=sum(int(a[-1] == 0) for a in attempts),
                exact_columns_read=sum(a[5] for a in attempts), failed_bound_checks=sum(int(a[4] == 0) for a in attempts),
                chosen_planted=int(exact and sorted(res["triple"]) == sorted(grade["triple"])))
    c.update({k:row[k] for k in ("cpu_ns", "wall_ns", "init_cpu_ns", "synth_cpu_ns", "verify_cpu_ns", "verify_wall_ns", "return_bytes")})
    return c


def payment(paid_curve, bench_curve, training_cost, pair_counts):
    gaps = [a + training_cost - b for a,b in zip(paid_curve, bench_curve, strict=True)]
    # Prefix 0 is startup. Report crossings only after returning a verified rule.
    hits = [i for i in range(1, len(gaps)) if gaps[i] <= 0]
    positive = [i for i in range(1, len(gaps)) if gaps[i] > 0]
    durable = max(positive, default=0) + 1
    first = hits[0] if hits else None
    return dict(gap_ns=gaps[-1], first_break_even=first,
                first_break_even_completed_pairs=pair_counts[first] if first else None,
                sustained_break_even=durable if durable < len(gaps) else None, cumulative_gap_ns=gaps)


def assess(out):
    design, train, release = (read(out / p) for p in ("design.json","train-receipt.json","held-bound.json"))
    check_hashes(out, train["files"])
    check_hashes(out, {k:release[k] for k in ("held.json","held-grades.json","model.json","design.json","train-receipt.json")})
    if not train["frozen_utc"] < release["test_opened_utc"]:
        raise ValueError("model freeze did not precede held release")
    tasks, grades = read(out/"held.json"), read(out/"held-grades.json")
    times = defaultdict(dict)
    cells = defaultdict(list)
    totals = defaultdict(list)
    curves = defaultdict(list)
    ranks = defaultdict(list)
    identities = {}
    failures = []
    pair_counts, seen = [0], set()
    for t in tasks:
        pair = grades[t["id"]]["pair"]
        pair_counts.append(pair_counts[-1] + int(pair in seen))
        seen.add(pair)
    for line in (out/"results.jsonl").read_text().splitlines():
        event = json.loads(line)
        if event["status"] != "ok":
            raise ValueError("incomplete worker; preserve and inspect receipt " + event["case"])
        s = event["result"]
        arm, rep = s["arm"], s["repeat"]
        if s["cpu"] != design["cpu"] or rep in times[arm] or s["sha256"] != sha(out/s["file"]):
            raise ValueError("mismatched worker or receipt")
        with gzip.open(out/s["file"], "rt") as f:
            rows = [json.loads(line) for line in f]
        counters = Counter()
        by = defaultdict(Counter)
        operations = Counter()
        rank_values = defaultdict(list)
        path = [s["startup_cpu_ns"]]
        fingerprint = []
        encountered = set()
        for task,row in zip(tasks,rows,strict=True):
            if row["id"] != task["id"]:
                raise ValueError("task order changed")
            grade = grades[task["id"]]
            m = single({**row, "n":task["n"]}, grade)
            if not m["exact"]:
                failures.append([event["case"],task["id"],row["failure"]])
            counters.update(m)
            seen_output = any((task["n"], o) in encountered for o in task["outputs"])
            encountered.update((task["n"], o) for o in task["outputs"])
            res = row["result"] or {}
            for label in (grade["kind"], str(task["n"]), grade["operation"], "seen_output" if seen_output else "new_outputs",
                          grade["kind"] + ("-seen" if seen_output else "-new")):
                by[label].update(m)
            if m["rank_observed"]:
                rank_values[grade["kind"]].append(m["first_rank_sum"])
            operations.update({k:v for k,v in res.get("work",{}).items() if type(v) is int})
            for k,v in (res.get("ranking_work") or {}).items():
                if type(v) is int:
                    operations["rank_" + k] += v
            path.append(path[-1] + m["cpu_ns"])
            fingerprint.append([res.get("triple"),res.get("summary_wires"),res.get("circuit"),res.get("width")])
        ident = encoded(fingerprint)
        if arm in identities and identities[arm] != ident:
            raise ValueError("different programs in repeated deterministic deployments")
        identities[arm] = ident
        counters.update(startup_cpu_ns=s["startup_cpu_ns"], startup_wall_ns=s["startup_wall_ns"],
                        deployment_cpu_ns=path[-1], deployment_wall_ns=s["startup_wall_ns"]+counters["wall_ns"])
        times[arm][rep] = counters
        curves[arm].append(path)
        cells[arm].append(by)
        totals[arm].append(operations)
        ranks[arm].append(rank_values)
    methods, prefix = {}, {}
    for arm in METHODS:
        if set(times[arm]) != set(range(REPEATS)):
            raise ValueError("missing scheduled deployments: " + arm)
        ordered = [times[arm][i] for i in range(REPEATS)]
        m = methods[arm] = med_counters(ordered)
        m["groups"] = {k:med_counters([w[k] for w in cells[arm]]) for k in cells[arm][0]}
        m["rank_median"] = {k:median(v) for k,v in ranks[arm][0].items() if v}
        m["work"] = med_counters(totals[arm])
        m["cpu_repeats_ns"] = [w["deployment_cpu_ns"] for w in ordered]
        m["wall_repeats_ns"] = [w["deployment_wall_ns"] for w in ordered]
        m["paid_cpu_ns"] = m["deployment_cpu_ns"] + (train["cpu_ns"] if arm == "learned" else 0)
        m["paid_wall_ns"] = m["deployment_wall_ns"] + (train["wall_ns"] if arm == "learned" else 0)
        prefix[arm] = [median(v) for v in zip(*curves[arm], strict=True)]
    benchmark = min((k for k in METHODS if k != "learned"), key=lambda a:methods[a]["paid_cpu_ns"])
    learner = methods["learned"]
    comparisons = {}
    for name,m in methods.items():
        if name == "learned":
            continue
        paid_wins = sum(x + train["cpu_ns"] < y for x,y in zip(learner["cpu_repeats_ns"], m["cpu_repeats_ns"], strict=True))
        deploy_wins = sum(x < y for x,y in zip(learner["cpu_repeats_ns"], m["cpu_repeats_ns"], strict=True))
        comparisons[name] = dict(paid_cpu_gap_ns=learner["paid_cpu_ns"]-m["paid_cpu_ns"],
                paid_wall_gap_ns=learner["paid_wall_ns"]-m["paid_wall_ns"],
                paid_cpu_ratio=learner["paid_cpu_ns"]/m["paid_cpu_ns"], paid_wins=paid_wins, deployment_wins=deploy_wins,
                deployment_cpu_gap_ns=learner["deployment_cpu_ns"]-m["deployment_cpu_ns"],
                fewer_exact_trials=m["trials"]-learner["trials"])
    fees = {"fully_paid":train["cpu_ns"], "frozen_policy_available":0,
            "labelled_training_available":train["cpu_ns"]-train["phases"]["training_tasks_and_labels"]["cpu_ns"]}
    label_cost = read(out / "label-cost.json")
    if not label_cost["exact"] or label_cost["train_sha256"] != sha(out/"train.json"):
        raise ValueError("raw-table label sensitivity is unverified")
    fees["raw_training_tables_available"] = fees["labelled_training_available"] + label_cost["cpu_ns"]
    trajectory = {k:payment(prefix["learned"],prefix[benchmark],fee,pair_counts) for k,fee in fees.items()}
    gate = not failures and comparisons[benchmark]["paid_cpu_gap_ns"] < 0 and comparisons[benchmark]["paid_wins"] >= 8
    return dict(benchmark=benchmark, meets_paid_criterion=gate, train=train, sensitivity_fees=fees,
                label_sensitivity=label_cost, tasks=len(tasks), pairs=len(seen),
                repeats=REPEATS, methods=methods, comparisons=comparisons, trajectories=trajectory, failures=failures,
                observed_programs=sum(t["tasks"] for rep in times.values() for t in rep.values()),
                checked_assignments=sum(t["table_rows"] for rep in times.values() for t in rep.values()),
                checked_output_bits=sum(t["output_bits"] for rep in times.values() for t in rep.values()),
                held_sha256=sha(out/"held-bound.json"), design_sha256=sha(out/"design.json"))


if __name__ == "__main__":
    directory = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else DEFAULT
    res = assess(directory)
    (directory/"result.json").write_text(json.dumps(res, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k:res[k] for k in ("benchmark","meets_paid_criterion","tasks","pairs","observed_programs","failures")}))
