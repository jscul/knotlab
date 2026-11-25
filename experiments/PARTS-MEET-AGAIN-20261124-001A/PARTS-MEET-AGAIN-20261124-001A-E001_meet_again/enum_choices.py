"""Run 2: Q and SHORT-TAKES with ALL-CHOICES through round 4 (every choice of every take enumerated; at most 100,000
histories, otherwise 100,000 drawn by seed 2026112401), on the two small starts and Ring(5, 3), under COPY-LAW(t) and
RING-LAW, from round 1 and from the late start, both knot laws; swaps FLOOR0, ONE-FEWER (COPY-LAW), FILLERS (RING-LAW)
and fresh by parents (all).  Readings: one part again; come apart; the knot tests at every round of every history.

usage: python -B enum_choices.py [--procs 8] [--only substring]
"""
import argparse
import random
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

import common as C
import knots as K
import paired as P
import pm

MAX_HIST = 100000
ROUNDS = 4
SEED = 2026112401


class Odometer:
    """Enumerates every combination of the decisions of one round (decisions found as the round is formed)."""

    def __init__(self):
        self.idx = []
        self.n = []
        self.pos = 0

    def chooser(self, key, cands):
        i = self.pos
        self.pos += 1
        if i < len(self.idx):
            self.n[i] = len(cands)
            return cands[self.idx[i]]
        self.idx.append(0)
        self.n.append(len(cands))
        return cands[0]

    def next(self):
        self.pos = 0
        j = len(self.idx) - 1
        while j >= 0 and self.idx[j] + 1 >= self.n[j]:
            j -= 1
        if j < 0:
            return False
        self.idx[j] += 1
        del self.idx[j + 1:]
        del self.n[j + 1:]
        return True


def round_children(S, law):
    """Every child of S under every choice of its round, one at a time: (structure, record).  GuardStop propagates."""
    od = Odometer()
    while True:
        T = S.copy()
        rec = pm.round_step(T, law, {'chooser': od.chooser})
        yield T, rec
        if not od.next():
            break


def count_histories(S0, law, budget):
    """The number of histories through round 4 (leaves), or None when it passes the budget."""
    n = [0]

    def dfs(S, t, last):
        if t == ROUNDS or (last is not None and last['residual_stall']) or S.n_knots > pm.KNOT_BOUND:
            n[0] += 1
            if n[0] > budget:
                raise OverflowError
            return
        try:
            for T, rec in round_children(S, law):
                dfs(T, t + 1, rec)
        except pm.GuardStop:
            n[0] += 1
            if n[0] > budget:
                raise OverflowError
    try:
        dfs(S0, 0, None)
    except OverflowError:
        return None
    return n[0]


def round_random(S, law, rng):
    T = S.copy()
    rec = pm.round_step(T, law, {'chooser': lambda key, c: c[rng.randrange(len(c))]})
    return T, rec


class Path:
    """A history as a run-like object for the readings (snap, records, law, rounds_done)."""

    def __init__(self, law, snaps, recs):
        self.law = law
        self.snap = snaps
        self.records = recs
        self.rounds_done = len(recs)
        self.rounds_asked = ROUNDS
        self.knot_bound = pm.KNOT_BOUND


class Stats:
    def __init__(self):
        self.d = {'histories': 0, 'pairs_wholly_apart': 0, 'pairs_came_apart': 0, 'one_part_again': 0,
                  'one_part_again_came_apart': 0, 'joint_births': 0, 'came_apart_events': 0, 'histories_with_apart': 0,
                  'knot_verdicts': 0, 'knot_fails': 0, 'method_disagreements': 0, 'untested': 0, 'guard_stops': 0,
                  'knot_stops': 0, 'residual_stalls': 0, 'max_holders': 0, 'nodes': 0}
        self.examples = []


