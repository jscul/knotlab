"""Run the canonical knot test on the flagged constituents of the seven sampled parity starts."""
import argparse
import gzip
import json
import os
import subprocess
import sys
from itertools import product
from pathlib import Path
from time import perf_counter

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def check(stars, target, law):
    clauses = []
    for knot in stars:
        for bits in product((0, 1), repeat=len(knot)):
            forbidden = sum(bits) % 2 == 1 if law == 'parity' else len(set(bits)) == 1
            if forbidden:
                clauses.append(' '.join(('~' if b else '') + f'x{i}' for i, b in zip(knot, bits)))
    visible = [f'x{i}' for i in stars[target]]
    others = sorted({f'x{i}' for knot in stars for i in knot} - set(visible))
    cmd = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', '; '.join(clauses),
           '--loops', *visible[:-1], '--contact', visible[-1], '--witnesses', *others, '--json']
    answer = subprocess.run(cmd, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'tools'}, check=True,
                            capture_output=True, text=True)
    return json.loads(answer.stdout)


def main(pilot):
    started = perf_counter()
    census = json.loads((OUT / 'sample_check.json').read_text())
    flagged = sorted(census['current_laws']['parity']['not_admitted'], key=lambda x: x['index'])
    by_id = {r['index']: list(map(int, r['knot_test'])) for r in (flagged[:1] if pilot else flagged)}
    result = []
    with gzip.open(OUT.parent / 'grown_fresh_parity.jsonl.gz', 'rt') as stream:
        for r in map(json.loads, stream):
            for i in by_id.get(r['index'], []):
                pair = {law: check(r['stars'], i, law) for law in ['parity', 'nae']}
                assert not pair['parity']['is_knot'] and pair['nae']['is_knot']
                result.append({'census index': r['index'], 'starting rules': r['stars'], 'tested rule position': i,
                               'by law': pair})
    assert len(result) == sum(map(len, by_id.values()))
    target = OUT / ('admission_pilot.json' if pilot else 'admission.json')
    target.write_text(json.dumps({'seconds': perf_counter()-started, 'checks': result}, indent=2) + '\n')
    print(target.name, len(result), round(perf_counter() - started, 3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    main(parser.parse_args().pilot)
