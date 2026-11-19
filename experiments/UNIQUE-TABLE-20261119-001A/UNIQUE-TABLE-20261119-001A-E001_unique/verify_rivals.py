"""Independent checks of every different-equation rival in realize.json: B1-B4 including no cut vertex but the outside one,
the two exact tables compared entry by entry, the equation spaces compared, and whether the rival is isomorphic to the truth as an
arrangement (incidence graphs with loose distinctions marked).  Run: .venv/bin/python -B verify_rivals.py -> verify_rivals.json"""
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import uniq as U  # noqa: E402
A = ROOT / 'artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'


def incidence(junctions):
    g = nx.Graph()
    own = U.R.owners(junctions)
    for j, s in enumerate(junctions):
        g.add_node(('j', j), kind='j')
        for b in s:
            g.add_node(('b', b), kind='loose' if len(own[b]) == 1 else 'shared')
            g.add_edge(('j', j), ('b', b))
    return g


def cut_vertex_ok(junctions):
    edges, nv = U.graph_of(junctions)
    o = nv - 1
    return all(v == o for v in U.cut_vertices(edges))


def main():
    data = json.loads((A / 'realize.json').read_text())
    rows = []
    for x in data['other_codes']:
        for ex in x['example']:
            truth = [frozenset(s) for s in x['truth']]
            rival = [frozenset(s) for s in ex]
            tt, tr = U.full_table(truth), U.full_table(rival)
            rc, _ = U.rank([U.word(s) for s in truth])
            rboth, _ = U.rank([U.word(s) for s in truth] + [U.word(s) for s in rival])
            rows.append({'case': x['case'], 'key': x['key'], 'round': x['round'], 'junctions': len(truth),
                         'truth': x['truth'], 'rival': ex,
                         'rival_legal_B1_B2': U.legal(rival, sorted(U.R.owners(truth))),
                         'rival_no_cut_vertex_but_outside': cut_vertex_ok(rival), 'truth_no_cut_vertex_but_outside': cut_vertex_ok(truth),
                         'tables_equal_entry_by_entry': tt == tr, 'entries': len(tt),
                         'equations_differ': rboth > rc,
                         'isomorphic_as_arrangements': nx.is_isomorphic(incidence(truth), incidence(rival),
                                                                         node_match=lambda a, b: a['kind'] == b['kind']),
                         'junctions_that_differ': [sorted(sorted(s) for s in set(truth) - set(rival)),
                                                   sorted(sorted(s) for s in set(rival) - set(truth))]})
    (A / 'verify_rivals.json').write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(json.dumps({k: r[k] for k in ('case', 'junctions', 'rival_legal_B1_B2', 'rival_no_cut_vertex_but_outside',
                                            'tables_equal_entry_by_entry', 'equations_differ', 'isomorphic_as_arrangements',
                                            'junctions_that_differ')}))


if __name__ == '__main__':
    main()
