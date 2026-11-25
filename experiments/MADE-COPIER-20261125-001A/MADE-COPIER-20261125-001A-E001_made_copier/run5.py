"""Run 5: the swaps (P, "Runs", row 5; deviations 35 to 39).

cases  - every case of run 2 (two of Y made by X in a reading, under a stated rule): the other rules, the other base
         laws, the renamings registered for the design, the order of births reversed, demand before the takes, HOLD,
         STEPS-1 for MET and back, the knot law; whether the case survives each, with its verdicts.
cases3 - every case of run 3: n1 and n4 only (n4 drawn with the pair start's name).
lists  - the registered take lists (run 4's cases): the swaps that name no rule, by D 7.8's translation.
iv     - reading (iv) (D 7.8) on every values case of the designs with Y present from round 0: the stated-rule cases of
         run 2 and the registered take lists of those designs.
form   - every run of the form arm under n1, n3, n4, the order of births reversed, demand before the takes, HOLD.

usage: python -B run5.py cases|cases3|lists|iv|form [--procs 4]
"""
import argparse
import json
import os
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402
import run2  # noqa: E402
import run3  # noqa: E402
import run4  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P
READ_KEYS = (('values', 'Y_by_X_some'), ('form', 'two_by_X_some'), ('built', 'two_by_X_some'))
CONTROLS = ('made-2', 'made-2-exchanged', 'ystart-two-22')


# ------------------------------------------------------------------------------------- the reading in one run A
def read_case(A, d, kl, reading, X=None, Y=None, s=None):
    X = d.X if X is None else X
    Y = d.Y if Y is None else Y
    s = d.s if s is None else s
    if A.rounds_done < s + 1:
        return {'survives': False, 'rounds': A.rounds_done, 'note': 'ended before round s + 1'}
    view = P.RunView(A)
    ref = mc.Reference(A.snap[s], view.roster(s), Y, s, X=X)
    rr = mc.readings_per_round(A, ref, X, Y, s, kl, built=(reading == 'built'), values=(reading == 'values'),
                               form=(reading == 'form'))
    if reading == 'values':
        fl = mc.values_flags(rr)
        hit = fl['Y_by_X_some']
        cases = [c for c in fl['cases'] if c['made_by_X']][:2]
        who = [sorted(c['descents']) for c in cases]
        fl = {k: fl[k] for k in ('Y_by_X_some', 'Y_by_X_last', 'Y_own_some', 'X_place_by_X_some')}
        fl['cases'] = cases
    elif reading == 'form':
        fl = mc.form_flags(rr)
        hit = fl['two_by_X_some']
        who = [['X only', 'X only']] if hit else []
    else:
        fl = mc.built_flags(rr)
        hit = fl['two_by_X_some']
        who = [['X only', 'X only']] if hit else []
    kt = mc.knot_tests_A(A)
    meet = P.one_part_again(view, s, X, Y)
    link = None
    if meet is not None:
        lk = P.linking(view, meet, X, Y, s)
        link = {k: lk[k] for k in ('made_connected', 'start_connected', 'link_classes')}
    return {'survives': hit is not None, 'round': hit, 'flags': fl, 'who made the two': who,
            'rounds': A.rounds_done, 'stop': A.stop, 'knot_fails': kt['n_fails'], 'meeting_round': meet,
            'link': link, 'nae_made_ties': nae_made_ties(A, kl)}


def nae_made_ties(run, kl):
    """Run 6 (P2): under not-all-equal, the tie classes at the last round read containing a distinction made by any
    birth (S1: a tie among distinctions existing after a round is the same after every later round)."""
    if kl != 'nae':
        return None
    nd0 = run.snap[0].n_distinctions
    T = mc.ties(run.snap[run.rounds_done], 'nae')
    cl = [c for c in T.classes if any(x >= nd0 for x in c)]
    return {'n': len(cl), 'classes': cl[:4], 'unsat': T.unsat}


