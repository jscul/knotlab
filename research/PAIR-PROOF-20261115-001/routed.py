"""Freeze a favorable per-edit probe menu learned from timing repeats, then use new processes to price it."""
from pathlib import Path
import sys

NOTES = Path(__file__).resolve().parent
HERE = NOTES.parents[1] / "experiments" / NOTES.name / (NOTES.name + "-E001_shared_witnesses")
sys.path[:0] = [str(HERE), str(NOTES)]
from bind import OUT, ROOT, write, sha, load
from oracle_plans import fit_timing_choices, materialize_choices, crossfit_envelope


def main():
    original, timing = load(OUT/"design.json"), load(OUT/"timing.json")
    if timing["failures"]:
        raise ValueError("incomplete initial timing")
    records, plans = load(OUT/"edit-times.json"), load(OUT/"plans.json")
    # A route may use any fresh legal schedule or abstain. Old-skip is excluded here:
    # that strategy buys old history; its start-up charge is absent in fresh-advice arms.
    allowed = [arm for arm,s in original["arms"].items() if "advice" in s and not s.get("history")]
    dets = [arm for arm,s in original["arms"].items() if "advice" not in s]
    menu_by_arm = {a:plans[original["arms"][a]["advice"]] for a in allowed}
    selected, predicted = {}, {}
    for panel in ("mixed","broken"):
        rows = [r for r in records if r["panel"]==panel]
        details = timing["panels"][panel]
        blocks=details["arms"][allowed[0]]["blocks"]
        fit = fit_timing_choices(rows, blocks, default="ideal-skip", arms=allowed)
        for pid, edits in fit["choices"].items():
            selected.setdefault(pid,{}).update(edits)
        total = {b:{a:details["arms"][a]["totals_ns"][i] for a in allowed+dets}
                 for i,b in enumerate(blocks)}
        predicted[panel] = crossfit_envelope(rows, default="ideal-skip", arms=allowed,
                                             comparators=dets, block_totals=total)
    destination = OUT/"timing-selection"
    destination.mkdir(exist_ok=True)
    write(destination/"choices.json",selected)
    write(destination/"crossfit.json",predicted)
    route=materialize_choices(menu_by_arm,selected)
    arms = ["ordinary","compact","no-proof"]
    for panel in ("broken","mixed"):
        s=timing["panels"][panel]
        arms.extend([s["fastest_deterministic"],s["fastest_advice"]])
        actual = [arm for arm, item in s["arms"].items() if "advice" in original["arms"][arm] and
                  item["counts"]["broken.solver"].get("proofs_returned",0)>0]
        arms.append(min(actual,key=lambda arm:s["arms"][arm]["median_ms"]["total"]))
        # Include the fastest actual old-first method to retain the acquisition comparison.
        arms.append(min(["old-three","same-four","old-fresh","old-packed"],
            key=lambda a:s["arms"][a]["median_ms"]["total"]))
    arms=list(dict.fromkeys(arms))
    spec = {a:original["arms"][a] for a in arms}
    spec["ideal-routed"] = dict(mode="advice",advice="routed")
    keep = {s["advice"]:plans[s["advice"]] for s in spec.values()
            if "advice" in s and s["advice"]!="routed"}
    keep["routed"] = route
    write(destination/"plans.json",keep)
    write(destination/"stream.json",load(OUT/"stream.json"))
    design = dict(original)
    design["arms"] = spec
    design["sources"] = {**design["sources"],str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__))}
    design["data"] = {**design["data"], **{str(f.relative_to(ROOT)):sha(f) for f in
                      (OUT/"design.json",destination/"plans.json",destination/"choices.json",destination/"stream.json")}}
    write(destination/"design.json",design)
    print("Routed follow-up arms",list(spec))


if __name__=="__main__":
    main()
