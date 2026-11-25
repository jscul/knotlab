"""Ticket C's analysis of one sampled growth: its pairs and readings, its cases, the first stage (DC 4.4: 100
continuations of nothing barred, Y barred and X barred), the confirmation (1,000 of each of the five kinds), the knot
test and the counts by form.  Used by the gate, the controls and every run."""
from __future__ import annotations

import gzip
import json
import os
import resource
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
from mcc import P, pm  # noqa: E402

T0 = time.time()


# ------------------------------------------------------------------------------------------------------------- io
class TimeLimit(Exception):
    pass


def _alarm(signum, frame):
    raise TimeLimit()


def with_time_limit(seconds, f, *a, **kw):
    """Run f in this (worker) process under a wall-time limit (dev 61): past it, TimeLimit is raised."""
    import signal
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(int(seconds))
    try:
        return f(*a, **kw)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def cap_memory(gb=6):
    lim = int(gb * 1024 ** 3)
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def log(*a):
    mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    print('[%8.1fs %6.0fMB]' % (time.time() - T0, mb), *a, flush=True)


def out_path(name):
    os.makedirs(mcc.OUT, exist_ok=True)
    return os.path.join(mcc.OUT, name)


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


def write_json(name, obj):
    p = out_path(name)
    op = gzip.open if name.endswith('.gz') else open
    with op(p, 'wt') as f:
        json.dump(obj, f, indent=None if name.endswith('.gz') else 1, sort_keys=True, default=_default)
    log('wrote', p, os.path.getsize(p), 'bytes')
    return p


def _feed(d, data):
    """Feed data to the decompressor d; on an error keep every byte of output decodable before it (by halving the
    piece fed, from a copy of d's state).  Returns (output, error)."""
    import zlib
    out = []
    i = 0
    step = len(data)
    while i < len(data):
        piece = data[i:i + step]
        bk = d.copy()
        try:
            out.append(d.decompress(piece))
            i += len(piece)
            if d.eof:
                return b''.join(out), False, i
        except zlib.error:
            d = bk
            if step == 1:
                return b''.join(out), True, i
            step = max(1, step // 2)
            # the next call reuses d's restored state
            continue
    return b''.join(out), False, i


def gunzip_members(raw, chunk=1 << 16):
    """Every gzip member of a file, each read up to where it ends or is cut off (a process stopped while writing
    leaves a member cut mid-block, after which a resumed run appends a new member): the output decodable before a
    cut is kept, and the next member is the first gzip header after the member's start whose first piece decodes
    to a record.  Returns the members' texts."""
    import zlib
    out, pos, n = [], 0, len(raw)
    while pos < n:
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        parts, i, err = [], pos, False
        while i < n and not d.eof:
            c = raw[i:i + chunk]
            bk = d.copy()
            try:
                parts.append(d.decompress(c))
                i += len(c)
            except zlib.error:
                o, err, used = _feed(bk, c)
                parts.append(o)
                break
        out.append(b''.join(parts))
        if d.eof and not err:
            pos = i - len(d.unused_data)
            continue
        if not err:
            break
        nxt = raw.find(b'\x1f\x8b\x08', pos + 1)
        while nxt != -1:
            try:
                t = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(raw[nxt:nxt + 4096])
                if t.startswith(b'{"'):
                    break
            except zlib.error:
                pass
            nxt = raw.find(b'\x1f\x8b\x08', nxt + 1)
        if nxt == -1:
            break
        pos = nxt
    return out


def read_jsonl(name):
    """Every complete line of a result file (a member cut off is read up to its last complete line)."""
    p = out_path(name)
    if not os.path.exists(p):
        return []
    out = []
    if p.endswith('.gz'):
        texts = gunzip_members(open(p, 'rb').read())
        lines = []
        for t in texts:
            lines.extend(t.decode(errors='replace').split('\n'))
    else:
        lines = open(p).read().split('\n')
    for x in lines:
        if x.strip():
            try:
                out.append(json.loads(x))
            except ValueError:
                pass
    return out


class JsonLines:
    def __init__(self, name, mode='w'):
        self.path = out_path(name)
        self.f = (gzip.open if name.endswith('.gz') else open)(self.path, mode + 't')

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True, default=_default) + '\n')

    def flush(self):
        self.f.flush()

    def close(self):
        self.f.close()


