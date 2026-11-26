"""List small sides by assigning holders to distinctions. Check the exact catalogue."""
import argparse
import itertools
import json
import time
from functools import cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CATALOGUE = next((HERE.parents[2] / "artifacts/REVIEW-LEADS-20261123-001C").glob("*"))
LAWS = range(3)  # even, odd, not-all-equal


@cache
def truth_sets(width, support):
    """Bit j of an integer records whether the knot allows word j."""
    accepted = [0, 0, 0]
    for word in range(1 << width):
        number = (word & support).bit_count()
        accepted[number % 2] |= 1 << word
        if 0 < number < support.bit_count():
            accepted[2] |= 1 << word
    return accepted


def build(shared, internal, size):
    public = 3 + shared
    width = public + internal
    one = [(k,) for k in range(size)]
    one_or_two = one + list(itertools.combinations(range(size), 2))
    full = (1 << (1 << width)) - 1
    counts = {}
    structures = 0
    for observed in itertools.product(one, repeat=public):
        for private in itertools.product(one_or_two, repeat=internal):
            holdings = [0] * size
            for pos, owners in enumerate(observed + private):
                for k in owners:
                    holdings[k] |= 1 << (width - pos - 1)
            if any(k.bit_count() not in (3, 4) for k in holdings):
                continue
            if holdings != sorted(holdings):
                continue
            same = [i for i in range(1, size) if holdings[i] == holdings[i - 1]]
            allocation = observed[1] == observed[2] and observed[0] != observed[1]
            supports = [truth_sets(width, k) for k in holdings]
            for laws in itertools.product(LAWS, repeat=size):
                if any(laws[i-1] >= laws[i] for i in same):
                    continue
                structures += 1
                words = full
                for law, support in zip(laws, supports):
                    words &= support[law]
                block = 1 << internal
                mask = (1 << block) - 1
                table = bytes(((words >> (row * block)) & mask).bit_count()
                              for row in range(1 << public))
                counts[table] = counts.get(table, False) or allocation
    return structures, counts


def census(shared, limit):
    counts, total = {}, 0
    for i in range(limit + 1):
        for k in (1, 2, 3):
            number, tables = build(shared, i, k)
            total += number
            for table, flag in tables.items():
                counts[table] = counts.get(table, False) or flag
    with np.load(CATALOGUE / f"sides_c{shared}_k3_i3.npz") as archive:
        expected = {table.astype('uint8').tobytes(): bool(flag)
                    for table, flag in zip(archive['T'], archive['alloc'])}
    if limit == 3:
        assert counts == expected
    else:
        assert set(counts) <= expected.keys()
    return dict(shared=shared, internal_limit=limit, structures=total,
                tables=len(counts), nonempty=sum(any(t) for t in counts),
                allocation=sum(counts.values()), archived_tables=len(expected),
                exact_tables_and_allocation_flags_match=counts == expected)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true")
    args = p.parse_args()
    start = time.process_time()
    results = [census(c, 2 if args.pilot else 3) for c in (1, 2)]
    print(json.dumps(dict(results=results, process_seconds=time.process_time()-start), indent=2))
