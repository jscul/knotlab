"""Fresh census structure audit; only the explicitly allowed referee builder is reused.

Run from the repository root with .venv/bin/python -B. No study producer is
opened or imported. The theorem supplies predictions, not search outcomes.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import gzip
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / 'research/LEVEL-REACH-20261114-001/referee-R1/codex'
FORBIDDEN = tuple(ROOT / p for p in (
    'research/RULER-LEVEL-20261114-001/exploratory',
    'proofs/RULER-LEVEL-20261114-001A',
    'experiments/LEVEL-REACH-20261114-001A',
))


def deny_producer_python(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        path = Path(args[0]).resolve()
        if path.suffix in ('.py', '.pyc') and any(path.is_relative_to(d) for d in FORBIDDEN):
            raise RuntimeError(f'Forbidden producer-code read: {path}')


sys.addaudithook(deny_producer_python)
sys.path.insert(0, str(PRIOR))
from fresh_pattern import build, direct_build, level


def load_gz(path):
    with gzip.open(path, 'rt') as f:
        for line in f:
            yield json.loads(line)


def incidence_analysis(knots, nvars):
    """Detect cycles using knot-incidence union/find, including 2-knot cycles."""
    parent = list(range(nvars + len(knots)))
    rank = [0] * len(parent)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    cycles = 0
    for i, knot in enumerate(knots):
        assert len(knot) == len(set(knot)) == 3
        for v in knot:
            a, b = find(v), find(nvars + i)
            if a == b:
                cycles += 1
            else:
                if rank[a] < rank[b]:
                    a, b = b, a
                parent[b] = a
                if rank[a] == rank[b]:
                    rank[a] += 1
    components = len({find(v) for v in range(nvars)})
    # An independent incidence-count identity checks the computed cycle rank.
    assert cycles == 3 * len(knots) - (nvars + len(knots)) + components
    return {'acyclic': cycles == 0, 'cycle_rank': cycles, 'components': components}


def shortest_levels(knots, nvars, k0, targets):
    """Multi-source BFS on co-knotted distinctions; each knot traversal costs 1."""
    adj = [set() for _ in range(nvars)]
    for knot in knots:
        for v in knot:
            adj[v].update(x for x in knot if x != v)
    distance = [None] * nvars
    predecessor = [None] * nvars
    q = deque()
    for v in range((1 << k0) - 1, (1 << (k0 + 1)) - 1):
        distance[v] = 0
        q.append(v)
    while q:
        v = q.popleft()
        for w in sorted(adj[v]):
            if distance[w] is None:
                distance[w] = distance[v] + 1
                predecessor[w] = v
                q.append(w)
    result = []
    for n in targets:
        candidates = [v for v in range((1 << n) - 1, (1 << (n + 1)) - 1)
                      if distance[v] is not None]
        if not candidates:
            result.append({'distance': None, 'path': None})
            continue
        v = min(candidates, key=lambda x: (distance[x], x))
        path = [v]
        while predecessor[v] is not None:
            v = predecessor[v]
            path.append(v)
        result.append({'distance': distance[path[0]], 'path': path[::-1]})
    return result


def descending_reach(knots, k0, S):
    reachable = set(range((1 << k0) - 1, (1 << (k0 + 1)) - 1))
    result = []
    for n in range(k0, k0 + S):
        following = set()
        for knot in knots:
            lo = {v for v in knot if level(v) == n}
            hi = {v for v in knot if level(v) == n + 1}
            if lo & reachable:
                following.update(hi)
        reachable = following
        result.append(bool(reachable))
    return result


def theorem_a_form(key):
    placements = set(tuple(sorted(p)) for p in key[4])
    return len(placements) == 1 and sorted(t % 3 for t in next(iter(placements))) == [0, 1, 2]


def classify(row):
    # This is re-derived from the frozen outcome definitions, not summary code.
    if row['flags']['no_join']:
        return 'no join'
    if row['union'] == 'dead':
        return 'dead'
    values = [p['L_N'] for p in row['levels']]
    if 'none' in values:
        return 'no bond'
    if row['union'] != 'alive' or 'undecided' in values:
        return 'undecided'
    if values == [3, 4, 5, 6]:
        return 'chained'
    if all(isinstance(x, int) for x in values) and len(set(values)) == 1:
        return 'direct'
    return 'other'


def controls():
    cases = [([], 8, True), ([(0, 1, 2)], 8, True),
             ([(0, 1, 2), (2, 3, 4)], 8, True),
             ([(0, 1, 2), (3, 4, 5)], 8, True),
             ([(0, 1, 2), (0, 1, 3)], 8, False),
             ([(0, 1, 2), (2, 3, 4), (0, 4, 5)], 8, False)]
    data = []
    for knots, nv, expected in cases:
        actual = incidence_analysis(knots, nv)
        assert actual['acyclic'] == expected
        data.append({'knots': knots, 'expected_acyclic': expected, **actual})
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    parser.add_argument('--output', default='census.json')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    start = time.monotonic()
    src = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach'
    slim = list(load_gz(src / 'records_slim.jsonl.gz'))
    full = {}
    for envelope in load_gz(src / 'results.jsonl.gz'):
        assert envelope['status'] == 'ok'
        row = envelope['result']
        assert envelope['case'] == row['case'] and row['case'] not in full
        full[row['case']] = {
            'key': row['key'], 'union': row['union']['verdict'],
            'knot_count': row['knot_count'], 'memberships': row['memberships'],
            'levels': [(x['s'], x['components'], x['L_N'], x['L_target']) for x in row['levels']],
        }
    assert {r['case'] for r in slim} == set(full) and len(slim) == 1288
    rows = []
    cross = Counter()
    weight_cross = Counter()
    discrepancies = []
    for i, row in enumerate(slim[:args.limit]):
        recorded = full[row['case']]
        assert recorded['key'] == row['key']
        assert recorded['memberships'] == row['memberships']
        assert recorded['union'] == row['union']
        assert recorded['levels'] == [(x['s'], x['components'], x['L_N'], x['L_target']) for x in row['levels']]
        key = row['key']
        knots = build(key, 9)
        assert len(knots) == row['knot_count'] == recorded['knot_count']
        assert knots == sorted(set(knots))
        assert all(max(map(level, knot)) - min(map(level, knot)) <= 1 for knot in knots)
        no_join = not any(any(t % 3 == 0 for t in p) and any(t % 3 != 0 for t in p) for p in key[4])
        assert no_join == row['flags']['no_join']
        structure = incidence_analysis(knots, 1023)
        paths = shortest_levels(knots, 1023, 3, range(4, 8))
        distances = [p['distance'] for p in paths]
        chain = descending_reach(knots, 3, 4)
        assert all((d is not None and d >= s) or d is None for s, d in enumerate(distances, 1))
        assert chain == [d == s for s, d in enumerate(distances, 1)]
        assert [x['components'] for x in row['levels']] == [d is not None for d in distances]
        outcome = classify(row)
        # Metadata includes memberships from the original 4,000-draw build;
        # the frozen registered study kept only draw indices 0..1,999.
        w = sum(m['family'] == 'W_R' and m['index'] < 2000 for m in row['memberships'])
        a_form = theorem_a_form(key)
        if a_form:
            assert structure['acyclic'] and structure['components'] == 1 and all(chain)
        bucket = ('acyclic, chains at every s' if all(chain) else 'acyclic, some s without a chain') if structure['acyclic'] else 'cyclic'
        cross[outcome, bucket] += 1
        weight_cross[outcome, bucket] += w
        predicted = [d + 2 if d is not None else 'none' for d in distances] if structure['acyclic'] else None
        observed = [x['L_N'] for x in row['levels']]
        if predicted is not None and (predicted != observed or row['union'] != 'alive'):
            discrepancies.append({'case': row['case'], 'observed': observed, 'prediction': predicted, 'union': row['union']})
        # A direct bitwise builder is a second construction on a spread of keys.
        direct_checked = i % 53 == 0 or a_form and i % 7 == 0
        if direct_checked:
            assert knots == direct_build(key, 9)
        rows.append({'case': row['case'], 'key': key, 'weight': w, 'outcome': outcome,
                     'union': row['union'], 'knot_count': len(knots), **structure,
                     'descending_chain': chain, 'distance': distances,
                     'path_exists': [d is not None for d in distances], 'paths': [p['path'] for p in paths],
                     'theorem_a_form': a_form, 'prediction': predicted, 'observed_L': observed,
                     'direct_builder_checked': direct_checked})
        if (i + 1) % 100 == 0:
            print(json.dumps({'done': i + 1, 'seconds': round(time.monotonic() - start, 2)}), flush=True)
    rulers = [r for r in rows if r['outcome'] == 'chained']
    forests = [r for r in rows if r['acyclic']]
    uniform = [r for r in rulers if r['theorem_a_form']]
    explained = [r for r in rulers if r['acyclic']]
    summary = {
        'N': 9, 'k0': 3, 's': [1, 2, 3, 4], 'registered_count': 1288,
        'processed': len(rows), 'outcomes': dict(Counter(r['outcome'] for r in rows)),
        'cross_tab': [{'outcome': o, 'structure': b, 'count': c, 'weight': weight_cross[o, b]} for (o, b), c in sorted(cross.items())],
        'acyclic_descriptions': len(forests), 'cyclic_descriptions': len(rows) - len(forests),
        'acyclic_outcome_mismatches': discrepancies,
        'acyclic_paths_without_descending_chain': [{'case': r['case'], 'distance': r['distance'], 'chain': r['descending_chain']} for r in forests if any(p and not c for p, c in zip(r['path_exists'], r['descending_chain']))],
        'ruler_shares': {'rulers': len(rulers), 'ruler_weight': sum(r['weight'] for r in rulers),
                        'acyclic_at_N9': len(explained), 'acyclic_at_N9_weight': sum(r['weight'] for r in explained),
                        'theorem_a_all_depths': len(uniform), 'theorem_a_all_depths_weight': sum(r['weight'] for r in uniform)},
        'all_description_weight': sum(r['weight'] for r in rows),
        'weight_rule': 'Number of W_R memberships with index < 2000, as frozen in preregistration; E_R is unweighted.',
        'direct_builder_checks': sum(r['direct_builder_checked'] for r in rows),
        'controls': controls(), 'seconds': time.monotonic() - start,
        'peak_rss_MiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (src / 'records_slim.jsonl.gz', src / 'results.jsonl.gz', PRIOR / 'fresh_pattern.py')},
        'provenance': 'Fresh structural analysis and outcome aggregation; permitted prior referee builder reused. No producer Python opened; an audit hook rejects it.',
        'rows': rows,
    }
    (OUT / args.output).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('rows', 'controls')}, indent=2))


if __name__ == '__main__':
    main()
