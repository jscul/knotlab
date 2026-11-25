"""Run 4 (P8a, P8b, P9, PO8) and the replay of the registered take lists.

Every choice (D 2.7): MET with every combination of the candidates of every take of rounds s + 1 to s + 4, counted
depth first; read in full when there are at most 60,000 histories, otherwise 20,000 drawn under the take-by-take
weighting (`random.Random('2026112502|<design>|<law>')`, one `randrange` per take on the candidates sorted by name).

usage: python -B run4.py replay
       python -B run4.py every [--procs 4] [--only substring]
"""
import argparse
import json
import os
import random
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P
MAX_FULL = 60000
N_DRAWN = 20000
DESIGNS4 = mc.DESIGNS_MADE + mc.DESIGNS_YSTART


def law_every(base, kl):
    """The law of a history: MET with every choice (the chooser decides; the law's own rule is never used)."""
    return mc.make_law(base, 'MET', 'OLDEST', kl)


def law_label(law):
    return law.name().replace('MET(OLDEST)', 'MET(every choice)')


class Odometer:
    def __init__(self):
        self.idx, self.n, self.pos = [], [], 0

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


def children(S, law):
    od = Odometer()
    while True:
        T = S.copy()
        picks = []

        def ch(key, cands, od=od, picks=picks):
            d = od.chooser(key, cands)
            picks.append(d)
            return d
        rec = pm.round_step(T, law, {'chooser': ch})
        yield T, rec, picks
        if not od.next():
            break


def random_child(S, law, rnd):
    T = S.copy()
    picks = []

    def ch(key, cands):
        d = cands[rnd.randrange(len(cands))]
        picks.append(d)
        return d
    rec = pm.round_step(T, law, {'chooser': ch})
    return T, rec, picks


def listed_child(S, law, listed):
    T = S.copy()
    it = iter(listed)
    bad = []

    def ch(key, cands):
        d = next(it)
        if d not in cands:
            bad.append((d, list(cands)))
            return cands[0]
        return d
    rec = pm.round_step(T, law, {'chooser': ch})
    rest = list(it)
    return T, rec, bad, rest


# ----------------------------------------------------------------------------- the values reading, birth by birth
class Tracker:
    """Ties of made distinctions to the places of Y and X, decided at birth (S1, S3; deviations 30)."""

    def __init__(self, S_s, X, Y, s, kl, ref):
        self.s, self.X, self.Y, self.kl = s, X, Y, kl
        T_s = mc.ties(S_s, kl)
        self.elig = {'Y': mc.eligible_places(ref, T_s, 'Y'), 'X': mc.eligible_places(ref, T_s, 'X')}
        self.nd_s = S_s.n_distinctions

    def new_ties(self, S_before, rec):
        """{made distinction: [(owner, v)]} for the births of one round (parity: one fresh distinction f is tied to v
        exactly when the inputs' sum plus v is in the span of the rules before the round)."""
        out = {}
        if self.kl != 'parity':
            return out
        for b in rec['births']:
            if b['f'] != 1:
                continue
            f = b['fresh'][0]
            row = 0
            for d in b['inputs']:
                row ^= 1 << d
            for owner in ('Y', 'X'):
                for v in self.elig[owner]:
                    if pm.span_contains(S_before.span, row ^ (1 << v)):
                        out.setdefault(f, []).append((owner, v))
        return out


def read_round(tr, S_t, tied, t):
    """Cases at round t: two usable loose made distinctions tied to one place v (by owner), with descents."""
    by_v = {}
    for f, lst in tied.items():
        if f >= S_t.n_distinctions:
            continue
        if len(S_t.holders[f]) == 1 and not S_t.barred[f]:
            for owner, v in lst:
                by_v.setdefault((owner, v), []).append(f)
    cases = []
    desc = None
    for (owner, v), fs in by_v.items():
        if len(fs) >= 2:
            if desc is None:
                desc = mc.descent_map(S_t, tr.X, tr.Y, tr.s)
            ds = [desc.get(S_t.holders[f][0]) for f in fs]
            cases.append({'owner': owner, 'v': v, 'two': sorted(fs), 'descents': ds, 'made_by_X': mc.made_by_x(ds),
                          'by_Y_only': all(x == 'Y only' for x in ds), 't': t,
                          'holders_v': len(S_t.holders[v])})
    return cases


