"""The registered runs C0, 1a, P1, N2, 1b, P2, 1c, U1, M2 (pre-registration, "Runs"), each a list of items in the
registered order (law in family.json order, then start in starts.json order, then parity before not-all-equal), run
on a pool with `imap` so that what is written is always a prefix of whole items.

  python -B runs.py <run> --procs k --deadline <unix time> [--sample n]
"""
import sys

sys.dont_write_bytecode = True

import argparse
import itertools
import json
import multiprocessing as mp
import os
import time
from collections import Counter

import common
from common import log
import eng
import item
import read
import wbc

KLS = ('parity', 'nae')
TREAT = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
RATIONS3 = ('FLOOR1', 'CAP-3', 'ORD')


def starts():
    return common.load('starts.json')


def law_of(d):
    return eng.Law(d['ration'], d['treatment'], d['take'], d['knot_law'], d.get('choice'))


def ldict(ration, treatment, take, kl, choice=None):
    return {'ration': ration, 'treatment': treatment, 'take': take, 'knot_law': kl, 'choice': choice}


# --------------------------------------------------------------------------------------------------------- items
def items_search(run_id):
    st = starts()
    fam = common.load('family.json')['search']
    out = []
    for L in fam:
        if L['run'] != run_id:
            continue
        for sname in st['order']:
            for kl in KLS:
                out.append({'id': '%s|%s|%s' % (L['id'], sname, kl), 'law': ldict(L['ration'], L['treatment'],
                            L['take'], kl), 'law_id': L['id'], 'start': sname, 'stars': st['stars'][sname],
                            'cfg': {}})
    return out


RING_STARTS = ('Ring(5,3)', 'Ring(5,3)+1', 'D2(5,3)', 'Ring(7,3)')   # starts.json order


def items_P1():
    st = starts()
    fam = common.load('family.json')['controls']['ration_controls_run_P1']
    out = []
    for rule in fam['rules']:
        for tr in TREAT:
            for sname in RING_STARTS:
                for kl in KLS:
                    out.append({'id': 'P1|%s|%s|%s|%s' % (rule, tr, sname, kl),
                                'law': ldict(rule, tr, 'MET-SOLE', kl), 'law_id': '%s/%s' % (rule, tr),
                                'start': sname, 'stars': st['stars'][sname], 'cfg': {'knot_test': 'full'}})
    return out


def items_M2():
    st = starts()
    out = []
    for tr in TREAT:
        for sname in RING_STARTS:
            for kl in KLS:
                out.append({'id': 'M2|%s|%s|%s' % (tr, sname, kl), 'law': ldict('MOD2', tr, 'MET-SOLE', kl),
                            'law_id': 'MOD2/%s' % tr, 'start': sname, 'stars': st['stars'][sname], 'cfg': {}})
    return out


def items_U1():
    st = starts()
    fam = {L['id']: L for L in common.load('family.json')['search']}
    out = []
    for lid in ('L02', 'L10'):
        L = fam[lid]
        for kl in KLS:
            out.append({'id': 'U1|%s|%s' % (lid, kl), 'law': ldict(L['ration'], L['treatment'], L['take'], kl),
                        'law_id': lid, 'start': st['extra']['name'], 'stars': st['extra']['stars'],
                        'cfg': {'knot_test': 'full'}})
    return out


def items_C0():
    st = starts()
    out = []
    for r in RATIONS3:
        for tr in TREAT:
            for sname in st['order']:
                for kl in KLS:
                    out.append({'id': 'C0-neg|%s|%s|%s|%s' % (r, tr, sname, kl), 'law': ldict(r, tr, None, kl),
                                'law_id': 'none/%s/%s' % (r, tr), 'start': sname, 'stars': st['stars'][sname],
                                'cfg': {}})
    for r in RATIONS3:
        for tr in TREAT:
            for sname in st['order']:
                for kl in KLS:
                    out.append({'id': 'C0-pos|%s|%s|%s|%s' % (r, tr, sname, kl),
                                'law': ldict(r, tr, 'J-EACH-PART', kl), 'law_id': 'J-EACH-PART/%s/%s' % (r, tr),
                                'start': sname, 'stars': st['stars'][sname],
                                'cfg': {'rounds': 4, 's_range': (1, 2, 3)}})
    for kl in KLS:
        out.append({'id': 'C0-planted|%s' % kl, 'law': ldict('ORD', 'CANCEL-RETIRE', 'MET', kl, 'OLDEST'),
                    'law_id': 'planted', 'start': 'made-4', 'stars': [[0, 1, 2], [0, 3, 4, 5, 6]],
                    'cfg': {'planted': True}})
    assert len(out) == 290
    return out


