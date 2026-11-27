"""Check the closed archive against an exhaustive enumeration by discovery order."""

import argparse
from itertools import combinations, islice, permutations
import json
from pathlib import Path
import time

from recount_run import CLOSED, records


def incoming_bits(n):
    """Enumerate simple connected cubic meeting patterns in breadth-first order."""
    incoming = [0] * n

    def extend(current, discovered, code):
        if current == n:
            yield code
            return
        require = 3 - incoming[current]
        existing = [i for i in range(current + 1, discovered) if incoming[i] < 3]
        for n_fresh in range(min(require, n - discovered) + 1):
            next_discovered = discovered + n_fresh
            if next_discovered == current + 1 and next_discovered < n:
                continue
            new = tuple(range(discovered, next_discovered))
            for also in combinations(existing, require - n_fresh):
                others = new + also
                bits = sum(1 << (n * current + member) for member in others)
                for member in others:
                    incoming[member] += 1
                yield from extend(current + 1, next_discovered, code | bits)
                for member in others:
                    incoming[member] -= 1

    yield from extend(0, 1, 0)


def archived_labels(links, n):
    neighbors = [set() for _ in range(n)]
    for a, b in links:
        if a == b or b in neighbors[a]:
            raise ValueError("closed archive is not simple")
        neighbors[a].add(b)
        neighbors[b].add(a)
    if any(len(adj) != 3 for adj in neighbors):
        raise ValueError("closed archive is not cubic")

    def extend(queue, expanded):
        if len(queue) == n:
            inv = {member: i for i, member in enumerate(queue)}
            yield sum(1 << (n * min(inv[a], inv[b]) + max(inv[a], inv[b])) for a, b in links)
            return
        if expanded == len(queue):
            return
        for extension in permutations(neighbors[queue[expanded]].difference(queue)):
            yield from extend(queue + extension, expanded + 1)

    return {code for first in range(n) for code in extend((first,), 0)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="time a prefix at the same size")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    start = time.perf_counter()
    known = {}
    records_seen = 0
    for file, line, record in records(CLOSED / "out", "cubic_12_*.jsonl"):
        codes = archived_labels(record["links"], 12)
        if not codes or any(code in known for code in codes):
            raise ValueError(f"{file}:{line} is disconnected or duplicates another class")
        known.update(dict.fromkeys(codes, (file, line)))
        records_seen += 1
    generated = set(islice(incoming_bits(12), args.limit))
    if not generated <= known.keys():
        raise ValueError("closed archive lacks a generated label")
    if args.limit is None and generated != known.keys():
        raise ValueError("closed archive contains a label missed by generation")
    result = {
        "knots": 12,
        "archived_isomorphism_classes": records_seen,
        "archived_breadth_first_labels": len(known),
        "generated_breadth_first_labels": len(generated),
        "generated_isomorphism_classes": len({known[code] for code in generated}),
        "prefix": args.limit,
        "agreement_of_complete_label_sets": generated == known.keys(),
        "wall_seconds": time.perf_counter() - start,
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