def node_knot_tests(law, snaps, t, st, prev=None, check_decomposed=False):
    """The knot tests at round t of a history (deviations 32 and 40).  Returns the verdicts at round t when the law can
    give a birth no fresh distinction (FLOOR0, ONE-FEWER under not-all-equal), so that the next round can carry them."""
    S = snaps[t]
    if law.knot_law == 'parity':
        pt = K.parity_test(S)
        st.d['knot_verdicts'] += pt['n']
        st.d['knot_fails'] += len(pt['fail'])
        st.d['method_disagreements'] += len(pt['disagree'])
        if pt['fail'] and len(st.examples) < 20:
            st.examples.append({'kind': 'parity fail', 'round': t, 'knots': pt['fail'][:5],
                                'places': [len(S.places[u]) for u in pt['fail'][:5]],
                                'made': [S.made[u] for u in pt['fail'][:5]]})
        return None
    if law.every_birth_fresh():
        new = [u for u in S.knots() if S.made[u] == t]
        if not new:
            return None
        small = [u for u in new if len(S.places[u]) <= K.DIRECT_LIMIT]
        d = K.nae_direct(S, small)
        for u in new:
            b = K.nae_direct(S, [u])[u] if t == 0 else K.birth_method(snaps[t - 1], S, u)
            if b is None:
                st.d['untested'] += 1
                continue
            st.d['knot_verdicts'] += 1
            v = d.get(u, b)
            if u in d and d[u] != b:
                st.d['method_disagreements'] += 1
            if not v:
                st.d['knot_fails'] += 1
                if len(st.examples) < 20:
                    st.examples.append({'kind': 'nae fail', 'round': t, 'knot': u, 'places': len(S.places[u])})
        return None
    # FLOOR0 / ONE-FEWER under not-all-equal
    ks = S.knots()
    all_fresh = False
    if t > 0:
        nd0 = snaps[t - 1].n_distinctions
        newk = [u for u in ks if S.made[u] == t]
        all_fresh = all(any(d >= nd0 for d in S.places[u]) for u in newk)
    verd = {}
    if t > 0 and all_fresh and prev is not None:
        newk = [u for u in ks if S.made[u] == t]
        for u in ks:
            if S.made[u] < t:
                verd[u] = prev.get(u)
        small = [u for u in newk if len(S.places[u]) <= K.DIRECT_LIMIT]
        d = K.nae_direct(S, small)
        for u in newk:
            verd[u] = d[u] if u in d else K.birth_method(snaps[t - 1], S, u)
        st.d['rounds_carried'] = st.d.get('rounds_carried', 0) + 1
    else:
        small = [u for u in ks if len(S.places[u]) <= K.DIRECT_LIMIT]
        d = K.nae_direct(S, small)
        for u in ks:
            verd[u] = d[u] if u in d else K.nae_decomposed(S, u)
            if u not in d:
                st.d['decomposed_tests'] = st.d.get('decomposed_tests', 0) + 1
        if check_decomposed:
            for u in small:
                st.d['decomposed_vs_direct'] = st.d.get('decomposed_vs_direct', 0) + 1
                if K.nae_decomposed(S, u) != d[u]:
                    st.d['method_disagreements'] += 1
        st.d['rounds_retested'] = st.d.get('rounds_retested', 0) + 1
    for u, v in verd.items():
        if v is None:
            st.d['untested'] += 1
            continue
        st.d['knot_verdicts'] += 1
        if not v:
            st.d['knot_fails'] += 1
            if len(st.examples) < 20:
                st.examples.append({'kind': 'nae fail (FLOOR0/ONE-FEWER)', 'round': t, 'knot': u,
                                    'places': len(S.places[u]), 'made': S.made[u], 'parents': len(S.parents[u])})
    return verd


