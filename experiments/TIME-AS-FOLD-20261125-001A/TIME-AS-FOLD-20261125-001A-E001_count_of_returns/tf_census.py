"""Tables of runs 1 to 3 (the census), P2, P3, P7, P8, P9, and the comparison with compare.json's census table.

Usage: python -B tf_census.py   (reads run1.jsonl.gz, run2.jsonl.gz, run3.jsonl.gz; writes census.json)
"""
from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict

import tf_common as C
import tf_runs as RN

PRIMARY = {('STEPS-1', 'COPY-LAW(RETIRE)'), ('STEPS-1', 'COPY-LAW(OFFSHOOT)'), ('STEPS-1', 'COPY-LAW(WAIT)'),
           ('MET', 'CAP-3(RETIRE)'), ('MET', 'CAP-3(OFFSHOOT)'), ('MET', 'RING-LAW')}


def ration(base):
    return 'FLOOR1' if base.startswith('COPY-LAW') else 'CAP-3'


def load(fn):
    return list(C.jsonl(fn))


def proto_key(r):
    """The key of compare.json's 'unfinished' list for a run (its format: group|family|clause|base|start|choice|law)."""
    rule = r['rule']
    if rule is None:
        fam, cl = 'none', 'None'
    elif ':' in rule:
        b, c = rule.split(':')
        fam = b
        cl = ('MET:' + c) if b == 'MET' else ('STEPS:' + c)
    else:
        fam, cl = rule, 'None'
    st = r['start']
    if st.startswith('atlas '):
        a, l = st[6:].split(' loose ')
        st = 'g%s:%s' % (a, l.replace(',', ''))
    return '|'.join([r['group'], fam, cl, r['base'], st, r['choice'], r['knot_law']])


def cell_counts(rows):
    c = Counter()
    mx = 0
    for r in rows:
        c['runs'] += 1
        if r.get('stop') == 'knots':
            c['cut short by the knot bound'] += 1
        if r['past'].get('p2_exceeds_start_bound') or r['nopast'].get('p2_exceeds_start_bound'):
            c['bound exceeded'] += 1
        if r['nopast'].get('p2_exceeds_start_bound'):
            c['bound exceeded (nopast)'] += 1
        if r['past'].get('p2_exceeds_start_bound'):
            c['bound exceeded (past)'] += 1
        for mode in ('past', 'nopast'):
            s = r[mode]
            c['%s: runs with a clock of 4 equal ticks' % mode] += int(s['clock'])
            c['%s: runs with a clock giving parts off at 4 ticks' % mode] += int(s['clock_off4'])
            c['%s: runs with a clock giving parts off at 4 ticks (anywhere)' % mode] += int(s['clock_off4_anywhere'])
            c['%s: runs with a series giving parts off at 2+ ticks' % mode] += int(s['series_off2'])
        mx = max(mx, r['past']['max_ticks_off'], r['nopast']['max_ticks_off'])
    c = dict(c)
    c['max ticks giving parts off in a series'] = mx
    return c


def census():
    rows = load('run1.jsonl.gz') + load('run2.jsonl.gz')
    cmp_ = C.compare()['census']
    unf_proto = set(k.rsplit('|', 1)[0] for k in cmp_['unfinished'])
    cells = defaultdict(list)
    unfinished = []
    for r in rows:
        if r.get('unfinished'):
            unfinished.append({k: r[k] for k in ('group', 'start', 'base', 'rule', 'choice', 'knot_law', 'unfinished',
                                                  'sec') if k in r})
            continue
        key = '%s|%s|%s' % (r['group'], r['rule'] or 'none', ration(r['base']))
        cells[key].append(r)
    table = {k: cell_counts(v) for k, v in sorted(cells.items())}
    # the comparison, over runs finished in both (dev 33): drop the prototype's unfinished runs; MET's join clause
    # alone with IN-TURN is the same run as with OLDEST, and the prototype ran it, so OLDEST counts twice
    mine_unf = defaultdict(int)
    for u in unfinished:
        mine_unf['%s|%s|%s' % (u['group'], u['rule'] or 'none', ration(u['base']))] += 1
    comp = {}
    for key, ref in cmp_['table'].items():
        rs = [r for r in cells.get(key, []) if proto_key(r) not in unf_proto]
        dup = [r for r in rs if r['rule'] == 'MET:join' and r['choice'] == 'OLDEST'
               and proto_key(dict(r, choice='IN-TURN')) not in unf_proto]
        mine = cell_counts(rs + dup) if rs else {}
        diffs = {}
        for k, v in ref.items():
            if k == 'runs':
                continue
            if mine.get(k, 0) != v:
                diffs[k] = [mine.get(k, 0), v]
        comp[key] = {'mine_runs_compared': mine.get('runs', 0), 'prototype_runs': ref.get('runs'),
                     'mine_unfinished_in_cell': mine_unf.get(key, 0), 'differences': diffs,
                     'comparable': mine_unf.get(key, 0) == 0}
    return table, comp, unfinished, rows


