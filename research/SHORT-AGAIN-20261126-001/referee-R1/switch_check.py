"""Recount the switch records and test the specified receiver against local alternatives.

Run from the repository with .venv/bin/python -B on this file, followed by
pilot, raw, route, changes, or swaps. Each command writes its own JSON here.
"""

import argparse
import gzip
import json
import resource
import time
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

from growth import STARTS, build, changes, grow


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
A = 'g7:122@0'
OWN = frozenset({'A'})
WAIT, RETIRE, SHOOT = 'CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT'
TREATMENTS = (WAIT, RETIRE, SHOOT)
SENDERS = (*STARTS, 'stub')


def load(filename):
    with gzip.open(SOURCE / filename, 'rt') as stream:
        return list(map(json.loads, stream))


def switched(counts):
    return next((r for r, count in enumerate(counts, 1) if count != r + 2), None)


def first(xs, ys):
    return next((r for r, (x, y) in enumerate(zip(xs, ys), 1) if x != y), None)


def loose(b):
    if b == 'stub':
        return 'stub'
    pattern = STARTS[b]
    occurrences = Counter(x for knot in pattern.knots for x in knot)
    return sum(occurrences[x] == 1 for x in pattern.knots[pattern.site])


def counts(g):
    return [len(r.own_births) for r in g.rows]


def strict(g):
    return [r.own_births for r in g.rows]


def run(b, d, cap='CAP-3', tr=WAIT, join='meeting', a=A, change=None,
        rounds=16, bound=3000, trace=False):
    return grow(build(a, b, d, join, change=change), cap, tr, rounds, bound, trace=trace)


def horizon(values):
    return dict(sorted(Counter(values).items()))


def called(rows):
    return [r for r in rows if r['join'] == 'meeting' and r['A'] == A]


def raw(rows):
    by = defaultdict(list)
    field_disagreements = []
    for r in rows:
        n = r['rounds']
        dep = switched(r['own births'])
        assert len(r['own births']) == len(r['A short']) == n
        if dep != r['leaves first way']:
            field_disagreements.append((r['A'], r['B'], r['d'], r['join'], r['law']))
        by[(*r['law'], r['join'], r['A'], r['d'])].append(r)
    published = {}
    verbs = {'waits': WAIT, 'retires': RETIRE, 'offshoots': SHOOT}
    for ln in (SOURCE / 'switch_table.md').read_text().splitlines():
        if ln.startswith('| CAP-'):
            _, cap, tr, join, site, d, dep, far, latest, _ = map(str.strip, ln.split('|'))
            published[cap, verbs[tr], join, 'g7:122@' + site, int(d)] = (dep, far, latest)
    assert set(published) == set(by)
    cells, table_disagreements = [], []
    for key, runs in by.items():
        assert Counter(r['B'] for r in runs) == Counter(SENDERS)
        dep = Counter(switched(r['own births']) for r in runs)
        far = [c for r in runs for c in r['changes'] if c['distance'] >= 3]
        hearings = [c['heard'] for c in far if c['heard'] is not None]
        labels = ', '.join(f"{x if x is not None else 'never'}: {dep[x]}"
                           for x in sorted(dep, key=lambda x: (x is None, x or 0)))
        tab = (labels, f'{len(hearings)} of {len(far)}', str(max(hearings, default='-')))
        if tab != published[key]:
            table_disagreements.append([*key, list(tab), list(published[key])])
        cells.append({'configuration': key, 'first departure': labels, 'heard from distance >= 3': len(hearings),
                      'tested from distance >= 3': len(far), 'latest first hearing': max(hearings, default=None),
                      'baseline horizons': horizon(r['rounds'] for r in runs),
                      'no-departure horizons': horizon(r['rounds'] for r in runs if switched(r['own births']) is None)})
    templates = defaultdict(set)
    repeated = Counter()
    link_marks = defaultdict(Counter)
    ep_by_d = defaultdict(Counter)
    horizon_null = Counter()
    for r in called(rows):
        cap, tr = r['law']
        if cap != 'CAP-3':
            continue
        d, b = r['d'], r['B']
        dep = switched(r['own births'])
        group = 'no departure' if dep is None else 'early' if dep == 2*d+1 else 'late' if dep == 2*d+3 else 'other'
        templates[b].add(group)
        if dep is None:
            horizon_null[r['rounds']] += 1
        elif tr == WAIT:
            repeated['waiting switched histories'] += 1
            repeated['histories with a missed alternating short round'] += any(
                bool(v) != bool((i-dep) % 2) for i, v in enumerate(r['A short'], 1) if i > dep)
        if tr != WAIT:
            continue
        for c in r['changes']:
            label = c['at']
            if 'B' in label:
                key = 'bar' if label.startswith('b') else 'add'
                ep_by_d[d][key + ' tested'] += 1
                ep_by_d[d][key + ' heard'] += c['heard'] is not None
            else:
                k = c['distance']
                key = 'link add' if label.startswith('L') else 'link bar, first' if k == 1 else 'link bar, later'
                expected = 2*k+1 if key == 'link add' else 1 if k == 1 else dep
                link_marks[key]['tested'] += 1
                link_marks[key]['heard'] += c['heard'] is not None
                link_marks[key]['matches predicted first hearing or silence'] += c['heard'] == expected
    sender_classes = defaultdict(list)
    for b, classes in templates.items():
        assert len(classes) == 1
        sender_classes[next(iter(classes))].append({'sender': b, 'loose at unjoined site': loose(b)})
    duplicate = STARTS['copier'] == STARTS['g3:22@0']
    return {'input rows': len(rows), 'reported switch field disagreements': field_disagreements,
            'published table cells': len(cells), 'published table disagreements': table_disagreements, 'cells': cells,
            'cap three, one-loose site, meeting, all lengths and treatments': {
                'class stable by sender': sender_classes, 'no-departure horizons': horizon_null,
                'two-knot bench part and sited census entry g3:22@0 literally equal': duplicate,
                'early entries versus distinct sited starts': [len(sender_classes['early']),
                    len({STARTS[s['sender']] for s in sender_classes['early']})],
                'own short after first departure': repeated,
                'both signs at sender knots by length, waiting': ep_by_d,
                'additions and bars at link knots, waiting': link_marks}}


