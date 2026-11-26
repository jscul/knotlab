"""Compare seeded replays of complete rounds with the closed growth records."""

import argparse
import gzip
import json
import random
import resource
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from growth import (
    A_ONLY, B_ONLY, STARTS, Growth, Setup, build, changes, descent,
    distance_from, first_difference, fresh_count, groups_for, grow, start,
)


HOME = Path(__file__).resolve().parent
SEED = 2026112601
SPECS = {
    'switch_runs': ('law', 'join', 'A'),
    'jam_d3_meeting': ('law',),
    'jam_d2_meeting_sample': ('law',),
    'jam_d5_meeting_sample': ('law',),
    'jam_d3_share_sample': ('law',),
    'far': ('law',),
    'ring_line_runs': ('law', 'join'),
    'reach_runs': ('law',),
    'made_bench': ('law', 'join'),
    'made_census': ('law', 'join'),
    'made_mark': ('law',),
    'again_runs': ('law',),
}


class Comparison:
    def __init__(self, name, line, record):
        self.report = {
            'file': name + '.jsonl.gz', 'line': line,
            'case': {k: record[k] for k in ('A', 'B', 'd', 'steps', 'join', 'law') if k in record},
            'rounds compared': 0, 'checks': 0, 'differences': [],
        }

    def check(self, key, expected, observed):
        self.report['checks'] += 1
        if observed != expected:
            self.report['differences'].append({'field': key, 'recorded': expected, 'rebuilt': observed})

    def rounds(self, prefix, expected, observed, *, same_growth=False):
        if not same_growth:
            self.report['rounds compared'] += min(map(len, observed.values()), default=0)
        for key in expected:
            self.check(prefix + key, expected[key], observed[key])


def sample(name, seed):
    fields = SPECS[name]
    strata = defaultdict(list)
    missing = 0
    with gzip.open(HOME.parent / (name + '.jsonl.gz'), 'rt') as f:
        for line, data in enumerate(map(json.loads, f), 1):
            if 'law' not in data:
                missing += 1
                continue
            key = tuple(tuple(data[k]) if isinstance(data[k], list) else data[k] for k in fields)
            strata[key].append((line, data))
    rng = random.Random(f'{seed}:{name}')
    selected = [rng.choice(rows) for _, rows in sorted(strata.items())]
    return selected, sum(map(len, strata.values())), missing


def signature(rounds, field):
    return [len(getattr(row, field)) for row in rounds]


def record_growth(rec, default_rounds, bound, change=None, remove=False, trace=False):
    setup = build(rec['A'], rec['B'], rec.get('d', rec.get('steps', 1)), rec.get('join', 'meeting'),
                  change=change, remove=remove)
    return grow(setup, *rec['law'][:2], default_rounds, bound, trace=trace)


def replay_jam(c, rec, switch=False):
    horizon, bound = (16, 3000) if switch else (12, 1500)
    whole = record_growth(rec, horizon, bound)
    rows = whole.rows
    c.check('rounds', rec['rounds'], len(rows))
    c.check('knots', rec['knots'], len(whole.places))
    primary = {'A short': [r.a_short for r in rows], 'own births': signature(rows, 'own_births')}
    if switch:
        c.check('leaves first way', rec['leaves first way'], leaves_first_way(whole))
    else:
        c.check('ended', rec['ended'], whole.stop or 'rounds')
        primary.update({
            'births': [r.births for r in rows], 'A members': [r.a_members for r in rows],
            'A shortfall': [r.a_shortfall for r in rows], 'shortfall': [r.shortfall for r in rows],
        })
    c.rounds('', {k: rec[k] for k in primary}, primary)

    replayed = []
    for label, distance, edit in changes(rec['B'], rec['d']):
        try:
            another = record_growth(rec, horizon, bound, edit)
        except ValueError as err:
            if str(err) != 'no usable distinction to bar':
                raise
            continue
        r = first_difference(whole, another)
        compared = min(len(rows), len(another.rows))
        ra, rb = (rows[r - 1], another.rows[r - 1]) if r else (None, None)
        summary = {'at': label, 'distance': distance, 'heard': r}
        if switch:
            summary.update({'waiting own without': bool(ra.a_short) if r else None,
                            'waiting own with': bool(rb.a_short) if r else None})
        else:
            summary['rounds'] = compared
            if r:
                jam = lambda row: row.a_members > 0 and row.a_members == row.a_short
                summary.update({
                    'jammed without': jam(ra), 'jammed with': jam(rb),
                    'waiting own without': bool(ra.a_short), 'waiting own with': bool(rb.a_short),
                    'jammed without, round before': jam(rows[r - 2]) if r > 1 else None,
                    'A short with': [row.a_short for row in another.rows],
                    'own births with': signature(another.rows, 'own_births'),
                })
                c.report['rounds compared'] += len(another.rows)
        replayed.append(summary)
    c.check('changes listed', [r['at'] for r in rec['changes']], [r['at'] for r in replayed])
    old = {row['at']: row for row in rec['changes']}
    for trial in replayed:
        c.check('change ' + trial['at'], old.get(trial['at']), trial)