def p2(rows):
    """P2 on the laws of the count, and STEPS-2 with its own bound."""
    per = defaultdict(lambda: {'runs': 0, 'series_checked': 0, 'exceeding': 0, 'most_ticks_off_or_copies': 0,
                               'most_excess': None, 'examples': []})
    for r in rows:
        if r.get('unfinished') or r['group'] not in ('main', 'dbt'):
            continue
        if not r['base'].startswith('COPY-LAW'):
            continue
        rule = r['rule']
        if rule in RN.LAWS_OF_THE_COUNT or rule == 'STEPS-2':
            key = '%s|%s' % (r['group'], rule)
            d = per[key]
            d['runs'] += 1
            w = r['nopast'].get('p2_worst')
            n_ex = r['nopast'].get('p2_exceeds_k_bound' if rule == 'STEPS-2' else 'p2_exceeds_start_bound', 0)
            if w:
                d['series_checked'] += 1
                d['most_ticks_off_or_copies'] = max(d['most_ticks_off_or_copies'], w['ticks_off_or_copies'])
            if n_ex:
                d['exceeding'] += 1
                if len(d['examples']) < 5:
                    d['examples'].append({k: r[k] for k in ('start', 'base', 'choice', 'knot_law')})
            # the same with the filter
            n_ex2 = r['past'].get('p2_exceeds_k_bound' if rule == 'STEPS-2' else 'p2_exceeds_start_bound', 0)
            if n_ex2:
                d['exceeding_past'] = d.get('exceeding_past', 0) + 1
    return dict(per)


def births_gain(rows):
    per = defaultdict(lambda: [0, 0])
    for r in rows:
        if r.get('unfinished') or r['group'] not in ('main', 'fbp') or not r['base'].startswith('COPY-LAW'):
            continue
        if r['rule'] in ('STEPS-1', 'MET', 'Q', 'UP-TO-2', 'STEPS-2'):
            k = '%s|%s|%s' % (r['knot_law'], r['rule'], 'distinct inputs' if r['group'] == 'main' else
                              'fresh by parents')
            per[k][0] += r['births']
            per[k][1] += r['births_gaining_outside_start_offshoots']
    return {k: {'births': v[0], 'gaining_outside_start_offshoots': v[1]} for k, v in sorted(per.items())}


def p3(rows):
    named = set(C.named_stars())
    bad = []
    q_fbp = []
    for r in rows:
        if r.get('unfinished') or r['start'] not in named:
            continue
        if r['group'] == 'main' and (r['rule'], r['base']) in PRIMARY:
            for mode in ('past', 'nopast'):
                if r[mode]['clock_off4'] or r[mode]['clock_off4_anywhere']:
                    bad.append({k: r[k] for k in ('start', 'base', 'rule', 'choice', 'knot_law')} | {'mode': mode})
        if r['group'] == 'fbp' and r['rule'] == 'Q' and r['base'].startswith('COPY-LAW'):
            if r['past']['clock_off4'] or r['nopast']['clock_off4']:
                q_fbp.append({k: r[k] for k in ('start', 'base', 'choice', 'knot_law')})
    return {'primary_clock_off4': bad, 'fbp_Q_FLOOR1_clock_off4_runs': len(q_fbp), 'fbp_Q_examples': q_fbp[:10],
            'verdict': 'holds' if not bad and q_fbp else 'fails'}


def p8(rows):
    ctl = [r for r in rows if r['group'] == 'ring227' and r['rule'] is None]
    met = [r for r in rows if r['group'] == 'ring227' and r['rule'] == 'MET']
    cu = [r for r in ctl if r.get('unfinished')]
    mu = [r for r in met if r.get('unfinished')]
    ctl_f = [r for r in ctl if not r.get('unfinished')]
    met_f = [r for r in met if not r.get('unfinished')]
    a = sum(1 for r in ctl_f if r['past']['clock_off4'] and r['nopast']['clock_off4'])
    b = sum(1 for r in met_f if r['past']['clock_off4'] or r['nopast']['clock_off4'])
    starts_ok = len({r['start'] for r in ctl_f if r['past']['clock_off4']})
    return {'control_runs': len(ctl), 'control_unfinished': len(cu), 'control_with_clock_off4_both_modes': a,
            'control_starts_with_clock_off4': starts_ok, 'MET_runs': len(met), 'MET_unfinished': len(mu),
            'MET_runs_with_clock_off4': b,
            'verdict': 'holds' if (a == len(ctl_f) and b == 0) else 'fails'}


