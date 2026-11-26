"""Check equality up to renaming and both orders of growth and exchange."""
import argparse
import json
from collections import Counter
from itertools import permutations
from pathlib import Path
from rebuild import grow, mask, multiplicities, places, preparation, ring, union

HERE = Path(__file__).resolve().parent


def holder_names(rows):
    groups = {}
    for i in places(union(rows)):
        holders = tuple(k for k, row in enumerate(rows) if (row >> i) & 1)
        groups.setdefault(holders, []).append(i)
    return groups


def renaming(source, target):
    if len(source) != len(target):
        return None
    left, right = holder_names(source), holder_names(target)
    if Counter(map(len, left.values())) != Counter(map(len, right.values())):
        return None
    for order in permutations(range(len(target))):
        keys = {group: tuple(sorted(order[i] for i in group)) for group in left}
        if any(len(names) != len(right.get(keys[key], ())) for key, names in left.items()):
            continue
        mapping = {a: b for group, names in left.items()
                   for a, b in zip(names, right[keys[group]], strict=True)}
        assert all(mask(mapping[i] for i in places(row)) == target[order[k]]
                   for k, row in enumerate(source))
        return dict(holders=order, distinctions=mapping)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sizes", nargs="+", type=int, choices=range(5, 9))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = json.loads((HERE/"rings.json").read_text())
    result = {}
    for n in args.sizes:
        grown_exchange = [mask(row) for row in cases[str(n)]["pinned"]["moves"]]
        start = ring(n)
        _, _, _, bare_exchange = preparation(start, True)
        assert bare_exchange == [(1 << n)-1]
        reversed_order = grow(bare_exchange)
        identity = renaming(grown_exchange, start)
        same_orders = renaming(grown_exchange, reversed_order) is not None
        result[n] = dict(bare_exchange=[list(places(row)) for row in bare_exchange],
                         reversed_sizes=[r.bit_count() for r in reversed_order],
                         rename_to_start=identity, orders_agree=same_orders,
                         exchange_holder_counts=dict(Counter(multiplicities(grown_exchange).values())))
        print(n, identity is not None, same_orders, result[n]["reversed_sizes"])
    if args.output:
        args.output.write_text(json.dumps(result, indent=1)+"\n")


if __name__ == "__main__":
    main()