def two_knot_numberings():
    """Every numbering of the two-knot start up to its symmetries (30): the shared distinction, the split of the
    other four into the two knots' loose pairs, and the order of the two knots; places listed in increasing name."""
    out = []
    for e in range(5):
        rest = [d for d in range(5) if d != e]
        a = rest[0]
        for b in rest[1:]:
            P = sorted([a, b])
            Q = sorted(d for d in rest if d not in P)
            k1, k2 = sorted([e] + P), sorted([e] + Q)
            out.append([k1, k2])
            out.append([k2, k1])
    assert len(out) == 30 and len({json.dumps(x) for x in out}) == 30
    return out


def items_N2(law_ids):
    st = starts()
    fam = {L['id']: L for L in common.load('family.json')['search']}
    with open(os.path.join(common.TICKET_A, 'numberings.json')) as f:
        made3 = json.load(f)['made_class']['made-3']
    ren = common.load('renamings.json')['renamings']
    assert len(made3) == 120 and made3[0] == st['stars']['made-3']
    tk = two_knot_numberings()
    assert tk[0] == st['stars']['two-knot']
    out = []
    for lid in law_ids:
        L = fam[lid]
        for sname in st['order']:
            if sname == 'two-knot':
                lst = [('n%03d' % i, s) for i, s in enumerate(tk)]
            elif sname == 'made-3':
                lst = [('n%03d' % i, s) for i, s in enumerate(made3)]
            elif sname in ren:
                lst = [('registered', st['stars'][sname])] + [(r['name'], r['stars']) for r in ren[sname]]
            else:
                continue
            for kl in KLS:
                for nm, stars in lst:
                    out.append({'id': 'N2|%s|%s|%s|%s' % (lid, sname, kl, nm),
                                'law': ldict(L['ration'], L['treatment'], L['take'], kl), 'law_id': lid,
                                'start': sname, 'renaming': nm, 'stars': stars,
                                'cfg': {'knot_test': 'none', 'bars': 'A0', 'structure_invariants': True,
                                        'courses_all': True, 'n2': True}})
    return out


# ------------------------------------------------------------------------------------------------------ the worker
def _init():
    common.cap_memory(6)


def do_item(it):
    t0 = time.time()
    law = law_of(it['law'])
    c = dict(it['cfg'])
    if c.pop('planted', False):
        rec = planted(law, it['stars'])
    else:
        n2 = c.pop('n2', False)
        cfg = item.Cfg(**c)
        if n2:
            cfg.with_courses = True
        rec = item.analyse_item(law, it['start'], it['stars'], cfg, item_id=it['id'])
        if n2:
            rec = n2_digest(rec)
    rec['id'] = it['id']
    rec['law_id'] = it['law_id']
    rec['renaming'] = it.get('renaming')
    rec['stars'] = it['stars']
    rec['wall_seconds'] = round(time.time() - t0, 3)
    return json.loads(json.dumps(rec, default=common._default))


