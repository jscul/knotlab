"""Stress-test the proved sufficient offsets, including the last physical mark."""
import json
from pathlib import Path

from side_balls import read_profile, indices
from side_sources import CAPS, cases, generate, loads

DATA = Path(__file__).resolve().parents[3] / "artifacts" / Path(__file__).resolve().parents[1].name / Path(__file__).resolve().parent.name
CHECKS = [("P8",5,(31,)),("P16",7,(43,47))]


def main():
    result = []
    for tag, radius, marks in CHECKS:
        case = cases()[tag]
        seam, = case["roles"]["seams"]
        assert min(marks)-seam == 2*radius+9
        assert max(marks) == len(case["roles"]["anchors"])-1
        seen = {}
        arms = {}
        for arm, state in loads(case).items():
            rec = arms[arm] = {}
            for age, frame in generate(case, state, radius+2, CAPS):
                if age < radius+1:
                    continue
                profile = read_profile((frame["stars"], marks, marks if radius==7 else ()))
                for m in marks:
                    low, high, knlo, knhi = profile["root_masks"][m][radius]
                    assert low == high and knlo == knhi
                    physical_names = tuple(profile["names"][j] for j in indices(low))
                    physical_holders = tuple(indices(knlo))
                    point = (arm,m)
                    if point in seen:
                        assert (physical_names,physical_holders) == seen[point]
                    else:
                        seen[point] = (physical_names,physical_holders)
                    rec.setdefault(age,{})[m] = [len(physical_names),len(physical_holders)]
        common = sorted(set(arms["0"]) & set(arms["1"]))
        assert radius+1 in common
        assert all(arms["0"][age] == arms["1"][age] for age in common)
        result.append({"source":tag,"radius":radius,"stage_cap":CAPS,"marks":marks,"offsets":[m-seam for m in marks],"common_complete_ages":common,"names_and_holders_stable_in_each_arm":True,"arms":arms})
    (DATA/"fixed_bound_check.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