def swaps_of(case):
    """[(label, base, take, rule, knot law, renaming, extra law kwargs)], one change each from the case's law."""
    base, take, rule, kl, name = case['base'], case['take'], case['choice'], case['knot_law'], case['design']
    out = []
    for r in mc.RULES:
        if r != rule:
            out.append(('rule %s' % r, base, take, r, kl, None, {}))
    for b in mc.NINE:
        if b != base:
            out.append(('base law %s' % b, b, take, rule, kl, None, {}))
    for rn in (mc.renamings_for(name) if name in mc.STARTS['renamings'] else []):
        out.append(('renaming %s' % rn, base, take, rule, kl, rn, {}))
    out.append(('order of births reversed', base, take, rule, kl, None, {'order_reversed': True}))
    out.append(('demand before the takes', base, take, rule, kl, None, {'demand_before_takes': True}))
    out.append(('HOLD', base, take, rule, kl, None, {'release': 'HOLD'}))
    out.append(('STEPS-1 for MET' if take == 'MET' else 'MET for STEPS-1', base,
                'STEPS-1' if take == 'MET' else 'MET', rule, kl, None, {}))
    out.append(('knot law', base, take, rule, 'nae' if kl == 'parity' else 'parity', None, {}))
    return out


def do_case(case):
    C.cap_memory(6)
    t0 = time.time()
    out = {'case': case, 'swaps': {}}
    try:
        law0 = mc.make_law(case['base'], case['take'], case['choice'], case['knot_law'])
        d0 = mc.design(case['design'])
        out['as run'] = read_case(mc.grow(d0, law0), d0, case['knot_law'], case['reading'])
        for label, b, tk, r, kl, rn, extra in swaps_of(case):
            law = mc.make_law(b, tk, r, kl, **extra)
            d = mc.design(case['design'], renaming=rn)
            row = read_case(mc.grow(d, law), d, kl, case['reading'])
            row['law'] = law.name()
            out['swaps'][label] = row
        regs = [k for k in out['swaps'] if k.startswith('renaming')]
        out['survives every registered renaming'] = bool(regs) and all(out['swaps'][k]['survives'] for k in regs)
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


def cases_run2():
    cases = []
    for r in C.read_jsonl('run2.jsonl.gz'):
        j = r['job']
        for name, d in r.get('designs', {}).items():
            for reading, key in READ_KEYS:
                if d.get(reading, {}).get(key):
                    cases.append({'run': 2, 'design': name, 'base': j['base'], 'take': j['take'],
                                  'choice': j['choice'], 'knot_law': j['knot_law'], 'reading': reading,
                                  'round': d[reading][key], 'control': name in CONTROLS,
                                  'knot_fails_A': d['knot_tests_A']['n_fails']})
    return cases


# ------------------------------------------------------------------------------------------------- run 3's cases
def cases_run3():
    cases = []
    for r in C.read_jsonl('run3.jsonl.gz'):
        for p_ in r.get('pairs', []):
            for reading, key in READ_KEYS:
                if p_.get(reading, {}).get(key):
                    cases.append({'run': 3, 'start': r['job']['start'], 's': p_['s'], 'X': p_['X'], 'Y': p_['Y'],
                                  'base': r['job']['base'], 'take': r['job']['take'], 'choice': r['job']['choice'],
                                  'knot_law': r['job']['knot_law'], 'reading': reading, 'round': p_[reading][key]})
    return cases


def do_case3(case):
    """Deviation 36: in the renamed run, the pairs of D 4.8 at the same s whose Y is the same as the case's Y."""
    import run1
    C.cap_memory(6)
    t0 = time.time()
    out = {'case': case, 'swaps': {}}
    try:
        kl = case['knot_law']
        law = mc.make_law(case['base'], case['take'], case['choice'], kl)
        st = run3.pair_starts()[case['start']]
        A0 = mc.grow(pm.from_stars(st), law, rounds=7)
        v0 = P.RunView(A0)
        refY = mc.Reference(A0.snap[case['s']], v0.roster(case['s']), case['Y'], case['s'], X=case['X'])
        for rn in ('n1', 'n4'):
            stars = run3.renamed_stars(st, case['start'], rn)
            A = mc.grow(pm.from_stars(stars, reverse_names=(rn == 'n1')), law, rounds=7)
            view = P.RunView(A)
            pairs = [p_ for p_ in run3.find_pairs(A, view, run1.two_knot_ref()) if p_['s'] == case['s']]
            R = view.roster(case['s']) if A.rounds_done >= case['s'] else None
            rows = []
            for p_ in pairs:
                if R is None or not mc.same_as(refY, R, frozenset(p_['Y'])):
                    continue
                d = mc.Design('pair', stars, p_['X'], p_['Y'], p_['s'])
                rows.append(dict(read_case(A, d, kl, case['reading']), X=p_['X'], Y=p_['Y']))
            out['swaps']['renaming %s' % rn] = {'pairs with the same Y': len(rows),
                                                'survives': any(x['survives'] for x in rows), 'rows': rows[:4]}
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


