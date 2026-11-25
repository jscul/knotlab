"""Part 9: the engine check of TD 7.3's agreement rule (PR part 9; R 35) on the 100 census starts, six laws, both knot
laws, 3 rounds, grown by the fold study's engine."""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction as Fr
from multiprocessing import Pool

from pysat.solvers import Solver

import tc

sys.path.insert(0, tc.REPO + '/experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
import pm  # noqa: E402

LAWS = {
    'ORDINARY': dict(ration='ORD', treatment='STALL', release='RELEASE'),
    'Q-OLDEST': dict(ration='ORD', treatment='STALL', release='RELEASE', take='Q', choice='OLDEST'),
    'Q-NEWEST': dict(ration='ORD', treatment='STALL', release='RELEASE', take='Q', choice='NEWEST'),
    'RING-LAW': dict(ration='CAP-3', treatment='CANCEL-WAIT', release='RELEASE'),
    'COPY-LAW(CANCEL-RETIRE)': dict(ration='FLOOR1', treatment='CANCEL-RETIRE', release='RELEASE'),
    'COPY-LAW(CANCEL-RETIRE)+MET(OLDEST)': dict(ration='FLOOR1', treatment='CANCEL-RETIRE', release='RELEASE',
                                                take='MET', choice='OLDEST'),
}
PATTERN_CAP = 1 << 16
DIRECT_CAP = 24


def rule_round(S, births):
    """TD 7.3 at one round (not-all-equal): whether prod_i m_i(o) is the same for every allowed old state o of S."""
    var = [b for b in births if len(set(b['inputs'])) >= 2]
    const = 1
    for b in births:
        if len(set(b['inputs'])) < 2:
            const *= (1 << b['f']) - 1
    if not var:
        return {'verdict': 'agree', 'varying births': 0, 'patterns': 1}
    n = S.n_distinctions
    sat = Solver(name='minisat22')
    try:
        for u in range(S.n_knots):
            vs = [d + 1 for d in S.places[u]]
            sat.add_clause(vs)
            sat.add_clause([-v for v in vs])
        top = n
        ind = []
        for b in var:
            O = sorted(set(b['inputs']))
            t, g, e = top + 1, top + 2, top + 3
            top += 3
            for o in O:
                sat.add_clause([-t, o + 1])
                sat.add_clause([-g, -(o + 1)])
            sat.add_clause([t] + [-(o + 1) for o in O])
            sat.add_clause([g] + [o + 1 for o in O])
            sat.add_clause([-e, t, g])
            sat.add_clause([e, -t])
            sat.add_clause([e, -g])
            ind.append(e)
        # which indicators vary
        varying = []
        fixed = {}
        for i, e in enumerate(ind):
            a1 = sat.solve(assumptions=[e])
            a0 = sat.solve(assumptions=[-e])
            assert a1 or a0, 'no allowed state'
            if a1 and a0:
                varying.append(i)
            else:
                fixed[i] = 1 if a1 else 0
        base = const
        for i, v in fixed.items():
            base *= (1 << var[i]['f']) - v
        if not varying:
            return {'verdict': 'agree', 'varying births': 0, 'patterns': 1}
        prods = set()
        pats = 0
        while sat.solve():
            m = sat.get_model()
            pat = tuple(1 if m[ind[i] - 1] > 0 else 0 for i in varying)
            pats += 1
            p = base
            for i, v in zip(varying, pat):
                p *= (1 << var[i]['f']) - v
            prods.add(p)
            if len(prods) > 1:
                return {'verdict': 'part', 'varying births': len(varying), 'patterns': pats}
            if pats >= PATTERN_CAP:
                return {'verdict': 'undecided', 'varying births': len(varying), 'patterns': pats}
            sat.add_clause([(-ind[i] if v else ind[i]) for i, v in zip(varying, pat)])
        return {'verdict': 'agree', 'varying births': len(varying), 'patterns': pats}
    finally:
        sat.delete()


def direct(snaps, records, j, knot_law):
    """Both countings through round j by enumeration; returns (agree, tv) or None when too large."""
    S = snaps[j]
    if S.n_distinctions > DIRECT_CAP:
        return None
    rule = 'nae' if knot_law == 'nae' else 'even'
    stages = [[(rule, tuple('d%d' % d for d in snaps[0].places[u])) for u in range(snaps[0].n_knots)]]
    for r in range(1, j + 1):
        st = []
        for b in records[r - 1]['births']:
            st.append((rule, tuple('d%d' % d for d in snaps[r].places[b['id']])))
        stages.append(st)
    H = tc.History(stages)
    Wt, kept = tc.counting(H, 0, renorm=False)
    d = tc.as_dict(H, Wt)
    N = len(H.A[H.t])
    u = Fr(1, N)
    tv = sum((abs(x - u) for x in d.values()), Fr(0)) / 2
    return {'agree': tv == 0, 'tv': tv, 'kept': kept, 'states': N}


def one(job):
    tc.cap_memory()
    st, lawname, knot_law = job
    law = pm.Law(knot_law=knot_law, closing='IMPLIED', **LAWS[lawname])
    S0 = pm.from_stars(st['stars'])
    run = pm.Run(S0, law, rounds=3)
    recs = run.records
    snaps = run.snap
    out = {'census_index': st['census_index'], 'law': lawname, 'knot law': knot_law, 'rounds done': run.rounds_done,
           'stop': run.stop, 'births per round': [r['n_births'] for r in recs],
           'stalled': [r['stalled'] for r in recs], 'rounds': []}
    agree_so_far = True
    first_part = None
    for j in range(1, run.rounds_done + 1):
        births = recs[j - 1]['births']
        row = {'round': j, 'births': len(births)}
        if agree_so_far:
            if knot_law == 'parity':
                row.update({'verdict': 'agree', 'varying births': 0, 'patterns': 1,
                            'note': 'parity births: m_i constant'})
            else:
                row.update(rule_round(snaps[j - 1], births))
            if row['verdict'] == 'part':
                first_part = j
                agree_so_far = False
            elif row['verdict'] == 'undecided':
                agree_so_far = None
        dc = direct(snaps, recs, j, knot_law)
        if dc is None:
            row['direct'] = 'not computed (size)'
        else:
            row['direct'] = {'agree': dc['agree'], 'tv': tc.fstr(dc['tv']), 'kept': tc.fstr(dc['kept']),
                             'states': dc['states']}
            if 'verdict' in row and row['verdict'] in ('agree', 'part'):
                rule_agree_through = row['verdict'] == 'agree'
                row['rule matches direct'] = rule_agree_through == dc['agree']
        out['rounds'].append(row)
        if agree_so_far is None:
            break
    out['first parting round'] = first_part
    out['made a birth'] = any(n > 0 for n in out['births per round'])
    out['undecided'] = agree_so_far is None
    return out


def main():
    T0 = time.time()
    tc.cap_memory()
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    ci = json.load(open(tc.REPO + '/research/TWO-COUNTINGS-20261125-001A/census_index.json'))
    jobs = [(st, l, k) for st in ci['starts'] for l in LAWS for k in ('parity', 'nae')]
    with Pool(nproc) as pool:
        rows = list(pool.imap(one, jobs, chunksize=6))
    counts = {}
    for l in LAWS:
        for k in ('parity', 'nae'):
            rs = [r for r in rows if r['law'] == l and r['knot law'] == k]
            mb = [r for r in rs if r['made a birth']]
            counts['%s / %s' % (l, k)] = {
                'growths': len(rs), 'made a birth': len(mb),
                'first parting at round': {str(k2): v for k2, v in sorted(Counter(r['first parting round'] for r in mb
                                                                                  if r['first parting round']).items())},
                'not parted through the rounds done': sum(1 for r in mb if r['first parting round'] is None
                                                         and not r['undecided']),
                'undecided': sum(1 for r in mb if r['undecided']),
                'rounds checked directly': sum(1 for r in rs for x in r['rounds'] if isinstance(x.get('direct'), dict)),
                'rule against direct: mismatches': sum(1 for r in rs for x in r['rounds']
                                                       if x.get('rule matches direct') is False)}
    mism = [(r['census_index'], r['law'], r['knot law'], x['round']) for r in rows for x in r['rounds']
            if x.get('rule matches direct') is False]
    out = {'part': 9, 'growths': len(rows), 'counts': counts, 'mismatches (a bug)': mism, 'rows': rows,
           'wall_s': round(time.time() - T0, 1), 'processes': nproc}
    tc.dump('part9_engine_check.json', out)
    for k, v in counts.items():
        print(k, v)
    print('mismatches', mism, 'wall', out['wall_s'])


if __name__ == '__main__':
    main()