def read_history(law, snaps, recs, st):
    path = Path(law, snaps, recs)
    view = P.RunView(path)
    st.d['histories'] += 1
    st.d['max_holders'] = max(st.d['max_holders'], max(len(h) for h in snaps[-1].holders))
    ap = P.all_pairs_checks(view)
    if ap['one_part_again']:
        st.d['one_part_again'] += 1
        if len(st.examples) < 40:
            st.examples.append({'kind': 'one part again', 'detail': ap['one_part_again'][:3]})
    if ap['joint_birth']:
        st.d['joint_births'] += 1
    st.d['came_apart_events'] += ap['came_apart']
    any_apart = False
    for s in range(1, min(3, view.R - 1) + 1):
        Rs = view.roster(s)
        cls = pm.roster_classes(Rs)
        parts = Rs.parts
        anc_parts = []
        for P_ in parts:
            A = set()
            for u in P_:
                A |= P.anc_or_self(snaps[s], u)
            tags = set()
            for r in range(0, s):
                Rr = view.roster(r)
                for z in A:
                    j = Rr.part_of.get(z)
                    if j is not None:
                        tags.add((r, j))
            anc_parts.append(tags)
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                if cls[i] != cls[j]:
                    st.d['pairs_wholly_apart'] += 1
                    any_apart = True
                    if anc_parts[i] & anc_parts[j]:
                        st.d['pairs_came_apart'] += 1
    if any_apart:
        st.d['histories_with_apart'] += 1


def _progress(case, st, mode, t0):
    pf = case.get('progress')
    if not pf:
        return
    import json as _json
    with open(C.out_path(pf), 'a') as f:
        f.write(_json.dumps({'id': case['id'], 'mode': mode, 'histories_so_far': st.d['histories'],
                             'stats_so_far': st.d, 'seconds': round(time.time() - t0, 1)}, sort_keys=True) + '\n')


def enumerate_case(case):
    C.cap_memory(case.get('mem', 6))
    t0 = time.time()
    every = case.get('progress_every', 5000)
    law = pm.Law(**case['kw'])
    S0 = pm.start(case['start'])
    st = Stats()
    n = count_histories(S0, law, MAX_HIST)
    t_count = time.time() - t0
    if n is not None:
        mode = 'every choice'

        def dfs(snaps, recs, prev=None):
            st.d['nodes'] += 1
            t = len(recs)
            verd = node_knot_tests(law, snaps, t, st, prev, check_decomposed=(st.d['histories'] < 300))
            S = snaps[-1]
            if t == ROUNDS or (recs and recs[-1]['residual_stall']) or S.n_knots > pm.KNOT_BOUND:
                if recs and recs[-1]['residual_stall']:
                    st.d['residual_stalls'] += 1
                if S.n_knots > pm.KNOT_BOUND:
                    st.d['knot_stops'] += 1
                read_history(law, snaps, recs, st)
                if st.d['histories'] % every == 0:
                    _progress(case, st, 'every choice', t0)
                return
            try:
                for T, rec in round_children(S, law):
                    dfs(snaps + [T], recs + [rec], verd)
            except pm.GuardStop:
                st.d['guard_stops'] += 1
                read_history(law, snaps, recs, st)
        dfs([S0], [])
        assert st.d['histories'] == n, (st.d['histories'], n)
    else:
        mode = 'drawn'
        rng = random.Random('%d|%s' % (SEED, case['id']))
        seen = set()
        for h in range(MAX_HIST):
            snaps, recs = [S0], []
            S = S0
            for t in range(ROUNDS):
                if recs and recs[-1]['residual_stall']:
                    break
                if S.n_knots > pm.KNOT_BOUND:
                    break
                try:
                    T, rec = round_random(S, law, rng)
                except pm.GuardStop:
                    st.d['guard_stops'] += 1
                    break
                snaps.append(T)
                recs.append(rec)
                S = T
            if recs and recs[-1]['residual_stall']:
                st.d['residual_stalls'] += 1
            seen.add(hash(tuple(tuple(p) for p in snaps[-1].places)))
            verd = None
            for t in range(len(snaps)):
                st.d['nodes'] += 1
                verd = node_knot_tests(law, snaps, t, st, verd, check_decomposed=(h < 300))
            read_history(law, snaps, recs, st)
            if (h + 1) % every == 0:
                _progress(case, st, 'drawn', t0)
        st.d['distinct_final_structures'] = len(seen)
    out = {'id': case['id'], 'start': case['start'], 'law': law.name(), 'mode': mode, 'n_histories_counted': n,
           'stats': st.d, 'examples': st.examples, 'seconds': round(time.time() - t0, 1),
           'count_seconds': round(t_count, 1), 'peak_mb': C.peak_mb(),
           **{k: case[k] for k in ('base', 'rule', 'late', 'swap', 'knot_law')}}
    return out


