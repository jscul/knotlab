"""MEET-ONCE-20261119-001A pairing.  Run: .venv/bin/python -B pairs_meet.py runs/meet-once -> meet_pairs.json beside the artifacts.
- arrangement classes by exact incidence isomorphism (provenances kept);
- candidate groups: classes whose tables pooled at H = 8 are isomorphic (VF2 with Weisfeiler-Leman node colours);
- each candidate group regrouped with the tables pooled at H = 12, 16, 20, ... and finally the full table (H = number of
  distinctions); a group surviving at the full table is a collision (non-isomorphic arrangements, isomorphic full tables);
- states: some isomorphism of the full tables carrying one equation space onto the other (enumerated up to 5,000 isomorphisms;
  each tested by rank); 'same', 'other' (all enumerated, none), or 'undecided' (cap reached).
A computation over the time limit leaves its group 'undecided'."""
import json
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
sys.path.insert(0, str(ROOT / 'scripts'))
import job as J  # noqa: E402
from longrun import load_results  # noqa: E402
R, X = J.R, J.X
LIMIT = 1800


def incidence(stars):
    own = R.owners(stars)
    g = nx.Graph()
    for j, s in enumerate(stars):
        g.add_node(('j', j), k='j')
        for b in s:
            g.add_node(('b', b), k='loose' if len(own[b]) == 1 else 'shared')
            g.add_edge(('j', j), ('b', b))
    return g


def coloured(table, labels):
    g = nx.Graph()
    g.add_nodes_from(labels)
    for (a, b), d in table.items():
        g.add_edge(a, b, d=str(d))
    hs = nx.weisfeiler_lehman_subgraph_hashes(g, edge_attr='d', iterations=3)
    for v in g.nodes:
        g.nodes[v]['k'] = tuple(hs[v])
    return g


def matcher(g1, g2):
    return isomorphism.GraphMatcher(g1, g2, node_match=lambda a, b: a['k'] == b['k'], edge_match=lambda a, b: a['d'] == b['d'])


def iso(g1, g2):
    if sorted(d['k'] for _, d in g1.nodes(data=True)) != sorted(d['k'] for _, d in g2.nodes(data=True)):
        return False
    return matcher(g1, g2).is_isomorphic()


def group(items, make):
    groups = []
    for it in items:
        g = make(it)
        for grp in groups:
            if iso(grp[0], g):
                grp[1].append(it)
                break
        else:
            groups.append((g, [it]))
    return [m for _, m in groups]


def table_at(stars, H):
    labels = sorted(R.owners(stars))
    return X.exact_table(stars, H), labels


def code_words(stars, labels):
    idx = {b: i for i, b in enumerate(labels)}
    return [sum(1 << idx[b] for b in s) for s in stars], idx


def states(a, b, full_a, full_b):
    """Some isomorphism of the full tables carrying a's equation space onto b's?"""
    ta, la = full_a
    tb, lb = full_b
    ga, gb = coloured(ta, la), coloured(tb, lb)
    wb, idxb = code_words(b, lb)
    rb = J.R.__dict__  # noqa: F841
    import uniq_rank as UR  # noqa: E402
    rank_b, _ = UR.rank(wb)
    count = 0
    for phi in matcher(ga, gb).isomorphisms_iter():
        count += 1
        mapped = [sum(1 << idxb[phi[x]] for x in s) for s in a]
        r_all, _ = UR.rank(wb + mapped)
        if r_all == rank_b:
            r_m, _ = UR.rank(mapped)
            if r_m == rank_b:
                return 'same', count
        if count >= 5000:
            return 'undecided', count
    return 'other', count


def examine(cands):
    """cands: classes whose pooled-8 tables are isomorphic.  Escalate H; return collision groups with their states."""
    t0 = time.time()
    groups = [cands]
    N = cands[0]['distinctions']
    for H in list(range(12, N, 4)) + [N]:
        nxt = []
        for g in groups:
            tabs = {id(c): table_at([frozenset(s) for s in c['stars']], H) for c in g}
            for sub in group(g, lambda c: coloured(*tabs[id(c)])):
                if len(sub) >= 2:
                    nxt.append(sub)
            if time.time() - t0 > LIMIT:
                return [{'undecided_at_H': H, 'classes': len(g), 'distinctions': N}]
        groups = nxt
        if not groups:
            return []
    out = []
    for g in groups:
        fulls = [table_at([frozenset(s) for s in c['stars']], N) for c in g]
        verdicts = []
        for k in range(1, len(g)):
            verdicts.append(states([frozenset(s) for s in g[0]['stars']], [frozenset(s) for s in g[k]['stars']], fulls[0], fulls[k]))
        out.append({'classes': len(g), 'distinctions': N, 'junctions': [c['junctions'] for c in g],
                    'states_vs_first': verdicts, 'members': [{'stars': c['stars'], 'prov': c['prov'][:3]} for c in g[:4]]})
    return out


def main(out_dir):
    recs = load_results(out_dir)
    stages = [st for c, r in sorted(recs.items()) if r['status'] == 'ok' for st in r['result']['stages']]
    by_a = defaultdict(list)
    for st in stages:
        by_a[st['arrangement_hash']].append(st)
    classes = []
    for h, sts in by_a.items():
        for members in group(sts, lambda st: _inc(st)):
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
        tabs = {id(c): table_at([frozenset(s) for s in c['stars']], J.HPOOL) for c in v}
        for sub in group(v, lambda c: coloured(*tabs[id(c)])):
            if len(sub) >= 2:
                work.append(sub)
    out['candidate_groups_pooled_8'] = len(work)
    with Pool(8) as pool:
        res = [g for r in pool.imap_unordered(examine, work) for g in r]
    out['collision_groups'] = [g for g in res if 'states_vs_first' in g]
    out['undecided_groups'] = [g for g in res if 'undecided_at_H' in g]
    out['summary'] = {'collisions': len(out['collision_groups']),
                      'collision_states': dict(Counter(v for g in out['collision_groups'] for v, _ in g['states_vs_first'])),
                      'undecided': len(out['undecided_groups'])}
    dest = ROOT / 'artifacts/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'meet_pairs.json').write_text(json.dumps(out, indent=1, default=list))
    print(json.dumps({k: v for k, v in out.items() if k not in ('collision_groups', 'undecided_groups')}, indent=1, default=list))


def _inc(st):
    return incidence([frozenset(s) for s in st['stars']])


if __name__ == '__main__':
    main(sys.argv[1])