def nae_cases(tr, path_snaps, t_from):
    """Not-all-equal (made-2): ties read with the solver at the last round of the history (S1: a tie among existing
    distinctions after round t is the same after every later round), then the cases at each round."""
    S_last = path_snaps[-1]
    T = mc.ties(S_last, 'nae')
    tied = {}
    for c in T.classes:
        for owner in ('Y', 'X'):
            for v in tr.elig[owner]:
                if v in c:
                    for f in c:
                        if f >= tr.nd_s:
                            tied.setdefault(f, []).append((owner, v))
    cases = []
    for i, S_t in enumerate(path_snaps):
        t = t_from + i
        if t <= tr.s:
            continue
        cases += read_round(tr, S_t, tied, t)
    return cases, len(T.classes)


def history_knots_pass(snaps, law):
    kt = K.test_run(snaps, law)
    return not kt['fails'] and not kt['disagree'], mc.brief(kt)


def state_pair(snaps, recs, X, Y, s, T):
    """(X's state, Y's state) at round T (deviations 13), from a history's structures and records."""
    class R_:
        pass
    r = R_()
    r.snap, r.records, r.rounds_done = snaps, recs, len(recs)
    return mc.ending(r, X, s, T).get('state'), mc.ending(r, Y, s, T).get('state')


# ----------------------------------------------------------------------------------------------- one enumeration
def enumerate_case(job):
    C.cap_memory(job.get('mem', 6))
    t0 = time.time()
    name, base, kl = job['design'], job['base'], job['knot_law']
    d = mc.design(name)
    law = law_every(base, kl)
    label = law_label(law)
    S0 = d.start()
    s = d.s
    end = s + 4
    # rounds 1..s grown with no take asked (deviations 31: the chooser is used and must not be called)
    pre = mc.grow(S0, law, rounds=s) if s > 0 else None
    S_s = pre.snap[s] if pre else S0
    pre_snaps = pre.snap[:] if pre else [S0]
    pre_recs = pre.records[:] if pre else []
    view = P.RunView(pre) if pre else None
    R_s = pm.roster_of(S_s.copy(), law)
    ref = mc.Reference(S_s, R_s, d.Y, s, X=d.X)
    tr = Tracker(S_s, d.X, d.Y, s, kl, ref)
    st = Counter()
    found = []           # histories with two (any owner), first ones in full
    first_three = []
    states = Counter()
    check = Counter()

    def finish_history(snaps, recs, picks_by_round, guard_stop, tied_path):
        st['histories'] += 1
        if guard_stop:
            st['stopped by the guard'] += 1
        if kl == 'parity':
            cases = []
            for i in range(s + 1, len(snaps)):
                cases += read_round(tr, snaps[i], tied_path, i)
        else:
            cases, nclass = nae_cases(tr, snaps[s:], s)
            if nclass:
                st['histories with a tie class (not-all-equal)'] += 1
        kinds = set()
        for c in cases:
            key = '%s place, %s' % (c['owner'], 'made by X' if c['made_by_X'] else
                                    ('by Y only' if c['by_Y_only'] else 'by neither'))
            kinds.add(key)
        for k_ in kinds:
            st['histories with two: ' + k_] += 1
        if any(c['owner'] == 'Y' and c['made_by_X'] for c in cases):
            ok, kt = history_knots_pass(snaps, law)
            st['histories with two of a place of Y made by X'] += 1
            st['  of them, every knot passing'] += ok
            if ok and len(first_three) < 3:
                c0 = next(c for c in cases if c['owner'] == 'Y' and c['made_by_X'])
                first_three.append({'history': st['histories'], 'take_list': picks_by_round, 'case': c0,
                                    'holders of v after round s': len(S_s.holders[c0['v']]), 'knot_tests': kt})
            if len(found) < 20:
                found.append({'history': st['histories'], 'cases': cases[:4], 'every knot passes': ok})
        if name == 'made-2':
            states[str(state_pair(snaps, recs, d.X, d.Y, s, min(end, len(recs))))] += 1
        # check the birth rule against the full basis on a sample (deviations 30)
        if kl == 'parity' and (st['histories'] % 97 == 1 or any(c['made_by_X'] for c in cases)):
            check['histories checked against the full basis'] += 1
            S_last = snaps[-1]
            T = mc.ties_parity(S_last)
            for owner in ('Y', 'X'):
                for v in tr.elig[owner]:
                    full = {f for f in T.members(v) if f >= tr.nd_s}
                    mine = {f for f, lst in tied_path.items() if (owner, v) in lst and f < S_last.n_distinctions}
                    if full != mine:
                        check['disagreements'] += 1

    def history_rounds(S, snaps, recs, picks, tied, rnd_mode, rnd=None, depth_cb=None):
        pass

    n = count_histories(S_s, law, s, end, MAX_FULL)
    mode = 'every history' if n is not None else 'drawn'
    if mode == 'every history':
        def dfs(S, t, snaps, recs, picks, tied):
            if t == end or (recs and recs[-1]['stopped']) or S.n_knots > mc.KNOT_BOUND:
                finish_history(snaps, recs, picks, False, tied)
                return
            try:
                for T, rec, pk in children(S, law):
                    nt = dict(tied)
                    nt.update(tr.new_ties(S, rec))
                    dfs(T, t + 1, snaps + [T], recs + [rec], picks + [pk], nt)
            except pm.GuardStop:
                finish_history(snaps, recs, picks, True, tied)
        dfs(S_s, s, pre_snaps, pre_recs, [], {})
    else:
        rnd = random.Random('2026112502|%s|%s' % (name, label))
        for h in range(N_DRAWN):
            S = S_s
            snaps, recs, picks, tied = list(pre_snaps), list(pre_recs), [], {}
            guard = False
            for t in range(s, end):
                if (recs and recs[-1]['stopped']) or S.n_knots > mc.KNOT_BOUND:
                    break
                try:
                    T, rec, pk = random_child(S, law, rnd)
                except pm.GuardStop:
                    guard = True
                    break
                tied.update(tr.new_ties(S, rec))
                snaps.append(T)
                recs.append(rec)
                picks.append(pk)
                S = T
            finish_history(snaps, recs, picks, guard, tied)
    return {'design': name, 'base': base, 'knot_law': kl, 'law': label, 'mode': mode, 'n_counted': n,
            'counts': dict(st), 'first_three': first_three, 'found': found[:10], 'states_made2': dict(states),
            'basis_check': dict(check), 'eligible': tr.elig, 'seconds': round(time.time() - t0, 1),
            'peak_mb': C.peak_mb()}


