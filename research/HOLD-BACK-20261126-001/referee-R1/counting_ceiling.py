"""Post hoc identifiability check against every recorded birth in the four cap pairs.

The comparison ceiling allows one fresh distinction plus the minimum number of
binary distinctions needed to distinguish D requests. All inputs are local.
Identical allocations on every birth imply identical growth by induction.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fresh(p, d):
    floor = max(3-p, 1)
    capacity = 1 + (max(1, d)-1).bit_length()
    return max(floor, min(d, capacity))


def check(rows):
    n = Counter()
    demands = Counter()
    for row in rows:
        data = row["arms"]["cap"]
        for section, bins in [("unchanged", data["base_overlap"])] + [
                ("changed suffix", e["marked_suffix_overlap"]) for e in data["changes"]]:
            for kind, p, d, own, local, capped, occurrences in bins:
                assert capped == min(max(3-p, d, 1), 3)
                n[section] += occurrences
                n["different"] += occurrences * (fresh(p, d) != capped)
                demands[d] += occurrences
    out = dict(counts=n, demand_histogram=demands)
    out["next_demand_example"] = dict(p=2, D=5, counting_ceiling=fresh(2, 5), cap=3)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    files = ["threshold_pilot.jsonl"]
    if not parser.parse_args().pilot:
        files.append("threshold_sample.jsonl")
    rows = [json.loads(line) for name in files for line in (HERE/name).read_text().splitlines()]
    print(json.dumps(check(rows), indent=2))
