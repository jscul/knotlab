"""Compare every registered small numbering by an explicit renaming of the two structures."""

import argparse
from collections import Counter, defaultdict
from itertools import permutations
import json
from pathlib import Path
import resource
from time import perf_counter

from growth import Law, run

HERE = Path(__file__).resolve().parent
TICKET = HERE.parents[1] / (HERE.parent.name + "A")
STARTS = json.loads((TICKET / "starts.json").read_text())["starts"]
ROWS = json.loads((TICKET / "laws.json").read_text())["recorded"][:5]


def signature(state, rename):
    return Counter((tuple(sorted(rename[k] for k in holders)), d in state.barred)
                   for d, holders in state.holders.items())


def check(original, other, order):
    rename = dict(enumerate(order))
    for left, right in zip(original.rounds, other.rounds, strict=True):
        available = defaultdict(list)
        for b in left.births:
            available[tuple(sorted(b.parents))].append(b.knot)
        for b in right.births:
            parent_ids = tuple(sorted(rename[k] for k in b.parents))
            rename[b.knot] = available[parent_ids].pop()
        if any(available.values()):
            return False
    if len(rename) != len(original.structure.stars) or len(set(rename.values())) != len(rename):
        return False
    identity = range(len(original.structure.stars))
    return signature(original.structure, identity) == signature(other.structure, rename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1_500_000_000,1_500_000_000))
    t = perf_counter()
    results = {}
    for name in ("LONE-THREE","LONE-FOUR","TWO-KNOT","TRIANGLE"):
        stars = STARTS[name]["stars"]
        size = len(set().union(*stars))
        counts = Counter()
        inputs = set()
        for law in ROWS:
            for form in ("PU","PB","BB"):
                variant = Law.from_record(law,form=form)
                base = run(stars,variant,4)
                for order in permutations(range(len(stars))):
                    # Equal sorted input lists have identical computation and the same required start-knot map.
                    checked = {}
                    for mapping in permutations(range(size)):
                        mapped = tuple(tuple(sorted(mapping[i] for i in stars[k])) for k in order)
                        inputs.add(mapped)
                        if mapped not in checked:
                            checked[mapped] = check(base, run(mapped,variant,4),order)
                            counts["constructive_checks"] += 1
                        counts["numberings_with_form_and_law"] += 1
                        if not checked[mapped]:
                            counts["failures"] += 1
                        if args.pilot and counts["numberings_with_form_and_law"] == 5:
                            break
                    if args.pilot: break
                if args.pilot: break
            if args.pilot: break
        counts["distinct_numbered_start_lists"] = len(inputs)
        results[name] = dict(counts)
    if not args.pilot:
        (HERE/"numbering_counts.json").write_text(json.dumps(results,indent=2)+"\n")
    print("seconds",round(perf_counter()-t,3), results)

if __name__ == "__main__":
    main()