def timed_pilot():
    args = [
        ('g6:123@1', 3, 'CAP-3', WAIT, 16, 3000, True),
        ('g7:122@0', 3, 'CAP-3', RETIRE, 16, 3000, True),
        ('g7:113@0', 6, 'CAP-3', SHOOT, 16, 3000, True),
        ('g7:222@0', 6, 'CAP-4', WAIT, 20, 30000, False),
        ('g7:222@0', 6, 'CAP-4', RETIRE, 20, 30000, False),
        ('g7:222@0', 6, 'CAP-4', SHOOT, 20, 30000, False),
        ('source', 3, 'CAP-5', WAIT, 15, 30000, False),
    ]
    results = []
    for b, d, cap, tr, rounds, bound, trace in args:
        start = time.perf_counter()
        g = run(b, d, cap, tr, rounds=rounds, bound=bound, trace=trace)
        results.append({'sender': b, 'd': d, 'cap': cap, 'treatment': tr, 'round limit': rounds,
                        'knot bound': bound, 'trace': trace, 'rounds': len(g.rows),
                        'knots': g.rows[-1].knots, 'seconds': round(time.perf_counter()-start, 4)})
    return {'configurations': results,
            'planned': {'route': '720 original baselines plus four simple reference runs per treatment and length',
                        'changes': 'all changed runs for the three-step meeting, cap three, waiting',
                        'swaps': 'cap four to round 3d+2 with 30000 knots, all sender entries and treatments; cap five at d=2,3 with 30000 knots and waiting'}}


def ancestry_of(g, initial, ids):
    stack = list(ids)
    seen, origins = set(), set()
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        if g.parents[u]:
            stack.extend(g.parents[u])
        else:
            origins.add(initial[u])
    return tuple(sorted(origins))


