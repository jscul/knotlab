"""GROWN-PAIR-20261119-001A pairing: from the stage records of job.py, every pair of non-isomorphic arrangements with isomorphic
exact tables.  Run: .venv/bin/python -B pairs.py runs/grown-pair  -> pairs.json beside the artifacts.

- Arrangements are deduplicated by exact isomorphism of their incidence graphs (junctions, distinctions, loose marks); every
  provenance (start, round) is kept.
- Within a table-hash bucket, pairs of distinct arrangement classes are tested for exact table isomorphism (VF2 on the complete
  graph of distinctions, edges labelled by distance, nodes coloured by their sorted row of distances).
- States: they agree if some table isomorphism carries one arrangement's circuits (hence its equation space) onto the other's,
  decided as one isomorphism test of the table with the circuits attached as extra coloured vertices; renaming only, no value flips.
- Sanity: arrangement classes carrying two tables (impossible: the table is a function of the arrangement) are counted.
- Each pair is labelled start-start, start-grown or grown-grown (a start is round 0), and same-lineage when one arrangement's
  provenance includes the other's start; each grown-grown pair's next joins and growth (two rounds) are compared."""
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import job as J  # noqa: E402
from longrun import load_results  # noqa: E402
R, S, F, X = J.R, J.S, J.F, J.X
UNIQ = ROOT / 'experiments/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'


def incidence(stars):
    own = R.owners(stars)
    g = nx.Graph()
    for j, s in enumerate(stars):
        g.add_node(('j', j), k='j')
        for b in s:
            g.add_node(('b', b), k='loose' if len(own[b]) == 1 else 'shared')
            g.add_edge(('j', j), ('b', b))
    return g


def table_graph(stars, with_circuits=False):
    labels = sorted(R.owners(stars))
    table = X.exact_table(stars, len(labels))
    g = nx.Graph()
    for x in labels:
        row = tuple(sorted(table[tuple(sorted((x, y)))] for y in labels if y != x))
        g.add_node(('b', x), k=('b', row))
    for (a, b), d in table.items():
        g.add_edge(('b', a), ('b', b), d=d)
    if with_circuits:
        idx = {b: i for i, b in enumerate(labels)}
        code = set()
        for s in stars:
            w = sum(1 << idx[b] for b in s)
            code |= {x ^ w for x in code} | {w}
        circuits = []
        for w in sorted((w for w in code if w), key=lambda w: (w.bit_count(), w)):
            if not any((w & c) == c for c in circuits):
                circuits.append(w)
        for k, c in enumerate(circuits):
            g.add_node(('c', k), k=('c', c.bit_count()))
            for i, b in enumerate(labels):
                if c >> i & 1:
                    g.add_edge(('c', k), ('b', b), d='in')
    return g


def relabel(stars):
    labels = sorted({b for s in stars for b in s}, key=str)
    idx = {b: i for i, b in enumerate(labels)}
    return [frozenset(idx[b] for b in s) for s in stars]


def iso(g1, g2):
    gm = isomorphism.GraphMatcher(g1, g2, node_match=lambda a, b: a['k'] == b['k'],
                                  edge_match=lambda a, b: a.get('d') == b.get('d'))
    return gm.is_isomorphic()


