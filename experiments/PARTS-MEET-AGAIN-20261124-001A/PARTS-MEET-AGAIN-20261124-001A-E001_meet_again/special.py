"""Runs 4, 5 and 6.

run4 - the named cases round by round (births, met sets, parts), the four marks, "the choice is necessary" (only the
       takes of X and its descendants use another choice), the course with what the other is (larger founder), the
       swaps of P9 and P10, and the control of P13 on Ring(5, 3); the knot tests.
run5 - the swap battery: every case (law, base law, start, kind of pair) of runs 1 and 3 with a confirmed "course
       differs" mark under not-all-equal, with each swap.
run6 - the A225 control placed by hand.

usage: python -B special.py run4|run5|run6 [--procs n]
"""
import argparse
import gzip
import json
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

import common as C
import knots as K
import paired as P
import pm

COPY = {'RETIRE': 'CANCEL-RETIRE', 'OFFSHOOT': 'CANCEL-OFFSHOOT', 'WAIT': 'CANCEL-WAIT'}


def base_kw(base):
    """'COPY-LAW(RETIRE)', 'CAP-3(WAIT)', 'RING-LAW' -> Law kwargs."""
    if base == 'RING-LAW':
        return dict(ration='CAP-3', treatment='CANCEL-WAIT')
    nm, t = base.split('(')
    t = COPY[t.rstrip(')')]
    return dict(ration='FLOOR1' if nm == 'COPY-LAW' else 'CAP-3', treatment=t)


def take_kw(law_name):
    if law_name == 'none':
        return {}
    if law_name in ('RECORD-2', 'RECORD-3'):
        return dict(joinable=law_name)
    if law_name == 'ALL-JOINABLE':
        return dict(joinable='ALL')
    if law_name == 'CARRY':
        return dict(take='CARRY')
    if law_name.startswith('FIRST'):
        return dict(take='FIRST', choice='OLDEST')
    late = law_name.startswith('late ')
    nm = law_name[5:] if late else law_name
    rule, ch = nm.split('(')
    ch = ch.rstrip(')')
    if rule == 'SHORT-TAKES':
        d = dict(treatment='SHORT-TAKES', choice=ch)
    else:
        d = dict(take=rule, choice=ch)
    if late:
        d['late'] = 'LATE'
    return d


def make_law(base, law_name, knot_law='nae', start=None, **extra):
    kw = base_kw(base)
    tk = take_kw(law_name)
    if tk.get('late') == 'LATE':
        tk['late'] = pm.LATE_S0[start]
        if tk.get('treatment') == 'SHORT-TAKES':
            tk['base_treatment'] = kw['treatment']
    kw.update(tk)
    kw.update(extra)
    return pm.Law(knot_law=knot_law, **kw)


# --------------------------------------------------------------------------------------------- listings, controls
def listing(run, upto=None):
    """Round by round: births (parents, inputs, holders of each input at the start of the round, fresh), met sets, parts."""
    rows = []
    upto = run.rounds_done if upto is None else upto
    view = P.RunView(run)
    for t in range(1, upto + 1):
        rec = run.records[t - 1]
        Sb = run.snap[t - 1]
        R = view.roster(t)
        rows.append({'t': t, 'groups': rec['groups'], 'short': rec['short'], 'retired': rec['retired'],
                     'waiting': rec['waiting'],
                     'births': [{'id': b['id'], 'kind': b['kind'], 'parents': b['parents'], 'inputs': b['inputs'],
                                 'holders_at_start': {str(d): list(Sb.holders[d]) for d in b['inputs']},
                                 'rule_takes': b['rule_takes'], 'given_shared': b['given_shared'], 'D': b['D'],
                                 'f': b['f'], 'usable': b['usable'], 'barred': b['barred'], 'implied': b['implied']}
                                for b in rec['births']],
                     'metsets': [[sorted(M), list(c)] for M, c in zip(R.maxsets, R.commons)],
                     'parts': [list(p) for p in R.parts]})
    return rows


