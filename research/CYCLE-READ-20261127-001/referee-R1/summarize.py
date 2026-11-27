"""Tabulate separately by sample and law; keep the rank and growth cutoffs visible."""
from collections import Counter
import json
from pathlib import Path
import sys


def summarize(rows):
    cut = Counter()
    table = Counter()
    anomalies = []
    for x in rows:
        if 'cut' in x:
            cut[x['cut']] += 1
            continue
        has_chain = any(p['chains'] for p in x['pieces'])
        group = ('cycle' if x['cyclic'] else 'no cycle',
                 'chains' if has_chain else 'no chains',
                 'twins' if x['twin'] is not None else 'no flag')
        for law in ('nae', 'parity'):
            y = x[law]
            if 'first' not in y:
                table[group + (law, y['status'])] += 1
                continue
            first = [v for v in y['first'].values() if v is not None]
            t = min(first, default=None)
            if t is None and x['twin'] is not None and x["twin"] - 1 > y["rounds"]:
                label = 'stopped before twin'
            elif t is None and x['twin'] is None:
                label = 'agree'
            elif t is not None and x["twin"] is not None and t == x["twin"] - 1:
                label = 'differ at twin birth round'
            else:
                label = 'exception'
                anomalies.append([x['index'], law, t, x['twin']])
            table[group + (law, label)] += 1
    return {'cuts':dict(cut), 'table':{' / '.join(k): n for k, n in sorted(table.items())},
            'exceptions':anomalies}


if __name__ == '__main__':
    rows = [json.loads(line) for file in sys.argv[1:] for line in Path(file).read_text().splitlines()]
    print(json.dumps(summarize(rows), indent=2))