def leaves_first_way(growth):
    return next((r.round for r in growth.rows if len(r.own_births) != r.round + 2), None)


def replay_reach(c, rec):
    whole = record_growth(rec, 16, 3000, trace='demand' in rec)
    rows = whole.rows
    c.check('rounds', rec['rounds'], len(rows))
    c.check('ended', rec['ended'], whole.stop or 'rounds')
    c.check('knots', rec['knots'], len(whole.places))
    primary = {'short': [sum(r.short_by.values()) for r in rows], 'kept': [r.a_kept for r in rows],
               'own births': signature(rows, 'own_births'), 'joint births': signature(rows, 'joint_births')}
    c.rounds('', {k: rec[k] for k in primary}, primary)
    if 'demand' in rec:
        names = {'A': 'own A', 'B': 'own B', 'joint': 'joint', 'link': 'link side'}
        demand = Counter((names[descent(whole.roles[b.id])], b.kind, len(b.parents), b.demand)
                         for row in rows for b in row.birth_records)
        c.check('demand', rec['demand'], [[list(k), v] for k, v in sorted(demand.items())])
    trial_edits = {label: edit for label, _, edit in changes(rec['B'], rec['d']) if not label.startswith('b')}
    site = start(rec['B']).site
    trial_edits.update(two=('B', site, 2), less=('B', site, -1))
    replayed = []
    for label, edit in trial_edits.items():
        try:
            another = record_growth(rec, 16, 3000, edit, remove=label == 'less')
        except ValueError as err:
            if label != 'less' or str(err) not in {
                'no usable distinction to bar', 'removal would leave fewer than three places or no loose distinction',
            }:
                raise
            continue
        observed = {key: first_difference(whole, another, field) for key, field in (
            ('own', 'own_births'), ('joint', 'joint_births'), ('groups', 'a_cancelled'),
        )}
        observed['rounds'] = min(len(rows), len(another.rows))
        c.check('change ' + label, rec['changes'].get(label), observed)
        replayed.append(label)
    c.check('changes listed', sorted(rec['changes']), sorted(replayed))
    alone = grow(build(rec['A'], None, 1), *rec['law'])
    c.check('alone', rec['alone'], {'rounds': len(alone.rows), 'own births, last round': len(alone.rows[-1].own_births),
                                   'knots': len(alone.places)})


def replay_ring(c, rec):
    fixed = dict(A='source', d=rec['d'], join=rec['join'], law=[rec['law'], 'CANCEL-WAIT'])
    whole = record_growth(dict(fixed, B='ring'), 16, 3000)
    stub = record_growth(dict(fixed, B='stub'), 16, 3000)
    c.check('rounds', rec['rounds'], len(whole.rows))
    c.check('ended', rec['ended'], whole.stop or 'rounds')
    for label, growth in (('whole', whole), ('stub', stub)):
        c.rounds(label + '/', rec[label], {
            'knots': [r.knots for r in growth.rows], 'short by': [r.short_by for r in growth.rows],
            'births by': [r.births_by for r in growth.rows], 'own births': signature(growth.rows, 'own_births'),
        })
    diffs = [r.round for r, s in zip(whole.rows, stub.rows) if r.own_births != s.own_births]
    c.check('own births differ from with a stub, rounds', rec['own births differ from with a stub, rounds'], diffs)


