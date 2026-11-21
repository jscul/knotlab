"""Enumerate connected and disjoint sources and their native complete updates."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from itertools import product
import json
from math import factorial, prod
from pathlib import Path
import sys

from census_exact_rates import owners


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PRIOR = 'FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C'
PRIOR_CODE = ROOT / 'experiments' / PRIOR / f'{PRIOR}-E001_pair_births'
SMALL = 'READS-HOLDERS-SOURCES-20261120-001B'
TEN = 'THREE-READERS-AND-GROWTH-20261120-001B'
LAWS = ('nae', 'parity')
sys.path.insert(0, str(PRIOR_CODE))
sys.path.insert(0, str(ROOT / 'experiments/ORDINARY-DYNAMICS-20261120-001A'
                       / 'ORDINARY-DYNAMICS-20261120-001A-E001_ordinary'))
from census_reached import mask_of, reduced, width
from model import spanned
from end_operator import End, proposals, step


@dataclass(frozen=True)
class Source:
    width: int
    rows: tuple
    automorphisms: int


def load_cases(ticket, family):
    path = ROOT / 'artifacts' / ticket / f'{ticket}-E001_{family}' / 'census_cases.json.gz'
    with gzip.open(path, 'rt') as file:
        return json.load(file)


def connected_archive():
    series = load_cases(SMALL, 'irredundant')
    series['10'] = load_cases(TEN, 'state_recovery')
    return {law: {int(n): tuple(Source(int(n), tuple(tuple(s) for s in p['supports']),
                                        p['presentation_automorphisms'])
                                for state in cases[law] for p in state['presentations'])
                  for n, cases in series.items()}
            for law in LAWS}


def sizes(total, least=3):
    if total == 0:
        yield ()
    for first in range(least, total + 1):
        for rest in sizes(total - first, first):
            yield (first, *rest)


def selections(archive, n):
    for partition in sizes(n):
        ranges = [range(len(archive[q])) for q in partition]
        for indices in product(*ranges):
            if any(a == b and i > j for a, b, i, j in zip(partition, partition[1:], indices, indices[1:])):
                continue
            yield tuple(archive[q][i] for q, i in zip(partition, indices, strict=True))


def disjoint_rows(parts):
    at, all_rows = 0, []
    for piece in parts:
        all_rows.extend(tuple(at + i for i in row) for row in piece.rows)
        at += piece.width
    return tuple(all_rows)


def end_of(rows):
    loose = defaultdict(list)
    shared = defaultdict(set)
    for name, holding in owners(rows).items():
        if len(holding) == 1:
            loose[holding[0]].append(name)
        else:
            a, b = holding
            shared[a].add(b)
            shared[b].add(a)
    witness = tuple(v & loose.keys() for v in shared.values())
    return End({h: len(values) for h, values in loose.items()}, witness), loose


def following(rows):
    end, _ = end_of(rows)
    if not end.opens:
        return 'closed', 0
    shared = proposals(end)
    used = Counter(h for p in shared for h in p)
    if any(used[h] > value for h, value in end.opens.items()):
        return 'stall', 0
    return 'births', len(shared) + sum(length - used[h] for h, length in end.opens.items())


def advance(rows, law, reverse=False):
    end, loose = end_of(rows)
    # Compute the globally funded roster with the continuing floor. For parity
    # replace its provisional price when that actual input is already implied
    # by the entire old rowspace, also on a disjoint union.
    turn = step(end, 'nae')
    if turn.status != 'extend':
        return turn.status, rows, ()
    at = width(rows)
    available = {h: iter(sorted(names, reverse=reverse)) for h, names in loose.items()}
    basis = reduced(map(mask_of, rows)) if law == 'parity' else None
    made, births = [], []
    for k, (parents, ordinary_price) in enumerate(zip(turn.parents, turn.fresh, strict=True)):
        inputs = tuple(next(available[h]) for h in parents)
        price = ordinary_price
        if basis is not None and spanned(mask_of(inputs), basis):
            assert turn.demand[k] == 0
            price = 0
        made.append(tuple(sorted((*inputs, *range(at, at + price)))))
        births.append((parents, price))
        at += price
    assert all(next(stream, None) is None for stream in available.values())
    return 'births', (*rows, *made), tuple(births)


def all_stages(parts, law):
    source = stage = disjoint_rows(parts)
    n = width(source)
    denominator = prod(s.automorphisms for s in parts) * prod(factorial(k) for k in Counter(parts).values())
    assert factorial(n) % denominator == 0
    record = {'source_rows': source, 'source_width': n, 'source_parts_widths': [s.width for s in parts],
              'source_components': len(parts), 'labelled_source_multiplicity': factorial(n) // denominator,
              'attempts': [], 'stages': []}
    for age in range(1, 3 if n <= 8 else 2):
        old_size = len(stage)
        status, stage, births = advance(stage, law)
        record['attempts'].append(status)
        if status != 'births':
            break
        next_status, next_count = following(stage)
        record['stages'].append({'age': age, 'width': width(stage), 'rows': stage, 'youngest': tuple(range(old_size, len(stage))),
                                 'recorded_births': births, 'next_status': next_status, 'next_birth_count': next_count})
    return record


def stage_work():
    archive = connected_archive()
    output = {}
    for law, sources in archive.items():
        found = []
        for n in range(3, 11):
            records = [all_stages(parts, law) for parts in selections(sources, n)]
            found.extend(records)
            print(law, 'source width', n, 'eligible', len(records), flush=True)
        output[law] = found
    return output


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = stage_work()
    (OUTPUT / 'census_stages.json.gz').write_bytes(gzip.compress(json.dumps(records).encode(), mtime=0))


if __name__ == '__main__':
    main()
