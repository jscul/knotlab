"""Recover charged CPU, exact widths and paid phase/work counts from the recorded returns."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import argparse
from pathlib import Path
from statistics import median

NOTES = Path(__file__).resolve().parent
TICKET = NOTES.name
OUT = NOTES.parents[1] / "artifacts" / TICKET / (TICKET + "-E001_consumer_edits")
ARMS = ("ordinary", "ordinary-prior", "ordinary-hint", "fold", "ordinary-exact", "ordinary-exact-hint")


def object_at(path):
    return json.loads(path.read_bytes())


def numbers(values):
    return {k:v for k, v in values.items() if type(v) in (int, float)}


def main(artifact_dir=OUT):
    OUT = artifact_dir
    public = {p["id"]:p for p in object_at(OUT / "public.json")}
    grades = object_at(OUT / "grades.json")
    records, failures = {}, []
    for path in (OUT / "results.jsonl", OUT / "extra" / "results.jsonl"):
        if path.is_file():
            for line in path.read_bytes().splitlines():
                row = json.loads(line)
                if row["status"] != "ok":
                    failures.append([row["case"], row["status"], row["error"]])
                else:
                    info = row["result"]
                    records[info["arm"], info["repeat"]] = info
    blocks = sorted({block for _, block in records})
    if len(blocks) not in (8, 16) or len(records) != len(ARMS) * len(blocks):
        raise ValueError("timing blocks incomplete")
    work = {arm:defaultdict(Counter) for arm in ARMS}
    performance = {arm:defaultdict(list) for arm in ARMS}
    correct = {arm:Counter() for arm in ARMS}
    produced = {arm:Counter() for arm in ARMS}
    for (arm, block), rec in records.items():
        path = OUT / rec["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != rec["sha256"]:
            raise ValueError("changed trace: " + path.name)
        costs = Counter(startup=rec["startup_ns"], total=rec["cpu_ns"], wall=rec["wall_ns"])
        seen = set()
        with gzip.open(path, "rt") as file:
            for line in file:
                parent = json.loads(line)
                pid = parent["id"]
                grade, case = grades[pid], public[pid]
                if pid in seen or parent["failure"]:
                    failures.append([arm,block,pid,parent["failure"] or "duplicate parent"])
                seen.add(pid)
                costs["history"] += parent["setup_ns"]
                costs["producer history"] += parent["history"].get("producer_ns",0)
                costs["checker history"] += parent["history"].get("checker_ns",0)
                costs[f"seed {grade['seed']}"] += parent["cpu_ns"]
                costs[f"m={len(case['frontier'])}"] += parent["cpu_ns"]
                prior = parent["prior"]
                if prior:
                    costs["prior purchase"] += prior["cpu_ns"]
                    if prior["failure"] or prior["answer"]["width"] != grade["base"]["width"]:
                        failures.append([arm,block,pid,"bad old global solution"])
                if block == 0:
                    work[arm]["history.solver"].update(numbers(parent["history"]["producer"]))
                    work[arm]["history.checker"].update(numbers(parent["history"]["checker"]))
                got = set()
                for q in parent["edits"]:
                    eid = q["id"]
                    target = grade["edits"][eid]
                    role = target["kind"]
                    got.add(eid)
                    answer = q["answer"]
                    ok = (not q["failure"] and answer and answer["width"] == target["width"] and
                          sorted(answer["triple"]) in target["minimizers"] and
                          answer["class_count"] == target["candidate_classes"][
                              _group_index(len(case["frontier"]), answer["triple"])])
                    if not ok:
                        failures.append([arm,block,pid,eid,q["failure"] or "wrong minimum"])
                    costs[role] += q["cpu_ns"]
                    for name, elapsed in q["phases"].items():
                        costs[role + "." + name] += elapsed
                        costs["edits." + name] += elapsed
                    if block == 0:
                        correct[arm][role] += int(bool(ok))
                        produced[arm][role + ".physical gates"] += len(answer["physical"]["gates"]) if answer else 0
                        produced[arm][role + ".bytes"] += q["return_bytes"]
                        for label, fields in (("solver", "work"), ("edit", "edit_work"), ("checker", "check")):
                            work[arm][role + "." + label].update(numbers(q[fields]))
                if got != set(grade["edits"]):
                    failures.append([arm,block,pid,"missing edited return"])
        if seen != set(grades):
            failures.append([arm,block,"missing parents"])
        for key, value in costs.items():
            performance[arm][key].append((block, value))
    series = {arm:{k:[x for _,x in sorted(values)] for k,values in table.items()}
              for arm,table in performance.items()}
    ms = {arm:{k:median(vals)/1e6 for k,vals in table.items()} for arm,table in series.items()}
    best = min(("ordinary", "ordinary-prior", "ordinary-exact"), key=lambda arm:ms[arm]["total"])
    delta = [a-b for a,b in zip(series[best]["total"], series["fold"]["total"])]
    wins = sum(x > 0 for x in delta)
    lower_median = ms["fold"]["total"] < ms[best]["total"]
    decision = "stop"
    if failures:
        decision = "correctness failure"
    elif lower_median and wins >= (7 if len(blocks)==8 else 12):
        decision = "train"
    elif lower_median and len(blocks)==8:
        decision = "repeat timing"
    result = dict(ticket=TICKET, bounded=True, parents=len(public), edits=sum(len(c["edits"]) for c in public.values()),
                  timing_blocks=len(blocks), failures=failures, correct_unique=correct, best_unhinted=best,
                  median_ms=ms, series_ns=series, work_first_block=work, program_totals_first_block=produced,
                  paid_saving_ms=ms[best]["total"] - ms["fold"]["total"],
                  paired_savings_ms=[x/1e6 for x in delta], fold_wins=wins, decision=decision)
    destination = OUT / ("result.json" if decision != "repeat timing" else "timing-first-eight.json")
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if destination.exists() and destination.read_text() != payload:
        raise FileExistsError(destination)
    if not destination.exists():
        destination.write_text(payload)
    print(json.dumps({k:result[k] for k in ("best_unhinted","paid_saving_ms","fold_wins","decision")}))
    print({arm:round(ms[arm]["total"],3) for arm in ARMS})
    print(f"failures={len(failures)}")


def _group_index(m, group):
    from itertools import combinations
    return list(combinations(range(m), 3)).index(tuple(sorted(group)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=OUT)
    main(parser.parse_args().artifacts)
