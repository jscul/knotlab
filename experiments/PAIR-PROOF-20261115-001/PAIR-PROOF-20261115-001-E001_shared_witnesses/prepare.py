"""Prepare the preselected stream and the offline menu of legal ideal test requests."""
from pathlib import Path
import sys
from time import process_time_ns, perf_counter_ns

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bind import OUT, bind, load, write


def _skip_misses(options):
    chosen, covered = [], set()
    while options:
        key, (test, groups) = max(options.items(), key=lambda item:len(item[1][1]-covered))
        del options[key]
        if not groups-covered:
            break
        chosen.append(test)
        covered |= groups
    return chosen


def extra_plans(coverage, full):
    full_three, old_only, fixed_only = {}, {}, {}
    for pid, tasks in coverage["tasks"].items():
        full_three[pid], old_only[pid], fixed_only[pid] = {}, {}, {}
        originals = {tuple(w["test"][:2]):[*w["test"],sum(1<<x for x in w["corners"])]
                     for w in coverage["original_witnesses"][pid]}
        for eid, t in tasks.items():
            available = {tuple(x["test"][:2]):x for x in t["available"]}
            out = []
            for i,j,base in full[pid][eid]:
                record = available[i,j]
                mask = record["corner_masks"][record["bases"].index(base)][0]
                out.append([i,j,base,mask])
            full_three[pid][eid] = out
            survivors = t["original_rechecked"]["same_three"]["pairs"]
            old_only[pid][eid] = _skip_misses({tuple(g):(originals[tuple(g)],set(available[tuple(g)]["covers"]))
                                               for g in survivors})
            fixed = {}
            for pair, record in available.items():
                i,j = pair
                high = ((1<<t["m"])-1) ^ (1<<i) ^ (1<<j)
                for base in (0,high):
                    if base in record["bases"]:
                        mask = record["corner_masks"][record["bases"].index(base)][0]
                        fixed[pair] = ([i,j,base,mask],set(record["covers"]))
                        break
            fixed_only[pid][eid] = _skip_misses(fixed)
    return {"full-three":full_three,"old-skip":old_only,"fixed-skip":fixed_only}


def main():
    from oracle_plans import build_plan_maps
    cache = OUT / "plans.json"
    if cache.exists():
        plans = load(cache)
    else:
        cpu, wall = process_time_ns(), perf_counter_ns()
        evidence = load(OUT / "coverage.json")
        full = load(OUT / "oracle_advice.json")["parents"]
        plans = build_plan_maps(evidence, {"parents":full})
        plans.update(extra_plans(evidence,full))
        write(cache,plans)
        write(OUT / "offline_plan_cost.json",dict(cpu_ns=process_time_ns()-cpu,wall_ns=perf_counter_ns()-wall,
              scope="Build legal cost/coverage advice menus from enumerated pair/setting coverage. Excluded from advisory deployment clocks."))
    arms = {
        "ordinary":{"mode":"ordinary"},
        "compact":{"mode":"compact"},
        "no-proof":{"mode":"no-proof"},
        "old-three":{"mode":"old-three","history":True},
        "same-four":{"mode":"same-four","history":True},
        "fresh":{"mode":"fresh"}, "packed":{"mode":"packed"}, "balanced":{"mode":"balanced"},
        "old-fresh":{"mode":"old-fresh","history":True},
        "old-packed":{"mode":"old-packed","history":True},
    }
    for name in plans:
        arms["ideal-"+name] = dict(mode="advice",advice=name,history=(name=="old-skip"))
    arms["old-ideal-full"] = dict(mode="old-advice",history=True,advice="full-three")
    if "--plans-only" not in sys.argv[1:]:
        bind(plans,arms)


if __name__=="__main__":
    main()