# -------------------------------------------------------------------------------------------------- readings sets
FORM_TYPE = ('form', 'both', 'formany_X')
VAL_TYPE = ('vX', 'v1b', 'vbb', 'vA')
CASE_READINGS = mcc.CLAIMED + mcc.REPORTED


def needs(readings):
    return any(r in FORM_TYPE for r in readings), any(r in VAL_TYPE for r in readings)


class ViewAdapter:
    """What paired.linking needs of a run view (snap, roster) over a Grown."""

    def __init__(self, G, law):
        class _R:
            pass
        self.run = _R()
        self.run.snap = G.snaps
        self._law = law
        self._ros = {}

    def roster(self, t):
        if t not in self._ros:
            self._ros[t] = pm.roster_of(self.run.snap[t], self._law)
        return self._ros[t]


def made_questions(g, s, X, Y, m):
    """DC 6: where X, Y and their meeting come from."""
    S = g.G.snaps[s]
    y_made = all(S.made[u] > 0 for u in Y)
    out = {'X made by births': True, 'Y made': y_made}
    if m is not None:
        try:
            link = P.linking(ViewAdapter(g.G, g.law), m, list(X), list(Y), s)
            out['meeting through made knots'] = bool(link['made_connected'])
            out['meeting through start knots'] = bool(link['start_connected'])
            out['link classes'] = sorted(set(link['link_classes'].values()))
        except pm.GuardStop:
            out['meeting'] = 'not read (guard)'
    out['made'] = bool(y_made and out.get('meeting through made knots') and not out.get('meeting through start knots'))
    return out


# --------------------------------------------------------------------------------------------- continuation reading
def read_continuation(g, kind, s, i, pairs_readings, plant=None):
    """One continuation of `kind` from round s, reading every pair of pairs_readings [(X, Y, readings)].  BN is shared
    by every pair of round s (DC 4.1).  plant: (parent knot, r_default, arms set) for the planted case (DC 4.7).
    Returns (stop, last round, knot test brief, [per pair: meet, first, first_after])."""
    X0, Y0, _ = pairs_readings[0]
    if kind[:2] in ('BY', 'BX', 'BM', 'BT'):
        assert len(pairs_readings) == 1
    Gc, seed = g.continuation(kind, s, X0, Y0, i)
    nf = any(needs(r)[0] for _, _, r in pairs_readings) or kind[:2] == 'BX'
    nv = any(needs(r)[1] for _, _, r in pairs_readings)
    refs = [g.ref(s, X, Y) for X, Y, _ in pairs_readings]
    rd = mcc.read_pairs(Gc.snaps, Gc.records, Gc.R, refs, need_form=nf, need_values=nv)
    res = []
    for (X, Y, rs), r in zip(pairs_readings, rd):
        first, after = dict(r.first), dict(r.first_after)
        placed = None
        if plant is not None and kind in plant[2]:
            import random
            if random.Random(seed + '|PLANT').random() < 0.5:
                rr = r.meet if r.meet is not None else plant[1]
                got, c = mcc.placed_form_reading(Gc.snaps, Gc.records, r.ref, rr, plant[0]) if rr <= Gc.R \
                    else (set(), {})
                placed = {'r': rr, 'got': sorted(got)}
                for gg in got:
                    if gg not in first or rr < first[gg]:
                        first[gg] = rr
                    if r.meet is not None and rr >= r.meet and (gg not in after or rr < after[gg]):
                        after[gg] = rr
        res.append({'meet': r.meet, 'first': first, 'after': after, 'placed': placed})
    kt = mcc.knot_test(Gc, only_new_after=s)
    ktb = {'verdicts': kt['verdicts'], 'n_fails': kt['n_fails'], 'disagree': kt['disagree'],
           'fail_rows': kt['fails'][:3]}
    return Gc.stop, Gc.R, ktb, res


