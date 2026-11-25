"""R7, the exact renaming check (PC, "Runs", order 10; Lemma C-S1): every history of rounds 1 to 3 with its chance as an
exact fraction, where there are at most 30,000, else of rounds 1 and 2, or of round 1; the start against five
renamings (dev 30); the class compared is the state up to renaming, birth record and barred marks included, by
networkx's weisfeiler_lehman_graph_hash with 6 iterations on the graph of knots (kind, round made, retirement),
distinctions (barred), places and parent links.  Writes R7.jsonl and R7.json."""
import argparse
import multiprocessing as mp
import os
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import networkx as nx  # noqa: E402
import mcc  # noqa: E402
import study  # noqa: E402
from mcc import pm  # noqa: E402
from r8 import RENAMINGS, rename  # noqa: E402
from study import log  # noqa: E402

LIMIT = 30000


def checks():
    C = mcc.census()
    three = [i for i, s in enumerate(C) if s['n'] == 3][:6]
    four = [i for i, s in enumerate(C) if s['n'] == 4][:2]
    laws18 = [mcc.Spec(r, 'CANCEL-OFFSHOOT', tk, 'parity') for r in mcc.RATIONS for tk in mcc.TAKES] + \
        [mcc.Spec('FLOOR1', t, tk, 'parity') for t in ('CANCEL-RETIRE', 'CANCEL-WAIT') for tk in mcc.TAKES]
    out = []
    for i in three:
        for sp in laws18:
            out.append(('parity three-knot', i, sp.name()))
    seven = [mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'MET', 'parity', 'RELEASE', 'T2'),
             mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'STEPS-1', 'parity', 'RELEASE', 'T1'),
             mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'STEPS-1', 'parity', 'RELEASE', 'T2')] + \
        [mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', tk, 'parity', 'HOLD', w) for tk in mcc.TAKES for w in ('T1', 'T2')]
    for i in four:
        for sp in seven:
            out.append(('parity four-knot', i, sp.name()))
    for i in three[:2]:
        for sp in laws18:
            out.append(('nae three-knot', i, mcc.Spec(sp.ration, sp.treatment, sp.take, 'nae').name()))
    return out


def state_hash(S, retired):
    G = nx.Graph()
    for u in range(S.n_knots):
        if u in S.removed:
            continue
        G.add_node(('k', u), a='K|%s|%d|%d' % (S.kind[u], S.made[u], int(u in retired)))
    for d in range(S.n_distinctions):
        if S.holders[d]:
            G.add_node(('d', d), a='D|%d' % int(S.barred[d]))
    for u in range(S.n_knots):
        if u in S.removed:
            continue
        for d in S.places[u]:
            G.add_edge(('k', u), ('d', d), e='place')
        for p in S.parents[u]:
            G.add_edge(('k', u), ('k', p), e='parent')
    return nx.weisfeiler_lehman_graph_hash(G, node_attr='a', edge_attr='e', iterations=6)


def round_outcomes(S, law, weighting):
    """Every outcome of one round from S: (state after, exact chance, record, number of takes with two or more
    candidates); a round the guard stops gives (None, chance, None, ...)."""
    prefix = []
    while True:
        lens = []
        prob = [Fraction(1)]
        multi = [0]
        pos = [0]

        def chooser(key, cands):
            i = pos[0]
            pos[0] += 1
            if i >= len(prefix):
                prefix.append(0)
            k = prefix[i]
            lens.append(len(cands))
            if len(cands) >= 2:
                multi[0] += 1
            if weighting == 'T1':
                prob[0] *= Fraction(1, len(cands))
            else:
                h = [len(S.holders[d]) for d in cands]
                prob[0] *= Fraction(h[k], sum(h))
            return cands[k]
        T = S.copy()
        try:
            rec = pm.round_step(T, law, {'chooser': chooser})
        except pm.GuardStop:
            T, rec = None, None
        yield T, prob[0], rec, multi[0]
        del prefix[len(lens):]
        while prefix and prefix[-1] + 1 >= lens[len(prefix) - 1]:
            prefix.pop()
        if not prefix:
            return
        prefix[-1] += 1


def histories(S0, law, weighting, depth, limit):
    """Depth-first: every history of rounds 1..depth, each reduced at once to its class (state_hash) and exact
    chance (dev 57: no state is kept); None when there are more than `limit`.  Returns (dist, n, flags)."""
    dist = defaultdict(Fraction)
    flags = Counter()
    n = [0]

    def leaf(S, prob, retired, f):
        n[0] += 1
        if n[0] > limit:
            raise OverflowError
        dist[state_hash(S, retired)] += prob
        for k in f:
            flags[k] += 1

    def rec_(S, r, prob, retired, f0):
        if r == depth:
            leaf(S, prob, retired, f0)
            return
        for T, p, rec, multi in round_outcomes(S, law, weighting):
            if T is None:
                leaf(S, prob * p, retired, dict(f0, guard=True))
                continue
            f = dict(f0)
            if any(len(b['parents']) >= 3 for b in rec['births'] if b['kind'] == 'join'):
                f['join3'] = True
            if any(b['implied'] for b in rec['births']):
                f['implied'] = True
            if sum(1 for b in rec['births'] if b['rule_takes']) >= 2:
                f['two_taking'] = True
            if multi:
                f['multi'] = True
            rr = retired | set(rec['retired'])
            if T.n_knots - len(T.removed) > mcc.KNOT_BOUND:
                leaf(T, prob * p, rr, dict(f, knots=True))
                continue
            rec_(T, r + 1, prob * p, rr, f)
    try:
        rec_(S0, 0, Fraction(1), frozenset(), {})
    except OverflowError:
        return None
    return dist, n[0], flags


def job(args):
    label, idx, law, how, depth = args
    st = mcc.census()[idx]
    spec = mcc.Spec.from_name(law)
    stars = rename(st['stars'], st['id'], how)
    t0 = time.time()
    S0 = pm.from_stars(stars)
    try:
        if depth is None:
            for d in (3, 2, 1):
                H = histories(S0, spec.law(), spec.weighting, d, LIMIT)
                if H is not None:
                    depth = d
                    break
        else:
            H = histories(S0, spec.law(), spec.weighting, depth, 10 ** 9)
    except MemoryError:
        return {'label': label, 'index': idx, 'start': st['id'], 'law': law, 'renaming': how, 'depth': depth,
                'error': 'memory', 'sec': round(time.time() - t0, 2)}
    dist, n, flags = H
    assert sum(dist.values()) == 1
    return {'label': label, 'index': idx, 'start': st['id'], 'law': law, 'renaming': how, 'depth': depth,
            'histories': n, 'flags': dict(flags), 'dist': {k: str(v) for k, v in sorted(dist.items())},
            'sec': round(time.time() - t0, 2)}


class _Null:
    def __enter__(self):
        class P:
            def imap_unordered(self, f, jobs, chunksize=1):
                return iter(())
        return P()

    def __exit__(self, *a):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--analyse-only', action='store_true')
    a = ap.parse_args()
    ch = checks()
    prev = [x for x in study.read_jsonl('R7.jsonl') if 'error' not in x]
    log('R7', len(ch), 'checks;', len(prev), 'enumerations already written (resumed, dev 57)')
    ctx = mp.get_context('fork')
    w = study.JsonLines('R7.jsonl', 'a')
    t0 = time.time()
    first = {(x['label'], x['index'], x['law']): x for x in prev if x['renaming'] == 'none'}
    res = defaultdict(dict)
    for x in prev:
        if x['renaming'] != 'none':
            res[(x['label'], x['index'], x['law'])][x['renaming']] = x
    errors = [x for x in study.read_jsonl('R7.jsonl') if 'error' in x]
    with (ctx.Pool(a.procs, initializer=study.cap_memory) if not a.analyse_only else _Null()) as pool:
        todo = [(lab, i, law, 'none', None) for lab, i, law in ch if (lab, i, law) not in first]
        if a.analyse_only:
            todo = []
        jobs = todo + [(lab, i, law, how, first[(lab, i, law)]['depth']) for lab, i, law in ch
                       if (lab, i, law) in first for how in RENAMINGS[1:] if how not in res[(lab, i, law)]]
        if a.analyse_only:
            jobs = []
        later = []
        for k, r in enumerate(pool.imap_unordered(job, jobs, chunksize=1), 1):
            w.write(r)
            if 'error' in r:
                errors.append(r)
            elif r['renaming'] == 'none':
                first[(r['label'], r['index'], r['law'])] = r
                later += [(r['label'], r['index'], r['law'], how, r['depth']) for how in RENAMINGS[1:]]
            else:
                res[(r['label'], r['index'], r['law'])][r['renaming']] = r
            if k % 100 == 0:
                w.flush()
                log('R7 %d/%d' % (k, len(jobs)))
        for r in pool.imap_unordered(job, later, chunksize=1):
            w.write(r)
            if 'error' in r:
                errors.append(r)
            else:
                res[(r['label'], r['index'], r['law'])][r['renaming']] = r
    w.close()
    rows = []
    for key, f in first.items():
        row = {'label': key[0], 'start': f['start'], 'law': key[2], 'depth': f['depth'], 'histories': f['histories'],
               'single_history': f['histories'] == 1, 'flags': f['flags'], 'equal': {}}
        for how in RENAMINGS[1:]:
            r = res[key].get(how)
            row['equal'][how] = None if r is None else (r['dist'] == f['dist'])
            row.setdefault('histories_renamed', {})[how] = None if r is None else r['histories']
        row['all_equal'] = all(v is True for v in row['equal'].values())
        row['complete'] = all(v is not None for v in row['equal'].values())
        rows.append(row)
    stopped = [(lab, mcc.census()[i]['id'], law) for lab, i, law in ch if (lab, i, law) not in first]
    summ = {'checks registered': len(ch), 'checks read': len(rows), 'checks not read (stopped, dev 58)': stopped,
            'checks not read (memory cap)': sorted({(e['label'], e['start'], e['law']) for e in errors
                                                    if (e['label'], e['index'], e['law']) not in first}),
            'renamings not read (memory cap)': [(e['label'], e['start'], e['law'], e['renaming']) for e in errors
                                                if e['renaming'] != 'none'],
            'checks': sum(r['complete'] for r in rows), 'all_equal': sum(r['all_equal'] for r in rows),
            'differ': [r for r in rows if r['complete'] and not r['all_equal']],
            'single_history': sum(r['single_history'] for r in rows if r['complete']),
            'histories': sum(r['histories'] for r in rows), 'by_label': {},
            'depths': dict(Counter(r['depth'] for r in rows))}
    for lab in sorted({r['label'] for r in rows}):
        rr = [r for r in rows if r['label'] == lab and r['complete']]
        summ['by_label'][lab] = {'checks': len(rr), 'all_equal': sum(r['all_equal'] for r in rr),
                                 'single_history': sum(r['single_history'] for r in rr),
                                 'starts': len({r['start'] for r in rr}),
                                 'histories': sum(r['histories'] for r in rr),
                                 'depths': dict(Counter(r['depth'] for r in rr)),
                                 'checks_with': {k: sum(1 for r in rr if r['flags'].get(k)) for k in
                                                 ('multi', 'two_taking', 'join3', 'implied', 'guard', 'knots')},
                                 'histories_with': {k: sum(r['flags'].get(k, 0) for r in rr) for k in
                                                    ('multi', 'two_taking', 'join3', 'implied', 'guard', 'knots')}}
    summ['rows'] = rows
    study.write_json('R7.json', summ)
    log('R7', summ['checks'], 'checks complete,', summ['all_equal'], 'all equal,', summ['single_history'],
        'single history; not read:', summ['checks not read (memory cap)'], round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
