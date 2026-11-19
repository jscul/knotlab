"""Post hoc reading of part B (after the frozen read-out): how many presentations take part in a collision under each law, and of
which kind.  python3 -B posthoc_b.py <runner out dir> <out.json>"""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('nae_merge', HERE / 'merge.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def main():
    R = M.load_results(sys.argv[1])
    st = []
    for cid, r in R.items():
        if cid.startswith('B-'):
            for a in r['result']['arrangements']:
                st += [dict(s, key=a['key']) for s in a['stages']]
    reps = M.distinct(st)
    out = {'distinct_presentations': len(reps)}
    for law in ('nae', 'parity'):
        found = M.collisions(st, reps, law)
        kinds = Counter()
        involved, joins_differ = set(), set()
        for i, k in found:
            a, b = st[i], st[k]
            ss = M.same_states(a, b, law)
            red = a[law]['redundant'] > 0 or b[law]['redundant'] > 0
            same_j = nx.is_isomorphic(M.join_graph(a['stars'], a['next_parents']), M.join_graph(b['stars'], b['next_parents']),
                                      node_match=M.NM)
            kinds[(('same states' if ss else 'different states' if ss is False else 'undecided'),
                   ('redundant junction' if red else 'no redundant junction'),
                   ('same next joins' if same_j else 'different next joins'))] += 1
            involved |= {i, k}
            if not same_j:
                joins_differ |= {i, k}
        out[law] = {'collisions': len(found), 'presentations_in_a_collision': len(involved),
                    'presentations_whose_table_misleads_the_next_joins': len(joins_differ),
                    'kinds': {' / '.join(k): v for k, v in sorted(kinds.items())},
                    'with_redundant_junction': sum(1 for i in reps if st[i][law]['redundant'] > 0)}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
