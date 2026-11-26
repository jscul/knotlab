"""Test the larger-cap secondary observation with the 48 earlier sender entries."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import time

from growth import grow, mutual_three, start

HERE = Path(__file__).resolve().parent
RAISED_BOUND = 40000


def compare(sender, run, stub):
    first = next((i for i, (subject, reference) in enumerate(zip(run, stub), 1)
                  if subject.own_signature != reference.own_signature), None)
    return {'sender': sender, 'through': min(len(run), len(stub)), 'first': first}


def counts(rows, target):
    summary = Counter()
    for row in rows:
        if row['first'] == target:
            outcome = 'at target'
        elif row['first'] is not None:
            outcome = 'earlier'
        elif row['through'] < target:
            outcome = 'shortened'
        else:
            outcome = 'equal'
        summary[str(row['site_loose_before_meeting']), outcome] += 1
    return [{'site_loose': stock, 'result': outcome, 'entries': number}
            for (stock, outcome), number in sorted(summary.items())]


def read(site_loose, d, senders):
    # The study recorded these rounds on the original five-sender panel.
    target = 3 * d + 1 if site_loose == 3 else 3 * d
    cap = site_loose + 3
    receiver = mutual_three(site_loose)
    law = f'CAP-{cap}'
    stub = grow(receiver, 'stub', d, law, rounds=target)
    rows = []
    extended = []
    long_stub = None
    for sender in senders:
        trace = grow(receiver, sender, d, law, rounds=target)
        row = compare(sender, trace, stub)
        source = start(sender)
        row['site_loose_before_meeting'] = source.loose[source.site] if source.stars else None
        rows.append(row)
        if row['through'] < target and row['first'] is None:
            if long_stub is None:
                long_stub = grow(receiver, 'stub', d, law, rounds=target, bound=RAISED_BOUND)
            longer = grow(receiver, sender, d, law, rounds=target, bound=RAISED_BOUND)
            extended.append(compare(sender, longer, long_stub))
    update = {row['sender']: row for row in extended}
    final = [row | update.get(row['sender'], {}) for row in rows]
    return {
        'receiver_site_loose': site_loose, 'cap': cap, 'd': d, 'target': target,
        'rows': rows, 'original_knot_limit': 3000, 'counts': counts(rows, target),
        'raised_knot_limit': RAISED_BOUND, 'raised_bound_comparisons': extended,
        'counts_after_extension': counts(final, target),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    with gzip.open(HERE.parent / 'senders_runs.jsonl.gz', 'rt') as archive:
        senders = sorted({json.loads(line)['B'] for line in archive})
    chosen = ['g1:3@0', 'g3:33@0', 'source'] if args.pilot else senders
    before = time.monotonic()
    result = [read(a, d, chosen) for a in (3, 4, 5) for d in (2, 3)]
    elapsed = time.monotonic() - before
    if not args.pilot:
        output = {'seconds': elapsed, 'cells': result}
        (HERE / 'secondary_rule.json').write_text(json.dumps(output, indent=2) + '\n')
    for cell in result:
        print(cell['cap'], cell['d'], cell['counts_after_extension'])
    print('seconds', round(elapsed, 3))