# ----------------------------------------------------------------------------- D 7.8's translation of a take list
class TRun:
    """A run grown round by round under a chooser: the attributes the readings and knot tests use."""

    def __init__(self, snaps, recs, law, rounds_asked, stop=None, guard=None):
        self.snap, self.records, self.law = snaps, recs, law
        self.rounds_done = len(recs)
        self.rounds_asked, self.knot_bound = rounds_asked, mc.KNOT_BOUND
        self.stop, self.guard, self.S, self.ctx = stop, guard, snaps[-1], {}


def list_run(d, law, take_list):
    """The take list's own run (as the replay of P8a): rounds 1 to s by the law, then the listed takes."""
    S0 = d.start()
    pre = mc.grow(S0, law, rounds=d.s) if d.s > 0 else None
    snaps = pre.snap[:] if pre else [S0]
    recs = pre.records[:] if pre else []
    S = snaps[-1]
    for listed in take_list:
        T, rec, bad, rest = run4.listed_child(S, law, listed)
        assert not bad and not rest, (bad, rest)
        snaps.append(T)
        recs.append(rec)
        S = T
    return TRun(snaps, recs, law, len(recs))


def _off_numbers(births):
    n, out = Counter(), {}
    for b in births:
        if b['kind'] == 'offshoot':
            out[b['id']] = n[b['parents'][0]]
            n[b['parents'][0]] += 1
    return out


def translate(orig, S0, law, distmap0, Z=(), rounds=None):
    """D 7.8: grow S0 under law; a birth with a parent among Z and its descendants takes by OLDEST; every other birth
    takes what the list's run (orig) took at the birth that answers it, translated.  Start knots answer by order,
    start distinctions through distmap0 (orig name -> new name), fresh distinctions of answering births in order.
    Returns (run, the round from which the list does not apply or None, why)."""
    rounds = rounds or orig.rounds_done
    knotmap = {i: i for i in range(orig.snap[0].n_knots)}         # orig knot -> new knot
    distmap = dict(distmap0)
    S = S0.copy()
    snaps, recs = [S.copy()], []
    zset = set(Z)
    stop, guard = None, None
    for t in range(1, rounds + 1):
        zd = (P.side_of(S, list(Z), 0) | zset) if Z else set()
        try:
            dry = S.copy()
            births = pm.round_step(dry, law, {'chooser': lambda key, c: c[0]})['births']
        except pm.GuardStop as g:
            stop, guard = 'guard', {'round': t, 'what': g.what}
            break
        orec = orig.records[t - 1]
        inv = {v: k for k, v in knotmap.items()}
        on_new, on_old = _off_numbers(births), _off_numbers(orec['births'])
        plan, answer = {}, {}
        why = None
        base = S.n_knots
        for b in births:
            bi = b['id'] - base
            if any(p in zd for p in b['parents']):
                plan[bi] = 'OLDEST'
                continue
            ps = [inv.get(p) for p in b['parents']]
            match = None
            if all(p is not None for p in ps):
                for ob in orec['births']:
                    if ob['kind'] != b['kind'] or sorted(ob['parents']) != sorted(ps):
                        continue
                    if b['kind'] == 'offshoot' and on_old[ob['id']] != on_new[b['id']]:
                        continue
                    match = ob
                    break
            if match is None:
                why = 'birth %d (%s of %s) has no birth answering it' % (b['id'], b['kind'], b['parents'])
                break
            answer[b['id']] = match
            plan[bi] = [distmap.get(x) for x in match['rule_takes']]
        if why:
            return TRun(snaps, recs, law, rounds, stop, guard), t, why
        failed = []

        def chooser(key, cands, plan=plan, failed=failed):
            pl = plan.get(key[1])
            if pl == 'OLDEST':
                return cands[0]
            if not pl:
                failed.append((key, 'a take with nothing listed', list(cands)))
                return cands[0]
            d = pl.pop(0)
            if d is None or d not in cands:
                failed.append((key, d, list(cands)))
                return cands[0]
            return d
        T = S.copy()
        try:
            rec = pm.round_step(T, law, {'chooser': chooser})
        except pm.GuardStop as g:
            stop, guard = 'guard', {'round': t, 'what': g.what}
            break
        left = [(bi, pl) for bi, pl in plan.items() if pl != 'OLDEST' and pl]
        if failed or left:
            why = 'a translated take is not a candidate' if failed else 'a listed take has no take to answer'
            return TRun(snaps, recs, law, rounds, stop, guard), t, why + ' %s' % ((failed or left)[:2],)
        for b in rec['births']:
            ob = answer.get(b['id'])
            if ob is not None:
                knotmap[ob['id']] = b['id']
                for a_, z_ in zip(ob['fresh'], b['fresh']):
                    distmap[a_] = z_
        snaps.append(T)
        recs.append(rec)
        S = T
        if rec['residual_stall']:
            stop = 'residual_stall'
            break
        if S.n_knots - len(S.removed) > mc.KNOT_BOUND:
            stop = 'knots'
            break
    return TRun(snaps, recs, law, rounds, stop, guard), None, None


