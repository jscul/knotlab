"""Determinism check (deviations.md C15): compare every result file of this experiment's output folder with a rerun
written to another folder (COPYING_OUT=<other> and another PYTHONHASHSEED), with the timing fields removed.

    determinism.py <other folder>

Writes determinism.json (in the main output folder): per file, equal or not, and the SHA-256 of the normalized
content of each side."""
import gzip
import hashlib
import json
import os
import sys

from cpcommon import OUT, write

TIMING_KEYS = {'resources', 'seconds', 'wall_seconds', 'cpu_seconds_sum_of_starts', 'slowest_starts', 'sec'}
FILES = ['gate.json', 'trace_two_knot_part.txt', 'run1.json', 'run2.json', 'run3.json', 'run4.json',
         'run5_census_check.json', 'run5.json', 'run5_starts.json.gz', 'run6.json', 'run6_trace.txt', 'summary.json']


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if k not in TIMING_KEYS}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def normalized(path):
    if path.endswith('.txt'):
        with open(path, 'rb') as f:
            return f.read()
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        return json.dumps(strip(json.load(f)), sort_keys=True).encode()


def main():
    other = sys.argv[1]
    rows = {}
    for name in FILES:
        a, b = os.path.join(OUT, name), os.path.join(other, name)
        if not (os.path.exists(a) and os.path.exists(b)):
            rows[name] = {'equal': False, 'missing': [p for p in (a, b) if not os.path.exists(p)]}
            continue
        na, nb = normalized(a), normalized(b)
        rows[name] = {'equal': na == nb, 'sha256_main': hashlib.sha256(na).hexdigest(),
                      'sha256_rerun': hashlib.sha256(nb).hexdigest(), 'bytes': len(na)}
        print('%-26s %s' % (name, 'identical' if na == nb else 'DIFFERENT'), flush=True)
    out = {'files': rows, 'all_identical': all(r['equal'] for r in rows.values()),
           'rerun_folder': os.path.abspath(other), 'rerun_hash_seed': os.environ.get('RERUN_HASHSEED'),
           'ignored_keys': sorted(TIMING_KEYS)}
    print('all identical:', out['all_identical'])
    write('determinism.json', out)


if __name__ == '__main__':
    main()
