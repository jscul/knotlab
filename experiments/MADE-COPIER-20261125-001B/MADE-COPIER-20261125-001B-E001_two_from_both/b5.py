"""Run B5, the checks of the settled statements on the 256 starts, no taking rule: F1 (PB2), the roster statement
(PB3), the marked start roster (PB4), the knot laws until a closing (PB8).  One job per ration, treatment and release.

usage: python -B b5.py [--procs 4]
"""
import argparse
import os
import sys
import time
import traceback
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402
import mcb  # noqa: E402

mc, pm, K, P = mcb.mc, mcb.pm, mcb.K, mcb.P
STARTS = [k for k in mcb.STB['starts'] if 'other' not in k.split(' / ')[1]]


def same_structure(S1, S2):
    return (S1.places == S2.places and S1.barred == S2.barred and S1.holders == S2.holders and
            S1.removed == S2.removed and S1.kind == S2.kind and S1.made == S2.made)


def marked_roster(S, R, X, Y, mforms):
    desc = mc.descent_map(S, X, Y, 0)
    return tuple(sorted(Counter(mforms.classify(R, p, desc) for p in R.parts).items()))


def unmarked_roster(R, forms):
    return tuple(sorted(Counter(forms.classify(R, p) for p in R.parts).items()))


def pb5_check(A, law, c):
    """Settled 4: no made knot holds three loose distinctions; a made knot holding two is an offshoot meeting only its
    parent; no part of the form of one-3, two-23, two-33, pairs-3, pairs-4 has every member made; a part of three-222's
    form with every member made has members that are offshoots of one start knot."""
    for t in range(1, A.rounds_done + 1):
        S = A.snap[t]
        for u in range(S.n_knots):
            if S.made[u] == 0 or u in S.removed:
                continue
            lo = sum(1 for d in S.places[u] if len(S.holders[d]) == 1)
            c['made knots read'] += 1
            if lo >= 3:
                c['made knots holding three or more loose'] += 1
            if lo == 2:
                c['made knots holding two'] += 1
                meets = {w for d in S.places[u] for w in S.holders[d] if w != u}
                if S.kind[u] != 'offshoot' or meets != set(S.parents[u]):
                    c['made knots holding two that are not offshoots meeting only their parent'] += 1
        R = mcb.roster_or_none(S, law)
        if R is None:
            c['rounds not read'] += 1
            continue
        for p in R.parts:
            if not all(S.made[u] > 0 for u in p):
                continue
            cid = FORMS_PB5.classify(R, p)
            for kind in ('one-3', 'two-23', 'two-33', 'pairs-3', 'pairs-4'):
                if cid == KIND_FORMS_PB5[kind]:
                    c['made parts of the form of ' + kind] += 1
            if cid == KIND_FORMS_PB5['three-222']:
                c['made parts of three-222\'s form'] += 1
                if not (len({S.parents[u] for u in p}) == 1 and all(S.made[S.parents[u][0]] == 0 for u in p)):
                    c['made parts of three-222\'s form not offshoots of one start knot'] += 1


FORMS_PB5 = mcb.Forms()
KIND_FORMS_PB5 = {}


def init_pb5(law):
    for kind in mcb.KINDS8:
        SA, mem = mcb.alone_b(kind, 'Y alone')
        RA = pm.roster_of(SA.copy(), law)
        KIND_FORMS_PB5[kind] = FORMS_PB5.classify(RA, next(p for p in RA.parts if set(mem) <= set(p)))


