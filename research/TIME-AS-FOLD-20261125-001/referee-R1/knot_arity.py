"""Count births with fewer than three places in the targeted replay."""

import json
import subprocess
import sys
from collections import Counter, defaultdict

from knot_counts import GROWTH_FILES, HERE, key, rows
from knot_replay import closure, grow, relation


def positive_test_counts(runs):
    tests = defaultdict(list)
    for row in rows('run4'):
        if row.get('verdict_C_iii') == 'holds':
            tests[key(row)].append(row)
    risks = {}
    for run in runs:
        config = tuple(run['configuration'])
        if config not in tests:
            continue
        paths = [(c['type'], c['after'], tuple(c['bar']), json.dumps(c['mask'])) for c in run['comparisons']
                 if c['under_three_places']]
        if paths or run['original_under_three_places']:
            risks[config] = (bool(run['original_under_three_places']), set(paths))
    records = {key(row): row for name in GROWTH_FILES for row in rows(name) if key(row) in risks}
    reports = []
    for config, (source_affected, paths) in risks.items():
        # No ancillary bar had a new two-place birth. Their identical comparison paths
        # use the source or an ordinary bar, which are already covered here.
        assert all(role in ('B', 'M', 'X barred') for role, _, _, _ in paths)
        series_at = {(s['t0'], tuple(s['P0'])): s for s in records[config]['nopast_series']}
        growth, _, _ = grow(config)
        for test in tests[config]:
            exact = []
            t_j = test['t_j']
            x = tuple(test['X'])
            if ('X barred', t_j, x, 'null') in paths:
                exact.append(['X barred', t_j])
            series = series_at[test['t0'], tuple(test['P0'])]
            ticks = {t[0]: tuple(t[1]) for t in series['ticks']}
            for comparison in test['bars']:
                tick = comparison['t_bar']
                part = ticks[tick]
                now = growth[tick]
                x_desc = closure(now.parents, x, len(growth[t_j].places))
                barred = tuple(u for u in part if u not in x_desc)
                mask = (tuple(sorted(x_desc)), part, len(now.places))
                for label, desc in [('B', ('B', tick, barred, 'null')),
                                    ('M', ('M', tick, (), json.dumps(mask)))]:
                    if desc in paths:
                        exact.append([label, tick])
            if source_affected or exact:
                reports.append({'config': config, 't_j': t_j, 'P_j': test['P_j'], 'X': x,
                                'source': source_affected, 'comparisons': exact})
    return {'all_positive_tests': sum(map(len, tests.values())),
            'source_or_comparisons': len(reports),
            'source_or_unmasked_comparisons': sum(r['source'] or any(role != 'M' for role, _ in r['comparisons'])
                                                  for r in reports),
            'comparisons': sum(bool(r['comparisons']) for r in reports),
            'source_only': sum(r['source'] and not r['comparisons'] for r in reports),
            'source_or_comparison_details': reports}


def main():
    runs = json.loads((HERE / 'knot_comparisons.json').read_text())
    data = Counter()
    roles = Counter()
    for run in runs:
        original = run['original_under_three_places']
        data['original_rules'] += len(original)
        data['original_runs'] += bool(original)
        if original:
            data['positive_tests_in_original_runs'] += run['tests']
        distinct = {(c['after'], c['last_round'], tuple(c['bar']), json.dumps(c['mask'])): c
                    for c in run['comparisons']}
        affected = [c for c in distinct.values() if c['under_three_places']]
        data['source_runs_with_affected_comparison'] += bool(affected)
        data['comparison_paths'] += len(affected)
        data['comparison_rules'] += sum(len(c['under_three_places']) for c in affected)
        roles.update(c['type'] for c in affected)

    config = ('main', 'Ring(5,3)', 'COPY-LAW(OFFSHOOT)', 'STEPS-2', 'BY-COUNT', 'parity')
    a, fresh, _ = grow(config, through=9)
    first_made = next(u for u, places in enumerate(a[-1].places) if len(places) < 3)
    view = relation(a[-1].places, a[-1].places[first_made])
    assert len(view['places']) == 2 and set(view['allowed_words']) == {'00', '11'}
    cli = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', '~a b; a ~b',
                          '--loops', 'a', '--contact', 'b', '--json'], text=True, capture_output=True, check=False)
    refusal = cli.stderr.splitlines()[-1]
    assert cli.returncode != 0 and 'a knot binds at least two loops' in refusal
    return {'counts': data, 'affected_paths_by_role': roles, 'positive_tests': positive_test_counts(runs),
            'example': {'configuration': config, 'birth': first_made, 'made': a[-1].born[first_made],
                        'parents': a[-1].parents[first_made], 'fresh': fresh[first_made - len(a[0].places)],
                        'projection': view, 'canonical_check': refusal}}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