def cancellation(g, r):
    """Own offshoots owed to a cancelled mixed group, and its short partners."""
    affected = Counter()
    short_partners = set()
    for group in r.groups:
        local = [u for u in group if g.roles[u] == OWN]
        if local and len(local) < len(group) and not r.short.isdisjoint(group):
            short_partners.update(u for u in group if u in r.short and g.roles[u] != OWN)
            affected.update(local)
    return affected, short_partners


def own_offshoots(g, r):
    return Counter(g.names[x.parents[0]] for x in r.birth_records
                   if x.kind == 'offshoot' and g.roles[x.id] == OWN)


def route(rows):
    source_rows = {(r['d'], r['law'][1], r['B']): r for r in called(rows) if r['law'][0] == 'CAP-3'}
    tests, differences, examples = Counter(), [], {}
    by_class = defaultdict(Counter)
    cancellation_sizes = defaultdict(Counter)
    origin_counts = Counter()
    for (d, tr) in product(range(2, 7), TREATMENTS):
        stub = run('stub', d, tr=tr, trace=True)
        local_early = run('stub', d+1, tr=tr, change=('link', d, 1), bound=12000)
        local_late = run('stub', d+2, tr=tr, change=('link', d+1, 1), bound=12000)
        add_two = run('stub', d, tr=tr, change=('B', 0, 2), bound=12000)
        add_one = run('stub', d, tr=tr, change=('B', 0, 1), bound=12000)
        tests['same-length stub +1 equals unchanged stub, exact own births to round 16'] += (
            len(stub.rows) == len(add_one.rows) == 16 and strict(stub) == strict(add_one))
        for b in SENDERS:
            original = source_rows[d, tr, b]
            g = run(b, d, tr=tr, trace=True)
            ours = counts(g)
            dep = switched(ours)
            tests['histories rebuilt'] += 1
            tests['rounds rebuilt'] += len(g.rows)
            if (ours != original['own births'] or [r.a_short for r in g.rows] != original['A short']
                    or len(g.rows) != original['rounds'] or g.rows[-1].knots != original['knots']):
                differences.append([d, tr, b, 'baseline counts or horizon'])
            class_name = 'no departure' if dep is None else 'early' if dep == 2*d+1 else 'late'
            mimic = {'early': local_early, 'late': local_late, 'no departure': stub}[class_name]
            comp = by_class[class_name]
            comp['histories'] += 1
            comp['all observed rounds available in reference'] += len(mimic.rows) >= len(g.rows)
            comp['identical own birth signatures to reference over observed rounds'] += (
                len(mimic.rows) >= len(g.rows) and strict(g) == strict(mimic)[:len(g.rows)])
            comp['identical own short counts to reference over observed rounds'] += (
                len(mimic.rows) >= len(g.rows) and [r.a_short for r in g.rows] == [r.a_short for r in mimic.rows[:len(g.rows)]])
            if class_name == 'early':
                comp['identical own birth signatures also with two extra loose distinctions at same-length stub'] += (
                    len(add_two.rows) >= len(g.rows) and strict(g) == strict(add_two)[:len(g.rows)])
            hit = next((r for r in g.rows if r.a_joined != r.a_kept), None)
            if (hit.round if hit else None) != dep or first(strict(g), strict(stub)) != dep:
                differences.append([d, tr, b, 'first cancelled mixed join or signature against stub'])
            tests['no short own knot through and including first departure, or end if none'] += (
                not any(r.a_short for r in g.rows[:dep]))
            if hit is None:
                continue
            prev = g.rows[hit.round-2]
            preceding = {u for group in prev.groups if any(g.roles[p] == OWN for p in group)
                         for u in group if g.roles[u] != OWN}
            affected, shorts = cancellation(g, hit)
            tests['departures'] += 1
            tests['preceding round all mixed partners owed and held three'] += (
                bool(preceding) and all((prev.owed[u], prev.available[u]) == (3,3) for u in preceding))
            tests['every short mixed partner owed four, held three, descended from receiver and link'] += (
                bool(shorts) and all((hit.owed[u], hit.available[u], g.roles[u]) ==
                                     (4, 3, frozenset({'A','link'})) for u in shorts))
            named = Counter({g.names[u]: n for u,n in affected.items()})
            tests['extra own offshoots against unchanged stub equal lost joins at each affected own parent'] += (
                own_offshoots(g, hit) == own_offshoots(stub, stub.rows[hit.round-1]) + named)
            tests['lost joins equal total excess over the slow count'] += (
                sum(affected.values()) == len(hit.own_births)-hit.round-2)
            sizes = (hit.a_joined-hit.a_kept, hit.a_kept, len(shorts), len(affected), len(hit.own_births))
            cancellation_sizes[hit.round][str(sizes)] += 1
            origins = {ancestry_of(g, g.names, (u,)) for u in affected}
            origin_counts[str(sorted(origins))] += 1
            if b == 'copier' and d == 3:
                examples[tr] = {'departure': dep, 'own births': ours, 'own short': [r.a_short for r in g.rows],
                                'attempted mixed groups at departure': hit.a_joined, 'kept': hit.a_kept}
    bare = run(None, 1, trace=True)
    ordinary = [(b,d,run(b,d,'ORD')) for b,d in product(('copier','g7:113@0','stub'),(2,3,6))]
    return {'raw versus independent baseline differences': differences, 'tests': tests,
            'strict birth signature includes': 'parent-derived name, fresh distinction count and total places; compared as a multiset',
            'references': {'early': 'stub one step farther with one extra loose distinction at link d',
                           'late': 'stub two steps farther with one extra loose distinction at link d+1',
                           'no departure': 'unchanged stub at same length'},
            'reference agreements': by_class, 'source labels of affected exclusively own parents': origin_counts,
            'at departure, by round, (cancelled mixed groups, kept mixed groups, distinct short mixed partners, affected own parents, own births)': cancellation_sizes,
            'two-knot sender at three steps': examples, 'bare receiver': {'rounds': len(bare.rows), 'birth counts': counts(bare)},
            'ordinary-count controls': [{'sender': b, 'd': d, 'rounds': len(g.rows), 'departure': switched(counts(g))} for b,d,g in ordinary]}