def replay_bench(c, rec, census=False):
    horizon, bound = (10, 1500) if census else (12, 3000)
    whole = record_growth(rec, horizon, bound, trace=not census)
    rows = whole.rows
    c.check('rounds', rec['rounds' if census else 'rounds read'], len(rows))
    c.check('ended', rec['ended' if census else 'ended by'], whole.stop or 'rounds')
    c.check('knots', rec['knots'], len(whole.places))
    short_key = 'short' if census else 'short members by round'
    joint_key = 'joint' if census else 'joint descent, births by round'
    c.rounds('', {k: rec[k] for k in (short_key, joint_key)}, {
        short_key: [sum(r.short_by.values()) for r in rows], joint_key: signature(rows, 'joint_births'),
    })
    for who, other, own_roles, own_field, kept_field in (
        ('A', 'B', A_ONLY, 'own_births', 'a_kept'), ('B', 'A', B_ONLY, 'b_births', 'b_kept'),
    ):
        reads = rec['reads'][who]
        if census:
            c.check(who + '/last kept', reads['last kept'], max((r.round for r in rows if getattr(r, kept_field)), default=0))
        else:
            other_joins = [[group for group in r.groups if any(whole.roles[u] == own_roles for u in group)] for r in rows]
            own_series = {
                'own members by round': [sum(whole.roles[u] == own_roles for u in r.available) for r in rows],
                'own births by round': signature(rows, own_field), 'kept by round': [getattr(r, kept_field) for r in rows],
                'joined by round': [sum(any(whole.roles[u] != own_roles for u in g) for g in joins) for joins in other_joins],
                'joined to the other by round': [sum(any(other in whole.roles[u] for u in g) for g in joins) for joins in other_joins],
            }
            c.rounds(who + '/', {k: reads[k] for k in own_series}, own_series, same_growth=True)
        stub = record_growth(dict(rec, **{other: 'stub'}), horizon, bound)
        stub_key = 'stub' if census else 'own making differs from with a stub, first round'
        c.check(who + '/' + stub_key, reads[stub_key], first_difference(whole, stub, own_field))
        for i in range(len(start(rec[other]).knots)):
            another = record_growth(rec, horizon, bound, change=(other, i, 1))
            own = first_difference(whole, another, own_field)
            joint = first_difference(whole, another, 'joint_births')
            if census:
                c.check(who + f'/mark {i}', reads['marks'][i], [own, joint])
            else:
                c.check(who + f'/mark {i}', reads['mark at a start knot of the other'][str(i)], {
                    'own making first differs': own, 'joint descent first differs': joint,
                    'rounds compared': min(len(rows), len(another.rows)),
                })


def replay_made_mark(c, rec, seed):
    checkpoint = record_growth(rec, 6, 3000)
    c.check('knots at round 6', rec['knots at round 6'], len(checkpoint.places))
    distance = distance_from(checkpoint.meets, (i for i, tags in enumerate(checkpoint.roles) if tags == A_ONLY))
    targets = [i for i, born in enumerate(checkpoint.born) if born == 6 and checkpoint.roles[i] != A_ONLY]
    c.check('marked targets', len(rec['marks']), len(targets))
    whole = checkpoint.fork().run(16, 3000)
    c.check('rounds', rec['rounds'], len(whole.rows))
    rng = random.Random(seed)
    for i in sorted(rng.sample(range(len(targets)), min(6, len(targets)))):
        target = targets[i]
        marked = checkpoint.fork()
        marked.mark(target)
        marked.run(16, 3000)
        earliest = first_difference(whole, marked, after=6)
        read = min(len(whole.rows), len(marked.rows))
        kind = {'B': 'own B', 'joint': 'joint', 'link': 'link side'}[descent(checkpoint.roles[target])]
        started_short = sum(bool(other.short_by) and not base.short_by for base, other in zip(whole.rows[6:], marked.rows[6:]))
        observed = [kind, distance.get(target), earliest, read, started_short]
        c.check(f'mark {i}', rec['marks'][i], observed)


