"""Evaluate one independently drawn physical source at each supplied knot law."""

from argparse import ArgumentParser
import gzip
import json

from panels_sources import COUNTS, LAWS, OUT, sources
from panels_physical import grow
from panels_rank import publish_minima


def cases():
    for panel in COUNTS:
        for sample in sources(panel):
            yield f'{panel}-{sample["draw"]:03d}', sample


def run(case_id, payload):
    assert case_id == f'{payload["panel"]}-{payload["draw"]:03d}'
    return dict(payload, laws={law: grow(payload, law) for law in LAWS})


def write(name, output):
    OUT.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(output, sort_keys=True) + '\n').encode()
    path = OUT / name
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def main():
    parser = ArgumentParser()
    parser.add_argument('--check-panel', choices=tuple(COUNTS))
    args = parser.parse_args()
    records = []
    for panel in (tuple(COUNTS) if args.check_panel is None else (args.check_panel,)):
        records.extend(run(f'{panel}-{s["draw"]:03d}', s) for s in sources(panel))
        print(panel, COUNTS[panel], 'complete', flush=True)
    minima = publish_minima(records)
    if args.check_panel is None:
        write('panels_witnesses.json', minima)
        write('panels_histories.json.gz', records)
    else:
        write(f'panels_check_{args.check_panel}.json', minima)
    print({key: None if minima[key] is None else minima[key].get('ranking_key', minima[key]['panel'])
           for key in ('whole', 'component', 'continuing_component', 'negative', 'positive_fresh')}, flush=True)


if __name__ == '__main__':
    main()
