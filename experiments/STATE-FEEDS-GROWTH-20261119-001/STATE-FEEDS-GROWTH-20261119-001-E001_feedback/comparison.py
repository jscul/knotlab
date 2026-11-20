"""Audit all sixteen first-layer laws directly on the one-spare ring attachment."""
from itertools import product
import json

import growth
from specificity import DATA, WORLD, ring_balls


def main():
    case = next(row for row in json.loads((WORLD / "inputs.json").read_text())["cases"] if row["id"] == "J1")
    stars = growth.predecessor().source_stars(case)
    ring = case["roles"]["ring_edges"][0]
    results = {}
    for cold, hot in product(growth.ACTIONS, repeat=2):
        row = {}
        for name, state in (("quiet", ()), ("loaded", ring)):
            frame = growth.step(stars, state, (cold, hot))
            row[name] = {"births": len(frame["births"]), "distinctions": frame["distinction_count"],
                         "ring_bond_balls": ring_balls(frame["stars"], ring)}
        results[cold + hot] = row
    (DATA / "comparison.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
