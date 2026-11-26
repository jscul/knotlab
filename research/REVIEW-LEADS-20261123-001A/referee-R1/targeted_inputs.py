"""Check every retained side of the eight seeded pools against its recorded knots."""
import argparse
import gzip
import json
import random
import time
from collections import Counter
from functools import cache
from pathlib import Path

import numpy as np

from side_catalogue import CATALOGUE


@cache
def columns(n):
    full = (1 << (1 << n)) - 1
    values = []
    for i in reversed(range(n)):
        count = 1 << i
        values.append((full // ((1 << (2*count))-1)) * ((1 << count)-1) << count)
    return full, values


@cache
def accepted(n, law, places):
    full, vals = columns(n)
    if law == 'nae':
        all_one, all_zero = full, full
        for pos in places:
            all_one &= vals[pos]
            all_zero &= full ^ vals[pos]
        return full ^ (all_zero | all_one)
    assert law in ('odd','even')
    odd = 0
    for pos in places:
        odd ^= vals[pos]
    return odd if law == 'odd' else full ^ odd


def project(struct, shared):
    internal = struct['internal']
    knots = struct['knots']
    assert 2 <= len(knots) <= 6 and 0 <= internal <= 9
    names = ['x1','x2','x3'] + [f's{i+1}' for i in range(shared)] + [f'h{i+1}' for i in range(internal)]
    n = len(names)
    holders = Counter()
    permitted = columns(n)[0]
    allocation = False
    for rule in knots:
        members = rule['members']
        assert len(members) in (3, 4) and len(set(members)) == len(members)
        holders.update(members)
        allocation |= 'x1' not in members and 'x2' in members and 'x3' in members
        permitted &= accepted(n, rule['law'], tuple(sorted(names.index(v) for v in members)))
    assert all(holders[v] == 1 for v in names[:3 + shared])
    assert all(1 <= holders[v] <= 2 for v in names[3 + shared:])
    block = 1 << internal
    mask = (1 << block) - 1
    table = [((permitted >> (i * block)) & mask).bit_count() for i in range(1 << (3 + shared))]
    return table, allocation


def check(file, pilot):
    with gzip.open(file, 'rt') as stream:
        saved = json.load(stream)
    with np.load(file.with_suffix('').with_suffix('.npz')) as archive:
        tables = archive['T']
    population = saved['structures']
    assert len(population) == len(tables)
    indices = random.Random(20261126).sample(range(len(tables)), 64) if pilot else range(len(tables))
    allocation_count = 0
    for i in indices:
        table, allocation = project(population[i]['struct'], saved['cut'])
        assert table == tables[i].ravel().tolist() and any(table)
        if saved['mode'] == 'alloc':
            assert allocation
        allocation_count += allocation
    return dict(pool=file.name.split('.')[0][6:], draw_seed=saved['seed'],
                draws_read=saved['tried'], admissible_draws_read=saved['valid'],
                retained_tables=len(tables), rebuilt_tables=len(indices),
                retained_witnesses_with_the_allocation_symmetry=allocation_count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    started = time.process_time()
    pools = [check(f, args.pilot) for f in sorted(CATALOGUE.glob('sides_*_t6*.json.gz'))]
    print(json.dumps(dict(pools=pools, process_seconds=time.process_time()-started), indent=2))
