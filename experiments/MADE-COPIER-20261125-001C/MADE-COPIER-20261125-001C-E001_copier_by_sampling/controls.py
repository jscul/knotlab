"""R0b, the controls of the rate rule (DC 4.7; PC "Runs", order 2): the machinery control (made-4, made-5, its own
rule); the planted case's three arms (index 13 of cases_c.json, chance 0.5); the negative controls (made-2 under the
six COPY-LAW laws, the fold study's name for (FLOOR1, t, RELEASE), not a law of copying; the two design cells where
form was met; the ten MET form cases of the registered sample).  Counted toward nothing.  Writes controls_R0b.json."""
import argparse
import multiprocessing as mp
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402
from study import log  # noqa: E402

CHUNK = 50


def design_growth(design, spec):
    d = mcc.STARTS_A['designs'][design]
    base = 'C|A|%s|%s|%s|%s|parity|0' % (design, spec.ration, spec.treatment, spec.take)
    g = mcc.Growth(d['stars'], spec, 'A|' + design, 0, base=base)
    return g, tuple(d['X']), tuple(d['Y']), d['s']


def case_growth(idx):
    c = mcc.CASES_C['cases'][idx]
    spec = mcc.Spec(c['ration'], c['treatment'], 'MET', c['knot_law'])
    g = mcc.Growth(mcc.start_by_id(c['start'])['stars'], spec, c['start'], c['sample'])
    return g, tuple(c['X']), tuple(c['Y']), c['s']


def control_growth(ctl):
    if ctl['type'] == 'design':
        return design_growth(ctl['design'], mcc.Spec.from_name(ctl['law']))
    return case_growth(ctl['index'])


def controls_list():
    out = []
    for design in ('made-4', 'made-5'):
        out.append({'name': 'machinery %s' % design, 'type': 'design', 'design': design, 'group': 'machinery',
                    'law': mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'STEPS-1', 'parity').name(),
                    'readings': ['Yown_val']})
    for arm in (1, 2, 3):
        out.append({'name': 'planted arm %d' % arm, 'type': 'case', 'index': 13, 'group': 'planted', 'arm': arm,
                    'readings': ['form']})
    for t in mcc.TREATS:
        for take in mcc.TAKES:
            sp = mcc.Spec('FLOOR1', t, take, 'parity')
            out.append({'name': 'made-2 %s' % sp.name(), 'type': 'design', 'design': 'made-2', 'law': sp.name(),
                        'group': 'negative', 'readings': ['form', 'both', 'vX', 'formany_X']})
    for r in ('RATION-2', 'FBP'):
        sp = mcc.Spec(r, 'CANCEL-OFFSHOOT', 'STEPS-1', 'parity')
        out.append({'name': 'made-4 %s' % sp.name(), 'type': 'design', 'design': 'made-4', 'law': sp.name(),
                    'group': 'negative', 'readings': ['form', 'both', 'vX']})
    for idx in mcc.CASES_C['R0b']['negative_control_sample']['indices']:
        out.append({'name': 'scratch case %d' % idx, 'type': 'case', 'index': idx, 'group': 'negative',
                    'readings': ['form']})
    return out


def plant_of(ctl):
    if ctl.get('group') != 'planted':
        return None
    arm = ctl['arm']
    if arm == 3:
        return None
    pc = mcc.CASES_C['R0b']['planted_case_pair']
    kinds = {'BN'} if arm == 1 else set(mcc.KINDS)
    return (pc['parent of placed members'], pc['meeting_round'], kinds)


def machinery_job(args):
    ci, kind, lo, hi = args
    ctl = controls_list()[ci]
    g, X, Y, s = control_growth(ctl)
    ref = g.ref(s, X, Y)
    n = met = 0
    for i in range(lo, hi):
        Gc, _ = g.continuation(kind, s, X, Y, i)
        r = mcc.read_pairs(Gc.snaps, Gc.records, Gc.R, [ref], need_form=False, need_values=True)[0]
        n += 1
        met += int('Yown_val' in r.first)
    return ci, kind, lo, {'n': n, 'met': met}


def stage_job(args):
    ci, kind, lo, hi = args
    ctl = controls_list()[ci]
    g, X, Y, s = control_growth(ctl)
    cnt = study.stage(g, s, {(X, Y): ctl['readings']}, (kind,), range(lo, hi), plant=plant_of(ctl))
    c = cnt[(X, Y)][kind]
    return ci, kind, lo, {k: (dict(v) if isinstance(v, Counter) else v) for k, v in c.items()}


def merge(parts):
    tot = {}
    for c in parts:
        for k, v in c.items():
            if isinstance(v, dict):
                tot.setdefault(k, Counter()).update(v)
            else:
                tot[k] = tot.get(k, 0) + v
    return tot


