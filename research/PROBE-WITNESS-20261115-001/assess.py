"""Measure the cost to return verified programs and the opportunity for choosing probes."""
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1] / "experiments" / HERE.name / (HERE.name + "-E001_fixed_probes")
sys.path.insert(0, str(EXP))
from advice import available, outside_patterns
from job import CALIBRATION, CONSTANT, DEFAULT, HELD, PRIMITIVES, REPEATS, check_hashes, encoded, read, sha


def middle(rows):
    return {k:median([r.get(k,0) for r in rows]) for k in set().union(*(r.keys() for r in rows))}


def public_example(task, records):
    for mask,a,b,c,settings,scheme in records:
        if settings != 3:
            continue
        grp = tuple(i for i in range(task["n"]) if mask >> i & 1)
        outs = [v & ~mask for v in outside_patterns(task["n"],scheme)]
        rows = []
        for local in (a,b,c):
            values = [(local >> j) & 1 for j in range(3)]
            offset = sum(v << i for v,i in zip(values,grp,strict=True))
            raw = [o | offset for o in outs]
            signatures = [tuple((t >> x) & 1 for t in task["outputs"]) for x in raw]
            rows.append(dict(local=values, global_rows=raw, responses=signatures))
        by_side = [{tuple(x["responses"][i]) for x in rows} for i in (0,1)]
        if all(len(s) < 3 for s in by_side) and len({tuple(x["responses"]) for x in rows}) == 3:
            return dict(id=task["id"], n=task["n"], group=grp, outside=outs, scheme=scheme, rows=rows)


def count_row(task, grade, raw):
    res, cert = raw["result"] or {}, raw["certificate"] or {}
    w = res.get("work", {})
    records = res.get("witnesses", [])
    exact = bool(not raw["failure"] and cert.get("exact") and cert["width"] == grade["width"]
                 and tuple(sorted(res["triple"])) in set(map(tuple,grade["minimizers"])))
    c = Counter(tasks=1, exact=int(exact), width1=int(exact and cert["width"] == 1),
                width2=int(exact and cert["width"] == 2), rows=cert.get("verified_assignments",0),
                output_bits=cert.get("verified_output_bits",0), gates=cert.get("gates",0),
                eligible=comb(task["n"],3), returned_witnesses=len(records),
                single=sum(rec[4] != 3 for rec in records), double=sum(rec[4] == 3 for rec in records),
                exact_search=w.get("attempted_by_exact",w.get("group_trials",w.get("triple_trials",0))),
                effective=cert.get("effective_witnesses",0), accepted=cert.get("accepted_witnesses",0),
                exact_alternatives=cert.get("exact_alternatives",cert.get("alternatives_checked",0)),
                verifier_requests=cert.get("verifier_row_requests",0), verifier_reads=cert.get("verifier_row_reads",0),
                verifier_reuse=cert.get("verifier_row_cache_hits",0))
    for rec in records:
        c["scheme_" + str(rec[5])] += 1
    for key in ("probe_row_requests","probe_row_unique","probe_row_reuses","probe_output_bit_reads",
                "probe_candidates","probe_witness_hits","probe_unresolved_fallback","resolved_by_witness",
                "exact_bound_rejections","witnesses_discarded_after_width1","witness_row_references",
                "witness_distinct_rows"):
        c[key] = w.get(key,0)
    for k in ("cpu_ns","wall_ns","init_cpu_ns","synth_cpu_ns","verify_cpu_ns","verify_wall_ns","serialization_cpu_ns","return_bytes"):
        c[k] = raw[k]
    return c


def potential(tasks, grades):
    # Off-clock, after the programs have been returned; never available to
    # primary solvers. Assess all eligible groups, including unvisited ones.
    split = defaultdict(Counter)
    for t in tasks:
        g = grades[t["id"]]
        all_scores = available(t)
        groups = combinations(range(t["n"]),3)
        for triple,count in zip(groups,g["candidate_classes"],strict=True):
            scores = all_scores[sum(1 << i for i in triple)]
            for k in ("all",g["kind"]):
                c = split[k]
                c["groups"] += 1
                c["impossible_one"] += count > 2
                c["scheme0"] += scores[0] is not None
                c["any_scheme"] += any(s is not None for s in scores)
                for i,s in enumerate(scores):
                    c["available_" + str(i)] += s is not None
            if count <= 2 and any(s is not None for s in scores):
                raise ValueError("a local witness falsely excludes a genuine one-bit group")
    return split


def compare(x,y):
    return dict(cpu_gap_ns=x["paid_cpu_ns"]-y["paid_cpu_ns"], cpu_ratio=x["paid_cpu_ns"]/y["paid_cpu_ns"],
                wall_gap_ns=x["paid_wall_ns"]-y["paid_wall_ns"],
                paired_cpu_wins=sum(a<b for a,b in zip(x["cpu_repeats_ns"],y["cpu_repeats_ns"],strict=True)))


def wins(x,y):
    v=compare(x,y)
    return v["cpu_gap_ns"] < 0 and v["paired_cpu_wins"] >= 7


