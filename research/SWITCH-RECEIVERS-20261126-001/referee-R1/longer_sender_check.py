"""Give the seven shortened cap-five sender comparisons a bounded test at round 15."""
import argparse
import gzip
import json
import time
from pathlib import Path

from growth import grow

HERE = Path(__file__).resolve().parent
CAP = 22000


def reread(row, bound=CAP, through=15):
    sender = row['B']
    read = grow('g7:122@0', sender, 3, 'CAP-5', rounds=through, bound=bound)
    copied = [r.own_births for r in read[:row['rounds']]]
    assert copied == row['own births']
    return {'sender': sender, 'round_limit': through, 'knot_limit': bound, 'original_rounds': row['rounds'], 'extended_rounds': len(read),
            'last_knot_count': read[-1].knots, 'own_birth_counts': [r.own_births for r in read],
            'first_departure': next((i for i, r in enumerate(read, 1) if r.own_births != i+2), None)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true', help='time a case with the earliest original stop at round nine')
    args = parser.parse_args()
    with gzip.open(HERE.parent / 'senders_runs.jsonl.gz', 'rt') as stream:
        data = [json.loads(line) for line in stream]
    selected = sorted((r for r in data if r['law'] == 'CAP-5' and r['d'] == 3 and r['rounds'] < 15),
                      key=lambda r: (r['rounds'], r['B']))
    assert len(selected) == 7
    t0 = time.monotonic()
    out = {'round_limit': 15, 'knot_limit': CAP, 'rows': [reread(row) for row in (selected[:1] if args.pilot else selected)]}
    # An observed first departure settles a prediction about the *first* round.
    # The remaining sender gets a raised-bound check through the round first seen on the other six.
    unresolved = [r for r in out['rows'] if not r['first_departure'] and r['extended_rounds'] < 15]
    source = next(r for r in selected if r['B'] == 'source')
    extension = ([source] if args.pilot else [r for r in selected if any(x['sender'] == r['B'] for x in unresolved)])
    out['remaining_shortened_runs'] = [reread(r, bound=90000, through=13) for r in extension]
    out['elapsed_seconds'] = round(time.monotonic() - t0, 3)
    if not args.pilot:
        (HERE / 'longer_sender_check.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out))
