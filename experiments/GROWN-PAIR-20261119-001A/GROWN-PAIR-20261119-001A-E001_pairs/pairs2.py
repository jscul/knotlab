"""GROWN-PAIR-20261119-001A pairing, version 2 (Amendment 1: pairs.py ran out of its 50-minute limit comparing every two classes in
a bucket).  Same definitions, organised by groups instead of pairs:
- arrangement classes: stages with equal arrangement hash, split by exact incidence isomorphism (VF2), provenances kept;
- table groups: within a table-hash bucket, classes whose exact tables are isomorphic (VF2 against one representative per group,
  nodes coloured by Weisfeiler-Leman subgraph hashes of the table, an isomorphism invariant);
- within a table group, state groups: classes for which some table isomorphism carries one equation space onto the other (the table
  with its circuits attached, the same way);
- a class is grown if one of its provenances has round >= 1, a start otherwise.
Reported: table groups holding two or more arrangement classes, by kind (grown-grown when at least two of its classes are grown),
by size, whether all its grown classes meet once, and how many state groups its grown classes form; for each grown-grown table group,
the census's own next stages of its grown classes (round + 1 from the same start), compared by table hash.
Run: .venv/bin/python -B pairs2.py runs/grown-pair  -> pairs2.json beside the artifacts."""
import json
import sys
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


def incidence(stars):
    own = R.owners(stars)
    g = nx.Graph()
    for j, s in enumerate(stars):
        g.add_node(('j', j), k='j')
        for b in s:
            g.add_node(('b', b), k='loose' if len(own[b]) == 1 else 'shared')
            g.add_edge(('j', j), ('b', b))
    return g


def coloured_table(stars, with_circuits=False):
    labels = sorted(R.owners(stars))
    table = X.exact_table(stars, len(labels))
    g = nx.Graph()
    g.add_nodes_from(('b', x) for x in labels)
    for (a, b), d in table.items():
        g.add_edge(('b', a), ('b', b), d=str(d))
    if with_circuits:
        idx = {b: i for i, b in enumerate(labels)}
        code = {0}
        for s in stars:
            w = sum(1 << idx[b] for b in s)
            code |= {x ^ w for x in code}
        circuits = []
        for w in sorted((w for w in code if w), key=lambda w: (w.bit_count(), w)):
            if not any((w & c) == c for c in circuits):
                circuits.append(w)
        for k, c in enumerate(circuits):
            g.add_node(('c', k))
            for i, b in enumerate(labels):
                if c >> i & 1:
                    g.add_edge(('c', k), ('b', b), d='in')
    hashes = nx.weisfeiler_lehman_subgraph_hashes(g, edge_attr='d', iterations=3)
    for v in g.nodes:
        g.nodes[v]['k'] = (v[0], tuple(hashes[v]))
    return g


def iso(g1, g2):
    if sorted(d['k'] for _, d in g1.nodes(data=True)) != sorted(d['k'] for _, d in g2.nodes(data=True)):
        return False
    gm = isomorphism.GraphMatcher(g1, g2, node_match=lambda a, b: a['k'] == b['k'],
                                  edge_match=lambda a, b: a.get('d') == b.get('d'))
    return gm.is_isomorphic()


def group(items, make):
    """Partition items by isomorphism of make(item), comparing each with one representative per group."""
    groups = []
    for it in items:
        g = make(it)
        for grp in groups:
            if iso(grp[0], g):
                grp[1].append(it)
                break
        else:
            groups.append((g, [it]))
    return [members for _, members in groups]


def process_bucket(classes):
    """classes: list of dicts with stars, prov, meet_once.  Returns table groups with two or more classes."""
    out = []
    for tg in group(classes, lambda c: coloured_table([frozenset(s) for s in c['stars']])):
        if len(tg) < 2:
            continue
        grown = [c for c in tg if any(r > 0 for _, r in c['prov'])]
        state_groups = group(grown, lambda c: coloured_table([frozenset(s) for s in c['stars']], True)) if len(grown) >= 2 else []
        out.append({'classes': len(tg), 'grown_classes': len(grown), 'distinctions': tg[0]['distinctions'],
                    'junctions': sorted(c['junctions'] for c in tg), 'grown_meet_once': [c['meet_once'] for c in grown],
                    'grown_state_groups': len(state_groups), 'grown_state_group_sizes': sorted(len(s) for s in state_groups),
                    'grown': [{'stars': c['stars'], 'prov': c['prov'][:4]} for c in grown[:6]]})
    return out


