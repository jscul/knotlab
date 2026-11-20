"""Read the preregistered pair at offset six with the larger bond-radius budget."""
import json

from far_bond_ball import DATA, anchored
from moving_count import adjacency
from side_sources import cases, generate, loads

ROOTS = (18, 19)


def stage(occupied):
    spec = cases()["P8"]
    ancestors = []
    for age, frame in generate(spec, occupied, max_age=4):
        if age == 0:
            ancestors = [{i} for i in range(len(frame["stars"]))]
        else:
            for i in range(len(ancestors), len(frame["stars"])):
                ancestors.append(set.union(*(ancestors[p] for p in frame["parent_sets"][i])))
    assert age == 4
    holders, _ = adjacency(frame["stars"])
    return frame["stars"], holders, ancestors


def one_arm(frame, cutoff):
    stars, holders, ancestors = frame
    roots = {m: anchored(stars, m, cutoff) for m in ROOTS}
    contained = set(ROOTS)
    for row in roots.values():
        for bond in row["bonds"]:
            contained.update(bond)
    knots = {v for m in contained for v in holders[m]}
    original_ring = set(cases()["P8"]["roles"]["rings"][0])
    return {
        "complete": all(row["complete"] for row in roots.values()),
        "holder_count": len(knots),
        "ring_holders": sorted(knots & original_ring),
        "outside_original_side": sum(any(a <= 12 or a > 32 for a in ancestors[v]) for v in knots),
        "ordered_roots": list(ROOTS),
        "enumerations": {m: {k: v for k,v in row.items() if k != "bonds"} for m,row in roots.items()},
        "roots_and_bonds": {m: row["bonds"] for m,row in roots.items()}
    }


def main():
    stages = {arm: stage(state) for arm, state in loads(cases()["P8"]).items()}
    assert set(stages) == {"0", "1"}
    result = {"source":"P8","age":4,"roots":ROOTS,"rows":{},
              "stage_knots": {arm: len(frame[0]) for arm, frame in stages.items()}}
    for radius in range(12):
        arms = {arm: one_arm(frame, radius + 1) for arm, frame in stages.items()}
        result["rows"][radius] = arms
        counts = [row["holder_count"] for row in arms.values()]
        print(radius, counts, [row["complete"] for row in arms.values()], flush=True)
        if not all(row["complete"] for row in arms.values()) or counts[0] != counts[1]:
            break
    (DATA/"radius_at_six.json").write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