def choice_is_necessary(view, s, X, Y, choices=('OLDEST', 'NEWEST', 'IN-TURN', 'BY-COUNT', 'BY-RECEIVED')):
    """D 5.4: only the takes of X and its descendants (births all of whose parents are there) use another choice."""
    A = view.run
    out = {}
    for c in choices:
        res = {}
        for which in ('A', 'B'):
            tr = P.SideTracker(side_of_now(A, X, s))

            def choice_of(S, b, tr=tr):
                if all(p in tr.xd for p in b['parents']):
                    return c
                return None
            S = A.snap[s] if which == 'A' else P.bar_part(A.snap[s], Y)
            r = pm.Run(S, A.law, ctx={'choice_of': choice_of}, records=A.records[:s], snapshots=A.snap[:s],
                       on_round=tr.on_round)
            res[which] = r
        d, way, dem, n = P.first_difference(P.trace(res['A'], X, s), P.trace(res['B'], X, s))
        out[c] = {'course_differs': d, 'way': way, 'demand_line': dem, 'rounds_compared': n}
    return out


def side_of_now(run, X, s):
    return P.side_of(run.snap[s], X, s)


def what_the_other_is(view, s, X, start_name, law, variant='three-knot-larger'):
    """D 5.3, fourth mark: X's course in run A against run A from the larger-founder start (R 26)."""
    A = view.run
    S = A.snap[s]
    anc = set()
    for u in X:
        anc |= {a for a in P.anc_or_self(S, u) if S.made[a] == 0}
    V = pm.Run(pm.start(variant), law)
    vv = P.RunView(V)
    if V.rounds_done < s:
        return {'found': False, 'note': 'the variant run ends before round s'}
    Rs = vv.roster(s)
    cands = []
    for Pt in Rs.parts:
        a2 = set()
        for u in Pt:
            a2 |= {a for a in P.anc_or_self(V.snap[s], u) if V.snap[s].made[a] == 0}
        if a2 == anc:
            cands.append(list(Pt))
    Ra = view.roster(s)
    same_anc = []
    for Pt in Ra.parts:
        a2 = set()
        for u in Pt:
            a2 |= {a for a in P.anc_or_self(S, u) if S.made[a] == 0}
        if a2 == anc:
            same_anc.append(list(Pt))
    idx = same_anc.index(sorted(X)) if sorted(X) in same_anc else 0
    if idx >= len(cands):
        return {'found': False, 'note': 'no part with the same start ancestry', 'candidates': cands}
    X2 = cands[idx]
    t1 = P.first_appearance(P.trace(A, X, s))
    t2 = P.first_appearance(P.trace(V, X2, s))
    n = min(len(t1), len(t2))
    d = None
    for i in range(n):
        if t1[i] != t2[i]:
            d = s + 1 + i
            break
    return {'found': True, 'X_variant': X2, 'course_differs': d, 'rounds_compared': n}


def find_pair(out, s=None, X=None):
    for p in out['pairs']:
        if (s is None or p['s'] == s) and (X is None or p['X'] == X):
            return p
    return None


def marks(p):
    if p is None:
        return None
    keys = ('s', 'X', 'Y', 'came_apart', 'wholly_apart', 'one_part_again', 'joint_birth', 'course_differs', 'way',
            'demand_line', 'confirmed', 'verdict', 'link', 'b2', 'joint_birth_detail')
    return {k: p.get(k) for k in keys}


def confirmed_marks(out, kind):
    """The confirmed "course differs" marks of one kind ('came apart' or 'first time') in an analysed run."""
    res = []
    for p in out['pairs']:
        if p.get('course_differs') is None or p.get('confirmed') is None or p['s'] == 0:
            continue
        k = 'came apart' if p['came_apart'] else 'first time'
        if k != kind:
            continue
        res.append(marks(p))
    return res