def replay_again(c, rec):
    first_edit = next(edit for label, _, edit in changes(rec['B'], rec['d']) if label == rec['first'])
    whole, first = (record_growth(rec, 12, 1500, edit) for edit in (None, first_edit))
    c.check('rounds for first change', rec['rounds'], [len(whole.rows), len(first.rows)])
    heard = first_difference(whole, first)
    c.check('h1', rec['h1'], heard)
    waiting = lambda w, x, h: [bool(w.rows[h - 1].a_short), bool(x.rows[h - 1].a_short)] if h else None
    c.check('waiting at h1', rec['waiting at h1'], waiting(whole, first, heard))

    checkpoint = record_growth(rec, heard, 1500, first_edit)
    baseline = first
    for trial_set in rec['again']:
        if not trial_set:
            c.check('round had no own B members', [], [i for i in checkpoint.usable if checkpoint.roles[i] == B_ONLY])
            break
        distance = distance_from(checkpoint.meets, (i for i, tags in enumerate(checkpoint.roles) if tags == A_ONLY))
        own_b = (i for i in checkpoint.usable if checkpoint.roles[i] == B_ONLY)
        targets = sorted(own_b, key=lambda i: (distance.get(i, 10**6), i))[:5]
        c.check(f'after round {heard}/targets', [trial['knot'] for trial in trial_set], targets)
        next_heard = None
        for target, trial in zip(targets, trial_set):
            branch = checkpoint.fork()
            branch.mark(target)
            marked = branch.fork().run(12, 1500)
            arrives = first_difference(baseline, marked, after=heard)
            c.check(f'after round {heard}/mark {target}', trial, {
                'set after round': heard, 'knot': target, 'sharings from A': distance.get(target), 'heard': arrives,
                'rounds': min(len(baseline.rows), len(marked.rows)), 'waiting': waiting(baseline, marked, arrives),
            })
            if arrives and next_heard is None:
                next_heard = arrives, branch, marked
        if next_heard is None:
            break
        heard, checkpoint, baseline = next_heard
        checkpoint.run(heard, 1500)


def primitive_checks(seed):
    """Check group enumeration against direct subset enumeration on small rosters."""
    rng = random.Random(seed)
    groups_checked = 0
    for n in range(2, 8):
        live = set(range(n))
        for _ in range(20):
            met = [{u for u in live if rng.randrange(2)} for _ in range(n)]
            meets = {u: [n + i for i, m in enumerate(met) if u in m] for u in live}
            pairs = {pair for pair in combinations(sorted(live), 2) if any(set(pair) <= m for m in met)}
            cliques = [frozenset(group) for k in range(3, n + 1) for group in combinations(sorted(live), k)
                       if all(pair in pairs for pair in combinations(group, 2))]
            big = [tuple(sorted(g)) for g in cliques if not any(g < other for other in cliques)
                   and not any(g <= m for m in met)]
            used = {pair for g in big for pair in combinations(g, 2)}
            assert groups_for(sorted(live), meets.__getitem__) == tuple(sorted(big) + sorted(pairs - used))
            groups_checked += 1

    # Four live knots each owe three and hold two. Each short treatment gives a distinct result.
    setup = Setup(((0, 4, 5), (1, 6, 7), (2, 8, 9), (3, 10, 11), (0, 1, 2, 3)), ('A', 'A', 'A', 'A', 'spent'))
    observed = {}
    for treatment, expected in {
        'CANCEL-WAIT': (1, 0, 4), 'CANCEL-RETIRE': (1, 0, 0), 'CANCEL-OFFSHOOT': (1, 8, 0),
        'SHORT-BY': (1, 4, 4), 'STALL': (0, 0, 4),
    }.items():
        g = grow(setup, 'FLOOR1', treatment, 1, trace=True)
        got = len(g.rows), len(g.places) - 5, sum(k < 4 for k in g.usable)
        assert got == expected, (treatment, got, expected)
        if g.rows:
            assert len(g.rows[0].short) == 4
            assert all(g.rows[0].owed[k] == 3 and g.rows[0].available[k] == 2 for k in range(4))
        observed[treatment] = dict(zip(('completed rounds', 'births', 'old members still usable'), got))
    assert (fresh_count('ONE-FEWER', 3, 1), fresh_count('REC-ONE-FEWER', 3, 1)) == (1, 0)
    assert len(STARTS) == 47
    return {'small group rosters': groups_checked, 'short treatment check': observed, 'sited starts plus bench starts': len(STARTS)}


