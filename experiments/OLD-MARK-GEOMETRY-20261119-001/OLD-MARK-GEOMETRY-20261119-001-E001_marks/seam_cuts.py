"""Replay the persistent seam pair on both orientations in both double-ring controls."""
from pathlib import Path
import json

from certify import Wired
from certify_flow import exact_pair
from sources import cases, loads, generate

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def main():
    samples = []
    for case in ("J1","T4","T8"):
        spec = cases()[case]
        for mask, state in loads(spec).items():
            for age, frame in generate(spec, state, max_age=6):
                graph = Wired(frame["stars"])
                for r, seam in enumerate(spec["roles"]["seams"]):
                    row = exact_pair(graph, seam-1, seam)
                    loaded = bool(int(mask) & (1<<r))
                    expected = 4 if loaded and age >= 4 else 7
                    assert row["bond_distance"] == expected
                    assert len(row["orientations"]) == 2
                    samples.append({"source":case,"mask":mask,"age":age,"seam":seam,"proof":row})
    assert len(samples) == 126
    (DATA/"seam_cuts.json").write_text(json.dumps(samples,separators=(",",":"))+"\n")
    print(len(samples),"literal connected-shore minima and",2*len(samples),"orientation bounds verified")


if __name__=="__main__":
    main()
