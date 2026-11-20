"""Compare every outermost-only parent set to the next archived physical birth."""
import argparse
import gzip
import json
from pathlib import Path

from interface_check import distances_from_tip


def validate(archive, evidence):
    checked = []
    for start in (3, 14):
        for age in (6, 7):
            record = json.loads((evidence / f"outer_{start}_{age}.json").read_text())
            path = archive / f"start-{start:02}-age{age+1:02}.parents.json.gz"
            with gzip.open(path, "rt") as stream:
                parents = json.load(stream)
            distances, _ = distances_from_tip(parents)
            predicted = {tuple(sorted(group)) for group in record["new_outer_supports_if_increased"]}
            observed = {tuple(sorted(parents[v])) for v, d in distances.items()
                        if d == record["old_radius"] + 1}
            assert predicted == observed and max(distances.values()) == record["new_radius"]
            checked.append(dict(start=start,old_age=age,predicted_maximum=record["new_radius"],
                                all_true_outer_groups_when_advancing=len(observed),
                                actual_whole_birth_roster=len(parents)))
    return checked


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for name in ("archive","evidence","output"):
        p.add_argument(name,type=Path)
    args = p.parse_args()
    rows = validate(args.archive,args.evidence)
    args.output.write_text(json.dumps(rows,indent=2)+"\n")
    print(rows)
