"""Compare saved counts, individual sample failures and a connected two-piece control."""
import argparse
import json
from collections import Counter
from pathlib import Path

from rebuild import HERE, RESEARCH, first_failure
from sampling import start_check


def table_check():
    study = HERE.parent
    table = (study / "counts_table.md").read_text().strip()
    assert table in (study / "README.md").read_text()
    fields = ["in the class, with chains", "in the class, no chains",
              "fails N1 (chained twins)", "fails N2 only (lifts do not meet)",
              "fails N3 only", "core does not finish by rank 25", "core over the cap"]
    rows = []
    for line in table.splitlines()[2:]:
        weighting, size, *counts = [s.strip(" `") for s in line.strip("|").split("|")]
        stored = json.loads((study / "counts" / f"{weighting}_{size}.json").read_text())
        draws = Counter(stored["accepted draws with repeats"])
        rejected = draws.pop("not accepted", 0)
        unique = Counter(stored["distinct accepted starts"])
        assert sum(draws.values()) + rejected == stored["draws"] == 3000
        assert stored["seed"] == 2026112701 and stored["knots"] == int(size)
        numbers = [(sum(draws.values()), sum(unique.values()))] + [(draws[k], unique[k]) for k in fields]
        assert numbers == [tuple(map(int, v.split("/"))) for v in counts]
        rows.append(dict(weighting=weighting, knots=int(size), accepted=numbers[0],
                         bins=numbers[1:], in_class_draws=sum(draws[k] for k in fields[:2]),
                         unresolved_draws=sum(draws[k] for k in fields[-2:])))
    return rows


def split_witness():
    """Join spent knots by a single fresh shared distinction, preserving both live pieces."""
    row = (HERE.parent / "referee_witnesses.jsonl").read_text().splitlines()[6]
    start = json.loads(row)["stars"]
    offset = max(d for knot in start for d in knot) + 1
    doubled = [s[:] for s in start] + [[a + offset for a in s] for s in start]
    multiplicity = Counter(d for s in start for d in s)
    spent = next(i for i, s in enumerate(start) if all(multiplicity[d] == 2 for d in s))
    for i in (spent, spent + len(start)):
        doubled[i].append(2 * offset)
    original = first_failure(start)
    combined = first_failure(doubled)
    assert combined["child_round"] == original["child_round"] == 10
    assert len(combined["gained"]) == 2 * len(original["gained"]) == 4
    assert len(combined["lost"]) == 2 * len(original["lost"]) == 2
    assert not combined["unexplained_gains"] and not combined["unexplained_losses"]
    cls, _, _, pieces = start_check(doubled, 5000, 250000, 25, "all", "nae")
    assert cls == "finished" and len(pieces) == 2
    return dict(stars=doubled, joined_spent_knots=[spent, spent + len(start)],
                child_round=10, gained=combined["gained"], lost=combined["lost"],
                splits=combined["splits"], pieces=len(pieces))


def original_sample(limit):
    graded = RESEARCH / "GRADED-ORDER-20261126-001"
    cycles = RESEARCH / "CYCLE-READ-20261127-001"
    srcs = [graded / "held_grow.jsonl", graded / "replays.jsonl", cycles / "twin8_draw.jsonl",
            cycles / "twin9_draw.jsonl", cycles / "cyc6_uniform.jsonl"]
    log = {}
    for line in (HERE.parent / "shapes_samples.txt").read_text().splitlines():
        if line.startswith("{"):
            record = json.loads(line)
            log[record["file"], record["draw"]] = record
    rows = []
    for path in srcs:
        for i, record in enumerate(map(json.loads, path.read_text().splitlines()), 1):
            if limit and len(rows) >= limit:
                break
            status, _, _, pcs = start_check(record["stars"], 5000, 250000, 25, "all", "nae")
            row = dict(file=path.name, line=i, status=status)
            if status == "finished":
                flags = sorted({k for p in pcs for k in p["witnesses"]})
                result = first_failure(record["stars"], horizon=10)
                assert result["status"] != "cut"
                row.update(flags=flags, child_round=result.get("child_round"))
                if result["status"] == "failure":
                    old = log[path.name, record.get("draw", record.get("index"))]
                    assert old["round"] == row["child_round"]
                    assert old["conditions"] == " ".join(("not " if k in flags else "") + k for k in ("N1","N2","N3"))
                    assert not result["unexplained_gains"] and not result["unexplained_losses"]
                    assert old["shapes"] == {"twin family":len(result["twins"])}
            rows.append(row)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    report = dict(tables=table_check(), two_piece=split_witness(), sample=original_sample(args.limit))
    print(Counter((s["status"], s.get("child_round")) for s in report["sample"]))
    if args.save:
        (HERE / "comparison.json").write_text(json.dumps(report, separators=(",", ":")) + "\n")
