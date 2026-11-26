"""List large sides by holder choices, counting the names suppressed during enumeration."""
import argparse
import itertools
import json
import math
import random
import time
from collections import Counter
from pathlib import Path

import numpy as np

from side_catalogue import CATALOGUE, truth_sets


def public_owners(knots, public):
    # Number the knots in the order of their first public distinction.
    possibilities = []
    for assignment in itertools.product(range(knots), repeat=public):
        used = 0
        for knot in assignment:
            if knot > used:
                break
            used = max(used, knot + 1)
        else:
            possibilities.append((assignment, used))
    return possibilities


def collect(shared, internal, knots, pilot):
    public = 3 + shared
    width = internal + public
    full = (1 << (1 << width)) - 1
    block = 1 << internal
    mask = (1 << block) - 1
    owner_sets = [(k,) for k in range(knots)] + list(itertools.combinations(range(knots), 2))
    private = []
    for pattern in itertools.combinations_with_replacement(range(len(owner_sets)), internal):
        holdings = [0] * knots
        for pos, entry in enumerate(pattern):
            for k in owner_sets[entry]:
                holdings[k] |= 1 << pos
        multiplicity = math.factorial(internal) // math.prod(math.factorial(v) for v in Counter(pattern).values())
        private.append((holdings, multiplicity))
    assignments = public_owners(knots, public)
    if pilot:
        assignments = random.Random(20261126).sample(assignments, min(4, len(assignments)))
    counts, ordered = {}, 0
    for assignment, used in assignments:
        visible = [0] * knots
        for index, k in enumerate(assignment):
            visible[k] |= 1 << (width - 1 - index)
        allocation = assignment[1] == assignment[2] != assignment[0]
        for hidden, multiplicity in private:
            holdings = [left | right for left, right in zip(visible, hidden)]
            if any(k.bit_count() not in (3, 4) for k in holdings):
                continue
            lawsets = [truth_sets(width, k) for k in holdings]
            ties = [(i, j) for i, j in itertools.combinations(range(knots), 2)
                    if holdings[i] == holdings[j]]
            # All ordered distinct rules will be divided by knots! at the end.
            for laws in itertools.product(range(3), repeat=knots):
                if any(laws[i] == laws[j] for i, j in ties):
                    continue
                ordered += multiplicity * math.perm(knots, used)
                words = full
                for accepted, law in zip(lawsets, laws):
                    words &= accepted[law]
                table = bytes(((words >> (i * block)) & mask).bit_count() for i in range(1 << public))
                counts[table] = counts.get(table, False) or allocation
    if not pilot:
        assert ordered % math.factorial(knots) == 0
    return counts, ordered // math.factorial(knots)


def run(shared, pilot):
    results, total = {}, 0
    for i in range(6):
        for k in (1, 2, 3, 4):
            if 3*k > 3+shared+2*i or 4*k < 3+shared+i:
                continue
            values, n = collect(shared, i, k, pilot)
            total += n
            for t, flag in values.items():
                results[t] = results.get(t, False) or flag
    with np.load(CATALOGUE / f'sides_c{shared}_k4_i5.npz') as archive:
        observed = {t.astype('uint8').tobytes(): bool(f) for t, f in zip(archive['T'], archive['alloc'])}
    assert all(t in observed and (not flag or observed[t]) for t, flag in results.items())
    if not pilot:
        assert results == observed
    return dict(shared=shared, labelled_structures=None if pilot else total,
                exact_tables=len(results), nonempty=sum(any(t) for t in results),
                allocation=sum(results.values()), equals_archive_with_flags=results == observed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    start = time.process_time()
    print(json.dumps(dict(results=[run(c, args.pilot) for c in (1, 2)],
                          process_seconds=time.process_time()-start), indent=2))