def cases():
    out = []
    bases = [('COPY-LAW(%s)' % t[7:], dict(ration='FLOOR1', treatment=t)) for t in
             ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')]
    bases.append(('RING-LAW', dict(ration='CAP-3', treatment='CANCEL-WAIT')))
    for bname, bkw in bases:
        swaps = [('base', {})]
        if bname.startswith('COPY'):
            swaps += [('FLOOR0', dict(ration='FLOOR0')), ('ONE-FEWER', dict(ration='ONE-FEWER'))]
        else:
            swaps += [('FILLERS', dict(fillers=True))]
        swaps += [('fresh by parents', dict(fresh_by_parents=True))]
        for st in ('two-knot', 'three-knot', 'Ring(5,3)'):
            s0 = pm.LATE_S0[st]
            for rule in ('Q', 'SHORT-TAKES'):
                for late in (None, s0):
                    for sw, swkw in swaps:
                        for kl in ('nae', 'parity'):
                            kw = dict(bkw)
                            kw.update(swkw)
                            kw['knot_law'] = kl
                            kw['choice'] = 'ALL-CHOICES'
                            if rule == 'Q':
                                kw['take'] = 'Q'
                            else:
                                kw['base_treatment'] = kw['treatment'] if late is not None else None
                                kw['treatment'] = 'SHORT-TAKES'
                            if late is not None:
                                kw['late'] = late
                            cid = '%s|%s|%s|%s|%s|%s' % (bname, st, rule, 'late' if late else 'r1', sw, kl)
                            out.append({'id': cid, 'start': st, 'kw': kw, 'base': bname, 'rule': rule,
                                        'late': late, 'swap': sw, 'knot_law': kl})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=8)
    ap.add_argument('--mem', type=float, default=6)
    ap.add_argument('--only', default=None)
    ap.add_argument('--out', default='run2.jsonl')
    ap.add_argument('--skip-done', default=None, help='comma-separated outputs whose enumerations are kept')
    ap.add_argument('--exclude', default=None, help='leave out the enumerations whose id holds all these substrings')
    ap.add_argument('--heavy-first', action='store_true')
    ap.add_argument('--progress', default=None, help='progress file (one line every --progress-every histories)')
    ap.add_argument('--progress-every', type=int, default=5000)
    args = ap.parse_args()
    cs = cases()
    if args.skip_done:
        import json as _json
        done = set()
        for fn in args.skip_done.split(','):
            p_ = C.out_path(fn)
            with open(p_) as f_:
                for line in f_:
                    if line.strip():
                        r_ = _json.loads(line)
                        if 'stats' in r_:
                            done.add(r_['id'])
        cs = [c for c in cs if c['id'] not in done]
    if args.only:
        cs = [c for c in cs if all(x in c['id'] for x in args.only.split(','))]
    if args.exclude:
        cs = [c for c in cs if not all(x in c['id'] for x in args.exclude.split(','))]
    if args.heavy_first:
        cs.sort(key=lambda c: (0 if 'ONE-FEWER' in c['id'] else 1 if 'Ring(5,3)' in c['id'] else 2))
    for c in cs:
        c['mem'] = args.mem
        c['progress'] = args.progress
        c['progress_every'] = args.progress_every
    C.log('run 2:', len(cs), 'enumerations')
    out = C.JsonLines(args.out)
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        futs = {ex.submit(enumerate_case, c): c for c in cs}
        for f in as_completed(futs):
            c = futs[f]
            try:
                r = f.result()
            except Exception as e:
                r = {'id': c['id'], 'error': repr(e), 'trace': traceback.format_exc()}
            out.write(r)
            C.log(r.get('id'), r.get('mode'), r.get('seconds'), r.get('error', ''),
                  {k: r['stats'][k] for k in ('histories', 'pairs_wholly_apart', 'one_part_again', 'joint_births')}
                  if 'stats' in r else '')
    out.close()


if __name__ == '__main__':
    main()
