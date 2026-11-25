"""Verdicts per pair, per law and knot law, and the minimal laws among the listed laws (BD2 6, 8; B 27, 28)."""
import sys

sys.dont_write_bytecode = True

from collections import Counter, defaultdict

import common

VALUES = ['1', '2', '3', 'h(u) + 1', 'unbounded']


def ktA_fails(rec):
    kt = rec.get('knot_test_A')
    return bool(kt and kt['n_fail'])


def pair_dependence(p, run_fails, knot_test=True):
    """B1-dependence of one pair with a meeting only through made knots."""
    if not p['strict']:
        return None
    if not p['course_differs']:
        return 'equal'
    if not p.get('attribution_accepted'):
        a = p.get('attribution') or {}
        return 'differs, not attributed (%s)' % a.get('class')
    if not knot_test:
        return 'differs through the meeting'
    kb = p.get('knot_test_barred')
    if kb is None or isinstance(kb, str):
        return 'undecided: knot test not run'
    if run_fails or kb['n_fail']:
        return 'marked: a failing knot'
    return 'differs through the meeting'


def item_summary(rec, knot_test=True):
    fails = ktA_fails(rec)
    c = Counter()
    starts = defaultdict(Counter)
    for p in rec['pairs']:
        c['meeting'] += 1
        c['meeting:' + p['link_verdict']] += 1
        if not p['strict']:
            if p['course_differs']:
                c['non-strict, course differs'] += 1
            continue
        if fails:
            c['strict, marked (failing knot in run A)'] += 1
            continue
        c['strict'] += 1
        if p['ancestral']:
            c['ancestral'] += 1
        if p['ancestral_every_member']:
            c['ancestral every member'] += 1
        if p['weak_FD57']:
            c['weak FD 5.7'] += 1
        if p['start_knot_holds_linking_distinction']:
            c['start knot holds a linking distinction'] += 1
        d = pair_dependence(p, fails, knot_test)
        c['dep: ' + d] += 1
        if p['course_differs']:
            c['strict, course differs'] += 1
    nm = sum(len(v.get('no_meeting_pairs', [])) for v in rec['s'].values() if isinstance(v, dict))
    c['no meeting'] = nm
    return c


def law_verdicts(recs, knot_test=True):
    """{(law_id, knot law): {...}} over the items of a run."""
    out = {}
    for rec in recs:
        key = (rec['law_id'], rec['law']['knot_law'])
        o = out.setdefault(key, {'items': 0, 'counts': Counter(), 'starts_link': Counter(),
                                 'starts_ancestral': Counter(), 'starts_dep': Counter(), 'failing_items': 0,
                                 'guard_items': 0})
        o['items'] += 1
        c = item_summary(rec, knot_test)
        o['counts'].update(c)
        if ktA_fails(rec):
            o['failing_items'] += 1
        if rec.get('stop') == 'guard':
            o['guard_items'] += 1
        if c['strict']:
            o['starts_link'][rec['start']] += c['strict']
        if c['ancestral']:
            o['starts_ancestral'][rec['start']] += c['ancestral']
        if c['dep: differs through the meeting']:
            o['starts_dep'][rec['start']] += c['dep: differs through the meeting']
    for key, o in out.items():
        c = o['counts']
        o['B1-link'] = 'found' if c['strict'] else 'none, every pair decided'
        o['B1-ancestral'] = 'found' if c['ancestral'] else 'none, every pair decided'
        und = c['dep: undecided: knot test not run']
        dec = c['strict'] - und
        if c['dep: differs through the meeting']:
            o['B1-dependence'] = 'found'
        elif und:
            o['B1-dependence'] = 'none among %d decided, %d undecided' % (dec, und)
        else:
            o['B1-dependence'] = 'none, every pair decided'
        o['counts'] = dict(c)
        o['starts_link'] = dict(o['starts_link'])
        o['starts_ancestral'] = dict(o['starts_ancestral'])
        o['starts_dep'] = dict(o['starts_dep'])
    return out


def cost_vec(cost):
    return (cost['holder_steps'], cost['record_steps'], 1 if cost['whole_roster'] else 0,
            VALUES.index(cost['values_at_one_birth']), cost['new_rules'])


def below(a, b):
    return all(x <= y for x, y in zip(a, b)) and a != b


def minimal(law_ids, costs):
    vs = {l: cost_vec(costs[l]) for l in law_ids}
    return sorted(l for l in law_ids if not any(below(vs[m], vs[l]) for m in law_ids if m != l))


def minimal_laws(verdicts_by_run, family):
    costs = {L['id']: L['cost'] for L in family['search']}
    out = {}
    for v in ('B1-link', 'B1-ancestral', 'B1-dependence'):
        res = {}
        for scope in ('either knot law', 'parity', 'nae'):
            have = set()
            for vb in verdicts_by_run:
                for (lid, kl), o in vb.items():
                    if lid not in costs:
                        continue
                    if scope != 'either knot law' and kl != scope:
                        continue
                    if o[v] == 'found':
                        have.add(lid)
            m = minimal(sorted(have), costs)
            res[scope] = {'laws_with_verdict': sorted(have), 'minimal': m,
                          'costs': {l: costs[l] for l in m}}
        out[v] = res
    return out