def count_histories(S_s, law, s, end, budget):
    # deviations 49: a lower bound first.  Every structure reached after round end - 1 that has not stopped leads to at
    # least one history (a child, or a round stopped by the guard, counted once below), and every history that stops
    # earlier is counted as below; so when this count passes the budget, so does the full one, and the enumeration is
    # drawn, as D 2.7 says.  Otherwise the histories are counted to the end as before.
    for cut in (end - 2, end - 1):
        if cut <= s:
            continue
        lb = [0]

        def dfs_lb(S, t, last, cut=cut, lb=lb):
            if t == end or (last is not None and last['stopped']) or S.n_knots > mc.KNOT_BOUND or t == cut:
                lb[0] += 1
                if lb[0] > budget:
                    raise OverflowError
                return
            try:
                for T, rec, _ in children(S, law):
                    dfs_lb(T, t + 1, rec)
            except pm.GuardStop:
                lb[0] += 1
                if lb[0] > budget:
                    raise OverflowError
        try:
            dfs_lb(S_s, s, None)
        except OverflowError:
            return None
    n = [0]

    def dfs(S, t, last):
        if t == end or (last is not None and last['stopped']) or S.n_knots > mc.KNOT_BOUND:
            n[0] += 1
            if n[0] > budget:
                raise OverflowError
            return
        try:
            for T, rec, _ in children(S, law):
                dfs(T, t + 1, rec)
        except pm.GuardStop:
            n[0] += 1
            if n[0] > budget:
                raise OverflowError
    try:
        dfs(S_s, s, None)
    except OverflowError:
        return None
    return n[0]


