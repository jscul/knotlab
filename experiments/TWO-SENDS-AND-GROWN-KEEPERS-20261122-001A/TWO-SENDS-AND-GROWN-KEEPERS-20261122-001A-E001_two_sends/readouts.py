"""Decoding support with one weight per enrolled sender alternative, before counting orders."""
from collections import defaultdict
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def analyze():
    with gzip.open(OUT / 'sends.json.gz', 'rt') as f:
        raw = json.load(f)
    units = defaultdict(list)
    for cell in raw['all_physical_orders']:
        units[cell['law'], cell['condition'], cell['naming'], cell['reversed_bank']].append(cell)
    output = []
    for (law, mode, naming, reversed_bank), alternatives in sorted(units.items()):
        assert sorted(x['offer'] for x in alternatives) == [1, 2]
        for i, receiver in enumerate(('c8', 'u8')):
            for read in ('terminal_receipt_bank', 'retained_memory','whole_local_history'):
                support = defaultdict(list)
                for row in alternatives:
                    history = row['receiver_transcripts'][i]
                    symbol = {'terminal_receipt_bank': history[-1][:3], 'retained_memory': history[-1][3:],
                              'whole_local_history': '|'.join(history)}[read]
                    support[symbol].append(row['offer'])
                # Each offered choice has precisely one symbol in its cell across every legal order.
                identifiable = sum(len(x) for x in support.values() if len(x) == 1)
                output.append({'law': law,'condition': mode,'naming': naming,'reversed_bank': reversed_bank,
                               'receiver': receiver,'read': read,'offered': 2,'identified': identifiable,
                               'ambiguous': 2 - identifiable,'best_correct_equal_choice_weight': len(support),
                               'symbol_to_sender_offers': {k: sorted(v) for k, v in support.items()}})
    (OUT / 'readouts.json').write_text(json.dumps({'weighting':'one per enrolled positive source offer within cell',
                                                   'support':output}, separators=(',',':'), sort_keys=True) + '\n')
    print(f'{len(units)} paired settings, {len(output)} complete support tables')


if __name__ == '__main__':
    analyze()
