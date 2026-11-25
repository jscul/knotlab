"""Part 7: grow again (PR part 7; TD 7.1; R 31-34).  The smallest gain's part and the first 10 starts of
census_index.json, each under its 4n renumberings, grown under Q-OLDEST and Q-NEWEST through 3 rounds by the fold study's
engine; finished structures compared after carrying the renaming back; counting from the start compared where they are
the same."""
from __future__ import annotations

import json
import signal
import sys
import time
from fractions import Fraction as Fr
from multiprocessing import Pool

import networkx as nx
from networkx.algorithms import isomorphism as iso

import tc

sys.path.insert(0, tc.REPO + '/experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
import pm  # noqa: E402

STATE_CAP = 1 << 20
SEARCH_LIMIT = 5


class SearchLimit(Exception):
    pass


def _alarm(*a):
    raise SearchLimit()


def renumberings(knots):
    """TD 7.1: 4n renumberings.  knots: [(rule, places)] with sortable names."""
    names = sorted({p for _, P in knots for p in P})
    n = len(names)
    out = []
    for k in range(n):
        rot = names[k:] + names[:k]
        for rev in (False, True):
            lst = list(reversed(rot)) if rev else rot
            pos = {nm: i for i, nm in enumerate(lst)}
            for krev in (False, True):
                ks = list(reversed(knots)) if krev else list(knots)
                out.append({'k': k, 'reversed': rev, 'knots reversed': krev, 'names': lst,
                            'knots': [(rule, tuple(pos[p] for p in P)) for rule, P in ks]})
    return out


def grow(rk, choice):
    """Grow the renumbered start through 3 rounds; return knots in original names (new distinctions 'n<i>'), with the
    round each knot was made, and the run's stop."""
    stars = [list(P) for _, P in rk['knots']]
    S0 = pm.from_stars(stars)
    assert S0.labels == list(range(len(rk['names'])))
    law = pm.Law(ration='ORD', treatment='STALL', release='RELEASE', knot_law='nae', take='Q', choice=choice)
    run = pm.Run(S0, law, rounds=3)
    S = run.S
    n = len(rk['names'])
    rules = [r for r, _ in rk['knots']]

    def nm(d):
        return rk['names'][d] if d < n else ('new', d)
    out = []
    for u in range(S.n_knots):
        rule = rules[u] if u < len(rules) else 'nae'
        out.append((rule, tuple(nm(d) for d in S.places[u]), S.made[u]))
    stalled = any(r['stalled'] for r in run.records)
    maker = {}
    for d in range(S.n_distinctions):
        if d >= n:
            maker[nm(d)] = S.holders[d][0]
    return {'knots': out, 'rounds': run.rounds_done, 'stop': run.stop, 'stalled': stalled,
            'births per round': [r['n_births'] for r in run.records],
            'parents': [list(S.parents[u]) for u in range(S.n_knots)], 'maker': maker}


def history_key(g):
    import hashlib
    keys = {}

    def dkey(p):
        if isinstance(p, tuple):
            return 'f:' + kkey(g['maker'][p])
        return 'n:' + repr(p)

    def kkey(u):
        if u in keys:
            return keys[u]
        rule, P, made = g['knots'][u]
        own = [p for p in P if isinstance(p, tuple) and g['maker'][p] == u]
        ins = sorted(dkey(p) for p in P if p not in own)
        par = sorted(kkey(q) for q in g['parents'][u])
        s = repr((rule, made, par, ins, len(own)))
        keys[u] = hashlib.sha1(s.encode()).hexdigest()
        return keys[u]
    return sorted(kkey(u) for u in range(len(g['knots'])))


def graph(g, with_round):
    """Knots and distinctions; a new distinction held by one knot alone is folded into that knot's label as a count (such
    distinctions are interchangeable), so the isomorphism search does not branch over them."""
    holders = {}
    for i, (rule, P, made) in enumerate(g['knots']):
        for p in P:
            holders[p] = holders.get(p, 0) + 1
    G = nx.Graph()
    leaves = {}
    for i, (rule, P, made) in enumerate(g['knots']):
        lv = [p for p in P if isinstance(p, tuple) and holders[p] == 1]
        leaves[i] = lv
        G.add_node(('K', i), label=str(('K', rule, made if with_round else None, len(lv))))
        for p in P:
            if p in lv:
                continue
            if not G.has_node(('D', p)):
                G.add_node(('D', p), label=str(('D', 'new' if isinstance(p, tuple) else p)))
            G.add_edge(('K', i), ('D', p))
    return G, leaves


def compare(g0, g1, with_round):
    (G0, L0), (G1, L1) = graph(g0, with_round), graph(g1, with_round)
    if G0.number_of_nodes() != G1.number_of_nodes() or G0.number_of_edges() != G1.number_of_edges():
        return None
    if (nx.weisfeiler_lehman_graph_hash(G0, node_attr='label', iterations=4)
            != nx.weisfeiler_lehman_graph_hash(G1, node_attr='label', iterations=4)):
        return None
    gm = iso.GraphMatcher(G0, G1, node_match=lambda a, b: a['label'] == b['label'])
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(SEARCH_LIMIT)
    try:
        found = gm.is_isomorphic()
    except SearchLimit:
        return 'undecided'
    finally:
        signal.alarm(0)
    if found:
        m = dict(gm.mapping)
        for (kind, i), (_, j) in list(m.items()):
            if kind == 'K':
                for p, q in zip(L0[i], L1[j]):
                    m[('D', p)] = ('D', q)
        return m
    return None


def history_of(g):
    rounds = max(m for _, _, m in g['knots'])
    stages = [[(r, P) for r, P, m in g['knots'] if m == j] for j in range(rounds + 1)]
    return stages


def weighting(g):
    """Counting from the start on the grown history (rounds as stages), or None if too large."""
    stages = history_of(g)
    nv = len(tc.variables_of([k for st in stages for k in st]))
    if nv > 24:
        return None, 'more than 24 distinctions'
    H = tc.History(stages)
    if len(H.A[-1]) > STATE_CAP:
        return None, 'more than %d states' % STATE_CAP
    W, kept = tc.counting(H, 0)
    return (H, W), None


def one(job):
    tc.cap_memory()
    label, knots = job
    rks = renumberings(knots)
    res = {'start': label, 'n distinctions': len({p for _, P in knots for p in P}), 'renumberings': len(rks), 'laws': {}}
    for choice in ('OLDEST', 'NEWEST'):
        grown = [grow(rk, choice) for rk in rks]
        base = grown[0]           # k = 0, as listed, knots as listed: the start as given (R 31)
        assert rks[0]['k'] == 0 and not rks[0]['reversed'] and not rks[0]['knots reversed']
        rows = []
        wb, why = weighting(base)
        hk0 = history_key(base)
        for rk, g in zip(rks, grown):
            same_hist = history_key(g) == hk0
            wg, why2 = weighting(g) if (wb is not None) else (None, why)
            numeric = wb is not None and wg is not None
            if same_hist and not numeric:
                struct, m_struct = True, None            # same history: same structure (R 36, step i)
            else:
                m_struct = compare(base, g, False)
                if m_struct == 'undecided':
                    struct, m_struct = (True if same_hist else 'not decided (search limit)'), None
                else:
                    struct = True if (m_struct is not None or same_hist) else False
            row = {'k': rk['k'], 'reversed': rk['reversed'], 'knots reversed': rk['knots reversed'],
                   'rounds': g['rounds'], 'stalled': g['stalled'], 'births per round': g['births per round'],
                   'knots': len(g['knots']), 'same finished structure': struct,
                   'same history (rounds kept)': same_hist}
            if struct is not True:
                row['weighting'] = 'no comparison' if struct is False else 'not decided (structure comparison)'
            elif not numeric or m_struct is None:
                row['weighting'] = ('same by the renaming of the whole history' if same_hist
                                    else 'not decided (%s)' % (why or why2 or 'no mapping'))
            else:
                (H0, W0), (H1, W1) = wb, wg
                inv = {v[1]: k[1] for k, v in m_struct.items() if k[0] == 'D'}
                d0 = tc.as_dict(H0, W0)
                d1 = {}
                for w, x in tc.as_dict(H1, W1).items():
                    y = 0
                    for v, i in H1.idx.items():
                        if (w >> i) & 1:
                            y |= 1 << H0.idx[inv[v]]
                    d1[y] = x
                row['weighting'] = 'same' if d0 == d1 else 'DIFFERENT'
                row['allowed states'] = len(d0)
            rows.append(row)
        res['laws']['Q-' + choice] = {
            'rows': rows, 'given': {'knots': len(base['knots']), 'rounds': base['rounds'], 'stalled': base['stalled'],
                                    'births per round': base['births per round'],
                                    'structure': ['%s(%s)@%d' % (r, ','.join(str(p) for p in P), m)
                                                  for r, P, m in base['knots']]},
            'different finished structures': sum(1 for r in rows if r['same finished structure'] is False),
            'structure comparison not decided': sum(1 for r in rows if r['same finished structure'] not in (True, False)),
            'same structure, different history': sum(1 for r in rows if r['same finished structure'] is True
                                                     and not r['same history (rounds kept)']),
            'weighting same': sum(1 for r in rows if r['weighting'] == 'same'),
            'weighting DIFFERENT': sum(1 for r in rows if r['weighting'] == 'DIFFERENT'),
            'weighting by renaming only': sum(1 for r in rows if str(r['weighting']).startswith('same by the renaming')),
            'weighting not decided': sum(1 for r in rows if str(r['weighting']).startswith('not decided'))}
    return res


def main():
    T0 = time.time()
    tc.cap_memory()
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    S = tc.load_structures()
    ci = json.load(open(tc.REPO + '/research/TWO-COUNTINGS-20261125-001A/census_index.json'))
    jobs = [('smallest gain: part', S['smallest gain: part'])]
    for st in ci['starts'][:10]:
        jobs.append(('census %d' % st['census_index'], [('nae', tuple(s)) for s in st['stars']]))
    with Pool(nproc) as pool:
        rows = list(pool.imap(one, jobs))
    p6a = any(r['laws'][l]['different finished structures'] > 0 for r in rows for l in r['laws'])
    p6b_fail = sum(r['laws'][l]['weighting DIFFERENT'] for r in rows for l in r['laws'])
    out = {'part': 7, 'rows': rows, 'P6a holds (some renumbering grows a different finished structure)': p6a,
           'P6b: weightings that differ on the same structure': p6b_fail,
           'counts': {r['start']: {l: {k: v for k, v in r['laws'][l].items() if k not in ('rows', 'given')}
                                   for l in r['laws']} for r in rows},
           'wall_s': round(time.time() - T0, 1), 'processes': nproc}
    tc.dump('part7_grow_again.json', out)
    print(json.dumps(out['counts'], indent=0)[:3000])
    print('P6a', p6a, 'P6b differing', p6b_fail, 'wall', out['wall_s'])


if __name__ == '__main__':
    main()