def change_links(setup, delta):
    holdings = Counter(x for knot in setup.knots for x in knot)
    next_id = max(holdings) + 1
    knots = []
    for knot, tag in zip(setup.knots, setup.roles):
        if tag == 'link' and delta > 0:
            knot = (*knot, next_id)
            next_id += 1
        elif tag == 'link' and delta < 0:
            remove = max(x for x in knot if holdings[x] == 1)
            knot = tuple(x for x in knot if x != remove)
        knots.append(knot)
    return Setup(tuple(knots), setup.roles, setup.barred)


def link_controls(pilot):
    """Swap one loose distinction at every link while preserving the supplied meetings."""
    cases = [(d, sender) for d in (2, 3, 6) for sender in ('g3:22@0', 'g7:113@0', 'g1:3@0', 'stub')]
    if pilot:
        cases = [(6, 'g3:22@0')]
    results = []
    for distance, sender in cases:
        setup = build('g7:122@0', sender, distance)
        for delta in (0, -1, 1):
            g = grow(change_links(setup, delta), 'CAP-3', 'CANCEL-WAIT')
            results.append({
                'sender': sender, 'd': distance, 'loose per link': 2 + delta,
                'rounds': len(g.rows), 'leaves first way': leaves_first_way(g), 'own births': signature(g.rows, 'own_births'),
            })
    return results


def replay(name, c, rec, seed):
    if name.startswith('switch_') or name.startswith('jam_'):
        replay_jam(c, rec, switch=name.startswith('switch_'))
    elif name in {'reach_runs', 'far'}:
        replay_reach(c, rec)
    elif name == 'ring_line_runs':
        replay_ring(c, rec)
    elif name in {'made_bench', 'made_census'}:
        replay_bench(c, rec, census=name == 'made_census')
    elif name == 'made_mark':
        replay_made_mark(c, rec, seed)
    elif name == 'again_runs':
        replay_again(c, rec)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--pilot', action='store_true')
    cli.add_argument('--stage', choices=[*SPECS, 'link-controls'], action='append')
    cli.add_argument('--seed', type=int, default=SEED)
    cli.add_argument('--output', type=Path)
    args = cli.parse_args()
    start_clock = time.monotonic()
    output = {'seed': args.seed, 'pilot': args.pilot, 'primitive checks': primitive_checks(args.seed), 'stages': {}}
    for name in args.stage or [*SPECS, 'link-controls']:
        began = time.monotonic()
        if name == 'link-controls':
            cases = link_controls(args.pilot)
            stage = {'cases': cases}
            print(f'{name}: {len(cases)} grows in {time.monotonic() - began:.2f} s', flush=True)
        else:
            chosen, available, unavailable = sample(name, args.seed)
            if args.pilot:
                chosen = chosen[:1]
            compared = []
            for line, row in chosen:
                c = Comparison(name, line, row)
                try:
                    replay(name, c, row, args.seed + line)
                except Exception as err:
                    c.report['exception'] = repr(err)
                compared.append(c.report)
            stage = {
                'stratified by': list(SPECS[name]), 'recorded cases': available, 'unavailable records': unavailable,
                'cases not run in this replay': available - len(compared), 'cases compared': len(compared),
                'rounds with recorded sequences compared': sum(c['rounds compared'] for c in compared),
                'values compared': sum(c['checks'] for c in compared),
                'cases with a difference': sum(bool(c['differences'] or 'exception' in c) for c in compared),
                'cases': compared,
            }
            print(f'{name}: {len(compared)} cases, {stage["cases with a difference"]} with a difference in '
                  f'{time.monotonic() - began:.2f} s', flush=True)
        stage['seconds'] = round(time.monotonic() - began, 3)
        stage['peak KiB at end of stage'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        output['stages'][name] = stage
    output['seconds'] = round(time.monotonic() - start_clock, 3)
    output['peak KiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if args.output:
        args.output.write_text(json.dumps(output, indent=2) + '\n')
    else:
        for stage in output['stages'].values():
            for case in stage.get('cases', []):
                if case.get('differences') or 'exception' in case:
                    print(json.dumps(case))
    return int(any(s.get('cases with a difference') for s in output['stages'].values()))


if __name__ == '__main__':
    raise SystemExit(main())
