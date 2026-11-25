"""Recount the frozen physical holder pairs under both knot laws."""

from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
from time import perf_counter

from check import Stage, classify


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FAMILY = HERE.parent
INPUT = ROOT / 'artifacts' / FAMILY.relative_to(ROOT / 'experiments')


def compact(row):
    return json.dumps(row, separators=(',', ':')).encode('utf-8')


def requests():
    rows = []
    seen = set()
    with (INPUT / 'requests.jsonl').open(encoding='utf-8') as source:
        for line in source:
            row = json.loads(line)
            key = physical_key(row)
            if key in seen:
                raise ValueError(f'duplicate physical request: {key}')
            if not (row['count'] > 0 and row['law'] in ('nae', 'parity')):
                raise ValueError(f'invalid frozen request: {row}')
            seen.add(key)
            rows.append(row)
    return rows


def physical_key(row):
    return (row['law'], row['system'], row['u'], row['v'], row['c'])


def read_supports(system):
    with gzip.open(INPUT / 'systems' / f'{system}.json.gz', 'rb') as source:
        raw = source.read()
    if hashlib.sha256(raw).hexdigest() != system:
        raise ValueError(f'frozen support has changed: {system}')
    return json.loads(raw)


def setup(params):
    global config
    case_plan = requests()
    if limit := params.get('limit'):
        case_plan = case_plan[:int(limit)]
    grouped = defaultdict(list)
    for row in case_plan:
        grouped[row['law'], row['system']].append(row)
    structural = {system: read_supports(system) for _, system in grouped}
    config = {'grouped': grouped, 'supports': structural, 'params': params}


def cases():
    for (law, system), rows in config['grouped'].items():
        yield f'{law}--{system}', (law, system, rows)


def run(case_id, payload):
    law, system, rows = payload
    start = perf_counter()
    stage = Stage(config['supports'][system])
    loaded = perf_counter()
    output = []
    times = defaultdict(Counter)
    for row in rows:
        first = perf_counter()
        u, v, c = row['u'], row['v'], row['c']
        if len(stage.rows) != row['knots']:
            raise ValueError(f'whole-stage node count changed: {physical_key(row)}')
        result = classify(stage, law, u, v, c)
        if result['a_width'] + result['b_width'] + 1 != row['width']:
            raise ValueError(f'private width disagrees with request: {physical_key(row)}')
        output.append({
            'law': law, 'system': system, 'u': u, 'v': v, 'c': c,
            'count': row['count'], 'width': row['width'], **result,
        })
        width = row['width']
        band = '1-14' if width <= 14 else '15-31' if width <= 31 else '32-49'
        times[band]['records'] += 1
        times[band]['seconds'] += perf_counter() - first
    classified = perf_counter()
    timing = {'law': law, 'system': system, 'records': len(rows), 'by_width': times,
              'setup_seconds': loaded - start, 'classification_seconds': classified - loaded,
              'seconds': classified - start, 'peak_self_rss_kib': getrusage(RUSAGE_SELF).ru_maxrss}
    if config['params'].get('assay') == '1':
        first = perf_counter()
        timing['temporary_receipt_bytes'] = len(compact(output))
        timing['serialization_seconds'] = perf_counter() - first
        timing['seconds'] = perf_counter() - start
        return timing
    return {'records': output, 'timing': timing}
