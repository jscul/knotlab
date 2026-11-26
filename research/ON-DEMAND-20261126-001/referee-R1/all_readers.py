"""Look for induced shortages on the actual frozen starts, including other reader choices."""

import argparse
from collections import Counter
from functools import cache
from itertools import combinations, islice
import json
from pathlib import Path
import resource
import time

from growth import grow, joins
from replay_inputs import cases, HORIZONS

HERE = Path(__file__).resolve().parent


def examine(case, counts):
    record = case.record
    if "not read" in record:
        counts["unread starts skipped"] += 1
        return []
    law = record["laws"]["nae"]
    if law["end"] == "stall":
        counts["original stalls skipped"] += 1
        return []
    last = int(law["rounds read"])
    counts["funded full starts"] += 1
    full = case.roster
    live = frozenset(full.loose)

    @cache
    def shortages(region):
        owed = Counter(k for group in joins(region, full.blocks) for k in group)
        return {k: [full.loose[k], owed[k]] for k in sorted(region) if owed[k] > full.loose[k]}

    @cache
    def full_first():
        return grow(full, 1, "nae").rows[0]

    large = [set(g) for g in joins(live, full.blocks) if len(g) >= 3]
    for t, region in case.h2 + case.admissions:
        if t <= last:
            counts["frozen H2 checks"] += 1
            counts["frozen H2 cuts a large group"] += any(g & region and g - region for g in large)
            counts["frozen H2 gives a shortage"] += bool(shortages(region))
    counts["reader choices"] += len(live)
    findings = []
    for reader in sorted(live):
        steps = full.steps_from(reader)
        for t in range(1, last + 1):
            region = frozenset(k for k, s in steps.items() if s <= t + 1)
            counts["reader and horizon comparisons"] += 1
            counts["proper reach comparisons"] += region != live
            if shortages(region):
                findings.append((reader, t, region, "prescribed reach"))
        within_two = frozenset(k for k, s in steps.items() if s <= 2)
        if case.population == "census6":
            rest = live - within_two
            for size in range(len(rest) + 1):
                for additions in combinations(sorted(rest), size):
                    region = within_two.union(additions)
                    counts["all two-step supersets by reader in six-knot sample"] += 1
                    if shortages(region):
                        findings.append((reader, 1, region, "superset in six-knot sample"))
        for omitted in sorted(live - within_two):
            region = live - {omitted}
            if region == within_two:
                continue
            counts["strict supersets missing one knot at round one"] += 1
            if reader == case.reader:
                counts["such supersets for registered reader"] += 1
            if shortages(region):
                findings.append((reader, 1, region, "strict superset missing one knot"))
    counted = []
    for reader, t, region, kind in findings:
        assert grow(full.restrict(region), 1, "nae").end == "stall"
        births = [b for b in full_first() if (b.ancestry >> reader) & 1]
        assert births
        counted.append({"index":case.index, "reader":reader, "registered_reader":case.reader,
                        "round":t, "kind":kind, "short_loose_and_owed":shortages(region),
                        "omitted": sorted(live - region), "full_first_reader_births":len(births)})
    return counted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (900 << 20, 900 << 20))
    begin = time.monotonic()
    data = {}
    for population in HORIZONS:
        counts = Counter()
        draws = cases(population)
        evidence = []
        for case in islice(draws, 3 if args.pilot else None):
            evidence += examine(case, counts)
        data[population] = {"counts": counts, "funding_failures": evidence}
    data["seconds"] = round(time.monotonic() - begin, 4)
    output = HERE / ("all_readers_pilot.json" if args.pilot else "all_readers.json")
    output.write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
