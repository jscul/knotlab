"""Compare the independent rebuild with the archived rows and frozen predictions."""

from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def archive_key(row):
    case = row["case"]
    if case == "adjacent":
        return "control: two adjacent knots of ring 0"
    reader = f'readers {row["choice"]}, rings '
    if case == "union":
        return reader + "0 and 2 against ring 1"
    a, b = row["rings"]
    return reader + f"{a} and {b}"


def compare_archive(stages, name):
    with gzip.open(HERE.parent / name, "rt") as raw:
        archived = [json.loads(line) for line in raw]
    squares = {}
    count = 0
    for rebuilt, original in zip(stages, archived, strict=True):
        for k_rebuilt, k_original in (("family", "family"), ("round", "round"),
                                      ("knot count", "knots"), ("distinction count", "distinctions")):
            assert rebuilt[k_rebuilt] == original[k_original]
        keys = {key for key, value in original.items() if isinstance(value, dict)}
        assert keys == {archive_key(row) for row in rebuilt["rows"]}
        for row in rebuilt["rows"]:
            key = archive_key(row)
            observed = dict(original[key])
            if "square" in observed:
                squares[(rebuilt["family"], rebuilt["round"], key)] = observed.pop("square")
            wanted = {"separated": row["separated"], "held": row["held"], "identities agree": True}
            for treatment, e in row["e"].items():
                key = f"e, middle {treatment}" if treatment != "only link" else "e, only the link distinction read for its change"
                wanted[key] = e
            assert observed == wanted, (rebuilt["family"], rebuilt["round"], archive_key(row))
            count += 1
    return count, squares


def count_predictions(stages):
    counts = Counter()
    distributions = defaultdict(Counter)
    zero_changes = []
    for stage in stages:
        loose_family = stage["extra loose at start"] is not None
        round_number = stage["round"]
        for row in stage["rows"]:
            case = row["case"]
            e = row["e"]
            triple = tuple(e[k] for k in ("unread", "changes", "values"))
            distributions[case][str(triple)] += 1
            if case == "pair":
                exception = loose_family and row["rings"] == [0, 1]
                override = exception and round_number == 0
                counts["prediction 1 rows"] += 1
                counts["prediction 1 as written"] += triple == (0, 1, 0)
                counts["prediction 1 with round-zero override"] += triple == ((0, 0, 0) if override else (0, 1, 0))
                if loose_family and round_number == 0:
                    counts["prediction 5 rows"] += 1
                    counts["prediction 5 matches"] += e["changes"] == (0 if exception else 1)
                if "only link" in e:
                    counts["prediction 2 rows"] += 1
                    counts["prediction 2 matches"] += e["only link"] == 1
                if "own with only link read" in row:
                    counts["own additional only-link rows"] += 1
                    counts["own additional only-link rows with e = 0"] += row["own with only link read"] == 0
                if e["changes"] == 0:
                    zero_changes.append({"family": stage["family"], "round": round_number, "choice": row["choice"],
                                         "rings": row["rings"], "value dimensions": [row["local dimensions"][k]["values"]
                                                                                   for k in ("A", "B", "AB")],
                                         **row["loose chain check"]})
            if case == "adjacent":
                counts["prediction 3 rows"] += 1
                counts["prediction 3 matches"] += triple == ((1, 1, 1) if round_number == 0 else (0, 1, 0))
            if case == "union" and round_number == 0:
                counts["prediction 4 rank rows"] += 1
                counts["prediction 4 rank matches"] += triple == (0, 2, 0)
            if row["separated"]:
                choice = row["choice"]
                counts[f"{choice} separated rows"] += 1
                counts[f"{choice} rows whose holdings meet"] += row["holders meet"]
    return {"predictions": counts, "e (unread, changes, values)": distributions, "zero change pair rows": zero_changes}


def main():
    stages = json.loads((HERE / "joined_results.json").read_text())
    assert len(stages) == 15
    frozen_count, frozen = compare_archive(stages, "rings_out_frozen.jsonl.gz")
    revised_count, revised = compare_archive(stages, "rings_out.jsonl.gz")
    assert frozen.keys() == revised.keys()
    square_changes = [{"family": family, "round": round_number, "reader": reader,
                       "before": frozen[family, round_number, reader], "after": revised[family, round_number, reader]}
                      for family, round_number, reader in revised if frozen[family, round_number, reader]
                      != revised[family, round_number, reader]]
    data = count_predictions(stages)
    data.update({"frozen rows matched apart from square": frozen_count, "revised rows matched apart from square": revised_count,
                 "square differences between archives": square_changes})
    (HERE / "joined_audit.json").write_text(json.dumps(data, indent=2) + "\n")
    print("Independent ranks matched all non-game fields in both archives:", frozen_count, revised_count)
    print(json.dumps(data["predictions"], sort_keys=True))


if __name__ == "__main__":
    main()
