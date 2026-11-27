"""tally_square.py: square_sample.jsonl.gz against preregistration.md, prediction 7 (one vote per start)."""
import json, gzip, collections
from pathlib import Path
rows = [json.loads(l) for l in gzip.open(Path(__file__).resolve().parent / 'square_sample.jsonl.gz', 'rt')]
for arm in ('ordinary', 'one_fewer', 'arity_floor'):
    R = [r for r in rows if r['arm'] == arm]
    print(json.dumps({'arm': arm, 'starts': len(R),
                      'pairs (two regions, or a union against a third)': sum(r['pairs'] for r in R),
                      'separated pairs': sum(r['separated pairs'] for r in R),
                      'pairs with e >= 1 (middle read for changes)': sum(r['pairs with e >= 1'] for r in R),
                      'pairs with e >= 2': sum(r['pairs with e >= 2'] for r in R),
                      'starts with a separated pair': sum(r['separated pairs'] > 0 for r in R),
                      'starts with a pair with e >= 1': sum(r['largest e, middle read for changes'] >= 1 for r in R),
                      'starts with a pair with e >= 2': sum(r['largest e, middle read for changes'] >= 2 for r in R),
                      'starts with e >= 1 and the middle unread': sum(r['largest e, middle unread'] >= 1 for r in R),
                      'rounds': dict(collections.Counter(r['rounds'] for r in R))}))
