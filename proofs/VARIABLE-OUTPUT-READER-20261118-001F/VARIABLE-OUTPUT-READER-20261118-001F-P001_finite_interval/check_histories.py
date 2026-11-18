"""Validate the independent count of reachable parent sequences at each width."""
import argparse
import json
from pathlib import Path
import re
import sys


def read(source):
    records = {}
    for line in source:
        path, types, births, successors = line.split()
        match = re.fullmatch(r"width(\d+)\.txt", Path(path).name)
        assert match, path
        width = int(match[1])
        assert width not in records
        records[width] = {
            "types": int(types),
            "parent_sequences": int(births),
            "weighted_next_parent_sets": int(successors),
        }
    return records


def verify(records):
    assert records and set(records) == set(range(3, max(records) + 1))
    for width, rec in sorted(records.items()):
        expected = int(width == 3) + sum(
            records[w]["weighted_next_parent_sets"] for w in (width - 2, width - 3)
            if w in records
        )
        assert rec["parent_sequences"] == expected, (width, rec, expected)
        assert 0 <= rec["types"] <= rec["parent_sequences"]


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--compare", type=Path, help="Compare against an earlier saved balance.")
    options = args.parse_args()
    records = read(sys.stdin)
    verify(records)
    if 5 in records:
        removed = dict(records)
        removed[5] = {"types": 0, "parent_sequences": 0, "weighted_next_parent_sets": 0}
        try:
            verify(removed)
        except AssertionError:
            pass
        else:
            raise AssertionError("removing the only two-site type at width five escaped the check")
    result = {"widths": {str(w): record for w, record in sorted(records.items())}}
    if options.compare:
        assert result == json.loads(options.compare.read_text())
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
