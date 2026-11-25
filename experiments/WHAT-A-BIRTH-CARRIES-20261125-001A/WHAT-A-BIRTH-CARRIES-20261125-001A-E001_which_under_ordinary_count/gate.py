"""Run G (RD 5.3): the engine against the fold engine on 648 runs; the gate listing birth by birth; the four
attribution records; 100 pairs of numberings related by a symmetry.

  python -B gate.py engine --chunk i/n     (the 648 runs, in chunks)
  python -B gate.py rest                   (listing, records, symmetric pairs)
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import os
import random
import time
from collections import Counter

import common
from common import log
import wbc
import pm

RATIONS = ('FLOOR1', 'CAP-3', 'ORD')
TREATMENTS = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
KNOT_LAWS = ('nae', 'parity')
TAKES = ((None, 'OLDEST'), ('MET', 'OLDEST'), ('MET', 'NEWEST'))


def g_starts():
    out = [(name, pm.STARS[name]) for name in pm.STARS]
    reg = common.numberings()['registered']
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
    mine = wbc.Law(ration=r, treatment=t, take=take, choice=ch, knot_law=kl)
    snaps, recs, stop, gd = wbc.plain_run(stars, mine, rounds=6, knot_bound=800)
    t1 = time.time()
    theirs = pm.Law(ration=r, treatment=t, release='RELEASE', knot_law=kl, closing='IMPLIED', take=take, choice=ch)
    R = pm.Run(pm.from_stars(stars), theirs, rounds=6, knot_bound=800)
    t2 = time.time()
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
    gA = None if gd is None else (gd['round'], gd['what'])
    gB = None if R.guard is None else (R.guard['round'], R.guard['what'])
    sB = R.stop
    if stop != sB or gA != gB:
        diffs.append('stop: mine %s %s, fold engine %s %s' % (stop, gA, sB, gB))
    return {'start': sname, 'ration': r, 'treatment': t, 'knot_law': kl, 'take': take, 'choice': ch,
            'rounds_read': len(snaps) - 1, 'stop': stop, 'guard': gA, 'knots': snaps[-1].n_knots,
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
def listing_text(h, usable):
    stars = common.numberings()['registered']['made-%d' % h]
    law = wbc.Law('ORD', 'CANCEL-RETIRE', 'MET', 'OLDEST', 'nae')
    run = wbc.RunState(stars, usable, law)
    lines = ['=== made-%d, a = %d (Y members left usable: those whose input is among %s), '
             'ORD/CANCEL-RETIRE/MET(OLDEST), not-all-equal' % (h, len(usable), usable)]
    for rec in run.recs[:3]:
        retired = [u for u in rec['members'] if rec['act'].get(u) == 'retire']
        if rec['round'] <= 2:
            lines.append(' round %d: %d groups %s; short %s; retired %s' % (
                rec['round'], len(rec['groups']), [list(g) for g in rec['groups']], rec['short'], retired))
            for b in rec['births']:
                lines.append('   knot %d %s parents %s inputs %s (taken %s) D=%d p=%d f=%d' % (
                    b['id'], b['kind'], list(b['parents']), b['inputs'], b['takes'], b['D'], b['p'], b['f']))
        else:
            lines.append(' round %d: %d groups; short %s; retired %s' % (rec['round'], len(rec['groups']),
                                                                         rec['short'], retired))
            c = Counter((b['kind'], len(b['parents']), tuple(b['takes']), b['D'], b['f']) for b in rec['births'])
            lines.append('   %d births; (kind, parents, taken, D, f): %s' % (len(rec['births']), sorted(c.items())))
    run3 = wbc.RunState(stars, usable, law, rounds=3)
    kt = wbc.knot_test(run3)
    lines.append(' knot test: %d verdicts, %d failing' % (kt['verdicts'], len(kt['fails'])))
    return lines, run


def gate_listing():
    with open(os.path.join(common.TICKET, 'gate_listing.txt')) as f:
        want = f.read().rstrip('\n').split('\n')
    got = []
    extra = {}
    for usable in ([3, 4, 5, 6], [3]):
        lines, run = listing_text(4, usable)
        got += lines
        extra['a=%d' % len(usable)] = {'rounds_read': run.rounds_read, 'stop': run.stop, 'guard': run.guard}
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(want, got)) if a != b]
    if len(want) != len(got):
        diffs.append(('length', len(want), len(got)))
    return {'equal': not diffs, 'diffs': diffs, 'lines_compared': len(want), 'registered_bounds_runs': extra,
            'got': got}


def attribution_records():
    with open(os.path.join(common.TICKET, 'attribution_records.json')) as f:
        recs = json.load(f)['records']
    out = []
    for r in recs:
        fd = wbc.record_attribution(r)
        got = {'first_differing': fd and fd['pos'], 'class': fd and fd['class']}
        out.append({'name': r['name'], 'expected': r['expected'], 'got': got,
                    'equal': got == r['expected']})
    return out


# ------------------------------------------------------------------------------------- symmetric numberings
def run_signature(run):
    """Everything a run reads, with the places of each knot as a set (the listed order is what the symmetry
    changes)."""
    sig = []
    for S in run.snaps:
        sig.append((S.round, [sorted(p) for p in S.places], [sorted(h) for h in S.holders], S.barred, S.parents,
                    S.kind, S.made))
    recs = [[(b['id'], b['kind'], b['parents'], sorted(b['inputs']), b['takes'], b['D'], b['p'], b['f'],
              b['implied']) for b in r['births']] for r in run.recs]
    vals = {t: [(e['pos'], e['value']) for e in E] for t, E in run.values.items()}
    courses = [wbc.course_invariant(c) if c else None for c in (wbc.course(run, R) for R in (2, 3, 4))]
    return (sig, recs, vals, courses, run.meet_round, run.stop, run.guard and run.guard['what'])


def symmetric_pairs(n=100):
    rng = random.Random('WBC-20261125-G-symmetric-pairs')
    rows = []
    cls = {h: common.class_by_nu(h) for h in (3, 4)}
    for i in range(n):
        h = rng.choice((3, 4))
        nu_i, stars, entries = rng.choice(cls[h])
        a, usable = rng.choice(entries)
        choice = rng.choice(('OLDEST', 'NEWEST'))
        kl = rng.choice(('nae', 'parity'))
        xs = 0 if len(stars[0]) == 3 else 1
        ys = 1 - xs
        e = (set(stars[0]) & set(stars[1])).pop()
        xl = [d for d in stars[xs] if d != e]
        yl = [d for d in stars[ys] if d != e]
        sx, sy = xl[:], yl[:]
        while sx == xl and sy == yl:
            rng.shuffle(sx)
            rng.shuffle(sy)
        sigma = {e: e}
        sigma.update(dict(zip(xl, sx)))
        sigma.update(dict(zip(yl, sy)))
        stars2 = [[sigma[d] for d in st] for st in stars]
        law = wbc.Law('ORD', 'CANCEL-RETIRE', 'MET', choice, kl)
        r1 = wbc.RunState(stars, usable, law)
        r2 = wbc.RunState(stars2, usable, law)
        same_set = all(sorted(a_) == sorted(b_) for a_, b_ in zip(stars, stars2))
        eq = run_signature(r1) == run_signature(r2)
        rows.append({'i': i, 'h': h, 'nu': nu_i, 'usable': usable, 'choice': choice, 'knot_law': kl,
                     'stars': stars, 'stars_listed': stars2, 'same_named_start': same_set, 'identical': eq})
    return rows


def rest():
    common.cap_memory(6)
    t0 = time.time()
    gl = gate_listing()
    log('gate listing equal:', gl['equal'], gl['diffs'][:3])
    ar = attribution_records()
    for r in ar:
        log('record', r['name'], 'equal' if r['equal'] else 'DIFFERS', r['got'])
    sp = symmetric_pairs()
    log('symmetric pairs identical:', sum(r['identical'] for r in sp), 'of', len(sp))
    common.write_json('G_rest.json', {'gate_listing': gl, 'attribution_records': ar, 'symmetric_pairs': sp,
                                      'seconds': round(time.time() - t0, 1)})


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