def label_distmap(S_orig, S_new, label_map=None):
    """Start distinctions answer by label (through a renaming's label map)."""
    out = {}
    for name, lab in enumerate(S_orig.labels):
        lab2 = label_map[str(lab)] if label_map else lab
        if lab2 in S_new.labels:
            out[name] = S_new.labels.index(lab2)
    return out


def list_law(L):
    kl = L['law'].split('/')[-1]
    ration, treat = L['law'].split('/')[:2]
    base = {'FLOOR1': 'COPY-LAW', 'CAP-3': 'CAP-3'}[ration] + '(%s)' % treat[7:]
    return base, kl


# ------------------------------------------------------------------------------------- the take lists' swaps
def list_swaps(L):
    base, kl = list_law(L)
    out = []
    for b in mc.NINE:
        if b != base:
            out.append(('base law %s' % b, b, kl, None, {}))
    for rn in mc.renamings_for(L['design']):
        out.append(('renaming %s' % rn, base, kl, rn, {}))
    out.append(('order of births reversed', base, kl, None, {'order_reversed': True}))
    out.append(('demand before the takes', base, kl, None, {'demand_before_takes': True}))
    out.append(('HOLD', base, kl, None, {'release': 'HOLD'}))
    out.append(('knot law', base, 'nae' if kl == 'parity' else 'parity', None, {}))
    return out


def do_list(L):
    C.cap_memory(6)
    t0 = time.time()
    out = {'index': L['index'], 'design': L['design'], 'law': L['law'], 'round seen': L['round'], 'swaps': {}}
    try:
        base, kl = list_law(L)
        d0 = mc.design(L['design'])
        orig = list_run(d0, run4.law_every(base, kl), L['take_list'])
        S_orig0 = orig.snap[0]
        # the identity translation, as a check of the translation itself
        A, ap, why = translate(orig, S_orig0, orig.law, label_distmap(S_orig0, S_orig0))
        out['identity'] = {'applies': ap is None, 'why': why,
                           'same structures': ap is None and len(A.snap) == len(orig.snap) and all(
                               a.places == b.places for a, b in zip(A.snap, orig.snap))}
        for label, b, kl2, rn, extra in list_swaps(L):
            law = mc.make_law(b, 'MET', 'OLDEST', kl2, **extra)
            d = mc.design(L['design'], renaming=rn)
            S0 = d.start()
            lm = mc.STARTS['renamings'][L['design']][rn] if rn not in (None, 'n1') else None
            A, ap, why = translate(orig, S0, law, label_distmap(S_orig0, S0, lm))
            row = {'law': law.name(), 'the list does not apply from round': ap, 'why': why,
                   'rounds': A.rounds_done, 'stop': A.stop}
            if A.rounds_done >= d.s + 1:
                r = read_case(A, d, kl2, 'values')
                row.update({k: r[k] for k in ('survives', 'round', 'who made the two', 'knot_fails')})
            else:
                row['survives'] = False
            out['swaps'][label] = row
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


