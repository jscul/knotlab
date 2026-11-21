"""Compare preserved six-rule predictions with the earlier benchmark tables."""

from argparse import ArgumentParser
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path


def compare(prediction_path, archive_path):
    prediction_bytes = prediction_path.read_bytes()
    receipt = loads(prediction_path.with_name('prediction_receipt.json').read_text())
    assert sha256(prediction_bytes).hexdigest() == receipt['prediction_sha256']
    predicted = loads(prediction_bytes)
    archive_bytes = archive_path.read_bytes()
    archive = loads(archive_bytes)
    assert predicted['words_order'] == archive['order']
    assert predicted['holdings'] == archive['six_sharing']
    t = predicted['catalogues']['signed']['tables']
    compared = {}
    for archive_key, predictions in [('six', ('coherent', 'literal')), ('biased_six', ('literal_biased',))]:
        for name in predictions:
            observed = {','.join(map(str, row['inputs'])): row for row in archive[archive_key]}
            assert set(t[name]) == set(observed)
            row_counts = {}
            for key, row in observed.items():
                expected = [Fraction(v) for v in t[name][key]['conditional']]
                former = [Fraction(v, row['denominator']) for v in row['numerator']]
                assert len(former) == len(expected) == 64
                if 'born_numerators_over_256' in row:
                    assert former == [Fraction(v, 256) for v in row['born_numerators_over_256']]
                assert expected == former
                row_counts[key] = {'compared_cells': len(former), 'equal_zero_cells': former.count(0),
                                   'equal_positive_cells': len(former) - former.count(0)}
            compared[name] = row_counts
    return {'compared_at_host_utc': datetime.now(timezone.utc).isoformat(),
            'prediction_sha256': receipt['prediction_sha256'], 'archive_sha256': sha256(archive_bytes).hexdigest(),
            'archive': str(archive_path), 'comparisons': compared}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[3]
    old = 'FOUR-READINGS-20261120-001A'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--prediction', type=Path, required=True)
    parser.add_argument('--archive', type=Path, default=Path('artifacts') / old / f'{old}-E001_signed_rules' / 'games.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    archive = args.archive if args.archive.is_absolute() or args.archive.exists() else root / args.archive
    result = compare(args.prediction, archive)
    with args.output.open('x') as out:
        out.write(dumps(result, indent=2) + '\n')