def do_job(job):
    cb.cap_memory(job.get('mem', 7))
    t0 = time.time()
    ration, t, release = job['ration'], job['treatment'], job['release']
    base = '%s(%s)' % (ration, t)
    out = {'job': job}
    try:
        forms, mforms = mcb.Forms(), mcb.Forms(marked=True)
        laws = {kl: mcb.law1(base, kl, release) for kl in ('nae', 'parity')}
        init_pb5(laws['nae'])
        fbp = {kl: mc.make_law('FBP(%s)' % t, None, 'OLDEST', kl) for kl in ('nae', 'parity')} \
            if (ration == 'COPY-LAW' and release == 'RELEASE') else None
        trans = {kl: {} for kl in laws}
        stats = {kl: Counter() for kl in laws}
        conflicts = {kl: [] for kl in laws}
        per_start = {kl: {} for kl in laws}
        round0 = {}
        f1 = Counter()
        f1_bad = []
        kl_cmp = Counter()
        kl_bad = []
        closing_runs = []
        pb5 = Counter()
        for key in STARTS:
            S0, X, Y = mcb.start_b(key)
            runs = {}
            for kl, law in laws.items():
                A = mcb.grow(S0, law, base)
                runs[kl] = A
                seq = []
                prev = None
                for tt in range(0, A.rounds_done + 1):
                    S = A.snap[tt]
                    R = mcb.roster_or_none(S, law)
                    if R is None:
                        seq.append(None)
                        prev = None
                        continue
                    mr = marked_roster(S, R, X, Y, mforms)
                    if tt == 0 and kl == 'nae':
                        round0[key] = {'roster': unmarked_roster(R, forms), 'marked': mr}
                    seq.append(mr)
                    if tt >= 1 and prev is not None:
                        closing = bool(A.records[tt - 1]['closing'])
                        k_ = (prev, closing)
                        stats[kl]['steps'] += 1
                        stats[kl]['steps from a roster with no member'] += (len(prev) == 0)
                        stats[kl]['closing steps'] += closing
                        if k_ in trans[kl]:
                            stats[kl]['repeats'] += 1
                            if trans[kl][k_] != mr:
                                conflicts[kl].append({'start': key, 'round': tt, 'closing': closing})
                        else:
                            trans[kl][k_] = mr
                        if closing:
                            stats[kl]['closing steps leaving a member'] += bool(mcb.members_now(S))
                    prev = mr
                per_start[kl][key] = {'seq': seq, 'rounds': A.rounds_done, 'stop': A.stop}
            # PB5 (Settled 4), under COPY-LAW(t)
            if ration == 'COPY-LAW':
                for kl, A in runs.items():
                    pb5_check(A, laws[kl], pb5)
            # F1: COPY-LAW(t) against FBP(t)
            if fbp:
                for kl, law in fbp.items():
                    B = mcb.grow(S0, law, base)
                    A = runs[kl]
                    eq = A.rounds_done == B.rounds_done and all(
                        same_structure(a, b) for a, b in zip(A.snap, B.snap))
                    f1['pairs'] += 1
                    f1['identical'] += eq
                    if not eq:
                        f1_bad.append(key)
            # the knot laws until a closing
            A, B = runs['parity'], runs['nae']
            c = next((rec['round'] for rec in A.records if rec['closing']), None)
            upto = (c - 1) if c else min(A.rounds_done, B.rounds_done)
            eq = all(same_structure(A.snap[i], B.snap[i]) for i in range(0, upto + 1)) and (
                c is not None or A.rounds_done == B.rounds_done)
            kl_cmp['pairs'] += 1
            kl_cmp['identical up to the first closing'] += eq
            if c:
                closing_runs.append({'start': key, 'round': c})
            if not eq:
                kl_bad.append(key)
        # PB4: starts with the same marked round-0 roster give the same marked rosters at every round
        groups = defaultdict(list)
        for key, r in round0.items():
            groups[r['marked']].append(key)
        pb4 = {}
        for kl in laws:
            bad = 0
            for g, keys in groups.items():
                seqs = {tuple(per_start[kl][k]['seq']) for k in keys}
                if len(seqs) > 1:
                    bad += 1
            pb4[kl] = {'classes': len(groups), 'classes whose starts differ': bad}
        alone0 = {}
        law0 = laws['nae']
        for kind in mcb.KINDS8:
            SA, mem = mcb.alone_b(kind, 'Y alone')
            alone0[kind] = list(unmarked_roster(pm.roster_of(SA.copy(), law0), forms))
        out.update({
            'law': base + '/' + release, 'alone round0': alone0,
            'round0': {k: {'roster': list(v['roster']), 'marked': list(v['marked'])} for k, v in round0.items()},
            'PB3': {kl: dict(stats[kl], distinct=len(trans[kl]), conflicts=conflicts[kl][:10],
                             n_conflicts=len(conflicts[kl])) for kl in laws},
            'PB4 per law': pb4,
            'PB2': dict(f1, differing=f1_bad[:10]) if fbp else None,
            'PB8': dict(kl_cmp, differing=kl_bad[:10], closing_runs=closing_runs),
            'PB5': dict(pb5) if ration == 'COPY-LAW' else None,
            'forms': forms.desc, 'marked_forms': mforms.desc})
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    out['peak_mb'] = cb.peak_mb()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    args = ap.parse_args()
    js = [{'ration': r, 'treatment': t, 'release': rel} for r in ('COPY-LAW', 'CAP-3')
          for t in ('RETIRE', 'OFFSHOOT', 'WAIT') for rel in ('RELEASE', 'HOLD')]
    cb.log('run B5:', len(js), 'jobs')
    out = cb.JsonLines('b5.jsonl.gz')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        for f in as_completed([ex.submit(do_job, j) for j in js]):
            r = f.result()
            out.write(r)
            cb.log(r.get('law'), r.get('seconds'), r.get('peak_mb'), r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