def inclusive(g):
    return [sum('A' in g.roles[x.id] for x in row.birth_records) for row in g.rows]


def changed_cases(rows):
    lookup = {r['B']: r for r in called(rows) if r['law'] == ['CAP-3', WAIT] and r['d'] == 3}
    result = defaultdict(Counter)
    departure_pairs = defaultdict(Counter)
    issues, examples = [], {}
    for b in SENDERS:
        base = run(b, 3, trace=True)
        base_wide = inclusive(base)
        declarations = {c['at']: c for c in lookup[b]['changes']}
        covered = set()
        for lab, dist, change in changes(b, 3):
            try:
                other = run(b, 3, change=change, trace=True)
            except ValueError as exc:
                if 'no usable distinction to bar' not in str(exc):
                    raise
                continue
            covered.add(lab)
            c = declarations[lab]
            answer = first(strict(base), strict(other))
            count_only = first(counts(base), counts(other))
            wide = first(base_wide, inclusive(other))
            own_without = None if answer is None else base.rows[answer-1].a_short > 0
            own_with = None if answer is None else other.rows[answer-1].a_short > 0
            if (answer, own_without, own_with, dist) != (
                    c['heard'], c['waiting own without'], c['waiting own with'], c['distance']):
                issues.append([b, lab, answer, c['heard']])
            group = 'sender' if 'B' in lab else 'link'
            if answer is not None:
                old, new = switched(counts(base)), switched(counts(other))
                departure_pairs[group][f'{old} to {new}'] += 1
            for label in (group, 'all'):
                stats = result[label]
                stats['changes'] += 1
                stats['strict signature heard'] += answer is not None
                stats['strict count-only heard'] += count_only is not None
                stats['strict count-only first difference matches signature or both silent'] += count_only == answer
                stats['birth count including mixed receiver descendants heard'] += wide is not None
                stats['inclusive count gives earlier hearing than strict count, including otherwise silent'] += (
                    wide is not None and (count_only is None or wide < count_only))
                stats['earlier differences from marks at distance >= 3'] += (
                    dist >= 3 and wide is not None and (count_only is None or wide < count_only))
            if wide is not None and (count_only is None or wide < count_only) and group not in examples:
                examples[group] = {'sender': b, 'change': lab, 'distance': dist, 'inclusive first difference': wide,
                                   'strict first difference': answer, 'rounds compared': min(len(base.rows),len(other.rows))}
        assert set(declarations) == covered
    return {'scope': 'cap three, waiting, one-loose receiver site, meeting at three steps, all sender and link changes',
            'method': 'Strict uses births descended exclusively from the receiver. Inclusive counts each birth with any receiver ancestor.',
            'disagreements with recorded change, distance and waiting flags': issues, 'comparisons': result,
            'unmarked to changed first departures among heard changes': departure_pairs, 'examples': examples}