# ------------------------------------------------------------------------------------------------------------ run 4
def run4(args):
    rows = C.JsonLines('run4.jsonl')
    cases = [
        ('smallest case', 'three-knot', 'COPY-LAW(RETIRE)', 'STEPS-2(OLDEST)', (2, [6, 7], [8, 9])),
        ('through the retired join', 'three-knot', 'COPY-LAW(RETIRE)', 'STEPS-2(BY-RECEIVED)', (2, [6, 7], [8, 9])),
        ('minimal: STEPS-1(OLDEST)', 'two-knot', 'COPY-LAW(OFFSHOOT)', 'STEPS-1(OLDEST)', None),
        ('minimal: MET(NEWEST)', 'Ring(5,3)', 'CAP-3(RETIRE)', 'MET(NEWEST)', None),
        ('minimal: MET(BY-COUNT)', 'Ring(5,3)', 'CAP-3(OFFSHOOT)', 'MET(BY-COUNT)', None),
        ('larger founder, STEPS-2(OLDEST)', 'three-knot-larger', 'COPY-LAW(RETIRE)', 'STEPS-2(OLDEST)', None),
    ]
    for label, st, base, lname, pair in cases:
        for kl in ('nae', 'parity'):
            t0 = time.time()
            law = make_law(base, lname, kl, st)
            out, view = P.analyse_run(st, law, every_pair=False)
            row = {'case': label, 'start': st, 'base': base, 'law_name': lname, 'knot_law': kl, 'law': law.name(),
                   'rounds': out['rounds'], 'stop': out['stop'], 'knots': out['knots'], 'listing': listing(view.run),
                   'knot_tests': out['knot_tests'], 'pairs': [marks(p) for p in out['pairs']],
                   'per_round': out['per_round']}
            targets = []
            if pair is not None:
                targets.append(pair)
            for p in out['pairs']:
                if p.get('course_differs') is not None and (p['s'], p['X'], p['Y']) not in targets:
                    targets.append((p['s'], p['X'], p['Y']))
            row['choice_is_necessary'] = []
            for (s, X, Y) in targets[:6]:
                row['choice_is_necessary'].append({'s': s, 'X': X, 'Y': Y,
                                                   'by_choice': choice_is_necessary(view, s, X, Y)})
            if st == 'three-knot':
                row['what_the_other_is'] = []
                for (s, X, Y) in targets[:6]:
                    row['what_the_other_is'].append({'s': s, 'X': X, 'Y': Y,
                                                     **what_the_other_is(view, s, X, st, law)})
            row['seconds'] = round(time.time() - t0, 1)
            rows.write(row)
            C.log(label, kl, 'done', row['seconds'])
    # P9 and P10: the swaps of the smallest case and of the case through the retired join
    sw = [('parity', dict(knot_law='parity'), {}), ('order reversed', {}, dict(order_reversed=True)),
          ('demand before the takes', {}, dict(demand_before_takes=True)),
          ('fresh by parents', {}, dict(fresh_by_parents=True)), ('HOLD', {}, dict(release='HOLD')),
          ('names reversed', dict(rev=True), {}), ('NEWEST', dict(law_name='STEPS-2(NEWEST)'), {}),
          ('BY-COUNT', dict(law_name='STEPS-2(BY-COUNT)'), {}), ('CAP-3', dict(base='CAP-3(RETIRE)'), {}),
          ('UP-TO-2', dict(rule='UP-TO-2'), {})]
    for label, lname in (('smallest case', 'STEPS-2(OLDEST)'), ('through the retired join', 'STEPS-2(BY-RECEIVED)')):
        for swname, ctl, lawextra in sw:
            base = ctl.get('base', 'COPY-LAW(RETIRE)')
            ln = ctl.get('law_name', lname)
            if ctl.get('rule'):
                ln = ln.replace('STEPS-2', ctl['rule'])
            kl = ctl.get('knot_law', 'nae')
            law = make_law(base, ln, kl, 'three-knot', **lawextra)
            out, view = P.analyse_run('three-knot', law, rev=ctl.get('rev', False),
                                      every_pair=(lawextra.get('release') == 'HOLD'))
            cm = confirmed_marks(out, 'came apart')
            rows.write({'case': label, 'swap': swname, 'law': law.name(), 'names_reversed': ctl.get('rev', False),
                        'confirmed_came_apart': cm, 'stands': bool(cm),
                        'all_marks': [marks(p) for p in out['pairs'] if p.get('course_differs') is not None],
                        'knot_tests': out['knot_tests'], 'listing': listing(view.run, min(5, view.run.rounds_done))})
            C.log('swap', label, swname, 'stands' if cm else 'vanishes', [m['verdict'] for m in cm])
    # P13, second half: Ring(5, 3), RING-LAW, STEPS-2(OLDEST): every registered pair in both orientations
    law = make_law('RING-LAW', 'STEPS-2(OLDEST)', 'nae', 'Ring(5,3)')
    out, view = P.analyse_run('Ring(5,3)', law)
    ring_rounds = {}
    R0 = view.roster(0)
    for t in range(1, view.R + 1):
        Rt = view.roster(t)
        ring_rounds[t] = [list(Pt) for Pt in Rt.parts if len(Pt) == len(R0.members) and
                          P.same_parts(R0, R0.members, Rt, Pt)]
    tests = []
    for p in out['pairs']:
        for (X, Y) in ((p['X'], p['Y']), (p['Y'], p['X'])):
            tests.append({'s': p['s'], 'X': X, 'Y': Y, 'X_is_ring_part': X in ring_rounds.get(p['s'], []),
                          'Y_is_ring_part': Y in ring_rounds.get(p['s'], []),
                          'by_choice': choice_is_necessary(view, p['s'], X, Y)})
    rows.write({'case': 'P13 ring', 'law': law.name(), 'ring_parts_by_round': ring_rounds, 'tests': tests,
                'pairs': [marks(p) for p in out['pairs']], 'listing': listing(view.run, min(5, view.R))})
    rows.close()


