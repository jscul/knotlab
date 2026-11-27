"""chain_check.py OUT.json: the pair costs of the frozen runs against the chain formula (tree_proof.md): the least change
flipping exactly two families' facts at round t is the shortest route between them in the complete graph on the
families with weights d + 2 + 2t.  A check after the frozen runs, on their recorded costs."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1] / "SELECTED-KNOTS-20261127-001"
tot = {'pair rows': 0, 'agree': 0, 'differ': [] , 'chain shorter than d + 2 + 2t': 0}
for s in ('census', 'heldout', 'sampled', 'built'):
    for l in open(HERE / ('frozen_%s.jsonl' % s)):
        r = json.loads(l)
        if 'distances' not in r: continue
        m = r['families']; D = {tuple(map(int, k.split('-'))): v for k, v in r['distances'].items()}
        for x in r['rounds']:
            if 'end' in x: continue
            t = x['round']; fails = {(i, j): w for i, j, d, w in x['SK1 failures']}
            dist = [[0 if a == b else D[(min(a, b), max(a, b))] + 2 + 2 * t for b in range(m)] for a in range(m)]
            for c in range(m):
                for a in range(m):
                    for b in range(m): dist[a][b] = min(dist[a][b], dist[a][c] + dist[c][b])
            for (i, j), d in D.items():
                measured = fails.get((i, j), d + 2 + 2 * t); tot['pair rows'] += 1
                if dist[i][j] < d + 2 + 2 * t: tot['chain shorter than d + 2 + 2t'] += 1
                if measured == dist[i][j]: tot['agree'] += 1
                else: tot['differ'].append([r['start'], t, i, j, measured, dist[i][j]])
json.dump(tot, open(sys.argv[1], 'w'), indent=1); print({k: (v if not isinstance(v, list) else len(v)) for k, v in tot.items()})