def swaps():
    summary = []
    for cap, distances, treatments in [('CAP-4', range(2,7), TREATMENTS), ('CAP-5', (2,3), (WAIT,))]:
        for d, tr in product(distances, treatments):
            until = 3*d+2 if cap == 'CAP-4' else 4*d+3
            observed, limited = defaultdict(list), []
            for b in SENDERS:
                g = run(b, d, cap, tr, rounds=until, bound=30000)
                dep = switched(counts(g))
                if dep is not None:
                    observed[dep].append({'sender': b, 'loose at unjoined site': loose(b)})
                if len(g.rows) < until:
                    limited.append({'sender': b, 'rounds': len(g.rows), 'departure': dep})
            summary.append({'cap': cap, 'd': d, 'treatment': tr, 'scheduled rounds': until, 'entries': len(SENDERS),
                            'switches': observed, 'ended before scheduled round': limited})
    alternatives = []
    raw_three = {(r['A'], r['join'], r['B']): r
                 for r in load('switch_runs.jsonl.gz') if r['d'] == 3 and r['law'] == ['CAP-3', WAIT]}
    for a, join, b in product((A, 'g7:122@1'), ('meeting','share'), ('copier','g7:113@0','g1:3@0','stub')):
        rec = raw_three[a,join,b]
        base = run(b, 3, join=join, a=a)
        site = STARTS[b].site if b != 'stub' else 0
        matched, changed = {}, {}
        for sign, prefix in ((1, 'B'), (-1, 'bB')):
            other = run(b, 3, join=join, a=a, change=('B', site, sign))
            label = f'{prefix}{site}'
            when = first(strict(base), strict(other))
            matched[label] = when == next(c['heard'] for c in rec['changes'] if c['at'] == label)
            changed[label] = when
        alternatives.append({'receiver site': a, 'join': join, 'sender': b,
                             'first departure': switched(counts(base)), 'rounds': len(base.rows),
                             'own births and short counts match record': counts(base) == rec['own births'] and
                                 [r.a_short for r in base.rows] == rec['A short'],
                             'sender site changes, first hearing': changed, 'matches record': matched})
    return {'scope': 'cap changes at the one-loose receiver site, with a meeting and knot bound 30000 after a round',
            'groups': summary, 'receiver site and join swaps': {'scope': 'cap three, waiting, d=3, 16 rounds or 3000 knots',
                                                                'cases': alternatives}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('part', choices=('pilot','raw','route','changes','swaps'))
    part = parser.parse_args().part
    resource.setrlimit(resource.RLIMIT_AS, (1_900_000_000, 1_900_000_000))
    started = time.perf_counter()
    if part == 'pilot':
        result = timed_pilot()
    elif part == 'swaps':
        result = swaps()
    else:
        rows = load('switch_runs.jsonl.gz')
        result = {'raw': raw, 'route': route, 'changes': changed_cases}[part](rows)
    result['runtime'] = {'elapsed seconds': round(time.perf_counter()-started,3),
                         'peak resident KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         'single process address-space limit bytes': 1_900_000_000}
    target = HERE / f'switch_{part}.json'
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(f'{target.name} {result["runtime"]}')


if __name__ == '__main__':
    main()