# ------------------------------------------------------------------------------------------------------------ run 5
SWAPS5 = ['names reversed', 'order reversed', 'demand before the takes', 'fresh by parents', 'HOLD', 'ration',
          'STEPS-k/UP-TO-k', 'knot law']


def swapped(base, lname, st, swap):
    """(law, rev, every_pair) for a swap, or None when the swap does not apply."""
    rev = False
    extra = {}
    b, ln, kl = base, lname, 'nae'
    if swap == 'names reversed':
        rev = True
    elif swap == 'order reversed':
        extra['order_reversed'] = True
    elif swap == 'demand before the takes':
        extra['demand_before_takes'] = True
    elif swap == 'fresh by parents':
        extra['fresh_by_parents'] = True
    elif swap == 'HOLD':
        extra['release'] = 'HOLD'
    elif swap == 'ration':
        kw = base_kw(base)
        extra['ration'] = 'CAP-3' if kw['ration'] == 'FLOOR1' else 'FLOOR1'
    elif swap == 'STEPS-k/UP-TO-k':
        if 'STEPS-2' in ln:
            ln = ln.replace('STEPS-2', 'UP-TO-2')
        elif 'UP-TO-2' in ln:
            ln = ln.replace('UP-TO-2', 'STEPS-2')
        else:
            return None
    elif swap == 'knot law':
        kl = 'parity'
    law = make_law(b, ln, kl, st, **extra)
    return law, rev, swap == 'HOLD'


def do_case5(case):
    C.cap_memory(case.get('mem', 6))
    t0 = time.time()
    out = {'case': case, 'swaps': {}}
    try:
        for swap in SWAPS5:
            sw = swapped(case['base'], case['law_name'], case['start'], swap)
            if sw is None:
                out['swaps'][swap] = {'applies': False}
                continue
            law, rev, every = sw
            res, view = P.analyse_run(case['start'], law, rev=rev, every_pair=every)
            cm = confirmed_marks(res, case['kind'])
            out['swaps'][swap] = {'applies': True, 'law': law.name(), 'survives': bool(cm),
                                  'verdicts': sorted({m['verdict'] for m in cm}), 'n_marks': len(cm),
                                  'marks': cm[:6], 'knot_tests': {k: res['knot_tests'][k] for k in
                                                                  ('verdicts', 'n_fails', 'n_disagree', 'n_untested')}}
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


def run5_cases():
    cases = {}
    for fn in ('run1.jsonl.gz', 'run3.jsonl.gz'):
        with gzip.open(C.out_path(fn), 'rt') as f:
            for line in f:
                r = json.loads(line)
                if r.get('knot_law') != 'nae' or 'pairs' not in r:
                    continue
                for p in r['pairs']:
                    if p.get('course_differs') is None or p.get('confirmed') is None or p['s'] == 0:
                        continue
                    kind = 'came apart' if p['came_apart'] else 'first time'
                    key = (r['base'], r['start'], r['law_name'], kind)
                    c = cases.setdefault(key, {'base': r['base'], 'start': r['start'], 'law_name': r['law_name'],
                                               'kind': kind, 'verdicts': set(), 'n_marks': 0, 'from': fn})
                    c['verdicts'].add(p.get('verdict'))
                    c['n_marks'] += 1
    out = []
    for k in sorted(cases):
        c = cases[k]
        c['verdicts'] = sorted(v for v in c['verdicts'] if v)
        out.append(c)
    return out