def main(out_dir):
    recs = load_results(out_dir)
    stages = [st for c, r in sorted(recs.items()) if r['status'] == 'ok' for st in r['result']['stages']]
    by_prov = {(st['index'], st['round']): st for st in stages}
    by_ahash = defaultdict(list)
    for st in stages:
        by_ahash[st['arrangement_hash']].append(st)
    classes = []
    for h, sts in by_ahash.items():
        for members in group(sts, lambda st: _inc(st)):
            st = members[0]
            classes.append({'stars': st['stars'], 'prov': [(m['index'], m['round']) for m in members],
                            'table_hashes': sorted({m['table_hash'] for m in members}), 'distinctions': st['distinctions'],
                            'junctions': st['junctions'], 'meet_once': st['max_shared'] < 2})
    out = {'stages': len(stages), 'arrangement_classes': len(classes),
           'G_classes_with_two_tables': sum(1 for c in classes if len(c['table_hashes']) > 1)}
    buckets = defaultdict(list)
    for c in classes:
        buckets[c['table_hashes'][0]].append(c)
    work = [v for v in buckets.values() if len(v) >= 2]
    out['table_hash_buckets_with_two_or_more_classes'] = len(work)
    with Pool(10) as pool:
        groups = [g for res in pool.imap_unordered(process_bucket, work, chunksize=4) for g in res]
    out['table_groups_with_two_or_more_classes'] = len(groups)
    out['classes_in_such_groups'] = sum(g['classes'] for g in groups)
    gg = [g for g in groups if g['grown_classes'] >= 2]
    out['grown_grown_groups'] = len(gg)
    out['grown_grown_groups_all_meet_once'] = sum(1 for g in gg if all(g['grown_meet_once']))
    out['grown_grown_groups_with_two_state_groups'] = sum(1 for g in gg if g['grown_state_groups'] >= 2)
    out['grown_grown_groups_with_two_state_groups_all_meet_once'] = sum(1 for g in gg if g['grown_state_groups'] >= 2
                                                                        and all(g['grown_meet_once']))
    out['groups_by_distinctions'] = dict(sorted(Counter(g['distinctions'] for g in groups).items()))
    out['grown_grown_by_distinctions'] = dict(sorted(Counter(g['distinctions'] for g in gg).items()))
    # the census's own continuation of grown classes in grown-grown groups with other states
    cont = Counter()
    examples = []
    for g in gg:
        if g['grown_state_groups'] < 2:
            continue
        nxt = []
        for c in g['grown']:
            i, r = next(((i, r) for i, r in c['prov'] if r > 0), c['prov'][0])
            n = by_prov.get((i, r + 1))
            nxt.append(n['table_hash'] if n else None)
        known = [h for h in nxt if h]
        cont['next_tables_all_equal' if len(known) == len(nxt) and len(set(known)) == 1 else
             ('next_tables_differ' if len(set(known)) > 1 else 'next_stage_missing_or_past_cap')] += 1
        if len(examples) < 6:
            examples.append({'distinctions': g['distinctions'], 'grown': g['grown'][:2], 'next_table_hashes': nxt[:2],
                             'meet_once': g['grown_meet_once'][:2]})
    out['other_state_grown_groups_next_stage'] = dict(cont)
    dest = ROOT / 'artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'pairs2.json').write_text(json.dumps({**out, 'examples': examples, 'groups': groups[:200]}, indent=1, default=list))
    print(json.dumps({**out, 'examples': examples}, indent=1, default=list))


def _inc(st):
    return incidence([frozenset(s) for s in st['stars']])


if __name__ == '__main__':
    main(sys.argv[1])