def n2_digest(rec):
    """N2 keeps, per pair, its verdicts and its two courses (for exact classes in the main process)."""
    pairs = []
    for p in rec['pairs']:
        dep = bool(p['strict'] and p['course_differs'] and p.get('attribution_accepted'))
        pairs.append({'s': p['s'], 'link_verdict': p['link_verdict'], 'strict': p['strict'],
                      'ancestral': p['ancestral'], 'ancestral_every_member': p['ancestral_every_member'],
                      'course_differs': p['course_differs'], 'dependence': dep,
                      'meeting_round': p['meeting_round'],
                      'course_A': p.get('course_A'), 'course_barred': p.get('course_barred'),
                      'n_X': len(p['X']), 'n_Y': len(p['Y'])})
    nm = {s: len(v.get('no_meeting_pairs', [])) for s, v in rec['s'].items()}
    return {'law_name': rec['law_name'], 'start': rec['start'], 'rounds_read': rec['rounds_read'],
            'stop': rec['stop'], 'guard': rec['guard'], 'knots': rec['knots'],
            'structure_invariants': rec['structure_invariants'], 'pairs': pairs, 'no_meeting_pairs_by_s': nm,
            'parts_by_s': {s: (len(v['parts']) if v.get('parts') is not None else None) for s, v in rec['s'].items()},
            'seconds': rec['seconds']}


def planted(law, stars):
    """C0's planted case (family.json, "planted_ticket_A"): made-4, ORD/CANCEL-RETIRE/MET(OLDEST); X the two round-1
    offshoots of the start knot with three places, Y the four of the other; s = 1; a = 4 (run A) against a = 1 (Y's
    member whose round-1 input is name 3 left usable, ticket A's listing); the linking set of BD2 5.2 in each."""
    runA = eng.Run(law, stars=stars, rounds=7)
    s = 1
    rec1 = runA.recs[0]
    X = tuple(b['id'] for b in rec1['births'] if b['parents'] == (0,))
    Y = tuple(b['id'] for b in rec1['births'] if b['parents'] == (1,))
    keep = [b['id'] for b in rec1['births'] if b['parents'] == (1,) and b['loose'] == [3]]
    R = runA.recs[1]['roster']
    parts = eng.roster_parts(R)
    member_part = {u: i for i, P in enumerate(parts) for u in P}
    i, j = member_part[X[0]], member_part[Y[0]]
    assert set(parts[i]) == set(X) and set(parts[j]) == set(Y), (parts, X, Y)
    cls = eng.classes_of_parts(runA.snaps[1], parts)
    out = {'law_name': law.name(), 'start': 'made-4', 's': s, 'X': list(X), 'Y': list(Y), 'wholly_apart': cls[i] != cls[j],
           'kept_usable_a1': keep, 'runs': {}}
    keysA = read.Keys(runA)
    r1 = eng.Run(law, base=runA, base_round=s, bar=[y for y in Y if y not in keep], rounds=7)
    k1 = read.Keys(r1, base=keysA)
    for name, run, keys in (('a=4', runA, keysA), ('a=1', r1, k1)):
        bits = read.desc_bits(run, s, member_part)
        meet = read.first_meetings(run, s, bits).get((min(i, j), max(i, j)))
        row = {'rounds_read': run.rounds_read, 'stop': run.stop, 'guard': run.guard, 'meeting': meet}
        if meet:
            v = read.View(run, keys, bits, i, j, s, X, Y)
            t = meet[0]
            L = read.linking(v, t, read.RoundIndex(run.recs[t - 1], bits), read.ancestor_bits(run.snaps[t]))
            row.update(L)
        out['runs'][name] = row
    out['class_a4'] = out['runs']['a=4'].get('link_verdict', 'no meeting')
    out['class_a1'] = out['runs']['a=1'].get('link_verdict', 'no meeting')
    out['passes'] = out['class_a4'] == 'through a start knot'
    return out


# ---------------------------------------------------------------------------------------------------- the driver
def run_items(name, items, procs, deadline, suffix=''):
    common.cap_memory(6)
    t0 = time.time()
    out = common.JsonLines('run%s%s.jsonl.gz' % (name, suffix))
    index = []
    done = 0
    cut = None
    pool = mp.Pool(procs, initializer=_init)
    it = pool.imap(do_item, items, chunksize=1)
    try:
        while done < len(items):
            try:
                rec = it.next(timeout=5)
            except mp.TimeoutError:
                if deadline and time.time() > deadline:
                    cut = done
                    log('deadline reached in run', name, 'after', done, 'of', len(items), 'items')
                    break
                continue
            out.write(rec)
            index.append(light(rec))
            done += 1
            if done % 20 == 0 or done == len(items):
                log(name, done, '/', len(items), 'items', round(time.time() - t0, 1), 's')
            if deadline and time.time() > deadline and done < len(items):
                cut = done
                log('deadline reached in run', name, 'after', done, 'of', len(items), 'items')
                break
    finally:
        if cut is not None:
            pool.terminate()        # this script's own worker processes only
        else:
            pool.close()
        pool.join()
        out.close()
    meta = {'run': name, 'items': len(items), 'done': done, 'cut_at': cut,
            'not_run': [x['id'] for x in items[done:]], 'wall_seconds': round(time.time() - t0, 1),
            'procs': procs, 'index': index}
    common.write_json('run%s%s_index.json' % (name, suffix), meta)
    return meta