def run5(args):
    cases = run5_cases()
    C.log('run 5:', len(cases), 'cases')
    rows = C.JsonLines('run5.jsonl')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        futs = [ex.submit(do_case5, dict(c, mem=args.mem)) for c in cases]
        for f in as_completed(futs):
            r = f.result()
            rows.write(r)
            C.log(r['case']['base'], r['case']['start'], r['case']['law_name'], r['case']['kind'],
                  {k: v.get('survives') for k, v in r['swaps'].items()}, r.get('error', ''), r['seconds'])
    rows.close()


# ------------------------------------------------------------------------------------------------------------ run 6
def place_knot(S, X, Y):
    """D 3.4: one knot, no parents, taking for X's and Y's lowest-named members the oldest distinction each holds with
    exactly one other knot, and one fresh distinction."""
    T = S.copy()
    picks = []
    for side in (X, Y):
        u = min(side)
        c = sorted(d for d in T.places[u] if len(T.holders[d]) == 2)
        if not c:
            return None, None
        picks.append(c[0])
    x = T.n_knots
    T.places.append(list(picks))
    T.parents.append(())
    T.made.append(S.round)
    T.kind.append('placed')
    for d in picks:
        T.holders[d].append(x)
    d = len(T.holders)
    T.holders.append([x])
    T.barred.append(False)
    T.places[x].append(d)
    T.cand.add(x)
    pm.span_insert(T.span, T.row(x))
    return T, {'knot': x, 'takes': picks, 'fresh': d}


