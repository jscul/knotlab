"""Reconstruct exact successes and end-to-end CPU from the paid deployment receipts."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
from statistics import median

NOTES = Path(__file__).resolve().parent
TICKET = NOTES.name
ROOT = NOTES.parents[1]
BASE = ROOT / "artifacts" / TICKET / (TICKET + "-E001_shared_witnesses")
PARENT = "PARENT-FOLD-20261115-001"
OLD = ROOT / "artifacts" / PARENT / (PARENT + "-E001_consumer_edits") / "explicit-piece"


def load(path):
    return json.loads(path.read_bytes())


def ns_fields(stats):
    return {k:v for k,v in stats.items() if type(v) is int}


def summarize(directory=BASE, write=True):
    directory = directory.resolve()
    design, grades = load(directory / "design.json"), load(OLD / "grades.json")
    manifest = directory / "results.jsonl"
    cases = {}
    for raw in manifest.read_bytes().splitlines():
        obj = json.loads(raw)
        if obj["status"] != "ok" or obj["case"] in cases:
            raise ValueError("unsuccessful or duplicate benchmark stream: " + obj["case"])
        cases[obj["case"]] = obj["result"]
    samples, unique, receipts = defaultdict(dict), defaultdict(dict), []
    example_work, correct, failures = defaultdict(lambda:defaultdict(Counter)), defaultdict(Counter), []
    cur_blocks = defaultdict(list)
    for obj in cases.values():
        cur_blocks[(obj["panel"],obj["arm"])].append(obj["block"])
    for case, obj in cases.items():
        panel, arm, block = (obj[k] for k in ("panel","arm","block"))
        path = directory / obj["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != obj["sha256"]:
            raise ValueError("benchmark trace changed: "+case)
        first = block == min(cur_blocks[panel,arm])
        units = Counter(total=obj["cpu_ns"], startup=obj["startup_ns"], wall=obj["wall_ns"])
        expected = {(pid,eid) for pid,record in grades.items() for eid,v in record["edits"].items()
                    if panel == "mixed" or v["kind"] == "broken"}
        observed = set()
        with gzip.open(path, "rt") as file:
            for line in file:
                p = json.loads(line)
                pid = p["id"]
                if p["failure"]:
                    failures.append((case,pid,p["failure"]))
                for phase,v in p["phases"].items():
                    units[phase] += v
                units["seed."+str(grades[pid]["seed"])] += p["cpu_ns"]
                if first:
                    example_work[panel,arm]["original"].update(ns_fields(p["acquisition"]))
                    example_work[panel,arm]["original.checker"].update(ns_fields(p["original_check"]))
                for q in p["edits"]:
                    eid = q["id"]
                    if (pid,eid) in observed:
                        raise ValueError("duplicate edit")
                    observed.add((pid,eid))
                    grade = grades[pid]["edits"][eid]
                    role = grade["kind"]
                    ans = q["answer"]
                    if (q["failure"] or not ans or ans["width"] != grade["width"] or
                        sorted(ans["triple"]) not in grade["minimizers"] or q["check"].get("exact") is not True):
                        failures.append((case,pid,eid,q["failure"] or "incorrect width, triple or circuit"))
                    else:
                        correct[panel,arm][role] += 1
                    for phase,v in q["phases"].items():
                        units["edits."+phase] += v
                    units[role] += q["cpu_ns"]
                    units["edit_cpu"] += q["cpu_ns"]
                    if first:
                        example_work[panel,arm][role+".solver"].update(ns_fields(q["work"]))
                        example_work[panel,arm][role+".checker"].update(ns_fields(q["check"]))
                        if ans:
                            unique[panel,arm][pid,eid] = (ans["width"],tuple(ans["triple"]))
                    # Per-edit choices affect the query; separate parent acquisition and startup stay charged.
                    receipts.append(dict(panel=panel,block=block,parent=pid,edit=eid,arm=arm,cpu_ns=q["cpu_ns"]))
        if observed != expected or obj["failures"]:
            failures.append((case,"incomplete collection",len(observed),len(expected),obj["failures"]))
        samples[panel,arm][block] = dict(units)
    panels = sorted({key[0] for key in samples})
    report = dict(failures=failures, panels={}, timing_comparison="paired whole-stream CPU", source=str(directory.relative_to(ROOT)))
    for panel in panels:
        arms = [arm for p,arm in samples if p==panel]
        data = {}
        for arm in arms:
            series = samples[panel,arm]
            keys = set().union(*(row.keys() for row in series.values()))
            med = {k:median(v.get(k,0) for v in series.values())/1e6 for k in keys}
            data[arm] = dict(median_ms=med, blocks=sorted(series),
                             totals_ns=[series[k]["total"] for k in sorted(series)],
                             correct=dict(correct[panel,arm]),unique=len(unique[panel,arm]),
                             counts={k:dict(v) for k,v in example_work[panel,arm].items()})
        deterministic = [arm for arm in arms if "advice" not in design["arms"][arm]]
        ideals = [arm for arm in arms if "advice" in design["arms"][arm]]
        best = min(deterministic,key=lambda arm:data[arm]["median_ms"]["total"])
        for arm in arms:
            row = data[arm]
            bs = row["blocks"]
            if bs != data[best]["blocks"]:
                raise ValueError("paired timing blocks differ")
            delta = [(samples[panel,best][b]["total"]-samples[panel,arm][b]["total"])/1e6 for b in bs]
            row.update(paired_wins=sum(d>0 for d in delta), paired_savings_ms=delta,
                       median_paired_saving_ms=median(delta),
                       whole_median_saving_ms=data[best]["median_ms"]["total"]-row["median_ms"]["total"])
        report["panels"][panel] = dict(arms=data, fastest_deterministic=best,
                    fastest_advice=min(ideals,key=lambda arm:data[arm]["median_ms"]["total"]) if ideals else None)
    if write:
        for path,data in ((directory/"timing.json",report),(directory/"edit-times.json",receipts)):
            text=json.dumps(data,sort_keys=True,separators=(",",":"))+"\n"
            if path.exists() and path.read_text()!=text:
                raise FileExistsError(path)
            if not path.exists(): path.write_text(text)
    return report,receipts


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir",type=Path,default=BASE)
    args=parser.parse_args()
    report,_=summarize(args.dir)
    for k,rec in report["panels"].items():
        print(k,rec["fastest_deterministic"],rec["fastest_advice"],
              {s:round(v["median_ms"]["total"],2) for s,v in rec["arms"].items()})
    print("failures",len(report["failures"]))
