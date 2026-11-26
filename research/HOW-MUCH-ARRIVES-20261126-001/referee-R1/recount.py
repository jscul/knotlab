"""Recount the archive and compare the printed tables, using the frozen verdict rules."""
import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import islice
import json
from pathlib import Path
import re
from time import perf_counter

HERE = Path(__file__).resolve().parent
READINGS = ('name', 'sig0', 'sig1')
START_SIZES = {'two-touching': 2, 'chain3': 3, 'generator7': 7, 'ring5-eddy': 5,
               'ring5-bare': 5, 'ring7-bare': 7}


def roster():
    jobs = set()
    for start, size in START_SIZES.items():
        for law in ('nae', 'parity'):
            for i in range(size):
                jobs.add((start, 'mark', i, law))
                if start == 'generator7' and i == 1:
                    continue  # This knot has no loose distinction to give.
                for j in range(size):
                    if j != i:
                        jobs.add((start, 'move', (i, j), law))
            jobs.add((start, 'made', 2, law))
        for change, t in (('made', 4), ('pulse', 2), ('pulse', 4)):
            jobs.add((start, change, t, 'nae'))
        if start in ('chain3', 'two-touching'):
            jobs.add((start, 'pair', 2, 'nae'))
    for setting, steps, supplied in [('B1', range(1, 9), 'REC-ONE-FEWER'),
                                     ('B2', range(2, 6), 'CAP-3')]:
        for d in steps:
            jobs.update((setting, law, d) for law in ('ORD', supplied))
    return jobs


def verdict(damage, sizes):
    count = len(damage)
    if count < 8:
        return 'too few rounds'
    mid = count // 2  # Upper middle observation, including when rounds start after a mark.
    if not any(damage[mid:]):
        return 'dies out'
    if all(n > 0 and 20 * c >= 19 * n for c, n in zip(damage[-4:], sizes[-4:])):
        return 'takes over'
    if sizes[-1] <= sizes[mid]:
        return 'bounded' if damage[-1] <= damage[mid] else 'grows'
    if 2 * sizes[-1] >= 3 * sizes[mid] and damage[-1] <= damage[mid]:
        return 'weakens'
    return 'holds'


def show_counter(c):
    return ', '.join(f'{key} {c[key]}' for key in sorted(c))


def table_strings(lines, columns):
    return [[v.strip() for v in line.strip('|').split('|')]
            for line in lines if line.startswith('| ') and line.count('|') == columns + 1]


