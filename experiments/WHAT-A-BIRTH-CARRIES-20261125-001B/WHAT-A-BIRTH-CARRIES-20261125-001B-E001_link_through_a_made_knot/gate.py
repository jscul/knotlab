"""Run G: the engine against the fold engine on ticket A's 648 gate runs; gate_listing_b.txt reproduced birth by
birth; ticket A's four attribution records.

  python -B gate.py engine --chunk i/n
  python -B gate.py rest
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import os
import time

import common
from common import log
import eng
import pm
import wbc

RATIONS = ('FLOOR1', 'CAP-3', 'ORD')
TREATMENTS = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
KNOT_LAWS = ('nae', 'parity')
TAKES = ((None, 'OLDEST'), ('MET', 'OLDEST'), ('MET', 'NEWEST'))


def g_starts():
    out = [(name, pm.STARS[name]) for name in pm.STARS]
    with open(os.path.join(common.TICKET_A, 'numberings.json')) as f:
        reg = json.load(f)['registered']
    out += [('made-2', [[0, 1, 2], [0, 3, 4]])] + [('made-%d' % h, reg['made-%d' % h]) for h in (3, 4, 5, 6)]
    assert len(out) == 12
    return out


def g_cases():
    cases = []
    for sname, stars in g_starts():
        for r in RATIONS:
            for t in TREATMENTS:
                for kl in KNOT_LAWS:
                    for take, ch in TAKES:
                        cases.append((sname, stars, r, t, kl, take, ch))
    assert len(cases) == 648
    return cases


def compare_one(case):
    sname, stars, r, t, kl, take, ch = case
    t0 = time.time()
    mine = eng.Law(ration=r, treatment=t, take=take, knot_law=kl, choice=ch if take else None)
    run = eng.run_stars(stars, mine, rounds=6, knot_bound=800)
    t1 = time.time()
    theirs = pm.Law(ration=r, treatment=t, release='RELEASE', knot_law=kl, closing='IMPLIED', take=take, choice=ch)
    R = pm.Run(pm.from_stars(stars), theirs, rounds=6, knot_bound=800)
    t2 = time.time()
    snaps, recs = run.snaps, run.recs
    diffs = []
    if len(snaps) != len(R.snap):
        diffs.append('rounds read: mine %d, fold engine %d' % (len(snaps) - 1, len(R.snap) - 1))
    for i, (A, B) in enumerate(zip(snaps, R.snap)):
        if A.places != B.places:
            diffs.append('round %d: places' % i)
        if [tuple(p) for p in A.parents] != [tuple(p) for p in B.parents]:
            diffs.append('round %d: parents' % i)
        if A.made != B.made or A.kind != B.kind:
            diffs.append('round %d: made/kind' % i)
        if A.barred != B.barred:
            diffs.append('round %d: barred' % i)
    for ra, rb in zip(recs, R.records):
        ba = [(b['id'], b['kind'], list(b['parents']), b['inputs'], b['takes'], b['D'], b['p'], b['f'],
               b['implied'], b['fresh']) for b in ra['births']]
        bb = [(b['id'], b['kind'], list(b['parents']), b['inputs'], b['rule_takes'], b['D'], b['p'], b['f'],
               b['implied'], b['fresh']) for b in rb['births']]
        if ba != bb:
            diffs.append('round %d: births' % ra['round'])
        if [list(g) for g in ra['groups']] != rb['groups'] or sorted(ra['short']) != sorted(rb['short']):
            diffs.append('round %d: groups/short' % ra['round'])
        if ra['closing'] != rb['closing']:
            diffs.append('round %d: closing' % ra['round'])
    gA = None if run.guard is None else (run.guard['round'], run.guard['what'])
    gB = None if R.guard is None else (R.guard['round'], R.guard['what'])
    if run.stop != R.stop or gA != gB:
        diffs.append('stop: mine %s %s, fold engine %s %s' % (run.stop, gA, R.stop, gB))
    return {'start': sname, 'ration': r, 'treatment': t, 'knot_law': kl, 'take': take, 'choice': ch,
            'rounds_read': len(snaps) - 1, 'stop': run.stop, 'guard': gA, 'knots': snaps[-1].n_knots,
            'equal': not diffs, 'diffs': diffs[:5], 'sec_mine': round(t1 - t0, 3), 'sec_fold': round(t2 - t1, 3)}


def engine(chunk):
    i, n = (int(x) for x in chunk.split('/'))
    common.cap_memory(6)
    cases = g_cases()
    out = common.JsonLines('G_engine_%d_of_%d.jsonl' % (i, n))
    neq = 0
    for ci, c in enumerate(cases):
        if ci % n != i:
            continue
        row = compare_one(c)
        row['case'] = ci
        out.write(row)
        if not row['equal']:
            neq += 1
            log('DIFFERS', row)
    out.close()
    log('chunk', chunk, 'differing', neq)


# ------------------------------------------------------------------------------------------- the gate listing
LISTING_CASES = (
    ('three-knot', eng.Law('PARENT-OWING', 'CANCEL-OFFSHOOT', 'MET-SOLE', 'nae'), 3),
    ('Ring(5,3)', eng.Law('FLOOR1', 'SHORT-BY', 'MET-SOLE', 'nae'), 2),
    ('two-knot', eng.Law('FLOOR1', 'CANCEL-WAIT', 'STEPS1-SOLE', 'parity'), 3),
)


def round_lines(rec):
    retired = [u for u in rec['members'] if rec['act'].get(u) == 'retire']
    waiting = [u for u in rec['members'] if rec['act'].get(u) == 'wait']
    owe = dict(sorted(rec['owe'].items()))
    lines = [' round %d: groups %s; short %s; owing %s; retired %s; waiting %s' % (
        rec['round'], [list(g) for g in rec['groups']], rec['short'], owe, retired, waiting)]
    for b in rec['births']:
        lines.append('   knot %d %s parents %s inputs %s (taken %s) D=%d p=%d f=%d' % (
            b['id'], b['kind'], list(b['parents']), b['inputs'], b['takes'], b['D'], b['p'], b['f']))
    return lines


def gate_listing():
    starts = common.load('starts.json')['stars']
    with open(os.path.join(common.TICKET, 'gate_listing_b.txt')) as f:
        want = [ln for ln in f.read().rstrip('\n').split('\n')[1:]]
    got = []
    for sname, law, R in LISTING_CASES:
        run = eng.run_stars(starts[sname], law)
        got.append('=== %s, %s, rounds 1..%d' % (sname, law.name(), R))
        for rec in run.recs[:R]:
            got += round_lines(rec)
        kt = knots.test_run(run.snaps[:R + 1], law)
        got.append(' knot test: %d verdicts, %d failing' % (kt['verdicts'], len(kt['fails'])))
    # the header lines name the law in the prototype's words; every other line is compared exactly
    wb = [ln for ln in want if not ln.startswith('===')]
    gb = [ln for ln in got if not ln.startswith('===')]
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(wb, gb)) if a != b]
    if len(wb) != len(gb):
        diffs.append(('length', len(wb), len(gb)))
    return {'equal': not diffs, 'diffs': diffs, 'lines_compared': len(wb), 'got': got}


def attribution_records():
    with open(os.path.join(common.TICKET_A, 'attribution_records.json')) as f:
        recs = json.load(f)['records']
    out = []
    for r in recs:
        fd = wbc.record_attribution(r)
        got = {'first_differing': fd and fd['pos'], 'class': fd and fd['class']}
        out.append({'name': r['name'], 'expected': r['expected'], 'got': got, 'equal': got == r['expected']})
    return out


def rest():
    common.cap_memory(6)
    t0 = time.time()
    gl = gate_listing()
    log('gate listing equal:', gl['equal'], gl['diffs'][:3])
    ar = attribution_records()
    for r in ar:
        log('record', r['name'], 'equal' if r['equal'] else 'DIFFERS', r['got'])
    common.write_json('G_rest.json', {'gate_listing': gl, 'attribution_records': ar,
                                      'seconds': round(time.time() - t0, 1)})


import knots  # noqa: E402  (unchanged; read-only; the fold folder is on the path through eng)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('engine', 'rest'))
    ap.add_argument('--chunk', default='0/1')
    a = ap.parse_args()
    common.check_frozen()
    if a.what == 'engine':
        engine(a.chunk)
    else:
        rest()
