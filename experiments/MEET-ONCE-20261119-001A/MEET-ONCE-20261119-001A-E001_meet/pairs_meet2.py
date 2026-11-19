"""MEET-ONCE-20261119-001A pairing, Amendment 1.  Run: .venv/bin/python -B pairs_meet2.py runs/meet-once -> meet_pairs2.json.

The frozen pairing (pairs_meet.py) escalates every candidate group to the full table, and a full table at 50 to 90 distinctions
takes hours (52 distinctions: 1.6 s pooled at 12, 238 s at 20).  The same verdicts, computed in another order:
- arrangement classes and candidate groups (tables pooled at H = 8 isomorphic) as in pairs_meet.py;
- states first.  Every bijection carrying one equation space onto the other keeps the full table, hence the pooled one, so:
  - a junction-graph isomorphism (junctions and the outside vertex o as plain vertices, distinctions as edges) carries the
    equation spaces: same states;
  - otherwise, isomorphisms of the pooled tables are enumerated on twin classes (distinctions held by the same junctions are
    parallel edges; any carrier maps such classes onto such classes, and permutations inside a class keep the equation space), up
    to 5,000, each tested by rank: same, other (all enumerated, none), or undecided (cap);
- classes with the same states have isomorphic full tables: same-states collisions, with no full table computed;
- classes in one candidate group with other states: their tables escalated at H = 12, 16, ... and the full table, exactly as in
  pairs_meet.py, under a hard time limit per group (an alarm); isomorphic at the full table is an other-states collision, a split is
  none, the limit is undecided."""
import json
import signal
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pairs_meet as PM  # noqa: E402
import uniq_rank as UR  # noqa: E402
J, R = PM.J, PM.R
LIMIT = 1800
CAP = 5000


class Late(Exception):
    pass


def _late(signum, frame):
    raise Late()


def junction_graph(stars):
    own = R.owners(stars)
    g = nx.Graph()
    g.add_nodes_from(range(len(stars)))
    for b, js in own.items():
        u, v = (js[0], 'o') if len(js) == 1 else tuple(js)
        if g.has_edge(u, v):
            g[u][v]['m'] += 1
        else:
            g.add_edge(u, v, m=1)
    return g


def graph_iso(a, b):
    ga, gb = junction_graph(a), junction_graph(b)
    if ga.number_of_nodes() != gb.number_of_nodes() or ga.number_of_edges() != gb.number_of_edges():
        return False
    return isomorphism.GraphMatcher(ga, gb, edge_match=lambda x, y: x['m'] == y['m']).is_isomorphic()


def quotient(stars, table):
    """Twin classes (distinctions with the same holders) as nodes labelled by size and inner reading; pooled readings between."""
    own = R.owners(stars)
    cls = defaultdict(list)
    for b in sorted(own):
        cls[tuple(sorted(own[b]))].append(b)
    keys = sorted(cls)
    rep = {k: cls[k][0] for k in keys}

    def t(x, y):
        return table[(x, y)] if (x, y) in table else table[(y, x)]
    g = nx.Graph()
    for k in keys:
        inner = str(t(cls[k][0], cls[k][1])) if len(cls[k]) > 1 else '-'
        g.add_node(k, s=(len(cls[k]), inner))
    for i, k in enumerate(keys):
        for k2 in keys[i + 1:]:
            g.add_edge(k, k2, d=str(t(rep[k], rep[k2])))
    hs = nx.weisfeiler_lehman_subgraph_hashes(g, node_attr='s', edge_attr='d', iterations=3)
    for k in keys:
        g.nodes[k]['k'] = (g.nodes[k]['s'], tuple(hs[k]))
    return g, cls


