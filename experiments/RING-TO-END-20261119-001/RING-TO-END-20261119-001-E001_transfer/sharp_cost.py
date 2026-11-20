"""Sharp source-wide cost and unrestricted interleavings inside the bare hot sector."""
from collections import Counter
from itertools import combinations
from math import comb, factorial
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/STATE-FEEDS-GROWTH-20261119-001/STATE-FEEDS-GROWTH-20261119-001-E001_feedback"))
import growth

DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
PV = ("P", "V")


def at_source(spec):
    stars = growth.predecessor().source_stars(spec)
    rim = set(spec["roles"]["ring_edges"][0])
    plan = growth.plan_round(stars, rim, PV)
    frame = growth.realize_round(plan)
    source_counts = {v: len(bits) for v, bits in plan.stage.loose.items()}
    hot = frame["hot_live_parents"]
    eligible = [child for child in frame["births"] if child["active"] and len(child["parents"]) == 1
                and source_counts[child["parents"][0]] == 2]
    assert all(len(child["fresh"]) == 2 for child in eligible)
    pairs = [set(child["fresh"]) for child in eligible]
    heated = rim.union(*pairs)
    direct = growth.step(frame["stars"], heated, PV)
    erased = growth.step(frame["stars"], rim, PV)
    assert all(len(set(row) & heated) % 2 == 0 for row in frame["stars"])
    assert heated - rim == set.union(*pairs)
    return ({"hot_source_open_counts": sorted(source_counts[v] for v in hot),
             "eligible_children": len(eligible), "all_fresh_writes": len(heated-rim),
             "held_incidence_births": [len(erased["births"]), len(direct["births"])],
             "held_incidence_distinctions": [erased["distinction_count"], direct["distinction_count"]]}, frame, rim, pairs)


def delayed_and_atomic(spec):
    _, frame, rim, pairs = at_source(spec)
    assert len(pairs) == 10
    observed = Counter()
    for mask in range(1 << len(pairs)):
        state = rim.union(*(pair for i,pair in enumerate(pairs) if mask & (1 << i)))
        next_plan = growth.plan_round(frame["stars"], state, PV)
        observed[len(next_plan.births)] += 1
    assert observed == {15+k: comb(5,k)*3**k for k in range(6)}
    # Each first-layer port birth enables two independent second-layer births.
    # Enumerate one component's causal ideals and all its named maximal orders.
    ground = (0,1,2)
    ideals = [members for k in range(4) for members in combinations(ground,k)
              if not (1 in members or 2 in members) or 0 in members]
    assert len(ideals) == 5
    return {"completed_delayed_subsets_by_next_births": dict(sorted(observed.items())),
            "one_port_orders": [[0,1,2],[0,2,1]], "one_port_downward_closed_sets": ideals,
            "two_depth_ideals_on_ten_ports": len(ideals)**10,
            "two_depth_named_linear_orders": factorial(30)//(3**10)}


def main():
    sources = json.loads((ROOT/"experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/inputs.json").read_text())
    specs = {row["id"]:row for row in sources["cases"]}
    cost = {tag:at_source(specs[tag])[0] for tag in ("R0","J1")}
    assert cost["R0"]["all_fresh_writes"] == 20 and cost["R0"]["held_incidence_births"] == [15,20]
    assert cost["J1"]["all_fresh_writes"] == 4 and cost["J1"]["held_incidence_births"] == [56,57]
    answer={"least_equivariant_total_in_fresh_only_class":cost,"bare_orders":delayed_and_atomic(specs["R0"])}
    (DATA/"sharp_cost.json").write_text(json.dumps(answer,indent=2)+"\n")
    print(json.dumps(answer,ensure_ascii=False))


if __name__=="__main__":
    main()