def stage(g, s, cases_by_pair, kinds, idx, plant=None):
    """Continuations i in idx of each kind for every case pair of round s.  cases_by_pair: {(X, Y): [readings]}.
    Returns {(X, Y): {kind: counts}} with the events of DC 4.3."""
    out = {key: {k: {'n': 0, 'stopped': 0, 'kt_verdicts': 0, 'kt_fails': 0, 'kt_disagree': 0,
                     'met': Counter(), 'met_ns': Counter(), 'met_any': Counter(), 'yown': Counter(),
                     'yown_ns': Counter(), 'meet': 0, 'placed': 0} for k in kinds}
           for key in cases_by_pair}
    keys = list(cases_by_pair)
    for k in kinds:
        for i in idx:
            groups = [[(X, Y, cases_by_pair[(X, Y)]) for (X, Y) in keys]] if k[:2] == 'BN' else \
                [[(X, Y, cases_by_pair[(X, Y)])] for (X, Y) in keys]
            for grp in groups:
                stop, R, kt, res = read_continuation(g, k, s, i, grp, plant)
                stopped = stop in ('knots', 'guard', 'residual_stall')
                for (X, Y, rs), r in zip(grp, res):
                    c = out[(X, Y)][k]
                    c['n'] += 1
                    c['stopped'] += int(stopped)
                    c['kt_verdicts'] += kt['verdicts']
                    c['kt_fails'] += kt['n_fails']
                    c['kt_disagree'] += kt['disagree']
                    c['meet'] += int(r['meet'] is not None)
                    c['placed'] += int(r['placed'] is not None)
                    for rd in rs:
                        if k[:2] == 'BN':
                            if rd in r['after']:
                                c['met'][rd] += 1
                                if not stopped:
                                    c['met_ns'][rd] += 1
                            if rd in r['first']:
                                c['met_any'][rd] += 1
                        else:
                            if rd in r['first']:
                                c['met'][rd] += 1
                                if not stopped:
                                    c['met_ns'][rd] += 1
                        yo = mcc.YOWN[rd]
                        if yo in r['first']:
                            c['yown'][rd] += 1
                            if not stopped:
                                c['yown_ns'][rd] += 1
    return out


def rates_of(cnt, rd):
    """q1 (BN, after the meeting), q1 at any round, q0 (BY), qY (BX: Y's own), qM (BM), qT (BT), with sizes."""
    def g(k, field):
        c = cnt.get(k)
        return (c[field][rd], c['n']) if c else (None, 0)
    q1, n1 = g('BN', 'met')
    q1a, _ = g('BN', 'met_any')
    q0, n0 = g('BY', 'met')
    qY, nY = (cnt['BX']['yown'][rd], cnt['BX']['n']) if 'BX' in cnt else (None, 0)
    qM, nM = g('BM', 'met')
    qT, nT = g('BT', 'met')
    out = {'q1': q1, 'n1': n1, 'q1_any': q1a, 'q0': q0, 'n0': n0, 'qY': qY, 'nY': nY, 'qM': qM, 'nM': nM,
           'qT': qT, 'nT': nT}
    # over the continuations not stopped
    ns = {}
    for k, field in (('BN', 'met_ns'), ('BY', 'met_ns'), ('BM', 'met_ns'), ('BT', 'met_ns')):
        if k in cnt:
            ns[k] = [cnt[k][field][rd], cnt[k]['n'] - cnt[k]['stopped']]
    if 'BX' in cnt:
        ns['BX'] = [cnt['BX']['yown_ns'][rd], cnt['BX']['n'] - cnt['BX']['stopped']]
    out['not_stopped'] = ns
    out['stopped'] = {k: cnt[k]['stopped'] for k in cnt}
    out['meetings'] = {k: cnt[k]['meet'] for k in cnt}
    return out


