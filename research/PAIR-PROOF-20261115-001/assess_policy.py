"""Read the sealed held traces and compare the price of each stream including the one-time learning bill."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
from statistics import median
from itertools import accumulate

ROOT = Path(__file__).resolve().parents[2]
TICKET = "PAIR-PROOF-20261115-001"
OUT = ROOT / "artifacts" / TICKET / (TICKET + "-E002_local_policy")


def read(path):
    return json.loads(path.read_bytes())


def financials():
    training, freeze = read(OUT/"train/origin.json"), read(OUT/"freeze.json")
    blind = read(OUT/"blind/origin.json")
    completed_fit = read(OUT/"training-cost.json")
    if completed_fit["model_sha256"]!=freeze["model_sha256"] or completed_fit["child_cpu_ns"]<freeze["train_process_cpu_ns"]:
        raise ValueError("incomplete or different training debit")
    failed = read(OUT/"failed-fits.json") if (OUT/"failed-fits.json").exists() else []
    return dict(train_fixture_and_grading_ns=training["cpu_ns"], model_training_process_ns=completed_fit["cpu_ns"],
                model_fit_only_ns=freeze["fit_cpu_ns"], failed_fit_cpu_ns=sum(f["cpu_ns"] for f in failed),
                training_ns=training["cpu_ns"]+completed_fit["cpu_ns"]+sum(f["cpu_ns"] for f in failed),
                blind_fixture_and_grading_common_ns=blind["cpu_ns"])


def summary():
    bill = financials()
    grade = read(OUT/"blind/grades.json")
    design = read(OUT/"design.json")
    known = {(pid,eid):v for pid,p in grade.items() for eid,v in p["edits"].items()}
    methods = set(design["arms"])
    runs, problems = defaultdict(dict), []
    first_counts = defaultdict(lambda:defaultdict(Counter))
    for item in (OUT/"results.jsonl").read_bytes().splitlines():
        rec = json.loads(item)
        if rec["status"]!="ok":
            problems.append((rec["case"], rec["status"]))
            continue
        result = rec["result"]
        arm,panel,block = result["arm"],result["panel"],result["block"]
        if block in runs[panel,arm]:
            raise ValueError("duplicate benchmark stream")
        file = OUT/result["file"]
        if hashlib.sha256(file.read_bytes()).hexdigest()!=result["sha256"]:
            raise ValueError("changed raw stream")
        times = Counter()
        per_seed, steps, ids = Counter(), [], []
        startup,total = result["startup_ns"],result["cpu_ns"]
        times["startup"] = startup
        seed_correct, returned, probecount = Counter(), Counter(), Counter()
        with gzip.open(file,"rt") as stream:
            for line in stream:
                parent = json.loads(line)
                pid = parent["id"]
                seed = grade[pid]["seed"]
                prepared = sum(parent["phases"].values())
                times.update(parent["phases"])
                per_seed[str(seed)] += parent["cpu_ns"]
                pos = len(steps)
                if parent.get("failure"):
                    problems.append((rec["case"],pid,parent["failure"]))
                for entry in parent["edits"]:
                    eid=entry["id"]
                    target=known[pid,eid]
                    answer=entry["answer"]
                    correct = (not entry["failure"] and answer and answer["width"]==target["width"] and
                               list(sorted(answer["triple"])) in target["minimizers"] and
                               entry["check"].get("exact") is True)
                    if not correct: problems.append((rec["case"],pid,eid,entry.get("failure") or "wrong result"))
                    seed_correct[str(seed),target["kind"]]+=int(bool(correct))
                    returned[target["kind"]]+=1
                    ids.append((pid,eid))
                    steps.append(entry["cpu_ns"])
                    times.update({"edits."+k:v for k,v in entry["phases"].items()})
                    work,check=entry.get("work") or {},entry.get("check") or {}
                    if block==0:
                        for label,stat in (("solver",work),("checker",check)):
                            first_counts[panel,arm][target["kind"]+"."+label].update(
                                {k:v for k,v in stat.items() if type(v) is int and not k.endswith(("_ns","_ms"))})
                    probecount[str(seed)] += work.get("proofs_returned",0)
                if pos==len(steps):raise ValueError("no edits for parent")
                steps[pos] += prepared
                steps[-1] += parent["cpu_ns"]-prepared-sum(q["cpu_ns"] for q in parent["edits"])
        expected={k for k,v in known.items() if panel=="mixed" or v["kind"]=="broken"}
        if set(ids)!=expected or len(ids)!=len(expected):
            problems.append((rec["case"],"missing or duplicate edit"))
        steps[0] += startup
        steps[-1] += total-sum(steps)
        steps=list(accumulate(steps))
        if steps[-1]!=total or not all(a<=b for a,b in zip(steps,steps[1:])):
            raise ValueError("invalid prefix accounting")
        times["total"]=total
        runs[panel,arm][block]=dict(total=total,times=times,seeds=per_seed,prefix=steps,ids=ids,
                                    correct=seed_correct,returned=returned,proof_per_seed=probecount)
    panels={}
    for panel in ("broken","mixed"):
        arms={}
        for arm in sorted(methods):
            data=runs[panel,arm]
            if set(data)!=set(range(8)):raise ValueError(f"missing timing repeats {panel}/{arm}")
            values=list(data.values())
            times={k:median(x["times"].get(k,0) for x in values) for k in set().union(*(x["times"] for x in values))}
            sd={s:median(x["seeds"][s] for x in values) for s in values[0]["seeds"]}
            initial=data[0]
            sums={kind:sum(v for (_,k),v in initial["correct"].items() if k==kind) for kind in initial["returned"]}
            arms[arm]=dict(median_ns=times,counts=first_counts[panel,arm],seed_deployment_ns=sd,
                           correct_unique=sums,correct_by_seed={s:{k:initial["correct"][s,k] for k in sums} for s in sd},
                           proofs_by_seed=dict(initial["proof_per_seed"]),
                           whole_with_training_ns=times["total"]+(bill["training_ns"] if arm=="learned" else 0))
        control=min(methods-{"learned"},key=lambda a:arms[a]["median_ns"]["total"])
        ordinary=min(("ordinary","compact","no-proof"),key=lambda a:arms[a]["median_ns"]["total"])
        comparisons={}
        for method in sorted(methods-{"learned"}):
            gains=[];curves=[]
            for b in range(8):
                baseline,candidate=runs[panel,method][b],runs[panel,"learned"][b]
                if baseline["ids"]!=candidate["ids"]:raise ValueError("unpaired stream order")
                gains.append(baseline["total"]-candidate["total"])
                if b%2==0:  # this is the published, chronological forward stream
                    curves.append([x-y-bill["training_ns"] for x,y in zip(baseline["prefix"],candidate["prefix"])])
            forward=[median(v) for v in zip(*curves)]
            savings=median(gains)
            comparisons[method]=dict(verification_and_deployment_gains_ns=gains,median_paired_ns=savings,
                paid_paired_ns=savings-bill["training_ns"],wins_without_training=sum(v>0 for v in gains),
                wins_with_training=sum(v>bill["training_ns"] for v in gains),
                first_paid_break_even=next((i for i,v in enumerate(forward,1) if v>=0),None),
                cheapest_remaining_prefix_gap_ns=max(0,-max(forward)),
                final_forward_prefix_net_ns=forward[-1],forward_net_ns=forward)
        panels[panel]=dict(best_deployable=control,best_ordinary=ordinary,arms=arms,comparisons=comparisons)
    return dict(training_bill=bill, panels=panels, failures=problems,
                streams=sum(map(len,runs.values())), total_timed_verified_edits=sum(sum(x["correct"].values()) for ds in runs.values() for x in ds.values()),
                prefix_rule="Median cumulative baseline minus learned deployment and one full training charge, across the four matched runs in the published forward order. All eight runs contribute to paired whole-stream costs.",
                seed_rule="Medians of parent + edits for the twelve parents from each seed. Whole-stream startup, training and common harness costs are shown separately.")


if __name__=="__main__":
    report=summary()
    path=OUT/"result.json"
    data=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if path.exists() and path.read_text()!=data:raise FileExistsError(path)
    if not path.exists():path.write_text(data)
    for panel,q in report["panels"].items():
        baseline=q["best_deployable"]; v=q["comparisons"][baseline]
        print(panel,baseline, v["median_paired_ns"]/1e6,v["paid_paired_ns"]/1e6,v["first_paid_break_even"])
    print("Total training seconds",report["training_bill"]["training_ns"]/1e9,"failures",len(report["failures"]))
