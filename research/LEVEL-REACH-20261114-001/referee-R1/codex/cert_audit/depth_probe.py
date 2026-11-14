"""Depth extension of the frozen referee sample; outputs stay in this lane."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
SOURCE_PATHS = [PARENT / 'fresh_pattern.py', PARENT / 'fresh_search.py', PARENT / 'sample_plan.json']


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE_PATHS}


PRE_IMPORT_HASHES = hashes()
sys.path.insert(0, str(PARENT))
from fresh_pattern import build
from fresh_search import compile_existence, levels, search, Limit
SOURCE_HASHES = hashes()
assert PRE_IMPORT_HASHES == SOURCE_HASHES, 'source changed during import'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--count', type=int, default=3)
    parser.add_argument('--seconds', type=float, default=45)
    parser.add_argument('--spans', default='3,4')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    plan = json.loads((PARENT / 'sample_plan.json').read_text())
    sample = ([x for x in plan['sample'] if x['stratum'] == 'chained'][:12]
              + [x for x in plan['sample'] if x['stratum'] == 'direct3'][:2]
              + [x for x in plan['sample'] if x['stratum'] == 'slow'][:2])
    output = HERE / 'depth_results.jsonl'
    done = set()
    if output.exists():
        done = {(r['case'], r['N'], r['s']) for r in map(json.loads, output.read_text().splitlines())}
    selected = sample[args.start:args.start + args.count]
    spans = sorted({int(x) for x in args.spans.split(',')})
    assert spans and set(spans) <= {1, 2, 3, 4}, 'invalid spans'
    for index, entry in enumerate(selected, args.start):
        for N in (10, 11):
            wanted = [s for s in spans if (entry['case'], N, s) not in done]
            if not wanted:
                continue
            started = time.monotonic()
            knots = build(entry['key'], N)
            nvars = (1 << (N + 1)) - 1
            try:
                compilation = compile_existence(knots, nvars, time.monotonic() + args.seconds, 8)
                failure = None
            except Limit as exc:
                compilation, failure = None, str(exc)
            compile_seconds = time.monotonic() - started
            for s in wanted:
                if failure:
                    result = {'L': 'undecided', 'exact': False, 'reason': failure, 'stats': {}}
                else:
                    A, B = levels(3, s)
                    result = search(knots, nvars, A, B, cap=10, seconds=args.seconds, precompiled=compilation)
                row = {'case': entry['case'], 'stratum': entry['stratum'], 'key': entry['key'],
                       'sample_index': index, 'incidence_forest_N9': entry.get('incidence_forest'),
                       'N': N, 's': s, 'study_N9': entry['study'][s-1],
                       'knots': len(knots), 'result': result, 'compile_seconds': compile_seconds,
                       'query_seconds_budget': args.seconds, 'width_limit': 8, 'cap': 10,
                       'loaded_source_sha256': SOURCE_HASHES, 'source_sha256_at_output': hashes(),
                       'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                       'peak_rss_mb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024}
                with output.open('a') as f:
                    f.write(json.dumps(row, separators=(',', ':')) + '\n')
                print(json.dumps({'case': entry['case'][:16], 'stratum': entry['stratum'],
                                  'N': N, 's': s, 'fresh': result['L'], 'exact': result['exact'],
                                  'seconds': result['stats'].get('seconds'), 'reason': result.get('reason'),
                                  'compile_seconds': compile_seconds}), flush=True)


if __name__ == '__main__':
    main()
