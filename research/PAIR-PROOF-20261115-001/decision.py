"""Compare finite ideal-choice schedules and the frozen per-edit timing chooser against deployable controls."""
import gzip
import json
from pathlib import Path
from statistics import median

NOTES = Path(__file__).resolve().parent
ROOT = NOTES.parents[1]
OUT = ROOT/"artifacts"/NOTES.name/(NOTES.name+"-E001_shared_witnesses")


def read(path):
    return json.loads(path.read_bytes())


def contrast(reports, candidate, control):
    ours, theirs = [],[]
    for report in reports:
        if candidate not in report or control not in report:
            continue
        ours.extend(report[candidate]["totals_ns"])
        theirs.extend(report[control]["totals_ns"])
    paired = [(b-a)/1e6 for a,b in zip(ours,theirs)]
    if not paired:
        raise ValueError("empty paired comparison")
    return dict(blocks=len(paired),wins=sum(d>0 for d in paired),paired_ms=paired,
                median_paired_ms=median(paired),candidate_median_ms=median(ours)/1e6,
                control_median_ms=median(theirs)/1e6,median_gap_ms=(median(theirs)-median(ours))/1e6)


def floor(directory, panel, arm):
    runs, components = [], []
    for line in (directory/"results.jsonl").read_bytes().splitlines():
        record=json.loads(line)["result"]
        if (record["panel"],record["arm"])!=(panel,arm):
            continue
        select=alt=whole_check=0
        with gzip.open(directory/record["file"],"rt") as f:
            for line in f:
                p=json.loads(line)
                for q in p["edits"]:
                    s=q["work"].get("minimum_selection_cpu_ns",0)
                    v=q["check"].get("alternative_checks_cpu_ns",0)
                    assert 0<=s<=q["phases"]["solve"] and 0<=v<=q["phases"]["verify"]
                    select+=s
                    alt+=v
                    whole_check+=q["phases"]["verify"]
        total=record["cpu_ns"]
        runs.append((total-select-alt)/1e6)
        components.append((select/1e6,alt/1e6,whole_check/1e6,(select+alt)/total))
    return dict(free_selection_and_alternatives_median_ms=median(runs),
                selection_ms=median(p[0] for p in components),alternative_verification_ms=median(p[1] for p in components),
                whole_verification_ms=median(p[2] for p in components),removable_fraction=median(p[3] for p in components),
                scope="Phase subtraction for same returned programs. Grants even chosen-group selection for free. Not an executable solver.")


def main():
    first=read(OUT/"timing.json"); more_dir=OUT/"timing-selection";more=read(more_dir/"timing.json")
    result=dict(failures=first["failures"]+more["failures"], coverage=read(OUT/"coverage.json")["totals"],panels={})
    if result["failures"]:raise ValueError("incorrect or missing returns")
    for panel in ("broken","mixed"):
        b=first["panels"][panel]; c=more["panels"][panel]
        original=b["arms"]; extra=c["arms"]
        best=c["fastest_deterministic"]
        spec=read(OUT/"design.json")["arms"]
        proof_arms=[arm for arm,record in original.items() if "advice" in spec[arm] and
                    record["counts"]["broken.solver"].get("proofs_returned",0)>0]
        selected=min(proof_arms,key=lambda a:original[a]["median_ms"]["total"])
        if selected not in extra:
            raise ValueError("fastest advice missing from actual repetition")
        candidates=sorted({selected,"ideal-routed"})
        comparisons={k:contrast([extra],k,best) for k in candidates}
        initial_best=b["fastest_deterministic"]
        pooled=contrast([original,extra],selected,best)
        best_replicated=any(t["wins"]>=7 and t["median_paired_ms"]>0 and t["median_gap_ms"]>0
                            and extra[a]["counts"].get("broken.solver",{}).get("proofs_returned",0)>0
                            for a,t in comparisons.items())
        pooled_win=(pooled["blocks"]>=16 and pooled["wins"]>=12 and pooled["median_paired_ms"]>0
                    and pooled["median_gap_ms"]>0 and original[selected]["counts"]["broken.solver"].get("proofs_returned",0)>0)
        result["panels"][panel]=dict(initial_best_deployable=initial_best,initial_best_advice=selected,
                initial_best_including_abstention=b["fastest_advice"],
                initial_best_contrast=contrast([original],selected,initial_best),
                repeat_best_deployable=best, repeat_contrasts=comparisons,best_fixed_advice_pooled=pooled,
                compact_phase_floor=floor(OUT,panel,"compact"),paid_headroom=bool(best_replicated or pooled_win))
    result["train_gate"]=result["panels"]["broken"]["paid_headroom"]
    result["decision"]="train" if result["train_gate"] else "stop"
    path=OUT/"result.json";data=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if path.exists() and path.read_text()!=data:
        raise FileExistsError(path)
    if not path.exists():path.write_text(data)
    print(result["decision"])
    for panel,v in result["panels"].items():
        print(panel,v["initial_best_deployable"],v["initial_best_advice"],v["repeat_best_deployable"],
              {k:(round(c["median_paired_ms"],3),c["wins"]) for k,c in v["repeat_contrasts"].items()})


if __name__=="__main__":
    main()
