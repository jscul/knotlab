"""Rebuild the growing end. The text export is scratch input for the sampling and census."""
from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(next((ROOT / "proofs/WALL-READ-20261119-001A").glob("*-P001_partnered"))))
import rosterlib as roster


def main():
    destination = Path(sys.argv[1])
    destination.mkdir(parents=True, exist_ok=True)
    rows = (json.loads(s) for s in (ROOT / "runs/merge-burst/results.jsonl").read_text().splitlines())
    start = next(r["result"]["start"] for r in rows if r.get("case") == "start-03")
    opens, blocks = roster.roster_of(start["sizes"], start["edges"])
    archive = {}
    def save(age, points, current, parents):
        if age < 5:
            return
        ids = {p:i for i,p in enumerate(sorted(points))}
        bs = sorted(tuple(sorted(ids[p] for p in b)) for b in current)
        with (destination / f"age{age}.txt").open("w") as stream:
            print(len(points), len(bs), file=stream)
            for block in bs:
                print(*block, file=stream)
        pr = [sorted(parents[p]) for p in sorted(points)]
        (destination / f"parents{age}.json").write_text(json.dumps(pr))
        archive[age] = dict(junctions=len(points), blocks=len(bs),
                            largest_block=max(map(len,bs)), parent_sum=sum(map(len,pr)),
                            parent_counts=dict(sorted(Counter(map(len,pr)).items())))
        print(age, archive[age]['junctions'],len(bs),archive[age]['parent_sum'],flush=True)
        if age == 8:
            raise StopIteration
    try:
        for row in roster.grow(opens, blocks, 8, on_stage=save):
            if row.get("t") == 7 and "open_sum" in row:
                archive[7]["open_sum"] = row["open_sum"]
    except (StopIteration, RuntimeError) as exc:
        if 8 not in archive:
            raise exc
    assert archive[8]["parent_sum"] == archive[7]["open_sum"] == 993164
    assert archive[8]["junctions"] == 28065 and archive[7]["junctions"] == 386
    out = ROOT / "artifacts" / HERE.parent.name / HERE.name
    (out / "stage.json").write_text(json.dumps(archive, indent=2) + "\n")


if __name__ == "__main__":
    main()