# ------------------------------------------------------------------------------------------------ reading (iv)
def read_iv(d, A, Bz, kl, applies=None):
    """D 7.8 (a) to (d).  applies: whether each run takes as its take list says through the list's last round (always,
    under a stated rule).  Each run that applies is read; (a) to (d) are read when both apply, at T."""
    applies = applies or {'with Z': True, 'Z barred': True}
    both = applies['with Z'] and applies['Z barred']
    T = min(A.rounds_done, Bz.rounds_done) if both else None
    out = {'T': T}
    # the places of Y and of Z are read in the start with Z (with Z barred its members are no members)
    vA = P.RunView(A)
    refY = mc.Reference(A.snap[0], vA.roster(0), d.Y, 0, X=d.X)
    refZ = mc.Reference(A.snap[0], vA.roster(0), d.Z, 0, X=d.X)
    for nm, run in (('with Z', A), ('Z barred', Bz)):
        if not applies[nm]:
            continue
        Tn = T if both else run.rounds_done
        ry = mc.readings_per_round(run, refY, d.X, d.Y, 0, kl, built=False, form=False)
        rz = mc.readings_per_round(run, refZ, d.X, d.Z, 0, kl, built=False, form=False)
        fy = [r['t'] for r in ry['rows'] if r['t'] <= Tn and any(c['made_by_X'] for c in r['values_Y'])]
        fz = [r['t'] for r in rz['rows'] if r['t'] <= Tn and any(c['made_by_X'] for c in r['values_Y'])]
        out[nm] = {'two of Y at': fy, 'two of Z at': fz, 'rounds': run.rounds_done, 'read through': Tn,
                   'stop': run.stop, 'knot_fails': mc.knot_tests_A(run)['n_fails'],
                   'nae_made_ties': nae_made_ties(run, kl)}
    if not both:
        return out
    eZ = mc.ending(A, d.Z, 0, T)
    out['Z in the run with Z'] = eZ
    out['(a) with Z, no two of Y'] = not out['with Z']['two of Y at']
    out['(b) with Z barred, two of Y'] = bool(out['Z barred']['two of Y at'])
    out['(c) with Z, no two of Z'] = not out['with Z']['two of Z at']
    out['(d) Z makes a birth in round T'] = eZ.get('state') == 'makes a birth in round T'
    out['(iv) holds'] = all(out[k] for k in ('(a) with Z, no two of Y', '(b) with Z barred, two of Y',
                                             '(c) with Z, no two of Z', '(d) Z makes a birth in round T'))
    return out


def do_iv(job):
    C.cap_memory(6)
    t0 = time.time()
    rows = []
    jj = {k: v for k, v in job.items() if k != 'list'}
    if 'list' in job:
        jj['index'] = job['list']['index']
    try:
        kind_y = job['design'][len('ystart-'):]
        if job['kind'] == 'stated':
            kl = job['knot_law']
            law = mc.make_law(job['base'], job['take'], job['choice'], kl)
        else:
            L = job['list']
            base, kl = list_law(L)
            law = run4.law_every(base, kl)
            orig = list_run(mc.design(L['design']), law, L['take_list'])
        for kz in mc.KINDS:
            if kz == kind_y:
                continue
            for where in ('before', 'after'):
                d = mc.third(kind_y, kz, where)
                S0 = d.start()
                SB = P.bar_part(S0, d.Z)
                r = {'Z': kz, 'where': where}
                if job['kind'] == 'stated':
                    A = mc.grow(S0, law)
                    Bz = mc.grow(SB, law)
                    applies = None
                else:
                    dm = label_distmap(orig.snap[0], S0)
                    A, ap1, w1 = translate(orig, S0, law, dm, Z=d.Z)
                    Bz, ap2, w2 = translate(orig, SB, law, dm, Z=d.Z)
                    r['the list does not apply from round'] = {'with Z': ap1, 'Z barred': ap2}
                    r['why'] = {'with Z': w1, 'Z barred': w2}
                    applies = {'with Z': ap1 is None, 'Z barred': ap2 is None}
                r.update(read_iv(d, A, Bz, kl, applies))
                rows.append(r)
        out = {'job': jj, 'rows': rows}
    except Exception as e:
        out = {'job': jj, 'error': repr(e), 'trace': traceback.format_exc(), 'rows': rows}
    out['seconds'] = round(time.time() - t0, 1)
    return out


# -------------------------------------------------------------------------------------------------- the form arm
FORM_SWAPS = [('n1', 'n1', {}), ('n3', 'n3', {}), ('n4', 'n4', {}),
              ('order of births reversed', None, {'order_reversed': True}),
              ('demand before the takes', None, {'demand_before_takes': True}), ('HOLD', None, {'release': 'HOLD'})]
FORM_DESIGNS = mc.DESIGNS_MADE + mc.DESIGNS_YSTART