def p9(table):
    def g(rule, rat, col='clock giving parts off at 4 ticks'):
        c = table.get('main|%s|%s' % (rule, rat), {})
        return c.get('past: runs with a %s' % col, 0) + c.get('nopast: runs with a %s' % col, 0) > 0
    out = {
        "MET's join clause alone keeps one under both rations": g('MET:join', 'FLOOR1') and g('MET:join', 'CAP-3'),
        'STEPS-k for offshoots of joins keeps one under FLOOR1 (k=1,2,3)': all(g('STEPS-%d:join' % k, 'FLOOR1')
                                                                               for k in (1, 2, 3)),
        'STEPS-k for offshoots of joins keeps none under the cap of three': not any(g('STEPS-%d:join' % k, 'CAP-3')
                                                                                    for k in (1, 2, 3)),
        'STEPS-k for offshoots of offshoots keeps one under the cap of three for k = 2, 3':
            g('STEPS-2:offshoot', 'CAP-3') and g('STEPS-3:offshoot', 'CAP-3'),
        'STEPS-1 for offshoots of offshoots keeps none under the cap of three': not g('STEPS-1:offshoot', 'CAP-3'),
        'STEPS-k for offshoots of offshoots keeps none under FLOOR1': not any(g('STEPS-%d:offshoot' % k, 'FLOOR1')
                                                                              for k in (1, 2, 3)),
        "MET's offshoot clause alone keeps none": not (g('MET:offshoot', 'FLOOR1') or g('MET:offshoot', 'CAP-3')),
    }
    out['verdict'] = 'holds' if all(out.values()) else 'fails'
    return out


def p7():
    rows = load('run3.jsonl.gz')
    per = []
    fails = []
    unfinished = []
    for r in rows:
        if r.get('unfinished') or r.get('stop') in ('guard', 'limit'):
            unfinished.append({k: r.get(k) for k in ('start', 'k', 'choice', 'knot_law', 'stop', 'rounds',
                                                      'unfinished')})
            if r.get('unfinished'):
                continue
        k = r['k']
        ret = r['start_roster_returns']
        per.append({'start': r['start'], 'k': k, 'choice': r['choice'], 'knot_law': r['knot_law'],
                    'rounds': r['rounds'], 'stop': r['stop'], 'returns': ret,
                    'first_take': r['first_take_round'], 'first_offshoot_take': r['first_offshoot_take_round'],
                    'ring_member_offshoot_first_take': r['ring_member_offshoot_first_take']})
        finished = r['stop'] not in ('guard', 'limit')
        if (2 * k + 2) in ret:
            fails.append(('returns at 2k+2', r['start'], k, r['choice'], r['knot_law']))
        if k == 1 and ret:
            fails.append(('k=1 returns', r['start'], k, r['choice'], r['knot_law'], ret))
        if k >= 2 and r['choice'] in ('OLDEST', 'IN-TURN') and finished and ret != list(range(2, 2 * k + 1, 2)):
            fails.append(('not exactly 2..2k', r['start'], k, r['choice'], r['knot_law'], ret))
    by_choice = defaultdict(lambda: Counter())
    for p in per:
        if p['k'] >= 2:
            ok = p['returns'] == list(range(2, 2 * p['k'] + 1, 2))
            by_choice[p['choice']]['exactly 2..2k' if ok else 'otherwise'] += 1
    first_take_ok = sum(1 for p in per if p['ring_member_offshoot_first_take'] == 2 * p['k'] + 1)
    return {'runs': len(rows), 'unfinished_or_cut_by_guard': unfinished, 'clause_failures': fails,
            'k>=2 by choice': {k: dict(v) for k, v in by_choice.items()},
            'ring member offshoot first takes at 2k+1': first_take_ok, 'per_run': per,
            'verdict': 'holds' if not fails else 'fails'}


def main():
    table, comp, unfinished, rows = census()
    out = {'table': table, 'comparison_with_compare_json': comp, 'unfinished': unfinished,
           'p2': p2(rows), 'births_gain': births_gain(rows), 'p3': p3(rows), 'p8': p8(rows), 'p9': p9(table),
           'p7': p7()}
    out['n_rows'] = len(rows)
    out['stops'] = dict(Counter(str(r.get('stop')) for r in rows))
    C.write_json('census.json', out)
    ncomp = sum(1 for v in comp.values() if v['comparable'])
    ndiff = sum(1 for v in comp.values() if v['comparable'] and v['differences'])
    C.log('census: %d rows, %d unfinished; cells compared %d, differing %d' % (len(rows), len(unfinished), ncomp,
                                                                              ndiff))
    C.log('P2', {k: (v['runs'], v['exceeding']) for k, v in out['p2'].items()})
    C.log('P3', out['p3']['verdict'], 'P8', out['p8']['verdict'], 'P9', out['p9'], 'P7', out['p7']['verdict'])


if __name__ == '__main__':
    main()