def first_stage_verdict(rt, level=0.01):
    p0 = mcc.fisher_greater(rt['q1'], rt['n1'], rt['q0'], rt['n0'])
    pY = mcc.fisher_greater(rt['q1'], rt['n1'], rt['qY'], rt['nY'])
    return {'p_vs_Ybarred': p0, 'p_vs_Yown': pY, 'passes_at_100': bool(p0 <= level and pY <= level),
            'one_history': bool(rt['q1'] <= 2),
            'ac_Ybarred': mcc.agresti_caffo(rt['q1'], rt['n1'], rt['q0'], rt['n0']),
            'ac_Yown': mcc.agresti_caffo(rt['q1'], rt['n1'], rt['qY'], rt['nY'])}


def confirm_verdict(rt, level):
    """DC 4.4: confirmed when q1 is above q0, qY and qT at `level` (0.01/m); the way by qM; 'needs the meeting'."""
    p0 = mcc.fisher_greater(rt['q1'], rt['n1'], rt['q0'], rt['n0'])
    pY = mcc.fisher_greater(rt['q1'], rt['n1'], rt['qY'], rt['nY'])
    pT = mcc.fisher_greater(rt['q1'], rt['n1'], rt['qT'], rt['nT'])
    pM = mcc.fisher_greater(rt['q1'], rt['n1'], rt['qM'], rt['nM'])
    pM2 = mcc.fisher_two(rt['q1'], rt['n1'], rt['qM'], rt['nM'])
    above0, aboveY, aboveT = p0 <= level, pY <= level, pT <= level
    conf = bool(above0 and aboveY and aboveT)
    out = {'level': level, 'p_vs_Ybarred': p0, 'p_vs_Yown': pY, 'p_vs_fully_masked': pT, 'p_vs_masked': pM,
           'p_masked_two_sided': pM2, 'confirmed': conf,
           'ac': {'Ybarred': mcc.agresti_caffo(rt['q1'], rt['n1'], rt['q0'], rt['n0']),
                  'Yown': mcc.agresti_caffo(rt['q1'], rt['n1'], rt['qY'], rt['nY']),
                  'fully_masked': mcc.agresti_caffo(rt['q1'], rt['n1'], rt['qT'], rt['nT']),
                  'masked': mcc.agresti_caffo(rt['q1'], rt['n1'], rt['qM'], rt['nM'])}}
    if conf:
        out['way'] = 'through joining' if pM <= level else 'through takes'
        out['needs the meeting'] = bool(rt['q0'] == 0 and rt['qT'] == 0)
    elif above0 and aboveY and not aboveT:
        out['way'] = "with Y's births, not through a meeting"
    return out


# ------------------------------------------------------------------------------------------------- one growth
def form_counts_by_round(g):
    """DC 7: for each round, the parts of each form with every member made after round 0; kept: the forms left twice."""
    out = []
    for t in range(g.G.R + 1):
        R = g.roster(t)
        if R is None:
            out.append(None)
            continue
        S = g.G.snaps[t]
        c = Counter()
        for i, Pt in enumerate(R.parts):
            if all(S.made[u] > 0 for u in Pt):
                f = mcc.Form(R, i)
                c[f.key()] += 1
        out.append({'parts': sum(c.values()), 'twice': {k: v for k, v in c.items() if v >= 2}})
    return out