def do_form(job):
    C.cap_memory(6)
    t0 = time.time()
    out = {'job': job, 'designs': {}}
    try:
        kl = job['knot_law']
        law = mc.make_law(job['base'], job['take'], job['choice'], kl, **job['extra'])
        out['law'] = law.name()
        runs = {}
        for name in FORM_DESIGNS:
            d = mc.design(name, renaming=job['renaming'])
            runs[name] = (d,) + run2.run_design(d, law, kl)
        refs = {'made': {n: runs[n][3] for n in mc.CLASS_MADE if runs[n][3] is not None},
                'ystart': {n: runs[n][3] for n in mc.CLASS_START if runs[n][3] is not None}}
        for name in FORM_DESIGNS:
            d, A, view, ref = runs[name]
            if ref is None:
                out['designs'][name] = {'note': 'run A ended before round s'}
                continue
            rr = mc.readings_per_round(A, ref, d.X, d.Y, d.s, kl, built=False, values=False)
            row = {'form': mc.form_flags(rr), 'knot_fails': mc.knot_tests_A(A)['n_fails'], 'rounds': A.rounds_done,
                   'rounds not read': [r['t'] for r in rr['rows'] if 'form not read' in r],
                   'stop': A.stop, 'guard': A.guard, 'nae_made_ties': nae_made_ties(A, kl)}
            fam = 'made' if name.startswith('made') else 'ystart'
            cross = {}
            for yn, yref in refs[fam].items():
                per = []
                for t in range(d.s + 1, A.rounds_done + 1):
                    R_t = mc.roster_or_none(view, t)
                    if R_t is None:
                        per.append({'not read': 1})
                        continue
                    desc = mc.descent_map(A.snap[t], d.X, d.Y, d.s)
                    parts = mc.form_reading(yref, A.snap[t], R_t, desc)
                    per.append(dict(Counter(p_['descent'] for p_ in parts)))
                cross[yn] = per
            row['parts_same_as_member'] = cross
            out['designs'][name] = row
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


def form_jobs():
    js = []
    for sw, rn, extra in FORM_SWAPS:
        for base in mc.BASES_CAP3 + mc.BASES_FBP:
            for take in ('MET', 'STEPS-1'):
                for ch in mc.RULES:
                    for kl in ('nae', 'parity'):
                        js.append({'swap': sw, 'renaming': rn, 'extra': extra, 'base': base, 'take': take,
                                   'choice': ch, 'knot_law': kl})
    return js


def pool(fn, js, name, procs, label, mode='w'):
    out = C.JsonLines(name, mode=mode)
    with ProcessPoolExecutor(max_workers=procs) as ex:
        futs = {ex.submit(fn, j): j for j in js}
        for i, f in enumerate(as_completed(futs)):
            try:
                r = f.result()
            except Exception as e:
                r = {'job': futs[f], 'error': repr(e)}
            out.write(r)
            if 'error' in r or (i + 1) % 25 == 0 or i + 1 == len(js):
                C.log(label, i + 1, '/', len(js), r.get('seconds'), r.get('error', ''))
    out.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('cases', 'cases3', 'lists', 'iv', 'form'))
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--only', default=None)
    ap.add_argument('--append', action='store_true', help='rerun the jobs written with an error, and append')
    args = ap.parse_args()
    C.cap_memory(7)
    if args.what == 'cases':
        js, name, fn = cases_run2(), 'run5_cases.jsonl', do_case
    elif args.what == 'cases3':
        js, name, fn = cases_run3(), 'run5_cases3.jsonl', do_case3
    elif args.what == 'lists':
        js, name, fn = json.load(open(os.path.join(mc.DATA, 'take_lists.json')))['lists'], 'run5_lists.jsonl', do_list
    elif args.what == 'iv':
        js = [dict(c, kind='stated') for c in cases_run2()
              if c['reading'] == 'values' and c['design'].startswith('ystart')]
        js += [{'kind': 'take list', 'design': L['design'], 'list': L}
               for L in json.load(open(os.path.join(mc.DATA, 'take_lists.json')))['lists']
               if L['design'].startswith('ystart')]
        name, fn = 'run5_iv.jsonl', do_iv
    else:
        js, name, fn = form_jobs(), 'run5_form.jsonl.gz', do_form
    if args.only:
        js = [j for j in js if all(x in json.dumps(j) for x in args.only.split(','))]
    mode = 'w'
    if args.append:
        done = {json.dumps(r['job'], sort_keys=True) for r in C.read_jsonl(name) if 'error' not in r}
        js = [j for j in js if json.dumps(j, sort_keys=True) not in done]
        mode = 'a'
    C.log('run 5 %s:' % args.what, len(js), 'jobs')
    pool(fn, js, name, args.procs, args.what, mode)


if __name__ == '__main__':
    main()