def states_pooled(a, b, ta, tb):
    """'same', 'other' or 'undecided', and the number of quotient isomorphisms tried."""
    if graph_iso(a, b):
        return 'same', 0
    ga, ca = quotient(a, ta)
    gb, cb = quotient(b, tb)
    if sorted(d['k'] for _, d in ga.nodes(data=True)) != sorted(d['k'] for _, d in gb.nodes(data=True)):
        return 'other', 0
    lb = sorted(R.owners(b))
    idxb = {x: i for i, x in enumerate(lb)}
    wb = [sum(1 << idxb[x] for x in s) for s in b]
    rank_b, _ = UR.rank(wb)
    m = isomorphism.GraphMatcher(ga, gb, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
    count = 0
    for phi in m.isomorphisms_iter():
        count += 1
        lift = {}
        for k, members in ca.items():
            for x, y in zip(members, cb[phi[k]]):
                lift[x] = y
        mapped = [sum(1 << idxb[lift[x]] for x in s) for s in a]
        r_all, _ = UR.rank(wb + mapped)
        if r_all == rank_b:
            r_m, _ = UR.rank(mapped)
            if r_m == rank_b:
                return 'same', count
        if count >= CAP:
            return 'undecided', count
    return 'other', count


def examine(cands):
    """cands: classes whose pooled-8 tables are isomorphic."""
    signal.signal(signal.SIGALRM, _late)
    signal.alarm(LIMIT)
    t0 = time.time()
    N = cands[0]['distinctions']
    res = {'classes': len(cands), 'distinctions': N, 'junctions': [c['junctions'] for c in cands]}
    try:
        stars = [[frozenset(s) for s in c['stars']] for c in cands]
        tabs = [PM.table_at(s, J.HPOOL)[0] for s in stars]
        # states groups: one representative each
        sg, tests = [], []
        for i in range(len(cands)):
            for g in sg:
                v, n = states_pooled(stars[g[0]], stars[i], tabs[g[0]], tabs[i])
                tests.append((g[0], i, v, n))
                if v == 'same':
                    g.append(i)
                    break
                if v == 'undecided':
                    res['states_undecided'] = True
            else:
                sg.append([i])
        res['state_groups'] = [[cands[i]['junctions'] for i in g] for g in sg]
        res['same_states_collision'] = any(len(g) >= 2 for g in sg)
        res['tests'] = tests
        res['members'] = [{'stars': c['stars'], 'prov': c['prov'][:3]} for c in cands[:4]]
        if len(sg) >= 2:
            reps = [cands[g[0]] for g in sg]
            groups = [reps]
            for H in list(range(12, N, 4)) + [N]:
                nxt = []
                for g in groups:
                    t = {id(c): PM.table_at([frozenset(s) for s in c['stars']], H) for c in g}
                    for sub in PM.group(g, lambda c: PM.coloured(*t[id(c)])):
                        if len(sub) >= 2:
                            nxt.append(sub)
                groups = nxt
                res['escalated_to_H'] = H
                if not groups:
                    break
            res['other_states_collision'] = len(groups) > 0
    except Late:
        res['undecided_late'] = True
    finally:
        signal.alarm(0)
    res['seconds'] = round(time.time() - t0, 1)
    return res


def main(out_dir):
    recs = PM.load_results(out_dir)
    stages = [st for c, r in sorted(recs.items()) if r['status'] == 'ok' for st in r['result']['stages']]
    by_a = defaultdict(list)
    for st in stages:
        by_a[st['arrangement_hash']].append(st)
    classes = []
    for h, sts in by_a.items():
        for members in PM.group(sts, lambda st: PM._inc(st)):
            st = members[0]
            classes.append({'stars': st['stars'], 'prov': [(m['index'], m['round']) for m in members],
                            'ph': st['pooled_table_hash'], 'distinctions': st['distinctions'], 'junctions': st['junctions']})
    out = {'stages': len(stages), 'arrangement_classes': len(classes),
           'by_junctions': dict(sorted(Counter(st['junctions'] for st in stages).items()))}
    buckets = defaultdict(list)
    for c in classes:
        buckets[(c['ph'], c['distinctions'])].append(c)
    work = []
    for v in buckets.values():
        if len(v) < 2:
            continue
        tabs = {id(c): PM.table_at([frozenset(s) for s in c['stars']], J.HPOOL) for c in v}
        for sub in PM.group(v, lambda c: PM.coloured(*tabs[id(c)])):
            if len(sub) >= 2:
                work.append(sub)
    out['candidate_groups_pooled_8'] = len(work)
    with Pool(8) as pool:
        res = list(pool.imap_unordered(examine, work))
    res.sort(key=lambda r: (r['distinctions'], r['junctions']))
    out['groups'] = res
    out['summary'] = {
        'candidate_groups': len(res),
        'same_states_collision_groups': sum(1 for r in res if r.get('same_states_collision')),
        'groups_with_other_state_groups': sum(1 for r in res if len(r.get('state_groups', [])) >= 2),
        'other_states_collisions': sum(1 for r in res if r.get('other_states_collision') and not r.get('states_undecided')),
        'full_table_collisions_with_states_undecided': sum(1 for r in res if r.get('other_states_collision') and r.get('states_undecided')),
        'other_states_split_by_escalation': sum(1 for r in res if r.get('other_states_collision') is False),
        'escalation_split_at_H': dict(Counter(r['escalated_to_H'] for r in res if r.get('other_states_collision') is False)),
        'states_undecided_groups': sum(1 for r in res if r.get('states_undecided')),
        'late_groups': sum(1 for r in res if r.get('undecided_late')),
        'same_states_by_junctions': dict(sorted(Counter(min(r['junctions']) for r in res if r.get('same_states_collision')).items())),
    }
    dest = ROOT / 'artifacts/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'meet_pairs2.json').write_text(json.dumps(out, indent=1, default=list))
    print(json.dumps({k: v for k, v in out.items() if k != 'groups'}, indent=1, default=list))


if __name__ == '__main__':
    main(sys.argv[1])
