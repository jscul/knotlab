"""Score NAE-GROWTH-20261119-001B-E001.  python3 -B merge.py <runner out dir> <results.json>

Part C: P1 (no parity-implied junction: identical counts and outcome), P2 (a parity closure at round T: equal through T, then k
junctions at T + k, or k + 1 when the top took one bit), P3 (no not-all-equal junction implied; the lemma's hypotheses hold),
P4 (parity implies only the closing top).  Part P: P5.  Part B, on distinct presentations (stars up to renaming): B1 (tree
stages: equal tables), B2 (some stage with a cycle differs), B3 / B3c (under not-all-equal / parity, two presentations with equal
tables up to renaming have the same allowed states up to renaming), B4 (every not-all-equal collision has a redundant junction
on one side), B5 / B5c (under not-all-equal / parity, equal tables and no redundant junction on either side give the same next
joins up to renaming)."""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402
sys.path.insert(0, str(HERE))
import bondlib as BL  # noqa: E402


def tail_ok(p, a, top_p):
    T = len(p['counts']) - 1
    if a['counts'][:T + 1] != p['counts']:
        return False, 'differs before the top'
    first = 1 if top_p >= 2 else 2
    want = [first + k for k in range(len(a['counts']) - T - 1)]
    if a['counts'][T + 1:] != want:
        return False, f"tail {a['counts'][T + 1:]} != {want}"
    if a['outcome'] not in ('alive',):
        return False, f"outcome {a['outcome']}"
    if len(a['counts']) - T - 1 < 3:
        return False, 'tail shorter than three rounds'
    return True, ''


def score_c(rows):
    res = {'arrangements': len(rows)}
    p1 = {'n': 0, 'held': 0, 'fails': []}
    p2 = {'n': 0, 'held': 0, 'fails': [], 'top_one_bit': 0}
    p3 = {'nae_implied': 0, 'min_places': 10 ** 9, 'max_given': 0, 'min_kept': 10 ** 9}
    p4 = {'parity_implied': 0, 'not_the_closing_top': []}
    trans = Counter()
    for r in rows:
        p, a = r['parity'], r['nae']
        trans[(p['outcome'], a['outcome'])] += 1
        p3['nae_implied'] += len(a['implied'])
        p3['min_places'] = min(p3['min_places'], a['min_places'])
        p3['max_given'] = max(p3['max_given'], a['max_given'])
        if a['min_kept'] is not None:
            p3['min_kept'] = min(p3['min_kept'], a['min_kept'])
        p4['parity_implied'] += len(p['implied'])
        if not p['implied']:
            p1['n'] += 1
            same = a['counts'] == p['counts'] and a['outcome'] == p['outcome']
            if same:
                p1['held'] += 1
            else:
                p1['fails'].append(r['key'])
            continue
        T = len(p['counts']) - 1
        if len(p['implied']) != 1 or p['outcome'] != 'closed' or p['implied'][0][0] != T or p['implied'][0][2] != 0:
            p4['not_the_closing_top'].append(r['key'])
            continue
        p2['n'] += 1
        top_p = p['implied'][0][1]
        p2['top_one_bit'] += top_p == 1
        ok, why = tail_ok(p, a, top_p)
        if ok:
            p2['held'] += 1
        else:
            p2['fails'].append([r['key'], why])
    p1['pass'] = p1['held'] == p1['n']
    p2['pass'] = p2['held'] == p2['n'] and p2['n'] > 0
    p3['pass'] = p3['nae_implied'] == 0 and p3['min_places'] >= 3 and p3['max_given'] <= 1 and p3['min_kept'] >= 2
    p4['pass'] = not p4['not_the_closing_top']
    for d in (p1, p2):
        d['fails'] = d['fails'][:20]
    res.update(P1=p1, P2=p2, P3=p3, P4=p4, transitions={f'{x} -> {y}': n for (x, y), n in sorted(trans.items())})
    return res


def ratio(c):
    return round(c[-1] / c[-2], 4) if len(c) >= 2 and c[-2] else None


def score_p(P):
    out = {}
    ok = True
    for name, r in sorted(P.items()):
        p, a = r['parity'], r['nae']
        row = {'parity': p['counts'], 'nae': a['counts'], 'parity_outcome': p['outcome'], 'nae_outcome': a['outcome'],
               'ratio_parity': ratio(p['counts']), 'ratio_nae': ratio(a['counts'])}
        if p['implied']:
            good, why = tail_ok(p, a, p['implied'][0][1])
        else:
            good, why = a['counts'] == p['counts'], 'counts differ'
        row['held'] = good
        ok &= good
        out[name] = row
    out['pass'] = ok
    return out


def table_graph(n, tab):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for (x, y), d in zip(itertools.combinations(range(n), 2), tab):
        G.add_edge(x, y, w=str(d))
    return G


def star_graph(stars):
    G = nx.Graph()
    for j, s in enumerate(stars):
        G.add_node(('j', j), kind='j')
        for b in s:
            G.add_node(('b', b), kind='b')
            G.add_edge(('j', j), ('b', b))
    return G


def join_graph(stars, parents):
    G = star_graph(stars)
    for i, ps in enumerate(parents):
        G.add_node(('n', i), kind='n')
        for j in ps:
            G.add_edge(('n', i), ('j', j))
    return G


NM = nx.algorithms.isomorphism.categorical_node_match('kind', None)
EM = nx.algorithms.isomorphism.categorical_edge_match('w', None)