# ------------------------------------------------------------------------------------------- the take lists (P8a)
def replay_all():
    tl = json.load(open(os.path.join(mc.DATA, 'take_lists.json')))
    rows = []
    for L in tl['lists']:
        d = mc.design(L['design'])
        kl = L['law'].split('/')[-1]
        tparts = L['law'].split('/')
        ration, treat = tparts[0], tparts[1]
        base = {'FLOOR1': 'COPY-LAW', 'CAP-3': 'CAP-3'}[ration] + '(%s)' % treat[7:]
        law = law_every(base, kl)
        assert law_label(law) == L['law'], (law_label(law), L['law'])
        S0 = d.start()
        s = d.s
        pre = mc.grow(S0, law, rounds=s) if s > 0 else None
        snaps = pre.snap[:] if pre else [S0]
        recs = pre.records[:] if pre else []
        S = snaps[-1]
        R_s = pm.roster_of(S.copy(), law)
        ref = mc.Reference(S, R_s, d.Y, s, X=d.X)
        tr = Tracker(S, d.X, d.Y, s, kl, ref)
        tied = {}
        bad = []
        for listed in L['take_list']:
            T, rec, b, rest = listed_child(S, law, listed)
            bad += b
            if rest:
                bad.append(('unused picks', rest))
            tied.update(tr.new_ties(S, rec))
            snaps.append(T)
            recs.append(rec)
            S = T
        t_seen = L['round']
        cases = read_round(tr, snaps[t_seen], tied, t_seen)
        want_v = int(next(iter(L['two'])))
        want = sorted(x[0] for x in L['two'][str(want_v)])
        want_desc = sorted(x[1] for x in L['two'][str(want_v)])
        got = [c for c in cases if c['owner'] == 'Y' and c['v'] == want_v]
        match = bool(got) and want == sorted(got[0]['two'][:2]) if got else False
        if got and len(got[0]['two']) > 2:
            match = set(want) <= set(got[0]['two'])
        earlier = [i for i in range(s + 1, t_seen) if any(c['owner'] == 'Y' and c['made_by_X'] for c in
                                                         read_round(tr, snaps[i], tied, i))]
        ok_kt, kt = history_knots_pass(snaps, law)
        # the full basis at the round seen, as a check of the birth rule
        Tfull = mc.ties_parity(snaps[t_seen])
        full_two = sorted(f for f in Tfull.members(want_v) if f >= tr.nd_s and len(snaps[t_seen].holders[f]) == 1
                          and not snaps[t_seen].barred[f])
        rows.append({'index': L['index'], 'design': L['design'], 'law': L['law'], 'round': t_seen,
                     'listed two': want, 'listed descents': want_desc, 'found': got[:1],
                     'found by the full basis': full_two, 'gives the two': match and not bad,
                     'picks not candidates': bad[:5], 'two seen earlier at': earlier,
                     'holders of v': [len(snaps[s].holders[want_v]), len(snaps[t_seen].holders[want_v])],
                     'listed holders of v': [L['holders of v']['after round s'],
                                             L['holders of v']['after the round seen']],
                     'every knot passes': ok_kt, 'knot_tests': kt})
    ok = all(r['gives the two'] and r['every knot passes'] for r in rows)
    out = {'lists': len(rows), 'P8a': 'holds' if ok else 'fails', 'rows': rows}
    C.write_json('run4_replay.json', out)
    C.log('P8a', out['P8a'], sum(r['gives the two'] for r in rows), 'of', len(rows), 'give the two;',
          sum(r['every knot passes'] for r in rows), 'every knot passing')


def jobs():
    js = []
    for name in DESIGNS4:
        for base in mc.BASES_COPY + mc.BASES_CAP3:
            js.append({'design': name, 'base': base, 'knot_law': 'parity'})
            if name == 'made-2':
                js.append({'design': name, 'base': base, 'knot_law': 'nae'})
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('replay', 'every'))
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--mem', type=float, default=6)
    ap.add_argument('--only', default=None)
    ap.add_argument('--out', default='run4.jsonl')
    ap.add_argument('--append', action='store_true', help='skip the enumerations already in the output and append')
    args = ap.parse_args()
    C.cap_memory(args.mem + 1)
    if args.what == 'replay':
        replay_all()
        return
    js = jobs()
    if args.only:
        js = [j for j in js if all(x in json.dumps(j) for x in args.only.split(','))]
    if args.append:
        done = {(r['design'], r['base'], r['knot_law']) for r in C.read_jsonl(args.out) if 'error' not in r}
        js = [j for j in js if (j['design'], j['base'], j['knot_law']) not in done]
        # the slow enumerations (CAP-3 with offshoots) last, so that the others are written first
        js.sort(key=lambda j: (j['base'] == 'CAP-3(OFFSHOOT)', DESIGNS4.index(j['design'])))
    for j in js:
        j['mem'] = args.mem
    C.log('run 4:', len(js), 'enumerations')
    out = C.JsonLines(args.out, mode='a' if args.append else 'w')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        futs = {ex.submit(enumerate_case, j): j for j in js}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:
                r = {'job': futs[f], 'error': repr(e), 'trace': traceback.format_exc()}
            out.write(r)
            C.log(r.get('design'), r.get('base'), r.get('knot_law'), r.get('mode'), r.get('n_counted'),
                  r.get('seconds'), {k: v for k, v in r.get('counts', {}).items() if 'two' in k or 'guard' in k},
                  r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
