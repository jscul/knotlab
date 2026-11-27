"""Compare the preserved and revised tables, then score the literal predictions."""

import argparse
import gzip
import json
from collections import Counter
from itertools import islice, zip_longest
from pathlib import Path
from time import process_time


def compare_records(directory, limit):
    changed = []
    counts = Counter()
    grouped = {}
    with gzip.open(directory / "rings_out_frozen.jsonl.gz", "rt") as before, \
            gzip.open(directory / "rings_out.jsonl.gz", "rt") as after:
        for original, revised in islice(zip_longest(before, after), limit):
            old, new = json.loads(original), json.loads(revised)
            counts["family_rounds"] += 1
            assert old.keys() == new.keys()
            for key, value in new.items():
                if old[key] != value:
                    prev, now = old[key].copy(), value.copy()
                    old_square, new_square = prev.pop("square"), now.pop("square")
                    assert old_square is None and new_square["cells certain"] == 9 and prev == now
                    changed.append([new["family"], new["round"], key])
                if not key.startswith("readers") or "against" in key:
                    continue
                counts["pair_rows"] += 1
                e = tuple(value["e, middle " + mode] for mode in ("unread", "values", "changes"))
                counts["literal_prediction_1"] += e == (0, 0, 1) and value["identities agree"]
                loose = "one loose" in new["family"]
                first_pair = key.endswith("rings 0 and 1")
                exception = loose and new["round"] == 0 and first_pair
                counts["prediction_1_with_prediction_5_override"] += (
                    e == (0, 0, int(not exception)) and value["identities agree"])
                if loose and new["round"] == 0:
                    counts["prediction_5_rows"] += 1
                    counts["prediction_5_matches"] += e[2] == int(not first_pair)
                group = grouped.setdefault(new["family"], Counter())
                group[e[2]] += 1
    return {"counts": dict(counts), "middle_changes_by_family": grouped,
            "only_changed_fields": changed}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    start = process_time()
    result = compare_records(Path(__file__).resolve().parents[1], args.limit)
    result["cpu_seconds"] = round(process_time() - start, 5)
    print(json.dumps(result, indent=2))