def light(rec):
    if 'pairs' not in rec or rec.get('law_id') == 'planted':
        return {'id': rec['id'], 'wall_seconds': rec['wall_seconds']}
    ps = rec['pairs']
    return {'id': rec['id'], 'wall_seconds': rec['wall_seconds'], 'rounds_read': rec.get('rounds_read'),
            'stop': rec.get('stop'), 'guard': rec.get('guard'), 'knots': rec.get('knots'),
            'meeting_pairs': len(ps), 'strict': sum(1 for p in ps if p['strict'])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--deadline', type=float, default=0)
    ap.add_argument('--sample', type=int, default=0, help='time every n-th item into the scratch folder only')
    ap.add_argument('--laws', default='')
    ap.add_argument('--mult', type=int, default=0)
    ap.add_argument('--from-runs', default='')
    a = ap.parse_args()
    common.check_frozen()
    r = a.run
    if r == 'C0':
        items = items_C0()
    elif r in ('1a', '1b', '1c'):
        items = items_search(r)
    elif r == 'P1':
        items = items_P1()
    elif r == 'M2':
        items = items_M2()
    elif r == 'U1':
        items = items_U1()
    elif r == 'N2':
        items = items_N2(a.laws.split(','))
    elif r == 'P2':
        items = items_P2(a.from_runs.split(','), a.mult)
    else:
        raise SystemExit('unknown run ' + r)
    if a.sample:
        sample = items[::a.sample]
        common.OUT = '/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/7d6e7b9e-634d-564b-a5b8-21bd756b246b/' \
                     'scratchpad/wbcb_impl/timing'
        meta = run_items(r, sample, a.procs, 0, suffix='_sample')
        secs = [x['wall_seconds'] for x in meta['index']]
        log('sample', len(sample), 'items: wall', meta['wall_seconds'], 's; item seconds sum', round(sum(secs), 1),
            'max', max(secs) if secs else None, '; estimate for', len(items), 'items:',
            round(sum(secs) * len(items) / max(1, len(sample)) / a.procs, 1), 's on', a.procs, 'processes')
        return
    meta = run_items(r, items, a.procs, a.deadline, suffix='' if r != 'P2' else '_x%d' % a.mult)
    log('run', r, 'done', meta['done'], 'of', meta['items'], 'cut at', meta['cut_at'], 'wall', meta['wall_seconds'])


def items_P2(from_runs, mult):
    """P2: the items of the runs named whose run A or some barred run stopped at the guard at x1, again with the
    guard's limits multiplied by `mult` (BD2 1.2)."""
    out = []
    for r in from_runs:
        meta = json.load(open(common.out_path('run%s_index.json' % r)))
        stopped = set()
        for rec in common.read_jsonl('run%s.jsonl.gz' % r):
            g = rec.get('stop') == 'guard' or any(p.get('barred_run', {}).get('stop') == 'guard'
                                                  for p in rec.get('pairs', []))
            if g:
                stopped.add(rec['id'])
        for it in globals()['items_' + ('search' if r in ('1a', '1b', '1c') else r)](
                *((r,) if r in ('1a', '1b', '1c') else ())):
            if it['id'] in stopped:
                it = dict(it)
                it['cfg'] = dict(it['cfg'])
                it['cfg']['mult'] = mult
                it['id'] = it['id'] + '|x%d' % mult
                out.append(it)
    return out


if __name__ == '__main__':
    main()