def run_stage(pool, cis, kinds, lo, hi, job=stage_job):
    jobs = [(ci, k, a, min(a + CHUNK, hi)) for ci in cis for k in kinds for a in range(lo, hi, CHUNK)]
    acc = defaultdict(list)
    for ci, k, a, c in pool.imap_unordered(job, jobs, chunksize=1):
        acc[(ci, k)].append(c)
    return {key: merge(v) for key, v in acc.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=6)
    a = ap.parse_args()
    C = controls_list()
    out = {'controls': [], 'engine_hashes': mcc.engine_hashes()}
    ctx = mp.get_context('fork')
    # check the planted pair and the cases' pairs after round s
    for ci, ctl in enumerate(C):
        g, X, Y, s = control_growth(ctl)
        R = g.roster(s)
        ok = X in R.parts and Y in R.parts
        ref = g.ref(s, X, Y)
        ctl['pair_present'] = ok
        ctl['xform'] = ref.xform.describe()
        ctl['yform'] = ref.yform.describe()
        ctl['same_form'] = ref.same_form
        ctl['growth_meet'] = mcc.read_pairs(g.G.snaps, g.G.records, g.G.R, [ref])[0].meet
        log(ctl['name'], 'pair present', ok, 'meeting', ctl['growth_meet'])
    with ctx.Pool(a.procs, initializer=study.cap_memory) as pool:
        mach = [ci for ci, c in enumerate(C) if c['group'] == 'machinery']
        rest = [ci for ci, c in enumerate(C) if c['group'] != 'machinery']
        log('machinery at 100')
        m1 = run_stage(pool, mach, ('BN', 'BY'), 0, 100, machinery_job)
        log('machinery at 1,000')
        m2 = run_stage(pool, mach, ('BN', 'BY'), 100, 1100, machinery_job)
        for ci in mach:
            row = dict(C[ci])
            for lab, mm in (('at 100', m1), ('at 1,000', m2)):
                bn, by = mm[(ci, 'BN')], mm[(ci, 'BY')]
                p = mcc.fisher_greater(bn['met'], bn['n'], by['met'], by['n'])
                row[lab] = {'nothing barred': [bn['met'], bn['n']], 'Y barred': [by['met'], by['n']], 'p': p,
                            'pass': p <= 0.01}
            row['pass'] = row['at 100']['pass'] and row['at 1,000']['pass']
            out['controls'].append(row)
            log(row['name'], row['at 100'], row['at 1,000'])
        log('first stage of the planted arms and negative controls')
        s1 = run_stage(pool, rest, ('BN', 'BY', 'BX'), 0, 100)
        rows = {}
        to_confirm = []
        for ci in rest:
            ctl = dict(C[ci])
            cnt = {k: s1[(ci, k)] for k in ('BN', 'BY', 'BX')}
            ctl['readings_at_100'] = {}
            for rd in ctl['readings']:
                rt = study.rates_of(cnt, rd)
                fs = study.first_stage_verdict(rt)
                ctl['readings_at_100'][rd] = {'rates': rt, 'first_stage': fs}
                if fs['passes_at_100'] or ctl['group'] == 'planted':
                    to_confirm.append(ci)
            rows[ci] = ctl
            log(ctl['name'], {rd: (v['rates']['q1'], v['rates']['q0'], v['rates']['qY'],
                                   v['first_stage']['passes_at_100']) for rd, v in ctl['readings_at_100'].items()})
        to_confirm = sorted(set(to_confirm))
        log('confirmations at 1,000:', [C[ci]['name'] for ci in to_confirm])
        s2 = run_stage(pool, to_confirm, mcc.KINDS, 100, 1100) if to_confirm else {}
        for ci in to_confirm:
            ctl = rows[ci]
            cnt = {k: s2[(ci, k)] for k in mcc.KINDS}
            ctl['readings_at_1000'] = {}
            for rd in ctl['readings']:
                rt = study.rates_of(cnt, rd)
                ctl['readings_at_1000'][rd] = {'rates': rt, 'confirmation': study.confirm_verdict(rt, 0.01)}
            log(ctl['name'], {rd: (v['rates']['q1'], v['rates']['q0'], v['rates']['qY'], v['rates']['qM'],
                                   v['rates']['qT'], v['confirmation']['confirmed'])
                              for rd, v in ctl['readings_at_1000'].items()})
        for ci in rest:
            ctl = rows[ci]
            if ctl['group'] == 'planted':
                passed = ctl['readings_at_100']['form']['first_stage']['passes_at_100']
                conf = ctl['readings_at_1000']['form']['confirmation']['confirmed']
                ctl['pass'] = (passed and conf) if ctl['arm'] == 1 else (not passed)
                ctl['must'] = 'pass at 100 and be confirmed' if ctl['arm'] == 1 else 'not pass at 100'
            else:
                confs = [v['confirmation']['confirmed'] for v in ctl.get('readings_at_1000', {}).values()]
                ctl['pass'] = not any(confs)
                ctl['must'] = 'not be confirmed'
            out['controls'].append(ctl)
    out['pass'] = all(c['pass'] for c in out['controls'])
    study.write_json('controls_R0b.json', out)
    log('R0b', 'PASS' if out['pass'] else 'A CONTROL FAILED', [(c['name'], c['pass']) for c in out['controls']])


if __name__ == '__main__':
    main()