def assess(out):
    d, data = read(out/"design.json"), read(out/"data-bound.json")
    check_hashes(out,{k:v for k,v in data.items() if k.endswith(".json")})
    if not d["frozen_utc"] < data["opened_utc"]:
        raise ValueError("freeze/release order")
    tasks={p:read(out/(p+".json")) for p in ("calibration","held")}
    grades={p:read(out/(p+"-grades.json")) for p in tasks}
    streams, groups, work, fingerprints = defaultdict(dict), defaultdict(list), defaultdict(list), {}
    failures, examples = [], []
    for line in (out/"results.jsonl").read_text().splitlines():
        event=json.loads(line)
        if event["status"] != "ok":
            raise ValueError("retained process failure, incomplete measurement: "+event["case"])
        s=event["result"]
        p,arm,rep=s["panel"],s["arm"],s["repeat"]
        key=p,arm
        path=out/s["file"]
        if rep in streams[key] or sha(path) != s["sha256"] or s["cpu"] != d["cpu"]:
            raise ValueError("duplicate case or different receipt/core")
        with gzip.open(path,"rt") as f:
            rows=[json.loads(line) for line in f]
        total, by, wsum, sig = Counter(), defaultdict(Counter),Counter(),hashlib.sha256()
        for task,row in zip(tasks[p],rows,strict=True):
            if task["id"] != row["id"]:
                raise ValueError("preselected order changed")
            grade=grades[p][row["id"]]
            c=count_row(task,grade,row)
            if not c["exact"]:
                failures.append([event["case"],row["id"],row["failure"]])
            total.update(c)
            for tag in (grade["kind"],str(task["n"]),grade["operation"]):
                by[tag].update(c)
            result=row["result"] or {}
            sig.update(encoded([result.get(k) for k in ("triple","width","summary_wires","circuit","witnesses")]))
            wsum.update({k:v for k,v in result.get("work",{}).items() if type(v) is int})
            if p=="held" and arm=="zero-one" and rep==0 and not examples and task["n"]==7:
                example=public_example(task,result.get("witnesses",[]))
                if example:
                    examples.append(example)
        if key in fingerprints and fingerprints[key]!=sig.hexdigest():
            raise ValueError("logical results changed between timed repetitions")
        fingerprints[key]=sig.hexdigest()
        total.update(startup_cpu_ns=s["startup_cpu_ns"],startup_wall_ns=s["startup_wall_ns"],
                     paid_cpu_ns=s["startup_cpu_ns"]+total["cpu_ns"], paid_wall_ns=s["startup_wall_ns"]+total["wall_ns"])
        streams[key][rep]=total
        groups[key].append(by)
        work[key].append(wsum)
    methods={}
    for p,roster in (("calibration",CALIBRATION),("held",HELD)):
        methods[p]={}
        for arm in roster:
            key=p,arm
            if set(streams[key]) != set(range(REPEATS)):
                raise ValueError("missing deployment "+str(key))
            series=[streams[key][i] for i in range(REPEATS)]
            m=methods[p][arm]=middle(series)
            m["groups"]={t:middle([g[t] for g in groups[key]]) for t in groups[key][0]}
            m["work"]=middle(work[key])
            m["cpu_repeats_ns"]=[x["paid_cpu_ns"] for x in series]
            m["wall_repeats_ns"]=[x["paid_wall_ns"] for x in series]
    held,cal=methods["held"],methods["calibration"]
    benchmark=min(PRIMITIVES,key=lambda k:held[k]["paid_cpu_ns"])
    constant=min(CONSTANT,key=lambda k:cal[k]["paid_cpu_ns"])
    skips=[f"skip-{i}" for i in range(4)]
    skip=min(skips,key=lambda k:cal[k]["paid_cpu_ns"])
    menu=cal["oracle-menu"]
    active_schemes=sum(menu.get(f"scheme_{i}",0)>0 for i in range(4))
    valid_cal=not any(case.startswith("calibration-") for case,_,_ in failures)
    select_context=valid_cal and active_schemes>1 and wins(menu,cal[constant]) and wins(menu,cal[skip])
    select_skip=valid_cal and wins(cal[skip],cal[constant]) and wins(cal[skip],cal["matched-exact"])
    choice="context" if select_context else ("skip" if select_skip else "stop")
    decision=dict(best_constant=constant,best_skip=skip,menu_schemes_used=active_schemes,
                  menu_vs_constant=compare(menu,cal[constant]),menu_vs_skip=compare(menu,cal[skip]),
                  menu_vs_primitive=compare(menu,cal["primitive"]),skip_vs_primitive=compare(cal[skip],cal["primitive"]),
                  skip_vs_constant=compare(cal[skip],cal[constant]),skip_vs_no_probe=compare(cal[skip],cal["matched-exact"]),
                  select_context=bool(select_context),select_skip=bool(select_skip),next=choice)
    totals=Counter()
    for sr in streams.values():
        for rr in sr.values():
            totals.update({k:rr[k] for k in ("tasks","rows","output_bits")})
    return dict(methods=methods,benchmark=benchmark,held_comparisons={k:compare(held["zero-one"],v) for k,v in held.items()},
                held_repeatable_win=not any(f[0].startswith("held-") for f in failures) and wins(held["zero-one"],held[benchmark]),
                headroom=decision,coverage={p:potential(tasks[p],grades[p]) for p in tasks},
                example=examples[0] if examples else None,failures=failures,replay_totals=totals,
                source_design_sha256=sha(out/"design.json"),data_sha256=sha(out/"data-bound.json"))


if __name__=="__main__":
    out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else DEFAULT
    result=assess(out)
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("benchmark","held_repeatable_win","headroom","failures","replay_totals")}))