def main(out_dir):
    recs = load_results(out_dir)
    stages = [st for c, r in sorted(recs.items()) if r['status'] == 'ok' for st in r['result']['stages']]
    out = {'stages': len(stages), 'cases': dict(Counter(r['status'] for r in recs.values()))}
    # arrangement classes (exact), with provenance
    by_ahash = defaultdict(list)
    for st in stages:
        by_ahash[st['arrangement_hash']].append(st)
    classes = []
    for h, sts in by_ahash.items():
        reps = []
        for st in sts:
            stars = [frozenset(s) for s in st['stars']]
            for rep in reps:
                if iso(rep['g'], incidence(stars)):
                    rep['prov'].append((st['index'], st['round']))
                    rep['tables'].add(st['table_hash'])
                    break
            else:
                reps.append({'g': incidence(stars), 'stars': stars, 'rec': st, 'prov': [(st['index'], st['round'])],
                             'tables': {st['table_hash']}})
        classes.extend(reps)
    out['arrangement_classes'] = len(classes)
    out['sanity_classes_with_two_tables'] = sum(1 for c in classes if len(c['tables']) > 1)
    by_thash = defaultdict(list)
    for c in classes:
        by_thash[c['rec']['table_hash']].append(c)
    out['table_buckets_with_two_or_more_classes'] = sum(1 for v in by_thash.values() if len(v) > 1)
    pairs = []
    for h, cl in by_thash.items():
        if len(cl) < 2:
            continue
        tg = [table_graph(c['stars']) for c in cl]
        for i, k in combinations(range(len(cl)), 2):
            a, b = cl[i], cl[k]
            if a['rec']['distinctions'] != b['rec']['distinctions'] or not iso(tg[i], tg[k]):
                continue
            states_agree = iso(table_graph(a['stars'], True), table_graph(b['stars'], True))
            grown_a = any(r > 0 for _, r in a['prov'])
            grown_b = any(r > 0 for _, r in b['prov'])
            kind = 'grown-grown' if grown_a and grown_b else ('start-grown' if grown_a or grown_b else 'start-start')
            starts_a = {i for i, _ in a['prov']}
            starts_b = {i for i, _ in b['prov']}
            pairs.append({'kind': kind, 'same_lineage': bool(starts_a & starts_b), 'states_agree': states_agree,
                          'junctions': [a['rec']['junctions'], b['rec']['junctions']],
                          'distinctions': a['rec']['distinctions'],
                          'meet_once': [a['rec']['max_shared'] < 2, b['rec']['max_shared'] < 2],
                          'a': {'stars': [sorted(s) for s in a['stars']], 'provenance': a['prov'][:5], 'key': a['rec']['key']},
                          'b': {'stars': [sorted(s) for s in b['stars']], 'provenance': b['prov'][:5], 'key': b['rec']['key']}})
    out['pairs'] = len(pairs)
    out['pairs_by_kind'] = dict(Counter(p['kind'] for p in pairs))
    out['pairs_by_kind_and_states'] = dict(Counter(f"{p['kind']}:{'same' if p['states_agree'] else 'other'} states" for p in pairs))
    out['pairs_by_size'] = dict(Counter(f"{p['distinctions']} distinctions" for p in pairs))
    out['grown_grown_meet_once_both'] = sum(1 for p in pairs if p['kind'] == 'grown-grown' and all(p['meet_once']))
    # growth of grown-grown pairs
    sys.path.insert(0, str(UNIQ))
    import importlib.util
    spec = importlib.util.spec_from_file_location('uniq_pairs', UNIQ / 'pairs.py')
    UP = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = UP
    spec.loader.exec_module(UP)
    for p in pairs:
        if p['kind'] != 'grown-grown':
            continue
        ga, ma = UP.grow([frozenset(s) for s in p['a']['stars']], 2)
        gb, mb = UP.grow([frozenset(s) for s in p['b']['stars']], 2)
        p['growth'] = {'menus_a': [m if m == 'stall' else len(m) for m in ma], 'menus_b': [m if m == 'stall' else len(m) for m in mb],
                       'sizes_a': sorted(Counter(map(len, ga)).items()), 'sizes_b': sorted(Counter(map(len, gb)).items()),
                       'grown_tables_isomorphic': (len(ga) == len(gb) and iso(table_graph(relabel(ga)), table_graph(relabel(gb))))}
    dest = ROOT / 'artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'pairs.json').write_text(json.dumps({**out, 'pair_list': pairs}, indent=1, default=list))
    print(json.dumps(out, indent=1, default=list))


if __name__ == '__main__':
    main(sys.argv[1])
