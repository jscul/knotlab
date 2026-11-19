"""A literal connected starting sample with a block retraction and an unfunded join."""
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(next((ROOT / "proofs/WALL-READ-20261119-001A").glob("*-P001_partnered"))))
sys.path.insert(0, str(next((ROOT / "experiments/GROWN-END-SWAP-20261119-001").glob("*-E001_reached"))))
import rosterlib as roster
import verify


def realize(live, blocks):
    supports = [[] for _ in range(live + len(blocks))]
    meetings = [(p, live + i) for i, block in enumerate(blocks) for p in block]
    meetings.extend((live + i, live + (i + 1) % len(blocks)) for i in range(len(blocks)))
    for distinction, (u, v) in enumerate(meetings):
        supports[u].append(distinction)
        supports[v].append(distinction)
    first = len(meetings)
    for row in supports[:live]:
        row.extend(range(first, first + 4))
        first += 4
    stage = verify.Arrangement.parse(supports)
    audit = verify.start_audit(stage)
    assert audit["census_open_legal"] and audit["meets_once"]
    opens, actual = roster.roster_of([len(s) for s in supports], meetings)
    assert opens == [4] * live and set(actual) == set(map(frozenset, blocks))
    should_join = verify.groups(stage.neighbors, stage.live)
    assert set(should_join) == set(roster.groups_of(range(live), actual))
    records = list(roster.grow(opens, actual, 1))
    return dict(supports=supports, audit=audit, growing_end=list(range(live)), blocks=blocks,
                demand=[sum(p in group for group in should_join) for p in range(live)],
                first_round=records, groups=sorted(sorted(g) for g in should_join),
                junctions=len(supports), distinctions=first)


def main():
    blocks = [pair for pair in combinations(range(6), 2) if pair[0] // 2 != pair[1] // 2]
    target = realize(6, blocks)
    source = realize(7, blocks + [(0, 6)])
    retract = [0, 1, 2, 3, 4, 5, 2]
    assert all(tuple(sorted({retract[v] for v in b})) in blocks for b in source["blocks"])
    assert source["demand"] == [5, 4, 4, 4, 4, 4, 1]
    assert target["demand"] == [4] * 6
    assert source["first_round"] == [{"t": 1, "end": "stall"}]
    assert target["first_round"][0]["count"] == 8
    info = dict(source=source, target=target, source_to_target=retract)
    (HERE / "literal_stall.json").write_text(json.dumps(info, indent=1) + "\n")
    print("source", source["junctions"], source["distinctions"], source["first_round"],
          "| target", target["junctions"], target["distinctions"], target["first_round"][0])


if __name__ == "__main__":
    main()

