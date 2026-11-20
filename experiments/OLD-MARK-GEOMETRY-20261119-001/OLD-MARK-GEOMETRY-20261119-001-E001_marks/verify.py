"""Reconcile the independently produced records on the same old physical marks."""
from collections import Counter
from hashlib import sha256
from itertools import accumulate, combinations
from pathlib import Path
import gzip
import json

from sources import cases

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def read(stem):
    return json.loads((DATA / (stem + ".json")).read_text())


def distances(frame):
    return {(i, j): value for i, j, value, *_ in frame["pairs"]}


def first_layer():
    records = read("bond_first")["cases"]
    shared = list(combinations(range(16), 2))
    compared = 0
    for source, case in records.items():
        spec = cases()[source]
        degree = Counter(holder for meeting in spec["meetings"] for holder in meeting)
        opens = [size - degree[v] for v, size in enumerate(spec["sizes"])]
        seams = case["roles"]["seams"]
        source_cost = distances(case["source"])
        for assignment in case["assignments"].values():
            frame = case["age_one_by_activity"][assignment["activity_id"]]
            active = set(frame["active_knots"])
            obtained = distances(frame)
            for i, j in shared:
                interval = range(i + 1, j + 1)
                shared_per_seam = 4 if source == "J1x2" else 2
                initial = 1 + sum(opens[v] + shared_per_seam * (v in seams) for v in interval)
                assert source_cost[i, j] == initial
                change = 0
                for s in seams:
                    if s - 1 in interval and s + 1 in interval:
                        if source == "J1x2":
                            ring = case["roles"]["rings"][0]
                            change += 4 - len(active.intersection([ring[1], ring[-1]]))
                        elif s not in active:
                            change += 2
                assert obtained[i, j] == initial - change, (source, i, j)
                compared += 1
    assert compared == 9600
    tables = {}
    for tag in ("J1", "T4", "T8"):
        case = records[tag]
        tables[tag] = [distances(case["age_one_by_activity"][arm["activity_id"]])
                       for arm in case["assignments"].values()]
    quiet, loaded = tables["J1"]
    assert Counter(loaded[key] - value for key, value in quiet.items()) == {2: 75, 0: 135}
    assert {k for k in shared if loaded[k] != quiet[k]} == {(i,j) for i in range(3) for j in range(5,16)}
    for tag in ("T4", "T8"):
        blank, one, two, both = tables[tag]
        assert len(blank) == 325
        assert all(both[k] - one[k] - two[k] + blank[k] == 0 for k in blank)
    later = read("bond_age_two_partitions")["cases"]
    independent = read("certify")
    assert not independent["missing"]
    for mask, first in enumerate(tables["J1"]):
        for age in (1, 2):
            assert distances(later[str(mask)][str(age)]) == first
            records = independent["ages"][str(age)]["pairs"]
            assert len(records) == len(shared)
            arm = "loaded" if mask else "quiet"
            assert all(row[arm]["bond_distance"] == first[tuple(row["path_positions"])] for row in records)
    return compared


def later_bonds():
    later = read("bond_later")["cases"]["J1"]
    for mask, expected in (("0", (13,13,13)), ("1", (15,15,12))):
        for age, value in zip((2,3,4), expected, strict=True):
            row = next(r for r in later[mask]["frames"][str(age)]["pairs"] if r[:2] == [2,5])
            assert row[2:4] == [value,value]
    seams = read("seam_cuts")
    for row in seams:
        seam_index = cases()[row["source"]]["roles"]["seams"].index(row["seam"])
        loaded = int(row["mask"]) & (1 << seam_index)
        p = row["proof"]
        assert p["bond_distance"] == (4 if loaded and row["age"] >= 4 else 7)
        assert p["cut_cost"] == p["bond_distance"] + 1
        assert min(x["lower_bound_cost"] for x in p["orientations"]) == p["cut_cost"]
        assert any(x.get("upper_witness",{}).get("cost") == p["cut_cost"] for x in p["orientations"])
    assert len(seams) == 126
    intervals = [row["interaction_bounds"] for case in read("bond_interaction")["cases"].values()
                 for rows in case["interactions"].values() for row in rows]
    assert len(intervals) == 24 and intervals.count([0,0]) == 14
    assert all(low <= 0 <= high for low, high in intervals)


def routes():
    path = DATA / "routes.json.gz"
    with gzip.open(path, "rt") as stream:
        receipt = json.load(stream)
    formula = read("ordinary_formula")
    assert formula["checked_first_layer_pairs"] == 9600
    count = 0
    for tag, case in receipt["cases"].items():
        for trace in case["activity_geometries"].values():
            for frame in trace["stages"].values():
                assert len(frame["pairs"]) == 120
                assert all(p["steps"] == p["j"] - p["i"] for p in frame["pairs"])
                assert all(sum(shell[0] for shell in p["shells"]) == frame["knots"] for p in frame["profiles"])
                count += len(frame["pairs"])
        for assignment, item in case["assignments"].items():
            frame = case["activity_geometries"][item["activity_mask"]]["stages"]["1"]
            for pair in frame["pairs"]:
                key = f"{pair['i']},{pair['j']}"
                assert pair["routes"] == formula["by_case"][tag][assignment][key]
    assert count == 20880
    single = receipt["cases"]["J1"]
    for mask, full, near, far in (("0",3432,14,58), ("1",2220,16,71)):
        stages = single["activity_geometries"][single["assignments"][mask]["activity_mask"]]["stages"]
        assert next(p for p in stages["7"]["pairs"] if [p["i"],p["j"]]==[0,15])["routes"] == full
        frame = stages["2"]
        pair = next(p for p in frame["pairs"] if [p["i"],p["j"]]==[2,5])
        totals = [list(accumulate(s[0] for s in frame["profiles"][pair[k]]["shells"]))
                  for k in ("union_profile", "fixed_profile")]
        assert [v[2] for v in totals] == [near, 9] and [v[6] for v in totals] == [far, far]
    final = read("last_routes")
    assert final["previous_routes_sha256"] == sha256(path.read_bytes()).hexdigest()
    assert final["target"]["complete_count"] == 3432
    assert all(c["literal_replay"]["agrees"] for c in final["controls"].values())
    return count


if __name__ == "__main__":
    comparisons = first_layer()
    later_bonds()
    print(f"{comparisons} first-layer bond formulas and {routes()} route profiles reconciled.")