def analyse_growth(stars, spec, sid, i, k1=100, rounds=mcc.ROUNDS, knot_bound=mcc.KNOT_BOUND, base=None,
                   pair_rule='sampled', first=True, kt=True, by_form=True, case_readings=CASE_READINGS,
                   return_growth=False, first_kinds=('BN', 'BY', 'BX')):
    t0 = time.time()
    g = mcc.Growth(stars, spec, sid, i, rounds, knot_bound, base=base, pair_rule=pair_rule)
    G = g.G
    row = {'start': sid, 'law': spec.name(), 'knot_law': spec.knot_law, 'weighting': spec.weighting, 'i': i,
           'seed': g.seed, 'rounds': G.R, 'stop': G.stop, 'guard': G.guard, 'knots': G.knots(),
           'n_start': len(stars)}
    prs = g.pairs()
    row['pair_rounds'] = {}
    row['pairs'] = []
    row['more_than_eight'] = []
    row['removed'] = 0
    cases = []
    for s, (plist, n_all, removed) in prs.items():
        row['pair_rounds'][s] = [len(plist), n_all, removed]
        row['removed'] += removed
        if n_all > 8:
            row['more_than_eight'].append(s)
        if not plist:
            continue
        refs = [g.ref(s, X, Y) for X, Y in plist]
        rd = mcc.read_pairs(G.snaps, G.records, G.R, refs, rosters=g.rosters, ties=g.ties)
        for (X, Y), ref, r in zip(plist, refs, rd):
            prow = {'s': s, 'X': list(X), 'Y': list(Y), 'xform': ref.xform.key(), 'yform': ref.yform.key(),
                    'same_form': ref.same_form, 'meet': r.meet, 'first': r.first, 'after': r.first_after,
                    'y_made': all(G.snaps[s].made[u] > 0 for u in Y)}
            row['pairs'].append(prow)
            for rdn in case_readings:
                if rdn in r.first_after:
                    S_s = G.snaps[s]
                    Rs = g.roster(s)
                    cases.append({'s': s, 'X': list(X), 'Y': list(Y), 'reading': rdn, 'meet': r.meet,
                                  'round_met': r.first_after[rdn], 'round_met_any': r.first[rdn],
                                  'xform': ref.xform.describe(), 'yform': ref.yform.describe(),
                                  'y_hk': [[Rs.h[u], Rs.k[u]] for u in Y],
                                  'y_loose_max': max(Rs.h[u] + Rs.k[u] for u in Y),
                                  'detail': r.detail.get('values'),
                                  'made_questions': made_questions(g, s, X, Y, r.meet)})
                    del S_s
    row['n_pairs'] = len(row['pairs'])
    row['has_pair'] = bool(row['pairs'])
    if kt:
        k = mcc.knot_test(G)
        row['knot_test'] = {'verdicts': k['verdicts'], 'n_fails': k['n_fails'], 'disagree': k['disagree'],
                            'fails': k['fails'][:20]}
        for x in ('untested', 'birth_vs_direct'):
            if x in k:
                row['knot_test'][x] = k[x]
    if by_form:
        row['by_form'] = form_counts_by_round(g)
    if first and cases:
        by_s = defaultdict(dict)
        for c in cases:
            by_s[c['s']].setdefault((tuple(c['X']), tuple(c['Y'])), []).append(c['reading'])
        for s, cbp in by_s.items():
            cnt = stage(g, s, cbp, first_kinds, range(k1))
            for c in cases:
                if c['s'] != s:
                    continue
                key = (tuple(c['X']), tuple(c['Y']))
                rt = rates_of({k[:2]: v for k, v in cnt[key].items()}, c['reading'])
                rt['kinds'] = list(first_kinds)
                c['rates100'] = rt
                c['first_stage'] = first_stage_verdict(rt)
                c['kt100'] = {k: [cnt[key][k]['kt_verdicts'], cnt[key][k]['kt_fails'], cnt[key][k]['kt_disagree']]
                              for k in cnt[key]}
    row['cases'] = cases
    row['sec'] = round(time.time() - t0, 3)
    if return_growth:
        return row, g
    return row
