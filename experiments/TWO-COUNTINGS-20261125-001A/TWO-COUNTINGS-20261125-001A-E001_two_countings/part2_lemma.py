"""Part 2: the lemma tests (PR, part 2; TD 9; R 16-24)."""
from __future__ import annotations

import glob
import gzip
import itertools
import json
import os
import sys
import time
from fractions import Fraction as Fr
from multiprocessing import Pool

import lemma
import specs
import tc

sys.path.insert(0, tc.REPO + '/experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
import pm  # noqa: E402  (the fold study's engine, unchanged)

ART = tc.REPO + '/artifacts/'
OP = ART + 'ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/'
RR = ART + 'REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/'


def compact(ev):
    out = {}
    for k, v in ev.items():
        if k == 'hypotheses':
            out[k] = v
        elif isinstance(v, Fr):
            out[k] = tc.fstr(v)
        else:
            out[k] = v
    return out


def compact_run(r):
    o = {'name': r['name'], 'variants': []}
    for v in r['variants']:
        o['variants'].append({'label': v['label'], 'info': v['info'], 'finished': v['finished'],
                              'rows': {k: compact(x) for k, x in v['rows'].items()}})
    if 'pooled' in r:
        o['pooled'] = {k: compact(x) for k, x in r['pooled'].items()}
    return o


# ------------------------------------------------------------------------------------------ the 10-knot starts
def q_all_round(knots):
    """Every combination of rule Q's round-1 choices on a start (R 17).  Returns (choice points, [(choice, births)])."""
    stars = [list(P) for _, P in knots]
    S0 = pm.from_stars(stars)
    law = pm.Law(ration='ORD', treatment='STALL', release='RELEASE', knot_law='nae', take='Q', choice='OLDEST')
    points = []

    def rec(key, cands):
        points.append((key, list(cands)))
        return cands[0]
    pm.round_step(S0.copy(), law, {'chooser': rec})
    out = []
    for combo in itertools.product(*[c for _, c in points]):
        pick = {k: d for (k, _), d in zip(points, combo)}
        seen = []

        def ch(key, cands):
            seen.append((key, list(cands)))
            return pick[key]
        T = S0.copy()
        r = pm.round_step(T, law, {'chooser': ch})
        assert seen == points, 'candidate lists depend on the other choices'
        births = []
        for b in r['births']:
            births.append({'parent': tc.kstr(knots[b['parents'][0]]),
                           'inputs': [S0.labels[d] for d in b['inputs']], 'f': b['f'], 'kind': b['kind']})
        out.append(({k[1]: S0.labels[d] for k, d in pick.items()}, births))
    return [(k, [S0.labels[d] for d in c]) for k, c in points], out


def ten_specs(key, label, S):
    start = S[key]
    points, combos = q_all_round(start)
    info = {'choice points': points, 'combinations': len(combos), 'births': {}}
    # identify births
    first = combos[0][1]
    ia = next(i for i, b in enumerate(first) if b['inputs'][0] == 'x1')
    ib = next(i for i, b in enumerate(first) if b['inputs'][0] == 'y1')
    ic = [i for i in range(len(first)) if i not in (ia, ib)]
    assert len(ic) == 1
    ic = ic[0]
    optsA = sorted({c[1][ia]['inputs'][1] for c in combos})
    optsB = sorted({c[1][ib]['inputs'][1] for c in combos})
    optsC = sorted({c[1][ic]['inputs'][1] for c in combos})
    orderB = ['y2', 'y3', 't']
    pairB = tuple(sorted(optsB, key=orderB.index))
    third_loose = first[ic]['inputs'][0]
    info.update({'first observer options': optsA, 'second observer options': list(pairB),
                 'third birth': 'the birth taking %s; options %s' % (third_loose, optsC)})
    fs = sorted({b['f'] for _, bs in combos for b in bs})
    info['fresh counts given by the engine'] = fs

    def birth_knot(b, zname):
        names = [zname] + ['%s_%d' % (zname, i) for i in range(2, b['f'] + 1)]
        return ('nae', tuple(b['inputs']) + tuple(names[:b['f']]))
    out = []
    for oa in specs.OPT_A:
        KA, KB, extra = {}, {}, {}
        variants = []
        for third in optsC:
            ex = {}
            for a in (0, 1):
                for b in (0, 1):
                    want = {ia: oa[a], ib: pairB[b], ic: third}
                    combo = next(bs for ch, bs in combos if all(bs[i]['inputs'][1] == want[i] for i in want))
                    KA.setdefault(a, [birth_knot(combo[ia], 'za')])
                    KB.setdefault(b, [birth_knot(combo[ib], 'zb')])
                    assert KA[a] == [birth_knot(combo[ia], 'za')] and KB[b] == [birth_knot(combo[ib], 'zb')]
                    ex[(a, b)] = [birth_knot(combo[ic], 'f3')]
            variants.append({'label': 'third birth takes %s' % third, 'extra': ex})
        out.append({'name': '%s %s/%s' % (label, '-'.join(oa), '-'.join(pairB)), 'pre': [start], 'KA': KA, 'KB': KB,
                    'recA': specs.REC_A, 'recB': specs.REC_B, 'variants': variants, 'extra_side': 'B',
                    'registered pair': oa == ('x2', 'x3')})
    return out, info


# ------------------------------------------------------------------------------------------------------ keyed
def keyed(spec_start, label):
    KA, KB = specs.setting_knots()
    Hs = {(a, b): tc.History([spec_start, KA[a] + KB[b]]) for a in (0, 1) for b in (0, 1)}
    H0 = Hs[(0, 0)]
    A0 = [int(o) for o in H0.A[0]]
    xs = ['x1', 'x2', 'x3']
    pat = {o: H0.value(o, xs) for o in A0}
    pats = sorted(set(pat.values()))
    # per (a, b), per old state: the second record's distribution contributions
    contrib_s = {}
    contrib_f = {}
    for (a, b), H in Hs.items():
        assert [int(x) for x in H.A[0]] == A0 or set(int(x) for x in H.A[0]) == set(A0)
        F = H.A[1]
        o_of = F & tc.np.int64(H.mask_at(0))
        v = H.values(F, specs.REC_B)
        cs = H.c[1]
        cmap = {int(o): int(c) for o, c in zip(H.A[0], cs)}
        dS = {}
        dF = {}
        for o, vv in zip(o_of.tolist(), v.tolist()):
            dS.setdefault(o, {}).setdefault(vv, Fr(0))
            dS[o][vv] += Fr(1, len(A0) * cmap[o])
            dF.setdefault(o, {}).setdefault(vv, 0)
            dF[o][vv] += 1
        contrib_s[(a, b)] = dS
        contrib_f[(a, b)] = dF
    nfun = 1 << len(pats) if label == 'eleven' else 256
    res = {}
    for b in (0, 1):
        dists_s, dists_f = [], []
        for gi in range(nfun):
            if label == 'eleven':
                g = {p: (gi >> i) & 1 for i, p in enumerate(pats)}
            else:
                g = {p: (gi >> p) & 1 for p in range(8)}
            ds = {}
            df = {}
            for o in A0:
                a = g[pat[o]]
                for vv, x in contrib_s[(a, b)].get(o, {}).items():
                    ds[vv] = ds.get(vv, Fr(0)) + x
                for vv, n in contrib_f[(a, b)].get(o, {}).items():
                    df[vv] = df.get(vv, 0) + n
            tot = sum(df.values())
            dists_s.append(ds)
            dists_f.append({k: Fr(n, tot) for k, n in df.items()})
        def largest(ds):
            best, arg = Fr(0), None
            for i in range(len(ds)):
                for j in range(i + 1, len(ds)):
                    t = tc.tv(ds[i], ds[j])
                    if t > best:
                        best, arg = t, (i, j)
            return best, arg
        const = [0, nfun - 1]
        bs, args = largest(dists_s)
        bf, argf = largest(dists_f)
        cf = max(tc.tv(dists_f[i], dists_f[c]) for i in range(nfun) for c in const)
        cs_ = max(tc.tv(dists_s[i], dists_s[c]) for i in range(nfun) for c in const)
        res['second observer fixed at %d' % b] = {
            'functions g': nfun, 'first observer allowed patterns of (x1,x2,x3)': len(pats),
            'from the start: largest change of the second record between two g': tc.fstr(bs),
            'from the finish (pooled): largest change of the second record between two g': tc.fstr(bf),
            'from the finish (pooled): attained by (g, g′) as bit strings over the patterns': None if argf is None else
            [format(argf[0], '0%db' % (len(pats) if label == 'eleven' else 8)),
             format(argf[1], '0%db' % (len(pats) if label == 'eleven' else 8))],
            'from the start: largest change against a constant function': tc.fstr(cs_),
            'from the finish (pooled): largest change against a constant function': tc.fstr(cf)}
    return {'structure': label, 'patterns': pats, 'results': res}


# ----------------------------------------------------------------------------------------------- records
def record_spec(r, name):
    ks = [tc.parse_knot(k) for k in r['knots']]
    nb = len(r['births'][0])
    KA, KB = specs.setting_knots()
    return {'name': name, 'pre': [ks[:len(ks) - nb], ks[len(ks) - nb:]], 'KA': KA, 'KB': KB, 'recA': specs.REC_A,
            'recB': specs.REC_B}


def run_record(job):
    tc.cap_memory()
    src, i, r = job
    name = '%s #%d (tid %s, %s, laws %s, choice %s)' % (src, i, r.get('tid'), r.get('kind'), r.get('laws', r.get('newborn_laws')),
                                                       r.get('choice'))
    t = time.time()
    out = lemma.run_spec(record_spec(r, name))
    c = compact_run(out)
    v = out['variants'][0]['rows']
    rec_val = r['eval'][3]
    fin = v['from the finish']
    c['record'] = {'source': src, 'index': i, 'eval': r['eval'], 'tid': r.get('tid'), 'si': r.get('si'),
                   'arm': r.get('arm'), 't': r.get('t'), 'kind': r.get('kind')}
    c['P1'] = {'recorded': rec_val, 'finish all functions': tc.fstr(fin['score_all']),
               'finish parity (absolute)': tc.fstr(fin['score_parity_abs']),
               'finish parity (signed)': tc.fstr(fin['score_parity']),
               'reproduced': rec_val in (tc.fstr(fin['score_all']), tc.fstr(fin['score_parity_abs'])),
               'equals all functions': rec_val == tc.fstr(fin['score_all']),
               'equals absolute parity': rec_val == tc.fstr(fin['score_parity_abs']),
               'recorded hidden': bool(r['eval'][0] and r['eval'][1]) if isinstance(r['eval'][0], bool) else None,
               'hidden here': fin['hidden']}
    c['wall_s'] = round(time.time() - t, 2)
    return c


def load_records():
    G = []
    for f in sorted(glob.glob(OP + 'census_gains_c_*.jsonl.gz')):
        G += [json.loads(l) for l in gzip.open(f, 'rt')]
    G1 = [r for r in G if r['t'] == 1]
    R = []
    for f in sorted(glob.glob(RR + 'arm1_gains_three_*.jsonl.gz')):
        R += [json.loads(l) for l in gzip.open(f, 'rt')]
    return G1, R


def main():
    T0 = time.time()
    tc.cap_memory()
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    S = tc.load_structures()
    res = {'part': 2, 'items': [], 'walls': {}}

    def add(item_label, r, t):
        res['items'].append({'item': item_label, 'result': compact_run(r)})
        res['walls'][item_label] = res['walls'].get(item_label, 0) + round(time.time() - t, 2)

    t = time.time()
    for oa in specs.OPT_A:
        for ob in specs.OPT_B:
            add('eleven, option pairs', lemma.run_spec(specs.eleven(oa, ob, S),
                                                       extra_marginals={'(s1,s2)': ['s1', 's2']}), t)
            t = time.time()
    print('eleven done', round(time.time() - T0, 1), flush=True)
    add('smallest gain, its three stages', lemma.run_spec(specs.smallest_gain(S)), t)
    t = time.time()
    for key, nm in [('seven (start)', 'seven'), ('eight (start)', 'eight'), ('nine, the pencil (start)', 'nine')]:
        add('7-, 8-, pencil 9-knot', lemma.run_spec(specs.simple(key, nm, S)), t)
        t = time.time()
    # the 18-knot: SAT with blocking clauses against the engine
    from pysat.solvers import Solver
    st = S['eighteen (start)']
    vs = tc.variables_of(st)
    iv = {v: i + 1 for i, v in enumerate(vs)}
    sat = Solver(name='minisat22')
    for rule, P in st:
        if rule == 'nae':
            sat.add_clause([iv[p] for p in P])
            sat.add_clause([-iv[p] for p in P])
        else:
            want = 0 if rule == 'even' else 1
            for bits in itertools.product((0, 1), repeat=len(P)):
                if sum(bits) % 2 != want:
                    sat.add_clause([(iv[p] if b == 0 else -iv[p]) for p, b in zip(P, bits)])
    sols = set()
    while sat.solve():
        m = sat.get_model()
        sols.add(tuple(1 if x > 0 else 0 for x in m[:len(vs)]))
        sat.add_clause([-x for x in m[:len(vs)]])
    sat.delete()
    H = tc.History([st])
    mine = {tuple((int(w) >> H.idx[v]) & 1 for v in vs) for w in H.A[0]}
    eighteen_sat = {'SAT with blocking clauses': len(sols), 'engine': len(mine), 'equal': sols == mine}
    print('eighteen start states', eighteen_sat, flush=True)
    add('eighteen', lemma.run_spec(specs.simple('eighteen (start)', 'eighteen', S)), t)
    res['eighteen start states'] = eighteen_sat
    t = time.time()
    tens = {}
    for key, lab in [('ten A: eleven less even(y2,k1,k2) (start)', 'ten A'),
                     ('ten B: eleven less odd(y3,k1,k2) (start)', 'ten B')]:
        sps, info = ten_specs(key, lab, S)
        tens[lab] = info
        for sp in sps:
            r = lemma.run_spec(sp)
            r['registered pair'] = sp['registered pair']
            add('two 10-knot starts, three rule-Q births (Q-ALL)', r, t)
            res['items'][-1]['registered pair'] = sp['registered pair']
            t = time.time()
    res['ten round 1'] = tens
    print('tens done', round(time.time() - T0, 1), flush=True)
    KA, KB = specs.setting_knots()
    eight3 = [('odd', ('x1', 'x3', 's1')), ('odd', ('h1', 'h2', 'h3')), ('even', ('x2', 'h1', 'h2', 'h3')),
              ('even', ('y1', 'y3', 's1')), ('odd', ('k1', 'k2', 'k3')), ('even', ('y2', 'k1', 'k2', 'k3'))]
    add('the 8/3 case of REVIEW-LEADS-20261123-001C', lemma.run_spec(
        {'name': 'eight-thirds case', 'pre': [eight3], 'KA': KA, 'KB': KB, 'recA': specs.REC_A, 'recB': specs.REC_B}), t)
    t = time.time()
    res['keyed'] = [keyed(S['eleven (start)'], 'eleven'), keyed(S['eighteen (start)'], 'eighteen')]
    res['walls']['keyed settings'] = round(time.time() - t, 2)
    print('keyed done', round(time.time() - T0, 1), flush=True)
    # the records, in parallel
    G1, R = load_records()
    jobs = [('ONE-PARENT-REREAD uniform', i, r) for i, r in enumerate(G1) if r['arm'] == 'uniform']
    jobs += [('ONE-PARENT-REREAD mixed', i, r) for i, r in enumerate(G1) if r['arm'] == 'mixed']
    jobs += [('REREAD-BIRTHS rule R', i, r) for i, r in enumerate(R)]
    print('records:', len(jobs), 'processes', nproc, flush=True)
    t = time.time()
    recs = []
    with Pool(nproc) as pool:
        for k, c in enumerate(pool.imap(run_record, jobs, chunksize=4)):
            recs.append(c)
            if k % 100 == 0:
                print('record', k, round(time.time() - T0, 1), flush=True)
    res['walls']['records'] = round(time.time() - t, 2)
    res['records'] = recs
    res['wall_s'] = round(time.time() - T0, 1)
    tc.dump('part2_lemma.json', res)
    print('part 2 wall', res['wall_s'])


if __name__ == '__main__':
    main()