def run6(args):
    rows = C.JsonLines('run6.jsonl')
    specs = [('three-knot', 'COPY-LAW(RETIRE)', 2, None), ('three-knot', 'COPY-LAW(WAIT)', 2, None),
             ('Ring(5,3)', 'RING-LAW', 2, 'ring')]
    for st, base, s, mode in specs:
        for kl in ('nae', 'parity'):
            law = make_law(base, 'none', kl, st)
            A = pm.Run(pm.start(st), law)
            view = P.RunView(A)
            Rs = view.roster(s)
            parts = [list(p) for p in Rs.parts]
            cls = pm.roster_classes(Rs)
            if mode == 'ring':
                R0 = view.roster(0)
                ring = [list(p) for p in Rs.parts if len(p) == len(R0.members) and
                        P.same_parts(R0, R0.members, Rs, p)]
                X = ring[0] if ring else None
                given = [p for p in parts if p != X]
                Y = given[0] if given else None
            else:
                # the two copies: the parts after round s whose members were all made in round s (deviations 36)
                Ss = A.snap[s]
                copies = [p for p in parts if all(Ss.made[u] == s for u in p)]
                X, Y = (copies[0], copies[1]) if len(copies) >= 2 else (None, None)
            row = {'start': st, 'base': base, 'knot_law': kl, 's': s, 'parts_after_s': parts, 'X': X, 'Y': Y}
            if X is None or Y is None:
                row['note'] = 'pair not found'
                rows.write(row)
                continue
            row['wholly_apart'] = cls[Rs.parts.index(tuple(X))] != cls[Rs.parts.index(tuple(Y))]
            T, placed = place_knot(A.snap[s], X, Y)
            row['placed'] = placed
            A2 = P.run_from(view, s, T)
            view2 = P.RunView(A2)
            B2 = P.run_from(view2, s, P.bar_part(T, Y))
            trA, trA2, trB2 = P.trace(A, X, s), P.trace(A2, X, s), P.trace(B2, X, s)
            # one part again at round s (the placed knot) or later; joint births
            R2s = pm.roster_of(T.copy(), law)
            px = {R2s.part_of[u] for u in R2s.members if u in set(X)}
            py = {R2s.part_of[u] for u in R2s.members if u in set(Y)}
            row['one_part_at_round_s_with_placed_knot'] = bool(px & py)
            row['one_part_again'] = P.one_part_again(view2, s, X, Y)
            jb = P.joint_birth(view2, s, X, Y)
            row['joint_birth'] = jb[0] if jb else None
            d1 = P.first_difference(trA2, trB2)
            d2 = P.first_difference(trA2, trA)
            row['course_differs_against_Y_barred'] = {'round': d1[0], 'way': d1[1], 'demand_line': d1[2]}
            row['course_differs_against_no_placed_knot'] = {'round': d2[0], 'way': d2[1], 'demand_line': d2[2]}
            row['verdict'] = 'supplied (the A225 knot is placed by hand)'
            row['placed_knot_record'] = [{'t': rec['round'], 'groups_with_placed': [g for g in rec['groups']
                                                                                   if placed['knot'] in g],
                                          'short': placed['knot'] in rec['short'],
                                          'retired': placed['knot'] in rec['retired'],
                                          'waiting': placed['knot'] in rec['waiting']}
                                         for rec in A2.records[s:]]
            kt = K.test_run(A2.snap, law, rounds=[A2.rounds_done]) if kl == 'parity' else None
            if kl == 'nae':
                Sl = A2.snap[A2.rounds_done]
                kt = K.test_run(A2.snap, law, rounds=[A2.rounds_done], only_new_after=s)
                pk = K.nae_direct(Sl, [placed['knot']])
                kt['placed_knot_pass'] = pk[placed['knot']]
            row['knot_tests'] = P._kt_brief(kt)
            if 'placed_knot_pass' in kt:
                row['knot_tests']['placed_knot_pass'] = kt['placed_knot_pass']
            row['listing_with_placed'] = listing(A2, min(A2.rounds_done, s + 3))
            rows.write(row)
            C.log('run6', st, base, kl, row['course_differs_against_Y_barred'],
                  row['course_differs_against_no_placed_knot'])
    rows.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('which', choices=('run4', 'run5', 'run6', 'run4-other'))
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--mem', type=float, default=6)
    args = ap.parse_args()
    C.cap_memory(args.mem + 1)
    {'run4': run4, 'run5': run5, 'run6': run6, 'run4-other': run4_other}[args.which](args)



def run4_other(args):
    """Supplement to run 4 (P14): the fourth mark for every pair on the three-knot start whose course differs in runs
    1 and 3, both knot laws, against the larger-founder start."""
    rows = C.JsonLines('run4_what_the_other_is.jsonl')
    seen = set()
    for fn in ('run1.jsonl.gz', 'run3.jsonl.gz'):
        with gzip.open(C.out_path(fn), 'rt') as f:
            for line in f:
                r = json.loads(line)
                if r.get('start') != 'three-knot' or 'pairs' not in r:
                    continue
                ps = [p for p in r['pairs'] if p['course_differs'] is not None and p['s'] >= 1]
                if not ps:
                    continue
                law = make_law(r['base'], r['law_name'], r['knot_law'], 'three-knot')
                A = pm.Run(pm.start('three-knot'), law)
                view = P.RunView(A)
                for p in ps:
                    key = (r['base'], r['law_name'], r['knot_law'], p['s'], tuple(p['X']))
                    if key in seen:
                        continue
                    seen.add(key)
                    S = A.snap[p['s']]
                    ax = {a for u in p['X'] for a in P.anc_or_self(S, u) if S.made[a] == 0}
                    ay = {a for u in p['Y'] for a in P.anc_or_self(S, u) if S.made[a] == 0}
                    # D 5.3: the starts differ only in the holdings of the start knot Y descends from (knot 2 here)
                    applicable = (ay == {2} and 2 not in ax)
                    w = what_the_other_is(view, p['s'], p['X'], 'three-knot', law) if applicable else {}
                    rows.write({'base': r['base'], 'law_name': r['law_name'], 'knot_law': r['knot_law'], 's': p['s'],
                                'X': p['X'], 'Y': p['Y'], 'X_start_knots': sorted(ax), 'Y_start_knots': sorted(ay),
                                'applicable': applicable, **w})
    rows.close()


if __name__ == '__main__':
    main()
