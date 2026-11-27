"""Test joined copies of the earlier irredundant pair with differing loose sets.

The seven-name inputs are the two exact mask encodings of the pair in
MANY-VALUED-20261119-001/referee-R1/report.md. Test either input with no
change, one added loose distinction on any knot, or one shared distinction
split into two loose ones. Join two edited copies at one or two matched
loose distinctions. Only joins with a loose distinction remaining are read.
The choice of copies is unordered. The weighting gives each merged tuple of
labelled supports in this constructed eight-knot panel one count.
"""

import argparse
import json
import resource
import time
from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path

from census_tools import connected, tree
from nae_audit import AS_LIMIT, all_presentations, holdings, indices


HERE = Path(__file__).resolve().parent
RESULT = HERE / "nae_compositions.json"
OLD_PAIR = ((7, 56, 73, 54), (7, 56, 73, 118))


def variants():
    possibilities = set()
    for base in OLD_PAIR:
        used, doubled = holdings(base)
        new = 1 << used.bit_length()
        possibilities.add(base)
        for j in range(len(base)):
            rows = list(base)
            rows[j] |= new
            possibilities.add(tuple(rows))
        for i in indices(doubled):
            bit = 1 << i
            rows = list(base)
            j = next(j for j, row in enumerate(rows) if row & bit)
            rows[j] ^= bit | new
            possibilities.add(tuple(rows))
    return sorted(possibilities)


def join(left, right, a, b):
    names = {j: 1 << i for i, j in zip(a, b)}
    next_id = holdings(left)[0].bit_length()
    for j in indices(holdings(right)[0]):
        if j not in names:
            names[j] = 1 << next_id
            next_id += 1
    fresh = [sum(names[j] for j in indices(row)) for row in right]
    return tuple(sorted((*left, *fresh)))


def cases():
    seen = set()
    for left, right in combinations_with_replacement(variants(), 2):
        al, sl = holdings(left)
        ar, sr = holdings(right)
        loose_left = list(indices(al ^ sl))
        loose_right = list(indices(ar ^ sr))
        for width in (1, 2):
            if len(loose_left) + len(loose_right) <= 2 * width:
                continue
            for a in combinations(loose_left, width):
                for b in permutations(loose_right, width):
                    rows = join(left, right, a, b)
                    if rows in seen:
                        continue
                    seen.add(rows)
                    yield rows, width


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    limit = min([AS_LIMIT] + [x for x in (soft, hard) if x != resource.RLIM_INFINITY])
    resource.setrlimit(resource.RLIMIT_AS, (limit, hard))
    panel = list(cases())
    indices_to_run = range(0, len(panel), 83) if args.pilot else range(len(panel))
    totals, by_length, by_join = Counter(), Counter(), Counter()
    examples = []
    start = time.perf_counter()
    for i in indices_to_run:
        rows, width = panel[i]
        solutions, summary = all_presentations(rows)
        assert connected(rows) and all(r.bit_count() >= 3 for r in rows)
        assert all((r & s).bit_count() <= 2 for r, s in combinations(rows, 2))
        used, shared = holdings(rows)
        loose = used ^ shared
        assert loose and max((r & loose).bit_count() for r in rows) <= 2
        by_length[used.bit_length()] += 1
        by_join[width] += 1
        essential = summary["every rule essential"]
        full = summary["full local projections"]
        totals["joined inputs"] += 1
        totals["irredundant inputs"] += essential
        totals["irredundant inputs with an underfull local projection"] += essential and not full
        totals["inputs with at least two remaining loose distinctions"] += loose.bit_count() >= 2
        totals["inputs with at least two start families"] += len(tree(rows)[0]) >= 2
        totals["inputs with an alternate presentation under all sizes and counts"] += len(solutions) > 1
        if len(solutions) > 1:
            filtered = [p for p in solutions if all_presentations(p)[1]["every rule essential"]]
            totals["inputs with multiple irredundant presentations"] += len(filtered) > 1
            totals["inputs with different families among irredundant presentations"] += len({tree(p)[0] for p in filtered}) > 1
            examples.append({"rows": rows, "loose": list(indices(loose)), "all presentations": solutions,
                             "irredundant presentations": filtered})
    for key in ("inputs with multiple irredundant presentations",
                "inputs with different families among irredundant presentations"):
        totals.setdefault(key, 0)
    timing = {"checked": len(indices_to_run), "panel": len(panel),
              "seconds": round(time.perf_counter() - start, 4),
              "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    print(json.dumps({**timing, "starts with alternatives": len(examples)}))
    if not args.pilot:
        record = {"construction": __doc__.strip(),
                  "original seven-name inputs": OLD_PAIR,
                  "number of one-copy variants before joining": len(variants()),
                  "eight-knot inputs by distinction count": by_length,
                  "eight-knot inputs by number of joined distinctions": by_join,
                  "counts": totals, "starts with alternatives": examples}
        RESULT.write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    main()
