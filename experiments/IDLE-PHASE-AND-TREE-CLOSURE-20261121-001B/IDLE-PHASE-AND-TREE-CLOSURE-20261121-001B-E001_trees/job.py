"""Run the two physical readings for each decorated tree representative."""

from argparse import ArgumentParser
from collections import Counter
import gzip
import json

from representatives import OUT, SIZES, representatives
from representatives_growth import grow


LAWS = ('parity', 'nae')


def cases():
    for n in SIZES:
        for record in representatives(n):
            yield record['id'], record


def run(case_id, payload):
    assert payload['id'] == case_id
    return dict(payload, laws={law: grow(payload['founder_rows'], law) for law in LAWS})


def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(data, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (OUT / name).write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)


def print_size(n, cases_for_size):
    def count(law):
        unweighted = Counter(r['laws'][law]['termination'] for r in cases_for_size)
        weights = Counter()
        for r in cases_for_size:
            h = r['laws'][law]
            weights[h['termination']] += r['mass']
            weights['admitted'] += r['mass'] if h['positive'] else 0
        return dict(unweighted), dict(weights)

    print(n, len(cases_for_size), sum(r['labelled'] for r in cases_for_size), sum(r['mass'] for r in cases_for_size),
          {law: count(law) for law in LAWS}, flush=True)


def main():
    parser = ArgumentParser()
    parser.add_argument('--n', type=int, choices=SIZES)
    opt = parser.parse_args()
    all_cases = []
    sizes = SIZES if opt.n is None else (opt.n,)
    for n in sizes:
        evaluated = [run(r['id'], r) for r in representatives(n)]
        print_size(n, evaluated)
        all_cases.extend(evaluated)
    name = 'representatives.json.gz' if opt.n is None else f'representatives_n{opt.n}.json.gz'
    write(name, all_cases)


if __name__ == '__main__':
    main()