def distinct(stages):
    """One representative stage per presentation (stars up to renaming)."""
    reps, by_hash = [], defaultdict(list)
    for sid, s in enumerate(stages):
        SG = star_graph(s['stars'])
        h = nx.weisfeiler_lehman_graph_hash(SG, node_attr='kind')
        if any(nx.is_isomorphic(SG, stages[i]['_sg'], node_match=NM) for i in by_hash[h]):
            continue
        s['_sg'] = SG
        by_hash[h].append(sid)
        reps.append(sid)
    return reps


def same_states(a, b, law, cap=20000):
    """Is there a renaming of a's distinctions, among the isomorphisms of their tables, that carries a's states onto b's?"""
    n = a['bits']
    sa = BL.states(n, a['stars'], law)
    sb = np.sort(BL.states(n, b['stars'], law))
    if len(sa) != len(sb):
        return False
    GM = nx.algorithms.isomorphism.GraphMatcher(table_graph(n, a[law]['table']), table_graph(n, b[law]['table']), edge_match=EM)
    for k, m in enumerate(GM.isomorphisms_iter()):
        if k >= cap:
            return None
        img = np.zeros(len(sa), dtype=np.int64)
        for x, y in m.items():
            img |= ((sa >> x) & 1) << y
        if np.array_equal(np.sort(img), sb):
            return True
    return False


def collisions(stages, reps, law):
    buckets = defaultdict(list)
    for i in reps:
        s = stages[i]
        s['_tg_' + law] = table_graph(s['bits'], s[law]['table'])
        buckets[(s['bits'], nx.weisfeiler_lehman_graph_hash(s['_tg_' + law], edge_attr='w'))].append(i)
    found = []
    for idx in buckets.values():
        for i, k in itertools.combinations(idx, 2):
            if nx.is_isomorphic(stages[i]['_tg_' + law], stages[k]['_tg_' + law], edge_match=EM):
                found.append((i, k))
    return found


def score_b(stages):
    reps = distinct(stages)
    R = [stages[i] for i in reps]
    tree = [s for s in R if s['cycle_rank'] == 0]
    cyc = [s for s in R if s['cycle_rank'] > 0]
    out = {'stages': len(stages), 'distinct_presentations': len(R), 'tree': len(tree), 'with_cycle': len(cyc)}
    out['B1'] = {'equal': sum(s['tables_equal'] for s in tree), 'n': len(tree)}
    out['B1']['pass'] = out['B1']['equal'] == len(tree) and len(tree) > 0
    out['B2'] = {'differ': sum(not s['tables_equal'] for s in cyc), 'n': len(cyc),
                 'pairs_nae_larger': sum(s['nae_larger'] for s in cyc), 'pairs_nae_smaller': sum(s['nae_smaller'] for s in cyc)}
    out['B2']['pass'] = out['B2']['differ'] > 0
    for law, b3, b5 in (('nae', 'B3', 'B5'), ('parity', 'B3c', 'B5c')):
        found = collisions(stages, reps, law)
        rows = []
        for i, k in found:
            a, b = stages[i], stages[k]
            ss = same_states(a, b, law)
            red = a[law]['redundant'] > 0 or b[law]['redundant'] > 0
            joins_same = nx.is_isomorphic(join_graph(a['stars'], a['next_parents']), join_graph(b['stars'], b['next_parents']),
                                          node_match=NM)
            rows.append({'a': [a['key'], a['round'], a['stars']], 'b': [b['key'], b['round'], b['stars']], 'same_states': ss,
                         'redundant': red, 'same_next_joins': joins_same})
        out[b3] = {'collisions': len(rows), 'same_states': sum(r['same_states'] is True for r in rows),
                   'undecided': sum(r['same_states'] is None for r in rows),
                   'with_redundant_junction': sum(r['redundant'] for r in rows), 'examples': rows[:12]}
        out[b3]['pass'] = all(r['same_states'] is True for r in rows)
        plain = [r for r in rows if not r['redundant']]
        out[b5] = {'collisions_without_redundancy': len(plain), 'different_next_joins': sum(not r['same_next_joins'] for r in plain),
                   'examples': [r for r in plain if not r['same_next_joins']][:6]}
        out[b5]['pass'] = all(r['same_next_joins'] for r in plain)
        if law == 'nae':
            out['B4'] = {'collisions': len(rows), 'with_redundant_junction': sum(r['redundant'] for r in rows),
                         'pass': all(r['redundant'] for r in rows)}
    out['reader_control'] = {law: {'exact': sum(s[law]['reader_exact'] for s in R), 'n': len(R)} for law in ('parity', 'nae')}
    for s in stages:
        for k in [x for x in s if x.startswith('_')]:
            del s[k]
    return out


def main():
    R = load_results(sys.argv[1])
    C, P, Bst, bad = [], {}, [], []
    for cid, r in R.items():
        if r.get('status') != 'ok':
            bad.append([cid, r.get('status')])
            continue
        res = r['result']
        if cid.startswith('C-'):
            C += res['arrangements']
        elif cid.startswith('P-'):
            P[cid[2:]] = res
        else:
            for a in res['arrangements']:
                for s in a['stages']:
                    Bst.append(dict(s, key=a['key']))
    out = {'cases_not_ok': bad, 'C': score_c(C), 'P5': score_p(P), 'B': score_b(Bst)}
    out['verdicts'] = {k: out['C'][k]['pass'] for k in ('P1', 'P2', 'P3', 'P4')}
    out['verdicts']['P5'] = out['P5']['pass']
    out['verdicts'].update({k: out['B'][k]['pass'] for k in ('B1', 'B2', 'B3', 'B3c', 'B4', 'B5', 'B5c')})
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out['verdicts']))


if __name__ == '__main__':
    main()