def audit(jobs, full):
    a_table = defaultdict(lambda: {r: Counter() for r in READINGS})
    a_shares = defaultdict(list)
    shell_rows = defaultdict(Counter)
    shell_tests = defaultdict(Counter)
    totals = defaultdict(Counter)
    power = defaultdict(Counter)
    hist = defaultdict(Counter)
    changed = defaultdict(Counter)
    examples = {}
    weaknesses = {}
    pulse_counts = Counter()
    pair_table = {}
    b_table = []
    actual_jobs = []
    validation = Counter()
    fixed = []
    for job in jobs:
        assert 'not run' not in job
        if 'setting' in job:
            setting, law, d = job['setting'], job['law'], job['d']
            actual_jobs.append((setting, law, d))
            items = job['marks'] if setting == 'B1' else job['pairs']
            first_rounds, first_shares, last_shares = [], [], []
            for label, item in items.items():
                rows = item['rows']
                for r in rows:
                    for reading in READINGS:
                        assert r[reading][0] - r[reading][1] == r["n'"] - r['n']
                first = next((r for r in rows if any(r['name'])), None)
                f = first['round'] if first else None
                assert f == item['first'] and len(rows) == item['rounds']
                first_rounds.append(f)
                def share(row):
                    return sum(row['sig1']) / (row['n'] + row["n'"]) if row['n'] + row["n'"] else 0
                if first:
                    first_shares.append(share(first))
                    last_shares.append(share(rows[-1]))
                if setting == 'B2':
                    b_table.append([law, str(d), label, str(f), f'{share(first):.2f}' if first else '-',
                                    f'{share(rows[-1]):.2f}', str(len(rows))])
            if setting == 'B1':
                b_table.append([law, str(d), f'{len(first_shares)} of {len(items)}', str(first_rounds),
                                f'{sum(first_shares)/len(first_shares):.2f}' if first_shares else '-',
                                f'{sum(last_shares)/len(last_shares):.2f}' if last_shares else '-'])
            continue

        start, change, law = job['start'], job['change'], job['knot law']
        at = job.get('at', job.get('round'))
        actual_jobs.append((start, change, tuple(at) if isinstance(at, list) else at, law))
        if change == 'pair':
            for reading in READINGS:
                c = Counter()
                for pair in job['pairs']:
                    x, y, both = pair['damage u, v, both'][reading]
                    if both < min(x, y):
                        label = 'less than either'
                    elif both < x + y:
                        label = 'less than the sum'
                    elif both > x + y:
                        label = 'more than the sum'
                    else:
                        label = 'the sum'
                    c[label] += 1
                pair_table[start, law, reading] = c
            continue
        kind = change if change in ('mark', 'move') else f'{change} {at}'
        key = start, kind, law
        cases = job.get('marks', [job])
        if 'marks' in job:
            assert job['marked'] == len(cases) == min(job['made'], 40)
        for case in cases:
            rows = case['rows']
            ident = f'{start} {change} {at} {law}' + (f" knot {case['knot']}" if 'knot' in case else '')
            assert rows and all(x['n'] == job['base counts'][x['round'] - 1] for x in rows)
            sizes = [x["n'"] + x['n'] for x in rows]
            alt_sizes = [x["n'"] for x in rows]
            mids = len(rows) // 2
            hist[law, change][rows[-1]['round']] += 1
            a_shares[key].append(float(Fraction(sum(rows[-1]['sig1']), sizes[-1])))
            all_verdicts = {}
            for reading in READINGS:
                for r in rows:
                    plus, minus = r[reading]
                    assert 0 <= plus <= r["n'"] and 0 <= minus <= r['n']
                    assert plus - minus == r["n'"] - r['n']
                    validation['directional identities'] += 1
                damage = [sum(r[reading]) for r in rows]
                v = verdict(damage, sizes)
                all_verdicts[reading] = v
                assert v == case['verdicts'][reading], (ident, reading, v)
                validation['archived verdicts'] += 1
                totals[law, reading][v] += 1
                a_table[key][reading][v] += 1
                forward = verdict([r[reading][0] for r in rows], alt_sizes)
                if forward != v:
                    changed[law, reading][f'{forward} -> {v}'] += 1
                    examples.setdefault((law, reading, forward, v), ident)
                if len(rows) >= 8 and 2*sizes[-1] >= 3*sizes[mids] and sizes[-1] > sizes[mids]:
                    power[law, reading]['passes size and length for weakens'] += 1
                if v == 'weakens':
                    extra = [r['round'] for r in rows if sum(r[reading]) != abs(r['n'] - r["n'"])]
                    weaknesses[ident, reading] = {'rounds exceeding count difference': extra,
                        'damages': damage, 'last n and changed n': [rows[-1]['n'], rows[-1]["n'"]]}
                if v == 'holds' and law == 'nae':
                    if damage[-1] * sizes[mids] < damage[mids] * sizes[-1]:
                        power[law, reading]['holds with falling middle-to-last share'] += 1
                    if damage[-1] <= damage[mids]:
                        power[law, reading]['holds without damage growing between compared rounds'] += 1
                    if damage[-1] == sizes[-1]:
                        power[law, reading]['holds with last share one'] += 1
                    if damage[-1] * sizes[mids] != damage[mids] * sizes[-1]:
                        power[law, reading]['holds with different middle and last share'] += 1
            if 'weakens' in all_verdicts.values():
                fixed.append((start, change, str(at), law, all_verdicts,
                              [(r['round'], sum(r['sig1']), n) for r, n in zip(rows, sizes)]))
            if change in ('made', 'pulse'):
                sh = rows[-1]['shells']
                hit = [int(k) for k, v in sh.items() if v[2]]
                available = [int(k) for k, v in sh.items() if v[0] + v[1]]
                width = max(hit) - min(hit) + 1 if hit else 0
                assert sum(v[0] for v in sh.values()) == rows[-1]['n']
                assert sum(v[1] for v in sh.values()) == rows[-1]["n'"]
                shell_rows[start, change, at, law][f'width {width}'] += 1
                front = bool(hit) and max(hit) == max(available)
                shell_rows[start, change, at, law]['damage at the last shell' if front else
                                                  'none at the last shell'] += 1
                stats = shell_tests[law, change]
                stats['cases'] += 1
                stats['damaged shell furthest'] += front
                stats['damaged shell nearest'] += min(hit) == min(available) and width == 1
                stats['multiple shells populated'] += len(available) >= 2
                stats['room to exceed width three'] += max(available) - min(available) >= 3
                stats['within two steps of furthest'] += max(available) - max(hit) <= 2
                stats['fits width one'] += width == 1
                if change == 'pulse':
                    pulse_counts['cases'] += 1
                    pulse_counts['unequal counts in final observation'] += rows[-1]['n'] != rows[-1]["n'"]
                    pulse_counts['reached round 16'] += rows[-1]['round'] == 16
    if full:
        assert len(set(actual_jobs)) == len(actual_jobs) and set(actual_jobs) == roster()
        lines = (HERE.parent/'tables.md').read_text().splitlines()
        assert lines[0] == f'# Jobs: {len(jobs)} read, 0 not run'
        computed = []
        for k, t in a_table.items():
            s = a_shares[k]
            computed.append([*k, str(len(s)), *(show_counter(t[r]) for r in READINGS),
                             f'{min(s):.2f} to {max(s):.2f}'])
        expected = [r for r in table_strings(lines, 8) if r[0] != 'start']
        assert sorted(computed) == sorted(expected)
        expected_b = [r for cols in (6, 7) for r in table_strings(lines, cols) if r[0] != 'law']
        assert sorted(b_table) == sorted(expected_b)
        archived_shells = {}
        archived_pairs = {}
        archived_fixed = []
        for l in lines:
            if l.startswith('- ('):
                key, values = l[2:].split(') ', 1)
                archived_shells[ast.literal_eval(key+')')] = ast.literal_eval(values)
            elif ' pairs: {' in l:
                label, counts = l[2:].split(' pairs: ')
                start, law, reading, n = label.split()
                table = ast.literal_eval(counts)
                assert sum(table.values()) == int(n)
                archived_pairs[start, law, reading] = table
            elif "sig1 damage/(n+n') by round:" in l:
                label, series = l.split(" sig1 damage/(n+n') by round: ")
                m = re.fullmatch(r'- (\S+) (\S+) (.+?) knot None (\S+) (\{.*\})', label)
                assert m
                archived_fixed.append((*m.groups()[:4], ast.literal_eval(m[5]), ast.literal_eval(series)))
        assert archived_shells == shell_rows and archived_pairs == pair_table
        assert sorted(archived_fixed, key=str) == sorted(fixed, key=str)
        validation.update({'ordinary table rows': len(computed), 'weakening series rows': len(fixed),
                           'shell table rows': len(shell_rows), 'pair table rows': len(pair_table),
                           'receiver table rows': len(b_table)})
    def pack(table):
        return {' | '.join(map(str, k)): v for k, v in sorted(table.items())}
    return {'jobs': len(jobs), 'verified': validation, 'verdicts': pack(totals),
            'last rounds by intervention': pack(hist), 'eligibility and residual verdict': pack(power),
            'one-way to both ways with same thresholds': pack(changed),
            'changed examples': pack(examples), 'weakens': pack(weaknesses),
            'shell opportunities': pack(shell_tests), 'pulse count check': pulse_counts,
            'ordinary table': pack(a_table),
            'last sig1 share ranges': pack({k:[min(v),max(v)] for k,v in a_shares.items()})}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    started = perf_counter()
    with gzip.open(HERE.parent/'runs.jsonl.gz', 'rt') as handle:
        records = [json.loads(line) for line in islice(handle, 10 if args.pilot else None)]
    result = audit(records, not args.pilot)
    if not args.pilot:
        (HERE/'recount.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(f'{len(records)} jobs in {perf_counter()-started:.4f} seconds')
